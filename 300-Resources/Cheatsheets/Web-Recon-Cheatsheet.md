---
tags: [cheatsheet, web-recon, osint, dns, subdomains, crawling, google-dorking]
---

# Information Gathering - Web Edition Cheatsheet

## Reconnaissance Types

| Type | Description | Risk | Examples |
|------|-------------|------|----------|
| Active | Direct interaction with target | Higher | Port scanning, vulnerability scanning |
| Passive | No direct interaction | Lower | Search queries, WHOIS, DNS enumeration |

---

## Primary Goals

| Goal | Description |
|------|-------------|
| Identifying Assets | Domains, subdomains, IP addresses |
| Uncovering Hidden Info | Directories, files, technologies |
| Analyzing Attack Surface | Open ports, services, versions |
| Gathering Intelligence | Employees, emails, tech stack |

---

## WHOIS

### Basic WHOIS Lookup

whois example.com

### Extract Specific Info

# Get registrar
whois example.com | grep -i "registrar:" | head -1

# Get creation date
whois example.com | grep -i "creation date:" | head -1

# Get name servers
whois example.com | grep -i "name server:" | awk '{print $3}' | sort -u

# Get registrant email
whois example.com | grep -i "registrant email:" | awk '{print $3}'

### IP WHOIS

whois 8.8.8.8

### Autonomous System WHOIS

whois AS15169

---

## DNS

### DNS Record Types

| Record | Description |
|--------|-------------|
| A | Maps hostname to IPv4 address |
| AAAA | Maps hostname to IPv6 address |
| CNAME | Alias for another hostname |
| MX | Mail servers for the domain |
| NS | Authoritative name servers |
| TXT | Arbitrary text information |
| SOA | Administrative zone information |

### dig Commands

# Basic A record lookup
dig example.com A

# IPv6 address
dig example.com AAAA

# Mail servers
dig example.com MX

# Name servers
dig example.com NS

# TXT records
dig example.com TXT

# SOA record
dig example.com SOA

# ALL records
dig example.com ANY

# Query specific name server
dig @8.8.8.8 example.com A

# Short answer only
dig +short example.com A

# Trace full resolution path
dig +trace example.com

# Reverse DNS lookup
dig -x 8.8.8.8

### nslookup

nslookup example.com
nslookup -type=MX example.com
nslookup -type=NS example.com

### host

host example.com
host -t MX example.com
host -t NS example.com
host -t TXT example.com

---

## Subdomains

### Passive Enumeration

# Certificate Transparency (crt.sh)
curl -s "https://crt.sh/?q=%25.example.com&output=json" | jq -r '.[].name_value' | sed 's/\*\.//g' | sort -u

# SecurityTrails (with API)
curl -s "https://api.securitytrails.com/v1/domain/example.com/subdomains" -H "APIKEY: YOUR_KEY"

# AlienVault OTX
curl -s "https://otx.alienvault.com/api/v1/indicators/domain/example.com/passive_dns" | jq -r '.passive_dns[].hostname'

# Wayback Machine
curl -s "http://web.archive.org/cdx/search/cdx?url=*.example.com&output=json&fl=original&collapse=urlkey" | jq -r '.[] | select(length > 0) | .[0]'

### Active Enumeration

# gobuster
gobuster dns -d example.com -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt -t 50

# dnsenum
dnsenum --dnsserver 8.8.8.8 --enum -p 0 -s 0 -o subdomains.txt -f /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt example.com

# dnsrecon
dnsrecon -d example.com -t brt -D /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt

# fierce
fierce --domain example.com --dns-servers 8.8.8.8

# Basic bash loop
for sub in $(cat /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt); do
    host $sub.example.com | grep "has address"
done

---

## Zone Transfers (AXFR)

### Check for Zone Transfer

dig AXFR example.com @ns1.example.com
host -l example.com ns1.example.com
nslookup -type=AXFR example.com ns1.example.com

### Test All Name Servers

for ns in $(dig NS example.com +short); do
    echo "[*] Testing $ns"
    dig AXFR example.com @$ns
done

---

## Virtual Hosts

### gobuster vhost

gobuster vhost -u http://192.168.1.10 -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt --append-domain

### ffuf vhost

ffuf -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt -H "Host: FUZZ.example.com" -u http://TARGET_IP -fc 404

### Manual Hosts File

# Add to /etc/hosts
echo "192.168.1.10 dev.example.com" | sudo tee -a /etc/hosts
echo "192.168.1.10 admin.example.com" | sudo tee -a /etc/hosts

---

## Certificate Transparency Logs

### crt.sh Queries

# Basic query
curl -s "https://crt.sh/?q=example.com&output=json" | jq -r '.[].name_value' | sort -u

# Remove wildcards
curl -s "https://crt.sh/?q=example.com&output=json" | jq -r '.[].name_value' | sed 's/\*\.//g' | sort -u

# Filter for specific patterns
curl -s "https://crt.sh/?q=example.com&output=json" | jq -r '.[].name_value' | grep -E "dev|staging|test" | sort -u

# Get with metadata
curl -s "https://crt.sh/?q=example.com&output=json" | jq '.[] | {id: .id, name: .name_value, issued: .not_before}'

---

## Fingerprinting

### Banner Grabbing

curl -I http://example.com
curl -I https://example.com
curl -IL http://example.com  # Follow redirects

### whatweb

whatweb example.com
whatweb -a 3 example.com  # Aggressive scan

### wafw00f (WAF Detection)

wafw00f https://example.com

