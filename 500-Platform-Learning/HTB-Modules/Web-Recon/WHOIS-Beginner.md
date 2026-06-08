---
tags: [module/web-recon, whois, passive-recon, osint, level/beginner]
---

# WHOIS - Beginner's Guide

## What is WHOIS?

WHOIS is a protocol that lets you look up information about who owns a domain name, IP address, or autonomous system. Think of it as a giant phonebook for the internet.

If you want to know who's behind a website, WHOIS is your first stop.

---

## Why WHOIS Matters for Pentesters

| Why | What You Find |
|-----|---------------|
| Find people | Names, email addresses, phone numbers of domain owners |
| Find infrastructure | Name servers, IP addresses |
| Find patterns | Same registrar, same tech contact across multiple domains |
| Social engineering | Contact info for phishing or pretexting |
| Historical data | Old records reveal changes over time |

---

## What a WHOIS Record Contains

| Field | What It Tells You |
|-------|-------------------|
| Domain Name | The domain you looked up |
| Registrar | Where it was registered (GoDaddy, Namecheap, etc.) |
| Registrant Contact | Who OWNS the domain |
| Administrative Contact | Who MANAGES the domain |
| Technical Contact | Who HANDLES technical issues |
| Creation Date | When it was registered |
| Expiration Date | When it expires (lapses in renewal = opportunity) |
| Name Servers | DNS servers for the domain |
| Registrar WHOIS Server | Where to get more detailed records |

---

## Basic WHOIS Lookup

### Command Line

whois inlanefreight.com

### Online Services

- https://whois.domaintools.com
- https://lookup.icann.org
- https://who.is

---

## Example WHOIS Output

Domain Name: inlanefreight.com
Registry Domain ID: 2420436757_DOMAIN_COM-VRSN
Registrar WHOIS Server: whois.registrar.amazon
Registrar URL: https://registrar.amazon.com
Updated Date: 2023-07-03T01:11:15Z
Creation Date: 2019-08-05T22:43:09Z
Registrar Registration Expiration Date: 2024-08-05T22:43:09Z
Registrar: Amazon Registrar, Inc.
Registrar IANA ID: 468
Registrar Abuse Contact Email: abuse@amazonaws.com
Registrar Abuse Contact Phone: +1.2062664064
Domain Status: ok https://icann.org/epp\#ok
Registry Registrant ID: Not Available From Registry
Registrant Name: On behalf of inlanefreight.com owner
Registrant Organization: Identity Protection Service
Registrant Street: PO Box 786
Registrant City: Hayes
Registrant State/Province: Middlesex
Registrant Postal Code: UB3 9TR
Registrant Country: GB
Registrant Phone: +44.1483307527
Registrant Phone Ext:
Registrant Fax:
Registrant Fax Ext:
Registrant Email: Email@inlanefreight.com

---

## What You Can Learn

From this output, you get:

- **Registrar:** Amazon Registrar, Inc. (they use AWS)
- **Creation Date:** August 5, 2019 (how long they've been around)
- **Expiration Date:** August 5, 2024 (watch for lapses)
- **Abuse Contact:** abuse@amazonaws.com (for reporting abuse)
- **Registrant Email:** Email@inlanefreight.com (pattern: firstname@domain)
- **Country:** GB (United Kingdom - geographic location)
- **Phone:** +44.1483307527 (UK number - potential for vishing)

---

## Privacy Protection

Notice in the example:

Registrant Name: On behalf of inlanefreight.com owner
Registrant Organization: Identity Protection Service

Many domains use privacy protection to hide the real owner. This makes WHOIS less useful, but you can still get:
- Registrar info
- Name servers
- Dates
- Abuse contact

---

## Historical WHOIS

Services like WhoisFreaks, DomainTools, and SecurityTrails store historical WHOIS records.

### Why Historical Data Matters

- See who owned the domain BEFORE privacy protection
- Track changes in contact info over time
- Find patterns across multiple domains
- Sometimes old records weren't redacted

### Historical WHOIS Services

| Service | URL | Notes |
|---------|-----|-------|
| WhoisFreaks | https://whoisfreaks.com | API available |
| DomainTools | https://domaintools.com | Paid, but comprehensive |
| SecurityTrails | https://securitytrails.com | Free tier available |
| Whoisology | https://whoisology.com | Historical database |

---

## Automating WHOIS Queries

### Simple Bash Loop

for domain in $(cat domains.txt); do
    whois $domain > "whois-$domain.txt"
    sleep 2  # Be polite, avoid rate limiting
done

### Extract Emails from WHOIS

whois inlanefreight.com | grep -E -o "\b[a-zA-Z0-9.-]+@[a-zA-Z0-9.-]+\.[a-zA-Z0-9.-]+\b" | sort -u

### Extract Name Servers

whois inlanefreight.com | grep "Name Server" | awk '{print $3}' | sort -u

---

## Key Takeaways

- WHOIS is a public database of domain ownership
- Always check WHOIS first - it's free, fast, and passive
- Look for names, emails, phones (social engineering gold)
- Check creation/expiration dates (old domains = legacy systems)
- Privacy protection hides details, but not everything
- Historical WHOIS can reveal what's been redacted
- Automate bulk lookups but add delays to avoid blocks
- Document everything - you'll need it later
- WHOIS is just the beginning of passive recon
