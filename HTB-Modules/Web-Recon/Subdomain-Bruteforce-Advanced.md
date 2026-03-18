---
tags: [module/web-recon, subdomains, dns, bruteforce, active-recon, automation, level/advanced, practical]
---

# Subdomain Bruteforcing - Practical Application

## Complete Subdomain Bruteforcing Workflow

Phase 1: Tool Selection
Phase 2: Wordlist Preparation
Phase 3: Execution
Phase 4: Resolution and Filtering
Phase 5: Validation
Phase 6: Automation

---

## Phase 1: Tool Selection

### Tool Comparison

| Tool | Speed | Accuracy | Features |
|------|-------|----------|----------|
| dnsenum | Medium | Medium | DNS records, zone transfers, Google scraping |
| fierce | Slow | Medium | Recursive discovery, wildcard detection |
| dnsrecon | Medium | High | Multiple techniques, custom output |
| amass | Slow | Very High | 20+ data sources, API integrations |
| assetfinder | Fast | Medium | Quick passive + active combo |
| puredns | Very Fast | High | Resolver, wildcard filtering, massdns wrapper |
| gobuster dns | Fast | Medium | Simple, fast bruteforcing |

---

## Phase 2: Wordlist Preparation

### Popular Wordlists

| Wordlist | Location | Size |
|----------|----------|------|
| SecLists (top 20k) | /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt | 20k |
| SecLists (top 110k) | /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt | 110k |
| dnscan | /usr/share/wordlists/dnscan.txt | 1.4M |
| Commonspeak2 | https://github.com/assetnote/commonspeak2 | 2M+ |
| Jhaddix's all.txt | https://gist.github.com/jhaddix/86a06c5dc309d08580a018c66354a056 | 2M+ |

### Combine Wordlists

cat wordlist1.txt wordlist2.txt wordlist3.txt | sort -u > combined.txt

### Generate Custom Wordlist

# From keywords
echo -e "dev\nstaging\ntest\nprod\nuat\nqa\ndemo" > custom.txt

# From company name patterns
echo -e "inlanefreight\nilf\ninlana\ninfra\ninternal" > company-words.txt

# From employee names (if known)
echo -e "john\njane\nbob\nalice" > names.txt

---

## Phase 3: Execution

### dnsenum (Comprehensive)

dnsenum --enum target.com -f /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt -r

Options:
- `-r`: Enable recursive bruteforcing
- `-p`: Set pages to scrape from Google
- `-s`: Set maximum Google scrape pages
- `-o`: Output file

### fierce (User-Friendly)

fierce --domain target.com --dns-servers 8.8.8.8 --subdomains /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt

### dnsrecon (Versatile)

dnsrecon -d target.com -t brt -D /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt

### amass (Professional)

amass enum -d target.com -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt -o amass-results.txt

### gobuster (Fast)

gobuster dns -d target.com -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt -t 50

### assetfinder (Quick)

assetfinder --subs-only target.com | tee assetfinder-results.txt

### puredns (Powerful)

puredns bruteforce /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt target.com -r /path/to/resolvers.txt

---

## Phase 4: Resolution and Filtering

### Basic Resolution with host

for sub in $(cat subdomains.txt); do
    host $sub.target.com | grep "has address" >> resolved.txt
done

### Extract IPs from Results

grep -oP '([0-9]{1,3}\.){3}[0-9]{1,3}' resolved.txt | sort -u

### Filter by HTTP Response

