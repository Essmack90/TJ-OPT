---
tags: [tool, network, scanner]
tool: "nmap"
category: "Network Scanner"
installed: true
phase: [recon]
---

# nmap - Network Mapper

## Overview
Network discovery and security auditing tool

## Location
/usr/bin/nmap

## Basic Usage
nmap -sC -sV target.com
nmap -p- -sV target.com
nmap -T4 -F target.com

## Common Options
-sC : Default scripts
-sV : Version detection
-p- : All ports
-O : OS detection
-A : Aggressive mode

## Related Tools
masscan, rustscan, naabu
