---
tags: [HTB, Blue, Windows, SMB, MS17-010, CVE-2017-0143, CVE-2017-0144, EternalBlue, Retrospective]
platform: HackTheBox
os: Windows
hostname: BLUE
difficulty: Easy
ip: $BoxIP
status: Retrospective stub
aliases: [Blue]
---

# HTB: Blue, Retrospective Kill Chain

## The gist

[RETRO: Blue] SMB enumeration and the Nmap MS17-010 check identified a vulnerable SMBv1 host under CVE-2017-0143. The reviewed EternalBlue path was tracked under CVE-2017-0144, followed by a Windows shell, local enumeration, and SYSTEM proof.

## Kill chain

1. Full TCP scanning found SMB/445 and the service identity.
2. SMB enumeration and `smb-vuln-ms17-010` produced the CVE-2017-0143 vulnerability evidence.
3. EternalBlue research and the reviewed exploit workflow covered the CVE-2017-0144 execution path.
4. The Windows callback was verified, local privilege context was recorded, and privileged proof was captured.

## Tree and CVE reconciliation

The chain is covered by SMB Enum, Known CVE, Service/Rev Shell, Windows PrivEsc, and Root/SYSTEM. CVE Quick-Wins now distinguishes the scanner identifier from the EternalBlue execution entry.
