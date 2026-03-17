---
tags: [module, nmap, evasion, firewall, ids, ips, advanced, practical]
module: "Firewall and IDS/IPS Evasion"
level: advanced
---

# Firewall and IDS/IPS Evasion - Complete Reference #evasion #firewall #ids #advanced

## Understanding Firewall Responses #firewall

When a firewall encounters a packet, it can take two actions:

| Action | Behavior | TCP Response | ICMP Response |
|--------|----------|--------------|---------------|
| Drop | Packet ignored, no response | None | None |
| Reject | Explicit refusal | RST flag | Error code |

### ICMP Error Codes for Rejected Packets

| Code | Meaning |
|------|---------|
| 0 | Net Unreachable |
| 1 | Net Prohibited |
| 2 | Host Unreachable |
| 3 | Host Prohibited |
| 4 | Port Unreachable |
| 5 | Proto Unreachable |

---

## ACK Scan Deep Dive #ack-scan

### Why ACK Works

Firewalls often block incoming SYN packets (connection attempts) but allow ACK packets (responses to established connections). The firewall can't easily tell if an ACK packet is part of a legitimate connection or not.

### Technical Explanation

- ACK scan sends packets with ONLY the ACK flag set
- RFC 793 requires hosts to respond to ACK packets on ANY port with RST
- This happens regardless of whether the port is open or closed
- Firewalls that block SYNs may still pass ACKs

### Interpreting Results

| Response | Meaning |
|----------|---------|
| RST received | Port is accessible (unfiltered) |
| ICMP error | Port is filtered (firewall rejecting) |
| No response | Port is filtered (firewall dropping) |

### Mapping Firewall Rules

sudo nmap -sA -p 1-1000 target.com

Ports that respond with RST are accessible through the firewall. Ports that don't respond are blocked. This maps the firewall's filtering rules without revealing open/closed status.

---

## Decoy Strategies #decoys

### Basic Decoy Syntax

| Pattern | Description |
|---------|-------------|
| -D RND:5 | Generate 5 random IPs |
| -D decoy1,decoy2,ME,decoy3 | Specify exact decoys, ME = your real IP |
| -D decoy1,decoy2,decoy3 | Your real IP not included (advanced) |

### Example with Specific Decoys

sudo nmap -D 192.168.1.10,192.168.1.20,ME,10.10.10.50 target.com

### Decoy Requirements

| Requirement | Reason |
|-------------|--------|
| Decoys must be alive | Dead decoys cause SYN-flooding protection |
| Decoys should be plausible | Random IPs from different continents look suspicious |
| Consider network topology | Decoys on same subnet as target work best |

### Advanced Decoy Strategy

1. Use real IPs from the same geographic region
2. Mix in IPs from known partner networks
3. Use IPs that would legitimately connect to the target
4. Rotate decoys across multiple scans

---

## Source IP Spoofing #spoofing

### When It Works

- Firewall trusts specific IP ranges (management networks, partners)
- Source-based filtering rather than stateful inspection
- Internal network segments

### Full Syntax

sudo nmap target.com -S spoofed_ip -e interface

### Example: Pretending to Be Management

sudo nmap 10.129.2.28 -p 445 -O -S 10.129.2.200 -e tun0

**Result:** Port 445 now appears open instead of filtered.

### Limitations

| Limitation | Explanation |
|------------|-------------|
| Responses go to spoofed IP | You won't see replies unless you can intercept them |
| Requires route to target | Spoofed IP must be routable |
| Won't work for full TCP | Can't complete handshake |

---

## DNS Source Port Technique #dns

### Why Port 53 Works

DNS (port 53) is often trusted by firewalls because it's essential for name resolution. Many administrators forget to filter DNS traffic as strictly as other ports.

### Step 1: Identify the Vulnerability

sudo nmap target.com -p50000 -sS

PORT      STATE    SERVICE
50000/tcp filtered ibm-db2

### Step 2: Test with Source Port 53

sudo nmap target.com -p50000 -sS --source-port 53

PORT      STATE SERVICE
50000/tcp open  ibm-db2

### Step 3: Manual Verification

ncat -nv --source-port 53 target.com 50000

220 ProFTPd

### Beyond Scanning

Once you know port 53 works, you can:
- Use it for all scans (--source-port 53)
- Tunnel other traffic through it
- Access services that were previously blocked

---

## Fragmentation Techniques #fragmentation

### Basic Fragmentation

sudo nmap -f target.com

