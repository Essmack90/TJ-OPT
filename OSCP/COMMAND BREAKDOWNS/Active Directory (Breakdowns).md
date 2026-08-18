# Active Directory (Breakdowns)

Teardowns for non-obvious AD commands. Phase-ordered coverage in [[Active Directory Methodology]], syntax in [[Active Directory]], decision logic in [[Active Directory (Decision Tree)]].

---

## ACL Abuse: PSCredential chain for multi-hop privilege escalation

**Full command set:**
```powershell
$passwd = ConvertTo-SecureString "transporter@4" -AsPlainText -Force
$Cred = New-Object System.Management.Automation.PSCredential('INLANEFREIGHT\wley', $passwd)
$newPass = ConvertTo-SecureString 'Pwn3d_by_ACLs!' -AsPlainText -Force
Set-DomainUserPassword -Identity damundsen -AccountPassword $newPass -Credential $Cred -Verbose
```

**Piece by piece:**
- `ConvertTo-SecureString "transporter@4" -AsPlainText -Force` → PowerShell requires passwords in `SecureString` format (encrypted in memory). `-AsPlainText` lets you start from a visible string; `-Force` acknowledges the security risk of having plaintext in the command.
- `New-Object System.Management.Automation.PSCredential('DOMAIN\user', $passwd)` → creates a credential object combining a domain-qualified username with the secure string. PowerView functions accept `-Credential $Cred` to operate in a different user's security context WITHOUT needing an interactive logon. This is how you chain compromised account A → attack account B without starting a new session.
- `Set-DomainUserPassword -Identity damundsen` → PowerView function that calls `net ads password` / ADSI under the hood to reset the named account's password. Requires `User-Force-Change-Password` or `GenericAll` ACE on the target account for the credential used in `-Credential`.
- `-Verbose` → shows the LDAP call being made, useful for confirming the correct DC was contacted.

