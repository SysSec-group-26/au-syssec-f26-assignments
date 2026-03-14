#!/usr/bin/env python3
import socket
from scapy.all import IP
import os
import struct
import fcntl
import select

TUNSETIFF = 0x400454CA
IFF_TUN = 0x0001
IFF_TAP = 0x0002
IFF_NO_PI = 0x1000

SERVER_IP = "0.0.0.0"
SERVER_PORT = 9090

# Create TUN interface
tun = os.open("/dev/net/tun", os.O_RDWR)
ifr = struct.pack("16sH", b"tun%d", IFF_TUN | IFF_NO_PI)
ifname_bytes = fcntl.ioctl(tun, TUNSETIFF, ifr)
ifname = ifname_bytes.decode("utf-8")[:16].strip("\x00")
print(f"Interface Name: {ifname}")

# Configure TUN interface on VPN server
os.system(f"ip addr add 192.168.53.1/24 dev {ifname}")
os.system(f"ip link set dev {ifname} up")

# Create UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((SERVER_IP, SERVER_PORT))

print(f"Listening on UDP {SERVER_IP}:{SERVER_PORT}")

ip, port = None, None

while True:
    # this will block until at least one interface is ready
    ready, _, _ = select.select([sock, tun], [], [])
    for fd in ready:
        if fd is sock:
            data, (cip, cport) = sock.recvfrom(2048)
            ip, port = cip, cport
            pkt = IP(data)
            print("From socket <==: {} --> {}".format(pkt.src, pkt.dst))

            os.write(tun, data)

        if fd is tun:
            packet = os.read(tun, 2048)
            if packet:
              pkt = IP(packet)
              print("From tun ==>: {} --> {}".format(pkt.src, pkt.dst))
              if ip is not None and port is not None:
                sock.sendto(packet, (ip, port))
