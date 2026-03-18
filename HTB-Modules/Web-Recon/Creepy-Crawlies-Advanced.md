---
tags: [module/web-recon, crawling, spidering, scrapy, burp, zap, automation, level/advanced, practical]
---

# Creepy Crawlies - Practical Application

## Complete Crawling Workflow

Phase 1: Tool Selection
Phase 2: Scrapy Custom Spiders
Phase 3: ReconSpider Deep Dive
Phase 4: Burp/ZAP Integration
Phase 5: Data Extraction & Analysis
Phase 6: Automation
Phase 7: Ethical Considerations

---

## Phase 1: Tool Selection

### Tool Comparison Matrix

| Tool | Speed | Depth | JS Support | Customization | Learning Curve |
|------|-------|-------|------------|---------------|----------------|
| Burp Spider | Medium | High | Yes | Low | Easy |
| ZAP Spider | Medium | High | Yes (AJAX) | Medium | Easy |
| Scrapy | High | Custom | With Splash | Very High | Steep |
| Gospider | Very High | Medium | Limited | Low | Easy |
| Katana | Very High | High | Yes | Medium | Easy |
| Nutch | Medium | Very High | No | High | Very Steep |
| HTTrack | Slow | Complete | No | Low | Easy |

---

## Phase 2: Scrapy Custom Spiders

### Installing Scrapy

pip3 install scrapy

### Project Structure

scrapy startproject recon_project
cd recon_project

### Basic Recon Spider

Save as recon_spider.py:

import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import re

class ReconSpider(CrawlSpider):
    name = 'recon_spider'
    
    def __init__(self, domain=None, *args, **kwargs):
        super(ReconSpider, self).__init__(*args, **kwargs)
        self.domain = domain
        self.start_urls = [f'https://{domain}']
        self.allowed_domains = [domain]
        self.data = {
            'emails': set(),
            'links': set(),
            'external_files': set(),
            'js_files': set(),
            'forms': [],
            'comments': [],
            'images': set()
        }
    
    rules = (
        Rule(LinkExtractor(), callback='parse_item', follow=True),
    )
    
    def parse_item(self, response):
        # Extract emails
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', response.text)
        self.data['emails'].update(emails)
        
        # Extract comments
        comments = response.xpath('//comment()').extract()
        self.data['comments'].extend(comments)
        
        # Extract JS files
        js_files = response.css('script::attr(src)').getall()
        self.data['js_files'].update([response.urljoin(js) for js in js_files])
        
        # Extract images
        images = response.css('img::attr(src)').getall()
        self.data['images'].update([response.urljoin(img) for img in images])
        
        # Extract forms
        forms = response.css('form')
        for form in forms:
            form_data = {
                'action': form.css('::attr(action)').get(),
                'method': form.css('::attr(method)').get(),
                'inputs': form.css('input::attr(name)').getall()
            }
            self.data['forms'].append(form_data)
        
        # Extract external files (PDF, DOC, XLS, etc.)
        file_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.zip', '.tar.gz']
        for ext in file_extensions:
            files = response.css(f'a[href$="{ext}"]::attr(href)').getall()
            self.data['external_files'].update([response.urljoin(f) for f in files])
        
        yield {
            'url': response.url,
            'data': {k: list(v) if isinstance(v, set) else v for k, v in self.data.items()}
        }

### Running the Spider

scrapy crawl recon_spider -a domain=target.com -o output.json

### Using Splash for JavaScript Sites

Install Splash:
docker run -p 8050:8050 scrapinghub/splash

Modified spider with Splash:

import scrapy
from scrapy_splash import SplashRequest

class SplashSpider(scrapy.Spider):
    name = 'splash_spider'
    
    def start_requests(self):
        yield SplashRequest(
            url=f'https://{self.domain}',
            callback=self.parse,
            args={'wait': 2}
        )
    
    def parse(self, response):
        # Now JavaScript-rendered content is available
        pass

---

## Phase 3: ReconSpider Deep Dive

### Download and Extract

wget -O ReconSpider.zip https://academy.hackthebox.com/storage/modules/144/ReconSpider.v1.2.zip
unzip ReconSpider.zip
cd ReconSpider

### Running ReconSpider

python3 ReconSpider.py http://inlanefreight.com

### Understanding the Code

View the spider code:
cat ReconSpider.py

