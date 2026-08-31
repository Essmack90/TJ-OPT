# Codex Context — OSCP Study Session

*Read this at the start of every session before doing anything. It covers who we are, the vault layout, the workflow, and the rules that matter.*

---

## What We're Doing

Studying for OSCP via Offsec modules + Hack The Box / Proving Grounds Practice boxes. Building a living Obsidian vault of notes, stage notes, and methodology docs as we go. The goal is exam-ready technique retention, not just flag collection.

**Division of labour:**
- **Claude** = strategy, methodology, module notes, planning, walk-through tutor
- **Codex** = heavy lifting -- autonomous box runs, transcript generation, write-ups (from our transcript), hub doc updates, runbook gap-fills

---

## Vault Location

```
/home/kali/Documents/Obsidian/main-vault/OSCP/
```

### Folder Map

| Folder | What's in it |
|---|---|
| `BOXES/WRITE UPS/AD/` | AD box write-ups (e.g. `Forest.md`, `Sauna.md`, `Return.md`) |
| `BOXES/WRITE UPS/Windows/` | Standalone Windows write-ups |
| `BOXES/WRITE UPS/Linux/` | Linux write-ups (numbered, e.g. `1. clamAV.md`) |
| `BOXES/MASTER BOX LIST.md` | Master tracking list -- check off completed boxes here |
| `BOXES/BOX LOGS/` | Raw terminal logs copied after each box |
| `RUNBOOK V2/` | **Primary methodology reference** -- 50-page GPS-style runbook |
| `RUNBOOK/` | Old runbook -- do not touch this folder |
| `MODULES/` | Per-module notes (M01–M26 etc.) |
| `COMMAND APPENDIX/` | Command reference by topic area |
| `DECISION TREE/` | "I found X, what do I try" decision trees by topic |
| `COMMAND BREAKDOWNS/` | Flag-by-flag command explanations |
| `METHODOLOGY CHEAT SHEET/` | High-level attack methodology by OS |

---

## Box Run Workflow (Codex Role)

### Phase 1 — Autonomous run

When given a box to run:

1. **Read RUNBOOK V2 first.** Start at `RUNBOOK V2/Start Here.md` (Step 1), then `Port Triage.md` (Step 2). Follow the arrows. Use it as a methodology checklist, not a rigid script. Note any techniques not covered for later gap-filling.

2. **You may search for public write-ups** for this box (ippsec.rocks, HTB forums, community walkthroughs) to inform your approach. This is allowed and encouraged for unfamiliar techniques. Document that you used one.

3. **Full chain** -- recon → foothold → privesc → both flags confirmed.

4. **No Metasploit whatsoever.** Not for initial exploitation, not for privesc, not for anything. No sqlmap either.

5. **Never output flag values, credentials, or hashes** -- not in transcripts, not in reports, not anywhere. Say "flag confirmed at path" and nothing more.

6. **Full transcript when done** -- every exact command, every exact output, in sequence. No collapsing, no summarising, no omitting steps. Claude follows this transcript command-for-command during the manual run. Send this before cleanup.

7. **Sudo credentials.** You may request sudo credentials from the user if needed for a step. State clearly which box you need them for. Use them only for that box. When the box is complete, explicitly state: "I no longer need sudo credentials for [BoxName]." Do not retain or reuse them for any other box.

8. **Clean-down -- ALL files, verified.** Remove everything you created, downloaded, uploaded, or staged -- on the target AND on Kali. This includes:
   - All files in the box working directory on Kali (loot, www, tools staged for transfer)
   - All webshells, reverse shell payloads, exploit scripts uploaded to the target
   - All /tmp artifacts on the target
   - Any accounts you created
   - Any persistence you added
   - The shadow copy if you created one
   - Verify each removal individually -- do not assume deletion succeeded

### Phase 2 — Write-up (after our manual run)

**Codex does not write the write-up from his own autonomous run.**

The write-up is written by Codex only after Claude passes the user's manual run transcript. The source for all write-up content is what the user did during their manual session -- commands, output, order of steps, tools used.

