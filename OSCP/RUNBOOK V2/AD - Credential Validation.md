# AD - Credential Validation

**Step 40 of 50 · AD**

*Check a recovered credential against the services that can provide the next step.*

## Run this

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
- [ ] All services reject the credential → **Recheck the username, password, domain, and clock, then go to Step 35 · [[AD - Clock Sync]]**

## Notes

Use `$Username` and `$Password` rather than putting private credentials into notes.

## Gotcha

> [!warning] 💡
> Test the exact domain context. A valid local account or wrong domain can produce a misleading authentication failure.
