---
tags: [module, nmap, port-scanning, advanced, practical]
module: "Host and Port Scanning"
level: advanced
---

# Host and Port Scanning - Complete Reference #nmap #portscanning #advanced

## Complete Port State Reference #port-states

| State | Detection Method | Meaning | Action |
|-------|------------------|---------|--------|
| open | SYN-ACK received | Service is listening | Target for -sV and exploitation |
| closed | RST received | No service listening | Usually ignore, but can indicate filtering |
| filtered | No response or ICMP error | Firewall blocking | Try different scan types, spoofing, or source ports |
| unfiltered | RST received (ACK scan only) | Port accessible but state unknown | Use SYN scan to determine open/closed |
| open\|filtered | No response (UDP/FIN scans) | Open or blocked | Use -sV or different scan type |
| closed\|filtered | Idle scan only | Can't determine | Use different scan method |

---

## TCP Scan Techniques Reference #scan-types

| Technique | Command | How It Works | Stealth | Use Case |
|-----------|---------|--------------|---------|----------|
| SYN Scan | -sS | Send SYN, wait for SYN-ACK (open) or RST (closed) | High | Default, fast, stealthy |
| Connect Scan | -sT | Full TCP handshake using connect() system call | Low | No root privileges needed |
| NULL Scan | -sN | Packet with no flags set | Medium | Bypass non-stateful firewalls |
| FIN Scan | -sF | Packet with only FIN flag | Medium | Bypass non-stateful firewalls |
| Xmas Scan | -sX | Packet with FIN, PSH, URG flags | Medium | Bypass non-stateful firewalls |
| ACK Scan | -sA | Send ACK packet | N/A | Map firewall rules |
| Window Scan | -sW | Like ACK, but examines window field | Low | Detect open ports on some systems |
| Maimon Scan | -sM | Send FIN/ACK packet | Low | BSD-based systems |
| Custom Flags | --scanflags | Specify any TCP flag combination | Variable | Stealth/evasion |
| Idle Scan | -sI | Zombie host bounce scan | Very High | Blind scan, hide source |

---

## TCP Scan Behavior Reference #tcp-behavior

| Scan Type | Open Port Response | Closed Port Response | Filtered Response |
|-----------|-------------------|----------------------|-------------------|
| SYN (-sS) | SYN-ACK | RST | No response / ICMP unreachable |
| Connect (-sT) | Connection succeeds | Connection refused | Timeout |
| NULL (-sN) | No response | RST | ICMP unreachable |
| FIN (-sF) | No response | RST | ICMP unreachable |
| Xmas (-sX) | No response | RST | ICMP unreachable |
| ACK (-sA) | RST (with TTL info) | RST | ICMP unreachable / no response |
| Window (-sW) | RST with positive window | RST with zero window | ICMP unreachable |
| Maimon (-sM) | No response (BSD) | RST | ICMP unreachable |

---

## UDP Scan Behavior Reference #udp-behavior

| Scenario | Response | Port State |
|----------|----------|------------|
| Service replies | UDP packet | open |
| ICMP type 3, code 3 | Port unreachable | closed |
| ICMP type 3, other codes | Other unreachable | filtered |
| No response | Timeout | open\|filtered |

**Note:** Many systems rate-limit ICMP port unreachable messages. Linux limits to 1 per second by default.

---

## Practical Port Scanning Strategies #strategies

### Strategy 1: Quick Initial Scan (All Ports)
sudo nmap -sS -p- -T4 --min-rate 1000 target.com -oA quick-full

### Strategy 2: Stealthy SYN Scan (Common Ports)
sudo nmap -sS -T2 --top-ports 1000 -Pn -n target.com -oA stealth

### Strategy 3: Firewall/IDS Evasion
sudo nmap -sS -f --mtu 24 -D RND:10 --source-port 53 target.com

### Strategy 4: Comprehensive Scan with Version Detection
sudo nmap -sS -sV -sC -O -p- --version-intensity 9 -T4 target.com -oA comprehensive

### Strategy 5: UDP Scan (Common Ports)
sudo nmap -sU --top-ports 50 --max-retries 1 -T4 target.com -oA udp-scan

### Strategy 6: SCTP Scan
sudo nmap -sY -p 2905,2906,2910,33003 target.com

