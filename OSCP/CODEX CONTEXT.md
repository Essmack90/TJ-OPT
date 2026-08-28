# Codex Context — OSCP Study Session

*Read this at the start of every session before doing anything. It covers who we are, the vault layout, the workflow, and the rules that matter.*

---

## What We're Doing

Studying for OSCP via Offsec modules + Hack The Box / Proving Grounds Practice boxes. Building a living Obsidian vault of notes, stage notes, and methodology docs as we go. The goal is exam-ready technique retention, not just flag collection.

**Division of labour:**
- **Claude** = strategy, methodology, module notes, write-ups, planning
- **Codex** = heavy lifting — full exploit chain on boxes, file editing, hub doc updates, anything that benefits from sandboxed execution

---

## Vault Location

```
/home/kali/Documents/Obsidian/main-vault/OSCP/
```

### Folder Map

| Folder | What's in it |
|---|---|
| `BOXES/WRITE UPS/` | Per-box write-ups (numbered, e.g. `9. Nukem.md`) |
| `BOXES/MASTER BOX LIST.md` | Master tracking list — check off completed boxes here |
| `BOXES/BOX LOGS/` | Raw terminal logs copied after each box |
| `RUNBOOK/` | Stage notes (one technique per file), FAQ, templates |
| `MODULES/` | Per-module notes (M01–M26 etc.) |
| `COMMAND APPENDIX/` | Command reference by topic area |
| `DECISION TREE/` | "I found X, what do I try" decision trees by topic |
| `COMMAND BREAKDOWNS/` | Flag-by-flag command explanations |
| `METHODOLOGY CHEAT SHEET/` | High-level attack methodology by OS |

---

## Box Workflow (Codex Role)

When given a box to run:

1. **Full chain** — recon → foothold → privesc → both flags. No Metasploit for initial exploitation. No sqlmap.
2. **Never output flag values** — say "flag found at /path/local.txt" but don't paste the value. User finds their own.
3. **Full cleanup after** — restore every modified file (sudoers, configs, webshells). Remove all /tmp artifacts. Verify cleanup (hash checks where practical).
4. **Report back** with: exact commands used, field names, paths on the box, web user identity, what cleanup was done and verified.
5. **CRITICAL — Full transcript, not a summary.** When the chain is complete, send the **full step-by-step working** — every exact command you ran, every exact response/output, in sequence. Do NOT collapse, summarise, or omit steps. Claude follows this transcript command-for-command during the manual run. A summary is useless — it loses the exact payload formats, timing details, and intermediate outputs that the manual run depends on. Send the full thing before doing cleanup or anything else.

### Cleanup Standards

- Modified `/etc/sudoers` → restore from package cache (`bsdtar -xOf /path/to/pkg.tar.zst etc/sudoers > /etc/sudoers`)
- Webshells → `rm` the exact file, verify 404
- `/tmp` artifacts → `rm -f /tmp/<name>*`
- Never use intermediate temp files for restores — write directly to the target

---

## Vault Writing Rules

### Variable Names — Always Use These, Never Hardcode

| Variable | Meaning |
|---|---|
| `$BoxIP` | Target IP |
| `$BoxName` | Target hostname |
| `$LocalIP` | Attacker IP (tun0) |
| `$Username` | First found username |
| `$Username2` | Second username |
| `$Password` | First found password |
| `$Password2` | Second password |
| `$Port` | Listener port |
| `$WebPort` | Target web port |
| `$Domain` | AD domain FQDN |
| `$Wordlist` | Active wordlist path |

**Never use:** `<username>`, `<target>`, `USER`, `192.168.x.x`, or any hardcoded value that belongs to a variable. If a value is box-specific and non-generic (like a static plugin token), leave it as a literal with a comment explaining what it is.

### Stage Note Format

```markdown
---
tags: [oscp, <topic>, runbook]
box_sources: [BoxName]
---

# Stage Name

| Command | Evidence | Works when | Notes | ✅ Go to | ❌ If nothing works |
|---|---|---|---|---|---|
| `command here` | what you see | conditions | gotchas | [[Next Stage]] | [[Previous Stage]] |
```

