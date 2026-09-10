# RUNBOOK V2

> [!tip] 💡 Start every new box here
> Open [[00 - Follow-Along Controller]]. It tells you what to run, what success looks like, and which page to open next. Use this index when you already know the technique.

> [!warning] 💡 The runbook loop
> Run one command block, compare the output, choose one **What did you get?** row, and follow its link. If a command fails, use the failure row before repeating it.

## How to use this index

Start at [[00 - Follow-Along Controller]] Step 0 and follow each stage's routing instructions. Use Ctrl+F to jump to a step number or technique when you already know what you need. When a public exploit needs editing, open [[Exploit Editing and Resource Guide]] before running it.

## Beginner orientation

The runbook is a decision path, not a list of commands to paste blindly. A beginner can use this order:

1. [[RUNBOOK V2/Start Here|Start Here]] sets the target, callback, and evidence variables, then performs the full TCP and UDP discovery scans.
2. [[RUNBOOK V2/Port Triage|Port Triage]] turns open ports into a Linux, Windows, AD, web, or IKE/IPSec branch.
3. A service-scan page identifies the product and version. A web-enum page identifies paths, forms, hosts, and parameters.
4. An exploit-search or technique page explains what the finding means before a public proof of concept is used.
5. [[RUNBOOK V2/Linux - RCE to Shell|RCE to Shell]] or [[RUNBOOK V2/Windows - Shell Received|Windows Shell Received]] proves the foothold with `whoami`, `id`, hostname, and a saved screenshot.
6. Local enumeration comes before privilege escalation: identity, groups, credentials, services, scheduled jobs, sudo or token privileges, and unusual files.
7. [[RUNBOOK V2/Linux - Clean Down|Linux Clean Down]] or [[RUNBOOK V2/Windows - Clean Down|Windows Clean Down]] records and removes only the artifacts created during the run.

If a result does not match a row, do not guess. Save the output, describe what is different, and route back to the closest service or enumeration stage.

## Seen in

- [[OSCP/BOXES/WRITE UPS/Linux/Networked|Networked]] -- source-first web upload, asynchronous cron filename injection, sudo configuration parsing, and verified cleanup
- [[OSCP/BOXES/WRITE UPS/Linux/Poison|Poison]] -- LFI, mechanical credential decoding, FreeBSD loopback enumeration, SSH local forwarding, and VNC root desktop
- [[OSCP/BOXES/WRITE UPS/Linux/Valentine|Valentine]] -- Heartbleed memory disclosure, encrypted SSH-key validation, legacy SSH negotiation, and tmux session access
- [[OSCP/BOXES/WRITE UPS/Linux/Traverxec|Traverxec]] -- Nostromo RCE, protected SSH archive, encrypted key cracking, and argument-specific journalctl pager escape
- [[OSCP/BOXES/WRITE UPS/AD/RockyColt|RockyColt]] -- anonymous LDAP, Tomcat HTML Manager WAR upload, FileZilla credential recovery, computer-object ACL abuse, RBCD, and S4U2Proxy
- [[OSCP/BOXES/WRITE UPS/Windows/Conceal|Conceal]] -- SNMP-disclosed IKE PSK, IPSec transport mode, anonymous FTP-to-IIS upload, and JuicyPotato SYSTEM
- [[OSCP/BOXES/WRITE UPS/Windows/Bastard|Bastard]] -- Drupalgeddon2 command execution, IUSR token triage, CLSID fallback, and JuicyPotato SYSTEM
- [[OSCP/BOXES/WRITE UPS/Linux/Knife|Knife]] -- PHP 8.1.0-dev `User-Agentt` backdoor, Bash callback, and passwordless sudo Knife Ruby execution

## Universal

0. [[00 - Follow-Along Controller]]: follow the complete box workflow from blank slate to closeout
0A. [[Exploit Editing and Resource Guide]]: review, edit, test, and troubleshoot public exploits and payloads
1. [[Start Here]]: initialise the workspace, variables, and full scan
2. [[Port Triage]]: classify the target from its open ports
2A. [[Windows - IKE-IPSec Transport]]: fingerprint IKEv1 and establish a scoped transport policy when UDP 500 hides TCP services

## Linux

3. [[Linux - Service Scan]]: identify Linux services and versions
3A. [[Linux - FTP Enumeration]]: test anonymous FTP and troubleshoot file transfers
3B. [[Linux - SSH Brute Force]]: test a controlled credential spray and legacy SSH negotiation
4. [[Linux - SNMP Enum|SNMP Enumeration]]: walk SNMP for usernames, processes, and credentials on Linux or Windows
12. [[Linux - Shell Stabilise]]: upgrade a basic shell into a more usable terminal
13. [[Linux - Local Enum]]: inspect the local host for privilege-escalation paths
14. [[Linux - Sudo Check]]: check commands the current user may run through sudo
15. [[Linux - SUID Check]]: find programs that run with a file owner's privileges
16. [[Linux - Cron Check]]: inspect scheduled jobs for writable scripts or commands
17. [[Linux - Credential Search]]: search local files and configuration for credentials
10A. [[Linux - Heartbleed]]: confirm and exploit CVE-2014-0160 memory disclosure
10B. [[Linux - Nostromo RCE]]: exploit Nostromo 1.9.6 CVE-2019-16278 after reviewing the standalone proof of concept
13A. [[Linux - Tmux Session Hijack]]: inspect and attach to an accessible privileged tmux socket
18. [[Linux - Database Access]]: use discovered database access for enumeration or execution
19. [[Linux - Kernel Exploit]]: assess a kernel exploit only after safer paths fail
20. [[Linux - Port Forwarding]]: tunnel an internal service to the testing machine
21. [[Linux - Clean Down]]: remove payloads and restore changed files

