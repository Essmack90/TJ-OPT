---
tags: [tool, network, scanner]
tool: "rustscan"
category: "Network Scanner"
installed: true
phase: [recon]
---

# rustscan - Fast Port Scanner

## Overview
Fast port scanner with nmap integration

## Location
~/.cargo/bin/rustscan

## Basic Usage
rustscan -a target.com
rustscan -a target.com -- -sV -sC
docker run -it --rm rustscan/rustscan:latest -a target.com

## Common Options
-a : Target address
-p : Ports to scan
-- : Pass args to nmap

## Related Tools
nmap, masscan
