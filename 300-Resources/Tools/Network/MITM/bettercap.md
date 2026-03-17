---
tags: [tool, network, mitm]
tool: "bettercap"
category: "Network MITM"
installed: true
phase: [post-exploit, mitm]
---

# bettercap - Modern MITM Framework

## Overview
Advanced MITM framework with modules

## Location
/usr/bin/bettercap

## Basic Usage
sudo bettercap
sudo bettercap -eval "set arp.spoof.targets 192.168.1.100; arp.spoof on; net.sniff on"

## Web UI
sudo bettercap -eval "set api.rest.username admin; set api.rest.password admin; api.rest on; ui"

## Related Tools
ettercap, dsniff
