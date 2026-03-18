---
tags: [module/web-recon, subdomains, dns, bruteforce, active-recon, level/beginner]
---

# Subdomain Bruteforcing - Beginner's Guide

## What is Subdomain Bruteforcing?

Subdomain bruteforcing is an active reconnaissance technique where you systematically test thousands of potential subdomain names against a target domain to find which ones actually exist.

Think of it like trying every key on a keyring to see which ones open doors.

---

## The Bruteforcing Process

### 4 Simple Steps

| Step | What Happens |
|------|--------------|
| 1. Wordlist Selection | Choose a list of potential subdomain names |
| 2. Iteration | Loop through each word in the list |
| 3. DNS Lookup | Check if subdomain.word.com resolves to an IP |
| 4. Filtering | Save only the ones that resolve successfully |

---

## Types of Wordlists

| Type | Description | Example |
|------|-------------|---------|
| General-Purpose | Common names that work everywhere | dev, staging, blog, mail, admin, test |
| Targeted | Specific to industries/technologies | aws, okta, salesforce, sharepoint |
| Custom | Created from your own intelligence | employee names, project codes, patterns |

---

## Common Subdomain Tools

| Tool | Description | Best For |
|------|-------------|----------|
| dnsenum | Comprehensive DNS enumeration | All-in-one scanning |
| fierce | User-friendly recursive discovery | Beginners |
| dnsrecon | Versatile with multiple techniques | Flexibility |
| amass | Advanced with many data sources | Professional recon |
| assetfinder | Simple and quick | Fast checks |
| puredns | Powerful resolver | Accuracy |

---

## dnsenum Deep Dive

dnsenum is a Perl-based DNS reconnaissance tool that does much more than just bruteforcing.

### What dnsenum Can Do

- Enumerate A, AAAA, NS, MX, TXT records
- Attempt zone transfers (AXFR)
- Brute force subdomains
- Scrape Google for subdomains
- Perform reverse lookups
- Run WHOIS queries

### Basic dnsenum Command

```bash
dnsenum --enum target.com -f /path/to/wordlist.txt
Example with SecLists
bash
dnsenum --enum inlanefreight.com -f /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt
Command Breakdown
Option	Meaning
--enum	Enable enumeration shortcuts
target.com	The domain you're targeting
-f /path/to/wordlist	Path to your subdomain wordlist
Real dnsenum Output
bash
dnsenum --enum inlanefreight.com -f /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt
Output:
text
dnsenum VERSION:1.2.6

-----   inlanefreight.com   -----


Host's addresses:
__________________

inlanefreight.com.                       300      IN    A        134.209.24.248

[...]

Brute forcing with /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt:
_______________________________________________________________________________________

www.inlanefreight.com.                   300      IN    A        134.209.24.248
support.inlanefreight.com.               300      IN    A        134.209.24.248
[...]

done.
What the Output Shows
Section	What It Means
Host's addresses	The main domain's IP
Brute forcing	Tool is testing subdomains
Found subdomains	Names that resolved successfully
Key Takeaways
Subdomain bruteforcing tests many potential names against a domain

Wordlists are essential - better lists = better results

dnsenum is a powerful all-in-one DNS tool

Always use quality wordlists like SecLists

Bruteforcing is active recon (can be detected)

Found subdomains often reveal hidden attack surfaces

Start with common subdomains, then get more specific

Combine results with other enumeration methods
