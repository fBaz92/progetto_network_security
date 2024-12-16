# RSA Encryption Demo Project

This project demonstrates RSA encryption algorithm through a client-server communication between two entities: Alice (sender) and Bob (receiver).

## Description

The project implements a secure communication system where:

- **Alice** (client) encrypts and sends messages using Bob's public key
- **Bob** (server) receives and decrypts messages using his private key

The system displays every step of the encryption process, including ASCII and binary message representations, making it ideal for educational and demonstration purposes.

## Prerequisites

- Python 3.6 or higher
- Socket library (included in Python standard library)
- argparse library (included in Python standard library)

## Project Structure

```
.
├── README.md
├── alice.py    # Client for sending encrypted messages
└── bob.py      # Server for receiving and decrypting
```

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd rsa-encryption-demo
```

2. No additional dependencies needed as the project uses only Python standard libraries.

## Usage

1. First, start Bob (the server):

```bash
python bob.py
```

2. In a new terminal, run Alice (the client) to send a message:

```bash
python alice.py -m Hello world
```

### Alice Options

- `--message` or `-m`: Specify the message to send (default: "Hello world")
  - You can send multiple words: `python alice.py -m This is a longer message`

## Technical Details

### RSA Parameters

- Prime numbers used: p = 61, q = 53
- Public exponent: e = 17
- The modulus n and private exponent d are calculated automatically

### Encryption Process

1. Text to ASCII conversion
2. RSA encryption of each character
3. Binary representation conversion for visualization
4. Encrypted message transmission

### Sample Output

```
Original message: Hello world
ASCII values: [72, 101, 108, 108, 111, 32, 119, 111, 114, 108, 100]
Encrypted message: [2012, 2981, 2645, 2645, 2981, 2012, 1209, 2981, 2645, 2645, 2981]
Binary representation: ['11111100100', '101110100101', ...]
```

## Security Notes

This is a demonstration project and uses very small keys for simplicity. In a production environment:

- Use keys of at least 2048 bits
- Implement proper padding
- Use certified cryptographic libraries like `pycryptodome`

## Troubleshooting

- If you receive "Connection Refused", ensure bob.py is running before alice.py
- To terminate the server (Bob), use Ctrl+C
- Verify that port 5000 is available on your system

## License

[Insert chosen license for the project]
