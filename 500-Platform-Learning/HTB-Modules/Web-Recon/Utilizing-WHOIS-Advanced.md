---
tags: [module/web-recon, whois, passive-recon, osint, threat-intel, automation, level/advanced, practical]
---

# Utilizing WHOIS - Practical Application

## Complete WHOIS Analysis Workflow

Phase 1: Initial Domain Investigation
Phase 2: Pattern Recognition
Phase 3: Infrastructure Mapping
Phase 4: Threat Intelligence Correlation
Phase 5: Automation for Bulk Analysis

---

## Phase 1: Initial Domain Investigation

### Basic WHOIS Lookup

whois suspicious-site.com

### Key Red Flags to Check

| Factor | What to Look For |
|--------|------------------|
| Creation Date | Less than 30 days old |
| Registrar | Known lax registrar (e.g., NameCheap, GoDaddy, etc.) |
| Registrant Info | Privacy protection, fake names, anonymous email |
| Name Servers | Known bulletproof hosting providers |
| Country | High-risk jurisdictions |
| Domain Status | Missing protection flags |

### Phishing Domain Checklist

- [ ] Domain registered in last 30 days?
- [ ] Registrant info hidden?
- [ ] Name servers suspicious?
- [ ] Registrar known for abuse?
- [ ] Domain matches brand name with typos?

---

## Phase 2: Pattern Recognition

### Cluster Analysis

When investigating threat actor groups, look for patterns across multiple domains:

for domain in $(cat threat-domains.txt); do
    echo "=== $domain ==="
    whois $domain | grep -E "Creation Date:|Registrar:|Name Server:|Registrant Organization:"
    echo ""
done

### Common Patterns

| Pattern | What It Means |
|---------|---------------|
| Same registrar | Actor prefers certain registrars |
| Same name servers | Shared infrastructure |
| Same creation date cluster | Domains bought together for campaign |
| Same registrant name/email | Same actor (even with fake names) |
| Similar naming convention | Automated domain generation |

### Identify Shared Infrastructure

for domain in $(cat domains.txt); do
    whois $domain | grep "Name Server:" | awk '{print $3}' >> all-nameservers.txt
done
sort -u all-nameservers.txt

---

## Phase 3: Infrastructure Mapping

### Map Domain to IP to Hosting Provider

IP=$(dig +short suspicious-site.com | head -1)
whois $IP | grep -E "OrgName|NetName|Country|AbuseEmail"

### Identify Hosting Provider

whois $IP | grep -E "OrgName|NetName|descr"

### Find Other Domains on Same IP

Use reverse IP services:
- https://viewdns.info/reverse-ip/
- https://www.yougetsignal.com/tools/web-sites-on-web-server/
- https://rapiddns.io/sameip/

### Find Other Domains with Same Name Servers

NS=$(whois suspicious-site.com | grep "Name Server:" | awk '{print $3}' | head -1)

---

## Phase 4: Threat Intelligence Correlation

### Build IOCs from WHOIS

Indicators of Compromise (IOCs) to extract:
- Domain names
- Name servers
- Registrant emails
- Registrant names
- Creation dates
- Registrar names

### Cross-Reference with Threat Intel Feeds

Check if domain appears in:
- VirusTotal
- AlienVault OTX
- AbuseIPDB
- ThreatFox
- URLhaus

### Automated IOC Generation Script

#!/bin/bash
DOMAIN=$1

echo "=== IOC Report for $DOMAIN ==="
echo "Domain: $DOMAIN"
echo "Creation Date: $(whois $DOMAIN | grep "Creation Date:" | head -1)"
echo "Registrar: $(whois $DOMAIN | grep "Registrar:" | head -1)"
echo "Name Servers:"
whois $DOMAIN | grep "Name Server:" | awk '{print $3}'
echo ""
echo "Check these threat intel feeds:"
echo "https://www.virustotal.com/gui/domain/$DOMAIN"
echo "https://otx.alienvault.com/indicator/domain/$DOMAIN"
echo "https://www.abuseipdb.com/check/$DOMAIN"

---

## Phase 5: Automation for Bulk Analysis

### Bulk Domain Checker

Save as bulk-domain-check.sh:

