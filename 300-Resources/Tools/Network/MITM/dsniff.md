---
tags: [tool, network, mitm]
tool: "dsniff"
category: "Network MITM"
installed: true
phase: [post-exploit, mitm]
---

# dsniff - Network Sniffing Toolkit

## Overview
Suite of sniffing tools for penetration testing

## Location
/usr/bin/dsniff

## Included Tools
dsniff - Password sniffer
arpspoof - ARP spoofing
dnsspoof - DNS spoofing
urlsnarf - URL capture
msgsnarf - Message capture
filesnarf - File capture
tcpkill - Kill TCP connections

## Basic Usage
sudo arpspoof -i eth0 -t target gateway
sudo dsniff -i eth0
sudo urlsnarf -i eth0
sudo tcpkill -i eth0 port 80

## Related Tools
ettercap, bettercap
