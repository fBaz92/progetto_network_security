# Secure Communication System with RSA and Diffie-Hellman

## Overview

This project implements a secure communication system between two parties (Alice and Bob) with different implementation variants:

1. **Complete Version**: Full implementation with:

   - RSA encryption for message security
   - Diffie-Hellman key exchange protocol
   - Certificate Authority (CA) for identity verification
   - Network sockets for communication

2. **Simple RSA Version** (`simple_RSA/`):

   - Basic implementation focusing only on RSA encryption
   - Direct message exchange without CA or DH
   - Simplified socket communication

3. **DH-RSA Version** (`DH_RSA/`):
   - Combined implementation using Diffie-Hellman for key exchange
   - RSA for message encryption
   - No Certificate Authority
   - Intermediate complexity level

## Project Structure

```
.
├── alice.py              # Client implementation (message sender)
├── bob.py               # Server implementation (message receiver)
├── ca.py                # Certificate Authority implementation
├── certificates.py      # Certificate class and utilities
├── config.py           # Network configuration
├── launch_ca.py        # CA server launcher
├── shared_protocol.py  # Shared cryptographic protocols
│
├── simple_RSA/         # Simple RSA implementation
│   ├── alice.py       # Simple RSA client
│   ├── bob.py         # Simple RSA server
│
├── DH_RSA/            # Diffie-Hellman with RSA implementation
│   ├── alice.py       # DH-RSA client
│   ├── bob.py        # DH-RSA server
│   └── shared_protocol.py         # DH implementation
│
└── README.md          # This file
```

## Requirements

- Python 3.8+
- No additional Python packages required (uses standard library only)

## Implementation Variants

### 1. Complete Version

- Full security implementation with CA, DH, and RSA
- Suitable for understanding complete secure communication flow
- Includes certificate management and validation
- Most complex but most secure variant

### 2. Simple RSA Version

- Basic RSA encryption/decryption
- Direct socket communication
- No key exchange protocol or certificates
- Perfect for learning basic cryptographic concepts

### 3. DH-RSA Version

- Combines Diffie-Hellman key exchange with RSA
- More secure than simple RSA but simpler than full version
- Good middle ground for learning both protocols

## Usage

### Complete Version

1. Start the Certificate Authority:

```bash
python launch_ca.py
```

2. Start Bob (Receiver):

```bash
python bob.py
```

3. Send Messages with Alice:

```bash
python alice.py
# or with custom message:
python alice.py -m Your message here
```

### Simple RSA Version

1. Start Bob:

```bash
cd simple_RSA
python bob.py
```

2. Send message with Alice:

```bash
cd simple_RSA
python alice.py
```

### DH-RSA Version

1. Start Bob:

```bash
cd DH_RSA
python bob.py
```

2. Send message with Alice:

```bash
cd DH_RSA
python alice.py
```

## Security Notes

This is an educational implementation to demonstrate cryptographic concepts. For production use, you would need:

### RSA Implementation (all versions)

- Larger prime numbers (1024+ bits)
- Secure prime number generation
- Proper padding (PKCS#1 v2.0 / OAEP)
- Message segmentation for long texts

### Diffie-Hellman (Complete and DH-RSA versions)

- Larger parameters
- Proper parameter validation
- Ephemeral key exchange

### Certificate Authority (Complete version only)

- Robust certificate management
- Proper certificate revocation
- Secure storage of CA keys
- Strong signature algorithms

## Ports Used

- CA Server (Complete version): 4999
- Bob's Server: 5003 (all versions)
- Alice connects to Bob's port

## Error Handling

- Certificate validation failures (Complete version)
- Connection errors
- Invalid message formats
- Encryption/decryption errors

## Author

Francesco Bazzani
