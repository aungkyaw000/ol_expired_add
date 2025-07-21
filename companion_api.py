# companion_api.py
# A simple Flask API to manage expiration dates for Outline keys.

from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)
# The file where we will store our expiration data
EXPIRATIONS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'expirations.json')

def read_expirations():
    """Reads the expirations data from the JSON file."""
    if not os.path.exists(EXPIRATIONS_FILE):
        return {}
    try:
        with open(EXPIRATIONS_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}

def write_expirations(data):
    """Writes the expirations data to the JSON file."""
    with open(EXPIRATIONS_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/expirations', methods=['GET'])
def get_all_expirations():
    """Returns all stored expiration dates."""
    return jsonify(read_expirations())

@app.route('/expirations/<string:key_id>', methods=['POST'])
def set_expiration(key_id):
    """Sets an expiration date for a specific key."""
    if not request.is_json:
        return jsonify({"error": "Invalid request: JSON required"}), 400
    
    data = request.get_json()
    timestamp = data.get('timestamp')

    if not isinstance(timestamp, int):
        return jsonify({"error": "Invalid timestamp"}), 400

    expirations = read_expirations()
    expirations[key_id] = timestamp
    write_expirations(expirations)
    
    return jsonify({"success": True, "key_id": key_id, "timestamp": timestamp}), 201

@app.route('/expirations/<string:key_id>', methods=['DELETE'])
def remove_expiration(key_id):
    """Removes an expiration date for a specific key."""
    expirations = read_expirations()
    if key_id in expirations:
        del expirations[key_id]
        write_expirations(expirations)
        return jsonify({"success": True, "message": f"Expiration for key {key_id} removed."}), 200
    else:
        return jsonify({"error": "Key not found"}), 404

if __name__ == '__main__':
    # The API will only be accessible from the server itself (localhost) for security.
    app.run(host='127.0.0.1', port=5500)
