---
tags: [OSCP, EE, Audit, Search, ActiveDirectory, Documentation]
status: Complete
date: 2026-09-13
---

# HTB Search — Everything Everywhere audit

## Result

The Search manual run has been written up and propagated through the relevant OSCP vault layers. The source transcript is preserved, the box is linked from the box indexes, and the reusable techniques are present in the runbooks, appendices, breakdowns, decision trees, methodology notes, modules, and exam-runbook views.

## Source audit

| Item | Result |
|---|---|
| Manual workspace | /home/kali/Platforms/HackTheBox/Search/ |
| Raw command/output log | Search.log, 1,141 lines |
| Scan artifacts | nmap/allports.* and nmap/services.* |
| Loot | .env, images, usernames, Kerberoast ticket, XLSX, PFX/P12, PSWA HTML/cookies, user proof, flag index |
| Screenshots | 23 screenshots, referenced from the write-up |
| Completed proof | user.txt and flags.txt retained in private loot |
| Target cleanup state | boxdone recorded; Tristan password restoration not recorded; two hosts-file additions remain documented |

## Required write-up-format audit

Five previous write-ups were read in full before drafting Search:

1. Forest
2. Sauna
3. Return
4. Blackfield
5. Vintage

Search follows the shared format: gist, box information, vulnerability summary, evidence and loot, variables, numbered route, evidence callouts, gotchas, RUNBOOK V2 stages, flags, clean-down, one-page narrative, tools, credentials, sensitive transcript evidence, remediation, lessons learned, related boxes, resources, and OSCP relevance.

## Everything Everywhere mapping

### Box and evidence layer

- BOXES/WRITE UPS/AD/Search.md — complete manual walkthrough with commands, outputs, screenshots, source paths, gotchas, and private-evidence handling.
- BOXES/BOX LOGS/Search.log — copied raw command/output transcript.
- BOXES/BOX LOGS/BOX LOGS.md — Search write-up, log, and source-workspace links.
- BOXES/WRITE UPS/AD/AD.md — Search added to the AD write-up hub.
- BOXES/WRITE UPS/WRITE UPS.md — Search added to the global write-up hub.
- BOXES/MASTER BOX LIST.md — Search marked complete in the HTB AD list, red-team list, tracker, dashboard totals, and phase totals.

### RUNBOOK V2

- AD - Service Scan — RESEARCH/search.htb service map, raw-socket fallback, and IIS/AD CS/ADWS findings.
- AD - Anonymous Enum — negative null-session result and the redirect to IIS enumeration.
- Windows - SMB Enum — authenticated share triage, redirected profile paths, XLSX retrieval, and certificate backups.
- AD - Web Enum — image-based credential discovery and the /certsrv clue.
- AD - Kerberoasting — DNS repair, TGS capture, and password crack evidence.
- AD - Credential Validation — Hope, web_svc, Edgar, and Sierra validation.
- AD - Group Triage — Sierra/ITSec route.
- AD - BloodHound — gMSA authorization and ACL reasoning.
- AD - ForceChangePassword — gMSA-to-Tristan password reset.
- AD - Privilege Triage — PSWA token/group checks and the distinction between triage output and the AD reset path.
- AD - WinRM Foothold — PSWA shell identity and client/tool boundary.
- AD - PowerShell Web Access.md — new dedicated PFX, IIS, ASP.NET state, browser, and PSWA stage.
- AD - Clean Down — hosts-file and un-restored target-password caveat.
- Index.md and RUNBOOK V2.md — PSWA stage and Search cross-links.

### Command reference layer

- COMMAND APPENDIX/Active Directory.md — gMSA reset, WMI proof, PFX, and PSWA syntax.
- COMMAND APPENDIX/Password Attacks.md — PFX cracking and one-password spray.
- COMMAND APPENDIX/Web Applications.md — homepage image review and certificate-authenticated PSWA.
- COMMAND APPENDIX/Windows Privilege Escalation.md — PSWA identity triage and gMSA handoff.
- COMMAND APPENDIX/COMMAND APPENDIX.md — Search coverage map.

### Explanation and routing layer

- COMMAND BREAKDOWNS/Active Directory (Breakdowns).md — Kerberos name resolution, gMSA identity semantics, delegated reset, and Windows quoting.
- COMMAND BREAKDOWNS/Password Attacks (Breakdowns).md — TGS and PFX as separate offline attacks.
- COMMAND BREAKDOWNS/COMMAND BREAKDOWNS.md — Search coverage map.
- DECISION TREE/Active Directory (Decision Tree).md — IIS-to-gMSA-to-delegated-reset chain.
- DECISION TREE/Secrets & Credentials (Decision Tree).md — PFX/PKCS#12 and gMSA branches.
- DECISION TREE/Web Applications (Decision Tree).md — image credential, XLSX, AD CS, and PSWA branches.
- DECISION TREE/DECISION TREE.md — Search coverage map.

