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

Buff-style webshell, tunnel, and staged proof cleanup:

~~~cmd
del /F /Q C:/Users/Public/shell.exe
del /F /Q C:/Users/Public/chisel.exe
del /F /Q C:/xampp/htdocs/gym/upload/snd.php
del /F /Q C:/xampp/htdocs/gym/upload/kamehameha.php
del /F /Q C:/xampp/htdocs/gym/upload/user-proof.txt
del /F /Q C:/xampp/htdocs/gym/upload/root-proof.txt
taskkill /F /IM chisel.exe
if exist C:/Users/Public/chisel.exe (echo present) else (echo removed)
if exist C:/xampp/htdocs/gym/upload/kamehameha.php (echo present) else (echo removed)
~~~

Devel-style anonymous FTP and IIS cleanup:

```cmd
del /F /Q C:\Users\Public\shell.exe
del /F /Q C:\Users\Public\jp32.exe
del /F /Q C:\inetpub\wwwroot\shell.exe
del /F /Q C:\inetpub\wwwroot\jp32.exe
del /F /Q C:\inetpub\wwwroot\shell.asp
```

Conceal-style anonymous FTP, IIS, and IPSec cleanup:

```bash
curl --ftp-pasv --user anonymous:anonymous \
  --quote "DELE $WebshellPath" "ftp://$BoxIP/"
curl --ftp-pasv --user anonymous:anonymous \
  --quote "DELE $ProofFile" "ftp://$BoxIP/"
curl -sS -o /dev/null -w "%{http_code}\n" \
  "http://$BoxIP/$RemoteWebshellPath"
sudo ipsec stop 2>/dev/null || true

```

# Bastard-style Drupal temporary-directory cleanup in the target cmd shell

~~~cmd
del /F /Q $PotatoPath
del /F /Q $NcPath
dir $RemoteTmp\*.exe
~~~

```bash
curl -s ftp://anonymous:@$BoxIP/
curl -s -o /dev/null -w "%{http_code}\n" http://$BoxIP/$Path
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

> [!warning] 💡
> Cleanup paths are placeholders. Replace them only with payloads, users, services, scheduled tasks, or configuration changes that you recorded creating during this box. Verify each removal from the target before closing the session.
## Seen in
- *(no write-up yet)*
- [[OSCP/BOXES/WRITE UPS/Windows/Buff|Buff]] -- verified removal of webshells, staged binaries, proof copies, and Chisel
- [[OSCP/BOXES/WRITE UPS/Windows/Devel|Devel]] -- verified removal of FTP-uploaded shells and JuicyPotato files
- [[OSCP/BOXES/WRITE UPS/Windows/Conceal|Conceal]] -- recorded removal of FTP-uploaded ASP and proof files plus local IPSec state
- [[OSCP/BOXES/WRITE UPS/Windows/Bastard|Bastard]] -- removed the certutil-staged Netcat and JuicyPotato binaries
- [[OSCP/BOXES/WRITE UPS/AD/RockyColt|RockyColt]] -- undeployed the Tomcat WAR and verified the old application path
- [[OSCP/BOXES/WRITE UPS/AD/Fermion|Fermion]] -- removed GodPotato/PrintSpoofer test files and reverse-shell staging from Srv01
- [[OSCP/BOXES/WRITE UPS/Windows/Love|Love]] -- recorded the PHP probe and MSI staging paths; target-side removal was not present in the supplied transcript

## Related stages

- [[Windows - Service Scan]]
- [[Windows - Web Enum]]
- [[Windows - SMB Enum]]

## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
