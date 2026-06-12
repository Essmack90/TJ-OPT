# When you get ANY Windows shell with domain user:
whoami & hostname & ipconfig /all & nslookup domain.local
net user /domain
net group "Domain Admins" /domain
net group "Enterprise Admins" /domain
net localgroup Administrators
systeminfo | findstr /i "hotfix"
wmic qfe list brief

# Then immediately run these if possible:
# Download and run SharpHound
# Dump LSASS if admin
# Check for unquoted service paths
# Check for AlwaysInstallElevated