**Where this comes from:** PowerView source; ACL abuse chain from [[Active Directory Enumeration & Attacks (HTB Supplementary)#AD.10. ACL Abuse Chain|AD.10]]; [[github.com/HackTricks-wiki/hacktricks/blob/master/windows-hardening/active-directory-methodology/acl-persistence-abuse.md|HackTricks ACL persistence]]

**Where to look in the response:** the Verbose output shows `Set-DomainUserPassword ... LDAP://...` followed by `[VERBOSE] Setting password for user damundsen...`. No news is good news: PowerView is silent on success unless you use `-Verbose`. If it throws an error, the ACE is missing or the password doesn't meet complexity requirements.

🔁 **Seen in:** [[Active Directory Enumeration & Attacks (HTB Supplementary)#AD.10. ACL Abuse Chain|AD.10 wley→damundsen→Help Desk Level 1→adunn chain]]

---

## ACL Abuse: Set-DomainObject to register a fake SPN (targeted Kerberoast)

**Full command:**
```powershell
Set-DomainObject -Credential $Cred2 -Identity adunn -SET @{serviceprincipalname='notahacker/LEGIT'} -Verbose
```

**Piece by piece:**
- `Set-DomainObject` → PowerView's generic attribute-setter against an AD object. Can write any non-protected attribute.
- `-Credential $Cred2` → runs the LDAP write as the account stored in `$Cred2`, which has `GenericWrite` on `adunn` (via Help Desk Level 1 group membership).
- `-Identity adunn` → the target account to modify.
- `-SET @{serviceprincipalname='notahacker/LEGIT'}` → PowerShell hashtable syntax for the attribute-value pair. `serviceprincipalname` is the LDAP attribute name; `notahacker/LEGIT` is a fake SPN value (class/hostname format). Any valid SPN string works — the content is irrelevant, just the existence of an SPN makes adunn Kerberoastable.
- The SPN causes the KDC to issue a TGS ticket for adunn encrypted with adunn's NTLM hash. Rubeus requests that ticket and you crack it offline.
- **Cleanup required:** `Set-DomainObject ... -Clear serviceprincipalname` to remove the fake SPN after cracking.

**Where this comes from:** [[Active Directory Enumeration & Attacks (HTB Supplementary)#AD.10. ACL Abuse Chain|AD.10]], [[github.com/HackTricks-wiki/hacktricks/blob/master/windows-hardening/active-directory-methodology/acl-persistence-abuse.md|HackTricks ACL — GenericWrite]]

**Where to look in the response:** `klist` after Rubeus should show a new TGS ticket for the target account. If you get "KRB_AP_ERR_MODIFIED" in Rubeus, the SPN format is wrong or conflicting with a real SPN — try a different class/hostname string.

🔁 **Seen in:** [[Active Directory Enumeration & Attacks (HTB Supplementary)#AD.10. ACL Abuse Chain|AD.10 step 3: Set SPN → targeted Kerberoast]]

---

## ExtraSids Golden Ticket: Rubeus golden with /sids flag

**Full command:**
```cmd
.\Rubeus.exe golden /rc4:9d765b482771505cbe97411065964d5f ^
  /domain:LOGISTICS.INLANEFREIGHT.LOCAL ^
  /sid:S-1-5-21-2806153819-209893948-922872689 ^
  /sids:S-1-5-21-3842939050-3880317879-2865463114-519 ^
  /user:hacker /ptt
```

**Piece by piece:**
- `golden` → Rubeus subcommand for forging a golden ticket (a Kerberos TGT signed with the KRBTGT hash, bypassing normal authentication).
- `/rc4:<hash>` → the KRBTGT account's NTLM hash from the child domain. This is what makes the ticket cryptographically valid: the KDC accepts any ticket signed with this key as legitimate.
- `/domain:CHILD.PARENT.LOCAL` → the child domain's FQDN. The ticket claims to be from this realm.
- `/sid:S-1-5-21-CHILD...` → the child domain's SID. Included in the PAC so the KDC can resolve the user's domain membership.
- `/sids:S-1-5-21-PARENT...-519` → the **ExtraSids** field. This is an additional SID array injected into the ticket's PAC. `519` is the Enterprise Admins RID. WITHIN_FOREST trusts don't strip extra SIDs (SID filtering only applies to cross-forest trusts), so the parent DC honours this injected group membership and treats the ticket holder as an Enterprise Admin.
- `/user:hacker` → the username claimed in the ticket. Arbitrary; doesn't need to exist in AD. The PAC's group memberships (including the injected EA SID) determine access, not the username.
- `/ptt` → Pass The Ticket: load the forged ticket directly into the current session's Kerberos cache. Equivalent to `kerberos::ptt` in mimikatz.

**Where this comes from:** [[Active Directory Enumeration & Attacks (HTB Supplementary)#AD.16. Child→Parent Trust Attack (Windows — ExtraSids)|AD.16]]; [[github.com/HackTricks-wiki/hacktricks/blob/master/windows-hardening/active-directory-methodology/sid-history-injection.md|HackTricks SID History Injection]]

**Where to look in the response:** `klist` immediately after should show the injected ticket. Then `ls \\parentdc.parent.local\c$` confirms access — a successful directory listing means the parent DC accepted the ticket and treated you as Enterprise Admin.

🔁 **Seen in:** [[Active Directory Enumeration & Attacks (HTB Supplementary)#AD.16. Child→Parent Trust Attack (Windows — ExtraSids)|AD.16 ExtraSids → parent DC access → f@ll1ng_l1k3_d0m1no3$]]

---

## dsquery LDAP filter: disabled admins with descriptions

**Full command:**
```cmd
dsquery * -filter "(&(objectCategory=person)(objectClass=user)(userAccountControl:1.2.840.113556.1.4.803:=2)(adminCount>=1)(description=*))" -attr samAccountName description -limit 50
```

**Piece by piece:**
- `dsquery *` → query any object type (not just users, computers, or groups). The wildcard `*` enables custom LDAP filters via `-filter`.
- `-filter "(...)"` → raw LDAP filter syntax. `&(...)` is AND. Each `(attr=value)` is one condition.
- `objectCategory=person` + `objectClass=user` → together these specifically match domain user accounts (not contacts, not computers, not groups).
- `userAccountControl:1.2.840.113556.1.4.803:=2` → the OID `1.2.840.113556.1.4.803` is the LDAP bitwise-AND matching rule. `:=2` means "the UAC attribute with bit 2 set". Bit 2 in the UserAccountControl bitmap is `ACCOUNTDISABLE`. So this clause matches disabled accounts only.
- `adminCount>=1` → filters to accounts that have had `adminCount` set to 1 by the SD Propagator, meaning they were (or are) in a privileged group (Domain Admins, Account Operators, etc). This avoids noise from regular disabled users.
- `description=*` → account has any description value. Sysadmins sometimes leave the old password in this field as a reminder.
- `-attr samAccountName description` → only print these two attributes (no noise).
- `-limit 50` → stop after 50 results.

**Where this comes from:** [[Active Directory Enumeration & Attacks (HTB Supplementary)#AD.8.3. dsquery — LDAP Filter for Disabled Admin Accounts with Descriptions|AD.8.3]]; LDAP filter syntax from RFC 4515

**Where to look in the response:** any account where the description field contains something like "Password123!" or "last changed 2019-03". Disabled admin accounts with memorable descriptions are common in enterprise environments that don't have a formal offboarding process.

🔁 **Seen in:** [[Active Directory Enumeration & Attacks (HTB Supplementary)#AD.8. Living Off the Land|AD.8]] Living Off the Land section — adunn appeared with description → Q answer HTB{LD@P_I$_W1ld}

---

#### Tags: #CommandBreakdowns #ActiveDirectory #ACLAbuse #PSCredential #SetDomainObject #ExtraSids #Rubeus #dsquery #GoldenTicket #HTBSupplementary
