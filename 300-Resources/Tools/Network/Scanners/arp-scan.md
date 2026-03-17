---
tags: [tool, network, arp]
tool: "arp-scan"
category: "Network Scanner"
installed: true
phase: [recon]
---

# arp-scan - ARP Scanner

## Overview
Send ARP requests to discover local hosts

## Location
/usr/bin/arp-scan

## Basic Usage
sudo arp-scan --localnet
sudo arp-scan 192.168.1.0/24

## Common Options
--localnet : Scan local network
--interface : Network interface
--retry : Retry count

## Related Tools
netdiscover, nmap
