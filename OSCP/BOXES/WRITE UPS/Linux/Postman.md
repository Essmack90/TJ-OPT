---
tags: [HTB, Postman, Linux, Redis, SSH, Webmin, CVE-2019-12840, Retrospective]
platform: HackTheBox
os: Linux
hostname: POSTMAN
difficulty: Easy
ip: $BoxIP
status: Retrospective stub
aliases: [Postman]
---

# HTB: Postman, Retrospective Kill Chain

## The gist

[RETRO: Postman] Unauthenticated Redis exposed writable configuration. A scoped SSH public-key write produced a Redis foothold; an encrypted private key at `/opt/id_rsa.bak` was cracked offline, and the recovered account access led to authenticated Webmin MiniServ 1.910 command injection (CVE-2019-12840) and root proof. Secrets and flag values are intentionally omitted.

## Kill chain

1. Full TCP and service scans identified SSH 22, HTTP 80, Redis 6379, and Webmin MiniServ 1.910 on 10000. Web content discovery found the public upload directory but no required web foothold.
2. Redis accepted unauthenticated commands. `CONFIG GET dir` and `CONFIG GET dbfilename` confirmed the writable persistence boundary; a temporary public key was written for the Redis service account and removed during cleanup.
3. The Redis shell exposed `/opt/id_rsa.bak`. `ssh2john` converted the encrypted key and John recovered its passphrase without storing it in the log.
4. The recovered access reached the Webmin login. Version-matched Exploit-DB 46984 / CVE-2019-12840 package-update command injection yielded a one-shot root identity proof.
5. Guided HTB questions were submitted one at a time through Firefox; user and root flags were accepted, and the page displayed the completed-machine confirmation.

## Tree and CVE reconciliation

The chain is covered by Redis SSH-Key Write, Offline SSH Key Crack, SSH Access, Webmin MiniServ 1.910, and Root. CVE Quick-Wins carries CVE-2019-12840, and Port Oracle indexes Redis 6379 plus Webmin 10000. Target Redis configuration was restored and the temporary authorized key removed before close-out.
