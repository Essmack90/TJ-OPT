# Windows Fast Path

Use this page after a Windows shell, WinRM session, or Windows service clue. Capture identity and token privileges first, then test only the privilege or misconfiguration that the output supports.

## Fast loop

### Run this

~~~cmd
whoami /all
hostname
systeminfo
ipconfig /all
netstat -ano
tasklist /v
~~~

~~~powershell
cmdkey /list
Get-CimInstance Win32_Service | Select-Object Name,StartName,State,PathName
schtasks /query /fo LIST /v
~~~

### Example output

~~~text
USER INFORMATION
User Name     $Username
PRIVILEGES INFORMATION
SeImpersonatePrivilege    Enabled
~~~

### What did you get?

- [ ] SeImpersonate or SeAssignPrimaryToken is enabled -> **Open [[OSCP/RUNBOOK V2/Windows - SeImpersonate Abuse|Windows SeImpersonate Abuse]].**
- [ ] Writable service path or service directory -> **Open [[OSCP/RUNBOOK V2/Windows - Service Abuse|Windows Service Abuse]].**
- [ ] Writable scheduled task action -> **Open [[OSCP/RUNBOOK V2/Windows - Scheduled Task Abuse|Windows Scheduled Task Abuse]].**
- [ ] Credential Manager, SAM, LSASS, or configuration evidence -> **Open [[OSCP/RUNBOOK V2/Windows - Credential Search|Windows Credential Search]].**
- [ ] AppLocker blocks the obvious binary -> **Open [[OSCP/RUNBOOK V2/Windows - Privilege Triage|Windows Privilege Triage]].**
- [ ] Domain clues or an AD credential are present -> **Open [[OSCP/EXAM RUNBOOK/05 - Active Directory Fast Path|Active Directory Fast Path]].**
- [ ] SYSTEM is confirmed -> **Open [[OSCP/EXAM RUNBOOK/08 - Evidence and Clean Down|Evidence and Clean Down]].**

### Open next

Validate the exact permission or identity before using a privilege tool. If a direct local branch is not confirmed, move to the AD path rather than guessing.

## 1. Confirm the shell

~~~cmd
whoami /all
hostname
systeminfo
ipconfig /all
route print
netstat -ano
tasklist /v
~~~

## 2. Fast credential and policy search

~~~powershell
cmdkey /list
Get-ChildItem C:\Users,C:\ProgramData,C:\inetpub -Recurse -File -Include *.txt,*.ini,*.cfg,*.config,*.xml,*.log,*.bak,*.rdp,*.kdbx -ErrorAction SilentlyContinue |
  Select-String -Pattern 'password','passwd','secret','token','connectionString'
Get-LocalGroupMember Administrators -ErrorAction SilentlyContinue
~~~

If a credential is recovered, validate it once with NetExec before opening a remote shell:

~~~bash
netexec smb "$BoxIP" -u "$Username" -p "$Password" -d "$Domain"
netexec winrm "$BoxIP" -u "$Username" -p "$Password" -d "$Domain"
evil-winrm -i "$FQDN" -u "$Username" -p "$Password"
~~~

## 3. Fast privilege enumeration

~~~powershell
Get-Process -IncludeUserName -ErrorAction SilentlyContinue | Sort-Object UserName,ProcessName
Get-CimInstance Win32_Service | Select-Object Name,StartName,State,PathName
schtasks /query /fo LIST /v
Get-ChildItem C:\ -Recurse -File -ErrorAction SilentlyContinue |
  Where-Object { $_.FullName -match 'unattend|web.config|backup|password|credential|.kdbx$' }
~~~

Run WinPEAS if the manual output does not expose the path:

~~~powershell
& "$WinPEAS" quiet cmdfast | Tee-Object "$EvidenceFile"
~~~

## Branches

| Output | Fast next action |
|---|---|
| SeImpersonatePrivilege or SeAssignPrimaryTokenPrivilege enabled | Open [[OSCP/RUNBOOK V2/Windows - SeImpersonate Abuse\|Windows - SeImpersonate Abuse]]; test the available Potato family tool |
| Service path or service directory is writable | Confirm with `sc qc $ServiceName` and `icacls $ServicePath`; open [[OSCP/RUNBOOK V2/Windows - Service Abuse\|Windows - Service Abuse]] |
| Scheduled task action is writable | Confirm task, action, trigger, and identity; open [[OSCP/RUNBOOK V2/Windows - Scheduled Task Abuse\|Windows - Scheduled Task Abuse]] |
| ACL grants write or modify rights | Verify with `icacls` or BloodHound, change only the identified object, and open [[OSCP/RUNBOOK V2/Windows - Privesc - ACL Misconfiguration\|Windows - Privesc - ACL Misconfiguration]] |
| AppLocker blocks the obvious binary | Identify allowed paths and use the approved signed-binary route; open [[OSCP/RUNBOOK V2/Windows - Privilege Triage\|Windows - Privilege Triage]] |
| SAM, SYSTEM, SECURITY, LSASS, or Credential Manager evidence appears | Preserve it privately and open [[OSCP/RUNBOOK V2/Windows - Credential Search\|Windows - Credential Search]] |
| No local path, but domain clues exist | Open [[OSCP/EXAM RUNBOOK/05 - Active Directory Fast Path\|Active Directory Fast Path]] |
| SYSTEM proof is confirmed | Capture proof privately, then [[OSCP/EXAM RUNBOOK/08 - Evidence and Clean Down\|Evidence and Clean Down]] |

## Write-up examples

- [[OSCP/BOXES/WRITE UPS/Windows/Love|Love]] -- SSRF, authenticated upload, AppLocker bypass, and MSI SYSTEM execution
- [[OSCP/BOXES/WRITE UPS/Windows/Bastard|Bastard]] -- Drupal RCE, token privilege triage, and impersonation
- [[OSCP/BOXES/WRITE UPS/Windows/Conceal|Conceal]] -- IPSec gate, FTP upload, and JuicyPotato
- [[OSCP/BOXES/WRITE UPS/Windows/MarkUp|MarkUp]] -- XML source disclosure and Windows privilege escalation

## Detailed routes

- [[OSCP/MODULES/17. Windows Privilege Escalation|Module 17 - Windows Privilege Escalation]]
- [[OSCP/DECISION TREE/Windows Privilege Escalation (Decision Tree)|Windows Privilege Escalation Decision Tree]]
- [[OSCP/COMMAND APPENDIX/Windows Privilege Escalation|Windows Privilege Escalation Command Appendix]]
