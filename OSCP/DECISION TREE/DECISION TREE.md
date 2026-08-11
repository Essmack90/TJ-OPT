# OSCP Decision Tree

Quick "I found X, what do I try" lookup. Skim for whatever's in front of you right now, follow the link for the full walkthrough.

Covers Modules 6 through 16 so far. Will grow as later modules get added.

Already know which tool you want and just need exact syntax? See [[COMMAND APPENDIX]] instead. Need the full phase-by-phase methodology? See [[METHODOLOGY CHEAT SHEET]].

Restructured 2026-08-04 from a single flat file into a folder split by area, same pattern as [[COMMAND APPENDIX]], [[COMMAND BREAKDOWNS]], and [[METHODOLOGY CHEAT SHEET]].

---

## Areas

- [[Reconnaissance & Enumeration (Decision Tree)|Reconnaissance & Enumeration]] — open ports, Nessus/Nmap CVE hits, scan troubleshooting
- [[File Inclusion & Traversal (Decision Tree)|File Inclusion & Traversal]] — traversal parameters, LFI-to-RCE, PHP wrappers
- [[File Upload Attacks (Decision Tree)|File Upload Attacks]] — upload form filter bypasses
- [[Web Applications (Decision Tree)|Web Applications]] — XSS, command injection, vhost pivots, WordPress, REST APIs
- [[SQL Injection & Databases (Decision Tree)|SQL Injection & Databases]] — MySQL/MSSQL/PostgreSQL injection, error-based/blind/stacked-query triage
- [[Shells & Payloads (Decision Tree)|Shells & Payloads]] — reverse shell delivery, listener troubleshooting
- [[Secrets & Credentials (Decision Tree)|Secrets & Credentials]] — private key extraction, hash type decisions (NTLM vs Net-NTLMv2), PtH vs relay vs crack, Credential Guard bypass path, Responder/relay troubleshooting
- [[Phishing (Decision Tree)|Phishing]] — website cloning, clone-patching gotchas, credential-capture delivery, pretext-building
- [[Client-Side Attacks (Decision Tree)|Client-Side Attacks]] — macro autorun troubleshooting, one-shot watcher scripts, Windows library file WebDAV rewriting, `.lnk` hiding tricks
- [[Locating Public Exploits (Decision Tree)|Locating Public Exploits]] — exploits with hardcoded ports, misidentified products from banner alone, patator's 0/0/0/0/0 gotcha, CSRF-protected brute forcing
- [[Fixing Exploits (Decision Tree)|Fixing Exploits]] — Windows-only exploit source on Kali, confusing downstream errors after a successful step
- [[Buffer Overflow & Memory Corruption (Decision Tree)|Buffer Overflow & Memory Corruption]] — rotated EIP values, target crashes mid-exploit, missing/wrong return addresses, multiple candidate exploits

*(More areas get added here as modules are worked through, Active Directory, Password Attacks, Pivoting, Privilege Escalation, etc.)*

---

## General Patterns Worth Remembering

- **A filter blocking `../` isn't blocking traversal.** Encoding (`%2e%2e/`, base64, etc) is the standard way past a filter that only checks literal plaintext. Shows up in 9.1.3, 9.2.2, and 9.3.1, always the same underlying idea.
- **Automated tool flags a vuln → confirm it manually.** Nessus/Nmap NSE finding something isn't proof it's exploitable. `curl` the disclosed PoC yourself. See [[Vulnerability Scanning#7.4. Wrapping Up|7.4]].
- **Check privilege level the moment you land a shell.** Don't assume you need privesc, training VMs frequently run services as root/SYSTEM already.
- **When a module's exact demo payload doesn't reproduce**, check whether an earlier tool/scan already disclosed the actual working PoC pattern before just varying parameters blindly.
- **A request to a reused hostname comes back empty/silent.** Check `/etc/hosts` before assuming the vuln itself isn't working. If the same hostname (e.g. `mountaindesserts.local`) gets reused across multiple labs in a module, it's easy to leave it pointed at an earlier box's stale IP. `grep <hostname> /etc/hosts` and fix with `sed -i` if needed. See [[Common Web Application Attacks#9.3.2. Using Non-Executable Files|9.3.2]] for where this bit us.
- **A `curl -X POST --data` payload with `&`, `=`, `+`, or spaces fails or gets truncated for no obvious reason.** `--data` sends the value raw, so those characters get reinterpreted by the server (`&`/`=` as form-field separators, `+` as a literal space per `application/x-www-form-urlencoded` rules). Switch to `--data-urlencode`, which percent-encodes automatically. Bit us with a reverse shell one-liner containing `>&`/`0>&1` in [[Common Web Application Attacks#9.4.1. OS Command Injection|9.4.1]], and again with a base64-encoded payload (base64 routinely contains `+`) in [[SQL Injection Attacks#Capstone: Exercise VM #3|Capstone Labs, VM #3]]. See [[SQL Injection (Breakdowns)#Why a base64 payload sent via curl --data silently corrupts (+ becomes a space)|Command Breakdowns]] for the full mechanics.
- **A lab question asks about specific code details (variable names, field names) and a module's generic example answer gets rejected.** The module's illustrative code snippet is often just an example, not a verbatim copy of the actual lab VM's source. Check the live app's real form field names (`curl` the page, or view source) instead of assuming the textbook variable names apply exactly. Bit us in [[SQL Injection Attacks#10.2.1. Identifying SQLi via Error-Based Payloads|10.2.1]] (`$uname` in the module vs. the actual `$uid`/`name="uid"` on the VM).
