---
tags: [tool, network, utilities]
tool: "ethtool"
category: "Network Utilities"
installed: true
phase: [recon]
---

# ethtool - Ethernet Device Settings

## Overview
Query and control network driver settings

## Location
/usr/sbin/ethtool

## Basic Usage
ethtool eth0
ethtool -p eth0 (identify port)
ethtool -s eth0 speed 1000 duplex full

## Common Options
-p : Identify port
-s : Change settings
-i : Driver info

## Related Tools
mii-tool
