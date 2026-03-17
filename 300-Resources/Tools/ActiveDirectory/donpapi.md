---
tags: [tool, activedirectory, dpapi]
tool: "donpapi"
category: "Active Directory"
installed: true
phase: [credential]
---

# DonPAPI - DPAPI Credential Dumper

## Tool Overview
Purpose: Dump DPAPI credentials remotely
Location: ~/tools/activedirectory/DonPAPI/DonPAPI.py

## How to Use It

Basic Usage:
DonPAPI.py domain/user:pass@target

With Hashes:
DonPAPI.py domain/user@target -hashes :hash

## Related Tools
lsassy, pypykatz
