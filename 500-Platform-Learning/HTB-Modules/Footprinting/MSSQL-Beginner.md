---
tags: [module/footprinting, mssql, database, sql, windows, level/beginner]
---

# MSSQL Enumeration - Beginner's Guide

## What is MSSQL?

Microsoft SQL Server (MSSQL) is Microsoft's relational database management system. Unlike MySQL (open source), MSSQL is closed source and primarily designed for Windows environments, though it can run on Linux now.

Think of it as Microsoft's enterprise-grade database solution, commonly used with .NET applications.

---

## Where You'll Find MSSQL

- Windows servers running Microsoft applications
- .NET web applications
- Enterprise environments with Microsoft infrastructure
- Often paired with ASP.NET or IIS
- Part of the Microsoft ecosystem (Active Directory integration)

---

## MSSQL vs MySQL

| Feature | MSSQL | MySQL |
|---------|-------|-------|
| Developer | Microsoft | Oracle |
| Open Source | No | Yes (Community Edition) |
| Platform | Primarily Windows | Cross-platform |
| Language | T-SQL | SQL |
| Authentication | Windows Auth, SQL Auth | Username/password |
| Default Port | 1433 | 3306 |
| Common Use | Enterprise, .NET apps | Web apps, LAMP stack |

---

## MSSQL Clients

Several tools can connect to MSSQL:

| Client | Description |
|--------|-------------|
| SSMS (SQL Server Management Studio) | Official GUI client (Windows only) |
| mssql-cli | Command-line tool (cross-platform) |
| SQL Server PowerShell | PowerShell modules |
| HeidiSQL | Free GUI (Windows) |
| SQLPro | GUI for Mac |
| Impacket's mssqlclient.py | Pentester favorite (Python) |

### Finding mssqlclient.py on Kali

locate mssqlclient

/usr/bin/impacket-mssqlclient
/usr/share/doc/python3-impacket/examples/mssqlclient.py

---

## Default MSSQL Databases

| Database | Purpose |
|----------|---------|
| master | Tracks all system information |
| model | Template for new databases |
| msdb | Used by SQL Server Agent for jobs/alerts |
| tempdb | Stores temporary objects |
| resource | Read-only system objects |

---

## Default Configuration

- Default port: TCP 1433
- Default instance name: MSSQLSERVER
- DAC (Dedicated Admin Connection) port: 1434
- Named pipes: `\\SERVERNAME\pipe\sql\query`
- Windows Authentication is default
- Encryption is NOT enforced by default

---

## Authentication Modes

### Windows Authentication (Default)
- Uses Windows credentials
- Integrated with Active Directory
- No separate SQL password
- More secure, uses Kerberos/NTLM

### SQL Server Authentication
- Separate username/password
- "sa" is the system administrator account
- Credentials stored in SQL Server
- Passwords sent over network (unless encrypted)

---

## Dangerous MSSQL Settings

| Setting | Risk |
|---------|------|
| Default "sa" account enabled | Well-known target, weak passwords common |
| No encryption | Credentials sent in plaintext |
| Self-signed certificates | Can be spoofed |
| Named pipes enabled | Additional attack surface |
| xp_cmdshell enabled | Command execution on server |
| SQL Server Agent jobs | Can be abused for persistence |
| Weak service account | If SQL runs as LOCAL SYSTEM or ADMIN |

---

## Connecting to MSSQL

### Using Impacket's mssqlclient.py

python3 mssqlclient.py Administrator@10.129.201.248 -windows-auth

Password: 
[*] Encryption required, switching to TLS
[*] ENVCHANGE(DATABASE): Old Value: master, New Value: master
[*] INFO(SQL-01): Line 1: Changed database context to 'master'.
SQL>

### Basic SQL Commands

-- List all databases
SELECT name FROM sys.databases;

-- Switch to a database
USE master;

-- List tables in current database
SELECT * FROM INFORMATION_SCHEMA.TABLES;

-- Get current user
SELECT CURRENT_USER;

-- Get server version
SELECT @@VERSION;

---

## MSSQL vs MySQL Commands

| Action | MySQL | MSSQL |
|--------|-------|-------|
| Show databases | SHOW DATABASES; | SELECT name FROM sys.databases; |
| Show tables | SHOW TABLES; | SELECT * FROM INFORMATION_SCHEMA.TABLES; |
| Current user | SELECT USER(); | SELECT CURRENT_USER; |
| Version | SELECT VERSION(); | SELECT @@VERSION; |

---

## Key Takeaways

- MSSQL runs on port 1433 by default
- Windows Authentication is default (uses AD)
- "sa" account is the superuser (often targeted)
- xp_cmdshell can enable command execution
- Default databases contain system info
- Named pipes provide alternate access
- Impacket's mssqlclient.py is the pentester's choice
- Always check for weak/default credentials
- MSSQL can be a foothold into Windows domains
- Configuration mistakes are common in enterprise
