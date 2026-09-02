# Linux - Clean Down

**Step 21 of 50 · Linux**

*Remove payloads and restore any modified target files after the box is complete.*

## Run this

> **Why:** This command gathers the linux clean down evidence needed to decide which documented route applies next.
```bash
rm -f /tmp/linpeas.sh
rm -f $PayloadFile
rm -f $ModifiedFile
cp $BackupFile $ModifiedFile
```

## Example output

 > *Example shape only: cleanup paths must be confirmed for the box.*
```
$ test ! -e /tmp/linpeas.sh && echo removed
removed
$ test ! -e $PayloadFile && echo removed
removed
```
## What did you get?

- [ ] Uploaded files are removed → **Run `find $BoxDir/loot -type f -maxdepth 1 -print` and confirm each recorded remote path is absent, then continue**
- [ ] A file was modified → **Run `cp $BackupFile $TargetFile`, then run `sha256sum $TargetFile $BackupFile` and confirm the hashes match**
- [ ] A listener or server is still running → **Run `pkill -f 'python3 -m http.server|nc -lvnp'`, then run `ss -ltnp` and confirm the port is closed**
- [ ] Verification is clean → **The Linux run is complete**

## Notes

The exact cleanup target must be recorded during the run.

If `/etc/sudoers` was modified (e.g. via DOSBox), restore it from the package cache:

> **Why:** This filter extracts readable evidence from the saved output so likely credentials or configuration clues can be validated.
```bash
# Find the original sudoers in the cached package
dpkg -L sudo | grep sudoers
bsdtar -xOf /var/cache/apt/archives/sudo_*.deb ./etc/sudoers > /etc/sudoers
visudo -c   # verify syntax
```

## Gotcha

> [!warning] 💡
> The commands containing `$PayloadFile`, `$ModifiedFile`, and `$BackupFile` are templates. Replace them only with paths you recorded during the box.

> [!warning] 💡
> If you modified `/etc/sudoers`, always verify the file is syntactically valid after restoring it. A broken sudoers file locks out all sudo access. Run `visudo -c` to check.

> [!warning]
> Command not yet verified against a real box. Confirm the exact cleanup paths before relying on them in an exam.
## Seen in
- *(no write-up yet)*
- [[OSCP/BOXES/WRITE UPS/Linux/Nibbles|Nibbles]] -- removed webshell, SUID helper, and created script tree
- [[OSCP/BOXES/WRITE UPS/Linux/OpenAdmin|OpenAdmin]] -- restored the modified internal PHP page and removed staged key material

## Related stages

- [[Linux - Service Scan]]
- [[Linux - Web Enum]]
- [[Linux - Exploit Search]]

## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
