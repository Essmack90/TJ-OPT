---
tags: [tool, network, mitm]
tool: "filesnarf"
category: "Network MITM"
installed: true
phase: [post-exploit, mitm]
---

# filesnarf - File Sniffer

## Overview
Capture NFS files from the network

## Location
/usr/sbin/filesnarf

## Basic Usage
sudo filesnarf -i eth0

## Common Options
-i : Interface
-n : No DNS resolution

## Related Tools
dsniff, urlsnarf
