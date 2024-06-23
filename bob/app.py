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
P = int(os.getenv("P"))
Q = int(os.getenv("Q"))
E = int(os.getenv("E"))

# RSA Key Generation
def generate_keys():

    n = P * Q
    phi = (P - 1) * (Q - 1)
    # Coprime with phi and 1 < e < phi
    d = pow(E, -1, phi)
    return (E, n), (d, n)

PUBLIC_KEY, PRIVATE_KEY = generate_keys()

# This will store all messages with timestamps and details
messages = []
known_public_keys = {}

def encrypt(message, pub_key):
    e, n = pub_key
    cipher = [pow(ord(char), e, n) for char in message]
    return cipher

def decrypt(cipher, priv_key):
    d, n = priv_key
    message = ''.join([chr(pow(char, d, n)) for char in cipher])
    return message

def to_bin(numbers):
    return ' '.join(format(x, 'b') for x in numbers)

@app.route('/')
def index():
    return render_template('index.html', name=NAME, messages=messages)

@app.route('/hosts')
def get_hosts():
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

@app.route('/get_public_key')
def get_public_key():
    return jsonify({'public_key': PUBLIC_KEY})

@app.route('/send', methods=['POST'])
def send():
    target_host = request.form['host']
    message = request.form['message']
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if message == "inviami la chiave pubblica":
        try:
            requests.post(f'http://{target_host}:5000/message', json={'message': message, 'timestamp': timestamp, 'sender': NAME})
            messages.append({
                'type': 'sent',
                'message': message,
                'timestamp': timestamp,
                'receiver': target_host,
                'sender': NAME
            })
        except requests.exceptions.RequestException as e:
            print(f"Failed to send message to {target_host}: {e}")
        return render_template('index.html', name=NAME, messages=messages)

    if target_host not in known_public_keys:
        try:
            response = requests.get(f'http://{target_host}:5000/get_public_key', timeout=5)
            known_public_keys[target_host] = tuple(response.json()['public_key'])
            messages.append({
                'type': 'info',
                'message': f'Chiave pubblica ricevuta da {target_host}: {known_public_keys[target_host]}',
                'timestamp': timestamp,
                'sender': target_host,
                'receiver': NAME
            })
        except requests.exceptions.RequestException as e:
            print(f"Failed to get public key from {target_host}: {e}")
            return render_template('index.html', name=NAME, messages=messages)
    
    pub_key = known_public_keys[target_host]
    encrypted_message = encrypt(message, pub_key)
    bin_message = to_bin(encrypted_message)
    ascii_values = [ord(char) for char in message]
    
    try:
        requests.post(f'http://{target_host}:5000/message', json={'message': encrypted_message, 'timestamp': timestamp, 'sender': NAME})
        messages.append({
            'type': 'sent',
            'message': message,
            'ascii_values': ascii_values,
            'encrypted_message': encrypted_message,
            'bin_message': bin_message,
            'timestamp': timestamp,
            'receiver': target_host,
            'sender': NAME
        })
    except requests.exceptions.RequestException as e:
        print(f"Failed to send message to {target_host}: {e}")
    return render_template('index.html', name=NAME, messages=messages)

@app.route('/message', methods=['POST'])
def message():
    received_message = request.json['message']
    send_timestamp = request.json['timestamp']
    sender = request.json['sender']
    recv_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if received_message == "inviami la chiave pubblica":
        try:
            requests.post(f'http://{sender}:5000/message', json={'message': PUBLIC_KEY, 'timestamp': recv_timestamp, 'sender': NAME})
            messages.append({
                'type': 'received',
                'message': received_message,
                'send_timestamp': send_timestamp,
                'recv_timestamp': recv_timestamp,
                'sender': sender,
                'receiver': NAME
            })
        except requests.exceptions.RequestException as e:
            print(f"Failed to send public key to {sender}: {e}")
        return '', 204

    if isinstance(received_message, list):
        decrypted_message = decrypt(received_message, PRIVATE_KEY)
        ascii_values = [ord(char) for char in decrypted_message]
        bin_message = to_bin(received_message)
        messages.append({
            'type': 'received',
            'message': decrypted_message,
            'ascii_values': ascii_values,
            'encrypted_message': received_message,
            'bin_message': bin_message,
            'send_timestamp': send_timestamp,
            'recv_timestamp': recv_timestamp,
            'sender': sender,
            'receiver': NAME
        })
        socketio.emit('new_message', {
            'message': decrypted_message,
            'ascii_values': ascii_values,
            'encrypted_message': received_message,
            'bin_message': bin_message,
            'send_timestamp': send_timestamp,
            'recv_timestamp': recv_timestamp,
            'sender': sender,
            'receiver': NAME
        })
    else:
        known_public_keys[sender] = tuple(received_message)
        messages.append({
            'type': 'info',
            'message': f'Chiave pubblica ricevuta da {sender}: {known_public_keys[sender]}',
            'send_timestamp': send_timestamp,
            'recv_timestamp': recv_timestamp,
            'sender': sender,
            'receiver': NAME
        })
        socketio.emit('new_message', {
            'message': f'Chiave pubblica ricevuta da {sender}: {known_public_keys[sender]}',
            'send_timestamp': send_timestamp,
            'recv_timestamp': recv_timestamp,
            'sender': sender,
            'receiver': NAME
        })

    return '', 204

def monitor_network():
    while True:
        time.sleep(5)

if __name__ == '__main__':
    threading.Thread(target=monitor_network).start()
    socketio.run(app, host='0.0.0.0', port=5000)