# OSCP & Red Teaming Machine Master Lists

> **Formatted, consolidated lists from LainKusanagi's spreadsheet 

---

## Instructions
- ✅ **Check off** machines as you complete them.
- 📝 **Use the Notes column** to track key techniques or vulnerabilities discovered.
- 🔄 **Revisit** machines that gave you trouble.

---

## OSCP-Style Machines

> **⏳ Pre-RUNBOOK boxes, tracked but not yet redone (added 2026-08-06):** completed before the RUNBOOK workflow existed. Old write-ups exist. Will redo properly when they come up in the rotation.
>
> | Completed | Machine Name | Platform | Notes / Key Technique |
> |---|---|---|---|
> | [ ] | Blue | HTB, Windows | Pre-RUNBOOK. Redo: MS17-010 EternalBlue. |
> | [ ] | Beep | HTB, Linux | Pre-RUNBOOK. Redo: Elastix LFI → RCE. |

### Hack The Box (HTB)

#### Linux
| Completed | Machine Name | Notes / Key Technique |
| --------- | ------------ | --------------------- |
| [x]       | Sea          | WonderCMS CVE-2023-41425 stored XSS → admin bot → malicious theme → www-data → bcrypt hash crack → amay SSH → localhost:8080 log_file cmd injection → root |
| [ ]       | Nibbles      |                       |
| [ ]       | Solidstate   |                       |
| [ ]       | Poison       |                       |
| [ ]       | Editor       |                       |
| [ ]       | Sunday       |                       |
| [ ]       | Keeper       |                       |
| [ ]       | Pilgrimage   |                       |
| [ ]       | Cozyhosting  |                       |
| [ ]       | Codify       |                       |
| [ ]       | Tartarsauce  |                       |
| [ ]       | Jarvis       |                       |
| [ ]       | Tabby        |                       |
| [ ]       | Connected    |                       |
| [ ]       | Mentor       |                       |
| [ ]       | Devvortex    |                       |
| [ ]       | Irked        |                       |
| [ ]       | Popcorn      |                       |
| [ ]       | Bashed       |                       |
| [ ]       | Broker       |                       |
| [ ]       | Silentium    |                       |
| [ ]       | Networked    |                       |
| [ ]       | UpDown       |                       |
| [ ]       | Swagshop     |                       |
| [ ]       | Nineveh      |                       |
| [ ]       | Pandora      |                       |
| [ ]       | OpenAdmin    |                       |
| [ ]       | Precious     |                       |
| [ ]       | Busqueda     |                       |
| [ ]       | Monitored    |                       |
| [ ]       | BoardLight   |                       |
| [ ]       | Magic        |                       |
| [ ]       | Help         |                       |
| [ ]       | Editorial    |                       |
| [ ]       | Builder      |                       |
| [ ]       | Linkvortex   |                       |
| [ ]       | UnderPass    |                       |
| [ ]       | Dog          |                       |
| [ ]       | Cctv         |                       |

#### Windows
| Completed | Machine Name | Notes / Key Technique |
| --------- | ------------ | --------------------- |
| [ ]       | Markup       |                       |
| [ ]       | Jerry        |                       |
| [ ]       | Netmon       |                       |
| [ ]       | Servmon      |                       |
| [ ]       | Chatterbox   |                       |
| [ ]       | Jeeves       |                       |
| [ ]       | Sniper       |                       |
| [ ]       | Querier      |                       |
| [ ]       | Giddy        |                       |
| [ ]       | Bounty       |                       |
| [ ]       | Artic        |                       |
| [ ]       | Remote       |                       |
| [ ]       | Buff         |                       |
| [ ]       | Love         |                       |
| [ ]       | Secnotes     |                       |
| [ ]       | Access       |                       |
| [ ]       | Mailing      |                       |
| [ ]       | Heist        |                       |

