---
tags: [oscp, planning, study-plan]
created: 2026-08-28
target-exam: March 2027
status: active
---

# OSCP Study Plan — March 2027

> **This is a living document.** Update it as phases complete, milestones shift, or weak areas emerge. Review it at the start of every week.

---

## The honest starting position (August 2026)

**Done:**
- M06-M27 theory complete
- 11 Linux boxes with write-ups
- 1 Windows box (MarkUp)
- Vault structured and gap-filled

**Not done (and will hurt in exam):**
- Most hands-on module labs still pending — especially exploit dev, AD, tunnelling, client-side, password attacks
- AD: theory only, no real practical reps
- Windows PrivEsc: one box is not enough
- Exploit modification: not demonstrated
- Pivoting/tunnelling: documented but not practiced
- Reporting under time pressure: never done
- Timed mock exams: zero

**Exam format reminder:**
- 23h 45m exam time
- 3 standalone machines + 1 three-machine AD set
- 24h reporting window after exam ends
- Open book, internet allowed — but time pressure is real
- AD set is all-or-nothing: partial points only if you get a foothold

---

## Timeline overview

| Phase | Dates | Focus | Duration |
|---|---|---|---|
| 1 | Sep 1 – Sep 28 | Pending labs + foundation completion | 4 weeks |
| 2 | Oct 1 – Oct 28 | Windows depth | 4 weeks |
| 3 | Nov 1 – Dec 14 | Active Directory | 6 weeks |
| 4 | Dec 15 – Jan 18 | Pivoting, client-side, exploit dev | 5 weeks |
| 5 | Jan 19 – Feb 22 | Mock exams + reporting | 5 weeks |
| 6 | Feb 23 – Mar 1 | Final polish, vault validation | 1 week |

---

## Phase 1: Pending Labs + Foundation (Sep 1 – Sep 28)

**Goal:** No more pending module labs. Everything theoretical becomes demonstrated.

**Priority order:**
1. Exploit development labs (buffer overflow — offset, bad chars, EIP control, jump, shellcode, full chain)
2. Password attacks labs (hash cracking, credential stuffing, brute force, spray)
3. Client-side attacks labs (Office macros, malicious docs, library files, shortcut files)
4. Active Directory module labs (any not yet completed)
5. Tunnelling/pivoting labs (SSH forwarding, SOCKS, Chisel, proxychains)
6. Any other outstanding VM labs from M06-M27

**Box targets:** 1-2 Linux boxes per day (Easy/Medium HTB or PG). Keep the momentum going but don't let box hunting replace lab completion. Labs first.

| Week | Dates | Primary Focus | Box Mix | Milestone |
|---|---|---|---|---|
| P1-W1 | Sep 1–7 | Exploit dev labs: crash → offset → bad chars | 2/day, labs first; pool of 8–10 boxes across Linux, Windows, BOF, and AD | Reproduce crash analysis, offset finding, and bad-character testing from notes alone |
| P1-W2 | Sep 8–14 | Exploit dev labs: EIP control → JMP ESP → shellcode → callback | 2/day, labs first; pool of 8–10 boxes across Linux, Windows, BOF, and AD | Deliver a working callback with a complete Windows BOF chain from notes alone |
| P1-W3 | Sep 15–21 | Password attacks and client-side attack labs | 2/day, labs first; pool of 8–10 boxes across Linux, Windows, BOF, and AD | Complete both lab areas and record the exact decision points used |
| P1-W4 | Sep 22–28 | AD module labs and tunnelling labs | 2/day, labs first; pool of 8–10 boxes across Linux, Windows, BOF, and AD | Finish the remaining Phase 1 labs and route through one tunnel successfully |

**Vault action:** After each lab, add the demonstrated commands to the cheatsheet. Fill in TODO markers as they're proven.

---

## Phase 2: Windows Depth (Oct 1 – Oct 28)

**Goal:** Windows PrivEsc stops being a gap. Minimum 15-20 Windows boxes with write-ups.

**Techniques to hit — deliberately, not accidentally:**

| Technique | Done when... |
|---|---|
| Weak service binary permissions | Box completed using it |
| Service DLL hijacking | Box completed using it |
| Unquoted service paths | Box completed using it |
| AlwaysInstallElevated | Box completed using it |
| SeImpersonatePrivilege + Potato | Box completed using it |
| Token impersonation | Box completed using it |
| Registry-based escalation | Box completed using it |
| Credential hunting (PS history, registry, config files) | Box completed using it |
| Scheduled task abuse (writable script) | Done — MarkUp |
| Kernel/driver vulnerabilities | Box completed using it |

