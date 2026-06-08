---
tags: [index, footprinting, enumeration, module-index]
---

# Footprinting Module - Complete Index

## Module Overview

This index covers all Footprinting-related modules from the HTB CPTS pathway. Use this as your central navigation point for everything related to initial enumeration and service discovery.

---

## Core Concepts

| Module | Description | Level |
|--------|-------------|-------|
| Enumeration-Principles | The mindset and methodology of enumeration | Beginner |
| Enumeration-Methodology | The six-layer framework for systematic enumeration | Beginner |
| Domain-Information | Passive domain enumeration (WHOIS, DNS, crt.sh) | Beginner |
| Cloud-Resources | Finding cloud storage (AWS, Azure, GCP) | Intermediate |
| Staff-Enumeration | OSINT on employees (LinkedIn, GitHub, job posts) | Intermediate |

---

## Service-Specific Modules

| Module | Protocol | Ports | Level |
|--------|----------|-------|-------|
| FTP | File Transfer Protocol | 21 | Beginner |
| SMB | Server Message Block | 139,445 | Beginner |
| NFS | Network File System | 111,2049 | Beginner |
| DNS | Domain Name System | 53 | Beginner |
| SMTP | Simple Mail Transfer Protocol | 25,465,587 | Beginner |
| IMAP-POP3 | Email Retrieval | 110,143,993,995 | Beginner |
| SNMP | Simple Network Management Protocol | 161 (UDP) | Intermediate |
| MySQL | MySQL Database | 3306 | Intermediate |
| MSSQL | Microsoft SQL Server | 1433 | Intermediate |
| Oracle-TNS | Oracle Database | 1521 | Advanced |
| IPMI | Intelligent Platform Management Interface | 623 (UDP) | Advanced |
| Linux-Remote-Management | SSH, Rsync, R-services | 22,873,512-514 | Intermediate |
| Windows-Remote-Management | RDP, WinRM, WMI | 3389,5985,5986,135 | Intermediate |

---

## Reference Materials

| Document | Description |
|----------|-------------|
| Footprinting-Cheatsheet | Complete command reference |
| Footprinting-Core-Summary | What you MUST know |

---

## Quick Navigation by Task

| Task | Recommended Module |
|------|-------------------|
| Learn enumeration mindset | Enumeration-Principles |
| Understand methodology | Enumeration-Methodology |
| Find subdomains | Domain-Information |
| Find cloud buckets | Cloud-Resources |
| Research employees | Staff-Enumeration |
| Enumerate FTP | FTP |
| Enumerate SMB | SMB |
| Enumerate NFS | NFS |
| Enumerate DNS | DNS |
| Enumerate SMTP | SMTP |
| Enumerate email servers | IMAP-POP3 |
| Enumerate SNMP | SNMP |
| Enumerate MySQL | MySQL |
| Enumerate MSSQL | MSSQL |
| Enumerate Oracle | Oracle-TNS |
| Enumerate IPMI | IPMI |
| Enumerate Linux remote services | Linux-Remote-Management |
| Enumerate Windows remote services | Windows-Remote-Management |
| Find a command | Footprinting-Cheatsheet |
| Review essentials | Footprinting-Core-Summary |

---

## Quick Command Reference by Service

### DNS
dig axfr target.com @nameserver
curl -s "https://crt.sh/?q=target.com&output=json" | jq -r '.[].name_value'

### FTP
ftp target.com
wget -m --no-passive ftp://anonymous:anonymous@target.com

### SMB
smbclient -N -L //target.com
enum4linux-ng.py target.com -A

### NFS
showmount -e target.com
mount -t nfs target.com:/share ./mnt/ -o nolock

### SMTP
smtp-user-enum -M VRFY -U users.txt -t target.com
nc -nv target.com 25

### SNMP
snmpwalk -v2c -c public target.com
onesixtyone -c community-strings.list target.com

### MySQL
mysql -u root -h target.com

### MSSQL
mssqlclient.py user@target.com -windows-auth

### Oracle
./odat.py all -s target.com
sqlplus scott/tiger@target.com/XE

### IPMI
msfconsole -q -x "use auxiliary/scanner/ipmi/ipmi_dumphashes; set rhosts target; run; exit"

### RDP
xfreerdp /u:user /p:pass /v:target.com
rdp-sec-check.pl target.com

### WinRM
evil-winrm -i target.com -u user -p pass

### WMI
wmiexec.py user:pass@target.com "hostname"

