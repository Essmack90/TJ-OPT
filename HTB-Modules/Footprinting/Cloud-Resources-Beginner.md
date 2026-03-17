---
tags: [module/footprinting, cloud, aws, azure, gcp, level/beginner]
---

# Cloud Resources - Beginner's Guide

## Why Cloud Matters in Pentesting

Cloud services (AWS, Azure, GCP) are now essential for most companies. They allow employees to work from anywhere with centralized management.

Important Truth: Cloud providers secure THEIR infrastructure, but YOUR configurations can still be vulnerable. The cloud is not automatically safe.

The biggest cloud mistakes:
- S3 buckets (AWS) left open to the public
- Blobs (Azure) without authentication
- Cloud storage (GCP) misconfigured
- Sensitive files exposed
- Private keys leaked

---

## Step 1: Identify Cloud Resources from DNS

When companies use cloud storage internally, they often add DNS records to make it easier for employees.

Example DNS lookup:
blog.inlanefreight.com 10.129.24.93
inlanefreight.com 10.129.27.33
matomo.inlanefreight.com 10.129.127.22
www.inlanefreight.com 10.129.127.33
s3-website-us-west-2.amazonaws.com 10.129.95.250

Notice that last entry - s3-website-us-west-2.amazonaws.com. That's an AWS S3 bucket!

The IP resolves to Amazon, not the company's own servers. This tells us they're using cloud storage.

---

## Step 2: Google Dorks for Cloud Resources

Google can find cloud storage if you know what to look for.

### AWS S3 Buckets
Search for:
intext:companyname inurl:amazonaws.com

This finds pages containing the company name that are hosted on Amazon AWS.

### Azure Blob Storage
Search for:
intext:companyname inurl:blob.core.windows.net

This finds Azure storage accounts.

### Google Cloud Storage
Search for:
intext:companyname inurl:storage.googleapis.com

### What You Might Find

These searches often reveal:
- PDF documents
- Text files
- Presentations
- Source code
- Images
- CSS files
- JavaScript files

Companies often host static content on cloud storage to offload their web servers.

---

## Step 3: Check Website Source Code

Sometimes cloud resources are hidden in the HTML source code.

View page source (Ctrl+U) and look for:
- Links to amazonaws.com
- Links to blob.core.windows.net
- Links to storage.googleapis.com
- Images loaded from cloud storage
- CSS/JS files from CDNs

Example:
link rel="preconnect" href="companyname.blob.core.windows.net"

This tells you they're using Azure blob storage for assets.

---

## Step 4: Use domain.glass

Domain.glass is a great tool for passive information gathering.

Visit: https://domain.glass/companyname.com

It shows you:
- Cloudflare security status (Safe? Not safe?)
- SSL certificate details
- DNS names on certificates
- Social media links
- IP information
- External tools used

This helps build the Gateway layer (Layer 2) by identifying security measures.

---

## Step 5: Use GrayHatWarfare

GrayHatWarfare is a search engine for publicly exposed cloud storage.

Website: https://buckets.grayhatwarfare.com

Features:
- Search for AWS, Azure, and GCP buckets
- Filter by file type (PDF, XLS, DOC, etc.)
- Sort by size, date, bucket name
- See what files are exposed

How to search:
1. Enter company name or abbreviation
2. Use filters to narrow results
3. Browse found buckets
4. Check if files are publicly accessible

---

## Step 6: Search for Company Abbreviations

Companies often use abbreviations in their cloud resource names.

Example:
- InlaneFreight -> ILF
- InlaneFreight -> inlane
- InlaneFreight -> freight

Try variations:
- ilf-backups
- inlane-storage
- freight-data
- ilf-prod
- inlane-dev

Use these in Google dorks and GrayHatWarfare.

---

## Step 7: Look for Leaked Sensitive Files

Sometimes cloud storage exposes CRITICAL files.

### What to Watch For

| File Type | What It Contains | Risk Level |
|-----------|------------------|-------------|
| id_rsa | SSH private key | CRITICAL - direct system access |
| id_rsa.pub | SSH public key | Low (but helps identify users) |
| .env | Environment variables | HIGH - passwords, API keys |
| config.php | Database credentials | HIGH |
| backup.sql | Database dump | CRITICAL - all data |
| credentials.txt | Plain text passwords | CRITICAL |
| .aws/credentials | AWS access keys | CRITICAL |

### Real Example

In GrayHatWarfare, you might find:
id_rsa
id_rsa.pub

This means someone uploaded their SSH private key to a public bucket. Anyone can download it and log into their servers.

No password needed. Just download and use:
ssh -i id_rsa user@target.com

---

## The Cloud Enumeration Principles

### Principle 1: More than meets the eye
You see a DNS entry for s3-website. What you don't see is that this could expose all their files.

### Principle 2: Visible vs Invisible
Visible: A company website
Invisible: Cloud storage hosting their images, backups, and sensitive files

### Principle 3: Always more information
One DNS record leads to:
- Cloud provider identification
- Potential file exposure
- Possible credential leaks
- Attack surface expansion

---

## Quick Reference Commands

Find cloud storage from DNS:
host target.com | grep -i amazonaws
host target.com | grep -i blob.core.windows
host target.com | grep -i storage.googleapis

Google Dorks (manual search):
intext:companyname inurl:amazonaws.com
intext:companyname inurl:blob.core.windows.net
intext:companyname inurl:storage.googleapis.com

GrayHatWarfare:
https://buckets.grayhatwarfare.com

Domain.glass:
https://domain.glass/companyname.com

---

## Key Takeaways

- Cloud resources often appear in DNS records
- Google dorks can find exposed cloud storage
- Website source code reveals cloud asset hosting
- domain.glass gives passive security assessment
- GrayHatWarfare finds publicly exposed buckets
- Company abbreviations help find more resources
- Sensitive files (SSH keys, credentials) get leaked
- One mistake can compromise the entire company
- Document all cloud resources for later testing
- Cloud misconfigurations are gold for pentesters
