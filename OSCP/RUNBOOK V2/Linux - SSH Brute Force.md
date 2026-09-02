# Linux - SSH Brute Force

**Step 3B of 50 · Linux**

*Test a known username against a controlled wordlist, then connect to old SSH servers using only the legacy algorithms they require.*

## When to use this page

Use this page only when you have a username from enumeration and password guessing is in scope. SSH is a remote-login service; a successful password gives an interactive foothold, so keep concurrency low and record failures.

## Password spray

> **Why:** Medusa tests the supplied username and wordlist against SSH with four workers; look for one successful credential and stop the run immediately when it appears.
```bash
medusa -h $BoxIP -u $Username -P $Wordlist -M ssh -t 4
```

> **Why:** Hydra is an alternative SSH tester for modern servers; use it only after Medusa or when the server negotiates modern algorithms normally.
```bash
hydra -l $Username -P $Wordlist ssh://$BoxIP -t 4
```

## Legacy SSH negotiation

Older OpenSSH versions may offer algorithms disabled by modern clients. These flags re-enable only the named RSA host key, Diffie-Hellman key exchange, and MAC algorithms needed for that target.

> **Why:** This command connects with legacy algorithm compatibility enabled; success is a normal SSH prompt, followed immediately by `whoami` and `hostname` checks.
```bash
ssh -oHostKeyAlgorithms=+ssh-rsa \
  -oKexAlgorithms=+diffie-hellman-group1-sha1,diffie-hellman-group14-sha1 \
  -oMACs=+hmac-md5,hmac-sha1 \
  $Username@$BoxIP
```

## Example output

```text
[SUCCESS] Host: $BoxIP User: $Username Password: [redacted]
username@host:~$
```

## What did you get?

- [ ] A password succeeds → **Connect with the matching SSH command, confirm the shell, and go to Step 12 · [[Linux - Shell Stabilise]]**
- [ ] SSH rejects modern negotiation → **Run the legacy SSH command shown in Run this with `-oHostKeyAlgorithms=+ssh-rsa`, then add the other displayed option named by the error**
- [ ] No password succeeds → **Treat this username/wordlist pair as a dead end; return to Step 5 · [[Linux - Web Enum]] or Step 17 · [[Linux - Credential Search]]**
- [ ] The account authenticates but has no shell → **Run `ssh -v $Username@$BoxIP 'id'` to see the login-shell error, then return to Step 5 · [[Linux - Web Enum]] for another service or username**

## Notes

Hydra’s SSH library does not read your OpenSSH configuration. The compatibility flags above apply to the OpenSSH client, while Medusa is often more forgiving with old servers.

## Gotcha

> [!warning] 💡
> Do not spray a password list without a username. Start with names confirmed by `/etc/passwd`, web content, FTP files, or another authorized source, and keep the thread count low on old SSH daemons.

## Additional routing

- [ ] SSH authentication succeeds → **Confirm the shell and go to Step 12 · [[Linux - Shell Stabilise]]**
- [ ] No controlled credential works → **Return to Step 5 · [[Linux - Web Enum]] or Step 17 · [[Linux - Credential Search]]**
## Seen in
- [[OSCP/BOXES/WRITE UPS/Linux/Payday|Payday]] -- confirmed in the box write-up

## Related stages

- [[Linux - Service Scan]]
- [[Linux - Web Enum]]
- [[Linux - Exploit Search]]

## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
