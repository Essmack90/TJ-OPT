---
tags: [tool, network, mitm]
tool: "tcpnice"
category: "Network MITM"
installed: true
phase: [post-exploit, mitm]
---

# tcpnice - Slow Down TCP Connections

## Overview
Throttle TCP connections on a network

## Location
/usr/sbin/tcpnice

## Basic Usage
sudo tcpnice -i eth0 port 80

## Common Options
-i : Interface
port : Port to throttle

## Related Tools
dsniff, tcpkill
