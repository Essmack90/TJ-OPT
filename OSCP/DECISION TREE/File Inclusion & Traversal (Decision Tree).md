# File Inclusion & Traversal, Decision Tree

Part of [[DECISION TREE]]. "I found X, what do I try" for directory traversal, LFI, and RFI.

---

### Found a parameter whose value looks like a filename (`page=`, `file=`, `template=`, `lang=`, `doc=`)
→ This is the classic LFI/traversal shape. Test it:
```
?page=../../../../../../../../../etc/passwd
```
→ Nothing back or 404? Try URL-encoding the dots: `%2e%2e/` (or the asymmetric `.%2e/%2e%2e/...` form if the uniform one doesn't land)
→ See [[Common Web Application Attacks#9.1.2. Identifying and Exploiting Directory Traversals|9.1.2]] and [[Common Web Application Attacks#9.1.3. Encoding Special Characters|9.1.3]]

### Traversal confirmed, target is Linux
→ Read `/etc/passwd`, then hunt disclosed users' home directories for `.ssh/id_rsa`
→ If found, extract it mechanically (never copy/paste by hand, see [[Secrets & Credentials (Decision Tree)|Secrets & Credentials]]) and try SSH
→ See [[Common Web Application Attacks#9.1.2. Identifying and Exploiting Directory Traversals|9.1.2]]

### Traversal confirmed, target is Windows
→ No direct "read passwd, find key" path on Windows. Check IIS-specific locations instead: `C:\inetpub\wwwroot\web.config`, `C:\inetpub\logs\LogFiles\W3SVC1\`
→ Try both `../` and `..\`
→ See the Windows notes in [[Common Web Application Attacks#9.1.2. Identifying and Exploiting Directory Traversals|9.1.2]]

### You have LFI and want code execution, not just file reads
→ Three options depending on what's available:
  1. **Log poisoning**: find a controllable field that lands in a log (User-Agent in `access.log` is the classic one), inject a PHP snippet via that field, then include the log. See [[Common Web Application Attacks#9.2.1. Local File Inclusion (LFI)|9.2.1]]
  2. **`data://` wrapper**: embed the payload directly in the URL, no write step needed, but requires `allow_url_include`. See [[Common Web Application Attacks#9.2.2. PHP Wrappers|9.2.2]]
  3. **RFI**: host a webshell yourself and include it remotely, also requires `allow_url_include`. See [[Common Web Application Attacks#9.2.3. Remote File Inclusion (RFI)|9.2.3]]

### You have LFI and want to read PHP source (not execute it)
→ Use `php://filter/convert.base64-encode/resource=<file>`, then `base64 -d` the response
→ See [[Common Web Application Attacks#9.2.2. PHP Wrappers|9.2.2]]