#### Active Directory & Networks
| Completed | Machine Name | Notes / Key Technique |
|-----------|--------------|----------------------|
| [ ] | Active | |
| [ ] | Forest | |
| [ ] | Sauna | |
| [ ] | Flight | |
| [ ] | Return | |
| [ ] | Blackfield | |
| [ ] | Cicada | |
| [ ] | TheFrizz (harder) | |
| [ ] | Administrator (Assumed Breach) | |
| [ ] | Monteverde (Priv Esc) | |
| [ ] | Escape (Priv Esc) | |
| [ ] | EscapeTwo (Assumed Breach) | |
| [ ] | Certified (Assumed Breach) | |
| [ ] | Puppy (harder) | |
| [ ] | Timelapse (harder) | |
| [ ] | Signed (Assumed Breach) | |

#### HTB ProLabs
| Completed | Machine Name | Notes / Key Technique |
|-----------|--------------|----------------------|
| [ ] | Dante | |
| [ ] | Zephyr (harder) | |

#### HTB AWS (Not in OSCP but good to know)
| Completed | Machine Name | Notes / Key Technique |
|-----------|--------------|----------------------|
| [ ] | Epsilon | |
| [ ] | Gobox | |
| [ ] | Bucket | |
| [ ] | Facts | |

---

### Proving Grounds (PG) Practice

