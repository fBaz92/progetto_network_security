import socket
from typing import Tuple
from shared_protocol import DiffieHellman, is_prime

def decrypt(cipher: list, private_key: Tuple[int, int]) -> str:
    d, n = private_key
    return ''.join(chr(pow(c, d, n)) for c in cipher)

def generate_rsa_keys(p: int, q: int, e: int) -> Tuple[Tuple[int, int], Tuple[int, int]]:
    n = p * q
    phi = (p - 1) * (q - 1)
    d = pow(e, -1, phi)
    return ((e, n), (d, n))

def main():
    # Init DH
    dh = DiffieHellman()
    
    # start the server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 5003))
    server.listen(1)
    
    print("Waiting Alice...")
    conn, addr = server.accept()
    print(f"Alice connected from {addr}")
    
    try:
        # receive public key from Alice
        alice_public_key = int(conn.recv(1024).decode())
        print(f"Received DH public key from Alice: {alice_public_key}")
        
        # send Bob's public key
        conn.send(str(dh.public_key).encode())
        
        # create shared secret
        shared_secret = dh.generate_shared_secret(alice_public_key)
        print(f"Generated shared secret: {shared_secret}")
        
        # create RSA keys from the shared secred
        p = 61 * shared_secret % 1000
        q = 53 * shared_secret % 1000
        # simplification to ensure both p and q are prime
        while not (is_prime(p) and is_prime(q)):
            p += 1
            q += 1
        e = 17
        
        _, private_key = generate_rsa_keys(p, q, e)
        print(f"RSA keys generated using shared secret")
        
        # receive encrypted message
        data = conn.recv(1024).decode()
        encrypted = eval(data)
        print(f"\nCyphered message received: {encrypted}")
        
        # binary representation
        binary = [bin(x)[2:] for x in encrypted]
        print(f"Binary representation: {binary}")
        
        # decrypt
        decrypted = decrypt(encrypted, private_key)
        print(f"Cyphered message: {decrypted}")
        
        # ascii values
        ascii_values = [ord(c) for c in decrypted]
        print(f"ASCII values: {ascii_values}")
        
    except Exception as e:
        print(f"An error occured: {e}")
    finally:
        conn.close()
        server.close()

if __name__ == "__main__":
    main()