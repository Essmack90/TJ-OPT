---
tags: [index, web-recon, enumeration, module-index]
---

# Information Gathering - Web Edition - Complete Index

## Module Overview

This index covers all Information Gathering - Web Edition modules. Use this as your central navigation point for everything related to web reconnaissance and OSINT.

---

## Core Concepts

| Module | Description | Level |
|--------|-------------|-------|
| Introduction | What is web recon, active vs passive | Beginner |
| Reconnaissance Types | Deep dive into active and passive techniques | Beginner |

---

## Service-Specific Modules

| Module | Topic | Level |
|--------|-------|-------|
| WHOIS | Domain registration information | Beginner |
| DNS | Domain Name System fundamentals | Beginner |
| Digging DNS | Using dig for DNS enumeration | Beginner |
| Subdomains | Understanding subdomains | Beginner |
| Subdomain Bruteforcing | Active subdomain discovery | Intermediate |
| DNS Zone Transfers | AXFR requests and vulnerabilities | Intermediate |
| Virtual Hosts | Discovering vhosts on shared IPs | Intermediate |
| Certificate Transparency Logs | CT logs for passive recon | Intermediate |
| Fingerprinting | Technology identification | Intermediate |
| Crawling | Web spidering fundamentals | Beginner |
| Creepy Crawlies | Web crawling tools | Intermediate |
| robots.txt | Understanding crawler directives | Beginner |
| .well-known URIs | Standardized metadata endpoints | Intermediate |
| Search Engine Discovery | Google dorks and OSINT | Intermediate |
| Web Archives | Wayback Machine and historical data | Intermediate |
| Automating Recon | Frameworks and scripting | Advanced |

---

## Reference Materials

| Document | Description |
|----------|-------------|
| Web-Recon-Cheatsheet | Complete command reference |
| Web-Recon-Core-Summary | What you MUST know |

---

## Quick Navigation by Task

| Task | Recommended Module |
|------|-------------------|
| Find domain owner | WHOIS |
| Map DNS records | DNS, Digging DNS |
| Find subdomains | Subdomains, Subdomain Bruteforcing, Certificate Transparency |
| Try zone transfer | DNS Zone Transfers |
| Find virtual hosts | Virtual Hosts |
| Identify technologies | Fingerprinting |
| Discover hidden pages | Crawling, robots.txt |
| Find metadata | .well-known URIs |
| Google dorks | Search Engine Discovery |
| Find old versions | Web Archives |
| Automate everything | Automating Recon |
| Need a command | Web-Recon-Cheatsheet |
| Review essentials | Web-Recon-Core-Summary |

---

## Quick Command Reference by Task

### WHOIS

whois target.com

### DNS Records

dig target.com A
dig target.com MX
dig target.com NS
dig target.com TXT

### Subdomain Discovery

curl -s "https://crt.sh/?q=%25.target.com&output=json" | jq -r '.[].name_value' | sed 's/\*\.//g' | sort -u

gobuster dns -d target.com -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt -t 50

### Zone Transfer

dig AXFR target.com @ns1.target.com

### Virtual Hosts

gobuster vhost -u http://TARGET_IP -w subdomains.txt --append-domain

### Fingerprinting

curl -I https://target.com
whatweb target.com
wafw00f https://target.com

### Crawling

katana -u https://target.com -d 3 -jc -o urls.txt
curl -s https://target.com/robots.txt | grep -i "disallow"

### .well-known

curl -s https://target.com/.well-known/security.txt
curl -s https://target.com/.well-known/openid-configuration | jq .

### Google Dorks

site:target.com filetype:pdf
site:target.com inurl:admin
site:target.com intitle:"index of"

### Web Archives

curl -s "http://web.archive.org/cdx/search/cdx?url=target.com&output=json&fl=original&collapse=urlkey" | jq -r '.[] | select(length > 0) | .[0]'

### Automation

./finalrecon.py --full --url http://target.com
theHarvester -d target.com -b google

---

## Key Takeaways by Module

### Introduction
- Active recon touches the target (loud)
- Passive recon uses public data (quiet)
- Always start passive, stay passive as long as possible

### WHOIS
- Domain registration is public
- Find owner, registrar, dates, name servers
- Privacy protection hides details, not everything

### DNS
- DNS translates domains to IPs
- A, MX, NS, TXT, CNAME, SOA records
- Each record reveals different infrastructure

### Digging DNS
- dig is the most powerful DNS tool
- Use +short for concise answers
- Query specific name servers with @

### Subdomains
- Subdomains extend the main domain
- Often host dev, admin, or legacy apps
- Subdomains are frequently less secure

### Subdomain Bruteforcing
- Test thousands of potential names
- Wordlists are critical (SecLists)
- dnsenum, gobuster, ffuf

### DNS Zone Transfers
- AXFR copies entire zone file
- Misconfigured servers leak everything
- Always try on every name server

### Virtual Hosts
- Multiple sites on one IP
- Use Host header to differentiate
- gobuster vhost enumerates them

### Certificate Transparency
- Every SSL cert is public
- crt.sh reveals all subdomains ever certified
- Best passive subdomain source

### Fingerprinting
- Identify technologies and versions
- curl -I for headers
- whatweb, wafw00f, nikto

### Crawling
- Follow links to discover pages
- robots.txt reveals hidden paths
- Katana, gospider, Scrapy

### robots.txt
- Instructions for crawlers
- Disallowed paths are often interesting
- Always check it

### .well-known URIs
- Standardized metadata location
- security.txt, openid-configuration
- Predictable endpoints = predictable recon

### Search Engine Discovery
- Google dorks find hidden content
- site:, filetype:, inurl:, intitle:
- Google Hacking Database (GHDB)

### Web Archives
- Wayback Machine has historical snapshots
- Find removed pages and files
- API access for automation

### Automating Recon
- FinalRecon combines multiple modules
- Recon-ng is a professional framework
- theHarvester finds emails
- Custom scripts tie everything together

---

## Learning Path

Introduction
Reconnaissance Types
WHOIS
DNS
Digging DNS
Subdomains
Certificate Transparency Logs
Subdomain Bruteforcing
DNS Zone Transfers
Virtual Hosts
Fingerprinting
Crawling
robots.txt
.well-known URIs
Search Engine Discovery
Web Archives
Automating Recon
Practice with Cheatsheet
Review Core Summary

---

## Additional Resources

| Resource | Description |
|----------|-------------|
| crt.sh | Certificate Transparency logs |
| Google Hacking Database | Pre-made Google dorks |
| Wayback Machine | Web archive |
| SecLists | Wordlists for brute forcing |
| Exploit-DB | Vulnerabilities by version |

---

## Version Information

Module Version: 1.0
Last Updated: 2026-03-17
Pathway: Information Gathering - Web Edition
