---
tags: [module, nmap, performance, timing, advanced, practical]
module: "Nmap Performance Optimization"
level: advanced
---

# Nmap Performance - Complete Reference #nmap #performance #timing #advanced

## Performance Tuning Philosophy #core

One of Nmap's highest development priorities has always been performance. A default scan of a local host takes a fifth of a second, but scanning hundreds or thousands of hosts adds up. UDP scanning and version detection can increase scan times substantially. Firewall configurations, particularly response rate limiting, can also dramatically slow scans.

Expert users carefully craft Nmap commands to obtain only the information they care about while meeting their time constraints.

---

## Complete Performance Options Reference #options

| Option | Description | Time Format | Default |
|--------|-------------|-------------|---------|
| --min-hostgroup | Minimum parallel scan group size | Number of hosts | Varies |
| --max-hostgroup | Maximum parallel scan group size | Number of hosts | Varies |
| --min-parallelism | Minimum probes outstanding | Number of probes | Dynamic |
| --max-parallelism | Maximum probes outstanding | Number of probes | Dynamic |
| --min-rtt-timeout | Minimum probe timeout | ms, s, m, h | 10ms |
| --max-rtt-timeout | Maximum probe timeout | ms, s, m, h | 9000ms |
| --initial-rtt-timeout | Initial probe timeout | ms, s, m, h | 1000ms |
| --max-retries | Maximum port scan retransmissions | Number | 10 |
| --host-timeout | Give up on slow hosts | ms, s, m, h | None |
| --script-timeout | Maximum script execution time | ms, s, m, h | None |
| --scan-delay | Delay between probes | ms, s, m, h | 0 |
| --max-scan-delay | Maximum allowed delay | ms, s, m, h | 65535ms |
| --min-rate | Minimum packet sending rate | Packets/sec | None |
| --max-rate | Maximum packet sending rate | Packets/sec | None |
| --defeat-rst-ratelimit | Ignore RST rate limiting | Flag | Off |
| --defeat-icmp-ratelimit | Ignore ICMP rate limiting | Flag | Off |

**Time format examples:** 900ms, 5s, 3m, 2h

---

## Parallel Host Groups #hostgroups

Nmap scans multiple hosts in parallel for efficiency. It divides targets into groups and scans one group at a time.

### Default Behavior

Nmap starts with small groups (as low as 5) so first results come quickly, then increases group size up to 1024 for efficiency.

### Manual Control

| Option | Effect |
|--------|--------|
| --min-hostgroup 64 | Never use groups smaller than 64 |
| --max-hostgroup 256 | Never use groups larger than 256 |

### Example

sudo nmap --min-hostgroup 64 --max-hostgroup 256 -sS -p 1-1000 10.129.2.0/24

**Use case:** When scanning large networks, larger groups are more efficient. Trade-off is you wait longer for first results.

---

## Probe Parallelization #parallelism

Controls how many probes can be outstanding simultaneously.

### Default Behavior

Nmap calculates an ideal parallelism based on network performance. If packets are dropped, Nmap slows down. In perfect conditions, it can rise to several hundred.

### Manual Control

| Option | Effect |
|--------|--------|
| --min-parallelism 10 | Never go below 10 outstanding probes |
| --max-parallelism 100 | Never exceed 100 outstanding probes |

### Warning

Setting --min-parallelism too high may affect accuracy and reduces Nmap's ability to adapt to network conditions. Only use as last resort.

---

## Advanced RTT Optimization #rtt

### Formula

Nmap calculates timeout as:
timeout = max( min, min( max, last_rtt * 2 + safety_margin ) )

### Strategic RTT Settings

| Network Type | --initial-rtt-timeout | --min-rtt-timeout | --max-rtt-timeout |
|--------------|----------------------|-------------------|-------------------|
| Local network | 50ms | 10ms | 100ms |
| Data center | 100ms | 20ms | 200ms |
| Internet (good) | 250ms | 50ms | 500ms |
| Internet (poor) | 500ms | 100ms | 2000ms |
| Satellite | 1000ms | 200ms | 5000ms |

### Aggressive Settings for Speed

sudo nmap 10.129.2.0/24 -F --initial-rtt-timeout 50ms --max-rtt-timeout 100ms --min-rate 300

**Risk:** May miss hosts with higher latency.

### Conservative Settings for Accuracy

sudo nmap 10.129.2.0/24 -p- --initial-rtt-timeout 500ms --max-rtt-timeout 2000ms

---

## Retransmission Strategy #retries

### Default Behavior (--max-retries 10)

If no response, Nmap retries up to 10 times. This ensures accuracy but can significantly lengthen scans.

### Aggressive (--max-retries 0-2)

sudo nmap --max-retries 2 10.129.2.0/24 -F

**Use case:** Quick surveys where missing occasional ports is acceptable.

### Conservative (--max-retries 5-10)

sudo nmap --max-retries 5 10.129.2.28 -p- -sV

**Use case:** Thorough assessments where accuracy is critical.

### Formula for Success

The number of retries should balance:
- Network reliability (poor network needs more retries)
- Time constraints (less time = fewer retries)
- Criticality of missing ports (critical systems need more retries)

---

## Rate Limiting Mastery #rate

### --min-rate: Force Speed

sudo nmap --min-rate 300 10.129.2.0/24 -F

Forces Nmap to send at least 300 packets/second. Can dramatically speed scans but risks accuracy if network can't handle it.

