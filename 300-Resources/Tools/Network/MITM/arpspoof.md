---
tags: [tool, network, mitm]
tool: "arpspoof"
category: "Network MITM"
installed: true
phase: [post-exploit, mitm]
---

# arpspoof - ARP Spoofing

## Overview
Redirect packets on a LAN through your machine

## Location
/usr/sbin/arpspoof

## Basic Usage
sudo arpspoof -i eth0 -t 192.168.1.100 192.168.1.1
sudo arpspoof -i eth0 192.168.1.1

## Common Options
-i : Interface
-t : Target IP
host : Gateway or target

## Related Tools
dsniff, ettercap, bettercap
