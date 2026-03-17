---
tags: [module, nmap, service-enumeration, version-detection, advanced, practical]
module: "Service Enumeration"
level: advanced
---

# Service Enumeration - Complete Reference #serviceenum #versiondetection #advanced

## The Importance of Accurate Version Detection #core

Exact version numbers allow us to:

- Search for known vulnerabilities matching that specific version
- Analyze source code for that version (if available)
- Find exploits that fit both the service AND operating system
- Tailor attacks to the exact target configuration
- Determine patch levels and security posture

**Rule:** The more precise your version detection, the higher your success rate.

---

## Strategic Scanning Approach #strategy

### Phase 1: Quick Discovery (Minimal Traffic)

sudo nmap -T4 -F -sS target.com -oA quick

### Phase 2: Full Port Scan (Background)

sudo nmap -p- -T4 -sS target.com -oA full-portscan &

### Phase 3: Targeted Version Detection

sudo nmap -p $(grep open full-portscan.gnmap | cut -d' ' -f2 | cut -d'/' -f1 | tr '\n' ',') -sV -sC target.com -oA version

### Phase 4: Manual Verification of Critical Ports

nc -nv target.com 25
openssl s_client -connect target.com:443
telnet target.com 80
HEAD / HTTP/1.0

---

## Advanced Progress Monitoring #progress

### Real-time Status Updates

sudo nmap target.com -p- -sV --stats-every=10s

### Custom Timing Calculations

sudo nmap target.com -p- -sV --min-rate 100 --max-retries 2 --stats-every=30s

### Verbosity Levels

| Level | Flag | What It Shows |
|-------|------|---------------|
| Normal | (none) | Final results only |
| Verbose | -v | Open ports as discovered, extra details |
| Very Verbose | -vv | All of the above plus packet-level details |

### Example with High Verbosity

sudo nmap target.com -p- -sV -vv

Discovered open port 22/tcp on 10.129.2.28
Discovered open port 80/tcp on 10.129.2.28
Discovered open port 443/tcp on 10.129.2.28
SYN Stealth Scan Timing: About 42.67% done

---

## Banner Grabbing Deep Dive #bannergrabbing

### What Are Banners?

After a successful three-way handshake, many services send an identification banner. This happens at the network level with a PSH flag in the TCP header.

### Manual Banner Grabbing Techniques

**Netcat (generic):**
nc -nv target.com 22
nc -nv target.com 80
nc -nv target.com 443

**OpenSSL (SSL/TLS):**
openssl s_client -connect target.com:443 -quiet
openssl s_client -connect target.com:995 -quiet

**HTTP specific:**
telnet target.com 80
HEAD / HTTP/1.0
Host: target.com

**SMTP specific:**
telnet target.com 25
HELO test.com

**FTP specific:**
ftp target.com
USER anonymous

### Banner Grabbing Script

#!/bin/bash
TARGET=$1
PORTS=(21 22 23 25 80 110 143 443 445 993 995 3306 3389 5432 5900 8080)

for PORT in "${PORTS[@]}"; do
    echo "=== Port $PORT ==="
    timeout 2 nc -nv $TARGET $PORT 2>/dev/null
    echo ""
done

---

## The Nmap Banner Grabbing Limitation #limitations

### The Problem

Nmap sometimes misses information in banners. Look at this example:

**Nmap output:**
25/tcp open  smtp    Postfix smtpd

**Actual banner received by Nmap:**
NSOCK INFO: Callback: READ SUCCESS [10.129.2.28:25] (35 bytes): 220 inlane ESMTP Postfix (Ubuntu)..

Nmap received "Ubuntu" but didn't display it!

### Why This Happens

Nmap's service detection uses signature matching against a database. Sometimes the signature doesn't include all banner information, or the parser fails to extract certain fields.

### The Solution

Always verify critical ports manually. Banner grabbing with netcat or telnet often reveals information Nmap misses.

---

## Packet-Level Analysis with tcpdump #packetanalysis

### Setup

Terminal 1: Start packet capture
sudo tcpdump -i eth0 host 10.10.14.2 and 10.129.2.28 -w smtp-handshake.pcap

Terminal 2: Connect to service
nc -nv 10.129.2.28 25

### Packet Breakdown

18:28:07.128564 IP 10.10.14.2.59618 > 10.129.2.28.smtp: Flags [S], seq 1798872233, win 65535
18:28:07.255151 IP 10.129.2.28.smtp > 10.10.14.2.59618: Flags [S.], seq 1130574379, ack 1798872234, win 65160
18:28:07.255281 IP 10.10.14.2.59618 > 10.129.2.28.smtp: Flags [.], ack 1
18:28:07.319306 IP 10.129.2.28.smtp > 10.10.14.2.59618: Flags [P.], seq 1:36, ack 1, length 35: SMTP: 220 inlane ESMTP Postfix (Ubuntu)
18:28:07.319426 IP 10.10.14.2.59618 > 10.129.2.28.smtp: Flags [.], ack 36

