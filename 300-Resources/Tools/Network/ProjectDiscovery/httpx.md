---
tags: [tool, http, probe]
tool: "httpx"
category: "Network ProjectDiscovery"
installed: true
phase: [recon]
---

# httpx - HTTP Probe

## Overview
Fast HTTP probe for live hosts

## Location
~/go/bin/httpx

## Basic Usage
cat subdomains.txt | httpx
cat subdomains.txt | httpx -title -tech-detect -status-code

## Common Options
-title : Show page title
-tech-detect : Detect technology
-status-code : Show status code
-screenshot : Take screenshots

## Related Tools
nuclei, katana