while read sub; do
    code=$(curl -s -o /dev/null -w "%{http_code}" http://$sub 2>/dev/null)
    if [[ $code != "000" ]]; then
        echo "$sub -> $code"
    fi
done < subdomains.txt

### Wildcard Detection

# Check if random subdomain resolves
host asdfghjkl123.target.com

# If it resolves, wildcard DNS is enabled - need to filter

---

## Phase 5: Validation

### Check for Live Web Servers

for sub in $(cat resolved.txt | awk '{print $1}' | sed 's/\.$//'); do
    echo "[*] Checking $sub"
    curl -s -I -L -m 5 http://$sub -o /dev/null -w "%{http_code}\n" | grep -q "200\|301\|302\|401\|403" && echo "[+] Live: http://$sub"
    curl -s -I -L -m 5 https://$sub -o /dev/null -w "%{http_code}\n" | grep -q "200\|301\|302\|401\|403" && echo "[+] Live: https://$sub"
done

### Screenshot Live Subdomains

# Using aquatone
cat live-subdomains.txt | aquatone -out screenshots

# Using httpx
cat subdomains.txt | httpx -title -status-code -content-length -o httpx-results.txt

### Technology Fingerprinting

for sub in $(cat live-subdomains.txt); do
    whatweb $sub -a 3 > "whatweb-$sub.txt"
done

### Port Scanning Interesting Subdomains

nmap -p 80,443,8080,8443,22,21,3306,5432 -iL live-subdomains.txt -oA subdomain-nmap

---

## Phase 6: Automation

### Complete Subdomain Bruteforce Script

Save as `bruteforce-subdomains.sh`:

#!/bin/bash
DOMAIN=$1
WORDLIST=$2
OUTPUT_DIR="bruteforce-$DOMAIN"
mkdir -p $OUTPUT_DIR

echo "[*] Starting subdomain bruteforce for $DOMAIN"
echo "[*] Using wordlist: $WORDLIST"

echo "[*] Running dnsenum..."
dnsenum --enum $DOMAIN -f $WORDLIST -o $OUTPUT_DIR/dnsenum.txt > /dev/null 2>&1

echo "[*] Running gobuster..."
gobuster dns -d $DOMAIN -w $WORDLIST -t 50 -o $OUTPUT_DIR/gobuster.txt > /dev/null 2>&1

echo "[*] Running assetfinder..."
assetfinder --subs-only $DOMAIN > $OUTPUT_DIR/assetfinder.txt

echo "[*] Combining results..."
cat $OUTPUT_DIR/*.txt | grep -oP '([a-zA-Z0-9._-]+\.'$DOMAIN')' | sort -u > $OUTPUT_DIR/all-subdomains.txt

echo "[*] Resolving subdomains..."
while read sub; do
    host $sub 2>/dev/null | grep "has address" >> $OUTPUT_DIR/resolved.txt
done < $OUTPUT_DIR/all-subdomains.txt

echo "[*] Checking live web servers..."
while read line; do
    sub=$(echo $line | awk '{print $1}' | sed 's/\.$//')
    http_code=$(curl -s -o /dev/null -w "%{http_code}" http://$sub 2>/dev/null)
    https_code=$(curl -s -o /dev/null -w "%{http_code}" https://$sub 2>/dev/null)
    
    if [[ $http_code != "000" ]]; then
        echo "http://$sub ($http_code)" >> $OUTPUT_DIR/live.txt
    fi
    if [[ $https_code != "000" ]]; then
        echo "https://$sub ($https_code)" >> $OUTPUT_DIR/live.txt
    fi
done < $OUTPUT_DIR/resolved.txt

echo "[*] Bruteforce complete!"
echo "[+] Total subdomains found: $(wc -l < $OUTPUT_DIR/all-subdomains.txt)"
echo "[+] Resolved subdomains: $(wc -l < $OUTPUT_DIR/resolved.txt)"
echo "[+] Live web servers: $(wc -l < $OUTPUT_DIR/live.txt)"
echo "[*] Results saved in $OUTPUT_DIR/"

---

## Performance Optimization

### Use Multiple Resolvers

Create a resolvers file:
8.8.8.8
8.8.4.4
1.1.1.1
1.0.0.1
9.9.9.9
208.67.222.222
208.67.220.220

### Use massdns for Speed

massdns -r resolvers.txt -t A -o S -w massdns-output.txt subdomains.txt

### Filter with puredns

puredns resolve subdomains.txt -r resolvers.txt -w resolved.txt

---

## Common Subdomain Patterns

| Pattern | Example | Likely Use |
|---------|---------|------------|
| dev.* | dev.target.com | Development environment |
| *.api | api.target.com | API endpoint |
| *.app | app.target.com | Web application |
| *.admin | admin.target.com | Admin panel |
| *.portal | portal.target.com | User portal |
| *.vpn | vpn.target.com | VPN gateway |
| *.mail | mail.target.com | Webmail |
| *.git | git.target.com | Git server |
| *.jenkins | jenkins.target.com | CI/CD |
| *.jira | jira.target.com | Project management |
| *.confluence | confluence.target.com | Wiki |
| *.grafana | grafana.target.com | Monitoring |
| *.prometheus | prometheus.target.com | Monitoring |
| *.kibana | kibana.target.com | Log analysis |
| *.elastic | elastic.target.com | Elasticsearch |
| *.s3 | s3.target.com | AWS S3 bucket |
| *.storage | storage.target.com | File storage |

---

## Tool-Specific Options

### dnsenum Advanced Options

| Option | Description |
|--------|-------------|
| `--enum` | Shortcut for common options |
| `-f` | Wordlist file |
| `-r` | Enable recursive enumeration |
| `-d` | Enable DNS dictionary brute force |
| `-s` | Maximum Google scrape pages |
| `-p` | Pages to scrape from Google |
| `-o` | Output file |
| `-w` | Enable WHOIS queries |

### amass Advanced Options

| Option | Description |
|--------|-------------|
| `-active` | Use active connection methods |
| `-brute` | Enable bruteforcing |
| `-w` | Wordlist file |
| `-config` | Config file |
| `-o` | Output file |
| `-oA` | Output in all formats |
| `-d` | Domain to enumerate |
| `-ip` | Show IP addresses |
| `-src` | Show source of each result |

---

## Key Takeaways

- Subdomain bruteforcing is active reconnaissance - it can be detected
- Quality wordlists are more important than tool choice
- Combine multiple tools for comprehensive results
- Always validate results (not all resolved subdomains are live)
- Check for wildcard DNS and filter accordingly
- Use multiple resolvers to avoid rate limiting
- Different tools find different subdomains
- Custom wordlists based on OSINT can be very effective
- Document all findings and their HTTP status codes
- Screenshot live subdomains for easy review
- Combine bruteforce results with passive sources
- Automate the process for large domains