### TCP Flag Reference

| Flag | Name | Meaning |
|------|------|---------|
| [S] | SYN | Synchronize - start connection |
| [S.] | SYN-ACK | Synchronize-Acknowledge - confirm and respond |
| [.] | ACK | Acknowledge - confirm receipt |
| [P.] | PSH-ACK | Push-Acknowledge - sending data |
| [F.] | FIN-ACK | Finish-Acknowledge - closing connection |
| [R] | RST | Reset - abort connection |

### The Three-Way Handshake

1. Client -> Server: [S] (SYN) - "Can we talk?"
2. Server -> Client: [S.] (SYN-ACK) - "Yes, let's talk"
3. Client -> Server: [.] (ACK) - "OK, connected"

### Data Transfer

After handshake, server sends [P.] (PSH-ACK) containing the banner. PSH tells the client "here's data immediately."

---

## Service Version Detection Automation #automation

### Script 1: Extract All Versions to CSV

#!/bin/bash
# extract-versions.sh
SCAN_XML=$1
echo "Port,Service,Version,CPE" > versions.csv
xmlstarlet sel -t -v "//port[state/@state='open']/concat(@portid,',',service/@name,',',service/@version,',',service/@cpe)" $SCAN_XML >> versions.csv
echo "Saved to versions.csv"

### Script 2: Search Exploits for Detected Versions

#!/bin/bash
# search-exploits.sh
SCAN_XML=$1
xmlstarlet sel -t -v "//port[state/@state='open']/service/@version" $SCAN_XML | while read VERSION; do
    if [ ! -z "$VERSION" ]; then
        echo "=== Searching for $VERSION ==="
        searchsploit "$VERSION" 2>/dev/null | grep -v "Exploit Title"
    fi
done

### Script 3: Verify Banners Manually

#!/bin/bash
# grab-banners.sh
TARGET=$1
PORTS=$(xmlstarlet sel -t -v "//port[state/@state='open']/@portid" $2 | tr '\n' ' ')

for PORT in $PORTS; do
    echo "=== Port $PORT Banner ==="
    timeout 2 nc -nv $TARGET $PORT 2>&1 | head -5
    echo ""
done

---

## Service Detection Optimization #optimization

### Version Intensity Levels

| Level | Flag | Probes | Use Case |
|-------|------|--------|----------|
| 0-2 | --version-light | 5-10 | Quick scans, many ports |
| 3-5 | (default) | 10-20 | Balanced |
| 6-7 | --version-intensity 7 | 20-30 | Deep scanning |
| 8-9 | --version-all | All | Maximum accuracy |

### Example with Custom Intensity

sudo nmap target.com -p 80,443,22 -sV --version-intensity 9

### Version Detection Tuning

| Option | Purpose |
|--------|---------|
| --version-trace | Show version detection process |
| --version-light | Alias for intensity 2 |
| --version-all | Alias for intensity 9 |
| --version-intensity 0-9 | Set custom intensity |

---

## Service-Specific Enumeration Techniques #service-specific

### Web Servers (Port 80,443)
- whatweb target.com
- curl -I target.com
- wget -S target.com

### SSH (Port 22)
- ssh-keyscan target.com
- ssh -v target.com

### SMTP (Port 25)
- nc -nv target.com 25
- VRFY root
- EXPN
- EHLO test.com

### FTP (Port 21)
- ftp target.com
- USER anonymous
- PASS anonymous
- SYST
- STAT

### SMB (Port 445)
- smbclient -L //target.com -N
- enum4linux target.com
- crackmapexec smb target.com

### DNS (Port 53)
- dig version.bind CHAOS TXT @target.com
- nslookup -type=TXT version.bind CHAOS target.com

### MySQL (Port 3306)
- mysql -h target.com -u root
- mysql -h target.com -u anonymous

---

## Alternative Tools #alternatives

| Tool | Purpose | Command |
|------|---------|---------|
| [[whatweb]] | Web service detection | whatweb target.com |
| [[wappalyzer]] | Browser-based detection | (browser extension) |
| [[amap]] | Application mapper | amap -B target.com 80 |
| [[masscan]] | Fast port discovery | masscan -p80 target.com |
| [[rustscan]] | Ultra-fast discovery | rustscan -a target.com |
| [[nmap]] with NSE | Service scripts | nmap --script=banner target.com |

---

## Key Takeaways #keypoints

- Version numbers are the key to finding specific exploits
- Scan strategically: quick first, full in background
- Use --stats-every to monitor long scans
- Increase verbosity to see results immediately
- Nmap may miss banner information - always verify manually
- Manual banner grabbing with nc reveals hidden details
- tcpdump lets you analyze the full TCP conversation
- The PSH flag indicates data being sent
- Different services require different enumeration techniques
- Automate version extraction and exploit searching
- Report incorrect Nmap results at https://nmap.org/submit/
- The combination of automated scanning and manual verification yields the best results
