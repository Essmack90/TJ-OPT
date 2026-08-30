# Windows - Privilege Triage

**Step 28 of 50 · Windows**

*Check enabled token privileges for a direct standalone Windows escalation path.*

## Run this

```powershell
whoami /priv
```

## Example output

```

Privilege Name                  State
=============================  ========
SeImpersonatePrivilege         Enabled
SeAssignPrimaryTokenPrivilege  Disabled
...
```
## What did you get?

- [ ] SeImpersonatePrivilege or SeAssignPrimaryTokenPrivilege is enabled → **Go to Step 29 · [[Windows - SeImpersonate Abuse]]**
- [ ] SeBackupPrivilege is enabled → **Follow the Windows backup privilege path**
- [ ] SeDebugPrivilege is enabled → **Follow the Windows process-access path**
- [ ] No useful privilege is enabled → **Run `icacls C:\ /T 2>nul | findstr "(F)" | findstr /i "users"` and go to Step 31 · [[Windows - Scheduled Task Abuse]] if a writable script is found, otherwise go to Step 30 · [[Windows - Service Abuse]]**

## Notes

Only enabled privileges are immediate candidates.

## Gotcha

> [!warning] 💡
> Listed but disabled privileges are not enough on their own.
