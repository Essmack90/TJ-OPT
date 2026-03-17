---
tags: [tool, privesc, windows, ldap, ad]
tool: "ldapdomaindump"
category: "Privesc"
installed: true
phase: [recon, enumeration]
---

# ldapdomaindump - Active Directory LDAP Dumper

## Tool Overview
Purpose: Dump Active Directory information via LDAP
Location: /usr/bin/ldapdomaindump

## When to Use
- For Active Directory enumeration
- When you have LDAP access
- To get comprehensive AD information

## How to Use It

Basic Dump:
ldapdomaindump ldaps://domain.local -u 'DOMAIN\user' -p 'password'

Dump with Specific DC:
ldapdomaindump ldaps://dc.domain.local -u 'DOMAIN\user' -p 'password'

Output Formats:
ldapdomaindump ldaps://domain.local -u 'DOMAIN\user' -p 'password' --outdir /tmp/ldap-dump

Dump Without Authentication:
ldapdomaindump ldap://domain.local

## Output Files
- domain_users.html - User information
- domain_computers.html - Computer objects
- domain_groups.html - Group information
- domain_policy.html - Password policy
- domain_trusts.html - Trust relationships
- domain_children.html - Child domains

## Convert to BloodHound
ldd2bloodhound

## Related Tools
bloodhound, enum4linux-ng, ldapsearch
