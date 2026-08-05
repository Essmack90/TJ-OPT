# Reconnaissance & Enumeration — Command Appendix

Part of [[COMMAND APPENDIX]]. Nmap and Gobuster, the two workhorse recon tools, plus document metadata analysis and client fingerprinting for client-side-attack prep.

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
```
See [[Information Gathering#6.4.3. Port Scanning with Nmap|6.4.3]], [[Vulnerability Scanning#7.3.1. NSE Vulnerability Scripts|7.3.1]], [[Vulnerability Scanning#7.3.2. Working with NSE Scripts|7.3.2]], [[Introduction to Web Application Attacks#8.2.1. Fingerprinting Web Servers with Nmap|8.2.1]].

#### Tags: #Nmap #NSE

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