#### Linux
| Completed | Machine Name  | Notes / Key Technique |
| --------- | ------------- | --------------------- |
| [x]       | ClamAV        | PG, Linux. SNMP process disclosure (clamav-milter --black-hole-mode) → EDB 4761 Sendmail RCE → inetd bind shell. Direct root. See [[1. clamAV\|clamAV]] |
| [x]       | Pelican       | PG, Linux. Exhibitor UI java.env script unauthenticated command injection → charles. sudo gcore → password-store memory dump → root:ClogKingpinInning731. See [[OSCP/BOXES/WRITE UPS/Linux/2. Pelican\|Pelican]] |
| [x]       | Payday        | PG, Linux. CS-Cart 1.3.x LFI (classes_dir null-byte) → /etc/passwd → patrick. medusa SSH brute → patrick:patrick. sudo (ALL) ALL → sudo su → root. See [[OSCP/BOXES/WRITE UPS/Linux/3. Payday\|Payday]] |
| [x]       | Snookums      | PG, Linux. Simple PHP Photo Gallery v0.8 — ffuf parameter fuzz found `image.php?img=` passing to include(). LFI via php://filter reads db.php (MySQL root creds). data:// wrapper RCE (SELinux httpd_t + firewall block reverse/bind shells). mysql CLI via shell_exec dumps users table. Double base64 decode → michael's SSH creds. /etc/passwd owned by michael → append UID-0 user → root. See [[OSCP/BOXES/WRITE UPS/Linux/4. Snookums\|Snookums]] |
| [x]       | Bratarina     | PG, Linux. OpenSMTPD 6.6.2 CVE-2020-7247 (EDB 47984) MAIL FROM injection → direct root. Key lesson: delivery PATH lacks `python3`, use `python`. Port 80 bypasses egress. See [[OSCP/BOXES/WRITE UPS/Linux/5. Bratarina\|Bratarina]] |
| [x] ♻️   | Pebbles       | PG, Linux. ZoneMinder 1.29.0 SQLi (EDB-41239) — `limit` param stacked queries → OUTFILE webshell → www-data. MySQL root creds in `/etc/zm/zm.conf`. UDF sys_exec SUID bash → root. **REDO: Codex left /tmp/rootbash on box — UDF privesc not done manually.** See [[OSCP/BOXES/WRITE UPS/Linux/6. Pebbles\|Pebbles]] |
| [x]       | Nibbles       | PG, Linux. PostgreSQL 11.3 on port 5437, default creds (postgres:postgres). COPY TO PROGRAM RCE → postgres shell. SUID /usr/bin/find → euid=0. See [[OSCP/BOXES/WRITE UPS/Linux/7. Nibbles\|Nibbles]] |
| [x]       | Zenphoto      | PG, Linux. Zenphoto 1.4.1.4 at /test/ (dir bust). Version in HTML comment. EDB-18083 unauthenticated RCE → www-data. Kernel 2.6.32-21 (Ubuntu 10.04) → CVE-2010-3904 EDB-15285 → root. See [[OSCP/BOXES/WRITE UPS/Linux/8. Zenphoto\|Zenphoto]] |
| [x]       | Nukem         | PG, Linux (Arch). WordPress Simple File List 4.2.2 — CVE-2020-36847 unauthenticated file upload + rename → http shell. wp-config.php → commander:CommanderKeenVorticons1990. su - commander. SUID dosbox → write to /etc/sudoers → sudo bash → root. See [[OSCP/BOXES/WRITE UPS/Linux/9. Nukem\|Nukem]] |
| [ ]       | Hetemit       |                       |
| [ ]       | ZenPhoto      |                       |
| [ ]       | Nukem         |                       |
| [x]       | Cockpit       | PG, Linux (Ubuntu). SQLi auth bypass (`' \|\| 1=1#` — WAF `OR` bypass) → base64 creds → Cockpit 9090 OS login → web terminal as james. sudo tar wildcard injection (`--checkpoint-action=exec=bash privesc.sh`) → SUID bash → root. See [[OSCP/BOXES/WRITE UPS/Linux/10. Cockpit\|Cockpit]] |
| [ ]       | Clue          |                       |
| [ ]       | Extplorer     |                       |
| [ ]       | Postfish      |                       |
| [ ]       | Hawat         |                       |
| [ ]       | Walla         |                       |
| [ ]       | PC            |                       |
| [ ]       | Apex          |                       |
| [ ]       | Sorcerer      |                       |
| [ ]       | Sybaris       |                       |
| [ ]       | Peppo         |                       |
| [ ]       | Hunit         |                       |
| [ ]       | Readys        |                       |
| [ ]       | Astronaut     |                       |
| [ ]       | Bullybox      |                       |
| [ ]       | Marketing     |                       |
| [ ]       | Exfiltrated   |                       |
| [ ]       | Fanatastic    |                       |
| [ ]       | QuackerJack   |                       |
| [ ]       | Wombo         |                       |
| [ ]       | Flu           |                       |
| [ ]       | Roquefort     |                       |
| [ ]       | Levram        |                       |
| [ ]       | Mzeeav        |                       |
| [ ]       | LaVita        |                       |
| [ ]       | Xposedapi     |                       |
| [ ]       | Zipper        |                       |
| [ ]       | Workaholic    |                       |
| [ ]       | Fired         |                       |
| [ ]       | Scrutiny      |                       |
| [ ]       | SPX           |                       |
| [ ]       | Vmdak         |                       |
| [ ]       | Mantis        |                       |
| [ ]       | BitForge      |                       |
| [ ]       | WallpaperHub  |                       |
| [ ]       | Zab           |                       |
| [ ]       | SpiderSociety |                       |

#### Windows
| Completed | Machine Name | Notes / Key Technique |
|-----------|--------------|----------------------|
| [ ] | Kevin | |
| [ ] | Internal | |
| [ ] | Algernon | |
| [ ] | Jacko | |
| [ ] | Craft | |
| [ ] | Squid | |
| [ ] | Nickel | |
| [ ] | MedJed | |
| [ ] | Billyboss | |
| [ ] | Shenzi | |
| [ ] | AuthBy | |
| [ ] | Slort | |
| [ ] | Hepet | |
| [ ] | DVR4 | |
| [ ] | Mice | |
| [ ] | Monster | |
| [ ] | Fish | |

#### Active Directory & Networks
| Completed | Machine Name | Notes / Key Technique |
|-----------|--------------|----------------------|
| [ ] | Access | |
| [ ] | Nagoya | |
| [ ] | Hokkaido | |
| [ ] | Vault | |
| [ ] | SkillForge (Linux) | |
| [ ] | Hutch (Priv Esc) | |
| [ ] | Resourced (Priv Esc) | |

