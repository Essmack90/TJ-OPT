---
tags: [tool, activedirectory, acl]
tool: "adaclscanner"
category: "Active Directory"
installed: true
phase: [analysis]
---

# ADACLScanner - ACL Scanning Tool

## Tool Overview
Purpose: Scan AD ACLs for misconfigurations
Location: ~/tools/activedirectory/ADACLScanner/

## How to Use It
powershell -ep bypass
. .\ADACLScanner.ps1
Invoke-ACLScanner -Domain domain.local

## Related Tools
aclight, bloodyad
