# How to Read Output

**Universal companion for RUNBOOK V2**

*Use this page whenever a command returns more information than you know how to interpret. The goal is to turn output into one of three decisions: confirm the branch, gather one missing fact, or move on.*

## The output loop

After every command, answer these questions in order:

1. **What did the command prove?** Separate a confirmed fact from a suggestion. `22/tcp open ssh` proves a reachable SSH service; it does not prove valid credentials.
2. **What exact value do I need next?** Usually this is a port, product/version, hostname, username, file path, permission, or response code. Save it in the matching runbook variable or loot file.
3. **What would make this branch valid?** Look for the success clue described on the current page, such as a version match, `uid=`, an authenticated redirect, a writable root-run file, or a successful ticket.
4. **What is the next cheapest test?** Prefer one confirming request or local check over a larger scanner or exploit attempt.
5. **What result closes the branch?** A negative result is useful when it tells you which adjacent stage to open next.

> [!tip] Beginner rule
> Do not try to understand every line. Mark the lines that change your next action. Everything else is context until a later branch needs it.

## Three kinds of output

| Output type | Meaning | Next move |
|---|---|---|
| Positive proof | The suspected service, behavior, identity, or permission is confirmed | Save the output, set the variable, and open the linked technique page |
| Useful clue | The branch is plausible but one fact is missing | Run the smallest follow-up command that confirms the fact |
| Negative or failure result | This test did not prove the branch | Read the failure message, fix only that issue, or choose the next routing row |

Do not treat an empty result as “nothing exists” until you know the command could see the object. Permission errors, wrong hostnames, a missing virtual host, filtered UDP, and an unstable service all produce misleading empty results.

## Port and Nmap output

Example:

```text
22/tcp   open     ssh       OpenSSH 8.2p1
53/tcp   open     domain    ISC BIND 9.10
80/tcp   open     http      Apache httpd 2.4.41
443/tcp  filtered https
```

Focus on:

- `open` versus `filtered`: open means the service answered; filtered means the probe was blocked or inconclusive.
- The exact port number: set `$WebPort`, `$SSHPort`, or another variable instead of assuming the default.
- Product and version: copy the exact banner into [[Linux - Exploit Search]] or the matching Windows/AD service page.
- Script output below a port: hostnames, titles, authentication modes, clock skew, and share information often route the next stage.

Move next:

- Web port -> [[Linux - Web Enum]] or [[Windows - Web Enum]] after reading the banner.
- DNS without the full AD set -> run `dig` and AXFR checks, then [[Web - Virtual Host Enumeration]].
- AD service combination -> [[AD - Service Scan]], then [[AD - Clock Sync]].
- Unknown service -> save the port and check for a downloadable client or binary before repeated probing.
- Only `filtered` results -> verify VPN/routing and UDP separately; do not call the host closed.

## HTTP output

Example:

```text
HTTP/1.1 302 Found
Server: Apache/2.4.41
Location: /login.php
Set-Cookie: PHPSESSID=REDACTED
```

Focus on:

- `200`: content is reachable. Read the body and source for forms, comments, version strings, parameters, and links.
- `301` or `302`: follow the `Location` value. A redirect often reveals the real application path or hostname.
- `401`: the path exists and requires authentication. Record the realm and test only already-validated credentials.
- `403`: the path exists but access is denied. Keep it in the wordlist and look for an alternate method, extension, or virtual host.
- `404`: the tested path was not found. Compare the response size and title with a known missing page before trusting a scanner result.
- `500`: the request reached application code. Read the response carefully for a parameter name, stack trace, or parser boundary, then send a harmless request before testing injection.

Move next:

- Login form -> identify field names and response differences, then [[Linux - SQLi]] or credential validation as appropriate.
- Upload form -> [[Linux - File Upload]] or the matching Windows upload page.
- Parameter that reads a file -> [[Linux - LFI]].
- Parameter that performs a diagnostic action or reflects shell syntax -> [[Linux - Command Injection]].
- Product/version header -> [[Linux - Exploit Search]] or the matching Windows web technique.
- Hostname-dependent content -> [[Web - Virtual Host Enumeration]].

## DNS and virtual-host output

Example:

```text
;; ANSWER SECTION:
example.test.  86400  IN  A  10.10.10.10

admin.example.test.  86400  IN  A  10.10.10.10
```

Focus on:

- The zone name and any names returned by normal queries.
- Names that point to the same target but may select a different web application.
- AXFR success versus refusal. A refused transfer is still useful because the DNS service is present; a successful transfer is a direct hostname list.
- Whether the application responds differently when the hostname is sent in the `Host` header.

Move next:

```bash
dig @$BoxIP "$Domain"
dig axfr "$Domain" @$BoxIP | tee "$BoxDir/loot/dns-axfr.txt"
curl --resolve "$Name:$WebPort:$BoxIP" "http://$Name:$WebPort/"
```

Set `$Domain` only after the output identifies it. For each interesting hostname, use [[Web - Virtual Host Enumeration]] and then return to the normal web branch.

