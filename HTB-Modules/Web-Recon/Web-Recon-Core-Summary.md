---
tags: [web-recon, summary, core, must-know]
---

# Information Gathering - Web Edition - What You MUST FUCKING KNOW

## The Absolute Essentials

If you learn NOTHING else from this module, learn these 10 things. Everything else is optimization and edge cases.

---

## 1. Active vs Passive Recon

| Type | Description | Risk | Examples |
|------|-------------|------|----------|
| Active | Direct interaction with target | HIGH - You'll be logged | Port scanning, directory brute force, zone transfer attempts |
| Passive | No direct interaction | LOW - Nearly undetectable | WHOIS, DNS queries, CT logs, search engines, web archives |

**The Rule:** Start passive. Stay passive as long as you can. Only go active when you have to.

---

## 2. The Five Goals of Web Recon

| Goal | What You're Looking For |
|------|------------------------|
| Identify Assets | Domains, subdomains, IP addresses, cloud instances |
| Uncover Hidden Info | Backup files, config files, dev environments, admin panels |
| Analyze Attack Surface | Open ports, service versions, technologies, vulnerabilities |
| Gather Intelligence | Employees, emails, tech stack, third-party services |
| Map Infrastructure | Network layout, server relationships, dependencies |

---

## 3. The DNS Records That Matter Most

| Record | What It Reveals | Why It's Gold |
|--------|-----------------|---------------|
| A | IPv4 addresses | Direct server access |
| MX | Mail servers | Email provider, potential entry point |
| NS | Name servers | Hosting provider, infrastructure |
| TXT | SPF, verification keys | Third-party services, internal IPs |
| CNAME | Aliases | Hidden relationships, outdated targets |
| SOA | Admin email | Social engineering target |

**TXT records are GOLD.** They reveal:
- MS= - Microsoft services (Office 365, Azure)
- atlassian-domain-verification - Jira/Confluence
- google-site-verification - Google services
- logmein-verification-code - Remote access platform
- include:mailgun.org - Email API service
- ip4: - INTERNAL IP ADDRESSES (network map)

---

## 4. Certificate Transparency (crt.sh) - The Free Subdomain List

Every SSL certificate ever issued is public record. This means every subdomain that ever had a cert is in these logs.

curl -s "https://crt.sh/?q=%25.target.com&output=json" | jq -r '.[].name_value' | sed 's/\*\.//g' | sort -u

This ONE COMMAND reveals more subdomains than most brute-force attacks. Use it on EVERY target.

---

## 5. The Wayback Machine - Your Time Machine

The Wayback Machine stores historical snapshots of websites. This reveals:

- Old pages no longer linked
- Removed directories (/backup/, /old-admin/)
- Deleted files (config backups, SQL dumps)
- Previous technology versions
- Past employee information

curl -s "http://web.archive.org/cdx/search/cdx?url=target.com&output=json&fl=original&collapse=urlkey" | jq -r '.[] | select(length > 0) | .[0]'

**The Rule:** What's gone from the live site might still be in the archive.

---

## 6. The Most Important Search Operators (Google Dorks)

| Operator | What It Does | Example |
|----------|--------------|---------|
| site: | Limit to domain | site:target.com |
| inurl: | Find in URL | inurl:admin |
| filetype: | Find file types | filetype:pdf |
| intitle: | Find in page title | intitle:"index of" |
| " " | Exact phrase | "confidential report" |
| - | Exclude term | -inurl:login |

**The Golden Dorks:**

site:target.com filetype:pdf
site:target.com inurl:backup
site:target.com intitle:"index of"
site:target.com filetype:sql
site:target.com filetype:env

---

## 7. The Subdomain Discovery Trinity

You need ALL THREE methods for complete coverage:

| Method | Tool/Command | What It Finds |
|--------|--------------|---------------|
| Certificate Logs | curl -s "https://crt.sh/?q=%25.target.com" | Every subdomain that ever had a cert |
| Brute Force | gobuster dns -d target.com -w wordlist.txt | Subdomains that never had certs |
| Search Engines | site:*.target.com | Subdomains indexed by Google |

**The Rule:** Use all three. Each finds what the others miss.

---

## 8. Zone Transfer (AXFR) - The Holy Grail

If a DNS server is misconfigured, you can download its ENTIRE zone file - every subdomain, every IP, every record.

dig AXFR target.com @nameserver

Always try this on every name server you find. It rarely works, but when it does, you win.

---

## 9. The .well-known Goldmine

Standardized location for metadata: https://target.com/.well-known/

| Endpoint | What It Reveals |
|----------|-----------------|
| security.txt | Who to contact (social engineering target) |
| openid-configuration | Authentication endpoints, keys |
| assetlinks.json | Mobile app associations |
| mta-sts.txt | Email security policy |

---

## 10. The Golden Rule of Web Recon

> "The more you find, the more you have to attack. Leave no stone unturned."

- Every subdomain is a potential entry point
- Every file is potential intelligence
- Every comment could leak credentials
- Every old backup might contain live data
- Every technology has known vulnerabilities

**If you're stuck, you haven't enumerated enough. There's ALWAYS more.**

---

## The One-Liners You MUST Know

### Certificate Transparency

curl -s "https://crt.sh/?q=%25.target.com&output=json" | jq -r '.[].name_value' | sed 's/\*\.//g' | sort -u

### Wayback Machine URLs

curl -s "http://web.archive.org/cdx/search/cdx?url=target.com&output=json&fl=original&collapse=urlkey" | jq -r '.[] | select(length > 0) | .[0]'

### DNS Zone Transfer

dig AXFR target.com @$(dig NS target.com +short | head -1)

### Google Dork for Files

site:target.com filetype:pdf OR filetype:docx OR filetype:xlsx

### Extract Emails from Page

curl -s https://target.com | grep -oE '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}' | sort -u

### Technology Detection

whatweb target.com

### WAF Detection

wafw00f https://target.com

### robots.txt Disallowed Paths

curl -s https://target.com/robots.txt | grep -i "disallow:" | awk '{print $2}'

---

## One Final Thing

If you remember ONLY one command, remember this:

curl -s "https://crt.sh/?q=%25.target.com&output=json" | jq -r '.[].name_value' | sed 's/\*\.//g' | sort -u

It's passive. It's free. It finds shit you didn't know existed.

**Now go recon some fucking websites.**
