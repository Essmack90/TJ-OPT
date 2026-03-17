---
tags: [module/footprinting, ssh, rsync, r-services, remote-access, level/beginner]
---

# Linux Remote Management - Beginner's Guide

## Why Remote Management Matters

Remote management protocols allow administrators to control servers from anywhere. Instead of being physically present, they can:
- Troubleshoot issues remotely
- Transfer files
- Run commands
- Manage multiple servers from one location

For attackers, these services are prime targets. If misconfigured, they can provide quick access.

---

## SSH - Secure Shell

SSH is the most common remote management protocol on Linux. It provides encrypted, secure communication over port TCP 22.

### SSH Authentication Methods

| Method | Description |
|--------|-------------|
| Password | Traditional username/password |
| Public-key | Uses key pairs (more secure) |
| Host-based | Trusts based on hostname |
| Keyboard | Interactive challenge-response |
| GSSAPI | Kerberos-based authentication |

### SSH Versions

| Version | Security | Status |
|---------|----------|--------|
| SSH-1 | Vulnerable to MITM | Deprecated, never use |
| SSH-2 | Secure | Current standard |

---

## SSH Default Configuration

File: `/etc/ssh/sshd_config`

Common default settings:

Include /etc/ssh/sshd_config.d/*.conf
ChallengeResponseAuthentication no
UsePAM yes
X11Forwarding yes
PrintMotd no
AcceptEnv LANG LC_*
Subsystem sftp /usr/lib/openssh/sftp-server

---

## Dangerous SSH Settings

| Setting | Description | Risk |
|---------|-------------|------|
| PasswordAuthentication yes | Allows password login | Can be brute-forced |
| PermitEmptyPasswords yes | Allows empty passwords | Easy access |
| PermitRootLogin yes | Root can log in directly | Full system compromise |
| Protocol 1 | Uses broken SSH-1 | MITM attacks |
| X11Forwarding yes | GUI app forwarding | Potential hijacking |
| AllowTcpForwarding yes | Port forwarding enabled | Pivoting potential |

---

## SSH Key Authentication

### How It Works

1. User generates a key pair (private + public)
2. Public key copied to server (`~/.ssh/authorized_keys`)
3. Private key stays on client (protected by passphrase)
4. Server challenges client to prove they have private key
5. Authentication succeeds without sending password

### Generate SSH Key

ssh-keygen -t rsa -b 4096

### Copy Public Key to Server

ssh-copy-id user@10.129.14.132

---

## Footprinting SSH

### Basic Nmap Scan

nmap -p22 -sV -sC 10.129.14.132

### SSH-Audit Tool

git clone https://github.com/jtesta/ssh-audit.git
cd ssh-audit
./ssh-audit.py 10.129.14.132

This checks:
- SSH version
- Supported algorithms
- Weak ciphers
- Known vulnerabilities

### Verbose SSH Connection

ssh -v user@10.129.14.132

Shows authentication methods available:
debug1: Authentications that can continue: publickey,password,keyboard-interactive

### Force Specific Authentication Method

ssh -v user@10.129.14.132 -o PreferredAuthentications=password

---

## Rsync - Remote File Sync

Rsync is a fast, efficient tool for copying files locally and remotely.

### Default Port

TCP 873

### Key Feature

Delta-transfer algorithm - only sends differences between files, not entire files.

---

## Rsync Enumeration

### Scan for Rsync

nmap -sV -p873 10.129.14.132

### Probe Rsync Service

nc -nv 10.129.14.132 873

(UNKNOWN) [10.129.14.132] 873 (rsync) open
@RSYNCD: 31.0
@RSYNCD: 31.0
#list
dev             Dev Tools
@RSYNCD: EXIT

### List Share Contents

rsync -av --list-only rsync://10.129.14.132/dev

Output:
drwxr-xr-x             48 2022/09/19 09:43:10 .
-rw-r--r--              0 2022/09/19 09:34:50 build.sh
-rw-r--r--              0 2022/09/19 09:36:02 secrets.yaml
drwx------             54 2022/09/19 09:43:10 .ssh

### Download Files

rsync -av rsync://10.129.14.132/dev ./downloaded-files/

### Rsync Over SSH

rsync -av -e ssh user@10.129.14.132:/path/to/files ./local-dir/

---

## R-Services - The Old Way (Insecure)

Before SSH, Unix systems used R-services for remote access. They are HIGHLY insecure and rarely used today, but you may encounter them in legacy environments.

### R-Services Ports

| Service | Port | Protocol | Command |
|---------|------|----------|---------|
| rexec | 512 | TCP | rexec |
| rlogin | 513 | TCP | rlogin |
| rsh | 514 | TCP | rsh, rcp |

### The Problem

All R-services transmit data in PLAIN TEXT - passwords, commands, everything can be sniffed.

---

## R-Services Authentication

R-services use "trusted host" files instead of passwords:

### /etc/hosts.equiv (system-wide)

# <hostname> <username>
pwnbox cry0l1t3
workstation john

### .rhosts (per-user)

htb-student     10.0.17.5
+               10.0.17.10
+               +

The `+` sign is a wildcard - it means "any". This is EXTREMELY dangerous.

---

## Abusing R-Services

### Login with rlogin

rlogin 10.0.17.2 -l htb-student

If trusted, you'll log in without password.

### Execute Remote Command

rsh 10.0.17.2 -l htb-student "whoami"

### Copy Files with rcp

rcp user@10.0.17.2:/etc/passwd ./

---

## R-Services Information Gathering

### rwho - Show Who's Logged In

rwho

root     web01:pts/0 Dec  2 21:34
htb-student     workstn01:tty1  Dec  2 19:57  2:25

### rusers - Detailed User Info

rusers -al 10.0.17.5

htb-student     10.0.17.5:console          Dec 2 19:57     2:25

---

## Key Takeaways

- SSH is the modern, secure standard (port 22)
- Rsync efficiently syncs files (port 873)
- R-services are ancient and insecure (ports 512-514)
- Always check SSH configuration for weak settings
- Rsync shares may be anonymous and leak files
- R-services trust based on hostname/IP - easily spoofed
- SSH public keys are better than passwords
- Never use SSH-1 protocol
- R-services are a relic but still appear in old networks
