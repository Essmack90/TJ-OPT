---
tags: [module/web-recon, fingerprinting, wappalyzer, whatweb, nikto, wafw00f, automation, level/advanced, practical]
---

# Fingerprinting - Practical Application

## Complete Fingerprinting Workflow

Phase 1: Manual Header Analysis
Phase 2: WAF Detection
Phase 3: Automated Fingerprinting
Phase 4: CMS Detection
Phase 5: Technology Stack Analysis
Phase 6: Version Vulnerability Correlation
Phase 7: Automation

---

## Phase 1: Manual Header Analysis

### Basic Header Fetch

```bash
curl -I http://target.com
curl -I https://target.com
Follow All Redirects
bash
curl -IL http://target.com
Get All Headers (Including Response Headers)
bash
curl -i http://target.com | head -20
Custom User-Agent (Avoid Default Detection)
bash
curl -I -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" http://target.com
Common Headers to Check
Header	What It Reveals
Server	Web server software and version
X-Powered-By	Backend technology (PHP, ASP.NET, etc.)
X-AspNet-Version	ASP.NET version
X-Drupal-Cache	Drupal CMS
X-Generator	Often reveals CMS (e.g., "WordPress 5.8")
X-Varnish	Varnish cache (may reveal backend)
Via	Proxy information
Set-Cookie	PHPSESSID= (PHP), JSESSIONID= (Java), ASP.NET_SessionId= (.NET)
Link	WordPress API endpoints
Manual Header Analysis Script
bash
#!/bin/bash
TARGET=$1

echo "=== Header Analysis for $TARGET ==="
echo ""

echo "[*] HTTP Headers:"
curl -s -I -A "Mozilla/5.0" http://$TARGET | sed 's/\r$//'
echo ""

echo "[*] HTTPS Headers:"
curl -s -I -k -A "Mozilla/5.0" https://$TARGET | sed 's/\r$//'
echo ""

echo "[*] Following redirects:"
curl -s -IL -A "Mozilla/5.0" http://$TARGET | sed 's/\r$//'
Phase 2: WAF Detection
Basic wafw00f Scan
bash
wafw00f https://target.com
Multiple Targets
bash
for domain in $(cat domains.txt); do
    wafw00f https://$domain
done
Manual WAF Detection
bash
# Check for common WAF cookies
curl -I https://target.com | grep -i "cf-ray\|__cfduid\|mod_security\|sucuri\|wordfence"

# Send malicious payload to trigger WAF
curl -X POST https://target.com -d "1=1' union select 1,2,3-- -" -i
WAF Fingerprinting with Custom Script
Save as waf-detect.sh:

bash
#!/bin/bash
TARGET=$1

echo "[*] Testing WAF on $TARGET"

# List of common WAF signatures
declare -A WAF_SIGNATURES=(
    ["Cloudflare"]="cf-ray|__cfduid"
    ["AWS WAF"]="x-amz-cf-id|AWSALB"
    ["ModSecurity"]="mod_security|NOYB"
    ["Wordfence"]="wordfence|wfvt_"
    ["Sucuri"]="sucuri|X-Sucuri"
    ["F5 BIG-IP"]="BIG-IP|F5"
    ["Akamai"]="akamai|AkamaiGHost"
    ["Imperva"]="incapsula|X-Iinfo"
)

response=$(curl -s -I https://$TARGET)

for waf in "${!WAF_SIGNATURES[@]}"; do
    if echo "$response" | grep -qiE "${WAF_SIGNATURES[$waf]}"; then
        echo "[+] Detected: $waf WAF"
    fi
done
Phase 3: Automated Fingerprinting
WhatWeb
Basic scan:
bash
whatweb https://target.com
Aggressive scan:
bash
whatweb -a 3 https://target.com
Save output:
bash
whatweb -a 3 https://target.com --log-verbose=whatweb-report.txt
Wappalyzer CLI (if installed)
bash
wappalyzer https://target.com
BuiltWith API
bash
curl "https://api.builtwith.com/v21/api.json?KEY=YOUR_KEY&LOOKUP=target.com"
Nmap Fingerprinting
bash
# OS and service detection
sudo nmap -O -sV -p 80,443 target.com

# HTTP script scanning
nmap -p 80,443 --script http-* target.com

# Specific HTTP fingerprints
nmap -p 80,443 --script http-server-header,http-title,http-generator target.com
Phase 4: CMS Detection
WordPress Detection
bash
# Check common WordPress paths
curl -s https://target.com/wp-login.php | grep -i "wordpress"
curl -s https://target.com/wp-json/wp/v2/users | jq .

# Use wpscan (WordPress specific)
wpscan --url https://target.com --enumerate u,vp,vt
Joomla Detection
bash
# Check for Joomla paths
curl -s https://target.com/administrator/ | grep -i "joomla"
curl -s https://target.com/language/en-GB/en-GB.xml | grep -i "version"

# Use joomscan
perl joomscan.pl --url https://target.com
Drupal Detection
bash
# Check for Drupal paths
curl -s https://target.com/CHANGELOG.txt | grep -i "drupal"
curl -s https://target.com/node | grep -i "drupal"

# Use droopescan
droopescan scan drupal -u https://target.com
Magento Detection
bash
curl -s https://target.com/js/mage/ | grep -i "magento"
curl -s https://target.com/skin/frontend/ | grep -i "css"
Phase 5: Technology Stack Analysis
JavaScript Library Detection
bash
# Extract all script tags
curl -s https://target.com | grep -oP '<script src="[^"]+"' | cut -d'"' -f2

# Check for common libraries
curl -s https://target.com | grep -i "jquery\|vue\|react\|angular\|bootstrap"
Framework Detection
bash
# Laravel
curl -I https://target.com | grep -i "laravel_session"

# Django
curl -I https://target.com | grep -i "csrftoken\|django_language"

# Rails
curl -I https://target.com | grep -i "_session_id\|rails"
Cookie Analysis
bash
curl -I https://target.com | grep -i "set-cookie" | cut -d':' -f2
Common Cookies and Their Meaning:
Cookie	Technology
PHPSESSID	PHP
JSESSIONID	Java (JSP)
ASP.NET_SessionId	ASP.NET
laravel_session	Laravel
django_language	Django
_cfduid	Cloudflare
AWSALB	AWS Load Balancer
Phase 6: Version Vulnerability Correlation
Extract Versions from Fingerprinting
bash
# Get Apache version
curl -I https://target.com | grep -i "server:" | cut -d'/' -f2

# Get PHP version (often in headers)
curl -I https://target.com | grep -i "x-powered-by:" | cut -d'/' -f2
Check for Known Vulnerabilities
bash
# Search for Apache version exploits
searchsploit apache 2.4.41

# Search for PHP version exploits
searchsploit php 7.4.3

# Search for WordPress version exploits
searchsploit wordpress 5.8
Automated Version Checking Script
Save as version-check.sh:

bash
#!/bin/bash
TARGET=$1

echo "[*] Extracting versions for $TARGET"

# Get server version
server=$(curl -s -I https://$TARGET | grep -i "^server:" | cut -d' ' -f2- | tr -d '\r')
echo "[*] Server: $server"

# Get powered-by
powered=$(curl -s -I https://$TARGET | grep -i "^x-powered-by:" | cut -d' ' -f2- | tr -d '\r')
echo "[*] X-Powered-By: $powered"

# Get generator from HTML
generator=$(curl -s https://$TARGET | grep -i "generator" | grep -oP 'content="[^"]+"' | cut -d'"' -f2)
echo "[*] Generator: $generator"

# Check for vulnerabilities
echo ""
echo "[*] Checking for known vulnerabilities..."
if [[ ! -z "$server" ]]; then
    searchsploit "$server" 2>/dev/null | head -20
fi
Phase 7: Automation
Complete Fingerprinting Script
Save as fingerprint.sh:

bash
#!/bin/bash
TARGET=$1
OUTPUT_DIR="fingerprint-$TARGET"
mkdir -p $OUTPUT_DIR

echo "[*] Starting comprehensive fingerprinting for $TARGET"

# Phase 1: Header Analysis
echo "[*] Analyzing headers..."
curl -s -I -A "Mozilla/5.0" https://$TARGET > $OUTPUT_DIR/headers.txt
curl -s -I -A "Mozilla/5.0" http://$TARGET >> $OUTPUT_DIR/headers.txt

# Phase 2: WAF Detection
echo "[*] Checking for WAF..."
wafw00f https://$TARGET > $OUTPUT_DIR/waf.txt 2>/dev/null

# Phase 3: WhatWeb Scan
echo "[*] Running WhatWeb..."
whatweb -a 3 https://$TARGET > $OUTPUT_DIR/whatweb.txt 2>/dev/null

# Phase 4: Nikto Fingerprint Scan
echo "[*] Running Nikto (fingerprint only)..."
if [ -f ~/nikto/program/nikto.pl ]; then
    perl ~/nikto/program/nikto.pl -h https://$TARGET -Tuning b -o $OUTPUT_DIR/nikto.txt > /dev/null 2>&1
fi

# Phase 5: Nmap Scan
echo "[*] Running Nmap fingerprinting..."
sudo nmap -sV -p 80,443 --script http-server-header,http-title,http-generator $TARGET -oN $OUTPUT_DIR/nmap.txt > /dev/null 2>&1

# Phase 6: Extract Key Information
echo "[*] Extracting key findings..."

# Server
grep -i "server:" $OUTPUT_DIR/headers.txt | head -1 >> $OUTPUT_DIR/summary.txt

# X-Powered-By
grep -i "x-powered-by:" $OUTPUT_DIR/headers.txt >> $OUTPUT_DIR/summary.txt

# CMS Detection
if grep -qi "wordpress" $OUTPUT_DIR/whatweb.txt; then
    echo "CMS: WordPress" >> $OUTPUT_DIR/summary.txt
fi

if grep -qi "joomla" $OUTPUT_DIR/whatweb.txt; then
    echo "CMS: Joomla" >> $OUTPUT_DIR/summary.txt
fi

if grep -qi "drupal" $OUTPUT_DIR/whatweb.txt; then
    echo "CMS: Drupal" >> $OUTPUT_DIR/summary.txt
fi

# WAF Detection
if grep -qi "behind" $OUTPUT_DIR/waf.txt; then
    grep "behind" $OUTPUT_DIR/waf.txt >> $OUTPUT_DIR/summary.txt
fi

echo "[*] Fingerprinting complete!"
echo "[*] Results saved in $OUTPUT_DIR/"
echo "[*] Summary:"
cat $OUTPUT_DIR/summary.txt
Fingerprinting Cheatsheet
Goal	Command
Basic headers	curl -I https://target.com
All redirects	curl -IL https://target.com
Custom user-agent	curl -I -A "Mozilla/5.0" https://target.com
WAF detection	wafw00f https://target.com
WhatWeb (aggressive)	whatweb -a 3 https://target.com
Nikto (fingerprint)	nikto -h https://target.com -Tuning b
Nmap service scan	nmap -sV -p 80,443 target.com
WordPress scan	wpscan --url https://target.com
Joomla scan	joomscan --url https://target.com
Drupal scan	droopescan scan drupal -u https://target.com
Tool Comparison
Tool	Type	Best For
curl	Manual	Quick header analysis
wafw00f	Passive	WAF detection
WhatWeb	Passive/Active	General fingerprinting
Nikto	Active	Vulnerability + fingerprinting
Nmap	Active	Service + OS detection
WPScan	Active	WordPress specific
Joomscan	Active	Joomla specific
Droopescan	Active	Drupal specific
Key Takeaways
Start with manual header analysis using curl

Always check for WAFs before deeper scanning

Follow all redirects - they reveal information

Use multiple tools (WhatWeb, Nikto, Nmap) for completeness

CMS-specific scanners (WPScan, Joomscan) are more thorough

Extract version numbers and correlate with vulnerabilities

Document all findings in a technology stack profile

Custom user-agents can avoid basic detection

Check cookies for technology hints

Look at HTML source for generator tags

Combine fingerprinting with subdomain enumeration

Automate the process for large targets
