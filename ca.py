import socket
from certificates import Certificate
from datetime import datetime, timedelta
from typing import Dict, Tuple
import json
from config import NetworkConfig
import base64

class CertificateAuthority:
    """Certificate Authority for issuing and verifying certificates"""
    
    def __init__(self):
        # Use fixed keys for demo purposes
        self.private_key = (53, 77)  # d, n
        self.public_key = (17, 77)   # e, n
        self.issued_certificates: Dict[str, Certificate] = {}

    def calculate_hash(self, message: str) -> int:
        """Calculate a simple hash of the message"""
        hash_value = 0
        for byte in message.encode('utf-8'):
            hash_value = (hash_value * 31 + byte) % 77  # Use n as modulus
        return hash_value

    def sign(self, message: str) -> str:
        """Sign a message using CA's private key"""
        try:
            d, n = self.private_key
            # Calculate hash
            message_hash = self.calculate_hash(message)
            print(f"Message hash before signing: {message_hash}")
            
            # Sign hash
            signature = pow(message_hash, d, n)
            print(f"Generated signature: {signature}")
            
            return base64.b64encode(str(signature).encode()).decode()
        except Exception as e:
            print(f"Error in signing: {e}")
            raise

    def verify_signature(self, message: str, signature: str) -> bool:
        """Verify a signature"""
        try:
            e, n = self.public_key
            # Decode signature
            signature_value = int(base64.b64decode(signature).decode())
            print(f"Received signature value: {signature_value}")
            
            # Decrypt signature
            decrypted = pow(signature_value, e, n)
            print(f"Decrypted signature: {decrypted}")
            
            # Calculate hash
            message_hash = self.calculate_hash(message)
            print(f"Calculated message hash: {message_hash}")
            
            return decrypted == message_hash
        except Exception as e:
            print(f"Error in verification: {e}")
            return False

    def issue_certificate(self, subject: str, public_key: Tuple[int, int]) -> Certificate:
        """Issue a new certificate for a subject"""
        print(f"\nIssuing new certificate for {subject}")
        cert = Certificate(
            subject=subject,
            public_key=public_key,
            issuer="TrustedCA",
            valid_from=datetime.now(),
            valid_until=datetime.now() + timedelta(days=365)
        )
        
        # Sign the certificate
        cert_string = cert.to_string()
        print(f"Certificate data to sign: {cert_string}")
        cert.signature = self.sign(cert_string)
        print(f"Final signature: {cert.signature}")
        
        # Store the certificate
        self.issued_certificates[subject] = cert
        return cert

    def verify_certificate(self, cert: Certificate) -> bool:
        """Verify a certificate's validity and signature"""
        print(f"\nVerifying certificate for {cert.subject}")
        
        # Check expiration
        if cert.valid_until < datetime.now():
            print("Certificate expired")
            return False
            
        # Verify signature
        cert_string = cert.to_string()
        print(f"Verifying signature for: {cert_string}")
        print(f"With signature: {cert.signature}")
        
        is_valid = self.verify_signature(cert_string, cert.signature)
        print(f"Signature verification result: {is_valid}")
        return is_valid

def run_ca_server():
    """Run the Certificate Authority server"""
    ca = CertificateAuthority()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((NetworkConfig.HOST, NetworkConfig.CA_PORT))
        server.listen(5)
        print(f"CA Server listening on {NetworkConfig.HOST}:{NetworkConfig.CA_PORT}")

        while True:
            conn, addr = server.accept()
            try:
                data = conn.recv(1024).decode()
                request = json.loads(data)
                
                if request["type"] == "issue":
                    cert = ca.issue_certificate(
                        request["subject"],
                        tuple(request["public_key"])
                    )
                    response = {"status": "success", "certificate": cert.to_dict()}
                elif request["type"] == "verify":
                    cert = Certificate.from_dict(request["certificate"])
                    is_valid = ca.verify_certificate(cert)
                    response = {"status": "success", "valid": is_valid}
                else:
                    response = {"status": "error", "message": "Unknown request type"}
                    
                conn.send(json.dumps(response).encode())
            except Exception as e:
                conn.send(json.dumps({"status": "error", "message": str(e)}).encode())
            finally:
                conn.close()
    except Exception as e:
        print(f"CA Server error: {e}")
    finally:
        server.close()

if __name__ == "__main__":
    run_ca_server()