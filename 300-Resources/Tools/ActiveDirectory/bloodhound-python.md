---
tags: [tool, activedirectory, bloodhound]
tool: "bloodhound-python"
category: "Active Directory"
installed: true
phase: [enumeration]
---

# BloodHound.py - BloodHound Collector for Linux

## Tool Overview
Purpose: Python-based BloodHound collector for Linux systems
Location: /usr/bin/bloodhound-python

## When to Use
- When you can't run Windows tools
- For remote AD enumeration
- To collect BloodHound data from Linux

## How to Use It

Basic Collection:
bloodhound-python -d domain.local -u user -p pass -ns DC_IP

Collect All Data:
bloodhound-python -d domain.local -u user -p pass -ns DC_IP -c All

With Authentication:
bloodhound-python -d domain.local -u user -p pass -dc DC_IP.domain.local -c All

With LDAPS:
bloodhound-python -d domain.local -u user -p pass -ns DC_IP -c All --ldaps

Output Directory:
bloodhound-python -d domain.local -u user -p pass -ns DC_IP -c All --outputdir /tmp/bh

## What It Collects
- Users
- Groups
- Computers
- Sessions
- ACLs
- Group membership
- Trust relationships

## Related Tools
bloodhound, ldapdomaindump
