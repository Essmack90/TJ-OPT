---
tags:
  - tool/nmap
  - cheatsheet
  - scanning
  - reference
  - "#Nmap-Cheatsheet"
---
# Nmap Cheatsheet - Complete Command Reference

## Target Selection

| Option | Description | Example |
|--------|-------------|---------|
| `10.10.10.0/24` | Target network range | `nmap 10.10.10.0/24` |
| `10.10.10.1-100` | Range of IPs | `nmap 10.10.10.1-100` |
| `10.10.10.1,10.10.10.5` | Specific IPs | `nmap 10.10.10.1,10.10.10.5` |
| `-iL targets.txt` | Read targets from file | `nmap -iL targets.txt` |
| `-iR 100` | Random targets | `nmap -iR 100` |
| `--exclude 10.10.10.1` | Exclude host | `nmap 10.10.10.0/24 --exclude 10.10.10.1` |

---

## Host Discovery

| Option | Description | Example |
|--------|-------------|---------|
| `-sn` | Disable port scanning (ping only) | `nmap -sn 10.10.10.0/24` |
| `-Pn` | Disable ICMP Echo Requests (assume host alive) | `nmap -Pn 10.10.10.1` |
| `-PE` | ICMP Echo Request ping | `nmap -PE 10.10.10.1` |
| `-PP` | ICMP Timestamp Request | `nmap -PP 10.10.10.1` |
| `-PM` | ICMP Address Mask Request | `nmap -PM 10.10.10.1` |
| `-PS22,80` | TCP SYN ping to specific ports | `nmap -PS22,80 10.10.10.1` |
| `-PA80,443` | TCP ACK ping to specific ports | `nmap -PA80,443 10.10.10.1` |
| `-PU53` | UDP ping to specific port | `nmap -PU53 10.10.10.1` |
| `-PO1,2,4` | IP Protocol ping | `nmap -PO1,2,4 10.10.10.1` |
| `-n` | Disable DNS resolution | `nmap -n 10.10.10.1` |
| `-R` | Always do DNS resolution | `nmap -R 10.10.10.1` |
| `--dns-server 8.8.8.8` | Use specified DNS server | `nmap --dns-server 8.8.8.8 10.10.10.1` |

---

## Port Selection

| Option | Description | Example |
|--------|-------------|---------|
| `-p-` | Scan all ports (1-65535) | `nmap -p- 10.10.10.1` |
| `-p22-110` | Scan range of ports | `nmap -p22-110 10.10.10.1` |
| `-p22,25,80` | Scan specific ports | `nmap -p22,25,80 10.10.10.1` |
| `-p U:53,T:22-25,80` | Mix UDP and TCP | `nmap -p U:53,T:22-25,80 10.10.10.1` |
| `--top-ports 10` | Scan top 10 most frequent ports | `nmap --top-ports 10 10.10.10.1` |
| `-F` | Fast scan (top 100 ports) | `nmap -F 10.10.10.1` |
| `-r` | Scan ports consecutively (no random) | `nmap -r -p 1-1000 10.10.10.1` |

---

## Scan Techniques

| Option | Description | Example |
|--------|-------------|---------|
| `-sS` | TCP SYN scan (stealth, default) | `sudo nmap -sS 10.10.10.1` |
| `-sT` | TCP Connect scan (no root) | `nmap -sT 10.10.10.1` |
| `-sA` | TCP ACK scan (firewall mapping) | `sudo nmap -sA 10.10.10.1` |
| `-sW` | TCP Window scan | `sudo nmap -sW 10.10.10.1` |
| `-sM` | TCP Maimon scan | `sudo nmap -sM 10.10.10.1` |
| `-sU` | UDP scan | `sudo nmap -sU 10.10.10.1` |
| `-sN` | TCP Null scan | `sudo nmap -sN 10.10.10.1` |
| `-sF` | TCP FIN scan | `sudo nmap -sF 10.10.10.1` |
| `-sX` | TCP Xmas scan | `sudo nmap -sX 10.10.10.1` |
| `-sO` | IP protocol scan | `sudo nmap -sO 10.10.10.1` |
| `-b` | FTP bounce scan | `nmap -b username:pass@ftp-server 10.10.10.1` |

---

## Service and Version Detection

| Option | Description | Example |
|--------|-------------|---------|
| `-sV` | Service version detection | `nmap -sV 10.10.10.1` |
| `--version-intensity 0-9` | Set version scan intensity | `nmap -sV --version-intensity 5 10.10.10.1` |
| `--version-light` | Light version scan (intensity 2) | `nmap -sV --version-light 10.10.10.1` |
| `--version-all` | Try all probes (intensity 9) | `nmap -sV --version-all 10.10.10.1` |
| `--version-trace` | Show version scan details | `nmap -sV --version-trace 10.10.10.1` |

---

## OS Detection

| Option | Description | Example |
|--------|-------------|---------|
| `-O` | OS detection | `sudo nmap -O 10.10.10.1` |
| `--osscan-guess` | Guess OS aggressively | `sudo nmap -O --osscan-guess 10.10.10.1` |
| `--osscan-limit` | Limit to promising targets | `sudo nmap -O --osscan-limit 10.10.10.1` |
| `--max-os-tries 1` | Set max OS detection tries | `sudo nmap -O --max-os-tries 1 10.10.10.1` |

