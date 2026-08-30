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

**Weekly milestone:**
- Week 1: Exploit dev labs done, buffer overflow chain reproducible from notes alone
- Week 2: Password attacks labs done, client-side labs done
- Week 3: AD module labs done, tunnelling labs done
- Week 4: Every module marked fully complete — theory AND hands-on

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

**Weekly milestone:**
- Week 1: 5 Windows boxes, at least 2 different PrivEsc techniques covered
- Week 2: 5 more, 2 more techniques covered
- Week 3: 5 more, 2 more techniques covered
- Week 4: Final 5, full Windows PrivEsc Decision Tree updated with all techniques demonstrated

**Vault action:** Every new Windows technique gets added to the Command Appendix and Command Breakdowns. Update the cheatsheet Windows PrivEsc section. Update the Decision Tree with any missing branches.

---

## Phase 3: Active Directory (Nov 1 – Dec 14)

**Goal:** AD stops being theoretical. Three full end-to-end chains completed.

**This is the most important phase. Do not rush it.**

### Week 1-2: Enumeration

Practice these until they're automatic:
- BloodHound collection, filtering, shortest-path queries
- Manual LDAP enumeration with `ldapsearch`
- PowerView / PowerShell AD enumeration
- SMB share enumeration, SYSVOL, GPP credential hunting
- SPN enumeration for Kerberoasting targets
- AS-REP roasting candidate identification
- Domain user and group mapping

### Week 3-4: Attack techniques

Practice each until it works from notes alone:
- Kerberoasting (GetUserSPNs → hashcat)
- AS-REP roasting (GetNPUsers → hashcat)
- Pass-the-Hash (crackmapexec/evil-winrm)
- Overpass-the-Hash / Pass-the-Ticket
- NTLM relay (Responder + ntlmrelayx)
- Net-NTLMv2 capture and crack
- Object permission abuse (GenericAll, GenericWrite, WriteDACL, ForceChangePassword)
- Unconstrained delegation abuse

### Week 5-6: Full chains

Three complete AD compromises, end-to-end:
- Start from supplied low-privilege domain user
- Enumerate, identify attack path, exploit
- Move laterally across machines
- DCSync or NTDS extraction
- Domain compromise demonstrated
- Write-up produced for each chain

**Box suggestions:**
- HTB AD-focused: Forest, Active, Sauna, Return, Search, Timelapse, Escape
- PG: craft labs, OSCP AD challenge sets
- OffSec challenge labs (A, B, C) — treat each as a mock

**Weekly milestones:**
- Week 1-2: BloodHound and manual enum are automatic, no googling needed
- Week 3-4: Each attack technique executed at least once from notes
- Week 5-6: Three full chains written up, reproducible from vault alone

**Vault action:** AD Command Appendix, Decision Tree, and Command Breakdowns all updated after each technique lands. Write-ups produced for every chain.

---

## Phase 4: Pivoting, Client-Side, Exploit Dev (Dec 15 – Jan 18)

**Goal:** Close the three remaining advanced gaps. These won't come from random boxes — they need deliberate focus.

### Week 1-2: Pivoting and tunnelling

Practice until multi-hop is comfortable:
- SSH local, remote, dynamic forwarding
- Windows SSH forwarding + Plink
- Chisel (client/server, SOCKS mode)
- Proxychains scanning through a pivot
- Netsh port forwarding
- Dnscat2 / Ligolo-ng
- Multi-hop: two pivots deep
- Scanning an internal subnet through a compromised host

### Week 3: Client-side attacks

One focused week:
- Office macro delivery (VBA, auto-open, obfuscated)
- Malicious document with embedded payload
- Windows library files (.library-ms)
- Shortcut (.lnk) files with payload
- Client-side reconnaissance
- Delivery and callback confirmation

### Week 4-5: Exploit development and modification

- Complete standalone buffer overflow from scratch (no walkthrough): crash, offset, bad chars, EIP, jump, shellcode, full working exploit
- Take three public exploits from ExploitDB that need modification and fix them: Python 2→3, path fixes, payload swap, parameter adjustment
- Reproduce from notes alone after 48h gap

**Vault action:** Pivoting runbook stages filled in. Client-side section of cheatsheet populated. Exploit dev Command Appendix and Breakdowns updated with real demonstrated steps.

---

## Phase 5: Mock Exams + Reporting (Jan 19 – Feb 22)

**This phase is non-negotiable.** Technique knowledge without exam execution is not exam readiness.

### Mock 1 (Week 1): Standalones only, 6 hours

- Pick 3 HTB/PG Easy-Medium boxes you haven't done
- Set a timer for 6 hours
- Work all three simultaneously (not sequentially)
- Screenshot every step
- Write the report in 3 hours after

Review: what took too long? Where did you get stuck? What did you google that should have been in the vault?

### Mock 2 (Week 2-3): Full exam format, 23h 45m

- 3 standalones + 1 AD chain (use OffSec challenge labs or a fresh HTB Pro Lab section)
- Full 23h 45m timed
- Full report in 24h after
- No googling — vault only

Review: could you produce a complete, submission-quality report? Did the vault answer every question you had? What was missing?

### Week 4: Targeted reps

Based on mock failures — go back and drill the specific techniques that slowed you down. No new techniques at this stage, just shoring up weak spots.

### Week 5: Mock 3 — confidence run

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
| Linux boxes with write-ups | 11 | 40+ |
| Windows boxes with write-ups | 1 | 20+ |
| Full AD chains completed | 0 | 3+ |
| Module labs fully complete | Partial | All |
| Timed mock exams | 0 | 3 |
| Full reports written | 0 | 3 |
| Cheatsheet TODO markers remaining | 20 | <5 |

---

## Related vault pages

- [[OSCP COMMAND MASTER CHEATSHEET]]
- [[RUNBOOK/00 - Master Index]]
- [[MODULES/MODULES]]
- [[DECISION TREE/DECISION TREE]]
- [[BOXES/WRITE UPS/Windows/MarkUp]]
- [[MODERN TOOLING/SysReptor]]
