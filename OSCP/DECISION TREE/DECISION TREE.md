# OSCP Decision Tree

Quick "I found X, what do I try" lookup. Skim for whatever's in front of you right now, follow the link for the full walkthrough.

Covers Modules 6 through 19, plus HTB supplementary modules. Will grow as later modules get added.

Already know which tool you want and just need exact syntax? See [[COMMAND APPENDIX]] instead. Need the full phase-by-phase methodology? See [[METHODOLOGY CHEAT SHEET]].

Restructured 2026-08-04 from a single flat file into a folder split by area, same pattern as [[COMMAND APPENDIX]], [[COMMAND BREAKDOWNS]], and [[METHODOLOGY CHEAT SHEET]].

---

## Areas

- [[OSCP/BOXES/WRITE UPS/Windows/Buff|Buff route]] — when a web shell reveals a loopback-only service, forward only the required port, then route to the service-specific exploit.

- [[Common Applications (Decision Tree)|Common Applications]] — application discovery workflow (EyeWitness/Aquatone/vHost fuzz), per-app attack decision: WordPress (WPScan→xmlrpc brute→plugin LFI→theme/plugin RCE), Joomla (README.txt→template RCE), Drupal (CHANGELOG.txt→PHP Filter RCE), Tomcat (mgr brute→WAR RCE / Windows CGI CVE-2019-0232), Jenkins (Groovy Script Console), Splunk (app-install), PRTG (notification execute), GitLab (repo cred hunt→authenticated RCE), Shellshock (CGI User-Agent), ColdFusion (50057.py), IIS Tilde (shortname scanner→gobuster), LDAP wildcard bypass, mass assignment hidden param, gdb ODBC breakpoint, WebLogic MSF, Nagios XI RCE, dnSpy .NET credential extraction, osTicket ticket credential disclosure

