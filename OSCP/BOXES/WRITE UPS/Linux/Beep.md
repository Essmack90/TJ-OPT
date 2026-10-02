---
tags: [HTB, Beep, Linux, Elastix, FreePBX, LFI, CVE-2012-4869, CVE-2012-4870, Retrospective]
platform: HackTheBox
os: Linux
hostname: BEEP
difficulty: Easy
ip: $BoxIP
status: Retrospective stub
aliases: [Beep]
---

# HTB: Beep, Retrospective Kill Chain

## The gist

[RETRO: Beep] Broad service enumeration found legacy HTTP/HTTPS Elastix with FreePBX, plus SSH and telephony services. Directory and parameter discovery identified the Elastix configuration/LFI surface; reviewed FreePBX research covered CVE-2012-4869 and CVE-2012-4870 before the Linux foothold and post-exploitation path.

## Kill chain

1. Nmap mapped the legacy multi-service host and the HTTP-to-HTTPS redirect.
2. Fingerprinting confirmed Elastix/FreePBX and legacy TLS; common paths exposed `/configs/` and the `graph.php` LFI candidate.
3. Exploit research linked the matching FreePBX results to CVE-2012-4869 and CVE-2012-4870; checks stayed version- and endpoint-scoped.
4. The resulting Linux access was followed by identity, credential, and privilege checks before proof capture.

## Tree and CVE reconciliation

The chain is covered by Recon, Web Enum, LFI/RFI, Known CVE, Rev Shell, Local Enum, Linux PrivEsc, and Root. CVE Quick-Wins now carries the two FreePBX identifiers recorded in the run.
