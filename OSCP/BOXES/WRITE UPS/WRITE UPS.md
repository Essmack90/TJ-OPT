---
tags: MOCs
---
```folder-index-content
```
## RUNBOOK V2 Stages Used

- [[OSCP/BOXES/WRITE UPS/Linux/Covfefe|Covfefe]] -- dotfile exposure, encrypted SSH key recovery, and source-derived SUID adjacent-string overwrite
- [[OSCP/BOXES/WRITE UPS/Linux/Shocker|Shocker]] -- CGI Shellshock proof, Bash callback, exact sudo Perl rule, and Linux cleanup boundary
- [[OSCP/BOXES/WRITE UPS/Windows/Optimum|Optimum]] -- HFS 2.3 command injection, PowerShell callback, one-CPU kernel-exploit gotcha, and MS16-098 SYSTEM proof
- [[OSCP/BOXES/WRITE UPS/Linux/Cap|Cap]] -- dashboard IDOR, predictable PCAP download, tshark FTP credential recovery, SSH reuse, and Python cap_setuid escalation
- [[OSCP/BOXES/WRITE UPS/Linux/Management|Management]] -- OpenAM JATO deserialization, GLPI application-secret recovery, SSH credential reuse, and rdiff-backup sudo wildcard abuse
- [[OSCP/BOXES/WRITE UPS/Windows/Grandpa|Grandpa]] -- IIS 6.0 WebDAV CVE-2017-7269, byte-preserving manual PoC diagnosis, staged migration, and MS14-058 SYSTEM proof


## Related Boxes

- [[OSCP/BOXES/WRITE UPS/AD/Forest|Forest]] -- shares a similar enumeration or escalation pattern
- [[OSCP/BOXES/WRITE UPS/Linux/Sea|Sea]] -- shares a similar enumeration or escalation pattern
- [[OSCP/BOXES/WRITE UPS/Linux/Poison|Poison]] -- shares a similar enumeration, credential-recovery, and port-forwarding pattern
- [[OSCP/BOXES/WRITE UPS/Linux/Covfefe|Covfefe]] -- shares a similar enumeration, credential-recovery, and custom-binary exploitation pattern
- [[OSCP/BOXES/WRITE UPS/AD/Vintage|Vintage]] -- shares a similar enumeration, credential-recovery, ACL, Kerberos, and delegated-access pattern
- [[OSCP/BOXES/WRITE UPS/AD/Search|Search]] -- shares a similar enumeration, credential-recovery, SMB, certificate, and delegated-access pattern
- [[OSCP/BOXES/WRITE UPS/Linux/Blocky|Blocky]] -- shares a similar enumeration, compiled-artifact credential recovery, password-reuse, SSH, and sudo pattern
- [[OSCP/BOXES/WRITE UPS/Linux/Shocker|Shocker]] -- shares a similar enumeration, shell delivery, identity-proof, and exact sudo-interpreter pattern
- [[OSCP/BOXES/WRITE UPS/Linux/Cap|Cap]] -- shares a similar web enumeration, evidence recovery, credential reuse, and Linux capability pattern
- [[OSCP/BOXES/WRITE UPS/Linux/Management|Management]] -- shares a similar application-secret, credential-reuse, and exact sudo-boundary pattern
- [[OSCP/BOXES/WRITE UPS/Windows/Grandpa|Grandpa]] -- shares a similar version-driven exploit, public-PoC review, callback diagnosis, and Windows local-escalation pattern

## External Resources

- https://www.exploit-db.com/search?q=WRITE%20UPS
- https://ippsec.rocks/?q=WRITE%20UPS
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
