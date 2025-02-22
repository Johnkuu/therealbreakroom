from flask import Flask, request, jsonify, send_from_directory
import requests
from requests.auth import HTTPBasicAuth
from flask_cors import CORS
import logging
import time
import subprocess
import os

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# Replace with your actual Kodi credentials
KODI_USERNAME = 'kodi'
KODI_PASSWORD = 'XXXXX'
KODI_URL = 'http://192.168.32.14:8080/jsonrpc'  # Kodi JSON-RPC endpoint

# Global variable to store the process instance for sensor-based volume script
sensor_script_process = None

# Function to call curl to set Kodi volume
def set_volume(volume_level):
    """Use curl to set volume on Kodi."""
    curl_command = [
        "curl",
        "-s", "--data-binary", 
        f'{{ "jsonrpc": "2.0", "method": "Application.SetVolume", "params": {{ "volume": {volume_level} }} , "id": 1 }}', 
        "-H", "Content-Type: application/json", 
        f"http://{KODI_USERNAME}:{KODI_PASSWORD}@{KODI_URL}"
    ]
    try:
        # Execute the curl command
        subprocess.run(curl_command, check=True)
        logging.info(f"Volume set to {volume_level}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error executing curl command for volume: {e}")

# Route for debugging volume changes
@app.route('/debug-volume', methods=['GET'])
def debug_volume():
    try:
        set_volume(50)  # Normal volume
        time.sleep(10)
        set_volume(0)   # Mute
        time.sleep(10)
        set_volume(50)  # Normal volume again

        return jsonify({
            "status": "success",
            "message": "Volume changed from normal to mute and back to normal"
        }), 200

    except Exception as e:
        logging.error(f"Error while debugging volume: {e}")
        return jsonify({"error": str(e)}), 500

# Serve index.html at the root URL
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

# Dynamic route to serve any file in the root folder
@app.route('/<path:filename>')
def serve_file(filename):
    try:
        return send_from_directory('.', filename)
    except Exception as e:
        logging.error(f"Error serving file {filename}: {e}")
        return jsonify({"error": f"File '{filename}' not found."}), 404

@app.route('/kodi', methods=['POST'])
def kodi_proxy():
    logging.debug(f"Received request: {request.json}")

    try:
        response = requests.post(
            KODI_URL,
            json=request.json,
            auth=HTTPBasicAuth(KODI_USERNAME, KODI_PASSWORD)
        )

        logging.debug(f"Response from Kodi: {response.status_code} {response.text}")
        return jsonify(response.json()), response.status_code

    except Exception as e:
        logging.error(f"Error while contacting Kodi: {str(e)}")
        return jsonify({"error": str(e)}), 500

# New route to start immersive mode (start sensor script)
@app.route('/immersion/start', methods=['POST'])
def start_immersion():
    global sensor_script_process
    if sensor_script_process is None or sensor_script_process.poll() is not None:  # If not running
        try:
            # Absolute path to the sensor-based volume script
            sensor_script_path = '/home/user/kodi/sensor_based_volume.py'  # Replace with your full path

            # Check if the file exists before trying to run it
            if not os.path.exists(sensor_script_path):
                logging.error(f"Sensor script not found at {sensor_script_path}")
                return jsonify({"status": "error", "message": "Sensor script not found."}), 500

            # Start the sensor-based volume script
            logging.info(f"Starting immersion mode with script: {sensor_script_path}")
            sensor_script_process = subprocess.Popen(['python3', sensor_script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Capture output and errors from the script
            stdout, stderr = sensor_script_process.communicate()
            if stdout:
                logging.info(f"Script output: {stdout.decode()}")
            if stderr:
                logging.error(f"Script error: {stderr.decode()}")

            return jsonify({"status": "success", "message": "Immersion mode started."}), 200
        except Exception as e:
            logging.error(f"Error starting immersion script: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500
    else:
        return jsonify({"status": "success", "message": "Immersion mode already running."})

# New route to stop immersive mode (stop sensor script)
@app.route('/immersion/stop', methods=['POST'])
def stop_immersion():
    global sensor_script_process
    if sensor_script_process is not None and sensor_script_process.poll() is None:  # If running
        try:
            sensor_script_process.terminate()  # Stop the process
            sensor_script_process = None
            return jsonify({"status": "success", "message": "Immersion mode stopped."}), 200
        except Exception as e:
            logging.error(f"Error stopping immersion script: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500
    else:
        return jsonify({"status": "success", "message": "Immersion mode not running."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # Run the Flask app for external access
