# Module 5: Report Writing for Penetration Testers

## Tags
#OSCP #Module5 #ReportWriting #NoteTaking #Methodology #Documentation #Obsidian #CherryTree #Screenshots #ExecutiveSummary #TechnicalFindings

---

## **Why This Module Matters**
This module isn't about hacking technique, it's about what happens *after* you hack something. If you can pop every box in the exam but can't write a note or a report that proves it, you don't pass. This is the "boring but mandatory" module, and it's worth taking seriously because report writing is graded in the actual OSCP exam.

**This is the methodology layer every other note in this vault already runs on**, not just theory read once and forgotten. The Application/URL/Request-Type/Issue-Detail/PoC note structure from 5.1.3 is exactly the shape every box writeup in this vault follows (see [[Active]] for a full worked example), and the screenshot discipline from 5.1.5/5.1.6 is why every technique across [[Common Web Application Attacks]], [[Client-Side Attacks]], and the rest carries a `![[Pasted image ...]]` at nearly every meaningful step.

Two learning units:
1. **Understanding Note-Taking** — how to record what you did *while* you're doing it.
2. **Writing Effective Technical Reports** — how to turn those notes into something a client (or exam grader) can act on.

---

## 5.1. Understanding Note-Taking

### **5.1.1. What Do We Actually Deliver to a Client?**

A pentest is messy in real life — you can't script it in advance because you don't know exactly what you'll find until you're in there. So instead of writing the report *before* the test (like a template), you take detailed notes *as you go*, then build the report from those notes afterward.

**Why bother taking such detailed notes?**
- So you (or someone else) can **repeat the test** later to prove an issue is real.
- So you can **repeat the test after a fix** to confirm the issue is actually gone.
- So if something breaks on the client's system during testing, everyone can figure out whether *your* testing caused it.

**Rules of Engagement (RoE)** matter here too — this is the agreement about what you're allowed to do (e.g. "no DoS attacks," "no social engineering"). In red team exercises, someone is sometimes assigned as a "referee" just to make sure everyone sticks to the RoE.

#### Tags: #Deliverables #RulesOfEngagement #RoE #Scope

---

### **5.1.2. Why Your Notes Need to Be Portable**

"Portable" notes = notes someone *else* on your team could pick up and understand, not just notes that make sense to you.

Why this matters:
- If you get sick or pulled off an engagement, someone else needs to be able to continue from your notes.
- On a team, everyone needs to be able to understand everyone else's notes.
- Clear notes are also just faster to turn into a report later.

#### Tags: #NotePortability #TeamWork #Documentation

---

### **5.1.3. How to Structure Your Notes**

There's no single "correct" way to take notes, but here's the core principle: **write down exactly what you did, not a vague summary of what you think you did.**

Practical rules:
- Record **every command typed**, every code change, every GUI click — enough that you (or someone else) could reproduce it exactly.
- If reading your notes later doesn't help you remember *exactly* what happened, they've failed their job.
- Structure top-down: start broad (what are we testing?) and drill down into detail (exact payload used).

**Example note structure for a web vulnerability:**
- **Application Name** — useful when testing multiple apps; also gives you a natural folder structure.
- **URL** — the exact URL where the vulnerability lives.
- **Request Type** — GET/POST/etc., and any manual tampering you did to the request.
- **Issue Detail** — a short explanation of the vulnerability (link a CVE if one exists, describe the impact — DoS, RCE, privesc, etc.).
- **Proof of Concept (PoC) Payload** — the exact code/command that triggers the issue. **This is the most important part** — it's what lets anyone reproduce your finding.

