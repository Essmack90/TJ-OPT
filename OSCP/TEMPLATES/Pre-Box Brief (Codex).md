# Pre-Box Brief — Codex Template

*Fill in the [ ] fields and paste directly into the Codex TUI before starting a new box.*

---

Read `/home/kali/Documents/Obsidian/main-vault/OSCP/CODEX CONTEXT.md` in full before starting.

**Run [BoxName] autonomously. Do not ask for confirmation between steps — work through the full kill chain and provide a complete transcript at the end.**

- **Platform:** [HackTheBox / ProvingGrounds / OffSecVM]
- **Box name:** [BoxName]
- **IP:** [BoxIP]
- **Domain:** [Domain] (if known — leave blank if unknown)
- **Type:** [AD / Standalone Windows / Linux]
- **OS:** [Windows / Linux]

---

## Rules

- Never read or display flag values — confirm the file exists and loot it, but keep the value private
- Clean down after: remove any accounts you created, files you uploaded, and persistence you added
- Provide a full step-by-step transcript when done, including all commands and key output
- If you get stuck, try alternative tools before stopping — document what failed and why
- Use $Variable conventions for credentials and IPs in the transcript
- No em dashes anywhere

---

## Reference runbook

The primary methodology reference is RUNBOOK V2 — a 50-page GPS-style runbook at:

`/home/kali/Documents/Obsidian/main-vault/OSCP/RUNBOOK V2/`

Start at `Start Here.md` (Step 1), then `Port Triage.md` (Step 2). Each page has a step number and path label at the top, and each arrow tells you the step number of the next page. Follow the arrows.

- **Linux path:** Steps 3–21
- **Windows path:** Steps 22–33
- **AD path:** Steps 34–50

You do not need to follow it rigidly — use it as a checklist and decision guide. If you hit a technique not covered in the runbook, note it in the transcript for later gap-filling.

---

## When done, send

- Full transcript (all commands, key output, gotchas hit along the way)
- Step numbers of RUNBOOK V2 pages that were used
- Any techniques from this box that are NOT in the runbook (new pages or new arrows needed)
- Confirmation that clean-down is complete
- Any efficiency improvements you noticed (faster tools, fewer steps)
