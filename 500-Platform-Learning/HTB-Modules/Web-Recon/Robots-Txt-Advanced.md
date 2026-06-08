---
tags: [module/web-recon, robots.txt, web-crawling, information-disclosure, automation, level/advanced, practical]
---

# robots.txt - Practical Application

## Complete robots.txt Analysis Workflow

Phase 1: Discovery
Phase 2: Parsing and Extraction
Phase 3: Path Validation
Phase 4: Sitemap Analysis
Phase 5: Automation
Phase 6: Integration

---

## Phase 1: Discovery

### Basic Fetch

curl -s https://target.com/robots.txt
curl -s http://target.com/robots.txt

### Check Common Variations

for proto in http https; do
    for domain in target.com www.target.com; do
        url="$proto://$domain/robots.txt"
        echo "[*] Checking $url"
        curl -s -o /dev/null -w "%{http_code}" $url
    done
done

### Case Sensitivity Check

curl -s https://target.com/robots.txt
curl -s https://target.com/Robots.txt
curl -s https://target.com/ROBOTS.TXT

---

## Phase 2: Parsing and Extraction

### Extract All Directives

curl -s https://target.com/robots.txt | grep -v "^#" | grep -v "^$"

### Extract Disallow Paths

curl -s https://target.com/robots.txt | grep -i "disallow:" | sed 's/Disallow: //i' | sed 's/ //g' | grep -v "^$"

### Extract Allow Paths

curl -s https://target.com/robots.txt | grep -i "allow:" | sed 's/Allow: //i' | sed 's/ //g' | grep -v "^$"

### Extract Sitemap URLs

curl -s https://target.com/robots.txt | grep -i "sitemap:" | sed 's/Sitemap: //i' | sed 's/ //g'

### Extract Crawl-Delay Values

curl -s https://target.com/robots.txt | grep -i "crawl-delay:" | sed 's/Crawl-delay: //i'

### Parse by User-Agent

# Rules for all bots
curl -s https://target.com/robots.txt | awk '/User-agent: \*/,/^$/'

# Rules for Googlebot
curl -s https://target.com/robots.txt | awk '/User-agent: Googlebot/,/^$/'

---

## Phase 3: Path Validation

### Check If Disallowed Paths Are Accessible

