---
tags: [tool, network, scanner]
tool: "naabu"
category: "Network Scanner"
installed: true
phase: [recon]
---

# naabu - Fast Port Scanner (ProjectDiscovery)

## Overview
Fast port scanner written in Go

## Location
/usr/bin/naabu

## Basic Usage
naabu -host target.com
naabu -host target.com -top-ports 1000

## Common Options
-host : Target host
-top-ports : Top N ports
-port : Specific ports

## Related Tools
nmap, masscan, rustscan
