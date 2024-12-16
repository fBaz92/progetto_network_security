import socket
from certificates import Certificate
from datetime import datetime, timedelta
from typing import Dict, Tuple
import json
from config import NetworkConfig
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.exceptions import InvalidSignature
from network_utils import send_msg, recv_msg

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

class SecureCertificateAuthority:
    """A more secure Certificate Authority implementation using the cryptography library"""
    
    def __init__(self):
        # Generate a secure RSA key pair
        self._private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        self.public_key = self._private_key.public_key()
        self.issued_certificates: Dict[str, Certificate] = {}

    def sign(self, message: str) -> str:
        """Sign a message using secure RSA with SHA-256 and PSS padding"""
        try:
            # Convert message to bytes
            message_bytes = message.encode('utf-8')
            
            # Create the signature
            signature = self._private_key.sign(
                message_bytes,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            # Encode signature in base64 for transmission
            return base64.b64encode(signature).decode('utf-8')
            
        except Exception as e:
            print(f"Error in signing: {e}")
            raise

    def verify_signature(self, message: str, signature: str) -> bool:
        """Verify a signature using secure RSA with SHA-256 and PSS padding"""
        try:
            # Decode the base64 signature
            signature_bytes = base64.b64decode(signature.encode('utf-8'))
            message_bytes = message.encode('utf-8')
            
            # Verify the signature
            try:
                self.public_key.verify(
                    signature_bytes,
                    message_bytes,
                    padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH
                    ),
                    hashes.SHA256()
                )
                return True
            except InvalidSignature:
                return False
                
        except Exception as e:
            print(f"Error in verification: {e}")
            return False

    def issue_certificate(self, subject: str, public_key: tuple) -> Certificate:
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
        return self.verify_signature(cert_string, cert.signature)

def run_ca_server():
    """Run the Certificate Authority server"""
    ca = SecureCertificateAuthority()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        server.bind((NetworkConfig.HOST, NetworkConfig.CA_PORT))
        server.listen(5)
        print(f"Secure CA Server listening on {NetworkConfig.HOST}:{NetworkConfig.CA_PORT}")

        while True:
            conn, addr = server.accept()
            try:
                print(f"\nNew connection from {addr}")
                request = recv_msg(conn)
                
                if request["type"] == "issue":
                    cert = ca.issue_certificate(
                        request["subject"],
                        tuple(request["public_key"])
                    )
                    response = {
                        "status": "success",
                        "certificate": cert.to_dict()
                    }
                elif request["type"] == "verify":
                    cert = Certificate.from_dict(request["certificate"])
                    is_valid = ca.verify_certificate(cert)
                    response = {
                        "status": "success",
                        "valid": is_valid
                    }
                else:
                    response = {
                        "status": "error",
                        "message": "Unknown request type"
                    }
                
                send_msg(conn, response)
                
            except Exception as e:
                print(f"Error handling request: {e}")
                error_response = {
                    "status": "error",
                    "message": str(e)
                }
                send_msg(conn, error_response)
            finally:
                conn.close()
    except Exception as e:
        print(f"CA Server error: {e}")
    finally:
        server.close()

if __name__ == "__main__":
    run_ca_server()