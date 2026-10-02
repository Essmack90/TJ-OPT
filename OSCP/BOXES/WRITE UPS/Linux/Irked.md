---
tags: [HTB, Irked, Linux, UnrealIRCd, CVE-2010-2075, Steganography, SUID, Retrospective]
platform: HackTheBox
os: Linux
hostname: IRKED
difficulty: Easy
ip: $BoxIP
status: Retrospective stub
aliases: [Irked]
---

# HTB: Irked, Retrospective Kill Chain

## The gist

[RETRO: Irked] Full-port scanning found UnrealIRCd 3.2.8.1 on non-standard IRC ports. The bounded `AB;id` backdoor probe matched CVE-2010-2075 and provided access; a steganography workflow recovered credential material, then the fixed-path SUID helper completed Linux privilege escalation.

## Kill chain

1. Full TCP scanning found SSH, IRC, and the non-standard UnrealIRCd listeners.
2. Banner and identity probes matched the UnrealIRCd backdoor workflow for CVE-2010-2075.
3. Post-shell enumeration found the image artifact; `steghide` and a private passphrase workflow recovered the next credential material.
4. Linux SUID enumeration identified the custom helper; its behavior was validated before root proof and cleanup.

## Tree and CVE reconciliation

The chain is covered by Recon, Known CVE, Rev Shell, Local Enum, the new Steganography node, Linux PrivEsc, and Root. CVE Quick-Wins now includes CVE-2010-2075.
