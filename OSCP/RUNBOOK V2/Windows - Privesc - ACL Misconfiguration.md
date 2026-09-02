# Windows - Privesc - ACL Misconfiguration

**Step 28A of 50 · Windows**

*Check inherited folder permissions before using a more complex escalation.*

## Run this

Check the protected file and its parent directory:

> **Why:** This command gathers the windows privesc acl misconfiguration evidence needed to decide which documented route applies next.
```cmd
icacls "C:\\Users\\$AdminUser\\Desktop\\root.txt"
icacls "C:\\Users\\$AdminUser\\Desktop"
```

Look for entries containing (I), (OI), (CI), and (F). These mean inherited, object inherit, container inherit, and full control.

If the current user can change the file ACL, grant access:

> **Why:** This command gathers the windows privesc acl misconfiguration evidence needed to decide which documented route applies next.
```cmd
icacls "C:\\path\\to\\file" /grant $Username:F
type "C:\\path\\to\\file"
```

Revert the temporary entry immediately:

> **Why:** This command gathers the windows privesc acl misconfiguration evidence needed to decide which documented route applies next.
```cmd
icacls "C:\\path\\to\\file" /remove $Username
icacls "C:\\path\\to\\file"
```

## What did you get?

- [ ] The current user has inherited full control on the parent → **Run `icacls $TargetPath /grant $Username:F`, run `type $TargetPath`, then run `icacls $TargetPath /remove $Username` to revert the ACL**
- [ ] The file has no usable entry → **Return to Step 31 · [[Windows - Scheduled Task Abuse]] or Step 30 · [[Windows - Service Abuse]]**
- [ ] Access was granted → **Run `type $TargetPath` to confirm the protected file privately, then run the revert commands above**
- [ ] The original ACL is restored → **Continue to Step 33 · [[Windows - Clean Down]]**

## Notes

Check the parent folder as well as the file. A folder ACE can flow to child objects through inheritance.

## Gotcha

> [!warning] 💡
> Use /remove $Username to undo the temporary entry. Do not use /reset unless you intentionally want to replace the whole DACL.

## External Resources

- [HackTricks: Windows ACL Abuse](https://book.hacktricks.xyz/windows-hardening/windows-local-privilege-escalation#accesschk)
## Seen in
- *(no write-up yet)*

## Related stages

- [[Windows - Service Scan]]
- [[Windows - Web Enum]]
- [[Windows - SMB Enum]]
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
