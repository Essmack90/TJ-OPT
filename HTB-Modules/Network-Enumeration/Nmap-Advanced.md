---
tags: [module, nmap, scanning, advanced, practical]
module: "Introduction to Nmap"
level: advanced
difficulty: easy
---

# Nmap - Practical Scanning Guide #nmap #scanning #practical

## The Four Scanning Phases #methodology

Nmap operations can be broken down into four distinct phases:

Phase 1: Host Discovery - Find live hosts
Commands: nmap -sn 192.168.1.0/24

Phase 2: Port Scanning - Find open ports
Commands: nmap -sS -p- target.com

Phase 3: Service Enumeration - Identify versions
Commands: nmap -sV target.com

Phase 4: OS Detection - Identify OS
Commands: nmap -O target.com

Phase 5: Scripting - Automate tasks
Commands: nmap --script vuln target.com

---

## Scan Techniques Reference #cheatsheet #scan-types

TCP SYN Scan (-sS)
Half-open scan, never completes handshake
Stealth Level: High

TCP Connect Scan (-sT)
Completes full TCP handshake
Stealth Level: Low

UDP Scan (-sU)
Scans UDP ports (slow)
Stealth Level: Medium

TCP ACK Scan (-sA)
Maps firewall rules
Stealth Level: N/A

TCP Window Scan (-sW)
Similar to ACK, detects open ports
Stealth Level: Medium

TCP Maimon Scan (-sM)
Uses FIN/ACK probe
Stealth Level: Medium

TCP Null Scan (-sN)
No flags set
Stealth Level: Medium

TCP FIN Scan (-sF)
FIN flag only
Stealth Level: Medium

TCP Xmas Scan (-sX)
FIN, PSH, URG flags
Stealth Level: Medium

IP Protocol Scan (-sO)
Determines IP protocols supported
Stealth Level: Medium

---

## Practical Port Scanning Strategies #strategies

### Strategy 1: Quick Scan (Initial Recon)

Fast scan of top 1000 ports
sudo nmap -sS -T4 target.com

Fast scan with version detection on common ports
sudo nmap -sS -sV -T4 target.com

Scan all ports quickly (risky, may be detected)
sudo nmap -sS -T4 -p- target.com

### Strategy 2: Stealthy Scan (Avoid Detection)

Slow scan to avoid IDS
sudo nmap -sS -T2 -p- target.com

Decoy scan (spoof source IPs)
sudo nmap -sS -D RND:10 target.com

Fragment packets to evade firewalls
sudo nmap -sS -f target.com

### Strategy 3: Comprehensive Scan (Deep Enumeration)

Full port scan with service versions and default scripts
sudo nmap -sC -sV -p- target.com

Add OS detection
sudo nmap -sC -sV -O -p- target.com

Output to all formats for reporting
sudo nmap -sC -sV -p- -oA full-scan target.com

### Strategy 4: Firewall/IDS Testing

ACK scan to map firewall rules
sudo nmap -sA target.com

IP protocol scan
sudo nmap -sO target.com

MTU manipulation
sudo nmap --mtu 24 target.com

---

## Nmap Output Formats #output

Normal format (-oN): Human readable
XML format (-oX): Machine parsing, tools
Grepable format (-oG): Grep-friendly
All formats (-oA): Save all three

Examples:
sudo nmap -sV -oN scan.txt target.com
sudo nmap -sV -oX scan.xml target.com
sudo nmap -sV -oG scan.gnmap target.com
sudo nmap -sV -oA full-scan target.com

---

## Nmap Timing Templates #timing

-T0 (Paranoid): Extremely slow - IDS evasion
-T1 (Sneaky): Very slow - IDS evasion
-T2 (Polite): Slow - Conservative scanning
-T3 (Normal): Default - General use
-T4 (Aggressive): Fast - Reliable networks
-T5 (Insane): Very fast - May miss ports

---

## The Nmap Scripting Engine (NSE) #nse #scripts

### Script Categories

auth: Authentication bypass (http-auth-finder)
broadcast: Broadcast discovery (broadcast-dhcp-discover)
brute: Brute force attacks (http-brute)
default: Default scripts (-sC uses these)
discovery: Service discovery (smb-enum-shares)
dos: Denial of service (http-slowloris)
exploit: Exploit vulnerabilities (smb-vuln-ms17-010)
external: External services (whois-domain)
fuzzer: Fuzzing scripts (http-form-fuzzer)
intrusive: May crash services (Many vuln scripts)
malware: Malware detection (http-malware-host)
safe: Won't crash things (ssl-enum-ciphers)
version: Version detection (-sV uses these)
vuln: Vulnerability checks (smb-vuln-*)

### Useful NSE Commands

List all scripts:
ls /usr/share/nmap/scripts/

Run specific script:
sudo nmap --script smb-vuln-ms17-010 -p445 target.com

Run multiple scripts:
sudo nmap --script http-enum,http-title target.com

Run category:
sudo nmap --script vuln target.com

Update scripts:
sudo nmap --script-updatedb

---

## Service Version Detection #version-detection

### Intensity Levels

-sV : Level 7 - Light version detection
--version-intensity 0-9 : Custom - 0=light, 9=all probes
--version-light : Level 2 - Alias for intensity 2
--version-all : Level 9 - Alias for intensity 9

Example:
sudo nmap -sV --version-intensity 5 target.com

---

## OS Detection #os-detection

Basic OS detection:
sudo nmap -O target.com

Aggressive OS detection:
sudo nmap -O --osscan-guess target.com

---

## Practical Examples #examples

### Example 1: HTB Machine Initial Scan
sudo nmap -sC -sV -oA htb-initial 10.10.10.10

### Example 2: Full Network Scan
sudo nmap -sS -sV -O -p- 192.168.1.0/24 -oA network-scan

### Example 3: Web Server Focus
sudo nmap -sS -sV -p80,443,8080,8443 --script http-* target.com

### Example 4: SMB Vulnerability Check
sudo nmap -p445 --script smb-vuln* target.com

---

## Alternative Tools #alternatives

masscan: Internet-scale scanning
masscan -p80 0.0.0.0/0

rustscan: Ultra-fast port discovery
rustscan -a target.com

naabu: Fast port scanner
naabu -host target.com

unicornscan: Asynchronous scanning
unicornscan target.com

---

## Key Takeaways #keypoints

- Nmap has four main phases: host discovery, port scanning, service detection, OS detection
- Different scan types serve different purposes (SYN for stealth, ACK for firewall mapping)
- Timing templates balance speed and stealth (-T0 to -T5)
- The NSE has hundreds of scripts organized by category
- Always verify SERVICE column guesses manually
- Save outputs in multiple formats with -oA
- Update your NSE scripts regularly
- Combine with other tools for best results
