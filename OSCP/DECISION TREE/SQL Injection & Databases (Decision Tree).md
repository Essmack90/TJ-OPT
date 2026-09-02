# SQL Injection & Databases, Decision Tree

Part of [[DECISION TREE]]. "I found X, what do I try" for SQL injection across MySQL, MSSQL, and PostgreSQL.

---

### Found a login form, search box, or any URL/POST parameter that likely touches a database
→ Test with a single `'` first. A SQL syntax error (rather than the app's normal error) confirms in-band injection
→ Login form? Try the classic auth bypass: `offsec' OR 1=1 -- //` in the username field
→ **Auth bypass still failing even though SQLi is confirmed?** The backend query may wrap user input in parentheses, e.g. `WHERE (username='INPUT')`. Your closing `-- -` comment is correct but there's still an unclosed `)`. Add the bracket: `') OR 1=1-- -` or `' OR ID=N)-- -` for specific-row access. Compare response sizes with and without `)` in Burp Repeater to confirm which variant stops the error
→ Results reflected on the page? Go UNION-based: find the column count with `' ORDER BY 1-- //` (increment until it errors), then `UNION SELECT` dummy values to see which columns render. Alternative: incremental UNION (`' UNION SELECT 1-- -`, `' UNION SELECT 1,2-- -`, etc.), same result, also immediately positions you to inject data into the columns you find
→ Nothing reflected at all? Test boolean-based (`' AND 1=1 -- //`) and time-based (`' AND IF(1=1,sleep(3),'false') -- //`) blind SQLi instead
→ See [[10. SQL Injection Attacks#10.2. Manual SQL Exploitation|10.2]], [[10. SQL Injection Attacks#10.2.1. Identifying SQLi via Error-Based Payloads|SQIF.6]]

### Confirmed SQLi on an INSERT/UPDATE-style form (nothing reflects back, e.g. a newsletter subscribe box), and the app shows raw DB errors
→ Don't reach for slow boolean/time-based blind first if the app leaks real MySQL error text on a broken query, error-based extraction is much faster and doesn't require sqlmap. Use `extractvalue()`/`updatexml()` to smuggle a subquery's result into the error message
→ `' AND extractvalue(1,concat(0x7e,(SELECT database())))-- -` (swap the subquery for whatever you want to pull: `group_concat(table_name)`, a specific column, etc)
→ Output truncates at 32 characters, page through longer values with `substring(value,start,31)`
→ See [[SQL Injection & Databases#SQL Injection Payloads|Command Appendix]] and [[10. SQL Injection Attacks#🏆 Capstone Labs|Capstone Labs]] (VM #2)

### Have SQLi with FILE privilege, but the injection point is INSERT-only (no SELECT context to attach INTO OUTFILE/UNION to)
→ `INTO OUTFILE` and `UNION` both need a `SELECT` to hang off of, an INSERT's `VALUES(...)` doesn't give you one, and PHP's `mysqli_query()` normally blocks stacked queries too
→ `LOAD_FILE('/path')` sidesteps all of that: it's a plain function callable from inside any subquery, including one wrapped in `extractvalue()` for error-based extraction. Needs `FILE` privilege and `secure_file_priv` either empty or matching the target path (check both via `information_schema.user_privileges` and `SELECT @@secure_file_priv`)
→ Good for reading a flag file directly once you know/guess the path, common ones seen so far: `/var/www/flag.txt`, `/var/www/html/tmp/flag.txt`
→ See [[10. SQL Injection Attacks#🏆 Capstone Labs|Capstone Labs]] (VM #2)

### Confirmed SQLi, want code execution
→ MySQL: write a webshell via `UNION SELECT ... INTO OUTFILE` to a writable web-servable path, then hit it with `?cmd=`
→ MSSQL: enable and use `xp_cmdshell` (`sp_configure` twice, then `EXECUTE xp_cmdshell '<command>'`)
→ PostgreSQL: confirm the connected role is a superuser first (`SELECT usesuper FROM pg_user`), then `COPY <table> FROM PROGRAM '<command>'` (needs stacked queries, e.g. via PHP's `pg_query()`, and a landing table created first)
→ Don't want to do it by hand? `sqlmap -r post.txt -p <param> --os-shell --web-root $BoxDir` automates the MySQL path end to end
→ See [[10. SQL Injection Attacks#10.3. Manual and Automated Code Execution|10.3]] and [[10. SQL Injection Attacks#Capstone: Exercise VM #3|Capstone Labs, VM #3]] for the Postgres path

### Nmap shows PostgreSQL (5432) open alongside a web app, and you've found an injectable field but nothing reflects on the page
→ Postgres backends commonly surface raw errors via PHP's `pg_query()`, same "leak data through error text" idea as MySQL's `extractvalue()`, but via a `CAST((subquery) AS int)` type-mismatch instead. No 32-character truncation cap, unlike MySQL
→ `' UNION SELECT NULL,CAST((SELECT version()) AS int),NULL-- ` (swap the subquery, and match the column position to one already confirmed integer-typed via an `ORDER BY`/column-probe)
→ See [[SQL Injection & Databases#PostgreSQL|Command Appendix]] and [[10. SQL Injection Attacks#Capstone: Exercise VM #3|Capstone Labs, VM #3]]

### Stacked-query injection (`'; <statement>-- `) doesn't error, doesn't reflect, doesn't seem to do anything, but you're not sure if it even ran
→ Don't trust silence as "it failed." Some apps only read the FIRST result set from a batch and never call `SqlDataReader.NextResult()` (or the equivalent), so errors/results from any statement after the first `;` never make it back to the response, even genuine unconditional errors like `SELECT 1/0`
→ Prove the statement actually executes with a timing side channel instead of an error/output one: `'; WAITFOR DELAY '0:0:5'-- ` (MSSQL) and measure the request with `time curl ...`. If the response takes ~5s longer, the stacked statement runs fine server-side, the app just isn't surfacing it
→ Once confirmed, don't waste more time trying to read data back through that channel, go straight for something that doesn't need a read-back at all (a reverse shell via `xp_cmdshell`/`COPY FROM PROGRAM`, confirmed by a caught listener connection instead of response text)
→ See [[SQL Injection (Breakdowns)#Why stacked-query errors silently vanish while the query still executes|Command Breakdowns]] and [[10. SQL Injection Attacks#Capstone: Exercise VM #4|Capstone Labs, VM #4]]

### An `AND`-based conditional payload (`' AND 1=CONVERT(int,(subquery))-- `) never errors, even though the same trick works fine as `UNION SELECT`
→ A per-row runtime error only fires if at least one row actually reaches that predicate. If the base condition (e.g. `username='offsec'`) matches zero real rows, the engine never needs to evaluate the second `AND` condition for anything, so an error-triggering expression sitting inside it silently never runs
→ `UNION SELECT` sidesteps this entirely, it's a separate result set that always executes unconditionally regardless of whether the first query matched any rows. Prefer `UNION`-based error injection over `AND`-based whenever the login/lookup value you're piggybacking on (`offsec`, etc) might not correspond to a real row
→ See [[10. SQL Injection Attacks#Capstone: Exercise VM #4|Capstone Labs, VM #4]], Step 8

### sqlmap immediately bails with "page not found (404)" or similar HTTP-error abort, even though the endpoint clearly works
→ Some endpoints (WordPress AJAX handlers especially) always answer with a non-2xx status even on a normal, successful response. sqlmap treats any error code as "target unreachable" by default
→ Add `--ignore-code=<code>` (e.g. `--ignore-code=404`) to keep testing anyway
→ See [[10. SQL Injection Attacks#10.3.2. Automating the Attack|10.3.2]]

### sqlmap finds nothing even though manual injection confirms it's vulnerable
→ Check which injection point sqlmap is testing. For cookie values, custom headers, or URL positions that aren't the last GET parameter, sqlmap's auto-detection misses them. Add the `*` marker explicitly: `-H 'Cookie: id=*'` or `?id=*` in the URL string
→ For JSON POST bodies, save the full raw HTTP request (including headers) and use `-r request.req`. sqlmap auto-detects the JSON content type and tests values inside the JSON object
→ If the injection point is fine but payloads are still being blocked: add `--random-agent` first (free bypass for UA-string WAF rules). Then try `--tamper=between` (converts `>` and spaces to less-blocked forms). Then stack both
→ If payloads still fail: try `--level 5 --risk 3` to test more injection points and more payload types. Note that `--risk 3` adds OR-based payloads that could modify rows
→ If the column count for UNION detection is wrong: use `--union-cols=N` where N is the known column count (confirm manually with `ORDER BY` first)
→ See [[10. SQL Injection Attacks#10.3.3. Advanced SQLMap Usage|SME.3]], [[SQL Injection & Databases#Sqlmap. Advanced Injection Points|Command Appendix]]

### sqlmap target has an anti-CSRF token on every form
→ The token changes per request so replaying the same POST body silently fails. Use `--csrf-token=<fieldname>`: sqlmap re-fetches the page, extracts the current token, and substitutes it before each request
→ Include the current token value in `--data` with its field name, then name the field with `--csrf-token`. sqlmap handles the rest automatically
→ If a parameter must be unique per request (e.g. a transaction ID): `--randomize=<paramname>` generates a fresh random value for it each request
→ See [[10. SQL Injection Attacks#10.3.3. Advanced SQLMap Usage|SME.6]]

### Have FILE privilege via sqlmap, want to read files or write a webshell
→ File reading: `--file-read "/path/to/file"`. sqlmap saves the content locally at `~/.local/share/sqlmap/output/<host>/files/` (path separator `/` becomes `_` in filename)
→ Webshell writing: `--os-shell --technique=E`. Using `--technique=E` (error-based) avoids the slow SLEEP-based timing of time-blind, making the stager upload faster. If sqlmap can't auto-detect the web root, add `--web-root "/var/www/html"`
→ See [[10. SQL Injection Attacks#10.3.3. Advanced SQLMap Usage|SME.7]], [[SQL Injection & Databases#Sqlmap. OS Exploitation|Command Appendix]]
## External Resources

- [HackTricks - Pentesting Index](https://hacktricks.wiki/en/index.html)
- [PayloadsAllTheThings - Methodology and Resources](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Methodology%20and%20Resources)
- [RevShells](https://www.revshells.com/) for shell troubleshooting
- [CyberChef](https://gchq.github.io/CyberChef/) for transformations
- [ippsec.rocks](https://ippsec.rocks/) for walkthrough searches
## Why this matters for OSCP

This page turns one repeatable part of an authorized assessment into a checklist you can apply under exam time pressure.

## Related Modules

- [[MODULES/10. SQL Injection Attacks]] -- module concepts used by this hub page

## Demonstrated in box write-ups

- [[OSCP/BOXES/WRITE UPS/Linux/Sea|Sea]] -- demonstrates the workflow described here
