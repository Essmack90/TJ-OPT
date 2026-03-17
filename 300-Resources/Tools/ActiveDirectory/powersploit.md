---
tags: [tool, activedirectory, powershell]
tool: "powersploit"
category: "Active Directory"
installed: true
phase: [enumeration, exploitation]
---

# PowerSploit - PowerShell Post-Exploitation Framework

## Tool Overview
Purpose: Collection of PowerShell modules for AD attacks
Location: /usr/share/powersploit/

## Key Modules

### Recon Module
/usr/share/powersploit/Recon/PowerView.ps1 - AD enumeration

### Privesc Module
/usr/share/powersploit/Privesc/PowerUp.ps1 - Privilege escalation checks

### CodeExecution Module
/usr/share/powersploit/CodeExecution/ - Shellcode and DLL injection

### Exfiltration Module
/usr/share/powersploit/Exfiltration/ - Credential theft

## How to Use
powershell -ep bypass
Import-Module /usr/share/powersploit/Recon/PowerView.ps1
Get-NetUser

## Related Tools
nishang, powerview
