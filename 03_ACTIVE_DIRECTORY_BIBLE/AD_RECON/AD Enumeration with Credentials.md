# With valid credentials (even low-priv)
USER=domain_user
PASS=password
DOMAIN=domain.local
DC=TARGET_DC

# CrackMapExec full enumeration
crackmapexec smb $DC -u $USER -p $PASS --shares
crackmapexec smb $DC -u $USER -p $PASS --users
crackmapexec smb $DC -u $USER -p $PASS --groups
crackmapexec smb $DC -u $USER -p $PASS --pass-pol
crackmapexec smb $DC -u $USER -p $PASS --loggedon-users
crackmapexec smb $DC -u $USER -p $PASS --sessions

# LDAP enumeration with creds
ldapsearch -x -H ldap://$DC -D "$USER@$DOMAIN" -w "$PASS" -b "dc=domain,dc=local"
ldapsearch -x -H ldap://$DC -D "$USER@$DOMAIN" -w "$PASS" -b "cn=users,dc=domain,dc=local"
ldapsearch -x -H ldap://$DC -D "$USER@$DOMAIN" -w "$PASS" -b "cn=computers,dc=domain,dc=local"

# BloodHound Python (no GUI needed)
bloodhound-python -d $DOMAIN -u $USER -p $PASS -ns $DC -c all
# Import the resulting JSON files into BloodHound GUI

# PowerShell enumeration (if you have WinRM access)
evil-winrm -i $DC -u $USER -p $PASS
# Then inside PowerShell:
Get-ADUser -Filter * -Properties *
Get-ADGroup -Filter *
Get-ADComputer -Filter *
Get-ADGroupMember "Domain Admins"