---
tags: [tool, network, performance]
tool: "iperf3"
category: "Network Performance"
installed: true
phase: [post-exploit]
---

# iperf3 - Network Bandwidth Test

## Overview
Measure maximum TCP/UDP bandwidth

## Location
/usr/bin/iperf3

## Basic Usage
iperf3 -s (server)
iperf3 -c server-ip (client)
iperf3 -c server-ip -u (UDP)
iperf3 -c server-ip -P 4 (parallel)

## Common Options
-s : Server mode
-c : Client mode
-u : UDP test
-P : Parallel streams

## Related Tools
nuttcp, qperf
