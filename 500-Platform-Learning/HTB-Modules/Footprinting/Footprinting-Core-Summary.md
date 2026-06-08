---
tags: [footprinting, summary, core, must-know]
---

# Footprinting - What You MUST FUCKING KNOW

## The Absolute Essentials

If you learn NOTHING else from this module, learn these 10 things. Everything else is optimization and edge cases.

---

## 1. The Six Layers of Enumeration

| Layer | Name | What We Find |
|-------|------|--------------|
| 1 | Internet Presence | Domains, subdomains, IPs, cloud instances |
| 2 | Gateway | Firewalls, IPS/IDS, VPNs, segmentation |
| 3 | Accessible Services | Open ports, service types, versions |
| 4 | Processes | Running tasks, data flows, dependencies |
| 5 | Privileges | Users, groups, permissions |
| 6 | OS Setup | OS type, patches, config files |

**The Rule:** Each layer builds on the previous. Don't skip layers.

---

## 2. The Three Core Principles

| # | Principle |
|---|-----------|
| 1 | There is more than meets the eye. Consider all points of view. |
| 2 | Distinguish between what we see and what we do not see. |
| 3 | There are always ways to gain more information. Understand the target. |

---

## 3. The Seven Questions You Must Ask

### About What You CAN See
1. What can we see?
2. What reasons can we have for seeing it?
3. What image does what we see create for us?
4. What do we gain from it?
5. How can we use it?

### About What You CANNOT See
6. What can we not see?
7. What reasons can there be that we do not see?
8. What image results for us from what we do not see?

---

## 4. Domain Information - The Gold Mine

| Record | What It Reveals |
|--------|-----------------|
| A | IPv4 addresses |
| AAAA | IPv6 addresses |
| MX | Mail servers (Google, Outlook, etc.) |
| NS | Hosting provider |
| TXT | Verification keys, SPF, third-party services |
| SOA | Admin email, zone serial |
| CNAME | Aliases to other domains |

**TXT records are GOLD.** They reveal:
- `MS=` - Microsoft services
- `atlassian-domain-verification` - Atlassian suite
- `google-site-verification` - Google services
- `logmein-verification-code` - LogMeIn remote access
- `include:mailgun.org` - Email API
- `include:_spf.google.com` - Google Workspace
- `ip4:` - Internal IP addresses

---

## 5. Certificate Transparency (crt.sh)

Every SSL certificate issued is public record.

`curl -s "https://crt.sh/?q=target.com&output=json" | jq -r '.[].name_value' | sed 's/\*\.//g' | sort -u`

This reveals ALL subdomains ever certificated.

---

## 6. The Most Dangerous Service Settings

| Service | Dangerous Setting | What It Means |
|---------|-------------------|----------------|
| FTP | `anonymous_enable=YES` | Anyone can log in |
| FTP | `anon_upload_enable=YES` | Anonymous can upload files |
| SMB | `guest ok = yes` | No password needed |
| SMB | `writable = yes` | Can upload/modify files |
| NFS | `no_root_squash` | Root on client = root on server |
| NFS | `insecure` | Can use ports above 1024 |
| SMTP | `mynetworks = 0.0.0.0/0` | Open relay - anyone can send spam |
| SNMP | `rwcommunity public 0.0.0.0` | Read-write from anywhere |
| IPMI | Default passwords | root:calvin, ADMIN:ADMIN |
| MySQL | Empty root password | Full database access |
| MSSQL | `sa` with weak password | System admin access |
| Oracle | `scott:tiger` | Default credentials |
| Rsync | Anonymous access | Can download all files |

---

## 7. The One-Liners You MUST Know

### Domain Enum
`curl -s "https://crt.sh/?q=target.com&output=json" | jq -r '.[].name_value' | sed 's/\*\.//g' | sort -u`

### Subdomain Brute
`for sub in $(cat subdomains.txt); do host $sub.target.com | grep "has address"; done`

### DNS Zone Transfer
`dig axfr target.com @nameserver`

### SMTP User Enum
`smtp-user-enum -M VRFY -U users.txt -t target.com`

### SMB Null Session
`smbclient -N -L //target.com`

### SNMP Walk
`snmpwalk -v2c -c public target.com`

### NFS Showmount
`showmount -e target.com`

### FTP Anonymous Download
`wget -m --no-passive ftp://anonymous:anonymous@target.com`

### IPMI Hash Dump
`msfconsole -q -x "use auxiliary/scanner/ipmi/ipmi_dumphashes; set rhosts target; run; exit"`

---

## 8. Default Credentials You MUST Try

| Service | Username | Password |
|---------|----------|----------|
| FTP | anonymous | anonymous |
| SMB | (null) | (null) |
| MySQL | root | (empty) |
| MySQL | root | root |
| MSSQL | sa | (empty) |
| MSSQL | sa | sa |
| Oracle | scott | tiger |
| Oracle | system | manager |
| Oracle | dbsnmp | dbsnmp |
| IPMI (Dell) | root | calvin |
| IPMI (HP) | Administrator | (random 8-char) |
| IPMI (Supermicro) | ADMIN | ADMIN |
| SNMP | public | (read-only) |
| SNMP | private | (read-write) |
| PostgreSQL | postgres | postgres |
| Redis | (none) | (none) |
| MongoDB | (none) | (none) |

---

## 9. What Each Service Reveals

| Service | Port | What You Can Get |
|---------|------|------------------|
| FTP (21) | TCP | Files, anonymous access, upload capability |
| SSH (22) | TCP | Version, OS, users, keys |
| SMTP (25) | TCP | User enumeration, open relay |
| DNS (53) | TCP/UDP | Subdomains, zone transfers, internal IPs |
| HTTP/HTTPS (80,443) | TCP | Web apps, directories, versions |
| POP3 (110) | TCP | Emails, credentials |
| RPC (111) | TCP/UDP | Service list, NFS info |
| NetBIOS (137-139) | TCP/UDP | Hostnames, shares, users |
| SNMP (161) | UDP | System info, processes, network data |
| LDAP (389) | TCP | Directory info, users, groups |
| SMB (445) | TCP | Shares, users, RPC, system info |
| SMTP (587) | TCP | Auth, email sending |
| Rsync (873) | TCP | File shares, anonymous access |
| IMAP (143,993) | TCP | Emails, folders |
| POP3S (995) | TCP | Encrypted email access |
| MSSQL (1433) | TCP | Databases, credentials, code exec |
| Oracle (1521) | TCP | Database access, file upload |
| NFS (2049) | TCP | Shared files, whole directories |
| MySQL (3306) | TCP | Databases, credentials |
| RDP (3389) | TCP | GUI access, system info |
| WinRM (5985,5986) | TCP | Remote command execution |
| IPMI (623) | UDP | Password hashes, system control |

---

## 10. The Golden Rule

> "Our goal is not to get at the systems but to find all the ways to get there."

Enumeration is NOT about running tools. It's about UNDERSTANDING.

- If you're stuck, you haven't enumerated enough
- There's ALWAYS more information
- What you DON'T see is often more important than what you do
- Filtered doesn't mean dead - it means there's a firewall
- Default credentials are everywhere
- Version numbers lead to exploits
- Document EVERYTHING

---

## One Final Thing

If you remember ONLY one command, remember this:

`nmap -sC -sV -p- target.com -oA initial`

Run it. Save it. Analyze it. Then enumerate deeper.

Everything else is just optimization.

**Now go footprint some fucking boxes.**