**Box list suggestions (HTB Easy/Medium Windows):**
- Optimum, Bastard, Devel, Jerry, Arctic, Grandpa, Granny — service/kernel basics
- SecNotes, Bounty, Chatterbox, Bart — credential hunting + web
- Access, Silo, Fuse — advanced Windows patterns

| Week | Dates | Primary Focus | Box Mix | Milestone |
|---|---|---|---|---|
| P2-W1 | Oct 1–7 | Windows service abuse: binary permissions, DLL hijacking, and unquoted paths | 2–3/day, 14–16 total; 6 Windows + 3 Linux + 2 AD + 1 BOF + 1 web + 1 flexible | Demonstrate two writable-service paths and verify the service context |
| P2-W2 | Oct 8–14 | Windows credential hunting: history, registry, and configuration files | 2–3/day, 14–16 total; 6 Windows + 3 Linux + 2 AD + 1 BOF + 1 web + 1 flexible | Extract and validate credentials from three Windows storage locations |
| P2-W3 | Oct 15–21 | Windows token and Potato privilege escalation | 2–3/day, 14–16 total; 6 Windows + 3 Linux + 2 AD + 1 BOF + 1 web + 1 flexible | Explain and reproduce one SeImpersonate-to-SYSTEM chain without a walkthrough |
| P2-W4 | Oct 22–28 | Windows kernel escalation and scheduled-task abuse | 2–3/day, 14–16 total; 6 Windows + 3 Linux + 2 AD + 1 BOF + 1 web + 1 flexible | Complete the Windows PrivEsc Decision Tree with verified kernel and scheduled-task branches |

**Vault action:** Every new Windows technique gets added to the Command Appendix and Command Breakdowns. Update the cheatsheet Windows PrivEsc section. Update the Decision Tree with any missing branches.

---

## Phase 3: Active Directory (Nov 1 – Dec 14)

**Goal:** AD stops being theoretical. Three full end-to-end chains completed.

**This is the most important phase. Do not rush it.**

| Week | Dates | Primary Focus | Box Mix | Milestone |
|---|---|---|---|---|
| P3-W1 | Nov 1–7 | AD enumeration and manual LDAP | 2–3/day, 14–16 total; 5 AD + 4 Windows + 3 Linux + 1 web + 1 container | Collect and interpret BloodHound data, LDAP results, SMB shares, users, groups, and SPNs without a walkthrough |
| P3-W2 | Nov 8–14 | Kerberoasting and AS-REP roasting | 2–3/day, 14–16 total; 5 AD + 4 Windows + 3 Linux + 1 web + 1 container | Obtain, crack, and validate both a Kerberos service-ticket hash and an AS-REP hash |
| P3-W3 | Nov 15–21 | Pass-the-Hash and lateral movement | 2–3/day, 14–16 total; 5 AD + 4 Windows + 3 Linux + 1 web + 1 container | Move between two Windows services with a recovered NT hash and record the required permissions |
| P3-W4 | Nov 22–28 | ACL abuse and chained AD escalation | 2–3/day, 14–16 total; 5 AD + 4 Windows + 3 Linux + 1 web + 1 container | Identify and exploit one GenericAll, GenericWrite, WriteDACL, or ForceChangePassword path |
| P3-W5 | Dec 1–7 | Full AD compromise chain 1 | 2–3/day, 14–16 total; 5 AD + 4 Windows + 3 Linux + 1 web + 1 container | Complete, verify, and write up the first end-to-end domain compromise |
| P3-W6 | Dec 8–14 | Full AD compromise chain 2 | 2–3/day, 14–16 total; 5 AD + 4 Windows + 3 Linux + 1 web + 1 container | Complete a second chain from enumeration through DCSync or NTDS extraction |

**Box suggestions:**
- HTB AD-focused: Forest, Active, Sauna, Return, Search, Timelapse, Escape
- PG: craft labs, OSCP AD challenge sets
- OffSec challenge labs (A, B, C) — treat each as a mock

**Vault action:** AD Command Appendix, Decision Tree, and Command Breakdowns all updated after each technique lands. Write-ups produced for every chain.

---

## Phase 4: Pivoting, Client-Side, Exploit Dev (Dec 15 – Jan 18)

**Goal:** Close the three remaining advanced gaps. These won't come from random boxes — they need deliberate focus.

