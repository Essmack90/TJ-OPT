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

## Gotcha

> [!warning] 💡
> Group membership may not refresh in an existing session. Reconnect after changing membership before testing the new access.
## Seen in
- [[OSCP/BOXES/WRITE UPS/AD/Return|Return]] -- confirmed in the box write-up

## Related stages

- [[AD - Service Scan]]
- [[AD - Credential Validation]]
- [[AD - BloodHound]]

## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
