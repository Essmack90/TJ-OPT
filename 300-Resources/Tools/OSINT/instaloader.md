---
tags: [tool, osint, instagram]
tool: "instaloader"
category: "OSINT"
installed: true
phase: [recon]
---

# instaloader - Instagram OSINT

## Tool Overview
Purpose: Download and analyze Instagram profiles
Location: /home/kali/.local/bin/instaloader

## When to Use
- Instagram profile investigation
- Downloading profile content
- Metadata extraction

## How to Use It

Download Profile:
instaloader profile username

Download with Metadata:
instaloader --metadata-json username

Login (for private):
instaloader --login=your_account username

## Related Tools
toutatis
