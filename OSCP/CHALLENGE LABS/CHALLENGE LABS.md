---
tags: [oscp, challenge-labs, MOCs]
---

# Challenge Labs

Multi-machine engagement labs. Not modules (no theory write-up) and not single boxes (too many machines for one write-up). Each lab is a mini pentest: enumerate everything, chain it together, get DA, write up the findings.

See [[28. Trying Harder - The Challenge Labs|M28]] for the full breakdown of what each lab involves.

---

## Structure

Each Challenge Lab lives in its own subfolder:
- One overview note (scope, assumed breach creds, scoring tracker, machine inventory)
- One file per standalone machine
- One file for the AD chain (all three machines together, one engagement)

RUNBOOK stage notes accumulate box_sources from CL machines the same as regular boxes.

---

## Recommended Order (Exam Prep Focus)

| Priority | Lab | Type | Notes |
|---|---|---|---|
| 1 | [[CL4 - OSCP Mock 1/CL4 Overview\|CL4]] | Mock Exam | Same structure as real OSCP+ |
| 2 | [[CL5 - OSCP Mock 2/CL5 Overview\|CL5]] | Mock Exam | |
| 3 | [[CL6 - OSCP Mock 3/CL6 Overview\|CL6]] | Mock Exam | |
| 4 | CL0 — SECURA | Scenario | ManageEngine, GPO abuse |
| 5 | CL1 — MEDTECH | Scenario | IoT/AD |
| 6 | CL2 — RELIA | Scenario | Perimeter breach |
| 7 | CL3 — SKYLARK | Scenario | Heavy pivoting, beyond OSCP scope |
| — | CL7-10 | Advanced | PEN-300 level, post-exam |

---

## Status

| Lab | Standalones | AD Chain | Total Score | Done? |
|---|---|---|---|---|
| CL4 | 0/60 | 0/40 | 0/100 | ⬜ |
| CL5 | — | — | — | ⬜ |
| CL6 | — | — | — | ⬜ |
| CL0 SECURA | — | — | — | ⬜ |
| CL1 MEDTECH | — | — | — | ⬜ |
| CL2 RELIA | — | — | — | ⬜ |
| CL3 SKYLARK | — | — | — | ⬜ |
## Why this matters for OSCP

Challenge labs combine separate techniques, so this page helps you practise routing from discovery to proof under time pressure.

## Relevant RUNBOOK V2 stages

- [[RUNBOOK V2/Index]]
- [[RUNBOOK V2/Linux - Service Scan]]
- [[RUNBOOK V2/Windows - Service Scan]]

## Related modules

- [[MODULES/28. Trying Harder - The Challenge Labs]] -- challenge-lab practice and review
- [[MODULES/27. Assembling the Pieces]] -- combining attack paths
## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