#!/bin/bash
INPUT_FILE=$1
OUTPUT_DIR="domain-analysis"
mkdir -p $OUTPUT_DIR

echo "Domain,Creation Date,Registrar,Name Servers" > $OUTPUT_DIR/summary.csv

while read domain; do
    echo "[*] Processing $domain"
    OUTPUT="$OUTPUT_DIR/$domain.txt"
    
    whois $domain > $OUTPUT
    
    CREATION=$(grep "Creation Date:" $OUTPUT | head -1 | cut -d' ' -f3-)
    REGISTRAR=$(grep "Registrar:" $OUTPUT | head -1 | cut -d' ' -f2-)
    NS=$(grep "Name Server:" $OUTPUT | awk '{print $3}' | head -3 | tr '\n' '|')
    
    echo "$domain,$CREATION,$REGISTRAR,$NS" >> $OUTPUT_DIR/summary.csv
    
    if [[ $CREATION > $(date -d '30 days ago' '+%Y-%m-%d') ]]; then
        echo "[!] $domain is less than 30 days old" >> $OUTPUT_DIR/red-flags.txt
    fi
    
    sleep 2
done < $INPUT_FILE

echo "[*] Analysis complete. Check $OUTPUT_DIR/"

### Registrar Reputation Database

cat > lax-registrars.txt << 'INNER'
NameCheap, Inc.
GoDaddy.com, LLC
Internet Domain Service BS Corp
PDR Ltd.
TUCOWS, Inc.
INNER

### Check Domain Against Registrar Blacklist

REGISTRAR=$(whois suspicious.com | grep "Registrar:" | head -1 | cut -d' ' -f2-)
if grep -q "$REGISTRAR" lax-registrars.txt; then
    echo "[!] Suspicious registrar: $REGISTRAR"
fi

### Automated Phishing Domain Detector

Save as phishing-detect.sh:

#!/bin/bash
DOMAIN=$1

BRANDS="facebook google amazon microsoft apple"
for brand in $BRANDS; do
    if [[ $DOMAIN == *"$brand"* ]] && [[ $DOMAIN != *"$brand.com"* ]]; then
        echo "[!] Possible typosquatting of $brand"
    fi
done

CREATION=$(whois $DOMAIN | grep "Creation Date:" | head -1 | cut -d' ' -f3-)
CREATION_EPOCH=$(date -d "$CREATION" +%s)
DAYS_OLD=$(( ($(date +%s) - $CREATION_EPOCH) / 86400 ))

if [[ $DAYS_OLD -lt 30 ]]; then
    echo "[!] Domain is only $DAYS_OLD days old (suspicious)"
fi

if whois $DOMAIN | grep -q "Registrant Name: REDACTED\|Registrant Name: On behalf of\|Registrant Name: Domain Admin"; then
    echo "[!] Registrant info is hidden/redacted"
fi

---

## Threat Actor Profile Template

When investigating a threat actor, create a profile:

Threat Actor: [Name/Group]
========================================

Domains Used:
- domain1.com (registered YYYY-MM-DD, registrar X)
- domain2.net (registered YYYY-MM-DD, registrar Y)

Patterns:
- All domains use same name servers: ns1.malicious.com
- Registered in clusters: 2024-01, 2024-06
- All use privacy protection

Infrastructure:
- Hosted on IP range: 185.xxx.xxx.0/24
- Hosting provider: Bulletproof Hosting Inc.

IOCs:
- Domains: [list]
- Name servers: [list]
- IPs: [list]
- Registrant emails: [list]

TTPs:
- Target: Financial institutions
- Method: Spear phishing with fake login pages
- Tools: [list]

---

## Key Takeaways

- WHOIS data reveals patterns across threat actor infrastructure
- Recent registration + hidden details = major red flag
- Same name servers across domains = shared infrastructure
- Registrars have different abuse reporting processes
- Automate bulk analysis for large investigations
- Cross-reference WHOIS with threat intel feeds
- Build IOCs from WHOIS for detection rules
- Track clusters of registrations to identify campaigns
- Always check domain age - new = suspicious
- Combine WHOIS with DNS, SSL, and hosting data for full picture
