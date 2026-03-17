---
tags: [tool, network, arp]
tool: "netdiscover"
category: "Network Scanner"
installed: true
phase: [recon]
---

# netdiscover - ARP Scanner

## Overview
ARP-based network discovery tool

## Location
/usr/sbin/netdiscover

## Basic Usage
sudo netdiscover -r 192.168.1.0/24
sudo netdiscover -p
sudo netdiscover -i eth0 -r 192.168.1.0/24

## Common Options
-r : Range to scan
-p : Passive mode
-i : Interface

## Related Tools
arp-scan, nmap
