---
tags: MOCs
---
```folder-index-content
```

> [!tip] Command companion
> The runbook supplies the route and decision logic; [[OSCP COMMAND MASTER CHEATSHEET|OSCP Command Master Cheatsheet]] supplies the compact syntax lookup. Follow the runbook first when the output or failure mode is unfamiliar.

## Seen in
- [[00 - Follow-Along Controller]] -- blank-slate controller with evidence-driven routing, failure handling, resource pointers, and closeout
- [[Exploit Editing and Resource Guide]] -- copy, review, patch, syntax-check, payload selection, and exploit troubleshooting
- [[OSCP/BOXES/WRITE UPS/Windows/Buff|Buff]] -- complete Windows web foothold, loopback pivot, and CloudMe BOF chain
- [[OSCP/BOXES/WRITE UPS/Windows/Devel|Devel]] -- anonymous FTP upload, IIS ASP foothold, and JuicyPotato SYSTEM escalation
- [[OSCP/BOXES/WRITE UPS/Linux/Networked|Networked]] -- source archive, upload bypass, webshell, cron filename injection, sudo configuration parsing, and cleanup
- [[OSCP/BOXES/WRITE UPS/Linux/Poison|Poison]] -- LFI, repeated Base64 decoding, SSH foothold, loopback VNC discovery, and SSH local forwarding
- [[OSCP/BOXES/WRITE UPS/Linux/Covfefe|Covfefe]] -- exposed dotfiles, encrypted SSH key cracking, custom SUID source review, and adjacent-string privilege escalation
- [[OSCP/BOXES/WRITE UPS/Linux/Valentine|Valentine]] -- exposed encrypted key, Heartbleed memory disclosure, legacy SSH, and root tmux socket access
- [[OSCP/BOXES/WRITE UPS/Linux/Traverxec|Traverxec]] -- Nostromo RCE, protected SSH archive, encrypted key cracking, and exact-argument journalctl pager escape
- [[OSCP/BOXES/WRITE UPS/Windows/Conceal|Conceal]] -- SNMP-disclosed IKE PSK, IPSec transport mode, anonymous FTP-to-IIS upload, and JuicyPotato SYSTEM
- [[OSCP/BOXES/WRITE UPS/Windows/Bastard|Bastard]] -- Drupalgeddon2 command execution, token triage, CLSID testing, and JuicyPotato SYSTEM
- [[OSCP/BOXES/WRITE UPS/Linux/Knife|Knife]] -- PHP 8.1.0-dev `User-Agentt` backdoor, Bash callback, and passwordless sudo Knife Ruby execution
- [[OSCP/BOXES/WRITE UPS/Linux/DevOops|DevOops]] -- multipart XML XXE, Flask source review, unsafe Python pickle proof, SSH-key extraction, and Git-history credential hunting
- [[OSCP/BOXES/WRITE UPS/Linux/Shocker|Shocker]] -- Apache CGI enumeration, Shellshock identity proof, Bash callback, and passwordless sudo Perl
- [[OSCP/BOXES/WRITE UPS/Linux/Mirai|Mirai]] -- Pi-hole fingerprint, unchanged IoT credential validation, SSH as `pi`, passwordless sudo, and safe mounted-USB metadata collection
- [[OSCP/BOXES/WRITE UPS/Windows/Love|Love]] -- staging-host SSRF, authenticated Voting System upload, `phoebe` shell, and AlwaysInstallElevated MSI SYSTEM callback
- [[OSCP/BOXES/WRITE UPS/Windows/Legacy|Legacy]] -- Windows XP SMBv1/RPC exposure, MS08-067 manual Python/Impacket exploitation, target-side bind shell, and legacy-shell verification
- [[OSCP/BOXES/WRITE UPS/Windows/Grandpa|Grandpa]] -- IIS 6.0 WebDAV CVE-2017-7269, manual byte-preserving PoC adaptation, worker-process crash diagnosis, staged migration, and MS14-058 SYSTEM
- [[OSCP/BOXES/WRITE UPS/AD/Search|Search]] -- image-based credential recovery, Office/XML triage, PKCS#12/PSWA, gMSA, and delegated password reset
- [[OSCP/BOXES/WRITE UPS/Linux/Management|Management]] -- OpenAM JATO deserialization, GLPI secret recovery, SSH reuse, and rdiff-backup sudo wildcard abuse
- [[OSCP/BOXES/WRITE UPS/Linux/Cap|Cap]] -- dashboard IDOR, PCAP FTP credential recovery, SSH reuse, and Python cap_setuid escalation
- [[OSCP/BOXES/WRITE UPS/Linux/Busqueda|Busqueda]] -- Searchor Python eval injection, Git credential leakage, Docker environment inspection, Gitea reuse, and relative-path sudo execution
- [[OSCP/BOXES/WRITE UPS/AD/Vintage|Vintage]] -- Kerberos-only assumed breach, pre-created computer account, gMSA read, ACL/group abuse, Kerberoasting, DPAPI Credential Manager, group-based RBCD, and SYSTEM proof
- [[OSCP/BOXES/WRITE UPS/Windows/Escape|Escape]] -- anonymous SMB PDF discovery, MSSQL `xp_dirtree` coercion, UTF-16LE log credential recovery, AD CS ESC1, and pass-the-hash

