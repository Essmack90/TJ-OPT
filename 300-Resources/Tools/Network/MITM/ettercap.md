---
tags: [tool, network, mitm]
tool: "ettercap"
category: "Network MITM"
installed: true
phase: [post-exploit, mitm]
---

# ettercap - MITM Attack Suite

## Overview
Comprehensive MITM attack framework

## Location
/usr/bin/ettercap

## Basic Usage
sudo ettercap -G
sudo ettercap -T -M arp:remote /target// /gateway//

## Common Plugins
dns_spoof : DNS spoofing
remote_browser : Browser control

## Related Tools
dsniff, bettercap
