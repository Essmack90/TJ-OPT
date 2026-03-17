---
tags: [tool, network, capture]
tool: "tcpdump"
category: "Network Capture"
installed: true
phase: [analysis]
---

# tcpdump - Command-Line Packet Analyzer

## Overview
Capture and analyze network traffic

## Location
/usr/bin/tcpdump

## Basic Usage
sudo tcpdump -i eth0
sudo tcpdump -i eth0 -w capture.pcap
sudo tcpdump -i eth0 port 80 -A

## Common Options
-i : Interface
-w : Write to file
-r : Read from file
-A : ASCII output
-n : Don't resolve DNS

## Related Tools
wireshark, tshark, termshark
