---
tags: [module/footprinting, dns, domain, name-resolution, level/advanced, practical]
---

# DNS Enumeration - Practical Application

## Complete DNS Enumeration Workflow

Phase 1: Server Discovery
Phase 2: Basic Record Enumeration
Phase 3: Zone Transfer Attempt
Phase 4: Subdomain Brute Forcing
Phase 5: Reverse DNS Lookups
Phase 6: TXT Record Analysis
Phase 7: Internal Network Mapping

---

## Phase 1: Server Discovery

### Find DNS Servers for a Domain

dig ns inlanefreight.htb
nslookup -type=ns inlanefreight.htb
host -t ns inlanefreight.htb

### Check DNS Server Version

dig CH TXT version.bind @10.129.14.128
dig CH TXT authors.bind @10.129.14.128
dig CH TXT hostname.bind @10.129.14.128

### Identify DNS Server Software

nmap -sV -p53 10.129.14.128

---

## Phase 2: Basic Record Enumeration

### Comprehensive Record Query

dig any inlanefreight.htb @10.129.14.128

### Specific Record Types

dig a inlanefreight.htb @10.129.14.128
dig mx inlanefreight.htb @10.129.14.128
dig txt inlanefreight.htb @10.129.14.128
dig ns inlanefreight.htb @10.129.14.128
dig soa inlanefreight.htb @10.129.14.128

### Using nslookup (Interactive)

nslookup
server 10.129.14.128
set type=any
inlanefreight.htb
exit

### Using host

host -a inlanefreight.htb 10.129.14.128

---

## Phase 3: Zone Transfer (AXFR)

### Test for Zone Transfer Vulnerability

dig axfr inlanefreight.htb @10.129.14.128

### Try Different Zone Names

dig axfr internal.inlanefreight.htb @10.129.14.128
dig axfr dev.inlanefreight.htb @10.129.14.128
dig axfr stage.inlanefreight.htb @10.129.14.128

### Automated AXFR Testing

for zone in $(cat zones.txt); do
    echo "Trying zone: $zone"
    dig axfr $zone @10.129.14.128
done

### Using dnsrecon for AXFR

dnsrecon -d inlanefreight.htb -t axfr -n 10.129.14.128

---

## Phase 4: Subdomain Brute Forcing

### Basic For Loop

for sub in $(cat /usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-110000.txt); do
    host $sub.inlanefreight.htb 10.129.14.128 | grep -v "not found"
done

### Using dnsenum

dnsenum --dnsserver 10.129.14.128 --enum -p 0 -s 0 -o subdomains.txt -f /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt inlanefreight.htb

### Using fierce

fierce --domain inlanefreight.htb --dns-servers 10.129.14.128 --subdomains /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt

### Using dnsrecon

dnsrecon -d inlanefreight.htb -t brt -D /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt -n 10.129.14.128

### Using gobuster

gobuster dns -d inlanefreight.htb -t 50 -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt --server 10.129.14.128

---

## Phase 5: Reverse DNS Lookups

### Single IP Reverse Lookup

dig -x 10.129.34.136 @10.129.14.128
nslookup 10.129.34.136 10.129.14.128
host 10.129.34.136 10.129.14.128

### Reverse Lookup on IP Range

for i in $(seq 1 255); do
    host 10.129.14.$i 10.129.14.128 | grep -v "not found"
done

### Using dnsrecon for Reverse Lookups

dnsrecon -r 10.129.14.0/24 -n 10.129.14.128

---

## Phase 6: TXT Record Analysis

### Extract SPF Records

dig txt inlanefreight.htb @10.129.14.128 | grep "v=spf1"

### Parse SPF for IPs and Includes

dig txt inlanefreight.htb @10.129.14.128 | grep "v=spf1" | grep -oE 'ip4:[0-9.]+' | cut -d: -f2
dig txt inlanefreight.htb @10.129.14.128 | grep "v=spf1" | grep -oE 'include:[a-zA-Z0-9._-]+' | cut -d: -f2

### Identify Third-Party Services

