// High value paths
MATCH p=((u:User)-[:MemberOf|GenericAll|WriteOwner|WriteDacl|AllExtendedRights|ForceChangePassword]->(g:Group)) RETURN p

// Kerberoastable users
MATCH (u:User) WHERE u.hasspn=true RETURN u

// AS-REP roastable users
MATCH (u:User) WHERE u.dontreqpreauth=true RETURN u

// Admin to user paths
MATCH p=(c:Computer)-[:AdminTo]->(u:User) RETURN p

// Session paths
MATCH p=(c:Computer)-[:HasSession]->(u:User) RETURN p

// Constrained delegation
MATCH (u:User {allowedtodelegate:true}) RETURN u
MATCH (c:Computer {allowedtodelegate:true}) RETURN c

// Unconstrained delegation
MATCH (c:Computer {unconstraineddelegation:true}) RETURN c