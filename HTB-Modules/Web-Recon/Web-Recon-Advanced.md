---
tags:
  - module/web-recon
  - reconnaissance
  - active
  - passive
  - tools
  - level/advanced
  - practical
tool:
phase:
  - recon
  - web
---

# Information Gathering - Web Edition - Practical Application

## Complete Web Recon Workflow

Phase 1: Passive Recon (No touch)
Phase 2: Subdomain Enumeration
Phase 3: Content Discovery
Phase 4: Technology Fingerprinting
Phase 5: Active Scanning (When ready)

---

## Phase 1: Passive Recon - Tools & Techniques

### WHOIS Lookups

whois target.com
whois -h whois.arin.net 8.8.8.8

Reveals:
- Registrant name/email
- Registrar
- Name servers
- Creation/expiration dates
- Abuse contact

### DNS Enumeration (Passive)

dig target.com ANY
nslookup target.com
host -t any target.com

### Certificate Transparency (crt.sh)

curl -s "https://crt.sh/?q=target.com&output=json" | jq -r '.[].name_value' | sed 's/\*\.//g' | sort -u

This reveals ALL subdomains that have ever had SSL certificates.

### Wayback Machine

curl -s "http://web.archive.org/cdx/search/cdx?url=*.target.com&output=json&fl=original&collapse=urlkey" | jq -r '.[] | select(length > 0) | .[0]' | sort -u

Finds historical URLs that may reveal old endpoints, backup files, etc.

### GitHub OSINT

Search for:
- target.com in code
- target-company in repos
- Filenames containing passwords, configs, etc.

### Google Dorks

| Dork | What It Finds |
|------|---------------|
| site:target.com | Everything on the domain |
| site:target.com filetype:pdf | PDF files |
| inurl:admin site:target.com | Admin panels |
| intitle:"index of" site:target.com | Open directories |
| ext:sql | SQL files |
| ext:bak | Backup files |
| ext:conf | Config files |

---

## Phase 2: Subdomain Enumeration

### Passive Subdomain Discovery

sublist3r -d target.com
amass enum -passive -d target.com
assetfinder -subs-only target.com
findomain -t target.com

### Active Subdomain Brute Force

gobuster dns -d target.com -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt -t 50

dnsenum --dnsserver 8.8.8.8 --enum -p 0 -s 0 -o subdomains.txt -f /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt target.com

### DNS Zone Transfer (AXFR)

dig axfr target.com @ns1.target.com
host -l target.com ns1.target.com

If this works, you get ALL DNS records. This is a critical misconfiguration.

### Virtual Host Discovery

gobuster vhost -u https://target.com -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt -t 50

ffuf -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt -H "Host: FUZZ.target.com" -u https://target.com -fc 404

---

## Phase 3: Content Discovery

### Directory Bruteforce

gobuster dir -u https://target.com -w /usr/share/seclists/Discovery/Web-Content/common.txt -t 50 -x php,html,txt,bak

ffuf -w /usr/share/seclists/Discovery/Web-Content/raft-large-directories.txt -u https://target.com/FUZZ -recursion -recursion-depth 2

dirb https://target.com /usr/share/wordlists/dirb/common.txt

dirsearch -u https://target.com -e php,html,js,txt,bak -r -t 50

### Extension-Specific Fuzzing

ffuf -w /usr/share/seclists/Discovery/Web-Content/raft-large-files.txt -u https://target.com/FUZZ

### Parameter Discovery

arjun -u https://target.com/page.php -o params.txt

ffuf -w /usr/share/seclists/Discovery/Web-Content/burp-parameter-names.txt -u https://target.com/page.php\?FUZZ\=test

### Backup File Discovery

curl https://target.com/backup.zip
curl https://target.com/backup.tar.gz
curl https://target.com/old/
curl https://target.com/backup/

Common backup extensions: .bak, .backup, .old, .orig, .copy, .txt, .zip, .tar.gz

---

## Phase 4: Technology Fingerprinting

### HTTP Headers

curl -I https://target.com

Look for:
- Server: Apache/nginx/IIS
- X-Powered-By: PHP/ASP.NET
- Via: Cloudflare/Akamai
- Set-Cookie: PHPSESSID (PHP), ASP.NET_SessionId (ASP)

### WhatWeb

whatweb target.com

Reveals:
- CMS (WordPress, Joomla, Drupal)
- JavaScript frameworks
- Web server
- Email addresses
- Country
- IP address

### Wappalyzer

Browser extension that shows:
- Web frameworks
- Analytics
- JavaScript libraries
- CDNs

### BuiltWith

https://builtwith.com

