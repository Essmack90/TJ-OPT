---
tags: [tool, activedirectory, certificate]
tool: "certify"
category: "Active Directory"
installed: true
phase: [exploitation]
---

# Certify - AD CS Enumeration/Abuse

## Tool Overview
Purpose: Windows tool for AD CS attacks
Location: ~/tools/activedirectory/windows/Certify.exe

## When to Use
- Finding vulnerable certificate templates
- Requesting certificates
- AD CS privilege escalation

## How to Use It

Find Vulnerable Templates:
Certify.exe find /vulnerable

Request Certificate:
Certify.exe request /ca:dc.domain.local\CA-NAME /template:VulnerableTemplate

Find All CAs:
Certify.exe cas

## Related Tools
certipy, pkinit-tools
