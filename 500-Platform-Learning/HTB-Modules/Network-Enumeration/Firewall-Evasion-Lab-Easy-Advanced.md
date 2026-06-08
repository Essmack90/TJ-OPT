---
tags: [module, nmap, evasion, firewall, ids, ips, lab, easy, advanced, practical]
module: "Firewall and IDS/IPS Evasion - Easy Lab"
level: advanced
---

# Firewall Evasion Easy Lab - Practical Guide #evasion #lab #advanced

## Lab Environment #environment

**Target:** 10.129.2.28
**Status Page:** http://10.129.2.28/status.php
**Ban Threshold:** Unknown - we must discover it through careful testing
**Goal:** Gather maximum information with minimum alerts

The status page shows us our "noise level" in real-time. This is invaluable feedback that real IDS systems don't provide - use it to learn!

---

## Methodology: Progressive Stealth Scanning #methodology

### Phase 0: Baseline Measurement

Before any scanning, visit the status page and record the baseline alert count.

curl -s http://10.129.2.28/status.php | grep -o '[0-9]\+'

### Phase 1: Host Discovery (Minimal Footprint)

**Test 1: TCP SYN Ping**
sudo nmap 10.129.2.28 -PS -n --disable-arp-ping -oA phase1-syn

Record alerts. If >5, move to quieter method.

**Test 2: TCP ACK Ping (Quieter)**
sudo nmap 10.129.2.28 -PA -n --disable-arp-ping -oA phase1-ack

ACK packets often trigger fewer alerts than SYN.

**Test 3: No Ping (-Pn)**
If both ping methods trigger alerts, assume host is up and skip discovery:

echo "10.129.2.28" > targets.txt

---

## Phase 2: Port Selection Strategy #port-selection

Instead of scanning all ports, use intelligent guessing:

### Most Common Ports (Least Traffic)

sudo nmap 10.129.2.28 -p 21,22,23,25,53,80,110,111,135,139,143,443,445,993,995,1723,3306,3389,5900,8080 -sS -T2 --max-retries 0 -oA phase2-common

### If That's Still Too Loud

Reduce to TOP 10 ports:

sudo nmap 10.129.2.28 --top-ports 10 -sS -T1 --max-retries 0 -oA phase2-top10

---

## Phase 3: Scan Technique Optimization #technique-optimization

### Technique A: TCP Connect Scan (-sT)

Completes full handshake, looks like normal traffic:

sudo nmap 10.129.2.28 -p 22,80,443 -sT -T1 --max-retries 0 -oA phase3-connect

### Technique B: SYN Scan with Fragmentation

sudo nmap 10.129.2.28 -p 22,80,443 -sS -f --mtu 16 -T1 --max-retries 0 -oA phase3-frag

### Technique C: Decoy Scan

sudo nmap 10.129.2.28 -p 22,80,443 -sS -D RND:4 -T1 --max-retries 0 -oA phase3-decoy

### Technique D: Source Port Manipulation

sudo nmap 10.129.2.28 -p 22,80,443 -sS --source-port 53 -T1 --max-retries 0 -oA phase3-port53

### Technique E: Idle Scan (Zombie)

If we find a suitable zombie host:

sudo nmap -sI zombie_ip:80 -p 22,80,443 -Pn -oA phase3-idle

---

## Phase 4: Incremental Port Expansion #expansion

Once we find a technique that works with low alerts, slowly expand:

### Step 4.1: Add 10 ports
sudo nmap 10.129.2.28 -p $(cat phase2-common.gnmap | grep Ports | cut -d' ' -f2 | tr ',' ' ') --top-ports 20 -sS -T1 --max-retries 0 -f --source-port 53 -oA phase4-20

### Step 4.2: Add 20 ports
sudo nmap 10.129.2.28 -p $(cat phase4-20.gnmap | grep Ports | cut -d' ' -f2 | tr ',' ' ') --top-ports 40 -sS -T1 --max-retries 0 -f --source-port 53 -oA phase4-40

### Step 4.3: Add 40 ports
Continue incrementing until you reach desired coverage or hit alert threshold.

---

## Phase 5: Service Detection (If Possible) #version-detection

Version detection (-sV) is NOISY. Only attempt if alert count is very low.

### Ultra-Stealthy Version Detection

sudo nmap 10.129.2.28 -p $(grep open phase4-40.gnmap | cut -d' ' -f2) -sV --version-intensity 0 -T1 --max-retries 0 --script-timeout 10s -oA phase5-version

