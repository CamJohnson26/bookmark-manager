
# Bookmark Manager

## Next Steps
- [x] Implement health checks
- [ ] Move off of transformers to Ollama
- [ ] Add tags to bookmark summary
- [ ] Implement embeddings for comparisons
- [ ] Containerize the application with Docker

# Usage
* Run the cli app
* Paste your new urls into ingest.txt
* Type bulk_ingest in the cli
* In a terminal window, run `python3 cli_app.py`
* Type 'consume'. URLs will be consumed from ingest.txt and added to the database.
* Check in the input/history file to version control.
* Watch RabbitMq at http://24.199.116.58/. If there were any errors, investigate and then run the retry commands
* Verify results show up at book.camjohnson.me

# Deployment
## Prerequisites
* SSH access to the destination server
* rsync installed on both local and remote machines
* Python 3 installed on the destination server
* Sudo access on the destination server (for systemd service installation)

## Environment Setup
1. Create an environment file (e.g., `.env` or `.env.production`) with the required configuration:
   ```
   DATABASE_URL=postgresql://...
   RABBITMQ_URL="..."
   RABBITMQ_PORT=...
   RABBITMQ_USERNAME="..."
   RABBITMQ_PASSWORD="..."
   HEALTHCHECK_URL="https://example.com/healthcheck"  # Optional: URL for healthcheck pings
   ```

## Deployment Steps
1. Make the deployment script executable (if not already):
   ```
   chmod +x deploy.sh
   ```

2. Run the deployment script:
   ```
   ./deploy.sh <destination_server> <destination_path> [env_file]
   ```

   Parameters:
   - `destination_server`: SSH address (e.g., user@example.com)
   - `destination_path`: Full path on the remote server where the application will be deployed
   - `env_file`: (Optional) Path to the environment file (defaults to `.env`)

   Example:
   ```
   ./deploy.sh 192.168.68.58 /home/cameron/bookmark-manager .env.production
   ```

3. The script will:
   - Stop any running instances of the application on the destination server
   - Transfer the application files to the destination server
   - Install system dependencies using `setup.sh`
   - Set up a Python virtual environment and install dependencies
   - Install a systemd service to automatically start the application on system boot
   - Start the application as a systemd service

## Auto-start Feature
The application is set up to start automatically when the server boots up using systemd. The systemd service:
- Runs the application in the background
- Automatically restarts the application if it crashes
- Logs output to the app.log file in the application directory

## Health Checks
The application includes a periodic health check system that pings an external healthcheck endpoint every 15 minutes. This helps monitor that the application is still running properly.

To use this feature:
1. Set the `HEALTHCHECK_URL` environment variable to your healthcheck service URL (e.g., UptimeRobot, Healthchecks.io, or your own monitoring service)
2. The application will automatically send a GET request to this URL every 15 minutes
3. If the request fails, an error will be logged but the application will continue running

If no `HEALTHCHECK_URL` is specified, a default URL is used (https://example.com/healthcheck) which serves as a no-op.

## Managing the Service
You can manage the service using standard systemd commands:

1. Check service status:
   ```
   sudo systemctl status bookmark-manager.service
   ```

2. Stop the service:
   ```
   sudo systemctl stop bookmark-manager.service
   ```

3. Start the service:
   ```
   sudo systemctl start bookmark-manager.service
   ```

4. Disable auto-start on boot:
   ```
   sudo systemctl disable bookmark-manager.service
   ```

5. Enable auto-start on boot:
   ```
   sudo systemctl enable bookmark-manager.service
   ```

6. View logs:
   ```
   tail -f /home/cameron/bookmark-manager/app.log
   ```

# Old notes
Install python dev tools: `sudo apt-get install python3-dev`
`sudo apt-get install build-essential`
sudo apt install python2-dev
sudo apt-get install libxml2-dev libxslt-dev

Ignore all the reqs and just use Python 3.9

Actually you can't, because of https://askubuntu.com/questions/1239829/modulenotfounderror-no-module-named-distutils-util
Going to try deleting requirements.txt and installing manually. I think part of the problem is some packages aren't compatible with 3.10, but I can't use 3.9 because of Debian.

geckodriver has a stupid install process. Download the release from mozilla github, sudo chmod +x it, and drop into /usr/local/bin.
Then venv isn't gonna pick it up because it's not in the path, so you have to move geckodriver manually into the venv bin folder
https://stackoverflow.com/questions/65318382/expected-browser-binary-location-but-unable-to-find-binary-in-default-location


pip freeze > requirements.txt How do I add a path to PYTHONPATH in virtualenv, Sometimes the trickiest part of setting up a virtual environment on Windows is finding your python distribution. If the installer didn't add it to your PATH variable,​  Then do any of the following steps: Create or modify an entry for python.pythonPath with the full path to the Python executable (if you edit settings.json Windows: "python.pythonPath": "c:/python36/python.exe", macOS/Linux: "python.pythonPath": "/home/python36/python", You can also use

You can add to the python path in the settings, view all interpreters, and then the little 'Paths' button but it's not doing anything

I don't get it, the pycharm /usr/bin folder in the paths selection has different content than ls in terminal.
Maybe pycharm needs sudo permissions. Forget it this is too much trouble.

Pyppeteer also is crashing, won't work with the installed version.

Ok I'm pretty sure it's because I was running PyCharm through flatpak. Use the jetbrains toolbox instead.
