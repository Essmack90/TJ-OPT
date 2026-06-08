---
tags: [module/footprinting, oracle, tns, database, level/beginner]
---

# Oracle TNS Enumeration - Beginner's Guide

## What is Oracle TNS?

Oracle TNS (Transparent Network Substrate) is a communication protocol that enables communication between Oracle databases and applications over networks. Think of it as Oracle's way of letting clients talk to databases.

It's commonly found in enterprise environments like healthcare, finance, and retail where large, complex databases are used.

---

## Key Concepts

### TNS Listener
- Listens for incoming database connections
- Default port: TCP 1521
- Routes client requests to the appropriate database instance

### SID (System Identifier)
- Unique name that identifies a specific database instance
- Clients must know the correct SID to connect
- Like a database's name or ID

### Service Name
- Alternative way to identify a database
- Defined in tnsnames.ora
- More flexible than SID

---

## Oracle TNS Default Configuration

### Main Configuration Files

| File | Location | Purpose |
|------|----------|---------|
| tnsnames.ora | $ORACLE_HOME/network/admin | Client-side configuration |
| listener.ora | $ORACLE_HOME/network/admin | Server-side listener config |

### tnsnames.ora Example

ORCL =
  (DESCRIPTION =
    (ADDRESS_LIST =
      (ADDRESS = (PROTOCOL = TCP)(HOST = 10.129.11.102)(PORT = 1521))
    )
    (CONNECT_DATA =
      (SERVER = DEDICATED)
      (SERVICE_NAME = orcl)
    )
  )

This defines a service called ORCL that points to 10.129.11.102:1521 with service name orcl.

### listener.ora Example

LISTENER =
  (DESCRIPTION_LIST =
    (DESCRIPTION =
      (ADDRESS = (PROTOCOL = TCP)(HOST = orcl.inlanefreight.htb)(PORT = 1521))
    )
  )

SID_LIST_LISTENER =
  (SID_LIST =
    (SID_DESC =
      (SID_NAME = PDB1)
      (ORACLE_HOME = C:\oracle\product\19.0.0\dbhome_1)
    )
  )

---

## Important tnsnames.ora Parameters

| Parameter | Description |
|-----------|-------------|
| PROTOCOL | Network protocol (TCP, IPC, etc.) |
| HOST | Server hostname or IP |
| PORT | Listener port (default 1521) |
| SERVICE_NAME | Database service name |
| SID | Database instance identifier |
| SERVER | Connection type (dedicated/shared) |
| USER | Username for authentication |
| PASSWORD | Password for authentication |
| SECURITY | Security type for connection |
| CONNECT_TIMEOUT | Connection timeout in seconds |

---

## Default Oracle Credentials

| Version | Default Username | Default Password |
|---------|------------------|------------------|
| Oracle 9 | sys/change_on_install | CHANGE_ON_INSTALL |
| Oracle 9 | system/manager | manager |
| Oracle 10+ | No default password | N/A |
| Oracle DBSNMP | dbsnmp | dbsnmp |
| Oracle | scott | tiger |

---

## Dangerous Oracle Settings

| Setting | Risk |
|---------|------|
| Default passwords | Easy to guess |
| Remote management enabled | Can be managed remotely |
| Weak SID naming | Easy to guess SIDs |
| Unencrypted connections | Credentials sent in plaintext |
| Excessive privileges | Users with DBA rights |
| PL/SQL exclusion list missing | Can execute dangerous packages |

---

## Installing Oracle Tools on Kali

### Install ODAT (Oracle Database Attacking Tool)

sudo apt-get update
sudo apt-get install -y build-essential python3-dev libaio1
git clone https://github.com/quentinhardy/odat.git
cd odat
pip install python-libnmap
git submodule init
git submodule update
sudo apt-get install python3-scapy -y
sudo pip3 install colorlog termcolor passlib python-libnmap
sudo apt-get install build-essential libgmp-dev -y
pip3 install pycryptodome

### Test ODAT Installation

./odat.py -h

---

## Basic Oracle Enumeration

### Nmap Scan

nmap -p1521 -sV 10.129.204.235 --open

Output:
PORT     STATE SERVICE    VERSION
1521/tcp open  oracle-tns Oracle TNS listener 11.2.0.2.0

### Enumerate SIDs

SIDs are like database names. You need the correct SID to connect.

nmap --script oracle-sid-brute -p1521 10.129.204.235

Output:
| oracle-sid-brute: 
|_  XE

Found SID: XE

---

## Connecting to Oracle Database

### Using sqlplus

sqlplus username/password@10.129.204.235/XE

Example:
sqlplus scott/tiger@10.129.204.235/XE

### Common Connection Errors

Error: sqlplus: error while loading shared libraries: libsqlplus.so

Fix:
sudo sh -c "echo /usr/lib/oracle/12.2/client64/lib > /etc/ld.so.conf.d/oracle-instantclient.conf"
sudo ldconfig

---

## Basic SQLPlus Commands

| Command | Description |
|---------|-------------|
| SELECT * FROM tab; | List all tables |
| SELECT table_name FROM all_tables; | List tables |
| SELECT * FROM user_role_privs; | Check user privileges |
| SELECT name, password FROM sys.user$; | Extract password hashes |
| DESCRIBE table_name; | Show table structure |
| EXIT | Exit sqlplus |

---

## Key Takeaways

- Oracle TNS runs on port 1521 by default
- SID identifies the database instance (must be guessed)
- Default credentials (scott:tiger, dbsnmp:dbsnmp) are common
- ODAT is the best tool for Oracle enumeration
- sqlplus is the official Oracle client
- SIDs can be brute-forced with nmap scripts
- Once connected, check user privileges
- Password hashes stored in sys.user$
- File upload possible if you have privileges
- Oracle often found in enterprise environments