- One row per technique that actually worked on a real box
- `✅ Go to` always links to a **separate file** (never a same-page anchor)
- `❌ If nothing works` links back to the parent stage
- Module wikilinks required: `[[18. Linux Privilege Escalation]]`

### Hub Doc Edits

When editing Command Appendix / Decision Tree / Breakdowns files:
1. **Read the full file first** — match the surrounding heading levels and style
2. Use `$Username`, `$BoxIP` etc. — never `<username>` or hardcoded values
3. Don't add `eeSecurity` / nonce params unless they're genuinely required and verified
4. Direct file writes — no intermediate temp files (`> /etc/sudoers` not `> /tmp/x && mv`)
5. After editing, confirm the section heading and line number inserted — don't paste the full file back

### Write-Up Format

See `BOXES/WRITE UPS/8. Zenphoto.md` or `9. Nukem.md` for the template. Key sections:
- Box Info table
- Recon (port scan, service scan, web enum)
- Vulnerability ID (searchsploit, CVE)
- Foothold (step by step with exact commands)
- Post-exploitation (flags, creds found)
- PrivEsc (enumeration → exploit → cleanup)
- Credentials table
- Tools Used table
- Vulnerabilities/Techniques table
- Lessons Learned
- External Resources
- Vault Update Checklist

---

## Current Progress (as of 2026-08-27)

### Completed PG Practice Boxes

| # | Box | Technique | Status |
|---|---|---|---|
| 1 | clamAV | SNMP → Sendmail RCE → direct root | ✅ |
| 2 | Pelican | Exhibitor UI injection → sudo gcore memory dump | ✅ |
| 3 | Payday | CS-Cart LFI → SSH brute → sudo su | ✅ |
| 4 | Snookums | LFI → data:// wrapper RCE → /etc/passwd write | ✅ |
| 5 | Bratarina | OpenSMTPD CVE-2020-7247 → direct root | ✅ |
| 6 | Pebbles | ZoneMinder SQLi → MySQL UDF | ✅ ♻️ (redo — Codex left /tmp/rootbash) |
| 7 | Nibbles (PG) | PostgreSQL default creds → COPY TO PROGRAM → SUID find | ✅ |
| 8 | Zenphoto | Zenphoto EDB-18083 → RDS kernel LPE | ✅ |
| 9 | Nukem | Simple File List CVE-2020-36847 → DOSBox SUID sudoers | ✅ |
| 10 | Cockpit | SQLi auth bypass (`' \|\| 1=1#`) → Cockpit 9090 web terminal → tar wildcard sudo injection → root | ✅ |

| 11 | Sea (HTB) | WonderCMS CVE-2023-41425 blind XSS → module upload → www-data → hash crack → amay SSH → localhost:8080 log_file injection → root | ✅ |

### Up Next

- Hetemit (PG Practice)
- HTB Nibbles (Nibbleblog 4.0.3 — different from PG Nibbles)

---

## Key Constraints (Non-Negotiable)

1. **No Metasploit for initial exploitation** — manual techniques only
2. **No sqlmap** — learn the injection by hand
3. **Never output flag values** — not to Claude, not in reports
4. **Always clean up after box runs** — verified, not just "I deleted it"
5. **Variables in vault writing** — `$Username` not `<username>`, `$BoxIP` not the literal IP
6. **Read before editing** — always read a file fully before making changes to it

---

## External Resources (Use These, Not Random Sites)

- GTFOBins: https://gtfobins.github.io
- RevShells: https://www.revshells.com
- HackTricks (GitHub): https://github.com/HackTricks-wiki/hacktricks
- PayloadsAllTheThings: https://github.com/swisskyrepo/PayloadsAllTheThings
- CyberChef: https://gchq.github.io/CyberChef/
- ippsec.rocks: https://ippsec.rocks
