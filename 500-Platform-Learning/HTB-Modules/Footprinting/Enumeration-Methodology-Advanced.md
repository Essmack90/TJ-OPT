---
tags: [module/footprinting, module/core, level/advanced, practical]
---

# Enumeration Methodology - Practical Application

## The Six Layers Framework

This is NOT a checklist. This is a mental framework to organize your enumeration.

LAYER 1: INTERNET PRESENCE
    Domains, Subdomains, IPs, ASN, Cloud
    ↓
LAYER 2: GATEWAY
    Firewalls, IPS/IDS, VPN, Segmentation
    ↓
LAYER 3: ACCESSIBLE SERVICES
    Ports, Services, Versions, Configs
    ↓
LAYER 4: PROCESSES
    PIDs, Data Flow, Tasks, Dependencies
    ↓
LAYER 5: PRIVILEGES
    Users, Groups, Permissions
    ↓
LAYER 6: OS SETUP
    OS Type, Patches, Network Config, Files

---

## Layer 1: Internet Presence - Deep Dive

### What to Enumerate

| Category | What to Look For | Tools |
|----------|------------------|-------|
| Domains | Main domain, alternative TLDs | whois, dig |
| Subdomains | dev, mail, admin, staging | sublist3r, amass, dnsrecon |
| vHosts | Different sites on same IP | gobuster vhost, ffuf |
| ASN | Autonomous System Numbers | whois, BGP tools |
| Netblocks | IP ranges owned | whois, ripe |
| Cloud Instances | AWS, Azure, GCP buckets | cloud enumeration tools |
| Security Measures | Cloudflare, WAF | whatweb, wafw00f |

### Practical Workflow

1. Start with the main domain
   whois target.com
   dig target.com ANY
   nslookup target.com

2. Find subdomains
   sublist3r -d target.com
   amass enum -d target.com
   dnsrecon -d target.com -D /usr/share/wordlists/dns/subdomains-top1million-5000.txt -t brt

3. Identify virtual hosts
   gobuster vhost -u https://target.com -w /usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-110000.txt

4. Map netblocks
   whois -h whois.arin.net target.com

5. Check cloud presence
   cloudbrute -d target.com

6. Identify security measures
   whatweb target.com
   wafw00f target.com

---

## Layer 2: Gateway - Deep Dive

### What to Enumerate

| Category | What to Look For | Tools/Methods |
|----------|------------------|---------------|
| Firewalls | Filtered ports, rules | nmap -sA, traceroute |
| IPS/IDS | Scan triggers, blocks | Aggressive vs stealth scans |
| VPN | VPN portals, protocols | nmap service detection |
| Segmentation | Network layout | traceroute, ping sweeps |
| Proxies | Forward/reverse proxies | HTTP headers, response analysis |

### Practical Workflow

1. Map firewall rules
   nmap -sA target.com
   nmap -sS -p- target.com

2. Test rate limiting
   nmap -T4 target.com
   nmap -T1 target.com

3. Identify VPN entry points
   nmap -p 500,4500,1194,1723 target.com

4. Trace network path
   traceroute target.com
   mtr target.com

5. Look for proxy headers
   curl -I target.com | grep -i via
   curl -I target.com | grep -i x-forwarded

---

## Layer 3: Accessible Services - Deep Dive

### What to Enumerate

| Category | What to Look For | Tools |
|----------|------------------|-------|
| Ports | Open, closed, filtered | nmap, masscan |
| Service Type | HTTP, SSH, FTP, etc. | nmap -sV |
| Version | Exact version numbers | nmap -sV, banner grabbing |
| Configuration | Default settings, misconfigs | Service-specific checks |
| Authentication | Login methods, default creds | hydra, ncrack |

### Practical Workflow

1. Quick port scan
   nmap -sS -T4 -F target.com -oA quick

2. Full port scan (if needed)
   nmap -sS -T4 -p- target.com -oA full

3. Version detection
   nmap -sV -p 22,80,443 target.com -oA versions

4. Banner grabbing
   nc -nv target.com 22
   nc -nv target.com 80
   openssl s_client -connect target.com:443

5. Service-specific enumeration
   smbclient -L //target.com -N
   ftp target.com
   curl -I target.com

---

## Layer 4: Processes - Deep Dive

This layer requires access to the system (post-exploitation).

