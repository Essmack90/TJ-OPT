---
tags: [tool, osint, username]
tool: "whatsmyname"
category: "OSINT"
installed: true
phase: [recon]
---

# WhatsMyName - Username Enumeration

## Tool Overview
Purpose: Username enumeration across many websites
Location: ~/tools/osint/WhatsMyName

## When to Use
- Comprehensive username checks
- Finding all sites where a username exists

## How to Use It

Run Web Interface:
cd ~/tools/osint/WhatsMyName
python3 web.py

Run CLI:
python3 whatsmyname.py -u username

Use Custom Sites:
python3 whatsmyname.py -u username -s sites.json

## Related Tools
sherlock, maigret