#### PG AWS (Not in OSCP)
| Completed | Machine Name | Notes / Key Technique |
|-----------|--------------|----------------------|
| [ ] | Pathway | |

---

### Proving Grounds (PG) Play (Free/Community)

| Completed | Machine Name | OS | Notes / Key Technique |
|-----------|--------------|-----|----------------------|
| [ ] | Amaterasu | Linux | |
| [ ] | Loly | Linux | |
| [ ] | Potato | Linux | |
| [ ] | Stapler | Linux | |
| [ ] | BBScute | Linux | |
| [ ] | Gaara | Linux | |
| [ ] | Blogger | Linux | |
| [ ] | FunboxEasyEnum | Linux | |
| [ ] | GlasgowSmile | Linux | |
| [ ] | Sams | Windows | |

---

### HackSmarter Platform

#### Linux
| Completed | Machine Name | Notes / Key Technique |
|-----------|--------------|----------------------|
| [ ] | BankSmarter | |
| [ ] | Ascension | |
| [ ] | Talisman | |
| [ ] | Verbose (harder) | |
| [ ] | Exception | |
| [ ] | Samurai | |

#### Windows
| Completed | Machine Name | Notes / Key Technique |
|-----------|--------------|----------------------|
| [ ] | Slayer | |

#### Active Directory & Networks
| Completed | Machine Name | Notes / Key Technique |
|-----------|--------------|----------------------|
| [ ] | ShareThePain | |
| [ ] | Sysco | |
| [ ] | StellarComms | |
| [ ] | MartiniAD | |
| [ ] | Building Magic (Assumed Breach) | |
| [ ] | PivotSmarter (Assumed Breach) | |
| [ ] | Odyssey (harder range) | |
| [ ] | BitStream (harder range) | |
| [ ] | ShadowGate (Priv Esc) | |
| [ ] | Welcome (Assumed Breach) | |
| [ ] | Arasaka (Assumed Breach) | |
| [ ] | Anomaly (harder range) | |
| [ ] | Lumon Industries (Assumed Breach) | |
| [ ] | 404 bank (harder) | |
| [ ] | NovaCart (harder) | |

#### HackSmarter AWS (Not in OSCP)
| Completed | Machine Name | Notes / Key Technique |
|-----------|--------------|----------------------|
| [ ] | Sns_secrets | |
| [ ] | Static | |

---

### Virtual Hacking Labs (VHL) - Not Fully Updated

#### Linux
| Completed | Machine Name | Notes / Key Technique |
|-----------|--------------|----------------------|
| [ ] | Techblog | |
| [ ] | Backupadmin V2 | |
| [ ] | Web01-Dev V2 | |
| [ ] | Web01-Prd V2 | |
| [ ] | Forum | |
| [ ] | Quick | |
| [ ] | Tiki | |
| [ ] | Helpdesk V2 | |
| [ ] | VPS1723 V2 | |
| [ ] | CMS02 V2 | |
| [ ] | Records | |
| [ ] | Trails | |
| [ ] | Dolphin V2 | |
| [ ] | Crash | |
| [ ] | Natural | |
| [ ] | Mantis | |
| [ ] | Fed V2 | |
| [ ] | CMS01 | |
| [ ] | Tracking | |
| [ ] | JS01 | |
| [ ] | PBX | |
| [ ] | Code V2 | |
| [ ] | Teamspeak | |
| [ ] | CMS101 | |
| [ ] | FW01 | |
| [ ] | Core | |
| [ ] | Websrv01 | |
| [ ] | Mon02 | |
| [ ] | Graphs01 | |
| [ ] | PM V2 | |
| [ ] | Tracker | |

#### Windows
| Completed | Machine Name | Notes / Key Technique |
|-----------|--------------|----------------------|
| [ ] | Steven | |
| [ ] | Aaron | |
| [ ] | Anthony | |
| [ ] | Jennifer | |
| [ ] | WinAS01 | |
| [ ] | AS45 | |
| [ ] | Trace | |
| [ ] | React | |

