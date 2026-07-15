#!/bin/bash

set -euo pipefail

# Use -y flag to automatically answer yes to prompts
sudo DEBIAN_FRONTEND=noninteractive apt-get update

# General Build
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y libxml2-dev libxslt-dev python3-dev python3-venv build-essential firefox

# Psycopg
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y libpq-dev

# Something
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y libffi-dev

# Selenium's Firefox driver is not installed by the Python package. Install a
# pinned release system-wide so both shells and systemd can find it.
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y ca-certificates curl tar

case "$(uname -m)" in
    x86_64)
        GECKODRIVER_PLATFORM="linux64"
        ;;
    aarch64|arm64)
        GECKODRIVER_PLATFORM="linux-aarch64"
        ;;
    *)
        echo "Unsupported architecture for geckodriver: $(uname -m)" >&2
        exit 1
        ;;
esac

GECKODRIVER_VERSION="${GECKODRIVER_VERSION:-v0.36.0}"
TEMP_DIR=$(mktemp -d)
trap 'rm -rf "$TEMP_DIR"' EXIT

GECKODRIVER_ARCHIVE="$TEMP_DIR/geckodriver.tar.gz"
GECKODRIVER_URL="https://github.com/mozilla/geckodriver/releases/download/${GECKODRIVER_VERSION}/geckodriver-${GECKODRIVER_VERSION}-${GECKODRIVER_PLATFORM}.tar.gz"

curl --fail --silent --show-error --location "$GECKODRIVER_URL" --output "$GECKODRIVER_ARCHIVE"
tar --extract --gzip --file "$GECKODRIVER_ARCHIVE" --directory "$TEMP_DIR"
sudo install --mode=0755 "$TEMP_DIR/geckodriver" /usr/local/bin/geckodriver

if [ ! -x /usr/bin/firefox ]; then
    echo "Firefox is required at /usr/bin/firefox but was not found" >&2
    exit 1
fi

command -v geckodriver
geckodriver --version
