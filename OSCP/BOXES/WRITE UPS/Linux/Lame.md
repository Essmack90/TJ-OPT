---
tags: [HTB, Lame, Linux, Samba, SMB, CVE-2007-2447, Distccd, Retrospective]
platform: HackTheBox
os: Linux
hostname: LAME
difficulty: Easy
ip: $BoxIP
status: Retrospective stub
aliases: [Lame]
---

# HTB: Lame, Retrospective Kill Chain

## The gist

[RETRO: Lame] Focused enumeration found anonymous FTP, null-session SMB, Samba 3.0.20-Debian, and distccd. The version-matched Samba `usermap_script` path produced a controlled one-shot callback as root; identity and location were checked without recording flag values.

## Kill chain

1. Full and top-port scans mapped FTP 21, SSH 22, SMB 139/445, and distccd 3632; no HTTP service was present.
2. Anonymous FTP and SMB null-session checks exposed service context, shares, and users. The vsftpd 2.3.4 backdoor check was negative.
3. Samba 3.0.20-Debian matched CVE-2007-2447. A manual TCP/139 `usermap_script` callback confirmed `uid=0(root)`.
4. Host identity and working location were recorded; listeners were stopped and no target files were left behind.

## Tree and CVE reconciliation

The chain is covered by Recon, SMB Enum, the Samba usermap RCE node, Rev Shell, and Root. CVE Quick-Wins carries CVE-2007-2447. Distccd 3632 is indexed in Port Oracle for a separate version-gated follow-up; it was not needed after the root callback.
