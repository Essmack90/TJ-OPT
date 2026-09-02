# Reconnaissance & Enumeration, Decision Tree

Part of [[DECISION TREE]]. "I found X during recon, what do I try."

---

### Found an open port, not sure what to do with it
→ Match it against the service-specific enumeration steps in [[Linux Methodology#Step 3: Service-Specific Enumeration]]
→ Full background on the scanning process itself: [[06. Information Gathering|Information Gathering]] (Module 6)

### A web root only shows the server's default page (e.g. "Apache2 Debian Default Page: It works")
→ The real application is almost always sitting under an undiscovered subdirectory, don't conclude the box has "nothing on port 80"
→ A single `gobuster`/wordlist pass often only finds the first-level folder, then needs a **second** pass scoped inside that folder to find the actual app root one level deeper, a recursive scanner like `feroxbuster` (see [[Feroxbuster]] in [[MODERN TOOLING]]) finds the full path in one run instead
→ See [[14. Fixing Exploits#Module Exercise VM #2: elFinder web application|Fixing Exploits, Module Exercise VM #2]]

### Ran Nessus or Nmap and it flagged a CVE
→ Search `<CVE-number> exploit` or `<CVE-number> nse` to find a known PoC before writing your own
→ See [[07. Vulnerability Scanning#7.3.2. Working with NSE Scripts|7.3.2]] for the search-and-adapt workflow
→ Nmap NSE quick scan: [[07. Vulnerability Scanning#7.3.1. NSE Vulnerability Scripts|7.3.1]]

### Nessus scan comes back with 0 hosts / 0 vulnerabilities
→ Don't touch scan config first. Check basic reachability:
```bash
ping -c 4 $BoxIP
ssh $Username@$BoxIP
```
→ If both fail, suspect the lab instance itself (may need reverting), not your scan settings
→ Full writeup: [[07. Vulnerability Scanning#7.2.5. Performing an Authenticated Vulnerability Scan|7.2.5 troubleshooting note]]

### Nessus Essentials says "license expired" or you've hit the 5-host cap
→ Get a fresh activation code from the Essentials "Register now" form, re-register with `nessuscli fetch --register`
→ Full steps: [[07. Vulnerability Scanning#7.2.1. Installing Nessus|7.2.1 troubleshooting box]], syntax: [[Reconnaissance & Enumeration#Nessus (Install & CLI)|Command Appendix]]

### A Nessus finding shows severity "MIXED" instead of a single rating
→ That's a **grouped finding**, several related vulnerabilities bundled under one entry, not a single ambiguous one. Click into it to expand the individual findings inside
→ To see every finding listed separately instead of grouped from the start: gear/wheel icon on the Vulnerabilities page → **Disable Groups**
→ See [[07. Vulnerability Scanning#7.2.4. Analyzing the Results|7.2.4]]

### A Nessus scan shows multiple similar-looking CVEs and you're not sure which one actually matches
→ Don't assume the first or highest-severity one is right. Check each candidate plugin's own **title and "Solution" field** against the exact version range you're actually dealing with, Nessus groups closely-related CVEs (e.g. two path-traversal bugs in adjacent Apache versions) under the same plugin family, and only one will genuinely match
→ Course material referencing a Nessus UI element that doesn't exist in your version (e.g. the "VPR Key Drivers" panel)? The same data is still available, just decode the CVSS Temporal Vector under Risk Information instead: [[Reconnaissance & Enumeration (Breakdowns)#Decoding a Nessus CVSS v3.0 Temporal Vector|Command Breakdowns]]
→ See [[07. Vulnerability Scanning#7.2.4. Analyzing the Results|7.2.4]]

### Preparing a client-side attack (no direct network access to the actual target machine)
→ Passive first: pull any public documents the org has posted (PDFs, Office files) and check `exiftool -a -u` for unscrubbed metadata, author name, dates, and critically the `Producer`/`Creator Tool` field for what software (and OS) created it
→ Then active fingerprinting to confirm live OS/browser before committing to a platform-specific payload: send a Canarytokens (canarytokens.org) tracking link wrapped in a pretext, check History for the JS-derived fingerprint once clicked (more reliable than the raw User-Agent alone)
→ An AdBlocker on the target's end can suppress the JS fingerprinting, don't over-trust a suspiciously sparse result
→ See [[12. Client-Side Attacks#12.1.1. Information Gathering|12.1.1]] and [[12. Client-Side Attacks#12.1.2. Client Fingerprinting|12.1.2]]

### SNMP query comes back completely empty
→ Don't assume SNMP isn't running, confirm the port's actually open first (`sudo nmap -sU --open -p 161 $BoxIP`), UDP scans miss things silently
→ If the port's open but a plain `snmpwalk -c public` gets nothing back, the community string is probably wrong, not the service. Brute force it: `onesixtyone -c community -i ips`
→ Syntax: [[Reconnaissance & Enumeration#SNMP Enumeration|Command Appendix]], mechanics of why the community string matters: [[Reconnaissance & Enumeration (Breakdowns)#SNMP: community-string brute force, then OID-walking|Command Breakdowns]]
→ See [[06. Information Gathering#6.4.6. SNMP Enumeration|6.4.6]]

### UDP port scan shows no response for a port you expected to be open
→ **This isn't proof the port is closed.** UDP is stateless, closed ports typically send back an ICMP port-unreachable, but open/filtered ports very often send nothing at all, so silence is ambiguous by design, not necessarily "nothing's there"
→ A firewall dropping ICMP outright can also make a genuinely closed port look identical to an open one, don't fully trust a single UDP scan's result either way
→ See [[06. Information Gathering#6.4.2. TCP/UDP Port Scanning Theory|6.4.2]]

### Netcraft site report page won't load / seems dead
→ Netcraft discontinued that specific service in 2024, this isn't a target-side problem
→ Use `wappalyzer.com/lookup/$Domain` instead for the same tech-stack fingerprinting
→ See [[06. Information Gathering#6.2.3. Netcraft|6.2.3]]

### SMTP VRFY returns 252 for every username you try, even obviously fake ones
→ `252` alone doesn't confirm an account exists, per RFC 5321 it literally means "can't verify, but will attempt delivery," some mail servers return it uniformly specifically to defeat this technique
→ Always test a deliberately bogus username alongside your real guesses as a baseline, the *contrast* between responses (not a single response in isolation) is the actual signal
→ If `VRFY` is fully neutered like this, check whether `EXPN` is still enabled, or fall back to `RCPT TO` probing instead
→ Full mechanics: [[Reconnaissance & Enumeration (Breakdowns)#SMTP: why VRFY's response code isn't a clean yes/no|Command Breakdowns]]
→ See [[06. Information Gathering#6.4.5. SMTP Enumeration|6.4.5]]

---

### Got a domain name but no subdomains — where to look next

→ **DNS zone transfer first** (if the nameserver allows it, free enumeration):
```bash
dig axfr $Domain @$BoxIP
```
→ **Gobuster DNS bruteforce** (needs a fast wordlist):
```bash
gobuster dns -d $Domain -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt
```
→ **Gobuster vHost** (finds virtual hosts on a single IP that respond differently by Host: header):
```bash
gobuster vhost -u http://$BoxIP -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt --append-domain
```
`--append-domain` is required when using a raw IP, it appends `.domain.tld` to each wordlist word so the Host header is valid.
→ **subbrute** for deeper DNS subdomain brute force using open resolvers (bypasses rate limiting):
```bash
python3 subbrute.py $Domain -s /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -r resolvers.txt
```
→ Found a new subdomain but can't resolve it? Add it to `/etc/hosts` for the lab environment.
→ Full reference: [[Reconnaissance & Enumeration#DNS Zone Transfer|Command Appendix]], [[06. Information Gathering|CS.5]]

---

### Found an open service and need to pick the right attack tool

Quick routing guide by service:

| Service | Port | Try First |
|---------|------|-----------|
| FTP | 21 | Anonymous login → `ftp $BoxIP` (user: anonymous); hydra -t 1 for brute force (slow to avoid lockouts) |
| SSH | 22 | hydra -l user -P rockyou.txt; check for weak keys |
| SMTP | 25/587 | smtp-user-enum RCPT mode; hydra for creds |
| POP3 | 110/995 | nc/telnet manual session (USER/PASS/LIST/RETR); hydra |
| SMB | 445 | enum4linux -A; smbclient -N -L; nxc smb --shares; rpcclient |
| MSSQL | 1433 | impacket-mssqlclient; sqlcmd (Windows); xp_cmdshell → xp_dirtree → impersonation |
| RDP | 3389 | xfreerdp; check DisableRestrictedAdmin for PtH |
| WinRM | 5985 | evil-winrm |

→ For credential brute force on any service: hydra is the go-to; nxc (NetExec) for SMB/WinRM/LDAP.
→ Always check for anonymous/null auth before reaching for a wordlist.
→ Full service attack reference: [[06. Information Gathering]]

#### Tags: #DecisionTree #Reconnaissance #Enumeration #vHost #Subdomains #ServiceAttacks
## External Resources

- [HackTricks - Pentesting Index](https://hacktricks.wiki/en/index.html)
- [PayloadsAllTheThings - Methodology and Resources](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Methodology%20and%20Resources)
- [RevShells](https://www.revshells.com/) for shell troubleshooting
- [CyberChef](https://gchq.github.io/CyberChef/) for transformations
- [ippsec.rocks](https://ippsec.rocks/) for walkthrough searches
## Why this matters for OSCP

This page turns one repeatable part of an authorized assessment into a checklist you can apply under exam time pressure.

## Related Modules

- [[MODULES/06. Information Gathering]] -- module concepts used by this hub page

## Demonstrated in box write-ups

- [[OSCP/BOXES/WRITE UPS/AD/Forest|Forest]] -- demonstrates the workflow described here
