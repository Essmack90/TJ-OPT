# AD - Clean Down

**Step 50 of 50 · AD**

*Remove temporary access and files, restore local settings, and verify the box run is clean.*

## Run this

> **Why:** This version or banner check identifies the exact product release before a matching public exploit is considered.
```cmd
net user $Username2 /delete /domain
```

> **Why:** This version or banner check identifies the exact product release before a matching public exploit is considered.
```bash
bloodyAD -d $Domain -u $Username2 -p $Password2 -H $BoxIP -i $BoxIP remove dcsync $Username2
sudo timedatectl set-ntp true
boxdone
```

## Example output

```

The command completed successfully.
Delegation removed
$ sudo timedatectl set-ntp true
$ boxdone
```
If PowerView or other scripts were uploaded to the target:

> **Why:** This request tests the identified web parameter or endpoint and records the response that proves whether the suspected behavior is present.
```powershell
# Remove PowerView or any uploaded script
Remove-Item -Force C:\Windows\Temp\PowerView.ps1
# Verify removal
Test-Path C:\Windows\Temp\PowerView.ps1
# Should return False
```

Confirm no HTTP 404 on any served payload:

> **Why:** This request tests the identified web parameter or endpoint and records the response that proves whether the suspected behavior is present.
```bash
curl -s -o /dev/null -w "%{http_code}" http://$BoxIP/PowerView.ps1
# Should return 404 if correctly removed from the web server
```

## What did you get?

- [ ] Controlled account and delegation were removed → **Run `netexec ldap $BoxIP -u $Username -p $Password --users` and confirm the temporary account is absent, then continue**
- [ ] Uploaded scripts (PowerView, etc.) are still on the target → **Remove them and verify `Test-Path` returns False**
- [ ] Temporary files were uploaded → **Remove them and verify the target path no longer exists**
- [ ] The clock was changed → **Run `sudo timedatectl set-ntp true`, then reconnect the VPN if needed**
- [ ] Verification is clean → **The run is complete. Go to Step 1 · [[Start Here]] for the next box**

## Notes

Do not delete study loot unless the box procedure requires it. Never include flag values in the write-up.

### Vintage cleanup pattern

When ACL abuse changed several directory objects, restore each one separately. The Vintage run removed `FS01$` from `DelegatedAdmins`, removed `gMSA01$` from `ServiceManagers`, cleared the temporary `svc_sql` SPN, and restored `svc_sql`'s disabled UAC value. It also removed the one-shot task and temporary file and restored `/etc/hosts` from its backup.

```bash
bloodyAD ... remove groupMember DelegatedAdmins 'FS01$'
bloodyAD ... remove groupMember ServiceManagers 'gMSA01$'
bloodyAD ... set object svc_sql servicePrincipalName -v ''
bloodyAD ... set object svc_sql userAccountControl -v 66050
sudo cp -a $BoxDir/notes/hosts.before /etc/hosts
```

## Gotcha

> [!warning] 💡
> Remove delegation before deleting a controlled account when both were created. Record each verification result.
## Seen in
- [[OSCP/BOXES/WRITE UPS/AD/Active|Active]] -- preserved local study loot and cleared the box marker without target-side changes
- [[OSCP/BOXES/WRITE UPS/AD/RockyColt|RockyColt]] -- removed RBCD, deleted exported hives, undeployed the WAR, and verified cleanup
- [[OSCP/BOXES/WRITE UPS/AD/Fermion|Fermion]] -- removed temporary privilege-test payloads, stopped listeners, retained evidence privately, and ran `boxdone`
- [[OSCP/BOXES/WRITE UPS/AD/Vintage|Vintage]] -- restored group membership, SPN/UAC state, scheduled task/file, and `/etc/hosts`

## Related stages

- [[AD - Service Scan]]
- [[AD - Credential Validation]]
- [[AD - BloodHound]]

## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.

## Search evidence

- [[OSCP/BOXES/WRITE UPS/AD/Search|Search]] -- retained local evidence, recorded both hosts-file additions, and explicitly noted that the Tristan password change was not restored in the manual transcript.
