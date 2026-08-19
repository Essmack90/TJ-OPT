# OSCP Habits — Screenshot & Loot

*The discipline that separates a clean report from a scramble at the end.*

---

## Pre-Engagement Setup

Before touching the target, export your standard variables:

```bash
export BoxIP="<target IP>"
export BoxName="<hostname>"
export Domain=""          # AD domain FQDN — leave blank if not AD
export DCip=""            # DC IP — leave blank if not AD
export Username=""        # update as you find creds
export Password=""
export Username2=""
export Password2=""
export Username3=""
export Password3=""
export Hash=""            # full NTLM hash — for PtH
export Port="4444"
export Port2="4445"
export WebPort="80"
export URL=""             # e.g. http://$BoxIP

# Run these two separately (not in a pasted block — causes zsh parse errors)
export LocalIP=$(ip a show tun0 | grep "inet " | awk '{print $2}' | cut -d/ -f1)
echo $LocalIP

export Wordlist="/usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt"
```

> 📸 **Screenshot: terminal with all exports confirmed** — do this at the very start of every session

Create a working directory:

```bash
mkdir -p ~/boxes/$BoxName/{nmap,loot,exploits,screenshots}
cd ~/boxes/$BoxName
```

---

## Screenshot Checklist

Screenshot every one of these moments **before moving on**. Name them descriptively — not `screenshot1.png`.

| Moment | What to capture | Example filename |
|--------|----------------|-----------------|
| Initial nmap full port scan | Full terminal output | `nmap-allports.png` |
| Targeted service scan | `-sC -sV` output for key ports | `nmap-services.png` |
| Finding something significant | The discovery in context | `smb-null-session.png` |
| Gaining a foothold | `whoami` + `id` + `hostname` in the shell | `foothold-whoami.png` |
| Reading user flag | `cat local.txt` / `type local.txt` output | `user-flag.png` |
| PrivEsc discovery | The vulnerable thing you found | `privesc-finding.png` |
| PrivEsc execution | The command that elevated you | `privesc-exploit.png` |
| Root / SYSTEM shell | `whoami` → `root` or `nt authority\system` | `root-whoami.png` |
| Reading root flag | `cat proof.txt` / `type proof.txt` output | `root-flag.png` |
| Proof screenshot (OSCP format) | `whoami` + `hostname` + `cat proof.txt` in one terminal | `PROOF-$BoxName.png` |

> 🔧 The OSCP exam proof screenshot needs all three things visible at once: whoami, hostname/ipconfig, and the flag. Practice this habit on every HTB box.

---

## Loot Storage

Store loot **immediately** on finding it. Don't trust your terminal history.

```bash
# Creds found
echo "$Username:$Password" >> ~/boxes/$BoxName/loot/creds.txt

# Hashes found
echo "$Username:$Hash" >> ~/boxes/$BoxName/loot/hashes.txt

# SSH keys
cp id_rsa ~/boxes/$BoxName/loot/
chmod 600 ~/boxes/$BoxName/loot/id_rsa

# Flags
echo "user: <flag value>" >> ~/boxes/$BoxName/loot/flags.txt
echo "root: <flag value>" >> ~/boxes/$BoxName/loot/flags.txt

# Any interesting files (configs, source code, etc.)
cp <file> ~/boxes/$BoxName/loot/
```

---

## During Enumeration — What to Note Down

Keep a running scratch note (`~/boxes/$BoxName/notes.md`) with:
- Open ports and services (copy from nmap output)
- Software versions and anything searchsploit-able
- Usernames found anywhere (files, headers, comments, web pages)
- Passwords found anywhere — even partial ones or hints
- Any internal hostnames or IPs seen
- Any paths that look interesting but you haven't explored yet
- What you tried that didn't work (prevents circling back)

---

## When You Get a Shell — Immediate Checklist

**Linux shell:**
```bash
# 1. Upgrade it first — before doing anything else
python3 -c 'import pty;pty.spawn("/bin/bash")'
# Ctrl+Z
stty raw -echo; fg
export TERM=xterm

# 2. Confirm your identity
whoami && id && hostname && ip a

# 3. Screenshot (foothold-whoami.png)

# 4. Quick orientation
uname -a
cat /etc/os-release
cat /etc/passwd | grep -v nologin
```

**Windows shell:**
```cmd
REM 1. Confirm identity
whoami /all
hostname
ipconfig

REM 2. Screenshot

REM 3. Quick orientation  
systeminfo
net user
net localgroup administrators
```

---

## End of Box — Pre-Report Checklist

Before writing the report, verify you have:
- [ ] All screenshots named and in `~/boxes/$BoxName/screenshots/`
- [ ] All flags recorded in `loot/flags.txt`
- [ ] All creds recorded in `loot/creds.txt`
- [ ] A note of every *exploit/technique* used (not every command — just the winning moves)
- [ ] The OSCP proof screenshot (whoami + hostname + flag, all in one frame)
- [ ] The attack path clear in your head: how did you get from "open ports" to "root"?

Then copy [[Box Report Template]] and fill it in while it's fresh.

---

## Module Cross-Reference

When you hit a technique on a box, these modules have the detail:

| Area | Module |
|------|--------|
| Recon / enumeration | [[Information Gathering]], [[Vulnerability Scanning]] |
| Web app attacks | [[Introduction to Web Application Attacks]], [[Common Web Application Attacks]] |
| SQLi | [[SQL Injection Attacks]] |
| File/client attacks | [[Client-Side Attacks]] |
| Public exploits | [[Locating Public Exploits]], [[Fixing Exploits]] |
| AV evasion | [[Antivirus Evasion]] |
| Passwords / hashes | [[Password Attacks]] |
| Linux privesc | [[Linux Privilege Escalation]] |
| Windows privesc | [[Windows Privilege Escalation]] |
| Pivoting | [[Port Redirection and SSH Tunneling]], [[Tunneling Through Deep Packet Inspection]] |
| Active Directory | [[Active Directory Introduction and Enumeration]], [[Attacking Active Directory Authentication]], [[Lateral Movement in Active Directory]] |
