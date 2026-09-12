# OSCP Exam Runbook

> [!tip] Fast mode
> This is the exam-time companion to [[OSCP/RUNBOOK V2/Index|RUNBOOK V2]]. It contains the shortest validated route, commands, and branch decisions. Use RUNBOOK V2 when a branch needs explanation or troubleshooting.

## Start here

1. [[OSCP/EXAM RUNBOOK/00 - Controller|Controller]]
2. [[OSCP/EXAM RUNBOOK/01 - Recon and Triage|Recon and Triage]]
3. Follow one branch: [[OSCP/EXAM RUNBOOK/02 - Web and Services|Web and Services]], [[OSCP/EXAM RUNBOOK/03 - Linux Fast Path|Linux Fast Path]], [[OSCP/EXAM RUNBOOK/04 - Windows Fast Path|Windows Fast Path]], or [[OSCP/EXAM RUNBOOK/05 - Active Directory Fast Path|Active Directory Fast Path]]
4. Use [[OSCP/EXAM RUNBOOK/06 - Modern Tooling|Modern Tooling]] when the faster tool is appropriate.
5. Use [[OSCP/EXAM RUNBOOK/07 - Branch Matrix|Branch Matrix]] when output does not match the primary path.
6. Use [[OSCP/EXAM RUNBOOK/09 - Box Route Index|Box Route Index]] to jump to a validated write-up route.
7. Use [[OSCP/EXAM RUNBOOK/10 - Scenario Matrix|Scenario Matrix]] when a write-up-specific technique is identified.
8. Close with [[OSCP/EXAM RUNBOOK/08 - Evidence and Clean Down|Evidence and Clean Down]].

## The fast loop

Every page follows the same rhythm:

1. **Run this**: execute the smallest command block that proves the next decision.
2. **Example output**: compare the shape of the result, not the exact values.
3. **What did you get?**: select one matching branch.
4. **Open next**: follow the linked page and save the output before moving on.

If no row matches, save the result and return to [[OSCP/EXAM RUNBOOK/07 - Branch Matrix|Branch Matrix]] rather than guessing.

## Operating rules

- Run the cheapest command that proves the next decision.
- Save raw output under `$BoxDir/nmap/` or `$BoxDir/loot/` before filtering it.
- Use one credential validation per likely account or service. Do not spray by default.
- Prefer a direct confirmed privilege boundary over a more complicated alternative.
- Use Burp Suite for request discovery and replay, not as a replacement for a confirmed manual request.
- Use BloodHound GUI to choose AD edges, then validate the exact edge with NetExec, LDAP, Impacket, or bloodyAD.
- Keep all box-specific values in variables. Never put secrets or flags in this runbook.

## Update loop after every box

1. Add the fastest successful route to the relevant page.
2. Add one failure branch only when it changes the next command.
3. Link the write-up, RUNBOOK V2 stage, module, decision tree, and modern-tooling page.
4. Add the box to the relevant Seen in section and master box list.
5. Run a wikilink audit and `git diff --check` before closing the update.

## Coverage seeded from existing write-ups

- Linux: [[OSCP/BOXES/WRITE UPS/Linux/Blocky|Blocky]], [[OSCP/BOXES/WRITE UPS/Linux/CronOS|CronOS]], [[OSCP/BOXES/WRITE UPS/Linux/DevOops|DevOops]], [[OSCP/BOXES/WRITE UPS/Linux/Mirai|Mirai]], [[OSCP/BOXES/WRITE UPS/Linux/Traceback|Traceback]], and [[OSCP/BOXES/WRITE UPS/Linux/Traverxec|Traverxec]]
- Windows: [[OSCP/BOXES/WRITE UPS/Windows/Bastard|Bastard]], [[OSCP/BOXES/WRITE UPS/Windows/Conceal|Conceal]], [[OSCP/BOXES/WRITE UPS/Windows/Love|Love]], and [[OSCP/BOXES/WRITE UPS/Windows/MarkUp|MarkUp]]
- Active Directory: [[OSCP/BOXES/WRITE UPS/AD/RockyColt|RockyColt]] and [[OSCP/BOXES/WRITE UPS/AD/Vintage|Vintage]]

## Detailed reference

- [[OSCP/RUNBOOK V2/Index|RUNBOOK V2]] -- full explanatory workflow
- [[OSCP/OSCP COMMAND MASTER CHEATSHEET|Command Master Cheatsheet]] -- syntax lookup
- [[OSCP/COMMAND APPENDIX/COMMAND APPENDIX|Command Appendix]] -- technique command pages
- [[OSCP/MODERN TOOLING/MODERN TOOLING|Modern Tooling]] -- tool-specific notes
- [[OSCP/BOXES/WRITE UPS/WRITE UPS|Write-up index]] -- validated box routes
- [[OSCP/EXAM RUNBOOK/10 - Scenario Matrix|Scenario Matrix]] -- every write-up route and distinct technique branch
