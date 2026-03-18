---
tags: [module/web-recon, robots.txt, web-crawling, information-disclosure, level/beginner]
---

# robots.txt - Beginner's Guide

## What is robots.txt?

robots.txt is a simple text file placed in the root directory of a website (e.g., www.example.com/robots.txt). It tells web crawlers (like Googlebot) which parts of the site they are allowed to visit and which parts are off-limits.

Think of it as a "virtual velvet rope" - it tells bots where they can and cannot go.

---

## Why robots.txt Matters for Pentesters

| Why | What You Find |
|-----|---------------|
| Hidden directories | Paths the owner wants to hide |
| Sensitive files | Admin panels, backup folders, private areas |
| Website structure | Map of important sections |
| Crawler traps | Honeypots for malicious bots |
| Sitemaps | Complete site structure |

**The Irony:** The file meant to hide things actually REVEALS them to anyone who looks.

---

## robots.txt Structure

A robots.txt file is plain text with a simple format:

User-agent: [bot name]
Directive: [path]

### Components

| Component | Description | Example |
|-----------|-------------|---------|
| User-agent | Which bot the rule applies to | User-agent: * (all bots) |
| Disallow | Paths bots cannot access | Disallow: /admin/ |
| Allow | Paths bots can access | Allow: /public/ |
| Crawl-delay | Seconds between requests | Crawl-delay: 10 |
| Sitemap | Location of XML sitemap | Sitemap: https://site.com/sitemap.xml |

---

## Example robots.txt

User-agent: *
Disallow: /admin/
Disallow: /private/
Disallow: /backup/
Allow: /public/

User-agent: Googlebot
Crawl-delay: 5

Sitemap: https://www.example.com/sitemap.xml

### What This Tells Us

| Line | What It Reveals |
|------|-----------------|
| /admin/ | There's an admin panel here |
| /private/ | Private content exists |
| /backup/ | Backup files might be accessible |
| /public/ | Public area (less interesting) |
| Googlebot rule | They care about Google's crawling |
| Sitemap | Complete site structure available |

---

## How to Find robots.txt

### Simple Browser Check

Just navigate to:
https://target.com/robots.txt
http://target.com/robots.txt

### Using curl

curl -s https://target.com/robots.txt
curl -s http://target.com/robots.txt

### Common Locations to Check

https://target.com/robots.txt
https://www.target.com/robots.txt
http://target.com/robots.txt
https://target.com/robots.txt/
https://target.com/Robots.txt

---

## What to Look For

### Interesting Disallow Paths

| Path | What It Might Be |
|------|------------------|
| /admin | Admin panel |
| /wp-admin | WordPress admin |
| /backup | Backup files |
| /backups | More backups |
| /temp | Temporary files |
| /tmp | Temp directory |
| /logs | Log files |
| /cache | Cached content |
| /dev | Development area |
| /test | Test environment |
| /private | Private content |
| /secure | Secure area |
| /.git | Git repository |
| /.env | Environment variables |

### Why These Are Interesting

If the owner wants to hide these from Google, they might contain:
- Sensitive information
- Configuration files
- Credentials
- Backup data
- Development code
- Internal tools

---

## robots.txt vs Security

### What robots.txt CAN'T Do

- It's NOT a security mechanism
- It does NOT restrict access
- It's just a polite request
- Malicious bots ignore it

### What robots.txt CAN Do

- Guide legitimate crawlers
- Prevent search engine indexing
- Reduce server load
- Accidentally reveal hidden paths

---

## Manual robots.txt Analysis

### Basic Fetch

curl -s https://inlanefreight.com/robots.txt

### Extract All Disallowed Paths

curl -s https://target.com/robots.txt | grep -i "disallow" | awk '{print $2}'

### Check If Paths Actually Exist

for path in $(curl -s https://target.com/robots.txt | grep -i "disallow" | awk '{print $2}'); do
    status=$(curl -s -o /dev/null -w "%{http_code}" https://target.com$path)
    echo "$path - HTTP $status"
done

---

## Key Takeaways

- robots.txt is always in the root directory
- Check it on EVERY target
- Disallowed paths are often interesting
- It's not security - just a polite request
- Malicious bots ignore it entirely
- Use it as a map to hidden areas
- Always verify if disallowed paths are actually accessible
- Combine with other recon techniques
- Document everything you find
- The irony: the hiding file reveals everything
