# Snaffler

A domain-aware file and share crawler that finds credentials, secrets, and sensitive data in accessible SMB shares, automatically filtering noise and prioritizing high-value finds.

---

## What it replaces, and why it's faster

Manual share enumeration (`smbclient //<host>/<share>`, `Get-ChildItem \\host\share -Recurse | Select-String "password"`) is slow and produces enormous output that's hard to triage. Snaffler runs from a domain-joined context, automatically enumerates all accessible shares across the domain, applies a set of rules to identify likely-valuable files (configs, scripts, `.git` repos, backup files, connection strings), and outputs colour-coded prioritised findings.

## Install

```bash
# Pre-built Windows .exe from GitHub releases:
# https://github.com/SnaffCon/Snaffler/releases
# Transfer to domain-joined target and run from there

# No Kali install — runs on the target
```

## Usage

```cmd
:: Standard run — scan all accessible domain shares, output to log file
.\Snaffler.exe -d <domain> -o snaffler.log -v data

:: If no domain name known, it will auto-discover from the current machine's domain membership
.\Snaffler.exe -o snaffler.log -v data

:: Limit to specific hosts (faster for known targets)
.\Snaffler.exe -n <host1>,<host2> -o snaffler.log -v data
```

**Flags:**
- `-d <domain>` → domain to enumerate (all DCs enumerated for shares)
- `-o <file>` → output log file (default: stdout only)
- `-v data` → verbosity level "data" shows file content previews for high-value finds

**Output priority levels** (colour coded):
- `[Black]` → highest priority, definite credentials or secrets
- `[Red]` → very likely sensitive
- `[Yellow]` / `[Green]` → lower confidence but worth reviewing

> 🔍 **Worth remembering:** Snaffler needs to run from a domain-joined Windows machine (or with domain credentials passed via `/u /p` flags) because it queries LDAP to discover computers and then connects to their shares. It won't work well from Kali directly without a SOCKS tunnel into the domain.

## Where this applies in the vault

- [[Active Directory Methodology#Step 1: Extract Credentials|AD Methodology, Phase 3 Step 1]]
- [[16. Password Attacks|PA.23]]

🔁 [[16. Password Attacks|PA.23]], [[Active Directory Methodology#Phase 3|AD Methodology Phase 3]]

#### Tags: #ModernTooling #Snaffler #ShareEnumeration #ActiveDirectory #CredentialHunting #FileSearch
