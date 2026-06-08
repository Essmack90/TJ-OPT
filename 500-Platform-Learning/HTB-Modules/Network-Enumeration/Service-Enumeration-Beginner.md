---
tags: [module, nmap, service-enumeration, version-detection, beginner]
module: "Service Enumeration"
level: beginner
---

# Service Enumeration - Beginner's Guide #serviceenum #versiondetection #beginner

## Why Service Enumeration Matters #core

Once we find open ports, we need to know what's actually running on them. Service enumeration is the process of identifying:

- The application running on each port (SSH, HTTP, SMTP, etc.)
- The exact version number (OpenSSH 7.6p1, Apache 2.4.29, etc.)
- Additional information (hostname, OS, configuration details)

**Why is this so important?**

With an exact version number, we can:
- Search for known vulnerabilities that match that specific version
- Analyze the source code for that version (if available)
- Find exploits that fit the service AND the operating system
- Tailor our attacks to the exact target configuration

Think of it like knowing the exact model of a car before trying to steal it - a key that works for a 2010 Honda won't help you with a 2020 BMW.

---

## The Smart Way to Scan #strategy

### Step 1: Quick Initial Scan (Low Traffic)

First, run a quick port scan to get an overview. This generates less traffic and reduces the chance of being detected or blocked.

sudo nmap 10.129.2.28 --top-ports 100 -v

### Step 2: Full Port Scan in Background

Then start a full port scan (-p-) that runs in the background while you work on the quick results.

sudo nmap 10.129.2.28 -p- -sV -oA full-scan &

The & at the end sends the scan to the background.

### Step 3: Version Detection on Open Ports

Once you know which ports are open, run version detection (-sV) specifically on those ports.

sudo nmap 10.129.2.28 -p 22,25,80,110,143 -sV

---

## Monitoring Scan Progress #progress

A full port scan (-p-) can take a long time (sometimes hours). Here are ways to monitor progress.

### Method 1: Press Space Bar

During the scan, press the space bar to see the current status:

sudo nmap 10.129.2.28 -p- -sV

[Space Bar]
Stats: 0:00:03 elapsed; 0 hosts completed (1 up), 1 undergoing SYN Stealth Scan
SYN Stealth Scan Timing: About 3.64% done; ETC: 19:45 (0:00:53 remaining)

### Method 2: Automatic Status Updates

Use --stats-every=5s to get status updates every 5 seconds:

sudo nmap 10.129.2.28 -p- -sV --stats-every=5s

Stats: 0:00:05 elapsed; 13.91% done; ETC: 19:49 (0:00:31 remaining)
Stats: 0:00:10 elapsed; 39.57% done; ETC: 19:48 (0:00:15 remaining)

### Method 3: Increase Verbosity

Use -v or -vv to see open ports as soon as they're discovered:

sudo nmap 10.129.2.28 -p- -sV -v

Discovered open port 995/tcp on 10.129.2.28
Discovered open port 80/tcp on 10.129.2.28
Discovered open port 993/tcp on 10.129.2.28
Discovered open port 143/tcp on 10.129.2.28

This is exciting - you don't have to wait for the whole scan to finish!

---

## Example: Full Scan with Version Detection #example

sudo nmap 10.129.2.28 -p- -sV

Nmap scan report for 10.129.2.28
Host is up (0.013s latency).
Not shown: 65525 closed ports
PORT      STATE    SERVICE      VERSION
22/tcp    open     ssh          OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
25/tcp    open     smtp         Postfix smtpd
80/tcp    open     http         Apache httpd 2.4.29 ((Ubuntu))
110/tcp   open     pop3         Dovecot pop3d
139/tcp   filtered netbios-ssn
143/tcp   open     imap         Dovecot imapd (Ubuntu)
445/tcp   filtered microsoft-ds
993/tcp   open     ssl/imap     Dovecot imapd (Ubuntu)
995/tcp   open     ssl/pop3     Dovecot pop3d
Service Info: Host:  inlane; OS: Linux; CPE: cpe:/o:linux:linux_kernel

### What We Learn

- **SSH:** OpenSSH 7.6p1 on Ubuntu - specific version info
- **SMTP:** Postfix smtpd - mail server
- **HTTP:** Apache 2.4.29 on Ubuntu - web server
- **POP3/IMAP:** Dovecot - email protocols
- **OS:** Linux (Ubuntu) confirmed

This information is gold for finding exploits.

---

## How Nmap Identifies Versions #how-it-works

Nmap uses two main methods to identify service versions:

### Method 1: Banner Grabbing

When you connect to many services, they send a "banner" - a welcome message identifying themselves.

Example connecting to SMTP:
nc -nv 10.129.2.28 25
220 inlane ESMTP Postfix (Ubuntu)

Nmap reads these banners and reports them.

### Method 2: Signature Matching

If no banner is sent, Nmap uses a database of service signatures to probe and match responses.

This takes longer but can identify services that don't advertise themselves.

---

## The Problem: Nmap Might Miss Information #limitations

Sometimes Nmap's automatic scan can miss information because it doesn't know how to handle it.

Look at this Nmap output:

25/tcp open  smtp    Postfix smtpd

Now look at what Nmap actually received:

NSOCK INFO: Callback: READ SUCCESS [10.129.2.28:25] (35 bytes): 220 inlane ESMTP Postfix (Ubuntu)..

The server sent "Ubuntu" in the banner, but Nmap didn't show it in the results! This happens because Nmap's parsing isn't always perfect.

**Lesson:** Always verify manually when possible.

---

## Manual Banner Grabbing #manual

### Using Netcat (nc)

nc -nv 10.129.2.28 25
Connection to 10.129.2.28 port 25 [tcp/*] succeeded!
220 inlane ESMTP Postfix (Ubuntu)

Now we see the Ubuntu information that Nmap missed.

### Using tcpdump to Watch the Conversation

In one terminal, start tcpdump:

sudo tcpdump -i eth0 host 10.10.14.2 and 10.129.2.28

In another terminal, connect with nc:

nc -nv 10.129.2.28 25

Now watch the packets:

18:28:07.128564 IP 10.10.14.2.59618 > 10.129.2.28.smtp: Flags [S]  (SYN)
18:28:07.255151 IP 10.129.2.28.smtp > 10.10.14.2.59618: Flags [S.] (SYN-ACK)
18:28:07.255281 IP 10.10.14.2.59618 > 10.129.2.28.smtp: Flags [.]  (ACK)
18:28:07.319306 IP 10.129.2.28.smtp > 10.10.14.2.59618: Flags [P.] (PSH-ACK) 35 bytes: SMTP: 220 inlane ESMTP Postfix (Ubuntu)
18:28:07.319426 IP 10.10.14.2.59618 > 10.129.2.28.smtp: Flags [.] (ACK)

### What the Flags Mean

| Flags | Meaning |
|-------|---------|
| [S] | SYN - Start connection |
| [S.] | SYN-ACK - Acknowledge and respond |
| [.] | ACK - Acknowledge receipt |
| [P.] | PSH-ACK - Sending data with acknowledgment |

The server sends data with the PSH flag, telling us "here's the information you requested."

---

## Key Takeaways #keypoints

- Service enumeration identifies exactly what's running on open ports
- Version numbers are critical for finding the right exploits
- Scan strategically: quick scan first, full scan in background
- Use --stats-every=5s to monitor long scans
- Increase verbosity (-v) to see results as they're found
- Nmap may miss some banner information - always verify manually
- Manual banner grabbing with nc can reveal hidden details
- tcpdump lets you watch the full conversation
- The more you know about the service, the easier your job becomes
- Report incorrect Nmap results at https://nmap.org/submit/
