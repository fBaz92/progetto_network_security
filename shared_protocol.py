# shared_protocol.py
from typing import Tuple
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
    
    # Default values for p and g. 
    DEFAULT_P = 23 
    DEFAULT_G = 5  
    
    def __init__(self, p=DEFAULT_P, g=DEFAULT_G):
        self.p = p
        self.g = g
        self._private_key = random.randint(2, p-1)
        self.public_key = pow(g, self._private_key, p)
    
    def generate_shared_secret(self, other_public_key: int) -> int:
        return pow(other_public_key, self._private_key, self.p)
