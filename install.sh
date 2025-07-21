#!/bin/bash

# This script installs the Outline Companion service.
# Run this on your Outline server as root.

echo ">>> Starting Outline Companion Service Installation <<<"

# --- Configuration ---
# Replace this with the RAW URL of your companion_api.py file on GitHub/Gist
API_SCRIPT_URL="https://gist.githubusercontent.com/YOUR_USERNAME/YOUR_GIST_ID/raw/companion_api.py"

# Replace this with the RAW URL of your check_expirations.py file on GitHub/Gist
CHECKER_SCRIPT_URL="https://gist.githubusercontent.com/YOUR_USERNAME/YOUR_GIST_ID/raw/check_expirations.py"

SERVICE_DIR="/opt/outline_companion"
SERVICE_FILE="/etc/systemd/system/outline-companion.service"
# --- End Configuration ---

# 1. Install Dependencies
echo "--> Step 1: Installing Python3 and dependencies..."
apt-get update
apt-get install -y python3 python3-pip python3-venv

# 2. Create Service Directory and Python Scripts
echo "--> Step 2: Creating service directory and downloading scripts..."
mkdir -p $SERVICE_DIR
cd $SERVICE_DIR

# Download your scripts from GitHub/Gist
curl -sSLo companion_api.py $API_SCRIPT_URL
curl -sSLo check_expirations.py $CHECKER_SCRIPT_URL

if [ ! -f "companion_api.py" ] || [ ! -f "check_expirations.py" ]; then
    echo "!!! ERROR: Failed to download scripts. Please check your URLs in the install script."
    exit 1
fi

# 3. Create Python Virtual Environment and Install Flask
echo "--> Step 3: Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate
pip install Flask requests

# 4. Create systemd service to run the API
echo "--> Step 4: Creating systemd service file..."
cat > $SERVICE_FILE << EOL
[Unit]
Description=Outline Companion API Service
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=$SERVICE_DIR
ExecStart=$SERVICE_DIR/venv/bin/python3 $SERVICE_DIR/companion_api.py
Restart=always

[Install]
WantedBy=multi-user.target
EOL

# 5. Setup Cron Job to check expirations every hour
echo "--> Step 5: Setting up cron job for expiration checks..."
CRON_JOB="0 * * * * root $SERVICE_DIR/venv/bin/python3 $SERVICE_DIR/check_expirations.py >> /var/log/outline_companion_cron.log 2>&1"
echo "$CRON_JOB" > /etc/cron.d/outline_companion_check

# 6. Start and Enable the Service
echo "--> Step 6: Starting and enabling the new service..."
systemctl daemon-reload
systemctl enable outline-companion.service
systemctl start outline-companion.service

echo ""
echo ">>> ✅ Installation Complete! <<<"
echo "The Outline Companion API is now running."
echo "Expiration checks will run automatically every hour."
