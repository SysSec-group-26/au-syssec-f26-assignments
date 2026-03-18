#!/bin/bash
# set iptables to filter any traffic that is not over ICMP
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT DROP
iptables -A INPUT -i lo -j ACCEPT
iptables -A OUTPUT -o lo -j ACCEPT
iptables -A INPUT -p icmp --icmp-type echo-request -j ACCEPT
iptables -A OUTPUT -p icmp -j ACCEPT

echo "iptables rules applied"
# Keep container running
tail -f /dev/null
