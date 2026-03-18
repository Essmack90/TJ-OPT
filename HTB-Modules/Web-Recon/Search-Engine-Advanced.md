---
tags: [module/web-recon, search-engine, google-dorking, osint, automation, ghdb, level/advanced, practical]
---

# Search Engine Discovery - Practical Application

## Complete Search Engine Discovery Workflow

Phase 1: Target Definition
Phase 2: Basic Reconnaissance
Phase 3: Advanced Dorking
Phase 4: File Discovery
Phase 5: Vulnerability Discovery
Phase 6: Automation
Phase 7: Alternative Search Engines

---

## Phase 1: Target Definition

### Identify Target Domain

Primary domain: example.com
Alternative domains: example.net, example.org
Subdomains: dev.example.com, staging.example.com

### Identify Related Entities

Use reverse WHOIS to find related domains:
https://viewdns.info/reversewhois/

Use certificate transparency:
curl -s "https://crt.sh/?q=%25example.com&output=json" | jq -r '.[].name_value' | sed 's/*.//g' | sort -u

---

## Phase 2: Basic Reconnaissance

### Site Mapping

site:example.com
Shows every indexed page.

site:example.com -www
Shows non-www subdomains.

### Subdomain Discovery

site:*.example.com
Finds all subdomains.

site:example.com -inurl:www
Excludes www.

### Directory Discovery

site:example.com intitle:"index of"
Finds open directories.

site:example.com inurl:admin
Finds admin areas.

site:example.com inurl:backup
Finds backup directories.

---

## Phase 3: Advanced Dorking

### Login Page Discovery

site:example.com inurl:login
site:example.com inurl:signin
site:example.com inurl:auth
site:example.com intitle:"login" intitle:"page"
site:example.com (inurl:admin OR inurl:login)
site:example.com (intitle:"admin" OR intitle:"login")

### Admin Panel Discovery

site:example.com inurl:admin
site:example.com inurl:dashboard
site:example.com inurl:control
site:example.com intitle:"admin panel"
site:example.com intitle:"control panel"
site:example.com inurl:cpanel
site:example.com inurl:webadmin

### Development Environments

site:example.com inurl:dev
site:example.com inurl:staging
site:example.com inurl:test
site:example.com inurl:uat
site:example.com inurl:demo
site:example.com intitle:"development"
site:example.com intitle:"staging"

---

## Phase 4: File Discovery

### Document Discovery

# PDFs
site:example.com filetype:pdf
site:example.com filetype:pdf confidential
site:example.com filetype:pdf "internal use only"

# Office documents
site:example.com (filetype:doc OR filetype:docx)
site:example.com (filetype:xls OR filetype:xlsx)
site:example.com (filetype:ppt OR filetype:pptx)

# Text files
site:example.com filetype:txt
site:example.com filetype:txt password
site:example.com filetype:txt "api key"

### Configuration Files

# Web server configs
site:example.com filetype:conf
site:example.com filetype:config
site:example.com inurl:config.php
site:example.com ext:conf ext:cnf
site:example.com ext:cfg ext:config

# Environment files
site:example.com filetype:env .env
site:example.com inurl:.env
site:example.com filetype:yml .env
site:example.com filetype:yaml

# XML files
site:example.com filetype:xml
site:example.com inurl:sitemap.xml
site:example.com inurl:web.config

### Database Files

site:example.com filetype:sql
site:example.com filetype:sql "INSERT INTO"
site:example.com filetype:sql "CREATE TABLE"
site:example.com inurl:backup.sql
site:example.com "dump.sql"
site:example.com "database.sql"
site:example.com filetype:sql "password"

### Backup Files

site:example.com filetype:bak
site:example.com filetype:backup
site:example.com filetype:old
site:example.com filetype:orig
site:example.com inurl:backup.zip
site:example.com inurl:backup.tar.gz
site:example.com (backup.sql OR database.sql)

### Log Files

site:example.com filetype:log
site:example.com inurl:error_log
site:example.com inurl:access_log
site:example.com filetype:log "error"
site:example.com filetype:log "password"

---

## Phase 5: Vulnerability Discovery

### Error Messages

site:example.com "warning" "error"
site:example.com "mysql_fetch"
site:example.com "parse error"
site:example.com "include_path"
site:example.com "failed to open stream"
site:example.com "Fatal error"

### Exposed Version Information

site:example.com intitle:"phpinfo" ext:php
site:example.com inurl:phpinfo.php
site:example.com intitle:"Apache Status"
site:example.com intitle:"Server Status"
site:example.com "Apache/2.2.*" "Server at"
site:example.com "nginx/1.18.*"

### Directory Listings

intitle:"index of" site:example.com
intitle:"index of" /etc
intitle:"index of" /config
intitle:"index of" /backup
intitle:"index of" /logs
intitle:"index of" /tmp
intitle:"index of" /admin
intitle:"index of" /private

### Sensitive Parameters

site:example.com inurl:?id=
site:example.com inurl:?page=
site:example.com inurl:?file=
site:example.com inurl:?path=
site:example.com inurl:?redirect=
site:example.com inurl:?url=
site:example.com inurl:?cmd=
site:example.com inurl:?exec=

### SQL Injection Indicators

site:example.com inurl:?id=1
site:example.com inurl:?id=1'
site:example.com "mysql error"
site:example.com "supplied argument is not a valid MySQL"

### XSS Indicators

