---
tags: [HTB, Dog, Linux, Backdrop CMS, Git, File Upload, Web Shell, Retrospective]
platform: HackTheBox
os: Linux
hostname: DOG
difficulty: Easy
ip: $BoxIP
status: Retrospective stub
aliases: [Dog]
---

# HTB: Dog, Retrospective Kill Chain

## The gist

[RETRO: Dog] Web fingerprinting identified Backdrop CMS. Repository/configuration discovery exposed application material, and a reviewed Backdrop module/archive upload path produced a PHP shell before Linux local enumeration and privilege escalation.

## Kill chain

1. Nmap and HTTP fingerprinting mapped the Backdrop CMS surface and exposed `/web.config` as a useful clue.
2. Directory and repository discovery identified application files and the module upload boundary.
3. A controlled module archive/PHP shell upload produced the foothold.
4. Local Linux enumeration and privilege checks completed the path to proof.

## Tree reconciliation

The chain is covered by Web Enum, Web Exploit, Upload Bypass, Web Shell, Local Enum, Linux PrivEsc, and Root. The run did not establish a target-specific CVE requiring a new Quick-Win entry.
