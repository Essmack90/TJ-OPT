# Using Web Proxies (HTB Supplementary)

#BurpSuite #ZAP #BurpDecoder #BurpIntruder #ZAPFuzzer #ZAPScanner #ZAPReplacer #FoxyProxy #ProxyingTools #HTBSupplementary

**HTB Using Web Proxies module**. Tier 2, Easy. Covers the full Burp Suite and ZAP toolsets as web proxies. This note documents content NOT already in the vault.

> 🔁 Cross-refs: [[Web Applications#Burp Suite|Web Applications Command Appendix]] (basic Burp setup, Repeater concept, Intruder skeleton), [[Introduction to Web Application Attacks#8.2.4. Security Testing with Burp Suite|8.2.4]] (Burp in the Offsec context), [[Common Web Application Attacks]] (command injection payloads), [[Using the Metasploit Framework (HTB Supplementary)]] (msfconsole usage)

---

## Already in vault — skipped

- Basic Burp proxy setup (127.0.0.1:8080, Intercept toggle, History tab), [[Web Applications#Burp Suite|Web Applications Appendix]]
- Burp Repeater concept (Send to Repeater, edit, Send), [[Web Applications#Burp Suite|Web Applications Appendix]]
- Burp Intruder basics (Clear §, Add §, simple payload list, Start Attack), [[Web Applications#Burp Suite|Web Applications Appendix]]
- Command injection via POST parameters (`;cat /flag.txt` pattern), [[Common Web Application Attacks]]
- msfconsole basics, [[Using the Metasploit Framework (HTB Supplementary)]]

---

## WP.1. FoxyProxy Preset Setup

FoxyProxy is a Firefox extension that lets you define named proxy profiles and switch between them via a toolbar icon. The HTB Pwnbox ships with two profiles pre-configured. On a custom Kali setup, add them manually:

| Profile | Host | Port | Use when |
|---|---|---|---|
| `Burp (8080)` | 127.0.0.1 | 8080 | Running Burp Suite |
| `ZAP (8090)` | 127.0.0.1 | 8090 | Running ZAP |

To add a profile: FoxyProxy icon → Options → Add → fill Host/Port → Save. Switch by clicking the icon and selecting the profile. Set back to "Disable FoxyProxy" when done to restore direct browsing.

> 🔍 Worth remembering generally: switching FoxyProxy to the right profile before starting the tool saves the "why isn't Burp intercepting" confusion. If pages stop loading with a proxy enabled, the tool crashed or Intercept is on without an active listener.

---

## WP.2. Intercepting and Modifying POST Requests

When a web form sends a POST request, Burp/ZAP intercepts the raw body. Modify the parameter value directly.

**Workflow in Burp:**
1. FoxyProxy → `Burp (8080)`, Intercept ON.
2. Submit the form in the browser. The request pauses in Burp's Intercept tab.
3. Modify the POST body parameter value directly in the editor.
4. URL-encode the modified value: highlight it → **Ctrl+U** (Burp's inline URL-encode shortcut).
5. Click **Forward** to send the modified request.

**Ctrl+U shortcut result:**
```
# Before:  ip=;cat flag.txt
# After:   ip=%3bcat+flag.txt
# ; → %3b, space → +
```

> 🔧 Technique: `Ctrl+U` encodes the currently highlighted text in-place. Use it to encode any special characters in parameter values that would otherwise be misinterpreted by the server (`; < > & =`). Right-click → URL-encode does the same thing if you forget the shortcut.

> 📸 Screenshot: Burp Intercept tab showing modified POST body with URL-encoded command injection payload, then response with flag

---

## WP.3. Burp Decoder — Multi-Round Decode Chain

Burp Decoder handles successive encoding layers. The workflow for a string encoded multiple times:

**Access:** Decoder tab (or right-click any value anywhere in Burp → Send to Decoder).

**Multi-round base64 decode:**
1. Paste the string into Decoder.
2. Click **Decode as → Base64**. The decoded output appears below.
3. If the result looks like another encoded string (still base64 characters, still ends in `=`), click **Decode as → Base64** again on the decoded output.
4. Repeat until the output changes format (e.g. becomes URL-encoded or plaintext).
5. If the final round is URL-encoded, click **Decode as → URL**.

```
Encoded string (ends in =) → Base64 → still base64? → Base64 again (x4)
→ URL-encoded string → URL Decode → HTB{3nc0d1n6_n1nj4}
```

In this module's exercise: 4 rounds of base64 then 1 URL decode.

> 🔍 Worth remembering generally: stacked encoding is common in obfuscated cookies and exfiltrated data. The giveaways are: base64 ends in `=` or `==`, URL encoding shows `%XX` characters, hex looks like `4854427b...`. Work through one layer at a time. Burp Decoder keeps the full chain visible so you can trace back if you decode one step too many.

> 📸 Screenshot: Burp Decoder showing 4-layer base64 decode chain with URL decode step at end

---

## WP.4. Proxying Tools Through Burp/ZAP

Any tool that supports an HTTP proxy can route traffic through Burp for inspection. Useful for understanding exactly what a tool sends before manually crafting the same request.

### Metasploit `PROXIES` option

```bash
msfconsole -q
use auxiliary/scanner/http/http_put      # or any scanner/auxiliary

set PROXIES HTTP:127.0.0.1:8080         # format: PROTOCOL:HOST:PORT
set RHOSTS <target_ip>
set RPORT 443
run
# MSF's traffic now flows through Burp — view/intercept it in Proxy tab
```

The same `PROXIES` syntax works for any MSF module with network output. ZAP equivalent: `PROXIES HTTP:127.0.0.1:8090`.

### curl

```bash
# Route a single curl request through Burp
curl http://<target> --proxy http://127.0.0.1:8080

# For HTTPS (ignore cert warning since Burp MITM)
curl https://<target> --proxy http://127.0.0.1:8080 -k
```

### Other tools

```bash
# Any tool supporting HTTP_PROXY / HTTPS_PROXY environment variables
export HTTP_PROXY="http://127.0.0.1:8080"
export HTTPS_PROXY="http://127.0.0.1:8080"
tool_command ...
unset HTTP_PROXY HTTPS_PROXY    # clean up after
```

> 🔍 Worth remembering generally: routing a tool through Burp is the quickest way to reverse-engineer what requests it actually sends. In this module, routing `coldfusion_locale_traversal` through Burp revealed the `/CFIDE/` path in the request, which answered the question without needing the scanner to work successfully.

---

## WP.5. Burp Intruder — Payload Processing Pipeline

The basic Intruder (payload list → fuzz) is in [[Web Applications#Burp Suite|the Command Appendix]]. This is the advanced pattern: combining a prefix + encoding steps so each payload gets transformed before it's sent.

**Use case:** the target cookie is `base64(ascii_hex(md5_hash))`. You want to fuzz the last character of an MD5 hash, but each candidate must be prefixed with the known partial hash, then encoded in that stack before sending.

### Setup

1. Capture the request → Intruder → Positions tab.
2. Clear all § markers. Place the § around the **single character being fuzzed** (just the unknown character, not the whole cookie).
3. Payloads tab → load the wordlist (`alphanum-case.txt` from SecLists/Fuzzing/).
4. Under **Payload Processing** → Add → for each step in order:

| Step | Rule type | Value |
|---|---|---|
| 1 | Add prefix | `3dac93b8cd250aa8c1a36fffc79a17a` (the partial hash) |
| 2 | Encode: Base64-encode | (no value needed) |
| 3 | Encode: Encode as ASCII hex | (no value needed) |

5. Start Attack. Each payload `X` becomes: prefix + `X` → base64 → hex → sent as cookie value.

> 🔧 Technique: the order of Payload Processing rules matters. They run top-to-bottom. "Add prefix" first (builds the full hash string), then encode in the same order the original encoding was applied. To figure out the encoding order: work backwards from what you can see in the cookie, decode it layer by layer (as in WP.3) and note the sequence, then reverse it for encoding.

> 📸 Screenshot: Intruder Payload Processing tab showing prefix + Base64 + ASCII hex rules in order; attack results sorted by response length with the winning request highlighted

---

## WP.6. ZAP Fuzzer — With Payload Processors

ZAP's fuzzer works like Burp Intruder but with one key extra: **Processors** let you transform each payload before it's sent (hash, encode, add prefix/suffix).

**Workflow for MD5 cookie fuzzing:**

1. Capture a request in ZAP's history → right-click → **Attack → Fuzz**.
2. In the request body/header, select the value to fuzz → click **Add**.
3. In the Payloads dialog: Type = **File** → Select → load `top-usernames-shortlist.txt`.
4. Click **Processors** → Add → Type = **MD5 Hash** → Add → OK.
5. The fuzzer will take each username, hash it with MD5, then send the hash as the cookie value.
6. Click **Start Fuzzer**.
7. Sort results by **Size Resp. Body** (or Response size). The outlier size contains the flag.

> 🔍 Worth remembering generally: the MD5 Hash processor is useful any time a cookie or token is `md5(input)` and you're brute-forcing the input. ZAP handles the hash generation automatically per candidate, no pre-hashing the wordlist needed.

> 📸 Screenshot: ZAP Fuzzer Processors dialog showing MD5 Hash type selected; results table sorted by body size with the hit row selected

---

## WP.7. ZAP Scanner — Spider + Active Scan + Alerts

ZAP has a built-in vulnerability scanner (Active Scan) and a crawler (Spider). Together they can identify high-severity vulnerabilities automatically.

**Workflow:**

```
1. Capture at least one request to the target in ZAP history (browse to it once)
2. Right-click the site/request → Attack → Spider
   → Keep defaults → Start Scan
   → Wait for Spider to finish crawling all discovered URLs

3. Right-click the site folder → Attack → Active Scan
   → Keep defaults → Start Scan
   → Watch the "High" column in the Alerts tab — stop when you see ≥1 High alert

4. Click the Alerts tab → expand "High" → click the alert type
   → Right-click the matching request → Open/Resend with Request Editor...
   → Examine the payload ZAP used; modify it for your goal → Send
```

**Alert severity levels:**

| Level | Meaning |
|---|---|
| High | Actively exploitable (SQLi, RCE, path traversal, command injection) |
| Medium | Likely exploitable (CSRF, clickjacking, header injection) |
| Low | Possible weakness (info disclosure, missing headers) |
| Informational | Not a vulnerability, just notable |

In this module: Active Scan found **Remote OS Command Injection** (High). The original ZAP payload read `/etc/passwd`. Modifying it to `;cat%20/flag.txt` in the Request Editor and clicking Send returned the flag.

> 🔧 Technique: you don't need to wait for the full Active Scan to finish. Watch the High column. The moment it shows ≥1, check Alerts and work the finding. Full scans on real targets can take hours.

> 📸 Screenshot: ZAP Alerts tab showing Remote OS Command Injection at High severity; Request Editor with modified payload returning flag

---

## WP.8. ZAP Replacer — Client-Side Restriction Bypass

ZAP Replacer auto-modifies requests or responses as they pass through the proxy. The key use case here: removing a `disabled` attribute from a button in the server's HTML response, so the browser renders it as clickable without you needing to edit the source manually every page load.

**Workflow:**

1. Open ZAP Replacer: **Ctrl+R** (or Tools → Replacer).
2. Click **Add...** and configure:

| Field | Value |
|---|---|
| Match Type | **Response Body String** |
| Match String | `disabled>` |
| Replacement String | `>` |
| Enable | Checked |

3. Click **Save**.
4. Now browse to the page. ZAP intercepts every response and strips `disabled` before Firefox receives the HTML.
5. The button is clickable. Click it (may need Ctrl+Shift+R force-refresh to clear cache).

> 🔍 Worth remembering generally: Replacer is useful for any client-side restriction enforced in HTML/JS that a proxy can remove in transit: `disabled`, `readonly`, `hidden`, `maxlength`, `type="hidden"`, JS validation functions. It's persistent across page loads (unlike manually editing the DOM), so you only set it once per session.

> 🔧 Technique: match just `disabled>` (with the closing `>`) rather than `disabled` alone to avoid accidentally stripping the word "disabled" from text content or other attributes that legitimately contain it.

> 📸 Screenshot: ZAP Replacer dialog with the disabled> → > rule; browser showing the now-clickable button; flag response after clicking

---

## WP.9. Skills Assessment — Techniques Summary

### SA Q1: Disabled button bypass
ZAP Replacer rule: Match = `disabled>` / Replace = `>` / Response Body String. After rule is active, use ZAP Request Editor (Open/Resend) to load a fresh copy of the page, then right-click response → Open URL in System Browser. The rendered page has the button active.

### SA Q2: Multi-layer cookie decode
Cookie arrived as: `ascii_hex_string`. Decode order: ASCII Hex Decode → reveals base64. Base64 Decode → 31-character partial MD5 hash `3dac93b8cd250aa8c1a36fffc79a17a`.

### SA Q3: Fuzz missing last character of MD5 hash
Burp Intruder Payload Processing pipeline (exact order):
1. Add prefix: `3dac93b8cd250aa8c1a36fffc79a17a` (the partial hash)
2. Encode: Base64-encode
3. Encode: ASCII hex

Wordlist: `/opt/useful/SecLists/Fuzzing/alphanum-case.txt`. The hit response is identifiable by a different response size (1248 bytes in the walkthrough). Flag in response body.

### SA Q4: Identify MSF module's target path
Route `auxiliary/scanner/http/coldfusion_locale_traversal` through Burp (`PROXIES HTTP:127.0.0.1:8080`), run it, intercept the request in Burp. The path `/CFIDE/administrator/..` is visible in the GET request line. Answer: **CFIDE**.

---

## WP.10. All Section Q&A Answers

| Section | Q | Answer |
|---|---|---|
| Intercepting Web Requests | Modified POST command injection flag? | **HTB{1n73rc3p73d_1n_7h3_m1ddl3}** |
| Repeating Requests | Flag at /flag.txt via Repeater? | **HTB{qu1ckly_r3p3471n6_r3qu3575}** |
| Encoding/Decoding | Multi-round decode flag? | **HTB{3nc0d1n6_n1nj4}** |
| Proxying Tools | Last line in the MSF request via Burp? | **msf test file** |
| Burp Intruder | Flag from /admin/ .html fuzz? | **HTB{burp_1n7rud3r_fuzz3r!}** |
| ZAP Fuzzer | Flag from MD5 cookie fuzz? | **HTB{fuzz1n6_my_f1r57_c00k13}** |
| ZAP Scanner | Flag via Active Scan RCE? | **HTB{5c4nn3r5_f1nd_vuln5_w3_m155}** |
| Skills Assessment Q1 | Flag from disabled button bypass? | **HTB{d154bl3d_bu770n5_w0n7_570p_m3}** |
| Skills Assessment Q2 | 31-char decoded cookie value? | **3dac93b8cd250aa8c1a36fffc79a17a** |
| Skills Assessment Q3 | Flag from MD5 fuzz with encoding pipeline? | **HTB{burp_1n7rud3r_n1nj4!}** |
| Skills Assessment Q4 | ColdFusion directory in MSF request? | **CFIDE** |

---

## Outstanding Sections

- [x] WP.1 FoxyProxy preset setup
- [x] WP.2 Intercepting and modifying POST requests (Ctrl+U URL-encode shortcut)
- [x] WP.3 Burp Decoder multi-round decode chain
- [x] WP.4 Proxying tools through Burp (MSF PROXIES option, curl, env vars)
- [x] WP.5 Burp Intruder payload processing pipeline (prefix + Base64 + ASCII hex)
- [x] WP.6 ZAP Fuzzer with payload processors (MD5 Hash type)
- [x] WP.7 ZAP Scanner (Spider + Active Scan + Alerts triage)
- [x] WP.8 ZAP Replacer (client-side restriction bypass via response body replacement)
- [x] WP.9 Skills assessment techniques summary
- [x] WP.10 All 11 Q&A answers
- All sections are HTB spawnable targets, no Offsec VM required

---

## Related Boxes

- **[Validation](https://0xdf.gitlab.io/2022/01/22/htb-validation.html)** (HTB, Linux, Easy): SQL injection via intercepted POST parameter. Burp Repeater is the primary tool for developing the payload iteratively, direct application of WP.2.
- **[Poison](https://0xdf.gitlab.io/2018/09/08/htb-poison.html)** (HTB, Linux, Medium): LFI via GET parameter, log poisoning. Burp Repeater for parameter manipulation and ZAP-style request editing.
- **[NodeBlog](https://0xdf.gitlab.io/2022/05/28/htb-nodeblog.html)** (HTB, Linux, Easy): XML injection via POST body. Burp Intercept and Repeater for crafting the XXE payload.
- **[Injection](https://www.hackthebox.com/machines/injection)** (HTB, Linux, Easy): Spring Boot SSTI via POST body. Burp Repeater for iterating payloads without touching the browser form each time.

> 🔍 Worth remembering generally: Burp/ZAP barely appear in OSCP exam boxes as a required tool (the exam tests manual exploitation, not proxy workflows). Their real value in OSCP prep is speed: Repeater lets you iterate on a payload 10x faster than editing a form and clicking Submit each time, and Intruder/ZAP Fuzzer replace manual wordlist loops. Use them as workflow accelerators, not as the technique itself.


---

## HTB Module Quick Reference

Commands formatted for use with the [[Pre-Engagement Kali Setup]] variable block.

```bash
# ============================================================
# BURP SUITE SHORTCUTS
# ============================================================
# CTRL+R           — Send request to Repeater
# CTRL+SHIFT+R     — Go to Repeater tab
# CTRL+I           — Send to Intruder
# CTRL+SHIFT+I     — Go to Intruder tab
# CTRL+U           — URL-encode selected text (payload prep)
# CTRL+SHIFT+U     — URL-decode selected text

# ============================================================
# ZAP SHORTCUTS
# ============================================================
# CTRL+B           — Toggle intercept on/off
# CTRL+R           — Go to Replacer (equivalent to Burp Match & Replace)
# CTRL+E           — Go to Encode/Decode/Hash tool

# ============================================================
# FIREFOX
# ============================================================
# CTRL+SHIFT+R     — Force refresh (bypass browser cache when testing)
```
