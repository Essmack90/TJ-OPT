---
tags: [module/web-recon, subdomains, dns, passive-recon, active-recon, level/beginner]
---

# Subdomains - Beginner's Guide

## What are Subdomains?

Subdomains are extensions of a main domain. If the main domain is example.com, subdomains look like:

- blog.example.com
- shop.example.com
- mail.example.com
- dev.example.com
- admin.example.com

Think of them as different departments in the same building - each has its own entrance, but they're all part of the same organization.

---

## Why Subdomains Matter for Pentesters

| Why | What You Find |
|-----|---------------|
| Development servers | dev.example.com, staging.example.com (often less secure) |
| Hidden login portals | admin.example.com, portal.example.com |
| Legacy applications | old.example.com, test.example.com (outdated software) |
| Sensitive information | docs.example.com, files.example.com |
| Third-party services | aws.example.com, cloud.example.com |

The main domain is locked down. Subdomains are often forgotten and vulnerable.

---

## How Subdomains Are Represented in DNS

| Record Type | How It Works | Example |
|-------------|--------------|---------|
| A Record | Subdomain points directly to an IP | blog.example.com to 192.168.1.10 |
| CNAME | Subdomain is an alias for another domain | shop.example.com to webserver.example.net |

---

## Subdomain Enumeration Methods

### 1. Active Enumeration

You directly interact with the target's DNS servers.

| Method | Description | Detectable? |
|--------|-------------|--------------|
| Zone Transfer | Request all DNS records at once | YES (loud) |
| Brute Force | Test thousands of possible subdomain names | YES (can be loud) |

### 2. Passive Enumeration

You use third-party sources without touching the target.

| Method | Description | Detectable? |
|--------|-------------|--------------|
| Certificate Transparency | Check public SSL certificate logs | NO |
| Search Engines | Google dorks like site:example.com | NO |
| DNS Databases | Online services that aggregate DNS data | NO |

---

## Why Subdomains Are Vulnerable

- Forgotten assets: Companies forget they exist
- Less security: Dev servers have weaker protections
- Outdated software: Old apps have unpatched vulnerabilities
- Exposed data: Configuration files, backups, internal docs
- Default credentials: Test servers often use admin:admin

---

## Key Takeaways

- Subdomains are extensions of the main domain
- They often host dev environments, admin panels, and legacy apps
- Subdomains are frequently less secure than the main domain
- Active enumeration = direct interaction (louder)
- Passive enumeration = third-party sources (stealthier)
- Use BOTH methods for best results
- Certificate Transparency logs are a goldmine
- Always check for forgotten subdomains
