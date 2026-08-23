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
- [[Cloud Methodology]] — AWS recon phases: external DNS/S3 recon (no auth), API oracle techniques (AMI account-ID leak, s3:ResourceAccount binary search, trust policy IAM role oracle, Pacu iam__enum_roles), post-compromise IAM triage (sts get-caller-identity → get-account-authorization-details → jq dump analysis), IAM privilege escalation (CreateAccessKey/CreateLoginProfile/AttachPolicy vectors, ABAC tag confusion)
- Reporting (below), assessment types (VA/pentest/red team + black/gray/white box), report structure, finding quality framework, SysReptor workflow; see [[05. Report Writing For Pen Testers|Report Writing For Pen Testers]] for full notes

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

---

## Reporting

### Assessment type — what was actually asked for?

| Type | Automation | Exploitation? | Goal |
|------|-----------|---------------|------|
| **Vulnerability Assessment** | Mostly automated | No | Identify and rate vulnerabilities |
| **Penetration Test** | Manual + tools | Yes | Demonstrate exploitability + business impact |
| **Red Team Assessment** | Manual, stealthy | Yes | Simulate APT; test people + process + technology |

Knowledge level provided:

| Level | What the tester knows |
|-------|----------------------|
| **Black Box** | Company name + network connection only |
| **Gray Box** | Some: network ranges, low-priv creds, architecture overview |
| **White Box** | Full: source code, admin creds, architecture diagrams |

### Report structure

```
1. Cover Page
2. Table of Contents
3. Executive Summary      ← non-technical; no vendor recommendations
4. Scope and Methodology
5. Findings               ← one entry per vuln; technical audience
6. Appendices             ← raw tool output, evidence
```

### Executive Summary rules

- Plain language, no jargon without explanation
- Business impact framing ("attacker could steal customer data" not "arbitrary RCE")
- No specific vendor product recommendations (describe the needed control, not the product)
- Summarise overall posture in one paragraph, then top 3-5 findings briefly

### Each finding must include

| Component | Content |
|-----------|---------|
| Title | Short, specific (e.g. "SMB Signing Disabled - NTLM Relay") |
| Severity | CVSS score + Critical/High/Medium/Low/Info |
| Description | What is the vulnerability and why it exists |
| Proof of Concept | Exact reproduction steps + screenshots |
| Business Impact | What an attacker does with it and what that costs the business |
| Recommendations | Specific, actionable, vendor-neutral remediation steps |

### Good vs bad remediation

Good: names the exact KB/config/setting, explains what happens if not fixed, vendor-neutral.
Bad: vague ("you should patch"), no specific CVE/fix, unprofessional tone.

### Reporting tool

We use [[SysReptor]] (cloud.sysreptor.com) for OSCP-format reports. See that note for templates and workflow. WriteHat (Docker, port 443) is used in the HTB Documentation & Reporting module lab but is not our tool of choice.

### Note-taking discipline during tests

Capture per finding at time of discovery: timestamp, exact command, full output (screenshot + text), target IP, your IP, one-sentence "what this means." Tmux logging keeps an automatic terminal session record. Vertical pane split: `Ctrl+B` then `Shift+%`.

---

**Remember**: Enumeration is the key to OSCP success. Take thorough notes, be methodical, and when stuck, enumerate more.

> "Try Harder" - Offensive Security
