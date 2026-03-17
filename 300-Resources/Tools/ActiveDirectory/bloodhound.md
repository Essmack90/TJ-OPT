---
tags: [tool, activedirectory, bloodhound]
tool: "bloodhound"
category: "Active Directory"
installed: true
phase: [enumeration, analysis]
---

# BloodHound - AD Visualization

## Tool Overview
Purpose: Graph-based tool to visualize Active Directory relationships and attack paths
Location: /usr/bin/bloodhound

## When to Use
- After collecting AD data with collectors
- To find attack paths to Domain Admin
- To visualize AD relationships

## How to Use It

Start BloodHound:
bloodhound

Default Credentials:
Username: neo4j
Password: neo4j

## Collectors

BloodHound.py (Python):
bloodhound-python -d domain.local -u user -p pass -ns DC_IP -c All

SharpHound (Windows - PowerShell):
powershell -ep bypass
. .\SharpHound.ps1
Invoke-BloodHound -CollectionMethod All

SharpHound.exe:
SharpHound.exe -c All

## Key Queries
- Find all Domain Admins
- Shortest path to Domain Admin
- Users with dangerous privileges
- Computers with unconstrained delegation

## Related Tools
bloodhound-python, neo4j
