---
tags: [module/web-recon, web-archives, wayback-machine, internet-archive, wayback-cdx, automation, level/advanced, practical]
---

# Web Archives - Practical Application

## Complete Web Archive Analysis Workflow

Phase 1: Wayback Machine Web Interface
Phase 2: Wayback CDX API
Phase 3: URL Discovery
Phase 4: Historical File Extraction
Phase 5: Diff Analysis
Phase 6: Automation
Phase 7: Alternative Archives

---

## Phase 1: Wayback Machine Web Interface

### Basic Navigation

1. Go to https://archive.org/web/
2. Enter target URL
3. Explore timeline

### Timeline Features

- Calendar view shows capture frequency
- Top dots represent years
- Timeline at bottom shows distribution
- Yellow highlights = redirects

### Advanced Web Interface Tips

Use "Save Page Now" to capture current page
Use "Changes" to see differences between captures
Use "Summary" to see all captures at a glance
Use "Site Map" to see discovered URLs

---

## Phase 2: Wayback CDX API

The CDX API allows programmatic access to the Wayback Machine's index.

### Basic CDX Query

curl -s "http://web.archive.org/cdx/search/cdx?url=example.com&output=json"

### Common CDX Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| url | Target URL | url=example.com |
| matchType | Domain matching | matchType=domain |
| limit | Max results | limit=1000 |
| output | Output format | output=json |
| from | Start date | from=20200101 |
| to | End date | to=20201231 |
| filter | Filter results | filter=statuscode:200 |

### CDX Query Examples

# Get all captures as JSON
curl -s "http://web.archive.org/cdx/search/cdx?url=example.com&output=json"

# Get only successful captures
curl -s "http://web.archive.org/cdx/search/cdx?url=example.com&filter=statuscode:200&output=json"

# Get captures from specific date range
curl -s "http://web.archive.org/cdx/search/cdx?url=example.com&from=20200101&to=20201231&output=json"

# Get all subdomains
curl -s "http://web.archive.org/cdx/search/cdx?url=*.example.com&output=json&fl=original&collapse=urlkey"

# Get only specific file types
curl -s "http://web.archive.org/cdx/search/cdx?url=example.com&filter=original:.*\.pdf&output=json"

### CDX Output Fields

{
  "urlkey": "com,example)/",
  "timestamp": "20210101120000",
  "original": "https://example.com/",
  "mimetype": "text/html",
  "statuscode": "200",
  "digest": "ABCD1234...",
  "length": "12345"
}

---

## Phase 3: URL Discovery

### Extract All URLs

curl -s "http://web.archive.org/cdx/search/cdx?url=example.com&output=json&fl=original&collapse=urlkey" | jq -r '.[] | select(length > 0) | .[0]' | sort -u > all-urls.txt

### Extract Subdomains

curl -s "http://web.archive.org/cdx/search/cdx?url=*.example.com&output=json&fl=original&collapse=urlkey" | jq -r '.[] | select(length > 0) | .[0]' | sed -E 's|https?://||' | cut -d'/' -f1 | sort -u > subdomains.txt

### Extract Paths

curl -s "http://web.archive.org/cdx/search/cdx?url=example.com&output=json&fl=original&collapse=urlkey" | jq -r '.[] | select(length > 0) | .[0]' | grep -oP 'https?://[^/]+\K.*' | sort -u > paths.txt

### Extract Parameters

curl -s "http://web.archive.org/cdx/search/cdx?url=example.com&output=json&fl=original&collapse=urlkey" | jq -r '.[] | select(length > 0) | .[0]' | grep -oP '\?[^#]+' | tr '?&' '\n' | grep '=' | cut -d'=' -f1 | sort -u > parameters.txt

---

## Phase 4: Historical File Extraction

### Find Specific File Types

# PDFs
curl -s "http://web.archive.org/cdx/search/cdx?url=example.com&filter=original:.*\.pdf&output=json&fl=original,timestamp" | jq -r '.[] | "https://web.archive.org/web/\(.[1])/\(.[0])"' > pdfs.txt

# SQL files
curl -s "http://web.archive.org/cdx/search/cdx?url=example.com&filter=original:.*\.sql&output=json&fl=original,timestamp" | jq -r '.[] | "https://web.archive.org/web/\(.[1])/\(.[0])"' > sql-files.txt

# Config files
curl -s "http://web.archive.org/cdx/search/cdx?url=example.com&filter=original:.*\.(conf|config|env|ini)&output=json&fl=original,timestamp" | jq -r '.[] | "https://web.archive.org/web/\(.[1])/\(.[0])"' > config-files.txt

