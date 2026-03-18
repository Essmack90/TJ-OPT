---
tags: [module/web-recon, certificate-transparency, ct-logs, crt.sh, ssl, tls, passive-recon, level/beginner]
---

# Certificate Transparency Logs - Beginner's Guide

## What are Certificate Transparency Logs?

Certificate Transparency (CT) logs are public, append-only ledgers that record every SSL/TLS certificate issued by a Certificate Authority (CA).

Think of them as a global registry of every website certificate ever issued. Whenever a company gets an SSL certificate for a domain or subdomain, it's permanently recorded in these public logs.

---

## Why SSL/TLS Certificates Matter

SSL/TLS certificates do two things:
1. **Encrypt** communication between your browser and the website
2. **Verify** that you're actually connecting to the real website

Every time you see the padlock icon in your browser, that site has a valid SSL/TLS certificate.

---

## Why CT Logs Were Created

Before CT logs, bad things could happen:
- Attackers could get fake certificates for legitimate sites
- Certificate Authorities could issue bad certificates secretly
- No one would know until it was too late

CT logs solved this by making ALL certificate issuances PUBLIC.

---

## How CT Logs Work

1. **Certificate Authority** issues a certificate for a domain
2. **Must submit** the certificate to multiple public CT logs
3. **CT logs** record it permanently (can't be deleted or altered)
4. **Anyone** can search and inspect these logs

---

## Why CT Logs Matter for Pentesters

| Why | What You Find |
|-----|---------------|
| Subdomain discovery | Every subdomain that ever had a certificate |
| Historical data | Old subdomains no longer in use |
| Hidden assets | Internal sites that got public certs |
| No brute force needed | Just query the logs |

**The Magic:** CT logs reveal subdomains you'd never find with brute force because you don't need to guess - they're all listed.

---

## crt.sh - The Easiest CT Log Search

crt.sh is a free, user-friendly website that lets you search CT logs.

### Web Interface

1. Go to https://crt.sh
2. Enter a domain (e.g., facebook.com)
3. See every certificate ever issued for that domain
4. Each certificate lists ALL subdomains in its SAN field

### SAN Field (Subject Alternative Name)

When a certificate is issued, it can cover multiple domains/subdomains. These are listed in the SAN field. This is GOLD for recon - one certificate might list dozens of subdomains.

---

## Command-Line CT Log Searching

### Basic crt.sh API Query

```bash
curl -s "https://crt.sh/?q=facebook.com&output=json"
Filter for Specific Subdomains
bash
curl -s "https://crt.sh/?q=facebook.com&output=json" | jq -r '.[].name_value' | grep "dev" | sort -u
Example: Finding dev subdomains on facebook.com
bash
curl -s "https://crt.sh/?q=facebook.com&output=json" | jq -r '.[] | select(.name_value | contains("dev")) | .name_value' | sort -u
Output:
*.dev.facebook.com
*.newdev.facebook.com
*.secure.dev.facebook.com
dev.facebook.com
devvm1958.ftw3.facebook.com
facebook-amex-dev.facebook.com
facebook-amex-sign-enc-dev.facebook.com
newdev.facebook.com
secure.dev.facebook.com
What This Reveals
Subdomain	What It Might Be
dev.facebook.com	Development environment
secure.dev.facebook.com	Secure dev environment
devvm1958.ftw3.facebook.com	Specific dev server
facebook-amex-dev.facebook.com	Partner integration dev
The Command Breakdown
bash
curl -s "https://crt.sh/?q=facebook.com&output=json"   # Fetch JSON data from crt.sh
| jq -r '.[].name_value'                                # Extract domain names
| grep "dev"                                             # Filter for "dev"
| sort -u                                                # Sort and remove duplicates
Key Takeaways
CT logs are public records of every SSL/TLS certificate ever issued

Every subdomain with a certificate appears in these logs

crt.sh is the easiest way to search CT logs

You can query crt.sh from the command line with curl

Filter results with jq and grep

CT logs reveal subdomains you'd never find with brute force

Historical certificates show old, forgotten subdomains

SAN fields list multiple domains per certificate

This is 100% passive recon - no traffic to target

Combine CT log data with other recon methods
