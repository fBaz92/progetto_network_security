import socket
import json
from typing import Optional, Tuple
from certificates import Certificate
from config import NetworkConfig
import random
from network_utils import send_msg, recv_msg


class DiffieHellman:
    """
    Enhanced Diffie-Hellman key exchange protocol with larger parameters.
    """
    # Larger parameters for better security
    DEFAULT_P = 0xFFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74020BBEA63B139B22514A08798E3404DDEF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7EDEE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3DC2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F83655D23DCA3AD961C62F356208552BB9ED529077096966D670C354E4ABC9804F1746C08CA18217C32905E462E36CE3BE39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9DE2BCBF6955817183995497CEA956AE515D2261898FA051015728E5A8AACAA68FFFFFFFFFFFFFFFF
    DEFAULT_G = 2
    
    def __init__(self, p=DEFAULT_P, g=DEFAULT_G):
        self.p = p
        self.g = g
        # Aumentiamo il range per la chiave privata
        self._private_key = random.randint(2, p-1)
        self.public_key = pow(g, self._private_key, p)
    
    def generate_shared_secret(self, other_public_key: int) -> int:
        """Generate shared secret using the other party's public key"""
        return pow(other_public_key, self._private_key, self.p)

def exchange_certificates(sock, my_name: str, my_dh_public: int) -> Certificate:
    """Exchange and verify certificates with the other party"""
    print(f"Starting certificate exchange for {my_name}")
    
    # Get certificate from CA
    my_cert = get_certificate_from_ca(my_name, (my_dh_public, DiffieHellman.DEFAULT_P))
    if not my_cert:
        raise Exception("Failed to get certificate from CA")
    
    # Send certificate
    sock.send(json.dumps(my_cert.to_dict()).encode())
    
    # Receive other's certificate
    other_cert_data = json.loads(sock.recv(1024).decode())
    other_cert = Certificate.from_dict(other_cert_data)
    
    # Verify certificate
    if not verify_certificate_with_ca(other_cert):
        raise Exception("Invalid certificate received")
    
    return other_cert

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
        
        send_msg(sock, request)
        response = recv_msg(sock)
        
        if response["status"] == "success":
            return Certificate.from_dict(response["certificate"])
        print(f"Failed to get certificate: {response.get('message', 'Unknown error')}")
        return None
    except Exception as e:
        print(f"Error getting certificate from CA: {str(e)}")
        return None
    finally:
        sock.close()

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
        
        send_msg(sock, request)
        response = recv_msg(sock)
        
        return response.get("status") == "success" and response.get("valid", False)
    except Exception as e:
        print(f"Error during CA verification: {str(e)}")
        return False
    finally:
        sock.close()