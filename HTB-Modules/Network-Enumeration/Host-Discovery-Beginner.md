---
tags: [module, nmap, host-discovery, beginner]
module: "Host Discovery with Nmap"
level: beginner
---

# Host Discovery - Finding Live Hosts #nmap #discovery #beginner

## What is Host Discovery? #core

Before we can attack anything, we need to know what's out there. Host discovery is the process of finding which systems on a network are alive and responding.

Think of it like walking down a street and checking which houses have lights on - we only want to knock on doors where someone might answer.

## Why Store Your Scans? #documentation

It is always recommended to store every single scan. This can later be used for:
- Comparison between different scans
- Documentation for reports
- Evidence of findings
- Tracking changes over time

Different tools may produce different results. Therefore it can be beneficial to distinguish which tool produces which results.

---

## Scanning Methods #methods

### Method 1: Scan a Network Range

The most common approach is to scan an entire subnet to see what's alive.

sudo nmap 10.129.2.0/24 -sn -oA tnet

| Option | Description |
|--------|-------------|
| 10.129.2.0/24 | Target network range |
| -sn | Disables port scanning (ping only) |
| -oA tnet | Stores results in all formats with name 'tnet' |

Example output:
10.129.2.4
10.129.2.10
10.129.2.11
10.129.2.18
10.129.2.19
10.129.2.20
10.129.2.28

### Method 2: Scan from an IP List

Sometimes we're given a specific list of IPs to test.

Create a file called hosts.lst:
cat hosts.lst
10.129.2.4
10.129.2.10
10.129.2.11
10.129.2.18
10.129.2.19
10.129.2.20
10.129.2.28

Then scan using that list:
sudo nmap -sn -oA tnet -iL hosts.lst

| Option | Description |
|--------|-------------|
| -iL hosts.lst | Reads targets from the provided list |

Notice that only 3 of 7 hosts responded:
10.129.2.18
10.129.2.19
10.129.2.20

This doesn't mean the others are dead. They might just be ignoring ICMP requests due to firewall settings.

### Method 3: Scan Multiple Specific IPs

If you only need to scan a few specific IPs:

sudo nmap -sn -oA tnet 10.129.2.18 10.129.2.19 10.129.2.20

If they're consecutive, you can use a range:
sudo nmap -sn -oA tnet 10.129.2.18-20

### Method 4: Scan a Single IP

Before deep scanning a host, verify it's alive:

sudo nmap 10.129.2.18 -sn -oA host

Output:
Starting Nmap 7.80 at 2020-06-14 23:59 CEST
Nmap scan report for 10.129.2.18
Host is up (0.087s latency).
MAC Address: DE:AD:00:00:BE:EF
Nmap done: 1 IP address (1 host up) scanned in 0.11 seconds

---

## How Nmap Determines if a Host is Alive #technique

When we disable port scan with -sn, Nmap automatically does a ping scan using ICMP Echo Requests (-PE). However, there's an important detail:

Before sending an ICMP echo request, Nmap first sends an ARP ping on the local network. This often gets an ARP reply immediately.

We can see this in action with --packet-trace:

sudo nmap 10.129.2.18 -sn -oA host -PE --packet-trace

Output shows:
SENT (0.0074s) ARP who-has 10.129.2.18 tell 10.10.14.2
RCVD (0.0309s) ARP reply 10.129.2.18 is-at DE:AD:00:00:BE:EF

We can also use --reason to see WHY Nmap thinks a host is alive:

sudo nmap 10.129.2.18 -sn -oA host -PE --reason

Output:
Host is up, received arp-response (0.028s latency).

### Disabling ARP

To force ICMP echo requests only (no ARP), use --disable-arp-ping:

sudo nmap 10.129.2.18 -sn -oA host -PE --packet-trace --disable-arp-ping

Now we see the ICMP exchange:
SENT ICMP [10.10.14.2 > 10.129.2.18 Echo request]
RCVD ICMP [10.129.2.18 > 10.10.14.2 Echo reply]

---

## Key Takeaways #keypoints

- Host discovery finds live systems before detailed scanning
- Always store your scans (-oA) for documentation
- Different methods work on different networks
- ARP is used automatically on local networks and is very reliable
- ICMP echo requests can be blocked by firewalls
- No response doesn't mean the host is dead - just that it didn't answer this particular probe
- Pay attention to details - the packet trace options show exactly what's happening
- The Nmap documentation has extensive host discovery strategies at https://nmap.org/book/host-discovery-strategies.html
