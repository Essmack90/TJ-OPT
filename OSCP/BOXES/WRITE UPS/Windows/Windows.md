---
tags: MOCs
---
```folder-index-content
```
## External Resources

- [HackTricks - Windows Local Privilege Escalation](https://hacktricks.wiki/en/windows-hardening/windows-local-privilege-escalation/index.html)
- [HackTricks - XXE](https://hacktricks.wiki/en/pentesting-web/xxe-xee-xml-external-entity.html)
- [PayloadsAllTheThings - Windows Privilege Escalation](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Methodology%20and%20Resources/Windows%20-%20Privilege%20Escalation.md)
- [RevShells](https://www.revshells.com/) for shell payloads
- [CyberChef](https://gchq.github.io/CyberChef/) for encoding and decoding
- [ippsec.rocks](https://ippsec.rocks/) for walkthrough searches
## RUNBOOK V2 Stages Used

- [[OSCP/BOXES/WRITE UPS/Windows/Grandpa|Grandpa]] -- IIS 6.0/WebDAV service and web enumeration, EDB-41738 review, staged callback migration, and MS14-058 privilege triage


## Related Boxes

- [[OSCP/BOXES/WRITE UPS/Windows/Jerry|Jerry]] -- shares a similar enumeration or escalation pattern
- [[OSCP/BOXES/WRITE UPS/Windows/Servmon|Servmon]] -- shares a similar enumeration or escalation pattern
- [[OSCP/BOXES/WRITE UPS/Windows/Buff|Buff]] -- shares the Windows web foothold, internal-service, and port-forwarding pattern
- [[OSCP/BOXES/WRITE UPS/Windows/Devel|Devel]] -- shares the IIS foothold, payload delivery, and token-escalation pattern
- [[OSCP/BOXES/WRITE UPS/Windows/Optimum|Optimum]] -- shares the Windows web foothold, reviewed public exploit, PowerShell callback, and patch-aware local escalation pattern
- [[OSCP/BOXES/WRITE UPS/Windows/Grandpa|Grandpa]] -- shares the IIS foothold, manual public-exploit review, callback diagnosis, process migration, and legacy kernel-escalation pattern
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
