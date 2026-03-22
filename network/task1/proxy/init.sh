#!/bin/bash
# set iptables to filter any traffic that is not over ICMP

# drop all the previous policies
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT DROP

# allow traffic to go in and out via the loopback interface. 
# this is done for the services behind proxy to be solved by
# local_net DNS.
iptables -A INPUT -i lo -j ACCEPT
iptables -A OUTPUT -o lo -j ACCEPT

# Allow in and out traffic for ICMP packets.
iptables -A INPUT -p icmp -j ACCEPT
iptables -A OUTPUT -p icmp -j ACCEPT

echo "iptables rules applied"
# Keep container running
tail -f /dev/null
