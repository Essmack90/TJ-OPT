---
tags: [tool, network, capture]
tool: "netsniff-ng"
category: "Network Capture"
installed: true
phase: [analysis]
---

# netsniff-ng - Network Sniffer

## Overview
High-performance network sniffer

## Location
/usr/bin/netsniff-ng

## Basic Usage
sudo netsniff-ng --in eth0
sudo netsniff-ng --in eth0 --out capture.pcap

## Common Options
--in : Input interface
--out : Output file
--bind-cpu : Bind to CPU

## Related Tools
tcpdump, wireshark
