---
tags: [module/web-recon, dns, zone-transfer, axfr, subdomains, level/beginner]
---

# DNS Zone Transfers - Beginner's Guide

## What is a DNS Zone Transfer?

A DNS zone transfer is a mechanism for replicating DNS records from one DNS server to another. It's like making a complete photocopy of an entire phone book.

In technical terms, it's a wholesale copy of all DNS records within a zone (a domain and its subdomains) from one name server to another.

---

## Why Zone Transfers Exist

Zone transfers are essential for:

- **Redundancy**: Keeping multiple DNS servers in sync
- **Load balancing**: Distributing DNS queries across servers
- **Consistency**: Ensuring all name servers have the same data

---

## The Zone Transfer Process

### 1. Zone Transfer Request (AXFR)

The secondary DNS server asks the primary server for a copy of all records using the AXFR (Full Zone Transfer) type.

### 2. SOA Record Transfer

The primary server sends its Start of Authority (SOA) record, which contains the zone's serial number.

### 3. DNS Records Transmission

The primary server sends ALL DNS records in the zone:
- A records (IP addresses)
- MX records (mail servers)
- NS records (name servers)
- CNAME records (aliases)
- TXT records (text info)
- Everything else

### 4. Zone Transfer Complete

The primary signals when done.

### 5. Acknowledgement (ACK)

The secondary confirms successful receipt.

---

## The Zone Transfer Vulnerability

In the early days of the internet, DNS servers were often configured to allow ANYONE to request a zone transfer. This was a massive security hole.

### What a Zone Transfer Reveals

| Information | What It Tells You |
|-------------|-------------------|
| All subdomains | Every single subdomain (including hidden ones) |
| IP addresses | Where each subdomain lives |
| Mail servers | Email infrastructure |
| Name servers | Hosting provider details |
| TXT records | SPF policies, verification keys |
| Internal hosts | Sometimes internal IPs are exposed |

This is like getting the complete floor plan of a building instead of just the address.

---

## The Good News (and Bad News)

### Good News
Most modern DNS servers are configured to allow zone transfers ONLY to trusted secondary servers.

### Bad News
Misconfigurations still happen due to:
- Human error
- Outdated practices
- Legacy systems
- Temporary debugging left enabled

---

## Testing for Zone Transfers

### Using dig (Basic)

```bash
dig axfr @nameserver target.com
Example: zonetransfer.me
bash
dig axfr @nsztm1.digi.ninja zonetransfer.me
What a Successful Zone Transfer Looks Like
bash
; <<>> DiG 9.18.12 <<>> axfr @nsztm1.digi.ninja zonetransfer.me
zonetransfer.me.	7200	IN	SOA	nsztm1.digi.ninja. robin.digi.ninja. 2019100801 172800 900 1209600 3600
zonetransfer.me.	300	IN	HINFO	"Casio fx-700G" "Windows XP"
zonetransfer.me.	301	IN	TXT	"google-site-verification=tyP28J7JAUHA9fw2sHXMgcCC0I6XBmmoVi04VlMewxA"
zonetransfer.me.	7200	IN	MX	0 ASPMX.L.GOOGLE.COM.
zonetransfer.me.	7200	IN	A	5.196.105.14
zonetransfer.me.	7200	IN	NS	nsztm1.digi.ninja.
zonetransfer.me.	7200	IN	NS	nsztm2.digi.ninja.
_sip._tcp.zonetransfer.me. 14000 IN	SRV	0 0 5060 www.zonetransfer.me.
canberra-office.zonetransfer.me. 7200 IN A	202.14.81.230
... (50+ records)

;; XFR size: 50 records
What This Reveals
Record Type	Found Example
Subdomains	canberra-office.zonetransfer.me
IP Addresses	5.196.105.14, 202.14.81.230
Mail Servers	ASPMX.L.GOOGLE.COM
Name Servers	nsztm1.digi.ninja, nsztm2.digi.ninja
TXT Records	Google site verification
SRV Records	_sip._tcp service info
Key Takeaways
A zone transfer copies ALL DNS records from one server to another

If misconfigured, ANYONE can request this data

A successful zone transfer reveals every subdomain and their IPs

Modern servers usually block unauthorized transfers

Always check for zone transfers during recon

zonetransfer.me is a legal test site for practicing

One successful transfer is worth thousands of brute-force attempts
