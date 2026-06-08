---
tags: [module/web-recon, dns, domain, passive-recon, active-recon, automation, level/advanced, practical]
---

# DNS - Practical Application

## Complete DNS Enumeration Workflow

Phase 1: Basic Record Enumeration
Phase 2: Zone Transfer (AXFR) Attempts
Phase 3: Subdomain Discovery
Phase 4: Reverse DNS Lookups
Phase 5: DNS History Analysis
Phase 6: Automation

---

## Phase 1: Basic Record Enumeration

### A Records (IPv4)

dig A example.com
host -t A example.com
nslookup -type=A example.com

### AAAA Records (IPv6)

dig AAAA example.com
host -t AAAA example.com

### MX Records (Mail Servers)

dig MX example.com
host -t MX example.com
nslookup -type=MX example.com

### NS Records (Name Servers)

dig NS example.com
host -t NS example.com
nslookup -type=NS example.com

### TXT Records

dig TXT example.com
host -t TXT example.com
nslookup -type=TXT example.com

### CNAME Records (Aliases)

dig CNAME www.example.com
host -t CNAME www.example.com

### SOA Record (Start of Authority)

dig SOA example.com
host -t SOA example.com

### ANY Record (All Records)

dig ANY example.com

---

## Phase 2: Zone Transfer (AXFR)

### What is AXFR?

Zone transfer is how DNS servers synchronize data. If misconfigured, ANYONE can request a full zone transfer, revealing ALL DNS records for a domain.

### Basic AXFR Request

dig AXFR example.com @ns1.example.com
host -l example.com ns1.example.com
nslookup -type=AXFR example.com ns1.example.com

### AXFR with Different Name Servers

for ns in $(dig NS example.com | grep "NS" | awk '{print $5}'); do
    echo "[*] Testing $ns"
    dig AXFR example.com @$ns
done

### AXFR Automation Script

#!/bin/bash
DOMAIN=$1
NAMESERVERS=$(dig NS $DOMAIN | grep "NS" | awk '{print $5}')

for ns in $NAMESERVERS; do
    echo "[*] Attempting zone transfer on $ns"
    dig AXFR $DOMAIN @$ns > "axfr-$ns.txt"
    if grep -q "Transfer failed" "axfr-$ns.txt"; then
        echo "[-] Zone transfer failed on $ns"
    else
        echo "[+] Zone transfer succeeded on $ns"
        cat "axfr-$ns.txt"
    fi
done

### What a Successful AXFR Reveals

example.com. 3600 IN SOA ns1.example.com. admin.example.com. 2024031201 3600 900 604800 86400
example.com. 3600 IN NS ns1.example.com.
example.com. 3600 IN NS ns2.example.com.
example.com. 3600 IN MX 10 mail.example.com.
www.example.com. 3600 IN A 192.168.1.10
mail.example.com. 3600 IN A 192.168.1.20
vpn.example.com. 3600 IN A 10.0.0.5
dev.example.com. 3600 IN A 172.16.1.100
internal.example.com. 3600 IN A 192.168.100.50

This reveals internal IP addresses, development servers, and infrastructure.

---

## Phase 3: Subdomain Discovery

### Brute Force Subdomains

for sub in $(cat subdomains.txt); do
    host $sub.example.com | grep "has address" | cut -d' ' -f1,4
done

### Using Gobuster

gobuster dns -d example.com -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt -t 50

### Using dnsenum

dnsenum --dnsserver 8.8.8.8 --enum -p 0 -s 0 -o subdomains.txt -f /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt example.com

### Using dnsrecon

dnsrecon -d example.com -t brt -D /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt

### Using fierce

fierce --domain example.com --dns-servers 8.8.8.8

### Certificate Transparency (crt.sh)

curl -s "https://crt.sh/?q=%.example.com&output=json" | jq -r '.[].name_value' | sed 's/\*\.//g' | sort -u

### Virtual Host Discovery

gobuster vhost -u https://example.com -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt -t 50

---

## Phase 4: Reverse DNS Lookups

### Single IP Reverse Lookup

dig -x 192.0.2.1
host 192.0.2.1
nslookup 192.0.2.1

### Reverse Lookup on IP Range

for i in $(seq 1 254); do
    host 192.168.1.$i | grep -v "not found"
done

### Using dnsrecon for Reverse Lookups

