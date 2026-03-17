---
tags: [tool, network, scanner]
tool: "unicornscan"
category: "Network Scanner"
installed: true
phase: [recon]
---

# unicornscan - Advanced Port Scanner

## Overview
Asynchronous TCP/UDP port scanner

## Location
/usr/bin/unicornscan

## Basic Usage
unicornscan target.com
unicornscan -mT 192.168.1.1

## Common Options
-mT : TCP scan
-mU : UDP scan
-v : Verbose

## Related Tools
nmap, masscan