---

### TryHackMe (Deprecated - Not Updated)

#### Linux
| Completed | Machine Name | Notes / Key Technique |
|-----------|--------------|----------------------|
| [ ] | Mr Robot | |
| [ ] | Thompson | |
| [ ] | Kenobi | |
| [ ] | GameZone | |
| [ ] | Skynet | |
| [ ] | Daily bugle | |
| [ ] | Lazy admin | |
| [ ] | Tomghost | |
| [ ] | Rootme | |
| [ ] | CMesS | |
| [ ] | Ultratech | |
| [ ] | Internal | |
| [ ] | Zeno | |
| [ ] | Boiler CTF | |
| [ ] | Wonderland | |
| [ ] | Year of the Jellyfish | |

#### Windows
| Completed | Machine Name | Notes / Key Technique |
|-----------|--------------|----------------------|
| [ ] | Steel Mountain | |
| [ ] | Year of the Owl | |
| [ ] | Retro | |
| [ ] | Alfred | |
| [ ] | Relevant | |
| [ ] | Blueprint | |
| [ ] | Hackpark | |
| [ ] | Weasel | |
| [ ] | AllSignsPoint2Pwnage | |
| [ ] | Anthem | |

#### Active Directory
| Completed | Machine Name | Notes / Key Technique |
|-----------|--------------|----------------------|
| [ ] | Attacktive Directory | |
| [ ] | Attacking Kerberos | |
| [ ] | Wreath Network | |
| [ ] | Reset | |
| [ ] | Vulnnet: Active | |
| [ ] | Enterprise | |
| [ ] | Ledger | |
| [ ] | Corp (Assumed Breach) | |
| [ ] | Lateral Movement and Pivoting | |
| [ ] | Exploiting Active Directory | |

#### Recommended TryHackMe Rooms
| Completed | Room Name |
|-----------|-----------|
| [ ] | SQL Injection Lab |
| [ ] | Linux Privilege Escalation |
| [ ] | Windows Privilege Escalation |
| [ ] | Git Happens |
| [ ] | NahamStore |
| [ ] | Cyber Security 101 (Path) |
| [ ] | Jr Penetration Tester (Path) |
| [ ] | Offensive Pentesting (Path) |

---

## Red Teaming / Post-OSCP Machines

### Hack The Box (HTB)

#### Linux
| Completed | Machine Name | Notes / Key Technique |
|-----------|--------------|----------------------|
| [ ] | ScriptKiddie | |
| [ ] | Blunder | |
| [ ] | Solidstate | |
| [ ] | Delivery | |
| [ ] | Perfection | |
| [ ] | Alert | |
| [ ] | Mailroom | |
| [ ] | Luke | |
| [ ] | Trickster | |
| [ ] | Cat | |
| [ ] | Backfire | |
| [ ] | Cypher | |
| [ ] | Gofer | |

#### Windows
| Completed | Machine Name | Notes / Key Technique |
|-----------|--------------|----------------------|
| [ ] | Querier | |
| [ ] | Aero | |
| [ ] | Mailing | |
| [ ] | Atom | |
| [ ] | Compiled | |
| [ ] | Acute | |
| [ ] | Sniper | |
| [ ] | Visual | |
| [ ] | Giddy | |
| [ ] | Control | |
| [ ] | Heist | |
| [ ] | Worker | |