When Claude sends the write-up brief:
- Read it in full before starting
- Base all walkthrough sections on the transcript Claude provides
- Match the style of `Sauna.md` exactly (for AD boxes) or the relevant existing write-up for other types
- See the Write-up Format section below

---

## Variable and Tooling Rules

**Use the Kali box tooling -- never create your own variables.**

The user's Kali environment has helper commands. Use them:

| Command | What it does |
|---|---|
| `boxstart BoxName IP htb` | Initialises the box -- creates directories, sets all variables, starts logging |
| `boxset VAR value` | Sets and saves a variable to `.env` |
| `loot cred user pass` | Saves a credential to `loot/creds.txt` |
| `loot hash user hash` | Saves a hash to `loot/hashes.txt` |
| `loot flag user\|root value` | Saves a flag to `loot/flags.txt` |
| `loot key /path/to/key` | Copies an SSH key to loot/ |
| `loot file /path/to/file` | Copies a file to loot/ |
| `shot name` | Takes a screenshot to screenshots/ |
| `boxdone` | Clears the current-box marker |

**Variable names -- always use these:**

| Variable | Meaning |
|---|---|
| `$BoxIP` | Target IP |
| `$BoxName` | Target hostname |
| `$LocalIP` | Attacker IP (tun0) |
| `$BoxDir` | Box working directory |
| `$Domain` | AD domain FQDN |
| `$FQDN` | Full hostname (host.domain.local) |
| `$Username` | First credential username |
| `$Password` | First credential password |
| `$Username2` | Second username |
| `$Password2` | Second password |
| `$Username3` | Third username |
| `$Password3` | Third password |
| `$AdminUser` | Privileged account username |
| `$AdminHash` | Privileged account NTLM hash |
| `$Port` | Listener port |
| `$WebPort` | Target web port |
| `$Wordlist` | Active wordlist path |

**Never use:** `<username>`, `<target>`, `USER`, hardcoded IPs, or `export VAR=value` style. Never run `mkdir -p` manually -- `boxstart` creates the directory structure.

**Reference pages (read these):**
- Pre-Engagement Kali Setup: `/home/kali/Documents/Obsidian/main-vault/OSCP/METHODOLOGY CHEAT SHEET/Pre-Engagement Kali Setup.md`
- OSCP Habits (screenshot and loot workflow): `/home/kali/Documents/Obsidian/main-vault/OSCP/RUNBOOK/OSCP Habits - Screenshot & Loot.md`

---

## Write-Up Format

**Style reference:** `OSCP/BOXES/WRITE UPS/Windows/Jerry.md` is the master blueprint for all write-ups. Match it exactly. For AD boxes, also reference `OSCP/BOXES/WRITE UPS/AD/Sauna.md` for AD-specific section structure (BloodHound, ACL enumeration, DCSync etc.), but the prose style, inline resources, and tutorial feel come from Jerry.md.

- YAML frontmatter (tags, platform, os, hostname, domain, difficulty, ip, status)
- `# HTB: BoxName, Full Walkthrough` -- H1 title
- `## The gist` -- 2-3 sentence plain English kill chain
- `## Box information` -- table (Platform, OS, Hostname, Domain, Difficulty, IP)
- `## Variables` -- boxset commands
- Numbered walkthrough sections with:
  - **Tutorial prose per step, not summarised at the end.** Every numbered section opens with 2-4 sentences explaining the concept *before* the code block. The reader must understand why they are running the command before they see it. Do not collect explanations into Key Lessons and leave the walkthrough thin -- the walkthrough IS the tutorial.
  - Explain *why* each tool or flag is used, not just *what* it does. If a flag appears in a command, its purpose is named in the prose above it.
  - Where one approach was chosen over another (e.g. text API vs HTML manager), explain why.
  - Code blocks using `$Variable` conventions
  - `![[screenshot-name.png]]` on its own line, then `SCREENSHOT: caption` on the next line
  - `💡` gotcha callouts inline at the relevant step
  - `⚡` efficiency callouts inline at the relevant step -- name what alternative was avoided and why the chosen path is faster