- [[Reconnaissance & Enumeration (Decision Tree)|Reconnaissance & Enumeration]] — open ports, Nessus/Nmap CVE hits, scan troubleshooting, subdomain/vHost discovery, service attack tool routing table
- [[File Inclusion & Traversal (Decision Tree)|File Inclusion & Traversal]] — traversal parameter identification + bypass ladder (plain → URL-encoded → non-recursive `....//` → double URL-encoding), PHP source disclosure via php://filter (no allow_url_include needed), LFI-to-RCE option ladder (GIF upload + LFI → session poisoning → log poisoning → data:// → RFI), automated LFI discovery (ffuf param names + LFI-Jhaddix), upload+LFI chain with md5_file filename prediction
- [[File Upload Attacks (Decision Tree)|File Upload Attacks]] — step-by-step filter bypass ladder (absent → client-side → blacklist extension fuzzing → whitelist double/reverse-double extension → Content-Type header → MIME magic bytes), SVG-only upload path (XXE file read + php://filter source + SVG+PHP polyglot RCE), upload path discovery (source read, date-prefix convention), filename traversal when nothing executes
- [[Web Applications (Decision Tree)|Web Applications]] — web target enumeration flow (ffuf dir/ext/page/vhost/param/value chain), ffuf response filtering (-fs/-ac/-mr), HTTP Verb Tampering (OPTIONS/PATCH for basic auth bypass; GET swap for POST-only filter bypass), IDOR (user-controlled ID in URL/param → mass enumerate; encoded refs → reproduce base64/MD5 client-side; API path IDOR; chain read→write for privilege escalation + verb tamper the write endpoint if Access Denied), XXE (XML body → entity injection; basic file read; php://filter base64 for PHP source; CDATA external DTD for XML-breaking chars; error-based no-reflection leak; blind OOB with python HTTP server callback), XSS triage (Stored/Reflected/DOM identification; what to do with confirmed XSS: phishing form vs cookie steal; blind XSS per-field fingerprinting via unique nc filenames + HeadlessChrome UA; filter bypass approaches), command injection filter bypass ladder (blocked operator → try `%0a`/`%26`; space filter → `$IFS`/`%09`; slash filter → `${PATH:0:1}`; command blacklist → quote insertion; all filters → base64 + here-string; error-based output channel), vhost pivots, WordPress, REST APIs
- [[SQL Injection & Databases (Decision Tree)|SQL Injection & Databases]] — MySQL/MSSQL/PostgreSQL injection, error-based/blind/stacked-query triage, parenthesis-closing auth bypass variant, incremental UNION column count method, sqlmap injection point detection (*/cookie/JSON/-r file), sqlmap WAF bypass stack (--random-agent/--tamper/--level/--risk), CSRF token auto-refresh (--csrf-token), FILE privilege chain (--file-read/--os-shell --technique=E)
- [[Shells & Payloads (Decision Tree)|Shells & Payloads]] — reverse shell delivery, bind shell (NAT/firewall bypass), Tomcat WAR deployment, MSF session chaining, listener troubleshooting
- [[Secrets & Credentials (Decision Tree)|Secrets & Credentials]] — private key extraction, hash type decisions (NTLM vs Net-NTLMv2), PtH vs relay vs crack, Credential Guard bypass, kerbrute AD enum, Pass-the-Ticket (Windows kirbi/Linux ccache), Pass-the-Certificate (pywhisker+PKINIT), NTDS VSS dump, Responder/relay troubleshooting
- [[Service Attacks (Decision Tree)|Service Attacks]] — MSSQL full chain (xp_cmdshell → xp_dirtree coercion → impersonation → linked server), FTP chain (anonymous → write → CoreFTP CVE-2022-22836), SMB null session → relay, SMTP/POP3 email service attacks
- [[Phishing (Decision Tree)|Phishing]] — website cloning, clone-patching gotchas, credential-capture delivery, pretext-building
- [[Client-Side Attacks (Decision Tree)|Client-Side Attacks]] — macro autorun troubleshooting, one-shot watcher scripts, Windows library file WebDAV rewriting, `.lnk` hiding tricks
- [[Locating Public Exploits (Decision Tree)|Locating Public Exploits]] — exploits with hardcoded ports, misidentified products from banner alone, patator's 0/0/0/0/0 gotcha, CSRF-protected brute forcing
- [[Fixing Exploits (Decision Tree)|Fixing Exploits]] — Windows-only exploit source on Kali, confusing downstream errors after a successful step
- [[Buffer Overflow & Memory Corruption (Decision Tree)|Buffer Overflow & Memory Corruption]] — rotated EIP values, target crashes mid-exploit, missing/wrong return addresses, multiple candidate exploits
- [[Windows Privilege Escalation (Decision Tree)|Windows Privilege Escalation]] — service vector triage (binary hijack / DLL hijack / unquoted path), scheduled task attacks, kernel exploit triage, privilege triage (SeImpersonatePrivilege / SeBackupPrivilege), WinRM vs nc shell access differences, **HTB additions**: full privilege-to-technique table (SeDebug/SeTakeOwnership/SeLoadDriver), built-in group attack table (Event Log Readers/DnsAdmins/Print Operators/Server Operators), Windows credential hunting checklist (findstr→unattend.xml→Sticky Notes→cmdkey→LaZagne→SharpChrome→SessionGopher→mRemoteNG), SCF file attack for hash capture, old-OS triage (Sherlock/windows-exploit-suggester/MS10-092/MS16-032), CVE quick reference (HiveNightmare/PrintNightmare), Citrix breakout flow
- [[Linux Privilege Escalation (Decision Tree)|Linux Privilege Escalation]] — fast-win checklist order (env/dotfiles/sudo/SUID/capabilities/cron//etc/passwd/kernel), sudo binary GTFOBins table, SUID binary GTFOBins table, cron exploitability triage, kernel/binary CVE quick reference (CVE-2021-3493 overlayfs / CVE-2022-0847 DirtyPipe / CVE-2021-4034 PwnKit / CVE-2019-14287 sudo -u#-1 / GNU Screen 4.5.0), **HTB additions**: group membership attack table (adm/docker/lxd/disk/shadow), restricted shell escape flow, sudo env_keep+LD_PRELOAD injection, sudo -u#-1 (CVE-2019-14287), PATH abuse, LXD container escape, docker group chroot escape, NFS no_root_squash, shared object hijacking via writable RUNPATH, Python library hijacking, fast-win checklist extension rows
- [[Port Redirection and SSH Tunneling (Decision Tree)|Port Redirection and SSH Tunneling]] — which pivot technique fits (Socat/SSH -L/-D/-R/sshuttle on Linux; ssh.exe/Plink/Netsh on Windows), inbound-vs-outbound firewall triage, proxychains gotchas (-sT/-Pn/-n requirement, socks4/socks5 drift), PTY-before-SSH checklist, port conflict fixes; Meterpreter MSF-native pivot (autoroute + socks_proxy); protocol-restricted environments table (HTTP → Rpivot/Chisel, DNS → Dnscat2, ICMP → ptunnel-ng, RDP-only → SocksOverRDP)

- [[Active Directory (Decision Tree)|Active Directory]] — which spray tool to use from Linux vs Windows (kerbrute/crackmapexec/Spray-Passwords.ps1/DomainPasswordSpray), ACE-type to attack mapping (GenericAll/GenericWrite/ForceChangePassword/Self-Membership/WriteDACL), DA rights dump priority, child→parent ExtraSids decision (WITHIN_FOREST vs FOREST_TRANSITIVE), cross-forest attack options (Kerberoasting/credential reuse), NoPac applicability check (MachineAccountQuota + patch level), bloodhound-python vs SharpHound choice, service account NTLM hash decision (silver ticket vs PtH vs crack), KRB_AP_ERR_SKEW resolution (clock sync order to avoid killing VPN), Rubeus failure over evil-winrm (NTLM session = no TGT = use impacket instead), BUILTIN\Administrators "deny only" routing (UAC-filtered token — elevate locally or spray creds to find unfiltered admin elsewhere), cached Kerberos tickets from other logged-on users (sekurlsa::tickets /export + Group 0 vs Group 2 kirbi injection)

- [[Cloud Enumeration (Decision Tree)|Cloud Enumeration]] — domain → cloud hosting triage (awsdns NS = Route53, dig TXT for hidden data in SPF records, dnsenum subdomain brute), S3 bucket access triage (XML = open / AccessDenied = private / NoSuchBucket; direct object access bypasses listing ACL), cross-account enumeration without creds (AMI OwnerId = account ID, s3:ResourceAccount binary-search oracle, trust policy oracle via Pacu iam__enum_roles), post-compromise IAM triage (identity → scope → full dump with get-account-authorization-details), dangerous permission to privesc path routing (CreateAccessKey/CreateLoginProfile/AttachPolicy/PassRole vectors), assumed-role resource discovery

---

## General Patterns Worth Remembering

- **Three-hop access: Kali → pivot1 → pivot2 → target.** SSH alone can't get you there in one shot. Pattern: `ssh -L LOCAL:pivot2:PORT root@pivot1` for direct service access to pivot2 + `ssh -R PIVOT2_PORT:PWNIP:HANDLER_PORT root@pivot1` to let the second pivot call back through pivot1 to Kali. Then meterpreter autoroute on the callback session adds the third subnet to MSF's routing table. Assembled in [[27. Assembling the Pieces|AEN.10]] to reach 172.16.9.0/23 via DC01 via DMZ01.

- **A filter blocking `../` isn't blocking traversal.** Encoding (`%2e%2e/`, base64, etc) is the standard way past a filter that only checks literal plaintext. Shows up in 9.1.3, 9.2.2, and 9.3.1, always the same underlying idea.
- **Automated tool flags a vuln → confirm it manually.** Nessus/Nmap NSE finding something isn't proof it's exploitable. `curl` the disclosed PoC yourself. See [[07. Vulnerability Scanning#7.4. Wrapping Up|7.4]].
- **Check privilege level the moment you land a shell.** Don't assume you need privesc, training VMs frequently run services as root/SYSTEM already.
- **When a module's exact demo payload doesn't reproduce**, check whether an earlier tool/scan already disclosed the actual working PoC pattern before just varying parameters blindly.
- **A request to a reused hostname comes back empty/silent.** Check `/etc/hosts` before assuming the vuln itself isn't working. If the same hostname (e.g. `mountaindesserts.local`) gets reused across multiple labs in a module, it's easy to leave it pointed at an earlier box's stale IP. `grep <hostname> /etc/hosts` and fix with `sed -i` if needed. See [[09. Common Web Application Attacks#9.3.2. Using Non-Executable Files|9.3.2]] for where this bit us.
- **A `curl -X POST --data` payload with `&`, `=`, `+`, or spaces fails or gets truncated for no obvious reason.** `--data` sends the value raw, so those characters get reinterpreted by the server (`&`/`=` as form-field separators, `+` as a literal space per `application/x-www-form-urlencoded` rules). Switch to `--data-urlencode`, which percent-encodes automatically. Bit us with a reverse shell one-liner containing `>&`/`0>&1` in [[09. Common Web Application Attacks#9.4.1. OS Command Injection|9.4.1]], and again with a base64-encoded payload (base64 routinely contains `+`) in [[10. SQL Injection Attacks#Capstone: Exercise VM #3|Capstone Labs, VM #3]]. See [[SQL Injection (Breakdowns)#Why a base64 payload sent via curl --data silently corrupts (+ becomes a space)|Command Breakdowns]] for the full mechanics.
- **A lab question asks about specific code details (variable names, field names) and a module's generic example answer gets rejected.** The module's illustrative code snippet is often just an example, not a verbatim copy of the actual lab VM's source. Check the live app's real form field names (`curl` the page, or view source) instead of assuming the textbook variable names apply exactly. Bit us in [[10. SQL Injection Attacks#10.2.1. Identifying SQLi via Error-Based Payloads|10.2.1]] (`$uname` in the module vs. the actual `$uid`/`name="uid"` on the VM).
## External Resources

- [HackTricks - Pentesting Index](https://hacktricks.wiki/en/index.html)
- [PayloadsAllTheThings - Methodology and Resources](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Methodology%20and%20Resources)
- [RevShells](https://www.revshells.com/) for shell troubleshooting
- [CyberChef](https://gchq.github.io/CyberChef/) for transformations
- [ippsec.rocks](https://ippsec.rocks/) for walkthrough searches
## Why this matters for OSCP

This page turns one repeatable part of an authorized assessment into a checklist you can apply under exam time pressure.

## Related Modules

- [[MODULES/06. Information Gathering]] -- module concepts used by this hub page

## Demonstrated in box write-ups

- [[OSCP/BOXES/WRITE UPS/AD/Forest|Forest]] -- demonstrates the workflow described here
- [[OSCP/BOXES/WRITE UPS/Windows/Buff|Buff]] -- demonstrates the web foothold → internal service → port-forward → BOF decision path
