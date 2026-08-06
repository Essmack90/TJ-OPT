# Command Breakdowns

The other hub docs tell you *what* to run. This one explains *why it works*, piece by piece, and where you'd actually go find the pieces yourself if you were staring at a target with no note to copy from.

Not a syntax reference like [[COMMAND APPENDIX]], not phase-ordered like [[METHODOLOGY CHEAT SHEET]], not symptom-ordered like [[DECISION TREE]]. This is the "explain it like I've never seen this before" layer underneath all three. When a command looks like line noise (nested subqueries, weird hex encoding, chained pipes), it gets a full teardown here.

Split into one file per area, same categories as the module topics, so it grows alongside the vault instead of becoming one giant unreadable file.

## Areas

- [[SQL Injection (Breakdowns)|SQL Injection]] — error-based extraction, UNION payloads, blind SQLi logic, `LOAD_FILE`/`INTO OUTFILE`, MSSQL `xp_cmdshell`, sqlmap internals.
- [[File Inclusion & Traversal (Breakdowns)|File Inclusion & Traversal]] — `--path-as-is` traversal, encoding bypasses, PHP wrappers, null-byte tricks, mechanical secret extraction.
- [[Shells & Payloads (Breakdowns)|Shells & Payloads]] — CMD/PowerShell polyglots, shell-wrapping gotchas, encoding requirements.
- [[Web Applications (Breakdowns)|Web Applications]] — WordPress XSS-to-admin chains, mass assignment, plugin metadata abuse.
- [[Reconnaissance & Enumeration (Breakdowns)|Reconnaissance & Enumeration]] — output-wrangling tricks (negative grep, greppable-format parsing, LOLBAS port scanning).
- [[Privilege Escalation & Local Exploitation (Breakdowns)|Privilege Escalation & Local Exploitation]] — cron glob gotchas, LOLBAS downloaders, JuicyPotato/CLSID mechanics. (No matching [[COMMAND APPENDIX]] area yet, standing in until the Privesc modules are formally covered.)
- [[Phishing (Breakdowns)|Phishing]] — why `wget` can't clone JS-driven pages, BeautifulSoup vs raw string-replace fragility, the `127.0.0.1`-breaks-cross-machine gotcha.
- [[Client-Side Attacks (Breakdowns)|Client-Side Attacks]] — Windows library file XML tag semantics (DLL-resource indirect references), the 255-vs-4096 character `.lnk` Properties-hiding gap.

*(More areas get added here as modules are worked through — Active Directory, Password Attacks, Pivoting, etc.)*

---

## Entry format

Every breakdown in every area file follows this shape:

```markdown
## <Plain-English name for the technique>

**Full command:**
​```bash
<the actual command, copy-pasted from the box it was used on>
​```

**Piece by piece:**
- `<fragment>` → <why this fragment exists, what happens if you remove it, what it exploits>
- `<fragment>` → <...>

**Where this comes from:** <which reference site/page/section teaches this pattern, specifically enough to find it again, not just "check HackTricks">

**Where to look in the response:** <exactly what part of the raw output/HTML/terminal you scan for, and what it looks like buried in the noise>

🔁 **Seen in:** [[<Module or Box note>#<heading>|<context>]]
```

**Why this shape:** a command is only useful if you know which part to change for a different target and which part is fixed grammar. "Piece by piece" answers that. "Where this comes from" and "where to look in the response" exist because the hardest part of OSCP isn't memorizing payloads, it's knowing *which page of which reference to open* and *which line of a huge response actually matters*, so both get called out explicitly rather than assumed.

#### Tags: #CommandBreakdowns #Methodology
