# Windows - SMB Enum

**Step 25 of 50 · Windows**

*List SMB shares and determine whether anonymous or authenticated access exposes files.*

## Run this

> **Why:** This query tests the exposed directory or share interface for accounts, permissions, and readable data that determine the next route.
```bash
smbclient -N -L //$BoxIP
smbmap -H $BoxIP
```

## Example output

 > *Example shape only: the smbmap command is not yet verified against a real box.*
```
Share           Permissions     Comment
-----           -----------     -------
Public          READ            Files
Uploads         READ,WRITE     Drop zone
```
## What did you get?

- [ ] A readable share is exposed → **Run `smbclient //$BoxIP/$Share -U "$Domain/$Username%$Password" -c 'recurse ON; prompt OFF; mget *'`, then inspect the downloaded files for credentials**
- [ ] A writable share is exposed → **Run `smbclient //$BoxIP/$Share -U "$Domain/$Username%$Password" -c 'put $BoxDir/payload.txt'`, then go to Step 26 · [[Windows - Exploit Search]] if the upload succeeds**
- [ ] Anonymous access is denied → **Validate credentials or go to Step 26 · [[Windows - Exploit Search]]**
- [ ] No useful share is found → **Go to Step 23 · [[Windows - Web Enum]]**

## Notes

SMB null sessions use no password. Keep downloaded files in `$BoxDir/loot`.

## Gotcha

> [!warning] 💡
> Default administrative shares are not automatically useful to a low-privileged account.

> [!warning]
> Command not yet verified against a real box. Confirm the exact `smbmap` syntax before relying on it in an exam.

## Authenticated share triage

After recovering a credential, repeat SMB enumeration with authentication. A readable share can contain backups, forensic archives, or memory dumps; download interesting files before attempting exploitation.

> **Why:** These commands authenticate to SMB, list available shares, and recursively list a selected share; look for readable data and names such as `forensic`, `backup`, or dump archives.
```bash
# Use the recovered account and keep downloaded material under private loot.
smbclient -L //$BoxIP -U "$Domain/$Username%$Password"
smbclient //$BoxIP/SHARE -U "$Domain/$Username%$Password" -c 'recurse ON; prompt OFF; ls'
```

> **Why:** This command downloads the selected share recursively for offline triage; inspect filenames and archive metadata before parsing any dump.
```bash
smbclient //$BoxIP/SHARE -U "$Domain/$Username%$Password" -c 'recurse ON; prompt OFF; mget *'
find $BoxDir -type f -printf '%p\n' | grep -Ei 'dmp|zip|bak|config|password|ntds|lsass'
```

## Additional routing

- [ ] A memory dump is found → **Save it in loot and go to Step 44A · [[AD - LSASS Parsing]]**
- [ ] A backup or configuration file contains credentials → **Inspect it privately, validate the credential, and continue to Step 40 · [[AD - Credential Validation]]**
- [ ] The share is readable but empty → **Return to web and directory enumeration rather than repeatedly downloading it**
## Seen in
- [[OSCP/BOXES/WRITE UPS/Windows/Netmon|Netmon]] -- confirmed in the box write-up
- [[OSCP/BOXES/WRITE UPS/AD/Blackfield|Blackfield]] -- confirmed in the box write-up

## Related stages

- [[Windows - Service Scan]]
- [[Windows - Web Enum]]
- [[Windows - SMB Enum]]

## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
