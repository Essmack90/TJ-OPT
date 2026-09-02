# Windows - Privilege Triage

**Step 28 of 50 · Windows**

*Check enabled token privileges for a direct standalone Windows escalation path.*

## Run this

> **Why:** This lists privileges enabled in the current Windows token so a usable local escalation path can be selected instead of guessed.
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
- [ ] SeBackupPrivilege is enabled → **Go to the AD backup path at Step 43A · [[AD - Backup Operators]]**
- [ ] SeDebugPrivilege is enabled → **Run `tasklist /v`, choose an approved privileged process, and go to Step 44A · [[AD - LSASS Parsing]] only if you have an authorized dump**
- [ ] No useful privilege is enabled → **Check inherited ACLs in Step 28A · [[Windows - Privesc - ACL Misconfiguration]], then continue to Step 31 · [[Windows - Scheduled Task Abuse]] or Step 30 · [[Windows - Service Abuse]]**
- [ ] Valid credentials exist but WinRM and RDP are unavailable → **Go to Step 28B · [[Windows - RunasCs]] and run `.\RunasCs.exe $Username2 $Password2 "cmd /c whoami"`**
- [ ] Account is a member of Server Operators → **Go to Step 30 · [[Windows - Service Abuse]] and run its `sc.exe config`, `sc.exe start`, and restore commands in order**

If `SeImpersonatePrivilege` is enabled and the first potato tool does not work, try GodPotato:

> **Why:** This command gathers the windows privilege triage evidence needed to decide which documented route applies next.
```powershell
.\GodPotato.exe -cmd "cmd /c whoami"
```

The command should return `nt authority\\system` before moving to SYSTEM-only collection.

## Notes

Only enabled privileges are immediate candidates.

## Gotcha

> [!warning] 💡
> Listed but disabled privileges are not enough on their own.

## External Resources

- [RunasCs](https://github.com/antonioCoco/RunasCs)
- [GodPotato](https://github.com/BeichenDream/GodPotato)
## Seen in
- *(no write-up yet)*

## Related stages

- [[Windows - Service Scan]]
- [[Windows - Web Enum]]
- [[Windows - SMB Enum]]
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
