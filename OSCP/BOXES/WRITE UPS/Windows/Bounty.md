---
tags: [HTB, Bounty, Windows, IIS, ASP.NET, web.config, Upload Bypass, Retrospective]
platform: HackTheBox
os: Windows
hostname: BOUNTY
difficulty: Easy
ip: $BoxIP
status: Retrospective stub
aliases: [Bounty]
---

# HTB: Bounty, Retrospective Kill Chain

## The gist

[RETRO: Bounty] Web enumeration found the IIS transfer endpoint. A controlled upload workflow established the `web.config` filter/handler bypass, then a separate classic ASP shell produced the Windows foothold and the local privilege path.

## Kill chain

1. Nmap and HTTP discovery identified IIS and the upload form.
2. The upload behavior was tested with harmless configuration probes before the handler mapping was selected.
3. `web.config` plus a separate shell file bypassed the upload restriction and yielded a bounded callback.
4. Windows identity, service, and privilege enumeration completed the chain and proof was captured.

## Tree reconciliation

The chain is covered by Web Enum, Upload Bypass, IIS web.config Upload Bypass, Web Shell/Rev Shell, Windows PrivEsc, and Root/SYSTEM.
