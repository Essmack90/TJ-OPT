# Windows - Shell Received

**Step 27 of 50 · Windows**

*Identify the Windows account, host, system version, and token integrity after a shell lands.*

## Run this

> **Why:** This lists privileges enabled in the current Windows token so a usable local escalation path can be selected instead of guessed.
```powershell
whoami
hostname
systeminfo
whoami /priv
```

## Example output

```

C:\> whoami
nt authority\local service
C:\> hostname
HOSTNAME
C:\> systeminfo
OS Name: Microsoft Windows Server
...
```
## What did you get?

- [ ] SYSTEM is already returned → **Run `whoami`, run `dir C:\\Users\\$Username\\Desktop`, then go to Step 33 · [[Windows - Clean Down]]**
- [ ] A medium-integrity shell is returned → **Go to Step 28 · [[Windows - Privilege Triage]]**
- [ ] A low-integrity shell is returned → **Go to Step 28 · [[Windows - Privilege Triage]]**
- [ ] The shell is a webshell or service shell → **Run netstat -ano and tasklist /v for loopback-only services before choosing the next exploit**
- [ ] The shell is unstable → **Close the session, reconnect with the same command, run `whoami`, and rerun this page**

## Notes

Run these commands immediately so the shell context is recorded.

## Gotcha

> [!warning] 💡
> Do not confuse the hostname with the current username or privilege level.
## Seen in
- [[OSCP/BOXES/WRITE UPS/Windows/Jerry|Jerry]] -- Windows technique reference
- [[OSCP/BOXES/WRITE UPS/Windows/Chatterbox|Chatterbox]] -- confirmed in the box write-up
- [[OSCP/BOXES/WRITE UPS/Windows/Buff|Buff]] -- webshell and CloudMe Administrator shell

## Related stages

- [[Windows - Service Scan]]
- [[Windows - Web Enum]]
- [[Windows - SMB Enum]]

## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
