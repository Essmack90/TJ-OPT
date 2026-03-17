---
tags: [module, nmap, performance, timing, beginner]
module: "Nmap Performance Optimization"
level: beginner
---

# Nmap Performance - Beginner's Guide #nmap #performance #timing #beginner

## Why Performance Matters #core

When scanning large networks (like a whole /24 subnet with 256 hosts), scan speed becomes critical. A default scan might take 30-40 seconds, but with optimization we can often cut that to 8-12 seconds.

However, there's always a trade-off: **faster scans can miss hosts or ports**. We need to balance speed against accuracy.

The key performance factors we can control are:
- Timeouts (how long we wait for responses)
- Retries (how many times we re-send packets)
- Rates (how many packets we send per second)
- Timing templates (pre-configured speed settings)

---

## Understanding RTT (Round-Trip Time) #rtt

RTT is the time it takes for a packet to travel to the target and back. Nmap measures this for each response and adjusts its timing accordingly.

### The Problem

By default, Nmap starts with conservative timeouts (100ms). This is safe but slow.

### The Solution

We can adjust three RTT-related settings:

| Option | Description | Example |
|--------|-------------|---------|
| --initial-rtt-timeout | Starting timeout value | --initial-rtt-timeout 50ms |
| --min-rtt-timeout | Minimum timeout allowed | --min-rtt-timeout 10ms |
| --max-rtt-timeout | Maximum timeout allowed | --max-rtt-timeout 100ms |

### Example: Optimized RTT vs Default

**Default Scan (39 seconds):**
sudo nmap 10.129.2.0/24 -F

**Optimized RTT Scan (12 seconds):**
sudo nmap 10.129.2.0/24 -F --initial-rtt-timeout 50ms --max-rtt-timeout 100ms

| Result | Default | Optimized |
|--------|---------|-----------|
| Time | 39.44 seconds | 12.29 seconds |
| Hosts found | 10 | 8 |

**Important:** The optimized scan found 2 fewer hosts because we cut timeouts too aggressively. Some slow hosts didn't respond in time.

---

## Adjusting Retries #retries

When Nmap gets no response, it retries. Default is 10 retries. We can reduce this to speed up scans.

**Default Scan (10 retries):**
sudo nmap 10.129.2.0/24 -F | grep "/tcp" | wc -l
23 ports found

**Reduced Retries (0 retries):**
sudo nmap 10.129.2.0/24 -F --max-retries 0 | grep "/tcp" | wc -l
21 ports found

**Trade-off:** We lost 2 ports but the scan was faster. For casual reconnaissance, this might be acceptable. For thorough assessments, it's risky.

---

## Controlling Packet Rate #rate

If we know the network can handle it, we can set a minimum packet rate to force Nmap to send packets faster.

**Default Scan (29 seconds, 23 ports found):**
sudo nmap 10.129.2.0/24 -F -oN tnet.default

**Optimized Rate Scan (8.6 seconds, 23 ports found):**
sudo nmap 10.129.2.0/24 -F -oN tnet.minrate300 --min-rate 300

**Result:** Same number of ports found, 3.4x faster! This is a huge improvement.

The --min-rate 300 tells Nmap to send at least 300 packets per second. This works well when:
- You know the network bandwidth is sufficient
- You're not worried about detection
- You're in a white-box test (authorized to scan aggressively)

---

## Timing Templates (-T0 to -T5) #timing-templates

Nmap provides six pre-configured timing templates. These are the easiest way to adjust scan speed without understanding all the individual options.

| Template | Name | Description |
|----------|------|-------------|
| -T0 | Paranoid | Extremely slow, for IDS evasion |
| -T1 | Sneaky | Very slow, also for evasion |
| -T2 | Polite | Slower, uses less bandwidth |
| -T3 | Normal | Default, balanced |
| -T4 | Aggressive | Faster, assumes good network |
| -T5 | Insane | Fastest, may miss results |

### Default vs Insane Example

**Default (-T3):**
sudo nmap 10.129.2.0/24 -F -oN tnet.default
32.44 seconds, 23 ports found

**Insane (-T5):**
sudo nmap 10.129.2.0/24 -F -oN tnet.T5 -T5
18.07 seconds, 23 ports found

**Result:** Nearly twice as fast, same number of ports found. In this case, -T5 worked perfectly.

### When to Use Each Template

| Template | Best For |
|----------|----------|
| -T0, -T1 | IDS evasion, extremely stealthy scanning |
| -T2 | Slower networks, polite scanning |
| -T3 | Default - safe choice |
| -T4 | Fast networks, internal pentests |
| -T5 | Very fast networks, when speed critical |

---

## Key Performance Concepts #concepts

### The Speed/Accuracy Trade-off

Every performance optimization involves a trade-off:
- **Faster** = Might miss hosts or ports
- **Slower** = More accurate, but takes longer

### When to Optimize Aggressively

- **White-box tests:** You're authorized, know the network, can push hard
- **Internal networks:** Low latency, reliable connections
- **Large networks:** 256+ hosts need optimization to finish in reasonable time

### When to Be Conservative

- **Black-box tests:** Unknown network conditions
- **IDS/IPS present:** Need stealth
- **Critical systems:** Can't risk missing anything

---

## Practical Recommendations #recommendations

### For Beginners

Start with -T4 on internal networks. It's safe and fast:

sudo nmap 10.129.2.0/24 -F -T4

### For Large Networks (256+ hosts)

Add min-rate optimization:

sudo nmap 10.129.2.0/24 -F -T4 --min-rate 300

### For Maximum Stealth

Use -T1 or -T0, but be prepared to wait:

sudo nmap 10.129.2.0/24 -F -T1

### For Thorough Assessment

Don't optimize too aggressively. Use default -T3:

sudo nmap 10.129.2.0/24 -p- -sV -T3

---

## Key Takeaways #keypoints

- Performance tuning is about balancing speed against accuracy
- RTT timeouts (--initial-rtt-timeout, --max-rtt-timeout) control wait time
- Retries (--max-retries) can be reduced for speed, but may miss ports
- Rate limiting (--min-rate) can dramatically speed up scans
- Timing templates (-T0 to -T5) are the easiest way to adjust speed
- -T4 is recommended for most internal networks
- Always test optimizations to ensure you're not missing critical results
- Faster isn't always better - know when to slow down
- Document your scan parameters so you know what you might have missed
- More details at https://nmap.org/book/man-performance.html
