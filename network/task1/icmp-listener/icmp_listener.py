
import socket
import struct 
from cryptography.fernet import Fernet
import os
import sys

PROTOCOL_MAP = {
    1 : 'ICMP',
    6 : 'TCP',
    17: 'UDP'
}

if not os.getenv('SHARED_KEY'):
    from dotenv import load_dotenv
    load_dotenv()
 
SHARED_KEY = os.getenv('SHARED_KEY').encode()


def get_protocol_type_and_offset(header: bytes):
    iph = struct.unpack('!BBHHHBBH4s4s', header)
    
    version_ihl = iph[0]
    ihl = version_ihl & 0xF

    # Calculate IP header length in bytes
    iph_length = ihl * 4
    protocol_num = iph[6]
    if protocol_num in PROTOCOL_MAP:
        return (PROTOCOL_MAP[protocol_num], iph_length)
    return (protocol_num, iph_length)
    

if __name__ == '__main__':
    
    # this is the name that Docker DNS associate to this container.
    if len(sys.argv) > 1:
        HOST = sys.argv[1]
    else:
        exit()
        
    PORT = 0

    # general_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    sock.bind((HOST, PORT))
    # general_sock.connect((HOST, PORT))

    
    print("Listening to", HOST)

    cipher = Fernet(SHARED_KEY)

    while True:
        data, addr = sock.recvfrom(1024)
        print('data:', data)
        print('datalen:', len(data))
        ip_header = data[:20]
        protocol_type, offset = get_protocol_type_and_offset(ip_header)
        print(f"Protocol: {protocol_type}")
        print(f'offset: {offset}')
        if protocol_type == "ICMP":
            try:
                ciphertext = data[offset + 4: ]
                # print(f'Encrypted Message: {ciphertext}')
                plaintext = cipher.decrypt(ciphertext)
                print(f'Decrypted Message: {plaintext}')
            except Exception as e:
                print("Error: ", e)
        else:
            print("Got a message that is not ICMP!")
            
        #######
        
        # data, addr = general_sock.recvfrom(1024)
        # if data:
        #     print("data recieved from general:", data.decode('utf-8'))