### Methodology and curriculum layer

- METHODOLOGY CHEAT SHEET/Active Directory Methodology.md — combined IIS, Kerberos, SMB, PFX, PSWA, gMSA, ACL sequence.
- METHODOLOGY CHEAT SHEET/Windows Methodology.md — certificate-to-PSWA shell pattern.
- METHODOLOGY CHEAT SHEET/METHODOLOGY CHEAT SHEET.md — completed Search example.
- MODERN TOOLING/NetExec.md — full Search NetExec use.
- MODERN TOOLING/BloodyAD.md — gMSA delegated password reset.
- MODERN TOOLING/John the Ripper.md — Kerberos and PFX cracking example.
- MODERN TOOLING/MODERN TOOLING.md — Search coverage statement.
- MODULES/16. Password Attacks.md — TGS, PFX, and spray.
- MODULES/17. Windows Privilege Escalation.md — PSWA shell and administrator proof.
- MODULES/22. Active Directory Introduction and Enumeration.md — IIS-led AD enumeration and gMSA read.
- MODULES/23. Attacking Active Directory Authentication.md — TGS, PFX, and certificate authentication.
- MODULES/24. Lateral Movement in Active Directory.md — gMSA delegated reset and WMI proof.
- MODULES/MODULES.md — Search coverage map.

### Exam execution layer

- EXAM RUNBOOK/02 - Web and Services.md — image-first IIS and certificate branch.
- EXAM RUNBOOK/04 - Windows Fast Path.md — PSWA as a Windows shell path.
- EXAM RUNBOOK/05 - Active Directory Fast Path.md — web credential, Kerberos, SMB profile, and gMSA routing.
- EXAM RUNBOOK/06 - Modern Tooling.md — NetExec as a speed layer with manual proof.
- EXAM RUNBOOK/10 - Scenario Matrix.md — Search route and new T50 client-certificate/PSWA branch.

## Technique coverage

| Search lesson | Reusable destinations |
|---|---|
| Nmap raw socket failure and sudo fallback | Search write-up, service scan, Windows methodology |
| IIS staff image credential | Web Enum, Web Applications appendix/decision tree, Web exam runbook |
| Anonymous SMB and RedirectedFolders$ | SMB/AD appendix, credential validation, AD decision tree |
| Kerberos DNS failure | Kerberoasting, AD breakdowns, AD methodology |
| Kerberoast and controlled password reuse | Kerberoasting, Password Attacks, NetExec, Scenario Matrix |
| XLSX ZIP/XML and hidden credential data | Web decision tree, Search write-up, credential-search reasoning |
| PFX/P12 cracking and client certificate | PowerShell Web Access runbook, Password Attacks, Web appendix, Secrets tree |
| AD CS /certsrv clue | Web Enum, Web decision tree, Search write-up |
| Stateful PSWA login | PSWA runbook, Windows methodology, Windows exam runbook |
| gMSA and PrincipalsAllowedToReadPassword | Group Triage, BloodHound, AD appendix, Module 22, Secrets tree |
| gMSA delegated password reset | ForceChangePassword, BloodyAD, AD breakdowns, Modules 23/24 |
| WMI proof and quote continuation failure | NetExec, Windows appendix, AD breakdowns, Module 24 |
| Target and local cleanup | Clean Down, Search write-up, evidence/clean-down exam route |

## Deliberate boundaries

- The old RUNBOOK folder was not changed; the vault context identifies RUNBOOK V2 as the maintained methodology.
- The five reference write-ups were read but not modified.
- Flag values and reusable secret values are not duplicated in the narrative; the private source loot and transcript remain authoritative.
- The manual transcript says boxdone was run, but it does not prove that Tristan's original password was restored. The write-up records that uncertainty instead of inventing cleanup.

## Verification

- Search write-up exists and is 788 lines.
- Search runbook exists and is linked from RUNBOOK V2 Index.
- Search raw log exists in BOX LOGS and remains 1,141 lines.
- All 23 referenced screenshot filenames exist in the source workspace.
- Search appears in the box hubs, methodology hubs, command hubs, decision trees, module notes, and exam runbooks listed above.
- No public response output repeats the flag values or private passwords.