**Worked example — testing for XSS:**
```
Testing for Cross-Site Scripting

Testing Target: 192.168.1.52
Application:    XSSBlog
Date Started:   31 March 2022

1.  Navigated to the application
    http://192.168.1.52/XSSBlog.html
    Result: Blog page displayed as expected

2.  Entered our standard XSS test data:
    You will rejoice to hear that no disaster has accompanied the
    commencement of an enterprise which you have regarded with such
    evil forebodings.<script>alert("Your computer is infected!");</script>
    I arrived here yesterday, and my first task is to assure my dear
    sister of my welfare and increasing confidence in the success of
    my undertaking.

3.  Clicked Submit to post the blog entry.
    Result: Blog entry appeared to save correctly.

4.  Navigated to read the blog post
    http://192.168.1.52/XSSRead.php
    Result: The blog started to display and then the expected alert popped up.

5.  Test indicated the site is vulnerable to XSS.

PoC payload: <script>alert('Your computer is infected!')</script>
```

Notice: **these notes are not the report itself** — they're the raw material you'll build the report from later.

#### Tags: #NoteStructure #XSS #ProofOfConcept #PoC #TopDownApproach

---

### **5.1.4. Choosing a Note-Taking Tool**

What to look for in a tool:
- **Screenshots** — can you insert them inline easily?
- **Code blocks** — properly formatted, ideally with syntax highlighting.
- **Portability** — cross-OS, easy to move to another machine.
- **Directory structure** — useful on multi-target engagements; bonus if the tool manages this for you automatically.

**Three tools the module compares, plus a modern fourth worth knowing about:**

