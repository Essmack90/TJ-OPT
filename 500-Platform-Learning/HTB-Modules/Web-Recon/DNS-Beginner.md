---
tags: [module/web-recon, dns, domain, passive-recon, level/beginner]
---

# DNS - Beginner's Guide

## What is DNS?

DNS (Domain Name System) is the internet's GPS. It translates human-readable domain names (like www.example.com) into numerical IP addresses (like 192.0.2.1) that computers use to communicate.

Think of it like a phonebook for the internet. Instead of memorizing IP addresses, you remember domain names, and DNS does the translation for you.

---

## Why DNS Matters for Pentesters

| Why | What You Find |
|-----|---------------|
| Uncover assets | Subdomains, mail servers, name servers |
| Map infrastructure | Hosting providers, load balancers, network layout |
| Monitor changes | New subdomains = new attack surface |
| Find misconfigurations | Zone transfers, wildcard entries |
| OSINT | SPF records reveal third-party services |

---

## How DNS Works

When you type www.example.com into your browser:

1. Your computer checks its local cache
2. If not found, it asks a DNS resolver (usually your ISP)
3. The resolver asks a root name server
4. Root points to the TLD server (.com)
5. TLD server points to the authoritative name server for example.com
6. Authoritative server returns the IP address
7. Your browser connects to that IP

---

## DNS Hierarchy

Root Servers (13 worldwide)
Top-Level Domains (.com, .org, .net, .io)
Second-Level Domains (example.com)
Subdomains (mail.example.com, www.example.com)
Hostnames (server1.mail.example.com)

---

## The Hosts File

The hosts file is a manual override for DNS. It's a local text file that maps domain names to IP addresses.

### Locations

| OS | Path |
|----|------|
| Windows | C:\Windows\System32\drivers\etc\hosts |
| Linux/Mac | /etc/hosts |

### Format

<IP Address>    <Hostname> [<Alias> ...]

### Examples

127.0.0.1       localhost
192.168.1.10    devserver.local

### Common Uses

- Development: Point a domain to your local machine
- Testing: Force a domain to resolve to a specific IP
- Blocking: Redirect unwanted sites to 0.0.0.0

0.0.0.0       facebook.com
0.0.0.0       twitter.com

---

## DNS Zone Files

A zone is a portion of the domain namespace that an administrator manages. The zone file contains all the DNS records for that zone.

### Simplified Zone File Example

$TTL 3600
@       IN SOA   ns1.example.com. admin.example.com. (
                2024060401 ; Serial number
                3600       ; Refresh
                900        ; Retry
                604800     ; Expire
                86400 )    ; Minimum TTL

@       IN NS    ns1.example.com.
@       IN NS    ns2.example.com.
@       IN MX 10 mail.example.com.
www     IN A     192.0.2.1
mail    IN A     198.51.100.1
ftp     IN CNAME www.example.com.

---

## Common DNS Record Types

| Record | Full Name | What It Does | Example |
|--------|-----------|--------------|---------|
| A | Address Record | Maps domain to IPv4 address | www.example.com to 192.0.2.1 |
| AAAA | IPv6 Address Record | Maps domain to IPv6 address | www.example.com to 2001:db8::1 |
| CNAME | Canonical Name | Alias for another domain | blog.example.com to webserver.example.net |
| MX | Mail Exchange | Specifies mail servers | example.com to mail.example.com |
| NS | Name Server | Delegates DNS authority | example.com to ns1.example.com |
| TXT | Text Record | Arbitrary text (verification, SPF) | "v=spf1 include:spf.google.com" |
| SOA | Start of Authority | Administrative info about the zone | Serial, refresh, retry values |
| PTR | Pointer | Reverse DNS (IP to domain) | 1.2.0.192.in-addr.arpa to www.example.com |

### The "IN" Field

You'll see "IN" in DNS records. It stands for "Internet" and specifies the protocol family. Most records use "IN".

---

## What Each Record Reveals

| Record | What It Tells You |
|--------|-------------------|
| A/AAAA | IP addresses of servers |
| CNAME | Aliases that may point to other domains |
| MX | Email provider (Google, Microsoft, etc.) |
| NS | Hosting provider |
| TXT | SPF policies, domain verification keys, third-party services |
| SOA | Admin email, zone serial number |

---

## Key Takeaways

- DNS translates domain names to IP addresses
- Different record types serve different purposes
- Zone files contain all DNS records for a domain
- The hosts file bypasses DNS for local overrides
- DNS reveals infrastructure, providers, and services
- TXT records often leak third-party service usage
- Always check DNS during reconnaissance
- More records = more attack surface
