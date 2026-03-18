---
tags: [module/web-recon, certificate-transparency, ct-logs, crt.sh, censys, ssl, tls, passive-recon, automation, level/advanced, practical]
---

# Certificate Transparency Logs - Practical Application

## Complete CT Log Enumeration Workflow

Phase 1: Basic crt.sh Queries
Phase 2: Advanced Filtering with jq
Phase 3: Censys Search
Phase 4: Historical Analysis
Phase 5: Automation
Phase 6: Integration with Other Tools

---

## Phase 1: Basic crt.sh Queries

### Simple Domain Search

```bash
curl -s "https://crt.sh/?q=target.com&output=json" | jq -r '.[].name_value' | sort -u
Extract All Unique Subdomains
bash
curl -s "https://crt.sh/?q=target.com&output=json" | jq -r '.[].name_value' | sed 's/\*\.//g' | sort -u > subdomains.txt
Include Common Name Field
bash
curl -s "https://crt.sh/?q=target.com&output=json" | jq -r '.[].name_value, .[].common_name' | grep -v "null" | sed 's/\*\.//g' | sort -u
Get Full Certificate Details
bash
curl -s "https://crt.sh/?q=target.com&output=json" | jq '.[] | {id: .id, name: .name_value, issued: .not_before, expires: .not_after, issuer: .issuer_name}'
Phase 2: Advanced Filtering with jq
Filter by Date Range
bash
# Get certificates issued in the last 30 days
curl -s "https://crt.sh/?q=target.com&output=json" | jq '.[] | select(.not_before > "2025-01-01") | .name_value' | sort -u

# Get certificates expiring soon
curl -s "https://crt.sh/?q=target.com&output=json" | jq '.[] | select(.not_after < "2025-12-31") | .name_value' | sort -u
Filter by Issuer
bash
# Get certificates issued by Let's Encrypt
curl -s "https://crt.sh/?q=target.com&output=json" | jq '.[] | select(.issuer_name | contains("Let\'s Encrypt")) | .name_value' | sort -u

# Get certificates from specific CA
curl -s "https://crt.sh/?q=target.com&output=json" | jq '.[] | select(.issuer_name | contains("DigiCert")) | .name_value' | sort -u
Filter by Subdomain Pattern
bash
# Find all dev/staging subdomains
curl -s "https://crt.sh/?q=target.com&output=json" | jq -r '.[].name_value' | grep -E "dev|staging|test|uat|qa|demo" | sort -u

# Find all API subdomains
curl -s "https://crt.sh/?q=target.com&output=json" | jq -r '.[].name_value' | grep "api" | sort -u

# Find internal/hidden subdomains
curl -s "https://crt.sh/?q=target.com&output=json" | jq -r '.[].name_value' | grep -E "internal|private|admin|portal|secure" | sort -u
Extract IPs from Certificates (if included)
bash
curl -s "https://crt.sh/?q=target.com&output=json" | jq -r '.[].ip_addresses[]?' 2>/dev/null | sort -u
Phase 3: Censys Search
Censys API Setup
bash
# Set your API credentials
export CENSYS_API_ID="your-api-id"
export CENSYS_API_SECRET="your-api-secret"
Basic Censys Query
bash
curl -s -X POST "https://search.censys.io/api/v2/certificates/search" \
  -u "$CENSYS_API_ID:$CENSYS_API_SECRET" \
  -H "Content-Type: application/json" \
  -d '{"q":"target.com", "per_page":100}' | jq '.'
Search for Certificates with Specific Attributes
bash
# Search by organization
curl -s -X POST "https://search.censys.io/api/v2/certificates/search" \
  -u "$CENSYS_API_ID:$CENSYS_API_SECRET" \
  -H "Content-Type: application/json" \
  -d '{"q":"parsed.issuer.organization: \"Target Company\"", "per_page":100}'

# Search by common name pattern
curl -s -X POST "https://search.censys.io/api/v2/certificates/search" \
  -u "$CENSYS_API_ID:$CENSYS_API_SECRET" \
  -H "Content-Type: application/json" \
  -d '{"q":"parsed.subject.common_name: *.dev.target.com", "per_page":100}'
Phase 4: Historical Analysis
Track Certificate Changes Over Time
bash
#!/bin/bash
DOMAIN=$1
YEAR=2024

for month in {01..12}; do
    echo "[*] Checking $YEAR-$month"
    curl -s "https://crt.sh/?q=$DOMAIN&output=json" | \
        jq -r --arg date "$YEAR-$month" '.[] | select(.not_before | contains($date)) | .name_value' | \
        sort -u > "certs-$YEAR-$month.txt"
    echo "[+] Found $(wc -l < "certs-$YEAR-$month.txt") subdomains"
done
Find Expired Certificates
bash
curl -s "https://crt.sh/?q=target.com&output=json" | \
  jq '.[] | select(.not_after < "2025-01-01") | {name: .name_value, expired: .not_after}' | \
  jq -r '.name + " (expired: " + .expired + ")"'
Find Wildcard Certificates
bash
curl -s "https://crt.sh/?q=target.com&output=json" | jq -r '.[].name_value' | grep "^\*" | sort -u
Phase 5: Automation
Complete CT Log Enumeration Script
Save as ct-enum.sh:

bash
#!/bin/bash
DOMAIN=$1
OUTPUT_DIR="ct-enum-$DOMAIN"
mkdir -p $OUTPUT_DIR

echo "[*] Starting Certificate Transparency enumeration for $DOMAIN"

# Function to query crt.sh and process results
query_crt() {
    local filter=$1
    local output=$2
    
    if [ -z "$filter" ]; then
        curl -s "https://crt.sh/?q=$DOMAIN&output=json"
    else
        curl -s "https://crt.sh/?q=$DOMAIN&output=json" | jq -r "$filter"
    fi
}

echo "[*] Querying crt.sh..."

# Get all subdomains
echo "[*] Extracting all subdomains..."
query_crt '.[].name_value' | sed 's/\*\.//g' | sort -u > $OUTPUT_DIR/all-subdomains.txt

# Get unique domains only (without wildcards)
echo "[*] Processing unique domains..."
grep -v "^\*" $OUTPUT_DIR/all-subdomains.txt | sort -u > $OUTPUT_DIR/unique-domains.txt

# Extract wildcard domains
echo "[*] Extracting wildcard domains..."
grep "^\*" $OUTPUT_DIR/all-subdomains.txt | sort -u > $OUTPUT_DIR/wildcard-domains.txt

# Get certificates with metadata
echo "[*] Fetching certificate metadata..."
query_crt '.[] | {id: .id, name: .name_value, issued: .not_before, expires: .not_after, issuer: .issuer_name}' | jq -r '. | [.id, .name, .issued, .expires, .issuer] | @csv' > $OUTPUT_DIR/certificates.csv

# Extract subdomains by pattern
echo "[*] Categorizing subdomains by pattern..."

# Development/staging
grep -E "dev|staging|test|uat|qa|demo|stage|sandbox" $OUTPUT_DIR/unique-domains.txt > $OUTPUT_DIR/dev-domains.txt

# Admin/management
grep -E "admin|manage|portal|dashboard|control|cpanel" $OUTPUT_DIR/unique-domains.txt > $OUTPUT_DIR/admin-domains.txt

# API/services
grep -E "api|service|services|graphql|rest|soap" $OUTPUT_DIR/unique-domains.txt > $OUTPUT_DIR/api-domains.txt

# Internal/hidden
grep -E "internal|private|secure|vpn|corp|office" $OUTPUT_DIR/unique-domains.txt > $OUTPUT_DIR/internal-domains.txt

# Count everything
echo "" >> $OUTPUT_DIR/summary.txt
echo "=== CT Log Enumeration Summary for $DOMAIN ===" >> $OUTPUT_DIR/summary.txt
echo "Date: $(date)" >> $OUTPUT_DIR/summary.txt
echo "" >> $OUTPUT_DIR/summary.txt
echo "Total subdomains found: $(wc -l < $OUTPUT_DIR/unique-domains.txt)" >> $OUTPUT_DIR/summary.txt
echo "Wildcard domains: $(wc -l < $OUTPUT_DIR/wildcard-domains.txt)" >> $OUTPUT_DIR/summary.txt
echo "Development domains: $(wc -l < $OUTPUT_DIR/dev-domains.txt 2>/dev/null || echo 0)" >> $OUTPUT_DIR/summary.txt
echo "Admin domains: $(wc -l < $OUTPUT_DIR/admin-domains.txt 2>/dev/null || echo 0)" >> $OUTPUT_DIR/summary.txt
echo "API domains: $(wc -l < $OUTPUT_DIR/api-domains.txt 2>/dev/null || echo 0)" >> $OUTPUT_DIR/summary.txt
echo "Internal domains: $(wc -l < $OUTPUT_DIR/internal-domains.txt 2>/dev/null || echo 0)" >> $OUTPUT_DIR/summary.txt

echo "[*] CT log enumeration complete!"
echo "[*] Results saved in $OUTPUT_DIR/"
echo "[*] Summary:"
cat $OUTPUT_DIR/summary.txt
Bulk Domain CT Log Scanner
Save as bulk-ct-scan.sh:

bash
#!/bin/bash
DOMAIN_LIST=$1
OUTPUT_DIR="bulk-ct-scan"
mkdir -p $OUTPUT_DIR

while read domain; do
    echo "[*] Processing $domain"
    
    curl -s "https://crt.sh/?q=$domain&output=json" | \
        jq -r '.[].name_value' | \
        sed 's/\*\.//g' | \
        sort -u > "$OUTPUT_DIR/$domain.txt"
    
    echo "[+] Found $(wc -l < "$OUTPUT_DIR/$domain.txt") subdomains for $domain"
    sleep 1  # Be polite to the API
done < $DOMAIN_LIST

echo "[*] Bulk scan complete. Results in $OUTPUT_DIR/"
Phase 6: Integration with Other Tools
Feed Subdomains to Other Recon Tools
bash
# Get subdomains from CT logs
./ct-enum.sh target.com

# Feed to httpx for live host checking
cat ct-enum-target.com/unique-domains.txt | httpx -title -status-code -o live-hosts.txt

# Feed to nuclei for vulnerability scanning
cat live-hosts.txt | nuclei -t cves/ -o nuclei-results.txt

# Feed to aquatone for screenshots
cat live-hosts.txt | aquatone -out screenshots

# Feed to gobuster for directory scanning
for host in $(cat live-hosts.txt); do
    gobuster dir -u https://$host -w /usr/share/seclists/Discovery/Web-Content/common.txt -o "gobuster-$host.txt"
done
Combine with Subdomain Bruteforce
bash
# Get CT log subdomains
curl -s "https://crt.sh/?q=target.com&output=json" | jq -r '.[].name_value' | sed 's/\*\.//g' | sort -u > ct-subdomains.txt

# Get brute-forced subdomains
gobuster dns -d target.com -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt -o brute-subdomains.txt

# Combine and deduplicate
cat ct-subdomains.txt brute-subdomains.txt | sort -u > all-subdomains.txt

echo "CT logs found: $(wc -l < ct-subdomains.txt)"
echo "Brute force found: $(wc -l < brute-subdomains.txt)"
echo "Total unique: $(wc -l < all-subdomains.txt)"
CT Log API Comparison
Feature	crt.sh	Censys
Free Tier	Yes	Yes (limited)
API Rate Limits	None (but be polite)	Rate limited
Historical Data	Yes	Yes
Advanced Filtering	Limited	Extensive
Requires Registration	No	Yes
Data Depth	Certificates only	Certificates + hosts + services
CT Log Query Cheatsheet
Command	Purpose
curl -s "https://crt.sh/?q=target.com&output=json" | jq -r '.[].name_value'	Get all subdomains
curl -s "https://crt.sh/?q=%.target.com&output=json"	Wildcard search
curl -s "https://crt.sh/?q=target.com&exclude=expired"	Exclude expired certs
jq -r '.[] | select(.name_value | contains("dev"))'	Filter for dev subdomains
jq -r '.[].name_value' | sed 's/\*\.//g'	Remove wildcard asterisks
jq -r '.[] | {id, name_value, not_before}'	Get metadata
Common CT Log Use Cases
Use Case	Command
Find all subdomains	curl -s "https://crt.sh/?q=target.com&output=json" | jq -r '.[].name_value' | sort -u
Find staging environments	curl -s "https://crt.sh/?q=target.com&output=json" | jq -r '.[].name_value' | grep -E "staging|stage|stg"
Find recently issued certs	curl -s "https://crt.sh/?q=target.com&output=json" | jq '.[] | select(.not_before > "2025-01-01")'
Find wildcard certs	curl -s "https://crt.sh/?q=target.com&output=json" | jq -r '.[].name_value' | grep "^*"
Count subdomains	curl -s "https://crt.sh/?q=target.com&output=json" | jq -r '.[].name_value' | wc -l
Key Takeaways
CT logs are public records of ALL SSL/TLS certificates ever issued

crt.sh is the easiest free API for CT log searching

Every subdomain with a certificate appears in CT logs

No need to guess or brute force - just query

CT logs reveal historical subdomains (old certs)

Wildcard certificates reveal domain patterns

SAN fields often list multiple domains per cert

Filter with jq to find dev, staging, internal subdomains

Combine CT log data with brute forcing for best results

This is 100% passive recon - no traffic to target

Automate CT log queries in your recon workflow

Always check CT logs early in your enumeration
