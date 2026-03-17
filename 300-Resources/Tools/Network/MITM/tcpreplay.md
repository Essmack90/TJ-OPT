---
tags: [tool, network, mitm]
tool: "tcpreplay"
category: "Network MITM"
installed: true
phase: [post-exploit, mitm]
---

# tcpreplay - Replay PCAP Files

## Overview
Replay network traffic from capture files

## Location
/usr/bin/tcpreplay

## Basic Usage
sudo tcpreplay -i eth0 capture.pcap
sudo tcpreplay --loop=10 -i eth0 capture.pcap

## Common Options
-i : Interface
--loop : Number of times to replay
-M : Mbps speed limit

## Related Tools
tcprewrite, tcpdump
