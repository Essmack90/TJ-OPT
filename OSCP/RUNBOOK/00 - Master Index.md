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
- [[Port Scan - Full]] ← [[06. Information Gathering|Information Gathering]]
- [[Port Scan - Results Triage]] ← [[06. Information Gathering|Information Gathering]]

## Footprinting — Services
- [[SMB - Null Session]] ← [[06. Information Gathering|Information Gathering]]
- [[SMB - Authenticated Enum]] ← [[06. Information Gathering|Information Gathering]]
- [[SMB - Share Enumeration]] ← [[06. Information Gathering|Information Gathering]]
- [[FTP - Anonymous]] ← [[06. Information Gathering|Information Gathering]]
- [[FTP - Authenticated]] ← [[06. Information Gathering|Information Gathering]]
- [[SSH - Initial]] ← [[06. Information Gathering|Information Gathering]]
- [[DNS - Enumeration]] ← [[06. Information Gathering|Information Gathering]]
- [[SMTP - User Enum]] ← [[06. Information Gathering|Information Gathering]]
- [[SNMP - Enumeration]] ← [[06. Information Gathering|Information Gathering]]

## Footprinting — Web
- [[HTTP - Initial Recon]] ← [[08. Introduction to Web Application Attacks|Introduction to Web Application Attacks]]
- [[HTTP - Directory Brute]] ← [[08. Introduction to Web Application Attacks|Introduction to Web Application Attacks]]
- [[HTTP - CMS Detection]] ← [[08. Introduction to Web Application Attacks|Introduction to Web Application Attacks]]
- [[HTTP - Subdomain Enum]] ← [[06. Information Gathering|Information Gathering]]
- [[HTTP - Virtual Host Enum]] ← [[06. Information Gathering|Information Gathering]]

## Foothold
- [[Foothold - Web Exploit]] ← [[09. Common Web Application Attacks|Common Web Application Attacks]], [[08. Introduction to Web Application Attacks|Introduction to Web Application Attacks]]
- [[Foothold - Public Exploit]] ← [[13. Locating Public Exploits|Locating Public Exploits]], [[14. Fixing Exploits|Fixing Exploits]]
- [[Foothold - Default Creds]] ← [[16. Password Attacks|Password Attacks]]
- [[Foothold - File Upload]] ← [[09. Common Web Application Attacks|Common Web Application Attacks]]
- [[Foothold - SQLi to Shell]] ← [[10. SQL Injection Attacks|SQL Injection Attacks]]

## Shell Handling
- [[Shell - Upgrade]] ← [[09. Common Web Application Attacks|Common Web Application Attacks]]
- [[Shell - Stabilise]] ← [[09. Common Web Application Attacks|Common Web Application Attacks]]
- [[Shell - Transfer Files]] ← [[17. Windows Privilege Escalation]]

## PrivEsc — Linux
- [[PrivEsc Linux - Initial Enum]] ← [[18. Linux Privilege Escalation|Linux Privilege Escalation]]
- [[PrivEsc Linux - SUID]] ← [[18. Linux Privilege Escalation|Linux Privilege Escalation]]
- [[PrivEsc Linux - Cron]] ← [[18. Linux Privilege Escalation|Linux Privilege Escalation]]
- [[PrivEsc Linux - Sudo]] ← [[18. Linux Privilege Escalation|Linux Privilege Escalation]]
- [[PrivEsc Linux - Capabilities]] ← [[18. Linux Privilege Escalation|Linux Privilege Escalation]]
- [[PrivEsc Linux - Writable Config]] ← [[18. Linux Privilege Escalation|Linux Privilege Escalation]]
- [[PrivEsc Linux - NFS]] ← [[18. Linux Privilege Escalation|Linux Privilege Escalation]]
- [[PrivEsc Linux - Kernel]] ← [[18. Linux Privilege Escalation|Linux Privilege Escalation]]

