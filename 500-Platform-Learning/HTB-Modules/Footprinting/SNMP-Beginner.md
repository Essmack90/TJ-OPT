---
tags: [module/footprinting, snmp, network-monitoring, udp, level/beginner]
---

# SNMP Enumeration - Beginner's Guide

## What is SNMP?

SNMP (Simple Network Management Protocol) is used to monitor and manage network devices like routers, switches, servers, printers, and IoT devices. Think of it as a way for administrators to check the health of devices and even change settings remotely.

---

## Key Concepts

### SNMP Versions

| Version | Security | Encryption | Authentication | Usage |
|---------|----------|------------|----------------|-------|
| SNMPv1 | None | No | Community strings (plain text) | Legacy, avoid |
| SNMPv2c | None | No | Community strings (plain text) | Still common |
| SNMPv3 | Good | Yes | Username/password | Modern, secure |

### Community Strings

Community strings are like passwords for SNMP. There are two types:

| Type | Access | Risk |
|------|--------|------|
| **public** | Read-only | Can view system information |
| **private** | Read-write | Can modify device settings (DANGEROUS) |

The problem: In SNMPv1 and v2c, these are sent in PLAIN TEXT over the network.

---

## How SNMP Works

### Ports

| Port | Protocol | Use |
|------|----------|-----|
| 161 | UDP | Queries and commands |
| 162 | UDP | Traps (alerts from device to manager) |

### SNMP Communication Flow

1. Manager sends query to device on UDP 161
2. Device responds with requested data
3. Device can also send "traps" (alerts) to manager on UDP 162

---

## MIB and OID

### MIB (Management Information Base)

MIB is like a dictionary that defines what information is available on a device. It's a text file that describes all the SNMP objects a device supports.

### OID (Object Identifier)

OIDs are the actual addresses of information. They look like numbers separated by dots:

.1.3.6.1.2.1.1.1.0 = System description
.1.3.6.1.2.1.1.5.0 = Hostname
.1.3.6.1.2.1.25.1.6.0 = System uptime

Think of OIDs like a tree structure:
.iso.org.dod.internet.mgmt.mib-2.system.sysDescr.0

---

## Default SNMP Configuration

Config file: `/etc/snmp/snmpd.conf`

Example settings:

sysLocation    "Sitting on the Dock of the Bay"
sysContact     "admin@example.com"
sysServices    72
rocommunity    public  default -V systemonly
rwcommunity    private 10.129.14.0/24

### Important Directives

| Directive | Meaning |
|-----------|---------|
| rocommunity | Read-only community string |
| rwcommunity | Read-write community string |
| sysLocation | Device location |
| sysContact | Admin contact |
| sysName | Device hostname |

---

## Dangerous SNMP Settings

| Setting | Description | Risk |
|---------|-------------|------|
| rwuser noauth | Full write access without authentication | Complete control |
| rwcommunity public 0.0.0.0 | Write access from anywhere with "public" | Anyone can modify |
| rwcommunity6 public ::/0 | Same for IPv6 | Complete compromise |

**Critical:** If you find read-write access, you can change device configuration, reboot devices, or worse.

---

## What SNMP Reveals

A successful SNMP query can reveal:

- System information (OS, version, architecture)
- Hostname and domain
- Network interfaces and IP addresses
- Running processes
- Installed software
- User accounts
- Uptime
- System location
- Contact information
- Routing tables
- ARP tables

---

## Key Takeaways

- SNMP is for monitoring and managing network devices
- Versions 1 and 2c are insecure (no encryption)
- Community strings are like passwords
- "public" is read-only, "private" is read-write
- SNMP runs on UDP port 161
- MIB defines what data is available
- OIDs are the actual data addresses
- SNMP can reveal massive amounts of system info
- Misconfigured SNMP is a goldmine for attackers
- Always check for SNMP during enumeration