- `## Credentials` table (Account / Source / Use -- no passwords or hashes)
- `## Key lessons` bullet list
- `## External Resources` (verified deep-links, technique-specific not homepages)
- `## Checklist` with `- [x]` boxes per completed step

**Hard rules for all vault writing:**
- No flag values, no passwords, no hashes anywhere in any file
- $Variable conventions throughout -- never hardcode box-specific values
- No em dashes
- Read every file in full before editing
- Add only -- never remove existing content
- Jargon explained in the same sentence it appears
- Report what was added and where -- do not paste full files back

---

## Hub Doc and Runbook Edits

When editing Command Appendix / Decision Tree / Breakdowns / RUNBOOK V2 files:
1. Read the full file first -- match surrounding heading levels and style
2. Use `$Username`, `$BoxIP` etc. -- never `<username>` or hardcoded values
3. After editing, confirm the section heading and line number inserted -- do not paste the full file back
4. Do NOT touch `/home/kali/Documents/Obsidian/main-vault/OSCP/RUNBOOK/` -- that is the old runbook, leave it alone
5. RUNBOOK V2 edits: one decision per page, every arrow references a step number, new pages follow the established format

---

## Current Progress

### HTB AD Boxes
| Box | Status | Key Technique |
|---|---|---|
| Forest | ✅ | AS-REP roasting → Account Operators → WriteDACL → DCSync → PTH |
| Sauna | ✅ | AS-REP roasting → Winlogon autologon → direct DCSync → PTH |
| Return | ✅ | LDAP passback → Server Operators → VSS service hijack |
| Flight | ✅ ♻️ | LFI UNC bypass → NTLM theft → RunasCs → GodPotato → VSS NTDS (REDO: NTDS exfil incomplete) |

### PG Practice Boxes
| # | Box | Technique | Status |
|---|---|---|---|
| 1 | clamAV | SNMP → Sendmail RCE → direct root | ✅ |
| 2 | Pelican | Exhibitor UI injection → sudo gcore memory dump | ✅ |
| 3 | Payday | CS-Cart LFI → SSH brute → sudo su | ✅ |
| 4 | Snookums | LFI → data:// wrapper RCE → /etc/passwd write | ✅ |
| 5 | Bratarina | OpenSMTPD CVE-2020-7247 → direct root | ✅ |
| 6 | Pebbles | ZoneMinder SQLi → MySQL UDF | ✅ ♻️ |
| 7 | Nibbles (PG) | PostgreSQL default creds → COPY TO PROGRAM → SUID find | ✅ |
| 8 | Zenphoto | Zenphoto EDB-18083 → RDS kernel LPE | ✅ |
| 9 | Nukem | Simple File List upload → DOSBox SUID → sudoers | ✅ |
| 10 | Cockpit | SQLi auth bypass → tar wildcard sudo injection | ✅ |

### HTB Linux / Other
| Box | Status | Key Technique |
|---|---|---|
| Sea | ✅ | WonderCMS blind XSS → module upload → log_file injection |

---

## Key Constraints (Non-Negotiable)

1. **No Metasploit whatsoever** -- not for exploitation, not for privesc, not for anything
2. **No sqlmap** -- manual injection only
3. **Never output flag values, credentials, or hashes** -- keep all loot private
4. **Use the Kali tooling** -- boxstart, boxset, loot, shot -- never create your own variable system
5. **Follow RUNBOOK V2** -- it is the methodology reference
6. **Read before editing** -- always read a file fully before making changes
7. **Add only** -- never remove existing vault content
8. **Write-ups from our transcript** -- not from your autonomous run

---

## External Resources (Use These, Not Random Sites)

- GTFOBins: https://gtfobins.github.io
- RevShells: https://www.revshells.com
- HackTricks: https://book.hacktricks.xyz
- PayloadsAllTheThings: https://github.com/swisskyrepo/PayloadsAllTheThings
- CyberChef: https://gchq.github.io/CyberChef/
- ippsec.rocks: https://ippsec.rocks