---

## NSE Scripts

| Option | Description | Example |
|--------|-------------|---------|
| `-sC` | Default script scan | `nmap -sC 10.10.10.1` |
| `--script http-enum` | Run specific script | `nmap --script http-enum 10.10.10.1` |
| `--script vuln` | Run script category | `nmap --script vuln 10.10.10.1` |
| `--script "http-*"` | Run all HTTP scripts | `nmap --script "http-*" 10.10.10.1` |
| `--script-args userdb=users.txt` | Pass arguments to script | `nmap --script http-brute --script-args userdb=users.txt 10.10.10.1` |
| `--script-trace` | Show script execution details | `nmap --script http-enum --script-trace 10.10.10.1` |
| `--script-updatedb` | Update script database | `sudo nmap --script-updatedb` |
| `--script-help http-enum` | Show script help | `nmap --script-help http-enum` |

### NSE Categories

| Category | Description |
|----------|-------------|
| `auth` | Authentication credential testing |
| `broadcast` | Host discovery via broadcasting |
| `brute` | Brute-force login attempts |
| `default` | Default scripts (`-sC`) |
| `discovery` | Service and host discovery |
| `dos` | Denial of Service testing |
| `exploit` | Exploit known vulnerabilities |
| `external` | Use external services |
| `fuzzer` | Send malformed data |
| `intrusive` | May affect target |
| `malware` | Check for infections |
| `safe` | Won't harm target |
| `version` | Extended version detection |
| `vuln` | Vulnerability detection |

---

## Firewall/IDS Evasion

| Option | Description | Example |
|--------|-------------|---------|
| `-f` | Fragment packets | `sudo nmap -f 10.10.10.1` |
| `--mtu 24` | Set custom MTU (multiple of 8) | `sudo nmap --mtu 24 10.10.10.1` |
| `-D RND:5` | Use 5 random decoys | `sudo nmap -D RND:5 10.10.10.1` |
| `-D decoy1,decoy2,ME` | Specify decoys (ME = your IP) | `sudo nmap -D 192.168.1.10,10.10.10.1,ME 10.10.10.1` |
| `-S 10.10.10.200` | Spoof source IP | `sudo nmap -S 10.10.10.200 10.10.10.1` |
| `-e eth0` | Use specified interface | `sudo nmap -e eth0 10.10.10.1` |
| `-g 53` | Spoof source port | `sudo nmap -g 53 10.10.10.1` |
| `--source-port 53` | Spoof source port (alt syntax) | `sudo nmap --source-port 53 10.10.10.1` |
| `--data-length 30` | Append random data | `sudo nmap --data-length 30 10.10.10.1` |
| `--ttl 128` | Set TTL value | `sudo nmap --ttl 128 10.10.10.1` |
| `--badsum` | Send bad checksum | `sudo nmap --badsum 10.10.10.1` |
| `--spoof-mac 00:11:22:33:44:55` | Spoof MAC address | `sudo nmap --spoof-mac 00:11:22:33:44:55 10.10.10.1` |

---

## Performance and Timing

| Option | Description | Example |
|--------|-------------|---------|
| `-T0` to `-T5` | Timing templates (paranoid to insane) | `nmap -T4 10.10.10.1` |
| `--min-hostgroup 64` | Min parallel host group size | `nmap --min-hostgroup 64 10.10.10.0/24` |
| `--max-hostgroup 256` | Max parallel host group size | `nmap --max-hostgroup 256 10.10.10.0/24` |
| `--min-parallelism 10` | Min probes outstanding | `nmap --min-parallelism 10 10.10.10.1` |
| `--max-parallelism 100` | Max probes outstanding | `nmap --max-parallelism 100 10.10.10.1` |
| `--min-rtt-timeout 10ms` | Min RTT timeout | `nmap --min-rtt-timeout 10ms 10.10.10.1` |
| `--max-rtt-timeout 100ms` | Max RTT timeout | `nmap --max-rtt-timeout 100ms 10.10.10.1` |
| `--initial-rtt-timeout 50ms` | Initial RTT timeout | `nmap --initial-rtt-timeout 50ms 10.10.10.1` |
| `--max-retries 2` | Max retransmissions | `nmap --max-retries 2 10.10.10.1` |
| `--host-timeout 5m` | Max time per host | `nmap --host-timeout 5m 10.10.10.1` |
| `--script-timeout 30s` | Max script execution time | `nmap --script-timeout 30s 10.10.10.1` |
| `--scan-delay 1s` | Delay between probes | `nmap --scan-delay 1s 10.10.10.1` |
| `--max-scan-delay 10s` | Max allowed delay | `nmap --max-scan-delay 10s 10.10.10.1` |
| `--min-rate 300` | Min packet sending rate | `nmap --min-rate 300 10.10.10.1` |
| `--max-rate 100` | Max packet sending rate | `nmap --max-rate 100 10.10.10.1` |

### Timing Templates