## Related stages

- [[00 - Follow-Along Controller]]
- [[How to Read Output]]
- [[Exploit Editing and Resource Guide]]
- [[Linux - Service Scan]]
- [[Linux - Web Enum]]
- [[Linux - IDOR and PCAP Credential Recovery]]
- [[Linux - Shellshock CGI]]
- [[Linux - IoT Default Credentials]]
- [[Linux - SNMP Enum]]
- [[Linux - Exploit Search]]
- [[Windows - FTP Enumeration]]
- [[Windows - SMB Enum]]
- [[Windows - Exploit Search]]
- [[Windows - Shell Received]]
- [[Windows - Web - Gym Management Upload]]
- [[Windows - Web - FTP Upload]]
- [[Windows - Port Forwarding]]
- [[Windows - Remote - CloudMe Buffer Overflow]]
- [[Linux - Heartbleed]]
- [[Linux - Nostromo RCE]]
- [[Linux - OpenAM JATO Deserialization]]
- [[Linux - Rdiff-Backup Sudo Abuse]]
- [[Linux - Tmux Session Hijack]]
- [[Linux - File Capabilities]]
- [[Linux - Docker Enumeration]]
- [[Linux - XXE]]
- [[Linux - Python Pickle]]
- [[Linux - Credential Search]]
- [[Linux - Clean Down]]
- [[Windows - IKE-IPSec Transport]]
- [[AD - Service Scan]]
- [[AD - Credential Validation]]
- [[AD - BloodHound]]
- [[AD - Certificate Services ESC1]]
- [[AD - Kerberoasting]]
- [[AD - Resource-Based Constrained Delegation]]
- [[AD - Local Credential Search]]
- [[AD - Clean Down]]

## Recent coverage

- [[OSCP/BOXES/WRITE UPS/Linux/Shocker|Shocker]] — direct CGI discovery and Shellshock are covered by [[Linux - Shellshock CGI]]
- [[OSCP/BOXES/WRITE UPS/Windows/Optimum|Optimum]] — patch-aware Sherlock triage and the one-processor MS16-032 gotcha are covered by [[Windows - Privilege Triage]]
- [[OSCP/BOXES/WRITE UPS/Windows/Legacy|Legacy]] — manual MS08-067 source adaptation and bind-shell handling are covered by [[Windows - Exploit Search]] and [[Windows - Shell Received]]
- [[OSCP/BOXES/WRITE UPS/AD/Search|Search]] — image review, bounded password reuse, Office/XML triage, and certificate-authenticated PSWA are covered by [[AD - Web Enum]], [[AD - Credential Validation]], [[Windows - SMB Enum]], and [[AD - PowerShell Web Access]]
- [[OSCP/BOXES/WRITE UPS/Linux/Management|Management]] — OpenAM JATO deserialization and rdiff-backup sudo abuse are covered by [[Linux - OpenAM JATO Deserialization]] and [[Linux - Rdiff-Backup Sudo Abuse]]
- [[OSCP/BOXES/WRITE UPS/Linux/Cap|Cap]] — dashboard IDOR and predictable capture download are covered by [[Linux - IDOR and PCAP Credential Recovery]], and Python cap_setuid is covered by [[Linux - File Capabilities]]
- [[OSCP/BOXES/WRITE UPS/Windows/Grandpa|Grandpa]] -- IIS 6.0 version and method checks are covered by [[Windows - Service Scan]] and [[Windows - Web Enum]]; EDB-41738 adaptation is covered by [[Windows - Exploit Search]] and [[Exploit Editing and Resource Guide]]; migration and MS14-058 are covered by [[Windows - Shell Received]] and [[Windows - Privilege Triage]]
- [[OSCP/BOXES/WRITE UPS/Linux/Busqueda|Busqueda]] -- Searchor eval injection, Git remote credentials, Docker environment inspection, and relative-path sudo execution are covered by [[Linux - Command Injection]], [[Linux - Credential Search]], [[Linux - Docker Enumeration]], and [[Linux - Sudo Check]]
- [[OSCP/BOXES/WRITE UPS/Windows/Escape|Escape]] -- anonymous SMB/PDF discovery, MSSQL `xp_dirtree` coercion, log-based credential recovery, and AD CS ESC1 are covered by [[Windows - SMB Enum]], [[AD - Credential Validation]], [[Windows - Credential Search]], and [[AD - Certificate Services ESC1]]; the final hash route is covered by [[AD - Pass the Hash]]

## Search

- [[OSCP/BOXES/WRITE UPS/AD/Search|Search]] — end-to-end AD chain using IIS image OSINT, Kerberoasting, SMB profile traversal, PKCS#12, PSWA, gMSA, and delegated password reset
- [[AD - PowerShell Web Access]] — certificate-authenticated PSWA branch

## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
