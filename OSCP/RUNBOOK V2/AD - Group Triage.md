# AD - Group Triage

**Step 42 of 50 · AD**

*Decide whether group membership gives a direct path or a controlled delegation path.*

## Run this

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
- [ ] Backup Operators or another privileged backup group is present → **Follow the matching Windows privilege path**
- [ ] Domain Admins or an equivalent administrator group is present → **Validate the account and go to Step 49 · [[AD - Pass the Hash]] or post-exploitation**
- [ ] No useful group is present → **Go to Step 44 · [[AD - Local Credential Search]]**

## Notes

Account Operators can create domain users and add them to many delegated groups, but it is not Domain Admin.

## Gotcha

> [!warning] 💡
> Group membership may not refresh in an existing session. Reconnect after changing membership before testing the new access.