| Tool | Notes |
|---|---|
| **Sublime Text** | Great syntax highlighting for code blocks, but only one language per file, and no inline screenshots. |
| **CherryTree** | Comes standard on Kali. Stores notes in a SQLite DB, tree structure ("nodes"/"subnodes"), exports to HTML/PDF/plain text. |
| **Obsidian** | Markdown-based. Vault = a folder on disk (which is exactly what we're using for this whole OSCP note vault). Supports live markdown preview, inline images, code blocks, plugins, and can export straight to PDF. |
| **[SysReptor](https://github.com/Syslifters/sysreptor)** | Not just note-taking, a full open-source pentest *reporting* platform. Markdown-based content with drag-and-drop evidence, severity scoring, one-click Markdown → PDF via customizable HTML/CSS templates, and direct integration with Burp/Nessus/Nmap/OpenVAS/ZAP output. Free self-hosted, or a hosted cloud version. |

Getting Obsidian running via AppImage (if you ever need to on a fresh box):
```bash
wget https://github.com/obsidianmd/obsidian-releases/releases/download/v0.14.2/Obsidian-0.14.2.AppImage
chmod +x Obsidian-0.14.2.AppImage
./Obsidian-0.14.2.AppImage
```

**SysReptor's specific OSCP relevance:** a companion project, [Syslifters/OffSec-Reporting](https://github.com/Syslifters/OffSec-Reporting), ships ready-made report templates for OSCP/OSCP+/OSWP/OSEP and the rest of the OffSec certification line, built to mirror OffSec's own official report structure, explicitly **"with kind permission by OffSec."** Worth stating precisely rather than overclaiming: that's OffSec sanctioning the *template structure*, not OffSec officially endorsing SysReptor itself as "the" approved tool, still a genuinely strong signal, and a good option if the note-taking-tool-to-final-report handoff (5.1 into 5.2) is the part that feels clunky with a plain markdown vault.

There's no "perfect" tool, pick what fits the engagement and your own workflow.

#### Tags: #NoteTakingTools #Sublime #CherryTree #Obsidian #SysReptor #Markdown #ReportingPlatform

---

### **5.1.5. Taking Good Screenshots**

A screenshot should do the job of a thousand words — but only if it's a *good* screenshot. A bad one buries the important part in noise.

**A good screenshot:**
- Shows **only one concept** at a time.
- Is **legible** (no squinting/zooming required).
- Has a **visual indication it's specific to the client** (e.g. their URL, branding).
- Contains the actual material being described (e.g. the XSS alert box popping up).
- Is properly framed — the important thing isn't shoved off to the side.
- Has a short caption (aim for **8–10 words max**) — the caption just labels the image; extra context goes in surrounding text, not the caption.

**A bad screenshot:**
- Illegible.
- Generic (doesn't show it's this specific client/target).
- Cluttered with irrelevant info.
- Badly framed.

**Rule of thumb:** always support a screenshot with text — don't assume the reader (especially a non-technical one) will understand what an alert box or terminal output actually *means* just by looking at it.

#### Tags: #Screenshots #ReportEvidence #GoodScreenshotVsBad

---

### **5.1.6. Tools for Taking Screenshots**

| OS | Full Screen | Region Select |
|---|---|---|
| Windows | `PrintScreen` | `Win + Shift + S` (Snipping Tool) |
| macOS | `Cmd+Shift+3` | `Cmd+Shift+4` or `Cmd+Shift+5` |
| Linux | `PrintScreen` (saves to `~/Pictures`) | `Shift + PrintScreen` (area select) |

**Flameshot** is worth calling out specifically — it's OS-agnostic, has a CLI and GUI, and lets you annotate (highlight, pixelate, add text) right after capture. Great for pentest screenshots where you want to circle the important bit.

#### Tags: #Flameshot #Screenshots #ScreenshotTools

---

### **5.1. Lab Questions (from the module)**

| Question | Answer |
|---|---|
| A penetration tester and client should agree on what before the engagement starts? | **Scope** |
| Two words ending in "cise" that describe good note structure? | **Concise and precise** |
| Besides app name, URL, issue detail, and PoC payload — what else should notes include? | **Request type** |
| How many concepts should a single screenshot show? | **1** |

#### Tags: #Lab #Quiz #Module5

---

## 5.2. Writing Effective Technical Penetration Testing Reports

### **5.2.1. What's the Report Actually For?**

The report is (usually) **the only deliverable that matters to the client** — not the hacking itself. Finding 20 vulnerabilities is worthless to the business if you can't clearly explain them and how to fix them.

Two things to nail:
1. **The purpose** of the report.
2. **How to communicate** to your actual audience.

**If you find nothing:** don't over-explain your failed attempts in detail — a simple "no vulnerabilities found" is usually enough. Piling on technical noise about things that didn't work can drown out the real findings elsewhere in the report.

**Context matters more than raw severity.** The same technical bug can deserve very different priority depending on the client:
- A **hospital** with an unpatched medical device might genuinely need to keep it running 24/7 — the fix might be "isolate it on its own subnet" rather than "patch immediately."
- A **bank** with the same unpatched device is a much bigger deal — that's a foothold into a financial network, so it likely needs to be a **critical** finding.

Similarly: cleartext HTTP login on the public internet = very bad. Same thing on an internal-only network = still bad, but lower risk since there are more hoops to jump through to exploit it.

**Bottom line:** report useful, accurate, actionable information — without injecting your own bias about how "bad" something *feels*.

#### Tags: #ReportPurpose #ClientContext #RiskVsSeverity

---

### **5.2.2. Write for Your Actual Audience(s)**

Most reports have (at least) two audiences:
1. **Management / executives** — need the big picture and business impact, not deep technical detail.
2. **Technical staff** — need enough detail to actually understand and fix the issues, plus prevention advice for the future.

Solve this by **splitting the report into sections** pitched at each audience (Executive Summary for management, Technical Findings for the engineers).

#### Tags: #Audience #ReportStructure

---

### **5.2.3. The Executive Summary**

This is the **first section** of the report — written for senior management to grasp scope and outcome quickly, and to greenlight remediation work.

**Start with the quick facts:**
```
Executive Summary:

- Scope: https://kali.org/login.php
- Timeframe: Jan 3 - 5, 2022
- OWASP/PCI Testing methodology was used
- Social engineering and DoS testing were not in scope
- No testing accounts were given; testing was black box from an external IP address
- All tests were run from 192.168.1.2
```

This block should cover:
- **Scope** — exactly what was (and wasn't) tested. This also protects you: it proves you did what was agreed, and it's realistic about what fits in the time/budget given.
- **Timeframe** — dates, duration, testing hours.
- **Rules of Engagement** — reference the RoE / referee report; note if DoS or social engineering was allowed; note the methodology followed (e.g. OWASP, PCI).
- **Accounts / infrastructure** — any accounts the client gave you, IPs you tested from, and any accounts *you* created (so the client can confirm they were removed).

**Then write the long-form summary**, roughly in three parts:

**1. Describe the engagement:**
```
"The Client hired OffSec to conduct a penetration test of
their kali.org web application in October of 2025. The test was conducted
from a remote IP between the hours of 9 AM and 5 PM, with no users
provided by the Client."
```

**2. Call out what they did well** (this matters — it softens the blow of the bad news and shows respect for the security team you're actually working with day-to-day):
```
"The application had many forms of hardening in place. First, OffSec
was unable to upload malicious files due to the strong filtering
in place. OffSec was also unable to brute force user accounts
because of the robust lockout policy in place. Finally, the strong
password policy made trivial password attacks unlikely to succeed.
This points to a commendable culture of user account protections."
```
Note the careful wording — **never say "impossible"**. You only tested for a limited time; a flaw might exist that you just didn't find. Absolute claims need absolute evidence you don't have.

**3. Discuss the vulnerabilities found, and look for trends:**
```
"However, there were still areas of concern within the application.
OffSec was able to inject arbitrary JavaScript into the browser of
an unwitting victim that would then be run in the context of that
victim. In conjunction with the username enumeration on the login
field, there seems to be a trend of unsanitized user input compounded
by verbose error messages being returned to the user. This can lead
to some impactful issues, such as password or session stealing. It is
recommended that all input and error messages that are returned to the
user be sanitized and made generic to prevent this class of issue from
cropping up."
```
Grouping similar bugs (e.g. XSS + SQLi + unrestricted file upload = "input isn't being sanitized anywhere") lets you recommend a **systemic** fix (e.g. developer security training) instead of just patching each bug individually.

**4. Close it out:**
```
"These vulnerabilities and their remediations are described in more
detail below. Should any questions arise, OffSec is happy
to provide further advice and remediation help."
```

#### Tags: #ExecutiveSummary #ReportWriting #Trends #Hardening

---

### **5.2.4. Testing Environment Considerations**

A short section, usually right after the Executive Summary, documenting anything that affected the test (delays, missing credentials, scope creep, etc.). Being transparent here protects you and helps the client run a better engagement next time.

**Three example tones:**

**Positive:**
> "There were no limitations or extenuating circumstances in the engagement. The time allocated was sufficient to thoroughly test the environment."

**Neutral:**
> "There were no credentials allocated to the tester in the first two days of the test. However, the attack surface was much smaller than anticipated. Therefore, this did not have an impact on the overall test. OffSec recommends that communication of credentials occurs immediately before the engagement begins for future contracts."

**Negative:**
> "There was not enough time allocated to this engagement to conduct a thorough review of the application, and the scope became much larger than expected. It is recommended that more time is allocated to future engagements."

#### Tags: #TestingConsiderations #Transparency #Limitations

---

### **5.2.5. Technical Summary**

A list of **all key findings**, grouped by common area, written for a technical reader (e.g. a security architect) to skim and understand at a glance what needs fixing.

**Common grouping categories:**
- User and Privilege Management
- Architecture
- Authorization
- Patch Management
- Integrity and Signatures
- Authentication
- Access Control
- Audit, Log Management and Monitoring
- Traffic and Data Encryption
- Security Misconfigurations

**Example entry (Patch Management):**
```
4. Patch Management

Windows and Ubuntu operating systems that are not up to date were
identified. These are shown to be vulnerable to publicly-available
exploits and could result in malicious execution of code, theft
of sensitive information, or cause denial of services which may
impact the infrastructure. Using outdated applications increases the
possibility of an intruder gaining unauthorized access by exploiting
known vulnerabilities. Patch management ought to be improved and
updates should be applied in conjunction with change management.
```

This section should end with a **risk heat map** based on vulnerability severity — ideally adjusted with input from the client's own risk team, not just raw CVSS scores.

#### Tags: #TechnicalSummary #RiskHeatMap #PatchManagement

---

### **5.2.6. Technical Findings and Recommendations**

This is the **meaty, detailed section** — full technical write-up of every finding plus how to fix it. Even though it's "technical," don't assume the reader is a pentester — explain enough that a competent sysadmin/developer who isn't a security specialist can still follow it.

Usually presented as a table:

| Ref | Risk | Issue Description and Implications | Recommendations |
|---|---|---|---|
| 1 | H | Account, Password, and Privilege Management is inadequate — analysis of 122,624 accounts found 722 set to never expire, 23,142 never logged in, 6 in the domain admin group, 968 using default passwords. | Enforce a strict password policy, force weak-password accounts to change, set accounts to expire automatically, remove unneeded accounts. |
| 2 | H | Information enumerated through an anonymous SMB session, later used to gain unauthorized access (see Appendix E.9). | Restrict TCP 139/445 by role, disable SAM account enumeration via Local Security Policy. |
| 3 | M | Reflected XSS — the login form echoes the username back on failure, allowing malicious JS to run in the victim's browser. Can lead to credential/session theft. | Sanitize all user input, encode all user-controlled output, don't reflect the username in login error messages. |

**How to write each finding:**
1. A sentence or two on **what** the vulnerability is and **why it's dangerous**.
2. Enough **technical detail** to explain how it's exploited — assume less background knowledge, not more.
3. **Evidence** it's actually exploitable (inline if short, in an appendix if long).
4. The **specific instance** found in this system/app, backed by your notes and screenshots — walk the reader through it step-by-step. Screenshots should always come with a short explanation, not stand alone.
5. **Remediation advice** that is specific, concrete, and actually implementable — not vague ("harden the server") or so extreme it'll never get approved ("disable all remote logins" in a remote-work environment).

**Rules for good remediation advice:**
- Avoid broad, generic solutions — drill into specifics for this app/business.
- No purely theoretical fixes — must be practically implementable.
- One fix per recommendation — don't bundle multiple steps into a single blob.

For replication steps, always separate:
- **The affected URL/endpoint**
- **How to trigger the vulnerability**

If the same bug shows up in many places, you don't need to list every single instance — give a few examples and note that others exist, then recommend a **systemic** fix.

#### Tags: #TechnicalFindings #Remediation #FindingsTable #Severity

---

### **5.2.7. Appendices, Further Information, and References**

- **Appendices** — anything too long or detailed to sit inline (huge user lists, long PoC code, expanded write-ups). Rule of thumb: if it would break the flow of the page but is still needed, it goes here.
- **Further Information** *(optional)* — supplementary value-adds for the client (deeper articles on the vuln, relevant standards, alternate exploitation methods). Skip this section if you don't have anything worth adding.
- **References** — only cite authoritative sources, and cite them properly.

**Closing takeaways for this whole module:**
- There's no single "best" note-taking or reporting tool — try a few and settle on what works for you/the client.
- Document as you go — with hundreds/thousands of hosts, users, and steps, you cannot rely on memory.
- Always keep the full range of readers in mind (technical and non-technical) and structure the report so each audience gets what they need.

#### Tags: #Appendices #References #FurtherInformation

---

### **5.2. Lab Questions (from the module)**

| Question | Answer |
|---|---|
| Who do we usually write the Penetration Testing Report for? | **All of the above** (Head of Cybersecurity, CIO, SOC Analysts) |
| What section should usually begin a Penetration Testing Report? | **Executive Summary** |
| Missing word: "concrete and _____ implementation" | **Practical** |

#### Tags: #Lab #Quiz #Module5

---

## **Quick Reference Tags for Future Use**
- #NoteTaking #NotePortability #NoteStructure
- #Obsidian #CherryTree #Sublime
- #Screenshots #Flameshot
- #ExecutiveSummary #TechnicalSummary #TechnicalFindings
- #Remediation #RiskVsSeverity #Appendices
- #ReportWriting #Methodology #OSCP #Module5
