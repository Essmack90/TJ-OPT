---
tags: [tool, network, capture]
tool: "pcaputils"
category: "Network Capture"
installed: true
phase: [analysis]
---

# pcaputils - PCAP Utilities

## Overview
Collection of utilities for working with PCAP files

## Included Tools
capinfos - Show info about capture files
editcap - Edit capture files
mergecap - Merge capture files

## Basic Usage
capinfos capture.pcap
editcap -c 1000 capture.pcap out.pcap
mergecap -w merged.pcap file1.pcap file2.pcap

## Related Tools
wireshark, tshark
