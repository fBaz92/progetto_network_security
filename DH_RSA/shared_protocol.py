import random

class DiffieHellman:
    # Default small prime numbers (should be way larger in production)
    DEFAULT_P = 23 # prime number
    DEFAULT_G = 5  # primitive generator p
    
    def __init__(self, p=DEFAULT_P, g=DEFAULT_G):
        self.p = p
        self.g = g
        self._private_key = random.randint(2, p-1)
        self.public_key = pow(g, self._private_key, p)
    
    def generate_shared_secret(self, other_public_key: int) -> int:
        return pow(other_public_key, self._private_key, self.p)

def is_prime(n: int) -> bool:
    """
    Parameters:
        n: int - number to check if prime
    Returns:
        bool - True if n is prime, False otherwise

    Toy implementation of primality test
    """
    if n < 2:
        # 1 is not prime
        return False
    
    # try all the possible divisors from 2 to sqrt(n)
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True