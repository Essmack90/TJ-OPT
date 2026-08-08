# Command Appendix

A pure by-tool/by-area index. Not phase-ordered like [[METHODOLOGY CHEAT SHEET]], not symptom-ordered like [[DECISION TREE]], not a "why does this work" teardown like [[COMMAND BREAKDOWNS]], just: "I know roughly what I want to do, what's the exact syntax and where did we use it."

Split into one file per area (restructured 2026-08-04 from a single flat file, same pattern as [[COMMAND BREAKDOWNS]]) so it stays scannable as it grows. Every entry links back to the module section it came from for the full explanation and context.

## Areas

- [[Reconnaissance & Enumeration]] — WHOIS, Google dorking, passive OSINT, DNS/SMB/SMTP/SNMP enumeration, Nmap, Gobuster, Metasploit quick reference
- [[Web Requests & Delivery]] — Curl (requests/payload delivery), Python HTTP Server
- [[File Inclusion & Traversal]] — directory traversal, LFI, RFI, PHP wrappers, null-byte bypass
- [[File Upload Attacks]] — filter bypasses, PowerShell-via-upload reverse shell, upload+traversal `authorized_keys` overwrite
- [[Shells & Payloads]] — webshells (PHP/ASPX/CFM), reverse shells, SSH key theft/planting, LOLBIN downloaders, cron-based delivery
- [[SQL Injection & Databases]] — MySQL, MSSQL/Impacket, SQLi payloads, sqlmap
- [[Web Applications]] — WordPress, Webmin, command injection diagnosis
- [[Phishing]] — website cloning, clone-patching (BeautifulSoup), credential capture servers
- [[Client-Side Attacks]] — WsgiDAV/WebDAV setup, Windows library file XML, `.lnk` shortcut payloads, VBA macros, one-shot SMB delivery
- [[Locating Public Exploits]] — SearchSploit syntax, patching a found exploit's hardcoded values, cewl targeted wordlists, CSRF-aware patator brute forcing

*(New areas get added here as modules are worked through, Active Directory, Password Attacks, Pivoting, Linux/Windows Privilege Escalation, etc. Note: JuicyPotato, GPP/cPassword decryption, and Kerberoasting already showed up in the [[Arctic]] and [[Active]] box writeups, but deliberately have no area here yet, they're privesc/AD-specific techniques with no matching module coverage so far. See [[Privilege Escalation & Local Exploitation (Breakdowns)|Command Breakdowns' own note]] on the same gap.)*

#### Tags: #CommandAppendix #Methodology
