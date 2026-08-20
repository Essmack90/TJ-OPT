# Kerbrute

Fast Kerberos-based username enumeration and password spraying against Active Directory. Uses the AS-REQ pre-authentication flow to determine whether a username exists in the domain, without triggering account lockout for userenum.

---

## What it replaces, and why it's faster

[[Information Gathering]] and [[Password Attacks]] teach SMB-based credential verification (hydra, nxc smb). Kerbrute is faster for AD work specifically because it talks directly to Kerberos (port 88) rather than SMB, which means no NTLM negotiation overhead, no SMB session setup, and much higher request throughput. More importantly, `userenum` does NOT count against lockout policy because it sends pre-auth requests rather than full authentication attempts.

## Install

```bash
# Already on Kali
kerbrute --help

# Or download latest binary from GitHub
wget https://github.com/ropnop/kerbrute/releases/latest/download/kerbrute_linux_amd64
chmod +x kerbrute_linux_amd64
sudo mv kerbrute_linux_amd64 /usr/local/bin/kerbrute
```

## Usage

```bash
# Username enumeration — NO lockout risk
kerbrute userenum -d <domain> --dc <DC-IP> /usr/share/seclists/Usernames/xato-net-10-million-usernames.txt

# Pipe in a custom list (e.g. from username-anarchy)
kerbrute userenum -d corp.local --dc 192.168.1.10 candidate_users.txt

# Password spray — DOES count toward lockout, use carefully
kerbrute passwordspray -d <domain> --dc <DC-IP> valid_users.txt 'Password123!'
kerbrute passwordspray -d <domain> --dc <DC-IP> valid_users.txt 'Summer2024!'

# Brute force a single user — counts toward lockout
kerbrute bruteuser -d <domain> --dc <DC-IP> valid_users.txt /usr/share/wordlists/rockyou.txt
```

**Output:**
- `VALID USERNAME` → Kerberos returned `KRB5KDC_ERR_PREAUTH_REQUIRED` (account exists, pre-auth required, normal)
- `VALID USERNAME (account does not require pre-authentication)` → AS-REP roastable user
- No output → account doesn't exist (Kerberos returned `KRB5KDC_ERR_C_PRINCIPAL_UNKNOWN`)

> 🔍 **Worth remembering:** `userenum` is safe to run aggressively. `passwordspray` is not, same rules as any spray: one password at a time, wait between rounds, stay under the lockout threshold (usually 5-10 attempts per account per observation window).

## Where this applies in the vault

- [[Active Directory Methodology#Step 1: Username Enumeration (before spraying)|AD Methodology, Phase 2 Step 1]]
- [[Password Attacks (HTB Supplementary)#PA.20 kerbrute — Kerberos Username Enumeration & Spray|PA.20]]
- [[Secrets & Credentials (Decision Tree)#Need to validate a list of potential AD usernames before spraying|Decision Tree]]

🔁 [[Password Attacks (HTB Supplementary)#PA.20 kerbrute|PA.20]], [[Active Directory Methodology]]

#### Tags: #ModernTooling #kerbrute #ActiveDirectory #Kerberos #UsernameEnumeration #PasswordSpray
