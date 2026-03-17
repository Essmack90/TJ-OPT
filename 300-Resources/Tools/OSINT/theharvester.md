---
tags: [tool, osint, domain, email]
tool: "theharvester"
category: "OSINT"
installed: true
phase: [recon]
---

# theHarvester - Email and Subdomain Discovery

## Tool Overview
Purpose: Gather emails, subdomains, hosts from public sources
Location: /usr/bin/theharvester

## When to Use
- Initial domain reconnaissance
- Finding email addresses associated with a domain
- Discovering subdomains

## How to Use It

Basic Search:
theharvester -d example.com -b all

Specific Source:
theharvester -d example.com -b google

Save Output:
theharvester -d example.com -b all -f results.html

## Common Sources
- google - Google search
- bing - Bing search
- linkedin - LinkedIn search
- baidu - Baidu search
- yahoo - Yahoo search
- all - Use all sources

## Related Tools
recon-ng, sublist3r