# Backup files
curl -s "http://web.archive.org/cdx/search/cdx?url=example.com&filter=original:.*\.(bak|backup|old|orig)&output=json&fl=original,timestamp" | jq -r '.[] | "https://web.archive.org/web/\(.[1])/\(.[0])"' > backup-files.txt

### Download Historical Files

while read url; do
    wget -q "$url" -P downloaded-files/
    sleep 1
done < pdfs.txt

### Extract Emails from Historical Pages

for url in $(head -50 all-urls.txt); do
    archive_url="https://web.archive.org/web/20200101000000/$url"
    curl -s $archive_url | grep -oE '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}' >> historical-emails.txt
    sleep 1
done
sort -u historical-emails.txt > unique-historical-emails.txt

---

## Phase 5: Diff Analysis

### Compare Two Snapshots

# Get two timestamps
curl -s "http://web.archive.org/cdx/search/cdx?url=example.com&limit=2&output=json" | jq -r '.[1:][] | .[1]' | head -2

# View diff
https://web.archive.org/web/20200101000000/https://example.com
https://web.archive.org/web/20210101000000/https://example.com

# Use "Changes" feature on Wayback Machine
# Or use tools like wdiff, vimdiff

### Automated Diff Script

#!/bin/bash
URL=$1
TS1=$2
TS2=$3

curl -s "https://web.archive.org/web/$TS1/$URL" > version1.html
curl -s "https://web.archive.org/web/$TS2/$URL" > version2.html

diff -u version1.html version2.html > changes.diff
echo "Changes saved to changes.diff"

# Count changes
echo "Lines added: $(grep -c '^+' changes.diff)"
echo "Lines removed: $(grep -c '^-' changes.diff)"

### Track Technology Changes

# Check for technology indicators in old versions
for ts in 2015 2016 2017 2018 2019 2020 2021 2022 2023; do
    echo "=== $ts ==="
    curl -s "https://web.archive.org/web/${ts}0101000000/http://example.com/" | grep -i "generator\|powered-by\|server\|x-powered-by" | head -3
    echo ""
    sleep 2
done

---

## Phase 6: Automation

### Complete Wayback Scanner

Save as wayback-scan.sh:

#!/bin/bash
DOMAIN=$1
OUTPUT_DIR="wayback-$DOMAIN"
mkdir -p $OUTPUT_DIR

echo "[*] Starting Wayback Machine scan for $DOMAIN"

# Phase 1: Get all URLs
echo "[*] Fetching all URLs from CDX..."
curl -s "http://web.archive.org/cdx/search/cdx?url=$DOMAIN&output=json&fl=original,timestamp,mimetype,statuscode&collapse=urlkey" > $OUTPUT_DIR/raw.json

# Phase 2: Extract and categorize
echo "[*] Extracting URLs..."
jq -r '.[1:][] | .[0]' $OUTPUT_DIR/raw.json | sort -u > $OUTPUT_DIR/all-urls.txt

echo "[*] Found $(wc -l < $OUTPUT_DIR/all-urls.txt) unique URLs"

# Phase 3: Extract subdomains
echo "[*] Extracting subdomains..."
grep -oP 'https?://\K[^/]+' $OUTPUT_DIR/all-urls.txt | grep -v "^$DOMAIN$" | sort -u > $OUTPUT_DIR/subdomains.txt

# Phase 4: Extract file types
echo "[*] Categorizing by file type..."
grep "\.pdf" $OUTPUT_DIR/all-urls.txt > $OUTPUT_DIR/pdfs.txt
grep "\.sql" $OUTPUT_DIR/all-urls.txt > $OUTPUT_DIR/sql.txt
grep "\.\(conf\|config\|env\|ini\)" $OUTPUT_DIR/all-urls.txt > $OUTPUT_DIR/configs.txt
grep "\.\(bak\|backup\|old\|orig\)" $OUTPUT_DIR/all-urls.txt > $OUTPUT_DIR/backups.txt
grep "\.\(js\|css\)" $OUTPUT_DIR/all-urls.txt > $OUTPUT_DIR/assets.txt

# Phase 5: Extract timestamps for key pages
echo "[*] Getting timestamps for key pages..."
for path in admin login api backup config; do
    grep "/$path" $OUTPUT_DIR/all-urls.txt | head -10 > $OUTPUT_DIR/timestamps-$path.txt
done

