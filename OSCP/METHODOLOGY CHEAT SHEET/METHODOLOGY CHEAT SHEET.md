# OSCP - Complete Methodology Cheat Sheet

> **A step-by-step framework for attacking Linux, Windows, and Active Directory targets.**
> This sheet is phase-ordered (recon → foothold → privesc). For a pure by-tool index ("I know which tool, what's the syntax"), see [[COMMAND APPENDIX]]. For symptom-based triage ("I found X, what do I try"), see [[DECISION TREE]].

Restructured 2026-08-04 from a single flat file into a folder split by target type, same pattern as [[COMMAND APPENDIX]] and [[COMMAND BREAKDOWNS]].

---

## Areas

- [[Pre-Engagement Kali Setup]] — master paste block (export BoxIP/Username/Password/Hash/LocalIP/Domain/DCip), workspace directory creation, /etc/hosts management, variable-ified command library (nmap/gobuster/evil-winrm/impacket/msfvenom/PtH), variable syntax gotchas, OSCP vs HTB proof differences
- [[Linux Methodology]] — recon, web app exploitation (traversal/LFI/upload/command injection/SQLi), shells & payloads, privilege escalation
- [[Windows Methodology]] — recon, SMB/LDAP enumeration, shells & payloads, privilege escalation (unquoted services, DLL hijacking, potato attacks, UAC bypass); Phase 2.5: SAM/LSASS offline dump, pypykatz, NetExec remote dump, NTDS VSS, credential hunting (cmdkey/LaZagne/findstr)
- [[Active Directory Methodology]] — AD enumeration (PowerView, BloodHound), username-anarchy + kerbrute userenum before spraying, password attacks (spraying, Kerberoasting, AS-REP roasting), pass-the-hash/ticket (Windows kirbi + Linux ccache paths), Pass-the-Certificate (pywhisker + PKINIT), post-exploitation (Mimikatz, DCSync, Snaffler, NTDS VSS, golden/silver tickets), lateral movement, pivoting

---

## 4. Quick Reference Flowcharts

### Linux Attack Flow
```
Port Scan → Identify Services
    ↓
Web Service → Gobuster/WPScan → Find Vuln → Exploit → Shell
    ↓
Other Services → enum4linux, snmpwalk, smbclient → Find Creds/Info → Exploit
    ↓
Initial Shell → TTY Upgrade → Enumeration (LinPEAS, sudo -l, SUID)
    ↓
Priv Esc → SUID, Sudo, Capabilities, Cron, Kernel → Root Shell
```

### Windows Attack Flow
```
Port Scan → Identify Services
    ↓
SMB → enum4linux, smbclient → Find Shares, Users, Null Sessions
    ↓
RDP/WinRM → Hydra/CrackMapExec → Find Creds
    ↓
Web → Gobuster, WPScan → Find Vuln → Exploit
    ↓
Initial Shell → PowerShell → Enumeration (WinPEAS, whoami /all)
    ↓
Priv Esc → Unquoted Services, DLL Hijacking, Potato, UAC Bypass → SYSTEM
```

### Active Directory Attack Flow
```
Initial Creds → Enumeration (PowerView, BloodHound)
    ↓
Identify Attack Path
    ↓
Password Spray → Kerberoast → AS-REP Roast → Pass-the-Hash
    ↓
Access to Low-Priv User → BloodHound → Find Path to DA
    ↓
Lateral Movement → PsExec, WMI, WinRM, Impacket
    ↓
Post-Exploitation → Mimikatz → DCSync → Golden Ticket
    ↓
Domain Admin → Extract Creds → Persistence
```

---

## 5. Key Commands Summary

### Linux Key Commands
| Command | Purpose |
|---------|---------|
| `find / -perm -u=s -type f 2>/dev/null` | Find SUID files |
| `sudo -l` | Check sudo permissions |
| `cat /etc/cron*` | View cron jobs |
| `uname -a` | Kernel version |
| `getcap -r / 2>/dev/null` | Capabilities |

### Windows Key Commands
| Command | Purpose |
|---------|---------|
| `whoami /all` | User info + privileges |
| `systeminfo` | OS + patches |
| `wmic qfe list` | Installed updates |
| `net user /domain` | Domain users |
| `net group "Domain Admins" /domain` | DA members |

### AD Key Commands
| Command | Purpose |
|---------|---------|
| `Get-NetUser` | List users |
| `Get-NetGroup` | List groups |
| `Get-NetComputer` | List computers |
| `Get-NetUser -SPN` | Kerberoastable users |
| `Find-LocalAdminAccess` | Check local admin |
| `Invoke-BloodHound` | Collect AD data |

---

**Remember**: Enumeration is the key to OSCP success. Take thorough notes, be methodical, and when stuck, enumerate more.

> "Try Harder" - Offensive Security
