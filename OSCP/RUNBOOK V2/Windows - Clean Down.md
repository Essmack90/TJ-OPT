# Windows - Clean Down

**Step 33 of 50 · Windows**

*Remove uploaded files, payloads, and persistence created during the standalone Windows run.*

## Run this

PowerShell (general):

> **Why:** This command gathers the windows clean down evidence needed to decide which documented route applies next.
```powershell
Remove-Item -Force $PayloadPath
Remove-Item -Force $UploadedPath
Test-Path $PayloadPath
Test-Path $UploadedPath
```

cmd (MarkUp-style — certutil downloads and bat files):

> **Why:** This command gathers the windows clean down evidence needed to decide which documented route applies next.
```cmd
del C:\Users\$Username\payload.bat
del C:\Users\$Username\restore.bat
type C:\Log-Management\job.bat
dir C:\Users\$Username\
```

## Example output

 > *Example shape only: cleanup commands and paths are not yet verified against a real box.*
> **Why:** This command gathers the windows clean down evidence needed to decide which documented route applies next.
```powershell
PS> Test-Path $PayloadPath
False
PS> Test-Path $UploadedPath
False
```
## What did you get?

- [ ] Uploaded files return False from Test-Path → **Continue cleanup**
- [ ] A service or persistence item was created → **Remove it and verify its absence**
- [ ] A system file was modified → **Restore the recorded original and verify it**
- [ ] All verification is clean → **The Windows run is complete**

## Notes

Use only paths recorded during this box.

## Gotcha

> [!warning] 💡
> The cleanup paths are placeholders. Replace them only with files you actually created.

> [!warning]
> Command not yet verified against a real box. Confirm the exact cleanup commands and target paths before relying on them in an exam.
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
