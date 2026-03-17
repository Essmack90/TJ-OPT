---
tags: [tool, activedirectory, certificate]
tool: "delegate-your-cert"
category: "Active Directory"
installed: true
phase: [exploitation]
---

# Delegate-Your-Cert - ESC4 Automation

## Tool Overview
Purpose: Automate ESC4 certificate template attacks
Location: ~/tools/activedirectory/Delegate-Your-Cert/delegate.py

## How to Use It
python3 delegate.py -dc-ip dc.domain.local -u user -p pass -t target-user

## Related Tools
certipy, pywhisker
