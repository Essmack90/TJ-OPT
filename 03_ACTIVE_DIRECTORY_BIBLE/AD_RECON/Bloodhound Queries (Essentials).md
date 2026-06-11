// Find all Domain Admins
MATCH (u:User) WHERE u.admincount = True RETURN u

// Find shortest path to Domain Admin
MATCH p=ShortestPath((u:User)-[:MemberOf*1..]->(g:Group)) WHERE g.objectid ENDS WITH '-512' RETURN p

// Find users with Kerberoastable SPNs
MATCH (u:User {hasspn:true}) RETURN u

// Find users with AS-REP roasting enabled
MATCH (u:User {dontreqpreauth:true}) RETURN u

// Find high value targets
MATCH (c:Computer) WHERE c.highvalue = True RETURN c

// Find computers with unconstrained delegation
MATCH (c:Computer {unconstraineddelegation:true}) RETURN c

// Find all members of Domain Admins
MATCH (u:User)-[:MemberOf]->(g:Group {name: "DOMAIN ADMINS@DOMAIN.LOCAL"}) RETURN u

// Find local admin access
MATCH p=(c:Computer)-[:AdminTo]->(u:User) RETURN p