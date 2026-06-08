---
tags: [module/web-recon, subdomains, dns, passive-recon, active-recon, automation, level/advanced, practical]
---

# Subdomains - Practical Application

## Complete Subdomain Enumeration Workflow

Phase 1: Passive Subdomain Discovery
Phase 2: Active Subdomain Brute Forcing
Phase 3: Certificate Transparency Logs
Phase 4: DNS Zone Transfer Attempts
Phase 5: Subdomain Validation
Phase 6: Automation

---

## Phase 1: Passive Subdomain Discovery

### Certificate Transparency (crt.sh)

curl -s "https://crt.sh/?q=%.example.com&output=json" | jq -r '.[].name_value' | sed 's/\*\.//g' | sort -u

### SecurityTrails API

curl -s "https://api.securitytrails.com/v1/domain/example.com/subdomains" -H "APIKEY: YOUR_KEY" | jq -r '.subdomains[]' | awk '{print $1".example.com"}'

### AlienVault OTX

curl -s "https://otx.alienvault.com/api/v1/indicators/domain/example.com/passive_dns" | jq -r '.passive_dns[].hostname' | sort -u

### RapidDNS.io

curl -s "https://rapiddns.io/subdomain/example.com?full=1" | grep -oP '([a-zA-Z0-9._-]+\.example\.com)' | sort -u

### Wayback Machine

curl -s "http://web.archive.org/cdx/search/cdx?url=*.example.com&output=json&fl=original&collapse=urlkey" | jq -r '.[] | select(length > 0) | .[0]' | sed -E 's|https?://||' | cut -d'/' -f1 | sort -u

### Google Dorks

site:example.com -www

---

## Phase 2: Active Subdomain Brute Forcing

### Using gobuster

gobuster dns -d example.com -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt -t 50

### Using ffuf

ffuf -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt -H "Host: FUZZ.example.com" -u https://example.com -fc 404

### Using dnsenum

dnsenum --dnsserver 8.8.8.8 --enum -p 0 -s 0 -o subdomains.txt -f /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt example.com

### Using dnsrecon

dnsrecon -d example.com -t brt -D /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt

### Using fierce

fierce --domain example.com --dns-servers 8.8.8.8

### Basic Bash Loop

for sub in $(cat /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt); do
    host $sub.example.com | grep "has address" >> subdomains.txt
done

---

## Phase 3: Certificate Transparency Logs

### crt.sh Full Scan

curl -s "https://crt.sh/?q=%.example.com&output=json" | jq -r '.[].name_value' | sed 's/\*\.//g' | sort -u > crt-subdomains.txt

### Facebook CT Search

curl -s "https://developers.facebook.com/tools/ct/search/?q=example.com" | grep -oP '([a-zA-Z0-9._-]+\.example\.com)' | sort -u

---

## Phase 4: DNS Zone Transfer Attempts

### Find Name Servers

dig NS example.com +short

### Attempt Zone Transfer on Each Name Server

for ns in $(dig NS example.com +short); do
    echo "[*] Trying zone transfer on $ns"
    dig AXFR example.com @$ns
done

---

## Phase 5: Subdomain Validation

### Resolve Subdomains to IPs

for sub in $(cat subdomains.txt); do
    ip=$(dig A $sub +short | head -1)
    if [ ! -z "$ip" ]; then
        echo "$sub -> $ip"
    fi
done

### Check for Live Web Servers

for sub in $(cat subdomains.txt); do
    if curl -s -I -L $sub -o /dev/null -w "%{http_code}" | grep -q "200\|301\|302"; then
        echo "[+] Live web server: $sub"
    fi
done

### Check for Open Ports (Quick Scan)

for sub in $(cat subdomains.txt); do
    nc -zv -w 1 $sub 80 2>/dev/null && echo "[+] Port 80 open: $sub"
    nc -zv -w 1 $sub 443 2>/dev/null && echo "[+] Port 443 open: $sub"
    nc -zv -w 1 $sub 8080 2>/dev/null && echo "[+] Port 8080 open: $sub"
done

---

## Phase 6: Automation

### Complete Subdomain Enumeration Script