# Phase 6: Generate report
echo "[*] Generating report..."
echo "=== Wayback Scan Report for $DOMAIN ===" > $OUTPUT_DIR/report.txt
echo "Date: $(date)" >> $OUTPUT_DIR/report.txt
echo "" >> $OUTPUT_DIR/report.txt
echo "Total unique URLs: $(wc -l < $OUTPUT_DIR/all-urls.txt)" >> $OUTPUT_DIR/report.txt
echo "Subdomains found: $(wc -l < $OUTPUT_DIR/subdomains.txt)" >> $OUTPUT_DIR/report.txt
echo "" >> $OUTPUT_DIR/report.txt
echo "Files by type:" >> $OUTPUT_DIR/report.txt
echo "  PDFs: $(wc -l < $OUTPUT_DIR/pdfs.txt)" >> $OUTPUT_DIR/report.txt
echo "  SQL: $(wc -l < $OUTPUT_DIR/sql.txt)" >> $OUTPUT_DIR/report.txt
echo "  Configs: $(wc -l < $OUTPUT_DIR/configs.txt)" >> $OUTPUT_DIR/report.txt
echo "  Backups: $(wc -l < $OUTPUT_DIR/backups.txt)" >> $OUTPUT_DIR/report.txt
echo "  Assets: $(wc -l < $OUTPUT_DIR/assets.txt)" >> $OUTPUT_DIR/report.txt

echo "[*] Scan complete! Results in $OUTPUT_DIR/"

### Bulk Wayback Scanner

Save as bulk-wayback.sh:

#!/bin/bash
DOMAIN_LIST=$1
OUTPUT_DIR="bulk-wayback"
mkdir -p $OUTPUT_DIR

while read domain; do
    echo "[*] Scanning $domain"
    
    curl -s "http://web.archive.org/cdx/search/cdx?url=$domain&output=json&fl=original&collapse=urlkey" | \
        jq -r '.[1:][] | .[0]' | sort -u > "$OUTPUT_DIR/$domain.txt"
    
    count=$(wc -l < "$OUTPUT_DIR/$domain.txt")
    echo "[+] Found $count URLs for $domain"
    
    sleep 2
done < $DOMAIN_LIST

echo "[*] Bulk scan complete. Results in $OUTPUT_DIR/"

---

## Phase 7: Alternative Archives

### Archive.today

https://archive.today/
Captures on-demand, not automated.

Query API:
curl -s "https://archive.today/timemap/?url=example.com"

### Google Cache

https://webcache.googleusercontent.com/search?q=cache:example.com

### Bing Cache

https://cc.bingj.com/cache.aspx?q=example.com&d=123456789

### Library of Congress

https://www.loc.gov/web-archives/

### UK Web Archive

https://www.webarchive.org.uk/

### Stanford Web Archive

https://swap.stanford.edu/

### Perma.cc

https://perma.cc/
Academic-focused, creates permanent records.

---

## Wayback Machine Cheatsheet

| Goal | Command |
|------|---------|
| Get all URLs | curl -s "http://web.archive.org/cdx/search/cdx?url=example.com&output=json&fl=original&collapse=urlkey" | jq -r '.[1:][] | .[0]' |
| Get timestamps | curl -s "http://web.archive.org/cdx/search/cdx?url=example.com&output=json&fl=timestamp" |
| Get by date range | curl -s "http://web.archive.org/cdx/search/cdx?url=example.com&from=20200101&to=20201231" |
| Get PDFs | curl -s "http://web.archive.org/cdx/search/cdx?url=example.com&filter=original:.*\.pdf" |
| Get subdomains | curl -s "http://web.archive.org/cdx/search/cdx?url=*.example.com&fl=original&collapse=urlkey" |
| View snapshot | https://web.archive.org/web/TIMESTAMP/https://example.com |
| Latest snapshot | https://web.archive.org/web/https://example.com |
| Save page | https://web.archive.org/save/https://example.com |

---

## Key Takeaways

- The Wayback Machine CDX API enables automated queries
- Extract all historical URLs for a domain
- Find old subdomains no longer in DNS
- Discover removed files (PDFs, SQL dumps, configs)
- Track technology changes over time
- Diff snapshots to see content changes
- Use multiple archives for coverage
- Archive.today is good for on-demand captures
- Google/Bing caches show recent versions
- Always check archives during recon
- Historical data often reveals what's hidden now
- This is 100% passive - no target contact
- What was once public may still be accessible
- Combine with other OSINT techniques
