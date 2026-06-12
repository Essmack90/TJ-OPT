# Import AD Module
Import-Module ActiveDirectory

# User enumeration
Get-ADUser -Filter * -Properties *
Get-ADUser -Identity username -Properties *
Get-ADUser -Filter {Enabled -eq $true} -Properties DisplayName,SamAccountName
Get-ADUser -Filter * -SearchBase "OU=Users,DC=domain,DC=local"

# Group enumeration
Get-ADGroup -Filter *
Get-ADGroupMember "Domain Admins"
Get-ADGroupMember "Enterprise Admins"
Get-ADPrincipalGroupMembership username

# Computer enumeration
Get-ADComputer -Filter *
Get-ADComputer -Filter {OperatingSystem -like "*Server*"} -Properties OperatingSystem

# Domain info
Get-ADDomain
Get-ADDomainController

# ACL enumeration
Get-ADObject -LDAPFilter "(objectClass=group)" -Properties ntSecurityDescriptor
Get-ADObject -LDAPFilter "(objectClass=user)" -Properties ntSecurityDescriptor

# Find SPNs
setspn -T domain.local -Q */*
setspn -L username