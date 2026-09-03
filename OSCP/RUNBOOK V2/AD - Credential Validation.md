# AD - Credential Validation

**Step 40 of 50 · AD**

*Check a recovered credential against the services that can provide the next step.*

## Run this

> **Why:** This authenticated SMB or WinRM check validates the recovered credential and reveals whether the account has the requested access.
```bash
netexec smb $BoxIP -u $Username -p $Password -d $Domain
netexec winrm $BoxIP -u $Username -p $Password -d $Domain
netexec ldap $BoxIP -u $Username -p $Password -d $Domain
```

## Example output

```

SMB  10.10.10.1  445  DC01  [+] htb.local\username:password
WINRM 10.10.10.1  5985 DC01  [+] Pwn3d!
LDAP 10.10.10.1  389  DC01  [+] Authenticated
```
## What did you get?

- [ ] WinRM authentication succeeds → **Go to Step 41 · [[AD - WinRM Foothold]]**
- [ ] LDAP authentication succeeds → **Go to Step 45 · [[AD - BloodHound]]**
- [ ] SMB authentication succeeds only → **Check shares and go to Step 42 · [[AD - Group Triage]]**
- [ ] All services reject the credential → **Run `date -u`, recheck `$Username`, `$Password`, and `$Domain`, then go to Step 35 · [[AD - Clock Sync]]**

## Notes

Use `$Username` and `$Password` rather than putting private credentials into notes.

## Gotcha

> [!warning] 💡
> Test the exact domain context. A valid local account or wrong domain can produce a misleading authentication failure.
## Seen in
- *(no write-up yet)*
- [[OSCP/BOXES/WRITE UPS/AD/Active|Active]] -- validated the recovered service and administrator accounts over SMB

## Related stages

- [[AD - Service Scan]]
- [[AD - Credential Validation]]
- [[AD - BloodHound]]

## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