site:example.com inurl:?search=
site:example.com inurl:?q=
site:example.com inurl:?s=
site:example.com "document.cookie"

---

## Phase 6: Automation

### Python Automation Script

Save as google-dork.py:

#!/usr/bin/env python3
import requests
import time
import sys
from urllib.parse import quote

class GoogleDorker:
    def __init__(self, domain):
        self.domain = domain
        self.results = []
        
    def dork(self, query, delay=2):
        """Execute a single dork query"""
        full_query = f"site:{self.domain} {query}"
        encoded = quote(full_query)
        url = f"https://www.google.com/search?q={encoded}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        print(f"[*] Searching: {full_query}")
        time.sleep(delay)  # Be polite to Google
        
        # Note: This is simplified. Real implementation would need to parse HTML
        # or use Google's Custom Search API
        return full_query
    
    def run_batch(self, queries, delay=2):
        """Run multiple dorks"""
        for query in queries:
            self.dork(query, delay)
            time.sleep(delay)
    
    def save_results(self, filename):
        with open(filename, 'w') as f:
            for result in self.results:
                f.write(result + '\n')

# Example usage
if __name__ == "__main__":
    dorker = GoogleDorker(sys.argv[1])
    
    queries = [
        'filetype:pdf',
        'filetype:docx',
        'inurl:admin',
        'inurl:login',
        'intitle:"index of"',
        'filetype:sql',
        'filetype:env',
        'inurl:backup',
        'filetype:log'
    ]
    
    dorker.run_batch(queries)

### Bash Automation Script

Save as google-dork.sh:

#!/bin/bash
DOMAIN=$1
OUTPUT_DIR="dorks-$DOMAIN"
mkdir -p $OUTPUT_DIR

echo "[*] Starting Google dorking for $DOMAIN"

# Array of dorks
declare -a DORKS=(
    "filetype:pdf"
    "filetype:docx"
    "filetype:xlsx"
    "filetype:sql"
    "filetype:env"
    "filetype:log"
    "filetype:conf"
    "filetype:bak"
    "inurl:admin"
    "inurl:login"
    "inurl:backup"
    "inurl:config"
    "intitle:\"index of\""
    "ext:php intitle:phpinfo"
    "\"error\" \"warning\""
)

for dork in "${DORKS[@]}"; do
    echo "[*] Searching: site:$DOMAIN $dork"
    
    # URL encode the query
    query=$(echo "site:$DOMAIN $dork" | sed 's/ /%20/g' | sed 's/:/%3A/g' | sed 's/"//g')
    
    # Save to file
    echo "site:$DOMAIN $dork" >> "$OUTPUT_DIR/searches.txt"
    
    # Be polite
    sleep 3
done

echo "[*] Dorking complete. Check $OUTPUT_DIR/"

### Using Google Custom Search API

Get API key from: https://developers.google.com/custom-search/v1/introduction

#!/bin/bash
API_KEY="YOUR_API_KEY"
SEARCH_ENGINE_ID="YOUR_SEARCH_ENGINE_ID"
DOMAIN=$1
DORK=$2

curl -s "https://www.googleapis.com/customsearch/v1?q=site:$DOMAIN%20$DORK&key=$API_KEY&cx=$SEARCH_ENGINE_ID" | jq '.items[] | {title: .title, link: .link, snippet: .snippet}'

---

## Phase 7: Alternative Search Engines

### Bing

site:example.com filetype:pdf
Same operators mostly work.

### DuckDuckGo

site:example.com inurl:admin
Privacy-focused, similar syntax.

### Yandex

Useful for non-English targets.

### Shodan - Internet Device Search

Shodan searches for devices, not web pages.

hostname:example.com
Find all devices with that hostname.

port:443 hostname:example.com
Find HTTPS services.

ssl.cert.subject.cn:example.com
Find certificates.

### Censys

Similar to Shodan.

https://censys.io

### Wayback Machine - Historical Data

http://web.archive.org/cdx/search/cdx\?url\=\*.example.com\&output\=json\&fl\=original\&collapse\=urlkey

curl -s "http://web.archive.org/cdx/search/cdx?url=*.example.com&output=json&fl=original&collapse=urlkey" | jq -r '.[] | select(length > 0) | .[0]' | sort -u

---

## Google Dorking Cheatsheet

| Goal | Dork |
|------|------|
| All pages | site:example.com |
| PDF files | site:example.com filetype:pdf |
| Excel files | site:example.com filetype:xlsx |
| SQL dumps | site:example.com filetype:sql |
| Config files | site:example.com filetype:conf |
| Login pages | site:example.com inurl:login |
| Admin areas | site:example.com inurl:admin |
| Directories | intitle:"index of" site:example.com |
| Backups | site:example.com inurl:backup |
| Error pages | site:example.com "warning" "error" |
| PHP info | site:example.com intitle:phpinfo |
| Environment | site:example.com filetype:env |
| Git repos | site:example.com inurl:.git |
| API keys | site:example.com "api_key" |
| Passwords | site:example.com "password" filetype:txt |

---

## Key Takeaways

- Google Dorking is powerful but has limitations
- Google may block automated queries
- Always check robots.txt
- Be polite with delays
- Combine multiple search engines
- Use the Wayback Machine for historical data
- Shodan finds devices, not just websites
- Document all findings
- This is passive recon - no target contact
- The GHDB is your best resource
- Operators can be combined for precision
- Always verify findings manually
- Some things are indexed but not accessible
- Search engines miss a lot - combine with other methods