### nikto (Fingerprint Only)

nikto -h https://example.com -Tuning b

### nmap Fingerprinting

nmap -sV -p 80,443 example.com
nmap -O -sV -p 80,443 example.com

---

## Web Crawling

### Katana

katana -u https://example.com
katana -u https://example.com -d 3
katana -u https://example.com -jc -o urls.txt

### gospider

gospider -s https://example.com --js -o output

### robots.txt

curl -s https://example.com/robots.txt
curl -s https://example.com/robots.txt | grep -i "disallow"

### sitemap.xml

curl -s https://example.com/sitemap.xml | grep -oP '<loc>\K[^<]+'

---

## Search Engine Discovery (Google Dorks)

### Site Operators

site:example.com
site:example.com -www
site:*.example.com

### File Types

site:example.com filetype:pdf
site:example.com filetype:docx
site:example.com filetype:xlsx
site:example.com filetype:sql
site:example.com filetype:log
site:example.com filetype:conf
site:example.com filetype:env
site:example.com filetype:bak

### URL Patterns

site:example.com inurl:admin
site:example.com inurl:login
site:example.com inurl:backup
site:example.com inurl:config
site:example.com inurl:dev
site:example.com inurl:test
site:example.com inurl:api

### Page Titles

site:example.com intitle:"index of"
site:example.com intitle:"login"
site:example.com intitle:"admin"
site:example.com intitle:"phpinfo"

### Exact Phrases

site:example.com "password reset"
site:example.com "confidential"
site:example.com "internal use only"
site:example.com "do not distribute"

### Error Messages

site:example.com "warning"
site:example.com "error"
site:example.com "mysql_fetch"
site:example.com "parse error"

### Combined Dorks

site:example.com (inurl:admin OR inurl:login)
site:example.com (filetype:pdf OR filetype:docx) "confidential"
site:example.com intitle:"index of" (backup OR admin)

---

## Web Archives

### Wayback Machine

# Get all URLs
curl -s "http://web.archive.org/cdx/search/cdx?url=example.com&output=json&fl=original&collapse=urlkey" | jq -r '.[] | select(length > 0) | .[0]' | sort -u

# Get PDFs
curl -s "http://web.archive.org/cdx/search/cdx?url=example.com&filter=original:.*\.pdf&output=json&fl=original,timestamp" | jq -r '.[] | "https://web.archive.org/web/\(.[1])/\(.[0])"'

# Get subdomains
curl -s "http://web.archive.org/cdx/search/cdx?url=*.example.com&output=json&fl=original&collapse=urlkey" | jq -r '.[] | select(length > 0) | .[0]'

# Date range
curl -s "http://web.archive.org/cdx/search/cdx?url=example.com&from=20200101&to=20201231"

### View Snapshots

https://web.archive.org/web/20200101000000/https://example.com
https://web.archive.org/web/\*/https://example.com

---

## Automation Tools

### FinalRecon

git clone https://github.com/thewhiteh4t/FinalRecon.git
cd FinalRecon
pip3 install -r requirements.txt

# Modules
./finalrecon.py --url http://example.com --headers
./finalrecon.py --url http://example.com --whois
./finalrecon.py --url http://example.com --dns
./finalrecon.py --url http://example.com --sub
./finalrecon.py --url http://example.com --crawl
./finalrecon.py --url http://example.com --dir
./finalrecon.py --url http://example.com --wayback
./finalrecon.py --url http://example.com --full

### theHarvester

git clone https://github.com/laramies/theHarvester.git
cd theHarvester
python3 -m pip install -r requirements/base.txt

theHarvester -d example.com -b google
theHarvester -d example.com -b google,bing,linkedin
theHarvester -d example.com -b shodan -f results.html

### Recon-ng

git clone https://github.com/lanmaster53/recon-ng.git
cd recon-ng
pip3 install -r REQUIREMENTS
./recon-ng

# In recon-ng
workspace create example
marketplace search
marketplace install recon/domains-hosts/google_site_web
modules load recon/domains-hosts/google_site_web
options set SOURCE example.com
run

### SpiderFoot

docker pull spiderfoot
docker run -p 5001:5001 spiderfoot

# Access at http://localhost:5001

---

## Quick One-Liners

# Certificate Transparency subdomains
curl -s "https://crt.sh/?q=%25.example.com&output=json" | jq -r '.[].name_value' | sed 's/\*\.//g' | sort -u

# Wayback Machine URLs
curl -s "http://web.archive.org/cdx/search/cdx?url=example.com&output=json&fl=original&collapse=urlkey" | jq -r '.[] | select(length > 0) | .[0]'

# DNS A records
dig +short example.com A

# All DNS records
dig example.com ANY +noall +answer

# Check zone transfer
dig AXFR example.com @$(dig NS example.com +short | head -1)

# Extract emails from webpage
curl -s https://example.com | grep -oE '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}' | sort -u

# HTTP headers
curl -sI https://example.com

# Technology detection
whatweb example.com

# WAF detection
wafw00f https://example.com

# robots.txt disallowed paths
curl -s https://example.com/robots.txt | grep -i "disallow:" | awk '{print $2}'

---

## Key Takeaways

- Always start with passive recon (WHOIS, DNS, CT logs, archives)
- Use multiple tools and sources for comprehensive results
- Document everything - you'll need it later
- Combine active and passive techniques
- Respect rate limits and robots.txt
- Automation scales, but manual verification catches edge cases
- The more you find, the more attack surface you have
- This is 100% legal - all public information