| Option | Purpose |
|--------|---------|
| --version-intensity 0 | Lightest version detection |
| --script-timeout 10s | Kill slow scripts |

### Manual Banner Grabbing (Even Quieter)

For each open port, try manual connection:

nc -nv 10.129.2.28 22
nc -nv 10.129.2.28 80
GET / HTTP/1.0

This generates MINIMAL traffic and often reveals more than Nmap's version scan.

---

## Alert Monitoring Strategy #monitoring

### Track Alert Trends

Create a monitoring script:

#!/bin/bash
TARGET="10.129.2.28"
LOG="alert-log.txt"

while true; do
    ALERTS=$(curl -s http://$TARGET/status.php | grep -o '[0-9]\+')
    TIMESTAMP=$(date +%H:%M:%S)
    echo "$TIMESTAMP - $ALERTS alerts" >> $LOG
    sleep 10
done

### Alert Threshold Analysis

| Alert Rate | Interpretation | Action |
|------------|----------------|--------|
| 0-1/min | Excellent | Can proceed cautiously |
| 2-5/min | Good | Maintain current pace |
| 5-10/min | Warning | Reduce scan speed |
| 10+/min | Critical | Stop immediately, analyze |
| Sudden spike | Detection triggered | Abort, wait for reset |

---

## Ban Recovery Strategy #recovery

If banned:
1. Immediately stop all scanning
2. Wait 5-10 minutes
3. Check if ban has expired
4. Review logs to identify what triggered it
5. Use even quieter techniques when resuming
6. Consider using a different source IP if available

---

## Complete Stealthy Scan Workflow #workflow

### Script: progressive-evasion.sh

#!/bin/bash
TARGET="10.129.2.28"
BASENAME="evasion-lab"
ALERT_URL="http://$TARGET/status.php"

check_alerts() {
    curl -s $ALERT_URL | grep -o '[0-9]\+'
}

echo "Starting stealthy scan at $(date)"
INITIAL_ALERTS=$(check_alerts)
echo "Initial alerts: $INITIAL_ALERTS"

# Phase 1: Minimal host discovery
echo "Phase 1: TCP SYN ping"
sudo nmap $TARGET -PS -n --disable-arp-ping -oA $BASENAME-01

# Check alerts
CURRENT=$(check_alerts)
echo "Alerts after phase 1: $CURRENT"

# Phase 2: Top 10 ports, very slow
echo "Phase 2: Top 10 ports"
sudo nmap $TARGET --top-ports 10 -sS -T1 --max-retries 0 -f --source-port 53 -oA $BASENAME-02

# Check alerts
CURRENT=$(check_alerts)
echo "Alerts after phase 2: $CURRENT"

# Phase 3: Expand to ports found +20 more
if [ $CURRENT -lt 50 ]; then
    echo "Phase 3: Expanding ports"
    sudo nmap $TARGET --top-ports 30 -sS -T1 --max-retries 0 -f --source-port 53 -oA $BASENAME-03
else
    echo "Alert threshold high - stopping expansion"
fi

echo "Final alerts: $(check_alerts)"
echo "Scan complete at $(date)"

---

## Common Pitfalls #pitfalls

| Mistake | Consequence | Better Approach |
|---------|-------------|-----------------|
| Starting with -p- | Immediate ban | Scan 10 ports, expand gradually |
| Using -sV early | Massive alerts | Manual banner grabbing first |
| Ignoring status page | No feedback | Check after EVERY scan |
| Fast timing (-T4) | Detection | Start with -T1, adjust up slowly |
| No decoys | Source IP tracked | Use -D RND:3 to hide |
| Default scripts (-sC) | Extra traffic | Avoid entirely |

---

## What Success Looks Like #success

After a successful stealthy scan, you should have:

1. A list of open ports with minimal alerts (<20 total)
2. Service banners for critical ports (from manual grabbing)
3. A clear understanding of what triggers alerts
4. Documentation of your approach for the client report
5. Confidence to apply these techniques in real engagements

---

## Key Takeaways #keypoints

- The status page is your best friend - use it constantly
- Start extremely slow and gradually increase
- Different techniques trigger different alert levels
- Document every scan and its alert count
- If you get banned, you've learned something valuable
- Manual banner grabbing is often stealthier than -sV
- Source port 53 can be a game-changer
- Fragmentation helps with some IDS signatures
- Decoys distribute the "blame" across multiple IPs
- There's no one-size-fits-all approach - adapt to the target
- Real IDS systems won't give you a status page - learn the patterns here
