# Command Appendix

A pure by-tool/by-area index. Not phase-ordered like [[METHODOLOGY CHEAT SHEET]], not symptom-ordered like [[DECISION TREE]], not a "why does this work" teardown like [[COMMAND BREAKDOWNS]], just: "I know roughly what I want to do, what's the exact syntax and where did we use it."

Split into one file per area (restructured 2026-08-04 from a single flat file, same pattern as [[COMMAND BREAKDOWNS]]) so it stays scannable as it grows. Every entry links back to the module section it came from for the full explanation and context.

## Areas

- [[Reconnaissance & Enumeration]] — WHOIS, Google dorking, passive OSINT, DNS/SMB/SMTP/SNMP enumeration, Nmap, Gobuster, Metasploit quick reference
- [[Web Requests & Delivery]] — Curl (requests/payload delivery), Python HTTP Server
- [[File Inclusion & Traversal]] — directory traversal, LFI, RFI, PHP wrappers, null-byte bypass
- [[File Upload Attacks]] — filter bypasses, PowerShell-via-upload reverse shell, upload+traversal `authorized_keys` overwrite
- [[Shells & Payloads]] — webshells (PHP/ASPX/CFM), reverse shells, SSH key theft/planting, LOLBIN downloaders, cron-based delivery
- [[SQL Injection & Databases]] — MySQL, MSSQL/Impacket, SQLi payloads, sqlmap
- [[Web Applications]] — WordPress, Webmin, command injection diagnosis
- [[Phishing]] — website cloning, clone-patching (BeautifulSoup), credential capture servers
- [[Client-Side Attacks]] — WsgiDAV/WebDAV setup, Windows library file XML, `.lnk` shortcut payloads, VBA macros, one-shot SMB delivery
- [[Locating Public Exploits]] — SearchSploit syntax, patching a found exploit's hardcoded values, cewl targeted wordlists, CSRF-aware patator brute forcing
- [[Fixing Exploits]] — cross-compiling with `mingw-w64`, running Windows binaries via `wine`, multi-file SearchSploit copies, hex-decode pipelines
- [[Buffer Overflow & Memory Corruption]] — `msfvenom` shellcode generation for BOF payloads (bad chars, encoders, output formats), offset-discovery basics, Windows post-exploitation file search

- [[Password Attacks]] — Hydra (SSH/RDP/HTTP form/basic), Hashcat modes (NTLM 1000, Net-NTLMv2 5600, KeePass 13400, SSH key 22921), JtR (keepass2john, ssh2john), Mimikatz privilege chain (privilege::debug/token::elevate/lsadump::sam/sekurlsa::logonpasswords/misc::memssp), Responder, impacket-ntlmrelayx, Pass-the-Hash (impacket-psexec/wmiexec/smbclient)
- [[Windows Privilege Escalation]] — situational awareness, sensitive info hunting (PSReadLine/transcripts/registry), winPEAS/PowerUp/Seatbelt, service binary hijacking, DLL hijacking (nostdlib MinGW compile), unquoted service paths, scheduled task binary replacement, kernel exploits (CVE-2023-29360 / CVE-2023-28252), SeImpersonatePrivilege (SigmaPotato), SeBackupPrivilege (hive dump + FILE_FLAG_BACKUP_SEMANTICS), AlwaysInstallElevated

*(New areas get added here as modules are worked through, Active Directory, Pivoting, Linux Privilege Escalation, etc. Note: JuicyPotato, GPP/cPassword decryption, and Kerberoasting appeared in the [[Arctic]] and [[Active]] box writeups -- they are now partially covered by the Windows Privilege Escalation appendix above for the SeImpersonatePrivilege path.)*

#### Tags: #CommandAppendix #Methodology
