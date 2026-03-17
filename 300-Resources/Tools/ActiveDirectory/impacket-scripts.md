---
tags: [tool, activedirectory, impacket]
tool: "impacket-scripts"
category: "Active Directory"
installed: true
phase: [all]
---

# Impacket Scripts - Python Network Protocols

## Tool Overview
Purpose: Collection of Python scripts for AD penetration testing
Location: /usr/bin/impacket-* and ~/.local/bin/

## Key Scripts

### Credential Access
- secretsdump.py - Dump secrets from Windows
- lsadump.py - Dump LSA secrets
- samrdump.py - Dump SAM

### Remote Execution
- psexec.py - PSExec style execution
- wmiexec.py - WMI execution
- smbexec.py - SMB execution
- atexec.py - Task scheduler execution
- dcomexec.py - DCOM execution

### Kerberos
- GetUserSPNs.py - Kerberoasting
- GetNPUsers.py - AS-REP roasting
- ticketer.py - Create golden/silver tickets
- raiseChild.py - Child to parent domain attack

### Enumeration
- lookupsid.py - SID brute force
- rpcdump.py - RPC endpoint mapper
- samrdump.py - SAM enumeration

### Relaying
- ntlmrelayx.py - NTLM relay attacks

### Examples
secretsdump.py domain/user:pass@target
psexec.py domain/user:pass@target
GetUserSPNs.py domain/user:pass -dc-ip DC -request
GetNPUsers.py domain/ -usersfile users.txt -dc-ip DC
ticketer.py -nthash KRBTGT_HASH -domain-sid SID -domain domain.local GoldenAdmin
ntlmrelayx.py -t ldap://dc.domain.local -smb2support

## Related Tools
netexec, crackmapexec
