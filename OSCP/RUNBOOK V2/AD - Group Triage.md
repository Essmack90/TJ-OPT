# AD - Group Triage

**Step 42 of 50 · AD**

*Decide whether group membership gives a direct path or a controlled delegation path.*

## Run this

> **Why:** This shows the current account’s group memberships so delegated rights such as Backup Operators can be routed to the correct stage.
```powershell
whoami /groups
```

## Example output

```

GROUP INFORMATION
Account Operators
Remote Management Users
Users
...
```
## What did you get?

- [ ] Account Operators is present → **Go to Step 46 · [[AD - Account Operators Abuse]]**
- [ ] Backup Operators or another privileged backup group is present → **Go to Step 43A · [[AD - Backup Operators]]**
- [ ] Domain Admins or an equivalent administrator group is present → **Run `netexec smb $BoxIP -u $Username -p $Password`, confirm `Pwn3d!` or administrator access, then go to Step 49 · [[AD - Pass the Hash]]**
- [ ] No useful group is present → **Go to Step 44 · [[AD - Local Credential Search]]**

## Notes

Account Operators can create domain users and add them to many delegated groups, but it is not Domain Admin.

### Delegated groups and RBCD

If BloodHound shows `GenericWrite` or `AddSelf` over a group, inspect that group's members and downstream `AllowedToAct` relationships. A writable group that is trusted by a computer for RBCD can be the real target: add only the controlled SPN-bearing computer account, verify the membership and `tokenGroups`, then renew its TGT before requesting S4U tickets.

## Gotcha

> [!warning] 💡
> Group membership may not refresh in an existing session. Reconnect after changing membership before testing the new access.
## Seen in
- [[OSCP/BOXES/WRITE UPS/AD/Return|Return]] -- confirmed in the box write-up
- [[OSCP/BOXES/WRITE UPS/AD/Vintage|Vintage]] -- verified `ServiceManagers` and `DelegatedAdmins` membership before renewing tickets and using RBCD

## Related stages

- [[AD - Service Scan]]
- [[AD - Credential Validation]]
- [[AD - BloodHound]]

## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.

## Search evidence

- [[OSCP/BOXES/WRITE UPS/AD/Search|Search]] -- used the Sierra PowerShell Web Access context and ITSec authorization to route to the gMSA read.