#### Active Directory
| Completed | Machine Name | Notes / Key Technique |
|-----------|--------------|----------------------|
| [ ] | Sauna | |
| [ ] | Forest | |
| [ ] | Intelligence | |
| [ ] | Cascade | |
| [ ] | Monteverde | |
| [ ] | Blackfield | |
| [ ] | Fuse | |
| [ ] | Return | |
| [ ] | Timelapse | |
| [ ] | StreamIO | |
| [ ] | Flight | |
| [ ] | Office | |
| [ ] | Freelancer | |
| [ ] | Blazorized | |
| [ ] | Authority | |
| [ ] | Manager | |
| [ ] | Escape | |
| [ ] | Scrambled | |
| [ ] | Resolute | |
| [ ] | Mantis | |
| [ ] | Reel | |
| [ ] | Outdated | |
| [ ] | Certified (Assumed Breach) | |
| [ ] | Administrator (Assumed Breach) | |
| [ ] | Vintage (Assumed Breach) | |
| [ ] | Search | |
| [ ] | Axlle | |
| [ ] | Hospital | |
| [ ] | EscapeTwo (Assumed Breach) | |
| [ ] | TheFrizz | |
| [ ] | Haze | |
| [ ] | Scepter | |
| [ ] | Puppy (Assumed Breach) | |
| [ ] | Certificate | |
| [ ] | TombWatcher | |
| [ ] | RustyKey (Assumed Breach) | |
| [ ] | Infiltrator | |
| [ ] | Mirage | |
| [ ] | Anubis | |
| [ ] | Nanocorp | |
| [ ] | Signed (Assumed Breach) | |
| [ ] | Overwatch | |

#### HTB ProLabs
| Completed | Machine Name | Notes / Key Technique |
|-----------|--------------|----------------------|
| [ ] | Zephyr | |

#### HTB AWS
| Completed | Machine Name | Notes / Key Technique |
|-----------|--------------|----------------------|
| [ ] | Epsilon | |
| [ ] | Gobox | |
| [ ] | Bucket | |
| [ ] | Stacked | |
| [ ] | Sink | |
| [ ] | Facts | |

---

### HackSmarter (Red Team)

#### Linux
| Completed | Machine Name | Notes / Key Technique |
|-----------|--------------|----------------------|
| [ ] | BankSmarter | |
| [ ] | Ascension | |
| [ ] | Talisman | |

#### Windows
| Completed | Machine Name | Notes / Key Technique |
|-----------|--------------|----------------------|
| [ ] | Slayer | |
| [ ] | Evasive | |
| [ ] | Sideload | |

#### Active Directory
| Completed | Machine Name | Notes / Key Technique |
|-----------|--------------|----------------------|
| [ ] | ShareThePain | |
| [ ] | Sysco | |
| [ ] | 404bank | |
| [ ] | StellarComms | |
| [ ] | NovaCart | |
| [ ] | ShadowGate | |
| [ ] | Building Magic (Assumed Breach) | |
| [ ] | PivotSmarter (Assumed Breach) | |
| [ ] | Arasaka (Assumed Breach) | |
| [ ] | Welcome (Assumed Breach) | |
| [ ] | Midgarden2 (Assumed Breach) | |
| [ ] | NorthBridge (Assumed Breach) | |
| [ ] | Lumon Industries (Assumed Breach) | |
| [ ] | Edge (Assumed Breach) | |
| [ ] | Anomaly (Network) | |
| [ ] | Odyssey (Network) | |
| [ ] | BitStream (Network) | |

#### HackSmarter AWS
| Completed | Machine Name | Notes / Key Technique |
|-----------|--------------|----------------------|
| [ ] | Sns_secrets | |
| [ ] | Static | |

---

### Proving Grounds Practice (Red Team)

#### Linux
| Completed | Machine Name | Notes / Key Technique |
|-----------|--------------|----------------------|
| [ ] | Postfish | |
| [ ] | Thor | |
| [ ] | Megavolt | |

#### Windows
| Completed | Machine Name | Notes / Key Technique |
|-----------|--------------|----------------------|
| [ ] | Kevin | |
| [ ] | Butch | |
| [ ] | Craft | |
| [ ] | Craft2 | |
| [ ] | Hepet | |
| [ ] | Vector | |
| [ ] | Symbolic | |
| [ ] | Monster | |
| [ ] | Compromised | |