## PrivEsc — Windows
- [[PrivEsc Windows - Initial Enum]] ← [[17. Windows Privilege Escalation|Windows Privilege Escalation]]
- [[PrivEsc Windows - Services]] ← [[17. Windows Privilege Escalation|Windows Privilege Escalation]]
- [[PrivEsc Windows - Unquoted Path]] ← [[17. Windows Privilege Escalation|Windows Privilege Escalation]]
- [[PrivEsc Windows - Scheduled Tasks]] ← [[17. Windows Privilege Escalation|Windows Privilege Escalation]]
- [[PrivEsc Windows - Registry]] ← [[17. Windows Privilege Escalation|Windows Privilege Escalation]]
- [[PrivEsc Windows - Token Impersonation]] ← [[17. Windows Privilege Escalation|Windows Privilege Escalation]]
- [[PrivEsc Windows - DLL Hijack]] ← [[17. Windows Privilege Escalation|Windows Privilege Escalation]]
- [[PrivEsc Windows - Kernel]] ← [[17. Windows Privilege Escalation|Windows Privilege Escalation]]

## Credentials
- [[Creds - Hash Cracking]] ← [[16. Password Attacks|Password Attacks]]
- [[Creds - Password Spray]] ← [[16. Password Attacks|Password Attacks]]
- [[Creds - Reuse Check]] ← [[16. Password Attacks|Password Attacks]]
- [[Creds - Pass the Hash]] ← [[16. Password Attacks|Password Attacks]]

## Post-Exploitation
- [[Post - Credential Dumping]] ← [[16. Password Attacks|Password Attacks]], [[23. Attacking Active Directory Authentication|Attacking Active Directory Authentication]]
- [[Post - Lateral Movement]] ← [[24. Lateral Movement in Active Directory|Lateral Movement in Active Directory]]
- [[Post - Persistence]]

## Web App Track
- [[Web App - LFI]] ← [[09. Common Web Application Attacks|Common Web Application Attacks]]
- [[Web App - RFI]] ← [[09. Common Web Application Attacks|Common Web Application Attacks]]
- [[Web App - SQLi]] ← [[10. SQL Injection Attacks|SQL Injection Attacks]]
- [[Web App - File Upload]] ← [[09. Common Web Application Attacks|Common Web Application Attacks]]
- [[Web App - Command Injection]] ← [[09. Common Web Application Attacks|Common Web Application Attacks]]
- [[Web App - SSRF]] ← [[09. Common Web Application Attacks|Common Web Application Attacks]]
- [[Web App - XXE]]
- [[Web App - IDOR]]

## Active Directory Track
- [[AD - Initial Enum]] ← [[22. Active Directory Introduction and Enumeration|Active Directory Introduction and Enumeration]]
- [[AD - Kerberoast]] ← [[23. Attacking Active Directory Authentication|Attacking Active Directory Authentication]]
- [[AD - AS-REP Roast]] ← [[23. Attacking Active Directory Authentication|Attacking Active Directory Authentication]]
- [[AD - ACL Abuse]] ← [[22. Active Directory Introduction and Enumeration|Active Directory Introduction and Enumeration]]
- [[AD - Pass the Ticket]] ← [[23. Attacking Active Directory Authentication|Attacking Active Directory Authentication]]
- [[AD - DCSync]] ← [[23. Attacking Active Directory Authentication|Attacking Active Directory Authentication]]
- [[AD - Lateral Movement]] ← [[24. Lateral Movement in Active Directory|Lateral Movement in Active Directory]]
- [[AD - Golden Ticket]] ← [[24. Lateral Movement in Active Directory|Lateral Movement in Active Directory]]
- [[AD - Shadow Credentials]] ← [[23. Attacking Active Directory Authentication|Attacking Active Directory Authentication]]
- [[AD - Password Spray]] ← [[22. Active Directory Introduction and Enumeration|Active Directory Introduction and Enumeration]]
- [[AD - BloodHound]] ← [[22. Active Directory Introduction and Enumeration|Active Directory Introduction and Enumeration]]

