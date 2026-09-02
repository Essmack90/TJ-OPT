# OSCP & Red Teaming Machine Master Lists

> **Formatted, consolidated lists from LainKusanagi's spreadsheet 

---

## Instructions
- ✅ **Check off** machines as you complete them.
- 📝 **Use the Notes column** to track key techniques or vulnerabilities discovered.
- 🔄 **Revisit** machines that gave you trouble.

> **🔴 BOF / Exploit Dev Priority (Phase 1 — do these first):**
> **Windows stack BOF:** Chatterbox (done ✅) → Kyoto → Buff → SLMail → Brainpan
> **Linux stack BOF:** Ariti → Dawn2 → Dawn3 → Malbec
> **Advanced (Phase 2):** CVE-2024-56331 → RPC1 → Precision → Wasmo
> Use VulnServer between boxes to drill specific stages (crash, offset, bad chars, EIP, shellcode) without a full box.
> Do not start Phase 2 until you can reproduce the full Windows BOF chain from notes alone in under 90 minutes.

---

## Weekly Schedule

> Pick boxes from your current week's row. When done, mark them off in the tracking tables below.
> Labs (module exercises) always come before boxes. If labs are incomplete, do them first.

### Phase 1 - Foundation (Sep 1–28)

| Week | Dates | Primary Focus | Daily Target | Boxes (this week's pool) |
|---|---|---|---|---|
| P1-W1 | Sep 1–7 | Exploit dev labs: crash → offset → bad chars | 2 boxes/day, labs first | Ariti, Dawn2, Covfefe (BOF) · Nibbles, Bashed, OpenAdmin (Linux) · midnight (Windows) · Active (AD) |
| P1-W2 | Sep 8–14 | Exploit dev labs: EIP → JMP ESP → shellcode → callback | 2 boxes/day, labs first | Dawn3, Malbec (BOF) · Kyoto, Panic, Buff, midnight, Devel (Windows) · Jarvis (Linux) · Active (AD) |
| P1-W3 | Sep 15–21 | Password attacks + client-side labs | 2 boxes/day, labs first | Swagshop, Networked, Poison, Hetemit, Sumo (Linux) · midnight, Panic (Windows) · Brainpan (BOF) · Active (AD) |
| P1-W4 | Sep 22–28 | AD module labs + tunnelling labs | 2 boxes/day, labs first | OpenAdmin, Hetemit, Tartarsauce, Pilgrimage (Linux) · Kyoto, Panic (Windows) · Active, Active (AD) · Busqueda (flexible) |

### Phase 2 - Windows Depth (Oct 1–28)

| Week | Dates | Primary Focus | Daily Target | Boxes (this week's pool) |
|---|---|---|---|---|
| P2-W1 | Oct 1–7 | Windows service abuse | 2–3 boxes/day, 14–16 total | Granny, Devel, Arctic, Silo, Fuse, Compromised (Windows) · Tartarsauce, Jarvis, Breakout (Linux) · Cicada, Active (AD) · Butch (BOF) · Bolt (web) · Grandpa (flexible) |
| P2-W2 | Oct 8–14 | Windows credential hunting | 2–3 boxes/day, 14–16 total | Artic, Jeeves, Bounty, Secnotes, Querier, Access (Windows) · Pandora, Magic, Precious (Linux) · Nara, EscapeTwo (AD) · Buff (BOF) · Backend (web) · Sniper (flexible) |
| P2-W3 | Oct 15–21 | Windows token and Potato privilege escalation | 2–3 boxes/day, 14–16 total | Algernon, Craft2, Fuse, Grandpa, Remote, Love (Windows) · Tabby, Pwned, Escape (Linux) · Cicada, Flight (AD) · Panic (BOF) · Forge (web) · Arctic (flexible) |
| P2-W4 | Oct 22–28 | Windows kernel and scheduled-task abuse | 2–3 boxes/day, 14–16 total | Optimum, Bastard, Grandpa, Arctic, MarkUp, Fuse (Windows) · DriftingBlues6, Loly, Breakout (Linux) · Cicada, Heist (AD) · CVE-2024-56331 (BOF/local exploit) · Goodgames (web) · Sniper (flexible) |

### Phase 3 - Active Directory (Nov 1–Dec 14)

| Week | Dates | Primary Focus | Daily Target | Boxes (this week's pool) |
|---|---|---|---|---|
| P3-W1 | Nov 1–7 | AD enumeration: BloodHound + manual LDAP | 2–3 boxes/day, 14–16 total | Cicada, Nara, EscapeTwo, Heist, Active (AD) · Querier, Sniper, Bounty, Access (Windows) · Pandora, OpenAdmin, Magic (Linux) · Forge (web) · Busqueda (container) |
| P3-W2 | Nov 8–14 | Kerberoasting + AS-REP roasting | 2–3 boxes/day, 14–16 total | Escape, Timelapse, Heist, TheFrizz, Certified (AD) · Jeeves, Secnotes, Remote, Sniper (Windows) · Swagshop, Jarvis, Precious (Linux) · Backend (web) · Tabby (container) |
| P3-W3 | Nov 15–21 | Pass-the-Hash/Ticket + lateral movement | 2–3 boxes/day, 14–16 total | Administrator, Cicada, Nara, EscapeTwo, Heist (AD) · Silo, Bounty, Querier, Artic (Windows) · Magic, Nibbles, Hawat (Linux) · Pollution (web) · Escape (container) |
| P3-W4 | Nov 22–28 | ACL abuse + object permission chains | 2–3 boxes/day, 14–16 total | Certified, EscapeTwo, Nara, Heist, Active (AD) · Fuse, Silo, Optimum, MarkUp (Windows) · Busqueda, Pwned, Tabby (Linux) · Moderators (web) · Goodgames (container) |
| P3-W5 | Dec 1–7 | Full AD chain 1 - end to end | 2–3 boxes/day, 14–16 total | Puppy, Escape, Timelapse, Monteverde, TheFrizz (AD) · Silo, Craft2, Bastard, Access (Windows) · Forge, Pandora (Linux) · Sandworm (web) · Tabby (container) |
| P3-W6 | Dec 8–14 | Full AD chain 2 - different entry path | 2–3 boxes/day, 14–16 total | Puppy, Certified, Cicada, Nara, Heist (AD) · Optimum, Bastard, Fuse, Remote (Windows) · DriftingBlues6, Nibbles, OpenAdmin (Linux) · Nunchucks (web) · Escape (container) |

### Phase 4 - Advanced (Dec 15–Jan 18)

| Week | Dates | Primary Focus | Daily Target | Boxes (this week's pool) |
|---|---|---|---|---|
| P4-W1 | Dec 15–21 | Pivoting + SSH tunnelling | 2 boxes/day, 10–12 total | Forge, Moderators, Busqueda (advanced) · Remote, Silo, Grandpa (Windows) · Walla, Tabby (Linux) · Nara, Heist (AD) |
| P4-W2 | Dec 22–28 | Multi-hop pivoting + SOCKS | 2 boxes/day, 10–12 total | Gobox, Fetch, Registry (advanced cloud/container) · Craft2, Symbolic, Vector (Windows) · Tabby, Escape (Linux) · Certified, EscapeTwo (AD) |
| P4-W3 | Dec 29–Jan 4 | Client-side delivery + SSRF/SSTI | 2 boxes/day, 10–12 total | Goodgames, Backend, Pollution (advanced web) · Sniper, Artic, Bounty (Windows) · Nunchucks, Bolt (Linux) · Escape, Certified (AD) |
| P4-W4 | Jan 5–11 | Exploit modification from public advisories | 2 boxes/day, 10–12 total | CVE-2024-56331, RPC1, Precision, Wasmo (advanced binary) · Optimum, Bastard (Windows) · Sandworm, Magic (Linux) · Cicada, EscapeTwo (AD) |
| P4-W5 | Jan 12–18 | Consolidation and timed advanced repetitions | 2 boxes/day, 10–12 total | Precision, Wasmo, RPC1 (advanced) · Fuse, Algernon, MarkUp (Windows) · Forge, Nunchucks (Linux) · Flight, Heist (AD) |

### Phase 5 - Mock Exams (Jan 19–Feb 22)

| Week | Dates | Primary Focus | Daily Target | Boxes (this week's pool) |
|---|---|---|---|---|
| P5-W1 | Jan 19–25 | Mock 1: standalones timed for 6 hours | 0 extra boxes | Three unseen standalones: one Linux, one Windows, and one technique-gap box selected on mock day |
| P5-W2 | Jan 26–Feb 1 | Targeted repetitions from Mock 1 review | 5–7 boxes on weak spots | Choose 5–7 boxes directly from the techniques that caused delays or dead ends in Mock 1 |
| P5-W3 | Feb 2–8 | Mock 2: full exam format for 23 hours 45 minutes | 0 extra boxes | Three unseen standalones + one fresh AD chain, used for the timed run and report |
| P5-W4 | Feb 9–15 | Targeted repetitions from Mock 2 review | 5–7 boxes on weak spots | Choose 5–7 boxes directly from the techniques that caused delays or dead ends in Mock 2 |
| P5-W5 | Feb 16–22 | Mock 3: confidence run with smooth timed execution | 0 extra boxes | Three unseen standalones + one fresh AD chain for the final timed run |

## Tracking Tables

> Use these tables to check off completion and record technique notes. The weekly schedule above is the single view for choosing current targets.

## OSCP-Style Machines

> **⏳ Pre-RUNBOOK boxes, tracked but not yet redone (added 2026-08-06):** completed before the RUNBOOK workflow existed. Old write-ups exist. Will redo properly when they come up in the rotation.
>
> | Completed | Machine Name | Platform | Notes / Key Technique |
> |---|---|---|---|
> | [ ] | Blue | HTB, Windows | Pre-RUNBOOK. Redo: MS17-010 EternalBlue. |
> | [ ] | Beep | HTB, Linux | Pre-RUNBOOK. Redo: Elastix LFI → RCE. |

### Hack The Box (HTB)

#### Linux
| Phase | Completed | Machine Name | Notes / Key Technique |
|-----------|-----------|-----------|-----------|
| P1 | [x]       | Sea          | WonderCMS CVE-2023-41425 stored XSS → admin bot → malicious theme → www-data → bcrypt hash crack → amay SSH → localhost:8080 log_file cmd injection → root |
| P1 | [x]       | Nibbles      | HTB, Linux. Nibbleblog 4.0.3 → controlled default-credential login → CVE-2015-6967 My Image plugin upload → nibbler shell → create missing sudo-allowed monitor.sh → SUID Bash root. See [[OSCP/BOXES/WRITE UPS/Linux/Nibbles|Nibbles]] |
| P1 | [ ] | Solidstate | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Solidstate. |
| P1 | [ ] | Poison | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Poison. |
| P1 | [ ] | Editor | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Editor. |
| P1 | [ ] | Sunday | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Sunday. |
| P1 | [ ] | Keeper | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Keeper. |
| P1 | [ ] | Pilgrimage | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Pilgrimage. |
| P1 | [ ] | Cozyhosting | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Cozyhosting. |
| P1 | [ ] | Codify | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Codify. |
| P1 | [ ] | Tartarsauce | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Tartarsauce. |
| P1 | [ ] | Jarvis | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Jarvis. |
| P1 | [ ] | Connected | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Connected. |
| P1 | [ ] | Mentor | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Mentor. |
| P1 | [ ] | Devvortex | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Devvortex. |
| P1 | [ ] | Irked | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Irked. |
| P1 | [ ] | Popcorn | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Popcorn. |
| P1 | [ ] | Bashed | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Bashed. |
| P1 | [ ] | Broker | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Broker. |
| P1 | [ ] | Silentium | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Silentium. |
| P1 | [ ] | Networked | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Networked. |
| P1 | [ ] | UpDown | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for UpDown. |
| P1 | [ ] | Swagshop | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Swagshop. |
| P1 | [ ] | Nineveh | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Nineveh. |
| P1 | [ ] | Pandora | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Pandora. |
| P1 | [x] | OpenAdmin | OpenNetAdmin 18.1.1 command injection (Exploit-DB 47691) → www-data → ONA database credential reuse for Jimmy SSH → writable internal Apache app running as Joanna → encrypted SSH key + John → sudo nano GTFOBins shell escape → root. See [[OSCP/BOXES/WRITE UPS/Linux/OpenAdmin|OpenAdmin]] |
| P1 | [ ] | Precious | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Precious. |
| P1 | [ ] | Monitored | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Monitored. |
| P1 | [ ] | BoardLight | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for BoardLight. |
| P1 | [ ] | Magic | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Magic. |
| P1 | [ ] | Help | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Help. |
| P1 | [ ] | Editorial | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Editorial. |
| P1 | [ ] | Builder | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Builder. |
| P1 | [ ] | Linkvortex | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Linkvortex. |
| P1 | [ ] | UnderPass | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for UnderPass. |
| P1 | [ ] | Dog | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Dog. |
| P1 | [ ] | Cctv | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Cctv. |

#### Web Techniques
| Phase | Completed | Machine Name | Notes / Key Technique |
|-----------|-----------|-----------|-----------|
| P1 | [ ] | Nunchucks | Node.js SSTI via template injection → RCE → sudo SUID environment bypass. Key skill: clean server-side template-injection introduction. |
| P1 | [ ] | Bolt | SSTI in Bolt CMS template field → RCE → credential reuse → privilege escalation. Key skill: CMS template injection and credential reuse. |
| P2 | [ ] | Forge | SSRF to internal admin panel → bypass → LFI through SSRF → SSH key → sudo Python deserialization. Key skill: chain server-side request forgery into internal file access. |
| P2 | [ ] | Moderators | SSRF through image URL fetching → internal-service pivot → RCE chain. Key skill: identify SSRF through server-side URL fetches. |
| P2 | [ ] | Backend | API enumeration → JWT algorithm confusion (RS256 to HS256) → forged admin token → RCE → privilege escalation. Key skill: validate token-signing assumptions. |
| P1 | [ ] | Goodgames | GraphQL injection → Flask/Jinja2 SSTI → Docker container escape. Key skill: combine API injection, template injection, and container escalation. |
| P2 | [ ] | Pollution | XXE → SSRF → PHP deserialization → RCE. Key skill: follow a multi-stage web exploit chain. |
| P2 | [ ] | Sandworm | PGP SSTI through a signed-message parser → Firejail sandbox foothold → sandbox escape → Linux root. Key skill: parser abuse followed by sandbox escape. |

#### Windows
| Phase | Completed | Machine Name | Notes / Key Technique |
|-----------|-----------|-----------|-----------|
| P2 | [x] ♻️   | Markup       | XXE injection → file read → SSH key → foothold → SYSTEM via writable scheduled task script. **REDO: methodology steps skipped, transcript used as shortcut. See [[MarkUp]]** |
| P2 | [x]       | Jerry        | Tomcat 7.0.88 default creds (tomcat:s3cret) → Manager text API WAR deploy → JSP webshell → nt authority\system (no privesc -- Tomcat runs as SYSTEM). Both flags in one file: C:\Users\Administrator\Desktop\flags\2 for the price of 1.txt. See [[Jerry]] |
| P2 | [x]       | Netmon       | Anonymous FTP → full C: drive exposed → PRTG config .old.bak → stale cred PrTg@dmin2018 → year-increment PrTg@dmin2019 → CVE-2018-9276 (EDB 46527) notification injection → pentest:P3nT3st! local admin → psexec SYSTEM → both flags. Clean-down: tester.txt, pentest account, 6 PRTG notification objects (&approve=1 required). See [[Netmon]] |
| P2 | [x]       | Servmon      | Anonymous FTP → Nadine's Confidential.txt → Nathan's Passwords.txt via NVMS-1000 CVE-2019-20085 directory traversal (--path-as-is) → SSH spray (nadine) → NSClient++ nsclient.ini cleartext password → SSH tunnel to localhost:8443 → API script upload (PUT) + execute (/queries/check/commands/execute) → nt authority\system. See [[Servmon]] |
| P2 | [x]       | Chatterbox   | AChat 0.150 beta7 UDP buffer overflow (EDB-36025) → msfvenom x86/unicode_mixed BufferRegister=EAX → alfred shell → icacls inherited Full Control on Administrator Desktop (OI)(CI)(F) → /grant alfred:F on root.txt → both flags. ACL reverted on clean-down. See [[Chatterbox]] |
| P2 | [ ] | Grandpa | IIS 6.0 WebDAV ScStoragePathFromUrl → MS14-058 kernel token privilege escalation. Key skill: manual WebDAV and legacy Windows escalation. |
| P2 | [ ] | Granny | IIS 6.0 WebDAV PUT → local privilege escalation. Key skill: WebDAV upload validation and Windows enumeration. |
| P2 | [ ] | Optimum | HttpFileServer 2.3 RCE (CVE-2014-6287) → MS16-032 or MS16-098 kernel escalation. Key skill: version matching and local exploit selection. |
| P2 | [ ] | Devel | Anonymous IIS FTP upload → webshell → SeImpersonate or kernel privilege escalation. Key skill: chaining FTP and web enumeration. |
| P2 | [ ] | Arctic | ColdFusion 8 file-upload RCE → MS10-059 Chimichurri escalation. Key skill: old web-platform exploitation and payload transfer. |
| P2 | [ ] | Bastard | Drupalgeddon CVE-2018-7600 → MS15-051 kernel escalation. Key skill: web exploit validation and local privilege escalation. |
| P2 | [ ] | Silo | Oracle TNS listener enumeration → webshell → WMIC pass-the-hash SYSTEM. Key skill: database service enumeration and credential reuse. |
| P2 | [ ] | Fuse | Printer spool-page username disclosure → SeLoadDriverPrivilege → Capcom.sys → SYSTEM. Key skill: token privilege triage and driver abuse. |
| P2 | [ ] | Jeeves | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Jeeves. |
| P2 | [ ] | Bounty | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Bounty. |
| P2 | [ ] | Artic | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Artic. |
| P2 | [ ] | Remote | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Remote. |
| P2 | [ ] | Love | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Love. |
| P2 | [ ] | Secnotes | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Secnotes. |
| P2 | [ ] | Sniper | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Sniper. |
| P2 | [ ] | Querier | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Querier. |
| P2 | [ ] | Giddy | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Giddy. |
| P2 | [ ] | Mailing | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Mailing. |
| P2 | [ ] | Access (HTB) | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Access. |

#### Buffer Overflow / Exploit Dev
| Phase | Completed | Machine Name | Notes / Key Technique |
|-----------|-----------|-----------|-----------|
| P1 | [ ] | Buff | CloudMe 1.11.2 Windows BOF (EDB-48389) → msfvenom x86 shellcode → SYSTEM. Key skill: classic stack BOF on a live service. |
| P1 | [ ] | Brainpan (HTB) | Brainpan 1 pure Windows stack BOF over TCP: crash → offset → bad chars → EIP → JMP ESP → shellcode. Key skill: complete exam-style exploit development sequence. |
| P1 | [ ] | SLMail | SLMail 5.5 POP3 PASS stack BOF (EDB-638): long string → offset → bad chars → JMP ESP → shellcode. Key skill: repeat the classic exam-style workflow on a different service. |
| P1 | [ ] | VulnServer | Deliberately vulnerable server with 11 BOF types including TRUN, GMON, and GDOG. Key skill: drill individual exploit-development stages. |

#### Active Directory & Networks
| Phase | Completed | Machine Name                   | Notes / Key Technique                                                                                                                                                                                           |
|-----------|-----------|-----------|-----------|
| P3 | [ ] | Active | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Active. |
| P3 | [x]       | Forest                         | Anonymous RPC/LDAP enum → AS-REP roasting (svc-alfresco) → WinRM foothold → Account Operators → Exchange Windows Permissions → WriteDACL → DCSync (netexec --ntds) → PTH. See [[Forest]]                        |
| P3 | [x]       | Sauna                          | Web OSINT About page → username derivation (first-initial-surname) → AS-REP roasting (fsmith) → WinRM foothold → Winlogon autologon registry → svc_loanmgr cleartext creds → direct DCSync → PTH. See [[Sauna]] |
| P3 | [x]       | Return                         | LDAP passback via unauthenticated printer admin panel (settings.php Server Address field, nc -lvnp 389) → svc-printer cleartext creds → WinRM foothold → Server Operators → sc.exe VSS binary-path swap (error 1053 expected) → net localgroup administrators add → reconnect → Administrator Desktop. See [[Return]] |
| P3 | [x] ♻️   | Flight                         | LFI (forward slash WAF bypass) → Responder (svc_apache NTLMv2) → crack → spray (s.moon) → NTLM theft desktop.ini (c.bum NTLMv2) → crack → Web share PHP shell → RunasCs → ASPX shell (IIS AppPool) → GodPotato SYSTEM → vssadmin shadow copy → NTDS.dit → secretsdump LOCAL → PTH. **REDO: NTDS extraction not completed genuinely during manual run (stale Aug 30 files). Redo: shadow copy SMB exfil → fresh secretsdump.** See [[Flight]] |
| P3 | [x]       | Blackfield                     | SMB null session → profiles$ (314 usernames) → AS-REP roasting (support, pre-auth disabled) → crack → ForceChangePassword ACE on audit2020 (dacledit.py) → forced reset → forensic share LSASS dump → pypykatz (svc_backup NT hash) → PTH WinRM → Backup Operators → SeBackupPrivilege → DiskShadow VSS (CRLF required) → robocopy /b ntds.dit + SYSTEM hive → secretsdump LOCAL (pipx venv) → Administrator NT hash → PTH evil-winrm → root. See [[Blackfield]] |
| P3 | [ ] | Cicada | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Cicada. |
| P3 | [ ] | TheFrizz (harder) | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for TheFrizz (harder). |
| P3 | [ ] | Administrator (Assumed Breach) | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Administrator (Assumed Breach). |
| P3 | [ ] | Monteverde (Priv Esc) | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Monteverde (Priv Esc). |
| P3 | [ ] | Escape (Priv Esc) | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Escape (Priv Esc). |
| P3 | [ ] | EscapeTwo (Assumed Breach) | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for EscapeTwo (Assumed Breach). |
| P3 | [ ] | Certified (Assumed Breach) | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Certified (Assumed Breach). |
| P3 | [ ] | Puppy (harder) | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Puppy (harder). |
| P3 | [ ] | Timelapse (harder) | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Timelapse (harder). |
| P3 | [ ] | Signed (Assumed Breach) | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Signed (Assumed Breach). |

#### HTB ProLabs
| Phase | Completed | Machine Name | Notes / Key Technique |
|-----------|-----------|-----------|-----------|
| P4 | [ ] | Dante | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Dante. |
| P4 | [ ] | Zephyr (harder) | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Zephyr (harder). |



---

### Proving Grounds (PG) Practice

#### Linux
| Phase | Completed | Machine Name  | Notes / Key Technique |
|-----------|-----------|-----------|-----------|
| P1 | [x]       | ClamAV        | PG, Linux. SNMP process disclosure (clamav-milter --black-hole-mode) → EDB 4761 Sendmail RCE → inetd bind shell. Direct root. See [[1. clamAV\|clamAV]] |
| P1 | [x]       | Pelican       | PG, Linux. Exhibitor UI java.env script unauthenticated command injection → charles. sudo gcore → password-store memory dump → root:ClogKingpinInning731. See [[OSCP/BOXES/WRITE UPS/Linux/2. Pelican\|Pelican]] |
| P1 | [x]       | Payday        | PG, Linux. CS-Cart 1.3.x LFI (classes_dir null-byte) → /etc/passwd → patrick. medusa SSH brute → patrick:patrick. sudo (ALL) ALL → sudo su → root. See [[OSCP/BOXES/WRITE UPS/Linux/3. Payday\|Payday]] |
| P1 | [x]       | Snookums      | PG, Linux. Simple PHP Photo Gallery v0.8 — ffuf parameter fuzz found `image.php?img=` passing to include(). LFI via php://filter reads db.php (MySQL root creds). data:// wrapper RCE (SELinux httpd_t + firewall block reverse/bind shells). mysql CLI via shell_exec dumps users table. Double base64 decode → michael's SSH creds. /etc/passwd owned by michael → append UID-0 user → root. See [[OSCP/BOXES/WRITE UPS/Linux/4. Snookums\|Snookums]] |
| P1 | [x]       | Bratarina     | PG, Linux. OpenSMTPD 6.6.2 CVE-2020-7247 (EDB 47984) MAIL FROM injection → direct root. Key lesson: delivery PATH lacks `python3`, use `python`. Port 80 bypasses egress. See [[OSCP/BOXES/WRITE UPS/Linux/5. Bratarina\|Bratarina]] |
| P1 | [x] ♻️   | Pebbles       | PG, Linux. ZoneMinder 1.29.0 SQLi (EDB-41239) — `limit` param stacked queries → OUTFILE webshell → www-data. MySQL root creds in `/etc/zm/zm.conf`. UDF sys_exec SUID bash → root. **REDO: Codex left /tmp/rootbash on box — UDF privesc not done manually.** See [[OSCP/BOXES/WRITE UPS/Linux/6. Pebbles\|Pebbles]] |
| P1 | [x]       | Nibbles       | PG, Linux. PostgreSQL 11.3 on port 5437, default creds (postgres:postgres). COPY TO PROGRAM RCE → postgres shell. SUID /usr/bin/find → euid=0. See [[OSCP/BOXES/WRITE UPS/Linux/7. Nibbles\|Nibbles]] |
| P1 | [x]       | Zenphoto      | PG, Linux. Zenphoto 1.4.1.4 at /test/ (dir bust). Version in HTML comment. EDB-18083 unauthenticated RCE → www-data. Kernel 2.6.32-21 (Ubuntu 10.04) → CVE-2010-3904 EDB-15285 → root. See [[OSCP/BOXES/WRITE UPS/Linux/8. Zenphoto\|Zenphoto]] |
| P1 | [x]       | Nukem         | PG, Linux (Arch). WordPress Simple File List 4.2.2 — CVE-2020-36847 unauthenticated file upload + rename → http shell. wp-config.php → commander:CommanderKeenVorticons1990. su - commander. SUID dosbox → write to /etc/sudoers → sudo bash → root. See [[OSCP/BOXES/WRITE UPS/Linux/9. Nukem\|Nukem]] |
| P1 | [ ] | Hetemit | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Hetemit. |
| P1 | [x]       | Cockpit       | PG, Linux (Ubuntu). SQLi auth bypass (`' \|\| 1=1#` — WAF `OR` bypass) → base64 creds → Cockpit 9090 OS login → web terminal as james. sudo tar wildcard injection (`--checkpoint-action=exec=bash privesc.sh`) → SUID bash → root. See [[OSCP/BOXES/WRITE UPS/Linux/10. Cockpit\|Cockpit]] |
| P1 | [ ] | Sumo | Shellshock (CVE-2014-6271) via Apache mod_cgi → Dirty COW or OverlayFS. Key skill: legacy CGI command injection and kernel LPE selection. |
| P1 | [ ] | Loly | WordPress → plugin file upload → www-data → sudo LD_PRELOAD. Key skill: web foothold to environment-variable privilege escalation. |
| P1 | [ ] | Blogger | WordPress blog → vulnerable plugin → RCE → sudo ALL privilege escalation. Key skill: CMS enumeration and sudo abuse. |
| P1 | [ ] | Election | ElectiD web application → [verify] find or writable service. Key skill: service enumeration and local privilege escalation. |
| P1 | [ ] | DriftingBlues6 | WordPress → file upload → www-data → OverlayFS kernel LPE. Key skill: upload validation and kernel exploit matching. |
| P1 | [ ] | Tre | Admin webshell → sudo check_mk_agent. Key skill: web foothold and unusual sudo command auditing. |
| P1 | [ ] | Breakout | Web admin panel → sudo tar privilege escalation. Key skill: web enumeration and wildcard checkpoint injection. |
| P1 | [ ] | Photographer | Koken CMS file upload → www-data → SUID php7.2. Key skill: CMS upload abuse and SUID interpreter escalation. |
| P1 | [ ] | Sunsetmidnight | WordPress → reverse shell → sudo service privilege escalation. Key skill: CMS foothold and service abuse. |
| P1 | [ ] | Pwned | Anonymous FTP → web credentials → SSH → Docker privilege escalation. Key skill: cross-service credential reuse and container escape. |
| P2 | [ ] | Assertion | Apache mod_setenvif LFI → RCE → SUID cputils. Key skill: log/LFI exploitation and SUID triage. |
| P2 | [ ] | Thor | SQLi → webshell → sudo privilege escalation. Key skill: SQL injection to shell and local escalation. |
| P2 | [ ] | Exfiltrated | Subrion CMS RCE → cron job injection → root. Key skill: CMS exploitation and scheduled-job abuse. |
| P2 | [ ] | Fired | OpenFire RCE → SUID privilege escalation. Key skill: Java application exploitation and SUID review. |
| P2 | [ ] | Sybaris | MySQL service enumeration → [verify] foothold and privilege path. Key skill: database attack-surface triage. |
| P2 | [ ] | Hunit | API enumeration → sudo privilege escalation. Key skill: API discovery and local sudo auditing. |
| P2 | [ ] | Readys | WordPress data disclosure → screen 4.5.0 privilege escalation. Key skill: CMS information gathering and local exploit validation. |
| P2 | [ ] | Roquefort | Gitea → [verify] privilege path. Key skill: source-control service enumeration and credential discovery. |
| P2 | [ ] | Zab | Authenticated Zabbix RCE → sudo privilege escalation. Key skill: authenticated monitoring-platform exploitation. |
| P1 | [ ] | Clue | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Clue. |
| P1 | [ ] | Extplorer | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Extplorer. |
| P1 | [ ] | Postfish | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Postfish. |
| P1 | [ ] | Hawat | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Hawat. |
| P1 | [ ] | Walla | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Walla. |
| P1 | [ ] | PC | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for PC. |
| P1 | [ ] | Apex | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Apex. |
| P1 | [ ] | Sorcerer | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Sorcerer. |
| P1 | [ ] | Peppo | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Peppo. |
| P1 | [ ] | Astronaut | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Astronaut. |
| P1 | [ ] | Bullybox | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Bullybox. |
| P1 | [ ] | Marketing | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Marketing. |
| P1 | [ ] | Fanatastic | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Fanatastic. |
| P1 | [ ] | QuackerJack | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for QuackerJack. |
| P1 | [ ] | Wombo | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Wombo. |
| P1 | [ ] | Flu | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Flu. |
| P1 | [ ] | Levram | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Levram. |
| P1 | [ ] | Mzeeav | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Mzeeav. |
| P1 | [ ] | LaVita | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for LaVita. |
| P1 | [ ] | Xposedapi | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Xposedapi. |
| P1 | [ ] | Zipper | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Zipper. |
| P1 | [ ] | Workaholic | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Workaholic. |
| P1 | [ ] | Scrutiny | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Scrutiny. |
| P1 | [ ] | SPX | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for SPX. |
| P1 | [ ] | Vmdak | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Vmdak. |
| P1 | [ ] | Mantis | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Mantis. |
| P1 | [ ] | BitForge | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for BitForge. |
| P1 | [ ] | WallpaperHub | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for WallpaperHub. |
| P1 | [ ] | SpiderSociety | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for SpiderSociety. |

#### Buffer Overflow / Binary Exploitation
| Phase | Completed | Machine Name | Notes / Key Technique |
|-----------|-----------|-----------|-----------|
| P1 | [ ] | Ariti | Standalone Linux BOF → root directly, no privesc: crash → offset → bad chars → EIP/RIP → shellcode → root. Key skill: pure stack-overflow fundamentals. |
| P1 | [ ] | Dawn2 | Web enumeration → binary exploitation and stack BOF → foothold → Linux privilege escalation. Key skill: beginner BOF chain. |
| P1 | [ ] | Dawn3 | FTP enumeration → binary exploitation and stack BOF → foothold → Linux privilege escalation. Key skill: repeat the Dawn2 workflow with FTP as the initial vector. |
| P1 | [ ] | Covfefe | Web enumeration → password cracking → source-code analysis → BOF/binary exploitation → privilege escalation. Key skill: connect code review to exploit development. |
| P1 | [ ] | Educated | Web enumeration → SQL injection → BOF/binary exploitation → privilege escalation. Key skill: combine SQL-based access with binary exploitation. |
| P1 | [ ] | Malbec | Remote BOF in a custom Windows-style executable → initial access → Linux SUID dynamic-library hijacking → root. Key skill: remote memory corruption followed by local library hijacking. |
| P2 | [ ] | CVE-2024-56331 | Sudo misconfiguration → heap-based BOF → privilege escalation → root. Key skill: validate a modern local exploit against its required sudo conditions. |
| P2 | [ ] | RPC1 | RMI registry exposure → Remote Method Guesser enumeration → YsoSerial deserialization gadget chain → foothold → SUID BSS-segment overflow. Key skill: Java deserialization and binary exploitation. |
| P2 | [ ] | Precision | RISC-V format-string information leak → ASLR bypass → stack BOF → hidden `system("/bin/sh")` → root. Key skill: combine format strings, address disclosure, and BOF control. |
| P2 | [ ] | Wasmo | WebAssembly local-IP restriction bypass → data-leak binary configuration-file overflow → root. Key skill: application logic bypass and binary parsing. |


#### Windows
| Phase | Completed | Machine Name | Notes / Key Technique |
|-----------|-----------|-----------|-----------|
| P2 | [ ] | Kevin | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Kevin. |
| P2 | [ ] | Internal | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Internal. |
| P2 | [ ] | Jacko | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Jacko. |
| P2 | [ ] | Craft | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Craft. |
| P2 | [ ] | Squid | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Squid. |
| P2 | [ ] | Nickel | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Nickel. |
| P2 | [ ] | MedJed | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for MedJed. |
| P2 | [ ] | Billyboss | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Billyboss. |
| P2 | [ ] | Shenzi | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Shenzi. |
| P2 | [ ] | AuthBy | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for AuthBy. |
| P2 | [ ] | Slort | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Slort. |
| P2 | [ ] | Hepet | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Hepet. |
| P2 | [ ] | DVR4 | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for DVR4. |
| P2 | [ ] | Mice | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Mice. |
| P2 | [ ] | Monster | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Monster. |
| P2 | [ ] | Fish | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Fish. |

#### Buffer Overflow / Exploit Dev
| Phase | Completed | Machine Name | Notes / Key Technique |
|-----------|-----------|-----------|-----------|
| P1 | [ ] | Brainpan (PG) | PG version of the pure Windows stack BOF: crash → offset → bad chars → EIP → JMP ESP → shellcode. Key skill: second clean rep in an unfamiliar environment. |
| P2 | [ ] | Algernon | SmarterMail 16.0 RCE (EDB-49216) → SeImpersonatePrivilege → PrintSpoofer → SYSTEM. Key skill: service RCE to impersonation-token escalation. |
| P1 | [ ] | Kyoto | Windows stack BOF: crash analysis, offset, bad chars, EIP control, JMP ESP, and shellcode delivery. Key skill: repeat the full exploit-development workflow. |
| P1 | [ ] | Panic | Custom Windows web-server BOF → initial access shell → writable batch script executed by an elevated scheduled task → SYSTEM. Key skill: chain a service BOF with scheduled-task privilege escalation. |
| P1 | [ ] | midnight | Web and SMB enumeration → foothold → unquoted service path → SYSTEM. Key skill: identify and exploit unsafe Windows service paths. |

#### Additional Windows Practice
| Phase | Completed | Machine Name | Notes / Key Technique |
|-----------|-----------|-----------|-----------|
| P2 | [ ] | Craft2 | XLSM macro delivery → shell → PrintSpoofer SYSTEM. Key skill: document-based payload delivery and token impersonation. |
| P2 | [ ] | Butch | Custom-service stack BOF → direct SYSTEM shell. Key skill: Windows service exploit development and payload delivery. |
| P2 | [ ] | Vector | OpenSSL for Windows + service exploit → SYSTEM. Key skill: version-specific service exploitation. |
| P2 | [ ] | Symbolic | Symbolic-link abuse → service DLL hijack → SYSTEM. Key skill: filesystem redirection and service abuse. |
| P2 | [ ] | Compromised | Compromised service binary replacement → SYSTEM. Key skill: writable service-path privilege escalation. |

#### Active Directory & Networks
| Phase | Completed | Machine Name         | Notes / Key Technique |
|-----------|-----------|-----------|-----------|
| P3 | [ ] | Access (PG AD) | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Access. |
| P3 | [ ] | Nagoya | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Nagoya. |
| P3 | [ ] | Hokkaido | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Hokkaido. |
| P3 | [ ] | Vault | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Vault. |
| P3 | [ ] | SkillForge (Linux) | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for SkillForge (Linux). |
| P3 | [ ] | Hutch (Priv Esc) | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Hutch (Priv Esc). |
| P3 | [ ] | Resourced (Priv Esc) | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Resourced (Priv Esc). |
| P3 | [ ] | Nara | ADCS ESC1 → certificate-based domain compromise. Key skill: certificate-template abuse. |
| P3 | [ ] | Heist | AS-REP roasting → Kerberoasting → DCSync chain. Key skill: chained Active Directory credential attacks. |

#### Container & Docker Escapes
| Phase | Completed | Machine Name | Notes / Key Technique |
|-----------|-----------|-----------|-----------|
| P2 | [ ] | Tabby | LFI → Tomcat credential → WAR deploy → LXD group → container mount → root. Key skill: move from a web foothold into a privileged container boundary. |
| P2 | [ ] | Busqueda | Gitea SSRF → Docker container inspection → service credential reuse → sudo docker → host filesystem. Key skill: container discovery and Docker privilege escalation. |
| P2 | [ ] | Escape | Various foothold paths → Docker socket access → container mount → host filesystem → root. Key skill: recognise Docker socket access as a host-level escalation path. |




---

## Cloud & Container Labs (Bonus — not core OSCP)

> These are not required for the OSCP exam but build transferable skills for real engagements. Do Phase 3–4 boxes first. Treat these as Phase 5–6 enrichment or post-exam targets.

### HTB Cloud / AWS
| Phase | Completed | Machine Name | Notes / Key Technique |
|-----------|-----------|-----------|-----------|
| P5 | [ ] | Bucket | AWS S3 unauthenticated access → SSRF via DynamoDB → EC2 metadata. Key skill: cloud storage, SSRF, and instance-identity enumeration. |
| P5 | [ ] | Gobox | SSRF → AWS EC2 metadata → IAM role credential theft → S3 access → RCE. Key skill: follow cloud identity credentials across services. |
| P5 | [ ] | Epsilon | AWS Lambda JWT abuse → S3 flag → EC2 code execution. Key skill: connect serverless authentication to cloud compute access. |
| P5 | [ ] | Facts | [verify] Cloud-hosted application → IAM or instance-identity abuse. Key skill: separate application and cloud privilege paths. |

### HTB Kubernetes / Container Orchestration
| Phase | Completed | Machine Name | Notes / Key Technique |
|-----------|-----------|-----------|-----------|
| P5 | [ ] | Fetch | Gitea RCE → [verify] Kubernetes token → cluster privilege escalation. Key skill: recognise cluster credentials after application compromise. |
| P5 | [ ] | Registry | Unauthenticated Docker registry → image pull → credential extraction → SSH → Docker. Key skill: inspect container images for secrets and reuse credentials safely. |

### PG Practice Cloud
| Phase | Completed | Machine Name | Notes / Key Technique |
|-----------|-----------|-----------|-----------|
| P5 | [ ] | Pathway | AWS cloud enumeration → privilege-escalation chain. Key skill: map cloud identities, services, and trust boundaries. |

## Red Teaming / Post-OSCP Machines

### Hack The Box (HTB)

#### Linux
| Phase | Completed | Machine Name | Notes / Key Technique |
|-----------|-----------|-----------|-----------|
| P1 | [ ] | ScriptKiddie | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for ScriptKiddie. |
| P1 | [ ] | Blunder | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Blunder. |
| P1 | [ ] | Delivery | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Delivery. |
| P1 | [ ] | Perfection | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Perfection. |
| P1 | [ ] | Alert | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Alert. |
| P1 | [ ] | Mailroom | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Mailroom. |
| P1 | [ ] | Luke | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Luke. |
| P1 | [ ] | Trickster | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Trickster. |
| P1 | [ ] | Cat | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Cat. |
| P1 | [ ] | Backfire | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Backfire. |
| P1 | [ ] | Cypher | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Cypher. |
| P1 | [ ] | Gofer | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Gofer. |

#### Windows
| Phase | Completed | Machine Name | Notes / Key Technique |
|-----------|-----------|-----------|-----------|
| P2 | [ ] | Aero | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Aero. |
| P2 | [ ] | Atom | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Atom. |
| P2 | [ ] | Compiled | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Compiled. |
| P2 | [ ] | Acute | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Acute. |
| P2 | [ ] | Visual | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Visual. |
| P2 | [ ] | Control | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Control. |
| P2 | [ ] | Worker | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Worker. |

#### Active Directory
| Phase | Completed | Machine Name | Notes / Key Technique |
|-----------|-----------|-----------|-----------|
| P3 | [ ] | Intelligence | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Intelligence. |
| P3 | [ ] | Cascade | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Cascade. |
| P3 | [ ] | Monteverde | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Monteverde. |
| P3 | [ ] | Timelapse | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Timelapse. |
| P3 | [ ] | StreamIO | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for StreamIO. |
| P3 | [ ] | Office | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Office. |
| P3 | [ ] | Freelancer | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Freelancer. |
| P3 | [ ] | Blazorized | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Blazorized. |
| P3 | [ ] | Authority | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Authority. |
| P3 | [ ] | Manager | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Manager. |
| P3 | [ ] | Scrambled | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Scrambled. |
| P3 | [ ] | Resolute | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Resolute. |
| P3 | [ ] | Reel | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Reel. |
| P3 | [ ] | Outdated | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Outdated. |
| P3 | [ ] | Vintage (Assumed Breach) | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Vintage (Assumed Breach). |
| P3 | [ ] | Search | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Search. |
| P3 | [ ] | Axlle | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Axlle. |
| P3 | [ ] | Hospital | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Hospital. |
| P3 | [ ] | TheFrizz | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for TheFrizz. |
| P3 | [ ] | Haze | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Haze. |
| P3 | [ ] | Scepter | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Scepter. |
| P3 | [ ] | Puppy (Assumed Breach) | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Puppy (Assumed Breach). |
| P3 | [ ] | Certificate | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Certificate. |
| P3 | [ ] | TombWatcher | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for TombWatcher. |
| P3 | [ ] | RustyKey (Assumed Breach) | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for RustyKey (Assumed Breach). |
| P3 | [ ] | Infiltrator | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Infiltrator. |
| P3 | [ ] | Mirage | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Mirage. |
| P3 | [ ] | Anubis | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Anubis. |
| P3 | [ ] | Nanocorp | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Nanocorp. |
| P3 | [ ] | Overwatch | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Overwatch. |

#### HTB ProLabs
| Phase | Completed | Machine Name | Notes / Key Technique |
|-----------|-----------|-----------|-----------|
| P4 | [ ] | Zephyr | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Zephyr. |



---

### Proving Grounds Practice (Red Team)

#### Linux
| Phase | Completed | Machine Name | Notes / Key Technique |
|-----------|-----------|-----------|-----------|
| P1 | [ ] | Megavolt | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Megavolt. |

#### Windows
| Phase | Completed | Machine Name | Notes / Key Technique |
|-----------|-----------|-----------|-----------|

#### Windows Active Directory
| Phase | Completed | Machine Name | Notes / Key Technique |
|-----------|-----------|-----------|-----------|
| P2 | [ ] | Hutch | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Hutch. |
| P2 | [ ] | Kyoto (Buffer Overflow) | [verify] Foothold technique → [verify] privilege path. Key skill: verify this route on a clean run for Kyoto (Buffer Overflow). |



---

## Progress Tracking Dashboard

### OSCP Curriculum Summary
| Category | Total | Completed | Remaining | Percentage |
|----------|-------|-----------|-----------|------------|
| **HTB Linux** | 44 | 1 | 43 | 2.3% |
| **HTB Windows** | 28 | 5 | 23 | 17.9% |
| **HTB AD/Networks** | 16 | 5 | 11 | 31.3% |
| **PG Practice Linux** | 69 | 10 | 59 | 14.5% |
| **PG Practice Windows** | 26 | 0 | 26 | 0.0% |
| **PG Practice AD** | 9 | 0 | 9 | 0.0% |
| **OSCP Container & Docker** | 3 | 0 | 3 | 0.0% |
| **TOTAL** | **197** | **21** | **176** | **10.7%** |

### By phase
| Phase | Focus | Total boxes | Completed | Remaining |
|-------|-------|-------------|-----------|-----------|
| P1 | Exploit development and Linux depth | 103 | 11 | 92 |
| P2 | Windows depth | 67 | 5 | 62 |
| P3 | Active Directory | 25 | 5 | 20 |
| P4 | Advanced and harder chains | 2 | 0 | 2 |

### Bonus Labs Summary
| Category | Total | Completed | Remaining |
|----------|-------|-----------|-----------|
| **Cloud & Container (Bonus)** | 7 | 0 | 7 |

### Red Teaming Curriculum Summary
| Category | Total | Completed | Remaining | Percentage |
|----------|-------|-----------|-----------|------------|
| **HTB Red Team Linux** | 12 | 0 | 12 | 0.0% |
| **HTB Red Team Windows** | 7 | 0 | 7 | 0.0% |
| **HTB Red Team AD/Networks** | 30 | 0 | 30 | 0.0% |
| **PG Practice Red Team Linux** | 1 | 0 | 1 | 0.0% |
| **PG Practice Red Team Windows** | 0 | 0 | 0 | 0.0% |
| **PG Practice Red Team AD** | 2 | 0 | 2 | 0.0% |
| **TOTAL** | **52** | **0** | **52** | **0.0%** |

## Notes & Methodology Tracker

| Phase | Machine Name | Platform | Date Started | Date Completed | Key Takeaway / Attack Vector |
|-----------|-----------|-----------|-----------|-----------|-----------|
| P1 | [[1. clamAV\|clamAV]] | PG Practice, Linux | 2026-08-19 | 2026-08-19 | SNMP process disclosure → clamav-milter EDB 4761 → inetd bind shell. Direct root. |
| P1 | [[OSCP/BOXES/WRITE UPS/Linux/2. Pelican\|Pelican]] | PG Practice, Linux | 2026-08-25 | 2026-08-25 | Exhibitor UI java.env script unauthenticated command injection → charles. sudo gcore → password-store memory dump → root creds in plaintext. |
| P1 | [[OSCP/BOXES/WRITE UPS/Linux/3. Payday\|Payday]] | PG Practice, Linux | 2026-08-25 | 2026-08-25 | CS-Cart LFI (classes_dir null-byte) → /etc/passwd → patrick. medusa SSH brute (patrick:patrick). sudo (ALL) ALL → sudo su → root. |
| P1 | [[OSCP/BOXES/WRITE UPS/Linux/4. Snookums\|Snookums]] | PG Practice, Linux | 2026-08-25 | 2026-08-25 | ffuf parameter fuzz → image.php?img= include(). LFI php://filter reads db.php (MySQL root). data:// RCE (SELinux blocks network shells). mysql CLI via shell_exec dumps double-base64 creds → michael SSH. /etc/passwd owned by michael → UID-0 append → root. |
| P1 | [[OSCP/BOXES/WRITE UPS/Linux/5. Bratarina\|Bratarina]] | PG Practice, Linux | 2026-08-27 | 2026-08-27 | OpenSMTPD 6.6.2 CVE-2020-7247 (EDB 47984) MAIL FROM injection → direct root. TCP egress filtered (tcpdump confirmed). `python` (Python 2) in payload — delivery PATH lacks python3. Port 80 reverse shell bypasses filter. |
| P1 | [[OSCP/BOXES/WRITE UPS/Linux/6. Pebbles\|Pebbles]] | PG Practice, Linux | 2026-08-27 | 2026-08-27 | ZoneMinder 1.29.0 SQLi (EDB-41239) — `limit` POST param, stacked queries, SLEEP confirmed. Web root leaked from SQL error body. INTO OUTFILE webshell → www-data. MySQL root creds in /etc/zm/zm.conf. UDF sys_exec SUID bash → euid=0. |
| P1 | [[OSCP/BOXES/WRITE UPS/Linux/7. Nibbles\|Nibbles]] | PG Practice, Linux | 2026-08-27 | 2026-08-27 | PostgreSQL 11.3 on port 5437. Default creds postgres:postgres. Superuser confirmed. COPY TO PROGRAM mkfifo+nc (port 80 bypasses egress). SUID /usr/bin/find → euid=0. Both flags grabbed as root. |
| P1 | [[OSCP/BOXES/WRITE UPS/Linux/Nibbles\|Nibbles]] | HTB, Linux | 2026-09-01 | 2026-09-01 | Nibbleblog 4.0.3 → authenticated My Image upload (CVE-2015-6967) → nibbler → missing sudo-allowed monitor.sh created with SUID Bash payload → root. |
| P1 | [[OSCP/BOXES/WRITE UPS/Linux/8. Zenphoto\|Zenphoto]] | PG Practice, Linux | 2026-08-27 | 2026-08-27 | Zenphoto 1.4.1.4 at /test/ (gobuster). Version in HTML comment. EDB-18083 unauthenticated RCE via ajax_create_folder.php → www-data. Ubuntu 10.04 kernel 2.6.32-21 → CVE-2010-3904 EDB-15285 RDS LPE → root. |
| P3 | [[Forest]] | HTB, AD | 2026-08-30 | 2026-08-30 | Anonymous RPC/LDAP → AS-REP roasting (svc-alfresco, pre-auth disabled) → WinRM foothold → Account Operators → Exchange Windows Permissions WriteDACL → bloodyAD DCSync grant → netexec --ntds → PTH evil-winrm. Key: RPC exposed account LDAP missed; secretsdump failed, used netexec --ntds. |
| P3 | [[Sauna]] | HTB, AD | 2026-08-30 | 2026-08-30 | Web About page OSINT → first-initial-surname usernames → AS-REP roasting (fsmith) → WinRM foothold → Winlogon registry cleartext autologon (svc_loanmgr) → direct DCSync rights (no ACL chain needed) → netexec --ntds → PTH evil-winrm. Key: anonymous AD enum was dry; registry display name differs from SAMAccountName. |
| P3 | [[Return]] | HTB, AD | 2026-08-30 | 2026-08-30 | Unauthenticated printer admin panel → LDAP passback (nc -lvnp 389, cleartext Simple Bind) → svc-printer WinRM foothold → Server Operators → sc.exe VSS binPath swap (error 1053 expected, command still runs) → add to local Admins → reconnect → Administrator. Gotchas: only `ip` field POSTed; use nc not Responder; zsh `!!` expands in passwords (single quotes); 1053 is not failure; group membership needs new logon. |
| P3 | [[Flight]] ♻️ | HTB, AD | 2026-08-30 | 2026-08-30 | PHP LFI forward-slash WAF bypass → Responder NTLMv2 (svc_apache) → crack → password spray (s.moon) → NTLM theft via desktop.ini (c.bum NTLMv2) → crack → Web share PHP webshell → RunasCs as c.bum → ASPX shell in inetpub\development (IIS AppPool / SeImpersonatePrivilege) → GodPotato SYSTEM → vssadmin shadow copy (HarddiskVolumeShadowCopy3) → PowerShell Copy-Item NTDS.dit + SYSTEM hive → secretsdump LOCAL → Administrator hash → PTH evil-winrm. REDO NEEDED: NTDS extraction step not completed genuinely (stale files from prior session). Gotchas: WAF blocks `\\` use `//`; GodPotato -cmd must be quoted; cleanup script kills PHP fast; cmd.exe copy fails on \\?\ paths (use PowerShell); impacket-smbserver system version broken (use pipx). |
| P3 | [[Blackfield]] | HTB, AD | 2026-08-31 | 2026-08-31 | SMB null session → profiles$ share (314 usernames) → AS-REP roasting (support, pre-auth disabled) → hashcat crack → ForceChangePassword ACE on audit2020 (dacledit.py, BloodHound down) → rpcclient forced reset → forensic share → LSASS dump (pypykatz) → svc_backup NT hash → PTH WinRM → Backup Operators → SeBackupPrivilege → DiskShadow VSS (CRLF required, unix2dos) → robocopy /b ntds.dit → reg.exe SYSTEM hive → secretsdump LOCAL (pipx venv) → Administrator NT hash → PTH evil-winrm. Gotchas: ntpdate broken on newer Kali (manual date -s fix); netexec LDAP needs --port 389 (LDAPS timeout); DiskShadow needs CRLF (unix2dos); evil-winrm upload/download bare filenames only; impacket wrappers conflict (use pipx venv directly); `#` in passwords needs single quotes in zsh. |
| P2 | [[Netmon]] | HTB, Windows | 2026-08-31 | 2026-08-31 | Anonymous FTP → full C: drive → PRTG config .old.bak → stale cred year-incremented → CVE-2018-9276 (EDB 46527) authenticated notification injection → pentest local admin → psexec SYSTEM. Gotchas: delete tester.txt BEFORE deleting account (lose access); PRTG deleteobject.htm requires &approve=1; exploit creates 3 notification objects per run. |
| P2 | [[Jerry]] | HTB, Windows | 2026-08-31 | 2026-08-31 | Tomcat 7.0.88 on port 8080 (default landing page). Default Manager creds (tomcat:s3cret). WAR deploy via text API → JSP webshell (`cmd.exe /c` array exec). nt authority\system on first command (Tomcat runs as SYSTEM, no privesc needed). Both flags in C:\Users\Administrator\Desktop\flags\2 for the price of 1.txt. Clean undeploy via Manager text API. Gotchas: spaces in filenames need double-quoted paths inside cmd; --data-urlencode required for backslashes in curl; box has no SSH/SMB/RDP, port 8080 only. |
| P2 | [[Servmon]] | HTB, Windows | 2026-08-31 | 2026-08-31 | Anonymous FTP → Nadine's Confidential.txt (Nathan's Passwords.txt on Desktop) → NVMS-1000 CVE-2019-20085 directory traversal (--path-as-is, verified with win.ini first) → Nathan_Passwords.txt (7 passwords) → SSH spray (nadine:L1k3B1gBut7s@W0rk) → low-priv shell (medium integrity, BUILTIN\Users only) → NSClient++ nsclient.ini cleartext password + allowed hosts=127.0.0.1 → SSH tunnel -L 8444:127.0.0.1:8443 → API auth (admin:password, 200) → PUT script to /api/v1/scripts/ext/scripts/check.bat → execute via /api/v1/queries/check/commands/execute → nt authority\system. Gotchas: curl normalises ../ without --path-as-is; -N tunnel still prompts for SSH password; "no output from command" is normal for batch scripts (check result:0); delete proof.txt before removing the script. |

---

## How to use this list

This is a practice curriculum, not a speed-running list. The goal is technique breadth and repetition.

- **Pick by phase first** — the Phase column follows the study plan. Do not jump to Phase 3 boxes while Phase 1 labs are unfinished.
- **Pick by technique gap second** — if a technique has not been practised, find it in the Notes column and do that box next.
- **Never do a box you already know the path to** — if you have read a walkthrough, it does not count as a rep. Unknown targets are the priority.
- **A box is not done until the write-up is done** — flag, write-up, cheatsheet update, Seen In update. That is the standard.
- **REDO boxes count** — Flight, MarkUp, and Pebbles are still useful reps, but mark the redo honestly.

## External Resources

- https://book.hacktricks.wiki/en/generic-methodologies-and-resources/index.html
- https://www.revshells.com/
