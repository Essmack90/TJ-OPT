---
tags: MOCs
---
```folder-index-content
```
## Search coverage

- [[OSCP/MODULES/22. Active Directory Introduction and Enumeration|Module 22]] — domain services, SMB shares, gMSA read, and LDAP evidence
- [[OSCP/MODULES/23. Attacking Active Directory Authentication|Module 23]] — Kerberoasting, password reuse, and certificate authentication context
- [[OSCP/MODULES/24. Lateral Movement in Active Directory|Module 24]] — delegated password reset and WMI proof
- [[OSCP/MODULES/16. Password Attacks|Module 16]] — John, PFX, and controlled spraying
- [[OSCP/MODULES/17. Windows Privilege Escalation|Module 17]] — Windows shell identity and local-admin proof; Optimum processor-aware kernel triage and MS16-098 selection
- [[OSCP/MODULES/13. Locating Public Exploits|Module 13]] -- HFS version matching and source-reviewed public exploit use, demonstrated by [[OSCP/BOXES/WRITE UPS/Windows/Optimum|Optimum]]
- [[OSCP/BOXES/WRITE UPS/AD/Search|Search]] — end-to-end application
- [[OSCP/BOXES/WRITE UPS/Linux/Shocker|Shocker]] — Apache CGI Shellshock, Bash callback, and passwordless Perl sudo
- [[OSCP/BOXES/WRITE UPS/Linux/Cap|Cap]] -- IDOR-to-PCAP credential recovery and Python `cap_setuid` escalation
- [[OSCP/BOXES/WRITE UPS/Linux/Management|Management]] -- application-secret recovery, controlled credential reuse, and rdiff-backup argument abuse
- [[OSCP/BOXES/WRITE UPS/Linux/Busqueda|Busqueda]] -- Searchor Python eval injection, Git and Docker credential pivots, Gitea validation, and relative-path sudo execution
- [[OSCP/MODULES/13. Locating Public Exploits|Module 13]] / [[OSCP/MODULES/14. Fixing Exploits|Module 14]] / [[OSCP/MODULES/17. Windows Privilege Escalation|Module 17]] / [[OSCP/MODULES/21. The Metasploit Framework|Module 21]] -- Grandpa's IIS 6.0 WebDAV exploit review, byte-preserving PoC adaptation, worker-process migration, and MS14-058 local escalation

## External Resources

- [HackTricks - Pentesting Index](https://hacktricks.wiki/en/index.html)
- [PayloadsAllTheThings - Methodology and Resources](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Methodology%20and%20Resources)
- [GTFOBins](https://gtfobins.github.io/) for Unix binary abuse where applicable
- [RevShells](https://www.revshells.com/) for shell payloads where applicable
- [CyberChef](https://gchq.github.io/CyberChef/) for encoding and decoding
- [ippsec.rocks](https://ippsec.rocks/) for practical walkthrough searches
## RUNBOOK V2 Stages

- [[OSCP/RUNBOOK V2/Start Here]]
- [[OSCP/RUNBOOK V2/Port Triage]]
- [[OSCP/RUNBOOK V2/Linux - Service Scan]]
- [[OSCP/RUNBOOK V2/Linux - Command Injection]]
- [[OSCP/RUNBOOK V2/Linux - Credential Search]]
- [[OSCP/RUNBOOK V2/Linux - Docker Enumeration]]
- [[OSCP/RUNBOOK V2/Linux - Sudo Check]]

## Hub Docs

- [[METHODOLOGY CHEAT SHEET/METHODOLOGY CHEAT SHEET]]
- [[COMMAND APPENDIX/COMMAND APPENDIX]]
- [[DECISION TREE/DECISION TREE]]
- [[COMMAND BREAKDOWNS/COMMAND BREAKDOWNS]]

## Related Boxes

- [[OSCP/BOXES/WRITE UPS/Linux/clamAV|clamAV]] -- reconnaissance and exploit workflow
- [[OSCP/BOXES/WRITE UPS/AD/Forest|Forest]] -- enumeration and privilege escalation
- [[OSCP/BOXES/WRITE UPS/Linux/Busqueda|Busqueda]] -- chained web RCE, credential reuse, Docker inspection, and sudo path abuse
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
