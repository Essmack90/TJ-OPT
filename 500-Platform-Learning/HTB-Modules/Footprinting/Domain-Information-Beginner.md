---
tags: [module/footprinting, domain, osint, level/beginner]
---

# Domain Information - Beginner's Guide

## What is Domain Information Gathering?

Domain information is a core component of any penetration test. It's not just about finding subdomains - it's about understanding the company's entire Internet presence.

We gather this information PASSIVELY. That means:
- No direct scanning
- No active connections to the target
- We remain hidden like any normal visitor
- We use third-party services and public data

Think of it as being a detective reading public records, not knocking on doors.

---

## Step 1: Understand the Company First

Before you even look at domains, look at the company's website. Read it like a customer would.

Ask yourself:
- What services do they offer?
- What technologies would they NEED to offer those services?
- What does their business model tell us about their infrastructure?

Example:
If they offer app development and IoT services, they probably have:
- Development servers
- Test environments
- API endpoints
- Cloud infrastructure
- Code repositories

The services they OFFER tell you what they USE internally.

---

## Step 2: Check SSL Certificates

SSL certificates are a goldmine. Companies often list multiple domains on the same certificate.

### View Certificate in Browser
Click the padlock icon in your browser -> Certificate -> Details

Look for Subject Alternative Names (SAN). This lists ALL domains the certificate is valid for.

Example:
Subject Alternative Name:
    DNS: inlanefreight.htb
    DNS: www.inlanefreight.htb
    DNS: support.inlanefreight.htb

Boom - you just found support.inlanefreight.htb without scanning anything.

---

## Step 3: Use Certificate Transparency Logs (crt.sh)

Certificate Transparency is a system that logs every SSL certificate issued. This is PUBLIC data.

Website: https://crt.sh

Search for your target:
https://crt.sh/?q=inlanefreight.com

You'll see every certificate ever issued for that domain, including subdomains you never knew existed.

### Using the Command Line

Get results in JSON format:
curl -s https://crt.sh/\?q\=inlanefreight.com\&output\=json | jq .

Extract just the subdomains:
curl -s https://crt.sh/\?q\=inlanefreight.com\&output\=json | jq . | grep name | cut -d":" -f2 | grep -v "CN=" | cut -d'"' -f2 | awk '{gsub(/\\n/,"\n");}1;' | sort -u

This gives you a clean list of unique subdomains.

---

## Step 4: Identify Which Hosts Are In-Scope

Not every host you find is testable. Some are hosted by third parties (AWS, Cloudflare, etc.). You can only test hosts that belong to the company.

Use host command to check:
for i in $(cat subdomainlist); do
    host $i | grep "has address" | grep inlanefreight.com
done

This shows which subdomains resolve to IPs in the company's range.

---

## Step 5: Use Shodan

Shodan is a search engine for Internet-connected devices. It scans the entire Internet and stores information about services running on IPs.

### Get IP List
for i in $(cat subdomainlist); do
    host $i | grep "has address" | grep inlanefreight.com | cut -d" " -f4 >> ip-addresses.txt
done

### Query Shodan
for i in $(cat ip-addresses.txt); do
    shodan host $i
done

Shodan tells you:
- Open ports
- Service versions
- Operating systems
- SSL/TLS details
- Geographic location
- Organization name

Example output:
10.129.27.33
Ports:
  22/tcp OpenSSH 7.6p1 Ubuntu
  80/tcp nginx
  443/tcp nginx
    SSL Versions: TLSv1.2
    Diffie-Hellman Parameters: 2048 bits

---

## Step 6: Check All DNS Records

DNS holds much more than just IP addresses. Use dig to get everything:

dig any inlanefreight.com

### Types of DNS Records

| Record Type | What It Does | What It Reveals |
|-------------|--------------|-----------------|
| A | Points domain to IPv4 | Server IPs |
| AAAA | Points domain to IPv6 | IPv6 addresses |
| MX | Mail servers | Email provider (Google, Outlook, etc.) |
| NS | Name servers | Hosting provider |
| TXT | Text records | Verification keys, SPF, security policies |
| SOA | Start of Authority | Administrative info |
| CNAME | Aliases | Other domain names |

---

## What DNS Records Tell You

### MX Records (Mail Servers)
MX 1 aspmx.l.google.com
MX 5 alt1.aspmx.l.google.com

This tells you: They use Google for email. That means:
- Potential Google Workspace
- GDrive shares possible
- Google authentication

### NS Records (Name Servers)
NS ns.inwx.net
NS ns2.inwx.net

This tells you: Their hosting provider is INWX.
- You can check what else that provider hosts
- Known vulnerabilities of that provider

### TXT Records

TXT records are GOLD. Look at this example:

MS=ms92346782372
Microsoft verification code - they use Microsoft services

atlassian-domain-verification=IJdXMt1rKCy68JFszSdCKVpwPN
Atlassian verification - they use Jira, Confluence, Bitbucket

google-site-verification=O7zV5-xFh_jn7JQ31
Google verification - they use Google services

logmein-verification-code=87123gff5a479e-61d4325gddkbvc1
LogMeIn - remote access platform

v=spf1 include:mailgun.org include:_spf.google.com include:spf.protection.outlook.com include:_spf.atlassian.net ip4:10.129.24.8 ip4:10.129.27.2 ip4:10.72.82.106 ~all
SPF record - tells you:
- Mailgun (email API service)
- Google (email)
- Outlook (Microsoft email)
- Atlassian (Jira/Confluence)
- Internal IPs (10.129.24.8, 10.129.27.2, 10.72.82.106)

---

## What You Can Infer from This Data

From the TXT records above, we can deduce:

| Service | What It Means | Attack Surface |
|---------|---------------|----------------|
| Atlassian | They use Jira/Confluence | Default creds, open instances, CVEs |
| Google Gmail | Email via Google | GDrive shares, Google Auth |
| LogMeIn | Remote access platform | Admin access, password reuse |
| Mailgun | Email APIs | API endpoints, IDOR, SSRF |
| Outlook | Microsoft email | Office 365, OneDrive, Azure |
| INWX | Hosting provider | Domain management access |
| IPs 10.129.24.8, 10.129.27.2 | Internal servers | Potential targets for later |

---

## The Enumeration Principles in Action

### Principle 1: More than meets the eye
You see TXT records. But what you DON'T see is that these records reveal the company's entire third-party ecosystem.

### Principle 2: Visible vs Invisible
Visible: A list of subdomains
Invisible: The technologies behind them, the internal IPs, the service providers

### Principle 3: Always more information
From one TXT record, we found:
- Email provider (Google)
- Development platform (Atlassian)
- Remote access (LogMeIn)
- Email API (Mailgun)
- Internal IP ranges

---

## Key Takeaways

- Domain information gathering is PASSIVE - no scanning
- SSL certificates reveal multiple domains
- crt.sh gives you every certificate ever issued
- Subdomains lead to IPs, which lead to Shodan data
- DNS records (especially TXT) are treasure troves
- Third-party services tell you about internal infrastructure
- IPs in SPF records are internal servers - note them
- Document EVERYTHING you find
- You're building a map of the company's entire Internet presence
- This map will guide all your active testing later

---

## Quick Reference Commands

curl -s "https://crt.sh/?q=target.com&output=json" | jq .

curl -s "https://crt.sh/?q=target.com&output=json" | jq -r '.[].name_value' | sed 's/\*\.//g' | sort -u

for i in $(cat subdomains.txt); do host $i; done | grep "has address"

dig any target.com

dig txt target.com

shodan host IP_ADDRESS
