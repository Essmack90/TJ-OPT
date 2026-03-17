---
tags: [module, nmap, evasion, firewall, ids, ips, lab, easy, beginner]
module: "Firewall and IDS/IPS Evasion - Easy Lab"
level: beginner
---

# Firewall Evasion Easy Lab - Beginner's Guide #evasion #lab #beginner

## Lab Scenario #scenario

A company has hired us to test their IT security defenses, including their IDS and IPS systems. They want us to help them improve their security.

**The Challenge:** We have a target machine protected by IDS/IPS systems. There's a status page at:

http://\<target\>/status.php

This page shows the number of alerts triggered by our activity. If we generate too many alerts, we get banned!

**Goal:** Gather information about the target as quietly as possible without triggering too many alerts.

---

## Understanding the Alert System #alerts

The status page is our friend. It tells us how we're doing in real-time:

http://10.129.2.28/status.php

Visit this page before and after each scan to see how many alerts we've triggered.

If we see the alert count jump too high, we need to be even quieter!

---

## Step 1: Initial Reconnaissance (The Quiet Way) #step1

Before we scan anything, we need to understand our target. But we have to be CAREFUL.

### Check if the Host is Alive (Minimal Traffic)

Instead of a noisy ping scan, let's try a single TCP SYN ping:

sudo nmap 10.129.2.28 -PS -n --disable-arp-ping

| Option | Purpose |
|--------|---------|
| -PS | TCP SYN ping (less noisy than ICMP) |
| -n | No DNS resolution (avoid extra traffic) |
| --disable-arp-ping | Stay on our interface |

**Check the status page after this!** How many alerts?

### If That Was Too Noisy

Try an even quieter ACK ping:

sudo nmap 10.129.2.28 -PA -n --disable-arp-ping

ACK packets often blend in with normal traffic better than SYN.

---

## Step 2: Very Gentle Port Scanning #step2

We need to find open ports, but we can't just blast a SYN scan.

### Option A: Slow TCP Connect Scan

sudo nmap 10.129.2.28 -sT -p 1-1000 -T1 --max-retries 0

| Option | Purpose |
|--------|---------|
| -sT | TCP Connect scan (completes handshake, looks normal) |
| -p 1-1000 | Scan first 1000 ports (fewer ports = less traffic) |
| -T1 | Sneaky timing (slow) |
| --max-retries 0 | Don't retransmit (one chance only) |

**Check the status page.** Did alerts spike? If yes, we need to go even slower.

### Option B: Fragment Packets

sudo nmap 10.129.2.28 -sS -p 1-1000 -f -T2 --data-length 30

| Option | Purpose |
|--------|---------|
| -f | Fragment packets into tiny pieces |
| --data-length 30 | Add random data to make packets look different |

Fragmentation can sometimes bypass simple IDS signatures.

### Option C: Use a Decoy

sudo nmap 10.129.2.28 -sS -p 1-100 -D RND:3 -T2

This makes it look like 3 different IPs are scanning. The IDS might not know which one is really us.

---

## Step 3: Check the Status Page After Each Scan #step3

After every scan, visit:

http://10.129.2.28/status.php

Write down the alert count. If it's climbing fast, you're being too loud.

| Alert Increase | What It Means |
|----------------|---------------|
| 0-5 | Good - you're being stealthy |
| 5-20 | Moderate - slow down |
| 20+ | Danger - you'll be banned soon |
| Banned | Too late - start over |

---

## Step 4: If You Get Banned #step4

If the status page shows you've been banned, don't panic. This is part of learning!

1. Wait for the ban to expire (usually a few minutes)
2. Review what you did that caused the spike
3. Try again with quieter options
4. Remember: slower is better!

---

## Practice Workflow #workflow

### Attempt 1: Too Loud

sudo nmap 10.129.2.28 -p- -sS -T4
→ Alert count: 150 → BANNED

**Lesson:** Full port scan with -T4 is way too loud for this lab.

### Attempt 2: Better

sudo nmap 10.129.2.28 -p 1-100 -sS -T2
→ Alert count: 15 → Not banned, but getting close

### Attempt 3: Stealthy

sudo nmap 10.129.2.28 -p 1-100 -sT -T1 --max-retries 0 -f
→ Alert count: 3 → Success! Now we can scan a few more ports.

---

## Tips for Success #tips

1. **Start slow** - Begin with -T1 or -T2, not -T4
2. **Scan fewer ports** - 100 ports is better than 1000
3. **Check the status page OFTEN** - After every scan
4. **Take notes** - Write down what caused alert spikes
5. **Be patient** - Stealthy scanning takes time
6. **Use decoys** - -D RND:3 can hide your real IP
7. **Fragment packets** - -f sometimes helps
8. **Avoid default scripts** - -sC can be noisy
9. **No version detection** - -sV generates extra traffic
10. **If banned, learn and try again**

---

## Key Takeaways #keypoints

- This lab teaches you how IDS/IPS systems react to different scan types
- The status page gives you immediate feedback - use it!
- Slower scans generate fewer alerts
- Different techniques have different "noise levels"
- There's no single "right answer" - you must adapt to the target
- If you get banned, you've learned what NOT to do
- Real IDS/IPS systems work similarly - practice here helps in real engagements
- The goal is to gather information without being detected, not to scan fast
- Document your approach - what worked and what didn't
- When in doubt, go slower!