### --max-rate: Limit Speed

sudo nmap --max-rate 10 10.129.2.0/24 -F

Limits to 10 packets/second. Useful for:
- Evading IDS/IPS
- Scanning rate-limited targets
- Polite scanning

### Combined Rate Control

sudo nmap --min-rate 50 --max-rate 200 10.129.2.0/24 -F

Keeps rate between 50-200 packets/second.

### Performance Impact

| --min-rate | Time (256 hosts, top 100 ports) | Ports Found |
|------------|----------------------------------|-------------|
| Default | 29.8s | 23 |
| 100 | 18.2s | 23 |
| 300 | 8.7s | 23 |
| 1000 | 5.1s | 22 |
| 5000 | 3.2s | 19 |

**Observation:** At 1000 packets/sec, we start losing ports. At 5000, significant loss.

---

## Host and Script Timeouts #timeouts

### --host-timeout

Abort scanning a host if it takes too long:

sudo nmap 10.129.2.0/24 -p- -sV --host-timeout 15m

**Use case:** When a few slow hosts are holding up the entire scan.

### --script-timeout

Terminate scripts that run too long:

sudo nmap --script vuln --script-timeout 10m target.com

**Use case:** Some vulnerability scripts can take hours. This caps them.

---

## Defeating Rate Limiting #defeat

### RST Rate Limiting

Many systems rate limit RST packets. This can slow Nmap dramatically.

--defeat-rst-ratelimit

Tells Nmap to ignore these rate limits for scans that don't treat non-responsive ports as open.

### ICMP Rate Limiting

--defeat-icmp-ratelimit

Trades accuracy for speed in UDP scans. Ports with no response become closed|filtered instead of open|filtered.

**Warning:** Increases chance of inaccuracy as many UDP services don't respond.

---

## Scan Delay for Evasion #evasion

### --scan-delay

Wait between probes:

sudo nmap --scan-delay 1s target.com

**Use case:** Evading threshold-based IDS/IPS. Many intrusion detection systems trigger on high packet rates.

### --max-scan-delay

Cap the maximum delay:

sudo nmap --scan-delay 1s --max-scan-delay 5s target.com

---

## Timing Templates Deep Dive #templates

### Template Settings

| Template | --max-rtt-timeout | --initial-rtt-timeout | --max-retries | Scan Delay |
|----------|-------------------|----------------------|---------------|------------|
| T0 (Paranoid) | N/A | N/A | N/A | 5 minutes |
| T1 (Sneaky) | N/A | N/A | N/A | 15 seconds |
| T2 (Polite) | N/A | N/A | N/A | 0.4 seconds |
| T3 (Normal) | Dynamic | Dynamic | 10 | None |
| T4 (Aggressive) | 1250ms | 500ms | 6 | 10ms max TCP |
| T5 (Insane) | 300ms | 250ms | 2 | 5ms max TCP |

### Additional T4 Settings
--min-rtt-timeout 100ms
--max-tcp-scan-delay 10ms

### Additional T5 Settings
--min-rtt-timeout 50ms
--host-timeout 15m
--script-timeout 10m
--max-tcp-scan-delay 5ms

---

## Practical Performance Strategies #strategies

### Strategy 1: Progressive Scanning

Phase 1: Quick discovery (1-2 minutes)
sudo nmap -T4 -F -sS target.com -oA quick

Phase 2: Targeted deep scan (background)
sudo nmap -T4 -p- -sV -sC --min-rate 300 target.com -oA deep &

Phase 3: UDP scan (if needed)
sudo nmap -T4 -sU --top-ports 20 target.com -oA udp

### Strategy 2: Rate-Based Optimization

sudo nmap --min-rate 500 --max-retries 2 -T4 -p- target.com

### Strategy 3: Network-Aware Tuning

# Measure baseline RTT
ping -c 10 target.com | tail -1 | awk -F '/' '{print $5 "ms"}'

# Use that to set timeouts
sudo nmap --initial-rtt-timeout $(($RTT*2))ms --max-rtt-timeout $(($RTT*4))ms target.com

### Strategy 4: Stealth Optimization

sudo nmap -T2 --scan-delay 100ms --max-retries 3 target.com

---

## Performance Optimization Checklist #checklist

| Question | Action |
|----------|--------|
| Is this a large network (>256 hosts)? | Use -T4, consider --min-rate |
| Is accuracy critical? | Use -T3, don't cut retries |
| Do I need stealth? | Use -T1/T2, --scan-delay |
| Is this a white-box test? | Use -T4, --min-rate 300 |
| Am I scanning UDP? | Be patient, use --top-ports |
| Are hosts rate limiting? | Use --defeat-*-ratelimit |
| Are slow hosts killing scan? | Use --host-timeout |

---

## Key Takeaways #keypoints

- Performance tuning always involves trade-offs between speed and accuracy
- RTT timeouts should be based on measured network latency
- Retries balance network reliability against time
- Rate limiting (--min-rate) is the most powerful speed optimization
- Timing templates (-T0 to -T5) provide easy access to tuned settings
- -T4 is safe for most internal networks and yields significant speed gains
- -T5 can be too aggressive - test before relying on it
- Progressive scanning (quick first, deep second) is often optimal
- Document your scan parameters to understand what you might have missed
- More aggressive isn't always better - know when to slow down
- The official documentation at https://nmap.org/book/man-performance.html has extensive details
