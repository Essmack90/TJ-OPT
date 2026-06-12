# List all users
ldapsearch -x -H ldap://$DC -D "user@domain.local" -w "pass" -b "dc=domain,dc=local" "(objectClass=user)" | grep sAMAccountName

# List all groups
ldapsearch -x -H ldap://$DC -D "user@domain.local" -w "pass" -b "dc=domain,dc=local" "(objectClass=group)" | grep sAMAccountName

# Find Domain Admins
ldapsearch -x -H ldap://$DC -D "user@domain.local" -w "pass" -b "dc=domain,dc=local" "(&(objectClass=user)(adminCount=1))"

# Find computers
ldapsearch -x -H ldap://$DC -D "user@domain.local" -w "pass" -b "cn=computers,dc=domain,dc=local"

# Find SPNs (Kerberoast targets)
ldapsearch -x -H ldap://$DC -D "user@domain.local" -w "pass" -b "dc=domain,dc=local" "(&(objectClass=user)(servicePrincipalName=*))"

# Find users with no preauth (AS-REP roast)
ldapsearch -x -H ldap://$DC -D "user@domain.local" -w "pass" -b "dc=domain,dc=local" "(&(objectClass=user)(userAccountControl:1.2.840.113556.1.4.803:=4194304))"