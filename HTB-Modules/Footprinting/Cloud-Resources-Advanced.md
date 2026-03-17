---
tags: [module/footprinting, cloud, aws, azure, gcp, level/advanced, practical]
---

# Cloud Resources - Practical Application

## Complete Cloud Enumeration Workflow

Phase 1: DNS-Based Cloud Detection
Phase 2: Google Dorking for Cloud Assets
Phase 3: Source Code Analysis
Phase 4: Third-Party Tools (domain.glass)
Phase 5: GrayHatWarfare Deep Dive
Phase 6: Abbreviation and Permutation Brute Force
Phase 7: Leaked File Analysis

---

## Phase 1: DNS-Based Cloud Detection

### Automated Cloud Provider Detection

#!/bin/bash
DOMAIN=$1
echo "Checking DNS for cloud resources..."

dig any $DOMAIN | grep -E "amazonaws|blob.core.windows|storage.googleapis|cloudfront|azurewebsites" > cloud-dns.txt

if [ -s cloud-dns.txt ]; then
    echo "Found cloud resources:"
    cat cloud-dns.txt
else
    echo "No cloud resources found in DNS"
fi

### Cloud Provider DNS Patterns

| Provider | DNS Pattern | Service |
|----------|-------------|---------|
| AWS | s3-website[-region].amazonaws.com | S3 Static Website |
| AWS | cloudfront.net | CDN |
| AWS | elasticbeanstalk.com | Elastic Beanstalk |
| AWS | ec2.amazonaws.com | EC2 Instance |
| Azure | blob.core.windows.net | Blob Storage |
| Azure | azurewebsites.net | App Service |
| Azure | cloudapp.net | Cloud Service |
| GCP | storage.googleapis.com | Cloud Storage |
| GCP | appspot.com | App Engine |
| GCP | cloudfunctions.net | Cloud Functions |

---

## Phase 2: Google Dorking for Cloud Assets

### Advanced Google Dorks

AWS S3 Buckets:
site:s3.amazonaws.com "companyname"
site:amazonaws.com "companyname" ext:pdf
site:s3.amazonaws.com "companyname" intitle:index.of

Azure Blob Storage:
site:blob.core.windows.net "companyname"
site:blob.core.windows.net "companyname" ext:xlsx
site:blob.core.windows.net "companyname" ext:txt

Google Cloud Storage:
site:storage.googleapis.com "companyname"
site:storage.googleapis.com "companyname" ext:sql
site:storage.googleapis.com "companyname" ext:backup

### Automated Google Dork Script

Requires Google API key or manual use.

dorks=(
    "site:s3.amazonaws.com companyname"
    "site:blob.core.windows.net companyname"
    "site:storage.googleapis.com companyname"
    "site:amazonaws.com companyname ext:pdf"
    "site:blob.core.windows.net companyname ext:xlsx"
    "site:storage.googleapis.com companyname ext:sql"
)

for dork in "${dorks[@]}"; do
    echo "Searching: $dork"
    # Manual: open in browser
    echo "https://www.google.com/search?q=$dork"
done

---

## Phase 3: Source Code Analysis

### Extract Cloud URLs from HTML

curl -s https://target.com | grep -Eo '(http|https)://[^"]*\.(amazonaws|blob\.core\.windows|storage\.googleapis)[^"]*' | sort -u

### Find Preconnect/Hints

curl -s https://target.com | grep -i "preconnect\|preload\|dns-prefetch" | grep -E "amazonaws|blob|googleapis"

### Extract from JavaScript

curl -s https://target.com | grep -o '<script[^>]*src="[^"]*"' | grep -Eo 'http[^"]*' | grep -E "amazonaws|blob|googleapis"

---

## Phase 4: Third-Party Tools (domain.glass)

### domain.glass API (if available)

curl -s "https://domain.glass/api/v1/domain/companyname.com" | jq '.'

### Manual Information Extraction

Visit: https://domain.glass/companyname.com

