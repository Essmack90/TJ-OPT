# Reconnaissance & Enumeration, Command Breakdowns

Part of [[COMMAND BREAKDOWNS]]. A few recon one-liners whose output-wrangling (not the scan itself) is the non-obvious part. See that page for the entry format.

---

## Reverse DNS brute force with a negative-filter grep

**Full command:**
```bash
for ip in $(seq 64 79); do host 167.114.21.$ip; done | grep -Ev "not found|timed out"
```

**Piece by piece:**
- `seq 64 79` → generates the last-octet range to sweep, fed into the loop as plain numbers.
- `for ip in $(...); do host 167.114.21.$ip; done` → runs a reverse DNS lookup (`host <ip>`) against every address in that range, one at a time. Most of these will have no PTR record at all, that's expected and normal, not every IP in a range hosts something with reverse DNS configured.
- `grep -Ev "not found|timed out"` → this is the part worth pausing on. `-v` inverts the match, so instead of grep finding lines *containing* something, it prints every line that does **NOT** match either pattern. Most beginners default to grepping *for* a positive signal (a hostname, a keyword); here the useful signal is the *absence* of the two standard failure phrases `host` prints for a nonexistent/timed-out PTR record. Everything left over after filtering those out is, by elimination, an actual successful reverse lookup with a real hostname in it.
- `-E` → extended regex mode, needed here only because `|` (alternation, "match either pattern") is being used, plain `grep` without `-E` would treat `|` as a literal character instead of "or."

**Where this comes from:** this is a general shell/grep pattern (negative filtering via `-v`), not tied to any specific reference site, worth remembering as a reusable technique any time a command produces mostly noise with a few real hits mixed in and there's no reliable positive keyword to grep for instead.

**Where to look in the response:** the surviving output lines look like normal `host` output for a successful reverse lookup (`64.21.114.167.in-addr.arpa domain name pointer admin.megacorpone.com.`), the hostname itself is the last token on the line.

