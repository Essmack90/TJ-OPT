# Post-Box Brief — Codex Template

*After completing a box manually with Claude, Claude fills this file in and gives you the path. Paste this into Codex:*

> Read this file in full and follow all instructions:
> `/home/kali/Documents/Obsidian/main-vault/OSCP/TEMPLATES/Post-Box Brief (Codex).md`

*(Claude replaces this file with the real brief before handing you the path — the file always contains the current box's details.)*

---

Read `/home/kali/Documents/Obsidian/main-vault/OSCP/CODEX CONTEXT.md` in full before starting. **Do NOT run any live commands against the target — the box is already complete. Write everything from the transcript below.**

---

## Your tasks (in order)

1. Write the box write-up
2. Add ⚡ efficiency callouts for every faster alternative approach listed below
3. Add 💡 hint callouts for every gotcha listed below
4. Fill RUNBOOK V2 gaps — read the relevant pages, then add any missing arrows, gotchas, or new pages
5. Update hub docs — **new content only**, read every file before writing

---

## Write-up spec

**Save to:** `/home/kali/Documents/Obsidian/main-vault/OSCP/BOXES/WRITE UPS/[Windows or Linux or AD]/[BoxName].md`

**Style:** Match `Forest.md` or `Sauna.md` for AD boxes, `MarkUp.md` for Windows standalone, any Linux write-up for Linux. All are at `OSCP/BOXES/WRITE UPS/`.

- YAML frontmatter (tags, platform, os, hostname, domain, difficulty, ip, status)
- "The gist" paragraph (2-3 sentences, plain English kill chain)
- Variables table
- Numbered sections
- $Variable conventions throughout — never paste real credentials, IPs, or flag values
- Screenshot placeholders only — use `![[screenshot-name.png]]` with a descriptive name and a SCREENSHOT caption underneath explaining what to capture. **Do not attempt to reference actual screenshot files or guess filenames. The user will fill in the real screenshots.**
- No em dashes
- Casual scannable prose
- Jargon explained in the same sentence it appears
- External Resources section at the end (verified deep-links, technique-specific not homepages)
- Vault Update Checklist at the end

---

## Box metadata

- **Platform:** [HTB / PG / OffSec]
- **OS:** [Windows Server XXXX / Linux distro]
- **Hostname:** [$Hostname]
- **Domain:** [$Domain] (or N/A)
- **Difficulty:** [Easy / Medium / Hard]
- **IP:** $BoxIP
- **Tags:** [#HTB #BoxName #OS #Techniques]

---

## The gist

[2-3 sentence plain English summary of the full kill chain]

---

## Variables

- $BoxIP = [IP]
- $LocalIP = [VPN IP]
- $Domain = [domain] (if AD)
- $FQDN = [fqdn] (if AD)
- $Username = [user1]
- $Password = [pass1] — keep private
- $Username2 = [user2] (if applicable)
- $Password2 = [pass2] — keep private
- $AdminHash = [hash] — keep private

---

## Full transcript

[Full step-by-step transcript goes here — all commands and key output]

---

## Gotchas — use these for 💡 hint callouts

[List every thing that went wrong, was surprising, or would trip up a new tester]

---

## Efficiency candidates — use these for ⚡ callouts

[List faster alternative tools or approaches for key steps]

---

## RUNBOOK V2 gap-fill

RUNBOOK V2 is at `/home/kali/Documents/Obsidian/main-vault/OSCP/RUNBOOK V2/` — 50 numbered pages in GPS format.

**Step numbers used in this box:** [list the Step N pages that were followed]

**Gaps found — techniques in this box not covered in the runbook:**

[For each gap, say whether it needs:]
- A new arrow on an existing page (specify which page and which "What did you get?" bullet)
- A new gotcha on an existing page (specify which page)
- A brand new page (specify the page name and where it fits in the step sequence)

**Hard rules for RUNBOOK V2 edits:**
- Read each target page in full before editing
- One decision per page — do not create walls of text
- Every arrow must reference a step number: `Step N · [[Page Name]]`
- New pages must follow the format: Step stamp → Run this → Example output → What did you get? → Notes → Gotcha
- New pages must be added to `Index.md` in the correct step sequence
- Do NOT touch `/home/kali/Documents/Obsidian/main-vault/OSCP/RUNBOOK/` — that is the old runbook, leave it alone
- Do NOT remove existing content — only add

---

## Hub doc update scope — new content only

Read every file before writing. Only add what is genuinely absent. Hub docs are at `OSCP/HUB DOCS/` or within the relevant module folders.

**Command Appendix:** [new one-liner commands from this box]

**Command Breakdowns:** [new command explanations — flag-by-flag breakdowns]

**Decision Tree:** [new decision branches or attack paths]

**Methodology notes:** [new technique descriptions]

**Module notes:** [module number + what to add, if anything]

---

## Hard rules

- No flag values anywhere in any file
- $Variable conventions throughout
- No em dashes
- Read before writing every file
- No content removal — addition and clarification only
- Plain English, jargon explained in the same sentence
- External Resources: verified deep-links, technique-specific not homepages
- Screenshot placeholders only — descriptive name + SCREENSHOT caption, no real filenames
- Report what was added and where — do not paste full files back
