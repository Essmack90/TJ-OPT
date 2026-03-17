---
tags: [tool, python, packet]
tool: "scapy"
category: "Network Python"
installed: true
phase: [exploit, analysis]
---

# Scapy - Packet Manipulation

## Overview
Python library for packet manipulation

## Location
/usr/bin/scapy

## Basic Usage
sudo scapy
>>> IP(dst="google.com")/ICMP()
>>> sr1(IP(dst="8.8.8.8")/ICMP())
>>> sniff(count=10)

## Common Functions
sr() : Send and receive
sniff() : Capture packets
wrpcap() : Write to PCAP
rdpcap() : Read PCAP

## Related Tools
pcapy, dpkt