## Pivoting / Tunneling Track
- [[Pivot - Socat Forward]] ← [[19. Port Redirection and SSH Tunneling|Port Redirection and SSH Tunneling]]
- [[Pivot - SSH Local Forward]] ← [[19. Port Redirection and SSH Tunneling|Port Redirection and SSH Tunneling]]
- [[Pivot - SSH Dynamic SOCKS]] ← [[19. Port Redirection and SSH Tunneling|Port Redirection and SSH Tunneling]]
- [[Pivot - SSH Remote Forward]] ← [[19. Port Redirection and SSH Tunneling|Port Redirection and SSH Tunneling]]
- [[Pivot - Chisel]] ← [[20. Tunneling Through Deep Packet Inspection|Tunneling Through Deep Packet Inspection]]
- [[Pivot - Ligolo-ng]] ← [[19. Port Redirection and SSH Tunneling|Port Redirection and SSH Tunneling]]
- [[Pivot - Meterpreter Autoroute]] ← [[21. The Metasploit Framework|The Metasploit Framework]]

## Phishing / Client-Side Track
- [[Phish - Clone Page]] ← [[11. Phishing Basics|Phishing Basics]]
- [[Phish - Macro Payload]] ← [[12. Client-Side Attacks|Client-Side Attacks]]
- [[Phish - Library File]] ← [[12. Client-Side Attacks|Client-Side Attacks]]

## AWS / Cloud Track
- [[Cloud - AWS Recon]] ← [[25. Enumerating AWS Cloud Infrastructure|Enumerating AWS Cloud Infrastructure]]
- [[Cloud - S3 Enumeration]] ← [[25. Enumerating AWS Cloud Infrastructure|Enumerating AWS Cloud Infrastructure]]
- [[Cloud - IAM Enum]] ← [[25. Enumerating AWS Cloud Infrastructure|Enumerating AWS Cloud Infrastructure]]
- [[Cloud - Pacu PrivEsc]] ← [[25. Enumerating AWS Cloud Infrastructure|Enumerating AWS Cloud Infrastructure]]
- [[Cloud - CI/CD Poison]] ← [[26. Attacking AWS Cloud Infrastructure|Attacking AWS Cloud Infrastructure]]
- [[Cloud - Terraform State]] ← [[26. Attacking AWS Cloud Infrastructure|Attacking AWS Cloud Infrastructure]]

---

## box_sources — How Stage Notes Grow

Every stage note file carries a `box_sources:` YAML frontmatter key listing the boxes that informed it. After finishing a box, add its name to the `box_sources:` list of every stage note you used. This is how "Port Scan - Full taught me what I know about clamAV" becomes "Port Scan - Full knows about clamAV, Sea, Photobomb, …" over time.

Format in stage note frontmatter:
```yaml
---
tags: [oscp, port-scan, runbook]
box_sources: [clamAV, Sea, Photobomb]
---
```

The habit that drives this is in [[OSCP Habits - Screenshot & Loot#End of Box — Vault Feedback Loop|Habits: Vault Feedback Loop]].

---

## External Resources
- [GTFOBins](https://gtfobins.github.io) — SUID / sudo / capabilities / shell escape
- [RevShells](https://www.revshells.com) — shell one-liners, all languages
- [CyberChef](https://gchq.github.io/CyberChef/) — encode/decode/transform anything
- [PayloadsAllTheThings (GitHub)](https://github.com/swisskyrepo/PayloadsAllTheThings) — payloads by category
- [HackTricks](https://book.hacktricks.xyz) — technique reference (also available as local Obsidian vault at `~/Documents/Obsidian/HackTricks`)
- [ippsec.rocks](https://ippsec.rocks) — search HTB techniques by keyword
- **Internal quick-reference** (no internet needed): [[Active Directory]], [[Linux Privilege Escalation]], [[Windows Privilege Escalation]], [[Port Redirection and SSH Tunneling]], [[Reconnaissance & Enumeration]], [[SQL Injection & Databases]]
