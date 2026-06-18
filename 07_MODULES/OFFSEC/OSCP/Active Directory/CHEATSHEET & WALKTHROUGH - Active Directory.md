# Active Directory Enumeration - Cheat Sheet & Walkthrough

## Table of Contents
1. [Active Directory Introduction](#1-active-directory-introduction)
2. [Manual Enumeration](#2-manual-enumeration)
3. [Automated Enumeration](#3-automated-enumeration)
4. [Quick Reference](#4-quick-reference)

---

## 1. Active Directory Introduction

### 1.1 Active Directory Core Concepts

#### AD Objects

| Object Type | Description | Examples |
|-------------|-------------|----------|
| **Users** | Domain accounts | stephanie, jeffadmin |
| **Computers** | Domain-joined machines | CLIENT75, DC1 |
| **Groups** | Collections of objects | Domain Admins |
| **OUs** | Organizational Units | Sales Department |
| **Attributes** | Object properties | First name, last name |

#### Key AD Groups

| Group | Privilege Level | Description |
|-------|-----------------|-------------|
| **Domain Admins** | Highest | Full control over the domain |
| **Enterprise Admins** | Highest (Forest-wide) | Full control over all domains |
| **Administrators** | High | Built-in admin group |
| **Domain Users** | Low | Regular users |

#### AD Structure
```
Domain Forest (corp.com)
    ├── Domain Tree
    │   └── corp.com
    │       ├── Organizational Units (OUs)
    │       │   ├── Sales Department
    │       │   ├── Management Department
    │       │   └── Development Department
    │       ├── Users
    │       │   ├── stephanie
    │       │   ├── jeffadmin
    │       │   └── ...
    │       ├── Computers
    │       │   ├── CLIENT75
    │       │   ├── DC1
    │       │   └── ...
    │       └── Groups
    │           ├── Domain Admins
    │           └── ...
```

### 1.2 Enumeration Goals

- Identify high-value targets (Domain Admins)
- Map user/group relationships
- Find misconfigured permissions
- Discover service accounts
- Locate sensitive data

---

## 2. Manual Enumeration

### 2.1 Legacy Windows Tools (net.exe)

#### Domain Users
```cmd
# List all domain users
net user /domain

# Get specific user info
net user jeffadmin /domain
```

#### Domain Groups
```cmd
# List all groups
net group /domain

# Get group members
net group "Sales Department" /domain
```

#### Key net.exe Flags
| Flag | Purpose |
|------|---------|
| `/domain` | Query domain (not local) |
| `/add` | Add user/group |
| `/del` | Delete user/group |

---

### 2.2 PowerShell & .NET LDAP Queries

#### Domain Object
```powershell
# Get domain object
$domainObj = [System.DirectoryServices.ActiveDirectory.Domain]::GetCurrentDomain()
$domainObj.PdcRoleOwner.Name
```

#### ADSI Distinguished Name
```powershell
# Get DN
$DN = ([adsi]'').distinguishedName
```

#### Build LDAP Path
```powershell
$PDC = [System.DirectoryServices.ActiveDirectory.Domain]::GetCurrentDomain().PdcRoleOwner.Name
$DN = ([adsi]'').distinguishedName 
$LDAP = "LDAP://$PDC/$DN"
```

#### DirectoryEntry & DirectorySearcher
```powershell
$direntry = New-Object System.DirectoryServices.DirectoryEntry($LDAP)
$dirsearcher = New-Object System.DirectoryServices.DirectorySearcher($direntry)
$dirsearcher.filter="samAccountType=805306368"
$result = $dirsearcher.FindAll()
```

#### samAccountType Values
| Value (Decimal) | Value (Hex) | Object Type |
|-----------------|-------------|-------------|
| 805306368 | 0x30000000 | User |
| 805306369 | 0x30000001 | Computer |
| 268435456 | 0x10000000 | Group |

#### Full LDAP Search Function
```powershell
function LDAPSearch {
    param ([string]$LDAPQuery)
    $PDC = [System.DirectoryServices.ActiveDirectory.Domain]::GetCurrentDomain().PdcRoleOwner.Name
    $DN = ([adsi]'').distinguishedName
    $direntry = New-Object System.DirectoryServices.DirectoryEntry("LDAP://$PDC/$DN")
    $dirsearcher = New-Object System.DirectoryServices.DirectorySearcher($direntry, $LDAPQuery)
    return $dirsearcher.FindAll()
}
```

#### Usage Examples
```powershell
# All users
LDAPSearch -LDAPQuery "(samAccountType=805306368)"

# All groups
LDAPSearch -LDAPQuery "(objectClass=group)"

# Specific user
LDAPSearch -LDAPQuery "(name=jeffadmin)"

# Specific group members
$group = LDAPSearch -LDAPQuery "(&(objectCategory=group)(cn=Sales Department))"
$group.properties.member
```

### 2.3 PowerView

#### Import PowerView
```powershell
Import-Module .\PowerView.ps1
```

#### Domain Information
```powershell
# Domain info
Get-NetDomain

# Domain controllers
Get-NetDomainController

# Domain users
Get-NetUser
Get-NetUser | select cn

# Specific attributes
Get-NetUser | select cn,pwdlastset,lastlogon

# Computers
Get-NetComputer
Get-NetComputer | select operatingsystem,dnshostname
Get-NetComputer | select operatingsystemversion

# Groups
Get-NetGroup
Get-NetGroup "Sales Department" | select member

# Group memberships
Get-NetUser jeffadmin | select memberof
```

#### SPN Enumeration
```powershell
# SPN accounts
Get-NetUser -SPN | select samaccountname,serviceprincipalname

# SID to name
Convert-SidToName S-1-5-21-1987370270-658905905-1781884369-1104
```

#### Session & Permission Enumeration
```powershell
# Local admin access
Find-LocalAdminAccess

# Sessions
Get-NetSession -ComputerName client74

# Object ACLs
Get-ObjectAcl -Identity stephanie
Get-ObjectAcl -Identity "Management Department" | 
    Where-Object {$_.ActiveDirectoryRights -eq "GenericAll"} |
    select SecurityIdentifier,ActiveDirectoryRights

# Domain shares
Find-DomainShare
```

#### SYSVOL Enumeration
```powershell
# List SYSVOL
ls \\dc1.corp.com\sysvol\corp.com\

# Check policies
ls \\dc1.corp.com\sysvol\corp.com\Policies\

# View GPP files
cat \\dc1.corp.com\sysvol\corp.com\Policies\oldpolicy\old-policy-backup.xml
```

#### GPP Password Decryption
```bash
# Kali tool
gpp-decrypt "+bsY0V3d4/KgX3VJdO/vyepPfAN1zMFTiQDApgR92JE"
```

---

## 3. Automated Enumeration

### 3.1 SharpHound

#### Import SharpHound
```powershell
Import-Module .\SharpHound.ps1
```

#### Collection Methods
| Method | Description |
|--------|-------------|
| All | Everything except GPOLocalGroup |
| Default | Group, LocalAdmin, Session, Trusts, ACL |
| Session | Logged-on sessions |
| ACL | Access control lists |
| Group | Group memberships |
| LocalAdmin | Local admin privileges |
| Trusts | Domain trusts |

#### Run SharpHound
```powershell
# All data collection
Invoke-BloodHound -CollectionMethod All -OutputDirectory C:\Users\stephanie\Desktop\ -OutputPrefix "corp audit"

# Default collection
Invoke-BloodHound -CollectionMethod Default

# Loop collection (continuous)
Invoke-BloodHound -Loop -LoopDuration 02:00:00 -LoopInterval 00:30:00
```

#### Output Files
- `*.zip` - Compressed JSON data
- `*.bin` - Cache file

### 3.2 BloodHound

#### Start Neo4j
```bash
# Start service
sudo neo4j start

# Default credentials: neo4j:neo4j
# Change password on first login
```

#### Start BloodHound
```bash
bloodhound
```

#### Key Features

**Analysis Queries**:
- Find all Domain Admins
- Find Shortest Paths to Domain Admins
- Find Shortest Paths from Owned Principals
- Find Computers with Unsupported OS
- Find Users with Kerberoastable SPNs

#### Mark Objects as Owned
1. Search for object
2. Right-click node
3. Select "Mark User/Computer as Owned"
4. Skull icon appears

#### Node Information
- **Node Info**: Object properties and attributes
- **Inbound Control Rights**: Who controls this object
- **Outbound Control Rights**: What this object controls
- **Abuse**: How to exploit relationships
- **Opsec**: Detection risks

---

## 4. Quick Reference

### AD Enumeration Command Cheat Sheet

#### Users
```cmd
net user /domain
net user jeffadmin /domain
```

```powershell
# PowerView
Get-NetUser
Get-NetUser | select cn,lastlogon,pwdlastset
```

#### Groups
```cmd
net group /domain
net group "Sales Department" /domain
```

```powershell
# PowerView
Get-NetGroup
Get-NetGroup "Sales Department" | select member
```

#### Computers
```powershell
Get-NetComputer
Get-NetComputer | select dnshostname,operatingsystem
```

#### Sessions
```cmd
# PsLoggedOn
.\PsLoggedon.exe \\client74
```

```powershell
# PowerView (may fail on modern systems)
Get-NetSession -ComputerName files04
```

#### SPNs
```cmd
setspn -L iis_service
```

```powershell
Get-NetUser -SPN | select samaccountname,serviceprincipalname
```

#### ACLs
```powershell
Get-ObjectAcl -Identity stephanie
Get-ObjectAcl -Identity "Management Department" | 
    Where-Object {$_.ActiveDirectoryRights -eq "GenericAll"}
```

#### Shares
```powershell
Find-DomainShare
ls \\FILES04\docshare
```

---

### Key AD Attributes

| Attribute | Purpose |
|-----------|---------|
| `samAccountType` | Object type (user/computer/group) |
| `memberOf` | Group memberships |
| `servicePrincipalName` | SPN association |
| `pwdLastSet` | Last password change |
| `lastLogon` | Last login time |
| `operatingSystem` | OS version |
| `dnshostname` | Computer hostname |

---

### Permission Types

| Permission | Description |
|------------|-------------|
| `GenericAll` | Full control (most powerful) |
| `GenericWrite` | Edit attributes |
| `WriteOwner` | Change ownership |
| `WriteDACL` | Edit ACLs |
| `AllExtendedRights` | Reset password |
| `ForceChangePassword` | Password change |

---

### Key Takeaways

| Concept | Key Point |
|---------|-----------|
| **Domain Controllers** | Core of AD, store all objects |
| **LDAP** | Protocol for AD communication |
| **SYSVOL** | Accessible by all users |
| **GPP** | Can contain decrypted passwords |
| **SPNs** | Service accounts with higher privileges |
| **ACLs** | Object permissions |
| **Nested Groups** | Groups within groups |
| **BloodHound** | Visual AD relationship mapping |