# Windows - Credential Search

**Step 32 of 50 · Windows**

*Search registry values, user directories, and local account stores for reusable credentials.*

## Run this

> **Why:** These registry queries test both policy locations so a local-installation escalation is accepted only when the required settings are present.
```powershell
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"
cmdkey /list
Get-ChildItem -Force C:\Users
```

## Example output

```

HKEY_LOCAL_MACHINE\...\Winlogon
    DefaultUserName    REG_SZ    username
    DefaultPassword    REG_SZ    [redacted]
Currently stored credentials:
    Target: TERMSRV/host
...
```
## What did you get?

- [ ] Cleartext credentials are found → **Run `netexec smb $BoxIP -u $Username -p $Password` once, then return to Step 27 · [[Windows - Shell Received]] if access succeeds**
- [ ] A hash or SAM access is found → **Save it to `$BoxDir/loot/hash.txt`, run the matching offline hash check, or go to Step 49 · [[AD - Pass the Hash]] for an NT hash**
- [ ] No useful local credential is found → **Go to Step 33 · [[Windows - Clean Down]] or reassess services**

## Notes

SAM extraction requires administrator access. Keep credentials private.

## Gotcha

> [!warning] 💡
> Registry output can contain cleartext passwords. Redact screenshots and notes.

## AlwaysInstallElevated check

Windows can be configured so any user may install an MSI with SYSTEM privileges. Both the per-user (`HKCU`) and machine-wide (`HKLM`) policy values must be `1`; one value alone is not enough.

> **Why:** These registry queries check both policy locations; look for `AlwaysInstallElevated REG_DWORD 0x1` in both outputs.
```cmd
reg query HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
```

## Credential matrix validation

When a password is recovered but its username is uncertain, test one password against each known username with a small, evidence-based matrix. This is credential spraying, meaning one password is tested across multiple accounts to reduce lockout risk; stop when authentication succeeds.

> **Why:** This command tests the recovered password against the known username list over SMB; look for one successful authentication and record only the account name.
```bash
# Keep the username list private and stop on the first valid result.
netexec smb $BoxIP -u $BoxDir/loot/users.txt -p $Password --continue-on-success
```

## Additional routing

- [ ] Both AlwaysInstallElevated values are `1` → **Build or obtain an authorized MSI payload and route to Step 28 · [[Windows - Privilege Triage]]**
- [ ] One or both values are absent/zero → **Treat this path as a dead end and continue scheduled-task, service, or credential checks**
- [ ] The password validates for a username → **Set the matching variables and go to Step 28B · [[Windows - RunasCs]] or Step 27 · [[Windows - Shell Received]]**
## Seen in
- *(no write-up yet)*

## Related stages

- [[Windows - Service Scan]]
- [[Windows - Web Enum]]
- [[Windows - SMB Enum]]

## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
