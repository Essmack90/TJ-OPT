---
tags: [tool, network, mitm]
tool: "msgsnarf"
category: "Network MITM"
installed: true
phase: [post-exploit, mitm]
---

# msgsnarf - Message Sniffer

## Overview
Capture chat messages from the network

## Location
/usr/sbin/msgsnarf

## Basic Usage
sudo msgsnarf -i eth0

## Common Options
-i : Interface
-n : No DNS resolution

## Related Tools
dsniff, urlsnarf
