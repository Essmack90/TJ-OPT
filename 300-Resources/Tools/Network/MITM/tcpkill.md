---
tags: [tool, network, mitm]
tool: "tcpkill"
category: "Network MITM"
installed: true
phase: [post-exploit, mitm]
---

# tcpkill - Kill TCP Connections

## Overview
Forcibly terminate TCP connections

## Location
/usr/sbin/tcpkill

## Basic Usage
sudo tcpkill -i eth0 port 80
sudo tcpkill -i eth0 host 192.168.1.100

## Common Options
-i : Interface
port : Port to target
host : Host to target

## Related Tools
dsniff, tcpnice
