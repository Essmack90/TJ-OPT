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

Focus on `whoami`, hostname, integrity level, enabled privileges, architecture, and whether the account is a service identity. `systeminfo` gives context; `whoami /priv` and `whoami /groups` decide the privilege branch. If the shell is not already SYSTEM, open [[Windows - Privilege Triage]] before searching for an exploit.

## What did you get?

- [ ] SYSTEM is already returned → **Run `whoami`, run `dir C:\\Users\\$Username\\Desktop`, then go to Step 33 · [[Windows - Clean Down]]**
- [ ] A medium-integrity shell is returned → **Go to Step 28 · [[Windows - Privilege Triage]]**
- [ ] A low-integrity shell is returned → **Go to Step 28 · [[Windows - Privilege Triage]]**
- [ ] The shell is a webshell or service shell → **Run netstat -ano and tasklist /v for loopback-only services before choosing the next exploit**
- [ ] The shell is unstable → **Close the session, reconnect with the same command, run `whoami`, and rerun this page**

## Bind-shell route

Some legacy Windows exploits open a listening command shell on the target rather than calling back to Kali. Start the exploit, then connect as a client to the exact target-side port.

```bash
nc $BoxIP $Port
```

Run built-in identity and host checks immediately. On older Windows versions, `whoami` may not exist; use `echo %USERNAME%`, `hostname`, `ver`, and a controlled file listing when necessary.

## Crash-based IIS callback route

If the shell payload is delivered through an IIS 6.0 WebDAV overflow, identify the hosting process before deciding that a raw callback failed. The overflow executes in an IIS worker thread inside `w3wp.exe`. A reverse or bind socket created there can disappear when the worker process terminates. `EXITFUNC=thread` does not make the socket independent of the process.

Use a listener and `tcpdump` to distinguish egress failure from process death. If the HTTP response is delayed or returns 500 but no SYN reaches the listener, and a bind payload is reset as well, stop repeating the crash. Use staged delivery with immediate migration to a stable process, then verify `getuid`, `getpid`, `whoami`, `hostname`, and `systeminfo` in the migrated session.

## Notes

Run these commands immediately so the shell context is recorded.

For a callback created by HFS command injection, keep the HFS request, HTTP transfer log, listener port, and returned identity together. Optimum used a clean PowerShell callback as `optimum\\kostas` before local patch triage.

## Gotcha

> [!warning] 💡
> Do not confuse the hostname with the current username or privilege level.
## Seen in
- [[OSCP/BOXES/WRITE UPS/Windows/Jerry|Jerry]] -- Windows technique reference
- [[OSCP/BOXES/WRITE UPS/Windows/Chatterbox|Chatterbox]] -- confirmed in the box write-up
- [[OSCP/BOXES/WRITE UPS/Windows/Buff|Buff]] -- webshell and CloudMe Administrator shell
- [[OSCP/BOXES/WRITE UPS/Windows/Devel|Devel]] -- IIS ASP shell as an application-pool identity
- [[OSCP/BOXES/WRITE UPS/AD/RockyColt|RockyColt]] -- Tomcat WAR callback as ROCK local Administrator
- [[OSCP/BOXES/WRITE UPS/AD/Fermion|Fermion]] -- Jenkins Script Console command execution confirmed as Client01 SYSTEM
- [[OSCP/BOXES/WRITE UPS/Windows/Bastard|Bastard]] -- Drupalgeddon2 command execution and Netcat callback as IUSR
- [[OSCP/BOXES/WRITE UPS/Windows/Love|Love]] -- PHP upload callback as medium-integrity `phoebe`, followed by a separate SYSTEM MSI callback
- [[OSCP/BOXES/WRITE UPS/Windows/Optimum|Optimum]] -- HFS PowerShell callback as `optimum\\kostas`, followed by `systeminfo` and patch-aware escalation
- [[OSCP/BOXES/WRITE UPS/Windows/Legacy|Legacy]] -- MS08-067 opened a target-side bind shell, which was connected with `nc` before legacy identity verification
- [[OSCP/BOXES/WRITE UPS/Windows/Grandpa|Grandpa]] -- raw reverse and bind shells were diagnosed against the IIS worker-process lifetime, then staged Meterpreter migrated before worker termination

## Related stages

- [[Windows - Service Scan]]
- [[Windows - Web Enum]]
- [[Windows - SMB Enum]]

## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
