# Reconnaissance & Enumeration, Decision Tree

Part of [[DECISION TREE]]. "I found X during recon, what do I try."

---

### Found an open port, not sure what to do with it
→ Match it against the service-specific enumeration steps in [[Linux Methodology#Step 3: Service-Specific Enumeration]]
→ Full background on the scanning process itself: [[Information Gathering]] (Module 6)

### A web root only shows the server's default page (e.g. "Apache2 Debian Default Page: It works")
→ The real application is almost always sitting under an undiscovered subdirectory, don't conclude the box has "nothing on port 80"
→ A single `gobuster`/wordlist pass often only finds the first-level folder, then needs a **second** pass scoped inside that folder to find the actual app root one level deeper, a recursive scanner like `feroxbuster` (see [[Feroxbuster]] in [[MODERN TOOLING]]) finds the full path in one run instead
→ See [[Fixing Exploits#Module Exercise VM #2: elFinder web application|Fixing Exploits, Module Exercise VM #2]]

### Ran Nessus or Nmap and it flagged a CVE
→ Search `<CVE-number> exploit` or `<CVE-number> nse` to find a known PoC before writing your own
→ See [[Vulnerability Scanning#7.3.2. Working with NSE Scripts|7.3.2]] for the search-and-adapt workflow
→ Nmap NSE quick scan: [[Vulnerability Scanning#7.3.1. NSE Vulnerability Scripts|7.3.1]]

### Nessus scan comes back with 0 hosts / 0 vulnerabilities
→ Don't touch scan config first. Check basic reachability:
```bash
ping -c 4 <target-ip>
ssh <user>@<target-ip>
```
→ If both fail, suspect the lab instance itself (may need reverting), not your scan settings
→ Full writeup: [[Vulnerability Scanning#7.2.5. Performing an Authenticated Vulnerability Scan|7.2.5 troubleshooting note]]

### Nessus Essentials says "license expired" or you've hit the 5-host cap
→ Get a fresh activation code from the Essentials "Register now" form, re-register with `nessuscli fetch --register`
→ Full steps: [[Vulnerability Scanning#7.2.1. Installing Nessus|7.2.1 troubleshooting box]], syntax: [[Reconnaissance & Enumeration#Nessus (Install & CLI)|Command Appendix]]

### A Nessus finding shows severity "MIXED" instead of a single rating
→ That's a **grouped finding**, several related vulnerabilities bundled under one entry, not a single ambiguous one. Click into it to expand the individual findings inside
→ To see every finding listed separately instead of grouped from the start: gear/wheel icon on the Vulnerabilities page → **Disable Groups**
→ See [[Vulnerability Scanning#7.2.4. Analyzing the Results|7.2.4]]

### A Nessus scan shows multiple similar-looking CVEs and you're not sure which one actually matches
→ Don't assume the first or highest-severity one is right. Check each candidate plugin's own **title and "Solution" field** against the exact version range you're actually dealing with, Nessus groups closely-related CVEs (e.g. two path-traversal bugs in adjacent Apache versions) under the same plugin family, and only one will genuinely match
→ Course material referencing a Nessus UI element that doesn't exist in your version (e.g. the "VPR Key Drivers" panel)? The same data is still available, just decode the CVSS Temporal Vector under Risk Information instead: [[Reconnaissance & Enumeration (Breakdowns)#Decoding a Nessus CVSS v3.0 Temporal Vector|Command Breakdowns]]
→ See [[Vulnerability Scanning#7.2.4. Analyzing the Results|7.2.4]]

### Preparing a client-side attack (no direct network access to the actual target machine)
→ Passive first: pull any public documents the org has posted (PDFs, Office files) and check `exiftool -a -u` for unscrubbed metadata, author name, dates, and critically the `Producer`/`Creator Tool` field for what software (and OS) created it
→ Then active fingerprinting to confirm live OS/browser before committing to a platform-specific payload: send a Canarytokens (canarytokens.org) tracking link wrapped in a pretext, check History for the JS-derived fingerprint once clicked (more reliable than the raw User-Agent alone)
→ An AdBlocker on the target's end can suppress the JS fingerprinting, don't over-trust a suspiciously sparse result
→ See [[Client-Side Attacks#12.1.1. Information Gathering|12.1.1]] and [[Client-Side Attacks#12.1.2. Client Fingerprinting|12.1.2]]

### SNMP query comes back completely empty
→ Don't assume SNMP isn't running, confirm the port's actually open first (`sudo nmap -sU --open -p 161 <target>`), UDP scans miss things silently
→ If the port's open but a plain `snmpwalk -c public` gets nothing back, the community string is probably wrong, not the service. Brute force it: `onesixtyone -c community -i ips`
→ Syntax: [[Reconnaissance & Enumeration#SNMP Enumeration|Command Appendix]], mechanics of why the community string matters: [[Reconnaissance & Enumeration (Breakdowns)#SNMP: community-string brute force, then OID-walking|Command Breakdowns]]
→ See [[Information Gathering#6.4.6. SNMP Enumeration|6.4.6]]

### UDP port scan shows no response for a port you expected to be open
→ **This isn't proof the port is closed.** UDP is stateless, closed ports typically send back an ICMP port-unreachable, but open/filtered ports very often send nothing at all, so silence is ambiguous by design, not necessarily "nothing's there"
→ A firewall dropping ICMP outright can also make a genuinely closed port look identical to an open one, don't fully trust a single UDP scan's result either way
→ See [[Information Gathering#6.4.2. TCP/UDP Port Scanning Theory|6.4.2]]

### Netcraft site report page won't load / seems dead
→ Netcraft discontinued that specific service in 2024, this isn't a target-side problem
→ Use `wappalyzer.com/lookup/<domain>` instead for the same tech-stack fingerprinting
→ See [[Information Gathering#6.2.3. Netcraft|6.2.3]]

### SMTP VRFY returns 252 for every username you try, even obviously fake ones
→ `252` alone doesn't confirm an account exists, per RFC 5321 it literally means "can't verify, but will attempt delivery," some mail servers return it uniformly specifically to defeat this technique
→ Always test a deliberately bogus username alongside your real guesses as a baseline, the *contrast* between responses (not a single response in isolation) is the actual signal
→ If `VRFY` is fully neutered like this, check whether `EXPN` is still enabled, or fall back to `RCPT TO` probing instead
→ Full mechanics: [[Reconnaissance & Enumeration (Breakdowns)#SMTP: why VRFY's response code isn't a clean yes/no|Command Breakdowns]]
→ See [[Information Gathering#6.4.5. SMTP Enumeration|6.4.5]]
