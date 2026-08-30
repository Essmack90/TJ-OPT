# AD - Privilege Triage

**Step 43 of 50 · AD**

*Check enabled Windows token privileges for a direct escalation path.*

## Run this

```powershell
whoami /priv
```

## Example output

```

Privilege Name                  State
=============================  ========
SeImpersonatePrivilege         Enabled
SeChangeNotifyPrivilege        Enabled
...
```
## What did you get?

- [ ] SeImpersonatePrivilege is enabled → **Follow the Windows impersonation escalation path**
- [ ] SeBackupPrivilege or SeRestorePrivilege is enabled → **Follow the Windows backup privilege path**
- [ ] SeDebugPrivilege is enabled → **Follow the Windows process-access path**
- [ ] No useful enabled privilege is shown → **Go to Step 44 · [[AD - Local Credential Search]]**

## Notes

Disabled privileges are not an immediate path. Record the exact privilege state before moving on.

## Gotcha

> [!warning] 💡
> Seeing a privilege in the list is not enough. It must be enabled and usable by the current token.