dnsrecon -r 192.168.1.0/24 -n 8.8.8.8

---

## Phase 5: DNS History Analysis

### SecurityTrails

curl -s "https://api.securitytrails.com/v1/domain/example.com" -H "APIKEY: YOUR_KEY" | jq '.current_dns'

### DNS History Services

| Service | URL | Features |
|---------|-----|----------|
| SecurityTrails | https://securitytrails.com | Historical DNS, WHOIS |
| DNS History | https://dnshistory.org | Historical records |
| ViewDNS | https://viewdns.info | Multiple DNS tools |
| PassiveTotal | https://passivetotal.org | Threat intel + DNS history |

---

## Phase 6: Automation

### Complete DNS Enumeration Script

Save as dns-enum.sh:

#!/bin/bash
DOMAIN=$1
OUTPUT_DIR="dns-enum-$DOMAIN"
mkdir -p $OUTPUT_DIR

echo "[*] Starting DNS enumeration for $DOMAIN"

echo "[*] Getting NS records..."
dig NS $DOMAIN > $OUTPUT_DIR/ns-records.txt

echo "[*] Getting MX records..."
dig MX $DOMAIN > $OUTPUT_DIR/mx-records.txt

echo "[*] Getting TXT records..."
dig TXT $DOMAIN > $OUTPUT_DIR/txt-records.txt

echo "[*] Attempting zone transfers..."
NAMESERVERS=$(dig NS $DOMAIN | grep "NS" | awk '{print $5}')
for ns in $NAMESERVERS; do
    dig AXFR $DOMAIN @$ns > "$OUTPUT_DIR/axfr-$ns.txt" 2>/dev/null
done

echo "[*] Brute forcing subdomains..."
for sub in $(cat /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt 2>/dev/null); do
    host $sub.$DOMAIN 2>/dev/null | grep "has address" >> "$OUTPUT_DIR/subdomains.txt"
done

echo "[*] DNS enumeration complete. Check $OUTPUT_DIR/"

### TXT Record Parser

#!/bin/bash
DOMAIN=$1
TXT=$(dig TXT $DOMAIN +short)

echo "SPF Records:"
echo "$TXT" | grep "v=spf1"

echo "Microsoft Verification:"
echo "$TXT" | grep "MS="

echo "Google Verification:"
echo "$TXT" | grep "google-site-verification"

echo "Atlassian Verification:"
echo "$TXT" | grep "atlassian-domain-verification"

echo "LogMeIn Verification:"
echo "$TXT" | grep "logmein-verification-code"

### Mail Server Mapper

#!/bin/bash
DOMAIN=$1
MX=$(dig MX $DOMAIN +short | sort -n | awk '{print $2}')

echo "Mail servers for $DOMAIN:"
for server in $MX; do
    echo $server
    echo "  A record: $(dig A $server +short | head -1)"
    echo "  AAAA record: $(dig AAAA $server +short | head -1)"
    echo "  TXT: $(dig TXT $server +short | head -1)"
    echo ""
done

---

## DNS Record Analysis Cheatsheet

### What to Look For

| Record Type | What to Check |
|-------------|---------------|
| A | Unusual IPs, internal IPs (10.x, 172.16.x, 192.168.x) |
| MX | Email provider (Google, Microsoft, custom) |
| NS | Hosting provider, nameserver patterns |
| TXT | SPF records (reveal IPs), domain verification, third-party services |
| CNAME | Aliases to other domains (may point to outdated servers) |
| SOA | Admin email (often reveals domain owner) |

### Red Flags

- Internal IP addresses in public DNS
- Wildcard entries (anything.example.com resolves)
- Zone transfer enabled
- Outdated records pointing to dead servers
- SPF records with "all" (misconfigured)
- Missing security records (DMARC, DKIM)

---

## Key Takeaways

- DNS reveals infrastructure, providers, and services
- Zone transfer (AXFR) is the holy grail - try it on every nameserver
- Subdomain brute forcing finds hidden assets
- TXT records leak third-party service usage
- SPF records often contain internal IPs
- Reverse lookups map IPs to hostnames
- Historical DNS shows infrastructure changes
- Certificate transparency (crt.sh) finds subdomains
- Automate enumeration but be polite (rate limiting)
- Combine DNS with WHOIS and SSL data for full picture