### Strategy 7: IP Protocol Scan
sudo nmap -sO target.com

---

## Advanced Firewall Evasion Techniques #evasion

| Technique | Command | Purpose |
|-----------|---------|---------|
| Fragmentation | -f or --mtu 24 | Split packets to evade filters |
| Decoy IPs | -D RND:10 | Hide real source IP |
| Spoof source port | --source-port 53 | Make traffic look like DNS |
| Timing | -T0 or -T1 | Slow down to avoid detection |
| No ping | -Pn | Assume host is alive |
| MAC spoofing | --spoof-mac 00:11:22:33:44:55 | Spoof MAC address |
| Custom TTL | --ttl 128 | Set custom TTL value |
| Bad checksum | --badsum | Send bad checksums (may crash old systems) |

---

## Version Detection Intensity Levels #version-detection

| Level | Flag | Description |
|-------|------|-------------|
| 0-2 | --version-light | Light probe set |
| 3-5 | (default) | Balanced probing |
| 6-7 | --version-intensity 7 | More probes |
| 8-9 | --version-all | All available probes |

Example:
sudo nmap -sV --version-intensity 9 target.com

---

## Alternative Tools #alternatives

| Tool | Best For | Command |
|------|----------|---------|
| [[masscan]] | Internet-scale scanning | masscan -p0-65535 target.com --rate=10000 |
| [[rustscan]] | Ultra-fast port discovery | rustscan -a target.com -- -sV |
| [[naabu]] | Fast port scanner | naabu -host target.com |
| [[unicornscan]] | Asynchronous scanning | unicornscan target.com |
| [[zmap]] | Single port, large networks | zmap -p 443 target-network/24 |

---

## Practical Examples #examples

### Example 1: HTB Machine Initial Enumeration
sudo nmap -sC -sV -oA htb-initial 10.10.10.10

### Example 2: Firewall Evasion Scan
sudo nmap -sS -Pn -n -f -D RND:5 --source-port 53 -T2 --top-ports 1000 target.com

### Example 3: Full Network Scan with Version Detection
sudo nmap -sS -sV -O -p- 192.168.1.0/24 --exclude 192.168.1.100 -oA full-network

### Example 4: SMB Vulnerability Focus
sudo nmap -p445 --script smb-vuln* --script-args=unsafe=1 target.com

### Example 5: Web Server Deep Scan
sudo nmap -p80,443 -sV --script http-* --script-args http-enum.fingerprintfile=/usr/share/nmap/nselib/data/http-fingerprints.lst target.com

---

## Packet Trace Analysis Cheatsheet #packet-analysis

### SYN Packet (Sent)
SENT (0.0429s) TCP 10.10.14.2:63090 > 10.129.2.28:21 S ttl=56 id=57322 iplen=44 seq=1699105818 win=1024 <mss 1460>

| Field | Meaning |
|-------|---------|
| 10.10.14.2:63090 | Source IP and port |
| 10.129.2.28:21 | Destination IP and port |
| S | SYN flag |
| ttl=56 | Time to live |
| seq=1699105818 | Sequence number |
| win=1024 | Window size |
| mss 1460 | Maximum segment size |

### Response Packet (Received)
RCVD (0.0573s) TCP 10.129.2.28:21 > 10.10.14.2:63090 RA ttl=64 id=0 iplen=40 seq=0 win=0

| Field | Meaning |
|-------|---------|
| RA | RST + ACK flags (closed port) |
| ttl=64 | Response TTL (can indicate OS) |
| seq=0 | Sequence number reset |

---

## Key Takeaways #keypoints

- Master the different scan types - each serves a specific purpose
- SYN scan (-sS) is fastest and stealthiest for TCP
- Connect scan (-sT) is for non-root users but easily logged
- NULL, FIN, Xmas scans can bypass some firewalls but don't work on Windows
- UDP scanning is slow - use targeted port lists
- Always use --packet-trace to understand what's happening
- Combine -sV with different intensity levels based on time constraints
- Save all scans (-oA) for documentation and comparison
- Firewall evasion takes practice - start with -f and --source-port
- The official documentation is your friend: https://nmap.org/book/man-port-scanning-techniques.html
