# alice.py
import socket
from typing import Tuple
import sys
import argparse

def generate_keys(p: int, q: int, e: int) -> Tuple[Tuple[int, int], Tuple[int, int]]:
    n = p * q
    phi = (p - 1) * (q - 1)
    d = pow(e, -1, phi)
    return ((e, n), (d, n))

def encrypt(message: str, public_key: Tuple[int, int]) -> list:
    e, n = public_key
    return [pow(ord(char), e, n) for char in message]

def main():
    # Setup argument parser
    parser = argparse.ArgumentParser(description='Send an encrypted message to Bob')
    parser.add_argument('--message', '-m', nargs='+', default=["Hello", "world"],
                       help='Message to send (default: "Hello world"). Multiple words can be provided.')
    args = parser.parse_args()
    
    # Key generation
    p, q = 61, 53  # Example prime numbers
    e = 17  # Example public exponent
    public_key, _ = generate_keys(p, q, e)
    
    try:
        # Connect to Bob
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', 5003))
        
        # Get the message and join the words
        message = ' '.join(args.message)
        print(f"\nOriginal message: {message}")
        
        # Show ASCII values
        ascii_values = [ord(c) for c in message]
        print(f"ASCII values: {ascii_values}")
        
        # Encrypt and send
        encrypted = encrypt(message, public_key)
        print(f"Encrypted message: {encrypted}")
        
        # Convert to binary for visualization
        binary = [bin(x)[2:] for x in encrypted]
        print(f"Binary representation: {binary}")
        
        # Send encrypted message to Bob
        sock.send(str(encrypted).encode())
        print("Message sent successfully!")
        
    except ConnectionRefusedError:
        print("Error: Could not connect to Bob. Make sure bob.py is running.")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)
    finally:
        sock.close()

if __name__ == "__main__":
    main()