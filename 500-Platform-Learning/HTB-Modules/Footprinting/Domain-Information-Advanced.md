---
tags: [module/footprinting, domain, osint, level/advanced, practical]
---

# Domain Information - Practical Application

## Complete Domain Enumeration Workflow

This is a systematic approach to gathering all possible domain information passively.

Phase 1: Company Understanding
Phase 2: SSL Certificate Analysis
Phase 3: Certificate Transparency Logs
Phase 4: DNS Record Enumeration
Phase 5: IP Resolution and Shodan
Phase 6: Third-Party Provider Identification
Phase 7: Attack Surface Mapping

---

## Phase 1: Company Understanding

Before any technical steps, understand the business.

### What to Research

| Category | Questions | Sources |
|----------|-----------|---------|
| Products/Services | What do they sell? What tech is needed? | Company website |
| Size | Small, medium, enterprise? | About Us, LinkedIn |
| Locations | Geographic presence | Contact page, offices |
| Tech Stack | What do they advertise? | Careers page, job postings |
| Partners | Who do they work with? | Partners page, press releases |

### Why This Matters

If they offer IoT solutions, they likely have:
- MQTT brokers
- Device management platforms
- Cloud dashboards
- API endpoints

If they use Atlassian (from TXT records), they likely have:
- Jira (project management)
- Confluence (wiki)
- Bitbucket (code repos)

You can't test what you don't know exists.

---

## Phase 2: SSL Certificate Analysis

### Manual Browser Check

View certificate -> Details -> Subject Alternative Name

### Command Line Check

openssl s_client -connect target.com:443 2>/dev/null | openssl x509 -text | grep DNS

### Extract All SANs

openssl s_client -connect target.com:443 2>/dev/null | openssl x509 -text | grep -A1 "Subject Alternative Name" | tail -1 | sed 's/DNS://g' | tr ',' '\n' | sed 's/^ //g'

---

## Phase 3: Certificate Transparency Logs

### Multiple CT Log Sources

| Source | URL | Notes |
|--------|-----|-------|
| crt.sh | https://crt.sh | Main source |
| Facebook CT | https://developers.facebook.com/tools/ct | Alternative |
| Google CT | https://transparencyreport.google.com/https/certificates | Google's view |

### Advanced crt.sh Queries

Get all certificates for domain:
curl -s "https://crt.sh/?q=target.com&output=json" | jq -r '.[].name_value' | sed 's/\*\.//g' | sort -u

Get certificates issued in last 30 days:
curl -s "https://crt.sh/?q=target.com&excluded=expired&output=json" | jq -r '.[].name_value' | sort -u

Get only wildcard certificates:
curl -s "https://crt.sh/?q=%.target.com&output=json" | jq -r '.[].name_value' | grep '^\*\.' | sort -u

### Automation Script

DOMAIN=$1
curl -s "https://crt.sh/?q=$DOMAIN&output=json" | jq -r '.[].name_value' | sed 's/\*\.//g' | sort -u > crt-subdomains.txt
echo "Found $(wc -l < crt-subdomains.txt) unique subdomains from crt.sh"

---

## Phase 4: DNS Record Enumeration

### Complete DNS Query

dig any target.com

### Zone Transfer Attempt (If Misconfigured)

dig axfr target.com @ns1.target.com

### Brute Force Subdomains (Passive)

Use wordlists without scanning:
dnsrecon -d target.com -D /usr/share/wordlists/dns/subdomains-top1million-5000.txt -t brt

### DNS Record Types to Check

| Record | Command | What to Look For |
|--------|---------|------------------|
| A | dig target.com A | IPv4 addresses |
| AAAA | dig target.com AAAA | IPv6 addresses |
| MX | dig target.com MX | Mail providers |
| NS | dig target.com NS | Hosting providers |
| TXT | dig target.com TXT | Verification, SPF, DKIM |
| SOA | dig target.com SOA | Admin email |
| CNAME | dig target.com CNAME | Aliases to other domains |
| PTR | dig -x IP | Reverse lookup |

### TXT Record Deep Dive