## Windows

22. [[Windows - Service Scan]]: identify Windows services and versions
23. [[Windows - Web Enum]]: enumerate IIS and Windows web paths
23A. [[Windows - FTP Enumeration]]: test anonymous FTP and inspect exposed files
23B. [[Windows - Web - PRTG]]: assess PRTG management access and stored configuration
23C. [[Windows - Web - NVMS-1000]]: test NVMS-1000 for file disclosure and traversal
23D. [[Windows - Web - NSClient++]]: reach and assess an internal NSClient++ API
23E. [[Windows - Web - Tomcat]]: test Tomcat Manager access and WAR deployment
23F. [[Windows - Web - Gym Management Upload]]: exploit the unauthenticated Gym Management System 1.0 upload handler
23G. [[Windows - Web - FTP Upload]]: use anonymous FTP write access to place an ASP file in an IIS web root
24. [[Windows - XXE]]: test XML endpoints for external entity file reads
25. [[Windows - SMB Enum]]: enumerate SMB shares and permissions
26. [[Windows - Exploit Search]]: search for manual public exploits
26A. [[Windows - Remote - AChat Buffer Overflow]]: exploit AChat 0.150 beta7 with the standalone proof of concept
27. [[Windows - Shell Received]]: confirm and document a landed Windows shell
27A. [[Windows - Port Forwarding]]: expose a loopback-only service through a Windows foothold
27B. [[Windows - Remote - CloudMe Buffer Overflow]]: exploit CloudMe 1.11.2 with the standalone stack-overflow proof of concept
28. [[Windows - Privilege Triage]]: inspect Windows token privileges and groups
28A. [[Windows - Privesc - ACL Misconfiguration]]: abuse inherited file and folder permissions
28B. [[Windows - RunasCs]]: run a process with alternate credentials when interactive logon is unavailable
28C. [[Windows - Lateral Movement - PsExec]]: execute a service remotely with valid Windows credentials
29. [[Windows - SeImpersonate Abuse]]: assess impersonation privileges for escalation
30. [[Windows - Service Abuse]]: check for writable or misconfigured services
31. [[Windows - Scheduled Task Abuse]]: check writable scheduled-task scripts
32. [[Windows - Credential Search]]: search the registry and user files for credentials
32A. [[Windows - Registry Hive Extraction]]: export and parse SAM, SYSTEM, and SECURITY hives
33. [[Windows - Clean Down]]: remove Windows payloads and persistence

## Active Directory

34. [[AD - Service Scan]]: identify domain services, the domain name, and clock skew
35. [[AD - Clock Sync]]: synchronise time and check reachability
36. [[AD - Anonymous Enum]]: test anonymous RPC, LDAP, and SMB access
37. [[AD - Web Enum]]: find domain usernames and clues on web services
37A. [[AD - LDAP Passback]]: capture cleartext LDAP credentials from a writable server address field
38. [[AD - AS-REP Roasting]]: request responses for accounts without Kerberos pre-authentication
39. [[AD - Kerberoasting]]: request service tickets and assess their passwords offline
40. [[AD - Credential Validation]]: safely test recovered credentials against available services
41. [[AD - WinRM Foothold]]: use valid credentials to open a Windows shell
42. [[AD - Group Triage]]: choose a privilege path from the user's group memberships
43. [[AD - Privilege Triage]]: inspect token privileges for escalation paths
43A. [[AD - Backup Operators]]: use backup privileges to copy protected registry hives
44. [[AD - Local Credential Search]]: check Winlogon and other local credential stores
44A. [[AD - LSASS Parsing]]: parse a recovered LSASS memory dump for NT hashes
45. [[AD - BloodHound]]: map rights and attack paths in the domain
45B. [[AD - Resource-Based Constrained Delegation]]: use a writable computer ACL and a controlled machine account for S4U impersonation
45A. [[AD - ForceChangePassword]]: check and use delegated password-reset rights
46. [[AD - Account Operators Abuse]]: create a controlled domain account
47. [[AD - DCSync Grant]]: grant replication rights to a controlled account
48. [[AD - DCSync Dump]]: dump directory hashes and extract the administrator hash
49. [[AD - Pass the Hash]]: validate an NT hash and open a privileged shell
50. [[AD - Clean Down]]: remove domain changes and verify cleanup

## Web

5. [[Linux - Web Enum]]: find web paths and application entry points
5A. [[Web - Virtual Host Enumeration]]: discover hostname-selected web applications
6. [[Linux - CMS Check]]: identify and assess a content-management system
7. [[Linux - LFI]]: confirm local file inclusion and read sensitive files
7A. [[Linux - RFI]]: test remote file inclusion and PHP wrapper execution
7B. [[Linux - Binary Analysis]]: analyse downloaded executables and reproduce crashes locally
8. [[Linux - SQLi]]: confirm SQL injection and assess command execution
8A. [[Linux - Command Injection]]: confirm shell metacharacter execution and reach internal services
8B. [[Linux - Stored XSS]]: trigger an administrator browser and capture a callback
9. [[Linux - File Upload]]: bypass upload filters and land a webshell
9A. [[Web - WordPress Simple File List Upload]]: test the Simple File List upload and rename path
10. [[Linux - Exploit Search]]: match service versions to public exploits
11. [[Linux - RCE to Shell]]: run a suitable exploit and catch a shell