### Wafw00f (WAF Detection)

wafw00f target.com

Detects if there's a WAF and which one.

### Nmap Service Detection

nmap -sV -p80,443 target.com

### SSL/TLS Analysis

sslscan target.com
testssl.sh target.com

---

## Phase 5: Active Scanning Tools

### Nmap

nmap -sC -sV -p- target.com -oA initial-scan

### Nikto

nikto -h https://target.com

### Nuclei

nuclei -u https://target.com -t cves/ -t misconfiguration/ -t exposures/

### What to Scan For

| Tool | Purpose |
|------|---------|
| Nmap | Port scanning, service detection |
| Nikto | Web server vuln scanning |
| Nuclei | Template-based vuln scanning |
| WPScan | WordPress specific |
| Joomscan | Joomla specific |
| Droopescan | Drupal specific |

---

## Complete Passive Recon Script

Save as passive-recon.sh:

#!/bin/bash
DOMAIN=$1
OUTPUT_DIR="recon-$DOMAIN"
mkdir -p $OUTPUT_DIR

echo "[*] Starting passive reconnaissance on $DOMAIN"

echo "[*] WHOIS lookup..."
whois $DOMAIN > $OUTPUT_DIR/whois.txt

echo "[*] DNS records..."
dig $DOMAIN ANY > $OUTPUT_DIR/dns-any.txt

echo "[*] Certificate transparency..."
curl -s "https://crt.sh/?q=$DOMAIN&output=json" | jq -r '.[].name_value' | sed 's/\*\.//g' | sort -u > $OUTPUT_DIR/crt-subdomains.txt

echo "[*] Wayback URLs..."
curl -s "http://web.archive.org/cdx/search/cdx?url=*.$DOMAIN&output=json&fl=original&collapse=urlkey" | jq -r '.[] | select(length > 0) | .[0]' | sort -u > $OUTPUT_DIR/wayback-urls.txt

echo "[*] Passive subdomain enumeration with assetfinder..."
assetfinder --subs-only $DOMAIN > $OUTPUT_DIR/assetfinder.txt

echo "[*] Amass passive scan..."
amass enum -passive -d $DOMAIN -o $OUTPUT_DIR/amass.txt

echo "[*] Passive recon complete. Check $OUTPUT_DIR/"

---

## Complete Active Recon Script

Save as active-recon.sh:

#!/bin/bash
DOMAIN=$1
OUTPUT_DIR="recon-$DOMAIN"
mkdir -p $OUTPUT_DIR

echo "[*] Starting active reconnaissance on $DOMAIN"

echo "[*] Nmap scan..."
nmap -sC -sV -p- $DOMAIN -oA $OUTPUT_DIR/nmap

echo "[*] Gobuster directory scan..."
gobuster dir -u https://$DOMAIN -w /usr/share/seclists/Discovery/Web-Content/common.txt -t 50 -o $OUTPUT_DIR/gobuster.txt

echo "[*] WhatWeb fingerprinting..."
whatweb $DOMAIN > $OUTPUT_DIR/whatweb.txt

echo "[*] WAF detection..."
wafw00f $DOMAIN > $OUTPUT_DIR/waf.txt

echo "[*] Nikto scan..."
nikto -h https://$DOMAIN -o $OUTPUT_DIR/nikto.txt

echo "[*] Active recon complete. Check $OUTPUT_DIR/"

---

## Tool Comparison

| Tool | Type | Best For |
|------|------|----------|
| whois | Passive | Domain registration info |
| dig/nslookup | Passive | DNS records |
| crt.sh | Passive | Subdomain discovery |
| Wayback Machine | Passive | Historical URLs |
| assetfinder | Passive | Subdomain enumeration |
| amass | Passive/Active | Comprehensive subdomain discovery |
| gobuster | Active | Directory/file bruteforce |
| ffuf | Active | Fuzzing (fastest) |
| dirsearch | Active | Recursive directory scanning |
| whatweb | Active | Technology fingerprinting |
| wafw00f | Active | WAF detection |
| nikto | Active | Vulnerability scanning |
| nuclei | Active | Template-based scanning |

---

## Key Takeaways

- Start with PASSIVE recon - it's stealthy and safe
- Certificate transparency (crt.sh) finds subdomains no one knew about
- Wayback Machine reveals old endpoints that may still be live
- Google dorks find exposed files and directories
- Directory bruteforce finds hidden content
- Always check for zone transfer (AXFR) - free data
- Different tools find different things - use multiple
- Document EVERYTHING - you'll need it later
- Technology detection tells you what exploits to look for
- The quieter you are, the longer you'll have access