#### Windows Active Directory
| Completed | Machine Name | Notes / Key Technique |
|-----------|--------------|----------------------|
| [ ] | Access | |
| [ ] | Resourced | |
| [ ] | Nagoya | |
| [ ] | Hokkaido | |
| [ ] | Heist | |
| [ ] | Nara | |
| [ ] | Vault | |
| [ ] | Hutch | |
| [ ] | Kyoto (Buffer Overflow) | |

#### PG AWS
| Completed | Machine Name | Notes / Key Technique |
|-----------|--------------|----------------------|
| [ ] | Pathway | |

---

### VulnLab / HTB (Red Team)

#### Linux
| Completed | Machine Name | Notes / Key Technique |
|-----------|--------------|----------------------|
| [ ] | Forgotten | |
| [ ] | Down | |
| [ ] | Bamboo | |

#### Windows
| Completed | Machine Name | Notes / Key Technique |
|-----------|--------------|----------------------|
| [ ] | Escape | |
| [ ] | Job | |
| [ ] | Job2 | |
| [ ] | Lock | |
| [ ] | Media | |

#### Active Directory & Networks
| Completed | Machine Name | Notes / Key Technique |
|-----------|--------------|----------------------|
| [ ] | Baby | |
| [ ] | Baby2 | |
| [ ] | Breach | |
| [ ] | Phantom | |
| [ ] | Sweep | |
| [ ] | Delegate | |
| [ ] | Sendai | |
| [ ] | Retro | |
| [ ] | Retro2 | |
| [ ] | Bruno | |
| [ ] | Lustrous2 | |
| [ ] | Shibuya | |
| [ ] | Trusted (Chain) | |
| [ ] | Reflection (Chain) | |
| [ ] | Hybrid (Chain) | |
| [ ] | Lustrous (Chain) | |
| [ ] | Heron (Assumed Breach) | |
| [ ] | Tengu (Chain) | |
| [ ] | Puppet (Assumed Breach with C2) | |

#### VulnLab Red Teaming Labs
| Completed | Machine Name | Notes / Key Technique |
|-----------|--------------|----------------------|
| [ ] | Ifrit | |

---

## Progress Tracking Dashboard

### OSCP List Summary
| Category | Total | Completed | Remaining | Percentage |
|----------|-------|-----------|-----------|------------|
| **HTB Linux** | 40 | 0 | 40 | 0% |
| **HTB Windows** | 18 | 0 | 18 | 0% |
| **HTB AD/Networks** | 17 | 0 | 17 | 0% |
| **PG Practice Linux** | 47 | 4 | 43 | 8.5% |
| **PG Practice Windows** | 17 | 0 | 17 | 0% |
| **PG Practice AD** | 6 | 0 | 6 | 0% |
| **PG Play** | 10 | 0 | 10 | 0% |
| **HackSmarter** | 20 | 0 | 20 | 0% |
| **VHL** | 39 | 0 | 39 | 0% |
| **TryHackMe** | 33 | 0 | 33 | 0% |
| **TOTAL** | **247** | **4** | **243** | **1.6%** |

*(Blue and Beep tracked in the pre-RUNBOOK callout above, not counted in totals since they predate this list.)*

### Red Teaming List Summary
| Category | Total | Completed | Remaining | Percentage |
|----------|-------|-----------|-----------|------------|
| **HTB Red Team** | 50+ | 0 | 50+ | 0% |
| **HackSmarter Red Team** | 25+ | 0 | 25+ | 0% |
| **PG Practice Red Team** | 18 | 0 | 18 | 0% |
| **VulnLab Red Team** | 28 | 0 | 28 | 0% |
| **TOTAL** | **120+** | **0** | **120+** | **0%** |

---

## Notes & Methodology Tracker

