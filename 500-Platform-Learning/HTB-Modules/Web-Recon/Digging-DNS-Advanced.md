---
tags: [module/web-recon, dns, dig, nslookup, host, automation, level/advanced, practical]
---

# Digging DNS - Practical Application

## Complete DNS Digging Workflow

Phase 1: Basic Record Enumeration with dig
Phase 2: Advanced dig Techniques
Phase 3: Automated DNS Enumeration
Phase 4: DNS Brute Forcing
Phase 5: Output Parsing and Analysis

---

## Phase 1: Basic Record Enumeration with dig

### A Records

dig A example.com +short
dig A example.com +noall +answer

### AAAA Records (IPv6)

dig AAAA example.com +short

### MX Records

dig MX example.com +short
dig MX example.com +noall +answer

### NS Records

dig NS example.com +short
dig NS example.com +noall +answer

### TXT Records

dig TXT example.com +short
dig TXT example.com +noall +answer

### SOA Record

dig SOA example.com +noall +answer

### CNAME Records

dig CNAME www.example.com +noall +answer

### ANY Query (Often Blocked)

dig ANY example.com

---

## Phase 2: Advanced dig Techniques

### Query Specific Name Server

dig @8.8.8.8 example.com A
dig @1.1.1.1 example.com MX

### Trace Full Resolution Path

dig +trace example.com

This shows every step from root servers to authoritative answer.

### Reverse DNS Lookup

dig -x 142.251.47.142 +short
dig -x 8.8.8.8 +noall +answer

### Control Output Verbosity

# Only answer section
dig example.com +noall +answer

# Only question section
dig example.com +noall +question

# Only authority section
dig example.com +noall +authority

# Only additional section
dig example.com +noall +additional

# Statistics only
dig example.com +stats

### Set Custom Timeout

dig example.com +timeout=5

### Disable Recursion

dig example.com +norecurse

### Enable TCP Instead of UDP

dig example.com +tcp

### Batch Queries from File

dig -f domains.txt +short

---

## Phase 3: Automated DNS Enumeration

### dnsenum

dnsenum --dnsserver 8.8.8.8 --enum -p 0 -s 0 -o subdomains.txt -f /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt example.com

### dnsrecon

dnsrecon -d example.com -t brt -D /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt
dnsrecon -d example.com -t axfr
dnsrecon -d example.com -t std

### fierce

fierce --domain example.com --dns-servers 8.8.8.8

### theHarvester (OSINT + DNS)

theHarvester -d example.com -b google,bing,linkedin

---

## Phase 4: DNS Brute Forcing

### Basic Bash Loop

for sub in $(cat /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt); do
    host $sub.example.com | grep "has address" >> subdomains.txt
done

### Using Parallel for Speed

cat /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt | parallel -j 50 "host {}.example.com | grep 'has address'" >> subdomains.txt

### DNS Brute Forcing Script

#!/bin/bash
DOMAIN=$1
WORDLIST=$2
OUTPUT="subdomains-$DOMAIN.txt"

while read sub; do
    result=$(host $sub.$DOMAIN 2>/dev/null | grep "has address")
    if [ ! -z "$result" ]; then
        echo "$result" >> $OUTPUT
        echo $sub.$DOMAIN
    fi
done < $WORDLIST

### Certificate Transparency (crt.sh)

curl -s "https://crt.sh/?q=%.example.com&output=json" | jq -r '.[].name_value' | sed 's/\*\.//g' | sort -u

---

## Phase 5: Output Parsing and Analysis

### Extract IPs from dig Output

dig A example.com +short | grep -E '^[0-9]'

### Extract Mail Servers

dig MX example.com +short | awk '{print $2}'

### Extract Name Servers

dig NS example.com +short

### Extract All TXT Records

dig TXT example.com +short

### SPF Record Parser

dig TXT example.com +short | grep "v=spf1" | sed 's/"//g'

### Comprehensive DNS Scanner Script

#!/bin/bash
DOMAIN=$1
OUTPUT="dns-scan-$DOMAIN.txt"

echo "=== DNS Scan for $DOMAIN ===" > $OUTPUT
echo "" >> $OUTPUT

echo "[*] A Records:" >> $OUTPUT
dig A $DOMAIN +short >> $OUTPUT
echo "" >> $OUTPUT

echo "[*] MX Records:" >> $OUTPUT
dig MX $DOMAIN +short >> $OUTPUT
echo "" >> $OUTPUT

echo "[*] NS Records:" >> $OUTPUT
dig NS $DOMAIN +short >> $OUTPUT
echo "" >> $OUTPUT

echo "[*] TXT Records:" >> $OUTPUT
dig TXT $DOMAIN +short >> $OUTPUT
echo "" >> $OUTPUT

echo "[*] SOA Record:" >> $OUTPUT
dig SOA $DOMAIN +short >> $OUTPUT
echo "" >> $OUTPUT

echo "[*] Reverse Lookup on A Records:" >> $OUTPUT
for ip in $(dig A $DOMAIN +short); do
    echo "$ip: $(dig -x $ip +short)" >> $OUTPUT
done

cat $OUTPUT

---

## DNS Tool Comparison

| Tool | Use Case | Speed | Output Detail |
|------|----------|-------|---------------|
| dig | Manual queries | Fast | High |
| nslookup | Quick checks | Fast | Medium |
| host | Simple lookups | Fast | Low |
| dnsenum | Automated brute force | Slow | High |
| dnsrecon | Comprehensive | Medium | High |
| fierce | DNS recon | Medium | Medium |
| theHarvester | OSINT integration | Slow | High |

---

## Key Takeaways

- dig is the Swiss Army knife of DNS reconnaissance
- Use +short for quick answers, +noall +answer for clean output
- Always query multiple record types (not just A)
- Brute force subdomains with wordlists
- Certificate Transparency (crt.sh) finds subdomains passively
- Automate with scripts for large domains
- Parse output to extract IPs, mail servers, and name servers
- Combine DNS data with WHOIS and SSL data
- Be respectful with query rates
- Different tools reveal different information - use multiple
