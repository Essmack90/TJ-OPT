---
tags: [module/web-recon, automation, finalrecon, recon-ng, theharvester, spiderfoot, scripting, level/advanced, practical]
---

# Automating Recon - Practical Application

## Complete Automation Workflow

Phase 1: Tool Selection
Phase 2: FinalRecon Deep Dive
Phase 3: Recon-ng Automation
Phase 4: theHarvester Integration
Phase 5: SpiderFoot
Phase 6: Custom Scripting
Phase 7: Pipeline Creation

---

## Phase 1: Tool Selection

### Tool Comparison Matrix

| Tool | Language | Modules | API Support | Learning Curve |
|------|----------|---------|-------------|----------------|
| FinalRecon | Python | 8+ | Limited | Easy |
| Recon-ng | Python | 100+ | Extensive | Medium |
| theHarvester | Python | 20+ sources | Some | Easy |
| SpiderFoot | Python | 200+ modules | Yes | Medium |
| Custom scripts | Any | Unlimited | Full | Steep |

### When to Use What

| Goal | Best Tool |
|------|-----------|
| Quick web recon | FinalRecon |
| Professional OSINT | Recon-ng |
| Email gathering | theHarvester |
| Comprehensive intel | SpiderFoot |
| Specific needs | Custom scripts |

---

## Phase 2: FinalRecon Deep Dive

### Full Recon Scan

./finalrecon.py --full --url http://inlanefreight.com

This runs:
- Headers
- SSL info
- Whois
- Crawl
- DNS
- Subdomains
- Directory search
- Wayback URLs

### Custom Directory Scan

./finalrecon.py --dir --url http://inlanefreight.com -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -e php,html,txt,bak

### DNS Enumeration with Custom Servers

./finalrecon.py --dns --url http://inlanefreight.com -d 8.8.8.8

### Subdomain Enumeration with API Keys

./finalrecon.py --sub --url http://inlanefreight.com -k shodan@YOUR_API_KEY

### Export Results

./finalrecon.py --full --url http://inlanefreight.com -o json

Export formats: txt, json, csv

### Automating FinalRecon

#!/bin/bash
TARGET=$1
OUTPUT_DIR="finalrecon-$TARGET"
mkdir -p $OUTPUT_DIR

./finalrecon.py --full --url http://$TARGET -o json > $OUTPUT_DIR/full.json
./finalrecon.py --sub --url http://$TARGET > $OUTPUT_DIR/subdomains.txt
./finalrecon.py --dir --url http://$TARGET -e php,html,txt,bak > $OUTPUT_DIR/directories.txt

echo "[*] FinalRecon scan complete for $TARGET"

---

## Phase 3: Recon-ng Automation

### Starting Recon-ng

./recon-ng

### Basic Workspace Setup

workspace create target_company
workspace list
workspace load target_company

### Installing Modules

marketplace search
marketplace install recon/domains-hosts/google_site_web
marketplace install recon/domains-hosts/brute_hosts
marketplace install recon/hosts-hosts/resolve

### Running Modules

modules load recon/domains-hosts/google_site_web
options set SOURCE target.com
run

### API Key Configuration

keys add shodan YOUR_API_KEY
keys add virustotal YOUR_API_KEY

### Automated Recon-ng Script

Create a resource file target.rc:

workspace create target
workspace load target
marketplace install recon/domains-hosts/google_site_web
marketplace install recon/domains-hosts/brute_hosts
marketplace install recon/hosts-hosts/resolve

modules load recon/domains-hosts/google_site_web
options set SOURCE target.com
run

modules load recon/domains-hosts/brute_hosts
options set SOURCE target.com
options set WORDLIST /usr/share/wordlists/subdomains.txt
run

modules load recon/hosts-hosts/resolve
run

exit

Run it:
./recon-ng -r target.rc

### Export Results

marketplace install reporting/csv
modules load reporting/csv
options set FILENAME recon-results.csv
run

---

## Phase 4: theHarvester Integration

### Basic Email Harvesting

theHarvester -d target.com -b google -f theharvester_results

### Multiple Sources

theHarvester -d target.com -b google,bing,linkedin,shodan -f all_sources

### API-Enabled Sources

theHarvester -d target.com -b shodan -f shodan_results

### API Key Setup

Create ~/theHarvester/api-keys.yaml:
shodan: YOUR_API_KEY
virustotal: YOUR_API_KEY
hunter: YOUR_API_KEY

### Automating theHarvester

#!/bin/bash
DOMAIN=$1
OUTPUT_DIR="theharvester-$DOMAIN"
mkdir -p $OUTPUT_DIR

for source in google bing linkedin shodan; do
    theHarvester -d $DOMAIN -b $source -f $OUTPUT_DIR/$source.xml
    sleep 5  # Be polite
done

