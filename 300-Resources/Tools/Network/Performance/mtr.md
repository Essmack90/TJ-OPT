---
tags: [tool, network, traceroute]
tool: "mtr"
category: "Network Performance"
installed: true
phase: [recon]
---

# mtr - Traceroute + Ping

## Overview
Network diagnostic tool combining traceroute and ping

## Location
/usr/bin/mtr

## Basic Usage
mtr target.com
mtr -r target.com (report)
mtr --tcp target.com
mtr -c 10 --csv target.com

## Common Options
-r : Report mode
-c : Packet count
-n : No DNS resolution
--tcp : TCP mode

## Related Tools
traceroute, ping
