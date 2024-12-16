import socket
from shared_protocol import DiffieHellman, exchange_certificates
from config import NetworkConfig

def is_prime(n: int) -> bool:
    """Check if a number is prime"""
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True

def decrypt(cipher: list, shared_secret: int) -> str:
    """Decrypt a message using the shared secret"""
    # Use shared_secret to generate RSA parameters
    p = 61 * shared_secret % 1000
    q = 53 * shared_secret % 1000
    # Ensure p and q are prime
    while not is_prime(p):
        p += 1
    while not is_prime(q):
        q += 1
    
    n = p * q
    phi = (p - 1) * (q - 1)
    e = 17
    d = pow(e, -1, phi)  # Calculate private key
    
    # Decrypt using private key
    return ''.join(chr(pow(c, d, n)) for c in cipher)

def main():
    # Initialize Diffie-Hellman
    dh = DiffieHellman()
    
    # Start server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((NetworkConfig.HOST, NetworkConfig.BOB_PORT))
        server.listen(1)
        print(f"Listening on port {NetworkConfig.BOB_PORT}...")
        
        while True:
            conn, addr = server.accept()
            try:
                print(f"Connection from {addr}")
                
                # Exchange certificates
                other_cert = exchange_certificates(conn, "Bob", dh.public_key)
                if other_cert.subject != "Alice":
                    raise Exception("Received certificate from unexpected subject")
                
                # Complete Diffie-Hellman exchange
                alice_public_key = int(conn.recv(1024).decode())
                conn.send(str(dh.public_key).encode())
                shared_secret = dh.generate_shared_secret(alice_public_key)
                print(f"Generated shared secret: {shared_secret}")
                
                # Receive and decrypt message
                data = conn.recv(1024).decode()
                encrypted = eval(data)
                print(f"\nReceived encrypted message: {encrypted}")
                
                decrypted = decrypt(encrypted, shared_secret)
                print(f"Decrypted message: {decrypted}")
                
            except Exception as e:
                print(f"Error handling connection: {e}")
            finally:
                conn.close()
    except Exception as e:
        print(f"Server error: {e}")
    finally:
        server.close()

if __name__ == "__main__":
    main()