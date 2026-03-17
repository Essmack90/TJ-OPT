---
tags: [tool, network, monitor]
tool: "iftop"
category: "Network Performance"
installed: true
phase: [analysis]
---

# iftop - Bandwidth Monitoring

## Overview
Display bandwidth usage on an interface

## Location
/usr/sbin/iftop

## Basic Usage
sudo iftop
sudo iftop -i eth0
sudo iftop -n

## Common Options
-i : Interface
-n : No DNS resolution
-B : Show in bytes

## Related Tools
nethogs, iptraf-ng
