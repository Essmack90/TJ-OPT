# RUNBOOK V2

*Linear GPS flow for Linux, standalone Windows, and Active Directory. Open Start Here and follow the arrows.*

## Universal + Linux path (Steps 1–21)

1. [[Start Here]]: initialise the workspace, variables, and full scan
2. [[Port Triage]]: classify the target from the open ports
3. [[Linux - Service Scan]]: identify Linux services and versions
4. [[Linux - SNMP Enum]]: walk SNMP for usernames, processes, and credentials
5. [[Linux - Web Enum]]: find web paths and entry points
6. [[Linux - CMS Check]]: identify and scan a CMS
7. [[Linux - LFI]]: confirm local file inclusion and read sensitive files
8. [[Linux - SQLi]]: confirm SQL injection and escalate to RCE
9. [[Linux - File Upload]]: bypass upload filters and land a webshell
10. [[Linux - Exploit Search]]: match versions to public exploits
11. [[Linux - RCE to Shell]]: run the exploit and catch a shell
12. [[Linux - Shell Stabilise]]: upgrade the shell
13. [[Linux - Local Enum]]: find local privilege paths
14. [[Linux - Sudo Check]]: check sudo rules
15. [[Linux - SUID Check]]: check SUID programs
16. [[Linux - Cron Check]]: check scheduled jobs
17. [[Linux - Credential Search]]: search files for credentials
18. [[Linux - Database Access]]: use database credentials and hashes
19. [[Linux - Kernel Exploit]]: use a kernel exploit as a last resort
20. [[Linux - Port Forwarding]]: tunnel internal services to Kali
21. [[Linux - Clean Down]]: remove Linux payloads and restore files

## Standalone Windows path (Steps 22–33)

22. [[Windows - Service Scan]]: identify Windows services and versions
23. [[Windows - Web Enum]]: enumerate IIS and web paths
24. [[Windows - XXE]]: test XML endpoints for external entity file read
25. [[Windows - SMB Enum]]: enumerate shares and permissions
26. [[Windows - Exploit Search]]: search for manual public exploits
26A. [[Windows - Remote - AChat Buffer Overflow]]: exploit AChat 0.150 beta7 with the standalone PoC
27. [[Windows - Shell Received]]: identify the landed shell
28. [[Windows - Privilege Triage]]: check Windows token privileges
28A. [[Windows - Privesc - ACL Misconfiguration]]: abuse inherited file and folder permissions
29. [[Windows - SeImpersonate Abuse]]: attempt impersonation escalation
30. [[Windows - Service Abuse]]: check writable services
31. [[Windows - Scheduled Task Abuse]]: check writable scheduled task scripts
32. [[Windows - Credential Search]]: search registry and user files
33. [[Windows - Clean Down]]: remove Windows payloads and persistence

## Active Directory path (Steps 34–50)

34. [[AD - Service Scan]]: identify AD services, domain, and clock skew
35. [[AD - Clock Sync]]: synchronise time and check VPN reachability
36. [[AD - Anonymous Enum]]: test anonymous RPC, LDAP, and SMB
37. [[AD - Web Enum]]: find usernames on the website
37A. [[AD - LDAP Passback]]: capture cleartext LDAP credentials from a writable server address field
38. [[AD - AS-REP Roasting]]: request and crack AS-REP responses
39. [[AD - Kerberoasting]]: request and crack service tickets
40. [[AD - Credential Validation]]: test recovered credentials
41. [[AD - WinRM Foothold]]: open the Windows shell
42. [[AD - Group Triage]]: choose a group-based path
43. [[AD - Privilege Triage]]: choose a token-privilege path
44. [[AD - Local Credential Search]]: check Winlogon and local stores
45. [[AD - BloodHound]]: map rights and attack paths
46. [[AD - Account Operators Abuse]]: create the controlled account
47. [[AD - DCSync Grant]]: grant replication rights
48. [[AD - DCSync Dump]]: dump NTDS and extract the admin hash
49. [[AD - Pass the Hash]]: validate the hash and open the privileged shell
50. [[AD - Clean Down]]: remove changes and verify cleanup

## Scope

Sources: [[Forest]] and [[Sauna]] in `OSCP/BOXES/WRITE UPS/AD/`.
