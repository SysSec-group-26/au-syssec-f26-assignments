import struct
import socket
import os
from cryptography.fernet import Fernet
import sys

if not os.getenv('SHARED_KEY'):
    from dotenv import load_dotenv
    load_dotenv()
    
SHARED_KEY = os.getenv('SHARED_KEY').encode()

ICMP_TYPE = 47

def calculate_checksum( data):
  checksum = 0

  # Handle odd-length data by padding with byte 0
  if len(data) % 2 != 0:
      data += b"\x00"

  # Calculate checksum
  for i in range(0, len(data), 2):
      checksum += (data[i] << 8) + data[i+1]

  checksum = (checksum >> 16) + (checksum & 0xffff)
  checksum += checksum >> 16

  return (~checksum) & 0xffff 


def create_packet(payload: bytes) -> bytes:
    # compose header with checksum = 0
    header = struct.pack("!BBHHH", ICMP_TYPE, 0, 0, 0, 0)
    # calculate checksum
    checksum = calculate_checksum(header + payload)
    # add the checksum to the header
    header = struct.pack("!BBHHH", ICMP_TYPE, 0, checksum, 0, 0)
    # return the packet
    return header + payload


if __name__ == '__main__':
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    if len(sys.argv) > 1:
        CLIENT = sys.argv[1]
    else:
        exit()
    
    cipher = Fernet(SHARED_KEY)

    while True:
        message = input('Enter the message: ')
        encrypted_message = cipher.encrypt(bytes(message.encode()))
        packet = create_packet(encrypted_message)
        try:
            print(f'Sending to {(CLIENT, 0)} secret message {encrypted_message}...')
            sock.sendto(packet, (CLIENT, 0))
            print('ICMP packet sent!')
        except Exception as e:
            print("Error:", e)
        
