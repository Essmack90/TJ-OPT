# Penetration Testing: Information Gathering - Cheat Sheet & Walkthrough

## Table of Contents
1. [Penetration Testing Stages](#1-penetration-testing-stages)
2. [Passive Information Gathering (OSINT)](#2-passive-information-gathering-osint)
3. [LLM-Powered Passive Reconnaissance](#3-llm-powered-passive-reconnaissance)
4. [Active Information Gathering](#4-active-information-gathering)
5. [LLM-Powered Active Enumeration](#5-llm-powered-active-enumeration)

---

## 1. Penetration Testing Stages

### The 8 Stages of a Penetration Test

| Stage | Purpose | Key Activities |
|-------|---------|----------------|
| **1. Defining the Scope** | Establish boundaries | Define IP ranges, hosts, applications in/out of scope |
| **2. Information Gathering** | Collect actionable data | Passive & active reconnaissance |
| **3. Vulnerability Detection** | Identify weaknesses | Scan for vulnerabilities |
| **4. Initial Foothold** | Gain access | Exploit vulnerabilities |
| **5. Privilege Escalation** | Elevate access | Move from low to high privileges |
| **6. Lateral Movement** | Pivot through network | Access additional systems |
| **7. Reporting/Analysis** | Document findings | Create comprehensive report |
| **8. Lessons Learned/Remediation** | Improve security | Address vulnerabilities |

### Key Principle
> **Information Gathering is cyclical** - Each stage feeds back into recon. New discoveries lead to more targeted information gathering.

---

## 2. Passive Information Gathering (OSINT)

### What is Passive Information Gathering?
- Collecting openly-available information **without direct interaction** with the target
- Also known as **Open-Source Intelligence (OSINT)**
- Keeps our footprint low and avoids alerting the target

### Two Interpretations of "Passive"

| Strict Interpretation | Looser Interpretation |
|----------------------|----------------------|
| Never communicate with target directly | Interact only as a normal user would |
| Rely on third parties for information | Can register accounts, browse normally |
| Maximum secrecy | More practical for real engagements |
| May limit results | More actionable intelligence |

### 2.1 Whois Enumeration

**Protocol**: TCP port 43

**Forward Lookup** - Query domain owner:
```bash
whois megacorpone.com -h 192.168.50.251
```

**Reverse Lookup** - Query IP address owner:
```bash
whois 38.100.193.70 -h 192.168.50.251
```

**Key Information Found**:
- **Registrant**: Legal owner (name, organization, address)
- **Admin Contact**: Domain management contact
- **Technical Contact**: Technical setup manager
- **Name Servers**: DNS servers for the domain
- **Creation/Expiration Dates**: Domain lifecycle
- **Registrar**: Company that registered the domain

**Example Output Interpretation**:
```
Registrant Name: Alan Grofield
Registrant Organization: MegaCorpOne
Name Server: NS1.MEGACORPONE.COM
Name Server: NS2.MEGACORPONE.COM
Name Server: NS3.MEGACORPONE.COM
```

---

### 2.2 Google Hacking (Google Dorks)

**Definition**: Using clever search strings and operators to uncover critical information, vulnerabilities, and misconfigured websites.

**Essential Google Operators**:

| Operator | Purpose | Example |
|----------|---------|---------|
| `site:` | Limit to single domain | `site:megacorpone.com` |
| `filetype:` or `ext:` | Specific file types | `filetype:txt` or `ext:php` |
| `-` | Exclude items | `-filetype:html` |
| `intitle:` | Title contains term | `intitle:"index of"` |
| `inurl:` | URL contains term | `inurl:"admin"` |

**Practical Examples**:

1. **Find all indexed content**:
   ```
   site:megacorpone.com
   ```

2. **Find non-HTML files**:
   ```
   site:megacorpone.com -filetype:html
   ```

3. **Find directory listings**:
   ```
   intitle:"index of" "parent directory"
   ```

4. **Find specific file types**:
   ```
   site:megacorpone.com ext:txt
   ```

**Resources**:
- [Google Hacking Database (GHDB)](https://www.exploit-db.com/google-hacking-database)
- [DorkSearch](https://dorksearch.com/)

---

### 2.3 Netcraft

**Purpose**: Discover technologies running on websites and find hosts sharing the same IP netblock.

**Key Features**:
- DNS search
- Site reports with technology stack
- Hosting history
- Subdomain discovery

**Example Search**:
1. Visit Netcraft's DNS search page
2. Search for `*.megacorpone.com`
3. View site reports for each server found

**Information Revealed**:
- Web server technology
- Operating system
- Subdomains
- IPv4 autonomous systems
- Client-side frameworks

---

### 2.4 Open-Source Code Repositories

**Platforms to Search**:
- GitHub
- GitHub Gist
- GitLab
- SourceForge

**Search Strategies**:

1. **Manual Search**:
   ```
   path:users  # Search files with "users" in filename
   ```

2. **Automated Tools**:
   - **Gitrob**: Searches for sensitive data in repos
   - **Gitleaks**: Finds secrets using regex/entropy detection

**What to Look For**:
- Credentials and passwords
- API keys and tokens
- Configuration files
- Internal documentation
- Employee information

**Example Discovery**:
```
xampp.users file found containing username and password hash
```

---

### 2.5 Shodan

**Purpose**: Search engine for internet-connected devices and their exposed services.

**Key Difference**: Shodan crawls devices, not just web content.

**Basic Usage**:
```
hostname:megacorpone.com
```

**What Shodan Reveals**:
- Open ports and services
- Service banners and versions
- Technology stack
- Published vulnerabilities
- Hosting information

**Example Findings**:
- SSH servers with version information
- Web servers with specific technologies
- IoT devices

---

### 2.6 Security Headers & SSL/TLS Analysis

**Security Headers Scanner** ([securityheaders.com](https://securityheaders.com)):
- Analyzes HTTP response headers
- Identifies missing security headers:
  - Content-Security-Policy
  - X-Frame-Options
  - X-Content-Type-Options
  - Referrer-Policy

**SSL Server Test** ([Qualys SSL Labs](https://www.ssllabs.com/ssltest/)):
- Analyzes SSL/TLS configuration
- Identifies vulnerabilities (POODLE, Heartbleed)
- Checks cipher suite strength
- Evaluates protocol support

**Red Flags to Note**:
- TLS 1.0/1.1 support
- Weak cipher suites
- Missing security headers

---

## 3. LLM-Powered Passive Reconnaissance

### What LLMs Can Do for OSINT
- Process vast amounts of unstructured text
- Uncover patterns and connections
- Synthesize information from multiple sources
- Generate tailored wordlists and dorks

### Key Considerations ⚠️
| Do | Don't |
|----|-------|
| Cross-reference with reliable sources | Trust LLM output blindly |
| Use for brainstorming and planning | Share sensitive client data |
| Verify technical accuracy | Assume information is current |
| Check compliance with scope | Violate terms of service |

### Practical Prompts for LLMs

**1. WHOIS Information**:
```
whois megacorpone.com
```

**2. Company Structure & Employees**:
```
Can you print out all the public information about company structure and employees of megacorpone?
```

**3. Generate Google Dorks**:
```
can you provide the best 20 google dorks for megacorpone.com website tailored for a penetration test?
```

**4. Technology Stack**:
```
Retrieve the technology stack of the megacorpone.com website
```

**5. Generate Wordlists**:
```
Using public data from MegacorpOne's website and any information that can be inferred about its organizational structure, products, or services, generate a comprehensive list of potential subdomain names. Include common patterns...
```

---

## 4. Active Information Gathering

### What is Active Information Gathering?
- Direct interaction with target services
- Larger attacker footprint
- More accurate and actionable data
- May trigger IDS/IPS alerts

### Living Off the Land (LOLBAS)
Using pre-installed Windows binaries for enumeration:
- `whoami.exe`, `ping.exe`, `netstat.exe`
- `nslookup`, `net view`
- PowerShell cmdlets

---

### 4.1 DNS Enumeration

#### Common DNS Record Types

| Record | Purpose | Example |
|--------|---------|---------|
| **NS** | Name servers | `ns1.megacorpone.com` |
| **A** | IPv4 address | `149.56.244.87` |
| **AAAA** | IPv6 address | `2001:db8::1` |
| **MX** | Mail servers | `mail.megacorpone.com` |
| **PTR** | Reverse lookup | `64.21.114.167.in-addr.arpa` |
| **CNAME** | Alias | `www -> webserver` |
| **TXT** | Arbitrary data | Verification, SPF records |

#### Linux DNS Tools

**host command**:
```bash
# Forward lookup (A record)
host www.megacorpone.com

# MX records
host -t mx megacorpone.com

# TXT records
host -t txt megacorpone.com

# Specific nameserver
host mail.megacorpone.com 8.8.8.8
```

**Brute Force Forward DNS**:
```bash
# Create wordlist
cat list.txt
www
ftp
mail
owa
proxy
router

# Brute force
for ip in $(cat list.txt); do host $ip.megacorpone.com; done
```

**Brute Force Reverse DNS**:
```bash
# Scan IP range 64-79
for ip in $(seq 64 79); do host 167.114.21.$ip; done | grep -Ev "not found|timed out"
```

#### Automated DNS Tools

**DNSRecon**:
```bash
# Standard scan
dnsrecon -d megacorpone.com -t std

# Brute force with wordlist
dnsrecon -d megacorpone.com -D ~/list.txt -t brt
```

**DNSEnum**:
```bash
dnsenum megacorpone.com
```

#### Windows DNS Enumeration

**nslookup**:
```cmd
# Basic lookup
nslookup mail.megacorptwo.com

# Specific record type
nslookup -type=TXT info.megacorptwo.com 192.168.50.151

# Change DNS server
nslookup
> server 192.168.50.151
> set type=MX
> megacorptwo.com
```

---

### 4.2 TCP/UDP Port Scanning Theory

#### TCP Three-Way Handshake
```
Client -> Server: SYN
Server -> Client: SYN-ACK
Client -> Server: ACK
```

**CONNECT Scan**: Completes full handshake
**SYN Scan**: Doesn't complete handshake (more stealth)

#### UDP Scanning
- Stateless protocol
- **Open port**: No response OR application-specific response
- **Closed port**: ICMP port unreachable
- Can be unreliable due to firewalls dropping ICMP

#### Netcat Scanning

**TCP Scan**:
```bash
nc -nvv -w 1 -z 192.168.50.152 3388-3390
```

**UDP Scan**:
```bash
nc -nv -u -z -w 1 192.168.50.149 120-123
```

**Options Explained**:
- `-n`: No DNS resolution
- `-v`: Verbose
- `-w`: Timeout in seconds
- `-z`: Zero-I/O mode (scanning)
- `-u`: UDP mode

---

### 4.3 Port Scanning with Nmap

#### Installation & Basic Commands

**Install**:
```bash
sudo apt install nmap
```

**Basic Syntax**:
```bash
nmap [scan type] [options] [target]
```

#### Scan Types

| Scan Type | Command | Description |
|-----------|---------|-------------|
| SYN Stealth | `sudo nmap -sS` | Default with root, incomplete handshake |
| TCP Connect | `nmap -sT` | Full handshake, no root needed |
| UDP | `sudo nmap -sU` | UDP port scanning |
| Combined | `sudo nmap -sU -sS` | Both TCP and UDP |

#### Essential Nmap Options

| Option | Purpose | Example |
|--------|---------|---------|
| `-p` | Port specification | `-p 80,443` or `-p 1-65535` |
| `--top-ports` | Most common ports | `--top-ports=20` |
| `-A` | Aggressive scan | OS, version, scripts, traceroute |
| `-O` | OS fingerprinting | `-O --osscan-guess` |
| `-sV` | Service version detection | `-sV` |
| `-sn` | Ping sweep (no port scan) | `nmap -sn 192.168.50.1-253` |
| `-Pn` | Skip host discovery | Treat all hosts as online |

#### Network Sweeping

**Ping Sweep**:
```bash
nmap -sn 192.168.50.1-253 -oG ping-sweep.txt
grep Up ping-sweep.txt | cut -d " " -f 2
```

**Port Sweep**:
```bash
nmap -p 80 192.168.50.1-253 -oG web-sweep.txt
grep open web-sweep.txt | cut -d" " -f2
```

**Top Ports with OS/Version**:
```bash
nmap -sT -A --top-ports=20 192.168.50.1-253 -oG top-port-sweep.txt
```

#### Nmap Scripting Engine (NSE)

**Script Location**: `/usr/share/nmap/scripts/`

**Using Scripts**:
```bash
# Run specific script
nmap --script http-headers 192.168.50.6

# Script help
nmap --script-help http-headers

# List scripts
ls -1 /usr/share/nmap/scripts/smb*
```

**Common SMB Scripts**:
- `smb-os-discovery` - OS and domain info
- `smb-enum-shares` - List shares
- `smb-enum-users` - Enumerate users
- `smb2-security-mode` - Check SMB2 security

#### OS Fingerprinting

```bash
sudo nmap -O 192.168.50.14 --osscan-guess
```

**How it works**:
- Analyzes TCP/IP stack implementation differences
- TTL values, TCP window sizes, etc.
- Matches to known fingerprints

**Note**: Not 100% accurate, especially behind firewalls/proxies.

#### Monitoring Scan Traffic

```bash
# Set rules
sudo iptables -I INPUT 1 -s 192.168.50.149 -j ACCEPT
sudo iptables -I OUTPUT 1 -d 192.168.50.149 -j ACCEPT
sudo iptables -Z

# Run scan
nmap 192.168.50.149

# Check traffic
sudo iptables -vn -L
```

#### Windows Port Scanning

**Test-NetConnection**:
```powershell
# Check specific port
Test-NetConnection -Port 445 192.168.50.151

# Port scanning loop (first 1024 ports)
1..1024 | % {echo ((New-Object Net.Sockets.TcpClient).Connect("192.168.50.151", $_)) "TCP port $_ is open"} 2>$null
```

---

### 4.4 SMB Enumeration

#### SMB/NetBIOS Ports
- **NetBIOS**: TCP 139, UDP 137-138
- **SMB**: TCP 445

#### Scanning for SMB

**Nmap Scan**:
```bash
nmap -v -p 139,445 -oG smb.txt 192.168.50.1-254
```

**nbtscan**:
```bash
sudo nbtscan -r 192.168.50.0/24
```

#### Nmap SMB Scripts

```bash
# OS discovery
nmap -v -p 139,445 --script smb-os-discovery 192.168.50.152

# List all SMB scripts
ls -1 /usr/share/nmap/scripts/smb*
```

#### Windows SMB Enumeration

**Net View**:
```cmd
net view \\dc01 /all
```

**Common Shares Found**:
- ADMIN$ - Remote admin
- C$ - Default share
- IPC$ - Remote IPC
- NETLOGON - Domain logon
- SYSVOL - Domain policy

---

### 4.5 SMTP Enumeration

#### SMTP Commands for Enumeration

| Command | Purpose | Response Codes |
|---------|---------|----------------|
| **VRFY** | Verify email address | 252 = exists, 550 = unknown |
| **EXPN** | List mailing list members | Lists membership |

#### Manual Enumeration

**With Netcat**:
```bash
nc -nv 192.168.50.8 25
220 mail ESMTP Postfix (Ubuntu)
VRFY root
252 2.0.0 root
VRFY idontexist
550 5.1.1 <idontexist>: Recipient address rejected
```

**Python Script**:
```python
import socket
import sys

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((sys.argv[2], 25))
banner = s.recv(1024)
print(banner)
s.send(b'VRFY ' + sys.argv[1].encode() + b'\r\n')
print(s.recv(1024))
s.close()
```

**Usage**:
```bash
python3 smtp.py root 192.168.50.8
```

#### Windows SMTP Enumeration

**Check Port**:
```powershell
Test-NetConnection -Port 25 192.168.50.8
```

**Install Telnet Client** (requires admin):
```cmd
dism /online /Enable-Feature /FeatureName:TelnetClient
```

**Telnet Enumeration**:
```cmd
telnet 192.168.50.8 25
220 mail ESMTP Postfix (Ubuntu)
VRFY root
252 2.0.0 root
```

---

### 4.6 SNMP Enumeration

#### SNMP Overview
- Protocol: UDP
- Versions 1, 2c: No encryption, weak auth
- Common community strings: `public`, `private`, `manager`
- **Management Information Base (MIB)**: Hierarchical database

#### Key Windows SNMP MIB Values

| OID | Information |
|-----|-------------|
| `1.3.6.1.2.1.25.1.6.0` | System processes |
| `1.3.6.1.2.1.25.4.2.1.2` | Running programs |
| `1.3.6.1.2.1.25.4.2.1.4` | Process paths |
| `1.3.6.1.2.1.25.2.3.1.4` | Storage units |
| `1.3.6.1.2.1.25.6.3.1.2` | Software name |
| `1.3.6.1.4.1.77.1.2.25` | User accounts |
| `1.3.6.1.2.1.6.13.1.3` | TCP Local ports |

#### Finding SNMP Services

**Nmap**:
```bash
sudo nmap -sU --open -p 161 192.168.50.1-254 -oG open-snmp.txt
```

**onesixtyone** (community string brute force):
```bash
echo public > community
echo private >> community
echo manager >> community
for ip in $(seq 1 254); do echo 192.168.50.$ip; done > ips
onesixtyone -c community -i ips
```

#### SNMP Walking

**Full MIB Walk**:
```bash
snmpwalk -c public -v1 -t 10 192.168.50.151
```

**Specific OID Queries**:

**User Accounts**:
```bash
snmpwalk -c public -v1 192.168.50.151 1.3.6.1.4.1.77.1.2.25
```

**Running Processes**:
```bash
snmpwalk -c public -v1 192.168.50.151 1.3.6.1.2.1.25.4.2.1.2
```

**Installed Software**:
```bash
snmpwalk -c public -v1 192.168.50.151 1.3.6.1.2.1.25.6.3.1.2
```

**Open TCP Ports**:
```bash
snmpwalk -c public -v1 192.168.50.151 1.3.6.1.2.1.6.13.1.3
```

**Decode Hex Strings**:
```bash
snmpwalk -c public -v1 192.168.50.151 -Oa 1.3.6.1.2.1.2.2.1.2
```

---

## 5. LLM-Powered Active Enumeration

### Enhancing DNS Enumeration with LLMs

**Wordlist Generation**:
```
Using public data from MegacorpOne's website and any information that can be inferred about its organizational structure, products, or services, generate a comprehensive list of potential subdomain names.

Incorporate common patterns:
- Infrastructure: "api", "dev", "test", "staging"
- Services: "mail", "auth", "cdn", "status"
- Departments: "hr", "sales", "support"
- Regions: "us", "eu", "asia"

Compile into a wordlist of 1000 unique, lowercase entries.
```

### Gobuster for DNS Enumeration

**Installation**:
```bash
sudo apt update
sudo apt install gobuster
```

**DNS Brute Force**:
```bash
gobuster dns -d megacorpone.com -w wordlist.txt -t 10
```

**Note**: Gobuster > 3.6 uses `--do` flag instead.

---

## 6. Quick Reference: Tools by Category

### Passive Reconnaissance Tools

| Tool/Resource | Purpose |
|---------------|---------|
| `whois` | Domain/IP registration info |
| Google Search | Google dorks |
| Netcraft | Technology stack, subdomains |
| GitHub/GitLab | Code search, secrets |
| Shodan | Internet-connected devices |
| Security Headers | HTTP header analysis |
| SSL Labs | SSL/TLS configuration |
| ChatGPT/LLMs | OSINT synthesis, wordlist generation |

### Active Reconnaissance Tools

| Tool | Purpose | Example |
|------|---------|---------|
| `host` | DNS lookups | `host -t mx domain.com` |
| `nslookup` | DNS queries (Windows/Linux) | `nslookup -type=TXT domain` |
| `dnsrecon` | Automated DNS enumeration | `dnsrecon -d domain -t std` |
| `dnsenum` | Comprehensive DNS enumeration | `dnsenum domain.com` |
| `gobuster` | DNS brute force | `gobuster dns -d domain -w wordlist` |
| `nc` | Manual service connections | `nc -nv IP 25` |
| `nmap` | Port scanning, OS detection | `nmap -sS -A target` |
| `nbtscan` | NetBIOS name scanning | `nbtscan -r 192.168.1.0/24` |
| `snmpwalk` | SNMP MIB enumeration | `snmpwalk -c public -v1 IP OID` |
| `onesixtyone` | SNMP community brute force | `onesixtyone -c community -i ips` |
| `Test-NetConnection` | Windows port testing | `Test-NetConnection -Port 445 IP` |
| `net view` | Windows share enumeration | `net view \\\\host /all` |

---

## 7. Best Practices & Tips

### Information Gathering Checklist

- [ ] Define scope and rules of engagement
- [ ] Start with passive reconnaissance (OSINT)
- [ ] Document everything you find
- [ ] Cross-reference information from multiple sources
- [ ] Use LLMs for brainstorming and wordlist generation
- [ ] Verify LLM outputs with reliable sources
- [ ] Move to active scanning only within scope
- [ ] Start with broad scans, narrow based on findings
- [ ] Consider traffic impact and stealth requirements
- [ ] Never stop gathering information (it's cyclical!)

### Stealth Considerations

| Activity | Stealth Level | Notes |
|----------|--------------|-------|
| OSINT/Passive | High | No direct interaction |
| DNS enumeration | Medium | Normal traffic |
| Port scanning | Low | May trigger IDS/IPS |
| Service enumeration | Low | Direct service interaction |
| Vulnerability scanning | Very Low | High chance of detection |

### Common Pitfalls to Avoid

1. **Missing UDP ports** - Don't forget UDP scanning
2. **Using default wordlists** - Customize with LLMs
3. **Trusting tool output blindly** - Verify findings
4. **Forgetting to document** - Notes are crucial
5. **Ignoring small details** - Small finds can lead to big pivots
6. **Scanning without permission** - Always get authorization
7. **Overlooking SMB/SMTP/SNMP** - These often yield valuable info
8. **Not using LLMs effectively** - They can significantly speed up recon

### Remember

> **Information gathering is an iterative process.** Each discovery should lead to more targeted information gathering. The smallest detail - like a forum post or a misconfigured DNS record - can lead to the biggest compromise.

---

## Quick Commands Reference

### DNS
```bash
# Basic
host domain.com
host -t mx domain.com
nslookup domain.com

# Brute force
for ip in $(cat list.txt); do host $ip.domain.com; done
for ip in $(seq 1 254); do host IP.$ip; done

# Automated
dnsrecon -d domain.com -t std
dnsrecon -d domain.com -D wordlist.txt -t brt
dnsenum domain.com
gobuster dns -d domain.com -w wordlist.txt
```

### Port Scanning
```bash
# Netcat
nc -nvv -w 1 -z IP port-range

# Nmap
nmap -sS target
nmap -sU target
nmap -sT -A target
nmap -sn 192.168.1.1-254
nmap -p 80 192.168.1.1-254
nmap --script smb-os-discovery target
```

### SMTP
```bash
nc -nv IP 25
VRFY username
```

### SNMP
```bash
snmpwalk -c public -v1 IP
snmpwalk -c public -v1 IP 1.3.6.1.4.1.77.1.2.25
onesixtyone -c community.txt -i ips.txt
```

### Windows (RDP)
```bash
xfreerdp /u:username /p:password /v:IP
```

### PowerShell
```powershell
Test-NetConnection -Port 445 IP
1..1024 | % {echo ((New-Object Net.Sockets.TcpClient).Connect("IP", $_)) "Port $_ is open"} 2>$null
net view \\host /all
nslookup -type=TXT host.domain.com DNS_IP
```

