# Find domain controllers
nmap -p 389,636,3268,3269 --script ldap-rootdse TARGET_NETWORK/24

# LDAP anonymous bind
ldapsearch -x -H ldap://TARGET_DC -b "dc=domain,dc=local"
ldapsearch -x -H ldap://TARGET_DC -b "dc=domain,dc=local" "(objectclass=*)"

# SMB null session enumeration
enum4linux -a TARGET_DC
smbclient -N -L //TARGET_DC
rpcclient -U "" -N TARGET_DC

# RPC enumeration commands
rpcclient -U "" -N TARGET_DC -c "enumdomusers"
rpcclient -U "" -N TARGET_DC -c "enumdomgroups"
rpcclient -U "" -N TARGET_DC -c "lsaenumsid"
rpcclient -U "" -N TARGET_DC -c "querydominfo"
rpcclient -U "" -N TARGET_DC -c "enumprivs"
rpcclient -U "" -N TARGET_DC -c "getdompwinfo"

# CrackMapExec null session
crackmapexec smb TARGET_DC -u '' -p '' --shares
crackmapexec smb TARGET_DC -u '' -p '' --users
crackmapexec smb TARGET_DC -u '' -p '' --pass-pol

# Windapsearch (great tool)
windapsearch -d domain.local --dc TARGET_DC --users
windapsearch -d domain.local --dc TARGET_DC --groups
windapsearch -d domain.local --dc TARGET_DC --computers
windapsearch -d domain.local --dc TARGET_DC --spns