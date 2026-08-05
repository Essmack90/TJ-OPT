# Reconnaissance & Enumeration — Decision Tree

Part of [[DECISION TREE]]. "I found X during recon, what do I try."

---

### Found an open port, not sure what to do with it
→ Match it against the service-specific enumeration steps in [[Linux Methodology#Step 3: Service-Specific Enumeration]]
→ Full background on the scanning process itself: [[Information Gathering]] (Module 6)

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
→ Full steps: [[Vulnerability Scanning#7.2.1. Installing Nessus|7.2.1 troubleshooting box]]

### Preparing a client-side attack (no direct network access to the actual target machine)
→ Passive first: pull any public documents the org has posted (PDFs, Office files) and check `exiftool -a -u` for unscrubbed metadata, author name, dates, and critically the `Producer`/`Creator Tool` field for what software (and OS) created it
→ Then active fingerprinting to confirm live OS/browser before committing to a platform-specific payload: send a Canarytokens (canarytokens.org) tracking link wrapped in a pretext, check History for the JS-derived fingerprint once clicked (more reliable than the raw User-Agent alone)
→ An AdBlocker on the target's end can suppress the JS fingerprinting, don't over-trust a suspiciously sparse result
→ See [[Client-Side Attacks#12.1.1. Information Gathering|12.1.1]] and [[Client-Side Attacks#12.1.2. Client Fingerprinting|12.1.2]]
