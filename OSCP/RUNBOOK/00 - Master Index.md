# Runbook — Master Index

*Decision-tree runbook for HTB/OSCP box work.*
*Each link is a separate file. "Go to" columns in stage notes always point to a new file, never an anchor on the same page.*
*Naming convention: `[Parent Stage] - [Sub-stage].md`*
*Links with no target file = stage note not yet created. Build it when a box first needs it.*

---

## Workflow Quick Links
- [[OSCP Habits - Screenshot & Loot]] — what to capture and when
- [[FAQ - Quick Answers]] — stuck? check here first
- [[Box Report Template]] — copy this at the end of every box

---

## Discovery
- [[Port Scan - Full]] ← [[Information Gathering]]
- [[Port Scan - Results Triage]] ← [[Information Gathering]]

## Footprinting — Services
- [[SMB - Null Session]] ← [[Information Gathering]], [[Footprinting]]
- [[SMB - Authenticated Enum]] ← [[Information Gathering]], [[Footprinting]]
- [[SMB - Share Enumeration]] ← [[Information Gathering]], [[Footprinting]]
- [[FTP - Anonymous]] ← [[Information Gathering]], [[Footprinting]]
- [[FTP - Authenticated]] ← [[Information Gathering]], [[Footprinting]]
- [[SSH - Initial]] ← [[Information Gathering]]
- [[DNS - Enumeration]] ← [[Information Gathering]], [[Footprinting]]
- [[SMTP - User Enum]] ← [[Information Gathering]], [[Footprinting]]
- [[SNMP - Enumeration]] ← [[Information Gathering]]

## Footprinting — Web
- [[HTTP - Initial Recon]] ← [[Introduction to Web Application Attacks]]
- [[HTTP - Directory Brute]] ← [[Introduction to Web Application Attacks]]
- [[HTTP - CMS Detection]] ← [[Introduction to Web Application Attacks]]
- [[HTTP - Subdomain Enum]] ← [[Information Gathering - Web Edition (HTB Supplementary)]]
- [[HTTP - Virtual Host Enum]] ← [[Information Gathering - Web Edition (HTB Supplementary)]]

## Foothold
- [[Foothold - Web Exploit]] ← [[Common Web Application Attacks]], [[Introduction to Web Application Attacks]]
- [[Foothold - Public Exploit]] ← [[Locating Public Exploits]], [[Fixing Exploits]]
- [[Foothold - Default Creds]] ← [[Password Attacks]]
- [[Foothold - File Upload]] ← [[Common Web Application Attacks]]
- [[Foothold - SQLi to Shell]] ← [[SQL Injection Attacks]]

## Shell Handling
- [[Shell - Upgrade]] ← [[Common Web Application Attacks]]
- [[Shell - Stabilise]] ← [[Common Web Application Attacks]]
- [[Shell - Transfer Files]] ← [[File Transfers (HTB Supplementary)]]

## PrivEsc — Linux
- [[PrivEsc Linux - Initial Enum]] ← [[Linux Privilege Escalation]]
- [[PrivEsc Linux - SUID]] ← [[Linux Privilege Escalation]]
- [[PrivEsc Linux - Cron]] ← [[Linux Privilege Escalation]]
- [[PrivEsc Linux - Sudo]] ← [[Linux Privilege Escalation]]
- [[PrivEsc Linux - Capabilities]] ← [[Linux Privilege Escalation]]
- [[PrivEsc Linux - Writable Config]] ← [[Linux Privilege Escalation]]
- [[PrivEsc Linux - NFS]] ← [[Linux Privilege Escalation]]
- [[PrivEsc Linux - Kernel]] ← [[Linux Privilege Escalation]]

## PrivEsc — Windows
- [[PrivEsc Windows - Initial Enum]] ← [[Windows Privilege Escalation]]
- [[PrivEsc Windows - Services]] ← [[Windows Privilege Escalation]]
- [[PrivEsc Windows - Unquoted Path]] ← [[Windows Privilege Escalation]]
- [[PrivEsc Windows - Scheduled Tasks]] ← [[Windows Privilege Escalation]]
- [[PrivEsc Windows - Registry]] ← [[Windows Privilege Escalation]]
- [[PrivEsc Windows - Token Impersonation]] ← [[Windows Privilege Escalation]]
- [[PrivEsc Windows - DLL Hijack]] ← [[Windows Privilege Escalation]]
- [[PrivEsc Windows - Kernel]] ← [[Windows Privilege Escalation]]

## Credentials
- [[Creds - Hash Cracking]] ← [[Password Attacks]]
- [[Creds - Password Spray]] ← [[Password Attacks]]
- [[Creds - Reuse Check]] ← [[Password Attacks]]
- [[Creds - Pass the Hash]] ← [[Password Attacks]]

## Post-Exploitation
- [[Post - Credential Dumping]] ← [[Password Attacks]], [[Attacking Active Directory Authentication]]
- [[Post - Lateral Movement]] ← [[Lateral Movement in Active Directory]]
- [[Post - Persistence]]

## Web App Track
- [[Web App - LFI]] ← [[Common Web Application Attacks]]
- [[Web App - RFI]] ← [[Common Web Application Attacks]]
- [[Web App - SQLi]] ← [[SQL Injection Attacks]]
- [[Web App - File Upload]] ← [[Common Web Application Attacks]]
- [[Web App - Command Injection]] ← [[Common Web Application Attacks]]
- [[Web App - SSRF]] ← [[Common Web Application Attacks]]
- [[Web App - XXE]]
- [[Web App - IDOR]]

## Active Directory Track
- [[AD - Initial Enum]] ← [[Active Directory Introduction and Enumeration]]
- [[AD - Kerberoast]] ← [[Attacking Active Directory Authentication]]
- [[AD - AS-REP Roast]] ← [[Attacking Active Directory Authentication]]
- [[AD - ACL Abuse]] ← [[Active Directory Introduction and Enumeration]]
- [[AD - Pass the Ticket]] ← [[Attacking Active Directory Authentication]]
- [[AD - DCSync]] ← [[Attacking Active Directory Authentication]]
- [[AD - Lateral Movement]] ← [[Lateral Movement in Active Directory]]

---

## External Resources
- [GTFOBins](https://gtfobins.github.io). SUID / sudo / capabilities / shell escape
- [RevShells](https://www.revshells.com), shell one-liners, all languages
- [CyberChef](https://gchq.github.io/CyberChef/), encode/decode/transform anything
- [PayloadsAllTheThings (GitHub)](https://github.com/swisskyrepo/PayloadsAllTheThings), payloads by category
- [HackTricks (GitHub)](https://github.com/HackTricks-wiki/hacktricks), technique reference
- [ippsec.rocks](https://ippsec.rocks), search HTB techniques by keyword
