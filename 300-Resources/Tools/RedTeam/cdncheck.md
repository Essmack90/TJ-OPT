---
tags: [tool, recon]
tool: cdncheck
category: RedTeam
installed: true
---

# cdncheck - CDN Detection

## Overview
Check if IPs/domains are behind CDN services

## Location
/usr/local/bin/cdncheck

## Usage

### Check Domain
echo "example.com" | cdncheck

### Check Multiple
cat domains.txt | cdncheck

### Check IP
echo "1.2.3.4" | cdncheck

### JSON Output
cat domains.txt | cdncheck -json

### Silent Mode
cat domains.txt | cdncheck -silent
