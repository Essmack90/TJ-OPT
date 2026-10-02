---
tags: [HTB, Sense, FreeBSD, pfSense, CVE-2014-4688, CVE-2016-10709, Retrospective]
platform: HackTheBox
os: FreeBSD
hostname: SENSE
difficulty: Easy
ip: $BoxIP
status: Retrospective stub
aliases: [Sense]
---

# HTB: Sense, Retrospective Kill Chain

## The gist

[RETRO: Sense] A legacy pfSense web surface exposed a support-file credential clue. The authenticated status RRD graph endpoint then provided a version-gated command-injection path to root; both flag paths were read and their values intentionally excluded from this note and the engagement log.

## Kill chain

1. Nmap and service fingerprinting mapped HTTP/HTTPS on legacy lighttpd and pfSense.
2. Web content discovery found the support-file and the authenticated graph endpoint; exposed values were kept redacted.
3. The lower-case support account authenticated with the supplied default credential, then the graph parameter was validated with a one-shot identity callback.
4. The callback returned root identity. The user and root flag paths were read without recording their contents.

## Tree and CVE reconciliation

The chain is covered by Recon, Web Enum, Web Auth, the pfSense Graph Command Injection node, Rev Shell, Local Enum, and Root. CVE Quick-Wins now carries the CVE-2016-10709 reference and the matching CVE-2014-4688 / Exploit-DB 43560 lineage.