Look for:
- Cloudflare status (Safe? Not safe?)
- SSL certificate DNS names (more subdomains)
- DNS records summary
- Social media links
- IP ranges
- Registrar info
- Nameservers (hosting provider)

---

## Phase 5: GrayHatWarfare Deep Dive

### Search URL Patterns

AWS: https://buckets.grayhatwarfare.com/results/aws/companyname
Azure: https://buckets.grayhatwarfare.com/results/azure/companyname
GCP: https://buckets.grayhatwarfare.com/results/gcp/companyname

### File Type Filtering

Add extensions to URL:
https://buckets.grayhatwarfare.com/results/aws/companyname/pdf
https://buckets.grayhatwarfare.com/results/aws/companyname/sql
https://buckets.grayhatwarfare.com/results/aws/companyname/key
https://buckets.grayhatwarfare.com/results/aws/companyname/pem
https://buckets.grayhatwarfare.com/results/aws/companyname/env

### Sensitive Files to Hunt

| Extension | File Type | What to Look For |
|-----------|-----------|------------------|
| .key, .pem | Private Keys | SSH, SSL private keys |
| .pub | Public Keys | SSH public keys |
| .env | Environment | Database passwords, API keys |
| .sql | Database Dump | All data, user creds |
| .bak, .backup | Backups | Configuration, data |
| .conf, .config | Config Files | Service credentials |
| .log | Log Files | User data, errors |
| .git | Git Repo | Source code, history |

---

## Phase 6: Abbreviation and Permutation Brute Force

### Generate Company Abbreviations

#!/bin/bash
COMPANY="InlaneFreight"

# Common patterns
echo $COMPANY | tr '[:upper:]' '[:lower:]'
echo $COMPANY | cut -c1-3 | tr '[:upper:]' '[:lower:]'
echo $COMPANY | grep -o '^[A-Z]' | tr -d '\n' | tr '[:upper:]' '[:lower:]'
echo $COMPANY | sed 's/.*/\L&/; s/ .*//'
echo $COMPANY | sed 's/.*/\L&/; s/ //g'

# Manual list to try
ilf
inlane
freight
ilf-prod
ilf-dev
ilf-staging
ilf-backup
inlane-data
freight-storage
ilf-assets

### AWS Bucket Name Patterns

{bucket-name}.s3.amazonaws.com
s3.amazonaws.com/{bucket-name}
{bucket-name}.s3-website-{region}.amazonaws.com

### Azure Blob Patterns

{bucket-name}.blob.core.windows.net
{bucket-name}.blob.core.windows.net/{container}
{bucket-name}.azurewebsites.net

### GCP Patterns

{bucket-name}.storage.googleapis.com
storage.googleapis.com/{bucket-name}

---

## Phase 7: Leaked File Analysis

### SSH Private Key Detection

When you find id_rsa files:

1. Download the file
2. Check permissions:
   chmod 600 id_rsa
3. Try to use:
   ssh -i id_rsa root@target.com
   ssh -i id_rsa user@target.com
   ssh -i id_rsa ec2-user@target.com
   ssh -i id_rsa ubuntu@target.com

4. Extract public key from private (if only private found):
   ssh-keygen -y -f id_rsa > id_rsa.pub

### AWS Credentials Detection

Files to look for:
.aws/credentials
credentials.txt
aws-keys.txt
config.json with "aws_access_key_id"

Format:
[default]
aws_access_key_id = AKIA...
aws_secret_access_key = ...

Once found:
aws configure set aws_access_key_id AKIA...
aws configure set aws_secret_access_key ...
aws s3 ls

### Environment File Analysis

.env files often contain:
DB_PASSWORD=
API_KEY=
SECRET_KEY=
AWS_ACCESS_KEY_ID=
AZURE_STORAGE_CONNECTION_STRING=

### Database Backup Analysis

.sql files may contain:
INSERT INTO users VALUES ('admin', 'hash')
user credentials
customer data
financial information

---

## Real-World Example: SSH Key Leak

From the module example, a GrayHatWarfare search revealed:

