---
tags: [module, nmap, port-scanning, beginner]
module: "Host and Port Scanning"
level: beginner
---

# Host and Port Scanning - Beginner's Guide #nmap #portscanning #beginner

## Why Understand How Scanning Works? #core

It is essential to understand how the tool we use works and how it performs and processes the different functions. We will only understand the results if we know what they mean and how they are obtained.

After we find that our target is alive, we need a more accurate picture of the system. The information we need includes:

- Open ports and their services
- Service versions
- Information that the services provide
- Operating system

---

## The 6 Port States #port-states

When Nmap scans a port, it can report one of six different states:

| State | Description |
|-------|-------------|
| open | A connection was successfully established. This means the port is accepting connections. |
| closed | The port is accessible but no service is listening. The target sent back a RST packet. |
| filtered | Nmap cannot determine if the port is open or closed. Either no response was received, or we got an error code. This usually means a firewall is interfering. |
| unfiltered | This only happens during TCP-ACK scans. The port is accessible, but Nmap can't tell if it's open or closed. |
| open\|filtered | No response was received. This could mean the port is open, or a firewall is blocking us. |
| closed\|filtered | This only happens in idle scans. Nmap couldn't determine if the port is closed or filtered. |

---

## How Nmap Scans Ports by Default #defaults

By default, Nmap scans the top 1000 TCP ports using the SYN scan (-sS).

**Important:** The SYN scan is only the default when we run Nmap as root. If we run without root privileges, Nmap automatically uses the TCP Connect scan (-sT) instead.

We can define which ports to scan in several ways:

| Method | Example | Description |
|--------|---------|-------------|
| Specific ports | -p 22,25,80,139,445 | Scan only these exact ports |
| Range | -p 22-445 | Scan all ports from 22 to 445 |
| All ports | -p- | Scan all 65535 ports |
| Top ports | --top-ports=10 | Scan the 10 most common ports |
| Fast scan | -F | Scan top 100 ports (faster) |

---

## Example: Scanning Top 10 TCP Ports #example

sudo nmap 10.129.2.28 --top-ports=10

Output:
Starting Nmap 7.80 at 2020-06-15 15:36 CEST
Nmap scan report for 10.129.2.28
Host is up (0.021s latency).

PORT     STATE    SERVICE
21/tcp   closed   ftp
22/tcp   open     ssh
23/tcp   closed   telnet
25/tcp   open     smtp
80/tcp   open     http
110/tcp  open     pop3
139/tcp  filtered netbios-ssn
443/tcp  closed   https
445/tcp  filtered microsoft-ds
3389/tcp closed   ms-wbt-server

Notice how ports can be open, closed, or filtered.

---

## Watching Nmap in Action with --packet-trace #packet-trace

To really understand what's happening, we can watch the actual packets being sent and received using --packet-trace.

Let's scan just port 21 and watch what happens:

sudo nmap 10.129.2.28 -p 21 --packet-trace -Pn -n --disable-arp-ping

Output:
SENT (0.0429s) TCP 10.10.14.2:63090 > 10.129.2.28:21 S ttl=56 id=57322 iplen=44 seq=1699105818 win=1024 <mss 1460>
RCVD (0.0573s) TCP 10.129.2.28:21 > 10.10.14.2:63090 RA ttl=64 id=0 iplen=40 seq=0 win=0

### What This Means

**The SENT line:** We (10.10.14.2) sent a TCP packet with the SYN flag (S) to our target (10.129.2.28) on port 21.

**The RCVD line:** The target responded with a TCP packet containing RST and ACK flags (RA). This tells us the port is closed.

The RST flag resets the connection, and ACK acknowledges receiving our packet.

---

## TCP Connect Scan (-sT) #connect-scan

The Connect scan (-sT) uses the normal TCP three-way handshake to determine if a port is open.

### How it works:
1. Nmap sends a SYN packet
2. If the port is open, the target responds with SYN-ACK
3. Nmap completes the handshake by sending ACK
4. Then immediately closes the connection

### When to use it:
- When you don't have root privileges (can't use SYN scan)
- When accuracy is more important than stealth
- When you want to be "polite" to services (behaves like a normal client)

### When NOT to use it:
- It's easily detected and logged
- It's slower than SYN scan
- It completes connections, which may trigger alerts

### Example:
sudo nmap 10.129.2.28 -p 443 --packet-trace -sT

Output:
CONN (0.0396s) TCP localhost > 10.129.2.28:443 => Connected

---

## Understanding Filtered Ports #filtered

When a port shows as "filtered," a firewall is likely interfering. There are two common behaviors:

### 1. Firewall DROPS packets (no response)

sudo nmap 10.129.2.28 -p 139 --packet-trace

Notice:
- Nmap sends packets but gets no response
- It retries after a timeout (--max-retries defaults to 10)
- The scan takes much longer (2+ seconds instead of 0.05 seconds)

### 2. Firewall REJECTS packets (sends back an error)

sudo nmap 10.129.2.28 -p 445 --packet-trace

Output includes:
RCVD ICMP [10.129.2.28 > 10.129.2.28 Port 445 unreachable (type=3/code=3)]

This ICMP reply with type 3, code 3 means "port unreachable." The firewall is explicitly rejecting our packets.

---

## UDP Scanning (-sU) #udp-scan

UDP scanning is different from TCP because UDP is stateless - there's no handshake, no acknowledgments.

### The Challenges:

1. **Slower:** Since there's no acknowledgment, Nmap has to wait for timeouts, making UDP scans much slower.
2. **Unreliable:** Open ports often don't respond at all. We only know a port is open if the application specifically responds.
3. **Rate limiting:** Many systems limit how many ICMP "port unreachable" messages they send, making closed ports hard to detect.

### Example UDP Scan:

sudo nmap 10.129.2.28 -F -sU

This scans the top 100 UDP ports. Notice how long it takes (98 seconds vs 1-2 seconds for TCP).

### UDP Port States:

| Scenario | Result |
|----------|--------|
| Service responds with UDP packet | Port is open |
| ICMP error "port unreachable" (type 3, code 3) | Port is closed |
| ICMP error type 3, other codes | Port is filtered |
| No response after retries | open|filtered |

### Example: Open UDP Port

sudo nmap 10.129.2.28 -sU -p 137 --packet-trace

We see a UDP response, confirming the port is open.

### Example: Closed UDP Port

sudo nmap 10.129.2.28 -sU -p 100 --packet-trace

We receive ICMP "port unreachable," confirming the port is closed.

### Example: Filtered UDP Port

sudo nmap 10.129.2.28 -sU -p 138 --packet-trace

No response received → marked as open|filtered.

---

## Service Version Detection (-sV) #version-scan

The -sV option tells Nmap to probe open ports to determine exactly what service is running and what version.

sudo nmap 10.129.2.28 -p 445 -sV

Output includes:
445/tcp open  netbios-ssn Samba smbd 3.X - 4.X (workgroup: WORKGROUP)
Service Info: Host: Ubuntu

This tells us:
- The service is Samba (SMB)
- Version range: 3.X to 4.X
- Host is probably Ubuntu

This information is gold for finding exploits.

---

## Key Takeaways #keypoints

- There are 6 possible port states, each with specific meanings
- SYN scan (-sS) is the default when running as root
- Connect scan (-sT) is used without root privileges
- Filtered ports usually mean a firewall is interfering
- UDP scanning is much slower and less reliable than TCP
- Use --packet-trace to see exactly what's happening
- Always use -sV to identify service versions
- Different scan types work better in different situations
- The official Nmap documentation at https://nmap.org/book/man-port-scanning-techniques.html has extensive details on scanning techniques
