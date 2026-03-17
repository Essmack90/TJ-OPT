---
tags: [tool, network, monitor]
tool: "tcptrack"
category: "Network Performance"
installed: true
phase: [analysis]
---

# tcptrack - TCP Connection Monitor

## Overview
Monitor TCP connections in real-time

## Location
/usr/bin/tcptrack

## Basic Usage
sudo tcptrack -i eth0
sudo tcptrack -i eth0 port 80

## Common Options
-i : Interface
port : Filter by port
-r : Resolution mode

## Related Tools
iftop, nethogs
