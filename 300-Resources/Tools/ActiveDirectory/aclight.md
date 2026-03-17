---
tags: [tool, activedirectory, acl]
tool: "aclight"
category: "Active Directory"
installed: true
phase: [analysis]
---

# ACLight - ACL Analysis

## Tool Overview
Purpose: Analyze AD ACLs for dangerous permissions
Location: ~/tools/activedirectory/ACLight/

## How to Use It
powershell -ep bypass
. .\ACLight.ps1
Start-ACLight -TargetDirectory .\output\

## Related Tools
adaclscanner, bloodyad
