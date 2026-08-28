# Reconnaissance & Enumeration, Command Appendix

Part of [[COMMAND APPENDIX]]. Passive OSINT (WHOIS, Google dorking, GitHub secrets), DNS/SMB/SMTP/SNMP active enumeration, Nmap, Nessus, and Gobuster, document metadata analysis, and client fingerprinting for client-side-attack prep.

---

## WHOIS

```bash
# Forward lookup: domain name -> owner info
whois <domain> -h <whois-server-ip-if-in-a-lab>

# Reverse lookup: IP -> who owns the block
whois <ip> -h <whois-server-ip-if-in-a-lab>
```
*Pulls registrant/admin/tech contact names and emails, name servers, and IP netblock ownership, all from a public registration database, nothing touches the target's own infrastructure.*

See [[06. Information Gathering#6.2.1. WHOIS Enumeration|6.2.1]].

#### Tags: #Whois #ForwardLookup #ReverseLookup

---

## Google Dorking

```
site:<domain>                          # restrict to one domain
site:<domain> filetype:pdf             # restrict to a file type (also: ext:)
site:<domain> filetype:txt             # robots.txt, config files, etc, often exposes hidden paths
site:<domain> intext:"github.com"      # find mentions of a source repo
intitle:"index of" "parent directory"  # exposed directory listings
-filetype:html                         # exclude a term/operator
```
*The Google Hacking Database (GHDB) and DorkSearch are pre-built collections of these worth checking before hand-crafting one from scratch.*

See [[06. Information Gathering#6.2.2. Google Hacking|6.2.2]].

#### Tags: #GoogleHacking #GoogleDorks #GHDB

---

## Other Passive OSINT (no CLI, worth having as reflexes)

- **Netcraft** / **wappalyzer.com/lookup/\<domain\>**: tech-stack fingerprinting, subdomains, site history, purely passive.
- **GitHub search** (`path:users`, or similar path/content searches against an org's repos): accidentally committed credentials. Automated alternative once a repo list gets large: **Gitrob**/**Gitleaks** (need a GitHub personal access token to avoid rate limits).
- **Shodan** (`hostname:<domain>`): indexes internet-connected *devices* rather than website content, banners/open services/known vulns per host, all from prior crawling.
- **securityheaders.com** / **Qualys SSL Labs SSL Server Test**: third-party scanners for missing security headers and weak TLS config, a read on general security hygiene before active testing starts.

See [[06. Information Gathering#6.2.3. Netcraft|6.2.3]], [[06. Information Gathering#6.2.4. Open-Source Code (GitHub, GitLab, Gist, SourceForge)|6.2.4]], [[06. Information Gathering#6.2.5. Shodan|6.2.5]], [[06. Information Gathering#6.2.6. Security Headers and SSL/TLS|6.2.6]].

#### Tags: #Netcraft #Shodan #GitHubOSINT #SecurityHeaders #SSLLabs

---

## LLM-Assisted Wordlist Generation

```bash
# Feed the LLM's generated subdomain list straight into Gobuster's DNS mode
gobuster dns -d <domain> -w wordlist.txt -t 10

# Sublist3r/Subfinder pair well with an LLM-generated wordlist too, passive subdomain
# discovery pulled from certificate transparency logs and search engines, no brute force needed
sublist3r -d <domain>
subfinder -d <domain>
```
*A generic wordlist is one-size-fits-all, an LLM-tailored one (prompted with the target's own public info: industry terms, department names, product names) is shaped around that specific org's actual naming conventions, meaningfully higher hit rate. Always cross-check LLM output rather than trusting it as ground truth, see [[06. Information Gathering#6.3. LLM-Powered Passive Information Gathering|6.3]] for the full risk list.*

See [[06. Information Gathering#6.5. LLM-Powered Active Information Gathering|6.5]].

#### Tags: #LLM #Gobuster #WordlistGeneration #DNSBruteForce #Sublist3r #Subfinder

---

## DNS Enumeration

```bash
# Basic lookups
host <domain>                    # A record
host -t mx <domain>              # mail servers + priority
host -t txt <domain>             # TXT records (SPF, verification strings, etc)
host idontexist.<domain>         # NXDOMAIN confirms it doesn't exist

# Manual forward brute force against a wordlist
for ip in $(cat list.txt); do host $ip.<domain>; done

# Reverse brute force across an IP range (see Command Breakdowns for the negative-grep trick)
for ip in $(seq <start> <end>); do host <subnet>.$ip; done | grep -Ev "not found|timed out"

# Automated all-in-one tools
dnsrecon -d <domain> -t std
dnsrecon -d <domain> -D ~/list.txt -t brt
dnsenum <domain>
```
```powershell
# From Windows, no Kali tools available (LOLBAS-style)
nslookup mail.<domain>
nslookup -type=TXT info.<domain> <dns-server-ip>
```
See [[06. Information Gathering#6.4.1. DNS Enumeration|6.4.1]], [[Reconnaissance & Enumeration (Breakdowns)|Command Breakdowns]] for the reverse-DNS negative-grep mechanics.

#### Tags: #DNS #DNSEnumeration #DNSRecon #DNSEnum #Nslookup

---

## Port Scanning Theory (Netcat)

```bash
# Crude TCP port scanner
nc -nvv -w 1 -z <target> <start-port>-<end-port>

# UDP scan (unreliable by nature, closed ports send ICMP unreachable, open/filtered often send nothing)
nc -nv -u -z -w 1 <target> <start-port>-<end-port>
```
`-w 1` = 1 second timeout, `-z` = zero-I/O mode (connection check only, no data sent). Worth doing once to understand the raw TCP handshake/UDP-statelessness mechanics before leaning on Nmap for everything.

See [[06. Information Gathering#6.4.2. TCP/UDP Port Scanning Theory|6.4.2]].

#### Tags: #PortScanning #Netcat #TCPHandshake #UDPScan

---

## SMB Enumeration

```bash
# Port scan + NetBIOS name scan
nmap -v -p 139,445 -oG smb.txt <target-range>
sudo nbtscan -r <subnet>/24

# OS/domain discovery via SMB (needs SMBv1 enabled on target, legacy)
nmap -v -p 139,445 --script smb-os-discovery <target>
```
```cmd
:: From Windows, enumerating shares (LOLBAS-style)
net view \\<target> /all
```
*NetBIOS names are often descriptive of a host's role, useful context to carry into later steps. `/all` on `net view` includes the admin shares (`ADMIN$`, `C$`, `IPC$`).*

```bash
# rpcclient null session (no credentials)
rpcclient -U "" -N TARGET
# Inside: querydominfo  querydispinfo  enumdomusers  enumdomgroups
# netsharegetinfo <sharename>  → share permissions

# enum4linux: full null-session enumeration including share R/W access check
enum4linux TARGET
# Look for: "Mapping: OK, Listing: OK" = anonymous read access to that share

# smbclient null session — list shares, then access one anonymously
smbclient -N -L //TARGET
smbclient -N //TARGET/ShareName
# Inside smbclient: ls  cd DIR\  get FILE  prompt  mget *
```

See [[06. Information Gathering#6.4.4. SMB Enumeration|6.4.4]], [[06. Information Gathering|CS.9]].

#### Tags: #SMB #NetBIOS #Nbtscan #NetView #rpcclient #enum4linux #smbclientNull

---

## SMTP Enumeration

```bash
# VRFY probing via netcat
nc -nv <target> 25
# VRFY <username>    -> 252 accepted, 550 unknown

# Automate with a small Python script (raw socket, VRFY <user>\r\n)
python3 smtp.py <username> <target>
```
```cmd
:: From Windows, Test-NetConnection can only confirm the port is open, need the Telnet client to actually issue VRFY
dism /online /Enable-Feature /FeatureName:TelnetClient
telnet <target> 25
VRFY <username>
```
```bash
# smtp-user-enum: RCPT mode (more reliable than VRFY on modern servers)
smtp-user-enum -M RCPT -U users.list -D domain.htb -t TARGET

# nc POP3 manual session (cleartext port 110)
nc -nv TARGET 110
# user USERNAME → pass PASSWORD → list → retr 1 → quit
```

See [[06. Information Gathering#6.4.5. SMTP Enumeration|6.4.5]], [[06. Information Gathering#6.4.9. IMAP / POP3 Enumeration (Ports 110/143/993/995)|FP.6]], [[06. Information Gathering|CS.8]].

#### Tags: #SMTP #VRFY #EXPN #TelnetClient #smtpUserEnum #POP3

---

## SNMP Enumeration

```bash
# Find SNMP services first (UDP, easy to miss with a default scan)
sudo nmap -sU --open -p 161 <target-range> -oG open-snmp.txt

# Brute force community strings across a host list
echo public > community && echo private >> community && echo manager >> community
onesixtyone -c community -i ips

# Walk the MIB tree once you have a working community string (usually "public")
snmpwalk -c public -v1 -t 10 <target>                              # entire tree
snmpwalk -c public -v1 <target> 1.3.6.1.4.1.77.1.2.25              # Windows user accounts
snmpwalk -c public -v1 <target> 1.3.6.1.2.1.25.4.2.1.2             # running processes
snmpwalk -c public -v1 <target> 1.3.6.1.2.1.25.6.3.1.2             # installed software
```
*Cross-referencing running processes against installed software versions is a great way to spot exactly which vulnerable app version is running. SNMP v1/v2/v2c has no encryption at all, and default `public`/`private` community strings are still genuinely common in the wild.*

See [[06. Information Gathering#6.4.6. SNMP Enumeration|6.4.6]].

#### Tags: #SNMP #Snmpwalk #Onesixtyone #MIBTree #CommunityStrings

---

## Nmap

```bash
# Basic service/version scan
sudo nmap -p80 -sV <target>

# Full port range, fast
nmap -p- --min-rate 5000 <target>

# Web-specific NSE fingerprinting
sudo nmap -p80 --script=http-enum <target>

# Run every NSE script in the "vuln" category
sudo nmap -sV -p <port> --script "vuln" <target>

# List every script in a given category from the local NSE index
cd /usr/share/nmap/scripts/
cat script.db | grep "\"vuln\""

# Re-index NSE after adding a custom script
sudo nmap --script-updatedb

# Run a specific custom/downloaded NSE script
sudo nmap -sV -p <port> --script "<script-name>" <target>

# Check a specific well-known CVE's dedicated NSE script directly (faster than the full
# "vuln" category sweep once you already suspect one specific bug, e.g. an old SMB banner)
sudo nmap -p 445 --script smb-vuln-ms17-010 <target>
```
See [[06. Information Gathering#6.4.3. Port Scanning with Nmap|6.4.3]], [[07. Vulnerability Scanning#7.3.1. NSE Vulnerability Scripts|7.3.1]], [[07. Vulnerability Scanning#7.3.2. Working with NSE Scripts|7.3.2]], [[08. Introduction to Web Application Attacks#8.2.1. Fingerprinting Web Servers with Nmap|8.2.1]], [[Blue|Blue box writeup]] (`smb-vuln-ms17-010` confirming EternalBlue before ever touching Metasploit).

#### Tags: #Nmap #NSE

---

## Nessus (Install & CLI)

```bash
# Verify the downloaded .deb before installing, never skip this
echo "<paste-checksum-from-download-page> Nessus-<version>-debian10_amd64.deb" > sha256sum_nessus
sha256sum -c sha256sum_nessus
# Expect: Nessus-<version>-debian10_amd64.deb: OK

sudo apt install ./Nessus-<version>-debian10_amd64.deb
sudo systemctl start nessusd.service
sudo systemctl status nessusd.service   # if it fails to start or :8834 won't load

# License renewal / "license expired" on Nessus Essentials (a genuine 30-day license, not indefinite)
sudo /opt/nessus/sbin/nessuscli fetch --register <XXXX-XXXX-XXXX-XXXX-XXXX>
sudo systemctl restart nessusd.service
```
*A checksum `FAILED` means the download is corrupted or incomplete, delete and re-download rather than trying to install anyway. Get a fresh activation code from Nessus Essentials' own "Register now" form (not a Tenable account login) before running `nessuscli fetch --register`, an old/reused code won't work.*

See [[07. Vulnerability Scanning#7.2.1. Installing Nessus|7.2.1]] for the full install walkthrough and troubleshooting box.

#### Tags: #Nessus #NessusInstall #Checksum #ActivationCode

---

## Metasploit (quick reference)

```
msfconsole
msf > search <exploit name, e.g. eternalblue>
msf > use <module number or path>
msf exploit(...) > set RHOSTS <target>
msf exploit(...) > set LHOST <your_tun0_ip>
msf exploit(...) > run
```
*Worth reaching for Metasploit directly, rather than a manual PoC, specifically when the bug is a real memory-corruption exploit (like MS17-010/EternalBlue) rather than a scriptable web vulnerability, see [[13. Locating Public Exploits#13.3.1. Exploit Frameworks|13.3.1]] for where this line sits. Once a session lands:*
```
meterpreter > getuid          # confirm privilege level immediately
meterpreter > shell           # drop into a normal cmd/bash shell
```

See [[Blue|Blue box writeup]] for the full worked EternalBlue chain.

#### Tags: #Metasploit #Meterpreter #EternalBlue

---

## Gobuster

```bash
# Directory/file brute force
gobuster dir -u http://<target> -w /usr/share/wordlists/dirb/common.txt -t 5

# With extensions
gobuster dir -u http://<target> -w /usr/share/wordlists/dirb/big.txt -x php,txt,html,bak

# API path brute force with a version-number pattern file (containing {GOBUSTER}/v1 etc.)
gobuster dir -u http://<target>:<port> -w /usr/share/wordlists/dirb/big.txt -p pattern

# Brute force for a specific file extension (e.g. hunting for public documents to metadata-mine)
gobuster dir -u http://<target>/ -w /usr/share/wordlists/dirb/common.txt -x pdf -t 50
```
See [[08. Introduction to Web Application Attacks#8.2.3. Directory Brute Force with Gobuster|8.2.3]], [[08. Introduction to Web Application Attacks#8.3.3. Enumerating and Abusing APIs|8.3.3]], [[12. Client-Side Attacks#12.1.1. Information Gathering|12.1.1]].

#### Tags: #Gobuster #DirectoryBruteForce

---

## Ffuf (Web Fuzzer)

Faster and more flexible than Gobuster for web content discovery. Covers directory fuzzing, page/extension fuzzing, recursive scanning, vhost/sub-domain fuzzing, and GET/POST parameter + value brute-forcing in one tool.

```bash
# ── Directory fuzzing ────────────────────────────────────────────────────────
ffuf -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-small.txt:FUZZ \
     -u 'http://TARGET:PORT/FUZZ'

# ── Extension fuzzing (what file types does this server serve?) ──────────────
# Probe the index page — anything that returns 200 or 403 is a live extension
ffuf -w /usr/share/seclists/Discovery/Web-Content/web-extensions.txt:FUZZ \
     -u 'http://TARGET:PORT/indexFUZZ'

# ── Page fuzzing with known extension ───────────────────────────────────────
ffuf -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-small.txt:FUZZ \
     -u 'http://TARGET:PORT/blog/FUZZ.php'

# ── Recursive fuzzing (directory + pages in one pass) ───────────────────────
ffuf -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-small.txt:FUZZ \
     -u 'http://TARGET:PORT/FUZZ' \
     -recursion -recursion-depth 1 \
     -e '.php'

# ── Sub-domain fuzzing (real DNS resolution) ─────────────────────────────────
ffuf -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt:FUZZ \
     -u 'http://FUZZ.domain.com/'

# ── VHost fuzzing (Host-header injection, no DNS needed) ────────────────────
# Step 1: no filter — note the noise response size
ffuf -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt:FUZZ \
     -u http://domain.htb:PORT/ \
     -H 'Host: FUZZ.domain.htb'
# Step 2: filter noise by size (-fs) or use -ac to auto-calibrate
ffuf -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt:FUZZ \
     -u http://domain.htb:PORT/ \
     -H 'Host: FUZZ.domain.htb' \
     -fs 986            # or: -ac

# ── GET parameter fuzzing ────────────────────────────────────────────────────
ffuf -w /usr/share/seclists/Discovery/Web-Content/burp-parameter-names.txt:FUZZ \
     -u 'http://TARGET:PORT/page.php?FUZZ=key' \
     -fs 798            # filter the "invalid parameter" response size

# ── POST parameter fuzzing ───────────────────────────────────────────────────
ffuf -w /usr/share/seclists/Discovery/Web-Content/burp-parameter-names.txt:FUZZ \
     -u 'http://TARGET:PORT/page.php' \
     -X POST -d 'FUZZ=key' \
     -H 'Content-Type: application/x-www-form-urlencoded' \
     -fs 774

# ── Value fuzzing (POST) ─────────────────────────────────────────────────────
for i in $(seq 1 1000); do echo $i >> ids.txt; done   # build a numeric wordlist
ffuf -w ids.txt:FUZZ \
     -u 'http://TARGET:PORT/page.php' \
     -X POST -d 'id=FUZZ' \
     -H 'Content-Type: application/x-www-form-urlencoded' \
     -fs 768

# ── Match by response body regex (-mr) ──────────────────────────────────────
# Skip the two-step size-filter workflow — only show pages whose body matches
ffuf -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-small.txt:FUZZ \
     -u 'http://TARGET:PORT/FUZZ' \
     -recursion -recursion-depth 1 -e '.php,.php7' \
     -mr "You don't have access!" -t 100
```

**Key flags quick-ref:**
| Flag | Purpose |
|------|---------|
| `-e .php,.html` | Append extensions to each wordlist word |
| `-fs N` | Filter out responses of exactly N bytes |
| `-fw N` / `-fl N` | Filter by word or line count instead |
| `-ac` | Auto-calibrate filtering (no manual size-noting needed) |
| `-mr "regex"` | Only show responses whose body matches the regex |
| `-recursion -recursion-depth 1` | Auto-recurse into found directories |
| `-t 100` | 100 threads for speed (default 40) |
| `-s` | Silent mode (results only, no banner) |

🔁 [[08. Introduction to Web Application Attacks|Introduction to Web Application Attacks]]

#### Tags: #Ffuf #WebFuzzing #DirectoryFuzzing #VHostFuzzing #ParameterFuzzing #ExtensionFuzzing

---

## Exiftool (Document Metadata Analysis)

```bash
# Show all metadata, including duplicate and "unknown" tags, don't assume the interesting
# data (author, flag, whatever) lands in one specific predictable tag
exiftool -a -u <file>.pdf
```
*Passive recon technique: pull public documents (PDFs, Office files) an org has posted, and check for unscrubbed metadata, author name, creation/modification dates, and critically the exact software (and often OS) used to create the file. No packets ever touch the target's actual network. `Producer`/`Creator Tool` is the key field for planning a client-side payload, e.g. `Microsoft® PowerPoint® for Microsoft 365` confirms Office, no "macOS"/"for Mac" mention is a soft signal the source machine was Windows.*

See [[12. Client-Side Attacks#12.1.1. Information Gathering|12.1.1]].

#### Tags: #Exiftool #MetadataAnalysis #PassiveRecon

---

## Canarytokens (Client Fingerprinting)

No CLI command, web service at [canarytokens.org](https://canarytokens.org):
1. Pick **Web bug / URL token**, provide an email/webhook for alerts, generate the link
2. Send the link to the target (wrapped in a pretext, never bare)
3. Check **History** once they click, gives IP, rough geolocation, User-Agent, and JS-fingerprinting-derived OS/browser info

*Use before committing to a platform-specific client-side payload (e.g. an HTA that only works against IE/Edge on Windows), confirms what the target is actually running rather than assuming. The JS-derived info is more reliable than the raw User-Agent string alone, since User-Agent is trivially spoofable but the JS fingerprinting actively probes the real browser environment. Note: an AdBlocker on the target's end can suppress the JS fingerprinting script, giving a thinner result, don't assume a sparse fingerprint fully rules something out.*

See [[12. Client-Side Attacks#12.1.2. Client Fingerprinting|12.1.2]].

#### Tags: #Canarytokens #ClientFingerprinting #DeviceFingerprinting

---

## FTP Enumeration and Attack

```bash
# Anonymous login check
ftp TARGET PORT      # username: anonymous / password: anything@email.com
# Inside: passive  dir  prompt  mget *  get FILE  bye

# Bruteforce with Hydra (throttle to -t 1 if server returns 550 errors)
hydra -l username -P /usr/share/wordlists/rockyou.txt ftp://TARGET -t 1
```

🔁 [[06. Information Gathering#6.4.7. FTP Enumeration (Port 21)|FP.1]], [[06. Information Gathering|CS.10]]

#### Tags: #FTP #Anonymous #HydraFTP

---

## DNS Subdomain Brute Force (subbrute)

```bash
git clone https://github.com/TheRook/subbrute.git && cd subbrute
echo TARGET_IP > resolvers.txt    # point at the target's own nameserver
python3 subbrute.py domain.htb -s /usr/share/seclists/Discovery/DNS/namelist.txt -r resolvers.txt

# After finding subdomains, zone transfer each one and grep for TXT records
dig axfr subdomain.domain.htb @TARGET_IP | grep "TXT"
```

Use when the target runs split-horizon DNS: public resolvers return NXDOMAIN but the internal NS has the real records.

🔁 [[06. Information Gathering|CS.7]], [[06. Information Gathering#6.4.1. DNS Enumeration|FP.4]]

#### Tags: #DNS #subbrute #SubdomainBruteForce #AXFR

---

## Web Fingerprinting

```bash
# Virtual host enumeration (important: --append-domain so gobuster adds the base domain)
gobuster vhost -u http://domain.htb -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt --append-domain

# HTTP header fingerprinting (check Server: header)
curl -I http://TARGET

# CMS detection from meta tags
curl -s http://TARGET | grep -i "generator"

# Web server fingerprinting with nikto (-Tuning b = software identification only, no attacks)
nikto -host http://TARGET -Tuning b
```

```python
# Scrapy / ReconSpider — crawl and extract links, comments, emails, JS files
git clone https://github.com/bhavsec/reconspider.git
python3 reconspider.py http://TARGET
# Parse output:  cat results.json | python3 -m json.tool | grep -A5 '"comments"'
# jq queries:    cat results.json | jq '.emails[]'
```

🔁 [[06. Information Gathering#6.6.1. Virtual Host (vHost) Enumeration|IGWE.1]], [[06. Information Gathering#6.6.2. Web Server Fingerprinting|IGWE.2]], [[06. Information Gathering#6.6.3. Web Crawling with scrapy / ReconSpider|IGWE.3]]

#### Tags: #VirtualHost #gobusterVhost #nikto #scrapy #ReconSpider #WebFingerprinting

---

## OpenVAS (GVM)

```bash
# Start the OpenVAS / GVM stack
sudo gvm-start
# Web UI at: https://localhost:8080  (default admin:admin — change on first login)
```

Key scan workflow (UI):
1. **Configuration → Targets** → New Target → enter IP/range
2. **Configuration → Credentials** → add SSH/SMB creds if authenticated scan
3. **Scans → Tasks** → New Task → select Target + Scanner → Save → Launch (▶)
4. **Scans → Reports** → click report → filter by severity
5. **Scans → Vulnerabilities** → filter by QoD ≥ 70 to reduce false positives
6. **Assets → Hosts / Operating Systems** → see what GVM identified

🔁 [[07. Vulnerability Scanning#7.3b. OpenVAS / GVM|7.3b]]

#### Tags: #OpenVAS #GVM #VulnerabilityScanning #Authenticated
## External Resources

- [HackTricks - Windows and Linux Pentesting Index](https://hacktricks.wiki/en/index.html)
- [PayloadsAllTheThings - Methodology and Resources](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Methodology%20and%20Resources)
- [RevShells](https://www.revshells.com/) for shell payload selection
- [CyberChef](https://gchq.github.io/CyberChef/) for encoding and decoding
- [ippsec.rocks](https://ippsec.rocks/) for technique walkthrough searches
