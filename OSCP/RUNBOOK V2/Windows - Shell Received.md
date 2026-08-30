# Windows - Shell Received

**Step 27 of 50 · Windows**

*Identify the Windows account, host, system version, and token integrity after a shell lands.*

## Run this

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

- [ ] SYSTEM is already returned → **Confirm the flag path, then go to Step 33 · [[Windows - Clean Down]]**
- [ ] A medium-integrity shell is returned → **Go to Step 28 · [[Windows - Privilege Triage]]**
- [ ] A low-integrity shell is returned → **Go to Step 28 · [[Windows - Privilege Triage]]**
- [ ] The shell is unstable → **Reconnect and rerun this page**

## Notes

Run these commands immediately so the shell context is recorded.

## Gotcha

> [!warning] 💡
> Do not confuse the hostname with the current username or privilege level.
