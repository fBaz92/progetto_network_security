import socket
import sys
import argparse
from shared_protocol import *
from typing import Tuple

def is_prime(n: int) -> bool:
    """Check if a number is prime"""
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True

def encrypt(message: str, shared_secret: int) -> list:
    """Encrypt a message using the shared secret"""
    # Use shared_secret to generate RSA parameters
    p = 61 * shared_secret % 1000
    q = 53 * shared_secret % 1000
    # Ensure p and q are prime
    while not is_prime(p):
        p += 1
    while not is_prime(q):
        q += 1
    
    n = p * q
    e = 17  # Public key exponent
    
    # Encrypt the message
    return [pow(ord(char), e, n) for char in message]

def main():
    parser = argparse.ArgumentParser(description='Send an encrypted message to Bob')
    parser.add_argument('--message', '-m', nargs='+', default=["Hello", "world"],
                       help='Message to send (default: "Hello world")')
    args = parser.parse_args()
    
    try:
        # Initialize DH
        dh = DiffieHellman()
        
        # Connect to Bob
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((NetworkConfig.HOST, NetworkConfig.BOB_PORT))
        print(f"Connected to Bob on port {NetworkConfig.BOB_PORT}")

        # Exchange certificates
        other_cert = exchange_certificates(sock, "Alice", dh.public_key)
        if other_cert.subject != "Bob":
            raise Exception("Received certificate from unexpected subject")
        
        # Send DH public key
        sock.send(str(dh.public_key).encode())
        
        # Receive Bob's public key
        bob_public_key = int(sock.recv(1024).decode())
        print(f"Received DH public key from Bob: {bob_public_key}")
        
        # Generate shared secret
        shared_secret = dh.generate_shared_secret(bob_public_key)
        print(f"Generated shared secret: {shared_secret}")
        
        # Prepare and send message
        message = ' '.join(args.message)
        print(f"\nOriginal message: {message}")
        
        encrypted = encrypt(message, shared_secret)
        print(f"Encrypted message: {encrypted}")
        
        # Send encrypted message
        sock.send(str(encrypted).encode())
        print("Message sent successfully!")
        
    except ConnectionRefusedError:
        print("Error: Could not connect to Bob. Is Bob running?")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)
    finally:
        sock.close()

if __name__ == "__main__":
    main()