dig txt target.com | grep -E "MS=|atlassian|google|logmein|mailgun|outlook|spf"

Look for:
- MS=* (Microsoft)
- atlassian-domain-verification=*
- google-site-verification=*
- logmein-verification-code=*
- include:mailgun.org
- include:_spf.google.com
- include:spf.protection.outlook.com
- include:_spf.atlassian.net
- ip4: (internal IPs)

---

## Phase 5: IP Resolution and Shodan

### Resolve All Subdomains to IPs

SUBDOMAINS="subdomains.txt"
OUTPUT="ip-addresses.txt"

while read subdomain; do
    ip=$(host $subdomain | grep "has address" | awk '{print $4}')
    if [ ! -z "$ip" ]; then
        echo "$subdomain : $ip"
        echo $ip >> $OUTPUT
    fi
done < $SUBDOMAINS

sort -u $OUTPUT -o $OUTPUT
echo "Unique IPs: $(wc -l < $OUTPUT)"

### Shodan Bulk Query

IPS="ip-addresses.txt"

while read ip; do
    echo "========== $ip =========="
    shodan host $ip 2>/dev/null | grep -E "Ports|Port:|Organization|City|Country|SSL|SSH|http"
    echo ""
done < $IPS

### Shodan Filters

| Filter | Purpose | Example |
|--------|---------|---------|
| port | Specific port | port:22 |
| product | Service name | product:nginx |
| version | Version number | version:7.6p1 |
| os | Operating system | os:Linux |
| org | Organization | org:"InlaneFreight" |

Advanced Shodan Query:
shodan search org:"InlaneFreight" port:22,80,443,445

---

## Phase 6: Third-Party Provider Identification

### From DNS Records

| Provider | Indicators | Attack Surface |
|----------|------------|----------------|
| Google | MX: google.com, TXT: google-site-verification | GDrive, Google Auth, Workspace |
| Microsoft | MX: outlook.com, TXT: MS= | Office 365, OneDrive, Azure |
| Atlassian | TXT: atlassian-domain-verification | Jira, Confluence, Bitbucket |
| LogMeIn | TXT: logmein-verification-code | Remote access platform |
| Mailgun | SPF: include:mailgun.org | Email APIs |
| Amazon | CNAME to amazonaws.com | S3 buckets, EC2 |
| Cloudflare | NS: cloudflare.com | CDN, DDoS protection |

### From SSL Certificates

Check Certificate Issuer:
openssl s_client -connect target.com:443 2>/dev/null | openssl x509 -text | grep "Issuer"

Check Certificate Subject:
openssl s_client -connect target.com:443 2>/dev/null | openssl x509 -text | grep "Subject"

### From HTTP Headers

curl -I target.com | grep -i "server\|x-powered-by\|via"

Look for:
- Server: Apache/nginx/IIS
- X-Powered-By: PHP/ASP.NET
- Via: Cloudflare/Akamai

---

## Phase 7: Attack Surface Mapping

### Create a Target Inventory

| Asset Type | Examples | Found In |
|------------|----------|----------|
| Domains | target.com, dev.target.com | crt.sh |
| Subdomains | mail, admin, api | crt.sh, DNS |
| IPs | 10.129.27.33, 10.129.127.22 | A records |
| Services | SSH, HTTP, HTTPS | Shodan |
| Versions | OpenSSH 7.6p1, nginx 1.14 | Shodan |
| Technologies | Ubuntu, Apache, PHP | Headers, Shodan |
| Third-Party | Atlassian, Google, AWS | TXT records |
| Internal IPs | 10.129.24.8, 10.129.27.2 | SPF records |

### Prioritize Targets

High Priority (Test First):
- Custom applications (dev.target.com)
- Admin panels (admin.target.com)
- API endpoints (api.target.com)
- File servers (cloud.target.com)

Medium Priority:
- Standard web servers (www.target.com)
- Mail servers (mail.target.com)
- Development servers (dev.target.com)

Low Priority:
- Third-party hosted (amazonaws.com)
- CDN services (cloudflare.com)
- Redirects

---

## Real-World Example Analysis

