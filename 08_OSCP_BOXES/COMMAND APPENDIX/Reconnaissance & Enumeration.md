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

See [[Information Gathering#6.2.1. WHOIS Enumeration|6.2.1]].

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

See [[Information Gathering#6.2.2. Google Hacking|6.2.2]].

#### Tags: #GoogleHacking #GoogleDorks #GHDB

---

## Other Passive OSINT (no CLI, worth having as reflexes)

- **Netcraft** / **wappalyzer.com/lookup/\<domain\>**: tech-stack fingerprinting, subdomains, site history, purely passive.
- **GitHub search** (`path:users`, or similar path/content searches against an org's repos): accidentally committed credentials. Automated alternative once a repo list gets large: **Gitrob**/**Gitleaks** (need a GitHub personal access token to avoid rate limits).
- **Shodan** (`hostname:<domain>`): indexes internet-connected *devices* rather than website content, banners/open services/known vulns per host, all from prior crawling.
- **securityheaders.com** / **Qualys SSL Labs SSL Server Test**: third-party scanners for missing security headers and weak TLS config, a read on general security hygiene before active testing starts.

See [[Information Gathering#6.2.3. Netcraft|6.2.3]], [[Information Gathering#6.2.4. Open-Source Code (GitHub, GitLab, Gist, SourceForge)|6.2.4]], [[Information Gathering#6.2.5. Shodan|6.2.5]], [[Information Gathering#6.2.6. Security Headers and SSL/TLS|6.2.6]].

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
*A generic wordlist is one-size-fits-all, an LLM-tailored one (prompted with the target's own public info: industry terms, department names, product names) is shaped around that specific org's actual naming conventions, meaningfully higher hit rate. Always cross-check LLM output rather than trusting it as ground truth, see [[Information Gathering#6.3. LLM-Powered Passive Information Gathering|6.3]] for the full risk list.*

See [[Information Gathering#6.5. LLM-Powered Active Information Gathering|6.5]].

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
See [[Information Gathering#6.4.1. DNS Enumeration|6.4.1]], [[Reconnaissance & Enumeration (Breakdowns)|Command Breakdowns]] for the reverse-DNS negative-grep mechanics.

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

See [[Information Gathering#6.4.2. TCP/UDP Port Scanning Theory|6.4.2]].

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

See [[Information Gathering#6.4.4. SMB Enumeration|6.4.4]].

#### Tags: #SMB #NetBIOS #Nbtscan #NetView

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
See [[Information Gathering#6.4.5. SMTP Enumeration|6.4.5]].

#### Tags: #SMTP #VRFY #EXPN #TelnetClient

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

See [[Information Gathering#6.4.6. SNMP Enumeration|6.4.6]].

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
See [[Information Gathering#6.4.3. Port Scanning with Nmap|6.4.3]], [[Vulnerability Scanning#7.3.1. NSE Vulnerability Scripts|7.3.1]], [[Vulnerability Scanning#7.3.2. Working with NSE Scripts|7.3.2]], [[Introduction to Web Application Attacks#8.2.1. Fingerprinting Web Servers with Nmap|8.2.1]], [[Blue|Blue box writeup]] (`smb-vuln-ms17-010` confirming EternalBlue before ever touching Metasploit).

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

See [[Vulnerability Scanning#7.2.1. Installing Nessus|7.2.1]] for the full install walkthrough and troubleshooting box.

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
*Worth reaching for Metasploit directly, rather than a manual PoC, specifically when the bug is a real memory-corruption exploit (like MS17-010/EternalBlue) rather than a scriptable web vulnerability, see [[Locating Public Exploits#13.3.1. Exploit Frameworks|13.3.1]] for where this line sits. Once a session lands:*
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
See [[Introduction to Web Application Attacks#8.2.3. Directory Brute Force with Gobuster|8.2.3]], [[Introduction to Web Application Attacks#8.3.3. Enumerating and Abusing APIs|8.3.3]], [[Client-Side Attacks#12.1.1. Information Gathering|12.1.1]].

#### Tags: #Gobuster #DirectoryBruteForce

---

## Exiftool (Document Metadata Analysis)

```bash
# Show all metadata, including duplicate and "unknown" tags, don't assume the interesting
# data (author, flag, whatever) lands in one specific predictable tag
exiftool -a -u <file>.pdf
```
*Passive recon technique: pull public documents (PDFs, Office files) an org has posted, and check for unscrubbed metadata, author name, creation/modification dates, and critically the exact software (and often OS) used to create the file. No packets ever touch the target's actual network. `Producer`/`Creator Tool` is the key field for planning a client-side payload, e.g. `Microsoft® PowerPoint® for Microsoft 365` confirms Office, no "macOS"/"for Mac" mention is a soft signal the source machine was Windows.*

See [[Client-Side Attacks#12.1.1. Information Gathering|12.1.1]].

#### Tags: #Exiftool #MetadataAnalysis #PassiveRecon

---

## Canarytokens (Client Fingerprinting)

No CLI command, web service at [canarytokens.org](https://canarytokens.org):
1. Pick **Web bug / URL token**, provide an email/webhook for alerts, generate the link
2. Send the link to the target (wrapped in a pretext, never bare)
3. Check **History** once they click, gives IP, rough geolocation, User-Agent, and JS-fingerprinting-derived OS/browser info

*Use before committing to a platform-specific client-side payload (e.g. an HTA that only works against IE/Edge on Windows), confirms what the target is actually running rather than assuming. The JS-derived info is more reliable than the raw User-Agent string alone, since User-Agent is trivially spoofable but the JS fingerprinting actively probes the real browser environment. Note: an AdBlocker on the target's end can suppress the JS fingerprinting script, giving a thinner result, don't assume a sparse fingerprint fully rules something out.*

See [[Client-Side Attacks#12.1.2. Client Fingerprinting|12.1.2]].

#### Tags: #Canarytokens #ClientFingerprinting #DeviceFingerprinting

---

## **Outstanding**
This area grows alongside the modules. Whenever a new recon/enumeration tool comes up (ffuf, whatweb, enum4linux, etc), add it here with a link back to the source section.
