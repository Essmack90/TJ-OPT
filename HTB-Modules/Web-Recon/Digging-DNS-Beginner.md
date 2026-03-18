---
tags: [module/web-recon, dns, dig, nslookup, host, passive-recon, level/beginner]
---

# Digging DNS - Beginner's Guide

## What is DNS Reconnaissance?

DNS reconnaissance is the process of querying DNS servers to gather information about a target domain. This information can reveal subdomains, mail servers, name servers, and other infrastructure details.

Think of it as looking up a company's phone number, then finding all their department extensions.

---

## Common DNS Tools

| Tool | Best For | Difficulty |
|------|----------|------------|
| dig | Detailed DNS queries, troubleshooting | Intermediate |
| nslookup | Quick DNS lookups | Beginner |
| host | Simple, concise output | Beginner |
| dnsenum | Automated subdomain discovery | Advanced |
| fierce | DNS reconnaissance | Advanced |
| dnsrecon | Comprehensive DNS enumeration | Advanced |
| theHarvester | OSINT + DNS | Advanced |

---

## The dig Command (Domain Information Groper)

dig is the most powerful and flexible DNS lookup tool. It provides detailed output and supports every record type.

### Installing dig

sudo apt update
sudo apt install dnsutils -y

---

## Basic dig Commands

| Command | What It Does |
|---------|--------------|
| dig domain.com | Default A record lookup |
| dig domain.com A | Get IPv4 address |
| dig domain.com AAAA | Get IPv6 address |
| dig domain.com MX | Find mail servers |
| dig domain.com NS | Find name servers |
| dig domain.com TXT | Get text records |
| dig domain.com CNAME | Get canonical name |
| dig domain.com SOA | Get start of authority |
| dig @1.1.1.1 domain.com | Query specific name server |
| dig +trace domain.com | Show full resolution path |
| dig -x 192.168.1.1 | Reverse lookup (IP to domain) |
| dig +short domain.com | Short, concise answer |
| dig +noall +answer domain.com | Show only answer section |
| dig domain.com ANY | Get all records (often blocked) |

---

## Understanding dig Output

dig google.com

### Output Breakdown

; <<>> DiG 9.18.24 <<>> google.com
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 16449
;; flags: qr rd ad; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 0

;; QUESTION SECTION:
;google.com.                    IN      A

;; ANSWER SECTION:
google.com.             0       IN      A       142.251.47.142

;; Query time: 0 msec
;; SERVER: 172.23.176.1#53(172.23.176.1) (UDP)
;; WHEN: Thu Jun 13 10:45:58 SAST 2024
;; MSG SIZE  rcvd: 54

### What Each Section Means

| Section | Description |
|---------|-------------|
| Header | Query type, status, flags |
| Question Section | What was asked |
| Answer Section | The actual answer |
| Query time | How long it took |
| Server | Which DNS server answered |
| MSG SIZE | Size of the response |

### Key Flags

| Flag | Meaning |
|------|---------|
| qr | Query Response (this is a response) |
| rd | Recursion Desired (we asked for recursion) |
| ad | Authentic Data (resolver considers data authentic) |
| NOERROR | Query succeeded |

---

## Getting Just the Answer

If you only want the IP address, use +short:

dig +short hackthebox.com

Output:
104.18.20.126
104.18.21.126

---

## Other Useful DNS Tools

### nslookup (Simple)

nslookup google.com
nslookup -type=MX google.com
nslookup -type=NS google.com

### host (Concise)

host google.com
host -t MX google.com
host -t NS google.com
host -t TXT google.com

---

## Key Takeaways

- dig is the most powerful DNS lookup tool
- Use +short for concise answers
- Different record types reveal different information
- A records give IP addresses
- MX records reveal email providers
- NS records reveal hosting providers
- TXT records reveal SPF policies and third-party services
- Always check multiple record types during recon
- Be respectful with query rates
- Combine DNS data with other recon techniques
