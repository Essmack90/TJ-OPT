---
tags: [tool, network, capture]
tool: "wireshark"
category: "Network Capture"
installed: true
phase: [analysis]
---

# Wireshark - Network Protocol Analyzer

## Overview
GUI packet capture and analysis

## Location
/usr/bin/wireshark

## Basic Usage
wireshark
wireshark capture.pcap

## Common Filters
http
tcp.port == 80
ip.addr == 192.168.1.1

## Related Tools
tshark, tcpdump, termshark
