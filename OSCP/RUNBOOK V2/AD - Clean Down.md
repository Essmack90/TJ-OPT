# AD - Clean Down

**Step 50 of 50 · AD**

*Remove temporary access and files, restore local settings, and verify the box run is clean.*

## Run this

```cmd
net user $Username2 /delete /domain
```

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

```powershell
# Remove PowerView or any uploaded script
Remove-Item -Force C:\Windows\Temp\PowerView.ps1
# Verify removal
Test-Path C:\Windows\Temp\PowerView.ps1
# Should return False
```

Confirm no HTTP 404 on any served payload:

```bash
curl -s -o /dev/null -w "%{http_code}" http://$BoxIP/PowerView.ps1
# Should return 404 if correctly removed from the web server
```

## What did you get?

- [ ] Controlled account and delegation were removed → **Verify with the relevant NetExec or LDAP check, then continue**
- [ ] Uploaded scripts (PowerView, etc.) are still on the target → **Remove them and verify `Test-Path` returns False**
- [ ] Temporary files were uploaded → **Remove them and verify the target path no longer exists**
- [ ] The clock was changed → **Restore NTP and reconnect the VPN if needed**
- [ ] Verification is clean → **The run is complete. Go to Step 1 · [[Start Here]] for the next box**

## Notes

Do not delete study loot unless the box procedure requires it. Never include flag values in the write-up.

## Gotcha

> [!warning] 💡
> Remove delegation before deleting a controlled account when both were created. Record each verification result.
