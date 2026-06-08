---
tags: [nmap, summary, core, must-know]
---

# Nmap - What You MUST FUCKING KNOW

## The Absolute Essentials

If you learn NOTHING else from this module, learn these 10 things. Everything else is optimization and edge cases.

---

## 1. The 6 Port States - MEMORIZE THESE

| State | What It Means | How You See It |
|-------|---------------|----------------|
| open | Service is listening - doors open | SYN-ACK response |
| closed | Port accessible but no service - door locked | RST response |
| filtered | Firewall is interfering - can't tell | No response or ICMP error |
| unfiltered | Port accessible but state unknown (ACK scan only) | RST received |
| open|filtered | No response - could be open OR filtered | Timeout |
| closed|filtered | Idle scan only - can't determine | Rare |

The Critical Rule: Filtered doesn't mean dead. It means you need to try different scans.

---

## 2. The Four Scan Phases - ALWAYS Follow This Order

1. Host Discovery - Find live hosts (-sn)
2. Port Scanning - Find open ports (-sS, -sT, -sU)
3. Service Enumeration - Identify versions (-sV)
4. OS Detection - Identify OS (-O)

NEVER skip to phase 3 without doing phase 2. NEVER.

---

## 3. The Three Scan Types You MUST Master

| Scan | Command | When to Use |
|------|---------|-------------|
| SYN Scan | -sS | DEFAULT. Fast, stealthy. Run as root. |
| Connect Scan | -sT | When you don't have root. Less stealthy. |
| UDP Scan | -sU | SLOW. Target specific ports, not all. |

SYN scan is your workhorse. UDP scan is your patience tester.

---

## 4. Port Selection - Don't Be an Idiot

| Command | What It Does | When to Use |
|---------|--------------|-------------|
| -p- | ALL 65535 ports | When you have TIME. Otherwise, don't. |
| --top-ports 1000 | Most common ports (default) | Initial scans |
| -F | Top 100 ports | Quick checks |
| -p 22,80,443 | Specific ports | Targeted testing |

The mistake: Running -p- on every box wastes hours. Start small, expand if needed.

---

## 5. Version Detection - The Gold Mine

-sV tells you exactly what's running. Without it, you're blind.

Example:
nmap -p 22 -sV target.com
22/tcp open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.3

That version number is your key to finding exploits. Write it down.

Warning: -sV is noisy. On stealthy engagements, grab banners manually first:
nc -nv target.com 22

---

## 6. NSE Scripts - Your Automation Army

| Category | Command | What It Does |
|----------|---------|--------------|
| Default | -sC | Safe, common scripts |
| Vuln | --script vuln | Check for known vulnerabilities |
| Specific | --script http-enum | Run one script |

The vuln category is GOD-TIER. It checks vulnerability databases automatically.

Example:
nmap --script vuln -p 80,443 target.com

---

## 7. Output - SAVE EVERYTHING

| Command | What It Saves |
|---------|---------------|
| -oA name | All formats (normal, grepable, XML) |
| -oN name.nmap | Human-readable |
| -oG name.gnmap | Grepable (for scripting) |
| -oX name.xml | For tools and HTML reports |

ALWAYS use -oA on important scans. You WILL forget what you found. You WILL need to prove it later.

---

## 8. Timing - Fast vs Stealthy

| Template | Name | Speed | Use Case |
|----------|------|-------|----------|
| -T0 | Paranoid | SLOWEST | IDS evasion |
| -T1 | Sneaky | Very slow | Stealth |
| -T2 | Polite | Slow | Conservative |
| -T3 | Normal | Default | General use |
| -T4 | Aggressive | Fast | Internal networks |
| -T5 | Insane | FASTEST | Lab environments only |

The Rule: Start with -T4 on internal networks. Use -T1 if you're getting blocked.

---

## 9. The One-Liner You MUST Know

This command does 80% of what you need:

sudo nmap -sC -sV -oA quick-scan target.com

What it does:
- -sC : Default scripts
- -sV : Version detection
- -oA : Saves everything

Run this FIRST. Then decide what else you need.

---

## 10. The Three Most Important Evasion Techniques

| Technique | Command | Why It Works |
|-----------|---------|--------------|
| Source port 53 | --source-port 53 | DNS is often trusted |
| Decoys | -D RND:5 | Hides your real IP |
| Fragmentation | -f | Splits packets to evade filters |

If you're getting blocked, try:
sudo nmap -sS -f --source-port 53 -D RND:3 target.com

---

## The Nmap Cheat Sheet - 10 Commands You'll Actually Use

1. Quick check if host is alive
nmap -sn target.com

2. Initial scan (DO THIS FIRST)
sudo nmap -sC -sV -oA initial target.com

3. Full port scan (if needed)
sudo nmap -p- -sS -T4 -oA full target.com

4. UDP scan (specific ports only)
sudo nmap -sU --top-ports 20 -oA udp target.com

5. Vulnerability scan
sudo nmap --script vuln -oA vuln target.com

6. OS detection
sudo nmap -O target.com

7. Stealthy scan (when getting blocked)
sudo nmap -sS -f --source-port 53 -D RND:3 -T1 target.com

8. Service detection on specific ports
nmap -p 22,80,443 -sV target.com

9. Aggressive internal scan
sudo nmap -T4 -A -p- target.com

10. Convert XML to HTML report
xsltproc scan.xml -o scan.html

---

## What You MUST Remember

### 1. Port States
- Open = Target
- Closed = Move on
- Filtered = Try different scans

### 2. Scan Order
- Discovery to Ports to Services to OS
- NEVER skip steps

### 3. Version Numbers = Exploits
- Write down EVERY version
- Searchsploit is your friend

### 4. Save Everything
- -oA or it didn't happen
- You WILL need it for reports

### 5. Timing Matters
- -T4 for internal, -T1 for stealth
- Speed kills accuracy

### 6. If You're Stuck
- Try different scan types (-sS, -sT, -sA)
- Change source port (--source-port 53)
- Use decoys (-D RND:3)
- Go slower (-T1)

### 7. The Golden Rule
It's not hard to get access once you know HOW. The hard part is finding the HOW. That's enumeration.

Nmap is just a tool. Your brain does the real work.

---

## One Final Thing

If you only remember ONE command, remember this:

sudo nmap -sC -sV -oA scan target.com

Run it. Save it. Analyze it. Then decide.

Everything else is just optimization.

Now go scan some fucking boxes.
