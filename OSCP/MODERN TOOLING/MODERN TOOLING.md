# Modern Tooling

OSCP teaches things the manual way, deliberately, understanding *how* a technique works matters more than any specific tool. This hub doc is the complementary layer: once a manual technique is actually understood, here's a faster tool for the same job in real practice.

**The line drawn here (confirmed 2026-08-06):** these are speed/quality-of-life upgrades over a manual technique, not exploitation-automation frameworks. Nothing here is sqlmap, Metasploit, or in that same category (find-the-vuln-and-exploit-it-for-you). Every entry either speeds up recon/enumeration, generates a payload artifact faster, or moves data/traffic faster, the actual exploitation decision and technique stays exactly as manual as the module teaches it.

One file per tool, same pattern as [[COMMAND APPENDIX]] and [[COMMAND BREAKDOWNS]]. Each entry names which module section(s) it speeds up, and is explicit about what it does and doesn't replace.

---

## Tools

- [[TheHarvester]] — passive OSINT aggregator, pulls emails/subdomains/IPs from many public sources in one pass instead of checking WHOIS/Google/Netcraft/GitHub/Shodan by hand
- [[Rustscan]] — full-port-range scanning in seconds instead of minutes, still hands off to `nmap` for the actual service detection
- [[NetExec]] — SMB/AD enumeration and auth spraying across one host or a whole subnet, successor to CrackMapExec
- [[Smtp-user-enum]] — scripted `VRFY`/`EXPN`/`RCPT TO` username enumeration instead of one-at-a-time manual `telnet`
- [[Braa]] — mass SNMP scanning across many hosts at once instead of one `snmpwalk` per host
- [[Feroxbuster]] — recursive content discovery, automatically dives into subdirectories `gobuster` would need a manual re-run for
- [[Ffuf]] — general-purpose fast fuzzer, any injection point (path, header, POST body), not just directory names
- [[Kiterunner]] — API-route-aware brute forcer, tries realistic API paths and correct HTTP methods instead of generic web wordlists
- [[Httpx]] — fast HTTP fingerprinting (status/title/tech-stack) across a whole target list at once
- [[MacroPack]] — generates and obfuscates Office macro payloads, the artifact-building half of [[Client-Side Attacks#12.2.3. Leveraging Microsoft Word Macros|12.2.3]], faster once the manual VBA/chunking process is understood
- [[Ntlm_theft]] — generates a whole batch of NTLM-capturing lure file types at once (including the `.library-ms` format built by hand in [[Client-Side Attacks#Step 2: Build the Windows library file's XML|12.3.1]])
- [[Chisel]] — fast HTTP-tunneled pivoting, no module cross-link yet (pivoting isn't covered by the 7 modules swept so far), added since it's the exemplar tool for this whole category
- [[Ligolo-ng]] — TUN-interface-based pivoting, no `proxychains` needed once a route's added, same no-current-module-link caveat as Chisel
- [[SysReptor]] — speeds up the notes-to-report handoff specifically (one-click Markdown → PDF, OffSec-sanctioned report templates), not the note-taking itself

*(More tools get added here as later modules, e.g. Active Directory, Password Attacks, Privilege Escalation, introduce new manual techniques worth speeding up.)*

---

## Modules with no addition, and why

- **[[SQL Injection Attacks]]**: the obvious speed-up (sqlmap) is already core curriculum in [[SQL Injection Attacks#10.3.2. Automating the Attack|10.3.2]], it's not something to "add," it's already taught as its own topic. No non-automation alternative exists that meaningfully speeds up manual SQLi beyond what's already covered.
- **[[Phishing Basics]]**: already has its own properly-scoped [[Phishing Basics#🎯 Related Tools to Practice|Related Tools to Practice]] section (GoPhish, Evilginx2, King Phisher). Deliberately not duplicated here, and deliberately not expanded, those three are full-campaign automation platforms, the same category this hub doc is explicitly excluding elsewhere (same spirit as sqlmap/Metasploit, just for phishing instead of exploitation).
- **[[Vulnerability Scanning]]**: Nessus is the module's own topic, nothing to speed it up with that wouldn't just be "a worse Nessus." [[Rustscan]] applies to this module's port-scanning prerequisite though, see that entry.
- **[[Common Web Application Attacks]]**: the obvious speed-up (`commix`) automates command-injection discovery *and* exploitation end to end, the same excluded category as sqlmap. The module already carries this exact reasoning inline at the end of [[Common Web Application Attacks#9.4.1. OS Command Injection|9.4.1]], recorded here too so this index stays a complete list rather than requiring a reader to already know which modules were checked.
- **[[Locating Public Exploits]]**: the module's own core teaching *is* the efficient-lookup layer already (`searchsploit`, Exploit-DB, NSE), nothing to speed up further without crossing into the excluded automated vulnerability-to-exploit-matcher category (`nuclei` templates and similar). The module carries this reasoning inline at the end of [[Locating Public Exploits#13.5. Wrapping Up|13.5]].
- **[[Fixing Exploits]]**: `mingw-w64`, `wine`, and `msfvenom`'s bad-char/encoder workflow already are the efficient, manual-but-fast method the module teaches, and Metasploit modules exist for some of the exact CVEs covered here (Sync Breeze, Easy Chat Server), but reaching for those instead would cross into the same excluded find-and-exploit-automatically category as sqlmap/Metasploit generally, the whole point of this module is the adaptation skill itself, not a faster way to skip it. [[Feroxbuster]] applies to this module's own recon step though (see that entry).
- **[[Antivirus Evasion]]**: Shellter and Veil are themselves the efficient tools the module uses -- Shellter for PE injection (there's no non-automated wrapper that speeds it up further without just being "run Shellter for you"), Veil for `.bat`/payload generation (already curriculum, taught as the fast tool even if Wine issues forced a manual bypass in practice). PowerShell IEX itself is already the modern, fast in-memory technique -- the manual `.bat` approach and the IEX download cradle are the fastest non-framework methods available, and there's nothing to speed them up that doesn't cross into full-automation territory (tools like `Invoke-Obfuscation` for PowerShell obfuscation or `Donut` for in-memory PE shellcode are real but map to later, more advanced evasion topics beyond this module's scope).

#### Tags: #ModernTooling #Methodology