Save as `subdomain-enum.sh`:

#!/bin/bash
DOMAIN=$1
OUTPUT_DIR="subdomain-enum-$DOMAIN"
mkdir -p $OUTPUT_DIR

echo "[*] Starting subdomain enumeration for $DOMAIN"

echo "[*] Certificate Transparency (crt.sh)..."
curl -s "https://crt.sh/?q=%.$DOMAIN&output=json" | jq -r '.[].name_value' | sed 's/\*\.//g' | sort -u > $OUTPUT_DIR/crt.txt

echo "[*] SecurityTrails..."
curl -s "https://api.securitytrails.com/v1/domain/$DOMAIN/subdomains" -H "APIKEY: YOUR_KEY" 2>/dev/null | jq -r '.subdomains[]' | awk '{print $1".'$DOMAIN'"}' >> $OUTPUT_DIR/passive.txt 2>/dev/null

echo "[*] Wayback Machine..."
curl -s "http://web.archive.org/cdx/search/cdx?url=*.$DOMAIN&output=json&fl=original&collapse=urlkey" | jq -r '.[] | select(length > 0) | .[0]' | sed -E 's|https?://||' | cut -d'/' -f1 | sort -u >> $OUTPUT_DIR/passive.txt

echo "[*] Combining passive results..."
cat $OUTPUT_DIR/crt.txt $OUTPUT_DIR/passive.txt 2>/dev/null | sort -u > $OUTPUT_DIR/all-passive.txt

echo "[*] Brute forcing subdomains (this may take a while)..."
for sub in $(cat /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt 2>/dev/null | head -1000); do
    host $sub.$DOMAIN 2>/dev/null | grep "has address" >> $OUTPUT_DIR/brute.txt
done

echo "[*] Resolving unique subdomains..."
cat $OUTPUT_DIR/all-passive.txt $OUTPUT_DIR/brute.txt 2>/dev/null | grep -oP '([a-zA-Z0-9._-]+\.'$DOMAIN')' | sort -u > $OUTPUT_DIR/all-subdomains.txt

echo "[*] Checking live web servers..."
while read sub; do
    if curl -s -I -L http://$sub -o /dev/null -w "%{http_code}" | grep -q "200\|301\|302\|401\|403"; then
        echo "$sub" >> $OUTPUT_DIR/live-web.txt
    elif curl -s -I -L https://$sub -o /dev/null -w "%{http_code}" | grep -q "200\|301\|302\|401\|403"; then
        echo "$sub" >> $OUTPUT_DIR/live-web.txt
    fi
done < $OUTPUT_DIR/all-subdomains.txt

echo "[*] Subdomain enumeration complete."
echo "[+] Total subdomains found: $(wc -l < $OUTPUT_DIR/all-subdomains.txt)"
echo "[+] Live web servers: $(wc -l < $OUTPUT_DIR/live-web.txt)"
echo "[*] Results saved in $OUTPUT_DIR/"

---

## Subdomain Wordlists

| Wordlist | Location | Size |
|----------|----------|------|
| SecLists | /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt | 114k |
| dnscan | /usr/share/wordlists/dnscan.txt | 1.4M |
| commonspeak | https://github.com/assetnote/commonspeak2 | 2M+ |

---

## Tool Comparison

| Tool | Type | Speed | Best For |
|------|------|-------|----------|
| crt.sh | Passive | Fast | Quick wins |
| gobuster | Active | Fast | Brute forcing |
| dnsenum | Active | Medium | Comprehensive |
| dnsrecon | Both | Medium | All-in-one |
| fierce | Active | Slow | DNS recon |
| ffuf | Active | Fast | Web fuzzing |
| SecurityTrails | Passive | Fast | Historical data |

---

## Key Takeaways

- Always start with passive enumeration (crt.sh, SecurityTrails)
- Use multiple wordlists for brute forcing
- Combine results from multiple sources
- Validate subdomains by resolving to IPs
- Check for live web servers
- Certificate Transparency logs are the best free source
- Zone transfers rarely work but always try them
- Subdomains often lead to hidden attack surfaces
- Document all findings
- Automate the process for large domains
