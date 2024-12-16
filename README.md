# Secure Message Exchange System with RSA and Diffie-Hellman

## Overview

This project implements a secure message exchange system between two parties (Alice and Bob) using RSA encryption with Diffie-Hellman key exchange. The communication happens over a network socket with the following features:

- Diffie-Hellman key exchange protocol for secure key sharing
- RSA encryption for message security
- Complete visualization of message transformation stages
- Command-line interface for message input

## Requirements

- Python 3.8 or higher
- No additional Python packages required (uses only standard library)

## Project Structure

```
.
├── shared_protocol.py  # Shared cryptographic protocols
├── alice.py           # Client implementation (message sender)
├── bob.py            # Server implementation (message receiver)
└── README.md
```

## How It Works

### Key Exchange Process

1. Bob starts a server waiting for connections
2. Alice initiates connection with Bob
3. Both parties generate Diffie-Hellman key pairs
4. They exchange public keys and generate a shared secret
5. The shared secret is used to derive RSA parameters

### Message Exchange

1. Alice encrypts her message using RSA
2. The encrypted message is sent to Bob
3. Bob decrypts the message using his private key
4. Both parties see the message transformation at each step

## Usage

### Starting Bob (Receiver)

```bash
python bob.py
```

Bob will wait for incoming connections.

### Sending Messages with Alice

Send default "Hello world" message:

```bash
python alice.py
```

Send custom message:

```bash
python alice.py -m your message here
```

Get help on available options:

```bash
python alice.py --help
```

## Message Transformation Stages

The system shows:

1. Original message
2. ASCII representation
3. Encrypted form
4. Binary representation
5. Decrypted message (on Bob's side)

## Implementation Details

- Uses Diffie-Hellman for secure key exchange
- RSA encryption with dynamically generated parameters
- Communication via local TCP sockets (localhost:5003)
- Shows message transformation at each step
- Command-line interface for flexible message input

## Security Note

This is an educational implementation designed to demonstrate cryptographic concepts. For production use, you would need:

- Larger prime numbers
- More secure parameter generation
- Additional security measures like:
  - Certificate validation
  - Message integrity checks
  - Proper key management
  - Protection against known attacks

## Troubleshooting

- Ensure Bob is running before starting Alice
- If port 5003 is in use, you may need to modify the port number in both files
- Check that all three python files are in the same directory

## Author

Francesco Bazzani
