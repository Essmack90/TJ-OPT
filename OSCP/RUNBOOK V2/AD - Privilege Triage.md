# AD - Privilege Triage

**Step 43 of 50 · AD**

*Check enabled Windows token privileges for a direct escalation path.*

## Run this

> **Why:** This lists privileges enabled in the current Windows token so a usable local escalation path can be selected instead of guessed.
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

- [ ] SeImpersonatePrivilege is enabled → **Go to Step 29 · [[Windows - SeImpersonate Abuse]] and run the potato-tool check there**
- [ ] SeBackupPrivilege or SeRestorePrivilege is enabled → **Go to Step 43A · [[AD - Backup Operators]]**
- [ ] SeDebugPrivilege is enabled → **Run `tasklist /v`, identify an approved privileged process, and go to Step 44A · [[AD - LSASS Parsing]] if you have an authorized dump**
- [ ] No useful enabled privilege is shown → **Go to Step 44 · [[AD - Local Credential Search]]**

## Notes

Disabled privileges are not an immediate path. Record the exact privilege state before moving on.

## Gotcha

> [!warning] 💡
> Seeing a privilege in the list is not enough. It must be enabled and usable by the current token.
## Seen in
- [[OSCP/BOXES/WRITE UPS/AD/Return|Return]] -- confirmed in the box write-up

## Related stages

- [[AD - Service Scan]]
- [[AD - Credential Validation]]
- [[AD - BloodHound]]

## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
