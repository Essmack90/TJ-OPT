---
tags: [tool, network, scanner]
tool: "masscan"
category: "Network Scanner"
installed: true
phase: [recon]
---

# masscan - Mass IP Port Scanner

## Overview
Fastest port scanner, can scan entire internet

## Location
/usr/bin/masscan

## Basic Usage
masscan -p80 192.168.1.0/24
masscan --rate=1000 -p1-1000 192.168.1.1

## Common Options
--rate : Packets per second
-oJ : JSON output
--banners : Grab service banners

## Related Tools
nmap, rustscan
