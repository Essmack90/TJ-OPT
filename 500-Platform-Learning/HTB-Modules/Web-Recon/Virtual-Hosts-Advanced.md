---
tags: [module/web-recon, vhosts, virtual-hosts, web-servers, gobuster, ffuf, automation, level/advanced, practical]
---

# Virtual Hosts - Practical Application

## Complete Virtual Host Discovery Workflow

Phase 1: Target Identification
Phase 2: Wordlist Preparation
Phase 3: Tool-Based Enumeration
Phase 4: Result Analysis
Phase 5: Validation
Phase 6: Automation

---

## Phase 1: Target Identification

### Find the IP Address

dig +short target.com
host target.com
nslookup target.com

### Check for Multiple Sites on Same IP

Use reverse IP lookup services:
- https://viewdns.info/reverse-ip/
- https://www.yougetsignal.com/tools/web-sites-on-web-server/
- https://rapiddns.io/sameip/

### Manual Command-Line Check

for domain in $(cat potential-domains.txt); do
    curl -s -H "Host: $domain" http://TARGET_IP | grep -i "title\|html"
done

---

## Phase 2: Wordlist Preparation

### Popular VHost Wordlists

| Wordlist | Location | Use |
|----------|----------|-----|
| SecLists subdomains | /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt | General purpose |
| SecLists common | /usr/share/seclists/Discovery/Web-Content/common.txt | Quick scans |
| Virtual host specific | /usr/share/seclists/Discovery/DNS/namelist.txt | DNS names |
| Custom built | Create your own | Targeted scans |

### Create Custom Wordlist from OSINT

# Extract potential subdomains from certificate logs
curl -s "https://crt.sh/?q=%25.target.com&output=json" | jq -r '.[].name_value' | sed 's/\*\.//g' | sort -u > potential-vhosts.txt

# Add common patterns
echo -e "dev\nstaging\ntest\nuat\nqa\ndemo\nadmin\nportal\ninternal\nprivate\nsecure\nvpn\nmail\nwebmail\ngit\njenkins\njira\nconfluence" >> potential-vhosts.txt

# Add from company name variations
echo -e "target\ntargetco\ntargetinc\ntargetcorp\ntarget-group\ntargetglobal" >> potential-vhosts.txt

# Sort and deduplicate
sort -u potential-vhosts.txt -o potential-vhosts.txt

---

## Phase 3: Tool-Based Enumeration

### gobuster

# Basic vhost scan
gobuster vhost -u http://TARGET_IP -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt --append-domain -t 50

# With SSL and custom user-agent
gobuster vhost -u https://TARGET_IP -w wordlist.txt --append-domain -k -t 100 -o vhost-results.txt --user-agent "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

# Filter by response size (ignore common false positives)
gobuster vhost -u http://TARGET_IP -w wordlist.txt --append-domain -t 50 | grep -v "Size: 0\|Size: 1234"

### ffuf (Faster Alternative)

# Basic vhost fuzzing with ffuf
ffuf -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt -H "Host: FUZZ.target.com" -u http://TARGET_IP -fc 404

# With filtering and recursion
ffuf -w wordlist.txt -H "Host: FUZZ.target.com" -u http://TARGET_IP -fs 1234 -t 100

# Multiple wordlists
ffuf -w wordlist1.txt:W1 -w wordlist2.txt:W2 -H "Host: W1.W2.target.com" -u http://TARGET_IP

### feroxbuster

feroxbuster --url http://TARGET_IP --hosts target.com --wordlist /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt

### wfuzz

wfuzz -c -w wordlist.txt -H "Host: FUZZ.target.com" http://TARGET_IP

---

## Phase 4: Result Analysis

### Understanding Response Codes

| Code | Meaning | Likely |
|------|---------|--------|
| 200 | OK | Valid vhost |
| 301/302 | Redirect | Valid vhost, redirecting |
| 401/403 | Unauthorized/Forbidden | Valid vhost, restricted |
| 404 | Not Found | Probably invalid |
| 500 | Server Error | Might be valid, broken |

### Filtering False Positives

# Check baseline response (default vhost)
curl -s -H "Host: doesnotexist.target.com" http://TARGET_IP | wc -c

