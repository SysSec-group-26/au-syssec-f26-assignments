#!/usr/bin/env python3

import fcntl
import struct
import os
import time
from scapy.layers.inet import IP
import socket
import select
import ssl

TUNSETIFF = 0x400454CA
IFF_TUN = 0x0001
IFF_TAP = 0x0002
IFF_NO_PI = 0x1000

SERVER_IP = "10.9.0.11"
SERVER_PORT = 9090

# Create the tun interface
tun = os.open("/dev/net/tun", os.O_RDWR)
ifr = struct.pack("16sH", b"tun%d", IFF_TUN | IFF_NO_PI)
ifname_bytes = fcntl.ioctl(tun, TUNSETIFF, ifr)

# Get the interface name
ifname = ifname_bytes.decode("UTF-8")[:16].strip("\x00")
print("Interface Name: {}".format(ifname))

os.system("ip route add 192.168.60.0/24 dev {}".format(ifname))
os.system("ip addr add 192.168.53.99/24 dev {}".format(ifname))
os.system("ip link set dev {} up".format(ifname))

context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
context.load_cert_chain("client-cert.pem", "client-key.pem")
context.load_verify_locations("ca-cert.pem")
context.check_hostname = False

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
conn = context.wrap_socket(sock)
conn.connect(("10.9.0.11", 9090))

print("TLS connection successul")

while True:
    # this will block until at least one interface is ready
    ready, _, _ = select.select([conn, tun], [], [])
    for fd in ready:
        if fd is conn:
            data = conn.recv(2048)
            if not data:
                break
            pkt = IP(data)
            print("From TLS <==: {} --> {}".format(pkt.src, pkt.dst))

            os.write(tun, data)

        if fd is tun:
            packet = os.read(tun, 2048)
            pkt = IP(packet)
            print("From tun ==>: {} --> {}".format(pkt.src, pkt.dst))

            conn.send(packet)