dig txt inlanefreight.htb @10.129.14.128 | grep -E "MS=|atlassian|google|logmein|mailgun|outlook|amazon"

### What TXT Records Reveal

| Service | Indicator | Implication |
|---------|-----------|-------------|
| Microsoft | MS= | Office 365, Azure |
| Atlassian | atlassian-domain-verification | Jira, Confluence |
| Google | google-site-verification | GSuite, GCP |
| LogMeIn | logmein-verification-code | Remote access platform |
| Mailgun | include:mailgun.org | Email API |
| Outlook | include:spf.protection.outlook.com | Microsoft 365 |
| Amazon | awsdns-hostmaster | AWS Route53 |

---

## Phase 7: Internal Network Mapping

### From Zone Transfer

If you get a successful AXFR, extract all internal IPs:

dig axfr internal.inlanefreight.htb @10.129.14.128 | grep A | awk '{print $5}' | sort -u

### Map Network Segments

From internal IPs, identify subnets:
10.129.34.0/24 - Servers
10.129.18.0/24 - Mail servers
10.129.1.0/24 - Workstations
10.129.42.0/24 - Unknown (from SPF)

### Create Network Diagram

Based on discovered hosts:
- DCs: dc1.internal (10.129.34.16), dc2.internal (10.129.34.11)
- Mail: mail1.internal (10.129.18.200)
- VPN: vpn.internal (10.129.1.6)
- Workstations: ws1 (10.129.1.34), ws2 (10.129.1.35)
- WSUS: wsus.internal (10.129.18.2)

---

## Complete Enumeration Script

Save as dns-enum.sh:

#!/bin/bash
DOMAIN=$1
SERVER=$2
OUTPUT_DIR="dns-enum-$DOMAIN"
mkdir -p $OUTPUT_DIR

echo "[*] Starting DNS enumeration for $DOMAIN using server $SERVER"

echo "[*] Getting NS records..."
dig ns $DOMAIN @$SERVER > $OUTPUT_DIR/ns-records.txt

echo "[*] Getting ANY records..."
dig any $DOMAIN @$SERVER > $OUTPUT_DIR/any-records.txt

echo "[*] Getting MX records..."
dig mx $DOMAIN @$SERVER > $OUTPUT_DIR/mx-records.txt

echo "[*] Getting TXT records..."
dig txt $DOMAIN @$SERVER > $OUTPUT_DIR/txt-records.txt

echo "[*] Attempting zone transfer (AXFR)..."
dig axfr $DOMAIN @$SERVER > $OUTPUT_DIR/axfr.txt
dig axfr internal.$DOMAIN @$SERVER >> $OUTPUT_DIR/axfr.txt 2>/dev/null
dig axfr dev.$DOMAIN @$SERVER >> $OUTPUT_DIR/axfr.txt 2>/dev/null

echo "[*] Brute forcing subdomains..."
for sub in $(cat /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt 2>/dev/null); do
    host $sub.$DOMAIN $SERVER 2>/dev/null | grep "has address" >> $OUTPUT_DIR/subdomains.txt
done

echo "[*] DNS enumeration complete. Check $OUTPUT_DIR/"

---

## Tool Comparison

| Tool | Best For | Speed | Reliability |
|------|----------|-------|-------------|
| dig | Detailed queries | Fast | High |
| nslookup | Basic queries | Fast | High |
| host | Quick lookups | Fast | Medium |
| dnsrecon | Comprehensive scans | Medium | High |
| dnsenum | Brute forcing | Slow | Medium |
| fierce | Subdomain discovery | Medium | Medium |
| gobuster | Fast brute forcing | Fast | High |

---

## Key Takeaways

- DNS is the phonebook of the Internet
- Zone transfer (AXFR) is the holy grail - entire zone in one request
- TXT records leak third-party services
- SPF records often contain internal IPs
- Brute forcing finds hidden subdomains
- Reverse lookups map IPs to hostnames
- DNS server version may reveal vulnerabilities
- Internal IPs in DNS = network map
- Always check for zone transfer on all discovered domains
- Combine multiple tools for best results
- Document everything - you're building a network map