Key components:
- Email extraction using regex
- Link extraction using CSS selectors
- File type filtering
- Comment extraction
- Form field detection

### Parsing Results.json

Using jq to analyze results:

# Extract all emails
jq '.emails[]' results.json

# Count links by domain
jq '.links[]' results.json | cut -d'/' -f3 | sort | uniq -c

# Find all PDF files
jq '.external_files[] | select(contains(".pdf"))' results.json

# Extract all HTML comments
jq '.comments[]' results.json

# Find forms with password fields
jq '.form_fields[] | select(contains("password"))' results.json

### Customizing ReconSpider

Add new file types to extract:

Edit the spider to add:
file_extensions = [
    '.pdf', '.doc', '.docx', '.xls', '.xlsx',
    '.ppt', '.pptx', '.txt', '.csv', '.sql',
    '.bak', '.backup', '.old', '.orig', '.conf',
    '.config', '.env', '.yml', '.yaml', '.json',
    '.xml', '.wsdl', '.wadl', '.raml', '.swagger'
]

---

## Phase 4: Burp/ZAP Integration

### Burp Suite API

Start Burp with API:
java -jar burpsuite.jar --api-enabled --api-port=8081

Python script to control Burp:

import requests
import json

# Start scan
scan_data = {
    "urls": ["https://target.com"],
    "scope": ["target.com"]
}
response = requests.post(
    "http://localhost:8081/v0.1/scan",
    json=scan_data,
    headers={"Content-Type": "application/json"}
)

# Get results
scan_id = response.json()['scan_id']
results = requests.get(f"http://localhost:8081/v0.1/scan/{scan_id}")

### ZAP API

from zapv2 import ZAPv2

zap = ZAPv2(apikey='your-api-key', proxies={'http': 'http://127.0.0.1:8080'})

# Spider
zap.spider.scan('https://target.com')
while int(zap.spider.status()) < 100:
    time.sleep(1)

# Get results
print(zap.spider.results())

---

## Phase 5: Data Extraction & Analysis

### Email Extraction and Analysis

cat results.json | jq -r '.emails[]' | sort -u > emails.txt

# Extract domains from emails
cat emails.txt | cut -d'@' -f2 | sort -u > email-domains.txt

# Check for pattern (first.last@company.com)
cat emails.txt | grep -E '^[a-z]+\.[a-z]+@' > name-format.txt

### Link Analysis

# Extract all links
jq -r '.links[]' results.json > all-links.txt

# Find admin panels
grep -i "admin\|dashboard\|portal" all-links.txt > admin-panels.txt

# Find login pages
grep -i "login\|signin\|auth" all-links.txt > login-pages.txt

# Find development areas
grep -i "dev\|test\|stage\|uat" all-links.txt > dev-areas.txt

### JavaScript Analysis

# Download all JS files
for js in $(jq -r '.js_files[]' results.json); do
    wget $js -P js-files/
done

# Search for API endpoints
grep -r "api\|endpoint\|graphql" js-files/

# Search for hardcoded credentials
grep -r "password\|secret\|token\|key" js-files/

### Comment Analysis

jq -r '.comments[]' results.json | grep -i "todo\|fixme\|hack\|xxx\|note" > interesting-comments.txt

# Extract potential paths from comments
jq -r '.comments[]' results.json | grep -oP '"/[a-zA-Z0-9_/-]+"' | tr -d '"' > comment-paths.txt

---

## Phase 6: Automation

### Complete Automation Script

Save as auto-crawl.sh:

#!/bin/bash
TARGET=$1
OUTPUT_DIR="crawl-results-$TARGET"
mkdir -p $OUTPUT_DIR

echo "[*] Starting automated crawl for $TARGET"

# Phase 1: ReconSpider
echo "[*] Running ReconSpider..."
python3 ReconSpider.py https://$TARGET
mv results.json $OUTPUT_DIR/reconspider.json

# Phase 2: Katana crawl
echo "[*] Running Katana..."
katana -u https://$TARGET -d 3 -jc -o $OUTPUT_DIR/katana-urls.txt

# Phase 3: Gospider
echo "[*] Running Gospider..."
gospider -s https://$TARGET --js -o $OUTPUT_DIR/gospider

# Phase 4: Extract and analyze
echo "[*] Extracting emails..."
jq -r '.emails[]' $OUTPUT_DIR/reconspider.json > $OUTPUT_DIR/emails.txt