From the module example:

### Visible Data
- Subdomains: matomo, smartfactory, blog, shop, etc.
- IPs: 10.129.24.93, 10.129.27.33, 10.129.127.22
- Ports: 22, 80, 443, 25, 53, 81, 110, 111, 444

### Invisible Inferences

From TXT records:
MS=ms92346782372 → Microsoft services
atlassian-domain-verification → Atlassian suite (Jira, Confluence)
logmein-verification-code → LogMeIn remote access
include:mailgun.org → Email API
include:_spf.google.com → Google Workspace
include:spf.protection.outlook.com → Microsoft email
include:_spf.atlassian.net → Atlassian
ip4:10.129.24.8,10.129.27.2,10.72.82.106 → Internal servers

### Attack Surface Created

1. Web servers on 80/443 (blog, matomo, shop)
2. SSH on 22 (potential credentials)
3. SMTP on 25 (email enumeration)
4. DNS on 53 (zone transfer?)
5. HTTP on 81 (alternate port)
6. POP3 on 110 (email access)
7. RPC on 111 (NFS?)
8. HTTP on 444 (another web service)
9. Atlassian suite (Jira/Confluence exploits)
10. LogMeIn (admin access)
11. Mailgun (API testing)
12. Google Workspace (GDrive shares)
13. Microsoft (Office 365, Azure)
14. Internal IPs (10.129.24.8, 10.129.27.2) → future targets

---

## Complete Automation Script

Save as domain-enum.sh:

DOMAIN=$1
OUTPUT_DIR="domain-enum-$DOMAIN"
mkdir -p $OUTPUT_DIR

echo "[*] Starting domain enumeration for $DOMAIN"

echo "[*] Checking crt.sh..."
curl -s "https://crt.sh/?q=$DOMAIN&output=json" | jq -r '.[].name_value' | sed 's/\*\.//g' | sort -u > $OUTPUT_DIR/crt-subdomains.txt
echo "[+] Found $(wc -l < $OUTPUT_DIR/crt-subdomains.txt) subdomains from crt.sh"

echo "[*] Getting DNS records..."
dig any $DOMAIN > $OUTPUT_DIR/dns-any.txt
dig txt $DOMAIN | grep -E "MS=|atlassian|google|logmein|mailgun|outlook|spf" > $OUTPUT_DIR/dns-txt-interesting.txt

echo "[*] Resolving IPs..."
while read subdomain; do
    host $subdomain 2>/dev/null | grep "has address" >> $OUTPUT_DIR/resolved.txt
done < $OUTPUT_DIR/crt-subdomains.txt

cut -d" " -f4 $OUTPUT_DIR/resolved.txt | sort -u > $OUTPUT_DIR/ips.txt
echo "[+] Found $(wc -l < $OUTPUT_DIR/ips.txt) unique IPs"

echo "[*] Enumeration complete. Results in $OUTPUT_DIR/"

---

## Key Takeaways

- Domain enumeration is PASSIVE - don't scan yet
- SSL certificates reveal multiple domains
- crt.sh gives historical certificate data
- TXT records expose third-party services
- SPF records reveal internal IPs
- Third-party services = more attack surface
- Build a complete inventory before active testing
- Document everything - you'll need it later
- Every piece of information leads to more questions
- You're building a map of their entire infrastructure

---

## Quick Reference Card

LAYER 1: SSL CERTIFICATES
    openssl s_client -connect target.com:443 | openssl x509 -text | grep DNS

LAYER 2: CERTIFICATE TRANSPARENCY
    curl -s "https://crt.sh/?q=target.com&output=json" | jq -r '.[].name_value'

LAYER 3: DNS RECORDS
    dig any target.com
    dig txt target.com
    dig mx target.com
    dig ns target.com

LAYER 4: IP RESOLUTION
    host subdomain.target.com | grep "has address"

LAYER 5: SHODAN
    shodan host IP_ADDRESS

LAYER 6: THIRD-PARTY DETECTION
    grep -E "MS=|atlassian|google|logmein|mailgun|outlook|spf" dns-txt.txt