# Extract emails
grep -r -o '[a-zA-Z0-9._%+-]\+@[a-zA-Z0-9.-]\+\.[a-zA-Z]\{2,\}' $OUTPUT_DIR/ | sort -u > $OUTPUT_DIR/all-emails.txt

echo "[*] Found $(wc -l < $OUTPUT_DIR/all-emails.txt) unique emails"

---

## Phase 5: SpiderFoot

### Docker Setup

docker pull spiderfoot
docker run -d -p 5001:5001 spiderfoot

### CLI Usage

python3 sf.py -l 127.0.0.1:5001

### API Usage

#!/bin/bash
API_KEY="YOUR_API_KEY"
SCAN_NAME="target_scan"
TARGET="target.com"

# Create scan
curl -XPOST http://localhost:5001/startscan \
  -d "scanname=$SCAN_NAME&scantarget=$TARGET&modulelist=sfp_dns,sfp_subdomain&usecase=all"

# Check status
curl http://localhost:5001/scanstatus\?scanid\=$SCAN_ID

# Get results
curl http://localhost:5001/scanresultsevent\?scanid\=$SCAN_ID\&eventtype\=URL_FORM

### SpiderFoot Modules

Categories:
- DNS (sfp_dns, sfp_subdomain)
- Search engines (sfp_google, sfp_bing)
- Social media (sfp_linkedin, sfp_twitter)
- Threat intel (sfp_virustotal, sfp_shodan)
- Web (sfp_webframework, sfp_cookie)

---

## Phase 6: Custom Scripting

### Complete Recon Script

Save as auto-recon.sh:

#!/bin/bash
TARGET=$1
OUTPUT_DIR="recon-$TARGET-$(date +%Y%m%d_%H%M%S)"
mkdir -p $OUTPUT_DIR

echo "[*] Starting automated recon for $TARGET"
echo "[*] Results saved to $OUTPUT_DIR"

# Phase 1: FinalRecon
echo "[*] Running FinalRecon..."
if [ -d "FinalRecon" ]; then
    cd FinalRecon
    ./finalrecon.py --full --url http://$TARGET -o json > ../$OUTPUT_DIR/finalrecon.json
    cd ..
else
    echo "[-] FinalRecon not found, skipping"
fi

# Phase 2: DNS Enumeration
echo "[*] Running DNS enumeration..."
for type in A AAAA MX NS TXT SOA; do
    dig $TARGET $type +short > $OUTPUT_DIR/dns-$type.txt
done

# Phase 3: Subdomain discovery
echo "[*] Finding subdomains..."
if command -v subfinder &> /dev/null; then
    subfinder -d $TARGET -o $OUTPUT_DIR/subfinder.txt
fi

if command -v assetfinder &> /dev/null; then
    assetfinder --subs-only $TARGET > $OUTPUT_DIR/assetfinder.txt
fi

# Phase 4: Certificate Transparency
echo "[*] Checking crt.sh..."
curl -s "https://crt.sh/?q=%25.$TARGET&output=json" | jq -r '.[].name_value' | sed 's/*.//g' | sort -u > $OUTPUT_DIR/crt-subdomains.txt

# Phase 5: Wayback Machine
echo "[*] Fetching Wayback URLs..."
curl -s "http://web.archive.org/cdx/search/cdx?url=$TARGET&output=json&fl=original&collapse=urlkey" | jq -r '.[] | select(length > 0) | .[0]' | sort -u > $OUTPUT_DIR/wayback-urls.txt

# Phase 6: theHarvester (if installed)
if command -v theHarvester &> /dev/null; then
    echo "[*] Running theHarvester..."
    theHarvester -d $TARGET -b google -f $OUTPUT_DIR/theharvester.html
fi

# Phase 7: Technology detection
echo "[*] Detecting technologies..."
if command -v whatweb &> /dev/null; then
    whatweb $TARGET > $OUTPUT_DIR/whatweb.txt
fi

# Phase 8: Port scanning (quick)
echo "[*] Quick port scan..."
nmap -T4 -F $TARGET -oN $OUTPUT_DIR/nmap-quick.txt 2>/dev/null

