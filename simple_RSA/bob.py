import socket
from typing import Tuple

def decrypt(cipher: list, private_key: Tuple[int, int]) -> str:
    d, n = private_key
    return ''.join(chr(pow(c, d, n)) for c in cipher)

def main():
    # Key generation (same parameters as Alice)
    p, q = 61, 53
    n = p * q
    phi = (p - 1) * (q - 1)
    e = 17
    d = pow(e, -1, phi)
    private_key = (d, n)
    
    # Start server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 5000))
    server.listen(1)
    
    print("Waiting for Alice's message...")
    conn, addr = server.accept()
    
    # Receive encrypted message
    data = conn.recv(1024).decode()
    encrypted = eval(data)  # Convert string representation back to list
    print(f"\nReceived encrypted message: {encrypted}")
    
    # Show binary representation
    binary = [bin(x)[2:] for x in encrypted]
    print(f"Binary representation: {binary}")
    
    # Decrypt
    decrypted = decrypt(encrypted, private_key)
    print(f"Decrypted message: {decrypted}")
    
    # Show ASCII values
    ascii_values = [ord(c) for c in decrypted]
    print(f"ASCII values: {ascii_values}")
    
    conn.close()
    server.close()

if __name__ == "__main__":
    main()