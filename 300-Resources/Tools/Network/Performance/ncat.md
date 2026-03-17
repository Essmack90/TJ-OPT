---
tags: [tool, network, netcat]
tool: "ncat"
category: "Network Performance"
installed: true
phase: [all]
---

# ncat - Enhanced Netcat

## Overview
Netcat with SSL support

## Location
/usr/bin/ncat

## Basic Usage
ncat -lvnp 4444
ncat target 4444
ncat -lvnp 4444 --ssl
ncat target 4444 --ssl

## Common Options
-l : Listen
-v : Verbose
-n : No DNS
-p : Port
--ssl : SSL mode

## Related Tools
nc, socat
