---
tags: [module/web-recon, whois, passive-recon, osint, automation, level/advanced, practical]
---

# WHOIS - Practical Application

## Complete WHOIS Enumeration Workflow

Phase 1: Basic Domain WHOIS
Phase 2: IP WHOIS
Phase 3: Historical WHOIS Analysis
Phase 4: Cross-Referencing
Phase 5: Automation

---

## Phase 1: Basic Domain WHOIS

### Standard Lookup

whois inlanefreight.com

### Specify WHOIS Server

whois -h whois.verisign-grs.com inlanefreight.com

### Parse Specific Fields

# Get registrar
whois inlanefreight.com | grep -i "Registrar:" | head -1

# Get creation date
whois inlanefreight.com | grep -i "Creation Date:" | head -1

# Get name servers
whois inlanefreight.com | grep -i "Name Server:" | awk '{print $3}' | sort -u

# Get registrant email
whois inlanefreight.com | grep -i "Registrant Email:" | awk '{print $3}'

# Get all contacts
whois inlanefreight.com | grep -E "Registrant|Administrative|Technical" | grep -E "Name|Email|Phone"

---

## Phase 2: IP WHOIS

### WHOIS for IP Address

whois 8.8.8.8

### What IP WHOIS Reveals

inetnum:        8.8.8.0 - 8.8.8.255
netname:        LVLT-GOGL-8-8-8
descr:          Google LLC
country:        US
org:            ORG-GL161-ARIN
admin-c:        ZG39-ARIN
tech-c:         ZG39-ARIN
abuse-c:        ABUSE5250-ARIN
mnt-by:         MAINT-ARIN-GOOGLE-8-8-8
status:         ASSIGNED
source:         ARIN

This reveals:
- Organization (Google LLC)
- Country (US)
- Netblock range
- Abuse contact
- Ownership info

### Autonomous System WHOIS

whois AS15169

Reveals:
- AS Name: Google LLC
- Country: US
- Peering info
- Routing policy

---

## Phase 3: Historical WHOIS Analysis

### Why Historical WHOIS Matters

- Domains often change hands
- Privacy protection hides current owners
- Old records may show REAL names/emails
- Track infrastructure changes over time

### WhoisFreaks API Example

curl -X GET "https://api.whoisfreaks.com/v1.0/whois?apiKey=YOUR_KEY&domainName=inlanefreight.com&mode=history"

### Parse Historical Changes

Look for:
- Changes in registrant name/email
- Different name servers over time
- Expiration patterns
- Multiple domains with same historical contact

### Historical Email Extraction

Extract all emails from historical records:
jq '.whois_records[].registrant_email' whois-history.json | sort -u

---

## Phase 4: Cross-Referencing

### Find Other Domains Owned by Same Registrant

# If you have an email, search for it
whois -h whois.arin.net "! Email@domain.com"

# Use reverse WHOIS services
# https://viewdns.info/reversewhois
# https://www.domaintools.com/reverse-whois-search

### Identify Registrant Patterns

Look for:
- Same name across multiple domains
- Same email pattern (first.last@company)
- Same phone number format
- Same address/city/country

### Map Infrastructure

# Get IPs from domain
dig +short inlanefreight.com

# WHOIS those IPs
for ip in $(dig +short inlanefreight.com | grep -E '^[0-9]'); do
    echo "=== $ip ==="
    whois $ip | grep -E "OrgName|NetName|Country|AbuseEmail"
done

---

## Phase 5: Automation

### Bulk WHOIS Lookup Script

Save as whois-bulk.sh:

#!/bin/bash
INPUT_FILE=$1
OUTPUT_DIR="whois-results"
mkdir -p $OUTPUT_DIR

while read domain; do
    echo "[*] Processing $domain"
    
    # Basic WHOIS
    whois $domain > "$OUTPUT_DIR/$domain.txt"
    
    # Extract key info
    grep -E "Registrar:|Creation Date:|Expiry Date:|Name Server:|Registrant Email:|Admin Email:" "$OUTPUT_DIR/$domain.txt" > "$OUTPUT_DIR/$domain-summary.txt"
    
    # Extract emails
    grep -E -o "\b[a-zA-Z0-9.-]+@[a-zA-Z0-9.-]+\.[a-zA-Z0-9.-]+\b" "$OUTPUT_DIR/$domain.txt" | sort -u > "$OUTPUT_DIR/$domain-emails.txt"
    
    # Sleep to be polite
    sleep 2
