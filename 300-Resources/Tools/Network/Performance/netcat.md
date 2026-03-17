---
tags: [tool, network, netcat]
tool: "netcat"
category: "Network Performance"
installed: true
phase: [all]
---

# netcat - TCP/IP Swiss Army Knife

## Overview
Read and write data across network connections

## Location
/usr/bin/nc

## Basic Usage
nc -lvnp 4444 (listener)
nc target 4444 (connect)
nc target 80 (banner grab)

## Common Options
-l : Listen
-v : Verbose
-n : No DNS
-p : Port
-e : Execute program

## Related Tools
ncat, socat
