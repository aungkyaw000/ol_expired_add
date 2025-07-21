# check_expirations.py
# This script is run periodically by a cron job.

import json
import os
import time
import requests

# --- Configuration ---
# This script needs to know the Outline API URL to block keys.
# It reads it from the same config file the Outline server uses.
OUTLINE_CONFIG_PATH = '/opt/outline/persisted-state/shadowbox_server_config.json'
EXPIRATIONS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'expirations.json')
# --- End Configuration ---

def read_json_file(path):
    """A helper to read a JSON file."""
    if not os.path.exists(path):
        return None
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading {path}: {e}")
        return None

def set_data_limit(api_url, key_id, limit_bytes):
    """Calls the Outline API to set a data limit for a key."""
    url = f"{api_url}/access-keys/{key_id}/data-limit"
    payload = {'limit': {'bytes': limit_bytes}}
    try:
        # Outline API uses a self-signed cert, so we disable verification.
        response = requests.put(url, json=payload, verify=False)
        if response.status_code == 204:
            print(f"Successfully set data limit for key {key_id} to {limit_bytes} bytes.")
        else:
            print(f"Failed to set data limit for key {key_id}. Status: {response.status_code}, Body: {response.text}")
    except Exception as e:
        print(f"Error calling Outline API for key {key_id}: {e}")

def main():
    """Main function to check and enforce expirations."""
    print("Starting expiration check...")
    
    config = read_json_file(OUTLINE_CONFIG_PATH)
    if not config or 'apiUrl' not in config:
        print("Could not read Outline config or find apiUrl. Exiting.")
        return

    api_url = config['apiUrl']
    
    expirations = read_json_file(EXPIRATIONS_FILE)
    if not expirations:
        print("No expiration dates found. Exiting.")
        return

    now = int(time.time() * 1000) # Current time in milliseconds
    
    for key_id, timestamp in expirations.items():
        if timestamp <= now:
            print(f"Key {key_id} has expired. Setting data limit to 1 byte to block.")
            set_data_limit(api_url, key_id, 1)

    print("Expiration check finished.")

if __name__ == '__main__':
    # Suppress InsecureRequestWarning from requests library
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    main()
