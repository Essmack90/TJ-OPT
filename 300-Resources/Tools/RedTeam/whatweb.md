---
tags: [tool, recon]
tool: whatweb
category: RedTeam
installed: true
---

# WhatWeb - Website Fingerprinter

## Overview
Identify websites technologies (CMS, web servers, CDN)

## Location
/usr/bin/whatweb

## Usage

### Basic Scan
whatweb example.com

### Aggressive Mode
whatweb -a 3 example.com

### Multiple Targets
whatweb --list targets.txt

### JSON Output
whatweb --log-json results.json example.com

### CDN Detection
whatweb example.com | grep -i cloudflare