🔁 **Seen in:** [[Information Gathering#6.4.1. DNS Enumeration|Information Gathering, 6.4.1]].

#### Tags: #DNS #ReverseDNS #NegativeGrep #CommandBreakdowns

---

## Nmap greppable ping sweep → `grep`/`cut` field extraction

**Full command:**
```bash
nmap -v -sn 192.168.50.1-253 -oG ping-sweep.txt
grep Up ping-sweep.txt | cut -d " " -f 2
```

**Piece by piece:**
- `-oG ping-sweep.txt` → saves results in Nmap's **greppable output format**, a specific one-line-per-host layout designed to be parsed by exactly this kind of shell pipeline, distinct from Nmap's normal human-readable or XML output. A greppable line looks like: `Host: 192.168.50.5 (somehost)  Status: Up`.
- `grep Up` → filters down to only hosts that responded (Nmap's greppable format prints a line per scanned host regardless of status, `Up` or `Down`, so this step throws away the dead ones).
- `cut -d " " -f 2` → this only works because of exactly how the greppable format lays out its fields, space-delimited, with the IP address landing in the **second** space-separated field (`Host:` is field 1, the IP is field 2). This is entirely dependent on that specific format string, it isn't a general "extract the IP from any text" trick, it's tuned to `-oG`'s exact column layout.

**Where this comes from:** Nmap's own man page documents the `-oG` format's field layout under "Greppable Output." Worth knowing that `-oG` is explicitly called out in Nmap's own docs as legacy/for backward compatibility, XML output (`-oX`) plus a proper parser (or `-oA` to get all formats at once) is preferred for anything more complex than a quick `grep`/`cut` one-liner like this.

**Where to look in the response:** the extracted output is just a bare list of IPs, one per line, ready to feed straight into a follow-up loop or another tool's target list.

🔁 **Seen in:** [[Information Gathering#6.4.3. Port Scanning with Nmap|Information Gathering, 6.4.3]].

#### Tags: #Nmap #NetworkSweep #GreppableOutput #CommandBreakdowns

---

## PowerShell `TcpClient` inline port sweep (no Nmap on target)

**Full command:**
```powershell
1..1024 | % {echo ((New-Object Net.Sockets.TcpClient).Connect("192.168.50.151", $_)) "TCP port $_ is open"} 2>$null
```

**Piece by piece:**
- `1..1024` → PowerShell's range operator, generates the integers 1 through 1024 as a pipeline of port numbers to try.
- `| % {...}` → `%` is the alias for `ForEach-Object`, runs the block once per port number, `$_` inside the block refers to the current port.
- `(New-Object Net.Sockets.TcpClient).Connect("<ip>", $_)` → constructs a raw .NET `TcpClient` object inline and immediately calls `.Connect()` on it. This is the actual scanning mechanism, a bare TCP connection attempt using .NET's own networking class, used here because the target has no Nmap (or any dedicated scanner) installed at all, just PowerShell, which ships with every modern Windows box by default (a LOLBAS-style "living off the land" approach).
- `2>$null` → the entire trick that makes this readable output instead of a wall of noise. `.Connect()` **throws a terminating error** when the port is closed/unreachable, generating PowerShell's usual red exception text. `2>` redirects the error stream, and `$null` discards it entirely. The scan's actual logic depends on this: only ports where `.Connect()` succeeds *without* throwing make it to the `echo` statement at all, everything else's error just vanishes silently. The visible output list, by construction, only ever contains successful connections.

**Where this comes from:** this is a well-known LOLBAS/"living off the land" PowerShell port-scanning one-liner, appearing in various OSCP-adjacent cheat sheets and the LOLBAS project (lolbas-project.github.io) under PowerShell network techniques, worth searching there for other credential-free Windows-native recon tricks when Nmap isn't an option.

**Where to look in the response:** each successful line prints as `True TCP port <N> is open` (the `True` is `.Connect()`'s own return-ish echo from the outer `echo`), scan the output for `True` lines, everything else was silently suppressed by the `2>$null`.

🔁 **Seen in:** [[Information Gathering#6.4.3. Port Scanning with Nmap|Information Gathering, 6.4.3]] (LOLBAS/Windows section).

#### Tags: #PowerShell #PortScan #LOLBAS #CommandBreakdowns

---

## SNMP: community-string brute force, then OID-walking

**Full commands:**
```bash
onesixtyone -c community -i ips
snmpwalk -c public -v1 <target> 1.3.6.1.4.1.77.1.2.25
```

**Piece by piece:**
- **Why a community string is needed at all** → SNMPv1/v2c has no real authentication, the "community string" is closer to a shared password than a username/password pair, and it doubles as an access-control mechanism. `public` conventionally grants read-only access, `private` conventionally grants read-write, but plenty of real devices leave both at their defaults or use something equally guessable (`manager`, the device vendor's name, etc).
- `onesixtyone -c community -i ips` → `-c` is a wordlist of candidate community strings, `-i` is a list of target IPs. It tries every string against every host, fast, since SNMP is UDP and stateless, there's no handshake overhead per attempt the way a TCP brute force would have.
- `snmpwalk -c public -v1 <target> <OID>` → once a working string is found, this walks the **MIB tree**, a hierarchical database every SNMP-enabled device exposes, starting from a given OID (Object Identifier) node and returning every value nested underneath it. `-v1` picks the SNMP protocol version to speak, has to match what the target actually supports.
- **Why the specific OID `1.3.6.1.4.1.77.1.2.25` matters** → OIDs are effectively a global, hierarchical namespace, every branch is standardized (or vendor-registered), so the same OID means the same thing on every device that implements it. `1.3.6.1.4.1.77.1.2.25` specifically is the Windows-relevant branch for user accounts, this is why the module hands you a small table of specific OIDs rather than telling you to just walk the entire tree and eyeball it, you already know in advance which branch answers which question.

**Where this comes from:** SNMP's MIB structure is defined in RFC 1213 and vendor-specific MIB extensions, `snmpwalk`'s own man page documents the OID-tree-walking behavior. HackTricks' SNMP pentesting page has a longer table of useful OIDs beyond the handful covered in [[Information Gathering#6.4.6. SNMP Enumeration|6.4.6]].

**Where to look in the response:** `onesixtyone` prints `<ip> [<community-string>]` for every hit, silence means that string didn't work against that host. `snmpwalk` prints one line per OID node found under the branch you queried, formatted `OID = TYPE: value`, the `value` field is the actual data you want.

🔁 **Seen in:** [[Information Gathering#6.4.6. SNMP Enumeration|Information Gathering, 6.4.6]].

#### Tags: #SNMP #Onesixtyone #Snmpwalk #MIBTree #CommandBreakdowns

---

## SMTP: why VRFY's response code isn't a clean yes/no

**Full commands:**
```bash
nc -nv <target> 25
VRFY root
VRFY idontexist
```

**Piece by piece:**
- **What `VRFY` is actually for** → a legitimate SMTP command meant to let a mail client check a recipient address is deliverable before sending, not designed as a security boundary, which is exactly why it leaks information.
- **`252` on a real/likely-valid user** → RFC 5321 defines 252 as "cannot VRFY user, but will accept message and attempt delivery." Read that literally: the server is explicitly telling you it did **not** confirm the account exists, only that it'll try. Some mail servers return this for *every* input specifically to avoid a clean oracle, so `252` alone is weak evidence, not proof.
- **`550` on a genuinely unknown user** → "mailbox unavailable," a much stronger signal, most servers only return this when the account genuinely doesn't exist (or is disabled/blocked).
- **Why this still counts as a real enumeration technique despite the ambiguity** → the *contrast* between the two responses is the actual signal. Testing a deliberately bogus username (`idontexist`) alongside a real guess gives you a baseline: if bogus names reliably 550 and real-looking names reliably 252, the pattern itself confirms the server distinguishes valid from invalid input, even though 252 alone doesn't.
- **`EXPN`** → a related command that, if enabled, lists every address belonging to a mailing list, a much stronger leak than `VRFY` when it's not disabled, since it directly enumerates real addresses rather than confirming guesses one at a time.

**Where this comes from:** RFC 5321 §3.5 documents both commands and their exact status codes, most hardened mail servers disable `VRFY`/`EXPN` entirely or lie uniformly specifically because of this well-known enumeration technique.

**Where to look in the response:** the numeric code at the start of the line is what matters (`252 2.1.5 root <root@host>` vs `550 5.1.1 <idontexist> unknown`), the free-text after the code varies by mail server implementation and isn't reliable to grep for across different targets.

🔁 **Seen in:** [[Information Gathering#6.4.5. SMTP Enumeration|Information Gathering, 6.4.5]].

#### Tags: #SMTP #VRFY #EXPN #CommandBreakdowns

---

## Entropy-based secret detection (Gitrob/Gitleaks)

**The concept, not a single command this time:** automated GitHub secret scanners flag candidate strings using **entropy**, a measure of how "random" a string looks, rather than just pattern-matching known key formats.

**Why entropy is the signal:** normal source code, comments, and config values are made of real words, variable names, common syntax, all of which are statistically predictable (a human reading `password = "hunter2"` isn't surprised by any of those characters given the ones before them). A real API key or password hash, by contrast, is close to genuinely random data, every character is roughly equally likely regardless of what came before it. High **Shannon entropy** (a formal measure of that unpredictability, borrowed from information theory) is a strong proxy for "this looks like generated/random data, not human-written text," which is exactly the shape of most credentials, tokens, and hashes.

**Why this catches things pattern-matching alone would miss:** a regex can only flag a secret whose *format* is already known (e.g. `AKIA[0-9A-Z]{16}` for an AWS Access Key ID). Entropy detection catches novel or custom-format secrets too, at the cost of more false positives (a long hash-looking test fixture, a base64-encoded image, a UUID, none of these are secrets but all score high on entropy). This is exactly why [[Information Gathering#6.2.4. Open-Source Code (GitHub, GitLab, Gist, SourceForge)|6.2.4]] still recommends manual review even after running an automated scanner, entropy detection is a *filter to check by hand*, not a guaranteed hit.

**Where this comes from:** this is a standard, well-documented technique across secret-scanning tools generally (Gitleaks, TruffleHog, Gitrob all use some form of it), not unique to any one tool, worth recognizing the underlying idea rather than treating it as tool-specific magic.

**Where to look in the response:** both Gitrob and Gitleaks flag high-entropy findings distinctly from pattern-matched ones in their output, usually labeled something like "high entropy string" alongside the file/line it was found in, worth triaging those separately since they carry a higher false-positive rate than a clean regex match.

🔁 **Seen in:** [[Information Gathering#6.2.4. Open-Source Code (GitHub, GitLab, Gist, SourceForge)|Information Gathering, 6.2.4]].

#### Tags: #Gitrob #Gitleaks #EntropyDetection #ShannonEntropy #CommandBreakdowns

---

## Decoding a Nessus CVSS v3.0 Temporal Vector

**Full example:**
```
CVSS v3.0 Temporal Vector: CVSS:3.0/E:F/RL:O/RC:C
```

**Piece by piece:**
- **Why this is needed at all** → the OSCP course material points at a "VPR Key Drivers" panel (Tenable's own proprietary Vulnerability Priority Rating breakdown) that's supposed to show fields like "Exploit Code Maturity" directly. That panel doesn't exist in current Nessus Essentials. Rather than a missing feature being a dead end, the same information is still there, just encoded in the CVSS Temporal Vector string sitting under a finding's Risk Information instead.
- **The vector has three components, each independently meaningful:**
  - `E` (**Exploit Code Maturity**) → how mature/available exploit code actually is. `U` = Unproven (theoretical), `P` = Proof-of-Concept, `F` = Functional (reliable working exploit exists), `H` = High (widely automated, e.g. in Metasploit). `E:F` in the example means a functional exploit exists, worth prioritizing.
  - `RL` (**Remediation Level**) → how complete the fix is. `O` = Official Fix, `T` = Temporary Fix, `W` = Workaround, `U` = Unavailable.
  - `RC` (**Report Confidence**) → how confident the vulnerability report itself is. `U` = Unknown, `R` = Reasonable, `C` = Confirmed.
- **Why this decoding skill matters beyond just this one course quirk** → CVSS Temporal metrics exist specifically to layer real-world exploitability and fix-availability on top of the static CVSS Base score, a Base score alone doesn't tell you whether an exploit actually exists yet. Reading temporal vectors directly is a transferable skill any time a tool's own summary UI doesn't surface a field you need, most raw CVSS data ships as this same compact vector format underneath whatever dashboard sits on top of it.

**A related gotcha worth knowing alongside this:** Nessus groups multiple related CVEs under one plugin when they're closely tied (e.g. two path-traversal CVEs against the same Apache version range). Always check the specific plugin's own **title and Solution field** actually match the version range a question/finding is asking about, rather than assuming the first similar-looking plugin in a `MIXED`-severity group is the right one.

**Where this comes from:** the CVSS v3.0/v3.1 Temporal Metrics specification is published by FIRST.org, the same body that defines the Base score everything else is built on. Tenable's own Nessus documentation confirms the Temporal Vector string format shown in each finding's Risk Information section.

**Where to look in the response:** the vector string appears verbatim under a finding's **Risk Information**, formatted `CVSS:<version>/E:<X>/RL:<X>/RC:<X>`, read left to right, each two-letter code before its colon names the metric, the single letter after names its value.

🔁 **Seen in:** [[Vulnerability Scanning#7.2.4. Analyzing the Results|Vulnerability Scanning, 7.2.4]].

#### Tags: #Nessus #CVSS #TemporalVector #ExploitCodeMaturity #CommandBreakdowns
