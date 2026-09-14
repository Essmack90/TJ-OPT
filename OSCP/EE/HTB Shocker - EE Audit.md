---
tags: [EE, HTB, Shocker, Shellshock, Linux, OSCP]
box: Shocker
status: Complete
---

# HTB Shocker - EE Audit

## Scope

This Everything Everywhere audit synchronises the manual Shocker run from $BoxDir with the OSCP vault. The source contains a complete command transcript, Nmap outputs, Gobuster results, private flag loot, and seven screenshots.

The vault receives only the redacted command/output log. All seven screenshots, including the flag-containing screenshot, remain outside the vault.

## Evidence source

| Source | Vault treatment |
|---|---|
| Manual transcript | Copied as [[OSCP/BOXES/BOX LOGS/Shocker-redacted.log|redacted log]] |
| Nmap allports and services | Referenced from the private workspace and represented in the write-up |
| Gobuster root and CGI output | Referenced from the private workspace and represented in the write-up |
| Screenshots 1 through 6 | Retained in the private source workspace; not copied into the vault |
| Screenshot 7 | Retained in the private source workspace; not copied because it displays flag values |
| Private flag loot | Retained in $BoxDir/loot/flags.txt and not reproduced |

## Updated locations

### Box record and evidence

- [[OSCP/BOXES/WRITE UPS/Linux/Shocker|Shocker write-up]] added in the established Linux format.
- [[OSCP/BOXES/BOX LOGS/Shocker-redacted.log|Shocker log]] added with target and callback addresses converted to variables and sensitive values redacted.
- [[OSCP/BOXES/BOX LOGS/BOX LOGS|Box logs index]] updated.
- [[OSCP/BOXES/WRITE UPS/Linux/Linux|Linux write-up MOC]] updated.
- [[OSCP/BOXES/WRITE UPS/WRITE UPS|Write-up MOC]] updated.
- [[OSCP/BOXES/MASTER BOX LIST|Master box list]] marked Shocker complete and added to the methodology tracker.

### Command references

- [[OSCP/OSCP COMMAND MASTER CHEATSHEET|Command Master Cheatsheet]] now has Apache CGI Shellshock and passwordless Perl sections with separated commands and one-line comments.
- [[OSCP/COMMAND APPENDIX/Reconnaissance & Enumeration|Reconnaissance and Enumeration]] now covers direct CGI enumeration and harmless identity proof.
- [[OSCP/COMMAND APPENDIX/Web Requests & Delivery|Web Requests and Delivery]] now covers Shellshock header delivery.
- [[OSCP/COMMAND APPENDIX/Shells & Payloads|Shells and Payloads]] now covers the CGI Bash callback and raw-shell recovery.
- [[OSCP/COMMAND APPENDIX/Linux Privilege Escalation|Linux Privilege Escalation]] now covers the exact Perl sudo boundary.
- [[OSCP/COMMAND BREAKDOWNS/Reconnaissance & Enumeration (Breakdowns)|Reconnaissance breakdowns]] now explains 403 directory versus direct CGI file.
- [[OSCP/COMMAND BREAKDOWNS/Shells & Payloads (Breakdowns)|Shell breakdowns]] now explains callback timing and terminal recovery.
- [[OSCP/COMMAND BREAKDOWNS/Privilege Escalation & Local Exploitation (Breakdowns)|Privilege breakdowns]] now explains Perl process replacement.

### Routing and methodology

- [[OSCP/RUNBOOK V2/Linux - Shellshock CGI|Linux Shellshock CGI]] added as a dedicated stage.
- RUNBOOK V2 Index and MOC updated with the new stage and Shocker Seen in reference.
- Start Here, Port Triage, Linux Service Scan, Linux Web Enum, Linux RCE to Shell, Linux Shell Stabilise, Linux Local Enum, Linux Sudo Check, and Linux Clean Down updated with Shocker evidence notes.
- [[OSCP/DECISION TREE/Web Applications (Decision Tree)|Web Applications decision tree]] updated with CGI 403 and callback-failure branches.
- [[OSCP/DECISION TREE/Linux Privilege Escalation (Decision Tree)|Linux privilege decision tree]] updated with the exact Perl sudo branch.
- [[OSCP/DECISION TREE/Reconnaissance & Enumeration (Decision Tree)|Reconnaissance decision tree]] updated with stale-target recovery.
- [[OSCP/METHODOLOGY CHEAT SHEET/Linux Methodology|Linux Methodology]] and the methodology MOC updated.
- [[OSCP/REFERENCE CARDS/FAQ - Quick Answers|FAQ]] updated with stale-target, CGI, callback, Perl, and stty gotchas.

### Training and exam routes

- Modules 7, 9, 13, and 18 updated with Shocker validation, Shellshock, exploit-vetting, and Perl sudo references.
- Exam Recon and Triage updated with target-validation recovery.
- Exam Web and Services updated with CGI routing.
- Exam Linux Fast Path updated with the Shocker CGI-to-Perl route.
- Exam Evidence and Clean Down updated with the Shocker evidence boundary.
- Exam Box Route Index updated.
- Exam Scenario Matrix updated with T51 for Apache CGI Shellshock and passwordless Perl.
- Command Appendix, Command Breakdowns, Decision Tree, and Modules MOCs updated with the Shocker route.

## Reusable lessons added

1. Correct a stale target context before interpreting filtered scan results.
2. Enumerate direct CGI files when the directory listing returns 403.
3. Prove Shellshock with id before attempting a callback.
4. Treat an HTTP timeout after callback delivery as a possible attached CGI process.
5. Keep the target web port and Kali listener port separate.
6. Read the exact sudo interpreter path and arguments before using a GTFOBins technique.
7. Keep flags and sensitive screenshots in private loot.

## Validation checklist

- [x] Write-up follows the established frontmatter and Linux walkthrough structure.
- [x] Manual source workspace is represented by variables rather than a hardcoded target address.
- [x] Commands have explanatory prose and saved evidence paths.
- [x] All seven screenshots remain outside the write-up vault.
- [x] The flag-containing screenshot is excluded from the vault.
- [x] The redacted log contains no target or callback IP literals.
- [x] New Shocker material contains no 32-character flag or hash value.
- [x] Master list, write-up indexes, command references, runbooks, decision trees, modules, and exam routes are cross-linked.
