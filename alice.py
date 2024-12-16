import socket
import sys
import argparse
from shared_protocol import DiffieHellman
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
        # Inizializza DH
        dh = DiffieHellman()
        
        # Connessione a Bob
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', 5003))
        print("\nConnesso a Bob. Iniziando lo scambio delle chiavi...")
        
        # Invia la chiave pubblica DH
        sock.send(str(dh.public_key).encode())
        
        # Ricevi la chiave pubblica di Bob
        bob_public_key = int(sock.recv(1024).decode())
        print(f"Ricevuta chiave pubblica DH da Bob: {bob_public_key}")
        
        # Genera il segreto condiviso
        shared_secret = dh.generate_shared_secret(bob_public_key)
        print(f"Segreto condiviso generato: {shared_secret}")
        
        # Usa il segreto condiviso per generare le chiavi RSA
        p = 61 * shared_secret % 1000
        q = 53 * shared_secret % 1000
        # Assicurati che p e q siano primi (questa è una semplificazione)
        while not (is_prime(p) and is_prime(q)):
            p += 1
            q += 1
        e = 17
        
        public_key, _ = generate_rsa_keys(p, q, e)
        print(f"RSA keys generated using the shared secret")
        
        # Prepara e invia il messaggio
        message = ' '.join(args.message)
        print(f"\nOriginal message: {message}")
        
        ascii_values = [ord(c) for c in message]
        print(f"ASCII values: {ascii_values}")
        
        encrypted = encrypt(message, public_key)
        print(f"Cyphered message: {encrypted}")
        
        binary = [bin(x)[2:] for x in encrypted]
        print(f"Binary representation: {binary}")
        
        # Invia il messaggio cifrato
        sock.send(str(encrypted).encode())
        print("Message successfuly sent!")
        
    except ConnectionRefusedError:
        print("Error: Impossible to connect to Bob. Is Bob running?")
        sys.exit(1)
    except Exception as e:
        print(f"An error occured: {e}")
        sys.exit(1)
    finally:
        sock.close()

def is_prime(n: int) -> bool:
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True

if __name__ == "__main__":
    main()