## Web discovery output

Example:

```text
200  GET  /login.php
301  GET  /admin  -> /admin/
403  GET  /backup/
```

Focus on status, path, redirect, response size, and extensions. A single `200` login page is often more valuable than dozens of generic directories. A `403` backup directory is still a confirmed application boundary.

Move next:

- Save promising responses with `curl` before changing the request.
- Read source and forms manually before adding more wordlists.
- Route by behavior, not the directory name: CMS, login, upload, file read, command parameter, source archive, or hostname.
- If all results are generic, compare a known missing page and adjust the scanner before concluding that the web root is empty.

## Shell and identity output

Linux example:

```text
uid=33(www-data) gid=33(www-data) groups=33(www-data)
www-data
cronos
```

Windows example:

```text
nt authority\\local service
HOSTNAME
```

Focus on the account, groups, hostname, integrity level, architecture, and whether the shell is interactive. `id` or `whoami` is the proof of who executed the command, not merely proof that a page responded.

Move next:

- Low-privilege Linux shell -> [[Linux - Shell Stabilise]], then [[Linux - Local Enum]].
- Low-privilege Windows shell -> [[Windows - Shell Received]], then [[Windows - Privilege Triage]].
- Root or SYSTEM already present -> record the proof, collect authorised evidence privately, and go to the relevant clean-down page.
- Shell output is blank or truncated -> stabilize the terminal or use a marker around the command output before trying a callback.

## Local privilege output

Linux examples:

```text
User www-data may run the following commands on host:
    (root) NOPASSWD: /usr/bin/knife

-rwxrwxr-x 1 root devs 420 /opt/scripts/backup.sh
```

Windows example:

```text
BUILTIN\\Users:(F)
NT AUTHORITY\\SYSTEM:(I)(F)
```

Focus on the relationship between **who runs it**, **what is writable**, and **when it executes**. A root-owned file is not automatically useful. A writable file is not automatically useful. The path matters when a privileged service, scheduler, sudo rule, or task consumes it.

Move next:

- Sudo rule -> [[Linux - Sudo Check]].
- SUID or capability -> [[Linux - SUID Check]] or local binary analysis.
- Root cron or timer calls a writable path -> [[Linux - Cron Check]].
- Windows full-control ACE on a service/task file -> [[Windows - Service Abuse]] or [[Windows - Scheduled Task Abuse]].
- `SeImpersonatePrivilege` or a similar token privilege -> [[Windows - SeImpersonate Abuse]].
- Credential or key -> [[Linux - Credential Search]], [[Windows - Credential Search]], or [[AD - Credential Validation]].

## Exploit and callback output

Treat exploit output as a sequence of proofs:

1. The target version and prerequisites match.
2. A harmless command such as `id`, `whoami`, or `hostname` returns expected output.
3. The listener is ready and the callback address is the correct VPN/interface address.
4. The returned shell identity is recorded.
5. The exploit-created artifact is removed or restored.

Example of a real proof:

```text
uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

Example of an incomplete proof:

```text
[+] Exploit sent successfully
```

The second result only proves that the client sent bytes. Go back to the harmless command test before changing payloads.

## Failure output and what it usually means

| Message or symptom | First interpretation | Next move |
|---|---|---|
| Connection refused | Service is down, restarting, or not listening on that port | Wait, confirm the port, reduce scanner concurrency, or reset the lab service |
| Timeout | Filtering, wrong route, or a fragile service | Check VPN route and `nc`, then use a lower-noise probe |
| `401` or `403` | The route exists but access is controlled | Record it and inspect authentication, method, hostname, or permissions |
| Empty command output | Wrong parameter, shell quoting, or output is not returned | prove with markers and `id`; use URL encoding |
| Callback absent but proof command works | Listener, callback address, egress, or payload issue | keep the proven command path and change one callback variable at a time |
| `Permission denied` | Identity or file permission does not satisfy the branch | record owner/group/mode and route to credential or permission enumeration |
| Kerberos name/clock error | FQDN, DNS, or time is wrong | [[AD - Clock Sync]], local name resolution, then retry once |

## Evidence discipline

Save the raw command output first, then create a short note containing the fact that changed your route. Keep credentials, hashes, cookies, private keys, and flags in private loot. Screenshots should show the proof line and enough surrounding context to identify the command, but not sensitive values.

## Final decision before leaving a page

Write one sentence in your notes:

> **This output proves _X_, so I am setting _Y_ and opening _Z_.**

If you cannot complete that sentence, the current result is a clue, not a route. Run the smallest confirming check or return to the current page's failure row.

## Related stages

- [[00 - Follow-Along Controller]]
- [[Start Here]]
- [[Port Triage]]
- [[Linux - Local Enum]]
- [[Windows - Privilege Triage]]
- [[AD - Service Scan]]

## Why this matters for OSCP

The exam rewards a defensible chain from observation to action. Reading output this way prevents both common errors: abandoning a useful path because the output looks unfamiliar, and running an exploit without proving that its prerequisites are present.
