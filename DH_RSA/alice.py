import socket
import sys
import argparse
from shared_protocol import DiffieHellman, is_prime
from typing import Tuple

def generate_rsa_keys(p: int, q: int, e: int) -> Tuple[Tuple[int, int], Tuple[int, int]]:
    n = p * q
    phi = (p - 1) * (q - 1)
    d = pow(e, -1, phi)
    return ((e, n), (d, n))

def encrypt(message: str, public_key: Tuple[int, int]) -> list:
    e, n = public_key
    return [pow(ord(char), e, n) for char in message]

def main():
    parser = argparse.ArgumentParser(description='Send an encrypted message to Bob')
    parser.add_argument('--message', '-m', nargs='+', default=["Hello", "world"],
                       help='Message to send (default: "Hello world")')
    args = parser.parse_args()
    
    try:
        # init DH
        dh = DiffieHellman()
        
        # connect to Bob
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', 5003))
        print("\nConnected to Bob. Starting key sharing...")
        
        # send DH public key to Bob
        sock.send(str(dh.public_key).encode())
        
        # receive Bob's public key
        bob_public_key = int(sock.recv(1024).decode())
        print(f"Public key received from Bob: {bob_public_key}")
        
        # generate the shared secret
        shared_secret = dh.generate_shared_secret(bob_public_key)
        print(f"Generated shared secred: {shared_secret}")
        
        # use the shared secret to generate RSA keys
        p = 61 * shared_secret % 1000
        q = 53 * shared_secret % 1000

        # Semplification: make sure p and q are prime
        while not (is_prime(p) and is_prime(q)):
            p += 1
            q += 1
        e = 17
        
        public_key, _ = generate_rsa_keys(p, q, e)
        print(f"RSA keys generated using shared secret")
        
        # prepare to send the message
        message = ' '.join(args.message)
        print(f"\nOriginal Message: {message}")
        
        ascii_values = [ord(c) for c in message]
        print(f"ASCII values: {ascii_values}")
        
        encrypted = encrypt(message, public_key)
        print(f"Cyphred message: {encrypted}")
        
        binary = [bin(x)[2:] for x in encrypted]
        print(f"Binary representation: {binary}")
        
        # send the encrypted message to Bob
        sock.send(str(encrypted).encode())
        print("Message successfuly sent!")
        
    except ConnectionRefusedError:
        print("Error: Impossible to connect with Bob. Make sure bob.py is running")
        sys.exit(1)
    except Exception as e:
        print(f"An error occured: {e}")
        sys.exit(1)
    finally:
        sock.close()

if __name__ == "__main__":
    main()