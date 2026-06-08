---
tags: [module/web-recon, crawling, spidering, scrapy, burp, zap, tools, level/beginner]
---

# Creepy Crawlies - Beginner's Guide

## What are Web Crawlers?

Web crawlers (also called spiders) are automated tools that systematically browse websites, following links and extracting information. They're called "creepy crawlies" because they spider their way through websites, leaving no page unturned.

Think of them as robots that do the boring work of clicking every link and recording everything they find.

---

## Why Crawlers Matter for Pentesters

| Why | What They Do |
|-----|--------------|
| Save time | Automate the discovery process |
| Find hidden pages | Pages not linked from the homepage |
| Extract data | Emails, links, files, comments |
| Map structure | Complete site architecture |
| Never miss anything | Systematic coverage |

**The Rule:** A good crawler finds what manual browsing misses.

---

## Popular Web Crawlers

| Tool | Type | Best For | Difficulty |
|------|------|----------|------------|
| Burp Suite Spider | GUI/Professional | Deep app mapping | Easy |
| OWASP ZAP Spider | GUI/Free | Automated scanning | Easy |
| Scrapy | Python Framework | Custom crawlers | Advanced |
| Apache Nutch | Java/Scale | Massive crawls | Expert |
| HTTrack | Offline browser | Site mirroring | Easy |
| Gospider | CLI | Fast crawling | Intermediate |
| Katana | CLI | Modern crawling | Intermediate |

---

## Burp Suite Spider

Burp Suite's Spider is an active crawler that maps web applications.

### How to Use

1. Open Burp Suite
2. Configure your browser to use Burp as a proxy
3. Browse the site manually (or let Burp do it)
4. Go to Target > Site Map
5. Right-click on your target
6. Select "Spider this host"

### What It Finds

- All linked pages
- Hidden directories
- Parameters
- Forms
- Comments
- JavaScript files

---

## OWASP ZAP Spider

ZAP is a free, open-source alternative to Burp.

### How to Use

1. Open ZAP
2. Enter your target URL
3. Click "Attack" > "Spider"
4. Watch it crawl

### ZAP Spider Modes

- Traditional Spider: Basic link following
- AJAX Spider: Handles JavaScript-heavy sites
- Both available for comprehensive coverage

---

## Scrapy - Python Crawling Framework

Scrapy is a powerful Python framework for building custom crawlers.

### Installing Scrapy

pip3 install scrapy

### Creating a Basic Spider

Save as basic_spider.py:

import scrapy

class BasicSpider(scrapy.Spider):
    name = "basic"
    start_urls = ["https://target.com"]
    
    def parse(self, response):
        # Extract all links
        for link in response.css('a::attr(href)').getall():
            yield {'link': link}
        
        # Extract all text
        yield {'text': response.css('body::text').get()}
        
        # Follow links (continue crawling)
        for next_page in response.css('a::attr(href)').getall():
            if next_page is not None:
                yield response.follow(next_page, self.parse)

### Running the Spider

scrapy runspider basic_spider.py -o output.json

---

## HTTrack - Website Copier

HTTrack downloads entire websites for offline viewing.

### Installing HTTrack

sudo apt install httrack -y

### Basic Usage

httrack https://target.com -O ./target-mirror

This creates a complete offline copy of the website.

---

## ReconSpider - HTB Custom Tool

ReconSpider is a custom Scrapy spider designed for reconnaissance.

### Download ReconSpider

wget -O ReconSpider.zip https://academy.hackthebox.com/storage/modules/144/ReconSpider.v1.2.zip
unzip ReconSpider.zip

### Running ReconSpider

python3 ReconSpider.py http://inlanefreight.com

### Understanding ReconSpider Output

After running, a file called `results.json` is created with this structure:

{
    "emails": [
        "user@example.com",
        "admin@example.com"
    ],
    "links": [
        "https://target.com/about",
        "https://target.com/contact"
    ],
    "external_files": [
        "https://target.com/files/document.pdf"
    ],
    "js_files": [
        "https://target.com/js/main.js"
    ],
    "form_fields": [
        "username",
        "password"
    ],
    "images": [
        "https://target.com/images/logo.png"
    ],
    "videos": [],
    "audio": [],
    "comments": [
        "<!-- TODO: remove debug code -->",
        "<!-- admin login at /admin -->"
    ]
}

---

## What Each Field Means

| Field | Description | Why It Matters |
|-------|-------------|----------------|
| emails | Email addresses found | Phishing targets, usernames |
| links | URLs within the domain | Site structure, hidden pages |
| external_files | PDFs, docs, etc. | Sensitive documents |
| js_files | JavaScript files | Client-side code, API endpoints |
| form_fields | Input fields | Attack surfaces |
| images | Image URLs | Metadata, content |
| comments | HTML comments | Developer leaks, TODOs |

---

## Key Takeaways

- Web crawlers automate the discovery process
- Burp and ZAP are great GUI options
- Scrapy gives you full control for custom needs
- HTTrack creates offline site copies
- ReconSpider extracts structured data for recon
- Always check comments - developers leak info there
- Extract emails for OSINT and password spraying
- JavaScript files reveal API endpoints
- External files (PDFs) may contain sensitive data
- Document everything in structured format (JSON)
