import socket
from typing import Tuple
from shared_protocol import DiffieHellman

def decrypt(cipher: list, private_key: Tuple[int, int]) -> str:
    d, n = private_key
    return ''.join(chr(pow(c, d, n)) for c in cipher)

def generate_rsa_keys(p: int, q: int, e: int) -> Tuple[Tuple[int, int], Tuple[int, int]]:
    n = p * q
    phi = (p - 1) * (q - 1)
    d = pow(e, -1, phi)
    return ((e, n), (d, n))

def main():
    # Inizializza DH
    dh = DiffieHellman()
    
    # Avvia il server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 5003))
    server.listen(1)
    
    print("Waiting Alice...")
    conn, addr = server.accept()
    print(f"Alice connected from {addr}")
    
    try:
        # Ricevi la chiave pubblica di Alice
        alice_public_key = int(conn.recv(1024).decode())
        print(f"Received DH public key from Alice: {alice_public_key}")
        
        # Invia la tua chiave pubblica
        conn.send(str(dh.public_key).encode())
        
        # Genera il segreto condiviso
        shared_secret = dh.generate_shared_secret(alice_public_key)
        print(f"Generated shared secret: {shared_secret}")
        
        # Usa il segreto condiviso per generare le chiavi RSA
        p = 61 * shared_secret % 1000
        q = 53 * shared_secret % 1000
        # Assicurati che p e q siano primi (questa è una semplificazione)
        while not (is_prime(p) and is_prime(q)):
            p += 1
            q += 1
        e = 17
        
        _, private_key = generate_rsa_keys(p, q, e)
        print(f"RSA keys generated using shared secret")
        
        # Ricevi il messaggio cifrato
        data = conn.recv(1024).decode()
        encrypted = eval(data)
        print(f"\nCyphered message received: {encrypted}")
        
        # Mostra la rappresentazione binaria
        binary = [bin(x)[2:] for x in encrypted]
        print(f"Binary representation: {binary}")
        
        # Decifra
        decrypted = decrypt(encrypted, private_key)
        print(f"Cyphered message: {decrypted}")
        
        # Mostra i valori ASCII
        ascii_values = [ord(c) for c in decrypted]
        print(f"ASCII values: {ascii_values}")
        
    except Exception as e:
        print(f"An error occured: {e}")
    finally:
        conn.close()
        server.close()

def is_prime(n: int) -> bool:
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True

if __name__ == "__main__":
    main()