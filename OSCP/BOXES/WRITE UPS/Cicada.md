# Cicada

- **Box:** Cicada
- **Operating system:** Windows Active Directory
- **Status:** Complete

## Entry vector

Anonymous SMB enumeration exposed a readable HR share. Its notice contained a plaintext password. RID enumeration over the domain produced the user list, and a controlled password spray identified a valid domain account.

## Foothold

LDAP review showed that a second account belonged to both `Backup Operators` and `Remote Management Users`. A credential stored in the development backup script authenticated that account over WinRM.

## Privilege escalation

The foothold had `SeBackupPrivilege`. A VSS shadow copy exposed the protected volume, allowing `NTDS.dit`, `SAM`, and `SYSTEM` to be copied with backup semantics. `secretsdump.py` extracted the Administrator NT hash, which was validated with WinRM pass-the-hash access.

## Cleanup

The temporary hive copies, backup files, VSS metadata, and shadow copy were removed from the target. Local credential, hash, flag, and temporary transfer files were removed; the run log contains only redacted technique evidence.
