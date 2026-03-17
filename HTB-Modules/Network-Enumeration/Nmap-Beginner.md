---
tags: [module, nmap, scanning, beginner]
module: "Introduction to Nmap"
level: beginner
---

# Introduction to Nmap - Beginner's Guide #nmap #scanning #beginner

## What is Nmap? #core

Nmap (Network Mapper) is an open-source tool for network analysis and security auditing. It's written in C, C++, Python, and Lua.

Think of it as a **network flashlight** - it shines light on a network and tells you:
- What devices are connected (host discovery)
- What doors/ports are open (port scanning)
- What programs are running on those ports (service enumeration)
- What operating system is being used (OS detection)

## Who Uses Nmap? #use-cases

Nmap is one of the most used tools by:
- Network administrators
- IT security specialists
- Penetration testers
- Ethical hackers

## What Can Nmap Do? #capabilities

| Use Case | Description |
|----------|-------------|
| Security Auditing | Check if networks are configured securely |
| Penetration Testing | Simulate attacks to find weaknesses |
| Firewall Testing | Verify firewall rules are working as expected |
| IDS Testing | Check if intrusion detection systems alert properly |
| Network Mapping | Create a map of all devices on a network |
| Response Analysis | Analyze how devices respond to different packets |
| Open Port Identification | Find all entry points into a system |
| Vulnerability Assessment | Identify potential security holes |

---

## How Nmap Works #architecture

Nmap uses raw packets to probe networks and analyze responses. It's like sending different types of messages and seeing how devices reply.

The main scanning techniques can be broken down into:

1. Host discovery - Finding live hosts
2. Port scanning - Finding open doors
3. Service enumeration - Identifying what's running behind those doors
4. OS detection - Determining the operating system
5. Scriptable interaction - Using the Nmap Scripting Engine (NSE) to automate tasks

---

## Nmap Syntax #syntax

The basic syntax is simple:

nmap <scan types> <options> <target>

Examples:
nmap -sS localhost
nmap -sV -p- 192.168.1.1
nmap -sS -sV -O 10.10.10.10

---

## The TCP-SYN Scan (-sS) #scan-types

This is one of the most popular scan methods and is often the default.

### How it Works

1. Nmap sends a packet with the SYN flag (like knocking on a door)
2. If the door is open, the target sends back a SYN-ACK (acknowledging the knock)
3. Nmap NEVER completes the handshake - it's like walking away after hearing a response

This is called a "half-open" or "stealth" scan because it never establishes a full connection.

### What the Responses Mean

| Response | Meaning |
|----------|---------|
| SYN-ACK | Port is OPEN - the door is unlocked |
| RST | Port is CLOSED - the door is locked and bolted |
| No response | Port is FILTERED - something (like a firewall) is blocking us |

### Why This Matters

This scan is fast (thousands of ports per second) and less likely to be logged than a full connection.

---

## Example Scan #example

sudo nmap -sS localhost

Starting Nmap 7.80 ( https://nmap.org ) at 2020-06-11 22:50 UTC
Nmap scan report for localhost (127.0.0.1)
Host is up (0.000010s latency).
Not shown: 996 closed ports
PORT     STATE SERVICE
22/tcp   open  ssh
80/tcp   open  http
5432/tcp open  postgresql
5901/tcp open  vnc-1

Nmap done: 1 IP address (1 host up) scanned in 0.18 seconds

### Reading the Output

| Column | Meaning | Example |
|--------|---------|---------|
| PORT | Port number and protocol | 22/tcp |
| STATE | Open, closed, or filtered | open |
| SERVICE | Guessed service name | ssh |

## Key Takeaways #keypoints

- Nmap is a network discovery and security auditing tool
- It can find live hosts, open ports, running services, and operating systems
- The TCP-SYN scan (-sS) is fast and stealthy
- Different responses tell you if ports are open, closed, or filtered
- Always run Nmap with sudo for the most accurate results
- The SERVICE column is just a guess based on the port number - always verify manually
