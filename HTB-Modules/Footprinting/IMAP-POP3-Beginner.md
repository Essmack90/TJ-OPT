---
tags: [module/footprinting, imap, pop3, email, mail-client, level/beginner]
---

# IMAP/POP3 Enumeration - Beginner's Guide

## What are IMAP and POP3?

IMAP and POP3 are protocols used to retrieve emails from a mail server. Think of them as the "receiving" part of email, while SMTP is the "sending" part.

---

## POP3 vs IMAP

| Feature | POP3 | IMAP |
|---------|------|------|
| Ports | 110 (plain), 995 (SSL) | 143 (plain), 993 (SSL) |
| Storage | Downloads emails to local device | Keeps emails on server |
| Synchronization | One-way (server → client) | Two-way (syncs across devices) |
| Folders | Local only | Server-side folders |
| Multiple devices | No (emails downloaded) | Yes (centralized) |
| Internet connection | Only needed to download | Required to access emails |

### When to Use Which

- **POP3**: You use one device, want to save server space, need offline access
- **IMAP**: You use multiple devices, need folders, want emails accessible everywhere

---

## How Email Works (Complete Picture)

1. **SMTP** sends email from your client to the server
2. **SMTP** transfers email between servers
3. **IMAP/POP3** retrieves email from server to your client

Client (MUA) → SMTP → Server → SMTP → Server → IMAP/POP3 → Client

---

## IMAP Commands

| Command | Description | Example |
|---------|-------------|---------|
| LOGIN | Authenticate user | 1 LOGIN username password |
| LIST | List all folders | 1 LIST "" * |
| LSUB | List subscribed folders | 1 LSUB "" * |
| CREATE | Create a folder | 1 CREATE "Work" |
| DELETE | Delete a folder | 1 DELETE "Spam" |
| RENAME | Rename a folder | 1 RENAME "Old" "New" |
| SELECT | Select a folder | 1 SELECT INBOX |
| UNSELECT | Exit current folder | 1 UNSELECT |
| FETCH | Retrieve email(s) | 1 FETCH 1 all |
| STORE | Modify email flags | 1 STORE 1 +FLAGS \Deleted |
| CLOSE | Remove deleted emails | 1 CLOSE |
| LOGOUT | End session | 1 LOGOUT |

**Note:** The numbers before commands are tags (can be any unique identifier).

---

## POP3 Commands

| Command | Description | Example |
|---------|-------------|---------|
| USER | Send username | USER robin |
| PASS | Send password | PASS robin123 |
| STAT | Get mailbox status | STAT |
| LIST | List emails with sizes | LIST |
| RETR | Retrieve email by ID | RETR 1 |
| DELE | Delete email by ID | DELE 1 |
| NOOP | Keep alive | NOOP |
| RSET | Undelete marked emails | RSET |
| QUIT | End session | QUIT |
| CAPA | Show server capabilities | CAPA |

---

## IMAP vs POP3 Ports

| Protocol | Plain Port | SSL/TLS Port |
|----------|------------|--------------|
| IMAP | 143 | 993 |
| POP3 | 110 | 995 |

---

## Connecting to Mail Servers

### POP3 (Plain)

telnet 10.129.14.128 110
USER robin
PASS robin
STAT
LIST
RETR 1
QUIT

### POP3 (SSL)

openssl s_client -connect 10.129.14.128:995 -quiet
USER robin
PASS robin
STAT
LIST
QUIT

### IMAP (Plain)

telnet 10.129.14.128 143
1 LOGIN robin robin
2 LIST "" *
3 SELECT INBOX
4 FETCH 1 all
5 LOGOUT

### IMAP (SSL)

openssl s_client -connect 10.129.14.128:993 -quiet
1 LOGIN robin robin
2 LIST "" *
3 SELECT INBOX
4 FETCH 1 all
5 LOGOUT

---

## Dangerous IMAP/POP3 Settings

| Setting | Description | Risk |
|---------|-------------|------|
| auth_debug | Logs authentication details | Credentials in logs |
| auth_debug_passwords | Logs passwords | Plaintext passwords in logs |
| auth_verbose | Logs failed attempts | User enumeration possible |
| auth_verbose_passwords | Logs passwords used | Credential exposure |
| auth_anonymous_username | Allows anonymous login | No auth needed |

---

## Reading Emails with curl

### List Folders (IMAP)

curl -k 'imaps://10.129.14.128' --user robin:robin

* LIST (\HasNoChildren) "." Important
* LIST (\HasNoChildren) "." INBOX

### Verbose Connection

curl -k 'imaps://10.129.14.128' --user robin:robin -v

Shows:
- TLS version
- Certificate details
- Server banner (often reveals version)
- Capabilities

---

## Key Takeaways

- POP3 downloads emails, IMAP syncs them
- Ports: 110/995 (POP3), 143/993 (IMAP)
- POP3 is simpler but limited
- IMAP supports folders and multiple devices
- Always check for credentials (robin:robin is common)
- SSL certificates reveal server hostnames
- Server banners reveal version information
- Failed logins may be logged (user enumeration)
- Anonymous authentication might be enabled
- Emails contain sensitive information