| Week | Dates | Primary Focus | Box Mix | Milestone |
|---|---|---|---|---|
| P4-W1 | Dec 15–21 | Pivoting and SSH tunnelling | 2/day, 10–12 total; 3 advanced + 3 Windows + 2 Linux + 2 AD refreshers | Reach and enumerate one internal service through an SSH local or dynamic forward |
| P4-W2 | Dec 22–28 | Chisel, SOCKS, and proxy-based routing | 2/day, 10–12 total; 3 advanced + 3 Windows + 2 Linux + 2 AD refreshers | Scan and access an internal service through a SOCKS tunnel and document the route |
| P4-W3 | Dec 29–Jan 4 | Client-side delivery plus SSRF/SSTI web techniques | 2/day, 10–12 total; 3 advanced + 3 Windows + 2 Linux + 2 AD refreshers | Deliver one client-side payload with a confirmed callback, then reproduce one SSRF or SSTI chain |
| P4-W4 | Jan 5–11 | Exploit modification from ExploitDB | 2/day, 10–12 total; 3 advanced + 3 Windows + 2 Linux + 2 AD refreshers | Modify and run three public exploits with payload, interpreter, path, or parameter changes |
| P4-W5 | Jan 12–18 | Consolidation and timed advanced repetitions | 2/day, 10–12 total; 3 advanced + 3 Windows + 2 Linux + 2 AD refreshers | Reproduce the selected exploit and pivot chain from notes alone after a 48-hour gap |

**Vault action:** Pivoting runbook stages filled in. Client-side section of cheatsheet populated. Exploit dev Command Appendix and Breakdowns updated with real demonstrated steps.

---

## Phase 5: Mock Exams + Reporting (Jan 19 – Feb 22)

**This phase is non-negotiable.** Technique knowledge without exam execution is not exam readiness.

### Mock 1 (Week 1): Standalones only, 6 hours

**Box mix:** 0 extra boxes; complete the timed mock with one Linux, one Windows, and one technique-gap target.

- Pick 3 HTB/PG Easy-Medium boxes you haven't done
- Set a timer for 6 hours
- Work all three simultaneously (not sequentially)
- Screenshot every step
- Write the report in 3 hours after

Review: what took too long? Where did you get stuck? What did you google that should have been in the vault?

### Mock 2 (Week 2-3): Full exam format, 23h 45m

**Box mix:** 0 extra boxes; use the same three standalones and one AD chain for the timed run and report.

- 3 standalones + 1 AD chain (use OffSec challenge labs or a fresh HTB Pro Lab section)
- Full 23h 45m timed
- Full report in 24h after
- No googling — vault only

Review: could you produce a complete, submission-quality report? Did the vault answer every question you had? What was missing?

### Week 4: Targeted reps

**Box mix:** 5–7 boxes selected directly from the mock review, focused on the slowest or failed techniques.

Based on mock failures — go back and drill the specific techniques that slowed you down. No new techniques at this stage, just shoring up weak spots.

### Week 5: Mock 3 — confidence run

**Box mix:** 0 extra boxes; use the confidence run targets and no additional box work.

One more timed run, this time with the goal of feeling smooth, not just completing. Time each stage. If you're spending more than 2 hours on a box with no progress, practice the decision to move on.

**Reporting practice goals:**
- Every mock produces a full report
- By Mock 3, the report should take under 4 hours to write for a full exam
- Reports include: attack narrative, reproducible steps, proof screenshots with IP visible, impact, remediation, executive summary

---

## Phase 6: Final Polish (Feb 23 – Mar 1)

**Nothing new. Just consolidation.**

- [ ] Read through the entire cheatsheet — does everything make sense?
- [ ] Open the vault, close the internet, try to answer: "how do I Kerberoast?" — can you do it from the vault alone?
- [ ] Check all TODO markers — are any of them exam-relevant? Anything still TODO that you've actually done by now?
- [ ] Confirm exam booking, VPN, environment, screenshots tool, report template ready in SysReptor
- [ ] Light box practice — 1-2 per day, nothing new, just staying sharp
- [ ] Sleep. Eat. Hands aren't going to forget what they've practiced for 6 months.

---

## Weekly habit (every week, every phase)

At the end of every week:
1. Update this plan — check off milestones, adjust if something slipped
2. Update the cheatsheet — fill any TODO markers from that week's work
3. Add write-ups for any new boxes
4. Run the vault offline check — pick one technique from that week, close the internet, reproduce it from the vault alone

---

## Key numbers to track

| Metric | Now (Aug 2026) | Target (Feb 2027) |
|---|---|---|
| Linux boxes with write-ups | 11 | 80+ |
| Windows boxes with write-ups | 5 | 50+ |
| Full AD chains completed | 5 | 15+ |
| Module labs fully complete | Partial | All |
| Timed mock exams | 0 | 3 |
| Full reports written | 0 | 3 |
| Cheatsheet TODO markers remaining | 20 | <5 |

---

## Related vault pages

- [[OSCP COMMAND MASTER CHEATSHEET]]
- [[RUNBOOK V2/Index]]
- [[MODULES/MODULES]]
- [[DECISION TREE/DECISION TREE]]
- [[BOXES/WRITE UPS/Windows/MarkUp]]
- [[MODERN TOOLING/SysReptor]]
## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
