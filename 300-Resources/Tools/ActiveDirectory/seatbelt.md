---
tags: [tool, activedirectory, enumeration]
tool: "seatbelt"
category: "Active Directory"
installed: true
phase: [enumeration]
---

# Seatbelt - Windows Host Enumeration

## Tool Overview
Purpose: C# tool for Windows system enumeration
Location: ~/tools/activedirectory/windows/Seatbelt.exe

## When to Use
- After gaining access to Windows host
- Quick system enumeration
- Finding privesc vectors

## How to Use It

All Checks:
Seatbelt.exe -group=all

System Checks:
Seatbelt.exe -group=system

User Checks:
Seatbelt.exe -group=user

## Related Tools
winpeas, sharpup
