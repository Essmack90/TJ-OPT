# Reconnaissance & Enumeration — Command Appendix

Part of [[COMMAND APPENDIX]]. Nmap and Gobuster, the two workhorse recon tools.

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
```
See [[Introduction to Web Application Attacks#8.2.3. Directory Brute Force with Gobuster|8.2.3]], [[Introduction to Web Application Attacks#8.3.3. Enumerating and Abusing APIs|8.3.3]].

#### Tags: #Gobuster #DirectoryBruteForce

---

## **Outstanding**
This area grows alongside the modules. Whenever a new recon/enumeration tool comes up (ffuf, whatweb, enum4linux, etc), add it here with a link back to the source section.
