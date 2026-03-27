import socket
import sys

HOST = 'general-listener'
PORT = 5005

sock =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    print(f'Trying to connect to {HOST}...')
    sock.settimeout(5)
    sock.connect((HOST, PORT))
    print(f'Managed to connect to outside-listener with a TCP connection!')
    sock.sendall(b"TCP hello from general-sender!")
except Exception as e:
    print(f"Error on connecting to {HOST}: {e}")

