# SysReptor

Open-source pentest *reporting* platform, not just a note-taking tool. Speeds up the specific handoff [[Report Writing For Pen Testers#5.1. Understanding Note-Taking|5.1's raw notes]] into [[Report Writing For Pen Testers#5.2. Writing Effective Technical Penetration Testing Reports|5.2's finished client report]], not the note-taking itself, this vault's own Obsidian workflow already covers that half well.

---

## What it replaces, and why it's faster

The module teaches note-taking (Obsidian/CherryTree/Sublime, [[Report Writing For Pen Testers#5.1.4. Choosing a Note-Taking Tool|5.1.4]]) and report structure (Executive Summary, Technical Findings, remediation tables, [[Report Writing For Pen Testers#5.2. Writing Effective Technical Penetration Testing Reports|5.2]]) as two separate manual skills, you take notes as you go, then hand-assemble a formatted report from them afterward. SysReptor collapses that second step: markdown-based findings with drag-and-drop evidence, built-in severity scoring, and one-click Markdown → PDF export via customizable HTML/CSS templates. It also has direct integration for pulling in Burp/Nessus/Nmap/OpenVAS/ZAP output rather than manually copy-pasting scan results into a findings table.

**Worth being precise about what this doesn't replace:** the actual skill taught in 5.1 and 5.2, writing precise notes as you go, and structuring findings so both a technical and non-technical audience can use them, doesn't go away. SysReptor is a faster way to *format and deliver* that same disciplined content, not a shortcut around doing the disciplined note-taking itself.

## Install

Free and open-source, self-hosted (Docker-based) or a hosted cloud version:
```bash
# Self-hosted, official quick-start (see their docs for the current compose file)
git clone https://github.com/Syslifters/sysreptor
cd sysreptor/deploy
docker compose up -d
```

## OSCP-specific relevance

A companion project, [Syslifters/OffSec-Reporting](https://github.com/Syslifters/OffSec-Reporting), ships ready-made report templates for OSCP/OSCP+/OSWP/OSEP and the rest of the OffSec certification line, built to mirror OffSec's own official report structure, explicitly **"with kind permission by OffSec."** Worth stating precisely rather than overclaiming: that's OffSec sanctioning the *template structure*, not an official OffSec endorsement of SysReptor itself as "the" approved tool. Still a genuinely strong signal, and a good option specifically if the note-to-report handoff is the part that feels clunky with a plain markdown vault.

## Where this applies in the vault

- [[Report Writing For Pen Testers#5.1.4. Choosing a Note-Taking Tool|5.1.4]], listed as a fourth option alongside Sublime/CherryTree/Obsidian
- [[Report Writing For Pen Testers#5.2. Writing Effective Technical Penetration Testing Reports|5.2]], the report-structure/findings-table half this tool actually accelerates

#### Tags: #ModernTooling #SysReptor #ReportWriting #ReportingPlatform
