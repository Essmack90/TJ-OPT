---
tags: [module/web-recon, well-known, uris, metadata, configuration, automation, level/advanced, practical]
---

# .well-known URIs - Practical Application

## Complete .well-known Analysis Workflow

Phase 1: IANA Registry Research
Phase 2: Endpoint Discovery
Phase 3: security.txt Analysis
Phase 4: OpenID Connect Enumeration
Phase 5: MTA-STS and Email Security
Phase 6: Asset Verification
Phase 7: Automation

---

## Phase 1: IANA Registry Research

### IANA .well-known Registry

The full list of registered URIs is maintained by IANA:
https://www.iana.org/assignments/well-known-uris/well-known-uris.xhtml

### Fetch Registry Programmatically

curl -s https://www.iana.org/assignments/well-known-uris/well-known-uris.txt | grep -E "^[a-z-]+" > well-known-list.txt

### Extract All URIs

curl -s https://www.iana.org/assignments/well-known-uris/well-known-uris.xml | grep -oP '<registry>[^<]+' | sed 's/<registry>//' > well-known-uris.txt

---

## Phase 2: Endpoint Discovery

### Basic Discovery Script

#!/bin/bash
TARGET=$1
WORDLIST="well-known-uris.txt"
OUTPUT_DIR="wellknown-$TARGET"
mkdir -p $OUTPUT_DIR

while read uri; do
    url="https://$TARGET/.well-known/$uri"
    status=$(curl -s -o /dev/null -w "%{http_code}" $url)
    
    if [ $status -eq 200 ]; then
        echo "[FOUND] $url ($status)"
        curl -s $url > "$OUTPUT_DIR/$uri.txt"
    elif [ $status -eq 301 ] || [ $status -eq 302 ]; then
        redirect=$(curl -s -o /dev/null -w "%{redirect_url}" $url)
        echo "[REDIRECT] $url -> $redirect"
    elif [ $status -eq 401 ] || [ $status -eq 403 ]; then
        echo "[AUTH] $url ($status)"
    fi
done < $WORDLIST

### Using ffuf for Speed

ffuf -w well-known-uris.txt -u https://target.com/.well-known/FUZZ -mc 200,301,302,401,403 -o wellknown.json

### Using gospider

gospider -s https://target.com -o gospider-output --include-other-source

---

## Phase 3: security.txt Analysis

### Fetch and Parse

curl -s https://target.com/.well-known/security.txt > security.txt
curl -s https://target.com/security.txt >> security.txt

### Extract Contact Information

grep -i "^contact:" security.txt | cut -d' ' -f2-

### Extract Encryption Keys

grep -i "^encryption:" security.txt | cut -d' ' -f2-

### Download PGP Key (if available)

for url in $(grep -i "^encryption:" security.txt | grep -i "pgp\|key" | cut -d' ' -f2-); do
    curl -s $url > pgp-key.asc
    gpg --import pgp-key.asc 2>/dev/null
done

### Validate security.txt Compliance

# Check required fields
if grep -qi "^contact:" security.txt; then
    echo "[+] Has Contact field"
else
    echo "[-] Missing Contact field"
fi

# Check for multiple contacts
grep -c "^contact:" security.txt

# Check for HTTPS
grep "^contact:" security.txt | grep -q "https://" && echo "[+] HTTPS contact found"

---

## Phase 4: OpenID Connect Enumeration

### Fetch Configuration

curl -s https://target.com/.well-known/openid-configuration | jq . > openid-config.json

### Extract All Endpoints

jq -r 'to_entries | .[] | select(.value | startswith("http")) | "\(.key): \(.value)"' openid-config.json

### Check JWKS URI

JWKS_URI=$(jq -r '.jwks_uri' openid-config.json)
curl -s $JWKS_URI | jq .

### Extract Supported Flows

jq -r '.response_types_supported[]' openid-config.json
jq -r '.grant_types_supported[]?' openid-config.json
jq -r '.scopes_supported[]' openid-config.json

### Test Authorization Endpoint

AUTH_ENDPOINT=$(jq -r '.authorization_endpoint' openid-config.json)
curl -s -I "$AUTH_ENDPOINT?response_type=code&client_id=test&redirect_uri=https://example.com/callback&scope=openid"

### Check for Weak Algorithms

jq -r '.id_token_signing_alg_values_supported[]' openid-config.json | grep -E "none|HS256|RS256"

---

## Phase 5: MTA-STS and Email Security

### MTA-STS Policy

curl -s https://target.com/.well-known/mta-sts.txt

Example policy:
version: STSv1
mode: enforce
mx: mail.target.com
mx: backup.target.com
max_age: 86400

### Parse MTA-STS

# Extract MX records
grep "^mx:" mta-sts.txt | cut -d' ' -f2-

# Check mode (enforce/testing/none)
grep "^mode:" mta-sts.txt

### Auto-discover Email Configuration

# Check standard email security files
curl -s https://target.com/.well-known/autoconfig/mail/config-v1.1.xml
curl -s https://target.com/.well-known/autodiscover/autodiscover.xml

---

## Phase 6: Asset Verification

### assetlinks.json (Digital Asset Links)

