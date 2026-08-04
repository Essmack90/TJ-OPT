# Reconnaissance & Enumeration — Command Breakdowns

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

## **Outstanding**
- [ ] SNMP `onesixtyone`/`snmpwalk` OID walking, SMTP `VRFY`/`EXPN` user enumeration mechanics.
