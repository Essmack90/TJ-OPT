# Windows - Credential Search

**Step 32 of 50 · Windows**

*Search registry values, user directories, and local account stores for reusable credentials.*

## Run this

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

- [ ] Cleartext credentials are found → **Validate them and return to Step 27 · [[Windows - Shell Received]]**
- [ ] A hash or SAM access is found → **Use the matching offline or pass-the-hash path**
- [ ] No useful local credential is found → **Go to Step 33 · [[Windows - Clean Down]] or reassess services**

## Notes

SAM extraction requires administrator access. Keep credentials private.

## Gotcha

> [!warning] 💡
> Registry output can contain cleartext passwords. Redact screenshots and notes.
