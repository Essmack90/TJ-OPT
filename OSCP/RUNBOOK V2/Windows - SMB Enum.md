# Windows - SMB Enum

**Step 25 of 50 · Windows**

*List SMB shares and determine whether anonymous or authenticated access exposes files.*

## Run this

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

- [ ] A readable share is exposed → **Browse and download interesting files, then reassess credentials**
- [ ] A writable share is exposed → **Check whether it is a useful upload path, then go to Step 26 · [[Windows - Exploit Search]]**
- [ ] Anonymous access is denied → **Validate credentials or go to Step 26 · [[Windows - Exploit Search]]**
- [ ] No useful share is found → **Go to Step 23 · [[Windows - Web Enum]]**

## Notes

SMB null sessions use no password. Keep downloaded files in `$BoxDir/loot`.

## Gotcha

> [!warning] 💡
> Default administrative shares are not automatically useful to a low-privileged account.

> [!warning]
> Command not yet verified against a real box. Confirm the exact `smbmap` syntax before relying on it in an exam.