| Machine Name | Platform | Date Started | Date Completed | Key Takeaway / Attack Vector |
|--------------|----------|--------------|----------------|------------------------------|
| [[1. clamAV\|clamAV]] | PG Practice, Linux | 2026-08-19 | 2026-08-19 | SNMP process disclosure → clamav-milter EDB 4761 → inetd bind shell. Direct root. |
| [[OSCP/BOXES/WRITE UPS/Linux/2. Pelican\|Pelican]] | PG Practice, Linux | 2026-08-25 | 2026-08-25 | Exhibitor UI java.env script unauthenticated command injection → charles. sudo gcore → password-store memory dump → root creds in plaintext. |
| [[OSCP/BOXES/WRITE UPS/Linux/3. Payday\|Payday]] | PG Practice, Linux | 2026-08-25 | 2026-08-25 | CS-Cart LFI (classes_dir null-byte) → /etc/passwd → patrick. medusa SSH brute (patrick:patrick). sudo (ALL) ALL → sudo su → root. |
| [[OSCP/BOXES/WRITE UPS/Linux/4. Snookums\|Snookums]] | PG Practice, Linux | 2026-08-25 | 2026-08-25 | ffuf parameter fuzz → image.php?img= include(). LFI php://filter reads db.php (MySQL root). data:// RCE (SELinux blocks network shells). mysql CLI via shell_exec dumps double-base64 creds → michael SSH. /etc/passwd owned by michael → UID-0 append → root. |
| [[OSCP/BOXES/WRITE UPS/Linux/5. Bratarina\|Bratarina]] | PG Practice, Linux | 2026-08-27 | 2026-08-27 | OpenSMTPD 6.6.2 CVE-2020-7247 (EDB 47984) MAIL FROM injection → direct root. TCP egress filtered (tcpdump confirmed). `python` (Python 2) in payload — delivery PATH lacks python3. Port 80 reverse shell bypasses filter. |
| [[OSCP/BOXES/WRITE UPS/Linux/6. Pebbles\|Pebbles]] | PG Practice, Linux | 2026-08-27 | 2026-08-27 | ZoneMinder 1.29.0 SQLi (EDB-41239) — `limit` POST param, stacked queries, SLEEP confirmed. Web root leaked from SQL error body. INTO OUTFILE webshell → www-data. MySQL root creds in /etc/zm/zm.conf. UDF sys_exec SUID bash → euid=0. |
| [[OSCP/BOXES/WRITE UPS/Linux/7. Nibbles\|Nibbles]] | PG Practice, Linux | 2026-08-27 | 2026-08-27 | PostgreSQL 11.3 on port 5437. Default creds postgres:postgres. Superuser confirmed. COPY TO PROGRAM mkfifo+nc (port 80 bypasses egress). SUID /usr/bin/find → euid=0. Both flags grabbed as root. |
| [[OSCP/BOXES/WRITE UPS/Linux/8. Zenphoto\|Zenphoto]] | PG Practice, Linux | 2026-08-27 | 2026-08-27 | Zenphoto 1.4.1.4 at /test/ (gobuster). Version in HTML comment. EDB-18083 unauthenticated RCE via ajax_create_folder.php → www-data. Ubuntu 10.04 kernel 2.6.32-21 → CVE-2010-3904 EDB-15285 RDS LPE → root. |

---

## Tips for Using This List

1. **Start with Variety**: Mix Linux, Windows, and AD machines from the start.
2. **Prioritize Proving Grounds**: PG Practice has the most "OSCP-like" machines.
3. **Don't Skip AD**: AD is a significant part of the exam; practice it thoroughly.
4. **Use the Notes Column**: Track specific vulnerabilities, techniques, and tools used.
5. **Simulate Exam Conditions**: Try to complete machines without walkthroughs initially.
6. **Revisit Weak Areas**: If you struggle with a specific technique (e.g., SQL injection, buffer overflows, Kerberos attacks), note it and focus on those machines.

---

**Disclaimer**: This list is a consolidation of machines commonly recommended for OSCP and Red Teaming preparation. Availability and difficulty may vary across platforms (HackTheBox, Proving Grounds, HackSmarter, VHL, TryHackMe, VulnLab). Always practice responsibly and within the terms of service of the respective platform.