curl -s https://target.com/.well-known/assetlinks.json | jq .

Example:
[
  {
    "relation": ["delegate_permission/common.handle_all_urls"],
    "target": {
      "namespace": "android_app",
      "package_name": "com.example.app",
      "sha256_cert_fingerprints": ["14:6D:E9:83..."]
    }
  }
]

### Parse Asset Links

# Extract package names
jq -r '.[].target.package_name' assetlinks.json 2>/dev/null

# Extract certificate fingerprints
jq -r '.[].target.sha256_cert_fingerprints[]' assetlinks.json 2>/dev/null

### apple-app-site-association

curl -s https://target.com/.well-known/apple-app-site-association | jq .

### keybase.txt

curl -s https://target.com/.well-known/keybase.txt

---

## Phase 7: Automation

### Complete .well-known Scanner

Save as wellknown-scanner.sh:

#!/bin/bash
TARGET=$1
OUTPUT_DIR="wellknown-$TARGET"
mkdir -p $OUTPUT_DIR

echo "[*] Starting .well-known scan for $TARGET"

# Common URIs to check
URIS=(
    "security.txt"
    "openid-configuration"
    "change-password"
    "assetlinks.json"
    "mta-sts.txt"
    "keybase.txt"
    "apple-app-site-association"
    "autoconfig/mail/config-v1.1.xml"
    "autodiscover/autodiscover.xml"
    "acme-challenge/"
    "pki-validation/"
    "saml-metadata.xml"
    "webfinger"
    "nodeinfo"
    "host-meta"
    "host-meta.json"
)

for uri in "${URIS[@]}"; do
    url="https://$TARGET/.well-known/$uri"
    echo "[*] Checking $url"
    
    status=$(curl -s -o /dev/null -w "%{http_code}" $url)
    
    if [ $status -eq 200 ]; then
        echo "[+] FOUND: $url"
        curl -s $url > "$OUTPUT_DIR/$uri" &
        
        # Special handling based on URI
        case $uri in
            security.txt)
                echo "    Contact: $(grep -i "^contact:" "$OUTPUT_DIR/$uri" | head -1)"
                ;;
            openid-configuration)
                jq -r '.issuer' "$OUTPUT_DIR/$uri" 2>/dev/null | xargs -I {} echo "    Issuer: {}"
                ;;
            assetlinks.json)
                jq -r '.[].target.package_name' "$OUTPUT_DIR/$uri" 2>/dev/null | xargs -I {} echo "    Android app: {}"
                ;;
        esac
    elif [ $status -eq 301 ] || [ $status -eq 302 ]; then
        redirect=$(curl -s -o /dev/null -w "%{redirect_url}" $url)
        echo "[→] REDIRECT: $url -> $redirect"
    elif [ $status -eq 401 ] || [ $status -eq 403 ]; then
        echo "[!] AUTH REQUIRED: $url"
    else
        echo "[-] Not found: $url"
    fi
    
    echo ""
    sleep 0.5
done

echo "[*] Scan complete. Results in $OUTPUT_DIR/"

### Bulk Domain Scanner

Save as bulk-wellknown.sh:

#!/bin/bash
DOMAIN_LIST=$1
OUTPUT_DIR="bulk-wellknown"
mkdir -p $OUTPUT_DIR
SUMMARY="$OUTPUT_DIR/summary.csv"

echo "Domain,URI,Status,Size" > $SUMMARY

while read domain; do
    echo "[*] Scanning $domain"
    
    for uri in security.txt openid-configuration assetlinks.json; do
        url="https://$domain/.well-known/$uri"
        status=$(curl -s -o /dev/null -w "%{http_code}" $url)
        size=$(curl -s $url | wc -c)
        
        echo "$domain,$uri,$status,$size" >> $SUMMARY
        
        if [ $status -eq 200 ]; then
            mkdir -p "$OUTPUT_DIR/$domain"
            curl -s $url > "$OUTPUT_DIR/$domain/$uri"
        fi
    done
    
    sleep 1
done < $DOMAIN_LIST

echo "[*] Bulk scan complete. Results in $OUTPUT_DIR/"

---

## .well-known Attack Surface Summary

| URI | Information Leaked | Attack Potential |
|-----|-------------------|------------------|
| security.txt | Contacts, PGP keys | Phishing targets, key attacks |
| openid-configuration | Auth endpoints, keys | OAuth abuse, crypto attacks |
| mta-sts.txt | Mail servers | Email recon, MX targeting |
| assetlinks.json | App associations | Mobile app attacks |
| change-password | Password reset page | Password reset abuse |
| keybase.txt | Identity proofs | OSINT, identity verification |

---

## Key Takeaways

- The .well-known directory is a standardized metadata location
- IANA maintains the full registry of URIs
- security.txt reveals vulnerability disclosure contacts
- openid-configuration exposes authentication infrastructure
- MTA-STS policies reveal email server configurations
- assetlinks.json shows app-domain associations
- Always check the full IANA registry for new URIs
- Automate scanning for comprehensive coverage
- Parse JSON responses with jq for structured data
- Combine with subdomain enumeration
- Document all discovered endpoints
- This is passive recon - no detection risk
- The standardized nature makes it predictable and valuable
