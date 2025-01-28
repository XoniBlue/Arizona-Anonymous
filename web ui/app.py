from dotenv import load_dotenv
from flask import Flask, jsonify, request, render_template
import subprocess
import os
import signal
import json

app = Flask(__name__)

# Path to the timezone.json file
timezone_file = 'timezone.json'

# Initialize bot process variable
bot_process = None

# Load the bot's .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))


# Ensure the timezone file exists
if not os.path.exists(timezone_file):
    with open(timezone_file, 'w') as f:
        json.dump({"timezone": ""}, f)

# Route to display the main page with the timezone form
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle timezone submission
@app.route('/set_timezone', methods=['POST'])
def set_timezone():
    timezone = request.form.get('timezone')
    
    # Save the timezone to the timezone.json file
    with open(timezone_file, 'w') as f:
        json.dump({"timezone": timezone}, f)
    
    return jsonify({"status": "success", "timezone": timezone}), 200

# Route to get the current timezone
@app.route('/get_timezone', methods=['GET'])
def get_timezone():
    with open(timezone_file, 'r') as f:
        data = json.load(f)
    return jsonify({"timezone": data.get("timezone", "")}), 200

# Route to start the bot
@app.route('/bot/start', methods=['POST'])
def start_bot():
    global bot_process
    if bot_process is None:
        bot_process = subprocess.Popen(['python', 'main.py'])  # Replace 'main.py' with your bot script name
        return jsonify({"status": "Bot started!"}), 200
    else:
        return jsonify({"status": "Bot is already running."}), 400

# Route to stop the bot
@app.route('/bot/stop', methods=['POST'])
def stop_bot():
    global bot_process
    if bot_process:
        bot_process.terminate()  # Terminate the bot process
        bot_process = None
        return jsonify({"status": "Bot stopped!"}), 200
    else:
        return jsonify({"status": "Bot is not running."}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
