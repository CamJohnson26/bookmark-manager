#!/bin/bash

# Deployment script for bookmark-manager
# Usage: ./deploy.sh <destination_server> <destination_path> [env_file]
# Example: ./deploy.sh user@example.com /home/user/bookmark-manager .env.production

# Enable command echo for debugging
set -x

# Don't exit on error, we'll handle errors manually
# set -e

# Check arguments
if [ $# -lt 2 ]; then
    echo "Usage: $0 <destination_server> <destination_path> [env_file]"
    echo "Example: $0 user@example.com /home/user/bookmark-manager .env.production"
    exit 1
fi

DESTINATION_SERVER=$1
DESTINATION_PATH=$2
ENV_FILE=${3:-.env}  # Default to .env if not specified

# SSH connection sharing options to avoid multiple password prompts
SSH_OPTS="-o ControlMaster=auto -o ControlPath=/tmp/ssh_mux_%h_%p_%r -o ControlPersist=1h"

# Check if env file exists
if [ ! -f "$ENV_FILE" ]; then
    echo "Error: Environment file $ENV_FILE not found!"
    exit 1
fi

echo "Deploying to $DESTINATION_SERVER:$DESTINATION_PATH..."

# Kill any running instances of the application on the destination server
echo "Stopping any running instances of the application..."
if ! ssh $SSH_OPTS $DESTINATION_SERVER "pkill -f 'python3 $DESTINATION_PATH/main.py' || true"; then
    echo "Warning: Failed to stop running instances, but continuing anyway..."
fi

# Create destination directory if it doesn't exist
echo "Creating destination directory if it doesn't exist..."
if ! ssh $SSH_OPTS $DESTINATION_SERVER "mkdir -p $DESTINATION_PATH"; then
    echo "Error: Failed to create destination directory. Exiting."
    exit 1
fi

# Transfer files to the destination server
echo "Transferring files to the destination server..."
if ! rsync -avz --exclude '.git' --exclude '.venv' --exclude '__pycache__' \
    --exclude '*.pyc' --exclude '.idea' --exclude '.env*' \
    -e "ssh $SSH_OPTS" \
    ./ $DESTINATION_SERVER:$DESTINATION_PATH/; then
    echo "Error: Failed to transfer files to the destination server. Exiting."
    exit 1
fi

# Transfer the environment file
echo "Transferring environment file..."
if ! scp $SSH_OPTS $ENV_FILE $DESTINATION_SERVER:$DESTINATION_PATH/.env; then
    echo "Error: Failed to transfer environment file. Exiting."
    exit 1
fi

# Install system dependencies on the destination server
echo "Installing system dependencies..."
if ! ssh $SSH_OPTS -t $DESTINATION_SERVER "cd $DESTINATION_PATH && bash setup.sh"; then
    echo "Error: Failed to install system dependencies. Exiting."
    exit 1
fi

# Set up Python virtual environment and install dependencies
echo "Setting up Python environment and installing dependencies..."
if ! ssh $SSH_OPTS $DESTINATION_SERVER "cd $DESTINATION_PATH && \
    python3 -m venv .venv && \
    source .venv/bin/activate && \
    pip install --upgrade pip && \
    pip install -r requirements.txt"; then
    echo "Error: Failed to set up Python environment or install dependencies. Exiting."
    exit 1
fi

# Set up systemd service for auto-start on boot
echo "Setting up systemd service for auto-start on boot..."
# Extract username from DESTINATION_SERVER (if in format username@hostname)
if [[ $DESTINATION_SERVER == *"@"* ]]; then
    USERNAME=$(echo $DESTINATION_SERVER | cut -d '@' -f 1)
else
    # If no username specified, use current user
    USERNAME=$(whoami)
fi

# Transfer the service file
echo "Transferring service file..."
if ! scp $SSH_OPTS bookmark-manager.service $DESTINATION_SERVER:/tmp/bookmark-manager.service; then
    echo "Error: Failed to transfer service file. Exiting."
    exit 1
fi

# Replace placeholders in the service file
echo "Replacing placeholders in service file..."
if ! ssh $SSH_OPTS $DESTINATION_SERVER "sed -i 's|USER_PLACEHOLDER|$USERNAME|g' /tmp/bookmark-manager.service"; then
    echo "Error: Failed to replace USER_PLACEHOLDER in service file. Exiting."
    exit 1
fi

if ! ssh $SSH_OPTS $DESTINATION_SERVER "sed -i 's|PATH_PLACEHOLDER|$DESTINATION_PATH|g' /tmp/bookmark-manager.service"; then
    echo "Error: Failed to replace PATH_PLACEHOLDER in service file. Exiting."
    exit 1
fi

# Install the service file (requires sudo)
echo "Installing systemd service (you may be prompted for sudo password)..."
if ! ssh $SSH_OPTS -t $DESTINATION_SERVER "sudo mv /tmp/bookmark-manager.service /etc/systemd/system/"; then
    echo "Error: Failed to move service file to systemd directory. Exiting."
    exit 1
fi

if ! ssh $SSH_OPTS -t $DESTINATION_SERVER "sudo systemctl daemon-reload"; then
    echo "Error: Failed to reload systemd daemon. Exiting."
    exit 1
fi

if ! ssh $SSH_OPTS -t $DESTINATION_SERVER "sudo systemctl enable bookmark-manager.service"; then
    echo "Error: Failed to enable bookmark-manager service. Exiting."
    exit 1
fi

if ! ssh $SSH_OPTS -t $DESTINATION_SERVER "sudo systemctl start bookmark-manager.service"; then
    echo "Error: Failed to start bookmark-manager service. Exiting."
    exit 1
fi

echo "Deployment completed successfully!"
echo "Application is installed as a systemd service and will start automatically on boot"
echo "Service status: ssh $DESTINATION_SERVER 'sudo systemctl status bookmark-manager.service'"
echo "Check logs at $DESTINATION_PATH/app.log"
