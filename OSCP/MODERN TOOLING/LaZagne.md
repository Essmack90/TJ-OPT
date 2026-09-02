# LaZagne

An automated, multi-application credential extractor for Windows (and Linux). Queries browser credential stores, databases, mail clients, SSH agents, Windows Credential Manager, and more in one pass.

---

## What it replaces, and why it's faster

Manually hunting for saved credentials across browsers, databases, and system stores is a multi-tool, multi-step process (querying DPAPI via PowerShell, reading browser SQLite DBs, cmdkey /list, etc.). LaZagne does all of this in one run and outputs every credential it finds, structured by source application. On a target with many installed applications it saves significant enumeration time.

## Install

```bash
# Pre-built Windows binary from GitHub:
# https://github.com/AlessandroZ/LaZagne/releases
# Transfer to target via evil-winrm, xfreerdp /drive:, or python3 -m http.server

# No Kali install needed — it runs on the target
```

## Usage

```cmd
:: Run all modules (broadest search)
.\lazagne.exe all

:: Specific categories:
.\lazagne.exe browsers      :: Chrome, Firefox, IE, Edge saved passwords
.\lazagne.exe databases     :: MySQL, PostgreSQL, DBngin credentials
.\lazagne.exe mail          :: Outlook, Thunderbird
.\lazagne.exe windows       :: Windows Credential Manager, DPAPI-protected secrets
.\lazagne.exe wifi          :: Saved WiFi credentials

:: Output to file:
.\lazagne.exe all -oJ        :: JSON format
.\lazagne.exe all -oA -output C:\Temp\   :: all formats to directory
```

> 🔍 **Worth remembering:** LaZagne reads DPAPI-protected credentials using the current user's master key, which only works when run as the target user (not SYSTEM). Run it from a shell that's already the compromised user, not an elevated SYSTEM shell, otherwise browser credentials won't decrypt.

> ⚠️ AV will flag LaZagne by name and by behaviour. Consider renaming the binary before transfer and running it from a writable temp directory.

## Where this applies in the vault

- [[Windows Methodology#Step 7: Credential Hunting on Windows|Windows Methodology, Phase 2.5 Step 7]]
- [[16. Password Attacks|PA.12]]

🔁 [[16. Password Attacks|PA.12]], [[Windows Methodology#Step 7: Credential Hunting on Windows|Windows Methodology]]

#### Tags: #ModernTooling #LaZagne #CredentialHunting #Windows #Browser #DPAPI
## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

LaZagne supports a repeatable task in an authorized assessment; knowing when to use it keeps the workflow deliberate rather than tool-led.

## Tool description

LaZagne is a focused utility for the technique named by this page. Read its output as evidence and confirm important findings manually.

## Basic usage

Run the help screen first, then use the smallest command that answers the current question:

~~~bash
lazagne --help
~~~

## Related RUNBOOK V2 stage

- [[RUNBOOK V2/Index]] -- route to the technique-specific stage after identifying the finding

## Related module

- [[MODULES/13. Locating Public Exploits]] -- understand the tool’s place in a controlled workflow
