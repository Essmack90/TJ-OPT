---
tags: [tool, activedirectory, ldap]
tool: "ldapdomaindump"
category: "Active Directory"
installed: true
phase: [enumeration]
---

# ldapdomaindump - LDAP Domain Dumper

## Tool Overview
Purpose: Dump Active Directory information via LDAP
Location: /usr/bin/ldapdomaindump

## When to Use
- For Active Directory enumeration
- When you have LDAP access
- To get comprehensive AD information

## How to Use It

Basic Dump:
ldapdomaindump ldaps://dc.domain.local -u 'DOMAIN\user' -p 'password'

With Specific DC:
ldapdomaindump ldaps://dc.domain.local -u 'DOMAIN\user' -p 'password'

Output Directory:
ldapdomaindump ldaps://domain.local -u 'DOMAIN\user' -p 'password' --outdir /tmp/ldap-dump

## Output Files
- domain_users.html - User information
- domain_computers.html - Computer objects
- domain_groups.html - Group information
- domain_policy.html - Password policy
- domain_trusts.html - Trust relationships

## Related Tools
bloodhound, enum4linux-ng