### SSH
ssh-audit.py target.com
ssh user@target.com -o PreferredAuthentications=password

### Rsync
rsync rsync://target.com/

---

## Service Port Quick Reference

| Port | Service | Protocol |
|------|---------|----------|
| 21 | FTP | TCP |
| 22 | SSH | TCP |
| 23 | Telnet | TCP |
| 25 | SMTP | TCP |
| 53 | DNS | TCP/UDP |
| 110 | POP3 | TCP |
| 111 | RPC | TCP/UDP |
| 135 | WMI | TCP |
| 137-139 | NetBIOS | TCP/UDP |
| 143 | IMAP | TCP |
| 161 | SNMP | UDP |
| 389 | LDAP | TCP |
| 445 | SMB | TCP |
| 465 | SMTPS | TCP |
| 512-514 | R-services | TCP |
| 587 | SMTP | TCP |
| 623 | IPMI | UDP |
| 873 | Rsync | TCP |
| 993 | IMAPS | TCP |
| 995 | POP3S | TCP |
| 1433 | MSSQL | TCP |
| 1521 | Oracle | TCP |
| 2049 | NFS | TCP |
| 3306 | MySQL | TCP |
| 3389 | RDP | TCP |
| 5432 | PostgreSQL | TCP |
| 5985 | WinRM | TCP |
| 5986 | WinRM SSL | TCP |

---

## Key Takeaways by Module

### Enumeration-Principles
- Enumeration is a mindset, not a toolset
- Distinguish between visible and invisible
- There's ALWAYS more information

### Enumeration-Methodology
- Six layers: Internet Presence to Gateway to Services to Processes to Privileges to OS
- Each layer builds on the previous
- Not every gap leads inside

### Domain-Information
- crt.sh reveals all subdomains
- TXT records expose third-party services
- SPF records reveal internal IPs

### Cloud-Resources
- DNS entries like s3.amazonaws.com = cloud storage
- Google dorks find exposed buckets
- GrayHatWarfare searches public cloud storage

### Staff-Enumeration
- Job postings reveal tech stack
- LinkedIn shows employee skills
- GitHub can leak credentials

### FTP
- Anonymous access may be enabled
- Download all files with wget -m
- Upload may lead to RCE

### SMB
- Null sessions may list shares
- rpcclient enumerates users and groups
- Dangerous: guest ok, writable

### NFS
- showmount -e lists shares
- Mount to access files
- UID/GID mapping issues
- no_root_squash = root access

### DNS
- Zone transfer (AXFR) can leak everything
- Subdomain brute forcing finds hidden hosts
- TXT records reveal services

### SMTP
- VRFY/EXPN/RCPT enumerate users
- Open relays allow spam
- 252 responses may be false positives

### IMAP-POP3
- POP3 downloads emails, IMAP syncs
- CAPA shows server capabilities
- Emails contain sensitive data

### SNMP
- Community strings = passwords
- public = read-only, private = read-write
- snmpwalk reveals massive system info

### MySQL
- Default root with empty password
- FILE privilege = file read/write
- INFORMATION_SCHEMA reveals all

### MSSQL
- Windows Authentication integrated with AD
- xp_cmdshell = command execution
- Linked servers enable lateral movement

### Oracle-TNS
- SIDs must be guessed or brute-forced
- Default credentials (scott:tiger) are common
- UTL_FILE can upload files

### IPMI
- Port 623 UDP
- RAKP flaw leaks password hashes
- Default credentials are common
- BMC access = physical access

### Linux-Remote-Management
- SSH keys better than passwords
- Rsync may expose files without auth
- R-services are ancient and insecure

### Windows-Remote-Management
- RDP gives GUI access
- WinRM gives command-line access
- WMI is deep system management
- Pass-the-hash works on all three

---

## Learning Path

Enumeration Principles
Enumeration Methodology
Domain Information
Cloud Resources
Staff Enumeration
Service-Specific Modules (any order)
Practice with Footprinting Cheatsheet
Review Core Summary

---

## Additional Resources

| Resource | Description |
|----------|-------------|
| crt.sh | Certificate transparency logs |
| GrayHatWarfare | Public cloud storage search |
| Shodan | Internet device search |
| Censys | Internet asset search |
| Hunter.io | Email pattern discovery |
| Dehashed | Breached credential search |

---

## Version Information

Module Version: 1.0
Last Updated: 2026-03-17
CPTS Pathway: Footprinting
