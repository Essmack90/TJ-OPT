# AD - WinRM Foothold

**Step 41 of 50 · AD**

*Open the Windows foothold and identify the current account before choosing a privilege path.*

## Run this

> **Why:** This lists privileges enabled in the current Windows token so a usable local escalation path can be selected instead of guessed.
```bash
evil-winrm -i $BoxIP -u $Username -p $Password
```

> **Why:** This lists privileges enabled in the current Windows token so a usable local escalation path can be selected instead of guessed.
```powershell
whoami
hostname
whoami /groups
whoami /priv
```

## Example output

```

*Evil-WinRM* PS C:\Users\username\Documents> whoami
htb\username
*Evil-WinRM* PS C:\Users\username\Documents> whoami /priv
SeChangeNotifyPrivilege       Enabled
...
```
## What did you get?

- [ ] Useful group membership is shown → **Go to Step 42 · [[AD - Group Triage]]**
- [ ] An enabled token privilege is shown → **Go to Step 43 · [[AD - Privilege Triage]]**
- [ ] No useful groups or privileges are shown → **Go to Step 44 · [[AD - Local Credential Search]]**
- [ ] WinRM does not open → **Run `evil-winrm -i $BoxIP -u $Username -p $Password` once more, then return to Step 40 · [[AD - Credential Validation]]**

## Gotcha

> [!warning] 💡
> Do not treat every listed privilege as exploitable. Check that it is enabled and that the current account can use it.
## Seen in
- *(no write-up yet)*

## Related stages

- [[AD - Service Scan]]
- [[AD - Credential Validation]]
- [[AD - BloodHound]]

## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
