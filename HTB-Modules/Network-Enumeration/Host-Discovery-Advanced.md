---
tags: [module, nmap, host-discovery, advanced, practical]
module: "Host Discovery with Nmap"
level: advanced
---

# Host Discovery - Advanced Techniques #nmap #discovery #advanced

## The Most Effective Host Discovery Probes #research

Based on extensive research testing thousands of Internet hosts, here are the most effective single probes ranked by success rate:

| Probe | Success Rate | Description |
|-------|--------------|-------------|
| -PE | 62.47% | ICMP Echo Request |
| -PS443 | 44.17% | TCP SYN to port 443 |
| -PA80 | 43.28% | TCP ACK to port 80 |
| -PA443 | 43.01% | TCP ACK to port 443 |
| -PS80 | 42.47% | TCP SYN to port 80 |
| -PP | 36.66% | ICMP Timestamp Request |
| -PM | 4.21% | ICMP Address Mask Request |

**Key insight:** The best single probe by far is -PE (ICMP echo request).

---

## Optimal Probe Combinations #strategies

Using multiple probes together finds more hosts because different probes catch different types of systems. Here are the mathematically optimal combinations:

| Probes | Success Rate | Probe Combination |
|--------|--------------|-------------------|
| 1 probe | 62.47% | -PE |
| 2 probes | 77.61% | -PE -PA80 |
| 3 probes | 83.83% | -PE -PA80 -PS443 |
| 4 probes | 88.64% | -PE -PA80 -PS443 -PP |
| 5 probes | 91.12% | -PE -PA80 -PS443 -PP -PU40125 --source-port 53 |
| 6 probes | 92.42% | -PE -PS80 -PS443 -PP -PU40125 -PA3389 --source-port 53 |
| 7 probes | 93.10% | -PE -PS80 -PS443 -PP -PU40125 -PS3389 -PA21 --source-port 53 |
| 8 probes | 93.69% | -PE -PS80 -PS443 -PP -PU40125 -PS3389 -PA21 -PU161 --source-port 53 |

**Note:** Nmap's default four-probe combination was selected as a compromise between comprehensiveness and speed.

---

## TCP Probe Port Selection #tcp-ports

The most valuable TCP ports for discovery (ordered by accessibility):

| Port | Service | Why It's Valuable |
|------|---------|-------------------|
| 80 | HTTP | Web servers are everywhere |
| 443 | HTTPS | SSL web servers are common |
| 113 | auth (identd) | Often left unfiltered to avoid server timeouts |
| 21 | FTP | File transfer protocol |
| 23 | Telnet | Still used on many devices |
| 25 | SMTP | Mail servers need to be reachable |
| 53 | Domain | DNS servers are widespread |
| 22 | SSH | Remote administration standard |
| 110 | POP3 | Email retrieval |
| 3389 | MS Terminal Services | Windows RDP |
| 1723 | PPTP | VPN implementations |
| 8080 | HTTP proxy | Alternate web port |

**Pro Tip:** In addition to popular ports, choose at least one high-numbered port (e.g., 40000, 10042). Many poorly configured firewalls only block privileged ports (below 1024).

**Port Diversity Strategy:** Choose ports from different services. HTTP (80) and HTTPS (443) are related - if a machine has HTTPS, it probably also has HTTP. Better to choose HTTP and SSH (22) for broader coverage.

---

## UDP Probe Port Selection #udp-ports

For UDP probes (-PU), the most effective strategy is:

- Port 53 (DNS) - Often allowed through firewalls
- A randomly selected high-numbered port (e.g., 37452) - Catches hosts where DNS is blocked

**Important:** For UDP, we want unfiltered ports (closed) rather than open ports, because open UDP ports often don't respond to probes.

---

## ICMP Probe Selection #icmp

| Probe | Type | When to Use |
|-------|------|-------------|
| -PE | Echo Request | Standard ping - most effective |
| -PP | Timestamp Request | When admins block echo but forget timestamp |
| -PM | Address Mask Request | Rare but can catch some hosts |

---

## Designing Your Own Host Discovery Strategy #custom

### For Internal Networks
The default Nmap ping scan usually works well:
sudo nmap -sn target

### For Casual Scanning
Default is fine - missing an occasional host isn't critical.

### For Thorough Security Audits

Use a comprehensive probe set:
sudo nmap -sn -PE -PP -PS21,22,23,25,80,113,443,31339 -PA80,113,443,10042 --source-port 53 target

### Real-World Performance Comparison

Scanning 50,000 random IP addresses:

| Scan Type | Time | Hosts Found | Notes |
|-----------|------|-------------|-------|
| Default (4 probes) | 42 minutes | 3,927 hosts | Baseline |
| Comprehensive (14 probes) | 147 minutes | 4,712 hosts | 785 (20%) more hosts |

**Trade-off:** 3.5x longer time for 20% more hosts. For security audits, this extra time is often well spent.

**Warning:** More probes increases chance of false positives (firewalls that forge responses).

---

## Practical Workflow #workflow

### Phase 1: Quick Initial Discovery
sudo nmap -sn 10.129.2.0/24 -oA quick-discovery

### Phase 2: Comprehensive Ping Scan (if needed)
sudo nmap -sn -PE -PP -PS21,22,23,25,80,113,443 -PA80,443,3389 --source-port 53 10.129.2.0/24 -oA deep-discovery

### Phase 3: Full Port Scans in Background
sudo nmap -Pn -p- -sS -T4 target -oA full-portscan &

### Phase 4: Compare Results
When the full scan finishes, compare with quick scan results and investigate any new hosts or ports.

---

## Nmap Options Reference #cheatsheet

| Option | Description |
|--------|-------------|
| -sn | Ping scan only (no port scan) |
| -PE | ICMP Echo Request |
| -PP | ICMP Timestamp Request |
| -PM | ICMP Address Mask Request |
| -PS[ports] | TCP SYN probes to specified ports |
| -PA[ports] | TCP ACK probes to specified ports |
| -PU[ports] | UDP probes to specified ports |
| -PO[protocols] | IP protocol ping |
| --source-port 53 | Spoof source port 53 (DNS) |
| --packet-trace | Show all packets sent/received |
| --reason | Show reason for host state |
| --disable-arp-ping | Don't use ARP on local network |

---

## Alternative Tools #alternatives

| Tool | Best For | Command |
|------|----------|---------|
| [[fping]] | Fast ping sweeps | fping -a -g 192.168.1.0/24 |
| [[masscan]] | Internet-scale discovery | masscan -p80 0.0.0.0/0 |
| [[netdiscover]] | ARP discovery | sudo netdiscover -r 192.168.1.0/24 |
| [[arp-scan]] | ARP scanning | sudo arp-scan --localnet |

---

## Key Takeaways #keypoints

- -PE (ICMP Echo) is the single most effective host discovery probe (62%)
- Using multiple probes in combination finds significantly more hosts (up to 93% with 8 probes)
- Nmap's default uses 4 probes as a speed/completeness trade-off
- TCP probes to common ports (80, 443, 22) are very effective because servers must respond
- Include at least one high-numbered TCP port to bypass simple firewalls
- For UDP probes, use port 53 and a random high port
- Document your methodology and save all scan outputs
- More thorough scans take longer but find more hosts
- Always verify suspicious results manually
- The official Nmap documentation at https://nmap.org/book/host-discovery-strategies.html contains extensive research and strategies
