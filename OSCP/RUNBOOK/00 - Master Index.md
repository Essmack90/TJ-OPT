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
- [[Box Close-Out Checklist]] — run this before boxdone, every box

---

## Discovery
- [[Port Scan - Full]] ← [[06. Information Gathering|Information Gathering]]
- [[Port Scan - Results Triage]] ← [[06. Information Gathering|Information Gathering]]

## Footprinting — Services
- [[SMB - Null Session]] ← [[06. Information Gathering|Information Gathering]]
> **PENDING STAGE** — Not yet written. See [[COMMAND APPENDIX/Reconnaissance & Enumeration]] and [[DECISION TREE/Reconnaissance & Enumeration (Decision Tree)]] in the meantime. SMB authenticated enumeration, SMB share enumeration, FTP anonymous access, FTP authenticated access, SSH initial access, DNS enumeration, and SMTP user enumeration are covered there.
- [[SMTP - Exploitation]] ← [[13. Locating Public Exploits|Locating Public Exploits]], [[06. Information Gathering|Information Gathering]]
- [[SNMP - Enumeration]] ← [[06. Information Gathering|Information Gathering]]
- [[PostgreSQL - Initial Access]] ← [[06. Information Gathering|Information Gathering]], [[10. SQL Injection Attacks|SQL Injection Attacks]]
- [[PostgreSQL - COPY TO PROGRAM RCE]] ← [[10. SQL Injection Attacks|SQL Injection Attacks]]

## Footprinting — Web
- [[HTTP - Initial Recon]] ← [[08. Introduction to Web Application Attacks|Introduction to Web Application Attacks]]
- [[HTTP - Directory Brute]] ← [[08. Introduction to Web Application Attacks|Introduction to Web Application Attacks]], [[06. Information Gathering|Information Gathering]]
> **PENDING STAGE** — Not yet written. See [[COMMAND APPENDIX/Web Applications]] and [[DECISION TREE/Web Applications (Decision Tree)]] in the meantime. HTTP CMS detection, subdomain enumeration, and virtual-host enumeration are covered there.

## Foothold
- [[Foothold - Public Exploit]] ← [[13. Locating Public Exploits|Locating Public Exploits]], [[14. Fixing Exploits|Fixing Exploits]]
> **PENDING STAGE** — Not yet written. See [[COMMAND APPENDIX/Web Applications]], [[COMMAND APPENDIX/Password Attacks]], and [[DECISION TREE/Web Applications (Decision Tree)]] in the meantime. Web exploitation, default credentials, and file-upload footholds are covered there.
- [[Foothold - SQLi to Shell]] ← [[10. SQL Injection Attacks|SQL Injection Attacks]], [[09. Common Web Application Attacks|Common Web Application Attacks]]
- [[WordPress - Simple File List Upload]] ← [[08. Introduction to Web Application Attacks|Introduction to Web Application Attacks]], [[13. Locating Public Exploits|Locating Public Exploits]]

## Shell Handling
- [[Shell - Upgrade]] ← [[09. Common Web Application Attacks|Common Web Application Attacks]]
> **PENDING STAGE** — Not yet written. See [[COMMAND APPENDIX/Shells & Payloads]], [[COMMAND APPENDIX/File Transfers]], and [[DECISION TREE/Shells & Payloads (Decision Tree)]] in the meantime.

## PrivEsc — Linux
- [[PrivEsc Linux - SUID]] ← [[18. Linux Privilege Escalation|Linux Privilege Escalation]]
- [[PrivEsc Linux - Sudo]] ← [[18. Linux Privilege Escalation|Linux Privilege Escalation]]
- [[PrivEsc Linux - Kernel]] ← [[18. Linux Privilege Escalation|Linux Privilege Escalation]], [[13. Locating Public Exploits|Locating Public Exploits]]
> **PENDING STAGE** — Not yet written. See [[COMMAND APPENDIX/Linux Privilege Escalation]] and [[DECISION TREE/Linux Privilege Escalation (Decision Tree)]] in the meantime. Linux initial enumeration, cron, capabilities, writable configuration, NFS, and kernel paths are covered there.
- [[PrivEsc Linux - UDF]] ← [[18. Linux Privilege Escalation|Linux Privilege Escalation]], [[10. SQL Injection Attacks|SQL Injection Attacks]]
- [[PrivEsc Linux - Tar Wildcard]] ← [[18. Linux Privilege Escalation|Linux Privilege Escalation]]

