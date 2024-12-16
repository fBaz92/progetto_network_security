import socket
import json
from config import NetworkConfig

def test_ca_connection():
    """Test if we can connect to and get a response from the CA"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((NetworkConfig.HOST, NetworkConfig.CA_PORT))
        
        # Try to request a test certificate
        request = {
            "type": "issue",
            "subject": "TestUser",
            "public_key": [123, 456]  # Test public key
        }
        sock.send(json.dumps(request).encode())
        
        response = sock.recv(1024).decode()
        print(f"CA Response: {response}")
        return True
    except Exception as e:
        print(f"CA Connection Error: {e}")
        return False
    finally:
        sock.close()

if __name__ == "__main__":
    print("Testing CA connection...")
    is_connected = test_ca_connection()
    print(f"CA is {'running and responding' if is_connected else 'not responding'}")