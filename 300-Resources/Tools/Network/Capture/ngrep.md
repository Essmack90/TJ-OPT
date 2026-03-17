---
tags: [tool, network, capture]
tool: "ngrep"
category: "Network Capture"
installed: true
phase: [analysis]
---

# ngrep - Network Grep

## Overview
Grep for network traffic

## Location
/usr/bin/ngrep

## Basic Usage
sudo ngrep -d eth0
sudo ngrep -d eth0 -i "password"
sudo ngrep -d eth0 port 80

## Common Options
-d : Interface
-i : Case insensitive
-q : Quiet mode
-W : Output format

## Related Tools
tcpdump, grep
