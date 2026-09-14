---
tags: [OSCP, EE, Audit, HTB, Optimum, Windows]
box: Optimum
status: Complete
date: 2026-09-14
---

# HTB Optimum - EE Audit

## Result

The Optimum manual run has been written up and propagated through the relevant OSCP vault layers. The write-up follows the established box format, uses variables instead of target-specific connection details, keeps private evidence outside Obsidian, and joins the command, explanation, routing, methodology, curriculum, and box-index pages with wikilinks.

## Source audit

| Item | Result |
|---|---|
| Manual workspace | `/home/kali/Platforms/HackTheBox/Optimum/` |
| Raw command/output log | `Optimum.log`, 471 lines |
| Scan artifacts | `nmap/allports.*` and `nmap/services.*` |
| Exploit evidence | `exploits/49125.py`, reviewed locally before use |
| Staging material | `www/Sherlock.ps1`, `www/bfill.exe`, callback scripts, and `www/nc.exe` |
| Private loot | `loot/flags.txt`, retained outside the vault |
| Screenshots | Eight private PNG files remain in the source workspace; none were copied or embedded in Obsidian |
| Completed proof | User and root proof were read privately and are not reproduced here |
| Cleanup boundary | Local `boxdone` was recorded; target-side deletion was not fully evidenced, so the write-up marks target cleanup as uncertain |

## Required write-up-format audit

Five previous write-ups were read in full before drafting Optimum:

1. [[OSCP/BOXES/WRITE UPS/Linux/Traceback|Traceback]]
2. [[OSCP/BOXES/WRITE UPS/Linux/Bratarina|Bratarina]]
3. [[OSCP/BOXES/WRITE UPS/AD/Vintage|Vintage]]
4. [[OSCP/BOXES/WRITE UPS/Linux/Pebbles|Pebbles]]
5. [[OSCP/BOXES/WRITE UPS/Windows/Bastard|Bastard]]

The resulting note uses the shared formula: gist, box information, vulnerability summary, evidence and loot, variables, numbered route, evidence boundaries, gotchas, RUNBOOK V2 stages, private flag handling, cleanup, attack chain, tools, credentials without secret values, remediation, lessons, related boxes, external resources, and OSCP relevance.

## Everything Everywhere mapping

### Box and evidence layer

- [[OSCP/BOXES/WRITE UPS/Windows/Optimum|Optimum write-up]] added in the established Windows format with numbered, replayable commands.
- [[OSCP/BOXES/BOX LOGS/BOX LOGS|Box logs index]] updated with the private source workspace reference.
- [[OSCP/BOXES/WRITE UPS/Windows/Windows|Windows write-up MOC]] updated with the Optimum link.
- [[OSCP/BOXES/WRITE UPS/WRITE UPS|Write-up MOC]] updated with the Optimum link.
- [[OSCP/BOXES/MASTER BOX LIST|Master box list]] marked Optimum complete and updated in the Windows dashboard, schedule, phase tracker, and methodology notes.

### Command reference layer

- [[OSCP/OSCP COMMAND MASTER CHEATSHEET|OSCP Command Master Cheatsheet]] now has separated HFS and old-Windows kernel triage sections.
- [[OSCP/COMMAND APPENDIX/Web Applications|Web Applications]] now covers Rejetto HFS 2.3 command injection.
- [[OSCP/COMMAND APPENDIX/Web Requests & Delivery|Web Requests and Delivery]] now covers HFS command delivery and PowerShell staging.
- [[OSCP/COMMAND APPENDIX/Windows Privilege Escalation|Windows Privilege Escalation]] now covers MS16-098 and the CPU prerequisite check.
- [[OSCP/COMMAND APPENDIX/COMMAND APPENDIX|Command Appendix MOC]] now links the Optimum route.

### Explanation and routing layer

- [[OSCP/COMMAND BREAKDOWNS/Web Applications (Breakdowns)|Web Applications breakdowns]] explains HFS command injection, staging, and the web-worker boundary.
- [[OSCP/COMMAND BREAKDOWNS/Locating Public Exploits (Breakdowns)|Locating Public Exploits breakdowns]] explains product/version matching and PoC review.
- [[OSCP/COMMAND BREAKDOWNS/Privilege Escalation & Local Exploitation (Breakdowns)|Privilege Escalation breakdowns]] explains Sherlock limitations, the one-CPU MS16-032 failure, and MS16-098 selection.
- [[OSCP/COMMAND BREAKDOWNS/COMMAND BREAKDOWNS|Command Breakdowns MOC]] now links the Optimum route.
- [[OSCP/DECISION TREE/Web Applications (Decision Tree)|Web Applications decision tree]] now routes HFS 2.3 to the reviewed exploit and clean callback.
- [[OSCP/DECISION TREE/Locating Public Exploits (Decision Tree)|Locating Public Exploits decision tree]] now includes the HFS matching branch.
- [[OSCP/DECISION TREE/Windows Privilege Escalation (Decision Tree)|Windows Privilege Escalation decision tree]] now includes the one-processor caveat and MS16-098 reference.
- [[OSCP/DECISION TREE/DECISION TREE|Decision Tree MOC]] now links the Optimum route.

