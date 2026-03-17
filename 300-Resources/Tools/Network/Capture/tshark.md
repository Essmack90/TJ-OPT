---
tags: [tool, network, capture]
tool: "tshark"
category: "Network Capture"
installed: true
phase: [analysis]
---

# tshark - Terminal Wireshark

## Overview
Command-line version of Wireshark

## Location
/usr/bin/tshark

## Basic Usage
tshark -i eth0
tshark -r capture.pcap
tshark -Y "http" -r capture.pcap

## Common Options
-i : Interface
-r : Read from file
-Y : Display filter
-T : Output format

## Related Tools
wireshark, tcpdump, termshark
