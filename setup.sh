# Use -y flag to automatically answer yes to prompts
sudo DEBIAN_FRONTEND=noninteractive apt-get update

# General Build
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y libxml2-dev libxslt-dev python3-dev build-essential python3-distutils

# Psycopg
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y libpq-dev

# Something
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y libffi-dev
