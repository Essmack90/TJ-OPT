---
tags: [tool, network, mitm]
tool: "urlsnarf"
category: "Network MITM"
installed: true
phase: [post-exploit, mitm]
---

# urlsnarf - URL Sniffer

## Overview
Capture all HTTP requests on a network

## Location
/usr/sbin/urlsnarf

## Basic Usage
sudo urlsnarf -i eth0
sudo urlsnarf -i eth0 -n

## Common Options
-i : Interface
-n : No DNS resolution

## Related Tools
dsniff, msgsnarf