done < $INPUT_FILE

echo "[*] Done. Results in $OUTPUT_DIR/"

### WHOIS Parser Script

Save as whois-parse.sh:

#!/bin/bash
WHOIS_FILE=$1

echo "=== Domain Information ==="
grep "Domain Name:" $WHOIS_FILE | head -1

echo -e "\n=== Registrar ==="
grep "Registrar:" $WHOIS_FILE | head -1

echo -e "\n=== Dates ==="
grep "Creation Date:" $WHOIS_FILE | head -1
grep "Registry Expiry Date:" $WHOIS_FILE | head -1

echo -e "\n=== Name Servers ==="
grep "Name Server:" $WHOIS_FILE | awk '{print $3}' | sort -u

echo -e "\n=== Contacts ==="
grep -E "Registrant|Administrative|Technical" $WHOIS_FILE | grep -E "Name:|Organization:|Email:|Phone:" | sort -u

echo -e "\n=== Abuse Contact ==="
grep -i "abuse" $WHOIS_FILE | grep -E "Email:|Phone:"

### Complete Recon Script

Save as whois-recon.sh:

#!/bin/bash
DOMAIN=$1
OUTPUT_DIR="whois-recon-$DOMAIN"
mkdir -p $OUTPUT_DIR

echo "[*] Starting WHOIS recon for $DOMAIN"

echo "[*] Domain WHOIS..."
whois $DOMAIN > $OUTPUT_DIR/domain-whois.txt

echo "[*] Extracting IPs..."
IPS=$(dig +short $DOMAIN | grep -E '^[0-9]')

for ip in $IPS; do
    echo "[*] IP WHOIS for $ip..."
    whois $ip > "$OUTPUT_DIR/ip-$ip.txt"
    
    # Extract netname and organization
    grep -E "OrgName:|NetName:|Country:|Organization:" "$OUTPUT_DIR/ip-$ip.txt" | head -5
done

echo "[*] Extracting emails..."
grep -E -o "\b[a-zA-Z0-9.-]+@[a-zA-Z0-9.-]+\.[a-zA-Z0-9.-]+\b" "$OUTPUT_DIR/domain-whois.txt" | sort -u > "$OUTPUT_DIR/emails.txt"

echo "[*] Extracting name servers..."
grep "Name Server:" "$OUTPUT_DIR/domain-whois.txt" | awk '{print $3}' | sort -u > "$OUTPUT_DIR/nameservers.txt"

echo "[*] WHOIS recon complete. Check $OUTPUT_DIR/"

---

## Online WHOIS Tools

| Tool | URL | Features |
|------|-----|----------|
| DomainTools | https://domaintools.com | Historical, reverse WHOIS |
| WhoisFreaks | https://whoisfreaks.com | API, historical |
| SecurityTrails | https://securitytrails.com | DNS + WHOIS history |
| ViewDNS | https://viewdns.info | Reverse WHOIS |
| Whoisology | https://whoisology.com | Historical database |
| ICANN Lookup | https://lookup.icann.org | Official registrar data |

---

## Key WHOIS Servers

| Server | For |
|--------|-----|
| whois.verisign-grs.com | .com domains |
| whois.networksolutions.com | Network Solutions |
| whois.register.com | Register.com |
| whois.godaddy.com | GoDaddy |
| whois.arin.net | ARIN (North America IPs) |
| whois.ripe.net | RIPE (Europe IPs) |
| whois.apnic.net | APNIC (Asia Pacific IPs) |
| whois.lacnic.net | LACNIC (Latin America) |
| whois.afrinic.net | AFRINIC (Africa) |

---

## Tool Comparison

| Tool | Type | Best For |
|------|------|----------|
| whois command | CLI | Quick lookups |
| DomainTools | Web/API | Historical, reverse |
| WhoisFreaks | API | Automated bulk queries |
| ViewDNS | Web | Reverse WHOIS |
| Custom scripts | Automation | Bulk processing |

---

## Key Takeaways

- WHOIS is passive recon - no detection risk
- Always check domain AND IP WHOIS
- Historical WHOIS reveals what privacy hides
- Extract emails for social engineering
- Extract name servers for DNS recon
- Look for patterns across multiple domains
- Same contact info = owned by same person/org
- Abuse contact can be useful for reporting
- Automate bulk lookups but be polite (rate limiting)
- Combine WHOIS with DNS and certificate data
- Document everything - build a profile
