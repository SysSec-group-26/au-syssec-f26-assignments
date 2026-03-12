import struct
import socket
import os

ICMP_ECHO_REQUEST = 8

def calculate_checksum( data):
  checksum = 0

  # Handle odd-length data
  if len(data) % 2 != 0:
      data += b"\x00"

  # Calculate checksum
  for i in range(0, len(data), 2):
      checksum += (data[i] << 8) + data[i+1]

  checksum = (checksum >> 16) + (checksum & 0xffff)
  checksum += checksum >> 16

  return (~checksum) & 0xffff 


def create_packet(payload: bytes) -> bytes:
    pid = os.getpid() & 0xFFFF
    header = struct.pack("!BBHHH", ICMP_ECHO_REQUEST, 0, 0, pid, 1)

    chksum = calculate_checksum(header + payload)

    header = struct.pack("!BBHHH", ICMP_ECHO_REQUEST, 0, chksum, pid, 1)
    print("header", header)
    return header + payload


sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)

HOST = "127.0.0.1"

while True:
    message = input('Enter the message: ')
    payload = bytes(message.encode())
    packet = create_packet(payload)
    sock.sendto(packet, (HOST, 0))
    print('ICMP packet sent!')
    