Splits packets into 8-byte fragments. Each fragment is too small to contain complete TCP headers, potentially evading simple filters.

### MTU Customization

sudo nmap --mtu 24 target.com

Sets custom MTU size (must be multiple of 8). Smaller fragments are harder to detect.

### Why Fragmentation Works

Many simple firewalls only check the first fragment for header information. Later fragments may pass through unchecked.

### Limitations

| Limitation | Explanation |
|------------|-------------|
| Modern IDS can reassemble | Stateful inspection reassembles fragments |
| Some systems drop fragments | Some stacks don't handle fragmentation well |
| Can increase scan time | More packets = longer scan |

---

## Timing for Evasion #timing

### Why Timing Matters

IDS systems look for patterns. Regular, fast scans are easily detected. Varying timing breaks these patterns.

### Strategic Timing Options

| Option | Effect |
|--------|--------|
| -T0 (Paranoid) | 5 minutes between probes, extremely stealthy |
| -T1 (Sneaky) | 15 seconds between probes |
| -T2 (Polite) | 0.4 seconds between probes, less bandwidth |
| --scan-delay 1s | Custom delay between probes |
| --max-retries 0 | Don't retransmit (less traffic) |

### Example: Extremely Stealthy Scan

sudo nmap -T1 --scan-delay 1s --max-retries 0 -p 1-1000 target.com

This scan could take hours but is very hard to detect.

---

## Detecting IDS/IPS #detection-strategy

### Methodology

1. **Phase 1:** Scan from VPS1 with aggressive options
2. **Phase 2:** Monitor for connectivity loss
3. **Phase 3:** If blocked, switch to VPS2 with stealthy options
4. **Phase 4:** Continue with quieter techniques

### Indicators of IDS/IPS

| Indicator | Likely Cause |
|-----------|--------------|
| IP blocked after scan | IPS triggered |
| Connections reset mid-scan | IPS actively interfering |
| No response after certain threshold | Rate limiting (possible IPS) |
| Different results from different VPS | Geographic filtering |

### Professional Recommendation

Always maintain at least 3 VPS in different geographic regions for pentesting. When one gets blocked, you have backups.

---

## Complete Evasion Workflow #workflow

### Phase 1: Reconnaissance (Stealthy)

sudo nmap -T2 --source-port 53 -D RND:5 -sS -p 1-1000 target.com

### Phase 2: Firewall Mapping

sudo nmap -sA -p 1-1000 target.com

### Phase 3: Targeted Scanning

sudo nmap -sS --source-port 53 -p $(grep open phase1.gnmap | cut -d' ' -f2) target.com

### Phase 4: Version Detection (if safe)

sudo nmap -sV --source-port 53 -p $(grep open phase3.gnmap | cut -d' ' -f2) target.com

### Phase 5: Manual Verification

for port in $(grep open phase4.gnmap | cut -d' ' -f2 | cut -d'/' -f1); do
    ncat -nv --source-port 53 target.com $port
done

---

## Evasion Technique Comparison #comparison

| Technique | Stealth Level | Complexity | When to Use |
|-----------|--------------|------------|-------------|
| ACK scan | Medium | Low | Initial firewall mapping |
| Decoys | High | Medium | Hiding source IP |
| Source spoofing | Very High | High | Trusted IP impersonation |
| DNS source port | High | Low | When port 53 is open |
| Fragmentation | Medium | Low | Evading simple filters |
| Slow timing | Very High | Low | Avoiding detection thresholds |
| Multiple VPS | Very High | High | Professional pentests |

---

## Real-World Scenario: Banking Network #scenario

**Target:** Financial institution with strict firewall and IPS

**Approach:**

1. Start with -T1 and --source-port 53
2. Use decoys from same geographic region
3. Map firewall with ACK scan
4. Target only essential ports
5. Manual verification through established channels
6. If blocked, switch to different VPS

**Why this works:** The IPS sees traffic from "legitimate" IPs on "legitimate" ports and doesn't trigger alerts.

---

## Key Takeaways #keypoints

- Firewalls can drop (no response) or reject (error) packets
- ACK scans map firewall rules without revealing open/closed status
- Decoys hide your real IP among fake sources
- Source port 53 (DNS) is frequently trusted and can bypass filters
- Fragmentation evades simple packet filters
- Slow timing prevents detection by IDS threshold rules
- IPS systems actively block - always have backup VPS
- Different techniques work in different situations - know them all
- Document everything - you may need to prove what you did
- The official documentation at https://nmap.org/book/man-bypass-firewalls-ids.html has extensive details