id_rsa
id_rsa.pub

### Impact Assessment

1. id_rsa is a private SSH key
2. Anyone can download it
3. The .pub file reveals the username
4. Attacker can log into any server where that key is authorized

### Exploitation Steps

wget http://leaked-bucket.s3.amazonaws.com/id_rsa
chmod 600 id_rsa
ssh -i id_rsa user@target.com

No password required. Full access granted.

---

## Complete Automation Script

Save as cloud-enum.sh:

#!/bin/bash
DOMAIN=$1
COMPANY=$2
OUTPUT_DIR="cloud-enum-$DOMAIN"
mkdir -p $OUTPUT_DIR

echo "[*] Starting cloud enumeration for $DOMAIN"

echo "[*] Checking DNS for cloud resources..."
dig any $DOMAIN | grep -E "amazonaws|blob.core.windows|storage.googleapis|cloudfront|azurewebsites" > $OUTPUT_DIR/dns-cloud.txt

echo "[*] Checking source code for cloud URLs..."
curl -s https://$DOMAIN | grep -Eo '(http|https)://[^"]*\.(amazonaws|blob\.core\.windows|storage\.googleapis)[^"]*' | sort -u > $OUTPUT_DIR/source-cloud.txt

echo "[*] Generating abbreviation list..."
echo $COMPANY | tr '[:upper:]' '[:lower:]' > $OUTPUT_DIR/abbreviations.txt
echo $COMPANY | cut -c1-3 | tr '[:upper:]' '[:lower:]' >> $OUTPUT_DIR/abbreviations.txt
echo $COMPANY | grep -o '^[A-Z]' | tr -d '\n' | tr '[:upper:]' '[:lower:]' >> $OUTPUT_DIR/abbreviations.txt

echo "[*] Checking GrayHatWarfare manually:"
echo "Visit: https://buckets.grayhatwarfare.com/results/aws/$COMPANY"
echo "Visit: https://buckets.grayhatwarfare.com/results/azure/$COMPANY"
echo "Visit: https://buckets.grayhatwarfare.com/results/gcp/$COMPANY"

echo "[*] Google Dorks to try manually:"
echo "site:s3.amazonaws.com $COMPANY"
echo "site:blob.core.windows.net $COMPANY"
echo "site:storage.googleapis.com $COMPANY"
echo "site:amazonaws.com $COMPANY ext:pdf"
echo "site:blob.core.windows.net $COMPANY ext:xlsx"

echo "[*] Cloud enumeration complete. Results in $OUTPUT_DIR/"

---

## Key Takeaways

- DNS records reveal cloud provider usage
- Google dorks find exposed cloud storage
- Source code contains cloud asset URLs
- domain.glass provides passive security assessment
- GrayHatWarfare is the best tool for finding buckets
- Company abbreviations help find hidden resources
- SSH keys in public buckets = instant access
- .env files contain credentials
- Database backups expose all data
- Document everything for later testing
- Cloud misconfigurations are common and critical

---

## Quick Reference Card

DNS CHECK:
    dig any target.com | grep -E "amazonaws|blob.core.windows|storage.googleapis"

SOURCE CODE:
    curl -s https://target.com | grep -Eo 'https?://[^"]*\.(amazonaws|blob\.core\.windows|storage\.googleapis)[^"]*'

GOOGLE DORKS:
    site:s3.amazonaws.com companyname
    site:blob.core.windows.net companyname
    site:storage.googleapis.com companyname
    site:amazonaws.com companyname ext:pdf

GRAYHATWARFARE:
    https://buckets.grayhatwarfare.com/results/aws/companyname
    https://buckets.grayhatwarfare.com/results/azure/companyname
    https://buckets.grayhatwarfare.com/results/gcp/companyname

DOMAIN.GLASS:
    https://domain.glass/companyname.com

SENSITIVE FILES TO HUNT:
    id_rsa, id_rsa.pub, .env, .aws/credentials, *.sql, *.bak, *.key, *.pem
