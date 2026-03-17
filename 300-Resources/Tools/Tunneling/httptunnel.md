---
tags: [tool, tunneling]
tool: httptunnel
category: Tunneling
installed: true
---

# httptunnel - HTTP Tunneling

## Overview
Tunnel TCP connections over HTTP

## Location
/usr/bin/hts (server)
/usr/bin/htc (client)

## Usage

### Server (Target network)
hts -F localhost:22 8888

### Client (Kali)
htc -F 2222 localhost:8888

### Connect via tunnel
ssh -p 2222 localhost