# Compare discovered vhosts against baseline
while read vhost; do
    size=$(curl -s -H "Host: $vhost" http://TARGET_IP | wc -c)
    if [ $size -ne $BASELINE_SIZE ]; then
        echo "[+] Potential vhost: $vhost ($size bytes)"
    fi
done < discovered.txt

### Automated Analysis Script

Save as `vhost-analyze.sh`:

#!/bin/bash
TARGET=$1
WORDLIST=$2
OUTPUT_DIR="vhost-analysis-$TARGET"
mkdir -p $OUTPUT_DIR

echo "[*] Starting vhost analysis for $TARGET"

# Get baseline response
BASELINE_SIZE=$(curl -s -H "Host: thisisnotarealhostname$RANDOM" http://$TARGET | wc -c)
echo "[*] Baseline size: $BASELINE_SIZE bytes"

while read vhost; do
    # Send request with custom Host header
    response=$(curl -s -i -H "Host: $vhost" http://$TARGET)
    size=$(echo "$response" | wc -c)
    status=$(echo "$response" | head -1 | cut -d' ' -f2)
    
    # Compare with baseline
    if [ $size -ne $BASELINE_SIZE ]; then
        echo "[+] $vhost - Status: $status - Size: $size"
        echo "$vhost - Status: $status" >> $OUTPUT_DIR/potential.txt
        
        # Save full response for interesting finds
        if [ $status -eq 200 ] || [ $status -eq 301 ] || [ $status -eq 302 ] || [ $status -eq 401 ] || [ $status -eq 403 ]; then
            echo "$response" > "$OUTPUT_DIR/$vhost.txt"
        fi
    fi
done < $WORDLIST

echo "[*] Analysis complete. Results in $OUTPUT_DIR/"

---

## Phase 5: Validation

### Check with Hosts File

Add discovered vhosts to /etc/hosts:

echo "TARGET_IP forum.target.com" | sudo tee -a /etc/hosts
echo "TARGET_IP admin.target.com" | sudo tee -a /etc/hosts

Then visit in browser.

### Screenshot Live VHosts

# Using aquatone
cat potential-vhosts.txt | aquatone -out screenshots

# Using httpx
cat potential-vhosts.txt | httpx -title -status-code -content-length -o vhost-details.txt

### Technology Fingerprinting

for vhost in $(cat valid-vhosts.txt); do
    whatweb http://$vhost -a 3 > "whatweb-$vhost.txt"
done

### Port Scan Interesting VHosts

nmap -p 80,443,8080,8443,22,21,3306,5432 --script http-title -iL valid-vhosts.txt

---

## Phase 6: Automation

### Complete VHost Discovery Script

Save as `vhost-discover.sh`:

#!/bin/bash
TARGET_IP=$1
DOMAIN=$2
WORDLIST=$3
OUTPUT_DIR="vhost-scan-$TARGET_IP"
mkdir -p $OUTPUT_DIR

echo "[*] Starting vhost discovery for $TARGET_IP"
echo "[*] Using domain suffix: $DOMAIN"
echo "[*] Using wordlist: $WORDLIST"

# Step 1: Gobuster scan
echo "[*] Running gobuster..."
gobuster vhost -u http://$TARGET_IP -w $WORDLIST --append-domain -t 50 -o $OUTPUT_DIR/gobuster-raw.txt 2>/dev/null

# Step 2: Extract potential vhosts
grep "Found:" $OUTPUT_DIR/gobuster-raw.txt | awk '{print $2}' | cut -d':' -f1 > $OUTPUT_DIR/potential.txt

# Step 3: Get baseline response
BASELINE=$(curl -s -H "Host: invalid$RANDOM.$DOMAIN" http://$TARGET_IP | wc -c)
echo "[*] Baseline size: $BASELINE bytes" >> $OUTPUT_DIR/analysis.txt

# Step 4: Validate each vhost
while read vhost; do
    echo "[*] Checking $vhost"
    
    # Check HTTP
    http_response=$(curl -s -i -H "Host: $vhost" http://$TARGET_IP)
    http_size=$(echo "$http_response" | wc -c)
    http_status=$(echo "$http_response" | head -1 | cut -d' ' -f2)
    
    # Check HTTPS
    https_response=$(curl -s -i -k -H "Host: $vhost" https://$TARGET_IP 2>/dev/null)
    https_size=$(echo "$https_response" | wc -c)
    https_status=$(echo "$https_response" | head -1 | cut -d' ' -f2)
    
    # Compare with baseline
    if [ $http_size -ne $BASELINE ]; then
        echo "[+] HTTP: $vhost (Status: $http_status, Size: $http_size)"
        echo "$vhost HTTP $http_status $http_size" >> $OUTPUT_DIR/valid-http.txt
    fi
    
    if [ ! -z "$https_response" ] && [ $https_size -ne $BASELINE ]; then
        echo "[+] HTTPS: $vhost (Status: $https_status, Size: $https_size)"
        echo "$vhost HTTPS $https_status $https_size" >> $OUTPUT_DIR/valid-https.txt
    fi
    
    # Small delay to be polite
    sleep 0.1
done < $OUTPUT_DIR/potential.txt

# Step 5: Generate summary
echo "" >> $OUTPUT_DIR/summary.txt
echo "=== VHOST DISCOVERY SUMMARY ===" >> $OUTPUT_DIR/summary.txt
echo "Target: $TARGET_IP" >> $OUTPUT_DIR/summary.txt
echo "Domain: $DOMAIN" >> $OUTPUT_DIR/summary.txt
echo "Wordlist: $WORDLIST" >> $OUTPUT_DIR/summary.txt
echo "Date: $(date)" >> $OUTPUT_DIR/summary.txt
echo "" >> $OUTPUT_DIR/summary.txt

if [ -f $OUTPUT_DIR/valid-http.txt ]; then
    echo "HTTP VHosts Found:" >> $OUTPUT_DIR/summary.txt
    cat $OUTPUT_DIR/valid-http.txt >> $OUTPUT_DIR/summary.txt
fi

if [ -f $OUTPUT_DIR/valid-https.txt ]; then
    echo "" >> $OUTPUT_DIR/summary.txt
    echo "HTTPS VHosts Found:" >> $OUTPUT_DIR/summary.txt
    cat $OUTPUT_DIR/valid-https.txt >> $OUTPUT_DIR/summary.txt
fi

echo "" >> $OUTPUT_DIR/summary.txt
echo "Raw results saved in $OUTPUT_DIR/" >> $OUTPUT_DIR/summary.txt

echo "[*] Scan complete! Summary saved to $OUTPUT_DIR/summary.txt"

---

## Tool Comparison

| Tool | Speed | Accuracy | Best For |
|------|-------|----------|----------|
| gobuster | Fast | Medium | Quick scans |
| ffuf | Very Fast | High | Large wordlists |
| feroxbuster | Fast | High | Recursive discovery |
| wfuzz | Medium | Medium | Custom fuzzing |
| Custom scripts | Slow | Very High | Validation |

---

## Response Code Analysis

| Code | What It Means | Next Step |
|------|---------------|-----------|
| 200 OK | Site exists and is accessible | Visit, screenshot, enumerate |
| 301 Moved Permanently | Redirects to another URL | Check redirect target |
| 302 Found | Temporary redirect | Could be login portal |
| 401 Unauthorized | Authentication required | Try default creds |
| 403 Forbidden | Access denied | Could be admin area |
| 404 Not Found | Usually invalid | Probably ignore |
| 500 Server Error | Server error | Might be misconfigured |

---

## Common VHost False Positives

- Default virtual host (catch-all)
- Wildcard DNS entries
- CDN/proxy servers
- Load balancers
- Caching servers

### How to Filter

# Check if the same response appears for random hosts
curl -s -H "Host: asdfghjkl$RANDOM.target.com" http://TARGET_IP | md5sum

# If random host returns same content, you need a different approach

---

## Key Takeaways

- Virtual hosts allow multiple sites on one server
- The Host header determines which site is served
- VHosts can exist without DNS records
- Gobuster and ffuf are the primary tools
- Always establish a baseline response
- Filter out false positives by size comparison
- Check both HTTP and HTTPS
- Document all discovered vhosts
- Validate with browser after hosts file update
- Combine with other recon techniques
- Be careful with scan speed - it can be detected
- Screenshot interesting findings for reports
