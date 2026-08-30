# AD - Anonymous Enum

**Step 36 of 50 · AD**

*Test whether RPC, LDAP, or SMB exposes users or shares without credentials.*

## Run this

```bash
rpcclient -U '' -N $BoxIP -c 'enumdomusers'
ldapsearch -x -H ldap://$BoxIP \
  -b "$(echo $Domain | awk -F. '{for(i=1;i<=NF;i++) printf "DC="$i(i<NF?",":""); print ""}')" \
  '(&(objectCategory=person)(objectClass=user))' sAMAccountName | grep sAMAccountName
smbclient -N -L //$BoxIP
```

## Example output

```

enumdomusers: NT_STATUS_ACCESS_DENIED
# LDAP bind accepted, no user objects
Anonymous login successful for IPC$
```
## What did you get?

- [ ] RPC or LDAP returned users → **Save usernames and go to Step 38 · [[AD - AS-REP Roasting]]**
- [ ] SMB exposed a useful share → **Browse and loot it, then return to the AD path**
- [ ] All three returned nothing useful → **Go to Step 37 · [[AD - Web Enum]]**
- [ ] Anonymous access was denied everywhere → **Go to Step 37 · [[AD - Web Enum]]**

## Notes

RPC and LDAP can return different account lists. Keep both outputs.

## Gotcha

> [!warning] 💡
> Empty anonymous AD enumeration is not a dead end. The website may list the employee names needed to build a roasting list.
