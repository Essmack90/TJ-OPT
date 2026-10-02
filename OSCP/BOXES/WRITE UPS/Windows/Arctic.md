---
tags: [HTB, Arctic, Windows, ColdFusion, JRun, CVE-2010-2861, CVE-2009-2265, RCE, Retrospective]
platform: HackTheBox
os: Windows
hostname: ARCTIC
difficulty: Easy
ip: $BoxIP
status: Retrospective stub
aliases: [Arctic]
---

# HTB: Arctic, Retrospective Kill Chain

## The gist

[RETRO: Arctic] Nmap and web enumeration identified ColdFusion/JRun on the alternate web port. The reviewed CVE-2010-2861 traversal and CVE-2009-2265 ColdFusion upload/RCE research led to a Windows foothold, followed by local Windows privilege escalation and proof capture.

## Kill chain

1. Full TCP and version scans exposed the ColdFusion/JRun service.
2. Gobuster and HTTP checks mapped the alternate web surface and CFIDE paths.
3. Exploit research matched ColdFusion 8 to CVE-2010-2861 and CVE-2009-2265; the RCE path was reviewed before use.
4. The callback was stabilised, Windows identity and service context were recorded, and the privilege boundary was validated.
5. Evidence and cleanup were recorded in the private Arctic run log.

## Tree and CVE reconciliation

The chain is covered by Recon, Web Exploit, Known CVE, Rev Shell, Windows PrivEsc, and Root/SYSTEM. CVE Quick-Wins now includes both ColdFusion CVEs.
