# Command Appendix

A pure by-tool/by-area index. Not phase-ordered like [[METHODOLOGY CHEAT SHEET]], not symptom-ordered like [[DECISION TREE]], not a "why does this work" teardown like [[COMMAND BREAKDOWNS]], just: "I know roughly what I want to do, what's the exact syntax and where did we use it."

Split into one file per area (restructured 2026-08-04 from a single flat file, same pattern as [[COMMAND BREAKDOWNS]]) so it stays scannable as it grows. Every entry links back to the module section it came from for the full explanation and context.

## Areas

- [[Reconnaissance & Enumeration]] — Nmap, Gobuster
- [[Web Requests & Delivery]] — Curl (requests/payload delivery), Python HTTP Server
- [[File Inclusion & Traversal]] — directory traversal, LFI, RFI, PHP wrappers
- [[File Upload Attacks]] — upload filter bypasses
- [[Shells & Payloads]] — webshells, reverse shells, SSH key theft/planting
- [[SQL Injection & Databases]] — MySQL, MSSQL/Impacket, SQLi payloads, sqlmap
- [[Web Applications]] — WordPress, command injection diagnosis
- [[Phishing]] — website cloning, clone-patching (BeautifulSoup), credential capture servers
- [[Client-Side Attacks]] — WsgiDAV/WebDAV setup, Windows library file XML, `.lnk` shortcut payloads, VBA macros, one-shot SMB delivery

*(New areas get added here as modules are worked through — Active Directory, Password Attacks, Pivoting, Linux/Windows Privilege Escalation, etc.)*

#### Tags: #CommandAppendix #Methodology