## PrivEsc — Windows
- [[PrivEsc Windows - Scheduled Tasks]] ← [[17. Windows Privilege Escalation|Windows Privilege Escalation]]
> **PENDING STAGE** — Not yet written. See [[COMMAND APPENDIX/Windows Privilege Escalation]] and [[DECISION TREE/Windows Privilege Escalation (Decision Tree)]] in the meantime. Windows initial enumeration, services, unquoted paths, registry, token impersonation, DLL hijacking, and kernel paths are covered there.

## Credentials
> **PENDING STAGE** — Not yet written. See [[COMMAND APPENDIX/Password Attacks]] and [[DECISION TREE/Secrets & Credentials (Decision Tree)]] in the meantime. Hash cracking, password spraying, reuse checks, and pass-the-hash are covered there.

## Post-Exploitation
> **PENDING STAGE** — Not yet written. See [[COMMAND APPENDIX/Password Attacks]], [[COMMAND APPENDIX/Active Directory]], and [[DECISION TREE/Active Directory (Decision Tree)]] in the meantime. Credential dumping, lateral movement, and persistence are covered there.

## Web App Track
- [[Web App - LFI]] ← [[09. Common Web Application Attacks|Common Web Application Attacks]]
- [[Web App - RFI]] ← [[09. Common Web Application Attacks|Common Web Application Attacks]]
- [[Web App - SQLi]] ← [[10. SQL Injection Attacks|SQL Injection Attacks]]
- [[PrivEsc Linux - UDF]] ← [[18. Linux Privilege Escalation|Linux Privilege Escalation]], [[10. SQL Injection Attacks|SQL Injection Attacks]]
- [[Web App - Command Injection]] ← [[09. Common Web Application Attacks|Common Web Application Attacks]]
- [[Web App - XXE]]
> **PENDING STAGE** — Not yet written. See [[COMMAND APPENDIX/Web Applications]], [[COMMAND APPENDIX/File Upload Attacks]], and [[DECISION TREE/Web Applications (Decision Tree)]] in the meantime. File upload, SSRF, and IDOR are covered there.

## Active Directory Track
> **PENDING STAGE** — Not yet written. See [[COMMAND APPENDIX/Active Directory]] and [[DECISION TREE/Active Directory (Decision Tree)]] in the meantime. Initial enumeration, Kerberoasting, AS-REP roasting, ACL abuse, pass-the-ticket, DCSync, lateral movement, Golden Ticket, Shadow Credentials, password spraying, and BloodHound are covered there.

## Pivoting / Tunneling Track
> **PENDING STAGE** — Not yet written. See [[COMMAND APPENDIX/Port Redirection and SSH Tunneling]] and [[DECISION TREE/Port Redirection and SSH Tunneling (Decision Tree)]] in the meantime. Socat forwarding, SSH local/dynamic/remote forwarding, Chisel, Ligolo-ng, and Meterpreter autoroute are covered there.

## Phishing / Client-Side Track
> **PENDING STAGE** — Not yet written. See [[COMMAND APPENDIX/Phishing]], [[COMMAND APPENDIX/Client-Side Attacks]], and [[DECISION TREE/Phishing (Decision Tree)]] in the meantime. Clone pages, macro payloads, and library-file client-side attacks are covered there.

## AWS / Cloud Track
> **PENDING STAGE** — Not yet written. See [[COMMAND APPENDIX/Cloud Enumeration]] and [[DECISION TREE/Cloud Enumeration (Decision Tree)]] in the meantime. AWS reconnaissance, S3 enumeration, IAM enumeration, Pacu privilege escalation, CI/CD poisoning, and Terraform state review are covered there.

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