### Methodology and curriculum layer

- [[OSCP/METHODOLOGY CHEAT SHEET/Windows Methodology|Windows Methodology]] now includes the HFS-to-native-callback-to-kernel-selection pattern.
- [[OSCP/METHODOLOGY CHEAT SHEET/METHODOLOGY CHEAT SHEET|Methodology MOC]] now links Optimum.
- [[OSCP/MODULES/13. Locating Public Exploits|Module 13]] now includes the Optimum source-review case study.
- [[OSCP/MODULES/17. Windows Privilege Escalation|Module 17]] now includes the processor-aware MS16-098 application.
- [[OSCP/MODULES/MODULES|Modules MOC]] now links both relevant module applications.
- [[OSCP/REFERENCE CARDS/FAQ - Quick Answers|FAQ]] now covers HFS matching, false-positive Sherlock output, and web-worker versus native callback failures.

### Execution layer

- [[OSCP/RUNBOOK V2/Windows - Exploit Search|Windows - Exploit Search]] now includes HFS 2.3 and Exploit-DB 49125.
- [[OSCP/RUNBOOK V2/Windows - Shell Received|Windows - Shell Received]] now includes the clean callback handoff.
- [[OSCP/RUNBOOK V2/Windows - Privilege Triage|Windows - Privilege Triage]] now includes `systeminfo`, Sherlock, CPU checks, and MS16-098.
- [[OSCP/RUNBOOK V2/Windows - Clean Down|Windows - Clean Down]] now includes the HFS and kernel-payload cleanup boundary.
- [[OSCP/RUNBOOK V2/Index|RUNBOOK V2 Index]] now lists Optimum in the Seen in routes.

### Exam execution layer

- [[OSCP/EXAM RUNBOOK/02 - Web and Services|Web and Services]] now includes the HFS version-match and Exploit-DB 49125 branch.
- [[OSCP/EXAM RUNBOOK/04 - Windows Fast Path|Windows Fast Path]] now includes the clean-callback and processor-aware MS16-098 route.
- [[OSCP/EXAM RUNBOOK/07 - Branch Matrix|Branch Matrix]] now routes HFS 2.3 and old Windows kernel candidates.
- [[OSCP/EXAM RUNBOOK/08 - Evidence and Clean Down|Evidence and Clean Down]] now records the Optimum evidence boundary.
- [[OSCP/EXAM RUNBOOK/09 - Box Route Index|Box Route Index]] now lists Optimum.
- [[OSCP/EXAM RUNBOOK/10 - Scenario Matrix|Scenario Matrix]] now includes the Optimum route and T52 kernel-triage branch.
- [[OSCP/EXAM RUNBOOK/Index|Exam Runbook Index]] now includes Optimum in Windows coverage.

## Technique coverage

| Optimum lesson | Reusable destinations |
|---|---|
| Single-port TCP discovery and HTTP fingerprinting | Windows service scan, port triage, web enumeration, and write-up |
| Exact HFS 2.3 identification | Web Applications appendix, exploit-search runbook, decision trees |
| Exploit-DB source review and local syntax validation | Module 13, exploit-search breakdown, command master |
| HFS command injection to PowerShell callback | Web appendix, Web Requests and Delivery, Shell Received, web breakdown |
| Web worker versus native callback context | Shell Received, Windows Privilege Triage, privilege breakdown, FAQ |
| `systeminfo` before local exploit selection | Windows Methodology, Privilege Triage, Windows decision tree |
| Sherlock as candidate triage rather than final proof | Module 17, privilege appendix, methodology, FAQ |
| One-processor MS16-032 failure | Windows decision tree, privilege breakdown, Optimum write-up |
| MS16-098 `bfill.exe` from a clean callback | Windows privilege appendix, Module 17, command master, runbook |
| Private evidence and cleanup uncertainty | Optimum write-up, Windows Clean Down, this audit |

## Deliberate boundaries

- The source transcript and screenshots remain authoritative in the private manual workspace. No PNG files were copied into the write-up vault.
- Private flags, callback values, passwords, hashes, and exact target-specific proof values are not reproduced in this audit or the public-facing write-up.
- The audit records target-side cleanup as uncertain because the transcript does not contain a complete deletion and verification block. It does not convert a local closeout command into proof of remote cleanup.
- Existing unrelated notes were not rewritten. Changes were additive and limited to pages that carry the Optimum techniques or route the relevant links.

## Verification

- [x] Optimum write-up exists and uses the numbered command-by-command format.
- [x] Five reference write-ups were read in full before drafting.
- [x] The write-up contains no PNG embeds.
- [x] Private flag and credential values are excluded from the vault additions.
- [x] HFS, SearchSploit, PowerShell staging, Sherlock, CPU prerequisites, and MS16-098 are cross-linked across the appropriate vault layers.
- [x] Box hubs, master list, command master, appendices, breakdowns, decision trees, methodology, modules, FAQ, RUNBOOK V2, exam runbook, and MOCs were updated.
- [x] Final filesystem and Markdown hygiene checks were run after editing.
