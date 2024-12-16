import socket
import json
from typing import Optional, Tuple
from certificates import Certificate
from config import NetworkConfig
import random

class DiffieHellman:
    """
    Toy class to represent the Diffie-Hellman key exchange protocol.
    Attributes
    ----------
    p : int
        A prime number used as the modulus.
    g : int
        A primitive root modulo p.
    _private_key : int
        A randomly generated private key.
    public_key : int
        The public key generated from the private key.
    Methods
    -------
    generate_shared_secret(other_public_key: int) -> int
        Generates a shared secret using the other party's public key.
    """
    
    # Default parameters (would be much larger in production)
    DEFAULT_P = 23  # A prime number
    DEFAULT_G = 5   # A primitive root modulo p
    
    def __init__(self, p=DEFAULT_P, g=DEFAULT_G):
        self.p = p
        self.g = g
        self._private_key = random.randint(2, p-1)
        self.public_key = pow(g, self._private_key, p)
    
    def generate_shared_secret(self, other_public_key: int) -> int:
        """Generate shared secret using the other party's public key"""
        return pow(other_public_key, self._private_key, self.p)

def exchange_certificates(sock, my_name: str, my_dh_public: int):
    """Exchange and verify certificates with the other party"""
    print(f"Starting certificate exchange for {my_name}")  
    
    # Get your certificate from CA
    my_cert = get_certificate_from_ca(my_name, (my_dh_public, DiffieHellman.DEFAULT_P))
    if not my_cert:
        raise Exception("Failed to get certificate from CA")
    print(f"Got certificate from CA: {my_cert.to_dict()}")  
    
    # Send your certificate
    sock.send(json.dumps(my_cert.to_dict()).encode())
    print("Sent my certificate") 
    
    # Receive other's certificate
    other_cert_data = json.loads(sock.recv(1024).decode())
    print(f"Received certificate: {other_cert_data}")  
    other_cert = Certificate.from_dict(other_cert_data)
    
    # Verify received certificate
    print("Verifying received certificate...")  
    if not verify_certificate_with_ca(other_cert):
        raise Exception("Invalid certificate received")
    
    return other_cert

def verify_certificate_with_ca(cert: Certificate) -> bool:
    """Verify a certificate with the CA"""
    try:
        print(f"\nVerifying certificate with CA for subject: {cert.subject}")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((NetworkConfig.HOST, NetworkConfig.CA_PORT))
        
        request = {
            "type": "verify",
            "certificate": cert.to_dict()
        }
        print(f"Sending verification request to CA: {json.dumps(request, indent=2)}")
        sock.send(json.dumps(request).encode())
        
        response = json.loads(sock.recv(1024).decode())
        print(f"CA verification response: {json.dumps(response, indent=2)}")
        return response.get("valid", False)
    except Exception as e:
        print(f"Error during CA verification: {str(e)}")
        return False
    finally:
        sock.close()

def get_certificate_from_ca(subject: str, public_key: Tuple[int, int]) -> Optional[Certificate]:
    """Request a new certificate from the CA"""
    try:
        print(f"\nRequesting certificate from CA for {subject}")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((NetworkConfig.HOST, NetworkConfig.CA_PORT))
        
        request = {
            "type": "issue",
            "subject": subject,
            "public_key": list(public_key)
        }
        print(f"Sending certificate request: {json.dumps(request, indent=2)}")
        sock.send(json.dumps(request).encode())
        
        response = json.loads(sock.recv(1024).decode())
        print(f"CA response for certificate request: {json.dumps(response, indent=2)}")
        
        if response["status"] == "success":
            cert = Certificate.from_dict(response["certificate"])
            print(f"Successfully created certificate for {subject}")
            return cert
        print(f"Failed to get certificate: {response.get('message', 'Unknown error')}")
        return None
    except Exception as e:
        print(f"Error getting certificate from CA: {str(e)}")
        return None
    finally:
        sock.close()