
import socket
import struct 
import ctypes

# this stuff I took from internet to parse the IP header
class IP(ctypes.Structure):
    _fields_= [
        ("ihl",          ctypes.c_ubyte, 4),
        ("version",      ctypes.c_ubyte, 4),
        ("tos",          ctypes.c_ubyte),
        ("len",          ctypes.c_ushort),
        ("id",           ctypes.c_ushort),
        ("offset",       ctypes.c_ushort),
        ("ttl",          ctypes.c_ubyte),
        ("protocol_num", ctypes.c_ubyte),
        ("sum",          ctypes.c_ushort),
        ("src",          ctypes.c_uint32),
        ("dst",          ctypes.c_uint32)
    ]

    def __new__(cls, socket_buffer=None):
        return cls.from_buffer_copy(socket_buffer)
    
    def __init__(self, socket_buffer=None):
        self.socket_buffer = socket_buffer

        # map protocol constats to their names
        self.protocol_map = {1: "ICMP", 6: "TCP", 17:"UDP"}

        # human readable IP addresses
        self.src_address = socket.inet_ntoa(struct.pack("@I", self.src))
        self.dst_address = socket.inet_ntoa(struct.pack("@I", self.dst))

        # human readable protocol
        try:
            self.protocol = self.protocol_map[self.protocol_num]
        except IndexError:
            self.protocol = str(self.protocol_num)


# this stuff I took from internet to parse the ICMP header
class ICMP(ctypes.Structure):
    _fields_= [
        ("type",         ctypes.c_ubyte),
        ("code",         ctypes.c_ubyte),
        ("checksum",     ctypes.c_ushort),
        ("unused",       ctypes.c_ushort),
        ("next_hop_mtu", ctypes.c_ushort)
    ]

    def __new__(cls, socket_buffer):
        return cls.from_buffer_copy(socket_buffer)

    def __init__(self, socket_buffer):
        self.socket_buffer = socket_buffer


HOST = "127.0.0.1"
PORT = 0

sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
sock.bind((HOST, PORT))

print("Listening on port", PORT)

while True:
    data, addr = sock.recvfrom(1024)
    ip_header = IP(data[:20])
    print(f"Protocol: {ip_header.protocol}, {ip_header.src_address} -> {ip_header.dst_address}")
    if ip_header.protocol == "ICMP":
        # find where our ICMP packet starts
        # print('ihl', ip_header.ihl)
        offset = ip_header.ihl * 4 # ihl is internet header length, number of words (32 bits), the min value is 5 * 32 = 20 bytes
        
        buf = data[offset:offset + ctypes.sizeof(ICMP)]
        icmp_header = ICMP(buf)

        print(f"ICMP -> Type: {icmp_header.type}, {icmp_header.code}")
        payload = data[offset + ctypes.sizeof(ICMP) : ]
        print('Message:', payload)
