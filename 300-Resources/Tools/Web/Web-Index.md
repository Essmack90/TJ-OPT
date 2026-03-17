---
tags: [index, web, moc]
---

# Web Application Testing Tools Index

## Quick Navigation

| Category | Tools | Use Case |
|----------|-------|----------|
| Fuzzers | 6 tools | Directory/file discovery |
| Scanners | 4 tools | Automated scanning |
| Crawlers | 3 tools | Endpoint discovery |
| Python Tools | 5 tools | Specialized web attacks |
| Tomnomnom | 7 tools | URL/domain utilities |
| CMS Tools | 3 tools | Technology detection |
| XSS Tools | 2 tools | XSS discovery |
| ProjectDiscovery | 5 tools | Modern web toolkit |

## Fuzzers & Content Discovery

- ffuf - Fast web fuzzer (Go)
- gobuster - Directory/DNS brute force
- dirb - Classic directory scanner
- wfuzz - Web application brute forcer
- feroxbuster - Recursive content discovery
- dirsearch - Python directory brute forcer

## Vulnerability Scanners

- nikto - Web server scanner
- wpscan - WordPress vulnerability scanner
- nuclei - Template-based scanner
- wafw00f - WAF detection

## Crawlers & Probers

- katana - Fast web crawler
- httpx - HTTP prober
- httprobe - Live host probe

## Python Web Tools

- arjun - HTTP parameter discovery
- xsstrike - XSS detection suite
- cmseek - CMS detection
- dalfox - XSS scanner (Go/Python)
- whatweb - Web technology fingerprinter

## Tomnomnom Tools (URL Utilities)

- assetfinder - Subdomain finder
- httprobe - Probe for working HTTP/HTTPS
- waybackurls - Wayback Machine URLs
- unfurl - URL data extraction
- gf - Grep wrapper for patterns
- qsreplace - Query string replacer
- meg - Many endpoint grabber

## CMS & Fingerprinting

- wpscan - WordPress scanner
- whatweb - Technology detection
- cmseek - CMS detection

## XSS Tools

- dalfox - Advanced XSS scanner
- xsstrike - XSS detection suite

## ProjectDiscovery Tools

- nuclei - Vulnerability scanner
- katana - Web crawler
- httpx - HTTP prober
- dnsx - DNS toolkit
- subfinder - Subdomain discovery

## Kali System Tools

- nikto - Web server scanner
- wpscan - WordPress scanner
- whatweb - Technology detection
- wafw00f - WAF detection
- dirb - Directory scanner
- gobuster - Multi-purpose brute forcer
- wfuzz - Web fuzzer

## Quick Reference by Phase

### Reconnaissance Phase

assetfinder target.com | httprobe | tee hosts.txt
sublist3r -d target.com
waybackurls target.com | unfurl domains
ffuf -w wordlist.txt -u https://target.com/FUZZ
gobuster dir -u https://target.com -w wordlist.txt
whatweb https://target.com
wafw00f https://target.com

### Scanning Phase

nuclei -u https://target.com
nikto -h https://target.com
wpscan --url https://target.com
arjun -u https://target.com/page
katana -u https://target.com -jc

### Exploitation Phase

dalfox url https://target.com/page\?param\=test
xsstrike -u "https://target.com/page?q=test"
wpscan --url https://target.com --enumerate u,vp,vt
cmseek -u https://target.com

## Full Web Recon Workflow

subfinder -d target.com | tee subdomains.txt
assetfinder target.com >> subdomains.txt
cat subdomains.txt | httpx -title -tech-detect -status-code | tee live.txt
katana -list live.txt -jc -o endpoints.txt
nuclei -list live.txt -t cves/ -t misconfiguration/

## Directory Fuzzing

ffuf -w /usr/share/seclists/Discovery/Web-Content/common.txt -u https://target.com/FUZZ -fc 404
feroxbuster -u https://target.com -w wordlist.txt -x php,txt,html

## URL Processing

waybackurls target.com | tee urls.txt
cat urls.txt | unfurl domains | sort -u
cat urls.txt | gf xss | gf sqli

## Notes

- Go tools are in ~/go/bin/ - add to PATH
- Python tools are in ~/.local/bin/
- ProjectDiscovery tools need regular updates: nuclei -update-templates
- Wordlists in /usr/share/seclists/ and /usr/share/wordlists/