\#!/bin/bash
TARGET="target.com"
PATHS=$(curl -s https://$TARGET/robots.txt | grep -i "disallow:" | sed 's/Disallow: //i' | sed 's/ //g')

echo "=== robots.txt Path Analysis for $TARGET ==="
echo ""

for path in $PATHS; do
    # Handle relative paths
    if [[ $path == /* ]]; then
        url="https://$TARGET$path"
    else
        url="https://$TARGET/$path"
    fi
    
    status=$(curl -s -o /dev/null -w "%{http_code}" $url)
    size=$(curl -s $url | wc -c)
    
    echo "[$status] $url ($size bytes)"
    
    # If it returns 200, save it for further analysis
    if [ $status -eq 200 ]; then
        echo "$url" >> accessible-paths.txt
    fi
done

### Check for Directory Listing

for path in $PATHS; do
    url="https://$TARGET$path"
    curl -s $url | grep -i "index of" && echo "[!] Directory listing: $url"
done

### Check for Sensitive Files

curl -s https://target.com/backup.zip -o /dev/null -w "%{http_code}"
curl -s https://target.com/.env -o /dev/null -w "%{http_code}"
curl -s https://target.com/.git/HEAD -o /dev/null -w "%{http_code}"

---

## Phase 4: Sitemap Analysis

### Fetch Sitemap

SITEMAP=$(curl -s https://target.com/robots.txt | grep -i "sitemap:" | sed 's/Sitemap: //i' | head -1)
curl -s $SITEMAP

### Parse XML Sitemap

curl -s $SITEMAP | grep -oP '<loc>\K[^<]+' > sitemap-urls.txt

### Check for Multiple Sitemaps

curl -s $SITEMAP | grep -oP '<sitemap>\s*<loc>\K[^<]+' > sitemap-index.txt

### Extract All URLs from Sitemap

for sitemap in $(cat sitemap-index.txt); do
    curl -s $sitemap | grep -oP '<loc>\K[^<]+' >> all-urls.txt
done

wc -l all-urls.txt

---

## Phase 5: Automation

### Complete robots.txt Scanner

Save as robots-scanner.sh:

\#!/bin/bash
TARGET=$1
OUTPUT_DIR="robots-$TARGET"
mkdir -p $OUTPUT_DIR

echo "[*] Starting robots.txt analysis for $TARGET"

# Fetch robots.txt
echo "[*] Fetching robots.txt..."
curl -s https://$TARGET/robots.txt > $OUTPUT_DIR/robots.txt
curl -s http://$TARGET/robots.txt >> $OUTPUT_DIR/robots.txt 2>/dev/null

# Extract components
echo "[*] Extracting directives..."
grep -i "disallow:" $OUTPUT_DIR/robots.txt | sed 's/Disallow: //i' | sed 's/ //g' | grep -v "^$" > $OUTPUT_DIR/disallow.txt
grep -i "allow:" $OUTPUT_DIR/robots.txt | sed 's/Allow: //i' | sed 's/ //g' | grep -v "^$" > $OUTPUT_DIR/allow.txt
grep -i "sitemap:" $OUTPUT_DIR/robots.txt | sed 's/Sitemap: //i' | sed 's/ //g' > $OUTPUT_DIR/sitemap.txt

echo "[*] Disallowed paths: $(wc -l < $OUTPUT_DIR/disallow.txt)"
echo "[*] Allowed paths: $(wc -l < $OUTPUT_DIR/allow.txt)"
echo "[*] Sitemaps: $(wc -l < $OUTPUT_DIR/sitemap.txt)"

# Validate paths
echo "[*] Validating disallowed paths..."
while read path; do
    if [[ $path == /* ]]; then
        url="https://$TARGET$path"
    else
        url="https://$TARGET/$path"
    fi
    
    status=$(curl -s -o /dev/null -w "%{http_code}" $url)
    size=$(curl -s $url | wc -c)
    
    echo "$status $url" >> $OUTPUT_DIR/path-status.txt
    
    if [ $status -eq 200 ]; then
        echo "[!] Accessible: $url" >> $OUTPUT_DIR/accessible.txt
    fi
done < $OUTPUT_DIR/disallow.txt

# Process sitemaps
if [ -s $OUTPUT_DIR/sitemap.txt ]; then
    echo "[*] Processing sitemaps..."
    while read sitemap; do
        curl -s $sitemap | grep -oP '<loc>\K[^<]+' >> $OUTPUT_DIR/sitemap-urls.txt
    done < $OUTPUT_DIR/sitemap.txt
    echo "[*] Found $(wc -l < $OUTPUT_DIR/sitemap-urls.txt) URLs in sitemaps"
fi

# Generate report
echo "" > $OUTPUT_DIR/report.txt
echo "=== robots.txt Analysis Report for $TARGET ===" >> $OUTPUT_DIR/report.txt
echo "Date: $(date)" >> $OUTPUT_DIR/report.txt
echo "" >> $OUTPUT_DIR/report.txt
echo "Disallowed paths: $(wc -l < $OUTPUT_DIR/disallow.txt)" >> $OUTPUT_DIR/report.txt
echo "Allowed paths: $(wc -l < $OUTPUT_DIR/allow.txt)" >> $OUTPUT_DIR/report.txt
echo "Sitemaps found: $(wc -l < $OUTPUT_DIR/sitemap.txt)" >> $OUTPUT_DIR/report.txt
echo "" >> $OUTPUT_DIR/report.txt

if [ -f $OUTPUT_DIR/accessible.txt ]; then
    echo "ACCESSIBLE DISALLOWED PATHS:" >> $OUTPUT_DIR/report.txt
    cat $OUTPUT_DIR/accessible.txt >> $OUTPUT_DIR/report.txt
fi

echo "[*] Analysis complete. Results in $OUTPUT_DIR/"

### Bulk Domain robots.txt Checker

Save as bulk-robots.sh:

\#!/bin/bash
DOMAIN_LIST=$1
OUTPUT_DIR="bulk-robots"
mkdir -p $OUTPUT_DIR

while read domain; do
    echo "[*] Checking $domain"
    
    mkdir -p "$OUTPUT_DIR/$domain"
    
    curl -s "https://$domain/robots.txt" > "$OUTPUT_DIR/$domain/https.txt"
    curl -s "http://$domain/robots.txt" > "$OUTPUT_DIR/$domain/http.txt"
    
    for proto in http https; do
        file="$OUTPUT_DIR/$domain/$proto.txt"
        if [ -s $file ]; then
            paths=$(grep -i "disallow:" $file | wc -l)
            sitemaps=$(grep -i "sitemap:" $file | wc -l)
            echo "$domain,$proto,$paths,$sitemaps" >> $OUTPUT_DIR/summary.csv
        fi
    done
    
    sleep 1
done < $DOMAIN_LIST

echo "[*] Bulk scan complete. Results in $OUTPUT_DIR/"

---

## robots.txt Security Testing

### Test for Information Disclosure

Check if disallowed paths are actually accessible:
- Many sites block crawlers but not humans
- If you can access /admin/, that's a finding
- Test each disallowed path manually

### Check for Backup Files

Common backup locations:
/backup.zip
/backup.tar.gz
/backup.sql
/db.sql
/database.sql
/.env.backup
/config.php.bak

### Check for Development Artifacts

/.git/
/.svn/
/.hg/
/dev/
/test/
/staging/
/uat/

---

## robots.txt Cheatsheet

| Goal | Command |
|------|---------|
| Fetch robots.txt | curl -s https://target.com/robots.txt |
| Extract disallow | curl -s URL | grep -i "disallow" |
| Extract allow | curl -s URL | grep -i "allow" |
| Extract sitemap | curl -s URL | grep -i "sitemap" |
| Check path access | curl -s -o /dev/null -w "%{http_code}" https://target.com/admin |
| Find directory listing | curl -s https://target.com/admin/ | grep -i "index of" |
| Parse XML sitemap | curl -s SITEMAP_URL | grep -oP '<loc>\K[^<]+' |
| Check all paths | for p in $(cat paths.txt); do curl -s -I https://target.com$p; done |

---

## Common robots.txt Patterns

### WordPress
User-agent: *
Disallow: /wp-admin/
Disallow: /wp-includes/
Disallow: /wp-content/plugins/

### Generic CMS
User-agent: *
Disallow: /admin/
Disallow: /includes/
Disallow: /cache/
Disallow: /tmp/

### Development Site
User-agent: *
Disallow: /
This means: "Don't crawl anything" - often means it's a dev site

### Empty or Missing robots.txt
- No file = no instructions
- Could mean nothing to hide, or nothing to protect
- Still worth fuzzing for common paths

---

## Key Takeaways

- robots.txt is ALWAYS worth checking
- Disallowed paths are often interesting
- Many sites forget to ACTUALLY block access to disallowed paths
- Sitemaps reveal complete site structure
- Parse and validate every discovered path
- Combine with directory brute-forcing
- Check for backup files and .git
- Document all accessible disallowed paths
- Use automation for large targets
- This is passive recon - no detection risk
- The irony: the hiding file reveals everything
