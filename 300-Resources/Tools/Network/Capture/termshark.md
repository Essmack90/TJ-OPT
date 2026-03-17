---
tags: [tool, network, capture]
tool: "termshark"
category: "Network Capture"
installed: true
phase: [analysis]
---

# termshark - TUI Wireshark

## Overview
Terminal UI for Wireshark

## Location
/usr/bin/termshark

## Basic Usage
sudo termshark -i eth0
termshark -r capture.pcap
termshark -r capture.pcap -Y "http"

## Navigation
Tab : Switch panes
Enter : Expand packet
/ : Search
q : Quit

## Related Tools
wireshark, tcpdump, tshark
