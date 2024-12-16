import socket
import pickle
import struct
from typing import Any

def send_msg(sock: socket.socket, msg: Any) -> None:
    """Send a message using pickle serialization and length prefixing"""
    # Serialize the data
    serialized_data = pickle.dumps(msg)
    # Pack the length of the serialized data (using 8 bytes for the length)
    msg_len = struct.pack(">Q", len(serialized_data))
    # Send the length followed by the data
    sock.sendall(msg_len)
    sock.sendall(serialized_data)

def recv_msg(sock: socket.socket) -> Any:
    """Receive a message using pickle deserialization and length prefixing"""
    # Read message length (8 bytes)
    raw_msg_len = recvall(sock, 8)
    if not raw_msg_len:
        return None
    msg_len = struct.unpack(">Q", raw_msg_len)[0]
    
    # Read the message data
    serialized_data = recvall(sock, msg_len)
    if not serialized_data:
        return None
        
    # Deserialize and return
    return pickle.loads(serialized_data)

def recvall(sock: socket.socket, n: int) -> bytes:
    """Receive exactly n bytes from the socket"""
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(min(n - len(data), 4096))
        if not packet:
            return None
        data.extend(packet)
    return bytes(data)