| Template | Name | Speed | Use Case |
|----------|------|-------|----------|
| `-T0` | Paranoid | Extremely slow | IDS evasion |
| `-T1` | Sneaky | Very slow | IDS evasion |
| `-T2` | Polite | Slow | Conservative scanning |
| `-T3` | Normal | Default | General use |
| `-T4` | Aggressive | Fast | Reliable networks |
| `-T5` | Insane | Very fast | May miss ports |

---

## Output Options

| Option | Description | Example |
|--------|-------------|---------|
| `-oA scan` | Output in all formats | `nmap -oA scan 10.10.10.1` |
| `-oN scan.nmap` | Normal output | `nmap -oN scan.nmap 10.10.10.1` |
| `-oG scan.gnmap` | Grepable output | `nmap -oG scan.gnmap 10.10.10.1` |
| `-oX scan.xml` | XML output | `nmap -oX scan.xml 10.10.10.1` |
| `-oS scan.l33t` | Script kiddie output | `nmap -oS scan.l33t 10.10.10.1` |
| `-v` | Verbose output | `nmap -v 10.10.10.1` |
| `-vv` | Very verbose | `nmap -vv 10.10.10.1` |
| `-d` | Debugging output | `nmap -d 10.10.10.1` |
| `--reason` | Show reason for port state | `nmap --reason 10.10.10.1` |
| `--stats-every 5s` | Show status periodically | `nmap --stats-every 5s 10.10.10.1` |
| `--packet-trace` | Show all packets | `sudo nmap --packet-trace 10.10.10.1` |
| `--open` | Show only open ports | `nmap --open 10.10.10.1` |
| `--iflist` | List interfaces and routes | `nmap --iflist` |

### Convert XML to HTML

```bash
xsltproc scan.xml -o scan.html
```

---

## Time Format Examples

| Format | Meaning | Example |
|--------|---------|---------|
| `ms` | Milliseconds | `500ms` |
| `s` | Seconds | `30s` |
| `m` | Minutes | `5m` |
| `h` | Hours | `2h` |

---

## Quick Reference by Use Case

### Initial Recon (Top 100 ports)
```bash
nmap -sn 10.10.10.0/24
nmap -sS -T4 -F 10.10.10.1 -oA quick
```

### Full Port Scan
```bash
nmap -p- -sS -T4 10.10.10.1 -oA full
```

### Service Detection
```bash
nmap -sV -p 22,80,443 10.10.10.1 -oA versions
```

### Vulnerability Assessment
```bash
nmap --script vuln 10.10.10.1 -oA vulns
```

### Stealthy Scan (Evasion)
```bash
nmap -sS -T1 -f --source-port 53 -D RND:3 10.10.10.1 -oA stealth
```

### UDP Scan
```bash
nmap -sU --top-ports 20 10.10.10.1 -oA udp
```

### OS Detection
```bash
sudo nmap -O --osscan-guess 10.10.10.1 -oA os
```

### Complete Assessment (Aggressive)
```bash
nmap -A -T4 10.10.10.1 -oA complete
```

---

## Common One-Liners

```bash
# Quick check if host is alive
nmap -sn 192.168.1.1

# Find live hosts on network
nmap -sn 192.168.1.0/24

# Quick port scan (top 100)
nmap -F 192.168.1.1

# Service version detection
nmap -sV 192.168.1.1

# OS detection
sudo nmap -O 192.168.1.1

# Full scan with all features
sudo nmap -sC -sV -O -p- 192.168.1.1

# Web server focused scan
nmap -p 80,443 --script http-* 192.168.1.1

# SMB vulnerability check
nmap -p 445 --script smb-vuln-* 192.168.1.1

# Quick UDP scan
sudo nmap -sU --top-ports 20 192.168.1.1

# Evade firewall with source port 53
sudo nmap -sS --source-port 53 192.168.1.1
```

---

## Nmap Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Normal exit - all hosts scanned |
| `1` | Warning - something didn't work right |
| `2` | Error - Nmap couldn't start |
| `3-4` | Reserved |
| `5` | Received termination signal |

---

## Quick Nmap Workflow

```bash
# 1. Host Discovery
nmap -sn 192.168.1.0/24 -oA discovery

# 2. Port Scan live hosts
nmap -sS -T4 -p- -iL discovery.gnmap -oA ports

# 3. Service Detection
nmap -sV -p $(grep open ports.gnmap | cut -d' ' -f2 | cut -d'/' -f1 | tr '\n' ',') -iL discovery.gnmap -oA services

# 4. Vulnerability Scan
nmap --script vuln -p $(grep open services.gnmap | cut -d' ' -f2 | cut -d'/' -f1 | tr '\n' ',') -iL discovery.gnmap -oA vulns
```

---

## Port State Reference

| State | Description |
|-------|-------------|
| `open` | Service is actively accepting connections |
| `closed` | Port is accessible but no service listening |
| `filtered` | Firewall/filter preventing probe from reaching port |
| `unfiltered` | Port accessible but state unknown (ACK scan only) |
| `open\|filtered` | Unable to determine if open or filtered |
| `closed\|filtered` | Unable to determine if closed or filtered |