# Phase 9: Combine and deduplicate subdomains
echo "[*] Combining subdomain results..."
cat $OUTPUT_DIR/*subdomains*.txt $OUTPUT_DIR/crt-subdomains.txt 2>/dev/null | grep -oP '([a-zA-Z0-9._-]+\.'$TARGET')' | sort -u > $OUTPUT_DIR/all-subdomains.txt

# Phase 10: Generate report
echo "[*] Generating report..."
{
    echo "=== Automated Recon Report for $TARGET ==="
    echo "Date: $(date)"
    echo ""
    echo "=== DNS Records ==="
    echo "A: $(cat $OUTPUT_DIR/dns-A.txt 2>/dev/null | tr '\n' ' ')"
    echo "MX: $(cat $OUTPUT_DIR/dns-MX.txt 2>/dev/null | tr '\n' ' ')"
    echo "NS: $(cat $OUTPUT_DIR/dns-NS.txt 2>/dev/null | tr '\n' ' ')"
    echo ""
    echo "=== Subdomains ==="
    echo "Total found: $(wc -l < $OUTPUT_DIR/all-subdomains.txt 2>/dev/null)"
    head -20 $OUTPUT_DIR/all-subdomains.txt 2>/dev/null
    echo ""
    echo "=== Wayback URLs ==="
    echo "Total found: $(wc -l < $OUTPUT_DIR/wayback-urls.txt 2>/dev/null)"
    head -10 $OUTPUT_DIR/wayback-urls.txt 2>/dev/null
    echo ""
    echo "=== Technologies ==="
    cat $OUTPUT_DIR/whatweb.txt 2>/dev/null
    echo ""
    echo "=== Open Ports ==="
    grep open $OUTPUT_DIR/nmap-quick.txt 2>/dev/null
} > $OUTPUT_DIR/report.txt

echo "[*] Recon complete! Check $OUTPUT_DIR/report.txt"
echo "[*] All raw data in $OUTPUT_DIR/"

### Parallel Processing Script

Save as parallel-recon.sh:

#!/bin/bash
DOMAINS_FILE=$1
OUTPUT_DIR="parallel-recon-$(date +%Y%m%d_%H%M%S)"
mkdir -p $OUTPUT_DIR

# Function to scan one domain
scan_domain() {
    domain=$1
    outdir="$OUTPUT_DIR/$domain"
    mkdir -p $outdir
    
    echo "[*] Scanning $domain"
    
    # Quick checks
    dig $domain A +short > $outdir/ip.txt
    curl -sI "http://$domain" > $outdir/headers.txt
    whatweb $domain > $outdir/whatweb.txt 2>/dev/null
    
    echo "[+] Done with $domain"
}

export -f scan_domain
export OUTPUT_DIR

# Run in parallel (max 5 at once)
cat $DOMAINS_FILE | xargs -I {} -P5 bash -c 'scan_domain "$@"' _ {}

echo "[*] Parallel scan complete. Results in $OUTPUT_DIR/"

---

## Phase 7: Pipeline Creation

### Complete Recon Pipeline

Save as recon-pipeline.sh:

#!/bin/bash
TARGET=$1
STAGE=$2

case $STAGE in
    passive)
        echo "[*] Running passive recon..."
        ./auto-recon.sh $TARGET
        ;;
    active)
        echo "[*] Running active recon..."
        nmap -sC -sV -p- $TARGET -oA nmap-$TARGET
        gobuster dir -u https://$TARGET -w /usr/share/wordlists/dirb/common.txt -o gobuster-$TARGET.txt
        ;;
    full)
        echo "[*] Running full pipeline..."
        ./recon-pipeline.sh $TARGET passive
        ./recon-pipeline.sh $TARGET active
        ;;
    report)
        echo "[*] Generating final report..."
        # Combine all results into one report
        ;;
esac

### Dockerizing Your Recon Tools

Create Dockerfile:

FROM kalilinux/kali-rolling
RUN apt-get update && apt-get install -y \
    nmap dnsutils whatweb gobuster \
    python3 python3-pip git
RUN git clone https://github.com/thewhiteh4t/FinalRecon.git
RUN pip3 install -r FinalRecon/requirements.txt
ENTRYPOINT ["/bin/bash"]

Build and run:
docker build -t recon-tools .
docker run -v $(pwd)/output:/output recon-tools ./FinalRecon/finalrecon.py --url http://target.com

---

## Automation Cheatsheet

| Task | Command |
|------|---------|
| FinalRecon full | ./finalrecon.py --full --url http://target.com |
| Recon-ng script | ./recon-ng -r script.rc |
| theHarvester | theHarvester -d target.com -b google -f results |
| SpiderFoot API | curl http://localhost:5001/startscan -d "scanname=test&scantarget=target.com" |
| Custom script | ./auto-recon.sh target.com |
| Parallel scan | ./parallel-recon.sh domains.txt |
| Pipeline | ./recon-pipeline.sh target.com full |

---

## Key Takeaways

- Automation scales recon across multiple targets
- FinalRecon is great for quick all-in-one scans
- Recon-ng has 100+ modules for deep dives
- theHarvester specializes in email discovery
- SpiderFoot automates OSINT from 200+ sources
- Custom scripts give you full control
- Always use API keys when available
- Parallel processing speeds up large scans
- Build pipelines that chain tools together
- Dockerize tools for portability
- Always verify automated findings
- Document your workflows
- Start simple, then add complexity
- Automation doesn't replace thinking
