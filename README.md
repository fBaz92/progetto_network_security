# Secure Communication System with RSA, Diffie-Hellman, and Certificate Authority

## Overview

This project implements a secure communication system between two parties (Alice and Bob) using:

- RSA encryption for message security
- Diffie-Hellman key exchange protocol
- Certificate Authority (CA) for identity verification
- Network sockets for communication

## Features

- Certificate-based authentication
- Secure key exchange using Diffie-Hellman
- Message encryption using RSA
- Command-line interface for message input
- Complete message transformation visualization

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
└── README.md           # This file
```

## Requirements

- Python 3.8+
- No additional Python packages required (uses standard library only)

## How It Works

### Certificate Authority (CA)

- Issues digital certificates to verify identities
- Signs certificates using RSA
- Verifies certificates during communication
- Runs on port 4999

### Communication Flow

1. CA server starts and waits for certificate requests
2. Bob starts and listens for incoming connections
3. Alice initiates connection to Bob
4. Both parties obtain certificates from CA
5. Certificate exchange and validation occurs
6. Diffie-Hellman key exchange is performed
7. Shared secret is used to generate RSA parameters
8. Message is encrypted and sent from Alice to Bob
9. Bob decrypts and displays the message

## Usage

### 1. Start the Certificate Authority

```bash
python launch_ca.py
```

### 2. Start Bob (Receiver)

```bash
python bob.py
```

### 3. Send Messages with Alice

Send default "Hello world" message:

```bash
python alice.py
```

Send custom message:

```bash
python alice.py -m Your message here
```

View help:

```bash
python alice.py --help
```

## Security Notes

This is an educational implementation to demonstrate cryptographic concepts. For production use, you would need:

### RSA Implementation

- Larger prime numbers (1024+ bits)
- Secure prime number generation
- Proper padding (PKCS#1 v2.0 / OAEP)
- Message segmentation for long texts

### Diffie-Hellman

- Larger parameters
- Proper parameter validation
- Ephemeral key exchange

### Certificate Authority

- Robust certificate management
- Proper certificate revocation
- Secure storage of CA keys
- Strong signature algorithms

## Ports Used

- CA Server: 4999
- Bob's Server: 5003
- Alice connects to Bob's port

## Error Handling

- Certificate validation failures
- Connection errors
- Invalid message formats
- Encryption/decryption errors

## Future Improvements

- Implement proper RSA padding
- Add certificate revocation
- Improve key generation security
- Add message integrity checks
- Implement session management
- Add proper error recovery

## Author

Francesco Bazzani

## License

This project is for educational purposes only.
