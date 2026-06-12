# On attacker machine
cp /usr/share/wordlists/rockyou.txt.gz ~/oscp/wordlists/
gunzip ~/oscp/wordlists/rockyou.txt.gz

# Download SharpHound
wget https://github.com/BloodHoundAD/BloodHound/raw/master/Collectors/SharpHound.exe

# Download PowerView
wget https://raw.githubusercontent.com/PowerShellMafia/PowerSploit/master/Recon/PowerView.ps1

# Download Mimikatz
wget https://github.com/gentilkiwi/mimikatz/releases/latest/download/mimikatz_trunk.zip

# Download certipy
python3 -m pip install certipy-ad

# Download bloodyAD
python3 -m pip install bloodyad