echo "[*] Extracting JS files..."
jq -r '.js_files[]' $OUTPUT_DIR/reconspider.json > $OUTPUT_DIR/js-files.txt

echo "[*] Extracting comments..."
jq -r '.comments[]' $OUTPUT_DIR/reconspider.json > $OUTPUT_DIR/comments.txt

echo "[*] Extracting external files..."
jq -r '.external_files[]' $OUTPUT_DIR/reconspider.json > $OUTPUT_DIR/external-files.txt

# Phase 5: Download interesting files
echo "[*] Downloading JS files..."
mkdir -p $OUTPUT_DIR/js
for js in $(head -20 $OUTPUT_DIR/js-files.txt); do
    wget -q $js -P $OUTPUT_DIR/js/ 2>/dev/null
done

# Phase 6: Generate report
echo "[*] Generating report..."
echo "=== Crawl Report for $TARGET ===" > $OUTPUT_DIR/report.txt
echo "Date: $(date)" >> $OUTPUT_DIR/report.txt
echo "" >> $OUTPUT_DIR/report.txt
echo "Emails found: $(wc -l < $OUTPUT_DIR/emails.txt)" >> $OUTPUT_DIR/report.txt
echo "JS files: $(wc -l < $OUTPUT_DIR/js-files.txt)" >> $OUTPUT_DIR/report.txt
echo "External files: $(wc -l < $OUTPUT_DIR/external-files.txt)" >> $OUTPUT_DIR/report.txt
echo "Comments: $(wc -l < $OUTPUT_DIR/comments.txt)" >> $OUTPUT_DIR/report.txt
echo "" >> $OUTPUT_DIR/report.txt
echo "Interesting comments:" >> $OUTPUT_DIR/report.txt
grep -i "todo\|fixme\|hack\|xxx" $OUTPUT_DIR/comments.txt | head -20 >> $OUTPUT_DIR/report.txt

echo "[*] Complete! Results in $OUTPUT_DIR/"

### Dockerized Crawling

Create Dockerfile:
FROM python:3.9-slim
RUN apt-get update && apt-get install -y wget unzip
RUN pip install scrapy scrapy-splash
RUN wget -O ReconSpider.zip https://academy.hackthebox.com/storage/modules/144/ReconSpider.v1.2.zip && unzip ReconSpider.zip
ENTRYPOINT ["python3", "ReconSpider.py"]

Build and run:
docker build -t recon-spider .
docker run -v $(pwd)/output:/output recon-spider https://target.com

---

## Phase 7: Ethical Considerations

### Robots.txt Compliance

Always check robots.txt first:
curl -s https://target.com/robots.txt

Respect Disallow directives in automated tools.

### Rate Limiting

Add delays to avoid overwhelming servers:

In Scrapy:
DOWNLOAD_DELAY = 1  # 1 second between requests
RANDOMIZE_DOWNLOAD_DELAY = True

In custom scripts:
time.sleep(random.uniform(1, 3))

### User-Agent Identification

Always identify your crawler:

headers = {
    'User-Agent': 'ReconBot/1.0 (+https://yourdomain.com/bot)'
}

### Scope Limitation

Restrict crawls to target domain only:
allowed_domains = ['target.com']

---

## Crawling Cheatsheet

| Task | Command |
|------|---------|
| Run ReconSpider | python3 ReconSpider.py https://target.com |
| Parse emails | jq '.emails[]' results.json |
| Extract JS files | jq '.js_files[]' results.json |
| Find comments | jq '.comments[]' results.json |
| Download JS | wget -i js-files.txt |
| Run Katana | katana -u https://target.com -d 3 |
| Run Gospider | gospider -s https://target.com --js |
| Check robots.txt | curl -s https://target.com/robots.txt |
| Add delay | time.sleep(1) in Python |
| Custom Scrapy | scrapy crawl spider -o output.json |

---

## Key Takeaways

- Scrapy gives you complete control over crawling
- ReconSpider extracts structured recon data
- Always parse results with jq for analysis
- Comments and JS files reveal hidden endpoints
- Emails are gold for OSINT and password attacks
- External files may contain sensitive data
- Respect robots.txt and implement rate limiting
- Use multiple tools for comprehensive coverage
- Automate the entire workflow
- Document everything in structured format
- Combine with subdomain enumeration
- JavaScript analysis often reveals API endpoints
- Form fields show attack surfaces
- The more you crawl, the more you find
