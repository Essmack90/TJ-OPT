---
tags: [HTB, Jeeves, Windows, Jenkins, KeePass, NTFS ADS, Pass-the-Hash, Retrospective]
platform: HackTheBox
os: Windows
hostname: JEEVES
difficulty: Easy
ip: $BoxIP
status: Retrospective stub
aliases: [Jeeves]
---

# HTB: Jeeves, Retrospective Kill Chain

## The gist

[RETRO: Jeeves] Jenkins Script Console access led to a Windows foothold. A KeePass database was converted with `keepass2john` and cracked offline with John; the recovered NTLM material was validated with pass-the-hash, and the final proof was read from an NTFS Alternate Data Stream.

## Kill chain

1. Web enumeration fingerprinted Jenkins and the `/askjeeves/script` context.
2. Anonymous Script Console RCE was validated with a harmless Groovy identity probe.
3. KeePass data was staged locally; `keepass2john` produced an offline hash and John recovered the approved credential entry.
4. The LM:NT/NTLM material was used with the pass-the-hash workflow via PsExec/Evil-WinRM.
5. The hidden root proof was read from its NTFS ADS with `more < file:stream` / PowerShell stream syntax.

## Tree reconciliation

The chain is covered by Jenkins Script Console RCE, KeePass Credential Extraction, Offline Hash Crack, Pass-the-Hash LM:NT, NTFS Alternate Data Streams, and Root/SYSTEM. No additional target-specific CVE was established in the Jeeves run.
