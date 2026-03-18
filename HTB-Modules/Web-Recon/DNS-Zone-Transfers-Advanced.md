---
tags: [module/web-recon, dns, zone-transfer, axfr, subdomains, automation, level/advanced, practical]
---

# DNS Zone Transfers - Practical Application

## Complete Zone Transfer Workflow

Phase 1: Name Server Discovery
Phase 2: Zone Transfer Attempts
Phase 3: Analysis of Results
Phase 4: Automation
Phase 5: Remediation Testing

---

## Phase 1: Name Server Discovery

### Find Name Servers for a Domain

```bash
dig NS target.com +short
host -t NS target.com
nslookup -type=NS target.com
Get Name Servers with Full Details
bash
dig NS target.com +noall +answer
Example Output
bash
dig NS google.com +short
Output:
ns1.google.com.
ns2.google.com.
ns3.google.com.
ns4.google.com.
Extract Name Servers to File
bash
dig NS target.com +short > nameservers.txt
Phase 2: Zone Transfer Attempts
Basic Zone Transfer on Each Name Server
bash
for ns in $(dig NS target.com +short); do
    echo "[*] Trying zone transfer on $ns"
    dig AXFR target.com @$ns
    echo "-----------------------------------"
done
Zone Transfer with Different Tools
Using host
bash
host -l target.com ns1.target.com
Using nslookup (Interactive)
bash
nslookup
> server ns1.target.com
> ls -d target.com
> exit
Using fierce (Automated)
bash
fierce --domain target.com --dns-servers ns1.target.com
Full Zone Transfer Script
Save as axfr-check.sh:

bash
#!/bin/bash
DOMAIN=$1
OUTPUT_DIR="axfr-$DOMAIN"
mkdir -p $OUTPUT_DIR

echo "[*] Checking zone transfers for $DOMAIN"

NAMESERVERS=$(dig NS $DOMAIN +short)

for ns in $NAMESERVERS; do
    echo "[*] Testing $ns"
    dig AXFR $DOMAIN @$ns > "$OUTPUT_DIR/$ns.txt" 2>&1
    
    if grep -q "Transfer failed" "$OUTPUT_DIR/$ns.txt"; then
        echo "[-] Zone transfer failed on $ns"
    elif grep -q "XFR size" "$OUTPUT_DIR/$ns.txt"; then
        echo "[!] ZONE TRANSFER SUCCEEDED on $ns"
        echo "[!] Check $OUTPUT_DIR/$ns.txt for results"
    else
        echo "[-] No zone transfer on $ns"
    fi
done
Phase 3: Analysis of Results
Parse Successful Zone Transfer
bash
# Count records
grep "IN" axfr-results.txt | wc -l

# Extract all A records (IPs)
grep "IN A" axfr-results.txt

# Extract all subdomains
grep -oP '([a-zA-Z0-9._-]+\.'$DOMAIN')' axfr-results.txt | sort -u

# Extract all IPs
grep -oP '([0-9]{1,3}\.){3}[0-9]{1,3}' axfr-results.txt | sort -u

# Find mail servers
grep "IN MX" axfr-results.txt

# Find name servers
grep "IN NS" axfr-results.txt | grep -v $DOMAIN

# Find TXT records
grep "IN TXT" axfr-results.txt
Identify Internal IPs
bash
grep -E '10\.[0-9]+\.[0-9]+\.[0-9]+|172\.(1[6-9]|2[0-9]|3[0-1])\.[0-9]+\.[0-9]+|192\.168\.[0-9]+\.[0-9]+' axfr-results.txt
Create Subdomain List from Zone Transfer
bash
grep -oP '([a-zA-Z0-9._-]+\.'$DOMAIN')' axfr-results.txt | sed 's/\.$//' | sort -u > subdomains-from-axfr.txt
Phase 4: Automation
Complete Zone Transfer Scanner
Save as zone-transfer-scanner.sh:

bash
#!/bin/bash
DOMAIN=$1
OUTPUT_DIR="zone-transfer-scan-$DOMAIN"
mkdir -p $OUTPUT_DIR

echo "[*] Starting zone transfer scan for $DOMAIN"
echo "[*] Results will be saved in $OUTPUT_DIR/"

echo "[*] Finding name servers..."
dig NS $DOMAIN +short > $OUTPUT_DIR/nameservers.txt

if [ ! -s $OUTPUT_DIR/nameservers.txt ]; then
    echo "[-] No name servers found for $DOMAIN"
    exit 1
fi

echo "[+] Found $(wc -l < $OUTPUT_DIR/nameservers.txt) name servers"

while read ns; do
    echo "[*] Testing zone transfer on $ns"
    
    dig AXFR $DOMAIN @$ns > "$OUTPUT_DIR/axfr-$ns.txt" 2>&1
    
    if grep -q "XFR size" "$OUTPUT_DIR/axfr-$ns.txt"; then
        echo "[!] VULNERABLE: Zone transfer succeeded on $ns"
        echo "$ns" >> $OUTPUT_DIR/vulnerable.txt
        
        # Extract all subdomains
        grep -oP '([a-zA-Z0-9._-]+\.'$DOMAIN')' "$OUTPUT_DIR/axfr-$ns.txt" | sed 's/\.$//' | sort -u > "$OUTPUT_DIR/subdomains-$ns.txt"
        
        echo "[+] Found $(wc -l < "$OUTPUT_DIR/subdomains-$ns.txt") subdomains from $ns"
        
    elif grep -q "Transfer failed" "$OUTPUT_DIR/axfr-$ns.txt"; then
        echo "[-] Zone transfer failed on $ns (refused)"
    else
        echo "[-] Zone transfer failed on $ns (other error)"
    fi
    
    echo "-----------------------------------"
done < $OUTPUT_DIR/nameservers.txt

if [ -f $OUTPUT_DIR/vulnerable.txt ]; then
    echo "[!] VULNERABLE NAME SERVERS FOUND:"
    cat $OUTPUT_DIR/vulnerable.txt
else
    echo "[+] No vulnerable name servers found"
fi

echo "[*] Scan complete. Check $OUTPUT_DIR/ for details"
Bulk Domain Zone Transfer Check
Save as bulk-axfr-check.sh:

bash
#!/bin/bash
DOMAIN_LIST=$1
OUTPUT_DIR="bulk-axfr-scan"
mkdir -p $OUTPUT_DIR

while read domain; do
    echo "[*] Checking $domain"
    
    mkdir -p "$OUTPUT_DIR/$domain"
    
    dig NS $domain +short > "$OUTPUT_DIR/$domain/nameservers.txt"
    
    while read ns; do
        dig AXFR $domain @$ns > "$OUTPUT_DIR/$domain/$ns.txt" 2>&1
        
        if grep -q "XFR size" "$OUTPUT_DIR/$domain/$ns.txt"; then
            echo "[!] $domain is VULNERABLE on $ns"
            echo "$domain $ns" >> $OUTPUT_DIR/vulnerable.txt
        fi
    done < "$OUTPUT_DIR/$domain/nameservers.txt" 2>/dev/null
    
    sleep 1
done < $DOMAIN_LIST

echo "[*] Bulk scan complete. Vulnerable domains saved to $OUTPUT_DIR/vulnerable.txt"
Phase 5: Remediation Testing
Test if Zone Transfer is Properly Restricted
After finding a vulnerable server, test if the fix works:

bash
# Before fix - should work
dig AXFR target.com @ns1.target.com

# After fix - should fail with:
# ; Transfer failed.
# ;; Query time: ...
Check SOA Serial Number for Changes
bash
# Get SOA serial from primary
dig SOA target.com @ns1.target.com +short

# Get SOA serial from secondary
dig SOA target.com @ns2.target.com +short

# If they match, zone transfer is working (intended)
# If secondary has older serial, sync issues
Zone Transfer Prevention Checklist
Action	Description
Restrict by IP	Allow zone transfers only from specific secondary server IPs
Use TSIG	Transaction signatures for authenticated transfers
Disable AXFR	If not needed, disable entirely
Network segmentation	Isolate DNS management traffic
Monitoring	Alert on unauthorized zone transfer attempts
Real-World Vulnerable Domains (For Practice)
Do not test on real domains without permission. Use these for practice:

zonetransfer.me - Deliberately vulnerable for education

dig axfr @nsztm1.digi.ninja zonetransfer.me

Zone Transfer Cheatsheet
Command	Purpose
dig NS target.com +short	Find name servers
dig AXFR target.com @ns	Attempt zone transfer
host -l target.com ns	Zone transfer with host
nslookup -> ls -d target.com	Zone transfer with nslookup
grep "XFR size" axfr.txt	Check if transfer succeeded
grep "IN A" axfr.txt	Extract all A records
grep -oP '([a-zA-Z0-9._-]+\.target\.com)' axfr.txt	Extract all subdomains
What to Do If You Find a Vulnerable Server
Document everything (for your report)

Extract all subdomains and IPs

Check for internal IPs (10.x, 172.16.x, 192.168.x)

Validate live hosts from the list

Include in your findings as HIGH severity

Recommend immediate restriction of zone transfers

Key Takeaways
Zone transfers (AXFR) can leak your ENTIRE DNS infrastructure

Always check every name server for a domain

A single successful transfer is better than thousands of brute-force attempts

Modern servers should block unauthorized transfers, but misconfigurations happen

zonetransfer.me is a legal test site

Internal IPs in zone files = major red flag

Automate checking across all discovered name servers

If you find one, document carefully and report immediately

Use multiple tools to verify (dig, host, nslookup)

Combine zone transfer results with other recon methods
