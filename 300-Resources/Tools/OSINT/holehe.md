---
tags: [tool, osint, email]
tool: "holehe"
category: "OSINT"
installed: true
phase: [recon]
---

# holehe - Email OSINT

## Tool Overview
Purpose: Check if an email is registered on 120+ websites
Location: /home/kali/.local/bin/holehe

## When to Use
- Finding accounts associated with an email
- Email reconnaissance

## How to Use It

Basic Check:
holehe email@example.com

Only Registered Sites:
holehe email@example.com --only-used

No Color Output:
holehe email@example.com --no-color

CSV Output:
holehe email@example.com --csv

## Related Tools
sherlock, ghunt
