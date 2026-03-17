---
tags: [module, nmap, evasion, firewall, ids, ips, beginner]
module: "Firewall and IDS/IPS Evasion"
level: beginner
---

# Firewall and IDS/IPS Evasion - Beginner's Guide #evasion #firewall #ids #beginner

## What Are We Evading? #core

### Firewalls #firewall

A firewall is a security system that monitors network traffic and decides what to allow or block based on rules.

Think of it like a bouncer at a club:
- **Dropped packets:** The bouncer ignores you completely (no response)
- **Rejected packets:** The bouncer says "no" and you get a response (RST flag for TCP, error messages for ICMP)

### IDS/IPS #ids #ips

**IDS (Intrusion Detection System):** Watches network traffic and reports suspicious activity. Like a security camera - it sees everything but doesn't stop you.

**IPS (Intrusion Prevention System):** Watches AND takes action to block attacks. Like a security guard who tackles you if you try something suspicious.

IPS systems can:
- Block your IP address
- Reset your connections
- Alert the administrator

---

## Why Evasion Matters #importance

If we scan too aggressively:
1. IPS may block our IP address
2. Administrators get alerted
3. We lose access to the target
4. Our ISP might even get notified

In professional pentests, we need to be **quiet and stealthy** while still getting the information we need.

---

## Basic Evasion Techniques #techniques

### 1. ACK Scan (-sA) vs SYN Scan (-sS) #ack-scan

Firewalls often block incoming connection attempts (SYN packets) but allow ACK packets because they look like responses to established connections.

**SYN Scan (-sS):**
sudo nmap 10.129.2.28 -p 21,22,25 -sS

Port 22: SYN-ACK response (open)
Port 21: ICMP "port unreachable" (filtered)
Port 25: No response (filtered)

**ACK Scan (-sA):**
sudo nmap 10.129.2.28 -p 21,22,25 -sA

Port 22: RST response (unfiltered - port is accessible)
Port 21: ICMP error (filtered)
Port 25: No response (filtered)

**Key Insight:** ACK scan tells us which ports are accessible through the firewall, even if they're closed. This helps map firewall rules.

### 2. Decoys (-D) #decoys

Nmap can send packets from fake IP addresses to hide our real IP.

sudo nmap 10.129.2.28 -p 80 -sS -D RND:5

This sends packets appearing to come from 5 random IP addresses, plus our real IP randomly placed among them.

**What the target sees:** 6 different IPs scanning simultaneously. The administrator doesn't know which one is real.

**Important:** Decoys must be alive, or the target might get overwhelmed and block everything.

### 3. Spoofing Source IP (-S) #spoofing

If we know an IP that's trusted (like a management network), we can make our scans appear to come from there:

sudo nmap 10.129.2.28 -p 445 -O -S 10.129.2.200 -e tun0

This tells Nmap to:
- Use source IP 10.129.2.200
- Send packets through interface tun0
- Scan port 445 with OS detection

**When this works:** If the firewall trusts that IP range, our scan gets through.

### 4. DNS Proxying #dns

DNS (port 53) is often allowed through firewalls. We can abuse this:

sudo nmap 10.129.2.28 -p 50000 -sS --source-port 53

This makes our scan appear to come from DNS port 53. Many firewalls trust DNS traffic.

**Result:** Port 50000 goes from filtered to open!

### 5. Fragmentation (-f) #fragmentation

Split packets into smaller fragments to evade simple filters:

sudo nmap -f target.com

Each fragment is too small to contain complete header information, potentially bypassing filters.

---

## Real Example: DNS Port Trick #example

**Before (normal scan):**
sudo nmap 10.129.2.28 -p50000 -sS

PORT      STATE    SERVICE
50000/tcp filtered ibm-db2

**After (using source port 53):**
sudo nmap 10.129.2.28 -p50000 -sS --source-port 53

PORT      STATE SERVICE
50000/tcp open  ibm-db2

The firewall was allowing DNS traffic (port 53) through, and we exploited that!

We can even connect manually:
ncat -nv --source-port 53 10.129.2.28 50000
220 ProFTPd

---

## Detecting IDS/IPS #detection

It's hard to know if IDS/IPS is present, but here's one method:

1. Scan from a VPS
2. If the IP gets blocked, you know there's monitoring
3. Switch to a different VPS and be quieter

**Professional tip:** Always have multiple VPS with different IP addresses for pentesting.

---

## When to Use Each Technique #when-to-use

| Technique | Best For |
|-----------|----------|
| ACK scan | Mapping firewall rules |
| Decoys | Hiding your real IP |
| Source IP spoofing | Pretending to be trusted |
| DNS source port | Bypassing DNS filters |
| Fragmentation | Evading simple packet filters |
| Slow timing (-T1, -T2) | Avoiding detection thresholds |

---

## Key Takeaways #keypoints

- Firewalls can drop (no response) or reject (error response) packets
- ACK scans often bypass firewall rules because they look like responses
- Decoys hide your real IP among fake ones
- Spoofing trusted IPs can get you through filters
- DNS port 53 is frequently trusted and can be abused
- Fragmentation splits packets to evade simple filters
- IDS watches, IPS blocks - know the difference
- If your IP gets blocked, you've confirmed monitoring exists
- Always have backup VPS with different IPs
- The quieter you are, the longer you'll have access
- More evasion techniques at https://nmap.org/book/man-bypass-firewalls-ids.html
