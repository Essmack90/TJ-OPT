---
tags: [module/footprinting, dns, domain, name-resolution, level/beginner]
---

# DNS Enumeration - Beginner's Guide

## What is DNS?

DNS (Domain Name System) is like the phonebook of the Internet. It translates human-friendly domain names (like academy.hackthebox.com) into computer-friendly IP addresses (like 10.129.14.128).

Without DNS, you'd have to remember IP addresses for every website you visit.

---

## How DNS Works

1. You type www.example.com in your browser
2. Your computer asks a DNS server: "What is the IP for www.example.com?"
3. The DNS server responds with the IP address
4. Your browser connects to that IP

This happens in milliseconds, every time you visit a website.

---

## Types of DNS Servers

| Server Type | Description |
|-------------|-------------|
| Root Server | The top-level servers that know where to find TLD servers (.com, .org, etc.) |
| Authoritative | Holds the actual DNS records for a domain. Its answers are "official" |
| Non-authoritative | Has cached information but doesn't own the original records |
| Caching | Stores DNS results temporarily to speed up future queries |
| Recursive | Does all the work of finding the answer for you |
| Forwarding | Just passes queries to another DNS server |

---

## DNS Records Explained

| Record | Purpose | Example |
|--------|---------|---------|
| A | Maps domain to IPv4 address | 10.129.14.128 |
| AAAA | Maps domain to IPv6 address | 2001:db8::1 |
| MX | Mail server for the domain | mail.google.com |
| NS | Name server for the domain | ns1.google.com |
| TXT | Text information (verification, SPF, etc.) | "v=spf1 include:spf.google.com" |
| CNAME | Alias for another domain | www → example.com |
| PTR | Reverse lookup (IP → domain) | 128.14.129.10.in-addr.arpa |
| SOA | Start of Authority - administrative info | Contains serial, refresh, retry values |

---

## The SOA Record

The SOA (Start of Authority) record contains important administrative information:

- Primary name server
- Admin email address (the first dot is actually an @)
- Serial number (for tracking updates)
- Refresh interval
- Retry interval
- Expire time
- Minimum TTL

### Example SOA

dig soa example.com

inlanefreight.com. 900 IN SOA ns-161.awsdns-20.com. awsdns-hostmaster.amazon.com. 1 7200 900 1209600 86400

Note: The email is actually awsdns-hostmaster@amazon.com (the dot becomes @)

---

## DNS Configuration Files (Bind9)

### named.conf.local - Zone Definitions

zone "domain.com" {
    type master;
    file "/etc/bind/db.domain.com";
    allow-update { key rndc-key; };
};

### Zone File - Forward Lookup

$ORIGIN domain.com
$TTL 86400
@     IN     SOA    dns1.domain.com. hostmaster.domain.com. (
                    2001062501 ; serial
                    21600      ; refresh
                    3600       ; retry
                    604800     ; expire
                    86400 )    ; minimum TTL

      IN     NS     ns1.domain.com.
      IN     NS     ns2.domain.com.
      IN     MX     10     mx.domain.com.

server1  IN     A       10.129.14.5
server2  IN     A       10.129.14.7
www      IN     CNAME   server2

### Reverse Zone File - Reverse Lookup

$ORIGIN 14.129.10.in-addr.arpa
5    IN     PTR    server1.domain.com.
7    IN     PTR    server2.domain.com.

---

## Dangerous DNS Settings

| Option | Description | Risk |
|--------|-------------|------|
| allow-query any | Anyone can query the server | Information disclosure |
| allow-recursion any | Anyone can use recursive queries | Can be used in amplification attacks |
| allow-transfer any | Anyone can request zone transfers | COMPLETE zone data exposure |
| zone-statistics | Collects zone data | May leak information |

The most dangerous is allow-transfer any - it lets anyone download your entire DNS zone file.

---

## Basic DNS Queries with dig

### NS Query - Find Name Servers

dig ns inlanefreight.htb @10.129.14.128

### ANY Query - Show All Records

dig any inlanefreight.htb @10.129.14.128

### TXT Query - Get Text Records

dig txt inlanefreight.htb @10.129.14.128

### MX Query - Find Mail Servers

dig mx inlanefreight.htb @10.129.14.128

### Version Query

dig CH TXT version.bind 10.129.14.128

---

## What TXT Records Reveal

TXT records often contain:

- SPF records (which servers can send email)
- Domain verification codes (Google, Microsoft, Atlassian)
- DKIM keys
- DMARC policies

Example:
v=spf1 include:mailgun.org include:_spf.google.com include:spf.protection.outlook.com include:_spf.atlassian.net ip4:10.129.124.8 ip4:10.129.127.2 ip4:10.129.42.106 ~all

This tells us they use:
- Mailgun
- Google Workspace
- Microsoft 365
- Atlassian
- Internal IPs: 10.129.124.8, 10.129.127.2, 10.129.42.106

---

## Zone Transfer (AXFR) - The Big Prize

Zone transfer is how DNS servers synchronize data. If misconfigured, ANYONE can request a full zone transfer.

### Why It's Dangerous

A zone transfer gives you:
- Every subdomain
- Every IP address
- Internal hostnames
- Network structure

### How to Test for AXFR

dig axfr inlanefreight.htb @10.129.14.128

### Success Example

inlanefreight.htb. 604800 IN SOA ...
app.inlanefreight.htb. 604800 IN A 10.129.18.15
internal.inlanefreight.htb. 604800 IN A 10.129.1.6
mail1.inlanefreight.htb. 604800 IN A 10.129.18.201
dc1.internal.inlanefreight.htb. 604800 IN A 10.129.34.16
dc2.internal.inlanefreight.htb. 604800 IN A 10.129.34.11
vpn.internal.inlanefreight.htb. 604800 IN A 10.129.1.6
ws1.internal.inlanefreight.htb. 604800 IN A 10.129.1.34
ws2.internal.inlanefreight.htb. 604800 IN A 10.129.1.35
wsus.internal.inlanefreight.htb. 604800 IN A 10.129.18.2

This reveals their entire internal network structure!

---

## Subdomain Brute Forcing

If zone transfers are blocked, you can brute force subdomains using wordlists.

### Manual For Loop

for sub in $(cat subdomains.txt); do
    dig $sub.inlanefreight.htb @10.129.14.128 | grep -v ';\|SOA' | grep $sub
done

### Using dnsenum

dnsenum --dnsserver 10.129.14.128 --enum -f subdomains.txt inlanefreight.htb

### Using fierce

fierce --domain inlanefreight.htb --dns-server 10.129.14.128

---

## Key Takeaways

- DNS translates domain names to IP addresses
- Different record types serve different purposes
- TXT records leak information about third-party services
- Zone transfer (AXFR) can expose your entire network
- allow-transfer any is a CRITICAL misconfiguration
- Internal IPs in DNS reveal network structure
- Always check for zone transfer vulnerabilities
- Subdomain brute forcing finds hidden hosts
- DNS version queries may reveal software versions
- Document everything you find
