from flask import Flask, request, render_template, jsonify
from flask_socketio import SocketIO, emit
import requests
import threading
import time
import os
from dotenv import load_dotenv
from datetime import datetime

app = Flask(__name__)
socketio = SocketIO(app)

# Load environment variables
load_dotenv()

NAME = os.getenv("NAME")
PUBLIC_KEY = tuple(map(int, os.getenv("PUBLIC_KEY").split(',')))
PRIVATE_KEY = tuple(map(int, os.getenv("PRIVATE_KEY").split(',')))

# This will store all messages with timestamps
messages = []

def encrypt(message, pub_key):
    e, n = pub_key
    cipher = [pow(ord(char), e, n) for char in message]
    return cipher

def decrypt(cipher, priv_key):
    d, n = priv_key
    message = ''.join([chr(pow(char, d, n)) for char in cipher])
    return message

@app.route('/')
def index():
    return render_template('index.html', name=NAME, messages=messages)

@app.route('/hosts')
def get_hosts():
    # In a real scenario, this would discover hosts dynamically
    hosts = ["bob"] if NAME == "Alice" else ["alice"]
    available_hosts = []
    for host in hosts:
        try:
            response = requests.get(f'http://{host}:5000/ping', timeout=1)
            if response.status_code == 200:
                available_hosts.append(host)
        except requests.exceptions.RequestException:
            continue
    return jsonify(available_hosts)

@app.route('/ping')
def ping():
    return '', 200

@app.route('/send', methods=['POST'])
def send():
    target_host = request.form['host']
    message = request.form['message']
    encrypted_message = encrypt(message, PUBLIC_KEY)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        requests.post(f'http://{target_host}:5000/message', json={'message': encrypted_message, 'timestamp': timestamp})
        messages.append({'type': 'sent', 'message': message, 'encrypted_message': encrypted_message, 'timestamp': timestamp})
    except requests.exceptions.RequestException as e:
        print(f"Failed to send message to {target_host}: {e}")
    return render_template('index.html', name=NAME, messages=messages)

@app.route('/message', methods=['POST'])
def message():
    encrypted_message = request.json['message']
    timestamp = request.json['timestamp']
    decrypted_message = decrypt(encrypted_message, PRIVATE_KEY)
    messages.append({'type': 'received', 'message': decrypted_message, 'encrypted_message': encrypted_message, 'timestamp': timestamp})
    socketio.emit('new_message', {'message': decrypted_message, 'encrypted_message': encrypted_message, 'timestamp': timestamp})
    return '', 204

def monitor_network():
    while True:
        time.sleep(5)

if __name__ == '__main__':
    threading.Thread(target=monitor_network).start()
    socketio.run(app, host='0.0.0.0', port=5000)