### What to Enumerate

| Category | What to Look For | Commands |
|----------|------------------|----------|
| Running Processes | All active processes | ps aux, tasklist |
| Data Flow | Input/output sources | netstat, lsof |
| Tasks | Scheduled jobs | crontab, schtasks |
| Dependencies | Libraries, modules | ldd, ListDLLs |

### Practical Workflow (Linux)

ps aux
netstat -tulpn
lsof -i
crontab -l
systemctl list-units

### Practical Workflow (Windows)

tasklist /v
netstat -ano
schtasks /query /fo LIST
wmic process list
Get-Service

---

## Layer 5: Privileges - Deep Dive

This layer requires access to the system (post-exploitation).

### What to Enumerate

| Category | What to Look For | Commands |
|----------|------------------|----------|
| Users | All user accounts | cat /etc/passwd, net user |
| Groups | Group memberships | groups, net localgroup |
| Permissions | File/service perms | ls -la, icacls |
| Restrictions | What's denied | sudo -l, whoami /priv |
| Environment | ENV variables | env, set |

### Practical Workflow (Linux)

whoami
id
sudo -l
cat /etc/passwd
cat /etc/group
env
find / -perm -4000 2>/dev/null

### Practical Workflow (Windows)

whoami
whoami /priv
whoami /groups
net user
net localgroup
set
icacls C:\

---

## Layer 6: OS Setup - Deep Dive

This layer requires access to the system (post-exploitation).

### What to Enumerate

| Category | What to Look For | Commands |
|----------|------------------|----------|
| OS Type | Windows/Linux/Mac | uname -a, systeminfo |
| Patch Level | Update history | cat /etc/*release, systeminfo |
| Network Config | IP, routes, DNS | ifconfig, ipconfig, route |
| Config Files | System configs | find / -name "*.conf" |
| Sensitive Files | Keys, credentials | grep -r "password" /etc |

### Practical Workflow (Linux)

uname -a
cat /etc/os-release
hostnamectl
ifconfig
ip addr show
route -n
cat /etc/resolv.conf
find / -name "*.conf" 2>/dev/null
grep -r "password" /etc 2>/dev/null

### Practical Workflow (Windows)

systeminfo
hostname
ipconfig /all
netstat -r
dir /s *.config
findstr /si password *.txt *.ini *.config

---

## The Gap-Finding Methodology

Not every gap leads inside. You must evaluate each finding:

### Gap Evaluation Criteria

1. Does this gap provide new information? (yes → enumerate further)
2. Does this gap allow interaction? (yes → test)
3. Does this gap lead to another layer? (yes → pursue)
4. Is this gap a dead end? (yes → document and move on)

### Common Dead Ends

- Open ports with no response
- Filtered ports with no bypass
- Services with no known exploits
- Permissions that can't be abused
- Configurations that are locked down

### Common Paths Inside

- Vulnerable service versions
- Weak credentials
- Misconfigured permissions
- Exposed sensitive data
- Default configurations

---

## The SolarWinds Lesson

The SolarWinds attack taught us:

- Deep enumeration beats quick scanning
- Months of study can find what weeks cannot
- There is ALWAYS a way in
- You must understand the target completely

You won't have months in a pentest. But you can apply the same methodology systematically.

---

## Quick Reference Card

LAYER 1: INTERNET PRESENCE
    Find everything exposed
    Tools: whois, dig, sublist3r, amass, whatweb

LAYER 2: GATEWAY
    Understand protections
    Tools: nmap -sA, traceroute, mtr

LAYER 3: ACCESSIBLE SERVICES
    Identify running services
    Tools: nmap, nc, openssl

LAYER 4: PROCESSES
    Understand data flow
    Commands: ps, netstat, lsof

LAYER 5: PRIVILEGES
    Identify permissions
    Commands: whoami, id, sudo -l

LAYER 6: OS SETUP
    Understand the system
    Commands: uname, systeminfo, find

---

## Key Takeaways

- The six layers are a FRAMEWORK, not a checklist
- Each layer builds on the previous
- Not every gap leads inside
- Document EVERYTHING
- Understand WHY before trying HOW
- Tools change, methodology stays the same
- If you're stuck, go back a layer
- There's ALMOST ALWAYS a way in
- The SolarWinds attack proves deep enumeration wins
- Apply this systematically and you will find the way in
